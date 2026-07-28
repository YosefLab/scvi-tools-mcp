# NMI_ARI_CLUSTER_LABELS_LEIDEN — API Reference

**Class:** `scib_metrics.metrics._nmi_ari.nmi_ari_cluster_labels_leiden`

**Signature:** `nmi_ari_cluster_labels_leiden(X: scib_metrics.nearest_neighbors._dataclass.NeighborsResults, labels: numpy.ndarray, optimize_resolution: bool = True, resolution: float = 1.0, n_jobs: int = 1, seed: int = 42) -> dict[str, float]`

## Docstring

Compute nmi and ari between leiden clusters and labels.

This deviates from the original implementation in scib by using leiden instead of
louvain clustering. Installing joblib allows for parallelization of the leiden
resoution optimization.

Parameters
----------
X
    A :class:`~scib_metrics.utils.nearest_neighbors.NeighborsResults` object.
labels
    Array of shape (n_cells,) representing label values
optimize_resolution
    Whether to optimize the resolution parameter of leiden clustering by searching over
    10 values
resolution
    Resolution parameter of leiden clustering. Only used if optimize_resolution is False.
n_jobs
    Number of jobs for parallelizing resolution optimization via joblib. If -1, all CPUs
    are used.
seed
    Seed used for reproducibility of clustering.

Returns
-------
nmi
    Normalized mutual information score
ari
    Adjusted rand index score
