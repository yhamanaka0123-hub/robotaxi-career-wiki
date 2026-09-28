"""Search mode: expose the retrieval tool directly. No answer is generated."""
from . import config, evidence
from .retrieval import Index


def run_search(query: str, k: int = config.TOP_K) -> dict:
    ix = Index()
    hits, method = ix.search(query, k=k)
    hit_records = [evidence.hit_record(n, h) for n, h in enumerate(hits, start=1)]
    record = {"query": query, "retrieval_method": method, "stale_sources": ix.stale_sources(),
              "results": hit_records, "generated_answer": None}
    md = "\n".join([f"# Search: {query}", "",
                    "- **Mode:** search (retrieval only; no model answer generated)",
                    f"- **Retrieval:** {method}", "",
                    evidence.passages_markdown(hit_records) or "_No matching passages._"])
    record["saved_to"] = evidence.save_run("search", record, md)
    return record
