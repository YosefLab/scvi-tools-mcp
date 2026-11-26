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

Notes
-----
Lower-level functions are grouped under accessors that default to this
object's AnnData:

- ``ha.hs`` -- hotspot analysis, see :class:`~scviva.tools.harreman.HarremanHotspotAccessor`.
- ``ha.vs`` -- VISION signatures, see :class:`~scviva.tools.harreman.HarremanVisionAccessor`.
- ``ha.tl`` -- graph and interaction tools, see
  :class:`~scviva.tools.harreman.HarremanToolsAccessor`.
- ``ha.pl`` -- plotting, see :class:`~scviva.tools.harreman.HarremanPlottingAccessor`.

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

## setup

```python
HarremanAnalysis.setup(self, compute_neighbors_on_key: 'str', species: "Literal['human', 'mouse']" = 'human', database: "Literal['transporter', 'LR', 'both']" = 'both', n_neighbors: 'int | None' = 30, neighborhood_radius: 'float | None' = None, cell_type_key: 'str | None' = None, sample_key: 'str | None' = None, spot_diameter: 'int' = 10, extracellular_only: 'bool' = True, use_gpu: 'bool | None' = None) -> 'None'
```

Register adata with HarremanDB and build the spatial proximity graph.

Parameters
----------
compute_neighbors_on_key
    Key in ``adata.obsm`` to use for KNN computation (e.g. ``"spatial"``).
species
    ``"human"`` or ``"mouse"``.
database
    Which database to load: ``"transporter"``, ``"LR"``, or ``"both"``.
n_neighbors
    Number of nearest neighbors. Either this or ``neighborhood_radius`` required.
neighborhood_radius
    Radius for neighborhood graph. Alternative to ``n_neighbors``.
cell_type_key
    Key in ``adata.obs`` for cell types. Required for ``mode="cell_type"``.
sample_key
    Key in ``adata.obs`` for sample/batch.
spot_diameter
    Spot diameter of the spatial technology.
extracellular_only
    Restrict HarremanDB to extracellular metabolites only.
use_gpu
    ``None`` (default) tries GPU via rapids_singlecell/cuML and falls back to CPU.
    ``False`` forces CPU. ``True`` raises if GPU is unavailable.

## filter_genes

```python
HarremanAnalysis.filter_genes(self, model: "Literal['danb', 'bernoulli', 'normal', 'none']" = 'danb', feature_elimination: 'bool' = False, threshold: 'float' = 0.2, autocorrelation_filt: 'bool' = False, expression_filt: 'bool' = False, de_filt: 'bool' = False, device: 'str | None' = None, verbose: 'bool' = False) -> 'None'
```

Filter genes before gene pair computation.

Parameters
----------
model
    Expression model for autocorrelation-based filtering.
feature_elimination
    Filter genes expressed in fewer than ``threshold`` fraction of cells.
threshold
    Minimum fraction of cells expressing a gene.
autocorrelation_filt
    Keep only genes with significant local autocorrelation.
expression_filt
    Keep only genes expressed in each cell type.
de_filt
    Keep only genes differentially expressed between cell types.
device
    PyTorch device string. ``None`` uses auto-selection.
verbose
    Print progress.

## compute_gene_pairs

```python
HarremanAnalysis.compute_gene_pairs(self, cell_type_pairs: 'list | None' = None, ct_specific: 'bool' = True, fix_ct: 'str | None' = None, verbose: 'bool' = False) -> 'None'
```

Compute local correlations for gene pairs in the metabolite database.

Requires ``setup()`` to have been called.

Parameters
----------
cell_type_pairs
    List of ``(ct_a, ct_b)`` tuples. If ``None``, uses all pairs.
ct_specific
    Restrict gene pairs to cell-type-relevant combinations.
fix_ct
    Fix one cell type across all pairs.
verbose
    Print progress messages.

## compute_cell_communication

```python
HarremanAnalysis.compute_cell_communication(self, mode: "Literal['standard', 'cell_type']" = 'standard', model: 'str | None' = None, n_permutations: 'int' = 1000, seed: 'int' = 42, test: "Literal['parametric', 'non-parametric', 'both']" = 'both', mean: "Literal['algebraic', 'geometric']" = 'algebraic', layer_key_p_test: 'str | None' = None, layer_key_np_test: 'str | None' = None, device: 'str | None' = None, verbose: 'bool' = False) -> 'None'
```

Compute ligand-receptor / metabolite CCC scores.

Requires ``compute_gene_pairs()`` to have been called.

Parameters
----------
mode
    ``"standard"`` for cell-type-agnostic analysis or ``"cell_type"``
    for cell-type-stratified analysis.
model
    Expression normalization model.
n_permutations
    Number of permutations for the non-parametric test.
seed
    Random seed for reproducibility.
test
    Statistical test to run.
mean
    Averaging method for multi-gene interactions.
layer_key_p_test
    Layer to use for the parametric test. Defaults to the layer set at
    construction time (``layer_key``).
layer_key_np_test
    Layer to use for the non-parametric test. Defaults to the layer set at
    construction time (``layer_key``). Pass a different value from
    ``layer_key_p_test`` to use separate layers (e.g. raw counts vs log-norm).
device
    PyTorch device string. ``None`` uses the underlying default.
verbose
    Print progress.

## compute_interacting_cell_scores

```python
HarremanAnalysis.compute_interacting_cell_scores(self, mode: "Literal['standard', 'cell_type']" = 'standard', test: "Literal['parametric', 'non-parametric', 'both']" = 'both', restrict_significance: "Literal['gene pairs', 'metabolites', 'both']" = 'both', n_permutations: 'int' = 1000, seed: 'int' = 42, device: 'str | None' = None, verbose: 'bool' = False) -> 'None'
```

Compute per-cell interaction scores.

Requires ``compute_cell_communication()`` to have been called.

Parameters
----------
mode
    ``"standard"`` or ``"cell_type"`` matching the CCC mode used.
test
    Which test scores to compute.
restrict_significance
    Which significant interactions to use from CCC results.
n_permutations
    Permutations for non-parametric test.
seed
    Random seed.
device
    PyTorch device string.
verbose
    Print progress.

## select_significant_interactions

```python
HarremanAnalysis.select_significant_interactions(self, fdr_threshold: 'float' = 0.05, test: "Literal['parametric', 'non-parametric']" = 'parametric', use_fdr: 'bool' = True, ct_aware: 'bool | None' = None) -> 'None'
```

Filter to statistically significant interactions.

Requires ``compute_cell_communication()`` to have been called.

Parameters
----------
fdr_threshold
    Significance cutoff.
test
    Which test results to filter on.
use_fdr
    Use FDR or raw p-values.
ct_aware
    Whether to filter cell-type-aware results. Defaults to ``True`` when
    a cell type key was registered.
