# BATCHCORRECTION — API Reference

**Class:** `scib_metrics.benchmark._core.BatchCorrection`

**Signature:** `BatchCorrection(bras: bool | dict[str, typing.Any] = True, ilisi_knn: bool | dict[str, typing.Any] = True, kbet_per_label: bool | dict[str, typing.Any] = True, graph_connectivity: bool | dict[str, typing.Any] = True, pcr_comparison: bool | dict[str, typing.Any] = True) -> None`

## Docstring

Specification of which batch correction metrics to run in the pipeline.

Metrics can be included using a boolean flag. Custom keyword args can be
used by passing a dictionary here. Keyword args should not set data-related
parameters, such as `X` or `labels`.
