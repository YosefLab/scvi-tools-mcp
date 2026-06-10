---
name: scbasset-batch-correction
description: This skill should be used for integrating multi-batch single-cell ATAC-seq data using scBasset from scvi-tools while preserving the ability to infer transcription factor activity. Use this skill when the user has scATAC-seq data from multiple samples, batches, or experiments that need integration, and also wants TF activity analysis. This skill is appropriate for requests like "integrate multiple scATAC batches", "batch correct ATAC data with TF analysis", "combine scATAC samples", or "multi-sample ATAC integration".
---

# Multi-Batch scATAC-seq Integration with scBasset

## Overview

scBasset batch correction provides:

1. **Batch-aware integration**: Learns shared cell representations across batches
2. **L2 regularization**: Key parameter (`l2_reg_cell_embedding=1e-8`) for integration
3. **Preserved TF activity**: Maintains ability to score transcription factors
4. **Sequence-informed**: Still uses DNA sequences unlike simpler batch correction methods

**Key Difference from Standard scBasset**:
- Standard scBasset: `l2_reg_cell_embedding=0.0`
- Batch correction: `l2_reg_cell_embedding=1e-8`

This regularization encourages similar cells from different batches to have similar embeddings.

**Citation**: Yuan & Kelley (2022). "scBasset: sequence-based modeling of single-cell ATAC-seq using convolutional neural networks." Nature Methods.

---

## Workflow Steps

### Step 1: Environment Setup

```python
import numpy as np
import scanpy as sc
import scvi
import matplotlib.pyplot as plt
import torch

scvi.settings.seed = 0
sc.set_figure_params(figsize=(6, 6), frameon=False)
torch.set_float32_matmul_precision("high")
```

---

### Step 2: Load Multi-Batch scATAC-seq Data

```python
# Option 1: Load pre-concatenated data with batch labels
adata = sc.read_h5ad("path/to/combined_atac.h5ad")

# Option 2: Concatenate multiple samples
# sample1 = sc.read_h5ad("sample1.h5ad")
# sample2 = sc.read_h5ad("sample2.h5ad")
# sample1.obs['batch'] = 'sample1'
# sample2.obs['batch'] = 'sample2'
# adata = sc.concat([sample1, sample2], join='inner')

print(f"Data: {adata.n_obs} cells, {adata.n_vars} peaks")
print(f"Batches: {adata.obs['batch'].value_counts()}")
```

**Requirements**:
- Batch labels in `adata.obs['batch']` (or specified column)
- Peaks should be shared across batches (use `join='inner'` when concatenating)
- Genomic coordinates in `adata.var` (chr, start, end)

---

### Step 3: Parse Genomic Coordinates

```python
# Check if coordinates exist
if "chr" not in adata.var.columns:
    # Parse from peak names (format: chr1:1000-2000)
    split_interval = adata.var_names.str.split(":", expand=True)
    adata.var["chr"] = split_interval[0]
    split_coords = split_interval[1].str.split("-", expand=True)
    adata.var["start"] = split_coords[0].astype(int)
    adata.var["end"] = split_coords[1].astype(int)

# Verify coordinates
print(f"Chromosomes found: {adata.var['chr'].nunique()}")

# Filter to standard chromosomes
mask = adata.var["chr"].str.match(r"^chr[0-9XY]+$")
print(f"Peaks before chromosome filter: {adata.n_vars}")
adata = adata[:, mask].copy()
print(f"Peaks after chromosome filter: {adata.n_vars}")
```

---

### Step 4: Quality Control and Filtering

```python
# Calculate peak detection frequency
adata.var["n_cells"] = np.array((adata.X > 0).sum(axis=0)).flatten()
adata.var["detection_rate"] = adata.var["n_cells"] / adata.n_obs

# Filter peaks: keep those detected in at least 5% of cells
min_detection = 0.05
min_cells = int(adata.n_obs * min_detection)

print(f"Peaks before filtering: {adata.n_vars}")
sc.pp.filter_genes(adata, min_cells=min_cells)
print(f"Peaks after filtering (>{min_detection*100}% detection): {adata.n_vars}")

# Check batch balance in remaining data
print("\nCells per batch after filtering:")
print(adata.obs["batch"].value_counts())
```

---

