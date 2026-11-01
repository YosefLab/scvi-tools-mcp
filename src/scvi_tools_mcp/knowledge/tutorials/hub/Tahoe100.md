# Use pretrained models of scVI-hub for Tahoe100M

This notebook represent an example of how to perform downstream anaylsis on a pretrained SCVI model that was minified and saved in a model hub.
In this case we use the model that was trained based on the [Tahoe100M](https://doi.org/10.1101/2025.02.20.639398) dataset , by [Vevo Therapuetics](https://www.tahoebio.ai/news/open-sourcing-tahoe-100m). See link to model hub [here](https://huggingface.co/tahoebio/Tahoe-100M-SCVI-v1)

**Steps performed**:

1. Loading the minified data from AWS
2. Setting up minified model with minified data
3. Visualize the latent space
4. Perform differential expression and visualize with interactive volcano plot and heatmap using Plotly


```python
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import scvi.hub
import seaborn as sns
import torch
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

## Get the data

We start by downloading the model from its hub.
Note that the model is very large therefore it will take time to being download.

```python
tahoe_hubmodel = scvi.hub.HubModel.pull_from_huggingface_hub(
    repo_name="vevotx/Tahoe-100M-SCVI-v1", cache_dir="."
)
```

We can see the model card

```python
# This will be a bit long to scroll, but has all the info
# tahoe_hubmodel
```

We will extract he model and the minifed adata

```python
tahoe = tahoe_hubmodel.model
tahoe
```

```python
tahoe.adata
```

```python
tahoe.view_anndata_setup()
```

```python
# from pprint import pprint
# pprint(tahoe.registry)
```

## Get the latent space

```python
SCVI_LATENT_KEY = "X_scVI"
latent = tahoe.get_latent_representation()
tahoe.adata.obsm[SCVI_LATENT_KEY] = latent
latent.shape
```

```python
# we visualize a subset of the results to avoid meaningless overplotting.
subset_adata = tahoe.adata[np.random.randint(0, tahoe.adata.shape[0], (1_000_000,))]
subset_adata
```

```python
subset_adata.X.shape
```

```python
import gc

gc.collect()
```

## Exploritory Analysis

```python
tahoe.adata.obs.head()
```

```python
# confuison table of plates and cell type (they are spread evently)
pd.crosstab(subset_adata.obs.plate, subset_adata.obs.Cell_ID_Cellosaur)
```

```python
# integration of drugs and cell type (certain type of cancer are given certian type of drugs)
df = subset_adata.obs.groupby(["drug", "Cell_ID_Cellosaur"]).size().unstack(fill_value=0)
norm_df = df / df.sum(axis=0)
plt.figure(figsize=(8, 8))
_ = plt.pcolor(norm_df)
_ = plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90)
_ = plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xlabel("Cell_ID_Cellosaur")
plt.ylabel("drug")
```

### Visualization with batch correction (scVI)

```python
gc.collect()
```

```python
# use scVI latent space for UMAP generation
sc.pp.neighbors(subset_adata, use_rep=SCVI_LATENT_KEY)
sc.tl.umap(subset_adata, min_dist=0.3)
```

```python
# because we have so many drugs, we wont plot the umap here
# sc.pl.umap(
#    subset_adata,
#    color=["drug"],
#    frameon=False,
# )
```

```python
sc.pl.umap(
    subset_adata,
    color=["plate", "Cell_ID_Cellosaur"],
    ncols=2,
    frameon=False,
)
```

### Visualization PCA

In order to save time we will subset the data even further

```python
subset_adata2 = subset_adata[np.random.randint(0, subset_adata.shape[0], (100_000,))]
subset_adata2
```

```python
# run PCA then generate UMAP plots (here no results will be shown as no raw data exists)
sc.tl.pca(subset_adata2)
sc.pp.neighbors(subset_adata2, n_pcs=50, n_neighbors=50)
sc.tl.umap(subset_adata2, min_dist=0.1)
```

```python
# sc.pl.umap(
#    subset_adata2,
#    color=["plate", "Cell_ID_Cellosaur"],
#    frameon=False,
# )
```

### Clustering on the scVI latent space

```python
# neighbors were already computed using scVI
SCVI_CLUSTERS_KEY = "leiden_scVI"
sc.tl.leiden(subset_adata, key_added=SCVI_CLUSTERS_KEY, resolution=0.5)
```

```python
sc.pl.umap(
    subset_adata,
    color=[SCVI_CLUSTERS_KEY],
    frameon=False,
)
```

```python
# integration of leiden clsuters and cell type
df = subset_adata.obs.groupby(["leiden_scVI", "Cell_ID_Cellosaur"]).size().unstack(fill_value=0)
norm_df = df / df.sum(axis=0)
plt.figure(figsize=(8, 8))
_ = plt.pcolor(norm_df)
_ = plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90)
_ = plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xlabel("Cell_ID_Cellosaur")
plt.ylabel("leiden_scVI")
```

### SCANVI

Running scanvi from the scvi model will require the original counts matrix and cant be done, as count matrix is all 0.

```python
gc.collect()
```

```python
tahoe.save("tahoe_tmp", save_anndata=True, overwrite=True)
```

```python
tahoe_loaded = scvi.model.SCVI.load("tahoe_tmp", adata=tahoe.adata)
```

```python
tahoe_loaded.minify_adata(minified_data_type="latent_posterior_parameters_with_counts")
```

```python
# predict on drug?
tahoe_scanvi = scvi.model.SCANVI.from_scvi_model(
    tahoe_loaded,
    unlabeled_category="Unknown",
    labels_key="drug",
)
```

```python
tahoe_loaded.adata.X
```

```python
# tahoe_scanvi.train(max_epochs=5,batch_size=64) #this fails in the workstation
```

```python
predictions = tahoe_scanvi.predict(subset_adata)
subset_adata.obs["predictions_scanvi"] = predictions
# predictions
```

See the predictions confusion matrix

```python
df = subset_adata.obs.groupby(["drug", "predictions_scanvi"]).size().unstack(fill_value=0)
norm_df = df / df.sum(axis=0)
```

```python
print("The overall Accuracy is:", np.round(np.trace(norm_df), 2))
```

We create the scanvi embeddings as well (if model was trained)

```python
SCANVI_LATENT_KEY = "X_scanVI"
# latent_scanvi = tahoe_scanvi.get_latent_representation(subset_adata2)
# subset_adata2.obsm[SCANVI_LATENT_KEY] = latent_scanvi
```

```python
# use scVI latent space for UMAP generation
# sc.pp.neighbors(subset_adata2, use_rep=SCANVI_LATENT_KEY)
# sc.tl.umap(subset_adata2, min_dist=0.3)
```

```python
# sc.pl.umap(
#    subset_adata2,
#    color=["plate", "Cell_ID_Cellosaur"],
#    ncols=2,
#    frameon=False,
# )
```

### Perform Integration Analysis

```python
from scib_metrics.benchmark import Benchmarker

