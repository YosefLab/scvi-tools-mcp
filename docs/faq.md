# Frequently asked questions

Don't see what you're looking for here? Check the
[Discourse](https://discourse.scverse.org/c/help/scvi-tools/) or use `search_knowledge` in the MCP server.

## Why doesn't the MCP server run my model?

By design — this is a **knowledge-only** server. It returns documentation, code templates, and
guidance. To actually train a model, install scvi-tools and run the code that the server provides.

## How do I keep the knowledge base up to date?

Three monthly GitHub Actions jobs handle this automatically and open PRs when diffs are found:

- `refresh_knowledge.yaml` — re-scrapes GitHub issues + Discourse
- `sync_tutorials.yaml` — syncs tutorial notebooks from scvi-tools
- `sync_model_knowledge.yaml` — updates model docs from the scvi-tools CHANGELOG

You can also trigger them manually via `workflow_dispatch` or run the scripts locally:

```bash
python scripts/scrape_external.py
python scripts/convert_notebooks.py --src /path/to/scvi-tutorials --dst src/scvi_tools_mcp/knowledge/tutorials
python scripts/extract_api_docs.py
```

## Which models are covered?

Run `get_model_overview` or `list_tutorials` in the MCP server. The knowledge base currently covers
scVI, scANVI, TotalVI, MultiVI, PeakVI, LinearSCVI, MrVI, Stereoscope, CellAssign, SOLO, GIMVI,
veloVI, ContrastiveVI, SCBASSET, SysVI, DiagVI, and more.

## What is the `uvx` command?

`uvx` runs a package from PyPI without installing it permanently — provided by
[uv](https://github.com/astral-sh/uv). It is the recommended way to run MCP servers because it
always fetches the latest published version.

## Can I use this server from R?

Yes — any MCP-compatible client works. Configure your client to run `uvx scvi-tools-mcp` and use
the tools from whatever language your client supports. The server itself is language-agnostic.
