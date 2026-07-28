"""Extract docstrings and signatures from scvi-tools public API into Markdown files.

Requires scvi-tools installed: pip install scvi-tools-mcp[scvi]

Usage:
    python scripts/extract_api_docs.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from scripts._apidoc_utils import merge_with_user_guide, render_doc, resolve_dotted
except ImportError:  # running as `python scripts/extract_api_docs.py`, not as a package
    from _apidoc_utils import merge_with_user_guide, render_doc, resolve_dotted

KNOWLEDGE_MODELS = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/models"
KNOWLEDGE_API = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/api"

MODEL_CLASSES = {
    "scvi": "scvi.model.SCVI",
    "scanvi": "scvi.model.SCANVI",
    "totalvi": "scvi.model.TOTALVI",
    "multivi": "scvi.model.MULTIVI",
    "peakvi": "scvi.model.PEAKVI",
    "poissonvi": "scvi.model.POISSONVI",
    "autozi": "scvi.model.AutoZI",
    "linearscvi": "scvi.model.LinearSCVI",
    "mrvi": "scvi.external.MRVI",
    "destvi": "scvi.external.DestVI",
    "stereoscope": "scvi.external.RNAStereoscope",
    "cellassign": "scvi.external.CellAssign",
    "tangram": "scvi.external.Tangram",
    "solo": "scvi.external.SOLO",
    "gimvi": "scvi.external.GIMVI",
    "velovi": "scvi.external.VELOVI",
    "contrastivevi": "scvi.external.ContrastiveVI",
    "scbasset": "scvi.external.SCBASSET",
    "sysvi": "scvi.external.SysVI",
    "amortizedlda": "scvi.external.AmortizedLDA",
    "resolvi": "scvi.external.ResolVI",
}


EXTRA_METHODS = ("setup_anndata", "train")


def run(docs_dir: Path | None = None) -> None:
    KNOWLEDGE_MODELS.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_API.mkdir(parents=True, exist_ok=True)

    for model_name, dotted in MODEL_CLASSES.items():
        cls = resolve_dotted(dotted)
        if cls is None:
            print(f"  SKIP (not found): {dotted}")
            continue
        md = render_doc(model_name.upper(), [cls], extra_methods=EXTRA_METHODS)

        out_api = KNOWLEDGE_API / f"{model_name}.md"
        out_api.write_text(md, encoding="utf-8")

        merged = merge_with_user_guide(model_name, md, docs_dir)
        out_model = KNOWLEDGE_MODELS / f"{model_name}.md"
        out_model.write_text(merged, encoding="utf-8")
        print(f"  wrote: {out_model.name}")

    print("Done.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract API docs from scvi-tools")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Directory containing fetched scvi-tools user guide docs (subdirs: models/, use_case/)",
    )
    args = parser.parse_args()
    run(docs_dir=args.docs_dir)
