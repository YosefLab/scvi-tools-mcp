# BRAS — API Reference

**Function:** `scib_metrics.metrics._silhouette.bras`

**Signature:** `bras(X: numpy.ndarray, labels: numpy.ndarray, batch: numpy.ndarray, chunk_size: int = 256, metric: Literal['euclidean', 'cosine'] = 'cosine', between_cluster_distances: Literal['mean_other', 'furthest'] = 'mean_other') -> float`

## Docstring

Batch removal adapted silhouette (BRAS) for single-cell data integration assessment :cite:p:`rautenstrauch2025`.

BRAS evaluates batch effect removal with respect to batch ids within each label (cell type cluster),
using a modified silhouette score that accounts for nested batch effects. Unlike standard silhouette,
BRAS computes between-cluster distances using the `between_cluster_distances` method rather than
nearest-cluster approach. A higher scores indicates better batch mixing.

Parameters
----------
X
    Array of shape (n_cells, n_features).
labels
    Array of shape (n_cells,) representing label values
batch
    Array of shape (n_cells,) representing batch values
rescale
    Scale asw into the range [0, 1]. If True, higher values are better.
chunk_size
    Size of chunks to process at a time for distance computation.
metric
    The distance metric to use. The distance function can be 'euclidean' (default) or 'cosine'.
between_cluster_distances
    Method for computing inter-cluster distances.
    - 'mean_other': Mean distance to all cells in other clusters (default)
    - 'furthest': Distance to furthest cluster (conservative estimate)

Returns
-------
BRAS score
