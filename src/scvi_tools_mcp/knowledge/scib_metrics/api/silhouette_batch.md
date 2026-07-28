# SILHOUETTE_BATCH — API Reference

**Function:** `scib_metrics.metrics._silhouette.silhouette_batch`

**Signature:** `silhouette_batch(X: numpy.ndarray, labels: numpy.ndarray, batch: numpy.ndarray, rescale: bool = True, chunk_size: int = 256, metric: Literal['euclidean', 'cosine'] = 'euclidean', between_cluster_distances: Literal['nearest', 'mean_other', 'furthest'] = 'nearest') -> float`

## Docstring

Average silhouette width (ASW) with respect to batch ids within each label :cite:p:`luecken2022benchmarking`.

Default parameters ('euclidean', 'nearest') match scIB implementation.

Additional options enable BRAS compatible usage (see :func:`~scib_metrics.metrics.bras` documentation).

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
    - 'nearest': Standard silhouette (distance to nearest cluster)
    - 'mean_other': BRAS-specific (mean distance to all other clusters)
    - 'furthest': BRAS-specific (distance to furthest cluster)

Returns
-------
silhouette score
