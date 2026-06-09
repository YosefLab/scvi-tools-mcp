# Integrating datasets with scVI in R


In this tutorial, we go over how to use basic scvi-tools functionality in R. However, for more involved analyses, we suggest using scvi-tools from Python. Checkout the [Scanpy_in_R tutorial](https://theislab.github.io/scanpy-in-R/#converting-from-r-to-python-1) for instructions on converting Seurat objects to anndata. 

This tutorial requires Reticulate. Please check out our installation guide for instructions on installing Reticulate and scvi-tools.

## Loading and processing data with Seurat
We follow the basic Seurat [tutorial](https://satijalab.org/seurat/v3.2/pbmc3k_tutorial.html) for loading data and selecting highly variable genes.

**Note: scvi-tools requires raw gene expression**

```python
# devtools::install_github("satijalab/seurat-data")
# SeuratData::InstallData("pbmc3k")
# install.packages("https://seurat.nygenome.org/src/contrib/ifnb.SeuratData_3.0.0.tar.gz", repos = NULL, type = "source") 
# SeuratData::InstallData("ifnb")# devtools::install_github("cellgeni/sceasy")
```

```python
library(Seurat)
library(SeuratData)
library(cowplot)
library(reticulate)
library(sceasy)
SeuratData::InstallData("pbmc3k")
SeuratData::InstallData("ifnb")
```

```python
use_condaenv("base", required = TRUE)
```

```python
# We will work within the Seurat framework
data("pbmc3k")
pbmc <- pbmc3k
```

```python
pbmc = UpdateSeuratObject(object = pbmc) 
pbmc <- NormalizeData(pbmc, normalization.method = "LogNormalize", scale.factor = 10000)
```

```python
pbmc[["percent.mt"]] <- PercentageFeatureSet(pbmc, pattern = "^MT-")
```

```python
pbmc <- subset(pbmc, subset = nFeature_RNA > 200 & nFeature_RNA < 2500 & percent.mt < 5)
pbmc <- FindVariableFeatures(pbmc, selection.method = "vst", nfeatures = 2000)
top2000 <- head(VariableFeatures(pbmc), 2000)
pbmc <- pbmc[top2000]
```

```python
print(pbmc) # Seurat object
```

## Converting Seurat object to AnnData

scvi-tools relies on the [AnnData](https://anndata.readthedocs.io/en/latest/) object. Here we show how to convert our Seurat object to anndata for scvi-tools.



```python
sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)
```

```python
adata <- convertFormat(pbmc, from="seurat", to="anndata", main_layer="counts", drop_single_values=FALSE)
print(adata) # Note generally in Python, dataset conventions are obs x var
```

## Setup our AnnData for training

Reticulate allows us to call Python code from R, giving the ability to use all of scvi-tools in R. We encourage you to checkout their [documentation](https://rstudio.github.io/reticulate/articles/calling_python.html) and specifically the section on type conversions in order to pass arguments to Python functions.

In this section, we show how to setup the AnnData for scvi-tools, create the model, train the model, and get the latent representation. For a more in depth description of setting up the data, you can checkout our [introductory tutorial](https://www.scvi-tools.org/en/latest/user_guide/notebooks/api_overview.html) as well as our [data loading tutorial](https://www.scvi-tools.org/en/latest/user_guide/notebooks/data_loading.html). 


```python
# run setup_anndata
scvi$model$SCVI$setup_anndata(adata)

# create the model
model = scvi$model$SCVI(adata)

# train the model
model$train()

# to specify the number of epochs when training:
# model$train(max_epochs = as.integer(400))

```

## Getting the latent represenation and visualization
Here we get the latent representation of the model and save it back in our Seurat object. Then we run UMAP and visualize. 

```python
# get the latent represenation
latent = model$get_latent_representation()

# put it back in our original Seurat object
latent <- as.matrix(latent)
rownames(latent) = colnames(pbmc)
pbmc[["scvi"]] <- CreateDimReducObject(embeddings = latent, key = "scvi_", assay = DefaultAssay(pbmc))

```

```python
# Find clusters, then run UMAP, and visualize
pbmc <- FindNeighbors(pbmc, dims = 1:10, reduction = "scvi")
pbmc <- FindClusters(pbmc, resolution =1)

pbmc <- RunUMAP(pbmc, dims = 1:10, reduction = "scvi", n.components = 2)
```

```python
DimPlot(pbmc, reduction = "umap", pt.size = 3)
```

## Finding differentially expressed genes with scVI latent space

First, we put the seurat clusters into our original anndata.


```python
adata$obs$insert(adata$obs$shape[1], "seurat_clusters", pbmc[["seurat_clusters"]][,1])
```

Using our trained SCVI model, we call the `differential_expression()` method
We pass `seurat_clusters` to the groupby argument and compare between cluster `1` and cluster `2`.

The output of DE is a DataFrame with the bayes factors. Bayes factors > 3 have high probability of being differentially expressed. You can also set fdr_target, which will return the differentially expressed genes based on the posteior expected FDR. 

```python
DE <- model$differential_expression(adata, groupby="seurat_clusters", group1 = "1", group2 = "2")
```

```python
print(DE$head())
```

## Integrating datasets with scVI

Here we integrate two datasets from Seurat's [Immune Alignment Vignette](https://satijalab.org/seurat/v3.2/immune_alignment.html).

```python
data("ifnb")
```

```python
# use seurat for variable gene selection 
ifnb = UpdateSeuratObject(object = ifnb) 
ifnb <- NormalizeData(ifnb, normalization.method = "LogNormalize", scale.factor = 10000)
```

```python
ifnb[["percent.mt"]] <- PercentageFeatureSet(ifnb, pattern = "^MT-")
ifnb <- subset(ifnb, subset = nFeature_RNA > 200 & nFeature_RNA < 2500 & percent.mt < 5)
ifnb <- FindVariableFeatures(ifnb, selection.method = "vst", nfeatures = 2000)
top2000 <- head(VariableFeatures(ifnb), 2000)
ifnb <- ifnb[top2000]
```

```python
adata <- convertFormat(ifnb, from="seurat", to="anndata", main_layer="counts", drop_single_values=FALSE)
print(adata)
```

```python
adata
```

```python
# run setup_anndata, use column stim for batch
scvi$model$SCVI$setup_anndata(adata, batch_key = 'stim')

# create the model
model = scvi$model$SCVI(adata)

# train the model
model$train()

# to specify the number of epochs when training:
# model$train(max_epochs = as.integer(400))

```

```python
# get the latent represenation
latent = model$get_latent_representation()

# put it back in our original Seurat object
latent <- as.matrix(latent)
rownames(latent) = colnames(ifnb)
ifnb[["scvi"]] <- CreateDimReducObject(embeddings = latent, key = "scvi_", assay = DefaultAssay(ifnb))
```

```python
# for jupyter notebook
options(repr.plot.width=10, repr.plot.height=8)

ifnb <- RunUMAP(ifnb, dims = 1:10, reduction = "scvi", n.components = 2)
p1 <- DimPlot(ifnb, reduction = "umap", group.by = "stim", pt.size=2)
```

```python
plot_grid(p1)
```

```python
options(repr.plot.width=12, repr.plot.height=10)

FeaturePlot(ifnb, features = c("SELL", "CREM", "CD8A", "GNLY", "CD79A", "FCGR3A", 
    "CCL2", "PPBP"), min.cutoff = "q9")
```

```python
FeaturePlot(ifnb, features = c("GNLY", "IFI6"), split.by = "stim", max.cutoff = 3, 
    cols = c("grey", "red"))
```

#### Session Info Summary

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
