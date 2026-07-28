"""Extract docstrings and signatures from scib-metrics public API into Markdown files.

Requires scib-metrics installed: pip install scvi-tools-mcp[scib]

Usage:
    python scripts/extract_scib_metrics_api_docs.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from scripts._apidoc_utils import render_doc, resolve_dotted
except ImportError:  # running as `python scripts/extract_scib_metrics_api_docs.py`, not as a package
    from _apidoc_utils import render_doc, resolve_dotted

KNOWLEDGE_API = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/scib_metrics/api"

# Top-level metric functions exported from scib_metrics.__init__.
METRIC_FUNCTIONS: list[str] = [
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
]

# High-level orchestration classes in scib_metrics.benchmark.
BENCHMARK_CLASSES: dict[str, list[str]] = {
    "benchmarker": ["scib_metrics.benchmark.Benchmarker"],
    "bioconservation": ["scib_metrics.benchmark.BioConservation"],
    "batchcorrection": ["scib_metrics.benchmark.BatchCorrection"],
}

BENCHMARKER_EXTRA_METHODS = ("prepare", "benchmark", "get_results", "plot_results_table")


def run() -> None:
    KNOWLEDGE_API.mkdir(parents=True, exist_ok=True)

    for metric_name in METRIC_FUNCTIONS:
        func = resolve_dotted(f"scib_metrics.{metric_name}")
        if func is None:
            print(f"  SKIP (not found): scib_metrics.{metric_name}")
            continue
        md = render_doc(metric_name.upper(), [func])
        out = KNOWLEDGE_API / f"{metric_name}.md"
        out.write_text(md, encoding="utf-8")
        print(f"  wrote: {out.name}")

    for entry_name, dotted_paths in BENCHMARK_CLASSES.items():
        classes = [resolve_dotted(dotted) for dotted in dotted_paths]
        classes = [cls for cls in classes if cls is not None]
        if not classes:
            print(f"  SKIP (not found): {dotted_paths}")
            continue
        extra_methods = BENCHMARKER_EXTRA_METHODS if entry_name == "benchmarker" else ()
        md = render_doc(entry_name.upper(), classes, extra_methods=extra_methods)
        out = KNOWLEDGE_API / f"{entry_name}.md"
        out.write_text(md, encoding="utf-8")
        print(f"  wrote: {out.name}")

    print("Done.")


if __name__ == "__main__":
    run()
