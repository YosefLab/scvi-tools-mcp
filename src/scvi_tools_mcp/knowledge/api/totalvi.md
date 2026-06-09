# TOTALVI — API Reference

**Class:** `scvi.model._totalvi.TOTALVI`

**Signature:** `TOTALVI(adata: 'AnnOrMuData', n_latent: 'int' = 20, gene_dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', protein_dispersion: "Literal['protein', 'protein-batch', 'protein-label']" = 'protein', gene_likelihood: "Literal['zinb', 'nb']" = 'nb', latent_distribution: "Literal['normal', 'ln']" = 'normal', empirical_protein_background_prior: 'str | bool | None' = None, override_missing_proteins: 'bool' = False, **model_kwargs)`

## Docstring

total Variational Inference :cite:p:`GayosoSteier21`.

Parameters
----------
adata
    AnnOrMuData object that has been registered via :meth:`~scvi.model.TOTALVI.setup_anndata`
    or :meth:`~scvi.model.TOTALVI.setup_mudata`.
n_latent
    Dimensionality of the latent space.
gene_dispersion
    One of the following:

    * ``'gene'`` - genes_dispersion parameter of NB is constant per gene across cells
    * ``'gene-batch'`` - genes_dispersion can differ between different batches
    * ``'gene-label'`` - genes_dispersion can differ between different labels
protein_dispersion
    One of the following:

    * ``'protein'`` - protein_dispersion parameter is constant per protein across cells
    * ``'protein-batch'`` - protein_dispersion can differ between different batches NOT TESTED
    * ``'protein-label'`` - protein_dispersion can differ between different labels NOT TESTED
gene_likelihood
    One of:

    * ``'nb'`` - Negative binomial distribution
    * ``'zinb'`` - Zero-inflated negative binomial distribution
latent_distribution
    One of:

    * ``'normal'`` - Normal distribution
    * ``'ln'`` - Logistic normal distribution (Normal(0, I) transformed by softmax)
empirical_protein_background_prior
    Set the initialization of protein background prior empirically. This option fits a GMM for
    each of 100 cells per batch and averages the distributions. Note that even with this option
    set to `True`, this only initializes a parameter that is learned during inference. If
    `False`, randomly initializes. The default (`None`) sets this to `True` if greater than 10
    proteins are used.
override_missing_proteins
    If `True` does not treat proteins with all 0 expressions in a particular batch as missing.
**model_kwargs
    Keyword args for :class:`~scvi.module.TOTALVAE`

Examples
--------
>>> mdata = mudata.read_h5mu(path_to_mudata)
>>> scvi.model.TOTALVI.setup_mudata(
...     mdata, modalities={"rna_layer": "rna", "protein_layer": "prot"}
... )
>>> vae = scvi.model.TOTALVI(mdata)
>>> vae.train()
>>> mdata.obsm["X_totalVI"] = vae.get_latent_representation()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/multimodal/totalVI`
2. :doc:`/tutorials/notebooks/multimodal/cite_scrna_integration_w_totalVI`
3. :doc:`/tutorials/notebooks/multimodal/scarches_scvi_tools`

## setup_anndata

```python
TOTALVI.setup_anndata(adata: 'AnnData', protein_expression_obsm_key: 'str', protein_names_uns_key: 'str | None' = None, batch_key: 'str | None' = None, panel_key: 'str | None' = None, layer: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
protein_expression_obsm_key
    key in `adata.obsm` for protein expression data.
protein_names_uns_key
    key in `adata.uns` for protein names. If None, will use the column names of
    `adata.obsm[protein_expression_obsm_key]` if it is a DataFrame, else will assign
    sequential names to proteins.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
panel_key
    key in 'adata.obs' for the various panels used to measure proteins.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
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

Returns
-------
None. Adds the following fields:

.uns['_scvi']
    `scvi` setup dictionary
.obs['_scvi_labels']
    labels encoded as integers
.obs['_scvi_batch']
    batch encoded as integers

## train

```python
TOTALVI.train(self, max_epochs: 'int | None' = None, lr: 'float' = 0.004, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 256, early_stopping: 'bool' = True, check_val_every_n_epoch: 'int | None' = None, reduce_lr_on_plateau: 'bool' = True, n_steps_kl_warmup: 'int | None' = None, n_epochs_kl_warmup: 'int | None' = None, adversarial_classifier: 'bool | None' = None, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, external_indexing: 'list[np.array]' = None, **kwargs)
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
    Size of the training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train, and test set
    are split in the sequential order of the data according to `validation_size` and
    `train_size` percentages.
batch_size
    Minibatch size to use during training.
early_stopping
    Whether to perform early stopping with respect to the validation set.
check_val_every_n_epoch
    Check val every n train epochs. By default, val is not checked unless `early_stopping`
    is `True` or `reduce_lr_on_plateau` is `True`. If either of the latter conditions is
    met, val is checked every epoch.
reduce_lr_on_plateau
    Reduce learning rate on plateau of validation metric (default is ELBO).
n_steps_kl_warmup
    Number of training steps (minibatches) to scale weight on KL divergences from 0 to 1.
    Only activated when `n_epochs_kl_warmup` is set to None. If `None`, defaults
    to `floor(0.75 * adata.n_obs)`.
n_epochs_kl_warmup
    Number of epochs to scale weight on KL divergences from 0 to 1.
    Overrides `n_steps_kl_warmup` when both are not `None`.
adversarial_classifier
    Whether to use adversarial classifier in the latent space. This helps mixing when
    there are missing proteins in any of the batches. Defaults to `True` is missing
    proteins are detected.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.AdversarialTrainingPlan`. Keyword arguments passed
    to `train()` will overwrite values present in `plan_kwargs`, when appropriate.
external_indexing
    A list of data split indices in the order of training, validation, and test sets.
    Validation and test set are not required and can be left empty.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
