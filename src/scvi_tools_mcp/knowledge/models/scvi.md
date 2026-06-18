# SCVI — API Reference

**Class:** `scvi.model._scvi.SCVI`

**Signature:** `SCVI(adata: 'AnnData | None' = None, registry: 'dict | None' = None, n_hidden: 'int' = 128, n_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', gene_likelihood: "Literal['zinb', 'nb', 'poisson', 'normal']" = 'zinb', use_observed_lib_size: 'bool' = True, latent_distribution: "Literal['normal', 'ln']" = 'normal', **kwargs)`

## Docstring

single-cell Variational Inference :cite:p:`Lopez18`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.model.SCVI.setup_anndata`. If
    ``None``, then the underlying module will not be initialized until training, and a
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
    * ``'normal'`` - ``EXPERIMENTAL`` Normal distribution
use_observed_lib_size
    If ``True``, use the observed library size for RNA as the scaling factor in the mean of the
    conditional distribution.
latent_distribution
    One of:

    * ``'normal'`` - Normal distribution
    * ``'ln'`` - Logistic normal distribution (Normal(0, I) transformed by softmax)
**kwargs
    Additional keyword arguments for :class:`~scvi.module.VAE`.

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.SCVI.setup_anndata(adata, batch_key="batch")
>>> vae = scvi.model.SCVI(adata)
>>> vae.train()
>>> adata.obsm["X_scVI"] = vae.get_latent_representation()
>>> adata.obsm["X_normalized_scVI"] = vae.get_normalized_expression()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/quick_start/api_overview`
2. :doc:`/tutorials/notebooks/scrna/harmonization`
3. :doc:`/tutorials/notebooks/multimodal/scarches_scvi_tools`
4. :doc:`/tutorials/notebooks/r/scvi_in_R`

See Also
--------
:class:`~scvi.module.VAE`

## setup_anndata

```python
SCVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, **kwargs)
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
SCVI.train(self, max_epochs: 'int | None' = None, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, load_sparse_tensor: 'bool' = False, batch_size: 'int' = 128, early_stopping: 'bool' = False, datasplitter_kwargs: 'dict | None' = None, plan_config: 'KwargsLike | None' = None, plan_kwargs: 'KwargsLike | None' = None, datamodule: 'LightningDataModule | None' = None, trainer_config: 'KwargsLike | None' = None, **trainer_kwargs)
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


---

## User Guide

# scVI

**scVI** [^ref1] (single-cell Variational Inference; Python class {class}`~scvi.model.SCVI`) posits a flexible generative model of scRNA-seq count data that can subsequently
be used for many common downstream tasks.

The advantages of scVI are:

-   Comprehensive in capabilities.
-   Scalable to very large datasets (>1 million cells).

The limitations of scVI include:

-   Effectively requires a GPU for fast inference.
-   Latent space is not interpretable, unlike that of a linear method.

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/quick_start/api_overview`
-   {doc}`/tutorials/notebooks/scrna/harmonization`
-   {doc}`/tutorials/notebooks/multimodal/scarches_scvi_tools`
-   {doc}`/tutorials/notebooks/r/scvi_in_R`
```

## Preliminaries

scVI takes as input a scRNA-seq gene expression matrix $X$ with $N$ cells and $G$ genes.
Additionally, a design matrix $S$ containing $p$ observed covariates, such as day, donor, etc., is an optional input.
While $S$ can include both categorical covariates and continuous covariates, in the following, we assume it contains only one
categorical covariate with $K$ categories, which represents the common case of having multiple batches of data.

## Generative process

scVI posits that the observed UMI counts for cell $n$ and gene $g$, $x_{ng}$, are generated
by the following process:

```{math}
:nowrap: true

\begin{align}
 z_n &\sim {\mathrm{Normal}}\left( {0,I} \right) \\
 \ell_n &\sim \mathrm{LogNormal}\left( \ell_\mu^\top s_n ,\ell_{\sigma^2}^\top s_n \right) \\
 \rho _n &= f_w\left( z_n, s_n \right) \\
 \pi_{ng} &= f_h^g(z_n, s_n) \\
 x_{ng} &\sim \mathrm{ObservationModel}(\ell_n \rho_n, \theta_g, \pi_{ng})
 \end{align}
