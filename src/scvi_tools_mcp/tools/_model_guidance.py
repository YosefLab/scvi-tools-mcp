from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils
from scvi_tools_mcp.tools._constants import MODEL_NAMES  # noqa: F401 — re-exported
from scvi_tools_mcp.tools._scviva import MODEL_DESCRIPTIONS as SCVIVA_DESCRIPTIONS

TASK_MODEL_MAP: dict[str, list[str]] = {
    "batch_integration": ["scvi", "scanvi", "sysvi", "linearscvi"],
    "dimensionality_reduction": ["scvi", "multivi", "totalvi"],
    "differential_expression": ["scvi", "scanvi", "totalvi", "autozi"],
    "cell_type_annotation": ["scanvi", "cellassign", "solo"],
    "deconvolution": ["destvi", "stereoscope", "tangram"],
    "spatial_mapping": ["tangram", "destvi", "gimvi", "scviva"],
    "spatial_denoising": ["resolvi"],
    "niche_analysis": ["scviva", "resolvi"],
    "cell_communication": ["harreman", "scviva"],
    "spatial_signature_scoring": ["vision", "harreman"],
    "chromatin_accessibility": ["peakvi", "poissonvi", "scbasset", "multivi"],
    "multimodal_integration": ["totalvi", "multivi"],
    "reference_mapping": ["scanvi"],
    "perturbation_modeling": ["contrastivevi", "mrvi"],
}

DATA_TYPE_HINTS: dict[str, str] = {
    "scrna": "For scRNA-seq, start with scVI for batch integration or SCANVI if you have cell type labels.",
    "cite_seq": "For CITE-seq (RNA + protein), use TotalVI.",
    "spatial": (
        "For spatial transcriptomics (scviva-tools): spot-based data (Visium) -> DestVI, Stereoscope or "
        "Tangram for deconvolution; cellular-resolution data (Xenium, MERFISH, CosMx) -> ResolVI to correct "
        "segmentation errors and background, scVIVA for niche-aware embeddings and niche DE. Harreman for "
        "cell-cell communication and VISION for gene-signature scoring with spatial autocorrelation."
    ),
    "atac": "For scATAC-seq, use PeakVI or SCBASSET.",
    "multiome": "For RNA+ATAC multiome data, use MultiVI.",
    "cytometry": "For cytometry data, use CytoVI.",
    "methylation": "For methylation data, use MethylVI or MethylANVI.",
}


# On spatial data, generic tasks are better served by the spatial models: ResolVI
# integrates, annotates (semi-supervised) and runs DE on cellular-resolution data,
# and scVIVA adds niche-aware embeddings and niche DE.
SPATIAL_TASK_MODELS: dict[str, list[str]] = {
    "batch_integration": ["resolvi", "scviva"],
    "dimensionality_reduction": ["resolvi", "scviva"],
    "differential_expression": ["scviva", "resolvi"],
    "cell_type_annotation": ["resolvi"],
}

# Analysis tools that live only in scviva-tools (no scvi-tools model page).
SCVIVA_ONLY = {"harreman", "vision"}


class ModelGuidanceResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


