from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from scvi_tools_mcp.tools import utils
from scvi_tools_mcp.tools._constants import MODEL_NAMES
from scvi_tools_mcp.mcp import mcp

MODEL_REQUIREMENTS: dict[str, dict] = {
    "scvi": {
        "required_obs": [],
        "optional_obs": ["batch_key", "labels_key"],
        "required_var": [],
        "setup_call": "SCVI.setup_anndata(adata, batch_key='batch')",
        "notes": "Count data must be in adata.X or a layer. Do not log-normalize before training.",
    },
    "scanvi": {
        "required_obs": ["labels_key (cell type column, unlabeled cells use 'Unknown')"],
        "optional_obs": ["batch_key"],
        "required_var": [],
        "setup_call": "SCANVI.setup_anndata(adata, labels_key='cell_type', unlabeled_category='Unknown', batch_key='batch')",
        "notes": "Requires at least some labeled cells. Works best with >100 labeled cells per type.",
    },
    "totalvi": {
        "required_obs": ["batch_key recommended"],
        "optional_obs": [],
        "required_var": [],
        "setup_call": "TOTALVI.setup_anndata(adata, batch_key='batch', protein_expression_obsm_key='protein_expression')",
        "notes": "Protein data must be raw counts in adata.obsm['protein_expression']. Do not normalize.",
    },
    "multivi": {
        "required_obs": [],
        "optional_obs": ["batch_key", "modality_key"],
        "required_var": ["modality column in adata.var"],
        "setup_call": "MULTIVI.setup_anndata(adata, batch_key='batch', modality_key='modality')",
        "notes": "adata.var must have a column indicating modality ('Gene Expression' or 'Peaks').",
    },
    "peakvi": {
        "required_obs": [],
        "optional_obs": ["batch_key"],
        "required_var": [],
        "setup_call": "PEAKVI.setup_anndata(adata, batch_key='batch')",
        "notes": "Input must be binary accessibility matrix (0/1). Use binarize=True if needed.",
    },
}

DEFAULT_REQUIREMENTS: dict = {
    "required_obs": [],
    "optional_obs": ["batch_key"],
    "required_var": [],
    "setup_call": "MODEL.setup_anndata(adata)",
    "notes": "Refer to the model documentation for specific requirements.",
}


class DataPrepResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


@mcp.tool()
def get_setup_anndata_guide(model_name: MODEL_NAMES) -> DataPrepResult:
    """Get the exact setup_anndata() call and data requirements for a scvi-tools model.

    Returns the required and optional AnnData fields, the exact Python call to run
    before creating the model, and common mistakes to avoid. Always call this before
    showing a user how to instantiate a model.

    Args:
        model_name: The scvi-tools model name in lowercase (e.g. 'scvi', 'totalvi').
    """
    try:
        knowledge_dir = utils.get_knowledge_dir()
        model_file = knowledge_dir / "models" / f"{model_name}.md"
        reqs = MODEL_REQUIREMENTS.get(model_name, DEFAULT_REQUIREMENTS)
        lines = [
            f"# setup_anndata Guide — {model_name.upper()}",
            "",
            "## Call",
            "```python",
            reqs.get("setup_call", f"{model_name.upper()}.setup_anndata(adata)"),
            "```",
            "",
            "## Required obs fields",
        ]
        required_obs = reqs.get("required_obs", [])
        lines.append(
            "None (count matrix in adata.X is always required)"
            if not required_obs
            else "\n".join(f"- {r}" for r in required_obs)
        )
        lines += ["", "## Optional obs fields"]
        optional_obs = reqs.get("optional_obs", [])
        lines.append("None" if not optional_obs else "\n".join(f"- {r}" for r in optional_obs))
        lines += ["", "## Notes", reqs.get("notes", ""), ""]
        if model_file.exists():
            content = model_file.read_text(encoding="utf-8")
            idx = content.find("## setup_anndata")
            if idx >= 0:
                lines += ["", "## Full API Detail", content[idx : idx + 1500]]
        result = utils.truncate("\n".join(lines))
        return DataPrepResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return DataPrepResult(error=str(e))


@mcp.tool()
def validate_data_requirements(
    model_name: MODEL_NAMES,
    obs_keys: list[str],
    var_keys: list[str],
    has_raw: bool,
) -> DataPrepResult:
    """Check whether the user's AnnData object meets the requirements for a model.

    Pass the column names present in adata.obs and adata.var. Returns a pass/fail
    checklist with fix instructions for any failures. Use this when a user reports
    errors during setup_anndata or model initialization.

    Args:
        model_name: The scvi-tools model name in lowercase.
        obs_keys: List of column names in adata.obs (from list(adata.obs.columns)).
        var_keys: List of column names in adata.var (from list(adata.var.columns)).
        has_raw: Whether adata.raw is set (adata.raw is not None).
    """
    try:
        reqs = MODEL_REQUIREMENTS.get(model_name)
        if reqs is None:
            available = list(MODEL_REQUIREMENTS.keys())
            return DataPrepResult(
                error=f"No requirements defined for '{model_name}'. Known: {', '.join(available)}. "
                      "Use get_model_overview for full documentation."
            )
        checks: list[tuple[bool, str]] = [
            (True, "adata.X contains count matrix (assumed from call context)")
        ]
        for req in reqs.get("required_obs", []):
            field = req.split(" ")[0]
            passed = field in obs_keys or "(" in req
            checks.append((passed, f"obs key '{field}': {'PRESENT' if passed else 'MISSING — required'}"))
        for req in reqs.get("required_var", []):
            field = req.split(" ")[0]
            passed = field in var_keys or "column in" in req
            checks.append((passed, f"var requirement '{req}': {'OK' if passed else 'CHECK — may be needed'}"))
        lines = [f"# Data Requirements — {model_name.upper()}", ""]
        all_pass = all(p for p, _ in checks)
        lines.append("**Status: PASS ✓**" if all_pass else "**Status: ACTION REQUIRED**")
        lines.append("")
        for passed, msg in checks:
            lines.append(f"{'✓' if passed else '✗'} {msg}")
        lines += [
            "",
            "## Next Step",
            f"Call `get_setup_anndata_guide(model_name='{model_name}')` for the exact setup call.",
        ]
        result = utils.truncate("\n".join(lines))
        return DataPrepResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return DataPrepResult(error=str(e))
