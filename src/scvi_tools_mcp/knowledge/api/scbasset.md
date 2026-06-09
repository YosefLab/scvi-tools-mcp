# SCBASSET — API Reference

**Class:** `scvi.external.scbasset._model.SCBASSET`

**Signature:** `SCBASSET(adata: 'AnnData', n_bottleneck_layer: 'int' = 32, l2_reg_cell_embedding: 'float' = 0.0, **model_kwargs)`

## Docstring

Reimplementation of scBasset :cite:p:`Yuan2022`.

Performs representation learning of scATAC-seq data. Original implementation:
https://github.com/calico/scBasset.

We are working to measure the performance of this model compared to the original.

Parameters
----------
adata
    single-cell AnnData object that has been registered via
    :meth:`~scvi.external.SCBASSET.setup_anndata`.
n_bottleneck_layer
    Size of the bottleneck layer
l2_reg_cell_embedding
    L2 regularization for the cell embedding layer. A value, e.g. 1e-8 can be used to improve
    integration performance.
**model_kwargs
    Keyword args for :class:`~scvi.external.scbasset.ScBassetModule`

Examples
--------
>>> adata = anndata.read_h5ad(path_to_sc_anndata)
>>> scvi.data.add_dna_sequence(adata)
>>> adata = adata.transpose()  # regions by cells
>>> scvi.external.SCBASSET.setup_anndata(adata, dna_code_key="dna_code")
>>> model = scvi.external.SCBASSET(adata)
>>> model.train()
>>> adata.varm["X_scbasset"] = model.get_latent_representation()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/atac/scbasset`
2. :doc:`/tutorials/notebooks/atac/scbasset_batch`

## setup_anndata

```python
SCBASSET.setup_anndata(adata: 'AnnData', dna_code_key: 'str', layer: 'str | None' = None, batch_key: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
dna_code_key
    Key in `adata.obsm` with dna sequences encoded as integer code.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
batch_key
    key in `adata.var` for batch information. Categories will automatically be converted
    into integer categories and saved to `adata.var['_scvi_batch']`. If `None`, assigns the
    same batch to all the data.

Notes
-----
The adata object should be in the regions by cells' format. This is due to scBasset
considering regions as observations and cells as variables. This can be simply achieved
by transposing the data, `bdata = adata.transpose()`.

## train

```python
SCBASSET.train(self, max_epochs: 'int' = 1000, lr: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, early_stopping: 'bool' = True, early_stopping_monitor: 'str' = 'auroc_train', early_stopping_mode: "Literal['min', 'max']" = 'max', early_stopping_min_delta: 'float' = 1e-06, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Number of epochs to train for
lr
    Learning rate for optimization.
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
    Size of the training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train, and test set
    are split in the sequential order of the data according to `validation_size` and
    `train_size` percentages.
batch_size
    Minibatch size to use during training.
early_stopping
    Perform early stopping. Additional arguments can be passed in `**kwargs`.
    See :class:`~scvi.train.Trainer` for further options.
early_stopping_monitor
    Metric logged during validation set epoch. The available metrics will depend on
    the training plan class used. We list the most common options here in the typing.
early_stopping_mode
    In 'min' mode, training will stop when the quantity monitored has stopped decreasing,
    and in 'max' mode it will stop when the quantity monitored has stopped increasing.
early_stopping_min_delta
    Minimum change in the monitored quantity to qualify as an improvement,
    i.e., an absolute change of less than min_delta, will count as no improvement.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**trainer_kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
