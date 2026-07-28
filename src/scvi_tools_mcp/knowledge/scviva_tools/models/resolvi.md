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


---

## User Guide

# ResolVI

**ResolVI** {cite:p}`Ergen25` (Python class {class}`~scviva.ResolVI`) is a generative model of single-cell resolved spatial
transcriptomics that can subsequently be used for many common downstream tasks.

The advantages of ResolVI are:

-   Addresses noise and bias in ST data due to wrong segmentation, unspecific background and limited spatial resolution
-   Scalable to very large datasets (>1 million cells).

The limitations of ResolVI include:

-   Effectively requires a GPU for fast inference.
-   Latent space is not interpretable, unlike that of a linear method.
-   Assumes single cells are observed and do not work with low-resolution ST like Visium or Slide-Seq.

```{topic} Tutorials:

-   {doc}`/tutorials/resolVI_tutorial`
```

## Preliminaries

ResolVI takes as input spatially resolved RNA_seq count matrices downstream of cellular segmentation and molecule
assignments to cells. These counts can be either derived from sequencing spatially resolved molecules or fluorescent
imaging. ResolVI leverages the gene expression of neighboring cells and reassigns observed gene expression to neighboring
cells as well as an unspecific background.

ResolVI accepts as input the observed expression of the cell itself, its spatial neighbors and their gene expression
as well as the distance between these cells. Additionally, a vector of categorical covariates $S$, representing
batch, donor, etc., is an optional input to the model. ResolVI provides a semi-supervised mode, adjusting the prior in
the latent space for different cell types and training a classifier to predict cell types from latent embeddings.

## Generative process

ResolVI posits that the observed expression of cell $n$ in gene $g$, $x_{ng}$ is generated by the following process:

```{math}
:nowrap: true

\begin{align}
    z &\sim \mathrm{MixtureOfGaussians}(\mu_1, \dots, \mu_K, \Sigma_1, \dots, \Sigma_K) \\
    \alpha_n &\sim \mathrm{Dirichlet}(C) \\
    r_{ng} &\sim \mathrm{Exponential}(R) \\
    h_{ng} &=
    \mathrm{Gamma}(r_{ng}, \frac{r_{ng}}{\alpha_0 f_\theta(z, b) + \alpha_1 \sum\limits_{{N(n)}} \beta_{N(n)} f_\theta(z_{N(n)}, b)}) + \alpha_2 bg\\
    x_{ng} &\sim \mathrm{Poisson}(l_n h_{ng})
\end{align}
```

In particular, $z$ and $z_{N(n)}$ are the latent embeddings of the cell itself as well as its spatial neighbors
both of dimension $L$. ResolVI uses a mixture of Gaussians prior to $z$:

```{math}
:nowrap: true

\begin{align}
    c_n &\sim \textrm{Categorical}(
        \pi_1, \pi_2, \dots, \pi_K
    ), \\
    z_n \mid c_n = c &\sim \mathcal{N}(\mu_c, \sigma_c)
\end{align}
```

In brief, we assume that observed expression of gene $g$ for cell $n$ can be modelled as a sum over
the components of expression truly expressed by the cell $\alpha_0$, the expression explained by neighboring
cells $\alpha_1$ and wrongly assigned to $n$ and a component due to unspecific background $\alpha_2$.

The latent variables, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`z_n \in \mathbb{R}^L`
     - Low-dimensional representation capturing the state of a cell
     - ``latent``
   * - :math:`\beta_{N(n)} \in \Delta^{N(n) - 1}`
     - Per-neighbor diffusion
     - ``per_neighbor_diffusion``
   * - :math:`\alpha_{n0 \dots 2} \in \Delta^{2}`
     - Per cell true, diffusion and background proportion
     - ``mixture_proportions``
   * - :math:`bg_{ng} \in \Delta^{G - 1}`
     - Per cell estimate of background
     - ``background``
   * - :math:`background_{s} \in \mathbb{R}^G`
     - Per sample background vector
     - ``per_gene_background``
   * - :math:`\rho_n \in \Delta^{G - 1}`
     - Per cell rate of expression
     - ``px_scale``
   * - :math:`\mu_n, \mu_{N(n)} \in \mathbb{R}^G`
     - Per cell estimated expression
     - ``px_rate and px_rate_n``
```


## Inference

ResolVI uses variational inference, specifically auto-encoding variational Bayes in Pyro to learn both the model parameters
(the neural network parameters, dispersion parameters, etc.) and an approximate posterior distribution.
We perform amortization using neural network for $z_n$ and $\alpha_n$, while $\beta_{N(n)n}$ is estimated
for each cell.

## Tasks

Here we provide an overview of some of the tasks that ResolVI can perform. Please see {class}`scviva.ResolVI`
for the full API reference.

### Dimensionality reduction

For dimensionality reduction, the mean of the approximate posterior $q_\phi(z_i \mid y_i, n_i)$ is returned by default.
This is achieved using the method:

```
>>> adata.obsm["X_resolvi"] = model.get_latent_representation()
```

Users may also return samples from this distribution, as opposed to the mean, by passing the argument `give_mean=False`.
The latent representation can be used to create a nearest neighbor graph with scanpy with:

```
>>> import scanpy as sc
>>> sc.pp.neighbors(adata, use_rep="X_resolvi")
>>> adata.obsp["distances"]
```

### Transfer learning

A ResolVI model can be pre-trained on reference data and updated with query data using {meth}`~scviva.ResolVI.load_query_data`, which then facilitates transfer of metadata like cell type annotations.

### Estimation of true expression levels

In {meth}`~scviva.ResolVI.get_normalized_expression` ResolVI returns the expected true expression value of $\rho_n$ under the approximate posterior. For one cell $n$, this can be written as:

```{math}
:nowrap: true

\begin{align}
   \mathbb{E}_{q_\phi(z_n \mid x_n)}\left[f_{\theta}\left(z_{n}, s_n \right) \right]
\end{align}
```

### Differential expression

Differential expression analysis is achieved with {meth}`~scviva.ResolVI.differential_expression`.
ResolVI tests differences in expression levels $\rho_{n} = f_{\theta}\left(z_n, s_n\right)$.

### Cell-type prediction

Prediction of cell-type labels is performed with {meth}`~scviva.ResolVI.predict`.
A semisupervised model is necessary to perform this analysis as it leverages the cell-type classifier.

### Differential niche abundance

Differential niche abundance analysis is achieved with {meth}`~scviva.ResolVI.differential_niche_abundance`.
A semisupervised model is necessary to perform this analysis as it leverages the cell-type classifier.

## Quick Start

```python
import scviva

# Setup and train
scviva.ResolVI.setup_anndata(adata, layer="counts", spatial_key="spatial")
model = scviva.ResolVI(adata)
model.train()

# Get corrected expression
corrected = model.get_normalized_expression(adata)

# Get latent representation
latent = model.get_latent_representation()
```
