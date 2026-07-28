# STEREOSCOPE — API Reference

## `scviva.external.stereoscope._model.RNAStereoscope`

**Signature:** `RNAStereoscope(sc_adata: 'AnnData', **model_kwargs)`

Reimplementation of Stereoscope for the scRNA-seq component :cite:p:`Andersson20`.

Trains the RNA model whose parameters are then transferred to
:class:`~scviva.external.SpatialStereoscope` for spatial deconvolution.

Original implementation: https://github.com/almaan/stereoscope.

Parameters
----------
sc_adata
    Single-cell AnnData registered via
    :meth:`~scviva.external.RNAStereoscope.setup_anndata`.
**model_kwargs
    Keyword args for :class:`~scviva.external.stereoscope.RNADeconv`.

Examples
--------
>>> scviva.external.RNAStereoscope.setup_anndata(sc_adata, labels_key="labels")
>>> sc_model = RNAStereoscope(sc_adata)
>>> sc_model.train()

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/stereoscope_heart_LV_tutorial`

### setup_anndata

```python
RNAStereoscope.setup_anndata(adata: 'AnnData', labels_key: 'str | None' = None, layer: 'str | None' = None, batch_key: 'str | None' = None, **kwargs)
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
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.

### train

```python
RNAStereoscope.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float' = 1, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Train the model using MAP inference.

Parameters
----------
max_epochs
    Number of epochs to train for.
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
    Size of the training set in [0.0, 1.0].
validation_size
    Size of the test set.
shuffle_set_split
    Whether to shuffle indices before splitting.
batch_size
    Minibatch size.
datasplitter_kwargs
    Additional kwargs for :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.

## `scviva.external.stereoscope._model.SpatialStereoscope`

**Signature:** `SpatialStereoscope(st_adata: 'AnnData', sc_params: 'tuple[np.ndarray]', cell_type_mapping: 'np.ndarray', prior_weight: "Literal['n_obs', 'minibatch']" = 'n_obs', **model_kwargs)`

Reimplementation of Stereoscope for the spatial component :cite:p:`Andersson20`.

Deconvolves spatial transcriptomics spots into cell type proportions using
parameters learned by a pre-trained :class:`~scviva.external.RNAStereoscope` model.

Inherits :class:`~scviva.model.base.SpatialDeconvolutionMixin` which provides
:meth:`get_proportions_df` and :meth:`plot_cell_type_map`.

Parameters
----------
st_adata
    Spatial AnnData registered via
    :meth:`~scviva.external.SpatialStereoscope.setup_anndata`.
sc_params
    Parameters from the RNA model (from :meth:`~scviva.external.RNAStereoscope.get_params`).
cell_type_mapping
    numpy array mapping for the cell types used in the deconvolution.
prior_weight
    How to reweight minibatches. ``"n_obs"`` is statistically correct;
    ``"minibatch"`` reproduces the original Stereoscope paper.
**model_kwargs
    Keyword args for :class:`~scviva.external.stereoscope.SpatialDeconv`.

Examples
--------
>>> RNAStereoscope.setup_anndata(sc_adata, labels_key="labels")
>>> sc_model = RNAStereoscope(sc_adata)
>>> sc_model.train()
>>> SpatialStereoscope.setup_anndata(st_adata)
>>> st_model = SpatialStereoscope.from_rna_model(st_adata, sc_model)
>>> st_model.train()
>>> st_adata.obsm["deconv"] = st_model.get_proportions()

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/stereoscope_heart_LV_tutorial`

### setup_anndata

```python
SpatialStereoscope.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.

### train

```python
SpatialStereoscope.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Train the model using MAP inference.

Parameters
----------
max_epochs
    Number of epochs to train for.
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
shuffle_set_split
    Whether to shuffle indices before splitting.
batch_size
    Minibatch size.
datasplitter_kwargs
    Additional kwargs for :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
