# ScBasset: Analyzing scATACseq data

```{warning}
SCBASSET's development is still in progress. The current version may not fully reproduce the original implementation's results.
```

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import tempfile

import matplotlib.pyplot as plt
import muon
import numpy as np
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

## Loading data and preprocessing

Throughout this tutorial, we use [sample multiome data from 10X of 10K PBMCs](https://www.10xgenomics.com/resources/datasets/10-k-human-pbm-cs-multiome-v-1-0-chromium-x-1-standard-2-0-0).

```python
url = "https://cf.10xgenomics.com/samples/cell-arc/2.0.0/10k_PBMC_Multiome_nextgem_Chromium_X/10k_PBMC_Multiome_nextgem_Chromium_X_filtered_feature_bc_matrix.h5"
mdata = muon.read_10x_h5("data/multiome10k.h5mu", backup_url=url)
```

```python
mdata
```

```python
adata = mdata.mod["atac"]
```

We can use scanpy functions to handle, filter, and manipulate the data. In our case, we might want to filter out peaks that are rarely detected, to make the model train faster:

```python
print(adata.shape)
# compute the threshold: 5% of the cells
min_cells = int(adata.shape[0] * 0.05)
# in-place filtering of regions
sc.pp.filter_genes(adata, min_cells=min_cells)
print(adata.shape)
```

```python
adata.var
```

```python
split_interval = adata.var["gene_ids"].str.split(":", expand=True)
adata.var["chr"] = split_interval[0]
split_start_end = split_interval[1].str.split("-", expand=True)
adata.var["start"] = split_start_end[0].astype(int)
adata.var["end"] = split_start_end[1].astype(int)
adata.var
```

```python
# Filter out non-chromosomal regions
mask = adata.var["chr"].str.startswith("chr")
adata = adata[:, mask].copy()
```

```python
scvi.data.add_dna_sequence(
    adata,
    genome_name="GRCh38",
    genome_dir="data",
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
)
adata
```

```python
adata.varm["dna_sequence"]
```

## Creating and training the model

We can now set up the AnnData object, which will ensure everything the model needs is in place for training.

This is also the stage where we can condition the model on additional covariates, which encourages the model to remove the impact of those covariates from the learned latent space. Our sample data is a single batch, so we won't demonstrate this directly, but it can be done simply by setting the `batch_key` argument to the annotation to be used as a batch covariate (must be a valid key in `adata.obs`) .

```python
# alternatively load the local preprocessed data
# import os
# temp_dir_obj = tempfile.TemporaryDirectory()

# adata_path = os.path.join(temp_dir_obj.name, "adata_scbasset.h5ad")
# adata = sc.read(adata_path, backup_url="https://exampledata.scverse.org/scvi-tools/adata_scbasset.h5ad")
# adata
```

```python
bdata = adata.transpose()
bdata.layers["binary"] = (bdata.X.copy() > 0).astype(float)
scvi.external.SCBASSET.setup_anndata(bdata, layer="binary", dna_code_key="dna_code")
```

We can now create a scBasset model object and train it!

```{note}
The default max epochs is set to 1000, but in practice scBasset stops early once the model converges, which especially for large datasets (which require fewer epochs to converge, since each epoch includes letting the model view more data).
```

Here we are using 16 bit precision which uses less memory without sacrificing performance.

```python
bas = scvi.external.SCBASSET(bdata)
bas.train(max_epochs=150, precision=16)
```

```python
fig, ax = plt.subplots()
bas.history_["train_loss"].plot(ax=ax)
bas.history_["validation_loss"].plot(ax=ax)
```

```python
fig, ax = plt.subplots()
bas.history_["auroc_train"].plot(ax=ax)
bas.history_["auroc_validation"].plot(ax=ax)
```

## Visualizing and analyzing the latent space

We can now use the trained model to visualize, cluster, and analyze the data. We first extract the latent representation from the model, and save it back into our AnnData object:

```python
latent = bas.get_latent_representation()
adata.obsm["X_scbasset"] = latent

print(latent.shape)
```

```python
sns.scatterplot(
    x=bas.get_cell_bias(),
    y=np.log10(np.asarray(adata.X.sum(1))).ravel(),
    s=3,
)
plt.xlabel("Cell bias")
plt.ylabel("log10(UMI count)")
```

We can now use scanpy functions to cluster and visualize our latent space:

```python
# compute the k-nearest-neighbor graph that is used in both clustering and umap algorithms
sc.pp.neighbors(adata, use_rep="X_scbasset")
# compute the umap
sc.tl.umap(adata)
sc.tl.leiden(adata, key_added="leiden_scbasset")
```

```python
sc.pl.umap(adata, color="leiden_scbasset")
```

## Score TF activity

We will now use the motif injection procedure to infer the activity of human transcription factors using their motifs.

This process involves downloading a library of (1) random dinucleotide shuffled sequences and (2) random sequences with a known motif injected. We infer the accessibility of all the random sequences and all the motif injected sequences in every cell using the SCBASSET model. We then compute the difference in activity for the motif injected sequences and the random sequences. This difference serves as an estimate for the likelihood that a given motif is accessible in each cell, and therefore an estimate of a corresponding transcription factor's activity.

Any library with sequences of the appropriate size can be used. By default, we provide the human TF motif library used in the scBasset paper. The library is downloaded to a local folder (default: `./scbasset_motifs`). Each motif is stored in a specific FASTA file in the `{library_path}/shuffled_peaks_motifs` subdirectory. To see all available motifs, simply glob the path (e.g. `Path("./scbasset_motifs/shuffled_peaks_motifs").glob("*.fasta")`).

```python
tfs = ["PAX5", "TCF7", "RXRA"]

for tf in tfs:
    adata.obs[f"bas_{tf}"] = bas.get_tf_activity(
        tf=tf,
        motif_dir="data/motifs",
    )
```

```python
sc.pl.umap(
    adata,
    color=[f"bas_{tf}" for tf in tfs],
    cmap="PRGn_r",
    vmin=-2,
    vmax=2,
)
```
