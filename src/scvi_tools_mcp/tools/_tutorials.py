from __future__ import annotations
from typing import Literal
from pathlib import Path
from pydantic import BaseModel
from scvi_tools_mcp.tools import utils
from scvi_tools_mcp.mcp import mcp

TUTORIAL_CATEGORIES = Literal[
    "scrna", "multimodal", "spatial", "atac", "hub", "quick_start",
    "cytometry", "dev", "r", "use_cases", "scbs", "custom_dl"
]


class TutorialResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


def _tutorials_dir() -> Path:
    return utils.get_knowledge_dir() / "tutorials"


def _find_tutorial(name: str) -> Path | None:
    base = _tutorials_dir()
    candidate = base / f"{name}.md"
    if candidate.exists():
        return candidate
    stem = name.split("/")[-1]
    for md in base.rglob("*.md"):
        if md.stem == stem:
            return md
    return None


@mcp.tool()
def list_tutorials(category: TUTORIAL_CATEGORIES | None = None) -> TutorialResult:
    """List all available scvi-tools tutorials, optionally filtered by category.

    Returns tutorial names and one-line descriptions. Use get_tutorial to read
    the full content of any tutorial. Tutorial names returned here can be passed
    directly to get_tutorial.

    Args:
        category: Filter by category. Pass None to list all. Options: scrna, multimodal,
                  spatial, atac, hub, quick_start, cytometry, dev, r, use_cases, scbs, custom_dl.
    """
    try:
        base = _tutorials_dir()
        if not base.exists():
            return TutorialResult(error="Tutorial knowledge not found. Run scripts/convert_notebooks.py.")
        dirs = [base / category] if category else sorted(d for d in base.iterdir() if d.is_dir())
        lines = ["# Available Tutorials", ""]
        for d in dirs:
            if not d.exists():
                continue
            mds = sorted(d.glob("*.md"))
            if mds:
                lines.append(f"## {d.name}")
                for md in mds:
                    lines.append(f"- `{d.name}/{md.stem}` — use get_tutorial(tutorial_name='{d.name}/{md.stem}')")
                lines.append("")
        result = utils.truncate("\n".join(lines))
        return TutorialResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TutorialResult(error=str(e))


@mcp.tool()
def get_tutorial(tutorial_name: str, page: int = 1, page_size: int = 200) -> TutorialResult:
    """Read the full content of a scvi-tools tutorial.

    Returns the tutorial as Markdown with code cells as fenced blocks. Large tutorials
    are paginated — check total_pages and call again with page=2, 3, etc. if needed.
    Get tutorial names from list_tutorials.

    Args:
        tutorial_name: Tutorial path like 'scrna/harmonization' or 'quick_start/api_overview'.
        page: Page number starting at 1.
        page_size: Lines per page (default 200).
    """
    try:
        path = _find_tutorial(tutorial_name)
        if path is None:
            return TutorialResult(
                error=f"Tutorial '{tutorial_name}' not found. Call list_tutorials() to see available tutorials."
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        result = utils.paginate(lines, page=page, page_size=page_size)
        return TutorialResult(
            content="\n".join(result.lines),
            page=result.page,
            total_pages=result.total_pages,
            truncated=result.total_pages > 1,
        )
    except Exception as e:
        return TutorialResult(error=str(e))


@mcp.tool()
def search_tutorials(query: str) -> TutorialResult:
    """Search tutorials by keyword and return matching excerpts.

    Use this to find tutorials relevant to a user's question. Returns tutorial names
    ranked by keyword relevance with a matching excerpt from each. Then use get_tutorial
    to read the full content.

    Args:
        query: Space-separated keywords (e.g. 'batch integration totalvi reference mapping').
    """
    try:
        base = _tutorials_dir()
        if not base.exists():
            return TutorialResult(error="Tutorial knowledge not found. Run scripts/convert_notebooks.py.")
        keywords = [k.lower() for k in query.split() if k]
        results: list[tuple[int, str, str]] = []
        for md in sorted(base.rglob("*.md")):
            content = md.read_text(encoding="utf-8")
            lower = content.lower()
            score = sum(lower.count(kw) for kw in keywords)
            if score > 0:
                excerpt = next(
                    (line.strip()[:120] for line in content.splitlines() if any(kw in line.lower() for kw in keywords) and len(line.strip()) > 10),
                    "",
                )
                rel = str(md.relative_to(base).with_suffix(""))
                results.append((score, rel, excerpt))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# Tutorial Search: '{query}'", ""]
        for _, name, excerpt in results[:10]:
            lines.append(f"- **{name}**")
            if excerpt:
                lines.append(f"  > {excerpt}")
        if not results:
            lines.append("No tutorials matched. Try broader keywords or use list_tutorials().")
        lines.append("\nUse get_tutorial(tutorial_name='<name>') to read the full tutorial.")
        result = utils.truncate("\n".join(lines))
        return TutorialResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TutorialResult(error=str(e))
