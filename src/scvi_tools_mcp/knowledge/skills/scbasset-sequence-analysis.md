---
name: scbasset-sequence-analysis
description: This skill should be used for analyzing single-cell ATAC-seq data using scBasset from scvi-tools, which incorporates DNA sequence information into the analysis. Use this skill when the user needs to infer transcription factor (TF) activity, wants sequence-aware dimensionality reduction, needs to understand how DNA motifs affect chromatin accessibility, or wants interpretable deep learning analysis of scATAC-seq data. This skill is appropriate for requests like "infer TF activity from scATAC", "run scBasset analysis", "score transcription factor activity", or "sequence-based ATAC analysis".
---

# Sequence-Aware scATAC-seq Analysis with scBasset

## Overview

scBasset is a deep learning method that:

1. **Learns from DNA sequences**: Incorporates actual peak sequences into the model
2. **Infers TF activity**: Uses motif injection to score transcription factor activity per cell
3. **Provides interpretable embeddings**: Cell embeddings reflect sequence-learned features
4. **Handles sparse data**: Deep learning architecture designed for scATAC-seq sparsity

**Key Advantages**:
- TF activity scoring without external tools
- Sequence-aware representation learning
- Cell-type-specific chromatin pattern discovery
- Efficient handling of large-scale datasets

**Note**: scBasset's development is ongoing. Results may not fully reproduce the original implementation.

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
import muon

scvi.settings.seed = 0
sc.set_figure_params(figsize=(6, 6), frameon=False)
torch.set_float32_matmul_precision("high")
```

**Additional Requirements**:
- Reference genome files (FASTA)
- TF motif database (for TF activity scoring)

---

### Step 2: Load scATAC-seq Data

```python
# Load scATAC-seq data
# Option 1: From h5ad
adata = sc.read_h5ad("path/to/atac_data.h5ad")

# Option 2: From multiome h5mu
# mdata = muon.read_10x_h5("path/to/data.h5mu")
# adata = mdata.mod["atac"]

print(f"Data: {adata.n_obs} cells, {adata.n_vars} peaks")
```

**Data Requirements**:
- Peak-by-cell matrix
- Peak coordinates in `adata.var` (chr, start, end)
- Binary or count data (will be binarized)

---

### Step 3: Parse and Validate Genomic Coordinates

```python
# Check if coordinates exist
if "chr" not in adata.var.columns:
    # Parse from peak names (format: chr1:1000-2000 or chr1_1000_2000)
    if ":" in adata.var_names[0]:
        # Format: chr1:1000-2000
        split_interval = adata.var_names.str.split(":", expand=True)
        adata.var["chr"] = split_interval[0]
        split_coords = split_interval[1].str.split("-", expand=True)
        adata.var["start"] = split_coords[0].astype(int)
        adata.var["end"] = split_coords[1].astype(int)
    elif "_" in adata.var_names[0]:
        # Format: chr1_1000_2000
        split_parts = adata.var_names.str.split("_", expand=True)
        adata.var["chr"] = split_parts[0]
        adata.var["start"] = split_parts[1].astype(int)
        adata.var["end"] = split_parts[2].astype(int)
    else:
        # Try gene_ids column if available
        if "gene_ids" in adata.var.columns:
            split_interval = adata.var["gene_ids"].str.split(":", expand=True)
            adata.var["chr"] = split_interval[0]
            split_coords = split_interval[1].str.split("-", expand=True)
            adata.var["start"] = split_coords[0].astype(int)
            adata.var["end"] = split_coords[1].astype(int)

# Verify coordinates
print(f"Chromosomes: {adata.var['chr'].unique()[:5]}...")
print(f"Coordinate range: {adata.var['start'].min()} - {adata.var['end'].max()}")

# Filter to standard chromosomes only (remove chrM, chrUn, random, etc.)
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

# Cell-level QC
adata.obs["n_peaks"] = np.array((adata.X > 0).sum(axis=1)).flatten()
adata.obs["total_counts"] = np.array(adata.X.sum(axis=1)).flatten()
```

---

### Step 5: Add DNA Sequences

```python
# Download or specify genome location
genome_name = "GRCh38"  # or "hg19", "mm10", etc.
genome_dir = "path/to/genomes"  # Directory to store/find genome