```

Succinctly, the gene expression for each gene depends on a latent variable $z_n$ that is cell-specific.
The prior parameters $\ell_\mu$ and $\ell_{\sigma^2}$ are computed per batch as the mean and variance of the log library size over cells.
The expression data are generated from a count-based likelihood distribution, which here, we denote as the $\mathrm{ObservationModel}$.
While by default the $\mathrm{ObservationModel}$ is a $\mathrm{ZeroInflatedNegativeBinomial}$ (ZINB) distribution parameterized by its mean, inverse dispersion, and non-zero-inflation probability, respectively,
users can pass `gene_likelihood = "negative_binomial"` to {class}`~scvi.model.SCVI`, for example, to use a simpler $\mathrm{NegativeBinomial}$ distribution.

The generative process of scVI uses two neural networks:

```{math}
:nowrap: true

\begin{align}
   f_w(z_n, s_n) &: \mathbb{R}^{d} \times \{0, 1\}^K \to \Delta^{G-1}\\
   f_h(z_n, s_n) &: \mathbb{R}^d \times \{0, 1\}^K \to (0, 1)^T
\end{align}
```

which respectively decode the denoised gene expression and non-zero-inflation probability (only if using ZINB).

This generative process is also summarized in the following graphical model:

:::{figure} figures/scvi_annotated_graphical_model.png
:align: center
:alt: scVI graphical model
:class: img-fluid

scVI graphical model for the ZINB likelihood model. Note that this graphical model contains more latent variables than the presentation above. Marginalization of these latent variables leads to the ZINB observation model (math shown in publication supplement).
:::

The latent variables, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`z_n \in \mathbb{R}^d`
     - Low-dimensional representation capturing the state of a cell.
     - N/A
   * - :math:`\rho_n \in \Delta^{G-1}`
     - Denoised/normalized gene expression. This is a vector that sums to 1 within a cell, unless `size_factor_key is not None` in :class:`~scvi.model.SCVI.setup_anndata`, in which case this is only forced to be non-negative via softplus.
     - ``px_scale``
   * - :math:`\ell_n \in (0, \infty)`
     - Library size for RNA. Here it is modeled as a latent variable, but the recent default for scVI is to treat library size as observed, equal to the total RNA UMI count of a cell. This can be controlled by passing ``use_observed_lib_size=False`` to :class:`~scvi.model.SCVI`. The library size can also be set manually using `size_factor_key` in :class:`~scvi.model.SCVI.setup_anndata`.
     - N/A
   * - :math:`\theta_g \in (0, \infty)`
     - Inverse dispersion for negative binomial. This can be set to be gene/batch specific for example (and would thus be :math:`\theta_{kg}`), by passing ``dispersion="gene-batch"`` during model initialization. Note that ``px_r`` also refers to the underlying real-valued torch parameter that is then exponentiated on every forward pass of the model.
     - ``px_r``
```

## Inference

scVI uses variational inference and specifically auto-encoding variational bayes (see {doc}`/user_guide/background/variational_inference`) to learn both the model parameters (the
neural network params, dispersion params, etc.) and an approximate posterior distribution with the following factorization:

```{math}
:nowrap: true

\begin{align}
   q_\eta(z_n, \ell_n \mid x_n) :=
   q_\eta(z_n \mid x_n, s_n)q_\eta(\ell_n \mid x_n).
\end{align}
```

Here $\eta$ is a set of parameters corresponding to inference neural networks (encoders), which we do not describe in detail here,
but are described in the scVI paper. The underlying class used as the encoder for scVI is {class}`~scvi.nn.Encoder`.
In the case of `use_observed_lib_size=True`, $q_\eta(\ell_n \mid x_n)$ can be written as a point mass on the observed library size.

