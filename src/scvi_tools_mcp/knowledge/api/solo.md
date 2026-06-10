# SOLO — API Reference

**Class:** `scvi.external.solo._model.SOLO`

**Signature:** `SOLO(adata: 'AnnData', **classifier_kwargs)`

## Docstring

Doublet detection in scRNA-seq :cite:p:`Bernstein20`.

Original implementation: https://github.com/calico/solo.

Most users will initialize the model using the class method
:meth:`~scvi.external.SOLO.from_scvi_model`, which takes as
input a pre-trained :class:`~scvi.model.SCVI` object.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.model.SCVI.setup_anndata`.
    Object should contain the latent representation of real cells and doublets as `adata.X`.
    Object should also be registered, using `.X` and `labels_key="_solo_doub_sim"`.
**classifier_kwargs
    Keyword args for :class:`~scvi.module.Classifier`

Examples
--------
In the case of scVI trained with multiple batches:

>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.SCVI.setup_anndata(adata, batch_key="batch")
>>> vae = scvi.model.SCVI(adata)
>>> vae.train()
>>> solo_batch_1 = scvi.external.SOLO.from_scvi_model(vae, restrict_to_batch="batch 1")
>>> solo_batch_1.train()
>>> solo_batch_1.predict()

Otherwise:

>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.SCVI.setup_anndata(adata)
>>> vae = scvi.model.SCVI(adata)
>>> vae.train()
>>> solo = scvi.external.SOLO.from_scvi_model(vae)
>>> solo.train()
>>> solo.predict()

Notes
-----
Solo should be trained on one lane of data at a time. An
:class:`~scvi.model.SCVI` instance that was trained with multiple
batches can be used as input, but Solo should be created and run
multiple times, each with a new `restrict_to_batch` in
:meth:`~scvi.external.SOLO.from_scvi_model`.

## setup_anndata

```python
SOLO.setup_anndata(adata: 'AnnData', labels_key: 'str | None' = None, layer: 'str | None' = None, **kwargs)
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
SOLO.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.001, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, early_stopping: 'bool' = True, early_stopping_patience: 'int' = 30, early_stopping_warmup_epochs: 'int' = 0, early_stopping_min_delta: 'float' = 0.0, **kwargs)
```

Trains the model.

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
    Size of training set in the range [0.0, 1.0].
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
    Keyword args for :class:`~scvi.train.ClassifierTrainingPlan`.
early_stopping
    Adds callback for early stopping on validation_loss
early_stopping_patience
    Number of times early stopping metric cannot improve over early_stopping_min_delta
early_stopping_warmup_epochs
    Wait for a certain number of warm-up epochs before the early stopping starts monitoring
early_stopping_min_delta
    Threshold for counting an epoch towards patience
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
