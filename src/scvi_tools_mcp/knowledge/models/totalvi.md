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


---

## User Guide

# totalVI

**totalVI** [^ref1] (total Variational Inference; Python class {class}`~scvi.model.TOTALVI`) posits a flexible generative model of CITE-seq RNA and protein data that can subsequently
be used for many common downstream tasks.

The advantages of totalVI are:

-   Comprehensive in capabilities.
-   Scalable to very large datasets (>1 million cells).

The limitations of totalVI include:

-   Effectively requires a GPU for fast inference.
-   Difficult to understand the balance between RNA and protein data in the low-dimensional representation of cells.

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/multimodal/totalVI`
-   {doc}`/tutorials/notebooks/multimodal/cite_scrna_integration_w_totalVI`
-   {doc}`/tutorials/notebooks/multimodal/scarches_scvi_tools`
```

## Preliminaries

totalVI takes as input a scRNA-seq gene expression matrix of UMI counts $X$ with $N$ cells and $G$ genes
along with a paired matrix of protein abundance (UMI counts) $Y$, also of $N$ cells, but with $T$ proteins.
Thus, for each cell, we observe both RNA and protein information.
Additionally, a design matrix $S$ containing $p$ observed covariates for each of the cells, such as day, donor, etc., is an optional input.
While $S$ can include both categorical covariates and continuous covariates, in the following, we assume it contains only one
categorical covariate with $K$ categories, which represents the common case of having multiple batches of data.

## Generative process

We posit each cell's protein and RNA expression to be generated by the following process:

First, for each cell $n$,

```{math}
:nowrap: true

\begin{align}
   z_n &\sim \textrm{Normal}(0, I)   \tag{1} \\
   \rho_{n} &= f_\rho(z_n, s_n)  \tag{2} \\
   \alpha_n &= g_\alpha(z_n, s_n)  \tag{3} \\
   \pi_n &= h_\pi(z_n, s_n)  \tag{4} \\
   l_n &\sim \textrm{LogNormal}(l_\mu^\top s_n, l_{\sigma^2}^\top s_n) \tag{5}\\
\end{align}
```

The prior parameters $l_\mu$ and $l_{\sigma^2}$ are computed per batch as the mean and variance of the log library size over cells.
The generative process of totalVI uses neural networks:

```{math}
:nowrap: true

\begin{align}
   f_\rho(z_n, s_n) &: \mathbb{R}^d \times \{0, 1\}^K \to \Delta^{G-1}   \tag{6} \\
   g_\alpha(z_n, s_n) &: \mathbb{R}^d \times \{0, 1\}^K \to [1, \infty)^T \tag{7}\\
   h_\pi(z_n, s_n) &: \mathbb{R}^d \times \{0, 1\}^K \to (0, 1)^T \tag{8}
\end{align}
```

where $d$ is the dimension of the latent space (associated with latent variable $z$).
We also have global parameters $\theta_g$ and $\phi_t$, which represent
gene- and protein-specific (respectively) overdispersion.

Then for each gene $g$ in cell $n$,

```{math}
:nowrap: true

\begin{align}
   x_{ng} &\sim \textrm{NegativeBinomial}\left(l_n\rho_{ng}, \theta_g \right), \tag{10}\\
\end{align}
```

where the negative binomial is parameterized by its mean and inverse dispersion.
And finally for each protein $t$ in cell $n$,

```{math}
:nowrap: true

\begin{align}
   \beta_{nt} &\sim \textrm{LogNormal}(c_t^\top s_n, d_t^\top s_n)  \tag{11}\\
   v_{nt} &\sim \textrm{Bernoulli}(\pi_{nt})  \tag{12}\\
   y_{nt} &\sim \textrm{NegativeBinomial}\left(v_{nt}\beta_{nt} + (1-v_{nt})\beta_{nt}\alpha_{nt}, \phi_t \right)  \tag{14}
\end{align}
```

Integrating out $v_{nt}$ yields a negative binomial mixture conditional distribution for $y_{nt}$.
Furthermore, $\beta_{nt}$ represents a background protein signal due to ambient antibodies or non-specific antibody binding.
The prior parameters $c_t$ and $d_t$ are unfortunately called `background_pro_alpha` and `background_pro_log_beta` in the code.
They are learned parameters during inference but are initialized through a procedure that fits a two-component Gaussian mixture model for each cell
and records the mean and variance of the component with a smaller mean, aggregating across all cells. This can be disabled by setting `empirical_protein_background_prior=False`,
which then forces a random Initialization.

:::{figure} figures/totalvi_graphical_model.svg
:align: center
:alt: totalVI graphical model
:class: img-fluid

