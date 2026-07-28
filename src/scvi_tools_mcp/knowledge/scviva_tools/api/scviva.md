# SCVIVA — API Reference

**Class:** `scviva.model._scviva.SCVIVA`

**Signature:** `SCVIVA(adata: 'AnnData | None' = None, n_hidden: 'int' = 128, n_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', gene_likelihood: "Literal['zinb', 'nb', 'poisson']" = 'poisson', latent_distribution: "Literal['normal', 'ln']" = 'normal', **kwargs)`

## Docstring

scVIVA: variational auto-encoder with niche decoders for ST:cite:p:`Levy25`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scviva.model.SCVIVA.setup_anndata`.
    If ``None``, then the underlying module will not be initialized until training, and a
    :class:`~lightning.pytorch.core.LightningDataModule` must be passed in during training.
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
latent_distribution
    One of:

    * ``'normal'`` - Normal distribution
    * ``'ln'`` - Logistic normal distribution (Normal(0, I) transformed by softmax)
**kwargs
    Additional keyword arguments for :class:`~scviva.module._nichevae.nicheVAE`.

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scviva.model.SCVIVA.preprocessing_anndata(
    adata,
    k_nn = 20,
    sample_key = 'slide_ID',
    labels_key = "cell_type",
    cell_coordinates_key = "spatial",
    expression_embedding_key = "X_scVI",
    **kwargs
)
>>> scviva.model.SCVIVA.setup_anndata(adata, batch_key="batch")
>>> vae = scviva.model.SCVIVA(adata)
>>> vae.train()
>>> adata.obsm["X_scVIVA"] = vae.get_latent_representation()
>>> adata.obsm["X_normalized_scVIVA"] = vae.get_normalized_expression()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/spatial/scVIVA_tutorial`

See Also
--------
:class:`~scviva.module._nichevae.nicheVAE`

## setup_anndata

```python
SCVIVA.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, sample_key: 'str | None' = None, labels_key: 'str' = 'cell_type', cell_coordinates_key: 'str' = 'spatial', expression_embedding_key: 'str' = 'X_scVI', expression_embedding_niche_key: 'str' = 'niche_activation', niche_composition_key: 'str' = 'niche_composition', niche_indexes_key: 'str' = 'niche_indexes', niche_distances_key: 'str' = 'niche_distances', **kwargs)
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
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
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

## train

```python
SCVIVA.train(self, max_epochs: 'int | None' = None, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, load_sparse_tensor: 'bool' = False, batch_size: 'int' = 128, early_stopping: 'bool' = False, datasplitter_kwargs: 'dict | None' = None, plan_config: 'KwargsLike | None' = None, plan_kwargs: 'KwargsLike | None' = None, datamodule: 'LightningDataModule | None' = None, trainer_config: 'KwargsLike | None' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    The maximum number of epochs to train the model. The actual number of epochs may be
    less if early stopping is enabled. If ``None``, defaults to a heuristic based on
    :func:`~scvi.model.get_max_epochs_heuristic`. Must be passed in if ``datamodule`` is
    passed in, and it does not have an ``n_obs`` attribute.
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
    Float, or None. Size of training set in the range ``[0.0, 1.0]``. The default is None,
    which is practically 0.9 and potentially adding a small last batch to validation cells.
    Passed into :class:`~scvi.dataloaders.DataSplitter`.
    Not used if ``datamodule`` is passed in.
validation_size
    Size of the test set. If ``None``, defaults to ``1 - train_size``. If
    ``train_size + validation_size < 1``, the remaining cells belong to a test set. Passed
    into :class:`~scvi.dataloaders.DataSplitter`. Not used if ``datamodule`` is passed in.
shuffle_set_split
    Whether to shuffle indices before splitting. If ``False``, the val, train, and test set
    are split in the sequential order of the data according to ``validation_size`` and
    ``train_size`` percentages. Passed into :class:`~scvi.dataloaders.DataSplitter`. Not
    used if ``datamodule`` is passed in.
load_sparse_tensor
    ``EXPERIMENTAL`` If ``True``, loads data with sparse CSR or CSC layout as a
    :class:`~torch.Tensor` with the same layout. Can lead to speedups in data transfers to
    GPUs, depending on the sparsity of the data. Passed into
    :class:`~scvi.dataloaders.DataSplitter`. Not used if ``datamodule`` is passed in.
batch_size
    Minibatch size to use during training. Passed into
    :class:`~scvi.dataloaders.DataSplitter`. Not used if ``datamodule`` is passed in.
early_stopping
    Perform early stopping. Additional arguments can be passed in through ``**kwargs``.
    See :class:`~scvi.train.Trainer` for further options.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
    Values in this argument can be overwritten by arguments directly passed into this
    method, when appropriate. Not used if ``datamodule`` is passed in.
plan_config
    Configuration object or mapping used to build :class:`~scvi.train.TrainingPlan`.
    Values in ``plan_kwargs`` and explicit arguments take precedence.
plan_kwargs
    Additional keyword arguments passed into :class:`~scvi.train.TrainingPlan`. Values in
    this argument can be overwritten by arguments directly passed into this method, when
    appropriate.
datamodule
    ``EXPERIMENTAL`` A :class:`~lightning.pytorch.core.LightningDataModule` instance to use
    for training in place of the default :class:`~scvi.dataloaders.DataSplitter`. Can only
    be passed in if the model was not initialized with :class:`~anndata.AnnData`.
trainer_config
    Configuration object or mapping used to build :class:`~scvi.train.Trainer`. Values in
    ``trainer_kwargs`` and explicit arguments take precedence.
**kwargs
   Additional keyword arguments passed into :class:`~scvi.train.Trainer`.
