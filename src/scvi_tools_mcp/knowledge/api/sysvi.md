# SYSVI — API Reference

**Class:** `scvi.external.sysvi._model.SysVI`

**Signature:** `SysVI(adata: 'AnnData', prior: "Literal['standard_normal', 'vamp']" = 'vamp', n_prior_components: 'int' = 5, pseudoinputs_data_indices: 'np.array | None' = None, **model_kwargs)`

## Docstring

Integration with cVAE & optional VampPrior and latent cycle-consistency.

 Described in
 `Hrovatin et al. (2023) <https://doi.org/10.1101/2023.11.03.565463>`_.

Parameters
----------
adata
    AnnData object that has been registered via
    :meth:`~scvi.external.SysVI.setup_anndata`.
prior
    The prior distribution to be used.
    You can choose between ``"standard_normal"`` and ``"vamp"``.
n_prior_components
    Number of prior components (i.e., modes) to use in VampPrior.
pseudoinputs_data_indices
    By default, VampPrior pseudoinputs are randomly selected from data.
    Alternatively, one can specify pseudoinput indices using this parameter.
    The number of specified indices in the input 1D array should match
    ``n_prior_components``.
**model_kwargs
    Keyword args for :class:`~scvi.external.sysvi.SysVAE`

## setup_anndata

```python
SysVI.setup_anndata(adata: 'AnnData', batch_key: 'str', layer: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, weight_batches: 'bool' = False, **kwargs)
```

Prepare adata for input to SysVI model.

Setup distinguishes between two main types of covariates that can be
corrected for:

- batch - referred to as "system" in the original publication
  Hrovatin, et al., 2023):
  Single categorical covariate that will be corrected via cycle
  consistency loss.
  It will be also used as a condition in cVAE.
  This covariate is expected to correspond to stronger batch effects,
  such as between datasets from different sequencing technology or
  model systems (animal species, in-vitro models and tissue, etc.).
- covariate (includes both continuous and categorical covariates):
  Additional covariates to be used only
  as a condition in cVAE, but not corrected via cycle loss.
  These covariates are expected to correspond to weaker batch effects,
  such as between datasets from the same sequencing technology and
  system (animal, in-vitro, etc.) or between samples within a dataset.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
layer
    AnnData layer to use, default is X.
    Should contain normalized and log1p transformed expression.
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
SysVI.train(self, plan_kwargs: 'dict | None' = None, **train_kwargs)
```

Train the models.

Overwrites the ``train`` method of
class:`~scvi.model.base.UnsupervisedTrainingMixin`
to prevent the use of KL loss warmup (specified in ``plan_kwargs``).
This is disabled as our experiments showed poor integration in the
cycle model when using KL loss warmup.

Parameters
----------
plan_kwargs
    Training plan kwargs in `meth`:`scvi.train.TrainingPlan`.
train_kwargs
    Training kwargs. Passed to `meth`:`scvi.model.base.BaseModelClass.train`.
