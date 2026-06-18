"""Convert Jupyter notebooks to clean Markdown files for the MCP knowledge base.

Strips all cell outputs. Keeps markdown cells as-is and code cells as fenced
python blocks. Skips .ipynb_checkpoints directories.

Usage:
    python scripts/convert_notebooks.py
    python scripts/convert_notebooks.py --src /path/to/notebooks --dst /path/to/output
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

KNOWLEDGE_TUTORIALS = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/tutorials"


def convert_notebook(src: Path, dst: Path) -> None:
    nb = json.loads(src.read_text(encoding="utf-8"))
    lines: list[str] = []
    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        cell_type = cell.get("cell_type", "")
        if cell_type == "markdown":
            lines.append(source)
            lines.append("")
        elif cell_type == "code":
            lines.append("```python")
            lines.append(source)
            lines.append("```")
            lines.append("")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines), encoding="utf-8")


def convert_all(src_root: Path, dst_root: Path) -> list[Path]:
    converted: list[Path] = []
    for nb_path in sorted(src_root.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in nb_path.parts:
            continue
        rel = nb_path.relative_to(src_root)
        dst = dst_root / rel.with_suffix(".md")
        convert_notebook(nb_path, dst)
        converted.append(dst)
        print(f"  converted: {rel}")
    return converted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert scvi-tools notebooks to Markdown")
    parser.add_argument("--src", type=Path, required=True, help="Root directory containing .ipynb files")
    parser.add_argument("--dst", type=Path, default=KNOWLEDGE_TUTORIALS)
    args = parser.parse_args()
    print(f"Converting notebooks from {args.src} to {args.dst}")
    converted = convert_all(args.src, args.dst)
    print(f"Done: {len(converted)} notebooks converted.")
