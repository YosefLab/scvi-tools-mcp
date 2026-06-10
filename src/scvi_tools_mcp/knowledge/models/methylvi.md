# METHYLVI — User Guide

**Class:** `scvi.external.METHYLVI`

## Overview

**MethylVI** is a generative model of single-cell bisulfite sequencing (scBS-seq) data.

**Advantages:**

- Comprehensive in capabilities
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU
- Latent space not interpretable like a linear method

**Tutorial:** `tutorials/notebooks/scbs/MethylVI_batch`

## Preliminaries

**Input:** scBS-seq count matrices aggregated over genomic regions of interest (gene bodies, regulatory regions).

For each methylation context $C$ (e.g., CpG, non-CpG), two matrices:

- $Y^C_{mc}$: $N$ cells × $M$ regions — number of **methylated** cytosines
- $Y^C_{cov}$: $N$ cells × $M$ regions — **total** cytosines profiled

Optional: categorical covariates $S$ (batch, donor, etc.).

## Generative Process

Observed methylated cytosines $y^C_{ij}$ in context $C$, cell $i$, region $j$:

- $z_i \sim \mathcal{N}(0, I_d)$ — cell state
- $\mu^C_{ij} = f_{\theta^C}(z_i, s_i)_j$ — per-region methylation level
- $y^C_{ij} \sim \text{BetaBinomial}(n^C_{ij}, \mu^C_{ij}, \gamma^C_j)$

For each context $C$, one neural network: $f_{\theta^C}: \mathbb{R}^d \times \{0,1\}^K \to (0,1)^M$

**Latent variables:**

- $z_i \in \mathbb{R}^d$ — cell state (`z`)
- $\mu_i \in (0,1)^M$ — per-region methylation estimates (`mu`)
- $\gamma_i \in (0,1)$ — region-wise dispersion (`d`)

## Inference

Amortized variational Bayes with mean-field Gaussian approximate posterior $q_\phi(z_i | y_i, n_i, s_i)$.

## Tasks

### Dimensionality reduction

```python
adata.obsm["X_methylvi"] = model.get_latent_representation()
import scanpy as sc

sc.pp.neighbors(adata, use_rep="X_methylvi")
```

### Transfer learning

```python
model_query = scvi.external.METHYLVI.load_query_data(adata_query, reference_model=model)
```

### Estimation of methylation levels

```python
# Returns E[f_theta(z_i, s_i)] under approximate posterior
# By default uses z_i mean as point estimate; set use_z_mean=False for sampling
normalized = model.get_normalized_methylation()
```

### Differential methylation

```python
diff = model.differential_methylation(
    groupby="cell_type", group1="TypeA", group2="TypeB"
)
```

## References

- Weinberger, Lee (2021), *A deep generative model of single-cell methylomic data*, OpenReview.