### Step 5: Add DNA Sequences

```python
# Specify genome
genome_name = "hg19"  # or "GRCh38", "mm10", etc.
genome_dir = "path/to/genomes"

# Add DNA sequences
scvi.data.add_dna_sequence(
    adata,
    genome_name=genome_name,
    genome_dir=genome_dir,
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
)

print(f"DNA codes added: {adata.varm['dna_code'].shape}")
```

---

### Step 6: Prepare Data (Transpose and Binarize)

```python
# Transpose: scBasset requires peaks × cells format
bdata = adata.transpose()

# Create binary accessibility layer
bdata.layers["binary"] = (bdata.X.copy() > 0).astype(float)

print(f"Transposed data: {bdata.n_obs} peaks × {bdata.n_vars} cells")
print(f"Binary layer created")

# Verify DNA codes transferred correctly
print(f"DNA codes in obsm: {bdata.obsm['dna_code'].shape}")
```

---

### Step 7: Setup AnnData with Batch Key

```python
# Setup with batch correction
scvi.external.SCBASSET.setup_anndata(
    bdata,
    layer="binary",
    dna_code_key="dna_code",
    batch_key="batch",  # CRITICAL: specify batch key
)

print("AnnData registered for scBasset with batch correction")
print(f"Batch key: 'batch'")
print(f"Number of batches: {bdata.var['batch'].nunique()}")
```

**Note**: After transpose, batch information moves from `obs` to `var` (cells are now variables).

---

### Step 8: Initialize and Train with L2 Regularization

```python
# Initialize model with L2 regularization for integration
# This is the KEY parameter for batch correction
model = scvi.external.SCBASSET(
    bdata, l2_reg_cell_embedding=1e-8  # CRITICAL: enables batch integration
)

print(f"L2 regularization: {model.module.l2_reg_cell_embedding}")

# Train
model.train(precision=16)

# Check training metrics
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(model.history["train_loss_epoch"].values)
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training Loss")

plt.subplot(1, 3, 2)
if "auroc_train" in model.history:
    plt.plot(model.history["auroc_train"].values, label="Train")
if "auroc_validation" in model.history:
    plt.plot(model.history["auroc_validation"].values, label="Validation")
plt.xlabel("Epoch")
plt.ylabel("AUROC")
plt.legend()
plt.title("AUROC")

plt.subplot(1, 3, 3)
cell_bias = model.get_cell_bias()
plt.hist(cell_bias, bins=50)
plt.xlabel("Cell Bias")
plt.title("Cell Bias Distribution")

plt.tight_layout()
plt.show()
```

**Why L2 Regularization Works**:
- Without regularization: each batch can have arbitrary embedding scale
- With L2: embeddings are regularized toward zero
- Result: cells with similar accessibility patterns get similar embeddings regardless of batch

---

### Step 9: Extract Integrated Representation and Visualize

```python
# Get batch-corrected latent representation
latent = model.get_latent_representation()

# Add to original (non-transposed) adata
adata.obsm["X_scbasset"] = latent

print(f"Integrated embedding shape: {latent.shape}")

# Build neighborhood graph
sc.pp.neighbors(adata, use_rep="X_scbasset")

# UMAP with adjusted parameters for integration visualization
sc.tl.umap(adata, min_dist=1.0)  # Higher min_dist for clearer mixing

# Visualize integration
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Batch distribution
sc.pl.umap(adata, color="batch", ax=axes[0], show=False, title="Batch Distribution")

# Plot 2: Clustering (if cell type labels exist)
if "cell_type" in adata.obs.columns:
    sc.pl.umap(adata, color="cell_type", ax=axes[1], show=False, title="Cell Types")
else:
    # Cluster and plot
    sc.tl.leiden(adata, key_added="leiden_scbasset", resolution=0.5)
    sc.pl.umap(adata, color="leiden_scbasset", ax=axes[1], show=False, title="Clusters")

plt.tight_layout()
plt.show()
```

**Integration Assessment**:
- Good integration: batches mix within cell types
- Poor integration: batches form separate clusters
- Over-integration: all cells mix (lost biological variation)

---

### Step 10: Assess Integration Quality

