# Preprocessing datasets for analysis with scvi-tools

In this tutorial, we go over several preprocessing techniques for different types of data used with scvi-tools models. Each section of this tutorial is independent from the other sections, and is relevant to other scvi-tools tutorials which use the same type of dataset. For example, the preprocessing techniques used in the scRNA-seq section of this tutorial are generally used in the scvi-tools scRNA-seq related tutorials. Relevant tutorials are linked in each section.

## Dependencies

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

## Imports and preparing files

```python
import os
import tempfile
from pathlib import Path

import anndata as ad
import mudata as md
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

## scRNA-seq

### Relevant scRNA-seq Tutorials:

The following tutorial uses the exact preprocessed dataset that results from this section:

[Atlas-level integration of lung data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/harmonization.html)

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[MrVI Quick Start Tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/MrVI_tutorial.html)

[Differential expression on C. elegans data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scVI_DE_worm.html)

[Annotation with CellAssign](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/cellassign_tutorial.html)

[Linearly decoded VAE](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/linear_decoder.html)

[Isolating perturbation-induced variations with contrastiveVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/contrastiveVI_tutorial.html)

[Topic Modeling with Amortized LDA](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/amortized_lda.html)

[Identification of zero-inflated genes](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/AutoZI_tutorial.html)

[Integration of scRNA-seq data with substantial batch effects using sysVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/sysVI.html)

[Seed labeling with scANVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/seed_labeling.html)

[Benchmarking the scANVI fix](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scanvi_fix.html)

[Integration and label transfer with Tabula Muris](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/tabula_muris.html)

[Reference mapping with scvi-tools](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scarches_scvi_tools.html)

[Querying the Human Lung Cell Atlas](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/query_hlca_knn.html)

[Decipher Quick Start Tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/decipher_tutorial.html)

[Variational inference for RNA velocity with VeloVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/velovi.html)


### Preprocessing

Here we demonstrate preprocessing of an scRNA-seq dataset using cells from the lung atlas integration task from the [scIB manuscript](https://www.biorxiv.org/content/10.1101/2020.05.22.111161v2).

```python
adata_path = os.path.join(save_dir.name, "lung_atlas.h5ad")

adata = sc.read(
    adata_path,
    backup_url="https://exampledata.scverse.org/scvi-tools/lung_atlas.h5ad",
)
adata
```

This dataset was already processed as described in the scIB manuscript. Generally, models in scvi-tools expect data that has been filtered/aggregated in the same fashion as one would do with Scanpy/Seurat.

Another important thing to keep in mind is highly-variable gene selection. While scVI and scANVI both accomodate using all genes in terms of runtime, we usually recommend filtering genes for best integration performance. This will, among other things, remove batch-specific variation due to batch-specific gene expression.

We perform this gene selection using the Scanpy pipeline while keeping the full dimension normalized data in the `adata.raw` object. We obtain variable genes from each dataset and take their intersections.

This dataset already has counts stored in layers, and `adata.X` contains log transformed scran normalized expression. If this is not the case for your dataset, you can preserve the raw counts, then normalize and log transform them with
```python
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```

Below we perform gene selection while keeping the full dimension normalized data in `adata.raw`. We obtain variable genes from each dataset and take their intersections.

```python
adata.raw = adata  # keep full dimension safe
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat_v3",
    layer="counts",
    subset=True,
    batch_key="batch",  # Change depending on the batch key for your dataset
)
```

```{important}
We see a warning about the data not containing counts. This is due to some of the samples in this dataset containing SoupX-corrected counts. scvi-tools models will run for non-negative real-valued data, but we strongly suggest checking that these possibly non-count values are intended to represent pseudocounts, and not some other normalized data, in which the variance/covariance structure of the data has changed dramatically.
```

```python
# Save preprocessed data for later use
adata.write_h5ad("lung_atlas_preprocessed.h5ad")
```

## scATAC-seq

### Relevant scATAC-seq tutorials:

The following tutorial uses the exact preprocessed dataset that results from this section:

[PeakVI: Analyzing scATACseq data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/PeakVI.html)

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[PoissonVI: Analyzing quantitative scATAC-seq fragment counts](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/PoissonVI.html)

[ScBasset: Analyzing scATACseq data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/scbasset.html)

[scBasset: Batch correction of scATACseq data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/scbasset_batch.html)

### Preprocessing

To demonstrate preprocessing of scATAC-seq data, we use a 5k PBMC sample dataset from 10X. We use the pooch package to download the data.

```python
def download_data(save_path: str, fname: str = "atac_pbmc_5k") -> str:
    """Download the data files."""
    data_paths = pooch.retrieve(
        url="https://cf.10xgenomics.com/samples/cell-atac/1.2.0/atac_pbmc_5k_nextgem/atac_pbmc_5k_nextgem_filtered_peak_bc_matrix.tar.gz",
        known_hash="78e536a1508108fa5bd3b411a7484809c011f3403800369b20db05bdbfeb2284",
        fname=fname,
        path=save_path,
        processor=pooch.Untar(),
        progressbar=True,
    )
    return str(Path(data_paths[0]).parent)
