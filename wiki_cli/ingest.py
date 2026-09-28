"""Ingest: raw source -> local Gemma -> reviewed-style wiki note, then rebuild the index.

Note filenames come from sources.json ("note"), never from the model, so names stay
readable and re-ingesting a source rewrites the same file instead of creating a duplicate.
Notes marked `reviewed: true` are not overwritten unless --force is given.
"""
import datetime
import json
import pathlib
import re
import time

from . import config, evidence, llm, prompts, retrieval
from .sources import load_catalog, read_sections

FOLDER_BLURBS = {
    "Industry": "The robotaxi market as a whole",
    "Companies": "Robotaxi companies I follow or might apply to",
    "Visas": "US work authorization rules that shape my job search",
    "Career": "My own situation and plan",
    "Other": "Other sources",
}


# ---------- catalog ----------

def register_new_files(catalog: dict, log) -> dict:
    """Any file dropped into vault/raw/ without a catalog entry gets one, with a readable note name."""
    known = {m["file"] for m in catalog.values()}
    for f in sorted(config.RAW.iterdir()):
        rel = f"raw/{f.name}"
        if f.suffix in (".md", ".txt") and rel not in known:
            title = f.stem.replace(" - Wikipedia", "")
            sid = "local-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            catalog[sid] = {"file": rel, "title": title, "kind": "local file", "url": None,
                            "revision": None, "retrieved": datetime.date.today().isoformat(),
                            "license": "unknown - check before sharing", "note": f"Other/{title}"}
            log(f"  registered new source {rel} -> wiki/Other/{title}.md")
    config.CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    return catalog


def note_name(meta: dict) -> str:
    return meta["note"].split("/")[-1]


# ---------- existing notes ----------

def read_frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text[4:text.find("\n---", 4)]
    return dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)


def find_existing_note(source_id: str) -> pathlib.Path | None:
    """Find the note for this source even if the user moved or renamed it."""
    for path in config.WIKI.rglob("*.md"):
        if read_frontmatter(path).get("source_id") == source_id:
            return path
    return None


# ---------- links grounded in the source text ----------

def _alias_pattern(aliases: list[str]) -> re.Pattern:
    case = 0 if any(a.isupper() or "-" in a for a in aliases) else re.I
    return re.compile(r"\b(" + "|".join(re.escape(a) for a in aliases) + r")\b", case)


def find_mention(source_id: str, meta: dict, aliases: list[str]) -> str | None:
    """The best sentence of this source that names another note's topic, or None.
    Prefers short sentences that also name this source's own subject."""
    if not aliases:
        return None
    target = _alias_pattern(aliases)
    own = _alias_pattern(meta.get("aliases") or [meta["title"]])
    candidates = []
    for _, paras in read_sections(source_id, meta):
        for _, para in paras:
            for sentence in re.split(r"(?<=[a-z0-9)][.!?])\s+", para):
                sentence = sentence.lstrip("- ").strip()
                if target.search(sentence) and len(sentence) > 25:
                    candidates.append((not own.search(sentence), len(sentence) > 180, len(sentence), sentence))
    if not candidates:
        return None
    best = min(candidates)[3]
    return best if len(best) <= 180 else best[:177].rsplit(" ", 1)[0] + "…"


def mentioned_notes(source_id: str, meta: dict, catalog: dict) -> dict[str, str]:
    """{other note name: sentence where this source mentions it}."""
    out = {}
    for sid, other in catalog.items():
        if sid != source_id:
            sentence = find_mention(source_id, meta, other.get("aliases", []))
            if sentence:
                out[note_name(other)] = sentence
    return out


# ---------- model call ----------

def source_excerpt(source_id: str, meta: dict) -> tuple[str, int]:
    """Introduction in full, then the first paragraph of each section, up to INGEST_CHARS."""
    parts, used = [], 0
    for section, paras in read_sections(source_id, meta):
        chosen = paras if section == "Introduction" or meta["kind"] != "wikipedia" else paras[:1]
        block = f"## {section}\n" + "\n".join(t for _, t in chosen)
        if used + len(block) > config.INGEST_CHARS:
            break
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts), used


