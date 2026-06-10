# SCAR — User Guide

**Class:** `scvi.external.SCAR`

## Overview

**scAR** (single-cell Ambient Remover) is a deep learning model for removal of ambient signals in droplet-based single-cell omics. Ported from [Novartis/scar](https://github.com/Novartis/scar).

**Tutorials:** Work in progress.

## Ambient RNA Removal

```python
import anndata
import scvi.external

adata = anndata.read_h5ad(path_to_anndata)
raw_adata = anndata.read_h5ad(path_to_raw_anndata)
scvi.external.SCAR.setup_anndata(adata, batch_key="batch")
scvi.external.SCAR.get_ambient_profile(adata=adata, raw_adata=raw_adata, prob=0.995)
vae = scvi.external.SCAR(adata, ambient_profile="ambient_profile")
vae.train()
adata.obsm["X_scAR"] = vae.get_latent_representation()
adata.layers["denoised"] = vae.get_denoised_counts()
```

## Estimating the Ambient Profile

### Option 1: `get_ambient_profile` method (inspired by EmptyDrops)

1. Calculates initial ambient profile from average of all droplets in `raw_adata`
2. Tests if droplets fit a multinomial distribution (high probability = cell-free)
3. Recalculates ambient profile from identified cell-free droplets
4. Iterates steps 2–3
5. Saves final ambient profile in `adata.varm`

```python
scvi.external.SCAR.get_ambient_profile(adata=adata, raw_adata=raw_adata, prob=0.995)
```

### Option 2: Kneeplot-based estimation

Uses total counts to identify cell-free droplet subpopulations via a kneeplot, then computes the ambient profile from those droplets.

## References

- Sheng et al. (2022), *Probabilistic machine learning ensures accurate ambient denoising in droplet-based single-cell omics*, bioRxiv.
- Lun et al. (2019), *EmptyDrops: distinguishing cells from empty droplets in droplet-based single-cell RNA sequencing data*, Genome Biology.
