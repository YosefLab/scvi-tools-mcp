---
name: spatial-transcriptomics-scvi
description: This skill is a comprehensive guide for spatial transcriptomics analysis using scvi-tools. Use this skill when the user asks about spatial transcriptomics analysis, needs help choosing between spatial analysis methods, wants to perform deconvolution, spatial mapping, noise correction, or niche analysis on spatial data. This skill covers ResolVI, scVIVA, DestVI, Tangram, Stereoscope, and Cell2location methods.
---

# Spatial Transcriptomics Analysis with scvi-tools

## Overview

scvi-tools provides a unified framework for spatial transcriptomics analysis with six specialized methods:

| Method | Primary Use Case | Data Type |
|--------|------------------|-----------|
| **ResolVI** | Noise correction & denoising | Cellular-resolution (Xenium, MERFISH, CosMx) |
| **scVIVA** | Niche/microenvironment modeling | Cellular-resolution spatial |
| **DestVI** | Deconvolution with cell state variation | Spot-based (Visium) |
| **Tangram** | Cell type mapping & gene imputation | Any spatial with scRNA-seq |
| **Stereoscope** | Cell type proportion estimation | Spot-based (Visium) |
| **Cell2location** | Absolute cell abundance mapping | Spot-based (Visium) |

---

## Method Selection Decision Tree

```
Is your spatial data cellular-resolution (Xenium, MERFISH, CosMx)?
├── YES → Do you need noise correction?
│   ├── YES → Use ResolVI
│   └── NO → Do you want to model microenvironments?
│       ├── YES → Use scVIVA
│       └── NO → Use standard scVI workflow
│
└── NO (spot-based like Visium) → What's your goal?
    ├── Cell type proportions → DestVI or Stereoscope
    │   ├── Need intra-cell-type variation? → DestVI
    │   └── Just proportions? → Stereoscope
    │
    ├── Absolute cell abundances → Cell2location
    │
    └── Map scRNA-seq to spatial + gene imputation → Tangram
```

---

## Quick Comparison

### Deconvolution Methods

| Feature | DestVI | Stereoscope | Cell2location |
|---------|--------|-------------|---------------|
| Output | Proportions + gamma | Proportions | Absolute abundances |
| Cell state variation | Yes (gamma values) | No | No |
| Uncertainty quantification | Yes | Limited | Yes (posterior) |
| Training time | Medium | Fast | Slow |
| Memory usage | Medium | Low | High |

### When to Use Each Deconvolution Method

- **DestVI**: Best when you need both proportions AND continuous cell state information
- **Stereoscope**: Best for straightforward proportion estimation, computationally efficient
- **Cell2location**: Best when absolute cell counts matter, or for publication-quality uncertainty estimates

---

## Common Workflow Components

### Required Imports

```python
import numpy as np
import scanpy as sc
import scvi
import matplotlib.pyplot as plt
import torch

scvi.settings.seed = 0
torch.set_float32_matmul_precision("high")
```

### Data Loading Patterns

```python
# Visium from Space Ranger
adata = sc.read_visium("path/to/spaceranger/outs")

# Generic h5ad
adata = sc.read_h5ad("path/to/data.h5ad")

# 10x Xenium
adata = sc.read_h5ad("path/to/xenium_data.h5ad")
```

### Standard Preprocessing

```python
# Ensure raw counts
if 'counts' not in adata.layers:
    adata.layers['counts'] = adata.X.copy()

# Remove mitochondrial genes (recommended for deconvolution)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
adata = adata[:, ~adata.var['mt']].copy()

# Basic QC
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
```

---

## Individual Method Workflows

### 1. ResolVI (Spatial Denoising)

**Purpose**: Correct segmentation errors and background noise in cellular-resolution spatial data.

```python
# Setup
scvi.external.RESOLVI.setup_anndata(adata, layer="counts", labels_key="cell_type")

# Train
model = scvi.external.RESOLVI(adata, semisupervised=True)
model.train(max_epochs=100)

# Get corrected expression
samples = model.sample_posterior(
    model=model.module.model_corrected,
    return_sites=["px_rate"],
    summary_fun={"median": np.median},
    num_samples=3
)
adata.layers["corrected"] = samples.loc["median", "px_rate"]
```

**See full workflow**: `/resolvi-spatial-denoising` skill

---

### 2. scVIVA (Environment Modeling)

**Purpose**: Model how cellular neighborhoods affect gene expression; identify tissue niches.

```python
# Preprocess spatial graph
scvi.external.SCVIVA.preprocessing_anndata(adata, k_nn=20,
    sample_key="sample", labels_key="cell_type", cell_coordinates_key="spatial")

# Setup and train
scvi.external.SCVIVA.setup_anndata(adata, layer="counts", batch_key="sample", ...)
model = scvi.external.SCVIVA(adata)
model.train(max_epochs=600, batch_size=512)

# Niche-aware DE
DE_results = model.differential_expression(adata, groupby="cluster",
    group1="1", group2="0", niche_mode=True)
```

**See full workflow**: `/scviva-environment-modeling` skill

---

### 3. DestVI (Deconvolution + Cell States)

**Purpose**: Estimate cell type proportions AND continuous cell state variation within types.