```python
# Quantitative integration assessment using scib-metrics (if available)
try:
    import scib
    import scib_metrics

    # Calculate integration metrics
    # Note: requires cell type labels for full assessment
    if "cell_type" in adata.obs.columns:
        # Calculate various metrics
        print("Calculating integration metrics...")

        # Batch mixing (higher = better mixing)
        # Bio conservation (higher = better preservation)
        # See scib documentation for full metric suite

except ImportError:
    print("scib-metrics not installed. Using visual assessment.")

# Visual batch mixing check per cluster
if "leiden_scbasset" in adata.obs.columns:
    # Cross-tabulation of batch vs cluster
    import pandas as pd

    ct = pd.crosstab(adata.obs["leiden_scbasset"], adata.obs["batch"])
    ct_norm = ct.div(ct.sum(axis=1), axis=0)

    print("\nBatch composition per cluster:")
    print(ct_norm.round(2))

    # Plot
    ct_norm.plot(kind="bar", stacked=True, figsize=(10, 5))
    plt.ylabel("Proportion")
    plt.xlabel("Cluster")
    plt.title("Batch Composition per Cluster")
    plt.legend(title="Batch", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    plt.show()
```

---

### Step 11: Transcription Factor Activity (Post-Integration)

```python
# TF activity scoring works the same after batch correction
# The integrated embedding allows cross-batch TF comparison

motif_dir = "path/to/motifs"

# Score TFs of interest
tfs_to_score = ["PAX5", "TCF7", "SPI1", "GATA1"]

for tf in tfs_to_score:
    try:
        activity = model.get_tf_activity(tf=tf, motif_dir=motif_dir)
        adata.obs[f"TF_{tf}"] = activity
        print(f"Scored {tf}")
    except Exception as e:
        print(f"Could not score {tf}: {e}")

# Visualize TF activities across batches
tf_cols = [c for c in adata.obs.columns if c.startswith("TF_")]
if tf_cols:
    sc.pl.umap(adata, color=tf_cols, ncols=2, cmap="PRGn", vcenter=0)

    # Compare TF activity across batches
    for tf_col in tf_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        adata.obs.boxplot(column=tf_col, by="batch", ax=ax)
        plt.suptitle("")
        plt.title(f"{tf_col} by Batch")
        plt.tight_layout()
        plt.show()
```

---

### Save Results

```python
# Save model
model_dir = "scbasset_batch_model"
model.save(model_dir, overwrite=True)

# Save integrated data
adata.write_h5ad("atac_integrated_scbasset.h5ad")

# Export integration metrics
integration_summary = {
    "n_cells": adata.n_obs,
    "n_peaks": adata.n_vars,
    "n_batches": adata.obs["batch"].nunique(),
    "l2_regularization": 1e-8,
}
print("\nIntegration Summary:")
for k, v in integration_summary.items():
    print(f"  {k}: {v}")

# Reload later
# model = scvi.external.SCBASSET.load(model_dir, adata=bdata)
```

---

## Key Parameters Reference

### Critical Parameter for Batch Correction

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `l2_reg_cell_embedding` | `1e-8` | Regularizes cell embeddings for integration |

**Without this parameter** (default `0.0`): No batch correction
**With this parameter**: Encourages batch-invariant embeddings

### Setup Parameters

| Parameter | Description |
|-----------|-------------|
| `layer` | Binary accessibility layer |
| `dna_code_key` | DNA sequences key |
| `batch_key` | Batch labels column (required for integration) |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_epochs` | 1000 | Maximum training |
| `precision` | 32 | Use 16 for memory efficiency |

---

## Integration Quality Assessment

### Visual Checks

1. **UMAP colored by batch**: Should show mixing
2. **UMAP colored by cell type**: Should maintain separation
3. **Batch proportion per cluster**: Should be balanced

### Quantitative Metrics (with scib-metrics)

```python
# If scib is available
import scib

# Batch mixing metrics
batch_metrics = [
    "kBET",  # k-nearest neighbor batch effect test
    "graph_conn",  # Graph connectivity
    "silhouette_batch",  # Batch silhouette
]

# Biology preservation metrics
bio_metrics = [
    "NMI_cluster",  # Normalized mutual information
    "ARI_cluster",  # Adjusted Rand index
    "ASW_cell_type",  # Cell type silhouette
]
```

---

## Advanced Usage

### Tuning L2 Regularization

```python
# Lower value = less integration (preserve batch differences)
# Higher value = more integration (remove batch effects)

