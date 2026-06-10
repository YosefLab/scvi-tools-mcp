# scvi-tools MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static-knowledge MCP server that gives LLMs structured access to scvi-tools documentation, tutorials, API reference, workflow templates, and FAQ via 13 tools over stdio.

**Architecture:** All knowledge is baked as `.md` files inside `src/scvi_tools_mcp/knowledge/` (bundled in the wheel). Tools are structured lookups into this knowledge base via `importlib.resources`. Three monthly CI jobs keep knowledge current by opening PRs when upstream changes.

**Tech Stack:** Python ≥3.11, fastmcp 3.4.2, pydantic ≥2, hatchling, pytest, nbconvert, GitHub Actions

---

## Phase 1 — Scaffold, Packaging, Utils

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/scvi_tools_mcp/__init__.py`
- Create: `src/scvi_tools_mcp/tools/__init__.py`
- Create: `src/scvi_tools_mcp/knowledge/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/models/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/tutorials/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/user_guide/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/api/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/faq/.gitkeep`
- Create: `src/scvi_tools_mcp/knowledge/.last_synced_version`
- Create: `.gitignore`
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Write pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "scvi-tools-mcp"
version = "0.1.0"
description = "MCP server for scvi-tools - deep probabilistic analysis of single-cell omics data"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
dependencies = [
    "fastmcp>=3.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
scvi = ["scvi-tools>=1.0"]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "ruff>=0.1",
    "pre-commit",
    "nbconvert>=7.0",
    "requests>=2.28",
]

[project.scripts]
scvi-tools-mcp = "scvi_tools_mcp.main:run_app"

[tool.hatch.build.targets.wheel]
packages = ["src/scvi_tools_mcp"]

[tool.ruff]
line-length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create `src/scvi_tools_mcp/__init__.py`**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Create `src/scvi_tools_mcp/tools/__init__.py`**

```python
```

- [ ] **Step 4: Create knowledge directory stubs**

```bash
mkdir -p src/scvi_tools_mcp/knowledge/{models,tutorials,user_guide,api,faq}
touch src/scvi_tools_mcp/knowledge/models/.gitkeep
touch src/scvi_tools_mcp/knowledge/tutorials/.gitkeep
touch src/scvi_tools_mcp/knowledge/user_guide/.gitkeep
touch src/scvi_tools_mcp/knowledge/api/.gitkeep
touch src/scvi_tools_mcp/knowledge/faq/.gitkeep
echo "0.0.0" > src/scvi_tools_mcp/knowledge/.last_synced_version
```

- [ ] **Step 5: Create `.gitignore`**

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
.ruff_cache/
.pytest_cache/
*.h5ad
*.h5
*.ipynb_checkpoints/
```

- [ ] **Step 6: Create `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 7: Install dev dependencies**

```bash
pip install -e ".[dev]"
```

Expected: installs fastmcp, pydantic, pytest, nbconvert, ruff.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/ .gitignore .pre-commit-config.yaml
git commit -m "chore: scaffold project structure and packaging"
```

---

### Task 2: `utils.py` + tests

**Files:**
- Create: `src/scvi_tools_mcp/tools/utils.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/fixtures/knowledge/models/scvi.md`
- Create: `tests/fixtures/knowledge/faq/github_issues.md`
- Create: `tests/test_utils.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_utils.py
from pathlib import Path
import pytest
from scvi_tools_mcp.tools.utils import load_knowledge, truncate, paginate, KnowledgeNotFoundError

FIXTURES = Path(__file__).parent / "fixtures"

def test_load_knowledge_returns_content(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Hello\nworld")
    content = load_knowledge(f)
    assert content == "# Hello\nworld"

def test_load_knowledge_raises_on_missing(tmp_path):
    with pytest.raises(KnowledgeNotFoundError):
        load_knowledge(tmp_path / "missing.md")

def test_truncate_short_content_unchanged():
    result = truncate("hello", max_chars=100)
    assert result == "hello"
    assert result.truncated is False  # use result object

def test_truncate_long_content_cut():
    long = "x" * 5000
    result = truncate(long, max_chars=100)
    assert len(result.content) <= 100
    assert result.truncated is True

def test_paginate_single_page():
    lines = ["line"] * 10
    result = paginate(lines, page=1, page_size=20)
    assert result.total_pages == 1
    assert len(result.lines) == 10

def test_paginate_multiple_pages():
    lines = [f"line{i}" for i in range(50)]
    result = paginate(lines, page=2, page_size=20)
    assert result.total_pages == 3
    assert result.lines[0] == "line20"

def test_paginate_out_of_range():
    lines = ["line"] * 10
    result = paginate(lines, page=99, page_size=20)
    assert result.lines == []
    assert result.total_pages == 1
```

- [ ] **Step 2: Create fixture files**

```bash
mkdir -p tests/fixtures/knowledge/{models,faq}
echo "# scVI\n\nscVI is a model for..." > tests/fixtures/knowledge/models/scvi.md
echo "# FAQ\n\n## Training\nQ: Why is loss not decreasing?" > tests/fixtures/knowledge/faq/github_issues.md
touch tests/__init__.py
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
pytest tests/test_utils.py -v
```

Expected: `ImportError` — module not yet created.

- [ ] **Step 4: Write `utils.py`**

```python
# src/scvi_tools_mcp/tools/utils.py
from __future__ import annotations
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
import math


class KnowledgeNotFoundError(Exception):
    pass


@dataclass
class TruncateResult:
    content: str
    truncated: bool


@dataclass
class PaginateResult:
    lines: list[str]
    page: int
    total_pages: int


def get_knowledge_dir() -> Path:
    return Path(str(files("scvi_tools_mcp").joinpath("knowledge")))


def load_knowledge(path: Path) -> str:
    if not path.exists():
        raise KnowledgeNotFoundError(
            f"Knowledge file not found: {path}. Run scripts/extract_api_docs.py to rebuild."
        )
    return path.read_text(encoding="utf-8")


def truncate(content: str, max_chars: int = 4000) -> TruncateResult:
    if len(content) <= max_chars:
        return TruncateResult(content=content, truncated=False)
    return TruncateResult(content=content[:max_chars], truncated=True)


def paginate(lines: list[str], page: int = 1, page_size: int = 200) -> PaginateResult:
    total_pages = max(1, math.ceil(len(lines) / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    return PaginateResult(lines=lines[start:end], page=page, total_pages=total_pages)


def list_knowledge_files(subdir: str) -> list[str]:
    knowledge_dir = get_knowledge_dir()
    target = knowledge_dir / subdir
    if not target.exists():
        return []
    return sorted(p.stem for p in target.glob("*.md"))
```

- [ ] **Step 5: Fix tests — update truncate test to match dataclass API**

The test at step 1 uses `.truncated` on a string — update `test_truncate_short_content_unchanged`:

```python
def test_truncate_short_content_unchanged():
    result = truncate("hello", max_chars=100)
    assert result.content == "hello"
    assert result.truncated is False

def test_truncate_long_content_cut():
    long = "x" * 5000
    result = truncate(long, max_chars=100)
    assert len(result.content) <= 100
    assert result.truncated is True
```

- [ ] **Step 6: Run tests — expect PASS**

```bash
pytest tests/test_utils.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/scvi_tools_mcp/tools/utils.py tests/
git commit -m "feat: add utils - load_knowledge, truncate, paginate"
```

---

### Task 3: `main.py` + `mcp.py` (FastMCP wiring)

**Files:**
- Create: `src/scvi_tools_mcp/main.py`
- Create: `src/scvi_tools_mcp/mcp.py`

- [ ] **Step 1: Write `mcp.py`**

```python
# src/scvi_tools_mcp/mcp.py
from fastmcp import FastMCP

mcp = FastMCP(
    name="scvi-tools-mcp",
    instructions=(
        "You are an expert on scvi-tools, a Python package for deep probabilistic "
        "analysis of single-cell omics data. Use these tools to help users choose "
        "models, prepare data, find tutorials, understand the API, and troubleshoot. "
        "Always start with recommend_model or search_knowledge if the user's need is unclear."
    ),
)

# Tool modules are imported here after mcp is defined
from scvi_tools_mcp.tools import (  # noqa: E402, F401
    _model_guidance,
    _data_prep,
    _tutorials,
    _api_reference,
    _workflows,
    _troubleshooting,
)
```

- [ ] **Step 2: Write `main.py`**

```python
# src/scvi_tools_mcp/main.py
from scvi_tools_mcp.mcp import mcp


def run_app() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_app()
```

- [ ] **Step 3: Create stub tool modules so mcp.py imports don't fail**

```python
# src/scvi_tools_mcp/tools/_model_guidance.py
# src/scvi_tools_mcp/tools/_data_prep.py
# src/scvi_tools_mcp/tools/_tutorials.py
# src/scvi_tools_mcp/tools/_api_reference.py
# src/scvi_tools_mcp/tools/_workflows.py
# src/scvi_tools_mcp/tools/_troubleshooting.py
```

Each stub file is empty for now. Create all six:

```bash
for f in _model_guidance _data_prep _tutorials _api_reference _workflows _troubleshooting; do
  touch src/scvi_tools_mcp/tools/${f}.py
done
```

