"""Saves every command's actual output to evidence/runs/ (JSON for machines, Markdown for readers)."""
import datetime
import json

from . import config


def hit_record(n: int, h: dict) -> dict:
    p = h["passage"]
    return {"cite": f"S{n}", "path": p.path, "section": p.section,
            "lines": f"{p.start_line}-{p.end_line}", "passage_id": p.id,
            "score": h["score"], "bm25_rank": h["bm25_rank"], "vector_rank": h["vector_rank"],
            "text": p.text}


def save_run(mode: str, record: dict, markdown: str) -> str:
    """Write <timestamp>-<mode>.json and .md. Returns the Markdown path (repo-relative)."""
    config.EVIDENCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = config.EVIDENCE / f"{stamp}-{mode}"
    record = {"mode": mode, "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
              **record}
    base.with_suffix(".json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    base.with_suffix(".md").write_text(markdown, encoding="utf-8")
    return str(base.with_suffix(".md").relative_to(config.ROOT))


def passages_markdown(hits_records: list[dict]) -> str:
    lines = []
    for h in hits_records:
        lines.append(f"**[{h['cite']}]** `{h['path']}` § {h['section']} (lines {h['lines']}) "
                     f"— score {h['score']}, bm25 #{h['bm25_rank']}, vector #{h['vector_rank']}")
        lines.append("")
        lines += ["> " + l for l in h["text"].splitlines()]
        lines.append("")
    return "\n".join(lines)


def model_line(info: dict) -> str:
    return (f"{info.get('model')} ({info.get('parameters', '?')}, {info.get('quantization', '?')}) "
            f"via {info.get('runtime')} {info.get('runtime_version')} · execution: {info.get('execution')}")
