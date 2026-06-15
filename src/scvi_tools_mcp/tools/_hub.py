from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils


class HubResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


def _load_snapshot() -> dict:
    hub_file = utils.get_knowledge_dir() / "hub" / "models.json"
    if not hub_file.exists():
        raise utils.KnowledgeNotFoundError(
            "Hub knowledge file missing. Run scripts/scrape_huggingface_hub.py to rebuild."
        )
    snapshot = json.loads(hub_file.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("models"), list):
        raise ValueError("Malformed hub snapshot: expected a JSON object with a 'models' list.")
    return snapshot


def _as_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]


def _matches_text(values: list[str], query: str | None) -> bool:
    if query is None:
        return True
    query = query.lower()
    return any(query in value.lower() for value in values)


def _matches(
    model: dict,
    model_class: str | None = None,
    modality: str | None = None,
    tissue: str | None = None,
    annotated: bool | None = None,
) -> bool:
    if model_class is not None and str(model.get("model_class") or "").lower() != model_class.lower():
        return False
    if not _matches_text(_as_list(model.get("modalities")), modality):
        return False
    if not _matches_text(_as_list(model.get("tissues")), tissue):
        return False
    if annotated is not None and model.get("annotated") is not annotated:
        return False
    return True


def _join(values: list[str]) -> str:
    return ", ".join(values) if values else "unspecified"


def _format_model_row(model: dict, index: int) -> str:
    model_id = model.get("model_id", "unknown")
    model_class = model.get("model_class") or "unknown"
    modalities = _join(_as_list(model.get("modalities")))
    tissues = _join(_as_list(model.get("tissues")))
    annotated = "annotated" if model.get("annotated") is True else "not annotated"
    version = model.get("scvi_version") or "unknown scvi version"
    url = model.get("url") or f"https://huggingface.co/{model_id}"
    return f"{index}. **{model_id}** — {model_class}; {modalities}; {tissues}; {annotated}; scvi-tools {version}; {url}"


def _format_detail(model: dict) -> str:
    model_id = model.get("model_id", "unknown")
    model_class = model.get("model_class") or "unknown"
    modalities = _join(_as_list(model.get("modalities")))
    tissues = _join(_as_list(model.get("tissues")))
    files = _join(_as_list(model.get("files")))
    annotated = "Yes" if model.get("annotated") is True else "No"
    url = model.get("url") or f"https://huggingface.co/{model_id}"
    return "\n".join(
        [
            f"# Hugging Face Hub Model: {model_id}",
            "",
            f"**URL:** {url}",
            f"**Model class:** {model_class}",
            f"**Modalities:** {modalities}",
            f"**Tissues:** {tissues}",
            f"**Annotated:** {annotated}",
            f"**scvi-tools version:** {model.get('scvi_version') or 'unknown'}",
            f"**AnnData version:** {model.get('anndata_version') or 'unknown'}",
            f"**License:** {model.get('license') or 'unknown'}",
            f"**Last modified:** {model.get('last_modified') or 'unknown'}",
            f"**Downloads:** {model.get('downloads', 0)} | **Likes:** {model.get('likes', 0)}",
            "",
            "## Files",
            "",
            files,
            "",
            "## Usage Guidance",
            "",
            "This MCP server does not download or execute the model. Inspect the Hugging Face repo and load it "
            "from scvi-tools only when your query data matches the model class, modality, feature space, and "
            "expected setup.",
            "",
            "```python",
            "import scvi",
            "",
            f'model = scvi.model.{model_class}.load_from_hub("{model_id}")',
            "```",
        ]
    )


