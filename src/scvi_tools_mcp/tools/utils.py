from __future__ import annotations
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
import math


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
        raise KnowledgeNotFoundError(
            f"Knowledge file not found: {path}. Run scripts/extract_api_docs.py to rebuild."
        )
    return path.read_text(encoding="utf-8")


def truncate(content: str, max_chars: int = 4000) -> TruncateResult:
    if len(content) <= max_chars:
        return TruncateResult(content=content, truncated=False)
    return TruncateResult(content=content[:max_chars], truncated=True)


def paginate(lines: list[str], page: int = 1, page_size: int = 200) -> PaginateResult:
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
