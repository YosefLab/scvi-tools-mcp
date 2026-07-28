# GRAPH_CONNECTIVITY — API Reference

**Class:** `scib_metrics.metrics._graph_connectivity.graph_connectivity`

**Signature:** `graph_connectivity(X: scib_metrics.nearest_neighbors._dataclass.NeighborsResults, labels: numpy.ndarray) -> float`

## Docstring

Quantify the connectivity of the subgraph per cell type label.

Parameters
----------
X
    Array of shape (n_cells, n_cells) with non-zero values
    representing distances to exactly each cell's k nearest neighbors.
labels
    Array of shape (n_cells,) representing label values
    for each cell.
