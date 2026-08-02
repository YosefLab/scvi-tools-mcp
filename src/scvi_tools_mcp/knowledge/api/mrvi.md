# MRVI — API Reference

**Class:** `scvi.external.mrvi._model.MRVI`

**Signature:** `MRVI(adata: 'AnnData | None' = None, registry: 'dict | None' = None, **model_kwargs)`

## Docstring

Multi-resolution Variational Inference (MrVI) :cite:p:`Boyeau24`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.external.MRVI.setup_anndata`.
n_latent
    Dimensionality of the latent space for ``z``.
n_latent_u
    Dimensionality of the latent space for ``u``.
encoder_n_hidden
    Number of nodes per hidden layer in the encoder.
encoder_n_layers
    Number of hidden layers in the encoder.
z_u_prior
    Whether to use a prior for ``z_u``.
z_u_prior_scale
    Scale of the prior for the difference between ``z`` and ``u``.
u_prior_scale
    Scale of the prior for ``u``.
u_prior_mixture
    Whether to use a mixture model for the ``u`` prior.
u_prior_mixture_k
    Number of components in the mixture model for the ``u`` prior.
learn_z_u_prior_scale
    Whether to learn the scale of the ``z`` and ``u`` difference prior during training.
laplace_scale
    Scale parameter for the Laplace distribution in the decoder.
scale_observations
    Whether to scale loss by the number of observations per sample.
px_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.DecoderZXAttention`.
qz_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.EncoderUZ`.
qu_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.EncoderXU`.

Notes
-----
This implementation of MRVI is in PyTorch.
This will become the default version in v1.4.3 for MRVI.
The JAX version is deprecated starting v1.5.

See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/scrna/MrVI_tutorial_torch`

See the user guide for this model:

1. :doc:`/user_guide/models/mrvi`

See Also
--------
:class:`~scvi.external.mrvi.MRVAE`

## setup_anndata

```python
MRVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, sample_key: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, **kwargs)
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
**kwargs
    Additional keyword arguments passed into
    :meth:`~scvi.data.AnnDataManager.register_fields`.

## train

```python
MRVI.train(self, max_epochs: 'int | None' = None, accelerator: 'str | None' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, batch_size: 'int' = 128, early_stopping: 'bool' = False, plan_kwargs: 'dict | None' = None, datamodule=None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Maximum number of epochs to train the model. The actual number of epochs may be less if
    early stopping is enabled. If ``None``, defaults to a heuristic based on
    :func:`~scvi.model.get_max_epochs_heuristic`.
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
    Size of the training set in the range ``[0.0, 1.0]``.
validation_size
    Size of the validation set. If ``None``, defaults to ``1 - train_size``. If
    ``train_size + validation_size < 1``, the remaining cells belong to a test set.
batch_size
    Minibatch size to use during training.
early_stopping
    Perform early stopping. Additional arguments can be passed in through ``**kwargs``.
    See :class:`~scvi.train.Trainer` for further options.
plan_kwargs
    Additional keyword arguments passed into :class:`~scvi.train.TrainingPlan`.
datamodule
    ``EXPERIMENTAL`` A :class:`~lightning.pytorch.core.LightningDataModule` instance to use
    for training in place of the default :class:`~scvi.dataloaders.DataSplitter`.
**trainer_kwargs
    Additional keyword arguments passed into :class:`~scvi.train.Trainer`.
