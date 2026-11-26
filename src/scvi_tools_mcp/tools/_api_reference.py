from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils


class ApiResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


# Class names that differ from their knowledge-file stem.
_SYMBOL_ALIASES: dict[str, str] = {
    "harremananalysis": "harreman",
    "visionanalysis": "vision",
    "rnastereoscope": "stereoscope",
    "spatialstereoscope": "stereoscope",
}


def _api_dirs() -> list[Path]:
    """API reference directories, scvi-tools first, then scviva-tools (spatial)."""
    knowledge_dir = utils.get_knowledge_dir()
    return [knowledge_dir / "api", knowledge_dir / "scviva_tools" / "api"]


def _find_symbol(symbol: str) -> Path | None:
    raw_parts = symbol.lower().split(".")
    # Symbols are dotted Python names; anything else (path separators, '..') is rejected.
    if not all(part.isidentifier() for part in raw_parts):
        return None
    parts = [_SYMBOL_ALIASES.get(p, p) for p in raw_parts]
    knowledge_dir = utils.get_knowledge_dir()
    search_dirs = [*_api_dirs(), knowledge_dir / "models", knowledge_dir / "scviva_tools" / "models"]
    # For dotted symbols like 'SCANVI.setup_anndata', use the class component
    # to find the file so method-extraction logic can slice the right section.
    for name in parts:
        for directory in search_dirs:
            candidate = utils.knowledge_file(directory, name)
            if candidate is not None:
                return candidate
    return None


def _method_section(content: str, method: str) -> str | None:
    """Return the '## <method>' section, up to the next '## ' heading."""
    match = re.search(rf"^## {re.escape(method)}[ \t]*$", content, flags=re.MULTILINE | re.IGNORECASE)
    if match is None:
        return None
    nxt = re.search(r"^## ", content[match.end() :], flags=re.MULTILINE)
    end = match.end() + nxt.start() if nxt else len(content)
    return content[match.start() : end].rstrip() + "\n"


def _available_symbols() -> list[str]:
    return sorted({p.stem.upper() for d in _api_dirs() if d.exists() for p in d.glob("*.md")})


@mcp.tool()
def get_api_reference(symbol: str) -> ApiResult:
    """Get the API reference (signature + docstring) for a scvi-tools or scviva-tools class or method.

    Use this when a user asks about specific parameters, return types, or method
    behavior. Pass the class name or method name. Covers scvi-tools models and the
    scviva-tools spatial toolkit (ResolVI, scVIVA, DestVI, Harreman, VISION, ...).

    Args:
        symbol: Class or method name. Examples: 'SCVI', 'TOTALVI', 'SCANVI.setup_anndata',
            'HARREMAN', 'VisionAnalysis.compute_signatures'.
    """
    try:
        path = _find_symbol(symbol)
        if path is None:
            available = _available_symbols()
            return ApiResult(error=f"Symbol not found. Available: {', '.join(available)}.")
        content = path.read_text(encoding="utf-8")
        if "." in symbol:
            content = _method_section(content, symbol.split(".")[-1]) or content
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
        api_files = [md for d in _api_dirs() if d.exists() for md in sorted(d.glob("*.md"))]
        if not api_files:
            return ApiResult(error="API knowledge not found. Run scripts/extract_api_docs.py.")
        results: list[tuple[int, str, str]] = []
        seen: set[str] = set()
        for md in api_files:
            if md.stem in seen:  # scvi-tools entry wins over the scviva-tools duplicate
                continue
            seen.add(md.stem)
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
