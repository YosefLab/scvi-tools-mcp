# PCR_COMPARISON — API Reference

**Class:** `scib_metrics.metrics._pcr_comparison.pcr_comparison`

**Signature:** `pcr_comparison(X_pre: numpy.ndarray | jax.Array, X_post: numpy.ndarray | jax.Array, covariate: numpy.ndarray | jax.Array, scale: bool = True, **kwargs) -> float`

## Docstring

Principal component regression (PCR) comparison :cite:p:`buttner2018`.

Compare the explained variance before and after integration.

Parameters
----------
X_pre
    Pre-integration array of shape (n_cells, n_features).
X_post
    Post-integration array of shape (n_celss, n_features).
covariate_pre:
    Array of shape (n_cells,) or (n_cells, 1) representing batch/covariate values.
scale
    Whether to scale the score between 0 and 1. If True, larger values correspond to
    larger differences in variance contributions between `X_pre` and `X_post`.
kwargs
    Keyword arguments passed into :func:`~scib_metrics.principal_component_regression`.

Returns
-------
pcr_compared: float
    Principal component regression score comparing the explained variance before and
    after integration.
