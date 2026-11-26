from __future__ import annotations

import math
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


class KnowledgeNotFoundError(Exception):
    pass


@dataclass
class TruncateResult:
    content: str
    truncated: bool


@dataclass
class PaginateResult:
    lines: list[str]
    page: int
    total_pages: int


def get_knowledge_dir() -> Path:
    return Path(str(files("scvi_tools_mcp").joinpath("knowledge")))


def load_knowledge(path: Path) -> str:
    if not path.exists():
        raise KnowledgeNotFoundError(f"Knowledge file not found: {path}. Run scripts/extract_api_docs.py to rebuild.")
    return path.read_text(encoding="utf-8")


def truncate(content: str, max_chars: int = 4000) -> TruncateResult:
    if len(content) <= max_chars:
        return TruncateResult(content=content, truncated=False)
    return TruncateResult(content=content[:max_chars], truncated=True)


def paginate(lines: list[str], page: int = 1, page_size: int = 200) -> PaginateResult:
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    page = max(1, page)
    total_pages = max(1, math.ceil(len(lines) / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    return PaginateResult(lines=lines[start:end], page=page, total_pages=total_pages)


def list_knowledge_files(subdir: str) -> list[str]:
    knowledge_dir = get_knowledge_dir()
    target = knowledge_dir / subdir
    if not target.exists():
        return []
    return sorted(p.stem for p in target.glob("*.md"))


# Known mismatches between synced upstream tutorials and the current package API.
# Tutorials are regenerated from upstream notebooks on every sync, so corrections are
# injected at serve time instead of edited into the knowledge files.
# Each entry is (regex, note); the regex's `obj` group is substituted into the note so
# the suggested code uses the tutorial's own variable name.
TUTORIAL_PITFALLS: list[tuple[str, str]] = [
    (
        r"(?P<obj>[A-Za-z_][A-Za-z0-9_]*)\.gpc\.confident_genes",
        "> **Note (scvi-tools-mcp):** `gpc.confident_genes` is not set by "
        "`differential_expression()`. It is set only as a side effect of calling "
        "`{obj}.plot(...)`, and is restricted to the genes passed as `filter`. "
        "Without the plot, use `{obj}.gpc.y_[{obj}.gpc.y_].index` "
        "(boolean mask: genes DE at the FDR threshold and upregulated in group1 vs "
        "neighbors1, over all genes) instead.",
    ),
]


def annotate_pitfalls(lines: list[str]) -> list[str]:
    """Insert a note after the first code block that uses each known-broken pattern."""
    out = list(lines)
    for pattern, note in TUTORIAL_PITFALLS:
        found = next(((i, m) for i, line in enumerate(out) if (m := re.search(pattern, line))), None)
        if found is None:
            continue
        idx, match = found
        end = next((j for j in range(idx + 1, len(out)) if out[j].strip() == "```"), idx)
        out[end + 1 : end + 1] = ["", note.format(**match.groupdict()), ""]
    return out
