# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
