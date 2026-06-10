# AMORTIZED LDA — User Guide

**Class:** `scvi.model.AmortizedLDA`

## Overview

**LDA** (Latent Dirichlet Allocation) posits a generative model where a set of latent topics generates collections of elements. In scRNA-seq, topics correspond to gene modules and each cell is a collection of UMI counts. This implementation amortizes the cost of variational inference for each cell by training a common encoder.

**Advantages:**

- Can learn underlying topics without a reference
- Scalable to very large datasets (>1 million cells)

**Limitations:**

- Optimal number of topics is unclear
- Amortization gap in optimizing variational parameters

**Tutorials:** `tutorials/notebooks/scrna/amortized_lda`

## Preliminaries

Amortized LDA takes as input a cell-by-feature matrix $X$ with $C$ cells and $F$ features (bag-of-words representation). The number of topics $K$ must be manually set before fitting.

## Generative Process

For all $n \in [N]$ feature counts for cell $c \in [C]$:

- $\beta_k \sim \text{Dir}(\eta)$ for each topic $k$
- $\theta_c \sim \text{Dir}(\alpha)$ — cell topic distribution
- $x_{cn} \sim \text{Cat}(\theta_c \beta)$ — observed feature counts

The Dirichlet is approximated with a logistic-Normal distribution using the Laplace approximation for reparameterization gradients.

**Latent variables:**

- $\alpha \in (0,\infty)^K$ — Dirichlet prior on cell topic distribution (`cell_topic_prior`)
- $\eta \in (0,\infty)^K$ — Dirichlet prior on topic feature distribution (`topic_feature_prior`)
- $\theta_c \in \Delta^{K-1}$ — cell topic distribution (`cell_topic_dist`)
- $\beta_k \in \Delta^{F-1}$ — topic feature distribution (`topic_feature_dist`)

## Inference

Uses amortized variational inference (AEVB). The underlying encoder class is `scvi.nn.Encoder`.

## Tasks

### Topic-based dimensionality reduction

```python
topic_prop = model.get_latent_representation()
adata.obsm["X_LDA"] = topic_prop
# On held-out data:
test_topic_prop = model.get_latent_representation(test_adata)
```

Returns Monte Carlo estimate (mean over `n_samples` draws) of the logistic-Normal expectation.

### Feature module discovery

```python
feature_by_topic = model.get_feature_by_topic()
```

Returns the estimated feature-by-topic distribution (Monte Carlo estimate).

## setup_anndata

```python
AmortizedLDA.setup_anndata(adata, layer=None, batch_key=None, **kwargs)
```

## References

- Blei, Ng, Jordan (2003), *Latent Dirichlet Allocation*, JMLR.
- Srivastava, Sutton (2017), *Autoencoding Variational Inference for Topic Models*, ICLR.
