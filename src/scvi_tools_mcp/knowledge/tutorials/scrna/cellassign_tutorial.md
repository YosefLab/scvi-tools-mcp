# Annotation with CellAssign

## Assigning single-cell RNA-seq data to known cell types

CellAssign is a probabilistic model that uses prior knowledge of cell-type marker genes to annotate scRNA data into predefined cell types. Unlike other methods for assigning cell types, CellAssign does not require labeled single cell data and only needs to know whether or not each given gene is a marker of each cell type. The original paper and R code are linked below.

Paper: [Probabilistic cell-type assignment of single-cell RNA-seq for tumor microenvironment profiling, *Nature Methods 2019*](https://www.nature.com/articles/s41592-019-0529-1)

Code: https://github.com/Irrationone/cellassign

This notebook will demonstrate how to use CellAssign on follicular lymphoma and HGSC scRNA data.

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import os
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.external import CellAssign
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

To demonstrate CellAssign, we use the data from the original publication, which we converted into h5ad format. The data are originally available from here:

https://zenodo.org/record/3372746

```python
sce_follicular_path = os.path.join(save_dir.name, "sce_follicular.h5ad")
sce_hgsc_path = os.path.join(save_dir.name, "sce_hgsc.h5ad")
fl_celltype_path = os.path.join(save_dir.name, "fl_celltype.csv")
hgsc_celltype_path = os.path.join(save_dir.name, "hgsc_celltype.csv")
```

```python
os.system("wget -q https://ndownloader.figshare.com/files/27458798 -O " + sce_follicular_path)
os.system("wget -q https://ndownloader.figshare.com/files/27458822 -O " + sce_hgsc_path)
os.system("wget -q https://ndownloader.figshare.com/files/27458828 -O " + hgsc_celltype_path)
os.system("wget -q https://ndownloader.figshare.com/files/27458831 -O " + fl_celltype_path)
```

## Follicular Lymphoma Data

Load follicular lymphoma data and marker gene matrix (see Supplementary Table 2 from the original paper).

```python
follicular_adata = sc.read(sce_follicular_path)
fl_celltype_markers = pd.read_csv(fl_celltype_path, index_col=0)

follicular_adata.obs.index = follicular_adata.obs.index.astype("str")
follicular_adata.var.index = follicular_adata.var.index.astype("str")
follicular_adata.var_names_make_unique()
follicular_adata.obs_names_make_unique()

follicular_adata
```

### Create and fit CellAssign model

The anndata object and cell type marker matrix should contain the same genes, so we index into `adata` to include only the genes from `marker_gene_mat`.

```python
follicular_bdata = follicular_adata[:, fl_celltype_markers.index].copy()
```

Then we setup anndata and initialize a `CellAssign` model. Here we set the `size_factor_key` to "size_factor", which is a column in `bdata.obs`.

```{note}
A size factor may be defined manually as scaled library size (total UMI count) and should not be placed on the log scale, as the model will do this manually. The library size should be computed before any gene subsetting (in this case, technically, a few notebook cells up).
```

This can be acheived as follows:

```python
lib_size = adata.X.sum(1)
adata.obs["size_factor"] = lib_size / np.mean(lib_size)
```

```python
scvi.external.CellAssign.setup_anndata(follicular_bdata, size_factor_key="size_factor")
```

```python
follicular_model = CellAssign(follicular_bdata, fl_celltype_markers)
follicular_model.train()
```

Inspecting the convergence:

```python
follicular_model.history["elbo_validation"].plot()
```

### Predict and plot assigned cell types

Predict the soft cell type assignment probability for each cell.

```python
predictions = follicular_model.predict()
predictions.head()
```

We can visualize the probabilities of assignment with a heatmap that returns the probability matrix for each cell and cell type.

```python
sns.clustermap(predictions, cmap="viridis")
```

We then create a UMAP plot labeled by maximum probability assignments from the CellAssign model. The left plot contains the true cell types and the right plot contains our model's predictions.

```python
follicular_bdata.obs["cellassign_predictions"] = predictions.idxmax(axis=1).values
```

```python
# celltype is the original CellAssign prediction
sc.pl.umap(
    follicular_bdata,
    color=["celltype", "cellassign_predictions"],
    frameon=False,
    ncols=1,
)
```

### Model reproducibility

We see that the scvi-tools implementation highly reproduces the original implementation's predictions.

```python
df = follicular_bdata.obs
confusion_matrix = pd.crosstab(
    df["cellassign_predictions"],
    df["celltype"],
    rownames=["cellassign_predictions"],
    colnames=["Original predictions"],
)
confusion_matrix /= confusion_matrix.sum(1).ravel().reshape(-1, 1)
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(
    confusion_matrix,
    cmap=sns.diverging_palette(245, 320, s=60, as_cmap=True),
    ax=ax,
    square=True,
    cbar_kws={"shrink": 0.4, "aspect": 12},
)
```

## HGSC Data

We can repeat the same process for HGSC data.

```python
hgsc_adata = scvi.data.read_h5ad(sce_hgsc_path)
hgsc_celltype_markers = pd.read_csv(hgsc_celltype_path, index_col=0)

hgsc_adata.var_names_make_unique()
hgsc_adata.obs_names_make_unique()

hgsc_adata
```

### Create and fit CellAssign model

```python
hgsc_bdata = hgsc_adata[:, hgsc_celltype_markers.index].copy()
```

```python
scvi.external.CellAssign.setup_anndata(hgsc_bdata, "size_factor")
```

```python
hgsc_model = CellAssign(hgsc_bdata, hgsc_celltype_markers)
hgsc_model.train()
```

```python
hgsc_model.history["elbo_validation"].plot()
```

### Predict and plot assigned cell types

```python
predictions_hgsc = hgsc_model.predict()
```

```python
predictions.head()
```

```python
sns.clustermap(predictions_hgsc, cmap="viridis")
```

```python
hgsc_bdata.obs["cellassign_predictions"] = predictions_hgsc.idxmax(axis=1).values
```

```python
sc.pl.umap(
    hgsc_bdata,
    color=["celltype", "cellassign_predictions"],
    ncols=1,
    frameon=False,
)
```

### Model reproducibility

```
```

```python
df = hgsc_bdata.obs
confusion_matrix = pd.crosstab(
    df["cellassign_predictions"],
    df["celltype"],
    rownames=["cellassign_predictions"],
    colnames=["Original predictions"],
)
confusion_matrix /= confusion_matrix.sum(1).ravel().reshape(-1, 1)
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(
    confusion_matrix,
    cmap=sns.diverging_palette(245, 320, s=60, as_cmap=True),
    ax=ax,
    square=True,
    cbar_kws={"shrink": 0.4, "aspect": 12},
)
```
