"""Shared helpers for extracting API docs from installed Python packages.

Used by extract_api_docs.py (scvi-tools), extract_scviva_api_docs.py (scviva-tools),
and extract_scib_metrics_api_docs.py (scib-metrics) to avoid duplicating the same
inspect-based signature/docstring rendering logic per source.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path


def resolve_dotted(dotted: str) -> object | None:
    """Import and return the object at a dotted path, e.g. 'scvi.model.SCVI'."""
    parts = dotted.rsplit(".", 1)
    if len(parts) != 2:
        return None
    try:
        mod = importlib.import_module(parts[0])
        return getattr(mod, parts[1], None)
    except Exception:
        return None


def _signature_of(obj: object) -> str:
    try:
        if inspect.isclass(obj):
            return str(inspect.signature(obj.__init__)).replace("(self, ", "(").replace("(self)", "()")
        return str(inspect.signature(obj))
    except (ValueError, TypeError):
        return ""


def _render_one(obj: object, extra_methods: tuple[str, ...], nested: bool) -> list[str]:
    qualname = getattr(obj, "__qualname__", getattr(obj, "__name__", str(obj)))
    module = getattr(obj, "__module__", "unknown")
    sig = _signature_of(obj)
    doc = inspect.getdoc(obj) or "No docstring available."
    kind = "Class" if inspect.isclass(obj) else "Function"
    if nested:
        lines = [f"## `{module}.{qualname}`", "", f"**Signature:** `{qualname}{sig}`", "", doc, ""]
    else:
        lines = [
            f"**{kind}:** `{module}.{qualname}`",
            "",
            f"**Signature:** `{qualname}{sig}`",
            "",
            "## Docstring",
            "",
            doc,
            "",
        ]
    method_heading_level = "###" if nested else "##"
    for method_name in extra_methods:
        method = getattr(obj, method_name, None)
        if method is None:
            continue
        try:
            method_sig = str(inspect.signature(method))
            method_doc = inspect.getdoc(method) or ""
        except (ValueError, TypeError):
            continue
        lines += [
            f"{method_heading_level} {method_name}",
            "",
            "```python",
            f"{qualname}.{method_name}{method_sig}",
            "```",
            "",
            method_doc,
            "",
        ]
    return lines


def render_doc(heading: str, objs: list[object], extra_methods: tuple[str, ...] = ()) -> str:
    """Render one or more classes/functions sharing a knowledge-base entry name to Markdown.

    Most entries have a single object, matching the original scvi-tools API doc layout
    (flat '**Class:**' / '## Docstring' / '## setup_anndata' sections). A few entries
    (e.g. Stereoscope's RNAStereoscope + SpatialStereoscope) combine multiple objects
    under one heading, each nested under its own '## `module.Class`' subsection.
    """
    lines = [f"# {heading} — API Reference", ""]
    nested = len(objs) > 1
    for obj in objs:
        lines += _render_one(obj, extra_methods, nested=nested)
    return "\n".join(lines)


def merge_with_user_guide(item_name: str, md: str, docs_dir: Path | None, subdir: str = "models") -> str:
    """Append upstream narrative user-guide Markdown for item_name, if available."""
    if docs_dir is None:
        return md
    guide_path = docs_dir / subdir / f"{item_name}.md"
    if guide_path.exists():
        guide = guide_path.read_text(encoding="utf-8")
        return f"{md}\n\n---\n\n## User Guide\n\n{guide}"
    return md
