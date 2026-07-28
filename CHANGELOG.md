# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- scviva-tools knowledge source and tools — the companion spatial toolkit (ResolVI, DestVI, scVIVA, GIMVI, DiagVI, Stereoscope, Tangram, Harreman):
  - `knowledge/scviva_tools/models/`, `knowledge/scviva_tools/api/`, and `knowledge/scviva_tools/tutorials/` bundled offline snapshot
  - `list_scviva_models`, `get_scviva_model`, `list_scviva_tutorials`, `get_scviva_tutorial` MCP tools
  - `scripts/extract_scviva_api_docs.py` and monthly `sync_scviva_tools_knowledge.yaml` / `sync_scviva_tools_tutorials.yaml` refresh workflows
- scib-metrics knowledge source and tools — accelerated integration-benchmarking metrics (12 metric functions plus the `Benchmarker`/`BioConservation`/`BatchCorrection` orchestration classes):
  - `knowledge/scib_metrics/api/` and `knowledge/scib_metrics/tutorials/` bundled offline snapshot
  - `list_scib_metrics`, `get_scib_metric`, `list_scib_metrics_tutorials`, `get_scib_metrics_tutorial` MCP tools
  - `scripts/extract_scib_metrics_api_docs.py` and monthly `sync_scib_metrics_knowledge.yaml` / `sync_scib_metrics_tutorials.yaml` refresh workflows
- `scripts/_apidoc_utils.py` — shared class/function signature and docstring extraction helpers, used by `extract_api_docs.py` and the two new extraction scripts
- `optional-dependencies.scviva` and `optional-dependencies.scib` extras in `pyproject.toml`

## [0.1.5] - 2026-07-27

### Added

- `.github/dependabot.yml` — weekly grouped updates for GitHub Actions
- `.editorconfig` and `.vscode/` (settings, extensions, launch configs) for consistent contributor tooling
- `zizmor`, `pyproject-fmt`, and `check-merge-conflict` pre-commit hooks
- Structured YAML issue forms (`bug_report.yml`, `feature_request.yml`) replacing the old Markdown templates
- Changelog and package API reference pages in the Read the Docs documentation

### Changed

- Adopted the parts of the scverse cookiecutter template refresh that fit this repo: `pyproject.toml` dev/doc extras moved to `[dependency-groups]`, hardened and digest-pinned `test.yaml`/`release.yaml`, `fail_on_warning` enabled for the Read the Docs Sphinx build
- Dropped Python 3.11 support; now supports 3.12, 3.13, and 3.14 (default 3.13)
- Bumped pinned GitHub Actions versions (`actions/checkout` v4 → v5, `actions/setup-python` v5 → v6) across all workflows
- Updated copyright notice in `docs/conf.py`
- Enhanced `README.md` and `docs/installation.md` with Claude Code and OpenAI Codex MCP integration instructions
- Standardized the human-facing project name as **scVI-Tools MCP**

### Fixed

- HTML rendering of the architecture block diagram on Read the Docs
- Set `GH_REPO` in the GitHub release job so `gh release create` can resolve the repository without a checkout
- Updated development installation commands to install the PEP 735 `dev` dependency group
- Encoded issue-form labels as arrays so GitHub accepts and displays both forms

## [0.1.4.1] - 2026-07-02

### Fixed

- Added the `fastmcp[server]` extra to `pyproject.toml` — installs the `starlette` dependency required by fastmcp/mcp that was missing

## [0.1.4] - 2026-07-02

### Changed

- License changed from MIT to BSD 3-Clause, with badge added to `README.md`
- Knowledge base refreshed via the automated monthly sync workflows (external knowledge snapshot, scvi-tools model docs, tutorials, Hugging Face Hub snapshot)

---

## [0.1.3] - 2026-06-18

### Added

- DiagVI spatial proteomics + transcriptomics tutorials under `knowledge/tutorials/multimodal/`
- 20 scvi skill SKILL.md files + scvi-tools plugin SKILL.md + 12 reference docs in `knowledge/skills/`
- `docs/installation.md`, `docs/faq.md`, `docs/references.md`, `docs/references.bib`
- `.codecov.yaml`, `.markdownlint.yaml`, `.readthedocs.yaml`, `Dockerfile`, `LICENSE`
- `.github/ISSUE_TEMPLATE/` (bug report, feature request, release checklist)
- Updated `.pre-commit-config.yaml` to match scvi-tools pattern (blacken-docs, prettier, mdformat, markdownlint-fix, pre-commit-hooks)
- Second Discourse source URL in `scrape_external.py`; topics deduplicated and sorted by views
- Hugging Face Hub knowledge source for the official `scvi-tools` organization:
  - `knowledge/hub/models.json` and `knowledge/hub/summary.md` bundled offline snapshot
  - `list_hub_models`, `get_hub_model`, `suggest_hub_models` MCP tools
  - `scripts/scrape_huggingface_hub.py` and quarterly `sync_huggingface_hub.yaml` refresh workflow

### Fixed

- `_data_prep.py`: long setup_call strings wrapped to stay under 120-char line limit
- `tests/test_tools.py`: `import pytest` moved to top of file (E402)
- `pyproject.toml`: notebook fixtures excluded from ruff linting (F821)

## [0.1.0] - 2026-06-09

### Added

- **14 MCP tools** across 6 modules:
  - `recommend_model`, `get_model_overview`, `get_model_parameters` — model selection and documentation
  - `get_setup_anndata_guide`, `validate_data_requirements` — data preparation and validation
  - `list_tutorials`, `get_tutorial`, `search_tutorials` — tutorial browsing and search
  - `get_api_reference`, `search_api` — API reference lookup
  - `get_workflow_template`, `get_downstream_guide` — analysis workflow templates
  - `get_faq`, `search_knowledge` — FAQ and cross-knowledge search
- **Bundled knowledge base** (`knowledge/`):
  - 15 model `.md` files (scVI, scANVI, TotalVI, MultiVI, PeakVI, LinearSCVI, MrVI, Stereoscope, CellAssign, SOLO, GIMVI, veloVI, ContrastiveVI, SCBASSET, SysVI)
  - 61 tutorials converted from `.ipynb` to `.md` (outputs stripped, code + prose retained)
  - 15 API reference files extracted from scvi-tools 1.4.3 docstrings
  - 10 user guide files
  - GitHub issues snapshot (31 issues) and Discourse threads snapshot (30 threads)
- **Scripts** for knowledge refresh:
  - `scripts/convert_notebooks.py` — `.ipynb` → `.md` converter
  - `scripts/extract_api_docs.py` — docstring extractor from scvi-tools source
  - `scripts/scrape_external.py` — GitHub issues + Discourse scraper
- **GitHub Actions CI**:
  - `test.yaml` — Python 3.11 / 3.12 / 3.13 test matrix
  - `release.yaml` — PyPI publish on version tag (trusted publishing)
  - `refresh_knowledge.yaml` — monthly re-scrape of external knowledge
  - `sync_tutorials.yaml` — monthly tutorial sync from scvi-tools repo
  - `sync_model_knowledge.yaml` — monthly model docs sync via CHANGELOG diff
- stdio transport via FastMCP 3.x; no runtime scvi-tools dependency
- `scvi-tools` optional install extra: `pip install scvi-tools-mcp[scvi]`
