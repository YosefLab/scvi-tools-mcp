# DESTVI — User Guide

**Class:** `scvi.external.DestVI`

## Overview

**DestVI** (Deconvolution of Spatial Transcriptomics profiles using Variational Inference) posits a conditional generative model of spatial transcriptomics down to the sub-cell-type variation level.

**Advantages:**

- Stratifies cells into discrete cell types and models continuous sub-cell-type variation
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU

**Tutorial:** `tutorials/notebooks/spatial/DestVI_tutorial`

## Preliminaries

DestVI requires training two models:

1. **scLVM** (single-cell latent variable model): input is scRNA-seq matrix $X$ ($N$ cells × $G$ genes) + cell type labels $\vec{c}$
2. **stLVM** (spatial transcriptomic latent variable model): input is trained scLVM + spatial matrix $Y$ ($S$ spots × $G$ genes)

## Generative Process

### scLVM

For cell $n$ with discrete label $c_n$ and continuous covariate $\gamma_n \in \mathbb{R}^d$:

- $\gamma_n \sim \mathcal{N}(0, I)$
- $x_{ng} \sim \text{NegativeBinomial}(l_n f^g(c_n, \gamma_n), p_g)$

Uses rate-shape NB parametrization (not mean-dispersion). $f$ is a two-layer neural network.

### stLVM

For spot $s$ with cell type abundances $\beta_{sc}$:

- $\gamma_s^c \sim \sum_{k=1}^K m_{kc} q_\Phi(\gamma^c | u_{kc}, c)$ — VampPrior from scLVM clusters
- $x_{sg} \sim \text{NegativeBinomial}(l_s \alpha_g \sum_c \beta_{sc} f^g(c, \gamma_s^c), p_g)$

$\alpha_g$ is a correction term for assay differences. Optional L1 regularization on $\beta_{sc}$ increases sparsity.

**Loss hyperparameters:**

- `l1_reg` ($\lambda_\beta$): sparsity of cell type proportions
- `beta_reg` ($\lambda_\alpha$): regularization on assay correction
- `eta_reg` ($\lambda_\eta$): regularization on noise gene expression (do not change default)

## Tasks

### Cell type deconvolution

```python
proportions = st_model.get_proportions()
st_adata.obsm["proportions"] = proportions

import scanpy as sc

st_adata.obs["B cells"] = st_adata.obsm["proportions"]["B cells"]
sc.pl.spatial(st_adata, color="B cells", spot_size=130)
```

### Intra cell type variation

```python
gamma = st_model.get_gamma()["B cells"]
st_adata.obsm["B_cells_gamma"] = gamma
```

### Cell-type-specific gene expression imputation

```python
indices = np.where(st_adata.obsm["proportions"][ct_name].values > 0.03)[0]
imputed_counts = st_model.get_scale_for_ct("Monocyte", indices=indices)[
    ["Cxcl9", "Cxcl10", "Fcgr1"]
]
```

## References

- Lopez et al. (2022), *DestVI identifies continuums of cell types in spatial transcriptomics data*, Nature Biotechnology.
- Tomczak, Welling (2018), *VAE with a VampPrior*, PMLR.
