"""Extract docstrings and signatures from scviva-tools public API into Markdown files.

Requires scviva-tools installed: pip install scvi-tools-mcp[scviva]

Usage:
    python scripts/extract_scviva_api_docs.py --docs-dir /tmp/scviva-tools/docs/user_guide
"""

from __future__ import annotations

from pathlib import Path

try:
    from scripts._apidoc_utils import merge_with_user_guide, render_doc, resolve_dotted
except ImportError:  # running as `python scripts/extract_scviva_api_docs.py`, not as a package
    from _apidoc_utils import merge_with_user_guide, render_doc, resolve_dotted

KNOWLEDGE_MODELS = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/scviva_tools/models"
KNOWLEDGE_API = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/scviva_tools/api"

# scviva-tools does not put every model under `scviva.model` — DiagVI and Tangram live
# under `scviva.external`, Harreman under `scviva.tools.harreman`, and Stereoscope
# exposes two separate classes (RNAStereoscope, SpatialStereoscope) sharing one entry.
MODEL_CLASSES: dict[str, list[str]] = {
    "resolvi": ["scviva.model.ResolVI"],
    "destvi": ["scviva.model.DestVI"],
    "scviva": ["scviva.model.SCVIVA"],
    "gimvi": ["scviva.model.GIMVI"],
    "diagvi": ["scviva.external.DIAGVI"],
    "stereoscope": [
        "scviva.external.stereoscope.RNAStereoscope",
        "scviva.external.stereoscope.SpatialStereoscope",
    ],
    "tangram": ["scviva.external.tangram.Tangram"],
    "harreman": ["scviva.tools.harreman.HarremanAnalysis"],
}

EXTRA_METHODS = ("setup_anndata", "train")


def run(docs_dir: Path | None = None) -> None:
    KNOWLEDGE_MODELS.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_API.mkdir(parents=True, exist_ok=True)

    for model_name, dotted_paths in MODEL_CLASSES.items():
        classes = [resolve_dotted(dotted) for dotted in dotted_paths]
        classes = [cls for cls in classes if cls is not None]
        if not classes:
            print(f"  SKIP (not found): {dotted_paths}")
            continue
        md = render_doc(model_name.upper(), classes, extra_methods=EXTRA_METHODS)

        out_api = KNOWLEDGE_API / f"{model_name}.md"
        out_api.write_text(md, encoding="utf-8")

        merged = merge_with_user_guide(model_name, md, docs_dir)
        out_model = KNOWLEDGE_MODELS / f"{model_name}.md"
        out_model.write_text(merged, encoding="utf-8")
        print(f"  wrote: {out_model.name}")

    print("Done.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract API docs from scviva-tools")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Directory containing fetched scviva-tools user guide docs (subdir: models/)",
    )
    args = parser.parse_args()
    run(docs_dir=args.docs_dir)
