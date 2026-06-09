# Introduction to scvi-tools in R

In this introductory tutorial, we go through the different steps of an scvi-tools workflow. It is the R version of [this]("https://docs.scvi-tools.org/en/latest/tutorials/notebooks/quick_start/api_overview.html") python tutorial.

While we focus on scVI in this tutorial, the API is consistent across all models. 

```python
library(reticulate)
library(anndataR)
library(ggplot2)
library(IRdisplay)
```

Before we use reticulate, we will need to point it to the correct conda env we use for the analysis

```python
use_condaenv("base", required = TRUE)
```

### Import Python libraries with reticulate

```python
sc <- import('scanpy', convert = FALSE)
scvi <- import("scvi", convert = FALSE)
```

```python
scvi$`__version__`
```

```python
scvi$settings$seed=42L
```

Load a subsampled version of the heart cell atlas dataset directly from scvi, like the python tutorial:

```python
adata = scvi$data$heart_cell_atlas_subsampled()
adata
```

Apply scanpy preprocessing functions directly:

```python
sc$pp$filter_genes(adata, min_counts=3L)
sc$pp$filter_cells(adata, min_genes = 200L)
adata$layers["counts"] = adata$X$copy()  # preserve counts
sc$pp$normalize_total(adata, target_sum = 1e4)
sc$pp$log1p(adata)
adata$raw = adata  # freeze the state in `.raw`
```

Select highly variable genes

```python
sc$pp$highly_variable_genes(
    adata,
    n_top_genes=r_to_py(1200),
    subset=TRUE,
    layer="counts",
    flavor="seurat_v3",
    batch_key="cell_source",
)
```

```python
adata
```

### Creating and training a model

```python
# run setup_anndata
scvi$model$SCVI$setup_anndata(adata,
                            layer="counts",
                            categorical_covariate_keys=c("cell_source", "donor"),
                            continuous_covariate_keys=c("percent_mito", "percent_ribo")
                             )
```

```python
# create the model
model = scvi$model$SCVI(adata)
model
```

```python
# train the model
model$train(max_epochs = 400L)
```

```python
str(py_to_r(model$registry))
```

### Show trainning curves

```python
elbo_train <- py_to_r(model$history[['elbo_train']])
elbo_train$epoch = as.numeric(row.names(elbo_train))
elbo_train$elbo_train <- as.numeric(unlist(elbo_train$elbo_train))
```

```python
head(elbo_train)
```

```python
ggplot(elbo_train, aes(x = epoch, y = elbo_train)) +
  geom_line(color = "steelblue") +
  labs(title = "Negative ELBO over training epochs")
```

### Saving and loading

```python
model_dir = file.path(getwd(), "scvi_model")
model$save(model_dir, overwrite=TRUE)
```

```python
model = scvi$model$SCVI$load(model_dir, adata=adata)
model
```

### Obtaining model outputs

```python
SCVI_LATENT_KEY = "X_scVI"

latent = model$get_latent_representation()
adata$obsm[SCVI_LATENT_KEY] = latent
latent$shape
```

```python
adata_subset = adata[adata$obs$cell_type == "Fibroblast"]
latent_subset = model$get_latent_representation(adata_subset)
latent_subset$shape
```

```python
denoised = py_to_r(model$get_normalized_expression(adata_subset, library_size=1e4))
denoised[c(1:6),c(1:6)]
```

```python
SCVI_NORMALIZED_KEY = "scvi_normalized"

adata$layers[SCVI_NORMALIZED_KEY] = model$get_normalized_expression(library_size=10e4)
```

### Visualization without batch correction

```python
# run PCA then generate UMAP plots
sc$tl$pca(adata)
```

```python
sc$pp$neighbors(adata, n_pcs=30L, n_neighbors=20L) #note for the usage of "L" for integer
```

```python
sc$tl$umap(adata, min_dist=0.3)
```

```python
fig1 = sc$pl$umap(
    adata,
    color="cell_type",
    frameon=FALSE,
    return_fig=TRUE,
    show = FALSE
)
#We will use the saved file in order to plot in R notebook (might not directly render from the scanpy umap function)
fig1$savefig("pca_cell_type.png", bbox_inches="tight")
display_png(file = "pca_cell_type.png", width = 800, height = 600)
```

```python
fig2 = sc$pl$umap(
    adata,
    color=c("donor", "cell_source"),
    ncols=2L,
    frameon=FALSE,
    return_fig=TRUE,
    show = FALSE
)
fig2$savefig("pca_donor_source.png", bbox_inches="tight")
display_png(file = "pca_donor_source.png", width = 1400, height = 1200)
```

### Visualization with batch correction (scVI)

```python
# use scVI latent space for UMAP generation
sc$pp$neighbors(adata, use_rep=SCVI_LATENT_KEY)
sc$tl$umap(adata, min_dist=0.3)
```

```python
fig3 = sc$pl$umap(
    adata,
    color="cell_type",
    frameon=FALSE,
    return_fig=TRUE,
    show = FALSE
)
fig3$savefig("scvi_cell_type.png", bbox_inches="tight")
display_png(file = "scvi_cell_type.png", width = 800, height = 600)
```

```python
fig4 = sc$pl$umap(
    adata,
    color=c("donor", "cell_source"),
    ncols=2L,
    frameon=FALSE,
    return_fig=TRUE,
    show = FALSE
)
fig4$savefig("scvi_donor_source.png", bbox_inches="tight")
display_png(file = "scvi_donor_source.png", width = 1400, height = 1200)
```

### Clustering on the scVI latent space

```python
# neighbors were already computed using scVI
SCVI_CLUSTERS_KEY = "leiden_scVI"
sc$tl$leiden(adata, key_added=SCVI_CLUSTERS_KEY, resolution=0.5)
```

```python
fig5 = sc$pl$umap(
    adata,
    color=SCVI_CLUSTERS_KEY,
    frameon=FALSE,
    return_fig=TRUE,
    show = FALSE
)
fig5$savefig("scvi_leiden_cluster.png", bbox_inches="tight")
display_png(file = "scvi_leiden_cluster.png", width = 800, height = 600)
```

### Differential expression

```python
de_df = py_to_r(model$differential_expression(
    groupby="cell_type", group1="Endothelial", group2="Fibroblast"
))
head(de_df)
```

```python
de_df = py_to_r(model$differential_expression(groupby="cell_type", mode="change"))
head(de_df)
```

```python
sc$tl$dendrogram(adata, groupby="cell_type", use_rep="X_scVI")
```

### Session Info Summary

```python
#reticulate::py_last_error()
```

```python
sI <- sessionInfo()
sI$loadedOnly <- NULL
print(sI, locale=FALSE)
```
