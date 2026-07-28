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
