# SILHOUETTE_LABEL — API Reference

**Function:** `scib_metrics.metrics._silhouette.silhouette_label`

**Signature:** `silhouette_label(X: numpy.ndarray, labels: numpy.ndarray, rescale: bool = True, chunk_size: int = 256, metric: Literal['euclidean', 'cosine'] = 'euclidean') -> float`

## Docstring

Average silhouette width (ASW) :cite:p:`luecken2022benchmarking`.

Default parameters ('euclidean') match scIB implementation.

Parameters
----------
X
    Array of shape (n_cells, n_features).
labels
    Array of shape (n_cells,) representing label values
rescale
    Scale asw into the range [0, 1].
chunk_size
    Size of chunks to process at a time for distance computation
metric
    The distance metric to use. The distance function can be 'euclidean' (default) or 'cosine'.

Returns
-------
silhouette score
