# Identification of zero-inflated genes

AutoZI is a deep generative model adapted from scVI allowing a gene-specific treatment of zero-inflation. For each gene $g$, AutoZI notably learns the distribution of a random variable $\delta_g$ which denotes the probability that gene $g$ is not zero-inflated. In this notebook, we present the use of the model on a PBMC dataset.

More details about AutoZI can be found in : https://www.biorxiv.org/content/10.1101/794875v2

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import tempfile

import numpy as np
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scipy.stats import beta
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```{note}
You can modify `save_dir` below to change where the data files for this tutorial are saved.
```

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

## Imports, data loading and preparation

```python
adata = scvi.data.pbmc_dataset(save_path=save_dir.name)
adata.layers["counts"] = adata.X.copy()
scvi.data.poisson_gene_selection(
    adata,
    n_top_genes=1000,
    batch_key="batch",
    subset=True,
    layer="counts",
)
scvi.model.AUTOZI.setup_anndata(
    adata,
    labels_key="str_labels",
    batch_key="batch",
    layer="counts",
)
```

## Analyze gene-specific ZI

In AutoZI, all $\delta_g$'s follow a common $\text{Beta}(\alpha,\beta)$ prior distribution where $\alpha,\beta \in (0,1)$ and the zero-inflation probability in the ZINB component is bounded below by $\tau_{\text{dropout}} \in (0,1)$. AutoZI is encoded by the `AutoZIVAE` class whose inputs, besides the size of the dataset, are $\alpha$ (`alpha_prior`), $\beta$ (`beta_prior`), $\tau_{\text{dropout}}$ (`minimal_dropout`). By default, we set $\alpha = 0.5, \beta = 0.5, \tau_{\text{dropout}} = 0.01$.

Note : we can learn $\alpha,\beta$ in an Empirical Bayes fashion, which is possible by setting `alpha_prior = None` and `beta_prior = None`

```python
model = scvi.model.AUTOZI(adata)
```

We fit, for each gene $g$, an approximate posterior distribution $q(\delta_g) = \text{Beta}(\alpha^g,\beta^g)$ (with $\alpha^g,\beta^g \in (0,1)$) on which we rely. We retrieve $\alpha^g,\beta^g$ for all genes $g$ (and $\alpha,\beta$, if learned) as numpy arrays using the method `get_alphas_betas` of `AutoZIVAE`.

```python
model.train(max_epochs=200, plan_kwargs={"lr": 1e-2})
```

```python
outputs = model.get_alphas_betas()
alpha_posterior = outputs["alpha_posterior"]
beta_posterior = outputs["beta_posterior"]
```

Now that we obtained fitted $\alpha^g,\beta^g$, different metrics are possible. Bayesian decision theory suggests us the posterior probability of the zero-inflation hypothesis $q(\delta_g < 0.5)$, but also other metrics such as the mean wrt $q$ of $\delta_g$ are possible. We focus on the former. We decide that gene $g$ is ZI if and only if $q(\delta_g < 0.5)$ is greater than a given threshold, say $0.5$. We may note that it is equivalent to $\alpha^g < \beta^g$. From this we can deduce the fraction of predicted ZI genes in the dataset.

```python
# Threshold (or Kzinb/Knb+Kzinb in paper)
threshold = 0.5

# q(delta_g < 0.5) probabilities
zi_probs = beta.cdf(0.5, alpha_posterior, beta_posterior)

# ZI genes
is_zi_pred = zi_probs > threshold

print("Fraction of predicted ZI genes :", is_zi_pred.mean())
```

We noted that predictions were less accurate for genes $g$ whose average expressions - or predicted NB means, equivalently - were low. Indeed, genes assumed not to be ZI were more often predicted as ZI for such low average expressions. A threshold of 1 proved reasonable to separate genes predicted with more or less accuracy. Hence we may want to focus on predictions for genes with average expression above 1.

```python
mask_sufficient_expression = (np.array(adata.X.mean(axis=0)) > 1.0).reshape(-1)
print("Fraction of genes with avg expression > 1 :", mask_sufficient_expression.mean())
print(
    "Fraction of predicted ZI genes with avg expression > 1 :",
    is_zi_pred[mask_sufficient_expression].mean(),
)
```

## Analyze gene-cell-type-specific ZI

One may argue that zero-inflation should also be treated on the cell-type (or 'label') level, in addition to the gene level. AutoZI can be extended by assuming a random variable $\delta_{gc}$ for each gene $g$ and cell type $c$ which denotes the probability that gene $g$ is not zero-inflated in cell-type $c$. The analysis above can be extended to this new scale.

```python
# Model definition
model_genelabel = scvi.model.AUTOZI(adata, dispersion="gene-label", zero_inflation="gene-label")

# Training
model_genelabel.train(max_epochs=200, plan_kwargs={"lr": 1e-2})

# Retrieve posterior distribution parameters
outputs_genelabel = model_genelabel.get_alphas_betas()
alpha_posterior_genelabel = outputs_genelabel["alpha_posterior"]
beta_posterior_genelabel = outputs_genelabel["beta_posterior"]
```

```python
# q(delta_g < 0.5) probabilities
zi_probs_genelabel = beta.cdf(0.5, alpha_posterior_genelabel, beta_posterior_genelabel)

# ZI gene-cell-types
is_zi_pred_genelabel = zi_probs_genelabel > threshold

ct = adata.obs.str_labels.astype("category")
codes = np.unique(ct.cat.codes)
cats = ct.cat.categories
for ind_cell_type, cell_type in zip(codes, cats, strict=False):
    is_zi_pred_genelabel_here = is_zi_pred_genelabel[:, ind_cell_type]
    print(
        f"Fraction of predicted ZI genes for cell type {cell_type} :",
        is_zi_pred_genelabel_here.mean(),
        "\n",
    )
```

```python
# With avg expressions > 1
for ind_cell_type, cell_type in zip(codes, cats, strict=False):
    mask_sufficient_expression = (
        np.array(adata.X[adata.obs.str_labels.values.reshape(-1) == cell_type, :].mean(axis=0))
        > 1.0
    ).reshape(-1)
    print(
        f"Fraction of genes with avg expression > 1 for cell type {cell_type} :",
        mask_sufficient_expression.mean(),
    )
    is_zi_pred_genelabel_here = is_zi_pred_genelabel[mask_sufficient_expression, ind_cell_type]
    print(
        f"Fraction of predicted ZI genes with avg expression > 1 for cell type {cell_type} :",
        is_zi_pred_genelabel_here.mean(),
        "\n",
    )
```
