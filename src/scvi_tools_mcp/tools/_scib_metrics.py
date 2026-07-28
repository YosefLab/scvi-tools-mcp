from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils

ScibMetricName = Literal[
    "isolated_labels",
    "nmi_ari_cluster_labels_kmeans",
    "nmi_ari_cluster_labels_leiden",
    "pcr_comparison",
    "silhouette_label",
    "silhouette_batch",
    "bras",
    "ilisi_knn",
    "clisi_knn",
    "kbet",
    "kbet_per_label",
    "graph_connectivity",
    "benchmarker",
    "bioconservation",
    "batchcorrection",
]

METRIC_CATEGORIES: dict[str, list[str]] = {
    "bio_conservation": [
        "isolated_labels",
        "nmi_ari_cluster_labels_leiden",
        "nmi_ari_cluster_labels_kmeans",
        "silhouette_label",
        "clisi_knn",
    ],
    "batch_correction": [
        "bras",
        "ilisi_knn",
        "kbet",
        "kbet_per_label",
        "graph_connectivity",
        "pcr_comparison",
        "silhouette_batch",
    ],
}

BENCHMARK_ENTRIES = ["benchmarker", "bioconservation", "batchcorrection"]


class ScibMetricsResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


def _scib_metrics_dir() -> Path:
    return utils.get_knowledge_dir() / "scib_metrics"


@mcp.tool()
def list_scib_metrics() -> ScibMetricsResult:
    """List the integration-benchmarking metrics and orchestration classes exposed by scib-metrics.

    scib-metrics is an accelerated reimplementation of the scIB benchmarking suite, grouping
    12 metric functions into bio-conservation and batch-correction categories, plus a
    Benchmarker/BioConservation/BatchCorrection orchestration layer. Use get_scib_metric
    for details on any entry returned here.
    """
    try:
        lines = ["# scib-metrics Metrics", ""]
        lines.append("## Bio Conservation")
        for name in METRIC_CATEGORIES["bio_conservation"]:
            lines.append(f"- **{name}**")
        lines.append("")
        lines.append("## Batch Correction")
        for name in METRIC_CATEGORIES["batch_correction"]:
            lines.append(f"- **{name}**")
        lines.append("")
        lines.append("## Orchestration")
        for name in BENCHMARK_ENTRIES:
            lines.append(f"- **{name}**")
        result = utils.truncate("\n".join(lines))
        return ScibMetricsResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ScibMetricsResult(error=str(e))


@mcp.tool()
def get_scib_metric(metric_name: ScibMetricName) -> ScibMetricsResult:
    """Get the API reference for one scib-metrics metric function or benchmark class.

    Args:
        metric_name: A metric or orchestration entry, e.g. isolated_labels, ilisi_knn,
            kbet, benchmarker, bioconservation, batchcorrection. Case-insensitive.
    """
    try:
        key = metric_name.lower()
        path = _scib_metrics_dir() / "api" / f"{key}.md"
        if not path.exists():
            return ScibMetricsResult(
                error=f"scib-metrics entry '{metric_name}' not found. Call list_scib_metrics() for options."
            )
        result = utils.truncate(path.read_text(encoding="utf-8"))
        return ScibMetricsResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ScibMetricsResult(error=str(e))


@mcp.tool()
def list_scib_metrics_tutorials() -> ScibMetricsResult:
    """List available scib-metrics tutorials, converted from the package's own notebooks."""
    try:
        base = _scib_metrics_dir() / "tutorials"
        if not base.exists():
            return ScibMetricsResult(error="scib-metrics tutorial knowledge not found.")
        lines = ["# scib-metrics Tutorials", ""]
        for md in sorted(base.glob("*.md")):
            lines.append(f"- `{md.stem}` — use get_scib_metrics_tutorial(tutorial_name='{md.stem}')")
        result = utils.truncate("\n".join(lines))
        return ScibMetricsResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ScibMetricsResult(error=str(e))


@mcp.tool()
def get_scib_metrics_tutorial(tutorial_name: str, page: int = 1, page_size: int = 200) -> ScibMetricsResult:
    """Read the full content of a scib-metrics tutorial.

    Args:
        tutorial_name: Tutorial name from list_scib_metrics_tutorials, e.g. 'lung_example'.
        page: Page number starting at 1.
        page_size: Lines per page (default 200).
    """
    try:
        base = _scib_metrics_dir() / "tutorials"
        path = base / f"{tutorial_name}.md"
        if not path.exists():
            return ScibMetricsResult(
                error=f"scib-metrics tutorial '{tutorial_name}' not found. Call list_scib_metrics_tutorials() first."
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        result = utils.paginate(lines, page=page, page_size=page_size)
        return ScibMetricsResult(
            content="\n".join(result.lines),
            page=result.page,
            total_pages=result.total_pages,
            truncated=result.total_pages > 1,
        )
    except Exception as e:
        return ScibMetricsResult(error=str(e))
