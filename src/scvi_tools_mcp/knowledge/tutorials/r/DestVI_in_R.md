# Multi-resolution deconvolution of spatial transcriptomics in R


In this brief tutorial, we go over how to use scvi-tools functionality in R for analyzing spatial datasets. We will load spatial data following this Seurat [tutorial](https://satijalab.org/seurat/articles/spatial_vignette.html), subsequently analyzing the data using DestVI.

This tutorial requires Reticulate. Please check out our installation [guide](https://www.scvi-tools.org/en/latest/installation.html#scvi-tools-installation-for-R) for instructions on installing Reticulate and scvi-tools.

## Loading and processing data with Seurat

```{note}
For general pre-processing for various datatypes used by scvi-tools models, see the [preprocessing tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/use_cases/preprocessing.html#spatial-transcriptomics).
```

```python
# install.packages("Seurat")
# install.packages("reticulate")
# install.packages("anndata")
# install.packages("devtools")
# devtools::install_github("satijalab/seurat-data")

# if (!requireNamespace("BiocManager", quietly = TRUE))
#     install.packages("BiocManager")

# BiocManager::install(c("LoomExperiment", "SingleCellExperiment"))
# devtools::install_github("cellgeni/sceasy")
```

```python
library(Seurat)
library(SeuratData)
library(ggplot2)
```

First, we load the reference SMART-seq2 dataset of mouse brain. This dataset contains about 14,000 cells.

```python
cortex_sc_data <- readRDS(url("https://www.dropbox.com/s/cuowvm4vrf65pvq/allen_cortex.rds?dl=1"))
```

```python
InstallData("stxBrain")
```

```python
brain_st_data <- LoadData("stxBrain", type = "anterior1")
```

Now, we subset the data in the same way that was done in the [Seurat vignette](https://satijalab.org/seurat/articles/spatial_vignette.html#subset-out-anatomical-regions-1), to match the cortex single-cell reference we are using.

```python
brain_st_data <- SCTransform(brain_st_data, assay = "Spatial", verbose = FALSE)
brain_st_data <- RunPCA(brain_st_data, assay = "SCT", verbose = FALSE)
brain_st_data <- FindNeighbors(brain_st_data, reduction = "pca", dims = 1:30)
brain_st_data <- FindClusters(brain_st_data, verbose = FALSE)
brain_st_data <- RunUMAP(brain_st_data, reduction = "pca", dims = 1:30)

cortex_st_data <- subset(brain_st_data, idents = c(1, 2, 3, 4, 6, 7))
cortex_st_data <- subset(cortex_st_data, anterior1_imagerow > 400 | anterior1_imagecol < 150, invert = TRUE)
cortex_st_data <- subset(cortex_st_data, anterior1_imagerow > 275 & anterior1_imagecol > 370, invert = TRUE)
cortex_st_data <- subset(cortex_st_data, anterior1_imagerow > 250 & anterior1_imagecol > 440, invert = TRUE)
```

```python
cortex_sc_data
```

```python
cortex_st_data
```

```python
cortex_sc_data <- NormalizeData(cortex_sc_data, normalization.method = "LogNormalize", scale.factor = 10000)
cortex_sc_data <- FindVariableFeatures(cortex_sc_data, selection.method = "vst", nfeatures = 2000)
top2000 <- head(VariableFeatures(cortex_sc_data), 2000)
top2000intersect <- intersect(rownames(cortex_st_data), top2000)
```

```python
cortex_sc_data <- cortex_sc_data[top2000intersect]
cortex_st_data <- cortex_st_data[top2000intersect]
G <- length(top2000intersect)
G
```

```python
SpatialFeaturePlot(cortex_st_data, features = "nCount_Spatial") + theme(legend.position = "right")
```

## Data conversion (Seurat -> AnnData)

We use sceasy for conversion, and load the necessary Python packages for later.

```python
library(reticulate)
library(sceasy)
library(anndata)

sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)
```

We make two AnnData objects, one for the single-cell reference and one for the spatial transcriptomics data, and then move the measurement coordinates to the appropriate attribute of the spatial AnnData.

```python
cortex_sc_adata <- convertFormat(cortex_sc_data, from="seurat", to="anndata", main_layer="counts", drop_single_values=FALSE)
cortex_st_adata <- convertFormat(cortex_st_data, from="seurat", to="anndata", assay="Spatial", main_layer="counts", drop_single_values=FALSE)
```

## Fit the scLVM

```python
scvi$model$CondSCVI$setup_anndata(cortex_sc_adata, labels_key="subclass")
```

Here we would like to reweight each measurement by a scalar factor (e.g., the inverse proportion) in the loss of the model so that lowly abundant cell types get better fit by the model.

```python
sclvm <- scvi$model$CondSCVI(cortex_sc_adata, weight_obs=TRUE)
sclvm$train(max_epochs=as.integer(250))
```

```python
# Make plot smaller.
saved <- options(repr.plot.width=6, repr.plot.height=5)

sclvm_elbo <- py_to_r(sclvm$history["elbo_train"]$astype("float64"))
ggplot(data = sclvm_elbo, mapping = aes(x=as.numeric(rownames(sclvm_elbo)), y=elbo_train)) + geom_line() + xlab("Epoch") + ylab("ELBO") + xlim(10, NA)

# Revert plot settings.
options(saved)
```

## Deconvolution with stLVM

```python
scvi$model$DestVI$setup_anndata(cortex_st_adata)
```

```python
stlvm <- scvi$model$DestVI$from_rna_model(cortex_st_adata, sclvm)
stlvm$train(max_epochs=as.integer(2500))
```

```python
# Make plot smaller.
saved <- options(repr.plot.width=6, repr.plot.height=5)

stlvm_elbo <- py_to_r(stlvm$history["elbo_train"]$astype("float64"))
ggplot(data = stlvm_elbo, mapping = aes(x=as.numeric(rownames(stlvm_elbo)), y=elbo_train)) + geom_line() + xlab("Epoch") + ylab("ELBO") + xlim(10, NA)

# Revert plot settings.
options(saved)
```

## Cell type proportions

```python
cortex_st_adata$obsm["proportions"] <- stlvm$get_proportions()
```

```python
head(py_to_r(cortex_st_adata$obsm$get("proportions")))
```

```python
cortex_st_data[["predictions"]] <- CreateAssayObject(data = t(py_to_r(cortex_st_adata$obsm$get("proportions"))))
```

```python
DefaultAssay(cortex_st_data) <- "predictions"
SpatialFeaturePlot(cortex_st_data, features = c("L2/3 IT", "L4"), pt.size.factor = 1.6, ncol = 2, crop = TRUE)
```

## Intra cell type information

At the heart of DestVI is a multitude of latent variables (5 per cell type per spots). We refer to them as "gamma", and we may manually examine them for downstream analysis.

Because those values may be hard to examine for end-users, we presented several methods for prioritizing the study of different cell types (based on PCA and Hotspot). If you'd like to use those methods, please refer to our DestVI reproducibility repository. If you have suggestions to improve those, and would like to see them in the main codebase, reach out to us.

In this tutorial, we assume that the user have identified key gene modules that vary within one cell type in the single-cell RNA sequencing data (e.g., using [Hotspot](https://github.com/YosefLab/Hotspot)). We provide here a code snippet for imputing the spatial pattern of the cell type specific gene expression, using the example of the PLP1 gene in Endothelial cells.

```python
for (cell_type_gamma in iterate(stlvm$get_gamma()$items())) {
    cell_type <- cell_type_gamma[0]
    gamma_df <- cell_type_gamma[1]
    cortex_st_data[[paste(cell_type, "_gamma", sep = "")]] <- CreateAssayObject(data = t(py_to_r(gamma_df)))
}
```

```python
head(GetAssayData(cortex_st_data))
```

```python
ct_name <- "L6 IT"
gene_name <- "Plp1"

# filter for spots with low abundance
indices <- which(GetAssayData(cortex_st_data$predictions)[ct_name,] > 0.03)

# impute gene
specific_expression <- stlvm$get_scale_for_ct(ct_name, indices = r_to_py(as.integer(indices - 1)))[[gene_name]]
specific_expression <- 1 + 1e4 * py_to_r(specific_expression$to_frame())
```

```python
filtered_st_data <- cortex_st_data[, indices]
filtered_st_data[["imputation"]] <- CreateAssayObject(data = t(specific_expression))
```

```python
DefaultAssay(filtered_st_data) <- "imputation"
SpatialFeaturePlot(filtered_st_data, features = gene_name)
```

## Session Info

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