# Light integration
model_light = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=1e-9)

# Standard integration
model_standard = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=1e-8)

# Strong integration
model_strong = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=1e-7)

# Compare embeddings to find optimal
```

### Cross-Batch Differential TF Activity

```python
# Compare TF activity between conditions (after integration)
# Assumes batches represent different conditions

condition_map = {
    "batch1": "control",
    "batch2": "control",
    "batch3": "treatment",
    "batch4": "treatment",
}
adata.obs["condition"] = adata.obs["batch"].map(condition_map)

# Statistical test for TF activity differences
from scipy.stats import mannwhitneyu

tf_cols = [c for c in adata.obs.columns if c.startswith("TF_")]
results = []

for tf_col in tf_cols:
    ctrl = adata.obs.loc[adata.obs["condition"] == "control", tf_col]
    treat = adata.obs.loc[adata.obs["condition"] == "treatment", tf_col]

    stat, pval = mannwhitneyu(ctrl, treat, alternative="two-sided")
    results.append(
        {
            "TF": tf_col,
            "control_mean": ctrl.mean(),
            "treatment_mean": treat.mean(),
            "fold_change": treat.mean() / (ctrl.mean() + 1e-10),
            "p_value": pval,
        }
    )

import pandas as pd

results_df = pd.DataFrame(results)
results_df["p_adj"] = results_df["p_value"] * len(results_df)  # Bonferroni
print(results_df.sort_values("p_value"))
```

### Iterative Integration Refinement

```python
# If integration is poor, try:

# 1. Filter more peaks
min_cells = int(adata.n_obs * 0.10)  # Increase from 5% to 10%
sc.pp.filter_genes(adata, min_cells=min_cells)

# 2. Increase L2 regularization
model = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=1e-7)

# 3. Train longer
model.train(max_epochs=2000, precision=16)

# 4. Assess and iterate
```

---

## Parameter Tuning Guide

### When to Adjust Parameters

**Before running, ask the user:**
1. How many batches and what are the batch sizes?
2. Are batches technical replicates or different conditions?
3. How strong do you expect batch effects to be?
4. Is perfect mixing or biological preservation more important?

### L2 Regularization (`l2_reg_cell_embedding`) - THE KEY PARAMETER

| Batch Effect Strength | l2_reg_cell_embedding | Integration Strength |
|----------------------|----------------------|---------------------|
| Minimal (technical replicates) | 1e-9 | Light |
| Moderate (different experiments) | 1e-8 | **Standard (recommended)** |
| Strong (different labs/protocols) | 1e-7 | Strong |
| Very strong | 5e-7 | Very strong (may over-integrate) |

**How to diagnose:**
- If batches still separate after training → increase L2
- If cell types merge together → decrease L2
- Start with 1e-8, adjust based on UMAP

### Peak Filtering

| Scenario | min_detection | Rationale |
|----------|---------------|-----------|
| Batches have similar peak sets | 0.05 | Standard |
| Batches have different peaks | 0.08-0.10 | Focus on shared signal |
| Want to maximize shared features | 0.03 | Keep more, accept noise |

### UMAP Visualization

| Parameter | Default | Batch-Corrected |
|-----------|---------|-----------------|
| `min_dist` | 0.5 | 1.0 (clearer mixing visualization) |
| `n_neighbors` | 15 | 15-30 (for integration) |

---

## Adaptation Prompts for Claude

When a user invokes this skill, consider asking:

1. **Batch structure:**
   - "How many batches do you have?"
   - "What do batches represent (samples, experiments, conditions)?"
   - "Are batch sizes balanced?"

2. **Expected batch effects:**
   - "Are these technical or biological batches?"
   - "Have you seen strong batch effects in UMAP without correction?"
   - "Are the same cell types present in all batches?"

3. **Integration goals:**
   - "Do you need TF activity after integration?"
   - "Is it important to compare TF activity across conditions?"
   - "Would over-integration (merging cell types) be a problem?"

4. **Prior attempts:**
   - "Have you tried PeakVI with batch_key?"
   - "What were the integration results?"

### Integration Quality Assessment

```python
def assess_integration(adata, batch_key, cluster_key):
    """Assess quality of batch integration."""
    import pandas as pd

    # Batch mixing per cluster
    ct = pd.crosstab(adata.obs[cluster_key], adata.obs[batch_key])
    ct_norm = ct.div(ct.sum(axis=1), axis=0)

    print("Batch composition per cluster:")
    print(ct_norm.round(2))

    # Metrics
    # Ideal: each cluster has similar batch proportions
    # Problem: clusters dominated by single batch

    # Check for single-batch clusters
    dominant = (ct_norm > 0.8).any(axis=1)
    if dominant.any():
        print(f"\nWARNING: {dominant.sum()} clusters are >80% single-batch")
        print("Consider increasing l2_reg_cell_embedding")
    else:
        print("\nGood: No clusters are dominated by single batch")

    # Overall batch balance
    batch_sizes = adata.obs[batch_key].value_counts()
    expected_prop = batch_sizes / batch_sizes.sum()
    print(f"\nExpected batch proportions: {expected_prop.to_dict()}")

    return ct_norm
