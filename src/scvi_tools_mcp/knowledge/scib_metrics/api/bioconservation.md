# BIOCONSERVATION — API Reference

**Class:** `scib_metrics.benchmark._core.BioConservation`

**Signature:** `BioConservation(isolated_labels: bool | dict[str, typing.Any] = True, nmi_ari_cluster_labels_leiden: bool | dict[str, typing.Any] = False, nmi_ari_cluster_labels_kmeans: bool | dict[str, typing.Any] = True, silhouette_label: bool | dict[str, typing.Any] = True, clisi_knn: bool | dict[str, typing.Any] = True) -> None`

## Docstring

Specification of bio conservation metrics to run in the pipeline.

Metrics can be included using a boolean flag. Custom keyword args can be
used by passing a dictionary here. Keyword args should not set data-related
parameters, such as `X` or `labels`.
