# DIAGVI — API Reference

**Class:** `scviva.external.diagvi._model.DIAGVI`

**Signature:** `DIAGVI(adatas: 'dict[str, AnnData] | MuData', guidance_graph: 'Data | None' = None, mapping_df: 'pd.DataFrame | None' = None, n_latent: 'int' = 50, n_hidden: 'int' = 256, n_layers: 'int' = 2, dropout_rate: 'float' = 0.1, **model_kwargs)`

## Docstring

Diagonal Multi-Modal Integration Variational Inference (DIAGVI) model.

Integrates multi-modal single-cell data using a guidance graph and supports
semi-supervised learning and GMM priors.

The model architecture is inspired by GLUE (Cao & Gao, 2022).
This scvi-tools implementation is based on GimVI.
Handling of continuous data in decoder is inspired by CytoVI.

Parameters
----------
adatas
    Dictionary mapping input names to AnnData objects.
guidance_graph
    Precomputed guidance graph. If None, it will be constructed from the data
    by using overlapping feature names.
mapping_df
    DataFrame specifying feature correspondences between modalities
    (used to compute the guidance graph).
n_latent
    Dimensionality of the latent space.
n_hidden
    Number of nodes per hidden layer.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
dropout_rate
    Dropout rate for neural networks.
**model_kwargs
    Additional keyword arguments for :class:`~scviva.external.diagvi._module.DIAGVAE`.

Examples
--------
>>> adatas = {"rna_data": adata_rna, "protein_data": adata_protein}
>>> model = DIAGVI(adatas)
>>> model.train()

## setup_anndata

```python
DIAGVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, likelihood: "Literal['nb', 'zinb', 'nbmixture', 'normal', 'log1pnormal', 'ziln', 'zig']" = 'nb', normalize_lib: 'bool' = True, gmm_prior: 'bool' = False, n_mixture_components: 'int' = 10, unlabeled_category: 'str' = 'unknown', **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object to register.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
likelihood
    Likelihood model for this modality (default: 'nb').
    One of:
    - 'nb' : Negative Binomial
    - 'zinb' : Zero-Inflated Negative Binomial
    - 'nbmixture' : Negative Binomial Mixture (for protein data with background/foreground)
    - 'normal' : Normal distribution
    - 'log1pnormal' : Log1p Normal distribution
    - 'ziln' : Zero-Inflated Log Normal distribution
    - 'zig' : Zero-Inflated Gamma distribution
normalize_lib
    Whether to normalize counts with library size in the model.
gmm_prior
    Whether to use a GMM prior for this modality.
n_mixture_components
    Number of mixture components for the GMM prior. If labels_key is provided,
    this parameter is ignored and set to the number of unique labels in labels_key.
unlabeled_category
    Category for unlabeled cells in labels_key.
**kwargs
    Additional keyword arguments.

## train

```python
DIAGVI.train(self, max_epochs: 'int | None' = None, lr: 'float' = 0.001, batch_size: 'int' = 256, train_size: 'float' = 0.9, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', shuffle_set_split: 'bool' = True, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Train the DIAGVI model.

Parameters
----------
max_epochs
    Maximum number of training epochs. If None, a heuristic is used.
lr
    Learning rate for optimization.
batch_size
    Minibatch size for training.
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
    Proportion of data to use for training (rest for validation).
shuffle_set_split
    Whether to shuffle data before splitting into train/validation.
datasplitter_kwargs
    Additional keyword arguments for the DataSplitter and DataLoaders.
    Can be either:
    - A dict of shared kwargs applied to all modalities
    - A nested dict mapping modality names to their specific kwargs,
      e.g., ``{"rna": {"external_indexing": [train, val, test]}, "protein": {...}}``
plan_kwargs
    Additional keyword arguments for the training plan.
**kwargs
    Additional keyword arguments for the Trainer.
