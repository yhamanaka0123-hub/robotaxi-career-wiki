"""Loading instruction files and formatting retrieved passages for prompts."""
from . import config


def load_instructions(name: str) -> str:
    """Read instructions/<name>.md. The model never reads project files by itself;
    the harness loads the file for the current mode and puts it in the system prompt."""
    path = config.INSTRUCTIONS / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Instruction file missing: {path}")
    return path.read_text(encoding="utf-8")


def format_passages(hits: list[dict]) -> str:
    """Number passages [S1]..[Sn] and keep their source labels, so citations are checkable."""
    blocks = []
    for n, h in enumerate(hits, start=1):
        p = h["passage"]
        blocks.append(f"[S{n}] source: {p.path} | section: {p.section}\n{p.text}")
    return "\n\n".join(blocks)
