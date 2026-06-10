# SCVIVA — User Guide

**Class:** `scvi.external.SCVIVA`

## Overview

**scVIVA** is a generative model of single-cell resolved spatial transcriptomics that captures both gene expression heterogeneity and spatial variation from the micro-environment in a joint latent representation.

**Advantages:**

- Probabilistic low-dimensional representation corrected for batch effects capturing gene expression profile and spatial environment
- Enables differential expression analysis across niches while accounting for wrong molecule assignments
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU
- Latent space not interpretable
- Only works with single-cell resolved ST (not Visium or Slide-Seq)

**Tutorial:** `tutorials/notebooks/spatial/scVIVA_tutorial`

## Preliminaries

**Input per cell $n$:**

- Gene expression matrix $X$ ($N$ cells × $G$ genes)
- Spatial coordinates $y_n$
- Cell type assignment $c_n \in \{1, \ldots, T\}$
- Batch assignment $s_n$

**Preprocessing:** $K$ nearest neighbors in physical space define the niche. Characterized by:

- $\alpha_n$: $T$-dimensional cell type proportions among $K$ neighbors
- $\eta_n \in \mathbb{R}^{T \times D}$: average gene expression embeddings per cell type in niche

## Descriptive Model

Mixture of Gaussians prior:
$$z_n \sim \text{MixtureOfGaussians}(\mu_1, \ldots, \mu_M; \Sigma_1, \ldots, \Sigma_M; \pi_1, \ldots, \pi_M)$$

**Gene expression:**
$$\rho_n = f_w(z_n, s_n), \quad x_{ng} \sim \text{NegativeBinomial}(l_n \rho_n, \theta_g)$$

**Neighbor cell type proportions:**
$$\alpha_n \sim \text{Dirichlet}(f_\omega(z_n))$$

**Neighboring expression profiles:**
$$\eta_{nt} \sim \mathcal{N}(f_\nu^t(z_n))$$ if $\\alpha_t > 0$, else $0$

## Tasks

### Dimensionality reduction

```python
adata.obsm["X_scVIVA"] = model.get_latent_representation()
```

### Estimation of normalized expression

```python
expr = model.get_normalized_expression()
```

### Niche-aware differential expression

Uses lvm-DE adapted for spatial data. For two cell groups $C1$ and $C2$ in different spatial contexts:

```python
de_results = model.differential_expression(
    groupby="cell_type",
    group1="TypeA",
    group2="TypeB",
    niche_mode="true",  # accounts for neighborhood contamination
)
```

**Algorithm:** Computes DE between {C1, C2}, {N1, C2}, {C1, N1}, then scores genes by local marker probability $p(g \in S_1 | \text{LFCs})$ using a Gaussian process classifier. Filters spurious DE caused by neighborhood contamination.

## References

- See scvi-tools documentation for `scvi.external.SCVIVA`.
