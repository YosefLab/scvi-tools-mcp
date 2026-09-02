# DESTVI — API Reference

**Class:** `scviva.model._destvi.DestVI`

**Signature:** `DestVI(st_adata: 'AnnData', cell_type_mapping: 'np.ndarray', decoder_state_dict: 'OrderedDict', px_decoder_state_dict: 'OrderedDict', px_r: 'torch.tensor', per_ct_bias: 'torch.tensor', n_hidden: 'int', n_latent: 'int', n_layers: 'int', dropout_decoder: 'float', **module_kwargs)`

## Docstring

Multi-resolution deconvolution of Spatial Transcriptomics data (DestVI) :cite:p:`Lopez22`.

Most users will use the alternate constructor (see example).

Parameters
----------
st_adata
    spatial transcriptomics AnnData object that has been registered via
    :meth:`~scviva.model.DestVI.setup_anndata`.
cell_type_mapping
    mapping between numerals and cell type labels
decoder_state_dict
    state_dict from the decoder of the CondSCVI model
px_decoder_state_dict
    state_dict from the px_decoder of the CondSCVI model
px_r
    parameters for the px_r tensor in the CondSCVI model
n_hidden
    Number of nodes per hidden layer.
n_latent
    Dimensionality of the latent space.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
**module_kwargs
    Keyword args for :class:`~scviva.module.MRDeconv`

Examples
--------
>>> sc_adata = anndata.read_h5ad(path_to_scRNA_anndata)
>>> scvi.model.CondSCVI.setup_anndata(sc_adata)
>>> sc_model = scvi.model.CondSCVI(sc_adata)
>>> st_adata = anndata.read_h5ad(path_to_ST_anndata)
>>> DestVI.setup_anndata(st_adata)
>>> spatial_model = DestVI.from_rna_model(st_adata, sc_model)
>>> spatial_model.train(max_epochs=2000)
>>> st_adata.obsm["proportions"] = spatial_model.get_proportions(st_adata)
>>> gamma = spatial_model.get_gamma(st_adata)

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/spatial/DestVI_tutorial`
2. :doc:`/tutorials/notebooks/r/DestVI_in_R`

## setup_anndata

```python
DestVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, smoothed_layer: 'str | None' = None, batch_key: 'str | None' = None, **kwargs)
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
smoothed_layer
    When provided, the model adds a spatial-smoothing regularization that encourages a
    spot's inferred cell-type proportions to agree with those inferred from its
    neighborhood, yielding spatially smoother deconvolution.
    Optional; if ``None`` the regularization is disabled.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.

## train

```python
DestVI.train(self, max_epochs: 'int' = 2000, lr: 'float' = 0.003, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float' = 1.0, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, n_epochs_kl_warmup: 'int' = 200, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
```

Trains the model using MAP inference.

Parameters
----------
max_epochs
    Number of epochs to train for
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
n_epochs_kl_warmup
    number of epochs needed to reach unit kl weight in the elbo
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.


---

## User Guide

# DestVI

**DestVI** {cite:p}`Lopez22` (Deconvolution of Spatial Transcriptomics profiles using Variational Inference)
posits a conditional generative model of spatial transcriptomics down to the sub-cell-type variation level which
can be used to explore the spatial organization of a tissue and understanding gene expression variation between tissues and conditions.

The advantages of DestVI are:

-   Can stratify cells into discrete cell types and model continuous sub-cell-type variation.
-   Scalable to very large datasets (>1 million cells).

The limitations of DestVI include:

-   Effectively requires a GPU for fast inference.

```{topic} Tutorial:

-   {doc}`/tutorials/DestVI_tutorial`
```

## Preliminaries

DestVI requires training two models, the scLVM (single-cell latent variable model) and the
stLVM (spatial transcriptomic latent variable model). The scLVM takes in as input a scRNA-seq gene
expression matrix of UMI counts $X$ with $N$ cells and $G$ genes, along with
a vector of cell type labels $\vec{c}$. Subsequently, the stLVM takes in the trained scLVM,
along a spatial gene expression matrix $Y$ with $S$ spots and $G$ genes.
Optionally, the user can specify the number of components used for the mixture model underlying the
empirical prior.

