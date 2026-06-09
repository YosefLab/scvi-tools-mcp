"""Extract docstrings and signatures from scvi-tools public API into Markdown files.

Requires scvi-tools installed: pip install scvi-tools-mcp[scvi]

Usage:
    python scripts/extract_api_docs.py
"""
from __future__ import annotations
import importlib
import inspect
from pathlib import Path

KNOWLEDGE_MODELS = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/models"
KNOWLEDGE_API = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/api"
SCVI_DOCS = Path(__file__).parent.parent.parent / "scvi-tools2/docs/user_guide/models"

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


def get_class(dotted: str) -> type | None:
    parts = dotted.rsplit(".", 1)
    if len(parts) != 2:
        return None
    try:
        mod = importlib.import_module(parts[0])
        return getattr(mod, parts[1], None)
    except Exception:
        return None


def class_to_md(name: str, cls: type) -> str:
    sig = ""
    try:
        sig = str(inspect.signature(cls.__init__)).replace("(self, ", "(")
    except Exception:
        pass
    doc = inspect.getdoc(cls) or "No docstring available."
    lines = [
        f"# {name.upper()} — API Reference",
        "",
        f"**Class:** `{cls.__module__}.{cls.__name__}`",
        "",
        f"**Signature:** `{cls.__name__}{sig}`",
        "",
        "## Docstring",
        "",
        doc,
        "",
    ]
    # Add setup_anndata signature
    setup = getattr(cls, "setup_anndata", None)
    if setup:
        try:
            setup_sig = str(inspect.signature(setup))
            setup_doc = inspect.getdoc(setup) or ""
            lines += [
                "## setup_anndata",
                "",
                "```python",
                f"{cls.__name__}.setup_anndata{setup_sig}",
                "```",
                "",
                setup_doc,
                "",
            ]
        except Exception:
            pass
    # Add train signature
    train = getattr(cls, "train", None)
    if train:
        try:
            train_sig = str(inspect.signature(train))
            train_doc = inspect.getdoc(train) or ""
            lines += [
                "## train",
                "",
                "```python",
                f"{cls.__name__}.train{train_sig}",
                "```",
                "",
                train_doc,
                "",
            ]
        except Exception:
            pass
    return "\n".join(lines)


def merge_with_user_guide(model_name: str, api_md: str) -> str:
    guide_path = SCVI_DOCS / f"{model_name}.md"
    if guide_path.exists():
        guide = guide_path.read_text(encoding="utf-8")
        return f"{api_md}\n\n---\n\n## User Guide\n\n{guide}"
    return api_md


def run() -> None:
    KNOWLEDGE_MODELS.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_API.mkdir(parents=True, exist_ok=True)

    for model_name, dotted in MODEL_CLASSES.items():
        cls = get_class(dotted)
        if cls is None:
            print(f"  SKIP (not found): {dotted}")
            continue
        md = class_to_md(model_name, cls)
        md = merge_with_user_guide(model_name, md)
        out = KNOWLEDGE_MODELS / f"{model_name}.md"
        out.write_text(md, encoding="utf-8")
        print(f"  wrote: {out.name}")

    # Also write per-model API files (without user_guide merge)
    for model_name, dotted in MODEL_CLASSES.items():
        cls = get_class(dotted)
        if cls is None:
            continue
        md = class_to_md(model_name, cls)
        out = KNOWLEDGE_API / f"{model_name}.md"
        out.write_text(md, encoding="utf-8")

    # Update synced version
    version_file = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/.last_synced_version"
    try:
        import scvi
        version_file.write_text(scvi.__version__, encoding="utf-8")
        print(f"  synced version: {scvi.__version__}")
    except Exception:
        pass

    print("Done.")


if __name__ == "__main__":
    run()
