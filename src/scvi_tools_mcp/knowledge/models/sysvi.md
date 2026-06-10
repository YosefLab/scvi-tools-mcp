# SYSVI — API Reference

**Class:** `scvi.external.sysvi._model.SysVI`

**Signature:** `SysVI(adata: 'AnnData', prior: "Literal['standard_normal', 'vamp']" = 'vamp', n_prior_components: 'int' = 5, pseudoinputs_data_indices: 'np.array | None' = None, **model_kwargs)`

## Docstring

Integration with cVAE & optional VampPrior and latent cycle-consistency.

 Described in
 `Hrovatin et al. (2023) <https://doi.org/10.1101/2023.11.03.565463>`_.

Parameters
----------
adata
    AnnData object that has been registered via
    :meth:`~scvi.external.SysVI.setup_anndata`.
prior
    The prior distribution to be used.
    You can choose between ``"standard_normal"`` and ``"vamp"``.
n_prior_components
    Number of prior components (i.e., modes) to use in VampPrior.
pseudoinputs_data_indices
    By default, VampPrior pseudoinputs are randomly selected from data.
    Alternatively, one can specify pseudoinput indices using this parameter.
    The number of specified indices in the input 1D array should match
    ``n_prior_components``.
**model_kwargs
    Keyword args for :class:`~scvi.external.sysvi.SysVAE`

## setup_anndata

```python
SysVI.setup_anndata(adata: 'AnnData', batch_key: 'str', layer: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, weight_batches: 'bool' = False, **kwargs)
```

Prepare adata for input to SysVI model.

Setup distinguishes between two main types of covariates that can be
corrected for:

- batch - referred to as "system" in the original publication
  Hrovatin, et al., 2023):
  Single categorical covariate that will be corrected via cycle
  consistency loss.
  It will be also used as a condition in cVAE.
  This covariate is expected to correspond to stronger batch effects,
  such as between datasets from different sequencing technology or
  model systems (animal species, in-vitro models and tissue, etc.).
- covariate (includes both continuous and categorical covariates):
  Additional covariates to be used only
  as a condition in cVAE, but not corrected via cycle loss.
  These covariates are expected to correspond to weaker batch effects,
  such as between datasets from the same sequencing technology and
  system (animal, in-vitro, etc.) or between samples within a dataset.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
layer
    AnnData layer to use, default is X.
    Should contain normalized and log1p transformed expression.
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
SysVI.train(self, plan_kwargs: 'dict | None' = None, **train_kwargs)
```

Train the models.

Overwrites the ``train`` method of
class:`~scvi.model.base.UnsupervisedTrainingMixin`
to prevent the use of KL loss warmup (specified in ``plan_kwargs``).
This is disabled as our experiments showed poor integration in the
cycle model when using KL loss warmup.

Parameters
----------
plan_kwargs
    Training plan kwargs in `meth`:`scvi.train.TrainingPlan`.
train_kwargs
    Training kwargs. Passed to `meth`:`scvi.model.base.BaseModelClass.train`.


---

## User Guide

# SysVI

**sysVI** (cross-SYStem Variational Inference,
Python class {class}`~scvi.external.SysVI`)
is a representation learning models that can remove significant batch effects.

The advantages of SysVI are:

-   Improved integration: For datasets with **substantial batch effects**
(e.g., cross-species or organoid-tissue), where other models often fail.
It provides a good tradeoff between batch correction and preservation of
cell-type and sub-cell-type biological variation.
- Tunable integration: The **integration strength is directly tunable**
via cycle consistency loss.
- Generally applicable: The model operates on
**approximately normally distributed data**
(e.g., normalized and log+1 transformed scRNA-seq data), which makes it
more generally applicable than just scRNA-seq.
- Scalable: Can integrate very large datasets if using a GPU.

The limitations of SysVI include:

-   Weak batch effects: For datasets with **small batch effects**
(e.g., multiple subjects from a single laboratory) we recommend using scVI instead,
as it has slightly higher biological preservation in this setting.
To determine whether a dataset has substantial batch effects,
please refer to our paper.
- Model selection: The best performance is achieved if
**selecting the best model** from multiple
runs with a few different cycle consistency loss weights and random seed
initializations, as explained in the tutorial.
However, we provide **defaults** that generate decent results in
many settings.


```{topic} Tutorials:

-   {doc}`/tutorials/notebooks/scrna/sysVI`
```

```{topic} References:

