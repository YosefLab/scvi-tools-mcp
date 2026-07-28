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

1. :doc:`/tutorials/scVIVA_tutorial`

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


---

## User Guide

# scVIVA

**scVIVA** {cite:p}`Levy25` (Python class {class}`~scviva.SCVIVA`) is a generative model of single-cell resolved spatial
transcriptomics that can subsequently be used for many common downstream tasks.

The advantages of scVIVA are:

-   Provides a probabilistic low-dimensional representation of the state of each cell that is corrected for batch effects
    and captures its gene expression profile and its environment.
-   Enables differential expression analysis across niches while accounting for wrong assignment of molecules to cells.
-   Scalable to very large datasets (>1 million cells).

The limitations of scVIVA include:

-   Effectively requires a GPU for fast inference.
-   Latent space is not interpretable, unlike that of a linear method.
-   Assumes single cells are observed and do not work with low-resolution ST like Visium or Slide-Seq.

```{topic} Tutorials:

-   {doc}`/tutorials/scVIVA_tutorial`
```

## Preliminaries

scVIVA takes as input spatially resolved scRNA data. In addition to the gene expression matrix ${X}$ with $N$ cells and $G$ genes,
it requires for each cell $n$:
- the spatial coordinates of the cell $y_n$
- the cell type assignment (possibly coarse) $c_n \in \{1, ..., T\}$
- the batch assignment $s_n$.


As preprocessing, we take the $K$ nearest neighbors of a cell to define its niche using the Euclidean distance in physical space.
We characterize the niche by its cell-type composition and gene expression. We denote by ${\alpha_n}$ the $T$-dimensional vector of cell type
proportions among the $K$ nearest neighbors of the cell $n$. Its values are in the probability simplex.
The niche gene expression is defined as the average expression of each cell type present in the niche.
In practice, we leverage gene expression embeddings (PCA, scVI or similar) and characterize a cell type expression profile as the local average
embedding of cells of the same type. The average embeddings are stored in the matrix ${\eta_n} \in \mathbb{R}^{T \times D}$, where $D$ is the embedding dimension.
## Descriptive model

We propose a latent variable model aiming to capture both gene expression heterogeneity and spatial variation resulting from the micro-environment.
We assume these two sources of variability are both captured by a $P$-dimensional latent variable ($P \ll G$):

```{math}
:nowrap: true
\begin{align}
    z_n \sim \mathbf{MixtureOfGaussians}(\mu_1, ..., \mu_M; \Sigma_1, ..,\Sigma_M; \pi_1, ...,\pi_M)
\end{align}
```

We assume that the observed counts for cell $n$ and gene $g$, $x_{ng}$, are generated from the following process:

```{math}
:nowrap: true
\begin{align}
 \rho _n &= f_{w}\left( z_n, s_n \right) \\
 x_{ng} &\sim \mathbf{NegativeBinomial}(\ell_n \rho_n, \theta_g),
 \end{align}
```
where $\rho_n$ is the normalized gene expression, $\ell_n$ is the library size of cell $n$ and $\theta_g$ is the dispersion parameter for gene $g$.
The cell-type proportions of the cell's $K$ nearest neighbors are obtained as

```{math}
:nowrap: true
\begin{align}
    \alpha_n &\sim \mathbf{Dirichlet}\left( f_{\omega}(z_n) \right),
\end{align}
```

Last, we assume that the neighboring cells' average expression profiles are obtained as

```{math}
:nowrap: true
\begin{equation}
\eta_{nt} \sim
\begin{cases}
\mathcal{N} \left(f_{\nu}^{t}(z_n) \right), & \text{if } \alpha_{t} > 0 \\
0, & \text{otherwise}
\end{cases}
\end{equation}
```

where $t=1,...,T$. $w$, $\omega$ and $\nu$ are neural network parameters.


## Inference

We want to maximize the evidence of the data, which can be decomposed as:

```{math}
:nowrap: true
\begin{align}
    \log p \left( \alpha, x, \eta \mid s \right) = \log p \left(x \mid s \right) + \log p \left( \alpha, \eta \mid x, s \right).
\end{align}
```

scVIVA uses variational inference, specifically auto-encoding variational Bayes to learn both the model parameters
(the neural network parameters, dispersion parameters, etc.) and an approximate posterior distribution.

