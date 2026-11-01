<!-- Source: https://github.com/scverse/scvi-tools-site/blob/HEAD/blog/2026-7-8-scviva-tools.md -->

---
slug: scviva-tools
title:      Introducing scVIVA-Tools & scVI-Tools MCP
date:       2026-07-08
author:     Ori Kronfeld
tags: [scviva-tools, scvi-tools-mcp, spatial, mcp, release]
---
import useBaseUrl from '@docusaurus/useBaseUrl';

## Introduction

Alongside `scvi-tools` v1.5.0, we're shipping two new packages that round out the ecosystem in very different
directions: **scVIVA-Tools**, which consolidates seven spatial transcriptomics models into a single toolkit, and
**scVI-Tools MCP**, which puts scvi-tools knowledge directly in reach of LLM coding assistants like Claude.

<!--truncate-->

## scVIVA-Tools: a unified toolkit for spatial transcriptomics

If you've ever had to juggle different APIs, installation instructions, and tutorial conventions for
deconvolution, denoising, and niche analysis, scVIVA-Tools is meant to remove that friction.

Version 0.1.6, released alongside `scvi-tools` v1.5.0, bundles:

- **[scVIVA](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/scviva.html)** — a niche-aware VAE
  that jointly models a cell's own expression and its microenvironment, disentangling cell-intrinsic from
  environment-driven variation.
- **[ResolVI](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/resolvi.html)** — corrects
  segmentation errors, background contamination, and cell-size bias in cellular-resolution data (Xenium, MERFISH,
  CosMx).
- **[DestVI](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/destvi.html)** — multi-resolution
  deconvolution of spot-based data (e.g., Visium) into continuous cell-type compositions.
- **[GimVI](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/gimvi.html)** — joint imputation of
  missing genes between scRNA-seq and spatial datasets.
- **[Stereoscope](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/stereoscope.html)** — a
  two-stage generative model for spot deconvolution.
- **[Tangram](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/tangram.html)** — maps single cells
  onto spatial coordinates via optimal transport-style alignment.
- **[Harreman](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/harreman.html)** — new in v0.1.5,
  infers spatially-resolved metabolic gene programs and cell-cell metabolic / ligand-receptor communication using
  local autocorrelation and spatial proximity graphs.

### Why a unified package?

Each of these models started life with its own API, its own docs, and its own release cadence — great for
iterating quickly, but hard for users trying to build an end-to-end spatial analysis pipeline. scVIVA-Tools gives
them:

- a single `pip install`,
- one consistent `scviva` namespace and AnnData-first API,
- a shared user guide, API reference, and 11 worked tutorials (one or more per model, plus preprocessing),
- shared infrastructure for GPU acceleration (via optional `rapids` extras) and `SpatialData`/`squidpy` interop.

### Getting started

```bash
pip install scviva-tools
# or, with spatial I/O and GPU acceleration
pip install "scviva-tools[spatial,rapids]"
```

```python
import scviva
import scanpy as sc

adata = sc.read_h5ad("my_xenium_data.h5ad")
scviva.model.ResolVI.setup_anndata(adata, layer="counts")
model = scviva.model.ResolVI(adata)
model.train()

adata.obsm["X_resolvi"] = model.get_latent_representation()
```

