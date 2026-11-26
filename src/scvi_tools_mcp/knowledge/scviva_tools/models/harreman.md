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


---

## User Guide

# Harreman

**Harreman** {cite:p}`Etxezarreta-Arrastoa25` (`scviva.tl.harreman`) is a framework for inferring metabolic exchanges and cell-cell communication in tissues using spatial transcriptomics data.

The advantages of Harreman include:

-   Inference of spatially-resolved metabolic gene programs using local autocorrelation.
-   Identification of cell-cell metabolic communication and ligand-receptor interactions using spatial proximity graphs.
-   Support for multiple spatial technologies (Visium, Slide-seq, and others).
-   Scalability to large spatial datasets.
-   Support for both parametric and non-parametric significance testing.

The limitations of Harreman include:

-   Requires spatial coordinates to be available in `adata.obsm["spatial"]`.
-   Cell communication inference requires a ligand-receptor or metabolite transporter database.

```{topic} Tutorials:

-   {doc}`/tutorials/Visium_colon_Harreman_pipeline`
```

```{topic} External links:

- [Harreman documentation](https://harreman.readthedocs.io)
- [Harreman GitHub](https://github.com/YosefLab/Harreman)
```

## Overview

Harreman operates in three main steps:

1.  **Spatial graph construction** ({func}`~scviva.tl.harreman.tl.compute_knn_graph`): Builds a spatial proximity graph from cell coordinates, supporting both k-nearest neighbors and radius-based neighborhoods, with optional Gaussian kernel weighting.
2.  **Local autocorrelation** ({func}`~scviva.tl.harreman.hs.compute_local_autocorrelation`): Identifies spatially variable genes using the local autocorrelation statistic from the Hotspot algorithm (DeTomaso and Yosef, *Cell Systems*, 2021), supporting DANB, Bernoulli, and normal count models.
3.  **Cell communication** ({func}`~scviva.tl.harreman.tl.compute_cell_communication`): Infers spatially-resolved metabolic exchanges and ligand-receptor interactions between neighboring cells using HarremanDB and CellChatDB.

## Generative process

At the coarsest level, Harreman partitions the tissue into modules of different metabolic functions based on enzyme co-expression. In the next stage, Harreman formulates hypotheses about which metabolites are exchanged across the tissue or within each spatial zone. Finally, at a finer resolution, Harreman can also infer which specific cell subsets participate in the exchange of distinct metabolic activities within each zone.

For proteins composed of multiple subunits, Harreman computes either an arithmetic or geometric mean of the expression values of the corresponding genes:

```{math}
:nowrap: true

\begin{align}
    X_{ai} &= \frac{\sum_{l \in S_l} X_{a_li}}{|S_l|}; \quad X_{bj} = \frac{\sum_{r \in S_r} X_{b_rj}}{|S_r|}
\end{align}
```

### Test statistic 1: Spatial autocorrelation

Spatially variable genes are identified using the following autocorrelation statistic:

```{math}
:nowrap: true

\begin{align}
    H_{a} &= \sum_{i}\sum_{j} w_{ij}X_{ai}X_{aj}
\end{align}
```

where $w_{ij}$ represents the communication strength between neighboring cells, computed using a Gaussian kernel:

```{math}
:nowrap: true

\begin{align}
    \hat{w}_{ij} &= e^{-d_{ij}^2/\sigma_{i}^2}
\end{align}
```

Significance is assessed by converting $H_a$ to a Z-score and adjusting p-values using the Benjamini-Hochberg procedure.

### Test statistic 2: Spatial co-localization

Pairwise spatial correlation between genes is computed as:

```{math}
:nowrap: true

\begin{align}
    H_{ab} &= \sum_{i}\sum_{j} w_{ij} \left(X_{ai}X_{bj} + X_{bi}X_{aj}\right)
\end{align}
```

This statistic is used to group genes into spatial modules and to identify cell-type-agnostic metabolic exchange events.

### Test statistic 3: Metabolite autocorrelation

Gene-pair results are integrated at the metabolite level:

```{math}
:nowrap: true

\begin{align}
    H_{m} &= \sum_{a,b \in m} H_{ab}
\end{align}
```

where $m$ is a metabolite exchanged by genes $a$ and $b$.

## Usage

```python
from scviva import tl

harreman = tl.harreman

# 1. Build spatial KNN graph
harreman.tl.compute_knn_graph(adata, compute_neighbors_on_key="spatial", n_neighbors=10)

# 2. Identify spatially variable genes
harreman.hs.compute_local_autocorrelation(adata, model="danb")

# 3. Compute pairwise local correlation
harreman.hs.compute_local_correlation(adata)

# 4. Infer cell-cell communication
harreman.tl.compute_cell_communication(adata)
```

## API

Please see {mod}`scviva.tl.harreman` and {mod}`scviva.pl.harreman` for the full API reference.
