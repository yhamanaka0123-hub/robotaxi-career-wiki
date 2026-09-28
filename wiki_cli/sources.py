"""Source catalog and passage splitting. Reads vault/raw/ but never writes to it."""
import json
import re
from dataclasses import dataclass, asdict

from . import config

# Wikipedia plain text uses "== Heading ==", Markdown uses "# Heading".
WIKI_HEADING = re.compile(r"^(=+)\s*(.*?)\s*=+\s*$")
MD_HEADING = re.compile(r"^(#+)\s+(.*?)\s*$")
SKIP_SECTIONS = {"References", "External links", "See also", "Notes", "Further reading",
                 "Citations", "Sources", "Bibliography"}
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"(])")


@dataclass
class Passage:
    id: str          # "wiki-zoox#3" — machine id, shown only in metadata/evidence
    source_id: str
    path: str        # vault-relative path of the original, e.g. "raw/Zoox - Wikipedia.md"
    title: str
    section: str     # "History" or "Services > Waymo One"
    start_line: int
    end_line: int
    text: str

    def label(self) -> str:
        """Human-readable citation target."""
        return f"{self.path} § {self.section} (lines {self.start_line}-{self.end_line})"

    to_dict = asdict


def load_catalog() -> dict:
    if not config.CATALOG.exists():
        raise FileNotFoundError(f"Source catalog not found: {config.CATALOG}")
    return json.loads(config.CATALOG.read_text(encoding="utf-8"))


def read_sections(source_id: str, meta: dict) -> list[tuple[str, list[tuple[int, str]]]]:
    """Return [(section_path, [(line_no, paragraph), ...]), ...] for one raw file."""
    path = config.VAULT / meta["file"]
    if not path.exists():
        raise FileNotFoundError(f"Raw source missing for {source_id}: {path}")
    sections: list[tuple[str, list]] = [("Introduction", [])]
    stack: list[str] = []
    skipping = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = WIKI_HEADING.match(line) or MD_HEADING.match(line)
        if m:
            level = len(m.group(1)) - 1  # "== X ==" and "## X" are both top-level sections
            if level == 0:  # a Markdown "# Title" line: document title, not a section
                continue
            stack = stack[: level - 1] + [m.group(2)]
            skipping = stack[0] in SKIP_SECTIONS
            if not skipping:
                sections.append((" > ".join(stack), []))
            continue
        if line.strip() and not skipping:
            sections[-1][1].append((n, line.strip()))
    return [(name, paras) for name, paras in sections if paras]


def _split_long(text: str, limit: int) -> list[str]:
    """Split one long paragraph at sentence boundaries."""
    parts, cur = [], ""
    for sent in SENTENCE_END.split(text):
        if cur and len(cur) + len(sent) + 1 > limit:
            parts.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    return parts + ([cur] if cur else [])


def split_passages(source_id: str, meta: dict) -> list[Passage]:
    """Group paragraphs within a section into ~CHUNK_CHARS passages, keeping line numbers."""
    limit = config.CHUNK_CHARS
    passages: list[Passage] = []

    def emit(section, lines):
        passages.append(Passage(
            id=f"{source_id}#{len(passages)}", source_id=source_id, path=meta["file"],
            title=meta["title"], section=section, start_line=lines[0][0],
            end_line=lines[-1][0], text="\n".join(t for _, t in lines)))

    for section, paras in read_sections(source_id, meta):
        buf: list[tuple[int, str]] = []
        for line_no, para in paras:
            pieces = _split_long(para, limit) if len(para) > limit * 1.3 else [para]
            for piece in pieces:
                if buf and sum(len(t) for _, t in buf) + len(piece) > limit:
                    emit(section, buf)
                    buf = []
                buf.append((line_no, piece))
        if buf:
            emit(section, buf)
    return passages