Swapping in scVIVA for niche-aware differential expression, or DestVI for Visium deconvolution, follows the same
pattern — setup, train, extract. See the [scVIVA-Tools documentation](https://scviva-tools.readthedocs.io/en/latest/)
for the full API reference and tutorials for each model.

### What's next for scVIVA-Tools

scVIVA-Tools is under active development. Already in progress:

- **[DiagVI](https://scviva-tools.readthedocs.io/en/latest/user_guide/models/diagvi.html)** — a cross-modality model bridging spatial transcriptomics and spatial proteomics.
- **[AMICI](https://github.com/azizilab/amici)** — cell-cell interaction modeling.
- **[VIVS](https://github.com/YosefLab/VIVS)** — spatial variable selection.
- **NOLAN** — niche detection: identifies and characterizes recurring cellular neighborhoods (niches) directly
  from spatial coordinates and expression, complementing scVIVA's niche-conditioned representation learning.
- **[Starfysh](https://github.com/azizilab/starfysh)** — histology-based deconvolution.
- **SPARL** — a vision-transformer-based foundation model for spatial proteomics imaging data, part of a broader
  push toward foundation models for spatial omics.
- **[CSDE](https://github.com/YosefLab/CSDE)** (Corrected Spatial Differential Expression) — corrects for
  systematic errors like cell mis-segmentation and mislabeling in spatial transcriptomics before they propagate
  into false discoveries, by combining large automated annotations with a small manually-validated subset via
  prediction-powered inference (PPI) to recover unbiased estimates with valid confidence intervals.

Looking further out, expect standardized spatial benchmarking metrics (via [scIB-metrics](/ecosystem)) and
pre-trained reference models on public Xenium and Visium HD atlases.

## scVI-Tools MCP: scvi-tools knowledge for LLMs

The second release is a different kind of tool entirely: **[scVI-Tools MCP](https://scvi-tools-mcp.readthedocs.io/en/latest/index.html)**,
a [Model Context Protocol](https://modelcontextprotocol.io/) server that gives LLM coding assistants — Claude
Code, Claude Desktop, Cursor, Windsurf, OpenAI Codex CLI, or any other MCP-compatible client — structured,
up-to-date access to scvi-tools knowledge: model documentation, tutorials, API reference, workflow templates,
pretrained Hugging Face Hub models, and community FAQ.

It's a pure knowledge layer — no runtime model execution — so it's safe to point at any assistant you already use
for coding. Under the hood it exposes 17 tools, from `recommend_model` (rank models by task and data type) and
`get_setup_anndata_guide` (the exact `setup_anndata()` call for your data) to `search_tutorials`, `get_hub_model`,
and a catch-all `search_knowledge`. All of it is baked into the package at build time, and refreshed monthly by CI
against the live scvi-tools changelog, tutorials, GitHub issues, Discourse threads, and Hugging Face Hub registry —
so recommendations stay current with new models like the ones described above.

### Installation

```bash
pip install scvi-tools-mcp
```

Or skip the install entirely and let `uvx` fetch it on demand — this is what all the client configs below use.

### Connecting to your LLM client

**Claude Code (CLI)**

```bash
claude mcp add scvi-tools-mcp -s user -- uvx scvi-tools-mcp
```

**Claude Desktop** — add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scvi-tools-mcp": {
      "command": "uvx",
      "args": ["scvi-tools-mcp"]
    }
  }
}
```

**OpenAI Codex CLI** — add to `~/.codex/config.toml`:

```toml
[mcp_servers.scvi-tools-mcp]
command = "uvx"
args   = ["scvi-tools-mcp"]
```

**Cursor / Windsurf / other MCP-compatible clients**

```json
{ "command": "uvx", "args": ["scvi-tools-mcp"] }
```

Once connected, ask your assistant something like "which scvi-tools model should I use for CITE-seq data with a
reference atlas?" — it'll call `recommend_model` and walk you through setup, rather than guessing from a stale
training cutoff. See the [scVI-Tools MCP documentation](https://scvi-tools-mcp.readthedocs.io/en/latest/index.html)
for the full tool list and the [repository](https://github.com/YosefLab/scvi-tools-mcp) for source and issues —
and for a broader tour of LLM-assisted scvi-tools workflows (including the Claude skill bundle, ChatGPT, and
other engines), see the [user guide](https://docs.scvi-tools.org/en/stable/user_guide/use_case/llm_assisted_analysis.html).

## Try it out

The goal for both releases is the same: reduce the friction between having an idea and running the analysis,
whether that friction is API fragmentation across spatial models or an LLM assistant guessing at how to call
scvi-tools correctly. Please try them out, open issues, and let us know what you'd like to see next on
[GitHub](https://github.com/YosefLab/scviva-tools) or [Discourse](https://discourse.scvi-tools.org/).
