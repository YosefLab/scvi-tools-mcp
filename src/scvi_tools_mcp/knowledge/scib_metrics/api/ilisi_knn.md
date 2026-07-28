# ILISI_KNN — API Reference

**Function:** `scib_metrics.metrics._lisi.ilisi_knn`

**Signature:** `ilisi_knn(X: scib_metrics.nearest_neighbors._dataclass.NeighborsResults, batches: numpy.ndarray, perplexity: float = None, scale: bool = True) -> float`

## Docstring

Compute the integration local inverse simpson index (iLISI) for each cell :cite:p:`korsunsky2019harmony`.

Returns a scaled version of the iLISI score for each cell, by default :cite:p:`luecken2022benchmarking`.

Parameters
----------
X
    A :class:`~scib_metrics.utils.nearest_neighbors.NeighborsResults` object.
batches
    Array of shape (n_cells,) representing batch values
    for each cell.
perplexity
    Parameter controlling effective neighborhood size. If None, the
    perplexity is set to the number of neighbors // 3.
scale
    Scale lisi into the range [0, 1]. If True, higher values are better.

Returns
-------
ilisi
    iLISI score.
