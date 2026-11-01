# ATAC-seq analysis in R


In this tutorial, we go over how to use scvi-tools functionality in R for analyzing ATAC-seq data. We will closely follow the PBMC tutorial from [Signac](https://satijalab.org/signac/articles/pbmc_vignette.html), using scvi-tools when appropriate. In particular, we will 

1. Use PeakVI for dimensionality reduction and differential accessiblity for the ATAC-seq data
2. Use scVI to integrate the unpaired ATAC-seq dataset with a match scRNA-seq dataset of PBMCs

This tutorial requires Reticulate. Please check out our installation [guide](https://www.scvi-tools.org/en/latest/installation.html#scvi-tools-installation-for-R) for instructions on installing Reticulate and scvi-tools.

## Loading and processing data with Signac

```python
system("wget https://cf.10xgenomics.com/samples/cell-atac/1.0.1/atac_v1_pbmc_10k/atac_v1_pbmc_10k_filtered_peak_bc_matrix.h5")
system("wget https://cf.10xgenomics.com/samples/cell-atac/1.0.1/atac_v1_pbmc_10k/atac_v1_pbmc_10k_singlecell.csv")
system("wget https://cf.10xgenomics.com/samples/cell-atac/1.0.1/atac_v1_pbmc_10k/atac_v1_pbmc_10k_fragments.tsv.gz")
system("wget https://cf.10xgenomics.com/samples/cell-atac/1.0.1/atac_v1_pbmc_10k/atac_v1_pbmc_10k_fragments.tsv.gz.tbi")
```

```python
library(Signac)
library(Seurat)
library(GenomeInfoDb)
library(EnsDb.Hsapiens.v75)
library(ggplot2)
library(patchwork)
library(reticulate)
library(sceasy)
library(hdf5r)
library(biovizBase)
set.seed(1234)
```

```python
use_condaenv("base", required = TRUE)
```

## Pre-processing

We follow the original tutorial to create the Seurat object with ATAC data.

```{note}
For general pre-processing for various datatypes used by scvi-tools models, see the [preprocessing tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/use_cases/preprocessing.html#scatac-seq).
```

```python
counts <- Read10X_h5(filename = "atac_v1_pbmc_10k_filtered_peak_bc_matrix.h5")
metadata <- read.csv(
  file = "atac_v1_pbmc_10k_singlecell.csv",
  header = TRUE,
  row.names = 1
)
```

```python
chrom_assay <- CreateChromatinAssay(
  counts = counts,
  sep = c(":", "-"),
  genome = 'hg19',
  fragments = 'atac_v1_pbmc_10k_fragments.tsv.gz',
  min.cells = 10,
  min.features = 200
)
```

```python
pbmc <- CreateSeuratObject(
  counts = chrom_assay,
  assay = "peaks",
  meta.data = metadata
)
```

```python
pbmc = UpdateSeuratObject(object = pbmc) 
pbmc
```

```python
pbmc[['peaks']]
```

We add gene annotation information to facilitate downstream functionality.

```python
# extract gene annotations from EnsDb
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v75)

# change to UCSC style since the data was mapped to hg19
seqlevelsStyle(annotations) <- 'UCSC'
genome(annotations) <- "hg19"

# add the gene information to the object
Annotation(pbmc) <- annotations
```

## Computing QC metrics

We compute the same QC metrics as the [original tutorial](https://satijalab.org/signac/articles/pbmc_vignette.html#computing-qc-metrics-1). We leave it to the reader to follow the excellent Signac tutorial for understanding what these quantities represent.

```python
# compute nucleosome signal score per cell
pbmc <- NucleosomeSignal(object = pbmc)

# compute TSS enrichment score per cell
pbmc <- TSSEnrichment(object = pbmc, fast = FALSE)

# add blacklist ratio and fraction of reads in peaks
pbmc$pct_reads_in_peaks <- pbmc$peak_region_fragments / pbmc$passed_filters * 100
pbmc$blacklist_ratio <- pbmc$blacklist_region_fragments / pbmc$peak_region_fragments
```

```python
pbmc
```

```python
VlnPlot(
  object = pbmc,
  features = c('pct_reads_in_peaks', 'peak_region_fragments',
               'TSS.enrichment', 'blacklist_ratio', 'nucleosome_signal'),
  ncol = 5
)
```

```python
pbmc <- subset(
  x = pbmc,
  subset = peak_region_fragments > 3000 &
    peak_region_fragments < 20000 &
    pct_reads_in_peaks > 15 &
    blacklist_ratio < 0.05 &
    nucleosome_signal < 4 &
    TSS.enrichment > 2
)
pbmc
```

## Dimensionality reduction (PeakVI)


### Creating an AnnData object

We follow the standard workflow for converting between Seurat and AnnData.

```python
sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)
```

```python
adata <- convertFormat(pbmc, from="seurat", to="anndata", main_layer="counts", assay="peaks", drop_single_values=FALSE)
print(adata) # Note generally in Python, dataset conventions are obs x var
```

### Run the standard PeakVI workflow

```python
scvi$model$PEAKVI$setup_anndata(adata)
```

```python
pvi <- scvi$model$PEAKVI(adata)
pvi$train()
```

```python
# get the latent represenation
latent = pvi$get_latent_representation()

# put it back in our original Seurat object
latent <- as.matrix(latent)
rownames(latent) = colnames(pbmc)
ndims <- ncol(latent)
pbmc[["peakvi"]] <- CreateDimReducObject(embeddings = latent, key = "peakvi_", assay = "peaks")
```

```python
# Find clusters, then run UMAP, and visualize
pbmc <- FindNeighbors(pbmc, reduction = "peakvi", dims=1:ndims)
pbmc <- FindClusters(pbmc, resolution = 1)

pbmc <- RunUMAP(pbmc, reduction = "peakvi", dims=1:ndims)
```

```python
DimPlot(object = pbmc, label = TRUE) + NoLegend()
```

## Create a gene activity matrix

```{important}
The gene activity is used as an approximation of a gene expression matrix such that unpaired ATAC data can be integrated with RNA data. We recommend using this approach only for this unpaired case. Better results can be acheived if there is partially paired data, in which case MultiVI can be used.
```

```python
gene.activities <- GeneActivity(pbmc)

# add the gene activity matrix to the Seurat object as a new assay and normalize it
pbmc[['RNA']] <- CreateAssayObject(counts = gene.activities)
pbmc <- NormalizeData(
  object = pbmc,
  assay = 'RNA',
  normalization.method = 'LogNormalize',
  scale.factor = median(pbmc$nCount_RNA)
)
```

```python
DefaultAssay(pbmc) <- 'RNA'

FeaturePlot(
  object = pbmc,
  features = c('MS4A1', 'CD3D', 'LEF1', 'NKG7', 'TREM1', 'LYZ'),
  max.cutoff = 'q95',
  ncol = 3
)
```

## Integrating with scRNA-seq data (scANVI)

We can integrate the gene activity matrix with annotated scRNA-seq data using scANVI.

First we download the Seurat-processed PBMC 10k dataset (as in their tutorial). 

```python
pbmc_rna <- readRDS(url("https://www.dropbox.com/s/3f3p5nxrn5b3y4y/pbmc_10k_v3.rds?dl=1"))
```

```python
pbmc_rna<-UpdateSeuratObject(pbmc_rna)
```

And we convert it to AnnData using sceasy again. Subsequently, we follow the standard scANVI workflow: pretraining with scVI then running scANVI.

```python
adata_rna <- convertFormat(pbmc_rna, from="seurat", to="anndata", main_layer="counts", assay="RNA", drop_single_values=FALSE)
adata_atac_act <- convertFormat(pbmc, from="seurat", to="anndata", main_layer="counts", assay="RNA", drop_single_values=FALSE)
```

```python
# provide adata_atac_act unknown cell type labels
adata_atac_act$obs$insert(adata_atac_act$obs$shape[1], "celltype", "Unknown")
```

```python
adata_both <- adata_rna$concatenate(adata_atac_act)
```

We concatenated the RNA expression with the activity matrix using AnnData. Now we can see the last column is called "batch" and denotes which dataset each cell originated from.

```python
head(py_to_r(adata_both$obs))
```

```python
sc$pp$highly_variable_genes(
    adata_both, 
    flavor="seurat_v3", 
    n_top_genes=r_to_py(3000), 
    batch_key="batch", 
    subset=TRUE
)
scvi$model$SCVI$setup_anndata(adata_both, labels_key="celltype", batch_key="batch")
```

```python
model <- scvi$model$SCVI(adata_both, gene_likelihood="nb", dispersion="gene-batch")
model$train()
```

```python
lvae <- scvi$model$SCANVI$from_scvi_model(model, "Unknown", adata=adata_both)
lvae$train(max_epochs = as.integer(100), n_samples_per_label = as.integer(100))
```

Here we only use the prediction functionality of scANVI, but we also could have viewed an integrated representation of the ATAC and RNA using UMAP. 

```python
adata_both$obs$insert(adata_both$obs$shape[1], "predicted.labels", lvae$predict())
df <- py_to_r(adata_both$obs)
df <- subset(df, batch == 1)[, c("predicted.labels")]
pbmc <- AddMetaData(object = pbmc, metadata = df, col.name="predicted.labels")
```

```{important}
These labels should only serve as a starting point. Further inspection should always be performed. We leave this to the user, but will continue with these labels as a demonstration.
```

```python
plot1 <- DimPlot(
  object = pbmc_rna,
  group.by = 'celltype',
  label = TRUE,
  repel = TRUE) + NoLegend() + ggtitle('scRNA-seq')
```

```python
plot2 <- DimPlot(
  object = pbmc,
  group.by = 'predicted.labels',
  label = TRUE,
  repel = TRUE) + ggtitle('scATAC-seq')
```

```python
plot1 + plot2
```

## Finding differentially accessible peaks between clusters

As PeakVI learns uncertainty around the observed data, it can be leveraged for differential accessibility analysis. First, let's store the seurat cluster information back inside the AnnData.

```python
adata$obs$insert(adata$obs$shape[1], "predicted_ct", pbmc[["predicted.labels"]][,1])
```

Using our trained PEAKVI model, we call the `differential_accessibility()` (DA) method
We pass `predicted_ct` to the groupby argument and compare between naive CD4s and CD14 monocytes.

The output of DA is a DataFrame with the bayes factors. Bayes factors > 3 have high probability of being differentially expressed. You can also set fdr_target, which will return the differentially expressed genes based on the posteior expected FDR. 

```python
DA <- pvi$differential_accessibility(adata, groupby="predicted_ct", group1 = "CD4 Naive", group2 = "CD14+ Monocytes")
DA <- py_to_r(DA)
head(DA)
```

```python
# sort by proba_da and effect_size
DA <- DA[order(-DA[, 1], -DA[, 4]), ]
head(DA)
```

```python
DefaultAssay(pbmc) <- 'peaks'
```

```python
Idents(pbmc) <- pbmc[["predicted.labels"]][,1]
```

```python
head(Idents(pbmc))
```

```python
plot1 <- VlnPlot(
  object = pbmc,
  features = rownames(DA)[1],
  idents = c("CD4 Naive","CD14+ Monocytes")
)
```

```python
plot2 <- FeaturePlot(
  object = pbmc,
  features = rownames(DA)[1],
)
```

```python
plot1 | plot2
```

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