# Add DNA sequences to peaks
# This will download the genome if not present
scvi.data.add_dna_sequence(
    adata,
    genome_name=genome_name,
    genome_dir=genome_dir,
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
)

# Verify sequences added
print(f"DNA codes shape: {adata.varm['dna_code'].shape}")
print(f"Sequence length per peak: {adata.varm['dna_code'].shape[1]}")
```

**Genome Options**:
- `GRCh38` / `hg38`: Human (latest)
- `hg19` / `GRCh37`: Human (legacy)
- `mm10` / `GRCm38`: Mouse
- `mm39` / `GRCm39`: Mouse (latest)

**Note**: First run will download the genome (~3GB for human). Subsequent runs use cached files.

---

### Step 6: Prepare Data for scBasset (Transpose)

```python
# CRITICAL: scBasset requires data in peaks × cells format
# Standard AnnData is cells × peaks, so we transpose
bdata = adata.transpose()

# Create binary accessibility layer
# scBasset uses binary (0/1) accessibility
bdata.layers["binary"] = (bdata.X.copy() > 0).astype(float)

print(f"Transposed data: {bdata.n_obs} peaks × {bdata.n_vars} cells")
print(f"Binary layer created with dtype: {bdata.layers['binary'].dtype}")

# Verify dna_code is in correct location after transpose
# Should now be in bdata.obsm (since peaks are now observations)
print(
    f"DNA codes location: bdata.obsm['dna_code'] shape = {bdata.obsm['dna_code'].shape}"
)
```

**Why Transpose?**
- scBasset trains on mini-batches of peaks (not cells)
- Each peak has an associated DNA sequence
- Peaks as observations allows sequence-based batching

---

### Step 7: Setup AnnData for scBasset

```python
# Setup transposed data for scBasset
scvi.external.SCBASSET.setup_anndata(bdata, layer="binary", dna_code_key="dna_code")

print("AnnData registered for scBasset")
```

**Setup Parameters**:
- `layer`: Must be the binary accessibility layer
- `dna_code_key`: Key for DNA sequences (in obsm after transpose)
- `batch_key`: Optional, for multi-batch analysis (see batch correction skill)

---

### Step 8: Initialize and Train scBasset Model

```python
# Initialize model
model = scvi.external.SCBASSET(bdata)

# View model architecture
print(model)

# Train with 16-bit precision (reduces memory, same performance)
model.train(precision=16)

# Training uses AUROC metric for early stopping
# Default max_epochs=1000, typically stops earlier

# Check training history
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
# Cell bias (library size effect)
cell_bias = model.get_cell_bias()
plt.hist(cell_bias, bins=50)
plt.xlabel("Cell Bias")
plt.ylabel("Count")
plt.title("Cell Bias Distribution")

plt.tight_layout()
plt.show()
```

**Training Notes**:
- `precision=16`: Uses 16-bit floats, reduces memory ~50%
- AUROC monitors classification performance on held-out data
- Early stopping triggers after 45 epochs without improvement
- Training time ~1-2 hours for 10k cells

---

### Step 9: Extract Latent Representation and Cluster

```python
# Get latent representation (32 dimensions by default)
latent = model.get_latent_representation()

# Add back to ORIGINAL adata (not transposed bdata)
adata.obsm["X_scbasset"] = latent

print(f"Latent representation shape: {latent.shape}")

# Build neighborhood graph
sc.pp.neighbors(adata, use_rep="X_scbasset")

# UMAP visualization
sc.tl.umap(adata)

# Clustering
sc.tl.leiden(adata, key_added="leiden_scbasset")

# Visualize
sc.pl.umap(adata, color="leiden_scbasset", title="scBasset Clusters")

# Check cell bias correlation with counts (QC)
adata.obs["cell_bias"] = model.get_cell_bias()
sc.pl.umap(adata, color=["cell_bias", "n_peaks"], ncols=2)
```

---

### Step 10: Transcription Factor Activity Scoring

```python
# Score TF activity using motif injection
# Requires motif database (JASPAR, HOCOMOCO, etc.)

# Download or specify motif directory
motif_dir = "path/to/motifs"  # Contains .motif files