-  Paper: Hrovatin and Moinfar, et al.
Integrating single-cell RNA-seq datasets with substantial batch effects.
bioRxiv (2023): https://doi.org/10.1101/2023.11.03.565463
- Talk on caveats of scRNA-seq integration and strategies for removing
substantial batch effects: https://www.youtube.com/watch?v=i-a4BjAn90E
```

## Method background

The model is based on a variational autoencoder (VAE), with the integrated
representation corresponding to the latent space embedding of the cells.

### Stronger batch correction with cycle-consistency loss

Vanilla VAEs struggle to achieve strong batch correction without losing
substantial biological variation. This issue arises as the VAE loss
does not directly penalize the presence of batch covariate information in the
latent space.
Instead, conditional VAEs assume that batch covariate information will be
omitted from the latent space, which has limited-capacity,
as it is separately injected into the decoder. Namely, its presence in the
latent space is "unnecessary" for the reconstruction (Hrovatin and Moinfar, 2023).

To achieve stronger integration than vanilla VAEs, SysVI employs
cycle-consistency loss in the latent space. In particular, the model embeds a cell
from one system (i.e., the covariate representing substantial batch effect)
into latent space and then decodes it using another category of the system covariate.
In this way it generates a biologically identical cell with a
different batch effect. The generated cell is then likewise embedded into the
latent space, and the distance between the embeddings of the original and
the switched-batch cell is computed. The model is trained to minimize this distance.

:::{figure} figures/sysvi_cycleconsistency.png
:align: center
:alt: Cycle consistency loss used to increase batch correction in SysVI.
:class: img-fluid
:::

Benefits of this approach:
- As only cells with identical biological background are compared, this method
retains good biological preservation even when removing
substantial batch effects. This distinguishes it from alternative approaches
that compare cells with different biological backgrounds
(e.g., via adversarial loss; see Hrovatin and Moinfar (2023) for details).
- The integration strength can be directly tuned via the cycle-consistency
loss weight.

### Improved biological preservation via the VampPrior

Vanilla VAEs employ standard normal before regularizing latent space.
However, this prior is very restrictive and can lead to loss of
important biological variation in the latent space.

Instead, we use the
VampPrior ([Tomczak, 2017](https://doi.org/10.48550/arXiv.1705.07120)),
which permits a more expressive latent space. VampPrior is a multi-modal
prior for which the mode positions are learned during the training.

:::{figure} figures/sysvi_vampprior.png
:align: center
:alt: VampPrior used to increase the preservation of biological variation in SysVI.
:class: img-fluid
:::

Benefits of this approach:
- More expressive latent space leads to increased preservation of
biological variability.
- VampPrior was more robust with respect to the number of modes than the
better-known Gaussian mixture prior.

### Application flexibility due to using normally distributed inputs

Many scRNA-seq integration models are specially designed to work with
scRNA-seq data, e.g., raw counts that follow negative binomial distribution.
However, due to this, these models cannot be directly used for other
types of data.

We observed that for representation learning this specialized setup is not
strictly required. SysVI is designed for data following normal distribution, while
performing competitively in comparison to the more specialized models
on scRNA-seq data.
To make scRNA-seq data approximately normally distributed, we preprocess it via
size-factor normalization and log+1 transformation.

Thus, SysVI could be also applied to other types of normally distributed data.
However, we did not specifically test its performance on other data types.

## Other tips and tricks for data integration

Besides the benefits of the SysVI model, our paper
([Hrovatin and Moinfar, 2023](https://doi.org/10.1101/2023.11.03.565463))
and
[talk](https://www.youtube.com/watch?v=i-a4BjAn90E)
provide additional advice on scRNA-seq integration that applies beyond SysVI.
The two most important insights are:
- Try to make the **integration task as easy for the model** as possible.
This means that data should be pre-processed in a way that already eliminates
some of the batch differences, when possible:
  - Use intersection of HVGs across batches with substantial batch effects
  (e.g., the systems).
  - Mitigate known technical artefacts, such as ambient gene expression
  ([Hrovatin and Sikkema, 2024](https://doi.org/10.1038/s41592-024-02532-y)).
- Ensure that **the metrics used to evaluate integration are of high quality**:
  - They should be able to capture the key properties required for downstream tasks.
  For example, the standard cell-type-based biological preservation metrics do
  not assess whether subtler biological differences, such as within-cell-type
  disease effects, are preserved.
  - Be cautious of potential biases within integration metric scores. -
  The scores may not directly correspond to the desired data property,
  being influenced by other factors, or
  certain models may be able to trick the metrics.
