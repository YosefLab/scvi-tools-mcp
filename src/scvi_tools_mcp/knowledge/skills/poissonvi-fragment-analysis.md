---
name: poissonvi-fragment-analysis
description: This skill should be used for analyzing single-cell ATAC-seq data using PoissonVI from scvi-tools, specifically when working with quantitative fragment counts rather than binary accessibility. Use this skill when the user has high-coverage scATAC-seq data, wants to model fragment counts accurately, needs to convert read counts to fragments, or prefers quantitative modeling over binary approaches. This skill is appropriate for requests like "analyze my fragment counts", "run PoissonVI on scATAC data", "convert reads to fragments", or "quantitative ATAC analysis".
---

# Fragment-Level scATAC-seq Analysis with PoissonVI

## Overview

PoissonVI models single-cell ATAC-seq data using fragment counts rather than binary accessibility:

1. **Fragment-based modeling**: Uses actual fragment counts for more accurate quantitative inference
2. **Read-to-fragment conversion**: Handles the conversion from read counts to fragments
3. **Differential accessibility**: Provides count-aware differential testing
4. **Batch correction**: Supports multi-batch integration

**Key Advantages**:
- More accurate for high-coverage data
- Fragment counts have "monotonic decreasing" distribution (better for modeling)
- Captures accessibility intensity, not just presence/absence
- Published in Nature Methods (Martens et al., 2023)

**Citation**: Martens et al. (2023). "Modeling fragment counts improves single-cell ATAC-seq analysis." Nature Methods.

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

### Step 2: Load scATAC-seq Data

```python
# Load scATAC-seq data
adata = sc.read_h5ad("path/to/atac_data.h5ad")

# Alternative: Load from 10x ATAC output
# adata = scvi.data.read_10x_atac("path/to/10x_atac/")

print(f"Data: {adata.n_obs} cells, {adata.n_vars} regions")
print(f"Data type: {adata.X.dtype}")
print(f"Sparsity: {1 - (adata.X.nnz / (adata.n_obs * adata.n_vars)):.2%}")
```

**Data Requirements**:
- Cell-by-region count matrix
- Can be read counts (will convert) or fragment counts
- Regions as variables (peaks, windows, or other features)

---

### Step 3: Detect and Convert Read Counts to Fragments

**Critical Step**: Read counts and fragment counts have different statistical properties. PoissonVI requires fragment counts.

```python
# Detect if data is reads or fragments
# Key insight: Read count matrices have more 2s than 1s
# Fragment count matrices have more 1s than 2s

if hasattr(adata.X, "toarray"):
    X_dense = adata.X.toarray()
else:
    X_dense = adata.X

count_1s = np.sum(X_dense == 1)
count_2s = np.sum(X_dense == 2)

print(f"Count of 1s: {count_1s:,}")
print(f"Count of 2s: {count_2s:,}")

if count_2s > count_1s:
    print("-> Detected READ COUNTS (more 2s than 1s)")
    print("-> Converting to fragment counts...")

    # Convert reads to fragments
    # Method: round to nearest even count, divide by 2
    scvi.data.reads_to_fragments(adata)

    print(f"Fragment layer created: 'fragments' in adata.layers")
else:
    print("-> Detected FRAGMENT COUNTS (more 1s than 2s)")
    print("-> No conversion needed")

    # Store as fragments layer for consistency
    adata.layers["fragments"] = adata.X.copy()
```

**Why This Matters**:
- Each DNA fragment generates two reads (forward and reverse)
- Read count matrices therefore have ~2x the counts of fragments
- Fragment counts follow a monotonically decreasing distribution
- This distribution is better suited for Poisson modeling

---

### Step 4: Quality Control and Filtering

```python
# Use fragments layer for QC
X_frag = adata.layers["fragments"]

# Calculate region detection across cells
if hasattr(X_frag, "toarray"):
    n_cells_per_region = np.array((X_frag > 0).sum(axis=0)).flatten()
else:
    n_cells_per_region = np.array((X_frag > 0).sum(axis=0)).flatten()

adata.var["n_cells_fragment"] = n_cells_per_region
adata.var["detection_rate"] = n_cells_per_region / adata.n_obs

# Filter regions: keep those detected in at least 5% of cells
min_detection = 0.05
min_cells = int(adata.n_obs * min_detection)

print(f"Regions before filtering: {adata.n_vars}")
sc.pp.filter_genes(adata, min_cells=min_cells)
print(f"Regions after filtering (>{min_detection*100}% detection): {adata.n_vars}")

# Calculate cell-level QC on fragments
frag_layer = adata.layers["fragments"]
if hasattr(frag_layer, "toarray"):
    adata.obs["n_fragments"] = np.array(frag_layer.sum(axis=1)).flatten()
    adata.obs["n_regions"] = np.array((frag_layer > 0).sum(axis=1)).flatten()
else:
    adata.obs["n_fragments"] = np.array(frag_layer.sum(axis=1)).flatten()
    adata.obs["n_regions"] = np.array((frag_layer > 0).sum(axis=1)).flatten()

# Visualize QC
sc.pl.violin(adata, ["n_fragments", "n_regions"], jitter=0.4)
```

