# GIMVI — API Reference

**Class:** `scvi.external.gimvi._model.GIMVI`

**Signature:** `GIMVI(adata_seq: 'AnnData', adata_spatial: 'AnnData', generative_distributions: 'list[str] | None' = None, model_library_size: 'list[bool] | None' = None, n_latent: 'int' = 10, **model_kwargs)`

## Docstring

Joint VAE for imputing missing genes in spatial data :cite:p:`Lopez19`.

Parameters
----------
adata_seq
    AnnData object that has been registered via :meth:`~scvi.external.GIMVI.setup_anndata`
    and contains RNA-seq data.
adata_spatial
    AnnData object that has been registered via :meth:`~scvi.external.GIMVI.setup_anndata`
    and contains spatial data.
n_hidden
    Number of nodes per hidden layer.
generative_distributions
    List of generative distribution for adata_seq data and adata_spatial data. Defaults to
    ['zinb', 'nb'].
model_library_size
    List of bool of whether to model library size for adata_seq and adata_spatial. Defaults to
    [True, False].
n_latent
    Dimensionality of the latent space.
**model_kwargs
    Keyword args for :class:`~scvi.external.gimvi.JVAE`

Examples
--------
>>> adata_seq = anndata.read_h5ad(path_to_anndata_seq)
>>> adata_spatial = anndata.read_h5ad(path_to_anndata_spatial)
>>> scvi.external.GIMVI.setup_anndata(adata_seq)
>>> scvi.external.GIMVI.setup_anndata(adata_spatial)
>>> vae = scvi.model.GIMVI(adata_seq, adata_spatial)
>>> vae.train(n_epochs=400)

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/spatial/gimvi_tutorial`

## setup_anndata

```python
GIMVI.setup_anndata(adata: 'AnnData', batch_key: 'str | None' = None, labels_key: 'str | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.

## train

```python
GIMVI.train(self, max_epochs: 'int' = 200, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', kappa: 'int' = 5, train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
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
kappa
    Scaling parameter for the discriminator loss.
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
    Keyword args for model-specific Pytorch Lightning task. Keyword arguments passed
    to `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