# Score activity for specific TFs
tfs_to_score = ["PAX5", "TCF7", "RXRA", "SPI1", "GATA1"]

for tf in tfs_to_score:
    try:
        activity = model.get_tf_activity(tf=tf, motif_dir=motif_dir)
        adata.obs[f"TF_{tf}"] = activity
        print(f"Scored {tf}: range [{activity.min():.3f}, {activity.max():.3f}]")
    except Exception as e:
        print(f"Could not score {tf}: {e}")

# Visualize TF activities
tf_cols = [c for c in adata.obs.columns if c.startswith("TF_")]
if tf_cols:
    sc.pl.umap(
        adata,
        color=tf_cols,
        ncols=3,
        cmap="PRGn",  # Diverging colormap for TF activity
        vcenter=0,
    )
```

**How TF Activity Scoring Works**:
1. **Motif injection**: Insert TF binding motif into peak sequences
2. **Prediction comparison**: Compare accessibility prediction with vs without motif
3. **Activity score**: Difference indicates TF's effect on accessibility
4. **Per-cell scores**: Each cell gets a TF activity score

---

### Save Results

```python
# Save trained model
model_dir = "scbasset_model"
model.save(model_dir, overwrite=True)

# Save analyzed AnnData (original orientation)
adata.write_h5ad("atac_scbasset_analyzed.h5ad")

# Export TF activities
tf_cols = [c for c in adata.obs.columns if c.startswith("TF_")]
if tf_cols:
    adata.obs[["leiden_scbasset"] + tf_cols].to_csv("tf_activities.csv")

# Reload model later
# Note: Need to provide transposed bdata
# model = scvi.external.SCBASSET.load(model_dir, adata=bdata)
```

---

## Key Parameters Reference

### Setup Parameters

| Parameter | Description |
|-----------|-------------|
| `layer` | Binary accessibility layer (required) |
| `dna_code_key` | DNA sequence codes in obsm (required) |
| `batch_key` | Batch labels for integration (optional) |

### Model Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_bottleneck_layer` | 32 | Latent/embedding dimensions |
| `l2_reg_cell_embedding` | 0.0 | L2 regularization (for batch correction) |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_epochs` | 1000 | Maximum training epochs |
| `precision` | 32 | Float precision (16 or 32) |
| `early_stopping_patience` | 45 | Epochs without improvement |

---

## Understanding scBasset Architecture

### Model Structure

```
DNA Sequences (1344 bp per peak)
        ↓
Convolutional Layers (learn motifs)
        ↓
Pooling Layers
        ↓
Dense Layers
        ↓
Cell Embedding (32D) + Peak Embedding
        ↓
Accessibility Prediction
```

### Key Components

1. **DNA encoder**: Convolutional neural network learns sequence patterns
2. **Cell embedding**: 32D representation of each cell's accessibility profile
3. **Peak embedding**: Learned representations for each genomic region
4. **Cell bias**: Library size effect per cell

---

## TF Activity Scoring Details

### Motif Injection Method

```python
# Conceptually:
# 1. For each cell, get accessibility predictions
# 2. Inject TF motif into sequences
# 3. Get new predictions
# 4. Score = Δ(prediction with motif - prediction without)

# The actual implementation:
activity = model.get_tf_activity(
    tf="PAX5",  # TF name (must match motif file)
    motif_dir="motifs/",  # Directory with .motif files
)
```

### Motif Database Setup

```bash
# Download JASPAR motifs (example)
# Or use HOCOMOCO, CIS-BP, etc.
mkdir -p motifs
# Download individual .motif files or convert from .pfm/.pwm
```

### Interpreting TF Scores

| Score | Interpretation |
|-------|----------------|
| Positive | TF motif increases accessibility (activator) |
| Negative | TF motif decreases accessibility (repressor) |
| Near zero | TF has minimal effect in that cell |

---

## Advanced Usage

### Custom Training Configuration

```python
# More latent dimensions
model = scvi.external.SCBASSET(bdata, n_bottleneck_layer=64)  # Increase from default 32

# Extended training
model.train(max_epochs=2000, precision=16, early_stopping_patience=100)
```

### Cell-Type-Specific TF Programs

```python
# After clustering, compare TF activities across cell types
import pandas as pd