---

### Step 5: Setup AnnData for PoissonVI

```python
# Setup with fragments layer
scvi.external.POISSONVI.setup_anndata(adata, layer="fragments")

# OR: Setup with batch correction
# scvi.external.POISSONVI.setup_anndata(
#     adata,
#     layer="fragments",
#     batch_key="batch"
# )

print("AnnData registered for PoissonVI")
print(f"Using layer: fragments")
```

**Setup Parameters**:
- `layer`: Must specify the fragments layer
- `batch_key`: Optional, for multi-batch integration

---

### Step 6: Initialize and Train PoissonVI Model

```python
# Initialize model
model = scvi.external.POISSONVI(adata)

# View model
print(model)

# Train
# - max_epochs=500 default (early stopping typically activates earlier)
model.train()

# Plot training history
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(model.history["elbo_train"].values, label="Train")
if "elbo_validation" in model.history:
    plt.plot(model.history["elbo_validation"].values, label="Validation")
plt.xlabel("Epoch")
plt.ylabel("ELBO")
plt.legend()
plt.title("PoissonVI Training")

plt.subplot(1, 2, 2)
plt.plot(model.history["reconstruction_loss_train"].values)
plt.xlabel("Epoch")
plt.ylabel("Reconstruction Loss")
plt.title("Reconstruction Loss")
plt.tight_layout()
plt.show()

print(f"Training completed at epoch {len(model.history['elbo_train'])}")
```

**Training Notes**:
- Default `max_epochs=500`, early stopping typically triggers at ~50%
- Monitor reconstruction loss for convergence
- Larger datasets converge faster per epoch

---

### Step 7: Extract Latent Representation

```python
# Get latent space
latent = model.get_latent_representation()
adata.obsm["X_poissonvi"] = latent

print(f"Latent representation shape: {latent.shape}")
```

---

### Step 8: Clustering and Visualization

```python
# Build neighborhood graph on PoissonVI latent space
sc.pp.neighbors(adata, use_rep="X_poissonvi")

# UMAP embedding
sc.tl.umap(adata, min_dist=0.2)

# Leiden clustering
sc.tl.leiden(adata, key_added="clusters_poissonvi", resolution=0.2)

# Visualize
sc.pl.umap(adata, color="clusters_poissonvi", title="PoissonVI Clusters")

# Check batch mixing if applicable
if "batch" in adata.obs.columns:
    sc.pl.umap(adata, color=["clusters_poissonvi", "batch"], ncols=2)
```

---

### Step 9: Differential Accessibility Analysis

```python
# Differential accessibility between clusters
da_results = model.differential_accessibility(
    adata,
    groupby="clusters_poissonvi",
    group1="3",  # Target cluster
    mode="vanilla",  # Standard mode
    two_sided=False,  # One-sided for markers
    batch_correction=True,  # For multi-batch data
)

# View results
print(da_results.head(10))
print(f"\nTotal regions tested: {len(da_results)}")

# Filter for marker peaks
# emp_prob1: empirical probability in group1 (target)
markers = da_results[da_results["emp_prob1"] >= 0.05].copy()
print(f"Marker peaks (emp_prob1 >= 0.05): {len(markers)}")

# Key columns:
# - prob_da: Probability of differential accessibility
# - is_da_fdr: FDR-controlled significance
# - bayes_factor: Effect size
# - emp_prob1, emp_prob2: Empirical accessibility rates
```

---

### Step 10: Save Results

```python
# Save trained model
model_dir = "poissonvi_model"
model.save(model_dir, overwrite=True)

# Save processed AnnData
adata.write_h5ad("atac_poissonvi_analyzed.h5ad")

# Export differential accessibility results
da_results.to_csv("differential_accessibility.csv")

# Export cluster markers
for cluster in adata.obs["clusters_poissonvi"].unique():
    da = model.differential_accessibility(
        adata,
        groupby="clusters_poissonvi",
        group1=str(cluster),
        mode="vanilla",
        two_sided=False,
    )
    significant = da[da["is_da_fdr"]]
    significant.to_csv(f"markers_cluster_{cluster}.csv")
    print(f"Cluster {cluster}: {len(significant)} marker peaks")

# Reload model later
# model = scvi.external.POISSONVI.load(model_dir, adata=adata)
```

