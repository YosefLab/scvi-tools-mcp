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


---

## User Guide

# MultiVI

**MultiVI** [^ref1] (Python class {class}`~scvi.model.MULTIVI`) multimodal generative model capable of
integrating multiome, scRNA-seq and scATAC-seq data. After training, it can be used for many common downstream tasks
and also for imputation of a missing modality.

The advantages of multiVI are:

-   Comprehensive in capabilities. Able to perform DE gene, DA region analysis.
-   Scalable to very large datasets (>1 million cells).
-   Once trained with sufficient multimodal data, able to accurately input missing modalities.

The limitations of MultiVI include:

-   Effectively requires a GPU for fast inference.

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/multimodal/MultiVI_tutorial`
```

## Preliminaries

MultiVI takes as input a multiome single-cell matrix $X_{mult}$ with $N$ cells and $G$ genes and
$M$ genomic regions (peaks), or just a scRNA-seq gene expression matrix $X_{rna}$ with $N$ cells and
$G$ genes or just a scATAC-seq accessibility matrix $X_{acc}$ with $N$ cells and $M$ genomic
regions (peaks), which can be binary or have count data.
Additionally, a design matrix $S$ containing $p$ observed covariates, such as day, donor, etc., is an optional input.
While $S$ can include both categorical covariates and continuous covariates, in the following, we assume it contains only one
categorical covariate with $K$ categories, which represents the common case of having multiple batches of data.

## Generative process

MultiVI posits that the observed UMI counts for cell $n$, gene $g$, $x_{ng}$, and regions $j$,
$y_{nj}$, are generated by the following process:

```{math}
:nowrap: true

\begin{align}
 z_n &\sim {\mathrm{Normal}}\left( {0,I} \right) \\
 \ell_n &\sim \mathrm{LogNormal}\left( \ell_\mu^\top s_n ,\ell_{\sigma^2}^\top s_n \right) \\
 \rho _n &= f_w\left( z_n, s_n \right) \\
 \pi_{ng} &= f_h^g(z_n, s_n) \\
 x_{ng} &\sim \mathrm{ObservationModel}(\ell_n \rho_n, \theta_g, \pi_{ng}) \\
 p_{nj} &= g_z^j\left(z_n, s_n\right) \\
  \ell_n &= f_\ell\left(y_n\right)\\
  y_{nj} &\sim \mathrm{Bernoulli}\left(p_{nj} \cdot \ell_n \cdot r_j \right)
 \end{align}
```

For RNA-seq, the prior parameters $\ell_\mu$ and $\ell_{\sigma^2}$ are computed per batch as the mean and
variance of the log library size over cells. The expression data are generated from a count-based likelihood
distribution, which here, we denote as the $\mathrm{ObservationModel}$. While by default the
$\mathrm{ObservationModel}$ is a $\mathrm{ZeroInflatedNegativeBinomial}$ (ZINB) distribution parameterized
by its mean, inverse dispersion, and non-zero-inflation probability, respectively, users can pass
`gene_likelihood = "negative_binomial"` to {class}`~scvi.model.MULTIVI`, for example, to use a simpler
$\mathrm{NegativeBinomial}$ distribution.

For ATAC-seq, detecting a region as accessible ($y_{nj} > 0$) is
generated by a Bernoulli random variable which depends on a cell-specific latent variable $z_n$, which captures
biological heterogeneity, and two auxiliary scaling factors $\ell_n, r_j$, which account for cell-specific and
region-specific technical effects, respectively.

The generative process of MultiVI uses neural networks to produce:

```{math}
:nowrap: true

\begin{align}
   f_w(z_n, s_n) &: \mathbb{R}^{d} \times \{0, 1\}^K \to \Delta^{G-1}\\
   f_h(z_n, s_n) &: \mathbb{R}^d \times \{0, 1\}^K \to (0, 1)^T\\
   g_z(z_n, s_n) &: \mathbb{R}^{d} \times \{0, 1\}^K \to \left[0,1\right]^M
\end{align}
```

which respectively decodes the denoised gene expression, non-zero-inflation probability (only if using ZINB) and
estimates the probability of accessibility.

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
     - Denoised/normalized gene expression. This is a vector that sums to 1 within a cell, unless `size_factor_key is not None` in :class:`~scvi.model.MULTIVI.setup_mudata`, in which case this is only forced to be non-negative via softplus.
     - ``px_scale``
   * - :math:`\ell_n \in (0, \infty)`
     - Library size for RNA.
     - N/A
   * - :math:`\theta_g \in (0, \infty)`
     - Inverse dispersion for negative binomial. This can be set to be gene/batch specific for example (and would thus be :math:`\theta_{kg}`), by passing ``dispersion="gene-batch"`` during model initialization. Note that ``px_r`` also refers to the underlying real-valued torch parameter that is then exponentiated on every forward pass of the model.
     - N/A
   * - :math:`p_r`
     - Accessibility probability estimate
     - N/A
   * - :math:`\ell_n \in \left[0,1\right]`
     - Cell-wise scaling factor. Learned, but can be set manually with `size_factor_key` in :class:`~scvi.model.MULTIVI.setup_mudata`.
     - ``d``
   * - :math:`r_j \in \left[0,1\right]`
     - Region-wise scaling factor
     - ``f``