```

```python
data_path = download_data(save_dir.name)
```

PeakVI expects as input an AnnData object with a cell-by-region matrix. There are various pipelines that handle preprocessing of scATACseq to obtain this matrix from the sequencing data. If the data was generated by 10X genomics, this matrix is among the standard outputs of CellRanger. Other pipelines, like [SnapATAC](https://github.com/r3fang/SnapATAC/) and [ArchR](https://www.archrproject.com/bookdown/add-peak-matrix.html), also generate similar matrices.

In the case of 10X data, PeakVI has a special reader function `scvi.data.read_10x_atac` that reads the files and creates an AnnData object, demonstrated below. For conveniece, we also demonstrate how to initialize an AnnData object from scratch.

Throughout this tutorial, we use [sample scATACseq data from 10X of 5K PBMCs](https://support.10xgenomics.com/single-cell-atac/datasets/1.2.0/atac_pbmc_5k_nextgem).

```python
adata = scvi.data.read_10x_atac(data_path)
adata
```

We use Scanpy here to filter out peaks that are rarely detected, so that the model trains faster:

```python
print("# regions before filtering:", adata.shape[-1])

# compute the threshold: 5% of the cells
min_cells = int(adata.shape[0] * 0.05)
# in-place filtering of regions
sc.pp.filter_genes(adata, min_cells=min_cells)

print("# regions after filtering:", adata.shape[-1])
```

```python
adata.write_h5ad("atac_pbmc_5k_preprocessed.h5ad")
```

## CITE-seq

### Relevant CITE-seq Tutorials

The following tutorial uses the exact preprocessed dataset that results from this section:

[CITE-seq analysis with totalVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/totalVI.html)

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[CITE-seq reference mapping with totalVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/totalVI_reference_mapping.html)

[Integration of CITE-seq and scRNA-seq data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/cite_scrna_integration_w_totalVI.html)

### Preprocessing

Here we demonstrate preprocessing of CITE-seq data on integrated PBMC10k and PBMC5k datasets available from 10X Genomics. We will subset to the 17 proteins shared between the datasets.

```python
def download_data(save_path: str, fname: str = "CITE-seq_pbmc_10k") -> str:
    """Download the data files."""
    if fname == "CITE-seq_pbmc_10k":
        hash = "md5:26d53ffe08b5f7d3b28df61b592d51fb"
        url = "https://cf.10xgenomics.com/samples/cell-exp/3.0.0/pbmc_10k_protein_v3/pbmc_10k_protein_v3_filtered_feature_bc_matrix.tar.gz"
    else:
        hash = "md5:9be3d672b0445b944ca06a507c3d780b"
        url = "https://cf.10xgenomics.com/samples/cell-exp/3.1.0/5k_pbmc_protein_v3/5k_pbmc_protein_v3_filtered_feature_bc_matrix.tar.gz"

    data_paths = pooch.retrieve(
        url=url,
        known_hash=hash,
        fname=fname,
        path=save_path,
        processor=pooch.Untar(),
        progressbar=True,
    )
    return str(Path(data_paths[0]).parent)
