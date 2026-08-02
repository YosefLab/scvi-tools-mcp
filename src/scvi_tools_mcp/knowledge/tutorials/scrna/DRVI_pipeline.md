# Disentangled representation learning with DRVI

DRVI ([Moinfar & Theis, 2024](https://doi.org/10.1101/2024.11.06.622266)) is an unsupervised deep generative model that learns an **interpretable, disentangled** latent representation of single-cell omics data. Disentanglement is induced in the decoder: the latent is split into distinct groups that are decoded separately and aggregated, so each factor tends to capture a distinct, biologically meaningful axis of variation.

In this notebook we analyze an immune dataset of 9 batches from four human peripheral blood and bone marrow studies with 16 annotated cell types, training DRVI with 128 latent dimensions, to showcase:

- How to train DRVI
- How to inspect the latent space (vanished dimensions, UMAP, heatmap)
- How to run the interpretability pipeline and link latent dimensions to genes

The model in this tutorial is imported entirely from scvi-tools (`scvi.external.DRVI`).
But the visualization helpers (`drvi.utils.pl.*`) come from the companion [`drvi-py`](https://github.com/theislab/drvi) package, installed with `pip install drvi-py`.


```{note}
Running the following cell is necessary if running in Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

To install drvi-py package

```python
!pip install --quiet drvi-py
```

## Imports

```python
import os
import tempfile
import warnings

warnings.filterwarnings("ignore")


import anndata as ad

# Helper functions from drvi-py package
import drvi
import scanpy as sc
import scvi
from matplotlib import pyplot as plt
from scvi.external import DRVI

scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
print("Last run with drvi version:", drvi.__version__)
```

```python
sc.set_figure_params(figsize=(4, 4), frameon=False)
save_dir = tempfile.TemporaryDirectory()
plt.rcParams["figure.dpi"] = 100
%config InlineBackend.print_figure_kwargs={'facecolor': 'w'}
%config InlineBackend.figure_format='retina'
```

## Download and load data

We use the immune dataset (Luecken et al.) hosted on SCVERSE S3. The `Villani` batch is already removed because it contains non-count values, and 2000 batch-aware highly variable genes are selected.

```python
adata_path = os.path.join(save_dir.name, "immune_hvg.h5ad")
adata = sc.read(
    adata_path, backup_url="https://exampledata.scverse.org/scvi-tools/Immune_HVG_human.h5ad"
)
adata
```

## Train DRVI

We register the count layer with `scvi.external.DRVI.setup_anndata` and train a model with 128 latent dimensions and two hidden layers of width 128 in both the encoder and the decoder. By default DRVI splits every latent dimension (`n_split_latent = n_latent`) with `split_map` splitting and `logsumexp` aggregation — the fully disentangled setting.

DRVI's general hyperparameters are **fully compatible with scVI** (encoder width/depth, likelihood, covariate handling, and training arguments carry over directly). DRVI expects count data and uses a negative-binomial likelihood by default. Provide additional covariates via `categorical_covariate_keys` / `continuous_covariate_keys` in `setup_anndata` if needed.
Depending on the data and modality, users can also choose other appropriate likelihoods such as Normal (needs library- and log-normalized data) or Poisson.
Please refer to the API documentation for hyperparameter choices.

```python
DRVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
)

model = DRVI(
    adata,
    n_latent=128,
    n_hidden=128,
    n_layers=2,
    # depending on the variability of gene dispersions use 'gene' (default) or 'gene-batch'
    # dispersion='gene-batch',
)
model
```

```python
n_epochs = 400
model.train(
    max_epochs=n_epochs,
    plan_kwargs={"n_epochs_kl_warmup": n_epochs},
)
```

```python
model_path = os.path.join(save_dir.name, "drvi_model")
model.save(model_path, overwrite=True)
# model = DRVI.load(model_path, adata)
```

## Latent space and interpretability scores

We store the latent representation in a new `AnnData` object (`embed`), where each factor is a latent dimension. `DRVI.set_latent_dimension_stats` annotates `embed.var` with per-dimension statistics (reconstruction effect, vanished status, ordering, min/max), and `DRVI.calculate_interpretability_scores` stores per-gene scores in `embed.varm`. The scores are calculated as follows:

- **OOD** (out-of-distribution): traverses each latent dimension through the decoder.
- **IND** (in-distribution): averages each dimension's effect over the observed cells.


**Note:**
The order of latent dimensions (DR 1, DR 2, ...) is different from the order of columns in `embed`. Use `embed.var['title']`.

```python
embed = ad.AnnData(model.get_latent_representation(), obs=adata.obs.copy())

model.set_latent_dimension_stats(embed, vanished_threshold=0.5)
model.calculate_interpretability_scores(embed, "OOD")
model.calculate_interpretability_scores(embed, "IND")
```

```python
sc.pp.neighbors(embed, n_neighbors=10, use_rep="X", n_pcs=embed.X.shape[1])
sc.tl.umap(embed, spread=1.0, min_dist=0.5, random_state=123)
embed
```

```python
sc.pl.umap(embed, color=["batch", "final_annotation"], ncols=1, frameon=False)
```

### Latent dimension stats

```python
embed.var.sort_values("reconstruction_effect", ascending=False)[:5]
```

```python
drvi.utils.pl.plot_latent_dimension_stats(embed, ncols=2)
```

The same plot after removing vanished (inactive) dimensions:

```python
drvi.utils.pl.plot_latent_dimension_stats(embed, ncols=2, remove_vanished=True)
```

### Plot latent dimensions

By default vanished dimensions are not plotted.

#### On the latent UMAP

```python
drvi.utils.pl.plot_latent_dims_in_umap(embed)
```

#### As a heatmap

Heatmaps are useful to relate latent dimensions to known categories of the data. Dimensions can optionally be sorted by the category they are most relevant to.

```python
drvi.utils.pl.plot_latent_dims_in_heatmap(embed, "final_annotation")
```

```python
drvi.utils.pl.plot_latent_dims_in_heatmap(embed, "final_annotation", sort_by_categorical=True)
```

## Interpretability

The per-gene scores were already computed above and live in `embed.varm`.

```python
embed.varm
```

### Out-of-distribution (OOD) scores

The default `OOD_combined` score combines the maximum effect and the specificity of each gene per dimension, which makes it our suggested score for finding the most specific genes of a program. If human-readable gene symbols live in a column of `adata.var`, pass it as `gene_symbols=...`.

All scores can be obtained as a DataFrame (genes × dimensions). This includes all non-vanished dimensions / directions.

```python
gene_scores_df = model.get_interpretability_scores(embed, adata)
gene_scores_df.iloc[:10, :10]
```

```python
drvi.utils.pl.plot_interpretability_scores(gene_scores_df, score_threshold=0.1)
```

We can dig into individual dimensions: visualize a dimension on the UMAP (directional, so `+` and `-` are shown separately) and color the cells by its top genes. The exact dimension titles vary with the run and initialization.

```python
# copy the latent UMAP onto the original (gene-level) AnnData
adata.obsm["X_drvi_umap"] = embed[adata.obs.index].obsm["X_umap"]

# We only show a few interpretable dimensions
for dim_title in gene_scores_df.columns[:4]:
    if gene_scores_df[dim_title].max() < 0.1:
        continue
    top_genes = gene_scores_df[dim_title].sort_values(ascending=False).index.to_list()[:4]
    print(dim_title)
    drvi.utils.pl.plot_latent_dims_in_umap(embed, dim_subset=[dim_title], directional=True)
    sc.pl.embedding(adata, "X_drvi_umap", color=top_genes, frameon=False)
```

### In-distribution (IND) scores

The IND scores average each dimension's effect on each gene over all cells. Because genes are not filtered for uniqueness, broadly affected genes also keep high scores, giving a complete view of how each factor influences the transcriptome.

```python
gene_scores_df_ind = model.get_interpretability_scores(
    embed, adata, key="IND_linear_weighted_mean"
)
gene_scores_df_ind.iloc[:10, :10]
```

```python
drvi.utils.pl.plot_interpretability_scores(gene_scores_df_ind)
```

## Identification of programs

Once the top relevant genes of a dimension are known, the corresponding biological program can be identified using external information such as existing annotations, expert examination, gene-set enrichment analysis (GSEA), the literature, or automated annotation tools. Because this supervised information is never given to the model, the quality of the discovered signatures is neither affected nor biased by it — unidentified dimensions with high gene scores are promising candidates for further investigation.

## More resources

This notebook covered the core DRVI workflow. For more:

- **More tutorials** — the DRVI documentation hosts additional tutorials (e.g. identification of rare cell types and mapping query data onto a DRVI reference): https://drvi.readthedocs.io/latest/tutorials/
- **`drvi-py` package** — beyond the plotting helpers used here, the companion [`drvi-py`](https://github.com/theislab/drvi) package (`pip install drvi-py`) provides more utility functions for latent-space analysis. See the [API documentation](https://drvi.readthedocs.io/) for the full set of tools and plotting functions.
