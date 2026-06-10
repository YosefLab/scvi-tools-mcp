# TANGRAM — User Guide

**Class:** `scvi.external.Tangram`

## Overview

**Tangram** maps single-cell RNA-seq data to spatial data, permitting deconvolution of cell types in spatial data like Visium. This is a reimplementation of the original [Tangram](https://github.com/broadinstitute/Tangram).

**Tutorial:** `tutorials/notebooks/spatial/tangram_scvi_tools`

## Overview

Tangram learns a mapping matrix $M$ with shape $(n_{sc} \times n_{sp})$ where each row sums to 1. This matrix maps single cells to spatial observations.

## Usage

```python
import scvi
import scanpy as sc

# Setup: adata_sc (scRNA-seq), adata_sp (spatial)
scvi.external.Tangram.setup_anndata(adata_sc)
model = scvi.external.Tangram(adata_sc, adata_sp)
model.train()
mapping = model.get_cell_coordinates()  # returns the M matrix
```

## References

- Biancalani et al. (2021), *Deep learning and alignment of spatially resolved single-cell transcriptomes with Tangram*, Nature Methods.
