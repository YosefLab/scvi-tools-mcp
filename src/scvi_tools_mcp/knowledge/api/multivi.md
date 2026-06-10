# MULTIVI — API Reference

**Class:** `scvi.model._multivi.MULTIVI`

**Signature:** `MULTIVI(adata: 'AnnOrMuData', n_genes: 'int | None' = None, n_regions: 'int | None' = None, modality_weights: "Literal['equal', 'cell', 'universal']" = 'equal', modality_penalty: "Literal['Jeffreys', 'MMD', 'None']" = 'Jeffreys', n_hidden: 'int | None' = None, n_latent: 'int | None' = None, n_layers_encoder: 'int' = 2, n_layers_decoder: 'int' = 2, dropout_rate: 'float' = 0.1, region_factors: 'bool' = True, gene_likelihood: "Literal['zinb', 'nb', 'poisson']" = 'zinb', dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', use_batch_norm: "Literal['encoder', 'decoder', 'none', 'both']" = 'none', use_layer_norm: "Literal['encoder', 'decoder', 'none', 'both']" = 'both', latent_distribution: "Literal['normal', 'ln']" = 'normal', deeply_inject_covariates: 'bool' = False, encode_covariates: 'bool' = False, fully_paired: 'bool' = False, protein_dispersion: "Literal['protein', 'protein-batch', 'protein-label']" = 'protein', **model_kwargs)`

## Docstring

Integration of multi-modal and single-modality data :cite:p:`AshuachGabitto21`.

MultiVI is used to integrate multiomic datasets with single-modality (expression
or accessibility) datasets.

Parameters
----------
adata
    MuData object that has been registered via :meth:`~scvi.model.MULTIVI.setup_mudata`.
n_genes
    The number of gene expression features (genes).
n_regions
    The number of accessibility features (genomic regions).
modality_weights
    Weighting scheme across modalities. One of the following:
    * ``"equal"``: Equal weight in each modality
    * ``"universal"``: Learn weights across modalities w_m.
    * ``"cell"``: Learn weights across modalities and cells. w_{m,c}
modality_penalty
    Training Penalty across modalities. One of the following:
    * ``"Jeffreys"``: Jeffreys penalty to align modalities
    * ``"MMD"``: MMD penalty to align modalities
    * ``"None"``: No penalty
n_hidden
    Number of nodes per hidden layer. If `None`, defaults to square root
    of number of regions.
n_latent
    Dimensionality of the latent space. If `None`, defaults to square root
    of `n_hidden`.
n_layers_encoder
    Number of hidden layers used for encoder NNs.
n_layers_decoder
    Number of hidden layers used for decoder NNs.
dropout_rate
    Dropout rate for neural networks.
model_depth
    Model sequencing depth / library size.
region_factors
    Include region-specific factors in the model.
gene_dispersion
    One of the following
    * ``'gene'`` - genes_dispersion parameter of NB is constant per gene across cells
    * ``'gene-batch'`` - genes_dispersion can differ between different batches
    * ``'gene-label'`` - genes_dispersion can differ between different labels
protein_dispersion
    One of the following
    * ``'protein'`` - protein_dispersion parameter is constant per protein across cells
    * ``'protein-batch'`` - protein_dispersion can differ between different batches NOT TESTED
    * ``'protein-label'`` - protein_dispersion can differ between different labels NOT TESTED
latent_distribution
    One of
    * ``'normal'`` - Normal distribution
    * ``'ln'`` - Logistic normal distribution (Normal(0, I) transformed by softmax)
deeply_inject_covariates
    Whether to deeply inject covariates into all layers of the decoder. If False,
    covariates will only be included in the input layer.
fully_paired
    allows the simplification of the model if the data is fully paired. Currently ignored.
**model_kwargs
    Keyword args for :class:`~scvi.module.MULTIVAE`

Examples
--------
>>> adata_rna = anndata.read_h5ad(path_to_rna_anndata)
>>> adata_atac = scvi.data.read_10x_atac(path_to_atac_anndata)
>>> adata_protein = anndata.read_h5ad(path_to_protein_anndata)
>>> mdata = MuData({"rna": adata_rna, "protein": adata_protein, "atac": adata_atac})
>>> scvi.model.MULTIVI.setup_mudata(mdata, batch_key="batch",
>>> modalities={"rna_layer": "rna", "protein_layer": "protein", "batch_key": "rna",
>>>             "atac_layer": "atac"})
>>> vae = scvi.model.MULTIVI(mdata)
>>> vae.train()

Notes (for using setup_anndata)
---------------------------------
As of SCVI-Tools v1.4 there is no longer support for setup_anndata for multivi.
Please use setup_mudata instead.

## setup_anndata

```python
MULTIVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, protein_expression_obsm_key: 'str | None' = None, protein_names_uns_key: 'str | None' = None, **kwargs)
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
protein_expression_obsm_key
    key in `adata.obsm` for protein expression data.
protein_names_uns_key
    key in `adata.uns` for protein names. If None, will use the column names of
    `adata.obsm[protein_expression_obsm_key]` if it is a DataFrame, else will assign
    sequential names to proteins.

## train

```python
MULTIVI.train(self, max_epochs: 'int' = 500, lr: 'float' = 0.0001, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, weight_decay: 'float' = 0.001, eps: 'float' = 1e-08, early_stopping: 'bool' = True, check_val_every_n_epoch: 'int | None' = None, n_steps_kl_warmup: 'int | None' = None, n_epochs_kl_warmup: 'int | None' = 50, adversarial_mixing: 'bool' = True, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
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
adversarial_mixing
    Whether to use adversarial training to penalize the model for umbalanced mixing of
    modalities.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
