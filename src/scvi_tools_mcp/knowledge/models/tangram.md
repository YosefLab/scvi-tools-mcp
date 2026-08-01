# TANGRAM — API Reference

**Class:** `scvi.external.tangram._model.Tangram`

**Signature:** `Tangram(sc_adata: anndata.AnnData, constrained: bool = False, target_count: int | None = None, **model_kwargs)`

## Docstring

Torch reimplementation of Tangram :cite:p:`Biancalani21`.

Maps single-cell RNA-seq data to spatial data. Original implementation:
https://github.com/broadinstitute/Tangram.

Currently the "cells" and "constrained" modes are implemented.

Parameters
----------
mdata
    MuData object that has been registered via :meth:`~scvi.external.Tangram.setup_mudata`.
constrained
    Whether to use the constrained version of Tangram instead of cells mode.
target_count
    The number of cells to be filtered. Necessary when `constrained` is True.
**model_kwargs
    Keyword args for :class:`~scvi.external.tangram.TangramMapper`

Examples
--------
>>> from scvi.external import Tangram
>>> ad_sc = anndata.read_h5ad(path_to_sc_anndata)
>>> ad_sp = anndata.read_h5ad(path_to_sp_anndata)
>>> markers = pd.read_csv(path_to_markers, index_col=0)  # genes to use for mapping
>>> mdata = mudata.MuData(
        {
            "sp_full": ad_sp,
            "sc_full": ad_sc,
            "sp": ad_sp[:, markers].copy(),
            "sc": ad_sc[:, markers].copy()
        }
    )
>>> modalities = {"density_prior_key": "sp", "sc_layer": "sc", "sp_layer": "sp"}
>>> Tangram.setup_mudata(
        mdata, density_prior_key="rna_count_based_density", modalities=modalities
    )
>>> tangram = Tangram(sc_adata)
>>> tangram.train()
>>> ad_sc.obsm["tangram_mapper"] = tangram.get_mapper_matrix()
>>> ad_sp.obsm["tangram_cts"] = tangram.project_cell_annotations(
        ad_sc, ad_sp, ad_sc.obsm["tangram_mapper"], ad_sc.obs["labels"]
    )
>>> projected_ad_sp = tangram.project_genes(ad_sc, ad_sp, ad_sc.obsm["tangram_mapper"])

Notes
-----
See further usage examples in the following tutorials:
1. :doc:`/tutorials/notebooks/spatial/tangram_scvi_tools`
2. The JAX version is deprecated starting v1.5 and replaced by torch backend.

## setup_anndata

```python
Tangram.setup_anndata()
```

Not implemented, use `setup_mudata`.

## train

```python
Tangram.train(self, max_epochs: int = 1000, accelerator: str = 'auto', devices: int | list[int] | str = 'auto', lr: float = 0.1, plan_kwargs: dict | None = None)
```

Train the model.

Parameters
----------
max_epochs
    Number of passes through the dataset.
accelerator
    Supports passing different accelerator types `("cpu", "gpu", "tpu", "ipu", "hpu",
    "mps, "auto")` as well as custom accelerator instances.
devices
    The devices to use. Can be set to a non-negative index (`int` or `str`), a sequence
    of device indices (`list` or comma-separated `str`), the value `-1` to indicate all
    available devices, or `"auto"` for automatic selection based on the chosen
    `accelerator`. If set to `"auto"` and `accelerator` is not determined to be `"cpu"`,
    then `devices` will be set to the first available device.
lr
    Optimizer learning rate (default optimizer is :class:`~torch.optim.Adam`).
    Specifying optimizer via plan_kwargs overrides this choice of lr.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.


---

## User Guide

# Tangram

:::{note}
This model is deprecated starting v1.5.
:::

**Tangram** {cite:p}`Biancalani21` (Python class {class}`~scvi.external.Tangram`) maps single-cell RNA-seq data to spatial data, permitting deconvolution of cell types in spatial data like Visium.

