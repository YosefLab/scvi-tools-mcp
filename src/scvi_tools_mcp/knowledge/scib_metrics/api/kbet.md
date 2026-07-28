# KBET — API Reference

**Function:** `scib_metrics.metrics._kbet.kbet`

**Signature:** `kbet(X: scib_metrics.nearest_neighbors._dataclass.NeighborsResults, batches: numpy.ndarray, alpha: float = 0.05) -> float`

## Docstring

Compute kbet :cite:p:`buttner2018`.

This implementation is inspired by the implementation in Pegasus:
https://pegasus.readthedocs.io/en/stable/index.html

A higher acceptance rate means more mixing of batches. This implementation does
not exactly mirror the default original implementation, as there is currently no
`adapt` option.

Note that this is also not equivalent to the kbet used in the original scib package,
as that one computes kbet for each cell type label. To achieve this, use
:func:`scib_metrics.kbet_per_label`.

Parameters
----------
X
    A :class:`~scib_metrics.utils.nearest_neighbors.NeighborsResults` object.
batches
    Array of shape (n_cells,) representing batch values
    for each cell.
alpha
    Significance level for the statistical test.

Returns
-------
acceptance_rate
    Kbet acceptance rate of the sample.
stat_mean
    Mean Kbet chi-square statistic over all cells.
pvalue_mean
    Mean Kbet p-value over all cells.