```python
from scvi.model import CondSCVI, DestVI

# Stage 1: Reference model
CondSCVI.setup_anndata(sc_adata, layer="counts", labels_key="cell_type")
sc_model = CondSCVI(sc_adata)
sc_model.train(max_epochs=300)

# Stage 2: Spatial model
DestVI.setup_anndata(st_adata, layer="counts")
st_model = DestVI.from_rna_model(st_adata, sc_model)
st_model.train(max_epochs=2500)

# Results
proportions = st_model.get_proportions()
gamma = st_model.get_gamma()  # Cell state variation
```

**See full workflow**: `/destvi-deconvolution` skill

---

### 4. Tangram (Spatial Mapping)

**Purpose**: Map scRNA-seq cells to spatial locations; impute genes not measured spatially.

```python
from scvi.external import Tangram
import mudata

# Create MuData
mdata = mudata.MuData({"sp": adata_sp, "sc": adata_sc})

# Setup and train
Tangram.setup_mudata(mdata, density_prior_key="density_prior", ...)
model = Tangram(mdata, constrained=True, target_count=target_count)
model.train()

# Project annotations and genes
mapper = model.get_mapper_matrix()
ct_pred = model.project_cell_annotations(adata_sc, adata_sp, mapper, labels)
gene_imputed = model.project_genes(adata_sc, adata_sp, mapper)
```

**See full workflow**: `/tangram-spatial-mapping` skill

---

### 5. Stereoscope (Simple Deconvolution)

**Purpose**: Efficient cell type proportion estimation.

```python
from scvi.external import RNAStereoscope, SpatialStereoscope

# Stage 1: Reference
RNAStereoscope.setup_anndata(sc_adata, layer="counts", labels_key="cell_type")
sc_model = RNAStereoscope(sc_adata)
sc_model.train(max_epochs=100)

# Stage 2: Spatial
SpatialStereoscope.setup_anndata(st_adata, layer="counts")
spatial_model = SpatialStereoscope.from_rna_model(st_adata, sc_model)
spatial_model.train(max_epochs=2000)

# Results
proportions = spatial_model.get_proportions()
```

**See full workflow**: `/stereoscope-deconvolution` skill

---

### 6. Cell2location (Absolute Abundances)

**Purpose**: Estimate absolute cell counts per spot with uncertainty quantification.

```python
from cell2location.models import Cell2location, RegressionModel

# Stage 1: Reference signatures
RegressionModel.setup_anndata(adata_ref, labels_key="cell_type")
ref_model = RegressionModel(adata_ref)
ref_model.train(max_epochs=250)
adata_ref = ref_model.export_posterior(adata_ref)

# Stage 2: Spatial mapping
Cell2location.setup_anndata(adata_vis, batch_key="sample")
spatial_model = Cell2location(adata_vis, cell_state_df=signatures,
    N_cells_per_location=30)
spatial_model.train(max_epochs=30000)

# Results (with uncertainty)
adata_vis = spatial_model.export_posterior(adata_vis)
abundances = adata_vis.obsm["q05_cell_abundance_w_sf"]  # Conservative estimate
```

**See full workflow**: `/cell2location-spatial-mapping` skill

---

## Visualization Best Practices

### Spatial Plots

```python
# Basic spatial plot
sc.pl.spatial(adata, color="cell_type", spot_size=30)

# Multiple features
sc.pl.spatial(adata, color=["Gene1", "Gene2", "proportion_T_cells"], ncols=3)

# With image
sc.pl.spatial(adata, color="cluster", img_key="hires", size=1.3)
```

### Comparing Methods

```python
# Side-by-side deconvolution results
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (method, data) in zip(axes, [
    ("DestVI", destvi_proportions),
    ("Stereoscope", stereo_proportions),
    ("Cell2location", c2l_abundances)
]):
    sc.pl.spatial(adata, color=data["T_cells"], ax=ax, show=False, title=method)
plt.tight_layout()
```

---

## Troubleshooting Guide

### General Issues

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| Out of memory | Large dataset | Reduce genes, batch processing |
| Poor results | Not converged | Increase epochs, check loss |
| Missing cell types | Not in reference | Add to reference data |
| Noisy proportions | Low quality data | Better QC, filtering |

### Method-Specific Issues

**DestVI/Stereoscope**: If all spots look similar, train longer (>2500 epochs)

**Cell2location**: Adjust `N_cells_per_location` based on tissue type

**Tangram**: Use better marker genes (100-200 per cell type)

**ResolVI**: Ensure spatial coordinates are properly formatted

**scVIVA**: Increase `k_nn` for broader neighborhood context

---

## References

### Tutorials
- [ResolVI](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/resolVI_tutorial.html)
- [scVIVA](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/scVIVA_tutorial.html)
- [DestVI](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/DestVI_tutorial.html)
- [Tangram](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/tangram_scvi_tools.html)
- [Stereoscope](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/stereoscope_heart_LV_tutorial.html)
- [Cell2location](https://docs.scvi-tools.org/en/1.3.3/tutorials/notebooks/spatial/cell2location_lymph_node_spatial_tutorial.html)

### Papers
- DestVI: Nature Biotechnology (2022)
- Cell2location: Nature Biotechnology (2022)
- Tangram: Nature Methods (2021)
- Stereoscope: Communications Biology (2020)

### Documentation
- [scvi-tools](https://docs.scvi-tools.org/)
- [Scanpy](https://scanpy.readthedocs.io/)
- [Squidpy](https://squidpy.readthedocs.io/)