# Calculate mean TF activity per cluster
tf_cols = [c for c in adata.obs.columns if c.startswith("TF_")]
tf_by_cluster = adata.obs.groupby("leiden_scbasset")[tf_cols].mean()

# Visualize as heatmap
import seaborn as sns

plt.figure(figsize=(10, 6))
sns.heatmap(tf_by_cluster.T, cmap="RdBu_r", center=0)
plt.title("TF Activity by Cluster")
plt.tight_layout()
plt.show()

# Find cluster-specific TFs
for cluster in tf_by_cluster.index:
    top_tfs = tf_by_cluster.loc[cluster].nlargest(5)
    print(f"Cluster {cluster} top TFs: {list(top_tfs.index)}")
```

### Comparing Cell Bias with Library Size

```python
# Cell bias should correlate with total counts/peaks
# This validates the model captured technical variation

plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.scatter(adata.obs["n_peaks"], adata.obs["cell_bias"], alpha=0.3)
plt.xlabel("Number of Peaks")
plt.ylabel("Cell Bias")
plt.title("Cell Bias vs Peak Count")

plt.subplot(1, 2, 2)
plt.scatter(adata.obs["total_counts"], adata.obs["cell_bias"], alpha=0.3)
plt.xlabel("Total Counts")
plt.ylabel("Cell Bias")
plt.title("Cell Bias vs Total Counts")

plt.tight_layout()
plt.show()

# Calculate correlation
from scipy.stats import pearsonr

r, p = pearsonr(adata.obs["n_peaks"], adata.obs["cell_bias"])
print(f"Correlation (peaks vs bias): r={r:.3f}, p={p:.2e}")
```

---

## Parameter Tuning Guide

### When to Adjust Parameters

**Before running, ask the user:**
1. How many cells and peaks?
2. Which species/genome?
3. Do you need TF activity scoring?
4. What computational resources are available?

### Peak Filtering (`min_detection`)

| Data Characteristic | Recommended Value | Rationale |
|---------------------|-------------------|-----------|
| Standard 10x data | 0.05 (5%) | Balanced default |
| Very sparse | 0.03 (3%) | Preserve more sequence information |
| High quality | 0.08-0.10 | Focus training on robust peaks |
| Limited memory | 0.10+ | Reduce peak count for efficiency |

### Model Architecture (`n_bottleneck_layer`)

| Scenario | n_bottleneck_layer | Notes |
|----------|-------------------|-------|
| Standard analysis | 32 | Default, works well |
| Simple cell types | 16-24 | Fewer dimensions needed |
| Complex heterogeneity | 48-64 | More cell states to capture |
| Memory constrained | 16-24 | Reduces model size |

### Training Parameters

| Scenario | precision | max_epochs | Notes |
|----------|-----------|------------|-------|
| Quick test | 16 | 500 | Fast check |
| Standard | 16 | 1000 | Default, memory efficient |
| High accuracy | 32 | 1000-2000 | If memory allows |
| Large dataset | 16 | 1000 | May converge early |

### L2 Regularization (for batch effects)

| Scenario | l2_reg_cell_embedding | Notes |
|----------|----------------------|-------|
| No batch effects | 0.0 | Default for single-sample |
| Mild batch effects | 1e-9 | Light integration |
| Standard integration | 1e-8 | Recommended for multi-batch |
| Strong batch effects | 1e-7 | Aggressive integration |

---

## Adaptation Prompts for Claude

When a user invokes this skill, consider asking:

1. **Data and genome:**
   - "What species is your data from?"
   - "Do you have genomic coordinates (chr, start, end) for peaks?"
   - "Have you downloaded the reference genome?"

2. **Analysis goals:**
   - "Which transcription factors are you interested in?"
   - "Do you have TF motif files available?"
   - "Is TF activity the main goal, or also clustering?"

3. **Resources:**
   - "Do you have GPU access? (scBasset benefits greatly)"
   - "How much RAM is available?"
   - "Any time constraints?"

4. **Previous experience:**
   - "Have you run PeakVI first for quick clustering?"
   - "Are you familiar with motif analysis?"

### Data Readiness Check

```python
def check_scbasset_readiness(adata):
    """Verify data is ready for scBasset."""
    ready = True
    recommendations = []

    # Check coordinates
    required_cols = ["chr", "start", "end"]
    missing = [c for c in required_cols if c not in adata.var.columns]
    if missing:
        ready = False
        recommendations.append(f"Missing columns: {missing}. Parse from peak names.")

    # Check chromosomes
    if "chr" in adata.var.columns:
        non_standard = adata.var["chr"].str.contains("random|Un|chrM", na=False).sum()
        if non_standard > 0:
            recommendations.append(
                f"{non_standard} non-standard chromosomes. Filter these."
            )

    # Check size
    if adata.n_vars > 100000:
        recommendations.append(
            "Very many peaks. Consider stricter filtering (0.08-0.10)."
        )
    if adata.n_obs > 50000:
        recommendations.append("Large dataset. Use precision=16 and GPU if available.")

    # Memory estimate
    estimated_memory_gb = (adata.n_vars * 1344 * 4) / 1e9  # DNA codes
    recommendations.append(
        f"Estimated memory for DNA codes: ~{estimated_memory_gb:.1f} GB"
    )

    print("scBasset Readiness Check:")
    print(f"  Ready: {ready}")
    for rec in recommendations:
        print(f"  - {rec}")

    return ready