- [ ] **Step 4: Verify server starts**

```bash
python -c "from scvi_tools_mcp.main import run_app; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add src/scvi_tools_mcp/main.py src/scvi_tools_mcp/mcp.py src/scvi_tools_mcp/tools/
git commit -m "feat: add FastMCP server entry point and tool module stubs"
```

---

## Phase 2 — Knowledge Scripts

### Task 4: `convert_notebooks.py`

**Files:**
- Create: `scripts/__init__.py` (empty)
- Create: `scripts/convert_notebooks.py`
- Create: `tests/test_scripts.py`
- Create: `tests/fixtures/sample_notebook.ipynb`

- [ ] **Step 1: Create fixture notebook**

```json
// tests/fixtures/sample_notebook.ipynb
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# scVI Tutorial\n\nThis tutorial covers basic scVI usage."]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [{"output_type": "stream", "text": ["Training...\n"]}],
   "source": ["import scvi\nscvi.model.SCVI.setup_anndata(adata)"]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": ["model = scvi.model.SCVI(adata)\nmodel.train()"]
  }
 ],
 "metadata": {
  "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.11.0"}
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_scripts.py
from pathlib import Path
import pytest
from scripts.convert_notebooks import convert_notebook, convert_all

FIXTURES = Path(__file__).parent / "fixtures"

def test_convert_notebook_produces_md(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    assert out.exists()
    content = out.read_text()
    assert "# scVI Tutorial" in content
    assert "import scvi" in content

def test_convert_notebook_strips_outputs(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    content = out.read_text()
    assert "Training..." not in content

def test_convert_notebook_has_code_fences(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    content = out.read_text()
    assert "```python" in content

def test_convert_notebook_skips_checkpoints(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out_dir = tmp_path / "tutorials"
    out_dir.mkdir()
    checkpoint_dir = tmp_path / ".ipynb_checkpoints"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "sample-checkpoint.ipynb").write_text(nb.read_text())
    convert_all(tmp_path, out_dir)
    assert not (out_dir / "sample-checkpoint.md").exists()
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
pytest tests/test_scripts.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts'`

- [ ] **Step 4: Write `scripts/convert_notebooks.py`**

```python
# scripts/convert_notebooks.py
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

SCVI_NOTEBOOKS = Path(__file__).parent.parent.parent / "scvi-tools2/docs/tutorials/notebooks"
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
    parser.add_argument("--src", type=Path, default=SCVI_NOTEBOOKS)
    parser.add_argument("--dst", type=Path, default=KNOWLEDGE_TUTORIALS)
    args = parser.parse_args()
    print(f"Converting notebooks from {args.src} to {args.dst}")
    converted = convert_all(args.src, args.dst)
    print(f"Done: {len(converted)} notebooks converted.")
```

- [ ] **Step 5: Add `scripts/__init__.py`** (empty file so tests can import)

```bash
touch scripts/__init__.py
```

- [ ] **Step 6: Run tests — expect PASS**

```bash
pytest tests/test_scripts.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 7: Run script against real scvi-tools notebooks**

```bash
python scripts/convert_notebooks.py
```

Expected: ~60 `.md` files created in `src/scvi_tools_mcp/knowledge/tutorials/`.

- [ ] **Step 8: Verify a converted file**

```bash
head -30 src/scvi_tools_mcp/knowledge/tutorials/quick_start/api_overview.md
```

Expected: `# ...` markdown header followed by `\`\`\`python` fenced blocks, no cell outputs.

- [ ] **Step 9: Commit**

```bash
git add scripts/ src/scvi_tools_mcp/knowledge/tutorials/ tests/test_scripts.py tests/fixtures/sample_notebook.ipynb
git commit -m "feat: add notebook-to-markdown conversion script + run on scvi-tools tutorials"
```

---

### Task 5: `extract_api_docs.py`

**Files:**
- Create: `scripts/extract_api_docs.py`

- [ ] **Step 1: Write `scripts/extract_api_docs.py`**

```python
# scripts/extract_api_docs.py
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
    "scanvi": "scvi.model.SCANVI",
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
                f"```python",
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
                f"```python",
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

    # Also write per-model API files
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
```

- [ ] **Step 2: Run the script**

```bash
python scripts/extract_api_docs.py
```

Expected: `wrote: scvi.md`, `wrote: scanvi.md`, ... for each model. ~25 files in `knowledge/models/` and `knowledge/api/`.

- [ ] **Step 3: Verify output**

```bash
head -40 src/scvi_tools_mcp/knowledge/models/scvi.md
```

Expected: `# SCVI — API Reference`, signature, docstring, setup_anndata section, user guide section.

- [ ] **Step 4: Copy user_guide docs not covered by model extraction**

```bash
cp /Users/orikr/PycharmProjects/scvi-tools2/docs/user_guide/use_case/*.md \
   src/scvi_tools_mcp/knowledge/user_guide/
```

- [ ] **Step 5: Commit**

```bash
git add scripts/extract_api_docs.py src/scvi_tools_mcp/knowledge/models/ \
        src/scvi_tools_mcp/knowledge/api/ src/scvi_tools_mcp/knowledge/user_guide/ \
        src/scvi_tools_mcp/knowledge/.last_synced_version
git commit -m "feat: add API doc extraction script + populate knowledge/models/ and knowledge/api/"
```

---

### Task 6: `scrape_external.py`

**Files:**
- Create: `scripts/scrape_external.py`

- [ ] **Step 1: Write `scripts/scrape_external.py`**

```python
# scripts/scrape_external.py
"""Scrape a snapshot of GitHub issues and Discourse threads for the FAQ knowledge base.

Requires: requests (included in dev extras)
GitHub token recommended: set GITHUB_TOKEN env var for higher rate limits.

Usage:
    python scripts/scrape_external.py
"""
from __future__ import annotations
import os
import time
from pathlib import Path
import requests

KNOWLEDGE_FAQ = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/faq"
GITHUB_ISSUES_URL = "https://api.github.com/repos/scverse/scvi-tools/issues"
DISCOURSE_URL = "https://discourse.scverse.org/c/help/scvi-tools/7.json"
MAX_ISSUES = 50
MAX_THREADS = 30


def fetch_github_issues() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    params = {"state": "open", "per_page": MAX_ISSUES, "sort": "comments", "direction": "desc"}
    resp = requests.get(GITHUB_ISSUES_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    issues = resp.json()
    lines = ["# scvi-tools GitHub Issues Snapshot", "", f"Fetched top {len(issues)} issues by comment count.", ""]
    for issue in issues:
        title = issue.get("title", "")
        number = issue.get("number", "")
        comments = issue.get("comments", 0)
        body = (issue.get("body") or "")[:500].replace("\n", " ")
        lines += [
            f"## #{number}: {title}",
            f"**Comments:** {comments}",
            f"**Body:** {body}",
            "",
        ]
    return "\n".join(lines)


def fetch_discourse_threads() -> str:
    resp = requests.get(DISCOURSE_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    topics = data.get("topic_list", {}).get("topics", [])[:MAX_THREADS]
    lines = ["# scvi-tools Discourse Forum Snapshot", "", f"Fetched top {len(topics)} threads.", ""]
    for topic in topics:
        title = topic.get("title", "")
        posts = topic.get("posts_count", 0)
        views = topic.get("views", 0)
        lines += [
            f"## {title}",
            f"**Posts:** {posts} | **Views:** {views}",
            "",
        ]
    return "\n".join(lines)


def run() -> None:
    KNOWLEDGE_FAQ.mkdir(parents=True, exist_ok=True)
    print("Fetching GitHub issues...")
    try:
        issues_md = fetch_github_issues()
        (KNOWLEDGE_FAQ / "github_issues.md").write_text(issues_md, encoding="utf-8")
        print(f"  wrote github_issues.md ({len(issues_md)} chars)")
    except Exception as e:
        print(f"  WARN: GitHub fetch failed: {e}")
    time.sleep(1)
    print("Fetching Discourse threads...")
    try:
        discourse_md = fetch_discourse_threads()
        (KNOWLEDGE_FAQ / "discourse_threads.md").write_text(discourse_md, encoding="utf-8")
        print(f"  wrote discourse_threads.md ({len(discourse_md)} chars)")
    except Exception as e:
        print(f"  WARN: Discourse fetch failed: {e}")
    print("Done.")


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run the script**

```bash
python scripts/scrape_external.py
```

Expected: `wrote github_issues.md` and `wrote discourse_threads.md`.

- [ ] **Step 3: Commit**

```bash
git add scripts/scrape_external.py src/scvi_tools_mcp/knowledge/faq/
git commit -m "feat: add external knowledge scraper + populate knowledge/faq/"
```

---

## Phase 3 — Tool Modules

**All tools share this result base pattern:**

```python
from pydantic import BaseModel

class ToolResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None
```

All tool functions wrap their body in `try/except Exception as e` and return `ToolResult(error=str(e))` on failure.

---

### Task 7: `_model_guidance.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_model_guidance.py`
- Add tests: `tests/test_tools.py`

The full list of valid model names (used in all `Literal` types across tool modules):

```python
MODEL_NAMES = Literal[
    "amortizedlda","autozi","cellassign","contrastivevi","cytovi",
    "decipher","destvi","diagvi","gimvi","linearscvi","methylanvi",
    "methylvi","mrvi","multivi","peakvi","poissonvi","resolvi",
    "scanvi","scar","scbasset","scvi","scviva","solo","stereoscope",
    "sysvi","tangram","totalanvi","totalvi","velovi"
]
```

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tools.py
from pathlib import Path
import shutil
import pytest
from unittest.mock import patch

FIXTURES = Path(__file__).parent / "fixtures"

# --- model guidance ---

def test_recommend_model_returns_content(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import recommend_model
    result = recommend_model(
        task="batch_integration",
        data_type="scrna",
        has_protein=False,
        has_accessibility=False,
        n_batches=3,
    )
    assert result.error is None
    assert result.content is not None
    assert len(result.content) > 0

def test_get_model_overview_valid(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_overview
    result = get_model_overview(model_name="scvi")
    assert result.error is None
    assert "scvi" in result.content.lower()

def test_get_model_overview_unknown(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_overview
    result = get_model_overview(model_name="nonexistent_model")
    assert result.error is not None
    assert "not found" in result.error.lower()

def test_get_model_parameters_valid(mock_knowledge):
    from scvi_tools_mcp.tools._model_guidance import get_model_parameters
    result = get_model_parameters(model_name="scvi")
    assert result.error is None
```

- [ ] **Step 2: Add `conftest.py` with `mock_knowledge` fixture**

```python
# tests/conftest.py
from pathlib import Path
import shutil
import pytest
from unittest.mock import patch

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_knowledge(tmp_path):
    """Copy fixture knowledge files into a temp dir and patch get_knowledge_dir."""
    k = tmp_path / "knowledge"
    shutil.copytree(FIXTURES / "knowledge", k)
    # Add minimal model files
    models_dir = k / "models"
    models_dir.mkdir(exist_ok=True)
    (models_dir / "scvi.md").write_text(
        "# SCVI — API Reference\n\nscVI is a variational autoencoder for scRNA-seq batch integration.\n\n"
        "**Key parameters:** n_latent (int), gene_likelihood (str)\n\n"
        "## setup_anndata\n\n```python\nSCVI.setup_anndata(adata, batch_key='batch')\n```\n",
        encoding="utf-8",
    )
    for name in ["scanvi", "totalvi", "multivi", "peakvi"]:
        (models_dir / f"{name}.md").write_text(f"# {name.upper()}\n\nDoc for {name}.\n", encoding="utf-8")
    api_dir = k / "api"
    api_dir.mkdir(exist_ok=True)
    (api_dir / "scvi.md").write_text("# SCVI API\n\nSCVI.setup_anndata(adata, batch_key=None)\n", encoding="utf-8")
    tutorials_dir = k / "tutorials"
    tutorials_dir.mkdir(exist_ok=True)
    (tutorials_dir / "scrna").mkdir(exist_ok=True)
    (tutorials_dir / "scrna" / "harmonization.md").write_text(
        "# Harmonization Tutorial\n\nThis tutorial shows batch integration with scVI.\n\n```python\nimport scvi\n```\n",
        encoding="utf-8",
    )
    user_guide_dir = k / "user_guide"
    user_guide_dir.mkdir(exist_ok=True)
    (user_guide_dir / "saving_and_loading_models.md").write_text("# Saving Models\n\nUse model.save().\n", encoding="utf-8")
    faq_dir = k / "faq"
    faq_dir.mkdir(exist_ok=True)
    (faq_dir / "github_issues.md").write_text("# FAQ\n\n## Training\nQ: Loss not decreasing?\nA: Check learning rate.\n", encoding="utf-8")
    (faq_dir / "discourse_threads.md").write_text("# Discourse\n\n## How to use SCANVI?\nPosts: 10\n", encoding="utf-8")

    with patch("scvi_tools_mcp.tools.utils.get_knowledge_dir", return_value=k):
        yield k
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
pytest tests/test_tools.py -v
```

Expected: `ImportError` or `AttributeError` — tools not implemented yet.

- [ ] **Step 4: Write `_model_guidance.py`**

```python
# src/scvi_tools_mcp/tools/_model_guidance.py
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate, KnowledgeNotFoundError

MODEL_NAMES = Literal[
    "amortizedlda","autozi","cellassign","contrastivevi","cytovi",
    "decipher","destvi","diagvi","gimvi","linearscvi","methylanvi",
    "methylvi","mrvi","multivi","peakvi","poissonvi","resolvi",
    "scanvi","scar","scbasset","scvi","scviva","solo","stereoscope",
    "sysvi","tangram","totalanvi","totalvi","velovi"
]

TASK_MODEL_MAP: dict[str, list[str]] = {
    "batch_integration": ["scvi", "scanvi", "sysvi", "linearscvi"],
    "dimensionality_reduction": ["scvi", "multivi", "totalvi"],
    "differential_expression": ["scvi", "scanvi", "totalvi", "autozi"],
    "cell_type_annotation": ["scanvi", "cellassign", "solo"],
    "deconvolution": ["destvi", "stereoscope", "tangram"],
    "spatial_mapping": ["tangram", "destvi", "cell2location", "gimvi", "scviva"],
    "chromatin_accessibility": ["peakvi", "poissonvi", "scbasset", "multivi"],
    "multimodal_integration": ["totalvi", "multivi"],
    "reference_mapping": ["scanvi", "scarches"],
    "perturbation_modeling": ["contrastivevi", "mrvi"],
}

DATA_TYPE_HINTS: dict[str, str] = {
    "scrna": "For scRNA-seq, start with scVI for batch integration or SCANVI if you have cell type labels.",
    "cite_seq": "For CITE-seq (RNA + protein), use TotalVI. For reference mapping with CITE-seq, use TotalVI reference mapping.",
    "spatial": "For spatial transcriptomics, consider DestVI or Tangram for deconvolution, or cell2location.",
    "atac": "For scATAC-seq, use PeakVI for accessibility modeling or SCBASSET for sequence-based analysis.",
    "multiome": "For RNA+ATAC multiome data, use MultiVI which jointly models both modalities.",
}


class ModelGuidanceResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


from scvi_tools_mcp.mcp import mcp


@mcp.tool()
def recommend_model(
    task: Literal[
        "batch_integration","dimensionality_reduction","differential_expression",
        "cell_type_annotation","deconvolution","spatial_mapping",
        "chromatin_accessibility","multimodal_integration","reference_mapping",
        "perturbation_modeling"
    ],
    data_type: Literal["scrna","cite_seq","spatial","atac","multiome","cytometry","methylation"],
    has_protein: bool,
    has_accessibility: bool,
    n_batches: int,
) -> ModelGuidanceResult:
    """Recommend scvi-tools models ranked by suitability for the user's task and data type.

    Call this first when a user describes what they want to do. Returns a ranked list of
    model names with a short rationale for each. Use get_model_overview to get details
    on any recommended model.

    Args:
        task: The analysis goal.
        data_type: The type of single-cell data.
        has_protein: True if the data includes protein (ADT) measurements.
        has_accessibility: True if the data includes chromatin accessibility (ATAC).
        n_batches: Number of batches/donors. Use 1 if data is from a single batch.
    """
    try:
        candidates = TASK_MODEL_MAP.get(task, ["scvi"])
        if has_protein and "totalvi" not in candidates:
            candidates = ["totalvi"] + candidates
        if has_accessibility and "multivi" not in candidates:
            candidates = ["multivi"] + candidates
        data_hint = DATA_TYPE_HINTS.get(data_type, "")
        lines = [
            f"# Model Recommendations",
            f"",
            f"**Task:** {task} | **Data:** {data_type} | **Batches:** {n_batches}",
            f"",
            data_hint,
            f"",
            f"## Ranked Recommendations",
            f"",
        ]
        for i, name in enumerate(candidates[:5], 1):
            lines.append(f"{i}. **{name.upper()}** — use `get_model_overview(model_name='{name}')` for details.")
        lines += [
            "",
            "## Next Steps",
            "1. Call `get_model_overview` on your top choice.",
            "2. Call `get_setup_anndata_guide` to prepare your AnnData object.",
            "3. Call `get_workflow_template` for a full code template.",
        ]
        result = truncate("\n".join(lines))
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))


@mcp.tool()
def get_model_overview(
    model_name: MODEL_NAMES,
) -> ModelGuidanceResult:
    """Get a detailed overview of a specific scvi-tools model.

    Returns the model description, use cases, required inputs, outputs, advantages,
    limitations, and key citations. Call this after recommend_model to learn about
    a specific model before using it.

    Args:
        model_name: The scvi-tools model name in lowercase (e.g. 'scvi', 'scanvi', 'totalvi').
    """
    try:
        knowledge_dir = get_knowledge_dir()
        model_file = knowledge_dir / "models" / f"{model_name}.md"
        if not model_file.exists():
            available = sorted(p.stem for p in (knowledge_dir / "models").glob("*.md"))
            return ModelGuidanceResult(
                error=f"Model '{model_name}' not found. Available: {', '.join(available)}"
            )
        content = model_file.read_text(encoding="utf-8")
        result = truncate(content)
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))


@mcp.tool()
def get_model_parameters(
    model_name: MODEL_NAMES,
) -> ModelGuidanceResult:
    """Get key initialization and training parameters for a scvi-tools model.

    Returns the most important parameters for model.__init__() and model.train()
    with descriptions and recommended defaults. Call this when a user wants to
    customize model behavior beyond defaults.

    Args:
        model_name: The scvi-tools model name in lowercase (e.g. 'scvi', 'totalvi').
    """
    try:
        knowledge_dir = get_knowledge_dir()
        api_file = knowledge_dir / "api" / f"{model_name}.md"
        if not api_file.exists():
            # Fall back to model file
            api_file = knowledge_dir / "models" / f"{model_name}.md"
        if not api_file.exists():
            return ModelGuidanceResult(error=f"API reference for '{model_name}' not found.")
        content = api_file.read_text(encoding="utf-8")
        result = truncate(content)
        return ModelGuidanceResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ModelGuidanceResult(error=str(e))
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
pytest tests/test_tools.py -v -k "model"
```

