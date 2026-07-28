# Preprocessing datasets for analysis with scVIVA-Tools

In this tutorial, we go over several preprocessing techniques for different types of data used with scVIVA-Tools models. Each section of this tutorial is independent from the other sections, and is relevant to other scVIVA-Tools tutorials which use the same type of dataset. For example, the preprocessing techniques used in the scRNA-seq section of this tutorial are generally used in the scVIVA-Tools scRNA-seq related tutorials. Relevant tutorials are linked in each section.

## Dependencies

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scviva-tools

```

## Imports and preparing files

```python
import os
import tempfile
from pathlib import Path

import anndata as ad
import numpy as np
import pooch
import scanpy as sc
import scviva
import scvi
import seaborn as sns
import torch
```

```python
scviva.settings.seed = 0
print("Last run with scVIVA-Tools version:", scviva.__version__)
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```{note}
You can modify `save_dir` below to change where the data files for this tutorial are saved.

You can modify `file_name` below to the name of the dataset you would like to preprocess. This file will end with .h5ad or .h5 depending on which model you plan to use.
```

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

## Spatial transciptomics

### Relevant Spatial transciptomics Tutorials

The following tutorial uses the exact preprocessed dataset that results from this section:

[Multi-resolution deconvolution of spatial transcriptomics](./DestVI_tutorial.ipynb)

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[ResolVI to address noise and biases in spatial transcriptomics](./resolVI_tutorial.ipynb)

[Introduction to gimVI](./gimvi_tutorial.ipynb)

[Spatial mapping with Tangram](./tangram_scvi_tools.ipynb)

[Stereoscope applied to left ventricule data](./stereoscope_heart_LV_tutorial.ipynb)

[Mapping human lymph node cell types to 10X Visium with Cell2location](./cell2location_lymph_node_spatial_tutorial.ipynb)

### Preprocessing

To demonstrate preprocessing for spatial transcriptomics, we use data from a comparative study of murine lymph nodes, comparing wild-type with a stimulation after injection of a mycobacteria. We have at disposal a 10x Visium dataset as well as a matching scRNA-seq dataset from the same tissue.

```python
url1 = os.path.join(save_dir.name, "ST-LN-compressed.h5ad")
st_adata = sc.read(
    url1, backup_url="https://exampledata.scverse.org/scvi-tools/ST-LN-compressed.h5ad"
)
st_adata
```

```python
url2 = os.path.join(save_dir.name, "scRNA-LN-compressed.h5ad")
sc_adata = sc.read(
    url2, backup_url="https://exampledata.scverse.org/scvi-tools/scRNA-LN-compressed.h5ad"
)
sc_adata
```

First, let’s load the single-cell data. We profiled immune cells from murine lymph nodes with 10x Chromium, as a control / case study to study the immune response to exposure to a mycobacteria (refer to DestVI paper for more info). It contains the raw counts (DestVI always takes raw counts as input).

```python
# let us filter some genes
G = 2000
sc.pp.filter_genes(sc_adata, min_counts=10)

sc_adata.layers["counts"] = sc_adata.X.copy()

sc.pp.highly_variable_genes(
    sc_adata, n_top_genes=G, subset=True, layer="counts", flavor="seurat_v3"
)

sc.pp.normalize_total(sc_adata, target_sum=10e4)
sc.pp.log1p(sc_adata)
sc_adata.raw = sc_adata
```

Load the spatial data

```python
st_adata.layers["counts"] = st_adata.X.copy()
st_adata.obsm["spatial"] = st_adata.obsm["location"]

sc.pp.normalize_total(st_adata, target_sum=10e4)
sc.pp.log1p(st_adata)
st_adata.raw = st_adata
```

Here we must ensure that the two datasets have a common gene subset.

```python
# filter genes to be the same on the spatial data
intersect = np.intersect1d(sc_adata.var_names, st_adata.var_names)
st_adata = st_adata[:, intersect].copy()
sc_adata = sc_adata[:, intersect].copy()
G = len(intersect)
```

```python
st_adata.write_h5ad("st_lymph_node_preprocessed.h5ad")
sc_adata.write_h5ad("sc_lymph_node_preprocessed.h5ad")
```
