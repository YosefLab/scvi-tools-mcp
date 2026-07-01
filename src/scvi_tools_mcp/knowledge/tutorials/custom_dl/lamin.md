# Train a scVI model using Lamin

This notebook demonstrates a scalable approach to training an [scVI](https://docs.scvi-tools.org/en/latest/user_guide/models/scvi.html) model on Census data using [Lamin](https://lamin.ai/) dataloader.
LaminDB is a database system based on its MappedCollection designed to support efficient storage, management, and querying of scientific data, particularly in machine learning, bioinformatics, and data science applications. It allows for the easy organization, sharing, and querying of complex datasets, such as those involved in research, experiments, or models.
See [here](https://docs.scvi-tools.org/en/stable/user_guide/use_case/custom_dataloaders.html) for more information

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import time

import scanpy as sc
import scvi
from scvi.dataloaders import MappedCollectionDataModule
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

Well start by init the lamindb backend and read the known PBMC data

```python
# os.system("lamin init --storage ./lamindb_collection")
import lamindb as ln
# ln.setup.init()
```

```python
pbmc_dataset = scvi.data.pbmc_dataset(
    save_path=".",
    remove_extracted_data=True,
)
```

```python
pbmc_seurat_v4_cite_seq = scvi.data.pbmc_seurat_v4_cite_seq(save_path=".")
```

### Preprocessing of the data

In this case we read 2 PBMC data so that we will later show the integration power.
We will select the intersection of those 2 datasets gene names, and consolidate cell types names so that they will be alligned

```python
pbmc_seurat_v4_cite_seq.obs["batch"] = pbmc_seurat_v4_cite_seq.obs.Phase
```

```python
pbmc_seurat_v4_cite_seq.obs["batch"] = pbmc_seurat_v4_cite_seq.obs["batch"].astype("str")
pbmc_dataset.obs["batch"] = pbmc_dataset.obs["batch"].astype("str")
```

```python
import numpy as np

gene_intersection = np.intersect1d(
    pbmc_dataset.var.gene_symbols.values, pbmc_seurat_v4_cite_seq.var.index.values
)
pbmc_dataset_filtered = pbmc_dataset[:, pbmc_dataset.var["gene_symbols"].isin(gene_intersection)]
pbmc_seurat_v4_cite_seq_filtered = pbmc_seurat_v4_cite_seq[
    :, pbmc_seurat_v4_cite_seq.var_names.isin(gene_intersection)
]
```

```python
pbmc_dataset_filtered.var_names = pbmc_dataset_filtered.var["gene_symbols"].values
```

```python
pbmc_dataset_filtered.obs["cell_type"] = pbmc_dataset_filtered.obs["str_labels"].astype("str")
pbmc_dataset_filtered.obs.loc[
    pbmc_dataset_filtered.obs["cell_type"] == "FCGR3A+ Monocytes", "cell_type"
] = "Monocytes"
pbmc_dataset_filtered.obs.loc[
    pbmc_dataset_filtered.obs["cell_type"] == "CD14+ Monocytes", "cell_type"
] = "Monocytes"
pbmc_dataset_filtered.obs.loc[
    pbmc_dataset_filtered.obs["cell_type"] == "Megakaryocytes", "cell_type"
] = "Other"
```

```python
pbmc_dataset_filtered
```

The list of different cell types for the first dataaset can be seen 

```python
pbmc_dataset_filtered.obs["cell_type"].value_counts()
```

We will repeat for the other dataset

```python
pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] = pbmc_seurat_v4_cite_seq_filtered.obs[
    "celltype.l1"
].astype("str")
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "other", "cell_type"
] = "Other"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "B", "cell_type"
] = "B cells"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "DC", "cell_type"
] = "Dendritic Cells"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "NK", "cell_type"
] = "NK cells"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "CD4 T", "cell_type"
] = "CD4 T cells"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "CD8 T", "cell_type"
] = "CD8 T cells"
pbmc_seurat_v4_cite_seq_filtered.obs.loc[
    pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"] == "Mono", "cell_type"
] = "Monocytes"
```

```python
pbmc_seurat_v4_cite_seq_filtered
```

```python
pbmc_seurat_v4_cite_seq_filtered.obs["cell_type"].value_counts()
```

In the next part we are creating artifacts from those adata's and unite them to a collection.
Artifacts and collections are the ways lamindb interactes with the data.
From this point forward we will not use adatas again.

```python
ln.track()
```

```python
artifact1 = ln.Artifact.from_anndata(pbmc_dataset_filtered, key="part_one1.h5ad").save()
artifact2 = ln.Artifact.from_anndata(pbmc_seurat_v4_cite_seq_filtered, key="part_two1.h5ad").save()

collection = ln.Collection([artifact1, artifact2], key="gather")
collection.save()
```

```python
# We load the collection to see it consists of many h5ad files
artifacts = collection.artifacts.all()
artifacts.df()
```

we can now define the batch and data loader which replaces the default AnnDataloder of SCVI.

```python
batch_keys = "batch"
datamodule = MappedCollectionDataModule(
    collection,
    batch_key=batch_keys,
    batch_size=1024,
    shuffle=True,
    join="inner",
)
```

```python
print(datamodule.n_obs, datamodule.n_vars, datamodule.n_batch)
```

From here we continue like always, define the model (with the registry and not AnnDataManager ) and train it

```python
# Init the model
model = scvi.model.SCVI(registry=datamodule.registry)
```

```python
# Training the model
import gc

gc.collect()
start = time.time()
model.train(
    max_epochs=100,
    batch_size=1024,
    plan_kwargs={"lr": 0.003, "compile": False},
    early_stopping=False,
    datamodule=datamodule.inference_dataloader(),
)
end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")
```

```python
model.history["elbo_train"].tail()
```

```python
# Save the model
model.save("lamin_model", save_anndata=False, overwrite=True, datamodule=datamodule)
```

```python
model.history.keys()
```

```python
# The way to extract the internal model analysis is by the inference_dataloader
# Datamodule will always require to pass it into all downstream functions.
inference_dataloader = datamodule.inference_dataloader()
latent = model.get_latent_representation(dataloader=inference_dataloader)
```

```python
# We extract the adata of the model, to be able to use it for plot umaps
# To save time we could also select a sub set of it
adata = collection.load(join="inner")
```

```python
adata.obsm["scvi"] = latent
```

```python
adata.obs
```

```python
# We can now generate the neighbors and the UMAP.
sc.pp.neighbors(adata, use_rep="scvi", key_added="scvi")
sc.tl.umap(adata, neighbors_key="scvi")
```

```python
sc.pl.umap(adata, color=batch_keys, title="batch_SCVI")
```

```python
sc.pl.umap(adata, color="cell_type", title="cell_type_SCVI")
```

## scanvi

We will repeat the process just did for SCVI to run a SCANVI model

```python
labels_keys = "cell_type"
datamodule_scanvi = MappedCollectionDataModule(
    collection,
    batch_key=batch_keys,
    label_key=labels_keys,
    batch_size=1024,
    shuffle=True,
    model_name="SCANVI",
    join="inner",
)
```

```python
print(
    datamodule_scanvi.n_obs,
    datamodule_scanvi.n_vars,
    datamodule_scanvi.n_batch,
    datamodule_scanvi.n_labels,
)
```

```python
# We can now create the scanVI model object and train it:
datamodule_scanvi.setup(stage="train")
model_scanvi = scvi.model.SCANVI(
    adata=None,
    registry=datamodule_scanvi.registry,
    datamodule=datamodule_scanvi,
)
```

```python
# Training the model
import gc

gc.collect()
start3 = time.time()
model_scanvi.train(
    max_epochs=20,
    batch_size=1024,
    plan_kwargs={"lr": 0.01, "compile": False},
    early_stopping=False,
    n_samples_per_label=100,
    datamodule=datamodule_scanvi,
)
end3 = time.time()
print(f"Elapsed time: {end3 - start3:.2f} seconds")
```

```python
# Save the model
model_scanvi.save(
    "lamin_scanvi_model", save_anndata=False, overwrite=True, datamodule=datamodule_scanvi
)
```

```python
model_scanvi.history.keys()
```

```python
model_scanvi.history["train_accuracy"].tail()
```

```python
# The way to extract the internal model analysis is by the inference_dataloader
# Datamodule will always require to pass it into all downstream functions.
inference_scanvi_dataloader = datamodule_scanvi.inference_dataloader()
latent_scanvi = model_scanvi.get_latent_representation(dataloader=inference_scanvi_dataloader)
```

```python
adata.obsm["scanvi"] = latent_scanvi
```

```python
# We can now generate the neighbors and the UMAP.
sc.pp.neighbors(adata, use_rep="scanvi", key_added="scanvi")
sc.tl.umap(adata, neighbors_key="scanvi")
```

```python
sc.pl.umap(adata, color=batch_keys, title="batch_SCANVI")
```

```python
sc.pl.umap(adata, color="cell_type", title="cell_type_SCANVI")
```

Beucase its a scanvi model we can also produce the cell type predictions now

```python
adata.obs["predictions_scanvi"] = model_scanvi.predict(
    dataloader=inference_scanvi_dataloader, batch_size=1024
)
```

```python
df = adata.obs.groupby(["cell_type", "predictions_scanvi"]).size().unstack(fill_value=0)
norm_df = df / df.sum(axis=0)
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
_ = plt.pcolor(norm_df)
_ = plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90)
_ = plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xlabel("Predicted")
plt.ylabel("Observed")
```

## Run regulary using adata and compare

We will use the adata we already extracted and train an SCVI and SCANVI models under the 
same conditions as was done for Lamin, in order to compare the results

```python
adata.layers["counts"] = adata.X.copy()  # preserve counts
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata  # freeze the state in `.raw`
```

```python
adata.obs
```

```python
scvi.model.SCVI.setup_anndata(adata, batch_key="batch", layer="counts")
```

```python
# model_census3 = scvi.model.SCVI.load("census_model", adata=adata)
model_census3 = scvi.model.SCVI(adata)
```

```python
start2 = time.time()
model_census3.train(
    max_epochs=100,
)
end2 = time.time()
print(f"Elapsed time: {end2 - start2:.2f} seconds")
```

We can see that under same conditions, lamin training was faster by about 10% than using the AnnDataLoader

```python
model_census3.history["elbo_train"].tail()
```

```python
adata.obsm["scvi_non_dataloder"] = model_census3.get_latent_representation()
```

```python
sc.pp.neighbors(adata, use_rep="scvi_non_dataloder", key_added="scvi_non_dataloder")
sc.tl.umap(adata, neighbors_key="scvi_non_dataloder")
```

```python
sc.pl.umap(adata, color="batch", title="batch_SCVI_adata")
```

```python
sc.pl.umap(adata, color="cell_type", title="cell_type_SCVI_adata")
```

## scanvi (regular)

```python
adata
```

```python
scvi.model.SCANVI.setup_anndata(
    adata,
    layer="counts",
    labels_key="cell_type",
    unlabeled_category="label_0",
    batch_key=batch_keys,
)
```

```python
# model_census4 = scvi.model.SCVI.load("census_model", adata=adata)
model_census4 = scvi.model.SCANVI(adata)
```

```python
start4 = time.time()
model_census4.train(
    max_epochs=100,
)
end4 = time.time()
print(f"Elapsed time: {end4 - start4:.2f} seconds")
```

```python
model_census4.history["train_accuracy"].tail()
```

```python
adata.obsm["scanvi_non_dataloder"] = model_census4.get_latent_representation()
```

```python
sc.pp.neighbors(adata, use_rep="scanvi_non_dataloder", key_added="scanvi_non_dataloder")
sc.tl.umap(adata, neighbors_key="scanvi_non_dataloder")
```

```python
sc.pl.umap(adata, color=["batch"], title=["SCANVI__non_dataloder_" + x for x in ["batch"]])
```

```python
sc.pl.umap(adata, color="cell_type", title="SCANVI_non_dataloder")
```

```python
adata.obs["predictions_scanvi_non_dataloder"] = model_census4.predict()
```

```python
df = (
    adata.obs.groupby(["cell_type", "predictions_scanvi_non_dataloder"])
    .size()
    .unstack(fill_value=0)
)
norm_df = df / df.sum(axis=0)
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
_ = plt.pcolor(norm_df)
_ = plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90)
_ = plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xlabel("Predicted")
plt.ylabel("Observed")
```

## Compare results

Compute integration metrics

```python
from scib_metrics.benchmark import Benchmarker

bm = Benchmarker(
    adata,
    batch_key="batch",
    label_key="cell_type",
    embedding_obsm_keys=["X_pca", "scvi", "scanvi", "scvi_non_dataloder", "scanvi_non_dataloder"],
    n_jobs=-1,
)
bm.benchmark()
```

```python
bm.plot_results_table(min_max_scale=False)
```

As expected SCANVI outperforms the SCVI using the labels data, 
however as can be seen the regular use of Anndataloader dataloader
gives 5% better integration results comparing to the lamin dataloader