```

### Iterative L2 Tuning

```python
# If integration is unsatisfactory, try different L2 values
l2_values = [1e-9, 1e-8, 5e-8, 1e-7]

results = {}
for l2 in l2_values:
    print(f"\n--- Testing l2_reg_cell_embedding = {l2} ---")

    model = scvi.external.SCBASSET(bdata, l2_reg_cell_embedding=l2)
    model.train(precision=16, max_epochs=500)  # Shorter for testing

    latent = model.get_latent_representation()
    adata.obsm[f"X_scbasset_l2_{l2}"] = latent

    # Quick UMAP
    sc.pp.neighbors(adata, use_rep=f"X_scbasset_l2_{l2}")
    sc.tl.umap(adata)
    sc.pl.umap(adata, color="batch", title=f"L2 = {l2}")

# Choose best L2 based on visual assessment and metrics
```

---

## Troubleshooting

### Common Issues

1. **Batches still separate after integration**:
   - Increase `l2_reg_cell_embedding` (try `1e-7`)
   - Filter more peaks (shared signal)
   - Check batch sizes are balanced
   - Train longer

2. **Over-integration (lost cell types)**:
   - Decrease `l2_reg_cell_embedding` (try `1e-9`)
   - Verify cell type annotations are correct
   - Check if batches have different cell compositions

3. **Training fails with batch_key**:
   - Ensure batch labels are in correct location after transpose
   - Check no NaN values in batch column
   - Verify batch_key name matches column

4. **Unbalanced batches**:
   - Subsample large batches
   - Use weighted training (if available)
   - Be cautious interpreting results

5. **Memory issues with large multi-batch data**:
   - Use `precision=16`
   - Filter more aggressively
   - Process in chunks if necessary

### Verifying Batch Key Location

```python
# Before transpose:
# adata.obs['batch'] contains batch labels

# After transpose:
# bdata.var['batch'] contains batch labels (cells are now variables)

# Verify
print("Before transpose:")
print(f"  batch in obs: {'batch' in adata.obs.columns}")

print("\nAfter transpose:")
print(f"  batch in var: {'batch' in bdata.var.columns}")
```

---

## Comparison with Other Integration Methods

| Method | Sequence-aware | TF Activity | Integration Strength |
|--------|---------------|-------------|---------------------|
| scBasset (this) | Yes | Yes | Tunable |
| PeakVI + batch_key | No | No | Fixed |
| Harmony | No | No | Strong |
| LIGER | No | No | Medium |
| scVI | No | No | Tunable |

**When to use scBasset batch correction**:
- Need TF activity scoring after integration
- Want sequence-informed embeddings
- Have manageable dataset size (scBasset is slower)

**When to use simpler methods**:
- Only need clustering, no TF analysis
- Very large datasets
- Quick preliminary analysis

---

## References

- [scBasset Batch Tutorial](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/atac/scbasset_batch.html)
- [scBasset Paper](https://www.nature.com/articles/s41592-022-01562-8) - Yuan & Kelley, Nature Methods 2022
- [scvi-tools Documentation](https://docs.scvi-tools.org/)
- [scib-metrics](https://scib-metrics.readthedocs.io/) - Integration benchmarking