This is a reimplementation of Tangram, which can originally be found [here](https://github.com/broadinstitute/Tangram).

The advantages of Tangram are:

-   It maps single-cell transcriptomes onto spatial observations with a directly
    interpretable mapping matrix.
-   It can project cell annotations, such as cell types, from single-cell data to spatial
    data.
-   It can project gene expression from the single-cell reference into spatial
    coordinates.
-   The scvi-tools implementation supports Tangram's `"cells"` and `"constrained"`
    modes.

The limitations of Tangram include:

-   The scvi-tools model page is deprecated starting v1.5.
-   It requires matched genes between the single-cell and spatial modalities used for
    training.
-   Training is not mini-batched in the current implementation, so memory use depends on
    the number of single-cell observations and spatial observations.
-   Tangram is an optimization-based mapping model, not a generative model with posterior
    sampling.

## Overview

Tangram learns a matrix $M$ with shape ($n_{sc} \times n_{sp}$), in which each row sums to 1. Thus, this matrix can be viewed as a map from single cells to the spatial observations.

:::{note}
Starting scVI-Tools v1.5 this model is part of scVIVA-Tools, and no longer being maintained here.
:::

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/spatial/tangram_scvi_tools`
```

## Preliminaries

Tangram is registered with {meth}`~scvi.external.Tangram.setup_mudata`, not
`setup_anndata`. The input is a MuData object containing a single-cell modality and a
spatial modality. The two modalities used for training must contain the same genes in the
same order.

The `modalities` argument tells Tangram which MuData modality contains each registered
field. A typical setup registers:

-   `sc_layer`, the single-cell expression matrix used for mapping,
-   `sp_layer`, the spatial expression matrix used as the target, and
-   `density_prior_key`, an optional spatial observation column containing a density prior.

If a density prior is supplied, it must sum to 1. The tutorial computes a density prior
from estimated cell counts in spatial observations.

## Mapping Objective

The mapping matrix $M$ is parameterized by unconstrained trainable weights and converted
to a row-stochastic matrix with a softmax. The predicted spatial expression matrix is:

```{math}
:nowrap: true

\begin{align}
 \hat{X}_{sp} = M^\top X_{sc},
\end{align}
```

where $X_{sc}$ is the single-cell expression matrix and $\hat{X}_{sp}$ is the spatial
expression predicted from mapped single cells.

Tangram optimizes a loss that rewards agreement between measured spatial expression and
the predicted spatial expression. The default expression term uses gene-wise cosine
similarity, and an optional spatial-observation-wise cosine term can also be enabled. If a
density prior is registered, the loss includes a KL-divergence term between the predicted
spatial density and the supplied prior.

In constrained mode, Tangram also learns a cell filter and requires `target_count`. The
loss then includes a count term that encourages the selected number of cells to match
`target_count`, plus a filter regularizer.

## Tasks

Here we provide an overview of common tasks. Please see {class}`~scvi.external.Tangram`
for the full API reference.

### Mapping Matrix

After training, {meth}`~scvi.external.Tangram.get_mapper_matrix` returns the mapping
matrix with shape `(n_obs_sc, n_obs_sp)`:

```
>>> mapper = model.get_mapper_matrix()
```

Each row contains a probability distribution over spatial observations for one
single-cell observation.

### Projection of Cell Annotations

{meth}`~scvi.external.Tangram.project_cell_annotations` uses the mapping matrix to
project categorical single-cell labels, such as cell types, onto spatial observations:

```
>>> adata_sp.obsm["tangram_ct_pred"] = model.project_cell_annotations(
...     adata_sc, adata_sp, mapper, adata_sc.obs["cell_type"]
... )
```

The returned DataFrame has spatial observations as rows and label categories as columns.

### Projection of Genes

{meth}`~scvi.external.Tangram.project_genes` multiplies the mapping matrix by the
single-cell expression matrix and returns an AnnData object containing projected gene
expression in spatial coordinates.
