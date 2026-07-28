# ISOLATED_LABELS — API Reference

**Class:** `scib_metrics.metrics._isolated_labels.isolated_labels`

**Signature:** `isolated_labels(X: numpy.ndarray, labels: numpy.ndarray, batch: numpy.ndarray,
rescale: bool = True, iso_threshold: int | None = None) -> float`

## Docstring

Isolated label score :cite:p:`luecken2022benchmarking`.

Score how well labels of isolated labels are distiguished in the dataset by
average-width silhouette score (ASW) on isolated label vs all other labels.

The default of the original scib package is to use a cluster-based F1 scoring
procedure, but here we use the ASW for speed and simplicity.

Parameters
----------
X
    Array of shape (n_cells, n_features).
labels
    Array of shape (n_cells,) representing label values
batch
    Array of shape (n_cells,) representing batch values
rescale
    Scale asw into the range [0, 1].
iso_threshold
    Max number of batches per label for label to be considered as
    isolated, if integer. If `None`, considers minimum number of
    batches that labels are present in

Returns
-------
isolated_label_score
