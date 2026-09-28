"""Retrieval-only check for the four ask-mode tests (no answer generation).

For each test question, prints the top-k passages the harness would send to Gemma
and the rank of each expected passage. Usage:
    python3 tools/retrieval_check.py [label]
Writes evidence/retrieval/<label>.md
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from wiki_cli import config, retrieval  # noqa: E402
from wiki_cli.ask import expand_queries, retrieve_for_question  # noqa: E402

# (question, [(source_id, line) of expected evidence])  — mirrors tests/questions.md
TESTS = [
    ("Which company owns Zoox, and how much did it pay to acquire it?",
     [("wiki-zoox", 7)]),
    ("If I finish a graduate degree at an American university, is there a separate H-1B quota I can apply under?",
     [("wiki-h1b", 6), ("wiki-h1b", 104)]),
    ("After I graduate from my MBA, how long can I work in the US on OPT before I need an H-1B?",
     [("personal-career-notes", 10), ("wiki-opt", 4)]),
    ("Does Moove sponsor H-1B visas for its employees?", []),
]


def main(label: str) -> None:
    ix = retrieval.Index()
    out = [f"# Retrieval check: {label}", "",
           f"top_k={config.TOP_K}, chunk_chars={config.CHUNK_CHARS}, "
           f"vector_weight={config.VECTOR_WEIGHT}, query_expansion={config.QUERY_EXPANSION}", ""]
    for n, (q, expected) in enumerate(TESTS, start=1):
        queries = expand_queries(q) if config.QUERY_EXPANSION else [q]
        hits, method = retrieve_for_question(ix, queries)
        out += [f"## Test {n}: {q}", f"method: {method}", f"queries: {queries}", ""]
        for r, h in enumerate(hits, start=1):
            p = h["passage"]
            out.append(f"{r}. `{p.label()}` score={h['score']} bm25#{h['bm25_rank']} "
                       f"vec#{h['vector_rank']} — {p.text[:90]!r}")
        for sid, line in expected:
            rank = next((r for r, h in enumerate(hits, 1) if h["passage"].source_id == sid
                         and h["passage"].start_line <= line <= h["passage"].end_line), None)
            out.append(f"- expected {sid} line {line}: "
                       + (f"FOUND at rank {rank}" if rank else "MISSING from top-k"))
        out.append("")
    dest = config.ROOT / "evidence" / "retrieval" / f"{label}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    print(f"\nsaved {dest.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "latest")
