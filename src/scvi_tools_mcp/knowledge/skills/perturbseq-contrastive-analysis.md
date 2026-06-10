---
name: perturbseq-contrastive-analysis
description: This skill should be used for analyzing Perturb-seq (CRISPR perturbation screening) single-cell data using contrastiveVI from scvi-tools. Use this skill when the user asks to analyze CRISPR perturbation experiments, identify perturbation-specific effects, separate confounding factors from perturbation responses, or perform differential analysis on Perturb-seq data. This skill is appropriate for requests like "analyze my Perturb-seq data", "identify perturbation effects", "run contrastiveVI analysis", or "separate cell cycle from perturbation effects".
---

# Perturb-seq Analysis with ContrastiveVI

## Overview

ContrastiveVI isolates perturbation-induced variations in Perturb-seq experiments by explicitly decomposing single-cell data into:

- **Background variables**: Shared variations across perturbed and control cells (e.g., cell cycle, technical noise)
- **Salient variables**: Active only in perturbed cells, capturing true perturbation effects

This separation is critical because CRISPR-mediated gene perturbation effects are often confounded by variations shared with control cells.

**Citation**: Weinberger, E., Lin, C. & Lee, S. Isolating salient variations of interest in single-cell data with contrastiveVI. *Nature Methods* 20, 1336–1345 (2023).

---

## Workflow Steps

### Step 1: Environment Setup and Data Loading

```python
import os
import numpy as np
import scanpy as sc
import scvi
import seaborn as sns
import torch
import matplotlib.pyplot as plt

# Set reproducibility and display settings
scvi.settings.seed = 0
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")

# Load your Perturb-seq data
# IMPORTANT: Data must have raw counts available
adata = sc.read_h5ad("path/to/perturbseq_data.h5ad")

# Verify data structure
print(f"Cells: {adata.n_obs}, Genes: {adata.n_vars}")
print(f"Available layers: {list(adata.layers.keys())}")
print(f"Observation columns: {list(adata.obs.columns)}")
```

**Data Requirements**:
- Raw counts must be available (in `adata.X` or a layer like `adata.layers['counts']`)
- Perturbation labels in `adata.obs` (e.g., 'perturbation', 'gene_program', 'guide_id')
- Control cells must be identifiable (e.g., non-targeting guides, 'Ctrl' label)

---

### Step 2: Data Preprocessing

```python
# If counts are in a layer, ensure they're accessible
if "counts" in adata.layers:
    count_layer = "counts"
elif "count" in adata.layers:
    count_layer = "count"
else:
    # Assume adata.X contains counts, create a layer
    adata.layers["counts"] = adata.X.copy()
    count_layer = "counts"

# Basic filtering (adjust thresholds as needed)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Calculate QC metrics
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

# Filter based on QC (adjust thresholds for your data)
adata = adata[adata.obs.pct_counts_mt < 20, :].copy()

print(f"After filtering: {adata.n_obs} cells, {adata.n_vars} genes")
```

---

### Step 3: Cell Cycle Scoring (Optional but Recommended)

Cell cycle is a common confounding factor in Perturb-seq experiments. Scoring cells allows you to verify that contrastiveVI successfully separates this effect.

```python
import requests


def get_cell_cycle_genes():
    """Fetch cell cycle gene lists from Regev lab."""
    url = "https://raw.githubusercontent.com/scverse/scanpy_usage/master/180209_cell_cycle/data/regev_lab_cell_cycle_genes.txt"
    response = requests.get(url)
    cell_cycle_genes = response.text.strip().split("\n")
    return cell_cycle_genes


# Get cell cycle genes
cell_cycle_genes = get_cell_cycle_genes()
s_genes = cell_cycle_genes[:43]
g2m_genes = cell_cycle_genes[43:]

# Filter to genes present in dataset
s_genes = [g for g in s_genes if g in adata.var_names]
g2m_genes = [g for g in g2m_genes if g in adata.var_names]

# Normalize for scoring (temporary)
adata_norm = adata.copy()
sc.pp.normalize_total(adata_norm, target_sum=1e4)
sc.pp.log1p(adata_norm)

# Score cell cycle
sc.tl.score_genes_cell_cycle(adata_norm, s_genes=s_genes, g2m_genes=g2m_genes)
adata.obs["S_score"] = adata_norm.obs["S_score"]
adata.obs["G2M_score"] = adata_norm.obs["G2M_score"]
adata.obs["phase"] = adata_norm.obs["phase"]

print(f"Cell cycle phases:\n{adata.obs['phase'].value_counts()}")
```

