<!-- Source: https://github.com/YosefLab/scviva-tools-website/blob/HEAD/blog/2026-7-8-scviva-tools.md -->

---
slug: scviva-tools
title: Introducing scVIVA-Tools
date: 2026-07-08
author: Ori Kronfeld
tags: [scviva-tools, spatial, release]
---

## Introduction

Alongside `scvi-tools` v1.5.0, we're shipping **scVIVA-Tools**, which consolidates spatial
transcriptomics models into a single toolkit.

<!--truncate-->

## scVIVA-Tools: a unified toolkit for spatial transcriptomics

If you've ever had to juggle different APIs, installation instructions, and tutorial conventions
for deconvolution, denoising, and niche analysis, scVIVA-Tools is meant to remove that friction.

scVIVA-Tools bundles:

- **[scVIVA](https://scviva-tools.readthedocs.io/page/user_guide/models/scviva.html)** — a
  niche-aware VAE that jointly models a cell's own expression and its microenvironment,
  disentangling cell-intrinsic from environment-driven variation.
- **[ResolVI](https://scviva-tools.readthedocs.io/page/user_guide/models/resolvi.html)** —
  corrects segmentation errors, background contamination, and cell-size bias in
  cellular-resolution data (Xenium, MERFISH, CosMx).
- **[DestVI](https://scviva-tools.readthedocs.io/page/user_guide/models/destvi.html)** —
  multi-resolution deconvolution of spot-based data (e.g., Visium) into continuous cell-type
  compositions.
- **[DiagVI](https://scviva-tools.readthedocs.io/page/user_guide/models/diagvi.html)** —
  diagonal integration of unpaired multi-modal single-cell data.
- **[gimVI](https://scviva-tools.readthedocs.io/page/user_guide/models/gimvi.html)** — joint
  imputation of missing genes between scRNA-seq and spatial datasets.
- **[Stereoscope](https://scviva-tools.readthedocs.io/page/user_guide/models/stereoscope.html)** —
  a two-stage generative model for spot deconvolution.
- **[Tangram](https://scviva-tools.readthedocs.io/page/user_guide/models/tangram.html)** — maps
  single cells onto spatial coordinates via optimal transport-style alignment.
- **[Harreman](https://scviva-tools.readthedocs.io/page/user_guide/models/harreman.html)** —
  infers spatially-resolved metabolic gene programs and cell-cell metabolic/ligand-receptor
  communication using local autocorrelation and spatial proximity graphs.

### Why a unified package?

Each of these models started life with its own API, its own docs, and its own release cadence —
great for iterating quickly, but hard for users trying to build an end-to-end spatial analysis
pipeline. scVIVA-Tools gives them a single `pip install`, one consistent `scviva` namespace and
AnnData-first API, a shared user guide, API reference, and worked tutorials for every model, plus
shared infrastructure for GPU acceleration (via optional `rapids` extras) and
`SpatialData`/`squidpy` interop.

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

Swapping in scVIVA for niche-aware differential expression, or DestVI for Visium deconvolution,
follows the same pattern — setup, train, extract. See the
[scVIVA-Tools documentation](https://scviva-tools.readthedocs.io/page/index.html) for the full API
reference and tutorials for each model.

## Try it out

Please try scVIVA-Tools out, open issues, and let us know what you'd like to see next on
[GitHub](https://github.com/YosefLab/scviva-tools).
