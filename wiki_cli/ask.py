"""Ask mode: the RAG workflow.

question -> (optional query expansion) -> retrieve passages -> research rules + passages
-> local Gemma -> citation check -> display + save evidence.
Each call is standalone: no chat history and no persona are ever included.
"""
import json
import re

from . import config, evidence, llm, prompts
from .retrieval import Index

CITE = re.compile(r"\[S(\d+)\]")
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
INSUFFICIENT = "INSUFFICIENT EVIDENCE"


def expand_queries(question: str) -> list[str]:
    """Ask Gemma for encyclopedia-style keyword queries. The original question always comes first."""
    try:
        r = llm.chat([{"role": "system", "content": prompts.load_instructions("query-expansion")},
                      {"role": "user", "content": question}],
                     temperature=0.0, json_mode=True)
        extra = [q for q in json.loads(r["text"]).get("queries", []) if isinstance(q, str)]
    except (json.JSONDecodeError, AttributeError):
        extra = []
    return [question] + extra[:2]


def retrieve_for_question(ix: Index, queries: list[str]) -> tuple[list[dict], str]:
    """Search each query; keep each passage's best score; return the TOP_K overall."""
    best: dict[str, dict] = {}
    method = ""
    for q in queries:
        hits, method = ix.search(q, k=config.TOP_K * 2)
        for h in hits:
            pid = h["passage"].id
            if pid not in best or h["score"] > best[pid]["score"]:
                best[pid] = h
    ranked = sorted(best.values(), key=lambda h: -h["score"])[: config.TOP_K]
    return ranked, method + (f", {len(queries)} queries" if len(queries) > 1 else "")


def check_citations(answer: str, hits: list[dict]) -> dict:
    """Mechanical checks a reader would otherwise do by hand. They do not prove support;
    a person still has to read the cited passage."""
    n = len(hits)
    cited = sorted({int(m) for m in CITE.findall(answer)})
    invalid = [c for c in cited if not 1 <= c <= n]
    insufficient = answer.strip().upper().startswith(INSUFFICIENT)

    body = answer.split("\n", 1)[1] if insufficient and "\n" in answer else ("" if insufficient else answer)
    sentences = [s.strip() for s in re.split(r"(?<=[a-z0-9)\]][.!?])\s+|\n+", body) if len(s.strip()) > 20]
    uncited = [s for s in sentences if not CITE.search(s)] if not insufficient else []

    # numbers in a sentence should appear in at least one passage that sentence cites
    unsupported_numbers = []
    for s in sentences:
        refs = [int(m) for m in CITE.findall(s) if 1 <= int(m) <= n]
        texts = " ".join(hits[r - 1]["passage"].text for r in refs)
        for num in NUMBER.findall(CITE.sub("", s)):
            if refs and num not in texts:
                unsupported_numbers.append(num)

    if insufficient:
        status = "insufficient evidence (reported by model)"
    elif not cited:
        status = "FAIL: no citations"
    elif invalid:
        status = "FAIL: cites passages that were not retrieved"
    elif uncited or unsupported_numbers:
        status = "WARN: some claims lack matching citations"
    else:
        status = "ok: every sentence cites a retrieved passage"
    return {"status": status, "cited": [f"S{c}" for c in cited], "invalid": invalid,
            "uncited_sentences": uncited, "numbers_not_in_cited_passages": unsupported_numbers,
            "insufficient": insufficient}


def run_ask(question: str) -> dict:
    info = llm.runtime_info()
    ix = Index()
    stale = ix.stale_sources()

    queries = expand_queries(question) if config.QUERY_EXPANSION else [question]
    hits, method = retrieve_for_question(ix, queries)

    # The question is repeated after the passages: small models attend most to the end of the prompt.
    passages = prompts.format_passages(hits) if hits else "(no passages matched)"
    user = (f"Question: {question}\n\nSource passages:\n\n{passages}\n\n"
            f"Read every passage above, then answer the question using only them: {question}")
    messages = [{"role": "system", "content": prompts.load_instructions("wiki-instructions")},
                {"role": "user", "content": user}]
    result = llm.chat(messages, think=config.ASK_THINK)
    check = check_citations(result["text"], hits)

    hit_records = [evidence.hit_record(n, h) for n, h in enumerate(hits, start=1)]
    record = {"question": question, "model": info, "retrieval_method": method, "queries": queries,
              "settings": {"top_k": config.TOP_K, "chunk_chars": config.CHUNK_CHARS,
                           "vector_weight": config.VECTOR_WEIGHT, "query_expansion": config.QUERY_EXPANSION,
                           "temperature": config.TEMPERATURE, "num_ctx": config.NUM_CTX,
                           "think": config.ASK_THINK},
              "stale_sources": stale, "retrieved": hit_records, "answer": result["text"],
              "citation_check": check, "timing_seconds": result["seconds"],
              "prompt_tokens": result["prompt_tokens"], "output_tokens": result["output_tokens"]}
    record["saved_to"] = evidence.save_run("ask", record, _markdown(record))
    return record


def _markdown(r: dict) -> str:
    c = r["citation_check"]
    lines = [f"# Ask: {r['question']}", "",
             f"- **Mode:** ask (standalone, no chat history, no persona)",
             f"- **Model:** {evidence.model_line(r['model'])}",
             f"- **Retrieval:** {r['retrieval_method']}; queries: {r['queries']}",
             f"- **Time:** {r['timing_seconds']} s generation · {r['prompt_tokens']} prompt tokens · "
             f"{r['output_tokens']} output tokens",
             "", "## Answer", "", r["answer"], "",
             "## Citation check (automatic)", "", f"- status: {c['status']}",
             f"- cited: {', '.join(c['cited']) or 'none'}"]
    if c["uncited_sentences"]:
        lines.append(f"- sentences without citation: {c['uncited_sentences']}")
    if c["numbers_not_in_cited_passages"]:
        lines.append(f"- numbers not found in cited passages: {c['numbers_not_in_cited_passages']}")
    lines += ["", "## Retrieved passages", "", evidence.passages_markdown(r["retrieved"])]
    return "\n".join(lines)
