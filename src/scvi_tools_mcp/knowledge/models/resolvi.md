# RESOLVI — User Guide

**Class:** `scvi.external.RESOLVI`

## Overview

**ResolVI** is a generative model of single-cell resolved spatial transcriptomics. Addresses noise and bias from wrong segmentation, unspecific background, and limited spatial resolution.

**Advantages:**

- Addresses segmentation errors, unspecific background, and limited spatial resolution in ST data
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU
- Latent space not interpretable like a linear method
- Only works with single-cell resolved ST (not low-resolution like Visium or Slide-Seq)

**Tutorial:** `tutorials/notebooks/spatial/resolVI_tutorial`

## Preliminaries

**Input:**

- Spatially resolved RNA-seq count matrices (from sequencing-based or fluorescent imaging ST)
- Spatial neighbors and their gene expression
- Distances between cells
- Optional: categorical covariates $S$ (batch, donor)
- Optional (semi-supervised): cell type annotations for structured prior

## Generative Process

Observed expression $x_{ng}$ for cell $n$, gene $g$ decomposes into three components:

- $\alpha_0$: truly expressed by the cell
- $\alpha_1$: expression from neighboring cells wrongly assigned to $n$
- $\alpha_2$: unspecific background

$$z \sim \text{MixtureOfGaussians}(\mu_1, \ldots, \mu_K, \Sigma_1, \ldots, \Sigma_K)$$
$$\alpha_n \sim \text{Dirichlet}(C)$$
$$r_{ng} \sim \text{Exponential}(R)$$
$$h_{ng} = \text{Gamma}(r_{ng}, \frac{r_{ng}}{\alpha_0 f_\theta(z,b) + \alpha_1 \sum_{N(n)} \beta_{N(n)} f_\theta(z_{N(n)},b)}) + \alpha_2 bg$$
$$x_{ng} \sim \text{Poisson}(l_n h_{ng})$$

Mixture of Gaussians prior on $z$:

- $c_n \sim \text{Categorical}(\pi_1, \ldots, \pi_K)$
- $z_n | c_n = c \sim \mathcal{N}(\mu_c, \sigma_c)$

**Latent variables:**

- $z_n \in \mathbb{R}^L$ — cell state (`latent`), MoG prior
- $\beta_{N(n)} \in \Delta^{N(n)-1}$ — per-neighbor diffusion (`per_neighbor_diffusion`), Dirichlet prior
- $\alpha_{n0\ldots2} \in \Delta^2$ — per-cell proportions of true/diffusion/background (`mixture_proportions`), Dirichlet prior
- $bg_{ng} \in \Delta^{G-1}$ — per-cell background estimate (`background`)
- $\rho_n \in \Delta^{G-1}$ — per-cell rate of expression (`px_scale`)

## Inference

Amortized variational Bayes in Pyro. Neural network amortizes $z_n$ and $\alpha_n$; $\beta_{N(n)n}$ estimated per cell.

## Tasks

### Dimensionality reduction

```python
adata.obsm["X_resolvi"] = model.get_latent_representation()
import scanpy as sc

sc.pp.neighbors(adata, use_rep="X_resolvi")
```

### Transfer learning

```python
# beta_{N(n)n} extended to new cells, encoder can predict z_n without retraining
model_query = scvi.external.RESOLVI.load_query_data(adata_query, reference_model=model)
```

### Estimation of true expression levels

```python
# Returns E[f_theta(z_n, s_n)] under approximate posterior
true_expr = model.get_normalized_expression()
```

### Differential expression

```python
de_results = model.differential_expression(groupby="cell_type", group1="TypeA")
```

### Cell-type prediction (semi-supervised only)

```python
cell_types = model.predict()
```

### Differential niche abundance (semi-supervised only)

```python
niche_abundance = model.differential_niche_abundance(groupby="condition")
```

## References

- Ergen, Yosef (2025), *ResolVI - addressing noise and bias in spatial transcriptomics*, bioRxiv.
