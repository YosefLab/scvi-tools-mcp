# VISION on the Visium mouse colon dataset

This notebook demonstrates a standard, standalone VISION pipeline (gene signature scoring and graph autocorrelation) using `scviva.tools.vision.VisionAnalysis`.

**Dataset:** the same mouse colon 10x Visium dataset (Parigi et al.) used in [`Visium_colon_Harreman_pipeline`](Visium_colon_Harreman_pipeline.ipynb), loaded via `load_visium_mouse_colon_dataset()`. For how VISION and Harreman's Hotspot-equivalent gene modules intersect on this same dataset, see that other tutorial.

**Gene signatures:** KEGG metabolic pathway gene sets, fetched from the same hosted URL (`exampledata.scverse.org`) used in that other tutorial.

**Pipeline:**
1. Load the dataset and apply minimal per-sample gene filtering.
2. `VisionAnalysis.setup(compute_neighbors_on_key="spatial_unrolled")` — VISION builds and owns its own spot neighbor graph from the (unrolled) spatial coordinates.
3. `va.load_signatures()` / `va.compute_signatures()` — score every spot against the KEGG pathways and test each pathway's spatial autocorrelation.
4. `va.compute_differential_expression()` — test which pathways differ most between the two regeneration timepoints (Day 0 vs Day 14).
5. Spatial visualization of the most autocorrelated KEGG pathway.
6. Further VISION capabilities beyond the core pipeline: spatial autocorrelation of non-signature metadata, signature clustering, gene importance, one-vs-one differential expression, and the `results` typed accessor (sections 7 onward).

## 0 · Imports

```python
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import requests
import scanpy as sc

import scviva

from scviva.tools.harreman.datasets import load_visium_mouse_colon_dataset
from scviva.tools.vision import VisionAnalysis
```

```python
try:
    import rapids_singlecell as rsc

    print("RAPIDS SingleCell is installed and can be imported")
    HAS_RSC = True
except ImportError:
    HAS_RSC = False
```

```python
scviva.settings.seed = 0
print("Last run with scviva-tools version:", scviva.__version__)
```

## 1 · Load the Visium mouse colon dataset

```python
adata = load_visium_mouse_colon_dataset()
print(adata)
```

```python
# Minimal per-sample gene filtering: keep a gene if it passes the expression
# threshold in ANY sample (union across "cond" == "Day 0"/"Day 14"), matching
# the preprocessing in Visium_colon_Harreman_pipeline.ipynb.
sample_col = "cond"
n_genes_expr = 50
genes_to_keep = np.zeros(adata.shape[1], dtype=bool)

for sample in adata.obs[sample_col].unique():
    adata_sample = adata[adata.obs[sample_col] == sample]
    expressed = np.array((adata_sample.X > 0).sum(axis=0)).flatten()
    genes_to_keep |= expressed >= n_genes_expr

adata = adata[:, genes_to_keep].copy()

# Drop obs columns that are purely technical bookkeeping (array/pixel
# coordinates, per-spot barcodes, a QC flag that's constant after filtering to
# in-tissue spots) so the VISION differential-expression step below only
# compares signatures across the biologically meaningful metadata: "cond"
# (regeneration day), "layer", "ord" and "dist" (spatial axes).
adata.obs = adata.obs.drop(
    columns=["in_tissue", "array_row", "array_col", "id", "row", "col", "spot", "pixel_x", "pixel_y"]
)
print(adata)
```

## 2 · VISION setup: spatial neighbor graph

