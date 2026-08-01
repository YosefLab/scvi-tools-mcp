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