## Generative process

### scLVM

For cell $n$, the scLVM assumes observed discrete cell type labels $c_n$ and models
continuous covariates $\gamma_n$ of dimension $d$ to explain variation in gene expression within a cell type.
The scLVM posits that the observed UMI counts for cell $n$ are generated by the following process:

```{math}
:nowrap: true

\begin{align}
    \gamma_n &\sim \textrm{Normal}(0, I) \tag{1} \\
    x_{ng} &\sim \textrm{NegativeBinomial}(l_nf^g(c_n, \gamma_n), p_g) \tag{2} \\
\end{align}
```

where $l_n$ is the library size, $f$ is a two-layer neural network which outputs a $G$
dimensional vector, and $p_g$ is the rate parameter of the negative binomial distribution for
a given gene $g$.

:::{note}
We are using the standard rate-shape parametrization of the negative binomial here, rather than the mean-dispersion
parametrization used in scVI. This is to take advantage of the additive property of
negative binomial distributions sharing the same shape parameter. In this case, the rate parameter for the
negative binomial modeling the expression counts for a given gene and spot is equivalent to the sum of the rate
parameters for each contributing cell.
:::

The latent variables for the scLVM, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`\gamma_n \in \mathbb{R}^d`
     - Low-dimensional representation of sub-cell-type covariates.
     - ``z``
   * - :math:`p_g \in (0, \infty)`
     - Rate parameter for the negative binomial distribution.
     - ``px_r``
```

### stLVM

For the stLVM, we also model the expression counts with a $\mathrm{NegativeBinomial}$. However,
for spatial data, we assume that each spot $s$ has expression $x_s$ composed of a bulk of cell types, with
cell type abundance, $\beta_{sc}$, for each cell type $c$. We assume that for a given spot $s$
and gene $g$, the observation is generated as a function of the latent variables $(c, \gamma_s^c)$ by the following process:

```{math}
:nowrap: true

\begin{align}
    \gamma_x^c &\sim \sum_{k=1}^K m_{kc} q_\Phi(\gamma^c \mid u_{kc}, c) \tag{4} \\
    x_{sg} &\sim \mathrm{NegativeBinomial}(l_s\alpha_g\sum_{c=1}^{C}\beta_{sc}f^g(c, \gamma_s^c), p_g) \tag{5} \\
\end{align}
```

Where $l_s$ is the library size and $\alpha_g$ is a correction term for
difference in experimental assays. Like the scLVM, $f$ is a decoder neural network, and
$p_g$ is the rate parameter for the negative binomial distribution.

To avoid the latent variable $\gamma_s^c$ from incorporating variation attributed to experimental
assay differences, we assign an empirical prior informed by the scLVM and the corresponding
cells of the same cell type in the scRNA-seq dataset. To compute this function, we cluster the latent space of the
scLVM for each cell type to K cell-type-specific clusters. For each cluster we compute an empirical mean and variance.
Above, $\{u_{kc}\}_{k=1}^K$ designates the set of cell-type-specific subclusters from cell type $c$ in the scRNA-seq dataset, and
$q_\Phi$ designates the empirical normal distribution from the computed cluster mean and variance.
The loss is weighted by the probability of a random cell from this cell type to be in the respective cluster in the
scRNA-seq dataset (mixture probability, $m_{kc}$).
In literature, the prior is referred to as a VampPrior ("variational aggregated mixture of posteriors" prior) [^ref2].

The latent variables for the stLVM, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`\beta_{sc} \in (0, \infty)`
     - Spot-specific cell type abundance.
     - ``v_ind``
   * - :math:`\gamma_s^c \in (-\infty, \infty)`
     - Low-dimensional representation of sub-cell-type covariates for a given spot and cell type.
     - ``gamma``
   * - :math:`\eta_g \in (0, \infty)`
     - Gene-specific noise.
     - ``eta``
   * - :math:`\alpha_g \in (0, \infty)`
     - Correction term for technological differences.
     - ``beta``
   * - :math:`p_g \in (0,\infty)`
     - Rate parameter for the negative binomial distribution.
     - ``px_o``

```

