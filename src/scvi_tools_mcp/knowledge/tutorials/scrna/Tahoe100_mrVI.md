# MrVI analysis over Tahoe100M cells dataset

MrVI (Multi-resolution Variational Inference) is a model for analyzing multi-sample single-cell RNA-seq data. 
This tutorial show how to do run MrVI in PyTorch version over the [Tahoe100M](https://doi.org/10.1101/2025.02.20.639398) cells dataset and perform basic analysis.


```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

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
from scvi.external import MRVI

run_autotune = False
```

```python
# import inspect
# print(inspect.getsource(MRVI))
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

```python
pd.set_option("display.max_rows", 50)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 1000)
```

## Get the data

We start by downloading the model from its hub in order to use its metadata
Note that the model is very large therefore it will take time to being download.

```python
# get the hub data
tahoe_hubmodel = scvi.hub.HubModel.pull_from_huggingface_hub(
    repo_name="vevotx/Tahoe-100M-SCVI-v1", cache_dir="."
)
```

```python
tahoe_hubmodel.model.adata.obs.head()
```

```python
# Load Cell Line Metadata
cell_lines = pd.read_csv(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/cell_line_metadata.h5ad"
)
cell_lines.head()
```

```python
# Load the .h5ad file
adata = sc.read_h5ad(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_100000_rand.h5ad"
)
adata.obs.head()
```

We use a subset of data, show the plates stratification and perform HVG filtering following by merging the metadata and split to train and test

```python
adata.obs.plate.value_counts()
```

```python
# HVG filtering
sc.pp.highly_variable_genes(
    adata, n_top_genes=15000, inplace=True, subset=True, flavor="seurat_v3", batch_key="plate"
)
adata
```

```python
# merge metadata
adata.obs = adata.obs.merge(
    tahoe_hubmodel.model.adata.obs[
        [
            "Cell_Name_Vevo",
            "dataset",
            "phase",
            "observed_lib_size",
            "S_score",
            "G2M_score",
            "sublibrary",
        ]
    ],
    how="left",
    left_on="BARCODE_SUB_LIB_ID",
    right_index=True,
)
```

```python
adata.layers["counts"] = adata.X.copy()  # preserve counts
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata  # freeze the state in `.raw`
```

```python
from sklearn.model_selection import train_test_split

train_ind, valid_ind = train_test_split(
    adata.obs.plate.index.astype(int), test_size=0.9, stratify=adata.obs.plate
)
```

### Init the model

We will initialize the MRVI model with its "pytorch" backend. A JAX backend version can be also be used using backend="jax".

```python
sample_key = "sample"  # target covariate sample/cell_line_id
batch_key = "plate"  # nuisance variable identifier
MRVI.setup_anndata(
    adata, sample_key=sample_key, batch_key=batch_key, layer="counts", backend="torch"
)
```

## Train mrVI

```python
import gc
import time

