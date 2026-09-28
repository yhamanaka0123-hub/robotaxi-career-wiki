"""wiki — personal robotaxi-career wiki with local Gemma. Entry point and mode selection."""
import argparse
import pathlib
import sys

from . import config, llm

DESCRIPTION = f"""\
Personal wiki CLI backed by a local Gemma model ({config.CHAT_MODEL} via Ollama).

modes:
  chat    personal assistant "Navi": conversation memory, looks up notes only when needed
  ask     standalone factual answer from retrieved passages, with citations
  search  original matching passages and paths; no model answer is generated
  ingest  read sources in vault/raw/, write linked notes in vault/wiki/, rebuild the index
  status  show model, runtime, index, and vault state

examples:
  wiki ingest ./vault/raw
  wiki search "H-1B annual cap"
  wiki ask "Which company owns Zoox?" --mode local
  wiki chat

configuration (environment variables):
  WIKI_OLLAMA_URL      local runtime URL        (default {config.OLLAMA_URL})
  WIKI_MODEL           generation model         (default {config.CHAT_MODEL})
  WIKI_EMBED_MODEL     embedding model          (default {config.EMBED_MODEL})
  WIKI_TOP_K           passages per question    (default {config.TOP_K})
  WIKI_VECTOR_WEIGHT   embedding weight in fusion (default {config.VECTOR_WEIGHT})
  WIKI_QUERY_EXPANSION 1/0 extra search queries in ask (default {int(config.QUERY_EXPANSION)})

required inputs: sources.json (catalog), vault/raw/ (originals), instructions/*.md (prompts).
Every run is saved under evidence/runs/.
"""


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wiki", description=DESCRIPTION,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", metavar="{chat,ask,search,ingest,status}")

    s = sub.add_parser("ingest", help="build wiki notes and the search index from sources")
    s.add_argument("path", nargs="?", default=str(config.RAW), help="raw folder or one raw file")
    s.add_argument("--force", action="store_true", help="regenerate notes even if marked reviewed")

    s = sub.add_parser("search", help="show matching original passages (no generation)")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=config.TOP_K, help="number of passages")

    s = sub.add_parser("ask", help="standalone cited answer from your sources")
    s.add_argument("question")
    s.add_argument("--mode", choices=["local", "online"], default="local")

    s = sub.add_parser("chat", help="talk with Navi, your personal assistant")
    s.add_argument("--mode", choices=["local", "online"], default="local")

    sub.add_parser("status", help="show model, runtime, and index status")
    return p


def check_mode(mode: str) -> None:
    if mode == "online":
        sys.exit("Online mode is not configured in this project. Local mode is the default: "
                 "omit --mode or use --mode local.")


def header(mode: str) -> None:
    info = llm.runtime_info()
    q = f", {info['quantization']}" if info.get("quantization") else ""
    print(f"[{mode} · local · {info['model']}{q} · Ollama {info['runtime_version']}]")


def main(argv=None) -> None:
    args = parser().parse_args(argv)
    if args.command is None:
        parser().print_help()
        return
    try:
        if args.command == "ingest":
            from .ingest import run_ingest
            header("ingest")
            r = run_ingest(pathlib.Path(args.path), force=args.force)
            print(f"\nDone in {r['total_seconds']}s. Saved: {r['saved_to']}")

        elif args.command == "search":
            from .search import run_search
            r = run_search(args.query, k=args.k)
            print(f"[search · retrieval only, no model answer · {r['retrieval_method']}]\n")
            if not r["results"]:
                print("No matching passages.")
            for h in r["results"]:
                print(f"[{h['cite']}] {h['path']} § {h['section']} (lines {h['lines']})  score {h['score']}")
                for line in h["text"].splitlines():
                    print(f"    {line}")
                print()
            if r["stale_sources"]:
                print(f"! index is older than: {r['stale_sources']} — run `wiki ingest`")
            print(f"Saved: {r['saved_to']}")

        elif args.command == "ask":
            from .ask import run_ask
            from .chat import format_ask
            check_mode(args.mode)
            header("ask")
            print(f"Q: {args.question}")
            print(format_ask(run_ask(args.question)))

        elif args.command == "chat":
            from .chat import run_chat
            check_mode(args.mode)
            run_chat()

        elif args.command == "status":
            status()
    except llm.ModelUnavailable as e:
        sys.exit(f"Local model unavailable: {e}")
    except FileNotFoundError as e:
        sys.exit(f"Missing file: {e}")


def status() -> None:
    import json
    info = llm.runtime_info()
    print(f"model:     {info['model']} ({info.get('parameters', '?')}, {info.get('quantization', '?')})")
    print(f"embedding: {info['embed_model']}")
    print(f"runtime:   Ollama {info['runtime_version']} at {info['url']} (execution: local)")
    meta = config.INDEX_DIR / "meta.json"
    if meta.exists():
        m = json.loads(meta.read_text())
        print(f"index:     {m['passages']} passages from {len(m['sources'])} sources, embeddings {m['embeddings']}")
    else:
        print("index:     not built — run `wiki ingest`")
    notes = sorted(p.relative_to(config.WIKI) for p in config.WIKI.rglob("*.md"))
    print(f"wiki:      {len(notes)} notes in vault/wiki/")
    for n in notes:
        print(f"           {n}")


if __name__ == "__main__":
    main()
