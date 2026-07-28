# NMI_ARI_CLUSTER_LABELS_KMEANS — API Reference

**Function:** `scib_metrics.metrics._nmi_ari.nmi_ari_cluster_labels_kmeans`

**Signature:** `nmi_ari_cluster_labels_kmeans(X: numpy.ndarray, labels: numpy.ndarray) -> dict[str, float]`

## Docstring

Compute nmi and ari between k-means clusters and labels.

This deviates from the original implementation in scib by using k-means
with k equal to the known number of cell types/labels. This leads to
a more efficient computation of the nmi and ari scores.

Parameters
----------
X
    Array of shape (n_cells, n_features).
labels
    Array of shape (n_cells,) representing label values

Returns
-------
nmi
    Normalized mutual information score
ari
    Adjusted rand index score
