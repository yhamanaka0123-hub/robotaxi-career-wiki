"""The retrieval tool: a local index of raw-source passages, searched with
BM25 keywords + EmbeddingGemma vectors, fused by reciprocal rank.

Index files live in .index/ (outside the vault). Search degrades to keyword-only
if the embedding model is unreachable, so `wiki search` works without the LLM.
"""
import hashlib
import json
import math
import re
from collections import Counter

from . import config, llm
from .sources import Passage, load_catalog, split_passages

PASSAGES_FILE = config.INDEX_DIR / "passages.jsonl"
VECTORS_FILE = config.INDEX_DIR / "vectors.json"
META_FILE = config.INDEX_DIR / "meta.json"

STOPWORDS = set("""a an the and or of to in on for with by at from as is are was were be been
it its this that these those i my me we our you your do does did how what which who when where
why can could would should will about into than then there their they them he she his her not
if so after before""".split())
RRF_K = 60


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if t not in STOPWORDS]


def _index_text(p: Passage) -> str:
    return f"{p.title} {p.section} {p.text}"


def _file_hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ---------- building ----------

def build(log=print) -> dict:
    """Split every catalogued raw source into passages and (re)build the index."""
    catalog = load_catalog()
    passages: list[Passage] = []
    for sid, meta in catalog.items():
        ps = split_passages(sid, meta)
        passages += ps
        log(f"  split {meta['file']}: {len(ps)} passages")

    config.INDEX_DIR.mkdir(exist_ok=True)
    with PASSAGES_FILE.open("w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")

    vectors, embed_status = None, "ok"
    try:
        vectors = []
        for i in range(0, len(passages), 16):
            batch = passages[i:i + 16]
            vectors += llm.embed([f"title: {p.title} | text: {p.section}. {p.text}" for p in batch])
        VECTORS_FILE.write_text(json.dumps({p.id: v for p, v in zip(passages, vectors)}))
    except llm.ModelUnavailable as e:
        embed_status = f"skipped ({e})"
        VECTORS_FILE.unlink(missing_ok=True)
        log(f"  ! embeddings skipped, keyword search only: {e}")

    meta = {"passages": len(passages), "embed_model": config.EMBED_MODEL,
            "embeddings": embed_status, "chunk_chars": config.CHUNK_CHARS,
            "sources": {m["file"]: _file_hash(config.VAULT / m["file"]) for m in catalog.values()}}
    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


# ---------- searching ----------

class Index:
    def __init__(self):
        if not PASSAGES_FILE.exists():
            raise FileNotFoundError("No search index yet. Run: wiki ingest")
        self.passages = [Passage(**json.loads(l)) for l in PASSAGES_FILE.open(encoding="utf-8")]
        self.meta = json.loads(META_FILE.read_text())
        self.vectors = json.loads(VECTORS_FILE.read_text()) if VECTORS_FILE.exists() else {}
        # BM25 statistics
        self.docs = [Counter(tokenize(_index_text(p))) for p in self.passages]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_len = sum(self.lengths) / len(self.lengths)
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def stale_sources(self) -> list[str]:
        """Raw files that changed or appeared since the index was built."""
        catalog = load_catalog()
        known = self.meta.get("sources", {})
        return [m["file"] for m in catalog.values()
                if known.get(m["file"]) != _file_hash(config.VAULT / m["file"])]

    def bm25(self, query: str, k1=1.5, b=0.75) -> list[float]:
        q = tokenize(query)
        scores = []
        for d, length in zip(self.docs, self.lengths):
            s = 0.0
            for t in q:
                if t in d:
                    tf = d[t]
                    s += self.idf[t] * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / self.avg_len))
            scores.append(s)
        return scores

    def cosine(self, query: str) -> list[float] | None:
        if not self.vectors:
            return None
        qv = llm.embed([f"task: search result | query: {query}"])[0]
        qn = math.sqrt(sum(x * x for x in qv))
        out = []
        for p in self.passages:
            v = self.vectors[p.id]
            out.append(sum(a * b for a, b in zip(qv, v)) / (qn * math.sqrt(sum(x * x for x in v))))
        return out

    def search(self, query: str, k: int = config.TOP_K) -> tuple[list[dict], str]:
        """Return (hits, method). Each hit: passage + scores + ranks."""
        kw = self.bm25(query)
        method = "hybrid (BM25 + EmbeddingGemma, RRF)"
        try:
            vec = self.cosine(query)
            if vec is None:
                method = "keyword only (BM25) - index has no embeddings"
        except llm.ModelUnavailable:
            vec, method = None, "keyword only (BM25) - embedding model unreachable"

        kw_rank = _ranks(kw)
        fused = []
        for i, p in enumerate(self.passages):
            score = 1 / (RRF_K + kw_rank[i]) if kw[i] > 0 else 0.0
            fused.append(score)
        if vec is not None:
            vec_rank = _ranks(vec)
            fused = [f + config.VECTOR_WEIGHT / (RRF_K + vec_rank[i]) for i, f in enumerate(fused)]

        order = sorted(range(len(self.passages)), key=lambda i: -fused[i])[:k]
        hits = [{"passage": self.passages[i], "score": round(fused[i], 4),
                 "bm25": round(kw[i], 2), "bm25_rank": kw_rank[i],
                 "cosine": round(vec[i], 3) if vec else None,
                 "vector_rank": vec_rank[i] if vec else None}
                for i in order if fused[i] > 0]
        return hits, method


def _ranks(scores: list[float]) -> list[int]:
    """1-based rank of each item (1 = best)."""
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    ranks = [0] * len(scores)
    for r, i in enumerate(order, start=1):
        ranks[i] = r
    return ranks