## Tasks

Here we provide an overview of some of the tasks that scVIVA can perform. Please see {class}`scviva.SCVIVA`
for the full API reference.

### Dimensionality reduction

For dimensionality reduction, the mean of the approximate posterior $q_\phi(z \mid x)$ is returned by default.
This is achieved using the method:

```
>>> adata.obsm["X_scVIVA"] = model.get_latent_representation()
```

$\phi$ is a set of parameters corresponding to inference neural networks (encoders).
Users may also return samples from this distribution, as opposed to the mean, by passing the argument `give_mean=False`.

### Estimation of normalized expression

In {meth}`~scviva.SCVIVA.get_normalized_expression` scVIVA returns the expected true expression value of $\rho_n$ under the approximate posterior. For one cell $n$, this can be written as:

```{math}
:nowrap: true

\begin{align}
   \mathbb{E}_{q_\phi(z_n \mid x_n)}\left[f_{w}\left(z_{n}, s_n \right) \right]
\end{align}
```

### Differential Expression (DE)

Differential expression analysis is achieved with {meth}`~scviva.SCVIVA.differential_expression`.
We leverage the lvm-DE method and adapt it to spatial data by taking into account cell neighborhood expression in a bid to discard false positives due to contamination.
Considering two groups of cells $\textit{C1}$ and $\textit{C2}$ corresponding to different spatial contexts (for instance, astrocytes in two brain regions), the goal is to determine which genes have different expression levels between the two groups. When setting `niche_mode="true"`, we compute the group spatial neighborhoods $\textit{N1}$ and $\textit{N2}$, which are the spatial nearest neighbors of a different type than the cells in $\textit{C1}$, and $\textit{C2}$ respectively.


To determine the upregulated genes of $\textit{C1 vs C2}$, we compute DE between $\{\textit{C1, C2}\}$, $\{\textit{N1, C2}\}$ and $\{\textit{C1, N1}\}$: using lvm-DE, we test differences in expression levels $\rho_{n}$ to compute Log-Fold Changes (LFC).
The significantly upregulated genes for $\textit{C1, N1}$ define a set of local cell type markers, denoted $\mathcal{S}_1$. Conversely, if a gene is both higher expressed in $\textit{N1}$ compared to $\textit{C1}$ and $\textit{C1}$ compared to $\textit{C2}$, it is likely that the increased expression in $\textit{C1}$ is spurious.
We argue that the probability of a gene being a $\textit{local marker}$ could be a relevant score to filter spurious genes. To compute this score, we considered the upregulation of a gene in one group relative to the upregulation in its neighborhood: a local marker $g$ should verify

```{math}
:nowrap: true
\begin{align}
    \mathit{LFC^{~g}_{C1~vs~C2}} > \mathit{LFC^{~g}_{N1~vs~C2}},
\end{align}
```

which means that the signal comes from cells in $\textit{C1}$ rather than their neighbors $\textit{N1}$.
We select genes for which $\mathit{LFC_{C1~vs~C2}} > 0$ and use the genes $\mathcal{S}_1$ as truly differentially expressed. We also define $\mathcal{N}_1 = \{g|\mathit{LFC^{~g}_{C1~vs~C2}} > 0,~g \notin \mathcal{S}_1 \}$.
We train a Gaussian process classifier on $\mathbf{X} = [LFC_{C1~vs~C2}~,~LFC_{N1~vs~C2}]$ to classify between the $\textit{local markers}$ $\mathcal{S}_1$ and the $\textit{neighborhood genes}$ $\mathcal{N}_1$. Once fitted, the classifier returns a local marker probability $p_g=\mathit{p}(g \in \mathcal{S}_1 | \mathbf{X})$ for each gene $g$, that we can compare to a given threshold $\tau$ to filter the neighborhood genes.

## Quick Start

```python
import scviva

# Preprocess: compute spatial neighbors
scviva.SCVIVA.preprocessing_anndata(adata, k_nn=6)

# Setup and train
scviva.SCVIVA.setup_anndata(adata, layer="counts", batch_key="batch")
model = scviva.SCVIVA(adata)
model.train()

# Get latent representation
latent = model.get_latent_representation()
```
