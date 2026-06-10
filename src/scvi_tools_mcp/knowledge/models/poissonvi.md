# POISSONVI — User Guide

**Class:** `scvi.external.POISSONVI`

## Overview

**PoissonVI** is a variational inference model for single-cell ATAC-seq data using a Poisson likelihood. Documentation is under active development.

**Tutorial:** `tutorials/notebooks/atac/PoissonVI`

## Usage

```python
import scvi

scvi.external.POISSONVI.setup_anndata(adata)
model = scvi.external.POISSONVI(adata)
model.train()
adata.obsm["X_poissonvi"] = model.get_latent_representation()
```

## References

See the scvi-tools API documentation for `scvi.external.POISSONVI`.
