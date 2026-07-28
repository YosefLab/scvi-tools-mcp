# Benchmarking large-scale integration

Here we walkthrough applying the integration benchmarking metrics on a dataset of non-small cell lung cancer from the following paper:

Salcher, S., Sturm, G., Horvath, L., Untergasser, G., Kuempers, C., Fotakis, G., ... & Trajanoski, Z. (2022). High-resolution single-cell atlas reveals diversity and plasticity of tissue-resident neutrophils in non-small cell lung cancer. Cancer Cell.

This dataset contains ~900,000 cells, so here we demonstrate the scalbility of the metrics here on large data.

```python
import numpy as np
import scanpy as sc
from scvi.data import cellxgene

from scib_metrics.benchmark import Benchmarker, BioConservation, BatchCorrection

%matplotlib inline
```

## Load and preprocess data

```python
url = "https://cellxgene.cziscience.com/e/232f6a5a-a04c-4758-a6e8-88ab2e3a6e69.cxg/"
adata = cellxgene(url, filename="luca.h5ad", save_path="data/")
```

```python
adata
```

```python
sc.pp.subsample(adata, n_obs=500_000)
```

```python
# Number of unique cell types
adata.obs["cell_type"].nunique()
```

```python
adata.var["highly_variable"] = np.asarray(adata.var["is_highly_variable"].astype(bool))
sc.tl.pca(adata)
```

## "Run" methods

The authors used scVI and scANVI in their manuscript, and these embeddings are already stored in the AnnData object. We can use these to run the metrics.

### scVI

```python
adata.obsm["scVI"] = adata.obsm["X_scVI"]
```

### scANVI

```python
adata.obsm["scANVI"] = adata.obsm["X_scANVI"]
```

## Perform the benchmark

Here we use a custom nearest neighbor function to speed up the computation of the metrics. This is not necessary, but can be useful for large datasets.

In particular we use [faiss](https://github.com/facebookresearch/faiss), which can be accelerated with a GPU.

This can be installed as

```bash
conda install -c conda-forge faiss-gpu
```

When using approximate nearest neighbors, an issue can arise where each cell does not get a unique set of K neighbors. This issue happens with faiss hnsw below, so we use the brute force method instead, which is still faster than pynndescent approximate nearest neighbors on CPU.

```python
import faiss

from scib_metrics.nearest_neighbors import NeighborsResults


def faiss_hnsw_nn(X: np.ndarray, k: int):
    """Gpu HNSW nearest neighbor search using faiss.

    See https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md
    for index param details.
    """
    X = np.ascontiguousarray(X, dtype=np.float32)
    res = faiss.StandardGpuResources()
    M = 32
    index = faiss.IndexHNSWFlat(X.shape[1], M, faiss.METRIC_L2)
    gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
    gpu_index.add(X)
    distances, indices = gpu_index.search(X, k)
    del index
    del gpu_index
    # distances are squared
    return NeighborsResults(indices=indices, distances=np.sqrt(distances))


def faiss_brute_force_nn(X: np.ndarray, k: int):
    """Gpu brute force nearest neighbor search using faiss."""
    X = np.ascontiguousarray(X, dtype=np.float32)
    res = faiss.StandardGpuResources()
    index = faiss.IndexFlatL2(X.shape[1])
    gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
    gpu_index.add(X)
    distances, indices = gpu_index.search(X, k)
    del index
    del gpu_index
    # distances are squared
    return NeighborsResults(indices=indices, distances=np.sqrt(distances))
```

```python
import time

adata.obsm["Unintegrated"] = adata.obsm["X_pca"]

biocons = BioConservation(isolated_labels=False)

start = time.time()
bm = Benchmarker(
    adata,
    batch_key="sample",
    label_key="cell_type",
    embedding_obsm_keys=["Unintegrated", "scANVI", "scVI"],
    pre_integrated_embedding_obsm_key="X_pca",
    bio_conservation_metrics=biocons,
    batch_correction_metrics=BatchCorrection(),
    n_jobs=-1,
)
bm.prepare(neighbor_computer=faiss_brute_force_nn)
bm.benchmark()
end = time.time()
print(f"Time: {int((end - start) / 60)} min {int((end - start) % 60)} sec")
```

### Visualize the results

```python
bm.plot_results_table()
```

```python
bm.plot_results_table(min_max_scale=False)
```

We can also access the underlying dataframes to print the results ourselves.

```python
from rich import print

df = bm.get_results(min_max_scale=False)
print(df)
```
