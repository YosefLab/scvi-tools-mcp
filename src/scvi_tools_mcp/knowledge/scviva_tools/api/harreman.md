# HARREMAN — API Reference

**Class:** `scviva.tools.harreman._analysis.HarremanAnalysis`

**Signature:** `HarremanAnalysis(adata: 'AnnData', model: 'BaseModelClass | None' = None, layer_key: 'str | None' = None) -> 'None'`

## Docstring

Downstream spatial metabolic cell-cell communication analysis.

Parameters
----------
adata
    Spatial AnnData. Must have neighbor coordinates in ``obsm``.
model
    Optional trained scvi spatial model (RESOLVI, SCVIVA, DestVI).

    - DestVI: calls ``model.get_proportions()`` and attaches each cell-type
      proportion-weighted count matrix as ``adata.layers[cell_type]``.
    - RESOLVI: calls ``model.get_normalized_expression()`` and attaches as
      ``adata.layers[HARREMAN_DENOISED_LAYER]``.
    - SCVIVA: calls ``model.get_latent_representation()`` and attaches as
      ``adata.obsm[HARREMAN_LATENT_OBSM]``.

    Model reference is dropped after extraction.
layer_key
    Layer to use for counts. ``None`` uses ``adata.X``.

Examples
--------
Without model:

>>> ha = HarremanAnalysis(adata)
>>> ha.setup(compute_neighbors_on_key="spatial", species="human")
>>> ha.filter_genes()
>>> ha.compute_gene_pairs()
>>> ha.compute_cell_communication()
>>> ha.select_significant_interactions()
>>> results = ha.results

With DestVI model:

>>> ha = HarremanAnalysis(adata, model=destvi_model)
>>> ha.setup(compute_neighbors_on_key="spatial", cell_type_key="cell_type")
>>> ha.compute_gene_pairs()
>>> ha.compute_cell_communication(mode="cell_type")
