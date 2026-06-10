# MRVI — API Reference

**Class:** `scvi.external.mrvi._model.MRVI`

**Signature:** `MRVI(adata: 'AnnOrMuData | None' = None, registry: 'object | None' = None)`

## Docstring

Multi-resolution Variational Inference (MrVI).

This is a convenience wrapper that instantiates the Torch or JAX
implementation based on `backend` and returns that instance.

Parameters
----------
adata
    AnnData object that has been registered via the appropriate `setup_anndata`.
backend
    Which backend to use: "torch" or "jax".
registry
    (Torch-only) Registry dict for loading from saved state.
**model_kwargs
    Extra keyword args forwarded to the selected implementation.

Notes
-----
- When setup anndata with `backend="torch"`, this returns an instance of `TorchMRVI`.
- When setup anndata with `backend="jax"`, this returns an instance of `JaxMRVI`.

## setup_anndata

```python
MRVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, sample_key: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, backend: 'Backend' = 'torch', **kwargs)
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
sample_key
    key in `adata.obs` for sample information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_sample']`. If `None`, assigns the same sample
    to all the data.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
backend
    Which backend to use: "torch" or "jax".
**kwargs
    Additional keyword arguments passed into
    :meth:`~scvi.data.AnnDataManager.register_fields`.

## train

```python
MRVI.train(self)
```

Trains the model.
