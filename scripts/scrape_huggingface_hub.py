"""Scrape the scvi-tools Hugging Face Hub model registry into bundled knowledge files.

The scraper records public model metadata only. It does not download model weights,
AnnData/MuData files, TensorBoard logs, or model-card contents.

Usage:
    python scripts/scrape_huggingface_hub.py
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

HUGGINGFACE_ORG_URL = "https://huggingface.co/scvi-tools"
HUGGINGFACE_API_URL = (
    "https://huggingface.co/api/models?author=scvi-tools&full=false&sort=lastModified&direction=-1&limit=200"
)
KNOWLEDGE_HUB = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/hub"


def _tag_values(tags: list[str], prefix: str) -> list[str]:
    needle = f"{prefix}:"
    return [tag[len(needle) :] for tag in tags if tag.startswith(needle)]


def _first_tag_value(tags: list[str], prefix: str) -> str | None:
    values = _tag_values(tags, prefix)
    return values[0] if values else None


def normalize_model(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize one Hugging Face model response into the bundled snapshot schema."""

    model_id = raw.get("modelId") or raw.get("id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError(f"Missing Hugging Face model id in response: {raw!r}")

    tags = raw.get("tags") or []
    if not isinstance(tags, list):
        raise ValueError(f"Expected tags list for {model_id}")
    tags = [str(tag) for tag in tags]

    annotated_value = _first_tag_value(tags, "annotated")
    annotated = None if annotated_value is None else annotated_value.lower() == "true"
    siblings = raw.get("siblings") or []
    files = [str(item.get("rfilename")) for item in siblings if isinstance(item, dict) and item.get("rfilename")]

    return {
        "model_id": model_id,
        "url": f"https://huggingface.co/{model_id}",
        "model_class": _first_tag_value(tags, "model_cls_name"),
        "modalities": _tag_values(tags, "modality"),
        "tissues": _tag_values(tags, "tissue"),
        "annotated": annotated,
        "scvi_version": _first_tag_value(tags, "scvi_version"),
        "anndata_version": _first_tag_value(tags, "anndata_version"),
        "license": _first_tag_value(tags, "license"),
        "downloads": int(raw.get("downloads") or 0),
        "likes": int(raw.get("likes") or 0),
        "last_modified": raw.get("lastModified"),
        "created_at": raw.get("createdAt"),
        "files": files,
    }


def build_snapshot(raw_models: list[dict[str, Any]], fetched_at: str | None = None) -> dict[str, Any]:
    """Build the normalized hub snapshot document."""

    fetched_at = fetched_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    models = [normalize_model(raw) for raw in raw_models]
    models.sort(key=lambda model: model.get("last_modified") or "", reverse=True)
    return {
        "fetched_at": fetched_at,
        "source_url": HUGGINGFACE_ORG_URL,
        "api_url": HUGGINGFACE_API_URL,
        "models": models,
    }


def _count_values(models: list[dict[str, Any]], field: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for model in models:
        value = model.get(field)
        if isinstance(value, list):
            counts.update(str(item) for item in value if item)
        elif value:
            counts[str(value)] += 1
    return counts


def _format_counts(counts: Counter[str]) -> list[str]:
    if not counts:
        return ["- unknown: 0"]
    return [f"- {name}: {count}" for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def build_summary(snapshot: dict[str, Any]) -> str:
    """Build a Markdown summary for broad knowledge search."""

    models = snapshot.get("models") or []
    if not isinstance(models, list):
        raise ValueError("Snapshot field 'models' must be a list")

    class_counts = _count_values(models, "model_class")
    modality_counts = _count_values(models, "modalities")
    tissue_counts = _count_values(models, "tissues")
    annotated_count = sum(1 for model in models if model.get("annotated") is True)
    unannotated_count = sum(1 for model in models if model.get("annotated") is False)
    recent_models = models[:10]

    lines = [
        "# scvi-tools Hugging Face Hub Snapshot",
        "",
        f"Fetched {len(models)} public model repos from {snapshot.get('source_url', HUGGINGFACE_ORG_URL)}.",
        "",
        f"**Fetched at:** {snapshot.get('fetched_at', 'unknown')}",
        "",
        "The snapshot is bundled for offline MCP use. Runtime tools do not call Hugging Face.",
        "",
        "## Model Classes",
        "",
        *_format_counts(class_counts),
        "",
        "## Modalities",
        "",
        *_format_counts(modality_counts),
        "",
        "## Annotation Status",
        "",
        f"- annotated: {annotated_count}",
        f"- not annotated: {unannotated_count}",
        "",
        "## Top Tissues",
        "",
        *_format_counts(Counter(dict(tissue_counts.most_common(15)))),
        "",
        "## Recently Modified",
        "",
    ]
    for model in recent_models:
        model_id = model.get("model_id", "unknown")
        model_class = model.get("model_class") or "unknown"
        tissues = ", ".join(model.get("tissues") or []) or "unspecified tissue"
        modalities = ", ".join(model.get("modalities") or []) or "unspecified modality"
        lines.append(f"- {model_id} ({model_class}; {modalities}; {tissues})")

    lines += [
        "",
        "## Usage Notes",
        "",
        "- Use the dedicated hub tools to filter by model class, modality, tissue, and annotation status.",
        "- Check the linked Hugging Face repo and scvi-tools model class before loading a pretrained model.",
        "- In scvi-tools, use the appropriate model class with `load_from_hub()` when the repo matches the analysis.",
    ]
    return "\n".join(lines) + "\n"


def fetch_models() -> list[dict[str, Any]]:
    """Fetch public scvi-tools model metadata from Hugging Face."""

    response = requests.get(HUGGINGFACE_API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Expected Hugging Face API to return a list of models")
    return data


def write_snapshot(snapshot: dict[str, Any], output_dir: Path = KNOWLEDGE_HUB) -> None:
    """Write normalized JSON and Markdown summary files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "models.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(build_summary(snapshot), encoding="utf-8")


def run() -> None:
    print("Fetching scvi-tools Hugging Face Hub metadata...")
    snapshot = build_snapshot(fetch_models())
    write_snapshot(snapshot)
    print(f"  wrote {KNOWLEDGE_HUB / 'models.json'}")
    print(f"  wrote {KNOWLEDGE_HUB / 'summary.md'}")
    print(f"Done. Captured {len(snapshot['models'])} model repos.")


if __name__ == "__main__":
    run()
