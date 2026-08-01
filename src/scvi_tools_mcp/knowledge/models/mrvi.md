# MRVI — API Reference

**Class:** `scvi.external.mrvi._model.MRVI`

**Signature:** `MRVI(adata: 'AnnData | None' = None, registry: 'dict | None' = None, **model_kwargs)`

## Docstring

Multi-resolution Variational Inference (MrVI) :cite:p:`Boyeau24`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.external.MRVI.setup_anndata`.
n_latent
    Dimensionality of the latent space for ``z``.
n_latent_u
    Dimensionality of the latent space for ``u``.
encoder_n_hidden
    Number of nodes per hidden layer in the encoder.
encoder_n_layers
    Number of hidden layers in the encoder.
z_u_prior
    Whether to use a prior for ``z_u``.
z_u_prior_scale
    Scale of the prior for the difference between ``z`` and ``u``.
u_prior_scale
    Scale of the prior for ``u``.
u_prior_mixture
    Whether to use a mixture model for the ``u`` prior.
u_prior_mixture_k
    Number of components in the mixture model for the ``u`` prior.
learn_z_u_prior_scale
    Whether to learn the scale of the ``z`` and ``u`` difference prior during training.
laplace_scale
    Scale parameter for the Laplace distribution in the decoder.
scale_observations
    Whether to scale loss by the number of observations per sample.
px_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.DecoderZXAttention`.
qz_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.EncoderUZ`.
qu_kwargs
    Keyword args for :class:`~scvi.external.mrvi._module.EncoderXU`.

Notes
-----
This implementation of MRVI is in PyTorch.
This will become the default version in v1.4.3 for MRVI.
The JAX version is deprecated starting v1.5.

See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/scrna/MrVI_tutorial_torch`

See the user guide for this model:

1. :doc:`/user_guide/models/mrvi`

See Also
--------
:class:`~scvi.external.mrvi.MRVAE`

## setup_anndata

```python
MRVI.setup_anndata(adata: 'AnnData', layer: 'str | None' = None, sample_key: 'str | None' = None, batch_key: 'str | None' = None, labels_key: 'str | None' = None, **kwargs)
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
sample_key
    key in `adata.obs` for sample information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_sample']`. If `None`, assigns the same sample
    to all the data.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
**kwargs
    Additional keyword arguments passed into
    :meth:`~scvi.data.AnnDataManager.register_fields`.

## train

```python
MRVI.train(self, max_epochs: 'int | None' = None, accelerator: 'str | None' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, batch_size: 'int' = 128, early_stopping: 'bool' = False, plan_kwargs: 'dict | None' = None, datamodule=None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Maximum number of epochs to train the model. The actual number of epochs may be less if
    early stopping is enabled. If ``None``, defaults to a heuristic based on
    :func:`~scvi.model.get_max_epochs_heuristic`.
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
    Size of the training set in the range ``[0.0, 1.0]``.
validation_size
    Size of the validation set. If ``None``, defaults to ``1 - train_size``. If
    ``train_size + validation_size < 1``, the remaining cells belong to a test set.
batch_size
    Minibatch size to use during training.
early_stopping
    Perform early stopping. Additional arguments can be passed in through ``**kwargs``.
    See :class:`~scvi.train.Trainer` for further options.
plan_kwargs
    Additional keyword arguments passed into :class:`~scvi.train.TrainingPlan`.
datamodule
    ``EXPERIMENTAL`` A :class:`~lightning.pytorch.core.LightningDataModule` instance to use
    for training in place of the default :class:`~scvi.dataloaders.DataSplitter`.
**trainer_kwargs
    Additional keyword arguments passed into :class:`~scvi.train.Trainer`.


---

## User Guide

# MrVI

**MrVI** {cite:p}`Boyeau24` (Multi-resolution Variational Inference; Python class
{class}`~scvi.external.MRVI`) is a deep generative model designed for the analysis of large-scale
single-cell transcriptomics data with multi-sample, multi-batch experimental designs.

MrVI conducts both **exploratory analyses** (locally dividing samples into groups based on molecular properties)
and **comparative analyses** (comparing pre-defined groups of samples in terms of differential expression and differential abundance) at single-cell resolution.
It can capture nonlinear and cell-type-specific variation of sample-level covariates on gene expression.

```{topic} Tutorials:

