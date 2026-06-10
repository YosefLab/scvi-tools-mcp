# CONTRASTIVEVI — API Reference

**Class:** `scvi.external.contrastivevi._model.ContrastiveVI`

**Signature:** `ContrastiveVI(adata: 'AnnData', n_hidden: 'int' = 128, n_background_latent: 'int' = 10, n_salient_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, use_observed_lib_size: 'bool' = True, wasserstein_penalty: 'float' = 0) -> 'None'`

## Docstring

contrastive variational inference :cite:p:`Weinberger23`.

Parameters
----------
adata
    AnnData object that has been registered via
    :meth:`~scvi.external.ContrastiveVI.setup_anndata`.
n_hidden
    Number of nodes per hidden layer.
n_background_latent
    Dimensionality of the background shared latent space.
n_salient_latent
    Dimensionality of the salient latent space.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
dropout_rate
    Dropout rate for neural networks.
use_observed_lib_size
    Use observed library size for RNA as scaling factor in mean of conditional distribution.
wasserstein_penalty
    Weight of the Wasserstein distance loss that further discourages background
    shared variations from leaking into the salient latent space.

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/scrna/contrastiveVI_tutorial`

## setup_anndata

```python
ContrastiveVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
size_factor_key
    key in `adata.obs` for size factor information. Instead of using library size as a size factor,
    the provided size factor column will be used as offset in the mean of the likelihood. Assumed
    to be on linear scale.
categorical_covariate_keys
    keys in `adata.obs` that correspond to categorical data.
    These covariates can be added in addition to the batch covariate and are also treated as
    nuisance factors (i.e., the model tries to minimize their effects on the latent space). Thus,
    these should not be used for biologically-relevant factors that you do _not_ want to correct
    for.
continuous_covariate_keys
    keys in `adata.obs` that correspond to continuous data.
    These covariates can be added in addition to the batch covariate and are also treated as
    nuisance factors (i.e., the model tries to minimize their effects on the latent space). Thus,
    these should not be used for biologically-relevant factors that you do _not_ want to correct
    for.

## train

```python
ContrastiveVI.train(self, background_indices: 'list[int]', target_indices: 'list[int]', max_epochs: 'int | None' = None, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, load_sparse_tensor: 'bool' = False, batch_size: 'int' = 128, early_stopping: 'bool' = False, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Number of passes through the dataset. If `None`, defaults to
    `np.min([round((20000 / n_cells) * 400), 400])`
accelerator
    Supports passing different accelerator types `("cpu", "gpu", "tpu", "ipu", "hpu",
    "mps, "auto")` as well as custom accelerator instances.
devices
    The devices to use. Can be set to a non-negative index (`int` or `str`), a sequence
    of device indices (`list` or comma-separated `str`), the value `-1` to indicate all
    available devices, or `"auto"` for automatic selection based on the chosen
    `accelerator`. If set to `"auto"` and `accelerator` is not determined to be `"cpu"`,
    then `devices` will be set to the first available device.
train_size
    Size of training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train, and test set
    are split in the sequential order of the data according to `validation_size` and
    `train_size` percentages.
load_sparse_tensor
    ``EXPERIMENTAL`` If ``True``, loads data with sparse CSR or CSC layout as a
    :class:`~torch.Tensor` with the same layout. Can lead to speedups in data transfers to
    GPUs, depending on the sparsity of the data.
batch_size
    Minibatch size to use during training.
early_stopping
    Perform early stopping. Additional arguments can be passed in `**kwargs`.
    See :class:`~scvi.train.Trainer` for further options.
datasplitter_kwargs
    Additional keyword arguments passed into
    :class:`~scvi.external.contrastivevi.ContrastiveDataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**trainer_kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.


---

## User Guide

# contrastiveVI

**contrastiveVI** [^ref1] (contrastive variational inference; Python class
{class}`~scvi.external.ContrastiveVI`) is a generative model for the contrastive analysis
of scRNA-seq count data that can subsequently be used for many common downstream tasks.

Contrastive analysis requires a _target_ (e.g., treated cells) and a _background_
(e.g., control cells) dataset, and contrastiveVI is designed to isolate the variations
enriched in target cells from variations shared with background cells.

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/scrna/contrastiveVI_tutorial`
```

## Overview

:::{note}
This page is under construction.
:::

[^ref1]:
    Ethan Weinberger, Chris Lin, Su-In Lee (2023),
    _Isolating salient variations of interest in single-cell data with contrastiveVI_,
    [Nature Methods](https://www.nature.com/articles/s41592-023-01955-3).