gc.collect()
start = time.time()
model = MRVI(adata, backend="torch")
model.train(
    max_epochs=400,
    early_stopping=True,
    plan_kwargs={"lr": 1e-3, "n_epochs_kl_warmup": 40},
    batch_size=512,
    early_stopping_patience=5,
    check_val_every_n_epoch=1,
    datasplitter_kwargs={"external_indexing": [np.array(train_ind), np.array(valid_ind)]},
)
end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
```

```python
train_ind
```

```python
valid_ind
```

```python
plt.plot(model.history["elbo_validation"])
plt.xlabel("Epoch")
plt.ylabel("Validation ELBO")
plt.show()
```

```python
plt.plot(model.history["reconstruction_loss_validation"])
plt.xlabel("Epoch")
plt.ylabel("Validation reconstruction_loss")
plt.show()
```

```python
plt.plot(model.history["kl_local_validation"])
plt.xlabel("Epoch")
plt.ylabel("Validation KL")
plt.show()
```

```python
plt.plot(model.history["elbo_train"])
plt.xlabel("Epoch")
plt.ylabel("Training ELBO")
plt.show()
```

```python
plt.plot(model.history["kl_local_train"])
plt.xlabel("Epoch")
plt.ylabel("Training KL")
plt.show()
```

## Visualize cell embeddings and sample distances

The latent representations of the cells can also be accessed and visualized using the get_latent_representation method. MrVI learns two latent representations: u and z. u is designed to capture broad cell states invariant to sample and nuisance covariates, while z augments u with sample-specific effects but remains corrected for nuisance covariate effects.


```python
# run PCA then generate UMAP plots
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_pcs=50, n_neighbors=50)
sc.tl.umap(adata, min_dist=0.1)
```

```python
sc.pl.umap(
    adata,
    color=["plate", "cell_line_id"],
    ncols=2,
    frameon=False,
)
```

```python
u = model.get_latent_representation()
adata.obsm["X_mrVI_Torch"] = u
sc.pp.neighbors(adata, use_rep="X_mrVI_Torch")
sc.tl.umap(adata, min_dist=0.3)
```

```python
u.shape
```

```python
sc.pl.umap(
    adata,
    color=["plate", "cell_line_id"],
    frameon=False,
    ncols=2,
)
```

```python
sc.pl.umap(
    adata,
    color=["moa-broad", "phase"],
    frameon=False,
    ncols=2,
)
```

```python
sc.pl.umap(
    adata,
    color=["observed_lib_size", "S_score", "G2M_score"],
    frameon=False,
    ncols=3,
)
```

## Train regular SCVI model for comparison

```python
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key=batch_key)
```

```python
model_scvi = scvi.model.SCVI(adata)
```

```python
model_scvi.train(
    max_epochs=100,
    early_stopping=True,
    check_val_every_n_epoch=1,
    datasplitter_kwargs={"external_indexing": [np.array(train_ind), np.array(valid_ind)]},
)
```

```python
plt.plot(model_scvi.history["elbo_validation"])
plt.xlabel("Epoch")
plt.ylabel("Validation ELBO")
plt.show()
```

```python
SCVI_LATENT_KEY = "X_scVI"
latent = model_scvi.get_latent_representation()
adata.obsm[SCVI_LATENT_KEY] = latent
latent.shape
```

```python
# use scVI latent space for UMAP generation
sc.pp.neighbors(adata, use_rep=SCVI_LATENT_KEY)
sc.tl.umap(adata, min_dist=0.3)
```

```python
sc.pl.umap(
    adata,
    color=["plate", "cell_line_id"],
    title=["Plate ID SCVI", "Cell Line ID SCVI"],
    ncols=2,
    frameon=False,
)
```

```python
sc.pl.umap(
    adata,
    color=["moa-broad", "phase"],
    frameon=False,
    ncols=2,
)
```

```python
sc.pl.umap(
    adata,
    color=["observed_lib_size", "S_score", "G2M_score"],
    frameon=False,
    ncols=3,
)
```

## Compare results

```python
from scib_metrics.benchmark import BatchCorrection, Benchmarker, BioConservation
```

```python
bm = Benchmarker(
    adata[list(np.random.choice(np.arange(adata.n_obs), size=1000, replace=False)), :],
    batch_key="plate",
    bio_conservation_metrics=BioConservation(
        isolated_labels=True,
        nmi_ari_cluster_labels_leiden=True,
        silhouette_label=True,
        clisi_knn=True,
        nmi_ari_cluster_labels_kmeans=True,
    ),
    batch_correction_metrics=BatchCorrection(
        bras=True,
        pcr_comparison=True,
        kbet_per_label=True,
        graph_connectivity=False,
        ilisi_knn=True,
    ),
    label_key="cell_line_id",
    embedding_obsm_keys=["X_pca", "X_scVI", "X_mrVI_Torch"],
    n_jobs=-1,
)
bm.benchmark()
```

```python
bm.plot_results_table(min_max_scale=False)
```