bm = Benchmarker(
    subset_adata2,
    batch_key="plate",
    label_key="Cell_ID_Cellosaur",
    embedding_obsm_keys=["X_pca", "X_scVI"],
    n_jobs=-1,
)
bm.benchmark()
```

```python
bm.plot_results_table(min_max_scale=False)
```

## Performing Differential Expression in scVI

While we only have access to the minified data, we can still perform downstream analysis using the generative part of the model.
For example here, we will do it on a cluster of DMSO_TF controls vs the drug Harringtonine that is used for protein synthesis inhibitor per the cell line CVCL_0459 which is typicaly associated with Lung large cell carcinoma, a sub type of NSCLC.
We also choose to use the sub group of G2M cell cycle phase.

```python
tahoe.adata.obs["drug"].value_counts().head()
```

```python
tahoe.adata.obs["Cell_ID_Cellosaur"].value_counts().head()
```

scVI provides several options to identify the two populations of interest.

```python
cell_line = "CVCL_0459"
cell_cycle = "G2M"

drug1 = "Harringtonine"
cell_idx1 = np.logical_and(
    tahoe.adata.obs["Cell_ID_Cellosaur"] == cell_line,
    tahoe.adata.obs["drug"] == drug1,
    tahoe.adata.obs["phase"] == cell_cycle,
)
print(sum(cell_idx1), "cells from drug", drug1)

drug2 = "DMSO_TF"
cell_idx2 = np.logical_and(
    tahoe.adata.obs["Cell_ID_Cellosaur"] == cell_line,
    tahoe.adata.obs["drug"] == drug2,
    tahoe.adata.obs["phase"] == cell_cycle,
)
print(sum(cell_idx2), "cells of drug", drug2)
```

A simple DE analysis can then be performed using the following command

```python
de_change = tahoe.differential_expression(
    idx1=cell_idx1,
    idx2=cell_idx2,
    all_stats=True,
    batch_correction=True,
    mode="change",
    delta=0.05,
    pseudocounts=1e-12,
)
```

Volcano plot with p-values

```python
de_change["log10_pscore"] = np.log10(de_change["proba_not_de"] + 1e-6)
de_change = de_change.join(tahoe.adata.var, how="inner")
de_change = de_change.loc[np.max(de_change[["scale1", "scale2"]], axis=1) > 1e-4]
de_change.head()
```

We will use external gene annotations data base to extend our data

```python
gene_annotations = sc.queries.biomart_annotations(
    org="hsapiens",
    attrs=["ensembl_gene_id", "gene_biotype"],
)
```

```python
gene_annotations.index = gene_annotations["ensembl_gene_id"]
gene_annotation_dict = gene_annotations["gene_biotype"].to_dict()
```

```python
# gene_annotations.head()
```

```python
de_change["Biotype"] = [gene_annotation_dict.pop(i, "Unannotated") for i in de_change["gene_id"]]
de_change["Biotype"].value_counts()
```

display volcano plot Harringtonine vs controls volcano plot for a specific cell line and cycle

```python
import plotnine as p9

(
    p9.ggplot(de_change, p9.aes("lfc_mean", "-log10_pscore", color="Biotype"))
    + p9.geom_point(
        de_change.query("Biotype == 'protein_coding'"), alpha=0.5
    )  # Plot other genes with transparence
    + p9.xlim(-5, 5)  # Set x limits
    + p9.ylim(0, 2.5)  # Set y limits
    + p9.geom_point(de_change.query("Biotype != 'protein_coding'"))
    + p9.labs(x="LFC mean", y="Significance score (higher is more significant)")
)
```

Display generated counts from scVI model, for top 4 genes

```python
upregulated_genes = de_change.loc[de_change["lfc_median"] > 0, ["gene_id"]].head(4)
```

```python
upregulated_genes
```

```python
upregulated_genes.index
```

```python
# get the generated expression from the minified model (will take very long time)
# tahoe.adata[:, upregulated_genes.index] = tahoe.get_normalized_expression(
#    gene_list=list(upregulated_genes.index), n_samples=10
# )
```

## Future Work

Perform DE between each cell line and/or drug vs all other cell lines and/or drigs and make a dotplot of the result. In order to do this we will have to use a subset of data (both cells and genes) to save time.

Run advance models on this data such as SCANVI, MrVI using the AnnCollector dataloader.