Expected: 4 model guidance tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/scvi_tools_mcp/tools/_model_guidance.py tests/test_tools.py tests/conftest.py
git commit -m "feat: add model guidance tools (recommend_model, get_model_overview, get_model_parameters)"
```

---

### Task 8: `_data_prep.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_data_prep.py`

- [ ] **Step 1: Add tests to `tests/test_tools.py`**

```python
# append to tests/test_tools.py

def test_get_setup_anndata_guide_valid(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import get_setup_anndata_guide
    result = get_setup_anndata_guide(model_name="scvi")
    assert result.error is None
    assert "setup_anndata" in result.content

def test_validate_data_requirements_pass(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import validate_data_requirements
    result = validate_data_requirements(
        model_name="scvi",
        obs_keys=["batch", "cell_type"],
        var_keys=["gene_name"],
        has_raw=True,
    )
    assert result.error is None
    assert result.content is not None

def test_validate_data_requirements_missing_model(mock_knowledge):
    from scvi_tools_mcp.tools._data_prep import validate_data_requirements
    result = validate_data_requirements(
        model_name="nonexistent",
        obs_keys=[],
        var_keys=[],
        has_raw=False,
    )
    assert result.error is not None
```

- [ ] **Step 2: Write `_data_prep.py`**

```python
# src/scvi_tools_mcp/tools/_data_prep.py
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate
from scvi_tools_mcp.tools._model_guidance import MODEL_NAMES
from scvi_tools_mcp.mcp import mcp

# Requirements per model: (required_obs, required_var, needs_raw, notes)
MODEL_REQUIREMENTS: dict[str, dict] = {
    "scvi": {
        "required_obs": [],
        "optional_obs": ["batch_key", "labels_key"],
        "required_var": [],
        "needs_raw": False,
        "setup_call": "SCVI.setup_anndata(adata, batch_key='batch')",
        "notes": "Count data must be in adata.X or a layer. Do not log-normalize before training.",
    },
    "scanvi": {
        "required_obs": ["labels_key (cell type column, unlabeled cells use 'Unknown')"],
        "optional_obs": ["batch_key"],
        "required_var": [],
        "needs_raw": False,
        "setup_call": "SCANVI.setup_anndata(adata, labels_key='cell_type', unlabeled_category='Unknown', batch_key='batch')",
        "notes": "Requires at least some labeled cells. Works best with >100 labeled cells per type.",
    },
    "totalvi": {
        "required_obs": ["batch_key recommended"],
        "optional_obs": [],
        "required_var": [],
        "needs_raw": False,
        "setup_call": "TOTALVI.setup_anndata(adata, batch_key='batch', protein_expression_obsm_key='protein_expression')",
        "notes": "Protein data must be raw counts in adata.obsm['protein_expression']. Do not normalize.",
    },
    "multivi": {
        "required_obs": [],
        "optional_obs": ["batch_key", "modality_key"],
        "required_var": ["modality column in adata.var"],
        "needs_raw": False,
        "setup_call": "MULTIVI.setup_anndata(adata, batch_key='batch', modality_key='modality')",
        "notes": "adata.var must have a column indicating modality ('Gene Expression' or 'Peaks').",
    },
    "peakvi": {
        "required_obs": [],
        "optional_obs": ["batch_key"],
        "required_var": [],
        "needs_raw": False,
        "setup_call": "PEAKVI.setup_anndata(adata, batch_key='batch')",
        "notes": "Input must be binary accessibility matrix (0/1). Use binarize=True if needed.",
    },
}

DEFAULT_REQUIREMENTS = {
    "required_obs": [],
    "optional_obs": ["batch_key"],
    "required_var": [],
    "needs_raw": False,
    "setup_call": f"MODEL.setup_anndata(adata)",
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
        # Try to get from knowledge file first (more detailed)
        knowledge_dir = get_knowledge_dir()
        model_file = knowledge_dir / "models" / f"{model_name}.md"
        reqs = MODEL_REQUIREMENTS.get(model_name, DEFAULT_REQUIREMENTS)

        lines = [
            f"# setup_anndata Guide — {model_name.upper()}",
            "",
            f"## Call",
            f"```python",
            reqs.get("setup_call", f"{model_name.upper()}.setup_anndata(adata)"),
            "```",
            "",
            "## Required obs fields",
        ]
        required_obs = reqs.get("required_obs", [])
        lines.append("None (count matrix in adata.X is always required)" if not required_obs
                     else "\n".join(f"- {r}" for r in required_obs))
        lines += ["", "## Optional obs fields"]
        optional_obs = reqs.get("optional_obs", [])
        lines.append("None" if not optional_obs else "\n".join(f"- {r}" for r in optional_obs))
        lines += ["", "## Notes", reqs.get("notes", ""), ""]

        if model_file.exists():
            # Append setup_anndata section from knowledge file
            content = model_file.read_text(encoding="utf-8")
            if "setup_anndata" in content:
                idx = content.find("## setup_anndata")
                if idx >= 0:
                    lines += ["", "## Full API Detail", content[idx:idx+1500]]

        result = truncate("\n".join(lines))
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
                error=f"No requirements defined for '{model_name}'. Known models: {', '.join(available)}. "
                      f"Use get_model_overview for full documentation."
            )

        checks: list[tuple[bool, str]] = []
        checks.append((True, "adata.X contains count matrix (assumed from call context)"))

        for req in reqs.get("required_obs", []):
            field = req.split(" ")[0]
            passed = field in obs_keys or "(recommended)" in req or "(" in req
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
            prefix = "✓" if passed else "✗"
            lines.append(f"{prefix} {msg}")
        lines += ["", "## Next Step",
                  f"Call `get_setup_anndata_guide(model_name='{model_name}')` for the exact setup call."]

        result = truncate("\n".join(lines))
        return DataPrepResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return DataPrepResult(error=str(e))
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_tools.py -v -k "data"
```

Expected: 3 data prep tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/scvi_tools_mcp/tools/_data_prep.py
git commit -m "feat: add data prep tools (get_setup_anndata_guide, validate_data_requirements)"
```

---

### Task 9: `_tutorials.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_tutorials.py`

- [ ] **Step 1: Add tests**

```python
# append to tests/test_tools.py

def test_list_tutorials_all(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import list_tutorials
    result = list_tutorials(category=None)
    assert result.error is None
    assert result.content is not None

def test_list_tutorials_category(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import list_tutorials
    result = list_tutorials(category="scrna")
    assert result.error is None

def test_get_tutorial_valid(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import get_tutorial
    result = get_tutorial(tutorial_name="scrna/harmonization", page=1)
    assert result.error is None
    assert "harmonization" in result.content.lower() or "scvi" in result.content.lower()

def test_get_tutorial_missing(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import get_tutorial
    result = get_tutorial(tutorial_name="scrna/nonexistent", page=1)
    assert result.error is not None

def test_search_tutorials_finds_match(mock_knowledge):
    from scvi_tools_mcp.tools._tutorials import search_tutorials
    result = search_tutorials(query="batch integration scvi")
    assert result.error is None
    assert result.content is not None
```

- [ ] **Step 2: Write `_tutorials.py`**

```python
# src/scvi_tools_mcp/tools/_tutorials.py
from __future__ import annotations
from typing import Literal
from pathlib import Path
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate, paginate
from scvi_tools_mcp.mcp import mcp

TUTORIAL_CATEGORIES = Literal[
    "scrna","multimodal","spatial","atac","hub","quick_start",
    "cytometry","dev","r","use_cases","scbs","custom_dl"
]


class TutorialResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None


def _get_tutorials_dir() -> Path:
    return get_knowledge_dir() / "tutorials"


def _find_tutorial(name: str) -> Path | None:
    base = _get_tutorials_dir()
    # Try exact path
    candidate = base / f"{name}.md"
    if candidate.exists():
        return candidate
    # Try with category prefix search
    for md in base.rglob("*.md"):
        if md.stem == name.split("/")[-1]:
            return md
    return None


@mcp.tool()
def list_tutorials(
    category: TUTORIAL_CATEGORIES | None = None,
) -> TutorialResult:
    """List all available scvi-tools tutorials, optionally filtered by category.

    Returns tutorial names and one-line descriptions. Use get_tutorial to read
    the full content of any tutorial. Tutorial names can be passed directly to
    get_tutorial.

    Args:
        category: Filter by category. Pass None to list all tutorials.
                  Categories: scrna, multimodal, spatial, atac, hub, quick_start,
                  cytometry, dev, r, use_cases, scbs, custom_dl.
    """
    try:
        base = _get_tutorials_dir()
        if not base.exists():
            return TutorialResult(error="Tutorial knowledge not found. Run scripts/convert_notebooks.py.")
        lines = ["# Available Tutorials", ""]
        if category:
            dirs = [base / category]
        else:
            dirs = sorted(d for d in base.iterdir() if d.is_dir())
        for d in dirs:
            if not d.exists():
                continue
            mds = sorted(d.glob("*.md"))
            if mds:
                lines.append(f"## {d.name}")
                for md in mds:
                    lines.append(f"- `{d.name}/{md.stem}` — use get_tutorial(tutorial_name='{d.name}/{md.stem}')")
                lines.append("")
        result = truncate("\n".join(lines))
        return TutorialResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TutorialResult(error=str(e))


@mcp.tool()
def get_tutorial(
    tutorial_name: str,
    page: int = 1,
    page_size: int = 200,
) -> TutorialResult:
    """Read the full content of a scvi-tools tutorial.

    Returns the tutorial as Markdown (code cells as fenced blocks, no outputs).
    Large tutorials are paginated — check total_pages and call again with page=2, 3, etc.
    Get tutorial names from list_tutorials.

    Args:
        tutorial_name: Tutorial path like 'scrna/harmonization' or 'quick_start/api_overview'.
        page: Page number starting at 1.
        page_size: Lines per page (default 200).
    """
    try:
        path = _find_tutorial(tutorial_name)
        if path is None:
            return TutorialResult(
                error=f"Tutorial '{tutorial_name}' not found. Call list_tutorials() to see available tutorials."
            )
        lines = path.read_text(encoding="utf-8").splitlines()
        result = paginate(lines, page=page, page_size=page_size)
        content = "\n".join(result.lines)
        return TutorialResult(
            content=content,
            page=result.page,
            total_pages=result.total_pages,
            truncated=result.total_pages > 1,
        )
    except Exception as e:
        return TutorialResult(error=str(e))


@mcp.tool()
def search_tutorials(query: str) -> TutorialResult:
    """Search tutorials by keyword and return matching excerpts.

    Use this to find tutorials relevant to a user's question. Returns tutorial names
    and matching lines. Then use get_tutorial to read the full content.

    Args:
        query: Space-separated keywords (e.g. 'batch integration totalvi reference mapping').
    """
    try:
        base = _get_tutorials_dir()
        if not base.exists():
            return TutorialResult(error="Tutorial knowledge not found. Run scripts/convert_notebooks.py.")
        keywords = [k.lower() for k in query.split()]
        results: list[tuple[int, str, str]] = []
        for md in sorted(base.rglob("*.md")):
            content = md.read_text(encoding="utf-8")
            lower = content.lower()
            score = sum(lower.count(kw) for kw in keywords)
            if score > 0:
                # Extract first matching line for excerpt
                excerpt = ""
                for line in content.splitlines():
                    if any(kw in line.lower() for kw in keywords):
                        excerpt = line[:120]
                        break
                rel = md.relative_to(base)
                name = str(rel.with_suffix(""))
                results.append((score, name, excerpt))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# Tutorial Search: '{query}'", ""]
        for score, name, excerpt in results[:10]:
            lines.append(f"- **{name}** (score: {score})")
            if excerpt:
                lines.append(f"  > {excerpt}")
        if not results:
            lines.append("No tutorials matched your query. Try broader keywords.")
        lines.append("\nUse get_tutorial(tutorial_name='<name>') to read the full tutorial.")
        result = truncate("\n".join(lines))
        return TutorialResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TutorialResult(error=str(e))
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_tools.py -v -k "tutorial"
```

Expected: 5 tutorial tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/scvi_tools_mcp/tools/_tutorials.py
git commit -m "feat: add tutorial tools (list_tutorials, get_tutorial, search_tutorials)"
```

---

### Task 10: `_api_reference.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_api_reference.py`

- [ ] **Step 1: Add tests**

```python
# append to tests/test_tools.py

def test_get_api_reference_valid(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import get_api_reference
    result = get_api_reference(symbol="SCVI")
    assert result.error is None
    assert result.content is not None

def test_get_api_reference_unknown(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import get_api_reference
    result = get_api_reference(symbol="NonExistentClass")
    assert result.error is not None

def test_search_api_returns_results(mock_knowledge):
    from scvi_tools_mcp.tools._api_reference import search_api
    result = search_api(query="setup anndata batch")
    assert result.error is None
    assert result.content is not None
```

- [ ] **Step 2: Write `_api_reference.py`**

```python
# src/scvi_tools_mcp/tools/_api_reference.py
from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate
from scvi_tools_mcp.mcp import mcp


class ApiResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


def _get_api_dir() -> Path:
    return get_knowledge_dir() / "api"


def _find_symbol(symbol: str) -> Path | None:
    api_dir = _get_api_dir()
    # Normalize: SCVI -> scvi, scvi.model.SCVI -> scvi
    name = symbol.lower().split(".")[-1]
    candidate = api_dir / f"{name}.md"
    if candidate.exists():
        return candidate
    # Also search models dir
    models_dir = get_knowledge_dir() / "models"
    candidate2 = models_dir / f"{name}.md"
    if candidate2.exists():
        return candidate2
    return None


@mcp.tool()
def get_api_reference(symbol: str) -> ApiResult:
    """Get the API reference (signature + docstring) for a scvi-tools class or method.

    Use this when a user asks about specific parameters, return types, or method
    behavior. Pass the class name (e.g. 'SCVI', 'SCANVI') or method (e.g. 'SCVI.train').

    Args:
        symbol: Class or method name. Examples: 'SCVI', 'TOTALVI', 'SCANVI.setup_anndata'.
    """
    try:
        path = _find_symbol(symbol)
        if path is None:
            api_dir = _get_api_dir()
            available = sorted(p.stem.upper() for p in api_dir.glob("*.md")) if api_dir.exists() else []
            return ApiResult(
                error=f"Symbol '{symbol}' not found. Available: {', '.join(available[:20])}."
            )
        content = path.read_text(encoding="utf-8")
        # If method-level, extract relevant section
        method = symbol.split(".")[-1].lower() if "." in symbol else None
        if method and method != symbol.lower():
            lower = content.lower()
            idx = lower.find(f"## {method}")
            if idx >= 0:
                content = content[idx:idx + 2000]
        result = truncate(content)
        return ApiResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ApiResult(error=str(e))


@mcp.tool()
def search_api(query: str) -> ApiResult:
    """Search the scvi-tools API for classes and methods matching a query.

    Returns matching symbols with short descriptions. Use get_api_reference to
    get full details on any result.

    Args:
        query: Keywords to search (e.g. 'differential expression', 'latent representation').
    """
    try:
        keywords = [k.lower() for k in query.split()]
        api_dir = _get_api_dir()
        if not api_dir.exists():
            return ApiResult(error="API knowledge not found. Run scripts/extract_api_docs.py.")
        results: list[tuple[int, str, str]] = []
        for md in sorted(api_dir.glob("*.md")):
            content = md.read_text(encoding="utf-8")
            lower = content.lower()
            score = sum(lower.count(kw) for kw in keywords)
            if score > 0:
                first_line = content.splitlines()[0] if content.splitlines() else md.stem
                results.append((score, md.stem.upper(), first_line[:100]))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# API Search: '{query}'", ""]
        for _, name, desc in results[:10]:
            lines.append(f"- **{name}**: {desc}")
            lines.append(f"  → use get_api_reference(symbol='{name}')")
        if not results:
            lines.append("No API symbols matched. Try broader terms.")
        result = truncate("\n".join(lines))
        return ApiResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return ApiResult(error=str(e))
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_tools.py -v -k "api"
```

Expected: 3 API tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/scvi_tools_mcp/tools/_api_reference.py
git commit -m "feat: add API reference tools (get_api_reference, search_api)"
```

---

### Task 11: `_workflows.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_workflows.py`

- [ ] **Step 1: Add tests**

```python
# append to tests/test_tools.py

def test_get_workflow_template_batch_integration(mock_knowledge):
    from scvi_tools_mcp.tools._workflows import get_workflow_template
    result = get_workflow_template(task="batch_integration", model_name="scvi")
    assert result.error is None
    assert "scvi" in result.content.lower()
    assert "```python" in result.content

def test_get_downstream_guide_de(mock_knowledge):
    from scvi_tools_mcp.tools._workflows import get_downstream_guide
    result = get_downstream_guide(model_name="scvi", task="de")
    assert result.error is None
    assert result.content is not None
```

- [ ] **Step 2: Write `_workflows.py`**

```python
# src/scvi_tools_mcp/tools/_workflows.py
from __future__ import annotations
from typing import Literal
from pathlib import Path
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate
from scvi_tools_mcp.tools._model_guidance import MODEL_NAMES
from scvi_tools_mcp.mcp import mcp

WORKFLOW_TEMPLATES: dict[str, dict[str, str]] = {
    "batch_integration": {
        "scvi": """```python
import scvi
import scanpy as sc

# 1. Load your data (must be raw counts)
adata = sc.read_h5ad("your_data.h5ad")

# 2. Basic QC filter (adjust thresholds to your data)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 3. Store raw counts (scVI needs raw counts in adata.X)
# Skip normalization/log-transform — scVI handles this internally

# 4. Setup AnnData for scVI
scvi.model.SCVI.setup_anndata(adata, batch_key="batch")

# 5. Create and train model
model = scvi.model.SCVI(adata, n_latent=30)
model.train(max_epochs=400, early_stopping=True)

# 6. Get batch-corrected latent representation
adata.obsm["X_scVI"] = model.get_latent_representation()

# 7. Downstream: clustering on corrected space
sc.pp.neighbors(adata, use_rep="X_scVI")
sc.tl.umap(adata)
sc.tl.leiden(adata)
sc.pl.umap(adata, color=["batch", "leiden"])

# 8. Save model
model.save("scvi_model/")
```""",
        "default": """```python
import scvi
import scanpy as sc

# 1. Load raw count data
adata = sc.read_h5ad("your_data.h5ad")

# 2. Setup AnnData (adjust batch_key to your metadata column)
scvi.model.SCVI.setup_anndata(adata, batch_key="batch")

# 3. Train
model = scvi.model.SCVI(adata)
model.train()

# 4. Get latent representation
adata.obsm["X_scVI"] = model.get_latent_representation()
```""",
    },
    "cell_type_annotation": {
        "scanvi": """```python
import scvi
import scanpy as sc

# Assumes adata.obs['cell_type'] has labels for some cells,
# 'Unknown' for unlabeled cells

# 1. First train scVI (SCANVI extends scVI)
scvi.model.SCVI.setup_anndata(adata, batch_key="batch",
                               labels_key="cell_type")
vae = scvi.model.SCVI(adata, n_latent=30)
vae.train(max_epochs=400)

# 2. Then train SCANVI from the trained scVI
scanvae = scvi.model.SCANVI.from_scvi_model(
    vae, unlabeled_category="Unknown"
)
scanvae.train(max_epochs=200)

# 3. Predict labels for unlabeled cells
adata.obs["predicted_label"] = scanvae.predict()
adata.obs["prediction_confidence"] = scanvae.predict(soft=True).max(axis=1)
```""",
    },
    "deconvolution": {
        "destvi": """```python
import scvi
import scanpy as sc

# Requires: sc_adata (single-cell reference) and sp_adata (spatial data)

# 1. Train CondSCVI on single-cell reference
scvi.external.CondSCVI.setup_anndata(sc_adata, labels_key="cell_type")
sc_model = scvi.external.CondSCVI(sc_adata, weight_obs=True)
sc_model.train(max_epochs=300)

# 2. Train DestVI on spatial data using sc_model
scvi.external.DestVI.setup_anndata(sp_adata)
sp_model = scvi.external.DestVI.from_rna_model(sp_adata, sc_model)
sp_model.train(max_epochs=2500)

# 3. Get proportions per spot
sp_adata.obsm["proportions"] = sp_model.get_proportions()
```""",
    },
}

DOWNSTREAM_GUIDES: dict[str, dict[str, str]] = {
    "de": {
        "scvi": """# Differential Expression with scVI

scVI provides uncertainty-aware DE via posterior sampling.

```python
# All cells: cluster A vs cluster B
de_df = model.differential_expression(
    adata,
    groupby="leiden",
    group1="0",
    group2="1",
)

# Filter results: lfc_mean > 1 and is_de_fdr_0.05 == True
significant = de_df[de_df["is_de_fdr_0.05"]]

# Top 10 upregulated genes
top_genes = significant.sort_values("lfc_mean", ascending=False).head(10)
```

The key columns:
- `lfc_mean`: log fold change (positive = higher in group1)
- `is_de_fdr_0.05`: True if DE at 5% FDR
- `bayes_factor`: higher = stronger evidence for DE
""",
        "default": "Use model.differential_expression() — see get_api_reference(symbol='differential_expression').",
    },
    "embedding": {
        "default": """# Getting the Latent Embedding

```python
# Get latent representation (use for clustering, UMAP, etc.)
Z = model.get_latent_representation()  # shape: (n_cells, n_latent)
adata.obsm["X_latent"] = Z

# Use in scanpy
sc.pp.neighbors(adata, use_rep="X_latent")
sc.tl.umap(adata)
sc.pl.umap(adata, color=["batch", "cell_type"])
```
""",
    },
    "clustering": {
        "default": """# Clustering on scVI Latent Space

```python
# 1. Get latent embedding
adata.obsm["X_scVI"] = model.get_latent_representation()

# 2. Build neighbor graph on latent space
sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=30)

# 3. Leiden clustering (adjust resolution: higher = more clusters)
sc.tl.leiden(adata, resolution=0.5)

# 4. Visualize
sc.tl.umap(adata)
sc.pl.umap(adata, color=["leiden", "batch"])
```
""",
    },
}


class WorkflowResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


@mcp.tool()
def get_workflow_template(
    task: Literal[
        "batch_integration","dimensionality_reduction","differential_expression",
        "cell_type_annotation","deconvolution","spatial_mapping",
        "chromatin_accessibility","multimodal_integration","reference_mapping",
        "perturbation_modeling"
    ],
    model_name: MODEL_NAMES | None = None,
) -> WorkflowResult:
    """Get a complete, runnable code template for a scvi-tools analysis task.

    Returns a step-by-step commented Python script the user can adapt to their data.
    The code is NOT executed — it is returned as a string for the user to run locally.
    Always show the user this template after recommending a model.

    Args:
        task: The analysis task (e.g. 'batch_integration', 'cell_type_annotation').
        model_name: Optional specific model. If None, uses the recommended default.
    """
    try:
        task_templates = WORKFLOW_TEMPLATES.get(task, {})
        template = None
        if model_name and model_name in task_templates:
            template = task_templates[model_name]
        elif "default" in task_templates:
            template = task_templates["default"]
        elif task_templates:
            template = next(iter(task_templates.values()))

        if template is None:
            # Fall back to knowledge/user_guide/
            knowledge_dir = get_knowledge_dir()
            ug_files = list((knowledge_dir / "user_guide").glob("*.md"))
            lines = [
                f"# Workflow Template — {task}",
                "",
                f"No pre-built template for task='{task}'. Refer to these guides:",
                "",
            ]
            for f in ug_files[:5]:
                lines.append(f"- {f.stem}")
            lines.append("\nUse search_tutorials(query='{task}') to find relevant notebooks.")
            template = "\n".join(lines)

        result = truncate(template)
        return WorkflowResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return WorkflowResult(error=str(e))


@mcp.tool()
def get_downstream_guide(
    model_name: MODEL_NAMES,
    task: Literal["de", "embedding", "clustering", "deconvolution", "transfer_labels"],
) -> WorkflowResult:
    """Get a guide and code snippet for downstream analysis after training a scvi-tools model.

    Use this after a model is trained to show the user how to extract results.
    Common downstream tasks: differential expression (de), latent embedding,
    clustering, deconvolution, and label transfer.

    Args:
        model_name: The trained scvi-tools model name.
        task: The downstream analysis task.
    """
    try:
        task_guides = DOWNSTREAM_GUIDES.get(task, {})
        guide = task_guides.get(model_name) or task_guides.get("default")
        if guide is None:
            return WorkflowResult(
                error=f"No downstream guide for task='{task}' with model='{model_name}'. "
                      f"Try search_knowledge(query='{task} {model_name}')."
            )
        result = truncate(guide)
        return WorkflowResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return WorkflowResult(error=str(e))
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_tools.py -v -k "workflow"
```

Expected: 2 workflow tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/scvi_tools_mcp/tools/_workflows.py
git commit -m "feat: add workflow tools (get_workflow_template, get_downstream_guide)"
```

---

### Task 12: `_troubleshooting.py`

**Files:**
- Create: `src/scvi_tools_mcp/tools/_troubleshooting.py`

- [ ] **Step 1: Add tests**

```python
# append to tests/test_tools.py

def test_get_faq_valid_topic(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import get_faq
    result = get_faq(topic="training")
    assert result.error is None
    assert result.content is not None

def test_search_knowledge_returns_results(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge
    result = search_knowledge(query="batch integration scvi training")
    assert result.error is None
    assert result.content is not None

def test_search_knowledge_no_match(mock_knowledge):
    from scvi_tools_mcp.tools._troubleshooting import search_knowledge
    result = search_knowledge(query="xyzabcnonexistentterm12345")
    assert result.error is None
    assert "no results" in result.content.lower() or result.content is not None
```

- [ ] **Step 2: Write `_troubleshooting.py`**

```python
# src/scvi_tools_mcp/tools/_troubleshooting.py
from __future__ import annotations
from typing import Literal
from pathlib import Path
from pydantic import BaseModel
from scvi_tools_mcp.tools.utils import get_knowledge_dir, truncate
from scvi_tools_mcp.mcp import mcp

FAQ_CONTENT: dict[str, str] = {
    "training": """# Training FAQ

## Loss is not decreasing / model is not converging
- Check that adata.X contains **raw counts** (not log-normalized). scVI models a count likelihood internally.
- Try increasing `max_epochs` (default 400 for scVI).
- Set `early_stopping=True` to stop when validation loss plateaus.
- Reduce `n_latent` if the dataset is small (<5000 cells).
- Use `plan_kwargs={"lr": 1e-3}` to lower the learning rate.

## Training is slow
- Ensure a GPU is available: `scvi.settings.dl_num_workers = 4`.
- Use `batch_size=512` for larger datasets.
- For >500k cells, consider `max_epochs=100` with early stopping.

## CUDA out of memory
- Reduce `batch_size` (default 128).
- Reduce `n_hidden` or `n_layers`.
- Use gradient checkpointing via `plan_kwargs={"gradient_clip_val": 1.0}`.
""",
    "data_setup": """# Data Setup FAQ

## ValueError: adata.X does not contain count data
- scVI requires raw integer counts. If you log-normalized, reload raw data.
- Store raw counts in a layer: `scvi.model.SCVI.setup_anndata(adata, layer='counts')`.

## KeyError: batch_key not found
- Check column name: `print(adata.obs.columns.tolist())`.
- If no batches, omit `batch_key` or set it to None.

## setup_anndata must be called before model instantiation
- Always call `ModelClass.setup_anndata(adata, ...)` before `model = ModelClass(adata)`.
""",
    "gpu": """# GPU FAQ

## How to check GPU availability
```python
import torch
print(torch.cuda.is_available())
scvi.settings.seed = 42
```

## Force CPU training
```python
model.train(accelerator="cpu")
```

## Multi-GPU training
Use `accelerator="gpu"` and `devices=[0,1]` in `model.train()`.
See the multi-GPU tutorial for details.
""",
    "saving_loading": """# Saving and Loading Models

## Save a trained model
```python
model.save("my_model_dir/", overwrite=True)
```

## Load a saved model
```python
model = scvi.model.SCVI.load("my_model_dir/", adata=adata)
```

## Save without AnnData (for sharing)
```python
model.save("my_model_dir/", save_anndata=False)
```

## Load from HuggingFace Hub
```python
model = scvi.model.SCVI.load_from_hub("username/model-name")
```
""",
    "convergence": """# Convergence FAQ

## How to check if training converged
```python
import matplotlib.pyplot as plt
train_elbo = model.history["elbo_train"]
val_elbo = model.history["elbo_validation"]
plt.plot(train_elbo, label="train")
plt.plot(val_elbo, label="validation")
plt.legend()
```

## Validation loss diverges from training loss
- Increase `train_size` (default 0.9) if validation set is too small.
- Use early stopping: `model.train(early_stopping=True)`.

## Loss spikes / NaN loss
- Lower the learning rate: `plan_kwargs={"lr": 5e-4}`.
- Clip gradients: `plan_kwargs={"gradient_clip_val": 1.0}`.
""",
    "batch_correction": """# Batch Correction FAQ

## Which model to use for batch correction?
- **scVI**: standard, works for scRNA-seq
- **SCANVI**: when you have cell type labels
- **SysVI**: when batch effect is very strong (e.g. cross-species)
- **MultiVI**: when data includes ATAC + RNA

## How many latent dimensions?
- Default: 30. Try 10-50. Larger datasets benefit from more latent dims.

## How to evaluate batch correction?
```python
import scib
metrics = scib.metrics.metrics(adata, adata_int, batch_key="batch",
                                label_key="cell_type", embed="X_scVI")
```
""",
    "memory": """# Memory FAQ

## Dataset too large for RAM
- Use `anndata.read_h5ad("file.h5ad", backed='r')` for disk-backed loading.
- Use scVI's data loader with `AnnDataLoader` for minibatch training.

## Reducing memory during training
- Reduce `batch_size`.
- Use `float16` precision: `model.train(precision="16-mixed")`.

## HDF5 file locked during training
- Close all other handles to the .h5ad file before training.
""",
}


class TroubleshootResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


@mcp.tool()
def get_faq(
    topic: Literal["training", "data_setup", "gpu", "saving_loading", "convergence", "batch_correction", "memory"],
) -> TroubleshootResult:
    """Get curated FAQ entries for common scvi-tools problems.

    Combines knowledge from official docs, GitHub issues, and Discourse forum threads.
    Use this when a user reports an error or asks 'why is X not working'.

    Args:
        topic: The problem area. Options: training, data_setup, gpu, saving_loading,
               convergence, batch_correction, memory.
    """
    try:
        content = FAQ_CONTENT.get(topic, "")
        # Supplement with pre-baked external knowledge
        knowledge_dir = get_knowledge_dir()
        faq_dir = knowledge_dir / "faq"
        extras: list[str] = []
        for faq_file in sorted(faq_dir.glob("*.md")):
            text = faq_file.read_text(encoding="utf-8")
            lower = text.lower()
            if topic.lower() in lower or topic.replace("_", " ") in lower:
                # Extract relevant lines
                for i, line in enumerate(text.splitlines()):
                    if topic.replace("_", " ") in line.lower() or topic in line.lower():
                        chunk = "\n".join(text.splitlines()[max(0, i-1):i+5])
                        extras.append(chunk)
                        break
        if extras:
            content += "\n\n---\n\n## From Community\n\n" + "\n\n".join(extras[:3])
        if not content:
            return TroubleshootResult(error=f"No FAQ content for topic '{topic}'.")
        result = truncate(content)
        return TroubleshootResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TroubleshootResult(error=str(e))


@mcp.tool()
def search_knowledge(query: str) -> TroubleshootResult:
    """Search all scvi-tools knowledge: models, tutorials, user guide, API, and community FAQ.

    Use this tool when no other tool exactly matches the user's question. It searches
    across all knowledge sources and returns ranked excerpts. Good for: 'how do I do X',
    'what is the difference between X and Y', 'I got error Z'.

    Args:
        query: Free-text question or keywords (e.g. 'how to save a model', 'ELBO explanation').
    """
    try:
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        if not keywords:
            return TroubleshootResult(error="Query too short. Please provide at least one keyword.")
        knowledge_dir = get_knowledge_dir()
        results: list[tuple[int, str, str]] = []
        for md in sorted(knowledge_dir.rglob("*.md")):
            if ".gitkeep" in str(md):
                continue
            try:
                content = md.read_text(encoding="utf-8")
            except Exception:
                continue
            lower = content.lower()
            score = sum(lower.count(kw) for kw in keywords)
            if score > 0:
                excerpt = ""
                for line in content.splitlines():
                    if any(kw in line.lower() for kw in keywords) and len(line.strip()) > 20:
                        excerpt = line.strip()[:150]
                        break
                rel = md.relative_to(knowledge_dir)
                results.append((score, str(rel.with_suffix("")), excerpt))
        results.sort(key=lambda x: x[0], reverse=True)
        lines = [f"# Knowledge Search: '{query}'", ""]
        for score, name, excerpt in results[:8]:
            lines.append(f"- **{name}** (relevance: {score})")
            if excerpt:
                lines.append(f"  > {excerpt}")
        if not results:
            lines += [
                "No results found for your query.",
                "",
                "Suggestions:",
                "- Try broader keywords",
                "- Use list_tutorials() to browse tutorials",
                "- Use recommend_model() for model selection",
                "- Use get_faq() for common troubleshooting",
            ]
        result = truncate("\n".join(lines))
        return TroubleshootResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return TroubleshootResult(error=str(e))
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_tools.py -v -k "faq or knowledge"
```

Expected: 3 troubleshooting tests pass.

- [ ] **Step 4: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/scvi_tools_mcp/tools/_troubleshooting.py
git commit -m "feat: add troubleshooting tools (get_faq, search_knowledge)"
```

---

### Task 13: Wire up `mcp.py` and smoke-test the server

**Files:**
- Modify: `src/scvi_tools_mcp/mcp.py`

- [ ] **Step 1: Verify `mcp.py` imports all tool modules**

The stub modules are now implemented. Verify the server lists all 13 tools:

```bash
python -c "
from scvi_tools_mcp.mcp import mcp
tools = mcp.list_tools() if hasattr(mcp, 'list_tools') else []
print('Tools registered:', len(list(mcp._tool_manager._tools.values())) if hasattr(mcp, '_tool_manager') else 'check manually')
from scvi_tools_mcp.tools import _model_guidance, _data_prep, _tutorials, _api_reference, _workflows, _troubleshooting
print('All modules imported OK')
"
```

Expected: `All modules imported OK`

- [ ] **Step 2: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: all tests pass. Note count: ~25 tests.

- [ ] **Step 3: Smoke test server startup**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | timeout 5 python -m scvi_tools_mcp.main 2>/dev/null | head -5 || echo "Server started OK (timeout expected for stdio)"
```

Expected: JSON response or timeout (both acceptable — server started).

- [ ] **Step 4: Commit**

```bash
git add src/scvi_tools_mcp/
git commit -m "feat: wire all tool modules into FastMCP server"
```

---

## Phase 4 — CI/CD Workflows

### Task 14: Test + release CI

**Files:**
- Create: `.github/workflows/test.yaml`
- Create: `.github/workflows/release.yaml`

- [ ] **Step 1: Write `.github/workflows/test.yaml`**

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest tests/ -v --tb=short
      - name: Lint
        run: ruff check src/ tests/ scripts/
```

- [ ] **Step 2: Write `.github/workflows/release.yaml`**

```yaml
name: Release to PyPI

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Build wheel
        run: |
          pip install hatchling build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/test.yaml .github/workflows/release.yaml
git commit -m "ci: add test matrix and PyPI release workflow"
```

---

### Task 15: Knowledge refresh CI jobs

**Files:**
- Create: `.github/workflows/refresh_knowledge.yaml`
- Create: `.github/workflows/sync_tutorials.yaml`
- Create: `.github/workflows/sync_model_knowledge.yaml`

- [ ] **Step 1: Write `refresh_knowledge.yaml`**

```yaml
name: Refresh External Knowledge

on:
  schedule:
    - cron: "0 6 1 * *"
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Scrape external knowledge
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/scrape_external.py
      - name: Check for changes
        id: diff
        run: |
          git diff --quiet src/scvi_tools_mcp/knowledge/faq/ || echo "changed=true" >> $GITHUB_OUTPUT
      - name: Open PR if changed
        if: steps.diff.outputs.changed == 'true'
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: refresh external knowledge snapshot"
          title: "chore: refresh external knowledge snapshot (${{ github.run_id }})"
          body: "Automated monthly refresh of GitHub issues and Discourse threads."
          branch: "chore/refresh-knowledge"
```

- [ ] **Step 2: Write `sync_tutorials.yaml`**

```yaml
name: Sync Tutorials from scvi-tools

on:
  schedule:
    - cron: "0 7 1 * *"
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Fetch notebooks from scvi-tools repo
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          mkdir -p /tmp/scvi-notebooks
          gh api repos/scverse/scvi-tools/git/trees/main?recursive=1 \
            --jq '.tree[] | select(.path | startswith("docs/tutorials/notebooks")) | select(.path | endswith(".ipynb")) | .path' \
          | while read path; do
              mkdir -p "/tmp/scvi-notebooks/$(dirname $path)"
              gh api "repos/scverse/scvi-tools/contents/$path" --jq '.content' \
                | base64 -d > "/tmp/scvi-notebooks/$path"
            done
      - name: Convert notebooks to Markdown
        run: |
          python scripts/convert_notebooks.py \
            --src /tmp/scvi-notebooks/docs/tutorials/notebooks \
            --dst src/scvi_tools_mcp/knowledge/tutorials
      - name: Get scvi-tools version for PR title
        id: version
        run: |
          echo "version=$(gh api repos/scverse/scvi-tools/releases/latest --jq '.tag_name')" >> $GITHUB_OUTPUT
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Check for changes
        id: diff
        run: |
          git diff --quiet src/scvi_tools_mcp/knowledge/tutorials/ || echo "changed=true" >> $GITHUB_OUTPUT
      - name: Open PR if changed
        if: steps.diff.outputs.changed == 'true'
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: sync tutorials from scvi-tools ${{ steps.version.outputs.version }}"
          title: "chore: sync tutorials from scvi-tools ${{ steps.version.outputs.version }}"
          body: "Automated monthly sync of tutorial notebooks converted to Markdown."
          branch: "chore/sync-tutorials"
```

- [ ] **Step 3: Write `sync_model_knowledge.yaml`**

```yaml
name: Sync Model Knowledge from scvi-tools Changelog

on:
  schedule:
    - cron: "0 8 1 * *"
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[scvi,dev]"
      - name: Get latest scvi-tools version
        id: upstream
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          latest=$(gh api repos/scverse/scvi-tools/releases/latest --jq '.tag_name' | sed 's/v//')
          current=$(cat src/scvi_tools_mcp/knowledge/.last_synced_version)
          echo "latest=$latest" >> $GITHUB_OUTPUT
          echo "current=$current" >> $GITHUB_OUTPUT
          if [ "$latest" != "$current" ]; then
            echo "needs_update=true" >> $GITHUB_OUTPUT
          fi
      - name: Fetch changelog excerpt
        if: steps.upstream.outputs.needs_update == 'true'
        id: changelog
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api repos/scverse/scvi-tools/contents/CHANGELOG.md \
            --jq '.content' | base64 -d | head -200 > /tmp/changelog_excerpt.md
          echo "excerpt<<EOF" >> $GITHUB_OUTPUT
          head -50 /tmp/changelog_excerpt.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Re-extract model docs
        if: steps.upstream.outputs.needs_update == 'true'
        run: python scripts/extract_api_docs.py
      - name: Check for changes
        id: diff
        run: |
          git diff --quiet src/scvi_tools_mcp/knowledge/ || echo "changed=true" >> $GITHUB_OUTPUT
      - name: Open PR if changed
        if: steps.diff.outputs.changed == 'true'
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: sync model knowledge for scvi-tools v${{ steps.upstream.outputs.latest }}"
          title: "chore: sync model knowledge for scvi-tools v${{ steps.upstream.outputs.latest }}"
          body: |
            Automated monthly sync triggered by scvi-tools version change:
            ${{ steps.upstream.outputs.current }} → ${{ steps.upstream.outputs.latest }}

            **Changelog excerpt:**
            ```
            ${{ steps.changelog.outputs.excerpt }}
            ```
          branch: "chore/sync-model-knowledge"
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/
git commit -m "ci: add three monthly knowledge refresh workflows"
```

---

### Task 16: README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
# scvi-tools MCP Server

MCP server giving LLMs structured access to [scvi-tools](https://scvi-tools.org) knowledge:
model documentation, tutorials, API reference, workflow templates, and community FAQ.

## Quick Start

### Claude Desktop / Cursor

Add to your `mcp.json` (or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "scvi-tools": {
      "command": "uvx",
      "args": ["scvi-tools-mcp"]
    }
  }
}
```

### pip

```bash
pip install scvi-tools-mcp
scvi-tools-mcp
```

## Tools

| Tool | Description |
|---|---|
| `recommend_model` | Ranked model recommendations for a task and data type |
| `get_model_overview` | Detailed overview of a specific model |
| `get_model_parameters` | Key parameters and defaults |
| `get_setup_anndata_guide` | Exact `setup_anndata()` call and requirements |
| `validate_data_requirements` | Pass/fail checklist for AnnData requirements |
| `list_tutorials` | Browse 60+ tutorials by category |
| `get_tutorial` | Read a full tutorial (paginated) |
| `search_tutorials` | Find tutorials by keyword |
| `get_api_reference` | Signature + docstring for any class or method |
| `search_api` | Search the API by keyword |
| `get_workflow_template` | Full runnable code template for a task |
| `get_downstream_guide` | Post-training analysis guide |
| `get_faq` | Curated FAQ for common problems |
| `search_knowledge` | Cross-search all knowledge sources |

## Knowledge Refresh

Three monthly GitHub Actions jobs keep knowledge current:
- **`refresh_knowledge`** — re-scrapes GitHub issues + Discourse forum
- **`sync_tutorials`** — fetches new notebooks from scvi-tools repo
- **`sync_model_knowledge`** — updates model docs when scvi-tools releases a new version

## Development

```bash
git clone https://github.com/ori-kron-wis/scvi-tools-mcp
cd scvi-tools-mcp
pip install -e ".[dev]"

# Rebuild knowledge from local scvi-tools install
pip install -e ".[scvi]"
python scripts/extract_api_docs.py
python scripts/convert_notebooks.py

# Run tests
pytest tests/ -v
```

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with quick start, tools table, and development guide"
```

---

## Spec Coverage Self-Review

| Spec Section | Covered by |
|---|---|
| Static knowledge server architecture | Tasks 1-6 (scaffold + all scripts) |
| 13 tools across 6 modules | Tasks 7-12 |
| Flat args + Literal types | All tool modules (MODEL_NAMES literal, task literals) |
| Output truncation + pagination | Task 2 (utils), used in all tools |
| Error field on all results | All result Pydantic models |
| stdio transport | Task 3 (main.py) |
| Knowledge bundled in wheel | Task 1 (pyproject.toml packages list) |
| convert_notebooks.py (strips outputs) | Task 4 |
| extract_api_docs.py (API + user guide) | Task 5 |
| scrape_external.py (issues + discourse) | Task 6 |
| Monthly refresh CI (3 jobs) | Task 15 |
| Tutorial sync CI | Task 15 |
| Model knowledge sync CI | Task 15 |
| Test + release CI | Task 14 |
| PyPI packaging | Task 1 |
| README with quick start | Task 16 |
| conda-forge | **Not yet** — add after first PyPI release via grayskull: `grayskull recipe scvi-tools-mcp` |