---

## Key Parameters Reference

### Setup Parameters

| Parameter | Description |
|-----------|-------------|
| `layer` | Layer containing fragment counts (required) |
| `batch_key` | Column for batch labels (optional) |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_epochs` | 500 | Maximum training epochs |
| `early_stopping` | True | Stop on validation plateau |
| `batch_size` | 128 | Samples per batch |

### Differential Accessibility Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `groupby` | None | Column for group comparison |
| `group1` | None | Target group |
| `mode` | "vanilla" | Testing mode |
| `two_sided` | False | One or two-sided test |
| `batch_correction` | True | Sample across batches |

---

## Understanding Read vs Fragment Counts

### Why Convert Reads to Fragments?

```
DNA Fragment:     [===================]
                         ↓
Sequencing:       →→→→→→→→→→           (Read 1: forward)
                           ←←←←←←←←←←  (Read 2: reverse)
                         ↓
Read Count:       2 reads per fragment
Fragment Count:   1 fragment
```

**Statistical Properties**:
- Read counts: ~2x fragment counts
- Fragment distribution: Monotonically decreasing
- Read distribution: Peaks at even numbers (2, 4, 6...)
- Poisson models work better with fragment counts

### Detection Heuristic

```python
# Count occurrences
count_1s = np.sum(X == 1)
count_2s = np.sum(X == 2)

# Decision rule
if count_2s > count_1s:
    # READ COUNTS: More paired reads (2s) than single fragments
    # Each fragment → 2 reads → more 2s in the distribution
    scvi.data.reads_to_fragments(adata)
else:
    # FRAGMENT COUNTS: Natural distribution has more 1s
    # Already in correct format
    pass
```

---

## Interpretation Guidelines

### Differential Accessibility Results

| Column | Interpretation |
|--------|----------------|
| `prob_da` | Probability of differential accessibility (0-1) |
| `is_da_fdr` | True if significant after FDR correction |
| `bayes_factor` | Effect size (log scale) |
| `emp_prob1` | Empirical accessibility in group 1 |
| `emp_prob2` | Empirical accessibility in group 2 |

### Filtering Strategies

```python
# Conservative: FDR-controlled
significant = da_results[da_results["is_da_fdr"]]

# Moderate: High probability threshold
moderate = da_results[da_results["prob_da"] > 0.9]

# Marker-focused: High accessibility in target
markers = da_results[(da_results["prob_da"] > 0.8) & (da_results["emp_prob1"] >= 0.05)]
```

---

## Advanced Usage

### Multi-Batch Integration

```python
# Setup with batch correction
scvi.external.POISSONVI.setup_anndata(adata, layer="fragments", batch_key="batch")

model = scvi.external.POISSONVI(adata)
model.train()

# Verify batch integration
adata.obsm["X_poissonvi"] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_poissonvi")
sc.tl.umap(adata)
sc.pl.umap(adata, color=["batch", "clusters_poissonvi"], ncols=2)

# Differential accessibility with batch correction
da_results = model.differential_accessibility(
    adata,
    groupby="cell_type",
    group1="T_cells",
    batch_correction=True,  # Critical for multi-batch
)
```

### Comparing with PeakVI

```python
# Train both models on same data
# PoissonVI (quantitative)
scvi.external.POISSONVI.setup_anndata(adata, layer="fragments")
poissonvi = scvi.external.POISSONVI(adata)
poissonvi.train()
adata.obsm["X_poissonvi"] = poissonvi.get_latent_representation()

# PeakVI (binary)
scvi.model.PEAKVI.setup_anndata(adata)
peakvi = scvi.model.PEAKVI(adata)
peakvi.train()
adata.obsm["X_peakvi"] = peakvi.get_latent_representation()

# Compare embeddings
sc.pp.neighbors(adata, use_rep="X_poissonvi")
sc.tl.umap(adata)
adata.obsm["X_umap_poissonvi"] = adata.obsm["X_umap"].copy()

sc.pp.neighbors(adata, use_rep="X_peakvi")
sc.tl.umap(adata)
adata.obsm["X_umap_peakvi"] = adata.obsm["X_umap"].copy()

