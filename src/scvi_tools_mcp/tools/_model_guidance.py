from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from scvi_tools_mcp.tools import utils
from scvi_tools_mcp.mcp import mcp

MODEL_NAMES = Literal[
    "amortizedlda","autozi","cellassign","contrastivevi","cytovi",
    "decipher","destvi","diagvi","gimvi","linearscvi","methylanvi",
    "methylvi","mrvi","multivi","peakvi","poissonvi","resolvi",
    "scanvi","scar","scbasset","scvi","scviva","solo","stereoscope",
    "sysvi","tangram","totalanvi","totalvi","velovi"
]

TASK_MODEL_MAP: dict[str, list[str]] = {
    "batch_integration": ["scvi", "scanvi", "sysvi", "linearscvi"],
    "dimensionality_reduction": ["scvi", "multivi", "totalvi"],
    "differential_expression": ["scvi", "scanvi", "totalvi", "autozi"],
    "cell_type_annotation": ["scanvi", "cellassign", "solo"],
    "deconvolution": ["destvi", "stereoscope", "tangram"],
    "spatial_mapping": ["tangram", "destvi", "gimvi", "scviva"],
    "chromatin_accessibility": ["peakvi", "poissonvi", "scbasset", "multivi"],
    "multimodal_integration": ["totalvi", "multivi"],
    "reference_mapping": ["scanvi"],
    "perturbation_modeling": ["contrastivevi", "mrvi"],
}

DATA_TYPE_HINTS: dict[str, str] = {
    "scrna": "For scRNA-seq, start with scVI for batch integration or SCANVI if you have cell type labels.",
    "cite_seq": "For CITE-seq (RNA + protein), use TotalVI.",
    "spatial": "For spatial transcriptomics, consider DestVI or Tangram for deconvolution.",
    "atac": "For scATAC-seq, use PeakVI or SCBASSET.",
    "multiome": "For RNA+ATAC multiome data, use MultiVI.",
    "cytometry": "For cytometry data, use CytoVI.",
    "methylation": "For methylation data, use MethylVI or MethylANVI.",
}


class ModelGuidanceResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


@mcp.tool()
def recommend_model(
    task: Literal[
        "batch_integration","dimensionality_reduction","differential_expression",
        "cell_type_annotation","deconvolution","spatial_mapping",
        "chromatin_accessibility","multimodal_integration","reference_mapping",
        "perturbation_modeling"
    ],
    data_type: Literal["scrna","cite_seq","spatial","atac","multiome","cytometry","methylation"],
    has_protein: bool,
    has_accessibility: bool,
    n_batches: int,
) -> ModelGuidanceResult:
    """Recommend scvi-tools models ranked by suitability for the user's task and data type.

    Call this first when a user describes what they want to do. Returns a ranked list of
    model names with a short rationale for each. Use get_model_overview to get details
    on any recommended model.

    Args:
        task: The analysis goal.
        data_type: The type of single-cell data.
        has_protein: True if the data includes protein (ADT) measurements.
        has_accessibility: True if the data includes chromatin accessibility (ATAC).
        n_batches: Number of batches/donors. Use 1 if data is from a single batch.
    """
    try:
        candidates = list(TASK_MODEL_MAP.get(task, ["scvi"]))
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
            lines.append(f"{i}. **{name.upper()}** — use `get_model_overview(model_name='{name}')` for details.")
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
            available = sorted(p.stem for p in (knowledge_dir / "models").glob("*.md"))
            return ModelGuidanceResult(
                error=f"Model '{model_name}' not found. Available: {', '.join(available)}"
            )
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
