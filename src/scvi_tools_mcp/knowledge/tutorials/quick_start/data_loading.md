# Data loading and preparation

Here we walk through the necessary steps to get your data into ready for scvi-tools.

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

import anndata
import muon
import numpy as np
import pooch
import scanpy as sc
import scvi
import seaborn as sns
import torch
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

## Loading data

scvi-tools supports the [AnnData](https://anndata.readthedocs.io/en/latest/) data format, which also underlies [Scanpy](https://scanpy.readthedocs.io/en/stable/). AnnData is quite similar to other popular single cell objects like that of [Seurat](https://github.com/satijalab/seurat/wiki) and [SingleCellExperiment](https://bioconductor.org/packages/release/bioc/vignettes/SingleCellExperiment/inst/doc/intro.html). In particular, it allows cell-level and feature-level metadata to coexist in the same data structure as the molecular counts.

It's also now possible to automatically convert these R-based objects to AnnData within a Jupyter notebook. See the following [tutorial](https://github.com/LuckyMD/Code_snippets/blob/master/Seurat_to_anndata.ipynb) for more information.

scvi-tools has a number of convenience methods for loading data from `.csv`, `.loom`, and `.h5ad` formats. To load outputs from Cell Ranger, please use Scanpy's [reading functionality](https://scanpy.readthedocs.io/en/latest/api.html#reading).

Let us now download an AnnData object (`.h5ad` format) and load it using scvi-tools.

### PBMC3k

```python
pbmc3k_path = os.path.join(save_dir.name, "pbmc3k.h5ad")

pbmc3k = sc.read(filename=pbmc3k_path, backup_url="http://falexwolf.de/data/pbmc3k_raw.h5ad")
pbmc3k
```

This is a fairly simple object, it just contains the count data and the ENSEMBL ids for the genes.

```python
pbmc3k.var.head()
```

### PBMC5k

As another example, let's download a dataset from 10x Genomics. This data was obtained from a CITE-seq experiment, so it also contains protein count data.

```python
def download_data(
    save_path: str, fname: str = "pbmc5k_protein_filtered_feature_bc_matrix.h5"
) -> str:
    """Download the data files."""
    return pooch.retrieve(
        url="https://cf.10xgenomics.com/samples/cell-exp/3.0.2/5k_pbmc_protein_v3/5k_pbmc_protein_v3_filtered_feature_bc_matrix.h5",
        known_hash="7695e6b1888bdae6f53b3a28a99f0a0cdf387d1685e330a597cdd4b5541f8abd",
        fname=fname,
        path=save_path,
    )
```

```python
h5_path = download_data(save_dir.name)
```

We load this data using muon, which will load a `MuData` object containing both the RNA and protein data.

```python
pbmc5k = muon.read_10x_h5(h5_path)
```

```python
pbmc5k
```

It's often helpful to give the gene names unique names.

```python
pbmc5k.var_names_make_unique()
```

### Concatenate the datasets

```python
adata = anndata.concat([pbmc3k, pbmc5k.mod["rna"]], join="inner", label="batch")
```

Notice that the resulting AnnData has a batch key in `.obs`.

```python
adata.obs.sample(n=5)
```

## Preprocessing the data

It is common to remove outliers, and even perform feature selection before model fitting. We prefer the [Scanpy preprocessing module](https://scanpy.readthedocs.io/en/stable/api/index.html#module-scanpy.pp) at this stage.

```python
print("# cells, # genes before filtering:", adata.shape)

sc.pp.filter_genes(adata, min_counts=3)
sc.pp.filter_cells(adata, min_counts=3)

print("# cells, # genes after filtering:", adata.shape)
```

As it is popular to normalize the data for many methods, we can use Scanpy for this; however, it's important to keep the count information intact for scvi-tools models.

```python
adata.layers["counts"] = adata.X.copy()
```

Now we can proceed with common normalization methods.

```python
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
```

We can store the normalized values in `.raw` to keep them safe in the event the anndata gets subsetted feature-wise.

```python
adata.raw = adata
```

Alternatively, we can create a new MuData object where the normalized data are another "modality". This workflow is ideal going forward as `.raw` in AnnData has an akward interface.

We denote `axis=-1` when creating the MuData object to denote that both the obs and var axes are aligned across modalities.

```python
mdata = muon.MuData({"rna": adata.copy(), "log_norm_rna": adata.copy()}, axis=-1)
# Now rna is count-based and log_norm_rna is log-normalized
mdata.mod["rna"].X = mdata.mod["rna"].layers["counts"]
del mdata.mod["rna"].raw
del mdata.mod["rna"].layers["counts"]
del mdata.mod["log_norm_rna"].layers["counts"]
mdata
```

## Register the data with scvi-tools

Now that we have an AnnData object, we need to alert scvi-tools of all the interesting data in our object. For example, now that we have batches in our AnnData, we can alert the models that we'd like to perform batch correction. Also, because we have the count data in a layer, we can use the `layer` argument.

Normally, we set up the data right before using a model, thus we would call the `setup_anndata` method specific to that model. However, we are not using any particular model here since we are just demonstrating data usage and handling in this tutorial. We will use the SCVI model's `setup_anndata` method here and in what follows for sake of example.

### Basic case

```python
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
```

### CITE-seq case

As PBMC5k is a CITE-seq dataset, we can use scvi-tools to register the protein abundance. Note that totalVI is the only current model that uses the protein abundance. The usage of registered items is model specific.

We have not preprocessed the `pbmc5k` object, which we do recommend. However, here we show how to setup this object for totalVI.

#### `setup_mudata`

With CITE-seq data we can use a MuData or AnnData object. In the MuData case we use the `modalities` argument to specify which modality contains the RNA data and which contains the protein data. The `None` value of the layers indicates to use `.X`.

Therefore in the example below, the protein data will come from the `"prot"` modality's `.X`, and likewise the RNA data will come from the `"rna"` modality's `.X`.

```python
# totalVI requires dense protein data
pbmc5k.mod["prot"].X = (
    np.asarray(pbmc5k.mod["prot"].X.A)
    if hasattr(pbmc5k.mod["prot"].X, "A")
    else np.asarray(pbmc5k.mod["prot"].X.toarray())
)
scvi.model.TOTALVI.setup_mudata(
    pbmc5k,
    protein_layer=None,
    rna_layer=None,
    modalities={"protein_layer": "prot", "rna_layer": "rna"},
)
```

#### `setup_anndata`

```python
adata_pbm5k = pbmc5k.mod["rna"]
adata_pbm5k.obsm["prot"] = pbmc5k.mod["prot"].to_df()

scvi.model.TOTALVI.setup_anndata(
    adata_pbm5k,
    protein_expression_obsm_key="prot",
)
```

```{warning}
After `setup_anndata` or `setup_mudata` has been run, the adata object should not be modified. The very next step in the workflow is to initialize and train the model of interest (e.g., scVI, totalVI). If you do modify the adata, it's ok, just run `setup_anndata` or `setup_mudata` again -- and then reinitialize the model.
```

### Viewing the scvi-tools data setup

```python
model = scvi.model.TOTALVI(adata_pbm5k)
model.view_anndata_setup(adata_pbm5k)
```