```

```python
data_path1 = download_data(save_dir.name)
data_path2 = download_data(save_dir.name, "CITE-seq_pbmc_5k")
```

```python
mdata1 = muon.read_10x_mtx(data_path1)
mdata2 = muon.read_10x_mtx(data_path2)
```

```python
# Create batch annotations
mdata1.mod["rna"].obs["batch"] = "10kpbmc"
mdata2.mod["rna"].obs["batch"] = "5kpbmc"
```

```python
mdata1
```

```python
mdata2
```

```python
# Make variable names unique
mdata1.mod["rna"].var_names_make_unique()
mdata2.mod["rna"].var_names_make_unique()

# Filter to shared genes and proteins between the two datasets with an inner join
rna_c = ad.concat([mdata1.mod["rna"], mdata2.mod["rna"]])
rna_c.obs_names_make_unique()

prot_c = ad.concat([mdata1.mod["prot"], mdata2.mod["prot"]])
prot_c.obs_names_make_unique()
mdata = md.MuData({"rna": rna_c, "prot": prot_c})
```

```python
mdata
```

We make var names unique, store raw counts in layers, and normalize and log transform counts. Then we perform gene selection.

```python
def filter_pbmc(mdata):
    # mdata.mod["rna"].var_names_make_unique()
    mdata.mod["rna"].layers["counts"] = mdata.mod["rna"].X.copy()
    sc.pp.normalize_total(mdata.mod["rna"])
    sc.pp.log1p(mdata.mod["rna"])

    sc.pp.highly_variable_genes(
        mdata.mod["rna"],
        n_top_genes=4000,
        flavor="seurat_v3",
        layer="counts",
    )
    # Place subsetted counts in a new modality
    mdata.mod["rna_subset"] = mdata.mod["rna"][:, mdata.mod["rna"].var["highly_variable"]].copy()
    mdata = md.MuData(mdata.mod)

    return mdata
```

```python
mdata = filter_pbmc(mdata)
```

```python
mdata
```

```python
mdata.write("CITE-seq_pbmc_combined_preprocessed.h5mu")
```

## Multiome

### Relevant Multiome Tutorials

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[Joint analysis of paired and unpaired multiomic data with MultiVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/MultiVI_tutorial.html)

### Preprocessing

First we download three datasets from 10X to use in this section of the tutorial: multiome, scRNA-seq, and scATAC-seq.
Importantly, MultiVI assumes that there are shared features between the datasets. This is trivial for gene expression datasets, which generally use the same set of genes as features. For ATAC-seq peaks, this is less trivial, and often requires preprocessing steps with other tools to get all datasets to use a shared set of peaks. That can be achieved with tools like SnapATAC, ArchR, and CellRanger in the case of 10X data.

```{important}
MultiVI requires the datasets to use shared features. scATAC-seq datasets need to be processed to use a shared set of peaks.
```

Below we download 2 PBMC datasets from 10X:

[multiome](https://www.10xgenomics.com/datasets/10-k-human-pbm-cs-multiome-v-1-0-chromium-x-1-standard-2-0-0)

[scRNA-seq](https://www.10xgenomics.com/datasets/5k_Human_Donor3_PBMC_3p_gem-x)

```python
def load_10x_mudata(url, filename=None, cache_dir=None, hash=None):
    if filename is None:
        filename = url.split("/")[-1]
    path = pooch.retrieve(
        url=url,
        known_hash=hash,
        fname=filename,
        path=cache_dir,
    )
    mdata = muon.read_10x_h5(path)

    return mdata
