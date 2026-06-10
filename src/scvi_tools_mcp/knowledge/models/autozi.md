# AUTOZI — User Guide

**Class:** `scvi.model.AUTOZI`

## Overview

**AUTOZI** is a model for assessing gene-specific levels of zero-inflation in scRNA-seq data. It extends scVI with a spike-and-slab prior on the zero-inflation mixture per gene.

**Tutorials:** `tutorials/notebooks/scrna/AutoZI_tutorial`

## Generative Process

Very similar to scVI but with a Beta spike-and-slab prior on per-gene zero-inflation:

- $z_n \sim \mathcal{N}(0, I)$
- $l_n \sim \text{LogNormal}(l_u, l_{\sigma^2})$
- $\delta_g \sim \text{Beta}(\alpha^g, \beta^g)$ — per-gene zero-inflation probability
- $m_g \sim \text{Bernoulli}(\delta_g)$ — spike/slab selector
- $\pi_{ng} = (1-m_g)\delta_{\{0\}} + m_g \delta_{\{h^g(z_n)\}}$
- $x_{ng} | z_n, l_n, m_g \sim \text{ZINB}(l_n w_g(z_n), \theta_g, \pi_{ng})$

Default priors $\alpha^g = \beta^g = 0.5$ enforce sparsity with symmetry. $\delta_{\{x\}}$ denotes the Dirac distribution.

## Inference

Variational inference with factorized approximate posterior:

$$\bar{q} = \prod_g q(\delta_g) \prod_n q(z_n|x_n) q(l_n|x_n)$$

## Tasks

### Zero-inflation classification

```python
outputs = model.get_alpha_betas()
alpha_posterior = outputs["alpha_posterior"]
beta_posterior = outputs["beta_posterior"]

# Posterior probability of zero-inflation (Bayesian decision theory):
from scipy.stats import beta

zi_probs = beta.cdf(0.5, alpha_posterior, beta_posterior)
# Genes with zi_probs > threshold are zero-inflated
```

## setup_anndata

```python
AUTOZI.setup_anndata(
    adata,
    layer=None,
    batch_key=None,
    labels_key=None,
    categorical_covariate_keys=None,
    continuous_covariate_keys=None,
    **kwargs
)
```

## References

- Clivio, Lopez, Regier, Gayoso, Jordan, Yosef (2019), *Detecting zero-inflated genes in single-cell transcriptomics data*, MLCB.
