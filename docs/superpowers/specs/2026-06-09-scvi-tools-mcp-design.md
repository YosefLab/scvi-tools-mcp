# scvi-tools MCP Server — Design Spec

**Date:** 2026-06-09
**Status:** Approved — ready for implementation planning
**Author:** ori-kron-wis

---

## 1. Overview

A Model Context Protocol (MCP) server that gives LLMs structured, curated access to scvi-tools knowledge: model documentation, tutorials, API reference, workflow templates, and community FAQ. No runtime model execution — the server is a pure knowledge layer. The LLM uses it to guide users through scvi-tools analyses and answer developer questions.

**Reference implementation:** [anndata-mcp](https://github.com/biocontext-ai/anndata-mcp) (same scverse ecosystem, same FastMCP + stdio pattern).

---

## 2. Goals

- Help **bioinformaticians** choose and configure the right scvi-tools model for their task.
- Help **developers** understand model internals, API contracts, and contribution patterns.
- Keep knowledge current via automated monthly CI jobs — no manual maintenance required.
- Design every tool description as explicit LLM documentation (docstrings are the UI).
- Flat schemas, bounded output, deterministic responses — no surprises for the model.

---

## 3. Non-goals

- Runtime model training or inference (no `scvi-tools` required at server runtime).
- Live network calls during tool execution.
- HTTP transport (stdio only for now).
- Wrapping or proxying the scvi-tools Python API directly.

---

## 4. Architecture

### 4.1 Approach: Static Knowledge Server

All knowledge is baked into the package as `.md` files at build time. Tools are structured lookups into this knowledge base. `scvi-tools` is an optional soft dependency (`pip install scvi-tools-mcp[scvi]`) used only by refresh scripts, not by the server itself.

**Data flow:**

```
LLM calls tool (flat args)
    │
    ▼
Tool function → Pydantic arg validation
    │
    ▼
utils.load_knowledge(path)   ← reads bundled .md from knowledge/
    │
    ▼
utils.truncate(content, max_chars=4000)
    │
    ▼
Return Pydantic result { data, truncated: bool, page: int, total_pages: int, error: str | None }
```

Knowledge files are bundled **inside the wheel** via hatchling `include` — no filesystem assumptions post-install.

### 4.2 Transport

stdio only. Compatible with Claude Desktop, Cursor, and any client supporting `mcp.json`:

```json
{ "command": "uvx", "args": ["scvi-tools-mcp"] }
```

---

## 5. Repository Structure

```
scvi-tools-mcp/
├── src/scvi_tools_mcp/
│   ├── __init__.py
│   ├── main.py                    ← entry point, runs FastMCP server via run_app()
│   ├── mcp.py                     ← FastMCP instance + imports all tool modules
│   └── tools/
│       ├── __init__.py
│       ├── _model_guidance.py     ← recommend_model, get_model_overview, get_model_parameters
│       ├── _data_prep.py          ← get_setup_anndata_guide, validate_data_requirements
│       ├── _tutorials.py          ← list_tutorials, get_tutorial, search_tutorials
│       ├── _api_reference.py      ← get_api_reference, search_api
│       ├── _workflows.py          ← get_workflow_template, get_downstream_guide
│       ├── _troubleshooting.py    ← get_faq, search_knowledge
│       └── utils.py               ← load_knowledge(), truncate(), paginate()
├── knowledge/
│   ├── models/                    ← one .md per model (~30 files)
│   ├── tutorials/                 ← ~40 converted .ipynb → .md files
│   ├── user_guide/                ← copied from scvi-tools docs/user_guide/
│   ├── api/                       ← extracted docstrings per public class
│   └── faq/
│       ├── github_issues.md       ← pre-scraped top GitHub issues snapshot
│       └── discourse_threads.md   ← pre-scraped Discourse forum snapshot
├── scripts/
│   ├── convert_notebooks.py       ← .ipynb → .md (strips outputs, keeps code + markdown)
│   ├── extract_api_docs.py        ← pulls docstrings from scvi-tools source into knowledge/api/
│   └── scrape_external.py         ← fetches GitHub issues + Discourse threads snapshot
├── .github/workflows/
│   ├── test.yaml                  ← CI: test matrix Python 3.11/3.12/3.13
│   ├── release.yaml               ← publish to PyPI on tag
│   ├── refresh_knowledge.yaml     ← monthly: re-scrape issues + Discourse, open PR
│   ├── sync_tutorials.yaml        ← monthly: fetch new .ipynb from scvi-tools, convert, open PR
│   └── sync_model_knowledge.yaml  ← monthly: read scvi-tools CHANGELOG, update model .md + Literal enums
├── tests/
│   ├── conftest.py
│   ├── test_tools.py
│   └── test_utils.py
├── docs/
│   └── superpowers/specs/         ← this file
├── pyproject.toml
└── README.md
```

---

## 6. Tools Catalog

All tools follow these invariants:
- **Flat args** — no nested objects, no dicts as parameters.
- **Literals for constrained choices** — model names, task types, categories are all `Literal[...]`.
- **Output bounded** — max ~4000 chars per response; large content is paginated (`page`, `page_size`).
- **Error field** — every result model has `error: str | None`; tools never raise to the transport layer.
- **Docstrings are the UI** — every tool description is written as explicit LLM instructions.

### 6.1 `_model_guidance.py`

**`recommend_model`**
Args: `task: Literal["batch_integration","dimensionality_reduction","differential_expression","cell_type_annotation","deconvolution","spatial_mapping","chromatin_accessibility","multimodal_integration","reference_mapping","perturbation_modeling"]`, `data_type: Literal["scrna","cite_seq","spatial","atac","multiome"]`, `has_protein: bool`, `has_accessibility: bool`, `n_batches: int`
Returns: ranked list of models with rationale for each recommendation.

**`get_model_overview`**
Args: `model_name: Literal[...all models — exact list derived from knowledge/models/ at implementation time]`
Returns: description, use case, required inputs, outputs, advantages, limitations, key citations.

**`get_model_parameters`**
Args: `model_name: Literal[...]`
Returns: key `__init__` and `train()` parameters with descriptions and recommended defaults.

### 6.2 `_data_prep.py`

**`get_setup_anndata_guide`**
Args: `model_name: Literal[...]`
Returns: exact `setup_anndata()` call signature, required obs/var fields, optional fields, common setup mistakes.

**`validate_data_requirements`**
Args: `model_name: Literal[...]`, `obs_keys: list[str]`, `var_keys: list[str]`, `has_raw: bool`
Returns: pass/fail checklist for each requirement, with fix instructions for any failures.

### 6.3 `_tutorials.py`

**`list_tutorials`**
Args: `category: Literal["scrna","multimodal","spatial","atac","hub","quick_start","cytometry","dev","r","use_cases"] | None`
Returns: list of tutorial names + one-line descriptions, grouped by category.

**`get_tutorial`**
Args: `tutorial_name: str`, `page: int = 1`, `page_size: int = 200`
Returns: paginated .md content of the tutorial (code + markdown, no outputs).

**`search_tutorials`**
Args: `query: str`
Returns: tutorials ranked by keyword relevance with a matching excerpt from each.

### 6.4 `_api_reference.py`

**`get_api_reference`**
Args: `symbol: str` (e.g. `"SCVI"`, `"SCVI.train"`, `"DecodingParams"`)
Returns: full signature + docstring for the class or function.

**`search_api`**
Args: `query: str`
Returns: list of matching public symbols with short descriptions.

### 6.5 `_workflows.py`

**`get_workflow_template`**
Args: `task: Literal[...same as recommend_model task list]`, `model_name: Literal[...] | None`
Returns: step-by-step commented code template as a string (not executed — returned for the LLM to show the user).

**`get_downstream_guide`**
Args: `model_name: Literal[...]`, `task: Literal["de","embedding","clustering","deconvolution","transfer_labels"]`
Returns: prose guide + code snippet for the downstream analysis task.

### 6.6 `_troubleshooting.py`

**`get_faq`**
Args: `topic: Literal["training","data_setup","gpu","saving_loading","convergence","batch_correction","memory"]`
Returns: curated FAQ entries sourced from docs, pre-baked GitHub issues, and Discourse threads.

**`search_knowledge`** *(catch-all)*
Args: `query: str`
Returns: cross-searches models, FAQ, user_guide, discourse snapshot — ranked excerpts. Docstring explicitly instructs: *"Use this tool when no other tool exactly matches the question."*

---

## 7. Error Handling

Every tool returns a Pydantic result model:

```python
class ModelOverviewResult(BaseModel):
    model_name: str | None = None
    content: str | None = None
    truncated: bool = False
    page: int = 1
    total_pages: int = 1
    error: str | None = None  # set on any failure; rest of fields None
```

Three error classes, all surfaced in `error`, never raised:

| Class | Example message |
|---|---|
| Not found | `"Model 'foo' not found. Available: scvi, scanvi, totalvi, ..."` |
| Load failure | `"Knowledge file missing. Run scripts/refresh_knowledge.py to rebuild."` |
| Truncation | Not an error — flagged via `truncated=True` + `"Call again with page=2 to continue."` |

---

## 8. Knowledge Refresh — CI Jobs

All three jobs run on `schedule: cron: '0 6 1 * *'` (1st of each month, 06:00 UTC) and support `workflow_dispatch` for manual runs. Each opens a PR if a diff is found; no auto-merge.

### `refresh_knowledge.yaml`
1. Run `scripts/scrape_external.py` → rewrites `knowledge/faq/github_issues.md` + `knowledge/faq/discourse_threads.md`
2. Open PR titled `chore: refresh external knowledge snapshot (YYYY-MM)`

### `sync_tutorials.yaml`
1. Fetch `docs/tutorials/notebooks/**/*.ipynb` from `scverse/scvi-tools` via `gh api`
2. Run `scripts/convert_notebooks.py` on new or changed notebooks
3. Open PR titled `chore: sync tutorials from scvi-tools vX.Y.Z`

`convert_notebooks.py` strips all cell outputs (no data, no plots, no large arrays). Keeps markdown cells + code cells as fenced blocks. Produces clean, small `.md` files.

### `sync_model_knowledge.yaml`
1. Fetch `CHANGELOG.md` from `scverse/scvi-tools` via `gh api`
2. Compare latest version tag against `knowledge/.last_synced_version`
3. If newer: extract added/changed model entries from changelog
4. Re-run `scripts/extract_api_docs.py` for changed model classes → regenerate `knowledge/models/<model>.md`
5. Update `Literal[...]` enums in tool schemas if a new model was added
6. Open PR titled `chore: sync model knowledge for scvi-tools vX.Y.Z` with changelog excerpt as PR body

---

## 9. Packaging

```toml
[build-system]
requires = ["hatchling"]

[project]
name = "scvi-tools-mcp"
requires-python = ">=3.11"
dependencies = ["fastmcp", "pydantic>=2"]

[project.optional-dependencies]
scvi = ["scvi-tools>=1.0"]
dev  = ["pytest", "pytest-asyncio", "ruff", "pre-commit", "nbconvert"]

[project.scripts]
scvi-tools-mcp = "scvi_tools_mcp.main:run_app"

[tool.hatch.build.targets.wheel]
include = ["src/scvi_tools_mcp", "knowledge"]
```

Conda-forge feedstock submitted after first PyPI release via `grayskull` recipe auto-generation.

---

## 10. Testing Strategy

- Tests never require `scvi-tools` installed.
- Knowledge files loaded from fixtures (minimal `.md` files in `tests/`).
- No GPU required in CI.

| File | Coverage |
|---|---|
| `test_tools.py` | One test per tool: valid input → expected output shape; unknown input → `error` field set (not exception); truncation → `truncated=True` + `total_pages > 1` |
| `test_utils.py` | `truncate()`, `load_knowledge()`, `paginate()` |
| `test_scripts.py` | `convert_notebooks.py` on a real fixture `.ipynb` → valid `.md` |

CI matrix: Python 3.11, 3.12, 3.13 × stable deps.

---

## 11. Security

- No user filesystem reads (knowledge-only server).
- No `eval`, no subprocess calls in tool handlers.
- `scrape_external.py` runs only in CI, never at tool-call time.
- No HTTP surface exposed (stdio transport).

---

## 12. Existing scvi-tools Skills Integration

The existing Claude Code skills (`scvi-integration`, `scanvi-label-transfer`, `totalvi-citeseq-analysis`, etc.) and this MCP server are complementary:
- **Skills** guide Claude Code sessions (in-IDE, interactive).
- **MCP server** serves any MCP-compatible LLM client.

The `.md` files in `knowledge/models/` can be kept in sync with skill content as both evolve.

---

## 13. Open Questions (resolved before implementation)

None — all design decisions confirmed by user on 2026-06-09.
