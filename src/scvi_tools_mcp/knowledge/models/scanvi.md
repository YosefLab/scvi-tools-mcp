# SCANVI — API Reference

**Class:** `scvi.model._scanvi.SCANVI`

**Signature:** `SCANVI(adata: 'AnnData | None' = None, registry: 'dict | None' = None, n_hidden: 'int' = 128, n_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, dispersion: "Literal['gene', 'gene-batch', 'gene-label', 'gene-cell']" = 'gene', gene_likelihood: "Literal['zinb', 'nb', 'poisson']" = 'zinb', use_observed_lib_size: 'bool' = True, linear_classifier: 'bool' = False, datamodule: 'LightningDataModule | None' = None, **model_kwargs)`

## Docstring

Single-cell annotation using variational inference :cite:p:`Xu21`.

Inspired from M1 + M2 model, as described in (https://arxiv.org/pdf/1406.5298.pdf).

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.model.SCANVI.setup_anndata`.
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
use_observed_lib_size
    If ``True``, use the observed library size for RNA as the scaling factor in the mean of the
    conditional distribution.
linear_classifier
    If ``True``, uses a single linear layer for classification instead of a
    multi-layer perceptron.
**model_kwargs
    Keyword args for :class:`~scvi.module.SCANVAE`

Examples
--------
>>> adata = anndata.read_h5ad(path_to_anndata)
>>> scvi.model.SCANVI.setup_anndata(adata, batch_key="batch", labels_key="labels")
>>> vae = scvi.model.SCANVI(adata, "Unknown")
>>> vae.train()
>>> adata.obsm["X_scVI"] = vae.get_latent_representation()
>>> adata.obs["pred_label"] = vae.predict()

Notes
-----
See further usage examples in the following tutorials:

1. :doc:`/tutorials/notebooks/scrna/harmonization`
2. :doc:`/tutorials/notebooks/multimodal/scarches_scvi_tools`
3. :doc:`/tutorials/notebooks/scrna/seed_labeling`

## setup_anndata

```python
SCANVI.setup_anndata(adata: 'AnnData', labels_key: 'str', unlabeled_category: 'str', layer: 'str | None' = None, batch_key: 'str | None' = None, size_factor_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, use_minified: 'bool' = True, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
labels_key
    key in `adata.obs` for label information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_labels']`. If `None`, assigns the same label
    to all the data.
unlabeled_category
    value in `adata.obs[labels_key]` that indicates unlabeled observations.
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
use_minified
    If True, will register the minified version of the adata if possible.

## train

```python
SCANVI.train(self, max_epochs: 'int | None' = None, n_samples_per_label: 'float | None' = None, check_val_every_n_epoch: 'int | None' = None, train_size: 'float' = 0.9, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 128, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', adversarial_classifier: 'bool | None' = None, datasplitter_kwargs: 'dict | None' = None, plan_config: 'KwargsLike | None' = None, plan_kwargs: 'KwargsLike | None' = None, datamodule: 'LightningDataModule | None' = None, trainer_config: 'KwargsLike | None' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Number of passes through the dataset for semisupervised training.
n_samples_per_label
    Number of subsamples for each label class to sample per epoch. By default, there
    is no label subsampling.
check_val_every_n_epoch
    Frequency with which metrics are computed on the data for the validation set for both
    the unsupervised and semisupervised trainers. If you'd like a different frequency for
    the semisupervised trainer, set check_val_every_n_epoch in semisupervised_train_kwargs.
train_size
    Size of the training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train,
    and test set are split in the sequential order of the data according to
    `validation_size` and `train_size` percentages.
batch_size
    Minibatch size to use during training.
accelerator
    Supports passing different accelerator types `("cpu", "gpu", "tpu", "ipu", "hpu",
    "mps, "auto")` as well as custom accelerator instances.
devices
    The devices to use. Can be set to a non-negative index (`int` or `str`), a sequence
    of device indices (`list` or comma-separated `str`), the value `-1` to indicate all
    available devices, or `"auto"` for automatic selection based on the chosen
    `accelerator`. If set to `"auto"` and `accelerator` is not determined to be `"cpu"`,
    then `devices` will be set to the first available device.
adversarial_classifier
    Whether to use adversarial classifier in the latent space. This helps mixing when
    there are missing proteins in any of the batches. Defaults to `True` is missing
    proteins are detected.
datasplitter_kwargs
    Additional keyword arguments passed into
    :class:`~scvi.dataloaders.SemiSupervisedDataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.SemiSupervisedTrainingPlan`. Keyword
    arguments passed to `train()` will overwrite values present in `plan_kwargs`,
    when appropriate.
plan_config
    Configuration object or mapping used to build
    :class:`~scvi.train.SemiSupervisedTrainingPlan`. Values in ``plan_kwargs`` and
    explicit arguments take precedence.
datamodule
    ``EXPERIMENTAL`` A :class:`~lightning.pytorch.core.LightningDataModule` instance to use
    for training in place of the default :class:`~scvi.dataloaders.DataSplitter`. Can only
    be passed in if the model was not initialized with :class:`~anndata.AnnData`.
trainer_config
    Configuration object or mapping used to build :class:`~scvi.train.Trainer`. Values in
    ``trainer_kwargs`` and explicit arguments take precedence.
**trainer_kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.


---

## User Guide

# scANVI

**scANVI** {cite:p}`Xu21` (single-cell ANnotation using Variational Inference; Python class {class}`~scvi.model.SCANVI`) is a semi-supervised model for single-cell transcriptomics data.
In a sense, it can be seen as a scVI extension that can leverage the cell type knowledge for a subset of the cells present in the data sets to infer the states of the rest of the cells.
For this reason, scANVI can help annotate a data set of unlabelled cells from manually annotated atlases, e.g., Tabula Sapiens [^refts].

The advantages of scANVI are:

-   Comprehensive in capabilities.
-   Scalable to very large datasets (>1 million cells).

The limitations of scANVI include:

-   Effectively requires a GPU for fast inference.
-   Latent space is not interpretable, unlike that of a linear method.
-   May not scale to a very large number of cell types.

```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/scrna/harmonization`
-   {doc}`/tutorials/notebooks/multimodal/scarches_scvi_tools`
```

## Preliminaries

scANVI takes as input a scRNA-seq gene expression matrix $X$ with $N$ cells and $G$ genes,
as well as a vector $\mathbf{c}$ containing the partially observed cell type annotations.
Let $C$ be the number of observed cell types in the data.
Additionally, a design matrix $S$ containing $p$ observed covariates, such as day, donor, etc., is an optional input.
While $S$ can include both categorical covariates and continuous covariates, in the following, we assume it contains only one
categorical covariate with $K$ categories, which represents the common case of having multiple batches of data.

## Generative process

scANVI extends the scVI model by making use of observed cell types $c_n$ following a
graphical model inspired by works on semi-supervised VAEs [^ref2].

```{math}
:nowrap: true

\begin{align}
 c_n &\sim \mathrm{Categorical}(1/C, ..., 1/C) \\
 u_n &\sim \mathcal{N}(0, I) \\
 z_n &\sim \mathcal{N}(f_z^\mu(c_n, u_n), f_z^\sigma(c_n, u_n) \odot I) \\
 \ell_n &\sim \mathrm{LogNormal}\left( \ell_\mu^\top s_n ,\ell_{\sigma^2}^\top s_n \right) \\
 \rho _n &= f_w\left( z_n, s_n \right) \\
 \pi_{ng} &= f_h^g(z_n, s_n) \\
 x_{ng} &\sim \mathrm{ObservationModel}(\ell_n \rho_n, \theta_g, \pi_{ng})
 \end{align}
```

We assume no knowledge over the distribution of cell types in the data (i.e.,
uniform probabilities for categorical distribution on $c_n$).
This modeling choice helps ensure a proper handling of rare cell types in the data.
We assume that the within-cell-type characterization of the cell follows a Normal distribution, s.t. $u_n \sim \mathcal{N}(0, I_d)$.
The distribution over the random vector $z_n$ contains learnable parameters in the form of
the neural networks $f_z^\mu$, $f_z^\sigma$. Qualitatively, $z_n$ characterizes each cell
cellular state as a continuous, low-dimensional random variable and has the same interpretation as in the scVI model.
However, the prior for this variable takes into account the partial cell-type information to better structure the latent space.

The rest of the model closely follows scVI. In particular, it represents the library size as a random variable,
and gene expression likelihoods as negative binomial distributions parameterized by functions of $z_n, \ell_n$,
condition to the batch assignments $s_n$.

:::{figure} figures/scanvi_pgm.png
:align: center
:alt: scANVI graphical model
:class: img-fluid

scANVI graphical model for the ZINB likelihood model. Note that this graphical model contains more latent variables than the presentation above. Marginalization of these latent variables leads to the ZINB observation model (math shown in publication supplement).
:::

In addition to the table in {doc}`/user_guide/models/scvi`,
we have the following in scANVI.

```{eval-rst}
.. list-table::
   :widths: 20 90 15
   :header-rows: 1

   * - Latent variable
     - Description
     - Code variable (if different)
   * - :math:`c_n \in \Delta^{C-1}`
     - Cell type.
     - ``y``
   * - :math:`z_n \in \mathbb{R}^{d}`
     - Latent cell state
     - ``z_1``
   * - :math:`u_n \in \mathbb{R}^{d}`
     - Latent cell-type specific state
     - ``z_2``
```

## Inference

scANVI assumes the following factorization for the inference model

```{math}
:nowrap: true

\begin{align}
   q_\eta(z_n, \ell_n, u_n, c_n \mid x_n)
   =
   q_\eta(z_n \mid x_n)
   q_\eta(\ell_n \mid x_n)
   q_\eta(c_n \mid z_n)
   q_\eta(u_n \mid c_n, z_n)
\end{align}
```

We make several observations here.
First, each of those variational distributions will be parameterized by neural networks.
Second, while $q_\eta(z_n, x_n)$ and $q_\eta(u_n \mid c_n, z_n)$ are assumed Gaussian, $q_\eta(c_n \mid z_n)$ corresponds to a Categorical distribution over cell types.
In particular, the variational distribution $q_\eta(c_n \mid z_n)$ can predict cell types for any cell.

Behind the scenes, scANVI's classifier uses the mean of a cell's variational distribution $q_\eta(z_n \mid x_n)$
for classification.

### Training details

scANVI optimizes evidence lower bounds (ELBO) on the log evidence.
For the sake of clarity, we ignore the library size and batch assignments below.
We note that the evidence and hence the ELBO have a different expression for cells with observed and unobserved cell types.

First, assume that we observe both gene expressions $x_n$ and type assignments $c_n$.
In that case, we bound the log evidence as

```{math}
:nowrap: true

\begin{align}
 \log p_\theta(x_n, c_n)
 \geq
 \mathbb{E}_{q_\eta(z_n \mid x_n)
     q_\eta(u_n \mid z_n, c_n)}
 \left[
     \log
     \frac
     {
     p_\theta(x_n, c_n, z_n, u_n)
     }
     {
     q_\eta(z_n \mid x_n)
     q_\eta(u_n \mid z_n, c_n)
     }
 \right]
 =: \mathcal{L}_S
\end{align}
```

We aim to optimize for $\theta, \eta$ the right-hand side of this equation using stochastic gradient descent.
Gradient updates for the generative model parameters $\theta$ are easy to get.
In that case, the gradient of the expectation corresponds to the expectation of the gradients.

However, this is not the case when we differentiate for $\eta$.
The reparameterization trick solves this issue and applies to the (Gaussian) distributions associated with $q_\eta(z_n \mid x_n)
,q_\eta(u_n \mid z_n, c_n)$.
In particular, we can write $\mathcal{L}_S$ as an expectation under noise distributions independent of $\eta$.
For convenience, we will write expectations of the form $\mathbb{E}_{\epsilon_v}$ to denote expectation under the variational distribution using the reparameterization trick.
We refer the reader to [^ref3] for additional insight on the reparameterization trick.

```{math}
:nowrap: true

\begin{align}
 \nabla_\eta \mathcal{L}_S
 :=
 \mathbb{E}_{\epsilon_z, \epsilon_u}
 \left[
     \nabla_\eta
     \log
     \frac
     {
     p_\theta(x_n, c_n, z_n, u_n)
     }
     {
     q_\eta(z_n \mid x_n)
     q_\eta(u_n \mid z_n, c_n)
     }
 \right]
 =: \mathcal{L}_S
\end{align}
```

Things get trickier in the unobserved cell type case.
In this setup, the ELBO corresponds to the right-hand side of

```{math}
:nowrap: true

\begin{align}
 p_\theta(x_n)
 \geq
 \mathbb{E}_{
     q_\eta(z_n \mid x_n)
     q_\eta(c_n \mid z_n)
     q_\eta(u_n \mid z_n, c_n)
 }
 \left[
     \log
     \frac
     {
     p_\theta(x_n, c_n, z_n, u_n)
     }
     {
     q_\eta(z_n \mid x_n)
     q_\eta(c_n \mid z_n)
     q_\eta(u_n \mid z_n, c_n)
     }
 \right]=:\mathcal{L}_u
\end{align}
```

Unfortunately, the reparameterization trick does not apply naturally to $q_\eta(c_n \mid z_n)$.
As an alternative, we observe that

```{math}
:nowrap: true

\begin{align}
 \mathcal{L}_u
 =
 \mathbb{E}_{
     \epsilon_z
 }
 \left[
     \sum_{c=1}^C
     q_\eta(c_n=c \mid z_n)
     \mathbb{E}_{\epsilon_u}
         \left[
         \log
         \frac
         {
         p_\theta(x_n, c_n=c, z_n, u_n)
         }
         {
         q_\eta(z_n \mid x_n)
         q_\eta(c_n \mid z_n)
         q_\eta(u_n \mid z_n, c_n=c)
         }
     \right]
 \right]
\end{align}
```

In this form, we can differentiate $\mathcal{L}_u$ with respect to the inference network parameters, as

```{math}
:nowrap: true

\begin{align}
 \nabla_\eta \mathcal{L}_u
 =
 \mathbb{E}_{
     \epsilon_z
 }
 \left[
     \sum_{c=1}^C
     \nabla_\eta
     \left(
         q_\eta(c_n=c \mid z_n)
         \mathbb{E}_{\epsilon_u}
             \left[
             \log
             \frac
             {
             p_\theta(x_n, c_n=c, z_n, u_n)
             }
             {
             q_\eta(z_n \mid x_n)
             q_\eta(c_n \mid z_n)
             q_\eta(u_n \mid z_n, c_n=c)
             }
     \right)
     \right]
 \right]
\end{align}
```

In other words, we will need to marginalize $c_n$ out to circumvent the fact that categorical distributions cannot use the reparameterization trick.

Overall, we optimize $\mathcal{L} = \mathcal{L}_U + \mathcal{L}_S$ to train the model on both labeled and unlabelled data.

## Tasks

scANVI can perform all the same tasks as scVI (see {doc}`/user_guide/models/scvi`). In addition,
scANVI can do the following:

### Prediction

For prediction, scANVI returns $q_\eta(c_n \mid z_n)$ in the following function:

```
>>> adata.obs["scanvi_prediction"] = model.predict()
```

[^refts]:
    Tabula Sapiens Consortium (2021),
    _The Tabula Sapiens: a single cell transcriptomic atlas of multiple organs from individual human donors_,
    [BioRxiv](https://www.biorxiv.org/content/10.1101/2021.07.19.452956v1.full.pdf).

[^ref2]:
    Diederik P. Kingma, Shakir Mohamed, Danilo Jimenez Rezende, and Max Welling (2014),
    _Semi-supervised learning with deep generative models_,
    [Advances in neural information processing systems](https://proceedings.neurips.cc/paper/2014/file/d523773c6b194f37b938d340d5d02232-Paper.pdf).

[^ref3]:
    Diederik P. Kingma, Max Welling (2013) (2014),
    _Auto-Encoding Variational Bayes_,
    [Arxiv](https://arxiv.org/abs/1312.6114).
