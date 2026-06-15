# scvi-tools-mcp

An MCP (Model Context Protocol) server that gives LLMs structured access to [scvi-tools](https://scvi-tools.org)
knowledge: model documentation, tutorials, API reference, workflow templates, pretrained Hugging Face Hub models,
and community FAQ.

No runtime model execution — pure knowledge layer. Works with Claude Desktop, Cursor, and any MCP-compatible client.

______________________________________________________________________

## Quick Start

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cursor / other clients

```json
{ "command": "uvx", "args": ["scvi-tools-mcp"] }
```

### Local install

```bash
pip install scvi-tools-mcp
scvi-tools-mcp
```

______________________________________________________________________

## Tools

| Tool                         | Description                                            |
| ---------------------------- | ------------------------------------------------------ |
| `recommend_model`            | Rank models by task and data type — start here         |
| `get_model_overview`         | Full model description, use cases, inputs, outputs     |
| `get_model_parameters`       | Key `__init__` and `train()` parameters with defaults  |
| `get_setup_anndata_guide`    | Exact `setup_anndata()` call + required obs/var fields |
| `validate_data_requirements` | Pass/fail checklist for your AnnData against a model   |
| `list_tutorials`             | Browse tutorials by category                           |
| `get_tutorial`               | Paginated tutorial content (code + prose, no outputs)  |
| `search_tutorials`           | Keyword search across all tutorials                    |
| `get_api_reference`          | Signature + docstring for any public class or function |
| `search_api`                 | Search public symbols by keyword                       |
| `get_workflow_template`      | Step-by-step code template for an analysis task        |
| `get_downstream_guide`       | Guide for DE, clustering, embedding, label transfer    |
| `list_hub_models`            | Browse official scvi-tools Hugging Face Hub models     |
| `get_hub_model`              | Inspect one pretrained HubModel repo                   |
| `suggest_hub_models`         | Suggest Hub models for reference/query workflows       |
| `get_faq`                    | Curated FAQ from docs, GitHub issues, and Discourse    |
| `search_knowledge`           | Cross-search all knowledge (catch-all)                 |

______________________________________________________________________

## Knowledge Sources

All knowledge is baked into the package as Markdown files at build time. No network calls at tool-call time.

| Directory                            | Content                                                   |
| ------------------------------------ | --------------------------------------------------------- |
| `knowledge/models/`                  | One `.md` per model — description, use case, parameters   |
| `knowledge/tutorials/`               | 60+ tutorials converted from `.ipynb` (code + prose only) |
| `knowledge/api/`                     | Extracted class signatures and docstrings                 |
| `knowledge/hub/models.json`          | Normalized Hugging Face Hub model registry snapshot       |
| `knowledge/hub/summary.md`           | Searchable summary of Hub model classes and modalities    |
| `knowledge/user_guide/`              | Narrative documentation from the scvi-tools user guide    |
| `knowledge/faq/github_issues.md`     | Top GitHub issues snapshot                                |
| `knowledge/faq/discourse_threads.md` | Discourse forum thread snapshot                           |

______________________________________________________________________

## Knowledge Refresh (CI)

Automated GitHub Actions jobs keep knowledge current — each opens a PR if a diff is found:

| Workflow                    | Schedule     | What it does                                                |
| --------------------------- | ------------ | ----------------------------------------------------------- |
| `refresh_knowledge.yaml`    | 1st of month | Re-scrapes GitHub issues + Discourse threads                |
| `sync_tutorials.yaml`       | 1st of month | Fetches new `.ipynb` from scvi-tools, converts to `.md`     |
| `sync_model_knowledge.yaml` | 1st of month | Checks CHANGELOG, regenerates model docs for changed models |
| `sync_huggingface_hub.yaml` | Quarterly    | Refreshes the scvi-tools Hugging Face Hub model registry    |

All workflows also support `workflow_dispatch` for manual runs.

______________________________________________________________________

## Development

```bash
git clone https://github.com/ori-kron-wis/scvi-tools-mcp
cd scvi-tools-mcp
pip install -e ".[dev]"
pytest
```

### Rebuild knowledge manually

```bash
# Convert tutorials from a local scvi-tools checkout
python scripts/convert_notebooks.py /path/to/scvi-tools/docs/tutorials/notebooks \
    src/scvi_tools_mcp/knowledge/tutorials

# Extract API docs (requires scvi-tools installed)
pip install -e ".[scvi]"
python scripts/extract_api_docs.py

# Re-scrape external knowledge
python scripts/scrape_external.py

# Refresh Hugging Face Hub model registry snapshot
python scripts/scrape_huggingface_hub.py
```

### Adding a new model

1. Run `scripts/extract_api_docs.py` after updating scvi-tools.
1. Add the model name to `MODEL_NAMES` in `src/scvi_tools_mcp/tools/_constants.py`.
1. Add requirements to `MODEL_REQUIREMENTS` in `_data_prep.py` if needed.

______________________________________________________________________

## License

MIT
