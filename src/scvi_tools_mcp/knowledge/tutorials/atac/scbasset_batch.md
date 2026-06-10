# scBasset: Batch correction of scATACseq data

```{warning}
SCBASSET's development is still in progress. The current version may not fully reproduce the original implementation's results.
```

In addition to performing [representation learning on scATAC-seq data](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/atac/scbasset.html), scBasset can also be used to integrate data across several samples. This tutorial walks through the following:

1. Loading the dataset
1. Preprocessing the dataset with `scanpy`
1. Setting up and training the model
1. Visualizing the batch-corrected latent space with `scanpy`
1. Quantifying integration performance with `scib-metrics`

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

import matplotlib.pyplot as plt
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scib_metrics.benchmark import Benchmarker

scvi.settings.seed = 0
sc.set_figure_params(figsize=(4, 4), frameon=False)
%config InlineBackend.print_figure_kwargs={'facecolor' : "w"}
%config InlineBackend.figure_format='retina'
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

## Loading the dataset

We will use the dataset from [Buenrostro et al., 2018](https://pubmed.ncbi.nlm.nih.gov/29706549/) throughout this tutorial, which contains single-cell chromatin accessibility profiles across 10 populations of human hematopoietic cell types.

```python
adata = sc.read(
    "data/buen_ad_sc.h5ad",
    backup_url="https://storage.googleapis.com/scbasset_tutorial_data/buen_ad_sc.h5ad",
)
adata
```

We see that batch information is stored in `adata.obs["batch"]`. In this case, batches correspond to different donors.

```python
BATCH_KEY = "batch"
adata.obs[BATCH_KEY].value_counts()
```

We also have author-provided cell type labels available.

```python
LABEL_KEY = "label"
adata.obs[LABEL_KEY].value_counts()
```

## Preprocessing the dataset

We now use `scanpy` to preprocess the data before giving it to the model. In our case, we filter out peaks that are rarely detected (detected in less than 5% of cells) in order to make the model train faster.

```python
print("before filtering:", adata.shape)
min_cells = int(adata.n_obs * 0.05)  # threshold: 5% of cells
sc.pp.filter_genes(adata, min_cells=min_cells)  # in-place filtering of regions
print("after filtering:", adata.shape)
```

Taking a look at `adata.var`, we see that this dataset has already been processed to include the `start` and `end` positions of each peak, as well as the chromosomes on which they are located.

```python
adata.var.sample(10)
```

We will use this information to add DNA sequences into `adata.varm`. This can be performed in-place with `scvi.data.add_dna_sequence`.

```python
scvi.data.add_dna_sequence(
    adata,
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
    genome_name="hg19",
    genome_dir="data",
)
adata
```

The function adds two new fields into `adata.varm`: `dna_sequence`, containing bases for each position, and `dna_code`, containing bases encoded as integers.

```python
adata.varm["dna_sequence"]
```

## Setting up and training the model

Now, we are readyto register our data with `scvi`. We set up our data with the model using `setup_anndata`, which will ensure everything the model needs is in place for training.

In this stage, we can condition the model on covariates, which encourages the model to remove the impact of those covariates from the learned latent space. Since we are integrating our data across donors, we set the `batch_key` argument to the key in `adata.obs` that contains donor information (in our case, just `"batch"`).

Additionally, since scBasset considers training mini-batches across regions rather than observations, we transpose the data prior to giving it to the model. The model also expects binary accessibility data, so we add a new layer with binary information.

```python
# alternatively load the local preprocessed data
# import os
# temp_dir_obj = tempfile.TemporaryDirectory()

# adata_path = os.path.join(temp_dir_obj.name, "adata_scbasset_batch.h5ad")
# adata = sc.read(adata_path, backup_url="https://exampledata.scverse.org/scvi-tools/adata_scbasset_batch.h5ad")
# adata
```

```python
bdata = adata.transpose()
bdata.layers["binary"] = (bdata.X.copy() > 0).astype(float)
scvi.external.SCBASSET.setup_anndata(
    bdata, layer="binary", dna_code_key="dna_code", batch_key=BATCH_KEY
)
```

We now create the model. We use a non-default argument (`l2_reg_cell_embedding`), which is designed to aid integration of scATAC-seq data.

```python
model = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=1e-8)
model.view_anndata_setup()
```

```python
model.train(
    max_epochs=150,
)
```

```python
fig, ax = plt.subplots()
model.history_["auroc_train"].plot(ax=ax)
model.history_["auroc_validation"].plot(ax=ax)
```

## Visualizing the batch-corrected latent space

After training, we retrieve the integrated latent space and save it into `adata.obsm`.

```python
LATENT_KEY = "X_scbasset"
adata.obsm[LATENT_KEY] = model.get_latent_representation()
adata.obsm[LATENT_KEY].shape
```

Now, we use `scanpy` to visualize the latent space by first computing the k-nearest-neighbor graph and then computing its TSNE representation with parameters to reproduce the original scBasset tutorial for this dataset.

```python
sc.pp.neighbors(adata, use_rep=LATENT_KEY)
sc.tl.umap(adata, min_dist=1.0)
```

```python
sc.pl.umap(adata, color=LABEL_KEY)
```

```python
sc.pl.umap(adata, color=BATCH_KEY)
```

## Quantifying integration performance

Here we use the [scib-metrics](https://scib-metrics.readthedocs.io/en/stable/) package, which contains scalable implementations of the metrics used in the scIB benchmarking suite. We can use these metrics to assess the quality of the integration.

```python
bm = Benchmarker(
    adata,
    batch_key=BATCH_KEY,
    label_key=LABEL_KEY,
    embedding_obsm_keys=[LATENT_KEY],
    n_jobs=-1,
)
bm.benchmark()
```

```python
df = bm.get_results(min_max_scale=False)
```

```python
bm.plot_results_table(min_max_scale=False)
```
