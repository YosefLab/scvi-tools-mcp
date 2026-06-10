# TOTALANVI — User Guide

**Class:** `scvi.external.TOTALANVI`

## Overview

**TotalANVI** is a semi-supervised generative model of CITE-seq RNA and protein data. Extends TotalVI similarly to how scANVI extends scVI — uses partial cell type annotations to infer states of unlabeled cells and impute missing protein expression.

**Advantages:**

- Comprehensive in capabilities
- Scalable to >1 million cells

**Limitations:**

- Effectively requires GPU
- May not scale to very large number of cell types

**Tutorials:** Work in progress.

## Relationship to TotalVI

TotalANVI extends TotalVI by incorporating cell type labels into the model. It:

- Leverages partial annotations during training
- Infers cell type labels for unlabeled cells
- Imputes missing protein expression

## Usage

```python
import scvi

scvi.external.TOTALANVI.setup_anndata(
    adata, protein_expression_obsm_key="protein_expression", labels_key="cell_type"
)
model = scvi.external.TOTALANVI(adata)
model.train()

# Cell type prediction
predictions = model.predict()
adata.obs["totalanvi_prediction"] = predictions

# Latent representation
adata.obsm["X_totalanvi"] = model.get_latent_representation()
```

## References

- See scvi-tools documentation for `scvi.external.TOTALANVI`.
- Gayoso et al. (2021), *Joint probabilistic modeling of single-cell multi-omic data with totalVI*, Nature Methods.
- Xu et al. (2021), *Probabilistic harmonization and annotation of single-cell transcriptomics data with deep generative models*, Molecular Systems Biology. (scANVI)