-    {doc}`/tutorials/notebooks/scrna/MrVI_tutorial`
```

## Preliminaries

MrVI takes as input a scRNA-seq gene expression matrix $X$ with $N$ cells and $G$ genes.
Additionally, it requires specification, for each cell $n$:
- a sample-level target covariate $s_n$, that typically corresponds to the sample ID,
	which defines which sample entities will be compared in exploratory and comparative analyses.
- nuisance covariates $b_n$ (e.g. sequencing run, processing day).

Optionally, MrVI can also take as input
	- Cell-type labels for guided integration across samples, via a mixture of Gaussians prior where each mixture component serves as the mode of a cell type.
	- Additional sample-level covariates of interest $c_s$ for each sample $s$ (e.g.,
	  disease status, age, treatment) for comparative analysis.

## Generative process

MrVI posits a two-level hierarchical model (Figure 1):

1. A cell-level latent variable $u_n$ capturing cell state in a batch-corrected manner:
    $u_n \sim \mathrm{MixtureOfGaussians}(\mu_1, ..., \mu_K, \Sigma_1, ..., \Sigma_K, \pi_1, ..., \pi_K)$
2. A cell-level latent variable $z_n$ capturing both cell state and effects of sample $s_n$:
    $z_n | u_n \sim \mathcal{N}(u_n, I_L)$
3. The normalized gene expression levels $h_n$ are generated from $z_n$ as:
    $h_n = \mathrm{softmax}(A_{zh} \times [z_n + g_\theta(z_n, b_n)] + \gamma_{zh})$
4. Finally, the gene expression counts are generated as:
    $x_{ng} | h_{ng} \sim \mathrm{NegativeBinomial}(l_n h_{ng}, r_{ng})$

Here $l_n$ is the library size of cell $n$, $r_{ng}$ is the gene-specific inverse dispersion,
$A_{zh}$ is a linear matrix of dimension $G \times L$, $\gamma_{zh}$ is a bias vector of dimension
$G$, and $\theta$ are neural network parameters.
$u_n$ captures broad cell states invariant to sample and batch,
while $z_n$ augments $u_n$ with sample-specific effects while correcting for nuisance covariate effects.
Gene expression is obtained from $z_n$ using multi-head attention mechanisms to
    flexibly model batch and sample effects.

:::{figure} figures/mrvi_graphical_model.svg
:align: center
:alt: MrVI graphical model
:class: img-fluid

MrVI graphical model. Shaded nodes represent observed data, unshaded nodes represent latent variables.
:::

The latent variables, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`u_n \in \mathbb{R}^L`
     - "sample-unaware" representation of a cell, invariant to both sample and nuisance covariates.
     - ``u``
   * - :math:`z_n \in \mathbb{R}^L`
     - "sample-aware" representation of a cell, invariant to nuisance covariates.
     - ``z``
   * - :math:`h_n \in \mathbb{R}^G`
     - Cell-specific normalized gene expression.
     - ``h``
   * - :math:`l_n \in \mathbb{R}^+`
     - Cell size factor.
     - ``library``
   * - :math:`r_{ng} \in \mathbb{R}^+`
     - Gene and cell-specific inverse dispersion.
     - ``px_r``
   * - :math:`\mu_1, ..., \mu_K \in \mathbb{R}^L`
     - Mixture of Gaussians means for prior on $u_n$.
     - ``u_prior_means``
   * - :math:`\Sigma_1, ..., \Sigma_K \in \mathbb{R}^{L \times L}`
     - Mixture of Gaussians covariance matrices for prior on $u_n$.
     - ``u_prior_scales``
   * - :math:`\pi_1, ..., \pi_K \in \mathbb{R}^+`
     - Mixture of Gaussians weights for prior on $u_n$.
     - ``u_prior_logits``
```