def _task_score(model: dict, task: str) -> tuple[int, list[str]]:
    model_class = str(model.get("model_class") or "")
    model_id = str(model.get("model_id") or "")
    modalities = _as_list(model.get("modalities"))
    annotated = model.get("annotated") is True
    score = 0
    reasons: list[str] = []

    if task in {"label_transfer", "reference_mapping"}:
        if model_class == "SCANVI":
            score += 120
            reasons.append("SCANVI is preferred for label-aware reference mapping.")
        elif model_class == "SCVI":
            score += 80
            reasons.append("SCVI can provide query embeddings for reference workflows.")
        if annotated:
            score += 30
            reasons.append("The repo is annotated.")
    elif task == "query_embedding":
        if model_class == "SCVI":
            score += 120
            reasons.append("SCVI is a strong default for latent query embeddings.")
        elif model_class == "SCANVI":
            score += 70
            reasons.append("SCANVI can embed queries when label-transfer assumptions match.")
    elif task == "cite_seq":
        if model_class == "TOTALVI":
            score += 130
            reasons.append("TOTALVI is designed for paired RNA and protein CITE-seq data.")
        if "protein" in [modality.lower() for modality in modalities]:
            score += 50
            reasons.append("The repo includes protein modality metadata.")
    elif task == "spatial_deconvolution":
        if model_class == "RNAStereoscope":
            score += 120
            reasons.append("RNAStereoscope is a spatial deconvolution model component.")
        elif model_class == "CondSCVI":
            score += 100
            reasons.append("CondSCVI pairs with Stereoscope-style deconvolution workflows.")
    elif task == "example_usage":
        if "test" in model_id:
            score += 120
            reasons.append("This is an example/test repo for HubModel loading mechanics.")
        else:
            score += 20
            reasons.append("This repo can be inspected as a real pretrained model example.")

    if task != "example_usage" and "test" in model_id:
        score -= 100
        reasons.append("Test repos are examples, not biological references.")
    score += int(model.get("likes") or 0)
    score += min(int(model.get("downloads") or 0), 20)
    return score, reasons


def _score_model(model: dict, task: str, modality: str | None, tissue: str | None) -> tuple[int, list[str]]:
    score, reasons = _task_score(model, task)
    if modality is not None and _matches_text(_as_list(model.get("modalities")), modality):
        score += 35
        reasons.append(f"Matches requested modality '{modality}'.")
    if tissue is not None and _matches_text(_as_list(model.get("tissues")), tissue):
        score += 35
        reasons.append(f"Matches requested tissue '{tissue}'.")
    return score, reasons


@mcp.tool()
def list_hub_models(
    model_class: str | None = None,
    modality: str | None = None,
    tissue: str | None = None,
    annotated: bool | None = None,
    page: int = 1,
    page_size: int = 25,
) -> HubResult:
    """List pretrained scvi-tools models from the bundled Hugging Face Hub snapshot.

    Use this when a user asks what pretrained scvi-tools HubModels exist, or wants to
    filter the official scvi-tools Hugging Face organization by model class, modality,
    tissue, or annotation status. This tool does not call Hugging Face at runtime.

    Args:
        model_class: Optional class filter, e.g. SCVI, SCANVI, TOTALVI, CondSCVI, RNAStereoscope.
        modality: Optional modality filter, e.g. rna or protein.
        tissue: Optional tissue substring filter, e.g. lung or thymus.
        annotated: Optional annotation-status filter.
        page: Result page, starting at 1.
        page_size: Number of models per page.
    """
    try:
        snapshot = _load_snapshot()
        models = [
            model
            for model in snapshot["models"]
            if _matches(model, model_class=model_class, modality=modality, tissue=tissue, annotated=annotated)
        ]
        page_size = min(max(page_size, 1), 100)
        paged = utils.paginate(models, page=page, page_size=page_size)
        filters = [
            f"model_class={model_class}" if model_class else None,
            f"modality={modality}" if modality else None,
            f"tissue={tissue}" if tissue else None,
            f"annotated={annotated}" if annotated is not None else None,
        ]
        filters_text = ", ".join(item for item in filters if item) or "none"
        lines = [
            "# scvi-tools Hugging Face Hub Models",
            "",
            f"**Source:** {snapshot.get('source_url', 'https://huggingface.co/scvi-tools')}",
            f"**Fetched at:** {snapshot.get('fetched_at', 'unknown')}",
            f"**Filters:** {filters_text}",
            f"**Matches:** {len(models)}",
            "",
        ]
        if not models:
            lines.append("No hub models matched the provided filters.")
        else:
            start = (paged.page - 1) * page_size
            lines.extend(_format_model_row(model, start + offset) for offset, model in enumerate(paged.lines, 1))
        result = utils.truncate("\n".join(lines))
        return HubResult(
            content=result.content,
            truncated=result.truncated,
            page=paged.page,
            total_pages=paged.total_pages,
        )
    except Exception as e:
        return HubResult(error=str(e))