```

```python
mdata_multiome = load_10x_mudata(
    url="https://cf.10xgenomics.com/samples/cell-arc/2.0.0/10k_PBMC_Multiome_nextgem_Chromium_X/10k_PBMC_Multiome_nextgem_Chromium_X_filtered_feature_bc_matrix.h5",
    hash="md5:cee000a98c8a05d0456add3ff864cdb0",
    cache_dir=save_dir.name,
)
```

```python
mdata_expr = load_10x_mudata(
    url="https://cf.10xgenomics.com/samples/cell-exp/9.0.0/5k_Human_Donor3_PBMC_3p_gem-x_5k_Human_Donor3_PBMC_3p_gem-x/5k_Human_Donor3_PBMC_3p_gem-x_5k_Human_Donor3_PBMC_3p_gem-x_count_sample_filtered_feature_bc_matrix.h5",
    hash="md5:be6fbc95481d813c8113b696ca3c3efd",
    cache_dir=save_dir.name,
)
```

```python
mdata_multiome
```

```python
mdata_expr
```

```python
# Make var names unique
for m in [mdata_expr, mdata_multiome]:
    m.var_names_make_unique()
    m.update()
```

Because mdata_expr only has one modality, we will add an atac modality, filled with zeros, so that when we concatenate the mudatas, the rna modality will be padded to have the same number of observations as the atac modality. MultiVI requires that all modalities are fully paired.

```python
# Create a zero-filled ATAC AnnData with same variables as multiome ATAC
empty_atac = ad.AnnData(
    X=np.zeros((mdata_expr.n_obs, mdata_multiome.mod["atac"].n_vars)),
    var=mdata_multiome.mod["atac"].var.copy(),
    obs=mdata_expr.obs.copy(),
)

# Add ATAC modality to the RNA-only MuData
mdata_expr.mod["atac"] = empty_atac
```

```python
mdata = md.concat([mdata_multiome, mdata_expr], label="dataset")
```

```python
mdata
```

Below, we filter features for both modalities

```python
print(mdata.mod["rna"].shape)
sc.pp.filter_genes(mdata.mod["rna"], min_cells=int(mdata.mod["rna"].shape[0] * 0.1))
print(mdata.mod["rna"].shape)
```

```python
print(mdata.mod["atac"].shape)
sc.pp.filter_genes(mdata.mod["atac"], min_cells=int(mdata.mod["atac"].shape[0] * 0.1))
print(mdata.mod["atac"].shape)
```

```python
mdata
```

```python
# save preprocessed data
mdata.write("pbmc_multi_preprocessed.h5mu")
```

## Spatial transciptomics

### Relevant Spatial transciptomics Tutorials

The following tutorial uses the exact preprocessed dataset that results from this section:

[Multi-resolution deconvolution of spatial transcriptomics](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/DestVI_tutorial.html)

The following tutorials may not use the exact dataset, but the preprocessing steps should be very similar to what is covered in this section:

[ResolVI to address noise and biases in spatial transcriptomics](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/resolVI_tutorial.html)

[Introduction to gimVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/gimvi_tutorial.html)

[Spatial mapping with Tangram](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/tangram_scvi_tools.html)

[Stereoscope applied to left ventricule data](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/stereoscope_heart_LV_tutorial.html)

[Mapping human lymph node cell types to 10X Visium with Cell2location](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/cell2location_lymph_node_spatial_tutorial.html)

### Preprocessing

To demonstrate preprocessing for spatial transcriptomics, we use data from a comparative study of murine lymph nodes, comparing wild-type with a stimulation after injection of a mycobacteria. We have at disposal a 10x Visium dataset as well as a matching scRNA-seq dataset from the same tissue.

```python
url1 = "https://github.com/romain-lopez/DestVI-reproducibility/blob/master/lymph_node/deconvolution/ST-LN-compressed.h5ad?raw=true"
url2 = "https://github.com/romain-lopez/DestVI-reproducibility/blob/master/lymph_node/deconvolution/scRNA-LN-compressed.h5ad?raw=true"
out1 = "data/ST-LN-compressed.h5ad"
out2 = "data/scRNA-LN-compressed.h5ad"
```

First, let’s load the single-cell data. We profiled immune cells from murine lymph nodes with 10x Chromium, as a control / case study to study the immune response to exposure to a mycobacteria (refer to DestVI paper for more info). It contains the raw counts (DestVI always takes raw counts as input).

```python
sc_adata = sc.read(out2, backup_url=url2)
```

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
st_adata = sc.read(out1, backup_url=url1)
```

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
