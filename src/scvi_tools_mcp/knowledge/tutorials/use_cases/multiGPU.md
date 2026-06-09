# Train a scVI model using multiGPU

In this simple tutorial, we will show hot to train an scvi-tools model using multiGPU.

SCVI-Tools v1.3.0 now support training on a multi GPU system, which can significantly speed up training and allow you to handle larger datasets. It is supported only on Nvidia GPUs and DDP with CUDA backend.

We will start by downloading sample dataset and perform the standrad preprocessing

```python
import tempfile

import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.model import SCVI
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
adata = scvi.data.heart_cell_atlas_subsampled(save_path=".")
```

```python
sc.pp.filter_genes(adata, min_counts=3)
```

```python
adata.layers["counts"] = adata.X.copy()  # preserve counts
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata  # freeze the state in `.raw`
```

```python
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=1200,
    subset=True,
    layer="counts",
    flavor="seurat_v3",
    batch_key="cell_source",
)
```

```python
adata
```

```python
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",
    categorical_covariate_keys=["cell_source", "donor"],
    continuous_covariate_keys=["percent_mito", "percent_ribo"],
)
```

Lets compare the runtime of a single vs multigpu (X2) train for this small dataset (2 sessions of ddp cant be run in same session so we present the result of running single GPU here)

```python
# model_no_multigpu = SCVI(adata)
```

```python
# import time
# print("Single GPU SCVI train")
# start = time.time()
# model_no_multigpu.train(
#    max_epochs=100,
#    check_val_every_n_epoch=1,
# )
# print("done")
# end = time.time()
# print(f"Elapsed time: {end - start:.2f} seconds")
# Elapsed time: 62.12 seconds
```

```python
model = SCVI(adata)
```

Here we will set specific parameters (accelerator, devices and strategy) to be able to run this tutorial in an interactive environment such as jupyter or colab notebooks

```python
datasplitter_kwargs = {}
datasplitter_kwargs["drop_dataset_tail"] = True
datasplitter_kwargs["drop_last"] = False
```

```python
import time

print("multi GPU SCVI train")
start2 = time.time()
model.train(
    max_epochs=100,
    check_val_every_n_epoch=1,
    accelerator="gpu",
    devices=-1,
    datasplitter_kwargs=datasplitter_kwargs,
    strategy="ddp_notebook_find_unused_parameters_true",
)
print("done")
end2 = time.time()
print(f"Elapsed time: {end2 - start2:.2f} seconds")
```

```python
model
```

```python
assert model.is_trained
```

Model was trained and as can be seen faster than the single GPU version. If the data was larger we would have seen this gap increase.
We will continue the down stream analysis in the same manner as was previously done in other tutorials (get the latent representation, save and load the model and plot umaps of the embeddings.

```python
SCVI_LATENT_KEY = "X_scVI"
latent = model.get_latent_representation()
adata.obsm[SCVI_LATENT_KEY] = latent
latent.shape
```

```python
model.save("scvi_model", overwrite=True)
```

```python
model = scvi.model.SCVI.load("scvi_model", adata=adata)
```

```python
model
```

```python
# run PCA then generate UMAP plots
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_pcs=30, n_neighbors=20)
sc.tl.umap(adata, min_dist=0.3)
```

```python
sc.pl.umap(
    adata,
    color=["cell_type"],
    frameon=False,
)
sc.pl.umap(
    adata,
    color=["donor", "cell_source"],
    ncols=2,
    frameon=False,
)
```

```python
# use scVI latent space for UMAP generation
sc.pp.neighbors(adata, use_rep=SCVI_LATENT_KEY)
sc.tl.umap(adata, min_dist=0.3)
```

```python
sc.pl.umap(
    adata,
    color=["cell_type"],
    frameon=False,
)
sc.pl.umap(
    adata,
    color=["donor", "cell_source"],
    ncols=2,
    frameon=False,
)
```

```python
# neighbors were already computed using scVI
SCVI_CLUSTERS_KEY = "leiden_scVI"
sc.tl.leiden(adata, key_added=SCVI_CLUSTERS_KEY, resolution=0.5)
```

```python
sc.pl.umap(
    adata,
    color=[SCVI_CLUSTERS_KEY],
    frameon=False,
)
```
