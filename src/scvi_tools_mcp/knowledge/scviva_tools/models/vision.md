# VISION — API Reference

**Class:** `scviva.tools.vision._analysis.VisionAnalysis`

**Signature:** `VisionAnalysis(adata: 'AnnData', norm_data_key: 'str | None' = None, protein_obsm_key: 'str | None' = None) -> 'None'`

## Docstring

Unsupervised transcriptome analysis and gene-signature scoring.

Computes a cell neighbor-weight graph, per-cell gene-signature scores,
their spatial/graph autocorrelation (Geary's C), and one-vs-all
differential expression of signatures and metadata across clusters —
mirroring R VISION's ``analyze()`` pipeline.

Parameters
----------
adata
    Annotated data object.
norm_data_key
    Key in ``adata.layers`` for scaled/library-size-normalised
    expression. Use ``"use_raw"`` to pull from ``adata.raw``. ``None``
    (default) uses ``adata.X`` directly.

    Matching R VISION's documented contract, this data should be
    **normalized but not log-transformed** -- VISION log-transforms it
    internally wherever needed (:func:`~scviva.tools.vision._utils.log2p1`).
    If it looks already log-transformed (small, non-integer values),
    that internal step is skipped automatically and a warning is logged
    the first time it would otherwise have double-transformed your data;
    pass genuinely non-log-transformed data to avoid relying on that
    detection.
protein_obsm_key
    Key in ``adata.obsm`` for CITE-seq protein (ADT) data, if any.

Notes
-----
Lower-level VISION functions are available as ``va.tl.<method>``, defaulting to
this object's AnnData; see :class:`~scviva.tools.vision.VisionToolsAccessor`.

Examples
--------
>>> va = VisionAnalysis(adata)
>>> va.setup(compute_neighbors_on_key="X_pca")
>>> va.load_signatures(gmt_files=["h.all.v7.symbols.gmt"])
>>> va.compute_signatures()
>>> va.compute_differential_expression()
>>> results = va.results

Without a precomputed latent space:

>>> va = VisionAnalysis(adata)
>>> va.compute_latent_space()
>>> va.setup()

## setup

```python
VisionAnalysis.setup(self, compute_neighbors_on_key: 'str | None' = None, num_neighbors: 'int | None' = None, exact_knn: 'bool' = False, tree: 'str | None' = None, lca_knn: 'bool' = False, lca_min_size: 'int' = 20, random_state: 'int' = 0) -> 'None'
```

Build the VISION neighbor-weight graph and Louvain cell clusters.

Parameters
----------
compute_neighbors_on_key
    Key in ``adata.obsm`` to use as the latent space for the KNN
    weight graph. If ``None`` and ``adata.obsm["X_pca"]`` exists,
    that is used automatically. Falls back to L1-normalising
    ``adata.obsp["connectivities"]`` if available.
num_neighbors
    Number of KNN neighbors for the weight graph. Defaults to
    ``round(sqrt(n_cells))``, matching R VISION.
exact_knn
    Use exact (brute-force/kd-tree) KNN instead of approximate.
tree
    Newick string or path to a newick file for PhyloVision mode:
    build KNN weights from phylogenetic tree structure instead of
    an expression/embedding latent space.
lca_knn
    When ``tree`` is set, use LCA-distance-based tree weights instead
    of cophenetic-distance-based weights.
lca_min_size
    Minimum clade size for the LCA-based tree KNN weights.
random_state
    Seed for the Louvain clustering used to build ``VISION_Clusters``
    (``igraph``'s ``community_multilevel`` has no seed parameter of
    its own and is otherwise non-deterministic between runs).

## filter_genes

```python
VisionAnalysis.filter_genes(self, filters: 'tuple[str, ...]' = ('threshold', 'fano'), **kwargs) -> 'np.ndarray'
```

Compute a boolean gene filter mask; does not mutate ``adata`` in place.

Parameters
----------
filters
    Names of filters to apply in sequence, e.g. ``"novar"``,
    ``"threshold"``, ``"fano"``. See
    :func:`~scviva.tools.vision.preprocessing.filters.apply_filters`.
**kwargs
    Forwarded to :func:`~scviva.tools.vision.preprocessing.filters.apply_filters`
    (e.g. ``threshold``, ``num_mad``).

Returns
-------
np.ndarray
    Boolean mask of shape ``(n_vars,)``. Apply with
    ``adata[:, mask].copy()``.

## compute_latent_space

```python
VisionAnalysis.compute_latent_space(self, max_components: 'int' = 30, use_permutation_wpca: 'bool' = False, **kwargs) -> 'None'
```

Compute a PCA latent space, stored as ``adata.obsm["X_pca"]``.

Parameters
----------
max_components
    Maximum number of principal components to compute.
use_permutation_wpca
    If ``True``, run permutation weighted PCA and keep only the
    statistically significant components. If ``False``, keep all
    ``max_components`` components (mirrors R VISION's
    ``perm_wPCA=FALSE`` default).
**kwargs
    Forwarded to :func:`~scviva.tools.vision.compute_latent_space`
    (e.g. ``filters``, ``threshold``, ``num_mad``, ``projection_genes``).

## generate_projections

```python
VisionAnalysis.generate_projections(self, methods: 'list[str] | None' = None, **kwargs) -> 'None'
```

Generate 2-D visualisation projections (tSNE, UMAP, ISOMap, …).

Parameters
----------
methods
    Projection methods to compute, chosen from ``"tSNE30"``,
    ``"tSNE10"``, ``"UMAP"``, ``"ISOMap"``, ``"ICA"`` and ``"RBFPCA"``.
    If ``None``, all six methods are computed.
**kwargs
    Forwarded to :func:`~scviva.tools.vision.generate_projections`
    (e.g. ``obsm_key``, ``K``, ``projection_genes``).

## pool_cells

```python
VisionAnalysis.pool_cells(self, cells_per_partition: 'int' = 10, **kwargs) -> 'None'
```

Micro-cluster ("pool") cells into supercells for scalable analysis.

Parameters
----------
cells_per_partition
    Target number of cells per micro-cluster (supercell).
**kwargs
    Forwarded to :func:`~scviva.tools.vision.apply_micro_clustering`
    (e.g. ``filter_input``, ``filter_threshold``, ``latent_space_key``,
    ``K``, ``uns_key``).

## load_signatures

```python
VisionAnalysis.load_signatures(self, gmt_files: 'list[str] | None' = None, dicts: 'list[dict] | None' = None, use_raw: 'bool' = False, min_signature_genes: 'int' = 5, sig_gene_threshold: 'float' = 0.001, varm_key: 'str' = 'signatures', split_signed: 'bool' = True) -> 'None'
```

Load gene signatures into ``adata.varm`` ahead of :meth:`compute_signatures`.

Parameters
----------
gmt_files
    Paths to one or more GMT signature files.
dicts
    Signature definitions as Python dicts (see
    :func:`~scviva.tools.vision.tools.signature.load_signatures`).
use_raw
    Use ``adata.raw`` gene names/expression for gene-presence filtering.
min_signature_genes
    Minimum number of matching genes required to retain a signature.
sig_gene_threshold
    Minimum fraction of cells expressing a gene for it to be
    eligible for signature membership.
varm_key
    Key in ``adata.varm`` to store the resulting gene x signature matrix.
split_signed
    Auto-expand bidirectional (+/-) signatures into ``_UP``/``_DOWN``
    sub-columns after loading, matching R VISION's signature handling.

## attach_signatures

```python
VisionAnalysis.attach_signatures(self, varm_key: 'str' = 'signatures') -> 'None'
```

Point this session at signatures already loaded into ``adata.varm``.

Use this instead of :meth:`load_signatures` when signatures were
already loaded by another call on the same ``adata`` (e.g. a prior
``VisionAnalysis`` session, or
:func:`~scviva.tools.vision.tools.signature.load_signatures` called
directly) and re-parsing the source GMT/dict would be redundant.

Parameters
----------
varm_key
    Key in ``adata.varm`` (or ``adata.raw.varm`` when
    ``norm_data_key == "use_raw"``) for the gene x signature weight
    matrix to use.

## compute_signatures

```python
VisionAnalysis.compute_signatures(self, signature_names_uns_key: 'str | None' = None, sig_norm_method: 'str' = 'znorm_columns', device: 'str' = 'auto', batch_size: 'int' = 1200, random_state: 'int' = 0) -> 'None'
```

Score loaded signatures per-cell and compute their graph autocorrelation.

Requires :meth:`setup` (the neighbor-weight graph is used for Geary's C).

Parameters
----------
signature_names_uns_key
    Key in ``adata.uns`` holding custom signature names, if any.
sig_norm_method
    Normalisation method for the sparse scoring path. See
    :func:`~scviva.tools.vision.tools.signature.compute_signatures_anndata`.
device
    Compute device: ``"auto"``, ``"cuda"``, ``"mps"``, or ``"cpu"``.
    ``"cpu"`` forces the deterministic scipy sparse path (a dense
    torch CPU tensor path is not offered, since its multi-threaded
    matmul is not run-to-run bit-reproducible).
batch_size
    Number of signatures scored per device batch.
random_state
    Seed for the Geary's C permutation-null background signature
    generation (see
    :func:`~scviva.tools.vision.tools.signature.generate_permutations_null`).

## compute_differential_expression

```python
VisionAnalysis.compute_differential_expression(self) -> 'None'
```

Compute one-vs-all differential expression of metadata and signatures.

Requires :meth:`setup`. If signatures have been scored via
:meth:`compute_signatures`, also computes signature differential
expression, per-signature gene importance, a signature dendrogram,
and signature clusters — mirroring R VISION's ``ClusterComparisons``.

## compute_one_vs_one_de

```python
VisionAnalysis.compute_one_vs_one_de(self, key: 'str', group1: 'str', group2: 'str') -> 'pd.DataFrame'
```

Wilcoxon one-vs-one differential expression between two groups of ``adata.obs[key]``.

Full results are also stored in ``adata.uns[f"rank_genes_groups_{key}"]``
(overwriting any previous comparison for the same ``key``).

Parameters
----------
key
    Column of ``adata.obs`` defining the groups.
group1
    Group of ``adata.obs[key]`` to test.
group2
    Reference group of ``adata.obs[key]`` that ``group1`` is compared
    against.

Returns
-------
:class:`pandas.DataFrame`
    Per-gene results for ``group1`` versus ``group2`` as returned by
    :func:`scanpy.get.rank_genes_groups_df` (gene names, scores,
    log fold changes, p-values and adjusted p-values).

## get_gene_expression

```python
VisionAnalysis.get_gene_expression(self, genes: 'str | list[str]') -> 'np.ndarray'
```

Return the (dense) expression of one or more genes for every cell.

Expression is read from ``adata.raw`` when ``norm_data_key == "use_raw"``,
from ``adata.X`` when ``norm_data_key`` is ``None``, and from
``adata.layers[norm_data_key]`` otherwise.

Parameters
----------
genes
    Gene name or list of gene names.

Returns
-------
:class:`numpy.ndarray`
    Dense array of shape ``(n_cells, n_genes)`` (``n_genes == 1`` when a
    single gene name is given).

## get_genes_by_signature

```python
VisionAnalysis.get_genes_by_signature(self, sig_name: 'str') -> 'pd.DataFrame'
```

Genes belonging to signature ``sig_name``, indexed by gene name with +/-1 signs.

Parameters
----------
sig_name
    Name of a signature loaded via :meth:`load_signatures` (or
    :meth:`attach_signatures`) and scored via :meth:`compute_signatures`.

Returns
-------
:class:`pandas.DataFrame`
    Single-column frame indexed by the genes with a non-zero weight in
    the signature, holding each gene's signature weight (sign).


---

## User Guide

# VISION

**VISION** {cite:p}`DeTomaso19` (`scviva.tl.VisionAnalysis`) is a framework for interpreting single-cell (and spatial) transcriptomic similarity maps using annotated gene signatures.

The advantages of VISION include:

-   Unsupervised scoring of curated gene signatures (e.g. Hallmark, GO, custom) on a per-cell basis.
-   Spatial/graph autocorrelation (Geary's C) to identify signatures and metadata that vary systematically across the cell-cell neighbor graph.
-   One-vs-all differential expression of signatures and metadata across clusters, with per-signature gene importance and a signature dendrogram.
-   PhyloVision mode: builds the neighbor-weight graph from a phylogenetic tree instead of an expression/embedding latent space, and computes Fitch-Hartigan parsimony plasticity scores.

The limitations of VISION include:

-   Signature scoring requires curated gene sets (GMT files, R VISION `.txt` signature files, or plain dicts) — it does not discover signatures de novo (see {doc}`harreman` for unsupervised gene-module discovery).
-   The interactive web report from R VISION and visionpy (Flask app, REST routes, JS/HTML assets) was intentionally not ported; results are consumed programmatically via `va.results` or plotted directly from `adata`.

```{topic} Tutorials:

-   {doc}`/tutorials/Vision_tutorial`
-   {doc}`/tutorials/Visium_colon_Harreman_pipeline` (joint Harreman + VISION analysis via `ha.vs`)
```

```{topic} External links:

-   [R VISION documentation](https://yoseflab.github.io/VISION/)
-   [R VISION GitHub](https://github.com/YosefLab/VISION)
-   [visionpy GitHub](https://github.com/yoseflab/visionpy)
```

## Overview

VISION operates in up to four steps:

1.  **Setup** ({meth}`~scviva.tools.vision.VisionAnalysis.setup`): builds the cell-cell neighbor-weight graph (exponential kernel over a latent embedding, or over a phylogenetic tree in PhyloVision mode) and Louvain cell clusters.
2.  **Signature scoring** ({meth}`~scviva.tools.vision.VisionAnalysis.load_signatures`, {meth}`~scviva.tools.vision.VisionAnalysis.compute_signatures`): scores curated gene signatures per cell and computes their graph autocorrelation (Geary's C) against a permutation-based null.
3.  **Differential expression** ({meth}`~scviva.tools.vision.VisionAnalysis.compute_differential_expression`): one-vs-all Wilcoxon differential expression of signatures and metadata across clusters, per-signature gene importance, latent-component annotation, and a signature dendrogram/clustering.
4.  **PhyloVision (optional)**: passing `tree=` to `setup()` builds the neighbor graph from a Newick tree instead of an embedding; {meth}`~scviva.tools.vision.VisionAnalysis.tl.compute_plasticity_scores` (`va.tl.compute_plasticity_scores`) then scores how conserved each categorical metadata variable is along the lineage tree.

## Relationship to R VISION and visionpy

`scviva.tools.vision` is a direct Python port of [visionpy](https://github.com/yoseflab/visionpy), itself a port of the original [R VISION](https://github.com/YosefLab/VISION) package, excluding the interactive Flask web-report server. Where visionpy exposed its analysis session as a process-global singleton (`AnnDataAccessor`), `VisionAnalysis` instead follows {class}`~scviva.tools.harreman.HarremanAnalysis`'s pattern of an explicit, user-owned session object with an internal step-prerequisite gate (`va.setup()` before `va.compute_signatures()`, etc.) — the numerical results and `adata.obs`/`obsm`/`uns` key layout are otherwise unchanged from visionpy, so migrating an existing script is largely mechanical.

The port has been independently verified against the R source: it fixes three real R bugs (a PCA-loading row/column slice bug in permutation WPCA, an LCA-tree weight-matrix encoding inversion, and Fitch-Hartigan parsimony tie-break nondeterminism) while intentionally documenting two minor deviations (approximate KNN by default, where R VISION is always exact; no Wilcoxon continuity correction) that do not materially change results.

## Usage

```python
from scviva.tools.vision import VisionAnalysis

va = VisionAnalysis(adata)
va.setup(compute_neighbors_on_key="X_pca")
va.load_signatures(gmt_files=["h.all.v7.symbols.gmt"])
va.compute_signatures()
va.compute_differential_expression()

results = va.results
```

Without a precomputed latent space:

```python
va = VisionAnalysis(adata)
va.compute_latent_space()
va.setup()
```

VISION can also be run as part of a Harreman session on the same `adata`, reusing Harreman's spatial neighbor graph instead of building its own:

```python
from scviva import tl

ha = tl.HarremanAnalysis(adata)
ha.setup(compute_neighbors_on_key="spatial")
ha.vs.load_signatures(gmt_files=["h.all.v7.symbols.gmt"])
ha.vs.analyze_vision(signature_varm_key="signatures")
```

## API

Please see {mod}`scviva.tl.VisionAnalysis` for the full API reference.
