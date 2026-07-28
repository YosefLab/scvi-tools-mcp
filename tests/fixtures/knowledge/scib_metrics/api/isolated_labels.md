# ISOLATED_LABELS — API Reference

**Class:** `scib_metrics.metrics._isolated_labels.isolated_labels`

**Signature:** `isolated_labels(X, labels, batch, rescale=True, iso_threshold=None) -> float`

## Docstring

Isolated label score.

Score how well labels of isolated labels are distinguished in the dataset by
average-width silhouette score (ASW) on isolated label vs all other labels.
