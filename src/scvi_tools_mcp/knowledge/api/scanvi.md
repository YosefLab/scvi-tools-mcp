# SCANVI — API Reference

**Class:** `scvi.model._scanvi.SCANVI`

**Signature:** `SCANVI(adata: 'AnnData | None' = None, registry: 'dict | None' = None, n_hidden: 'int' = 128, n_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', gene_likelihood: "Literal['zinb', 'nb', 'poisson']" = 'zinb', use_observed_lib_size: 'bool' = True, linear_classifier: 'bool' = False, datamodule: 'LightningDataModule | None' = None, **model_kwargs)`

## Docstring

Single-cell annotation using variational inference :cite:p:`Xu21`.

Inspired from M1 + M2 model, as described in (https://arxiv.org/pdf/1406.5298.pdf).

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.model.SCANVI.setup_anndata`.
n_hidden
    Number of nodes per hidden layer.
n_latent
    Dimensionality of the latent space.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
dropout_rate
    Dropout rate for neural networks.
dispersion
    One of the following:

    * ``'gene'`` - dispersion parameter of NB is constant per gene across cells
    * ``'gene-batch'`` - dispersion can differ between different batches
    * ``'gene-label'`` - dispersion can differ between different labels
    * ``'gene-cell'`` - dispersion can differ for every gene in every cell
gene_likelihood
    One of:

    * ``'nb'`` - Negative binomial distribution
    * ``'zinb'`` - Zero-inflated negative binomial distribution
    * ``'poisson'`` - Poisson distribution
use_observed_lib_size
    If ``True``, use the observed library size for RNA as the scaling factor in the mean of the
    conditional distribution.
linear_classifier
    If ``True``, uses a single linear layer for classification instead of a
    multi-layer perceptron.
**model_kwargs
    Keyword args for :class:`~scvi.module.SCANVAE`

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.SCANVI.setup_anndata(adata, batch_key="batch", labels_key="labels")
>>> vae = scvi.model.SCANVI(adata, "Unknown")
>>> vae.train()
>>> adata.obsm["X_scVI"] = vae.get_latent_representation()
>>> adata.obs["pred_label"] = vae.predict()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/scrna/harmonization`
2. :doc:`/tutorials/notebooks/multimodal/scarches_scvi_tools`
3. :doc:`/tutorials/notebooks/scrna/seed_labeling`

## setup_anndata

```python
SCANVI.setup_anndata(adata: 'AnnData', labels_key: 'str', unlabeled_category: 'str', layer: 'str | None' = None, batch_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, use_minified: 'bool' = True, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
unlabeled_category
    value in `adata.obs[labels_key]` that indicates unlabeled observations.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
size_factor_key
    key in `adata.obs` for size factor information. Instead of using library size as a size factor,
    the provided size factor column will be used as offset in the mean of the likelihood. Assumed
    to be on linear scale.
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
use_minified
    If True, will register the minified version of the adata if possible.

## train

```python
SCANVI.train(self, max_epochs: 'int | None' = None, n_samples_per_label: 'float | None' = None, check_val_every_n_epoch: 'int | None' = None, train_size: 'float' = 0.9, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', adversarial_classifier: 'bool | None' = None, datasplitter_kwargs: 'dict | None' = None, plan_config: 'KwargsLike | None' = None, plan_kwargs: 'KwargsLike | None' = None, datamodule: 'LightningDataModule | None' = None, trainer_config: 'KwargsLike | None' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Number of passes through the dataset for semisupervised training.
n_samples_per_label
    Number of subsamples for each label class to sample per epoch. By default, there
    is no label subsampling.
check_val_every_n_epoch
    Frequency with which metrics are computed on the data for the validation set for both
    the unsupervised and semisupervised trainers. If you'd like a different frequency for
    the semisupervised trainer, set check_val_every_n_epoch in semisupervised_train_kwargs.
train_size
    Size of the training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train,
    and test set are split in the sequential order of the data according to
    `validation_size` and `train_size` percentages.
batch_size
    Minibatch size to use during training.
accelerator
    Supports passing different accelerator types `("cpu", "gpu", "tpu", "ipu", "hpu",
    "mps, "auto")` as well as custom accelerator instances.
devices
    The devices to use. Can be set to a non-negative index (`int` or `str`), a sequence
    of device indices (`list` or comma-separated `str`), the value `-1` to indicate all
    available devices, or `"auto"` for automatic selection based on the chosen
    `accelerator`. If set to `"auto"` and `accelerator` is not determined to be `"cpu"`,
    then `devices` will be set to the first available device.
adversarial_classifier
    Whether to use adversarial classifier in the latent space. This helps mixing when
    there are missing proteins in any of the batches. Defaults to `True` is missing
    proteins are detected.
datasplitter_kwargs
    Additional keyword arguments passed into
    :class:`~scvi.dataloaders.SemiSupervisedDataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.SemiSupervisedTrainingPlan`. Keyword
    arguments passed to `train()` will overwrite values present in `plan_kwargs`,
    when appropriate.
plan_config
    Configuration object or mapping used to build
    :class:`~scvi.train.SemiSupervisedTrainingPlan`. Values in ``plan_kwargs`` and
    explicit arguments take precedence.
datamodule
    ``EXPERIMENTAL`` A :class:`~lightning.pytorch.core.LightningDataModule` instance to use
    for training in place of the default :class:`~scvi.dataloaders.DataSplitter`. Can only
    be passed in if the model was not initialized with :class:`~anndata.AnnData`.
trainer_config
    Configuration object or mapping used to build :class:`~scvi.train.Trainer`. Values in
    ``trainer_kwargs`` and explicit arguments take precedence.
**trainer_kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
