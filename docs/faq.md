# Frequently asked questions

Don't see what you're looking for here? Check the
[Discourse](https://discourse.scverse.org/c/help/scvi-tools/) or use `search_knowledge` in the MCP server.

## Why doesn't the MCP server run my model?

By design — this is a **knowledge-only** server. It returns documentation, code templates, and
guidance. To actually train a model, install scvi-tools and run the code that the server provides.

## How do I keep the knowledge base up to date?

GitHub Actions jobs handle this automatically and open PRs when diffs are found:

- `refresh_knowledge.yaml` — re-scrapes GitHub issues + Discourse
- `sync_tutorials.yaml` — syncs tutorial notebooks from scvi-tools
- `sync_model_knowledge.yaml` — updates model docs from the scvi-tools CHANGELOG
- `sync_huggingface_hub.yaml` — refreshes the Hugging Face Hub model registry quarterly
- `sync_scviva_tools_knowledge.yaml` / `sync_scviva_tools_tutorials.yaml` — syncs scviva-tools docs + tutorials
- `sync_scib_metrics_knowledge.yaml` / `sync_scib_metrics_tutorials.yaml` — syncs scib-metrics docs + tutorials

You can also trigger them manually via `workflow_dispatch` or run the scripts locally:

```bash
python scripts/scrape_external.py
python scripts/convert_notebooks.py --src /path/to/scvi-tutorials --dst src/scvi_tools_mcp/knowledge/tutorials
python scripts/extract_api_docs.py
python scripts/scrape_huggingface_hub.py
python scripts/extract_scviva_api_docs.py --docs-dir /path/to/scviva-tools/docs/user_guide
python scripts/extract_scib_metrics_api_docs.py
```

## Which models are covered?

Run `get_model_overview` or `list_tutorials` in the MCP server. The knowledge base currently covers
scVI, scANVI, TotalVI, MultiVI, PeakVI, LinearSCVI, MrVI, Stereoscope, CellAssign, SOLO, GIMVI,
veloVI, ContrastiveVI, SCBASSET, SysVI, DiagVI, and more.

For pretrained model repos on the official scvi-tools Hugging Face organization, use
`list_hub_models`, `get_hub_model`, or `suggest_hub_models`.

The companion spatial toolkit scviva-tools (ResolVI, DestVI, scVIVA, GIMVI, DiagVI, Stereoscope,
Tangram, Harreman) is covered via `list_scviva_models` and `get_scviva_model`. Integration-benchmarking
metrics from scib-metrics are covered via `list_scib_metrics` and `get_scib_metric`.

## What is the `uvx` command?

`uvx` runs a package from PyPI without installing it permanently — provided by
[uv](https://github.com/astral-sh/uv). It is the recommended way to run MCP servers because it
always fetches the latest published version.

## Can I use this server from R?

Yes — any MCP-compatible client works. Configure your client to run `uvx scvi-tools-mcp` and use
the tools from whatever language your client supports. The server itself is language-agnostic.