```

## Inference

MultiVI uses variational inference and specifically auto-encoding variational bayes
(see {doc}`/user_guide/background/variational_inference`) to learn both the model parameters (the
neural network params, dispersion params, etc.) and an approximate posterior distribution with the following factorization:

```{math}
:nowrap: true

\begin{align}
   q_\eta(z_n, \ell_n \mid x_n) :=
   q_\eta(z_n \mid x_n, y_n, s_n)q_\eta(\ell_n \mid x_n).
\end{align}
```

Here $\eta$ is a set of parameters corresponding to inference neural networks (encoders), which we do not describe
in detail here, but are described in the MultiVI paper. The underlying class used as the encoder for MultiVI is
{class}`~scvi.nn.Encoder`. $z_n$ is calculated deterministically as the average of two latent variables part of
the variational approximation $z^{acc}_n$ and $z^{rna}_n$. These two variables are Normal, and for that
reason, $z_n$ is Normal. This formalism permits handling individual modalities by bypassing the average mechanism
and considering each modality variation approximation.

## Tasks

Here we provide an overview of some of the tasks that MultiVI can perform. Please see {class}`scvi.model.MULTIVI` for the full API reference.

### Dimensionality reduction

For dimensionality reduction, the mean of the approximate posterior $q_\eta(z_n \mid x_n, s_n)$ is returned by default.
This is achieved using the method:

```
>>> latent = model.get_latent_representation()
>>> adata.obsm["X_mvi"] = latent
```

Users may also return samples from this distribution, as opposed to the mean by passing the argument `give_mean=False`.
The latent representation can be used to create a nearest neighbor graph with scanpy with:

```
>>> import scanpy as sc
>>> sc.pp.neighbors(adata, use_rep="X_mvi")
>>> adata.obsp["distances"]
```

### Normalization/denoising/imputation of expression

In {func}`~scvi.model.MULTIVI.get_normalized_expression` MultiVI returns the expected value of $\rho_n$ under the approximate posterior. For one cell $n$, this can be written as:

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

It is worth noting that when accessibility data is passed, MultiVI computes the imputation of missing gene expression data.
When gene expression data is passed, MultiVI computes denoised gene expression data.

### Denoising/imputation of accessibility

In {func}`~scvi.model.MULTIVI.get_normalized_accessibility` MultiVI returns the expected value of $y_i$ under the
approximate posterior. For one cell $i$, this can be written as:

```{math}
:nowrap: true

\begin{align}
   \mathbb{E}_{q_\eta(z_i \mid x_i)}\left[g_z\left( z_i, s_i \right) \right],
\end{align}
```

The expectation is approximated by returning the mean of the variation approximation $z_n$ and
then, using this value to decode the accessibility probability estimate $p_r$. Alternatively, to approximate
the variational mean, a number of samples can be passed as an argument in the code:

```
>>> model.get_normalized_accessibility(n_samples_overall=10)
```

This value is used to compute the mean of the latent variable over these samples. Notably, this function also has
the `transform_batch` parameter that allows counterfactual prediction of accessibility in an unobserved batch.
See the {doc}`/user_guide/background/counterfactual_prediction` guide.

It is worth noting that when gene expression data is passed, MultiVI computes the imputation of missing accessibility data.
When accessibility data is passed, MultiVI computes denoised chromatin accessibility.

### Differential expression

Differential expression analysis is achieved with {func}`~scvi.model.MULTIVI.differential_expression`. MultiVI tests differences in magnitude of $f_w\left( z_n, s_n \right)$. More info is in {doc}`/user_guide/background/differential_expression`.

### Differential accessibility

Differential accessibility analysis is achieved with {func}`~scvi.model.MULTIVI.differential_accessibility`. MultiVI tests differences in accessibility of $g_z\left( z_n, s_n \right)$.

[^ref1]:
    Tal Ashuach\*, Mariano I. Gabitto\*, Michael I. Jordan, Nir Yosef (2021),
    _MultiVI: deep generative model for the integration of multi-modal data_,
    `Biorxiv`.