totalVI graphical model. Shaded nodes represent observed data, unshaded nodes represent latent variables.
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
     - Low-dimensional representation capturing joint state of a cell
     - N/A
   * - :math:`\rho_n \in \Delta^{G-1}`
     - Denoised/normalized gene expression. This is a vector that sums to 1 within a cell, unless `size_factor_key is not None` in :class:`~scvi.model.TOTALVI.setup_anndata`, in which case this is only forced to be non-negative via softplus.
     - ``px_["scale"]``
   * - :math:`\alpha_n \in [1, \infty)^T`
     - Foreground scaling factor for proteins, identifies the mixture distribution (see below)
     - ``py_["rate_fore"]``
   * - :math:`\pi_n \in (0, 1)^T`
     - Probability of background for each protein
     - ``py_["mixing"]`` (logits scale).
   * - :math:`l_n \in (0, \infty)`
     - Library size for RNA. Here it is modeled as a latent variable, but the recent default for totalVI is to treat library size as observed, equal to the total RNA UMI count of a cell. This can be controlled by passing ``use_observed_lib_size=False`` to :class:`~scvi.model.TOTALVI`. The library size can also be set manually using `size_factor_key` in :class:`~scvi.model.TOTALVI.setup_anndata`.
     - N/A
   * - :math:`\beta_{nt} \in (0, \infty)`
     - Protein background intensity. Used twice to identify the protein mixture model.
     - ``py_["rate_back"]``
```

## Inference

totalVI uses variational inference, and specifically auto-are encoding variational bayes (see {doc}`/user_guide/background/variational_inference`), to learn both the model parameters (the
neural network params, dispersion params, etc.), and an approximate posterior distribution with the following factorization:

```{math}
:nowrap: true

\begin{align}
   q_\eta(\beta_n, z_n, l_n \mid x_n, y_n, s_n) :=
   q_\eta(\beta_n \mid z_n,s_n)q_\eta(z_n \mid x_n, y_n,s_n)q_\eta(l_n \mid x_n, y_n, s_n).
\end{align}
```

Here $\eta$ is a set of parameters corresponding to inference neural networks, which we do not describe in detail here,
but are described in the totalVI paper. totalVI can also handle missing proteins (i.e., a dataset comprising
multiple batches, where each batch potentially has a different antibody panel, or no protein data at all).
We refer the reader to the original publication for these details.

## Tasks

### Dimensionality reduction

For dimensionality reduction, we by default return the mean of the approximate posterior $q_\eta(z_n \mid x_n, y_n,s_n)$.
This is achieved using the method:

```
>>> latent = model.get_latent_representation()
>>> adata.obsm["X_totalvi"] = latent
```

Users may also return samples from this distribution, as opposed to the mean by passing the argument `give_mean=False`.
The latent representation can be used to create a nearest neighbor graph with scanpy with:

```
>>> import scanpy as sc
>>> sc.pp.neighbors(adata, use_rep="X_totalvi")
>>> adata.obsp["distances"]
```

### Normalization and denoising of RNA and protein expression

In {func}`~scvi.model.TOTALVI.get_normalized_expression` totalVI returns, for RNA, the expected value of $l_n\rho_n$ under the approximate posterior,
and for proteins, the expected value of $(1 − \pi_{nt})\beta_{nt}\alpha_n$.
For one cell $n$, in the case of RNA, this can be written as:

```{math}
:nowrap: true

\begin{align}
   \mathbb{E}_{q_\eta(z_n \mid x_n, y_n,s_n)}\left[l_n'f_\rho\left( z_n, s_n \right) \right],
\end{align}
```

where $l_n'$ is by default set to 1. See the `library_size` parameter for more details. The expectation is approximated using Monte Carlo, and the number of samples can be passed as an argument in the code:

```
>>> rna, protein = model.get_normalized_expression(n_samples=10)
```

By default, the mean over these samples is returned, but users may pass `return_mean=False` to retrieve all the samples.

In the case of proteins, there are a few important options that control what constitutes denoised protein expression.
For example, `include_protein_background=True` will result in estimating the expectation of $(1 − \pi_{nt})\beta_{nt}\alpha_{nt} + \pi_{nt}\beta_{nt}$.
Setting `sampling_protein_mixing=True` will result in sampling $v_{nt} \sim \textrm{Bernoulli}(\pi_{nt})$ and
replacing $\pi_{nt}$ with $v_{nt}$.

Notably, this function also has the `transform_batch` parameter that allows counterfactual prediction of expression in an unobserved batch. See the {doc}`/user_guide/background/counterfactual_prediction` guide.

### Differential expression

Differential expression analysis is achieved with {func}`~scvi.model.TOTALVI.differential_expression`. totalVI tests differences in magnitude of $f_\rho\left( z_n, s_n \right)$ for RNA,
and $(1 − \pi_{nt})\beta_{nt}\alpha_{nt}$ with similar options to change this quantity as in the normalized expression function.
More info on the mathematics behind differential expression is in {doc}`/user_guide/background/differential_expression`.

### Data simulation

Data can be generated from the model using the posterior predictive distribution in {func}`~scvi.model.SCVI.posterior_predictive_sample`.
This is equivalent to feeding a cell through the model, sampling from the posterior
distributions of the latent variables, retrieving the likelihood parameters, and finally, sampling from this distribution.

[^ref1]:
    Adam Gayoso\*, Zoë Steier\*, Romain Lopez, Jeffrey Regier, Kristopher L Nazor, Aaron Streets, Nir Yosef (2021),
    _Joint probabilistic modeling of single-cell multi-omic data with totalVI_,
    [Nature Methods](https://www.nature.com/articles/s41592-020-01050-x).
