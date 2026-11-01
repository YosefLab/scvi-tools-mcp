<!-- Source: https://github.com/YosefLab/scviva-tools-website/blob/HEAD/src/pages/get_started.md -->

---
title: Get Started
description: Install scVIVA-Tools and run your first spatial transcriptomics model.
---

# Get Started

`scVIVA-Tools` is a consolidated spatial transcriptomics analysis toolkit built on top of
[scvi-tools](https://scvi-tools.org), exposing scVIVA, ResolVI, DestVI, DiagVI, Harreman, gimVI,
Stereoscope, and Tangram through one AnnData-first API.

## Installation

```bash
pip install scviva-tools
```

Optional extras:

```bash
pip install "scviva-tools[spatial]"    # SpatialData + squidpy integration
pip install "scviva-tools[rapids]"     # GPU-accelerated neighbor graphs (cuML/cuPy/cuGraph)
pip install "scviva-tools[tutorials]"  # jupyter, matplotlib, seaborn
pip install "scviva-tools[all]"        # everything above
```

## Quick Start

```python
import scviva

# ResolVI: denoising and segmentation-error correction
scviva.ResolVI.setup_anndata(adata, layer="counts")
model = scviva.ResolVI(adata)
model.train()

adata.obsm["X_resolvi"] = model.get_latent_representation()
```

Swapping in `scviva.SCVIVA` for niche-aware differential expression, or `scviva.DestVI` for Visium
deconvolution, follows the same setup → train → extract pattern.

## Resources

- Tutorials, user guide, and API reference are available in the
  [full documentation](https://scviva-tools.readthedocs.io/page/index.html).
- To report bugs or request features, open an issue on
  [GitHub](https://github.com/YosefLab/scviva-tools/issues).
- For usage questions, see [GitHub Discussions](https://github.com/YosefLab/scviva-tools/discussions).