## Inference

### scLVM

DestVI uses variational inference and specifically auto-encoding variational bayes to learn both the model parameters
(the neural network params, rate params, etc.) and an approximate posterior distribution for the scLVM.

### stLVM

For the stLVM, DestVI infers point estimates for latent variables $\gamma^c, \alpha, \beta$ using a penalized
likelihood method. Beyond vanilla MAP inference, to regularize $\alpha$ a variance penalty is applied across all genes.

The loss is defined as:

```{math}
:nowrap: true

\begin{align}
     L(l, \alpha, \beta, f^g, \gamma, p, \eta) := &-\log p(X \mid l, \alpha, \beta, f^g, \gamma, p, \eta) - \lambda_{\eta} \log p(\eta) \\
     &+ \lambda_{\alpha} \mathrm{Var}(\alpha) - \log p(\gamma \mid \mathrm{VampPrior}) + \lambda_{\beta} \lVert \beta_{sc} \rVert_1  \tag{6} \\
\end{align}
```

Where $\mathrm{Var}(\alpha)$ refers to the empirical variance of the parameters alpha across all genes.

$\lambda_{\beta}$ (`l1_reg` in code), $\lambda_{\eta}$ (`eta_reg` in code) and $\lambda_{\alpha}$ (`beta_reg` in code) are hyperparameters used to scale the loss term.

## Tasks

### Cell type deconvolution

Once the model is trained, one can retrieve the estimated cell type proportions in each spot using the method:

```
>>> proportions = st_model.get_proportions()
>>> st_adata.obsm["proportions"] = proportions
```

These proportions are computed by normalizing across all learned cell type abundances, $\beta_{sc}$, for a given spot $s$.

Subsequently for a given cell type, users can plot a heatmap of the cell type proportions spatially using scanpy with:

```
>>> import scanpy as sc
>>> st_adata.obs['B cells'] = st_adata.obsm['proportions']['B cells']
>>> sc.pl.spatial(st_adata, color="B cells", spot_size=130)
```

### Intra cell type variation

Users can retrieve the values of $\gamma$, the latent variables corresponding to the
modeled cell-type-specific continuous covariates with:

```
>>> gamma = st_model.get_gamma()["B cells"]
>>> st_adata.obsm["B_cells_gamma"] = gamma
```

### Cell-type-specific gene expression imputation

Assuming the user has identified key gene modules that vary within a cell type of interest, they can
impute the spatial pattern of the cell-type-specific gene expression with:

```
>>> # Filter spots with low abundance.
>>> indices = np.where(st_adata.obsm["proportions"][ct_name].values > 0.03)[0]
>>> imputed_counts = st_model.get_scale_for_ct("Monocyte", indices=indices)[["Cxcl9", "Cxcl10", "Fcgr1"]]
```

## New DestVI

The version is scVIVA-Tools is an upgraded version of DestVI compared to what we had in scvi-tools.

Main Additions of new version:

- Batch embedding for correction in condSCVI.
- MoG (Mixture-of-Gaussians) in CondSCVI instead of posterior Visa Acquirer Monitoring Program (VAMP) estimation.
- Option to use a more coarse spatial layer and let the coarse one inform the fine deconvolution (Curio sometimes has very few counts and then it's hard to do deconvolution)
- mixture of sc and spatial data in DestVI to guide deconvolution (analogue to https://pubmed.ncbi.nlm.nih.gov/38689377/)

## Quick Start

```python
import scvi
import scviva

# Step 1: Train CondSCVI reference on scRNA-seq
scvi.model.CondSCVI.setup_anndata(sc_adata, labels_key="cell_type", layer="counts")
sc_model = scvi.model.CondSCVI(sc_adata)
sc_model.train()

# Step 2: Deconvolve spatial spots
scviva.DestVI.setup_anndata(st_adata, layer="counts")
st_model = scviva.DestVI.from_rna_model(st_adata, sc_model)
st_model.train()

# Step 3: Get cell type proportions
proportions = st_model.get_proportions()
```

[^ref2]: Jakub Tomczak, Max Welling (2018),_VAE with a VampPrior_, [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v84/tomczak18a.html)
