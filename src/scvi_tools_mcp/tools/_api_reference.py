from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils


class ApiResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


def _find_symbol(symbol: str) -> Path | None:
    name = symbol.lower().split(".")[-1]
    api_dir = utils.get_knowledge_dir() / "api"
    candidate = api_dir / f"{name}.md"
    if candidate.exists():
        return candidate
    candidate2 = utils.get_knowledge_dir() / "models" / f"{name}.md"
    if candidate2.exists():
        return candidate2
    return None


@mcp.tool()
def get_api_reference(symbol: str) -> ApiResult:
    """Get the API reference (signature + docstring) for a scvi-tools class or method.

    Use this when a user asks about specific parameters, return types, or method
    behavior. Pass the class name or method name.

    Args:
        symbol: Class or method name. Examples: 'SCVI', 'TOTALVI', 'SCANVI.setup_anndata'.
    """
    try:
        path = _find_symbol(symbol)
        if path is None:
            api_dir = utils.get_knowledge_dir() / "api"
            available = sorted(p.stem.upper() for p in api_dir.glob("*.md")) if api_dir.exists() else []
            return ApiResult(error=f"Symbol '{symbol}' not found. Available: {', '.join(available[:20])}.")
        content = path.read_text(encoding="utf-8")
        if "." in symbol:
            method = symbol.split(".")[-1].lower()
            idx = content.lower().find(f"## {method}")
            if idx >= 0:
                content = content[idx : idx + 2000]
        result = utils.truncate(content)
        return ApiResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ApiResult(error=str(e))


@mcp.tool()
def search_api(query: str) -> ApiResult:
    """Search the scvi-tools API for classes and methods matching a query.

    Returns matching symbols with short descriptions. Use get_api_reference to
    get full details on any result.

    Args:
        query: Keywords to search (e.g. 'differential expression', 'latent representation').
    """
    try:
        keywords = [k.lower() for k in query.split() if k]
        api_dir = utils.get_knowledge_dir() / "api"
        if not api_dir.exists():
            return ApiResult(error="API knowledge not found. Run scripts/extract_api_docs.py.")
        results: list[tuple[int, str, str]] = []
        for md in sorted(api_dir.glob("*.md")):
            content = md.read_text(encoding="utf-8")
            score = sum(content.lower().count(kw) for kw in keywords)
            if score > 0:
                first_line = content.splitlines()[0] if content.splitlines() else md.stem
                results.append((score, md.stem.upper(), first_line[:100]))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# API Search: '{query}'", ""]
        for _, name, desc in results[:10]:
            lines.append(f"- **{name}**: {desc}")
            lines.append(f"  → use get_api_reference(symbol='{name}')")
        if not results:
            lines.append("No API symbols matched. Try broader terms.")
        result = utils.truncate("\n".join(lines))
        return ApiResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ApiResult(error=str(e))