@mcp.tool()
def get_hub_model(model_id: str) -> HubResult:
    """Get metadata and loading guidance for one scvi-tools Hugging Face Hub model.

    Use this after list_hub_models or suggest_hub_models when a user needs details for
    a specific pretrained repo. The response includes the Hugging Face URL and files
    available in the repo, but it does not fetch or download those files.

    Args:
        model_id: Hugging Face model id, e.g. scvi-tools/heart-cell-atlas-scvi.
    """
    try:
        snapshot = _load_snapshot()
        requested = model_id if "/" in model_id else f"scvi-tools/{model_id}"
        for model in snapshot["models"]:
            if model.get("model_id") == requested:
                result = utils.truncate(_format_detail(model))
                return HubResult(content=result.content, truncated=result.truncated)
        available = ", ".join(str(model.get("model_id")) for model in snapshot["models"][:8])
        return HubResult(error=f"Hub model '{model_id}' not found. Examples: {available}")
    except Exception as e:
        return HubResult(error=str(e))


@mcp.tool()
def suggest_hub_models(
    task: Literal[
        "reference_mapping",
        "label_transfer",
        "query_embedding",
        "cite_seq",
        "spatial_deconvolution",
        "example_usage",
    ],
    modality: str | None = None,
    tissue: str | None = None,
    require_annotated: bool = False,
    limit: int = 5,
) -> HubResult:
    """Suggest pretrained scvi-tools HubModels for an analysis task.

    Use this when a user wants an appropriate pretrained model from the official
    scvi-tools Hugging Face hub. Suggestions are metadata-based: verify biological
    compatibility, feature space, and model-card guidance before loading any model.

    Args:
        task: The intended use for the pretrained hub model.
        modality: Optional modality preference, e.g. rna or protein.
        tissue: Optional tissue preference, e.g. lung or heart.
        require_annotated: If true, only consider repos tagged annotated:True.
        limit: Maximum number of suggestions to return.
    """
    try:
        snapshot = _load_snapshot()
        candidates = []
        for model in snapshot["models"]:
            if require_annotated and model.get("annotated") is not True:
                continue
            if modality is not None and not _matches_text(_as_list(model.get("modalities")), modality):
                continue
            score, reasons = _score_model(model, task, modality=modality, tissue=tissue)
            if score > 0:
                candidates.append((score, model, reasons))
        candidates.sort(key=lambda item: (item[0], item[1].get("last_modified") or ""), reverse=True)
        limit = min(max(limit, 1), 25)
        lines = [
            "# Suggested scvi-tools Hub Models",
            "",
            f"**Task:** {task}",
            f"**Modality:** {modality or 'any'}",
            f"**Tissue:** {tissue or 'any'}",
            f"**Require annotated:** {require_annotated}",
            "",
        ]
        if not candidates:
            lines.append("No hub models matched the requested task and filters.")
        for index, (score, model, reasons) in enumerate(candidates[:limit], 1):
            reason = " ".join(reasons[:3]) or "Metadata matched the requested task."
            model_id = model.get("model_id", "unknown")
            model_class = model.get("model_class") or "unknown"
            tissues = _join(_as_list(model.get("tissues")))
            modalities = _join(_as_list(model.get("modalities")))
            lines.append(f"{index}. **{model_id}** — {model_class}; {modalities}; {tissues}; score {score}. {reason}")
            lines.append(f"   URL: {model.get('url') or f'https://huggingface.co/{model_id}'}")
        result = utils.truncate("\n".join(lines))
        return HubResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return HubResult(error=str(e))
