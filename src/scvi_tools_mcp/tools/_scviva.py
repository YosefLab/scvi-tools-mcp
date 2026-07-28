from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils

ScvivaModelName = Literal[
    "resolvi",
    "destvi",
    "scviva",
    "gimvi",
    "diagvi",
    "stereoscope",
    "tangram",
    "harreman",
]

MODEL_DESCRIPTIONS: dict[str, str] = {
    "resolvi": "Corrects segmentation errors and background noise in cellular-resolution spatial data.",
    "destvi": "Multi-resolution deconvolution of spatial transcriptomics spots into cell type proportions.",
    "scviva": "Models cellular microenvironments and niche effects on gene expression.",
    "gimvi": "Imputes missing genes in spatial transcriptomics data using a paired scRNA-seq reference.",
    "diagvi": "Diagonal integration of unpaired multi-modal single-cell data via a feature guidance graph.",
    "stereoscope": "Two-stage deconvolution of spatial spots into cell type proportions (RNA + spatial models).",
    "tangram": "Maps single-cell RNA-seq data onto spatial coordinates via constrained optimization.",
    "harreman": "Cell-cell interaction and communication analysis over spatial neighborhoods.",
}


class ScvivaResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


def _scviva_dir() -> Path:
    return utils.get_knowledge_dir() / "scviva_tools"


@mcp.tool()
def list_scviva_models() -> ScvivaResult:
    """List the spatial transcriptomics models exposed by the scviva-tools package.

    scviva-tools is a companion spatial toolkit built on top of scvi-tools, unifying
    ResolVI, DestVI, scVIVA, GIMVI, DiagVI, Stereoscope, Tangram, and Harreman under
    one API. Use get_scviva_model for details on any model returned here.
    """
    try:
        lines = ["# scviva-tools Models", ""]
        for name, description in MODEL_DESCRIPTIONS.items():
            lines.append(f"- **{name}** — {description}")
        result = utils.truncate("\n".join(lines))
        return ScvivaResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ScvivaResult(error=str(e))


@mcp.tool()
def get_scviva_model(model_name: ScvivaModelName, page: int = 1, page_size: int = 200) -> ScvivaResult:
    """Get the API reference and user guide for one scviva-tools model.

    Some entries (e.g. diagvi, stereoscope) exceed a single page — check total_pages
    and call again with page=2, 3, etc. to read the rest, including the User Guide section.

    Args:
        model_name: One of resolvi, destvi, scviva, gimvi, diagvi, stereoscope, tangram, harreman.
        page: Page number starting at 1.
        page_size: Lines per page (default 200).
    """
    try:
        path = _scviva_dir() / "models" / f"{model_name}.md"
        if not path.exists():
            return ScvivaResult(
                error=f"scviva-tools model '{model_name}' not found. Call list_scviva_models() for options."
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        result = utils.paginate(lines, page=page, page_size=page_size)
        return ScvivaResult(
            content="\n".join(result.lines),
            page=result.page,
            total_pages=result.total_pages,
            truncated=result.total_pages > 1,
        )
    except Exception as e:
        return ScvivaResult(error=str(e))


@mcp.tool()
def list_scviva_tutorials() -> ScvivaResult:
    """List available scviva-tools tutorials, converted from the package's own notebooks."""
    try:
        base = _scviva_dir() / "tutorials"
        if not base.exists():
            return ScvivaResult(error="scviva-tools tutorial knowledge not found.")
        lines = ["# scviva-tools Tutorials", ""]
        for md in sorted(base.glob("*.md")):
            lines.append(f"- `{md.stem}` — use get_scviva_tutorial(tutorial_name='{md.stem}')")
        result = utils.truncate("\n".join(lines))
        return ScvivaResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ScvivaResult(error=str(e))


@mcp.tool()
def get_scviva_tutorial(tutorial_name: str, page: int = 1, page_size: int = 200) -> ScvivaResult:
    """Read the full content of a scviva-tools tutorial.

    Args:
        tutorial_name: Tutorial name from list_scviva_tutorials, e.g. 'resolVI_tutorial'.
        page: Page number starting at 1.
        page_size: Lines per page (default 200).
    """
    try:
        base = _scviva_dir() / "tutorials"
        path = base / f"{tutorial_name}.md"
        if not path.exists():
            return ScvivaResult(
                error=f"scviva-tools tutorial '{tutorial_name}' not found. Call list_scviva_tutorials() first."
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        result = utils.paginate(lines, page=page, page_size=page_size)
        return ScvivaResult(
            content="\n".join(result.lines),
            page=result.page,
            total_pages=result.total_pages,
            truncated=result.total_pages > 1,
        )
    except Exception as e:
        return ScvivaResult(error=str(e))
