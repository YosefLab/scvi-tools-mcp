# KBET_PER_LABEL — API Reference

**Function:** `scib_metrics.metrics._kbet.kbet_per_label`

**Signature:** `kbet_per_label(X: scib_metrics.nearest_neighbors._dataclass.NeighborsResults, batches: numpy.ndarray, labels: numpy.ndarray, alpha: float = 0.05, diffusion_n_comps: int = 100, return_df: bool = False) -> float | tuple[float, pandas.DataFrame]`

## Docstring

Compute kBET score per cell type label as in :cite:p:`luecken2022benchmarking`.

This approximates the method used in the original scib package. Notably, the underlying
kbet might have some inconsistencies with the R implementation. Furthermore, to equalize
the neighbor graphs of cell type subsets we use diffusion distance approximated with diffusion
maps. Increasing `diffusion_n_comps` will increase the accuracy of the approximation.

Parameters
----------
X
    A :class:`~scib_metrics.utils.nearest_neighbors.NeighborsResults` object.
batches
    Array of shape (n_cells,) representing batch values
    for each cell.
alpha
    Significance level for the statistical test.
diffusion_n_comps
    Number of diffusion components to use for diffusion distance approximation.
return_df
    Return dataframe of results in addition to score.

Returns
-------
kbet_score
    Kbet score over all cells. Higher means more integrated, as in the kBET acceptance rate.
df
    Dataframe with kBET score per cell type label.

Notes
-----
This function requires X to be cell-cell connectivities, not distances.