def generate_note_material(source_id: str, meta: dict, other_notes: list[str]) -> tuple[dict, dict]:
    excerpt, chars = source_excerpt(source_id, meta)
    voice = ("This source is the wiki owner's own notes. Write the summary and facts in first "
             "person (\"I am...\", \"My goal...\").\n" if meta["kind"] == "personal note" else "")
    user = (f"Subject of the note: {note_name(meta)}\n{voice}"
            f"Other notes in the wiki: {', '.join(other_notes)}\n\n"
            f"Source document ({meta['file']}):\n\n{excerpt}")
    messages = [{"role": "system", "content": prompts.load_instructions("ingest-instructions")},
                {"role": "user", "content": user}]
    last_error = None
    for _ in range(2):  # one retry if the JSON is malformed
        r = llm.chat(messages, json_mode=True)
        try:
            data = json.loads(r["text"])
            if isinstance(data.get("summary"), str) and isinstance(data.get("facts"), list):
                return data, {"chars_sent": chars, "seconds": r["seconds"],
                              "prompt_tokens": r["prompt_tokens"], "output_tokens": r["output_tokens"]}
        except json.JSONDecodeError as e:
            last_error = e
    raise ValueError(f"Model did not return usable JSON for {source_id}: {last_error}")


# ---------- writing ----------

def render_note(source_id: str, meta: dict, data: dict, info: dict, catalog: dict) -> tuple[str, list[str]]:
    """Build the note in code. Returns (markdown, warnings)."""
    name, warnings = note_name(meta), []
    raw_text = (config.VAULT / meta["file"]).read_text(encoding="utf-8")
    sections = {s for s, _ in read_sections(source_id, meta)}
    raw_link = f"[[{meta['file'][:-3]}|{pathlib.Path(meta['file']).stem}]]"

    facts = []
    for f in data.get("facts", [])[:8]:
        if not isinstance(f, dict) or not f.get("fact"):
            continue
        sec = f.get("section", "")
        if sec not in sections:
            match = next((s for s in sections if s.split(" > ")[-1] == sec or s.startswith(sec)), None)
            if match is None:
                warnings.append(f"unknown section '{sec}' for fact: {f['fact'][:60]}")
            sec = match or "section not identified"
        missing = [n for n in re.findall(r"\d[\d,]*(?:\.\d+)?", f["fact"]) if n not in raw_text]
        if missing:
            warnings.append(f"numbers not in source {missing}: {f['fact'][:60]}")
        facts.append(f"- {f['fact'].strip()} — {raw_link} § {sec}")

    # A link is kept only if this source actually mentions the other topic. The model's
    # explanation is used when it proposed the link; otherwise the source sentence is quoted.
    mentions = mentioned_notes(source_id, meta, catalog)
    related, linked = [], set()
    for r in data.get("related", []):
        target = r.get("note", "").strip("[] ") if isinstance(r, dict) else ""
        if target in mentions and target not in linked:
            related.append(f"- [[{target}]] — {r.get('why', '').strip()}")
            linked.add(target)
        elif target and target != name:
            warnings.append(f"dropped link to '{target}' (source never mentions it)")
    for target, sentence in mentions.items():
        if target not in linked:
            related.append(f"- [[{target}]] — mentioned in the source: “{sentence}”")

    fm = {"source_id": source_id, "source_file": meta["file"], "source_url": meta.get("url") or "none",
          "source_revision": meta.get("revision") or "none", "license": meta.get("license"),
          "generated_by": f"{info.get('model')} ({info.get('quantization')}) via Ollama {info.get('runtime_version')}",
          "generated_at": datetime.date.today().isoformat(), "reviewed": "false"}
    lines = ["---", *[f"{k}: {v}" for k, v in fm.items()], "---", "", f"# {name}", "",
             data["summary"].strip(), "", "## Key facts", "", *facts, "", "## Related notes", "",
             *(related or ["- (none yet)"]), "", "## Sources", "",
             f"- {raw_link} — original, unchanged ({meta['kind']}"
             + (f", [revision {meta['revision']}]({meta['url']})" if meta.get("url") else "")
             + f", {meta.get('license')})", ""]
    return "\n".join(lines), warnings


def note_summary(path: pathlib.Path) -> str:
    """First sentence of the note's summary paragraph (reads the reviewed file, not the model)."""
    body = path.read_text(encoding="utf-8").split("\n# ", 1)[-1].split("\n\n")
    para = body[1] if len(body) > 1 else ""
    first = re.split(r"(?<=[a-z0-9)][.!?])\s", para.strip(), maxsplit=1)[0]
    return first if len(first) <= 200 else first[:197].rsplit(" ", 1)[0] + "…"