`VisionAnalysis.setup()` builds and owns its own KNN graph directly from `compute_neighbors_on_key="spatial_unrolled"` (Parigi et al.'s common linear coordinate across conditions).


```python
va = VisionAnalysis(adata, norm_data_key="log_norm")
va.setup(compute_neighbors_on_key="spatial_unrolled", num_neighbors=5)
print(f"obsp['weights'] shape: {adata.obsp['weights'].shape}, nnz: {adata.obsp['weights'].nnz}")
```

## 3 · Tissue sections at a glance

A quick look at the two conditions (regeneration Day 0 vs Day 14) across the
unrolled tissue before diving into signature analysis.


```python
sc.pl.spatial(adata, color="cond", spot_size=80, frameon=False)
```

## 4 · Load KEGG metabolic signatures and score them (`va`)

Gene signatures here are KEGG metabolic pathway gene sets, fetched from the same hosted URL as `Visium_colon_Harreman_pipeline.ipynb`. `compute_signatures()` both scores every spot against each pathway and tests each pathway's autocorrelation against the neighbor graph built in step 2.

```python
resp = requests.get("https://exampledata.scverse.org/scvi-tools/KEGG_metab_m.json")
resp.raise_for_status()
kegg_metab = resp.json()
print(f"KEGG metabolic pathways available: {len(kegg_metab)}")

va.load_signatures(dicts=[kegg_metab], min_signature_genes=5, sig_gene_threshold=0.001)
print(f"signatures loaded: {adata.varm['signatures'].shape[1]}")

va.compute_signatures()
print(f"vision_signatures: {adata.obsm['vision_signatures'].shape}")

autocorr_sig = adata.uns["vision_signature_scores"].sort_values("c_prime", ascending=False)
print("\nTop 10 most autocorrelated KEGG pathways:")
print(autocorr_sig.head(10).round(4).to_string())
```

## 5 · Differential expression: Day 0 vs Day 14

`compute_differential_expression()` runs a one-vs-all comparison of every KEGG pathway score across each categorical `adata.obs` column: here `"cond"` (condition; Day 0 or Day 14) is the only one left after the column pruning in step 1.

```python
va.compute_differential_expression()

cond_diff = adata.uns["vision_signature_differential"]["cond"]
for group, df in cond_diff.groupby("group"):
    top = df[df["pvals_adj"] < 0.05].sort_values("logfoldchanges", ascending=False).head(5)
    print(f"\nTop 5 KEGG pathways up in {group} (vs rest):")
    print(top[["names", "logfoldchanges", "pvals_adj"]].to_string(index=False))
```

## 6 · Spatial visualization of the top autocorrelated pathway

Rather than assume a specific expected biological pattern up front, we let the data pick the most spatially-autocorrelated KEGG pathway from the analysis above and plot it directly across the tissue.

```python
top_sig = autocorr_sig.index[0]
adata.obs["top_kegg_pathway_score"] = adata.obsm["vision_signatures"][top_sig].values

sc.pl.spatial(
    adata,
    color="top_kegg_pathway_score",
    spot_size=80,
    frameon=False,
    vmin="p1",
    vmax="p99",
    cmap="viridis",
    title=top_sig,
)
```

## 7 · Spatial autocorrelation of metadata covariates (`layer`, `ord`, `dist`)

`layer`, `ord`, and `dist` describe the tissue's own spatial axes (layer identity, position along the unrolled axis, distance from the tissue surface). The question we ask here is as follows: do these already-known spatial variables show graph autocorrelation the same way the KEGG pathway scores do?

```python
obs_scores = adata.uns["vision_obs_df_scores"]
print("Autocorrelation of adata.obs columns (c_prime = 1 - Geary's C for numeric, Cramer's V for categorical):")
print(obs_scores.sort_values("c_prime", ascending=False).round(4).to_string())
```

## 8 · Signature clustering: grouping KEGG pathways by spatial pattern

`compute_differential_expression()` also clusters signatures into groups with similar spatial score patterns (`adata.uns["vision_sig_clusters"]`), via a BIC-selected Gaussian mixture over signatures that pass a significance gate (FDR < 0.05 and Geary's C' > 0.2). A newick-format dendrogram of all signatures (regardless of significance) is also available (`adata.uns["vision_dendrogram"]`).

```python
sig_clusters = pd.Series(adata.uns["vision_sig_clusters"], name="cluster")
print(f"{sig_clusters.nunique()} signature cluster(s) across {len(sig_clusters)} KEGG pathways")
print(sig_clusters.value_counts().sort_index())

top_sig_cluster = sig_clusters[top_sig]
same_cluster = [s for s in sig_clusters[sig_clusters == top_sig_cluster].index if s != top_sig]
print(f"\n'{top_sig}' is in cluster {top_sig_cluster}, alongside {len(same_cluster)} other pathway(s):")
print(same_cluster[:10])
```

## 9 · Reusing already-loaded signatures (`attach_signatures`)

`load_signatures()` (section 4) both parses a GMT/dict source *and* stores the result in `adata.varm`. If signatures were already loaded (by an earlier `VisionAnalysis` session on the same `adata`, or by calling `scviva.tools.vision.tools.signature.load_signatures` directly) re-parsing the source is redundant. `attach_signatures()` just points a new session at the existing `adata.varm` entry. Here we use it to re-score the same KEGG pathways against a *different* expression layer (`"normalized"` instead of `"log_norm"`) without re-fetching or re-parsing the KEGG gene sets.

```python
va_reuse = VisionAnalysis(adata, norm_data_key="normalized")
va_reuse.setup(compute_neighbors_on_key="spatial_unrolled", num_neighbors=5)
va_reuse.attach_signatures()  # reuses the "signatures" `va` already loaded from KEGG
va_reuse.compute_signatures()  # overwrites adata's vision_signatures/vision_signature_scores

autocorr_reuse = adata.uns["vision_signature_scores"].sort_values("c_prime", ascending=False)
print("Top 5 KEGG pathways when scored on the 'normalized' layer instead of 'log_norm':")
print(autocorr_reuse.head(5).round(4).to_string())
```

## 10 · Direct one-vs-one gene differential expression (`compute_one_vs_one_de`)

`compute_differential_expression()` (section 5) tested *signatures*
one-vs-all across `"cond"`. `compute_one_vs_one_de()` complements it at the
*gene* level: a direct Wilcoxon test of every gene between two named groups
of an `adata.obs` column, returning a scanpy-style results `DataFrame`
rather than writing into `adata.uns`.


```python
de_day0_vs_day14 = va.compute_one_vs_one_de(key="cond", group1="Day 0", group2="Day 14")
print("Top genes up in Day 0 vs. Day 14 (one-vs-one Wilcoxon):")
print(de_day0_vs_day14.sort_values("scores", ascending=False).head(5).to_string(index=False))
```

## 11 · Inspecting a signature's genes and their expression

`get_genes_by_signature()` lists the genes making up a signature (with
their +/-1 sign), and `get_gene_expression()` pulls dense per-cell
expression for arbitrary genes from whichever layer the session is scoring
from. Together they let you drill from "this pathway is spatially
autocorrelated" (section 4/6) down to the individual genes driving it.


```python
top_sig_genes = va.get_genes_by_signature(top_sig)
print(f"'{top_sig}' has {len(top_sig_genes)} genes:")
print(top_sig_genes.head(10))

expr = va.get_gene_expression(top_sig_genes.index[:3].tolist())
print(f"\nDense expression for the top 3 genes, shape: {expr.shape}")
```

## 12 · Gene importance: which genes drive a signature's score

`get_genes_by_signature()` (section 11) lists a signature's member genes and their +/-1 sign, but not how much each gene actually drives the signature's score. `adata.uns["vision_gene_importance"]` ranks each signature's genes by their covariance with the signature score across spots, mirroring R VISION's own `evalSigGeneImportance`/`evalSigGeneImportanceSparse`.

```python
gene_importance = adata.uns["vision_gene_importance"][top_sig]
print(f"Gene importance for '{top_sig}' ({len(gene_importance)} genes):")
print(gene_importance.sort_values("importance", ascending=False).head(10))
```

## 13 · The lower-level `rank_genes_groups` function

`compute_one_vs_one_de()` (section 10) and `compute_differential_expression()` (section 5) both wrap `scviva.tools.vision.rank_genes_groups` (VISION's own Wilcoxon rank-sum implementation; extended from scanpy's to also report AUC). It's lazily imported (not eagerly pulled in when you `import scviva.tools.vision`) so it's available as a standalone function when you want gene-level one-vs-rest DE without a `VisionAnalysis` session at all.

```python
from scviva.tools.vision import rank_genes_groups

rank_genes_groups(
    adata, groupby="cond", method="wilcoxon", layer="log_norm", use_raw=False, key_added="rank_genes_groups_cond"
)
de_all = sc.get.rank_genes_groups_df(adata, "Day 14", key="rank_genes_groups_cond")
print("Top genes up in Day 14 (one-vs-rest Wilcoxon, called directly):")
print(de_all.sort_values("scores", ascending=False).head(5).to_string(index=False))
```

## 14 · Putting it together: the `va.results` typed accessor

Every VISION result above was reached via `adata.uns["vision_..."]`/`adata.obsm["vision_signatures"]` directly. `va.results` gives the same information as one typed `VisionResults` object, which is often more convenient once several analysis steps have run, and `repr(va)` gives a quick one-line summary of which pipeline steps a session has completed.

```python
print(f"repr(va): {va!r}\n")

results = va.results
print(f"Signature scores:          {results.signature_scores.shape}")
print(f"Signature autocorrelation: {results.signature_autocorrelation.shape}")
print(f"Meta/obs-column scores:    {results.obs_df_scores.shape}")
print(f"Signature clusters:        {len(results.signature_clusters)} entries")
print(f"Gene importance:           {len(results.gene_importance)} signature(s) scored")
```

## 15 · Takeaways

- `VisionAnalysis(adata, norm_data_key="log_norm")` ran the full VISION pipeline standalone on the Visium mouse colon dataset used in [`Visium_colon_Harreman_pipeline`](Visium_colon_Harreman_pipeline.ipynb), from a single hosted dataset download plus a hosted KEGG gene-set file.
- `compute_differential_expression()` surfaced KEGG pathways that significantly differ between the two regeneration timepoints, purely from per-cell signature scores (no gene-module discovery step required).
- See [`Visium_colon_Harreman_pipeline`](Visium_colon_Harreman_pipeline.ipynb) for how these same VISION signatures intersect with Harreman's Hotspot-equivalent gene modules via `ha.vs.integrate_vision_hotspot_results()`.
- `compute_obs_df_scores()`'s output (section 7) tested the tissue's own spatial-axis metadata (`layer`, `ord`, `dist`) for the same kind of graph autocorrelation used for KEGG pathways.
- Signature clustering (section 8) grouped KEGG pathways by spatial-pattern similarity, using the BIC-selected Gaussian mixture.
- `attach_signatures()` (section 9) re-scored the same KEGG pathways on a different expression layer without re-parsing the gene sets.
- `compute_one_vs_one_de()` (section 10) and the standalone `rank_genes_groups()` (section 13) gave direct, gene-level Wilcoxon tests independent of the signature-level differential expression in section 5.
- `get_genes_by_signature()` and `get_gene_expression()` (section 11) drilled from a signature's autocorrelation score down to its individual member genes; gene importance (section 12) ranked those genes by how much each one drives the signature's score.
- `va.results` and `repr(va)` (section 14) gave a typed, at-a-glance view over everything computed above.
