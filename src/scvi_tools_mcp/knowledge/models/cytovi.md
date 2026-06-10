# CYTOVI — User Guide

**Class:** `scvi.external.CYTOVI`

## Overview

**CytoVI** is a generative model for cytometry data (flow cytometry, mass cytometry, CITE-seq) leveraging deep probabilistic latent variable modeling for denoising, imputation, integration, and differential analysis.

**Advantages:**

- Batch-corrected low-dimensional representation across antibody-based single-cell technologies
- Integration of datasets with different antibody panels with imputation of non-overlapping markers
- Cross-technology integration (flow, mass cytometry, CITE-seq)
- Label-free differential abundance analysis
- Scalable to >20 million cells

**Limitations:**

- Requires at least partial feature overlap for integration
- Effectively requires GPU
- Assumes spillover-corrected, standard-practice preprocessed data

**Tutorials:**

- `tutorials/notebooks/cytometry/CytoVI_batch_correction_tutorial`
- `tutorials/notebooks/cytometry/CytoVI_advanced_tutorial`

## Preliminaries

**Input:** Transformed (and optionally scaled) protein expression matrix $X \in \mathbb{R}^{N \times P}$.

**Supported technologies:** Flow cytometry (PMT or full spectrum), mass cytometry, CITE-seq, any antibody-based single-cell protein expression.

**Preprocessing:** arcsinh, log1p, biexponential, or logicle transforms followed by optional feature-wise scaling (z-score, min-max, rank-scaled).

**Optional inputs:** batch annotation $s_n$, cell label annotations $y_n$, sample annotations for differential analyses.

## Descriptive Model

Latent variable model where each cell $n$ has a $d$-dimensional latent state $z_n$ decoupled from batch variation $s$.

**Prior on latent space:**

- Isotropic Gaussian: $z_n \sim \mathcal{N}(0, 1)$
- Mixture of Gaussians (default): $z_n \sim \sum_{k=1}^K \pi_k \mathcal{N}(\mu_k, \sigma_k^2)$

Prior weights can be informed by known labels $y$: $\pi_k' = \pi_k + \lambda y$ (default $\lambda=10$).

## Generative Process

Decoder: $f_x: \mathbb{R}^d \times \{0,1\}^S \to \mathbb{R}^P$

**Observation model:**

- Gaussian (default, for arcsinh/log-transformed data): $x_{np} | z_n, s_n \sim \mathcal{N}(\mu_{np}, \sigma_{np}^2)$
- Beta (for $[0,1]$-scaled data): $x_{np} | z_n, s_n \sim \text{Beta}(\alpha_{np}, \beta_{np})$

## Handling Overlapping Antibody Panels

Masking strategy for datasets with different protein panels:

- Binary mask $M_{np}^{(s)} = 1$ if protein $p$ measured in batch $s$
- Encoder uses only shared features $\mathcal{I} = \bigcap_s \mathcal{T}_s$
- Decoder reconstructs union $\mathcal{U} = \bigcup_s \mathcal{T}_s$

```python
adata_list = [adata_batch1, adata_batch2]
adata = scvi.external.CytoVI.merge_batches(adata_list)
```

## Tasks

### Dimensionality reduction

```python
latent = model.get_latent_representation()
adata.obsm["X_CytoVI"] = latent
import scanpy as sc

sc.pp.neighbors(adata, use_rep="X_CytoVI")
```

### Transfer learning

```python
model_query = scvi.external.CYTOVI.load_query_data(
    adata=adata_query, reference_model=model
)
model_query.is_trained = True
adata_query.obs["imputed_label"] = model_query.impute_categories_from_reference(
    adata_reference, cat_key="cell_type"
)
```

### Label-free differential abundance

```python
da_res = model.differential_abundance(adata, groupby="group")
```

Aggregates approximate posteriors across samples, computes log-ratio scores to detect condition-associated cell states without clustering.

### Normalization / denoising / imputation

```python
# Returns batch-corrected expression (averaged across batches by default)
# Imputes missing proteins when overlapping panels are used
expr = model.get_normalized_expression(adata)
```

### Differential expression

```python
de_res = model.differential_expression(adata, groupby="group")
```

### RNA / modality imputation

```python
# Impute RNA for cells with only protein data via kNN (k=20 default)
adata_imputed_rna = model.impute_rna_from_reference(
    reference_batch="CITE_seq",
    adata_rna=adata_rna,
    layer_key="rna_normalized",
    return_query_only=True,
)
```

## References

- Ingelfinger et al. (2025), *CytoVI: Deep generative modeling of antibody-based single cell technologies*, bioRxiv.
- Gayoso et al. (2021), *Joint probabilistic modeling of single-cell multi-omic data with totalVI*, Nature Methods.
- Boyeau et al. (2024), *Deep generative modeling of sample-level heterogeneity in single-cell genomics*, bioRxiv.