## Inference

MrVI uses variational inference to approximate the posterior of $u_n$ and $z_n$. The variational
distributions are:

$q_{\phi}(u_n | x_n) := \mathcal{N}(\mu_{\phi}(x_n), \sigma^2_{\phi}(x_n)I)$

$z_n := u_n + f_{\phi}(u_n, s_n)$

Here $\mu_{\phi}, \sigma^2_{\phi}$ are encoder neural networks and $f_{\phi}$ is a deterministic
mapping based on multi-head attention between $u_n$ and a learned embedding for sample $s_n$.

## Tasks

### Exploratory analysis

MrVI enables unsupervised local sample stratification via the construction of cell-specific
sample-sample distance matrices, for every cell $n$:

1. For each cell state $u_n$, compute counterfactual cell states $z^{(s)}_n$ for all possible samples $s$.
2. Compute cell-specific sample-sample distance matrices $D^{(n)}$ based on the Euclidean distance between all pairs of $z^{(s)}_n$.
3. Cluster cells based on their $D^{(n)}$ to find cell populations with distinct sample stratification.
4. Average $D^{(n)}$ within each cell cluster and hierarchically cluster samples
This automatically reveals distinct sample stratification that are specific to particular cell
subsets.

### Comparative analysis
MrVI also enables supervised comparative analysis to detect cell-type-specific DE and DA between sample groups.

#### Differential expression
At a high level, the DE procedure regresses, within each cell $n$, counterfactual cell states $z^{(s)}_n$ on sample-level covariates $c_s$ of interest for analysis as
$z^{(s)}_n = \beta_n c_s + \beta_0 + \epsilon_n$.
For instance, if $c_s$ is a binary covariate, then $\beta_n$ will capture the shift (in $z$-space) induced by samples for which $c_s = 1$ compared to samples for which $c_s = 0$.
This procedure, repeated for all cells, allows several downstream analyses.
First, comparing the norm of $\beta_n$ (using $\chi^2$ statistics) across cells can identify cell-states that vary the most for a given covariate, or conversely, identify sample covariates that strongly associate with specific cell states.
Second, by decoding the linear approximation of $z^{(s)}_n$ for different covariate vectors that we would like to compare, we can compute associated log fold-changes to identify the genes at the cell level.

#### Differential abundance
To compare two sets of samples, MrVI computes the log-ratio between the aggregated posteriors of the two groups, $A_1 \subset [[1, S]]$ and $A_2 \subset [[1, S]]$, where $S$ is the total number of samples.
In particular, the aggregated posterior for any sample $s$ is defined as
$q_s := \frac{1}{|s|} \sum_{n, s_n=s} q^{u}_{n}$,
where $q_n$ is the posterior of cell $n$ in $u$-space.
This aggregated posterior $q_s$ characterizes the distribution of all cells in sample $s$.
To characterize the distribution of cells in a group of samples $A$, we can consider the mixture of aggregated posteriors $q_s$ for all $s \in A$, corresponding to
$q_A := \frac{1}{|A|} \sum_{s \in A} q_s$.
In particular, cell states $u$ that are abundant in a sample group $A$ will have a high probability mass in $q_A$, while rare states will have low probability mass.
More generally, we can consider the log-ratio of aggregated posteriors between two groups of samples $A_1$ and $A_2$ as a measure of differential abundance:
$r = \log \frac{q_{A_1}}{q_{A_2}}$.
We can evaluate these log-ratios for all cell states $u$ to identify DA cell-state regions.
In particular, large positive (resp. negative) values of $r$ indicate that cell states are more abundant in $A_1$ (resp. $A_2$).