It is important to note that by default, scVI only
receives the expression data as input (i.e., not the observed cell-level covariates).
Empirically, we have seen little of a difference by having the encoder take as input the concatenation of these items (i.e., $q_\eta(z_n, \ell_n \mid x_n, s_n)$, but users can control it manually by passing
`encode_covariates=True` to {class}`scvi.model.SCVI`.

## Tasks

Here we provide an overview of some of the tasks that scVI can perform. Please see {class}`scvi.model.SCVI` for the full API reference.

### Dimensionality reduction

For dimensionality reduction, the mean of the approximate posterior $q_\eta(z_n \mid x_n, s_n)$ is returned by default.
This is achieved using the method:

```
>>> latent = model.get_latent_representation()
>>> adata.obsm["X_scvi"] = latent
```

Users may also return samples from this distribution, as opposed to the mean by passing the argument `give_mean=False`.
The latent representation can be used to create a nearest neighbor graph with scanpy with:

```
>>> import scanpy as sc
>>> sc.pp.neighbors(adata, use_rep="X_scvi")
>>> adata.obsp["distances"]
```

### Transfer learning

A scVI model can be pre-trained on reference data and updated with query data using {func}`~scvi.model.SCVI.load_query_data`, which then facilitates transfer of metadata like cell type annotations. See the {doc}`/user_guide/background/transfer_learning` guide for more information.

### Normalization/denoising/imputation of expression

In {func}`~scvi.model.SCVI.get_normalized_expression` scVI returns the expected value of $\rho_n$ under the approximate posterior. For one cell $n$, this can be written as:

```{math}
:nowrap: true

\begin{align}
   \mathbb{E}_{q_\eta(z_n \mid x_n)}\left[\ell_n'f_w\left( z_n, s_n \right) \right],
\end{align}
```

where $\ell_n'$ is by default set to 1. See the `library_size` parameter for more details. The expectation is approximated using Monte Carlo, and the number of samples can be passed as an argument in the code:

```
>>> model.get_normalized_expression(n_samples=10)
```

By default, the mean over these samples is returned, but users may pass `return_mean=False` to retrieve all the samples.

Notably, this function also has the `transform_batch` parameter that allows counterfactual prediction of expression in an unobserved batch. See the {doc}`/user_guide/background/counterfactual_prediction` guide.

### Differential expression

Differential expression analysis is achieved with {func}`~scvi.model.SCVI.differential_expression`. scVI tests differences in magnitude of $f_w\left( z_n, s_n \right)$. More info is in {doc}`/user_guide/background/differential_expression`.

### Data simulation

Data can be generated from the model using the posterior predictive distribution in {func}`~scvi.model.SCVI.posterior_predictive_sample`.
This is equivalent to feeding a cell through the model, sampling from the posterior
distributions of the latent variables, retrieving the likelihood parameters (of $p(x \mid z, s)$), and finally, sampling from this distribution.

## Alternative backends and platforms

The standard {class}`~scvi.model.SCVI` class uses PyTorch as its computational backend.
For users who prefer a different framework or are running on hardware where another backend offers better performance, two experimental alternatives are available:

- **JAX** – {class}`~scvi.model.JaxSCVI` is a JAX-based implementation of scVI. It can be substantially faster than the PyTorch implementation on CPUs (e.g., comparable to PyTorch on a GPU on a multi-core machine) and works on any platform supported by JAX. This version is deprecated starting v1.5.
- **MLX (Apple Silicon)** – {class}`~scvi.model.mlxSCVI` is an MLX-based implementation optimized for Apple Silicon (M-series) chips via the [MLX](https://ml-explore.github.io/mlx/) framework. It is only available on macOS with Apple Silicon.

Both alternatives expose the same high-level API (e.g., `setup_anndata`, `train`, `get_latent_representation`, `save`, `load`) as {class}`~scvi.model.SCVI`, though they may have reduced feature sets compared to the full PyTorch implementation.
Saved models are not interchangeable across backends — a model saved with one class cannot be loaded by another.

[^ref1]:
    Romain Lopez, Jeffrey Regier, Michael Cole, Michael I. Jordan, Nir Yosef (2018),
    _Deep generative modeling for single-cell transcriptomics_,
    [Nature Methods](https://www.nature.com/articles/s41592-018-0229-2.epdf?author_access_token=5sMbnZl1iBFitATlpKkddtRgN0jAjWel9jnR3ZoTv0P1-tTjoP-mBfrGiMqpQx63aBtxToJssRfpqQ482otMbBw2GIGGeinWV4cULBLPg4L4DpCg92dEtoMaB1crCRDG7DgtNrM_1j17VfvHfoy1cQ%3D%3D).