```

### TF Motif Setup Guide

```python
# Motif database options:
# 1. JASPAR (recommended): https://jaspar.genereg.net/
# 2. HOCOMOCO: https://hocomoco11.autosome.org/
# 3. CIS-BP: http://cisbp.ccbr.utoronto.ca/

# Download JASPAR vertebrate motifs:
# wget https://jaspar.genereg.net/download/data/2024/CORE/JASPAR2024_CORE_vertebrates_non-redundant_pfms_meme.txt

# Convert to individual .motif files or use direct MEME format
# Check TF naming matches motif filenames (e.g., PAX5.motif)
```

---

## Troubleshooting

### Common Issues

1. **Genome download fails**:
   - Check internet connection
   - Try manual download to genome_dir
   - Verify genome_name matches available genomes

2. **DNA codes shape mismatch**:
   - Ensure coordinates are within chromosome bounds
   - Check for invalid chromosomes (chrM, chrUn)
   - Verify start < end for all peaks

3. **Training very slow**:
   - Use `precision=16`
   - Filter more peaks
   - Ensure GPU is being used

4. **TF scoring fails**:
   - Verify motif file exists for TF name
   - Check motif format compatibility
   - Try different TF naming (e.g., PAX5 vs Pax5)

5. **Poor clustering**:
   - Check if training converged (AUROC should be > 0.7)
   - Train longer
   - Verify peak filtering was appropriate

6. **Out of memory**:
   - Use `precision=16`
   - Filter more peaks (reduce n_vars)
   - Process in batches

### Verifying Data Orientation

```python
# Before transpose (standard AnnData):
# adata: cells × peaks
# adata.obsm contains cell embeddings
# adata.varm contains peak info (dna_code)

# After transpose (for scBasset):
# bdata: peaks × cells
# bdata.obsm contains peak info (dna_code)
# bdata.varm contains cell info

# Verify orientation
print("Original adata:")
print(f"  Shape: {adata.shape} (cells × peaks)")
print(f"  DNA codes in varm: {'dna_code' in adata.varm}")

print("\nTransposed bdata:")
print(f"  Shape: {bdata.shape} (peaks × cells)")
print(f"  DNA codes in obsm: {'dna_code' in bdata.obsm}")
```

---

## Comparison with Other Methods

| Feature | scBasset | PeakVI | PoissonVI |
|---------|----------|--------|-----------|
| Sequence-aware | Yes | No | No |
| TF activity | Yes | No | No |
| Training speed | Slow | Fast | Medium |
| Memory usage | High | Low | Medium |
| Interpretability | High | Medium | Medium |
| Best for | TF analysis | Standard clustering | Quantitative |

---

## References

- [scBasset Tutorial](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/atac/scbasset.html)
- [scBasset Paper](https://www.nature.com/articles/s41592-022-01562-8) - Yuan & Kelley, Nature Methods 2022
- [scvi-tools Documentation](https://docs.scvi-tools.org/)
- [JASPAR Motif Database](https://jaspar.genereg.net/)