---

### Step 4: Define Control and Perturbed Populations

```python
# CRITICAL: Adjust the column name and control label for your data
# Common column names: 'perturbation', 'gene_program', 'guide_id', 'condition'
perturbation_col = "perturbation"  # <-- MODIFY for your data
control_label = (
    "Ctrl"  # <-- MODIFY for your data (e.g., 'non-targeting', 'NT', 'control')
)

# Verify the column exists and show available labels
print(f"Available perturbations:\n{adata.obs[perturbation_col].value_counts()}")

# Define indices
background_indices = np.where(adata.obs[perturbation_col] == control_label)[0]
target_indices = np.where(adata.obs[perturbation_col] != control_label)[0]

print(f"\nControl cells: {len(background_indices)}")
print(f"Perturbed cells: {len(target_indices)}")

# Sanity check
assert len(background_indices) > 0, "No control cells found! Check control_label"
assert len(target_indices) > 0, "No perturbed cells found! Check perturbation_col"
```

---

### Step 5: Setup and Train ContrastiveVI Model

```python
# Setup AnnData for scvi
scvi.external.ContrastiveVI.setup_anndata(
    adata, layer=count_layer  # Use the layer containing raw counts
)

# Create model instance
# Key parameters:
# - n_salient_latent: dimensions for perturbation-specific effects (default: 10)
# - n_background_latent: dimensions for shared variations (default: 10)
# - use_observed_lib_size: whether to use observed library size (default: False)
model = scvi.external.ContrastiveVI(
    adata, n_salient_latent=10, n_background_latent=10, use_observed_lib_size=False
)

print(model)
```

```python
# Train the model
# CRITICAL: Pass background and target indices correctly
model.train(
    background_indices=background_indices,
    target_indices=target_indices,
    max_epochs=500,
    early_stopping=True,
    early_stopping_patience=20,
    plan_kwargs={"lr": 1e-3},
)

# Plot training history
train_elbo = model.history["elbo_train"]
plt.figure(figsize=(8, 4))
plt.plot(train_elbo.index, train_elbo.values)
plt.xlabel("Epoch")
plt.ylabel("ELBO")
plt.title("ContrastiveVI Training")
plt.tight_layout()
plt.show()
```

---

### Step 6: Extract Latent Representations

```python
# Get all latent representations for analysis
# For perturbed cells only (salient representation is most informative)
perturbed_adata = adata[adata.obs[perturbation_col] != control_label].copy()

# Extract salient representation (perturbation-specific)
perturbed_adata.obsm["salient_rep"] = model.get_latent_representation(
    perturbed_adata, representation_kind="salient"
)

# Extract background representation (shared variations)
perturbed_adata.obsm["background_rep"] = model.get_latent_representation(
    perturbed_adata, representation_kind="background"
)

# For the full dataset (control + perturbed)
adata.obsm["salient_rep"] = model.get_latent_representation(
    adata, representation_kind="salient"
)
adata.obsm["background_rep"] = model.get_latent_representation(
    adata, representation_kind="background"
)

print(f"Salient representation shape: {perturbed_adata.obsm['salient_rep'].shape}")
print(
    f"Background representation shape: {perturbed_adata.obsm['background_rep'].shape}"
)
```

---

### Step 7: Visualization - Compare Before and After

```python
# BEFORE ContrastiveVI: Standard PCA/UMAP (confounded)
sc.pp.neighbors(perturbed_adata)
sc.tl.umap(perturbed_adata)
perturbed_adata.obsm["X_umap_standard"] = perturbed_adata.obsm["X_umap"].copy()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
sc.pl.umap(
    perturbed_adata,
    color="phase",
    ax=axes[0],
    show=False,
    title="Standard UMAP - Cell Cycle",
)
sc.pl.umap(
    perturbed_adata,
    color=perturbation_col,
    ax=axes[1],
    show=False,
    title="Standard UMAP - Perturbation",
)
plt.suptitle("Before ContrastiveVI (Standard Analysis)", y=1.02)
plt.tight_layout()
plt.show()
```

