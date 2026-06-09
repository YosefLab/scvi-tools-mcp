# Stereoscope applied to left ventricule data

- Developed by Carlos Talavera-López Ph.D, WSI, edited by Romain Lopez
- Version: 210301

In this notebook, we present the workflow to run Stereoscope within the scvi-tools codebase. We map the adult heart cell atlas data from [Litviňuková et al (2020)](https://www.nature.com/articles/s41586-020-2797-4). This experiment takes around one hour to run on Colab.

You can access the raw count matrices as 'anndata' objects at www.heartcellatlas.org.

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
import numpy as np
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.external import RNAStereoscope, SpatialStereoscope
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

## Download single-cell data

Read in expression data. This is a subset of the data you want to map. Here I use a balanced subset of cells from the left ventricle (~ 50K). You can create your own subset according to what you are interested in.

```python
adata_path = os.path.join(save_dir.name, "adata.h5ad")

sc_adata = sc.read(
    adata_path,
    backup_url="https://ndownloader.figshare.com/files/26153564",
)
sc_adata
```

## Preprocess single-cell data

```python
sc.pp.filter_genes(sc_adata, min_counts=10)
sc_adata
```

```python
sc_adata.obs["combined"] = [
    sc_adata.obs.loc[i, "cell_source"] + sc_adata.obs.loc[i, "donor"] for i in sc_adata.obs_names
]
sc_adata
```

Remove mitochondrial genes

```python
non_mito_genes_list = [name for name in sc_adata.var_names if not name.startswith("MT-")]
sc_adata = sc_adata[:, non_mito_genes_list]
sc_adata
```

Normalize data on a different layer, because Stereoscope works with raw counts. We did not see better results by using all the genes, so for computational purposed we cut here to 7,000 genes.

```python
sc_adata.layers["counts"] = sc_adata.X.copy()
sc.pp.normalize_total(sc_adata, target_sum=1e5)
sc.pp.log1p(sc_adata)
sc_adata.raw = sc_adata
```

```python
sc.pp.highly_variable_genes(
    sc_adata,
    n_top_genes=7000,
    subset=True,
    layer="counts",
    flavor="seurat_v3",
    batch_key="combined",
    span=1,
)
```

Examine the cell type labels

```python
sc_adata.obs["cell_states"].value_counts()
```

## Read in visium data

```python
st_adata = sc.datasets.visium_sge(sample_id="V1_Human_Heart")
st_adata.var_names_make_unique()
```

```python
st_adata.var["mt"] = st_adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(st_adata, qc_vars=["mt"], inplace=True)
st_adata
```

- Clean up data based on QC values

```python
fig, axs = plt.subplots(1, 4, figsize=(10, 2))
sns.distplot(st_adata.obs["total_counts"], kde=False, ax=axs[0])
sns.distplot(
    st_adata.obs["total_counts"][st_adata.obs["total_counts"] < 20000],
    kde=False,
    bins=60,
    ax=axs[1],
)
sns.distplot(st_adata.obs["n_genes_by_counts"], kde=False, bins=60, ax=axs[2])
sns.distplot(
    st_adata.obs["n_genes_by_counts"][st_adata.obs["n_genes_by_counts"] < 1000],
    kde=False,
    bins=60,
    ax=axs[3],
)
plt.tight_layout()
plt.show()
```

```python
sc.pp.filter_cells(st_adata, min_counts=500)
sc.pp.filter_cells(st_adata, min_genes=500)
sc.pl.violin(
    st_adata,
    ["n_genes_by_counts", "total_counts", "pct_counts_mt"],
    jitter=0.25,
    multi_panel=True,
)
st_adata
```

```python
sc.pl.spatial(st_adata, img_key="hires", color=["TTN"])
```

## Learn cell-type specific gene expression from scRNA-seq data

Filter genes to be the same on the spatial data

```python
intersect = np.intersect1d(sc_adata.var_names, st_adata.var_names)
st_adata = st_adata[:, intersect].copy()
sc_adata = sc_adata[:, intersect].copy()
```

Setup the AnnData object

```python
RNAStereoscope.setup_anndata(sc_adata, layer="counts", labels_key="cell_states")
```

Train the _scRNA-Seq_ model

```python
sc_model_path = os.path.join(save_dir.name, "sc_model")

sc_model = RNAStereoscope(sc_adata)
sc_model.train(max_epochs=100)
sc_model.history["elbo_train"][10:].plot()
sc_model.save(sc_model_path, overwrite=True)
```

## Infer proportion for spatial data

```python
st_adata.layers["counts"] = st_adata.X.copy()
SpatialStereoscope.setup_anndata(st_adata, layer="counts")
```

Train _Visium_ model

```python
spatial_model_path = os.path.join(save_dir.name, "spatial_model")

spatial_model = SpatialStereoscope.from_rna_model(st_adata, sc_model)
spatial_model.train(max_epochs=2000)
spatial_model.history["elbo_train"][10:].plot()
spatial_model.save(spatial_model_path, overwrite=True)
```

## Deconvolution results

```python
st_adata.obsm["deconvolution"] = spatial_model.get_proportions()

# also copy as single field in the anndata for visualization
for ct in st_adata.obsm["deconvolution"].columns:
    st_adata.obs[ct] = st_adata.obsm["deconvolution"][ct]
```

### Visualise populations

Et voilá, we have now an anndata object that contains the inferred proportions on each Visium spot for each cell type in our single cell reference dataset.

In this example we can observe how nicely the arterial endotehlial cells (EC5_art) and the venous endothelial cells (EC6_ven) are highlighted in the areas were we expect to see cardiac vessels based on the histology of the sample.

```python
# low dpi for uploading to github
sc.settings.set_figure_params(
    dpi=60, color_map="RdPu", dpi_save=200, vector_friendly=True, format="svg"
)
sc.pl.spatial(
    st_adata,
    img_key="hires",
    color=["EC5_art", "EC6_ven"],
    size=1.2,
    color_map="inferno",
)
```
