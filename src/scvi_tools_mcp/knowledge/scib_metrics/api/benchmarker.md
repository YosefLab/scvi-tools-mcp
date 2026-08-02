# BENCHMARKER — API Reference

**Class:** `scib_metrics.benchmark._core.Benchmarker`

**Signature:** `Benchmarker(adata: anndata.AnnData, batch_key: str, label_key: str, embedding_obsm_keys: list[str], bio_conservation_metrics: scib_metrics.benchmark._core.BioConservation | None = BioConservation(isolated_labels=True, nmi_ari_cluster_labels_leiden=False, nmi_ari_cluster_labels_kmeans=True, silhouette_label=True, clisi_knn=True), batch_correction_metrics: scib_metrics.benchmark._core.BatchCorrection | None = BatchCorrection(bras=True, ilisi_knn=True, kbet_per_label=True, graph_connectivity=True, pcr_comparison=True, sbee=False), pre_integrated_embedding_obsm_key: str | None = None, n_jobs: int = 1, progress_bar: bool = True, solver: str = 'arpack')`

## Docstring

Benchmarking pipeline for the single-cell integration task.

Parameters
----------
adata
    AnnData object containing the raw count data and integrated embeddings as obsm keys.
batch_key
    Key in `adata.obs` that contains the batch information.
label_key
    Key in `adata.obs` that contains the cell type labels.
embedding_obsm_keys
    List of obsm keys that contain the embeddings to be benchmarked.
bio_conservation_metrics
    Specification of which bio conservation metrics to run in the pipeline.
batch_correction_metrics
    Specification of which batch correction metrics to run in the pipeline.
pre_integrated_embedding_obsm_key
    Obsm key containing a non-integrated embedding of the data. If `None`, the embedding will be computed
    in the prepare step. See the notes below for more information.
n_jobs
    Number of jobs to use for parallelization of neighbor search.
progress_bar
    Whether to show a progress bar for :meth:`~scib_metrics.benchmark.Benchmarker.prepare` and
    :meth:`~scib_metrics.benchmark.Benchmarker.benchmark`.
solver
    SVD solver to use during PCA. can help stability issues. Choose from: "arpack", "randomized" or "auto"

Notes
-----
`adata.X` should contain a form of the data that is not integrated, but is normalized. The `prepare` method will
use `adata.X` for PCA via :func:`~scanpy.tl.pca`, which also only uses features masked via `adata.var['highly_variable']`.

See further usage examples in the following tutorial:

1. :doc:`/notebooks/lung_example`

## prepare

```python
Benchmarker.prepare(self, neighbor_computer: collections.abc.Callable[[numpy.ndarray, int], scib_metrics.nearest_neighbors._dataclass.NeighborsResults] | None = None) -> None
```

Prepare the data for benchmarking.

Parameters
----------
neighbor_computer
    Function that computes the neighbors of the data. If `None`, the neighbors will be computed
    with :func:`~scib_metrics.utils.nearest_neighbors.pynndescent`. The function should take as input
    the data and the number of neighbors to compute and return a :class:`~scib_metrics.utils.nearest_neighbors.NeighborsResults`
    object.

## benchmark

```python
Benchmarker.benchmark(self) -> None
```

Run the pipeline.

## get_results

```python
Benchmarker.get_results(self, min_max_scale: bool = False, clean_names: bool = True) -> pandas.DataFrame
```

Return the benchmarking results.

Parameters
----------
min_max_scale
    Whether to min max scale the results.
clean_names
    Whether to clean the metric names.

Returns
-------
The benchmarking results.

## plot_results_table

```python
Benchmarker.plot_results_table(self, min_max_scale: bool = False, show: bool = True, save_dir: str | None = None) -> plottable.table.Table
```

Plot the benchmarking results.

Parameters
----------
min_max_scale
    Whether to min max scale the results.
show
    Whether to show the plot.
save_dir
    The directory to save the plot to. If `None`, the plot is not saved.
