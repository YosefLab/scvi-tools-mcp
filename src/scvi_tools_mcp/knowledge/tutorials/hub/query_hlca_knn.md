# Querying the Human Lung Cell Atlas

Here we demonstrate how to query the Human Lung Cell Atlas using scANVI, scArches, and scvi-hub.

- Sikkema, Lisa, et al. "An integrated cell atlas of the human lung in health and disease." [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.03.10.483747v1) (2022).

If you use this tutorial in your research we recommend citing the HLCA as well as scANVI, scArches, and scvi-tools, which can be found on the [references page](https://docs.scvi-tools.org/en/stable/references.html) at Gayoso22, Lotfollahi21, Xu21 respectively.

This tutorial is adapted from a [similar one](https://github.com/LungCellAtlas/mapping_data_to_the_HLCA/blob/main/notebooks/LCA_scArches_mapping_new_data_to_hlca.ipynb) presented by the HLCA authors.

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
import numba
import numpy as np
import pandas as pd
import pooch
import pynndescent
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.hub import HubModel
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

## Download the reference files

First we download the pre-trained scANVI model from the HuggingFace [repo](https://huggingface.co/scvi-tools/human-lung-cell-atlas).

```python
hubmodel = HubModel.pull_from_huggingface_hub(
    "scvi-tools/human-lung-cell-atlas-scanvi", cache_dir=save_dir.name
)
adata = hubmodel.adata
model = hubmodel.model
```

```python
adata
```

```python
model
```

```python
model.view_anndata_setup()
```

## Learn a neighbors index on reference latent space

Here we create the neighbors index using `PyNNDescent`. We will use this later to classify query cells. `PyNNDescent` is an extremely fast approximate neighbors technique.

In the case of the `HubModel` instance above, we see that the data is in minified mode, meaning the count data is not actually in the object, and we only store a minified representation of the data. We see that we can access the mean of the embedding (`latent_qzm`) above.

```python
X_train = adata.obsm["scanvi_latent_qzm"]
ref_nn_index = pynndescent.NNDescent(X_train)
ref_nn_index.prepare()
```

## Download query data

In this tutorial we use the fresh, single-cell sample from the following publication:

- Delorey, Toni M., et al. "COVID-19 tissue atlases reveal SARS-CoV-2 pathology and cellular targets." Nature 595.7865 (2021): 107-113.

In principle at this stage you may load your own data. There are few important notes though:

- Using the HLCA requires using Gene IDs for the query data
- The query data should include batches in `query_data.obs["dataset"]`
- It's necessary to run `query_data.obs["scanvi_label"] = "unlabeled"` so that scvi-tools can properly register the query data.

```python
def download_data(save_path: str):
    """Download and cache the query data."""
    data_path = pooch.retrieve(
        url="https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM5230nnn/GSM5230027/suppl/GSM5230027_04-P103142-S149-R01_raw_feature_bc_matrix.h5.gz",
        known_hash="3b7f8318059d655ea774752b6d8b13381323f5018e9f3868ffc53674f94f537f",
        fname="query_data.h5.gz",
        path=save_path,
        processor=pooch.Decompress(),
        progressbar=True,
    )
    metadata_path = pooch.retrieve(
        url="https://ftp.ncbi.nlm.nih.gov/geo/series/GSE171nnn/GSE171668/suppl/GSE171668_lung_metadata.csv.gz",
        known_hash="290b0ac86e85183e65eefb68670ad27fc5156866144d9ac6f2eb27f34e31e79e",
        fname="query_metadata.csv.gz",
        path=save_path,
        processor=pooch.Decompress(),
        progressbar=True,
    )
    return data_path, metadata_path
```

```python
query_data_path, query_metadata_path = download_data(save_dir.name)

query_adata = sc.read_10x_h5(query_data_path)
query_metadata = pd.read_csv(query_metadata_path, index_col=0)
```

```python
# clean up .var.index (gene names)
query_adata.var["gene_names"] = query_adata.var.index
query_adata.var.index = [idx.split("___")[-1] for idx in query_adata.var.gene_ids]
# clean up cell barcodes:
query_adata.obs.index = query_adata.obs.index.str.rstrip("-1")
# read in metadata (to select only cells of interest and remove empty drops)
# subset to cells from our sample
query_metadata = query_metadata.loc[query_metadata.donor == "D12_4", :].copy()
# clean up barcodes:
query_metadata.index = [idx.split("-")[-1] for idx in query_metadata.index]
# subset adata to cells in metadata:
query_adata = query_adata[query_metadata.index, :].copy()
# add dataset information:
query_adata.obs["dataset"] = "test_dataset_delorey_regev"
```

## Loading the query model from the reference files

Here we run `prepare_query_anndata`, which reorders the genes and pads any missing genes with 0s. This should generally be run before reference mapping with scArches to ensure data correctness.

```{important}
Below we use the path to the model we downloaded from HuggingFace. While in most cases the model instance can be used instead of the path, here the reference model's adata is in minified mode.
```

```python
scvi.model.SCANVI.prepare_query_anndata(query_adata, model)
```

From above, we see that the model is expecting a labels key with the name `"scanvi_label"`.

```python
query_adata.obs["scanvi_label"] = "unlabeled"
```

```python
query_model = scvi.model.SCANVI.load_query_data(query_adata, model)
```

Here we use scArches/scANVI-specific query training arguments.

```python
surgery_epochs = 500
train_kwargs_surgery = {
    "early_stopping": True,
    "early_stopping_monitor": "elbo_train",
    "early_stopping_patience": 10,
    "early_stopping_min_delta": 0.001,
    "plan_kwargs": {"weight_decay": 0.0},
}
```

```python
query_model.train(max_epochs=surgery_epochs, **train_kwargs_surgery)
```

```python
query_model_path = os.path.join(save_dir.name, "query_model")
query_model.save(query_model_path, overwrite=True)
```

```python
query_emb = anndata.AnnData(query_model.get_latent_representation())
query_emb.obs_names = query_adata.obs_names
```

Now let's store the predictions in the query embedding object. We reuse the PyNNDescent index from before, converting distances to affinities, and weighting the predictions using these affinities.

This follows the same approach used in the HLCA.

```python
ref_neighbors, ref_distances = ref_nn_index.query(query_emb.X)

# convert distances to affinities
stds = np.std(ref_distances, axis=1)
stds = (2.0 / stds) ** 2
stds = stds.reshape(-1, 1)
ref_distances_tilda = np.exp(-np.true_divide(ref_distances, stds))
weights = ref_distances_tilda / np.sum(ref_distances_tilda, axis=1, keepdims=True)


@numba.njit
def weighted_prediction(weights, ref_cats):
    """Get highest weight category."""
    N = len(weights)
    predictions = np.zeros((N,), dtype=ref_cats.dtype)
    uncertainty = np.zeros((N,))
    for i in range(N):
        obs_weights = weights[i]
        obs_cats = ref_cats[i]
        best_prob = 0
        for c in np.unique(obs_cats):
            cand_prob = np.sum(obs_weights[obs_cats == c])
            if cand_prob > best_prob:
                best_prob = cand_prob
                predictions[i] = c
                uncertainty[i] = max(1 - best_prob, 0)

    return predictions, uncertainty


# for each annotation level, get prediction and uncertainty
label_keys = [f"ann_level_{i}" for i in range(1, 6)] + ["ann_finest_level"]
for l in label_keys:
    ref_cats = adata.obs[l].cat.codes.to_numpy()[ref_neighbors]
    p, u = weighted_prediction(weights, ref_cats)
    p = np.asarray(adata.obs[l].cat.categories)[p]
    query_emb.obs[l + "_pred"], query_emb.obs[l + "_uncertainty"] = p, u
```

Now let's filter our predictions on the uncertainty threshold, which is discussed in the HLCA manuscript.

```python
uncertainty_threshold = 0.2
for l in label_keys:
    mask = query_emb.obs[l + "_uncertainty"] > 0.2
    print(f"{l}: {sum(mask) / len(mask)} unknown")
    query_emb.obs[l + "_pred"].loc[mask] = "Unknown"
```

```python
query_emb.obs["dataset"] = "test_dataset_delorey_regev"
```

## Combine embeddings

```python
ref_emb = anndata.AnnData(X_train, obs=adata.obs)
ref_emb
```

```python
query_emb
```

```python
combined_emb = ref_emb.concatenate(query_emb)
```

## Visualize embeddings and predictions

In order for the notebook to run faster here, we recomment to swtich to RAPIDS (see https://docs.rapids.ai/install/). In this tutorial we will show how to visualrize the embeddings using UMAPs

```python
LATENT_KEY = "X_scanVI"
combined_emb.obsm[LATENT_KEY] = combined_emb.X
```

```python
sc.pp.neighbors(combined_emb, use_rep=LATENT_KEY)
sc.tl.umap(combined_emb, min_dist=0.3)
colors = [l + "_uncertainty" for l in label_keys]
sc.pl.umap(
    combined_emb,
    color=colors,
    ncols=2,
    frameon=False,
)
```

```python
colors = [l + "_pred" for l in label_keys]
sc.pl.umap(
    combined_emb,
    color=colors,
    ncols=1,
    size=0.5,
    frameon=False,
)
```

```python
sc.pl.umap(
    combined_emb,
    color="ann_finest_level",
    ncols=1,
    size=0.5,
    frameon=False,
)
```
