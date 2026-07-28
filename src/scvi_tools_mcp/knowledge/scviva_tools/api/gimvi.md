# GIMVI — API Reference

**Class:** `scviva.model._gimvi.GIMVI`

**Signature:** `GIMVI(adata_seq: 'AnnData', adata_spatial: 'AnnData', generative_distributions: 'list[str] | None' = None, model_library_size: 'list[bool] | None' = None, n_latent: 'int' = 10, **model_kwargs)`

## Docstring

Joint VAE for imputing missing genes in spatial data :cite:p:`Lopez19`.

Learns a joint latent space for paired scRNA-seq and spatial transcriptomics
data, enabling imputation of spatially unmeasured genes.

Parameters
----------
adata_seq
    AnnData object registered via :meth:`~scviva.model.GIMVI.setup_anndata`
    containing scRNA-seq data.
adata_spatial
    AnnData object registered via :meth:`~scviva.model.GIMVI.setup_anndata`
    containing spatial transcriptomics data.
generative_distributions
    List of generative distributions for seq and spatial data.
    Defaults to ``['zinb', 'nb']``.
model_library_size
    Whether to model library size per dataset. Defaults to ``[True, False]``.
n_latent
    Dimensionality of the latent space.
**model_kwargs
    Keyword args for :class:`~scviva.module.JVAE`.

Examples
--------
>>> adata_seq = anndata.read_h5ad(path_to_seq)
>>> adata_spatial = anndata.read_h5ad(path_to_spatial)
>>> scviva.model.GIMVI.setup_anndata(adata_seq)
>>> scviva.model.GIMVI.setup_anndata(adata_spatial)
>>> model = scviva.model.GIMVI(adata_seq, adata_spatial)
>>> model.train(max_epochs=200)

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/gimvi_tutorial`

## setup_anndata

```python
GIMVI.setup_anndata(adata: 'AnnData', batch_key: 'str | None' = None, labels_key: 'str | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Call once for ``adata_seq`` and once for ``adata_spatial`` before constructing the model.

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
kappa
    Scaling parameter for the discriminator loss.
train_size
    Size of training set in the range [0.0, 1.0].
validation_size
    Size of the test set.
shuffle_set_split
    Whether to shuffle indices before splitting.
batch_size
    Minibatch size.
datasplitter_kwargs
    Additional kwargs for :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for the training plan.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
