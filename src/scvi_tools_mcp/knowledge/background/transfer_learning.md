# Transfer Learning

## Overview

Transfer learning in scvi-tools enables ingesting new (query) data in the context of a reference dataset. Supported for all conditional VAE (cVAE) models that embed data into a lower-dimensional space (scVI, TotalVI, MethylVI, ResolVI, etc.).

Uses the **scArches** approach (architectural surgery).

**Tutorials:**

- `tutorials/notebooks/multimodal/scarches_scvi_tools`
- `tutorials/notebooks/multimodal/totalVI_reference_mapping`

## scArches — Architectural Surgery

### Preliminaries

In a cVAE with one categorical covariate (e.g., batch) of $K$ categories, the first encoder layer is:

$$f_1(x, s) = \max(0, W_x^{(1)} x + W_s^{(1)} s)$$

where $W_s^{(1)} \in \mathbb{R}^{H \times K}$.

### Augmentation for Query Data

Query data may have $L$ new unseen categories $s'$. scArches augments the first layer:

$$f_1(x, s, s') = \max(0, W_x^{(1)} x + W_s^{(1)} s + W_{s'}^{(1)} s')$$

where $W_{s'} \in \mathbb{R}^{H \times L}$ is randomly initialized. Applied to both encoder and decoder.

For models with deep covariate injection (`deeply_inject_covariates=True`), new parameters are added at each hidden layer.

### Training

By default, only the new query-specific parameters $W_{s'}$ are trained; all reference parameters are **frozen**. This ensures reference data latent representations remain unchanged after query mapping.

## Usage

```python
# Load query data into reference model
model_query = scvi.model.SCVI.load_query_data(
    adata=adata_query, reference_model=model_reference
)
model_query.train(max_epochs=100)

# The latent space is now shared between reference and query
latent_query = model_query.get_latent_representation()
```

## Key Properties

- Reference cells' $z$ representations do not change after query mapping
- Query cells are projected into the reference latent space
- Enables transfer of cell type annotations from reference to query
- Works across batches, datasets, and in some cases across species

## References

- Lotfollahi et al. (2021), *Mapping single-cell data to reference atlases by transfer learning*, Nature Biotechnology.
