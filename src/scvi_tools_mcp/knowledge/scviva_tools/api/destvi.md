# DESTVI — API Reference

**Class:** `scviva.model._destvi.DestVI`

**Signature:** `DestVI(st_adata: 'AnnData', cell_type_mapping: 'np.ndarray', decoder_state_dict: 'OrderedDict', px_decoder_state_dict: 'OrderedDict', px_r: 'torch.tensor', per_ct_bias: 'torch.tensor', n_hidden: 'int', n_latent: 'int', n_layers: 'int', dropout_decoder: 'float', **module_kwargs)`

## Docstring

Multi-resolution deconvolution of Spatial Transcriptomics data (DestVI) :cite:p:`Lopez22`.

Most users will use the alternate constructor (see example).

Parameters
----------
st_adata
    spatial transcriptomics AnnData object that has been registered via
    :meth:`~scviva.model.DestVI.setup_anndata`.
cell_type_mapping
    mapping between numerals and cell type labels
decoder_state_dict
    state_dict from the decoder of the CondSCVI model
px_decoder_state_dict
    state_dict from the px_decoder of the CondSCVI model
px_r
    parameters for the px_r tensor in the CondSCVI model
n_hidden
    Number of nodes per hidden layer.
n_latent
    Dimensionality of the latent space.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
**module_kwargs
    Keyword args for :class:`~scviva.module.MRDeconv`

Examples
--------
>>> sc_adata = anndata.read_h5ad(path_to_scRNA_anndata)
>>> scvi.model.CondSCVI.setup_anndata(sc_adata)
>>> sc_model = scvi.model.CondSCVI(sc_adata)
>>> st_adata = anndata.read_h5ad(path_to_ST_anndata)
>>> DestVI.setup_anndata(st_adata)
>>> spatial_model = DestVI.from_rna_model(st_adata, sc_model)
>>> spatial_model.train(max_epochs=2000)
>>> st_adata.obsm["proportions"] = spatial_model.get_proportions(st_adata)
>>> gamma = spatial_model.get_gamma(st_adata)

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/DestVI_tutorial`

## setup_anndata

```python
DestVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, smoothed_layer: 'str | None' = None, batch_key: 'str | None' = None, **kwargs)
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
smoothed_layer
    When provided, the model adds a spatial-smoothing regularization that encourages a
    spot's inferred cell-type proportions to agree with those inferred from its
    neighborhood, yielding spatially smoother deconvolution.
    Optional; if ``None`` the regularization is disabled.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.

## train

```python
DestVI.train(self, max_epochs: 'int' = 2000, lr: 'float' = 0.003, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float' = 1.0, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, n_epochs_kl_warmup: 'int' = 200, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
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
n_epochs_kl_warmup
    number of epochs needed to reach unit kl weight in the elbo
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
