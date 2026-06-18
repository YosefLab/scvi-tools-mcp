# MrVI analysis over Tahoe100M cells dataset using LaminDB Custom Dataloader

MrVI (Multi-resolution Variational Inference) is a model for analyzing multi-sample single-cell RNA-seq data. 
This tutorial show how to do run MrVI in PyTorch version over the [Tahoe100M](https://doi.org/10.1101/2025.02.20.639398) cells dataset and perform basic analysis, using [Lamin](https://lamin.ai/) custom dataloader.


```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import gc
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import scvi.hub
import seaborn as sns
import torch
from scvi.dataloaders import MappedCollectionDataModule
from scvi.external import MRVI

run_autotune = False
```

```python
# import inspect
# print(inspect.getsource(MRVI))
```

```python
# os.system("lamin init --storage ./lamindb_collection")
import lamindb as ln
# ln.setup.init()
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

In the next part we are creating artifacts from a subset of 1M cells per plate (and 5 plates) from the dataset and unite them to a collection. Artifacts and collections are the ways lamindb interactes with the data.
From this point forward we will not use adatas again.
The tutorial assumed those files were already ready (see for how to [here](https://huggingface.co/datasets/tahoebio/Tahoe-100M/blob/main/tutorials/loading_data.ipynb))

```python
# Init Lamin instance
ln.track()
```

```python
# We make a collection of artifactos from files that are stored on disk
artifact1 = ln.Artifact.from_anndata(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_1000000_plate1.h5ad",
    key="part_1.h5ad",
).save()
artifact2 = ln.Artifact.from_anndata(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_1000000_plate2.h5ad",
    key="part_2.h5ad",
).save()
artifact3 = ln.Artifact.from_anndata(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_1000000_plate3.h5ad",
    key="part_3.h5ad",
).save()
artifact4 = ln.Artifact.from_anndata(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_1000000_plate4.h5ad",
    key="part_4.h5ad",
).save()
artifact5 = ln.Artifact.from_anndata(
    "/home/access/PycharmProjects/scvi-tools/Tahoe100M/tahoe100m_sample_1000000_rand.h5ad",
    key="part_5.h5ad",
).save()
```

```python
collection = ln.Collection([artifact1, artifact2, artifact3, artifact4, artifact5], key="gather")
collection.save()
```

```python
# We load the collection to see it consists of many h5ad files
artifacts = collection.artifacts.all()
artifacts.df()
```

we can now define the batch and data loader which replaces the default AnnDataloder of and use that on MRVI model.

```python
datamodule = MappedCollectionDataModule(
    collection,
    batch_key="plate",
    sample_key="sample",
    batch_size=1024,
    shuffle=True,
    join="inner",
    model_name="TorchMRVI",
    collection_val=collection,
)
```

```python
print(datamodule.n_obs, datamodule.n_vars, datamodule.n_batch)
```

## Train mrVI with LaminDB

We will initialize the MRVI model with its "pytorch" backend. A JAX backend version can be also be used using backend="jax".

```python
# Init the model
model = MRVI(registry=datamodule.registry, backend="torch")
```

```python
# Training the model (for 5M cells will take 1 day+ with early stopping - better to cancel it)
import time

gc.collect()
start = time.time()
model.train(
    max_epochs=50,
    # early_stopping=True,
    plan_kwargs={"lr": 1e-3, "n_epochs_kl_warmup": 40},
    datamodule=datamodule,
    batch_size=1024,
    # early_stopping_patience=5,
    # check_val_every_n_epoch=1,
    # datasplitter_kwargs={
    #    "external_indexing": [np.array(train_ind), np.array(valid_ind)]
    # }
)
end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
```

```python
model.history.keys()
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

```python
# Save the model
model.save(
    "mrvi_torch_tahoe100_lamin_model", save_anndata=False, overwrite=True, datamodule=datamodule
)
```

```python
# Load the model
# model = MRVI.load("mrvi_torch_tahoe100_lamin_model", adata=False)
```

```python
# We extract the adata of the model, to be able to use it for plot umaps
# To save time we could also select a sub set of it
adata = collection.load(join="inner")
adata
```

```python
adata.obs.plate.value_counts()
```

```python
# merge metadata (will add memory)
# adata.obs = adata.obs.merge(tahoe_hubmodel.model.adata.obs[["Cell_Name_Vevo",
# "dataset","phase","observed_lib_size","S_score","G2M_score","sublibrary"]],
# how='left', left_on='BARCODE_SUB_LIB_ID', right_index=True)
```

```python
adata
```

```python
# In order to save memory for the sake of this tutorial we drop the
# count matrix from this adata (like done during minification)
from scipy.sparse import csr_matrix

del adata.raw
adata.X = csr_matrix(adata.X.shape)
```

```python
# The way to extract the internal model analysis is by the inference_dataloader
# Datamodule will always require to pass it into all downstream functions.
inference_dataloader = datamodule.inference_dataloader(
    batch_size=1024, parallel_cpu_count=5, shuffle=False
)
```

```python
gc.collect()
```

```python
latent_representation = model.get_latent_representation(
    give_z=False, dataloader=inference_dataloader
)
```

```python
latent_representation.shape
```

We removed the count layer from the adata therefore we cant run PCA like before

```python
# adata.layers["counts"] = adata.X.copy()  # preserve counts
# sc.pp.normalize_total(adata, target_sum=1e4)
# sc.pp.log1p(adata)
# adata.raw = adata  # freeze the state in `.raw`
```

```python
# run PCA then generate UMAP plots
# sc.tl.pca(adata)
# sc.pp.neighbors(adata)
# sc.tl.umap(adata, min_dist=0.1)
```

```python
# sc.pl.umap(
#    adata,
#    color=["plate", "cell_line_id"],
#    ncols=2,
#    frameon=False,
# )
```

```python
adata.obsm["X_mrVI_Torch_Lamin"] = latent_representation
```

```python
# Subsample the adata to save time and memory
adata_subsampled = adata[
    list(np.random.choice(np.arange(adata.n_obs), size=100000, replace=False)), :
].copy()
```

```python
adata_subsampled.obsm["X_mrVI_Torch_Lamin"].shape
```

```python
sc.pp.neighbors(adata_subsampled, use_rep="X_mrVI_Torch_Lamin")
sc.tl.umap(adata_subsampled, min_dist=0.3)
```

```python
sc.pl.umap(
    adata_subsampled,
    color=["plate", "cell_line_id"],
    frameon=False,
    ncols=2,
)
```

We also didnt use the metadata

```python
# sc.pl.umap(
#    adata,
#    color=["moa-broad","phase"],
#    frameon=False,
#    ncols=2,
# )
```

```python
# sc.pl.umap(
#    adata,
#    color=["observed_lib_size","S_score","G2M_score"],
#    frameon=False,
#    ncols=3,
# )
```

## Compare results

```python
from scib_metrics.benchmark import BatchCorrection, Benchmarker, BioConservation
```

```python
bm = Benchmarker(
    adata[list(np.random.choice(np.arange(adata.n_obs), size=10000, replace=False)), :],
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
    embedding_obsm_keys=["X_mrVI_Torch_Lamin"],
    n_jobs=-1,
)
bm.benchmark()
```

```python
bm.plot_results_table(min_max_scale=False)
```
