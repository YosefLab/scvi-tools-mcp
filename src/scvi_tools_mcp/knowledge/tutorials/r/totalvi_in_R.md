# CITE-seq analysis in R


In this brief tutorial, we go over how to use scvi-tools functionality in R for analyzing CITE-seq data. We will closely follow the Bioconductor PBMC [tutorial](https://bioconductor.org/books/release/OSCA/human-pbmc-with-surface-proteins-10x-genomics.html), using totalVI when appropriate.

This tutorial requires Reticulate. Please check out our installation [guide](https://www.scvi-tools.org/en/latest/installation.html#scvi-tools-installation-for-R) for instructions on installing Reticulate and scvi-tools.

```python
library(BiocFileCache)
library(DropletUtils)
library(scater)
library(scran)
library(reticulate)
library(sceasy)
library(anndata)
```

```python
use_condaenv("base", required = TRUE)
```

## Loading and processing data with Bioconductor

```python
bfc <- BiocFileCache(ask=FALSE)
exprs.data <- bfcrpath(bfc, file.path(
    "http://cf.10xgenomics.com/samples/cell-vdj/3.1.0",
    "vdj_v1_hs_pbmc3",
    "vdj_v1_hs_pbmc3_filtered_feature_bc_matrix.tar.gz"))
untar(exprs.data, exdir=tempdir())

sce.pbmc <- read10xCounts(file.path(tempdir(), "filtered_feature_bc_matrix"))
sce.pbmc <- splitAltExps(sce.pbmc, rowData(sce.pbmc)$Type)
```

## Pre-processing and quality control


```{note}
For general pre-processing for various datatypes used by scvi-tools models, see the [preprocessing tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/use_cases/preprocessing.html#cite-seq).
```

```python
unfiltered <- sce.pbmc
```

```python
is.mito <- grep("^MT-", rowData(sce.pbmc)$Symbol)
stats <- perCellQCMetrics(sce.pbmc, subsets=list(Mito=is.mito))

high.mito <- isOutlier(stats$subsets_Mito_percent, type="higher")
low.adt <- stats$`altexps_Antibody Capture_detected` < nrow(altExp(sce.pbmc))/2

discard <- high.mito | low.adt
sce.pbmc <- sce.pbmc[,!discard]
```

```python
summary(high.mito)
```

```python
colData(unfiltered) <- cbind(colData(unfiltered), stats)
unfiltered$discard <- discard

gridExtra::grid.arrange(
    plotColData(unfiltered, y="sum", colour_by="discard") +
        scale_y_log10() + ggtitle("Total count"),
    plotColData(unfiltered, y="detected", colour_by="discard") +
        scale_y_log10() + ggtitle("Detected features"),
    plotColData(unfiltered, y="subsets_Mito_percent",
        colour_by="discard") + ggtitle("Mito percent"),
    plotColData(unfiltered, y="altexps_Antibody Capture_detected",
        colour_by="discard") + ggtitle("ADT detected"),
    ncol=2
)
```

```python
plotColData(unfiltered, x="sum", y="subsets_Mito_percent",
    colour_by="discard") + scale_x_log10()
```

## Normalization

While we normalize the data here using standard Bioconductor practices, we will use the counts later for totalVI.

```python
set.seed(1000)
clusters <- quickCluster(sce.pbmc)
sce.pbmc <- computeSumFactors(sce.pbmc, cluster=clusters)
altExp(sce.pbmc) <- computeMedianFactors(altExp(sce.pbmc))
sce.pbmc <- logNormCounts(sce.pbmc, use_altexps=TRUE)
```

## Data conversion (SCE -> AnnData)

We use sceasy for conversion, and load the necessary Python packages for later.

```python
sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)
sys <- import ("sys", convert = FALSE)
```

We make two AnnData objects, one per modality, and then store the protein counts in the canonical location for scvi-tools.

```python
adata <- convertFormat(sce.pbmc, from="sce", to="anndata", main_layer="counts", drop_single_values=FALSE)
adata_protein <- convertFormat(altExp(sce.pbmc), from="sce", to="anndata", main_layer="counts", drop_single_values=FALSE)
adata$obsm["protein"] <- adata_protein$to_df()
```

```python
adata
```

## Run totalVI for dimensionality reduction

totalVI will output a low-dimensional representation of cells that captures information from both the RNA and protein. Here we show how to use totalVI for only dimensionality reduction, though totalVI can perform other tasks that are shown in the Python-based tutorials. The intention here is to provide some examples of how to use totalVI from R.

```python
scvi$model$TOTALVI$setup_anndata(adata, protein_expression_obsm_key="protein")
```

```python
vae <- scvi$model$TOTALVI(adata)
vae$train()
```

```python
reducedDims(sce.pbmc) <- list(TOTALVI=py_to_r(vae$get_latent_representation()))
sce.pbmc <- runUMAP(sce.pbmc, dimred="TOTALVI")
sce.pbmc <- runTSNE(sce.pbmc, dimred="TOTALVI")
```

## Clustering

```python
g <- buildSNNGraph(sce.pbmc, k=10, use.dimred = 'TOTALVI')
clust <- igraph::cluster_walktrap(g)$membership
colLabels(sce.pbmc) <- factor(clust)
```

```python
plotUMAP(sce.pbmc, colour_by="label")
```

```python
plotTSNE(sce.pbmc, colour_by="label")
```

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