@mcp.tool()
def recommend_model(
    task: Literal[
        "batch_integration",
        "dimensionality_reduction",
        "differential_expression",
        "cell_type_annotation",
        "deconvolution",
        "spatial_mapping",
        "chromatin_accessibility",
        "multimodal_integration",
        "reference_mapping",
        "perturbation_modeling",
        "spatial_denoising",
        "niche_analysis",
        "cell_communication",
        "spatial_signature_scoring",
    ],
    data_type: Literal["scrna", "cite_seq", "spatial", "atac", "multiome", "cytometry", "methylation"],
    has_protein: bool,
    has_accessibility: bool,
    n_batches: int,
) -> ModelGuidanceResult:
    """Recommend scvi-tools models ranked by suitability for the user's task and data type.

    Call this first when a user describes what they want to do. Returns a ranked list of
    model names with a short rationale for each. Use get_model_overview to get details
    on any recommended model.

    Spatial-specific tasks: spatial_denoising (segmentation / background correction),
    niche_analysis (cell microenvironment effects), cell_communication (ligand-receptor /
    metabolite interactions), spatial_signature_scoring (gene-signature scores and spatial
    autocorrelation).

    Args:
        task: The analysis goal (spatial-specific tasks are described above).
        data_type: The type of single-cell data.
        has_protein: True if the data includes protein (ADT) measurements.
        has_accessibility: True if the data includes chromatin accessibility (ATAC).
        n_batches: Number of batches/donors. Use 1 if data is from a single batch.
    """
    try:
        candidates = list(TASK_MODEL_MAP.get(task, ["scvi"]))
        if data_type == "spatial":
            boost = SPATIAL_TASK_MODELS.get(task, [])
            candidates = boost + [c for c in candidates if c not in boost]
        if has_protein and "totalvi" not in candidates:
            candidates = ["totalvi"] + candidates
        if has_accessibility and "multivi" not in candidates:
            candidates = ["multivi"] + candidates
        data_hint = DATA_TYPE_HINTS.get(data_type, "")
        lines = [
            "# Model Recommendations",
            "",
            f"**Task:** {task} | **Data:** {data_type} | **Batches:** {n_batches}",
            "",
            data_hint,
            "",
            "## Ranked Recommendations",
            "",
        ]
        for i, name in enumerate(candidates[:5], 1):
            rationale = f" {SCVIVA_DESCRIPTIONS[name]}" if name in SCVIVA_DESCRIPTIONS else ""
            if name in SCVIVA_ONLY:
                pointer = f"Use `get_scviva_model(model_name='{name}')` for details (scviva-tools)."
            else:
                pointer = f"Use `get_model_overview(model_name='{name}')` for details."
            lines.append(f"{i}. **{name.upper()}** —{rationale} {pointer}")
        lines += [
            "",
            "## Next Steps",
            "1. Call `get_model_overview` on your top choice.",
            "2. Call `get_setup_anndata_guide` to prepare your AnnData object.",
            "3. Call `get_workflow_template` for a full code template.",
        ]
        result = utils.truncate("\n".join(lines))
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))


@mcp.tool()
def get_model_overview(
    model_name: MODEL_NAMES,
) -> ModelGuidanceResult:
    """Get a detailed overview of a specific scvi-tools model.

    Returns the model description, use cases, required inputs, outputs, advantages,
    limitations, and key citations. Call this after recommend_model to learn about
    a specific model before using it.

    Args:
        model_name: The scvi-tools model name in lowercase (e.g. 'scvi', 'scanvi', 'totalvi').
    """
    try:
        knowledge_dir = utils.get_knowledge_dir()
        model_file = knowledge_dir / "models" / f"{model_name}.md"
        if not model_file.exists():
            models_dir = knowledge_dir / "models"
            available = sorted(p.stem for p in models_dir.glob("*.md")) if models_dir.exists() else []
            return ModelGuidanceResult(error=f"Model '{model_name}' not found. Available: {', '.join(available)}")
        content = model_file.read_text(encoding="utf-8")
        result = utils.truncate(content)
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))


@mcp.tool()
def get_model_parameters(
    model_name: MODEL_NAMES,
) -> ModelGuidanceResult:
    """Get key initialization and training parameters for a scvi-tools model.

    Returns the most important parameters for model.__init__() and model.train()
    with descriptions and recommended defaults. Call this when a user wants to
    customize model behavior beyond defaults.

    Args:
        model_name: The scvi-tools model name in lowercase (e.g. 'scvi', 'totalvi').
    """
    try:
        knowledge_dir = utils.get_knowledge_dir()
        api_file = knowledge_dir / "api" / f"{model_name}.md"
        if not api_file.exists():
            api_file = knowledge_dir / "models" / f"{model_name}.md"
        if not api_file.exists():
            return ModelGuidanceResult(error=f"API reference for '{model_name}' not found.")
        content = api_file.read_text(encoding="utf-8")
        result = utils.truncate(content)
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))
