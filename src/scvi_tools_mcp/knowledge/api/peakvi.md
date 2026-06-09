# PEAKVI — API Reference

**Class:** `scvi.model._peakvi.PEAKVI`

**Signature:** `PEAKVI(adata: 'AnnData', n_hidden: 'int | None' = None, n_latent: 'int | None' = None, n_layers_encoder: 'int' = 2, n_layers_decoder: 'int' = 2, dropout_rate: 'float' = 0.1, model_depth: 'bool' = True, region_factors: 'bool' = True, use_batch_norm: "Literal['encoder', 'decoder', 'none', 'both']" = 'none', use_layer_norm: "Literal['encoder', 'decoder', 'none', 'both']" = 'both', latent_distribution: "Literal['normal', 'ln']" = 'normal', deeply_inject_covariates: 'bool' = False, encode_covariates: 'bool' = False, **model_kwargs)`

## Docstring

Peak Variational Inference for chromatin accessilibity analysis :cite:p:`Ashuach22`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.model.PEAKVI.setup_anndata`.
n_hidden
    Number of nodes per hidden layer. If `None`, defaults to square root
    of number of regions.
n_latent
    Dimensionality of the latent space. If `None`, defaults to square root
    of `n_hidden`.
n_layers_encoder
    Number of hidden layers used for encoder NN.
n_layers_decoder
    Number of hidden layers used for decoder NN.
dropout_rate
    Dropout rate for neural networks
model_depth
    Model sequencing depth / library size (default: True)
region_factors
    Include region-specific factors in the model (default: True)
latent_distribution
    One of

    * ``'normal'`` - Normal distribution (Default)
    * ``'ln'`` - Logistic normal distribution (Normal(0, I) transformed by softmax)
deeply_inject_covariates
    Whether to deeply inject covariates into all layers of the decoder. If False (default),
    covariates will only be included in the input layer.
**model_kwargs
    Keyword args for :class:`~scvi.module.PEAKVAE`

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.PEAKVI.setup_anndata(adata, batch_key="batch")
>>> vae = scvi.model.PEAKVI(adata)
>>> vae.train()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/atac/PeakVI`

## setup_anndata

```python
PEAKVI.setup_anndata(adata: 'AnnData', batch_key: 'str | None' = None, labels_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
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
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.

## train

```python
PEAKVI.train(self, max_epochs: 'int' = 500, lr: 'float' = 0.0001, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, weight_decay: 'float' = 0.001, eps: 'float' = 1e-08, early_stopping: 'bool' = True, early_stopping_patience: 'int' = 50, check_val_every_n_epoch: 'int | None' = None, n_steps_kl_warmup: 'int | None' = None, n_epochs_kl_warmup: 'int | None' = 50, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Trains the model using amortized variational inference.

Parameters
----------
max_epochs
    Number of passes through the dataset.
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
weight_decay
    weight decay regularization term for optimization
eps
    Optimizer eps
early_stopping
    Whether to perform early stopping with respect to the validation set.
early_stopping_patience
    How many epochs to wait for improvement before early stopping
check_val_every_n_epoch
    Check val every n train epochs. By default, val is not checked, unless `early_stopping`
    is `True`. If so, val is checked every epoch.
n_steps_kl_warmup
    Number of training steps (minibatches) to scale weight on KL divergences from 0 to 1.
    Only activated when `n_epochs_kl_warmup` is set to None. If `None`, defaults
    to `floor(0.75 * adata.n_obs)`.
n_epochs_kl_warmup
    Number of epochs to scale weight on KL divergences from 0 to 1.
    Overrides `n_steps_kl_warmup` when both are not `None`.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
