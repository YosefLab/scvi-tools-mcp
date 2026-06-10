# STEREOSCOPE — API Reference

**Class:** `scvi.external.stereoscope._model.RNAStereoscope`

**Signature:** `RNAStereoscope(sc_adata: 'AnnData', **model_kwargs)`

## Docstring

Reimplementation of Stereoscope :cite:p:`Andersson20`.

Deconvolution of spatial transcriptomics from single-cell transcriptomics. Original
implementation: https://github.com/almaan/stereoscope.

Parameters
----------
sc_adata
    single-cell AnnData object that has been registered via
    :meth:`~scvi.external.RNAStereoscope.setup_anndata`.
**model_kwargs
    Keyword args for :class:`~scvi.external.stereoscope.RNADeconv`

Examples
--------
>>> sc_adata = anndata.read_h5ad(path_to_sc_anndata)
>>> scvi.external.RNAStereoscope.setup_anndata(sc_adata, labels_key="labels")
>>> stereo = scvi.external.stereoscope.RNAStereoscope(sc_adata)
>>> stereo.train()

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/spatial/stereoscope_heart_LV_tutorial`

## setup_anndata

```python
RNAStereoscope.setup_anndata(adata: 'AnnData', labels_key: 'str | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.

## train

```python
RNAStereoscope.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float' = 1, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Trains the model using MAP inference.

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
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
