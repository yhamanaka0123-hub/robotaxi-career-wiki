"""Paths and settings. Everything the harness reads or writes is listed here."""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

VAULT = ROOT / "vault"                  # the Obsidian vault (human-facing)
RAW = VAULT / "raw"                     # original sources, never modified
WIKI = VAULT / "wiki"                   # generated + reviewed notes
INDEX_MD = VAULT / "index.md"           # human landing page
CATALOG_MD = VAULT / "Source Catalog.md"

CATALOG = ROOT / "sources.json"         # source_id -> raw file, provenance, note name
INSTRUCTIONS = ROOT / "instructions"    # persona, research rules, router, ingest rules
INDEX_DIR = ROOT / ".index"             # retrieval chunks + embeddings (outside the vault)
EVIDENCE = ROOT / "evidence" / "runs"   # saved outputs of every command
DRAFTS = ROOT / "evidence" / "drafts"   # chat replies saved with /save (never used as evidence)

# Local model runtime (Ollama). Override with env vars if needed.
OLLAMA_URL = os.environ.get("WIKI_OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.environ.get("WIKI_MODEL", "gemma4:e2b")
EMBED_MODEL = os.environ.get("WIKI_EMBED_MODEL", "embeddinggemma")

NUM_CTX = 8192          # context window we request from the model (tokens)
TEMPERATURE = 0.0       # deterministic for ask/ingest; chat uses CHAT_TEMPERATURE
CHAT_TEMPERATURE = 0.7
# Gemma 4 "thinking" before answering in ask mode (slower on CPU, may read evidence more carefully)
ASK_THINK = os.environ.get("WIKI_ASK_THINK", "0") == "1"

# Retrieval
CHUNK_CHARS = 900       # target passage size (~225 tokens)
TOP_K = int(os.environ.get("WIKI_TOP_K", "6"))  # passages passed to the model (~1,300 tokens)
CHAT_HISTORY_TURNS = 6  # user+assistant messages kept in chat context
# weight of the embedding ranking in rank fusion (BM25 weight = 1).
# v1 used 1.0 / no expansion / top 5; see evidence/retrieval/ for why this changed.
VECTOR_WEIGHT = float(os.environ.get("WIKI_VECTOR_WEIGHT", "2.0"))
# ask Gemma for extra keyword queries before retrieving (ask mode)
QUERY_EXPANSION = os.environ.get("WIKI_QUERY_EXPANSION", "1") == "1"

# Ingest: how much of a long source is shown to the model when writing a note
INGEST_CHARS = 7000     # ~1,750 tokens
