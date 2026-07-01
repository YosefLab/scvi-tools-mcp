# STEREOSCOPE — API Reference

**Class:** `scvi.external.stereoscope._model.RNAStereoscope`

**Signature:** `RNAStereoscope(sc_adata: 'AnnData', **model_kwargs)`

## Docstring

Reimplementation of Stereoscope :cite:p:`Andersson20`.

Deconvolution of spatial transcriptomics from single-cell transcriptomics. Original
implementation: https://github.com/almaan/stereoscope.

Parameters
----------
sc_adata
    single-cell AnnData object that has been registered via
    :meth:`~scvi.external.RNAStereoscope.setup_anndata`.
**model_kwargs
    Keyword args for :class:`~scvi.external.stereoscope.RNADeconv`

Examples
--------
>>> sc_adata = anndata.read_h5ad(path_to_sc_anndata)
>>> scvi.external.RNAStereoscope.setup_anndata(sc_adata, labels_key="labels")
>>> stereo = scvi.external.stereoscope.RNAStereoscope(sc_adata)
>>> stereo.train()

Notes
-----
See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/spatial/stereoscope_heart_LV_tutorial`

## setup_anndata

```python
RNAStereoscope.setup_anndata(adata: 'AnnData', labels_key: 'str | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.

## train

```python
RNAStereoscope.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float' = 1, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, **kwargs)
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
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.


---

## User Guide

# Stereoscope

**Stereoscope** {cite:p}`Andersson20` (Python classes {class}`~scvi.external.RNAStereoscope` and {class}`~scvi.external.SpatialStereoscope`) posits a probabilistic model of spatial transcriptomics and an associated
method for the deconvoluton of cell type profiles using a single-cell RNA sequencing reference dataset.

The advantages of Stereoscope are:

-   Can stratify cells into discrete cell types.
-   Scalable to very large datasets (>1 million cells).

The limitations of Stereoscope include:

-   Effectively requires a GPU for fast inference.

:::{note}
Starting scVI-Tools v1.5 this model is part of scVIVA-Tools, and no longer being maintained here.
:::

```{topic} Tutorial:

-   {doc}`/tutorials/notebooks/spatial/stereoscope_heart_LV_tutorial`
```

## Preliminaries

Stereoscope requires training two latent variable models (LVMs): one for the single-cell reference
dataset and one for the spatial transcriptomics dataset, which incorporates the learned parameters of the
single-cell reference LVM. The first LVM takes in as input a scRNA-seq gene expression matrix of UMI counts
$Y$ with $N$ cells and $G$ genes, along with a vector of cell type labels $\vec{z}$.
Subsequently, the second LVM takes in the learned parameters of the first LVM, along with a spatial gene
expression matrix $X$ with $S$ spots and $G$ genes.

## Generative process

### Single-cell reference LVM

For cell $c$, the LVM assumes an observed discrete cell type label $z_c$ and models
the UMI count observation for a given gene $g$ as a negative binomial distribution. This LVM posits that the observed
UMI counts for cell $c$ and gene $g$ are generated by the following process:

```{math}
:nowrap: true

\begin{align}
    y_{gc} &\sim \textrm{NegativeBinomial}(s_{c}r_{gz}, p_{g}) \tag{1} \\
\end{align}
```

where $s_c = \sum_{g\in G} y_{gc}$ is the observed library size of the cell,
$r_{gz}$ is the latent rate parameter for the cell type $z_c$ and gene $g$,
and $p_g$ is the latent variable representing the success probability for gene $g$.

:::{note}
We are using the standard rate-shape parametrization of the negative binomial here, rather than the mean-dispersion
parametrization used in {doc}`/user_guide/models/scvi`. This is to take advantage of the additive property of
negative binomial distributions sharing the same shape parameter. In this case, the rate parameter for the
negative binomial modeling the expression counts for a given gene and spot is equivalent to the sum of the rate
parameters for each contributing cell.
:::

This generative process is also summarized in the following graphical model:

:::{figure} figures/stsc_scLVM_graphical_model.svg
:align: center
:alt: single-cell reference LVM graphical model
:class: img-fluid

single-cell reference LVM graphical model.
:::

The latent variables for the single-cell reference LVM, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`r_{gz} \in (0, \infty)`
     - Rate parameter for the negative binomial distribution.
     - ``px_scale``
   * - :math:`p_g \in [0, 1]`
     - Shape parameter for the negative binomial distribution.
     - ``px_o`` :math:`:= \log \left( \frac{p_g}{1 - p_g} \right)`
```

### Spatial transcriptomics LVM

For the second LVM, we also model the expression counts with a $\mathrm{NegativeBinomial}$. However,
for spatial data, we assume that each spot $s$ has expression $x_s$ composed of a bulk of cell types, with
cell type abundance, $v_{sz}$, for each cell type $z$. We assume that for a given spot $s$ and gene $g$,
the observation is generated by the following process:

```{math}
:nowrap: true

\begin{align}
    x_{sg} &\sim \mathrm{NegativeBinomial}(\beta_g\sum_{z\in Z}v_{sz}r_{gz}, p_g) \tag{2} \\
\end{align}
```

where $\beta_g$ is a gene-specific correction term for technical differences.
The parameters $r_{gz}$ and $p_g$ are the learned parameters from the first LVM.

An additional latent variable, $\eta_g$, is incorporated into the aggregated cell expression profile
as a dummy cell type to represent gene-specific noise. The dummy cell type's expression profile is distributed
as $\varepsilon_g := \mathrm{Softplus}(\eta_g)$ where $\eta_g \sim \mathrm{Normal}(0, 1)$ to avoid the model
from incorrectly assigning explanatory power to this term.
Like the other cell types, there is an associated cell type abundance parameter $\gamma_s$ associated with $\varepsilon$.

This generative process is also summarized in the following graphical model:

:::{figure} figures/stsc_stLVM_graphical_model.svg
:align: center
:alt: spatial transcriptomics LVM graphical model
:class: img-fluid

spatial transcriptomics LVM graphical model.
:::

The latent variables for the spatial transcriptomics LVM, along with their description, are summarized in the following table:

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`v_{sz} \in (0, \infty)`
     - Spot-specific cell type abundance. The code variable ``v_ind`` also incorporates the
       the abundance term, :math:`\gamma_s` for the dummy noise cell type, :math:`\varepsilon`.
     - ``v_ind``
   * - :math:`\eta_g \in (-\infty, \infty)`
     - Gene-specific noise. Incorporated into the model as :math:`\varepsilon_g := \mathrm{Softplus}(\eta_g)`.
     - ``eta``
   * - :math:`\beta_g \in (0, \infty)`
     - Correction term for technological differences.
     - ``beta``
   * - :math:`r_{gz} \in (0, \infty)`
     - Rate parameter for the negative binomial distribution shared from the single-cell reference LVM.
     - ``w``
   * - :math:`p_g \in [0,1]`
     - Shape parameter for the negative binomial distribution shared from the single-cell reference LVM.
     - ``px_o`` :math:`:= \log \left( \frac{p_g}{1 - p_g} \right)`

```

## Inference

### Single-cell reference LVM

Stereoscope uses maximum likelihood estimation to estimate the parameters of the first LVM w.r.t. The negative binomial model of
UMI observations. This is achieved via stochastic gradient ascent on the likelihood function using the Pytorch framework.

### Spatial transcriptomics LVM

For the spatial transcriptomics LVM, Stereoscope uses MAP inference to estimate the parameters specific to the model. To be exact,
the only parameter given a non-uniform prior is $\eta_g$ that is posited as a gene-specific random effect distributed by a standard
Normal prior. Note, the $r_{gz}$ and $p_g$ parameters are not inferred in this step, but held fixed as the parameters shared by the
single-cell reference LVM.

## Tasks

### Cell type deconvolution

Once the model is trained, one can retrieve the estimated cell type proportions in each spot using the method:

```
>>> proportions = spatial_model.get_proportions()
>>> st_adata.obsm["proportions"] = proportions
```

These proportions are computed by normalizing across all learned cell type abundances, $v_{sz}$, for a given spot $s$.
I.e., the estimated proportion of cell type $z$ for spot $s$ is $\frac{v_{sz}}{\sum_{z'} v_{sz'}}$.

Subsequently, for a given cell type, users can plot a heatmap of the cell type proportions spatially using scanpy with:

```
>>> import scanpy as sc
>>> sc.p1.embedding(st_adata, basis="location", color="B cells")
```