# Visualize side by side
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sc.pl.embedding(
    adata,
    basis="X_umap_poissonvi",
    color="cell_type",
    ax=axes[0],
    show=False,
    title="PoissonVI",
)
sc.pl.embedding(
    adata,
    basis="X_umap_peakvi",
    color="cell_type",
    ax=axes[1],
    show=False,
    title="PeakVI",
)
plt.tight_layout()
plt.show()
```

---

## Parameter Tuning Guide

### When to Adjust Parameters

**Before running, ask the user:**
1. What is your sequencing depth (fragments per cell)?
2. How many cells and peaks?
3. Single or multi-batch data?
4. Looking for coarse cell types or fine states?

### Peak Filtering (`min_detection`)

| Data Characteristic | Recommended Value | Rationale |
|---------------------|-------------------|-----------|
| Standard depth (~5-10k frags/cell) | 0.05 (5%) | Balanced default |
| Low depth (<3k frags/cell) | 0.03 (3%) | Preserve signal |
| High depth (>15k frags/cell) | 0.08-0.10 | Focus on consistent peaks |
| Small dataset (<2k cells) | 0.03 | Retain more features |
| Large dataset (>20k cells) | 0.05-0.10 | Can be stricter |

### Clustering Resolution

| Observation | Adjustment |
|-------------|------------|
| Too few clusters, known types missing | Increase to 0.3-0.5 |
| Too many clusters, fragmented | Decrease to 0.1-0.15 |
| Rare populations not appearing | Try 0.5-0.8, merge later |
| Expected ~10 cell types | Start at 0.2, adjust |

### Model Training

| Scenario | max_epochs | Notes |
|----------|------------|-------|
| Quick test | 200 | Check if data loads correctly |
| Standard | 500 | Default, early stopping helps |
| Large dataset | 500-750 | May converge faster per epoch |
| Not converging | 1000 | Check loss curve first |

---

## Adaptation Prompts for Claude

When a user invokes this skill, consider asking:

1. **Data characteristics:**
   - "Have you checked if your data is reads or fragments?"
   - "What's the median fragments per cell?"
   - "How many peaks after initial filtering?"

2. **Analysis goals:**
   - "Looking for major cell types or subtle states?"
   - "Will you be doing differential accessibility?"
   - "Need to compare with other methods?"

3. **Troubleshooting:**
   - "Have you tried PeakVI? How did results compare?"
   - "Any issues with previous clustering attempts?"

### Automatic Data Diagnostics

```python
def diagnose_atac_data(adata):
    """Provide data-driven parameter recommendations."""

    # Check read vs fragment
    X = adata.X.toarray() if hasattr(adata.X, "toarray") else adata.X
    count_1s = np.sum(X == 1)
    count_2s = np.sum(X == 2)

    if count_2s > count_1s:
        print("DETECTED: Read counts (more 2s than 1s)")
        print("ACTION: Run scvi.data.reads_to_fragments(adata)")
    else:
        print("DETECTED: Fragment counts (ready for PoissonVI)")

    # Sparsity
    sparsity = 1 - (adata.X.nnz / (adata.n_obs * adata.n_vars))
    print(f"Sparsity: {sparsity:.1%}")
    if sparsity > 0.99:
        print("Very sparse data - consider lower min_detection (0.03)")
    elif sparsity < 0.95:
        print("Relatively dense - standard filtering (0.05) ok")

    # Depth
    frags_per_cell = np.array(adata.X.sum(axis=1)).flatten()
    median_depth = np.median(frags_per_cell)
    print(f"Median fragments/cell: {median_depth:.0f}")
    if median_depth < 3000:
        print("Low depth - be conservative with filtering")
    elif median_depth > 15000:
        print("High depth - can use stricter filtering (0.08-0.10)")
```

---

## Troubleshooting

### Common Issues

1. **Forgot to convert reads to fragments**:
   - Check: count 1s vs 2s in your matrix
   - Fix: Run `scvi.data.reads_to_fragments(adata)`

2. **Poor clustering**:
   - Increase training epochs
   - Check peak filtering (may be too aggressive)
   - Verify fragment conversion was correct

3. **Training not converging**:
   - Reduce learning rate
   - Check for zero-variance regions
   - Increase batch size

4. **Few significant DA peaks**:
   - Lower probability threshold
   - Ensure sufficient cells per group
   - Check if groups overlap substantially

5. **Memory issues**:
   - Filter more regions
   - Use smaller batch size
   - Enable GPU training

### Debugging Read/Fragment Detection

```python
# Detailed count analysis
unique, counts = np.unique(X_dense.flatten(), return_counts=True)
for val, cnt in zip(unique[:10], counts[:10]):
    print(f"Value {val}: {cnt:,} occurrences")

# Plot distribution
plt.figure(figsize=(10, 4))
plt.hist(X_dense[X_dense > 0].flatten(), bins=50, log=True)
plt.xlabel("Count")
plt.ylabel("Frequency (log)")
plt.title("Count Distribution")
plt.show()
```

---

## References

- [PoissonVI Tutorial](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/atac/PoissonVI.html)
- [PoissonVI Paper](https://www.nature.com/articles/s41592-023-01949-0) - Martens et al., Nature Methods 2023
- [scvi-tools Documentation](https://docs.scvi-tools.org/)