def write_index(catalog: dict) -> None:
    groups: dict[str, list] = {}
    for meta in catalog.values():
        folder, name = meta["note"].split("/")[0], note_name(meta)
        path = config.WIKI / f"{meta['note']}.md"
        if path.exists():
            groups.setdefault(folder, []).append((name, note_summary(path)))
    lines = ["# Robotaxi Career Wiki", "",
             "My personal wiki for breaking into the robotaxi / autonomous-vehicle industry as an "
             "international MBA student. Start with [[My Career Plan]], then explore by topic.", ""]
    for folder in [f for f in FOLDER_BLURBS if f in groups]:
        lines += [f"## {folder}", f"_{FOLDER_BLURBS[folder]}_", ""]
        lines += [f"- [[{n}]] — {s}" for n, s in sorted(groups[folder])]
        lines.append("")
    lines += ["## Sources", "", "- [[Source Catalog]] — every original file in `raw/`, where it came "
              "from, and which note it feeds.", ""]
    config.INDEX_MD.write_text("\n".join(lines), encoding="utf-8")


def write_source_catalog(catalog: dict) -> None:
    lines = ["# Source Catalog", "",
             "Original files are kept unchanged in `raw/`. Each feeds exactly one wiki note.", "",
             "| Source ID | Original file | Wiki note | Origin | License |", "|---|---|---|---|---|"]
    for sid, m in catalog.items():
        origin = f"[Wikipedia rev {m['revision']}]({m['url']})" if m.get("url") else m["kind"]
        lines.append(f"| `{sid}` | [[{m['file'][:-3]}\\|{pathlib.Path(m['file']).name}]] | "
                     f"[[{note_name(m)}]] | {origin}, retrieved {m['retrieved']} | {m.get('license')} |")
    config.CATALOG_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- entry point ----------

def run_ingest(target: pathlib.Path, force: bool = False, log=print) -> dict:
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {target}")
    info = llm.runtime_info()
    started = time.time()
    catalog = register_new_files(load_catalog(), log)
    selected = {sid: m for sid, m in catalog.items()
                if (config.VAULT / m["file"]).resolve() == target
                or target in (config.VAULT / m["file"]).resolve().parents}
    if not selected:
        raise FileNotFoundError(f"No catalogued sources under {target}")
    valid_notes = {note_name(m) for m in catalog.values()}

    results = []
    for sid, meta in selected.items():
        dest = config.WIKI / f"{meta['note']}.md"
        existing = find_existing_note(sid)
        if existing and existing != dest:
            log(f"  note for {sid} was moved to {existing.relative_to(config.VAULT)}; updating it there")
            dest = existing
        if existing and read_frontmatter(existing).get("reviewed") == "true" and not force:
            log(f"= {meta['file']}: note '{dest.stem}' is reviewed; kept as is (use --force to regenerate)")
            results.append({"source": sid, "note": str(dest.relative_to(config.VAULT)), "action": "kept (reviewed)"})
            continue
        log(f"→ {meta['file']}: asking {config.CHAT_MODEL} to draft '{dest.stem}' ...")
        others = sorted(valid_notes - {note_name(meta)})
        try:
            data, stats = generate_note_material(sid, meta, others)
        except ValueError as e:
            log(f"  ! {e}")
            results.append({"source": sid, "action": "failed", "error": str(e)})
            continue
        text, warnings = render_note(sid, meta, data, info, catalog)
        dest.parent.mkdir(parents=True, exist_ok=True)
        action = "updated" if dest.exists() else "created"
        dest.write_text(text, encoding="utf-8")
        log(f"  {action} {dest.relative_to(config.VAULT)} ({stats['seconds']}s, "
            f"{stats['chars_sent']} chars sent, {stats['prompt_tokens']} prompt tokens)")
        for w in warnings:
            log(f"  ! {w}")
        results.append({"source": sid, "note": str(dest.relative_to(config.VAULT)), "action": action,
                        "warnings": warnings, **stats})

    log("→ rebuilding retrieval index from raw sources ...")
    index_meta = retrieval.build(log=log)
    write_index(catalog)
    write_source_catalog(catalog)
    log("  wrote vault/index.md and vault/Source Catalog.md")

    record = {"target": str(target), "model": info, "force": force, "results": results,
              "index": {k: v for k, v in index_meta.items() if k != "sources"},
              "total_seconds": round(time.time() - started, 1)}
    md = [f"# Ingest {target.name}", "", f"- **Model:** {evidence.model_line(info)}",
          f"- **Total time:** {record['total_seconds']} s",
          f"- **Index:** {index_meta['passages']} passages, embeddings {index_meta['embeddings']}", "",
          "| Source | Note | Action | Seconds | Chars sent | Warnings |", "|---|---|---|---|---|---|"]
    md += [f"| {r['source']} | {r.get('note', '')} | {r['action']} | {r.get('seconds', '')} | "
           f"{r.get('chars_sent', '')} | {'; '.join(r.get('warnings', [])) or r.get('error', '')} |"
           for r in results]
    record["saved_to"] = evidence.save_run("ingest", record, "\n".join(md) + "\n")
    return record
