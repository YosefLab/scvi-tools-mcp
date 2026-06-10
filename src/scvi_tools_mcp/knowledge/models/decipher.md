# DECIPHER — User Guide

**Class:** `scvi.external.Decipher`

## Overview

**Decipher** is a deep generative model for single-cell transcriptomics. Documentation is under active development.

**Tutorials:** `tutorials/notebooks/scrna/decipher_tutorial`

## Usage

```python
import scvi

scvi.external.Decipher.setup_anndata(adata)
model = scvi.external.Decipher(adata)
model.train()
adata.obsm["X_decipher"] = model.get_latent_representation()
```

## References

See the scvi-tools API documentation for `scvi.external.Decipher`.
