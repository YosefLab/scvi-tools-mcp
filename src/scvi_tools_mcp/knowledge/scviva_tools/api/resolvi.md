# RESOLVI — API Reference

**Class:** `scviva.model._resolvi.ResolVI`

**Signature:** `ResolVI(adata: 'AnnData', n_hidden: 'int' = 32, n_hidden_encoder: 'int' = 128, n_latent: 'int' = 10, n_layers: 'int' = 2, dropout_rate: 'float' = 0.05, dispersion: "Literal['gene', 'gene-batch']" = 'gene', gene_likelihood: "Literal['nb', 'poisson']" = 'nb', background_ratio=None, median_distance=None, semisupervised=False, mixture_k=50, downsample_counts=True, **model_kwargs)`

## Docstring

ResolVI addresses noise and bias in single-cell resolved spatial transcriptomics data.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scviva.model.ResolVI.setup_anndata`.
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
gene_likelihood
    One of:

    * ``'nb'`` - Negative binomial distribution
    * ``'poisson'`` - Poisson distribution
**model_kwargs
    Keyword args for :class:`~scviva.module.RESOLVAE`

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> ResolVI.setup_anndata(adata, batch_key="batch")
>>> model = ResolVI(adata)
>>> model.train()
>>> adata.obsm["X_resolVI"] = model.get_latent_representation()
>>> adata.layers["X_normalized_resolVI"] = model.get_normalized_expression()

## setup_anndata

```python
ResolVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, prepare_data: 'bool | None' = True, prepare_data_kwargs: 'dict | None' = None, unlabeled_category: 'str' = 'unknown', **kwargs)
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
    Key in ``adata.obs`` corresponding to pre-computed size factors.
categorical_covariate_keys
    keys in `adata.obs` that correspond to categorical data.
    These covariates can be added in addition to the batch covariate and are also treated as
    nuisance factors (i.e., the model tries to minimize their effects on the latent space). Thus,
    these should not be used for biologically-relevant factors that you do _not_ want to correct
    for.
prepare_data
    If ``True``, automatically compute spatial neighbors via :meth:`_prepare_data`.
    Set to ``False`` if neighbors are already in ``adata.obsm``.
prepare_data_kwargs
    Keyword args for :meth:`_prepare_data` (e.g. ``n_neighbors``, ``spatial_rep``).
unlabeled_category
    value in `adata.obs[labels_key]` that indicates unlabeled observations.

## train

```python
ResolVI.train(self, max_epochs: 'int' = 50, lr: 'float' = 0.003, lr_extra: 'float' = 0.01, extra_lr_parameters: 'tuple' = ('per_neighbor_diffusion_map', 'u_prior_means'), batch_size: 'int' = 512, weight_decay: 'float' = 0.0, eps: 'float' = 0.0001, n_steps_kl_warmup: 'int | None' = None, n_epochs_kl_warmup: 'int | None' = 20, plan_kwargs: 'dict | None' = None, expose_params: 'list' = (), **kwargs)
```

Train the model using amortized variational inference.

Parameters
----------
max_epochs
    Number of passes through the dataset.
lr
    Learning rate for optimization.
lr_extra
    Learning rate for parameters (non-amortized and custom ones)
extra_lr_parameters
    List of parameters to train with `lr_extra` learning rate.
batch_size
    Minibatch size to use during training.
weight_decay
    weight decay regularization term for optimization
eps
    Optimizer eps
n_steps_kl_warmup
    Number of training steps (minibatches) to scale weight on KL divergences from 0 to 1.
    Only activated when `n_epochs_kl_warmup` is set to None.
n_epochs_kl_warmup
    Number of epochs to scale weight on KL divergences from 0 to 1.
    Overrides `n_steps_kl_warmup` when both are not `None`.
plan_kwargs
    Keyword args for the Pyro training plan.
expose_params
    List of parameters to train if running model in Arches mode.
**kwargs
    Other keyword args for the Trainer.

Notes
-----
RESOLVI trains with Pyro SVI and maintains per-cell global parameters, so it does not
support a held-out validation set. ``train_size`` must be ``1.0`` and ``early_stopping``
is not available.
