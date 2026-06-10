# Train a scVI model using Anncollection dataloader wrapper

In this tutorial we will show how to apply the annCollection wrapper in scvi-tools to load and train SCANVI model on several adata's that are stored on disk

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
from pathlib import Path

import anndata
import gdown
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import seaborn as sns
import torch
from anndata.experimental import AnnCollection
from scipy import sparse as sp
from scvi.dataloaders import CollectionAdapter
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

We will use 2 types of datasets : PBMC and Covid data, both from SCVI datasets repo

```python
# the data is from this scvi reproducibility notebook
# https://yoseflab.github.io/scvi-tools-reproducibility/scarches_totalvi_seurat_data/
if Path("./pbmc_seurat_v4.h5ad").exists() and Path("./covid_cite.h5ad").exists():
    print("Data already downloaded")
else:
    gdown.download(
        url="https://drive.google.com/uc?id=1X5N9rOaIqiGxZRyr1fyZ6NpDPeATXoaC",
        output="pbmc_seurat_v4.h5ad",
        quiet=False,
    )
    gdown.download(
        url="https://drive.google.com/uc?id=1JgaXNwNeoEqX7zJL-jJD3cfXDGurMrq9",
        output="covid_cite.h5ad",
        quiet=False,
    )
```

## Preprocessing of the data

```python
covid = sc.read("covid_cite.h5ad")
pbmc = sc.read("pbmc_seurat_v4.h5ad")
```

```python
pbmc.obs["dataset"] = "pbmc"
```

```python
covid.obs["dataset"] = "covid"
```

```python
# take annotations from the `pbmc` dataset and leave annotations in `covid` as an Unknown (test)
covid.obs["celltype.l1"] = "Unknown"
```

Note covid datasets has more genes than the pbmc. We manualy inersect the correct genes.

```python
covid = covid[:, list(pbmc.var.index)]
```

```python
# create a fake counts layer to test training
covid.layers["test"] = covid.X.copy()
pbmc.layers["test"] = pbmc.X.copy()
covid.raw = covid
pbmc.raw = pbmc
```

```python
covid
```

```python
pbmc
```

```python
# create an AnnCollection on a subset of the data
# we're subsetting purely for speed
adata = AnnCollection(
    [covid, pbmc],
    join_vars="inner",
    join_obs="inner",
    label="dataset",
)
adata
```

```python
collection_adapter = CollectionAdapter(adata)
collection_adapter
```

```python
collection_adapter.adatas[0].X
```

But in this case we will run HVG selection first for both adatas together

```python
# have an object of 2 adatas from the collection concatenated together
adatas = anndata.concat([collection_adapter.adatas[0], collection_adapter.adatas[1]])
```

we will do the usuall HVG selection and count transformation on the data

```python
sc.pp.filter_genes(adatas, min_counts=3)
```

```python
sc.pp.normalize_total(adatas, target_sum=1e4)
sc.pp.log1p(adatas)
```

```python
sc.pp.highly_variable_genes(
    adatas,
    n_top_genes=1000,
    subset=True,
    layer="test",
    flavor="seurat_v3",
    batch_key="dataset",
)
```

```python
adatas
```

We can now save the adatas to disk to be used in anncollection

```python
adatas[adatas.obs.dataset == "covid"]
```

```python
adatas[adatas.obs.dataset == "pbmc"].write("pbmc_subset.h5ad")
```

```python
adatas[adatas.obs.dataset == "covid"].write("covid_subset.h5ad")
```

## Reload data after preprocessing into an AnndataCollection

```python
# we load the adataq in backed disk mode
covid_subset = sc.read("covid_subset.h5ad", backed="r")
pbmc_subset = sc.read("pbmc_subset.h5ad", backed="r")
```

Note that our count data is in a sparse form, which is the only one supported currently when using the AnnCollection Wrapper in SCVI-Tools

```python
# create an AnnCollection on a subset of the adata's
adata = AnnCollection(
    [covid_subset, pbmc_subset],
    join_vars="inner",
    join_obs="inner",
    label="dataset",
)
print(adata)
```

### Build a wrapper AnnData around the collection

```python
collection_adapter = CollectionAdapter(adata)
collection_adapter
```

```python
sp.issparse(collection_adapter.layers["test"])
```

```python
scvi.model.SCANVI.setup_anndata(
    collection_adapter,
    layer="test",
    batch_key="dataset",
    labels_key="celltype.l1",
    unlabeled_category="Unknown",
)
```

```python
model = scvi.model.SCANVI(collection_adapter, n_latent=10)
```

```python
# we're only training for a few epochs to show it works
model.train(max_epochs=25, early_stopping=True)
```

```python
SCANVI_LATENT_KEY = "X_scanVI"
latent = model.get_latent_representation()
latent.shape
```

```python
adatas.obsm[SCANVI_LATENT_KEY] = latent
```

Generate predictions that will include the covid unknown cells types

```python
predictions = model.predict(collection_adapter)
```

```python
adatas.obs["predictions_scanvi"] = predictions
```

```python
adata.obs["predictions_scanvi"] = predictions
```

```python
collection_adapter.obs["predictions_scanvi"] = predictions
```

Lets compare the PCA vs SCANVI Integrations UMAP results.
In order to show the UMAP's we will save the generated embeddings in the adatas object.

```python
# run PCA then generate UMAP plots
sc.tl.pca(adatas)
sc.pp.neighbors(adatas, n_pcs=30, n_neighbors=20)
sc.tl.umap(adatas, min_dist=0.3)
```

```python
sc.pl.umap(
    adatas,
    color=["predictions_scanvi", "dataset"],
    frameon=False,
)
```

And for SCANVI Intgeration

```python
# use scVI latent space for UMAP generation
sc.pp.neighbors(adatas, use_rep=SCANVI_LATENT_KEY)
sc.tl.umap(adatas, min_dist=0.3)
```

```python
sc.pl.umap(
    adatas,
    color=["predictions_scanvi", "dataset"],
    frameon=False,
)
```

```python
# neighbors were already computed using scVI
SCVI_CLUSTERS_KEY = "leiden_scVI"
sc.tl.leiden(adatas, key_added=SCVI_CLUSTERS_KEY, resolution=0.5)
```

```python
sc.pl.umap(
    adatas,
    color=[SCVI_CLUSTERS_KEY],
    frameon=False,
)
```

Confusion Matrix

```python
df = adatas.obs.groupby(["celltype.l1", "predictions_scanvi"]).size().unstack(fill_value=0)
norm_df = df / df.sum(axis=0)
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
_ = plt.pcolor(norm_df)
_ = plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90)
_ = plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xlabel("Predicted")
plt.ylabel("Observed")
```

```python
pd.crosstab(adatas.obs["celltype.l1"], adatas.obs["predictions_scanvi"])
```

## Compare results

```python
from scib_metrics.benchmark import Benchmarker

bm = Benchmarker(
    adatas[list(np.random.choice(np.arange(adatas.n_obs), size=10000, replace=False)), :],
    batch_key="dataset",
    label_key="predictions_scanvi",
    embedding_obsm_keys=["X_pca", "X_scanVI"],
    n_jobs=-1,
)
bm.benchmark()
```

```python
bm.plot_results_table(min_max_scale=False)
```

Save and load model

```python
model.save("model_scanvi_anncollection", save_anndata=False, overwrite=True)

# Load model again
loaded_model = scvi.model.SCANVI.load("model_scanvi_anncollection", adata=collection_adapter)
loaded_model
```

```python
# We can continue training the loaded model
loaded_model.train(max_epochs=1)
```

```python
# loaded_model.registry
```
