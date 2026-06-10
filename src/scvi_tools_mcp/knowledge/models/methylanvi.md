# METHYLANVI — User Guide

**Class:** `scvi.external.METHYLANVI`

## Overview

**MethylANVI** is a semi-supervised generative model of scBS-seq data. Extends MethylVI similarly to how scANVI extends scVI — uses partial cell type annotations to infer labels for unlabeled cells.

**Advantages:**

- Comprehensive in capabilities
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU
- Latent space not interpretable like a linear method
- May not scale to very large number of cell types

**Tutorials:** Work in progress.

## Preliminaries

Same input as MethylVI (two matrices per methylation context: methylated counts + total counts) plus:

- Partially observed cell type labels $\mathbf{l}$ ($L$ total cell types)
- Optional categorical covariates $S$

## Generative Process

- $l_i \sim \text{Categorical}(1/L, \ldots, 1/L)$ — cell type label
- $u_i \sim \mathcal{N}(0, I_d)$ — within-cell-type variation
- $z_i \sim \mathcal{N}(f_z^\mu(u_i, l_i), f_z^\sigma(u_i, l_i))$ — cell-type-aware latent state
- $\mu^C_{ij} = f_{\theta^C}(z_i, s_i)_j$
- $y^C_{ij} \sim \text{BetaBinomial}(n^C_{ij}, \mu^C_{ij}, \gamma^C_j)$

**Additional latent variables (vs. MethylVI):**

- $l_i \in \Delta^{L-1}$ — cell type label (`y`)
- $z_i \in \mathbb{R}^d$ — latent cell state (`z_1`)
- $u_i \in \mathbb{R}^d$ — cell-type specific state (`z_2`)

## Inference

Factorized variational posterior:

$$q_\phi(z_i, u_i, c_i | y_i, n_i, s_i) = q_\phi(z_i|y_i,n_i,s_i) \cdot q_\phi(c_i|z_i) \cdot q_\phi(u_i|c_i, z_i)$$

$q_\phi(c_i|z_i)$ is Categorical and can be used post-training for cell type prediction.

Optimizes two ELBOs: one for labeled cells, one for unlabeled (similar to scANVI).

## Tasks

MethylANVI supports all MethylVI tasks plus:

### Cell type label prediction

```python
mdata.obs["methylanvi_prediction"] = model.predict()
```

## References

- Weinberger, Lee (2021), *A deep generative model of single-cell methylomic data*, OpenReview.
