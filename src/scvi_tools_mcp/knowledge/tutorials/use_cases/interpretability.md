# Using SHAP values and IntegratedGradients for cell type classification interpretability

Previously we saw semi-supervised models, like SCANVI being used for tasks like cell type classification, enabling researchers to uncover complex biological patterns. However, as these models become more sophisticated, it is essential to understand not just the predictions they make, but why they make them. This is where interpretability methods like [SHAP (SHapley Additive exPlanations)](https://shap.readthedocs.io/en/latest/generated/shap.DeepExplainer.html#shap.DeepExplainer) and [CAPTUM IntegratedGradients](https://captum.ai/api/integrated_gradients.html) come into play. By providing insights into the influence of individual features on model predictions, these methods help us trust and validate our models in critical biological contexts.

In this tutorial, we'll explore the significance of interpretability techniques in supervised cell classification using ScanVI, which are now avialble as part of SCVI-Tools.

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import seaborn as sns
import torch

torch.set_float32_matmul_precision("high")
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

## Load data and train scanvi

In this tutorial we will be using the dataset of peripheral blood mononuclear cells from 10x Genomics, [PBMC dataset](https://docs.scvi-tools.org/en/stable/api/reference/scvi.data.pbmc_dataset.html#scvi.data.pbmc_dataset)

```python
adata = scvi.data.pbmc_dataset()
adata.layers["counts"] = adata.X.copy()
adata.obs["batch"] = adata.obs["batch"].astype("category")
adata
```

```python
adata.var_names = adata.var["gene_symbols"]
```

```python
adata.obs.str_labels.value_counts()  # list of classes and their observations
```

```python
print("# cells, # genes before filtering:", adata.shape)

sc.pp.filter_genes(adata, min_counts=3)
sc.pp.filter_cells(adata, min_counts=3)
```

```python
# We select a small number of genes here, so our later interpretability analysis will be fast
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=200,
    subset=True,
    layer="counts",
    flavor="seurat_v3",
    batch_key="batch",
)
print("# cells, # genes after filtering:", adata.shape)
```

```python
scvi.model.SCANVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    labels_key="str_labels",
    unlabeled_category="unknown",
)
```

```python
model = scvi.model.SCANVI(adata)
model
```

```python
model.train(
    max_epochs=100,
    early_stopping=True,
    check_val_every_n_epoch=1,
    train_size=0.8,
    validation_size=0.2,
    # accelerator="gpu",
    # devices=-1,
    # strategy="ddp_notebook_find_unused_parameters_true",
)
```

## Inspect scanvi training and test performance

```python
adata.obsm["X_scANVI"] = model.get_latent_representation()
```

```python
# use scVI latent space for UMAP generation
sc.pp.neighbors(adata, use_rep="X_scANVI", n_neighbors=30)
```

```python
sc.tl.umap(adata, min_dist=0.3)
```

```python
sc.pl.umap(adata, color=["str_labels", "batch"], ncols=2, wspace=0.4)
```

Next we will apply the 2 techniques for features interpretability and compare between them

## Integrated Gradients

Integrated Gradients is a robust interpretability technique that attributes the output of a model to its input features by calculating the cumulative sum of gradients along a path from a baseline (typically zero or a neutral input) to the actual input. This approach provides a way to measure how each feature contributes to the model's output in a smooth and consistent manner.

It is availble for any semi supervised model in SCVI-Tools by passing the ig_interpretability=True flag to the predict function.

```python
predictions, attributions = model.predict(ig_interpretability=True)
```

The method works relatievely fast and we can then plot the gene table with their importnace mean and variance, overall for all cell - types

```python
n_plot = 15
attributions.head(n_plot)
```

```python
df = attributions.head(n_plot)
ci = 1.96 * df["attribution_std"] / np.sqrt(df["cells"])
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 2), dpi=200)
sns.barplot(ax=ax, data=df, x="gene", y="attribution_mean", hue="gene", dodge=False)
ax.set_yticks([])
plt.tick_params(axis="x", which="major", labelsize=8, labelrotation=90)
ax.errorbar(
    df["gene"].values,
    df["attribution_mean"].values,
    yerr=ci,
    ecolor="black",
    fmt="none",
)
if ax.get_legend() is not None:
    ax.get_legend().remove()
```

We can repeat for specific class ('Dendritic Cells'):

```python
predictions_class, attributions_class = model.predict(
    indices=np.where(adata.obs.str_labels == "Dendritic Cells")[0].tolist(),
    ig_interpretability=True,
)
```

```python
attributions_class.head(n_plot)
```

```python
df_class = attributions_class.head(n_plot)
ci = 1.96 * df_class["attribution_std"] / np.sqrt(df_class["cells"])
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 2), dpi=200)
sns.barplot(ax=ax, data=df_class, x="gene", y="attribution_mean", hue="gene", dodge=False)
ax.set_yticks([])
plt.tick_params(axis="x", which="major", labelsize=8, labelrotation=90)
ax.errorbar(
    df_class["gene"].values,
    df_class["attribution_mean"].values,
    yerr=ci,
    ecolor="black",
    fmt="none",
)
if ax.get_legend() is not None:
    ax.get_legend().remove()
```

As expected, for a specific class, we can see different important genes, altough S100A4 is still the top contributer

More generally we would like to see a more general view of top genes to contribute to our celltype groups classification.

```python
classes = adata.obs.str_labels.cat.categories
features = adata.var_names
attributions_class_pos_agg = pd.DataFrame()
n_cols = 3
top_n = 5
nrows = round(classes.size / n_cols)
fig, ax = plt.subplots(nrows, n_cols, sharex=False, figsize=(20, 20))
for idx, ct in enumerate(classes):
    _, attributions_class = model.predict(
        indices=np.where(adata.obs.str_labels == ct)[0].tolist(),
        ig_interpretability=True,
    )
    positive = attributions_class.head(top_n)
    positive["contribution"] = "positive"
    negative = attributions_class.tail(top_n)
    negative["contribution"] = "negative"
    avg = pd.concat([positive, negative])
    title = f"IG importance for: {ct}"

    # also keep the positive contributions
    attributions_class_pos = attributions_class[attributions_class.attribution_mean > 0]
    attributions_class_pos["class"] = ct
    attributions_class_pos_agg = pd.concat([attributions_class_pos_agg, attributions_class_pos])

    sns.barplot(
        x="attribution_mean",
        y="gene",
        hue="contribution",
        palette=["blue", "red"],
        data=avg,
        ax=ax[idx // n_cols, idx % n_cols],
    )

    ax[idx // n_cols, idx % n_cols].set_title(title)
    ax[idx // n_cols, idx % n_cols].legend(title="IG Contribution", loc="lower right")

_ = [fig.delaxes(ax_) for ax_ in ax.flatten() if not ax_.has_data()]

fig.tight_layout()
```

And we can also show the positive contribution of each gene being aggregated per cell type group

```python
top_n = 20
# Pivot the data so that each group becomes a column for stacking
pivot_df = attributions_class_pos_agg.pivot_table(
    index="gene", columns="class", values="attribution_mean", aggfunc="sum"
)

# Sort by the total sum of each feature (sum across all groups)
pivot_df["total"] = pivot_df.sum(axis=1)  # Calculate the total sum for each feature
pivot_df = pivot_df.sort_values(by="total", ascending=False)  # Sort by the total value
pivot_df = pivot_df.head(top_n)  # Select the top 10 features

# Plotting the horizontal stacked bar plot
ax = pivot_df.drop("total", axis=1).plot(
    kind="barh", stacked=True, figsize=(10, 6), colormap="tab20"
)

# Add labels and title
ax.set_xlabel("IG Contribution Value")
ax.set_ylabel("Gene")
ax.set_title("Top 10 Stacked IG Contributions by Cell Type per Gene")

# Display the plot
plt.tight_layout()
plt.show()
```

## SHAP

SHAP (SHapley Additive exPlanations) values are a popular interpretability technique based on cooperative game theory. The core idea is to fairly allocate the "credit" for a model's prediction to each feature, by considering all possible combinations of features and their impact on the prediction. SHAP values are additive, meaning the sum of the SHAP values for all features equals the difference between the model’s output and the average prediction. This method works for any model type, providing a consistent way to explain individual predictions, making it highly versatile and widely applicable. Deep SHAP is an extension of the SHAP method designed specifically for deep learning models, such as the ones in SCVI-Tools. For more information see [this](https://www.nature.com/articles/s41592-024-02511-3)

Calcualtion of SHAP for SC data usually takes a lot of time. In SCVI-Tools we are running an approximation of FastSHAP in order to reduce runtime, where we train a shallow surrogate model to imitate the original model prediction and than run the SHAP over the surrogate model. See [this]("https://arxiv.org/abs/2107.07436")

```python
import torch.nn as nn
from scvi.utils import FastSHAP, Surrogate
from scvi.utils.fastshap import KLDivLoss, MaskLayer1d
```

```python
num_features = len(features)
num_classes = len(classes)
surr = nn.Sequential(
    MaskLayer1d(value=0, append=True),
    nn.Linear(2 * num_features, 128),
    nn.ELU(inplace=True),
    nn.Linear(128, 128),
    nn.ELU(inplace=True),
    nn.Linear(128, num_classes),
).to(model.device)
```

```python
# Set up surrogate object
surrogate = Surrogate(surr, num_features)
# Train Surrogate
surrogate.train_original_model(
    train_data=adata.X.toarray()[model.train_indices],
    val_data=adata.X.toarray()[model.validation_indices],
    original_model=model.shap_adata_predict,
    batch_size=64,
    max_epochs=10,
    loss_fn=KLDivLoss(),
    validation_samples=10,
    validation_batch_size=10000,
    verbose=True,
)
```

```python
# Train FastSHAP
# Create explainer model
explainer = nn.Sequential(
    nn.Linear(num_features, 128),
    nn.ReLU(inplace=True),
    nn.Linear(128, 128),
    nn.ReLU(inplace=True),
    nn.Linear(128, num_classes * num_features),
).to(model.device)
```

```python
# Set up FastSHAP object
fastshap = FastSHAP(explainer, surrogate, normalization="additive", link=nn.Softmax(dim=-1))
# Train
fastshap.train(
    train_data=adata.X.toarray()[model.train_indices],
    val_data=adata.X.toarray()[model.validation_indices],
    batch_size=32,
    num_samples=32,
    max_epochs=100,
    validation_samples=128,
    verbose=True,
)
```

We repeat the same figure plot like the previous case:

```python
classes = adata.obs.str_labels.cat.categories
features = adata.var_names
attributions_class_pos_agg = pd.DataFrame()
n_cols = 3
top_n = 5
nrows = round(classes.size / n_cols)
fig, ax = plt.subplots(nrows, n_cols, sharex=False, figsize=(20, 20))
for idx, ct in enumerate(classes):
    sum_shap_per_class = [0] * num_features
    for ind in np.where(adata.obs.str_labels == ct)[0].tolist():
        sum_shap_per_class += fastshap.shap_values(np.array([adata.X[ind].toarray()]))[0][:, 0]
    attributions_class = pd.DataFrame(
        {"gene": features, "mean_shap": sum_shap_per_class / num_features, "class": ct}
    ).sort_values("mean_shap", ascending=False)

    positive = attributions_class.head(top_n)
    positive["contribution"] = "positive"
    negative = attributions_class.tail(top_n)
    negative["contribution"] = "negative"
    avg = pd.concat([positive, negative])
    title = f"IG importance for: {ct}"

    # also keep the positive contributions
    attributions_class_pos = attributions_class[attributions_class.mean_shap > 0]
    attributions_class_pos["class"] = ct
    attributions_class_pos_agg = pd.concat([attributions_class_pos_agg, attributions_class_pos])

    sns.barplot(
        x="mean_shap",
        y="gene",
        hue="contribution",
        palette=["blue", "red"],
        data=avg,
        ax=ax[idx // n_cols, idx % n_cols],
    )

    ax[idx // n_cols, idx % n_cols].set_title(title)
    ax[idx // n_cols, idx % n_cols].legend(title="SHAP Contribution", loc="lower right")

_ = [fig.delaxes(ax_) for ax_ in ax.flatten() if not ax_.has_data()]

fig.tight_layout()
```

```python
top_n = 20
# Pivot the data so that each group becomes a column for stacking
pivot_df = attributions_class_pos_agg.pivot_table(
    index="gene", columns="class", values="mean_shap", aggfunc="sum"
)

# Sort by the total sum of each feature (sum across all groups)
pivot_df["total"] = pivot_df.sum(axis=1)  # Calculate the total sum for each feature
pivot_df = pivot_df.sort_values(by="total", ascending=False)  # Sort by the total value
pivot_df = pivot_df.head(top_n)  # Select the top 10 features

# Plotting the horizontal stacked bar plot
ax = pivot_df.drop("total", axis=1).plot(
    kind="barh", stacked=True, figsize=(10, 6), colormap="tab20"
)

# Add labels and title
ax.set_xlabel("SHAP Contribution Value")
ax.set_ylabel("Gene")
ax.set_title("Top 10 Stacked SHAP Contributions by Cell Type per Gene")

# Display the plot
plt.tight_layout()
plt.show()
```

And we can see some overlapping genes from the 2 methods for this specific group of cells

As for SCVI-tools v1.3 Work on SHAP is still in progress: please check back in the next release!