```python
# AFTER ContrastiveVI: Using salient representation
sc.pp.neighbors(perturbed_adata, use_rep="salient_rep")
sc.tl.umap(perturbed_adata)
perturbed_adata.obsm["X_umap_salient"] = perturbed_adata.obsm["X_umap"].copy()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
sc.pl.umap(
    perturbed_adata,
    color="phase",
    ax=axes[0],
    show=False,
    title="Salient UMAP - Cell Cycle",
)
sc.pl.umap(
    perturbed_adata,
    color=perturbation_col,
    ax=axes[1],
    show=False,
    title="Salient UMAP - Perturbation",
)
plt.suptitle("After ContrastiveVI (Salient Representation)", y=1.02)
plt.tight_layout()
plt.show()
```

**Expected Result**: In the salient representation, cells should cluster by perturbation (gene program) rather than by cell cycle phase, demonstrating successful separation of confounding factors.

---

### Step 8: Clustering and Perturbation Effect Analysis

```python
# Cluster based on salient representation
sc.pp.neighbors(perturbed_adata, use_rep="salient_rep")
sc.tl.leiden(perturbed_adata, resolution=0.5, key_added="salient_clusters")

# Visualize clusters
sc.pl.umap(
    perturbed_adata,
    color=["salient_clusters", perturbation_col],
    title=["Salient Clusters", "Perturbations"],
)
```

```python
# Analyze perturbation enrichment in clusters
import pandas as pd

# Cross-tabulation of clusters vs perturbations
crosstab = pd.crosstab(
    perturbed_adata.obs["salient_clusters"],
    perturbed_adata.obs[perturbation_col],
    normalize="index",
)

# Heatmap of perturbation distribution across clusters
plt.figure(figsize=(12, 6))
sns.heatmap(crosstab, cmap="viridis", annot=False)
plt.title("Perturbation Distribution Across Salient Clusters")
plt.xlabel("Perturbation")
plt.ylabel("Cluster")
plt.tight_layout()
plt.show()
```

---

### Step 9: Differential Expression Analysis

```python
# Differential expression between perturbations using salient representation
# First, get normalized expression for DE analysis
adata_de = perturbed_adata.copy()
sc.pp.normalize_total(adata_de, target_sum=1e4)
sc.pp.log1p(adata_de)

# Rank genes by perturbation group
sc.tl.rank_genes_groups(adata_de, groupby=perturbation_col, method="wilcoxon")

# View top differentially expressed genes
sc.pl.rank_genes_groups(adata_de, n_genes=10, sharey=False)
```

```python
# Extract DE results for specific perturbations
def get_de_results(adata, group, n_genes=50):
    """Extract DE results for a specific perturbation."""
    result = sc.get.rank_genes_groups_df(adata, group=group)
    return result.head(n_genes)


# Example: Get DE genes for a specific perturbation
# perturbation_of_interest = 'GENE_NAME'  # <-- MODIFY
# de_results = get_de_results(adata_de, perturbation_of_interest)
# print(de_results)
```

---

### Step 10: Save Results

```python
# Save the model
model_path = "contrastive_vi_model"
model.save(model_path, overwrite=True)
print(f"Model saved to: {model_path}")

# Save the annotated AnnData
perturbed_adata.write_h5ad("perturbseq_analyzed.h5ad")
print("Analyzed data saved to: perturbseq_analyzed.h5ad")

# To reload later:
# model = scvi.external.ContrastiveVI.load(model_path, adata=adata)
```

---

## Key Parameters Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_salient_latent` | 10 | Dimensions for perturbation-specific effects |
| `n_background_latent` | 10 | Dimensions for shared variations (cell cycle, batch) |
| `use_observed_lib_size` | False | Whether to use observed vs inferred library size |
| `max_epochs` | 500 | Maximum training epochs |
| `early_stopping` | True | Stop when validation loss plateaus |
| `early_stopping_patience` | 20 | Epochs to wait before stopping |

---

## Troubleshooting

### Common Issues

1. **"No control cells found"**: Check that `control_label` exactly matches your data (case-sensitive)

2. **Poor separation in UMAP**:
   - Increase `n_salient_latent` if perturbation effects are complex
   - Train for more epochs
   - Ensure sufficient control cells (recommend >500)

3. **Memory errors**:
   - Reduce batch size: `model.train(..., batch_size=128)`
   - Subset to highly variable genes first

4. **Convergence issues**:
   - Adjust learning rate: `plan_kwargs={'lr': 5e-4}`
   - Increase `early_stopping_patience`

---

## References

- [ContrastiveVI Tutorial](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/scrna/contrastiveVI_tutorial.html)
- [scvi-tools Documentation](https://docs.scvi-tools.org/)
- [Original Paper](https://doi.org/10.1038/s41592-023-01955-3)
