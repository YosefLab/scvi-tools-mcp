---
name: cellassign-annotation
description: This skill should be used for assigning cell types to single-cell RNA-seq data using known marker genes with CellAssign. It applies when users have a binary marker gene matrix defining cell types, want probabilistic cell type assignments, or need to annotate cells without labeled training data. Typical requests include "annotate cells using markers", "assign cell types with CellAssign", "use marker matrix for annotation", or "probabilistic cell type assignment".
---

# Cell Type Annotation with CellAssign

Automated workflow for assigning cell types to single-cell RNA-seq data using prior knowledge of marker genes with the CellAssign probabilistic model.

## When to Use This Skill

Use when users:
- Have well-defined cell types with known marker genes
- Want to avoid manual labeling of training data
- Have a binary marker gene matrix (genes × cell types)
- Need probabilistic confidence scores for assignments
- Are analyzing tissues with established cell type definitions (e.g., tumor microenvironment)

**CellAssign vs Other Methods:**
- Use **CellAssign** when you have a marker gene matrix and want probabilistic assignments
- Use **seed labeling** when you want to use markers to create training seeds for scANVI
- Use **label transfer** when you have a fully annotated reference dataset
- Use **CellTypist** when you want to use pre-trained models

**Key difference from seed labeling:** CellAssign directly uses marker information in a probabilistic model, while seed labeling uses markers to select training examples for a separate classifier.

**Supported input formats:**
- `.h5ad` files (AnnData format) with raw counts
- Marker gene matrix as CSV or DataFrame (binary: 1=marker, 0=not marker)

**Prerequisites:**
- Single-cell expression data with raw counts
- Binary marker gene matrix (rows=genes, columns=cell types)
- Matching gene names between data and marker matrix

## Approach 1: Complete CellAssign Pipeline (Recommended)

For standard cell type annotation, use the convenience script `scripts/cellassign_analysis.py`:

```bash
# Basic annotation with marker matrix
python3 scripts/cellassign_analysis.py \
    --input data.h5ad \
    --markers marker_matrix.csv \
    --output-dir cellassign_results

# With specific layer for counts
python3 scripts/cellassign_analysis.py \
    --input data.h5ad \
    --markers marker_matrix.csv \
    --layer counts \
    --output-dir cellassign_results

# With custom training parameters
python3 scripts/cellassign_analysis.py \
    --input data.h5ad \
    --markers marker_matrix.csv \
    --max-epochs 400 \
    --early-stopping
```

**When to use this approach:**
- Standard cell type annotation with known markers
- Tumor microenvironment analysis
- Any tissue with established marker definitions

**Requirements:** scvi-tools, anndata, scanpy, numpy, pandas, torch

**Parameters:**

Core parameters:
- `--input` - Path to input .h5ad file with expression data (required)
- `--markers` - Path to marker gene matrix CSV (required)
- `--output-dir` - Output directory (default: `cellassign_results`)
- `--layer` - Layer containing count data (default: uses .X)

Size factor options:
- `--size-factor-key` - Existing size factor column in obs
- `--compute-size-factors` - Compute size factors automatically (default)

Training parameters:
- `--max-epochs` - Maximum training epochs (default: 400)
- `--early-stopping` - Enable early stopping (recommended)

Output options:
- `--confidence-threshold` - Minimum probability for assignment (default: 0.0)
- `--save-model` - Save trained CellAssign model

Use `--help` to see all options.

**Outputs:**

All files saved to `cellassign_results/` (or `--output-dir`):
- `cell_type_assignments.csv` - Predicted cell types for all cells
- `prediction_probabilities.csv` - Full probability matrix
- `assignment_umap.png` - UMAP colored by cell type
- `probability_heatmap.png` - Clustered heatmap of probabilities
- `confidence_distribution.png` - Histogram of prediction confidence
- `training_history.png` - ELBO loss over training
- `annotated_data.h5ad` - Input data with predictions added
- `cellassign_model/` - Saved model (if --save-model)

### Marker Gene Matrix Format

The marker matrix should be a binary CSV file:

```csv
,T_cell,B_cell,Monocyte,NK_cell
CD3D,1,0,0,0
CD3E,1,0,0,0
CD4,1,0,0,0
CD8A,1,0,0,0
CD19,0,1,0,0
MS4A1,0,1,0,0
CD14,0,0,1,0
LYZ,0,0,1,0
FCGR3A,0,0,1,1
NKG7,0,0,0,1
GNLY,0,0,0,1
```

- Rows: Gene names (must match expression data)
- Columns: Cell type names
- Values: 1 if gene is a marker for the cell type, 0 otherwise
- A gene can be a marker for multiple cell types

### Workflow Steps

The script performs:

1. **Data Loading** - Load expression data and marker matrix
2. **Gene Matching** - Subset to genes present in both
3. **Size Factor Calculation** - Compute library size normalization
4. **Model Setup** - Configure CellAssign with marker matrix
5. **Training** - Fit probabilistic model
6. **Prediction** - Get cell type probabilities
7. **Assignment** - Assign types based on maximum probability
8. **Visualization** - Generate diagnostic plots

## Approach 2: Modular Building Blocks (For Custom Workflows)

For custom analysis workflows, use the modular functions from `scripts/cellassign_core.py`:

```python
import anndata as ad
import pandas as pd
import sys
sys.path.append('scripts/')
from cellassign_core import (
    load_marker_matrix,
    compute_size_factors,
    subset_to_markers,
    setup_cellassign,
    train_cellassign,
    predict_cell_types,
    get_prediction_probabilities
)

adata = ad.read_h5ad('data.h5ad')
marker_matrix = load_marker_matrix('markers.csv')
# ... custom workflow
```

**When to use this approach:**
- Need custom preprocessing
- Integration with larger pipelines
- Custom visualization or evaluation
- Iterative marker refinement

**Available utility functions:**

From `cellassign_core.py`:
- `load_marker_matrix(path)` - Load and validate marker CSV
- `create_marker_matrix(markers_dict)` - Create matrix from dict
- `compute_size_factors(adata)` - Calculate library size factors
- `subset_to_markers(adata, marker_matrix)` - Subset to marker genes
- `setup_cellassign(adata, marker_matrix, size_factor_key)` - Register for CellAssign
- `train_cellassign(adata, marker_matrix, max_epochs)` - Train model
- `predict_cell_types(model)` - Get hard assignments
- `get_prediction_probabilities(model)` - Get soft probabilities
- `filter_by_confidence(predictions, probabilities, threshold)` - Apply confidence filter
- `save_model(model, path)` / `load_model(path, adata)` - Model persistence

**Example custom workflows:**

**Example 1: Basic annotation**
```python
import anndata as ad
from cellassign_core import (
    load_marker_matrix,
    compute_size_factors,
    subset_to_markers,
    train_cellassign,
    predict_cell_types
)

# Load data
adata = ad.read_h5ad('data.h5ad')
marker_matrix = load_marker_matrix('markers.csv')

# Prepare data
adata = compute_size_factors(adata)
adata_subset = subset_to_markers(adata, marker_matrix)

# Train and predict
model = train_cellassign(adata_subset, marker_matrix)
predictions = predict_cell_types(model)
adata.obs['celltype'] = predictions
```

**Example 2: Create marker matrix from dictionary**
```python
from cellassign_core import create_marker_matrix

markers = {
    'T_cell': ['CD3D', 'CD3E', 'CD4', 'CD8A'],
    'B_cell': ['CD19', 'MS4A1', 'CD79A'],
    'Monocyte': ['CD14', 'LYZ', 'S100A8'],
    'NK_cell': ['NKG7', 'GNLY', 'NCAM1']
}

marker_matrix = create_marker_matrix(markers)
# Returns DataFrame with genes as rows, cell types as columns
```

**Example 3: Annotation with confidence filtering**
```python
# After training...
predictions = predict_cell_types(model)
probabilities = get_prediction_probabilities(model)

# Filter low-confidence assignments
confidence = probabilities.max(axis=1)
high_conf_mask = confidence > 0.8

adata.obs['celltype'] = predictions
adata.obs.loc[~high_conf_mask, 'celltype'] = 'Uncertain'
adata.obs['assignment_confidence'] = confidence
```

**Example 4: Iterative marker refinement**
```python
# Initial annotation
model = train_cellassign(adata_subset, marker_matrix)
probs = get_prediction_probabilities(model)

# Find ambiguous cells (low confidence)
confidence = probs.max(axis=1)
ambiguous = confidence < 0.5

# Examine these cells to identify missing markers
ambiguous_adata = adata[ambiguous]
# ... analyze and add new markers

# Retrain with refined markers
model2 = train_cellassign(adata_subset, refined_marker_matrix)
```

## Key Parameters Explained

### Size Factors

CellAssign requires size factors for library size normalization:

```python
# Size factor = total counts / mean(total counts)
size_factor = adata.X.sum(1) / np.mean(adata.X.sum(1))
```

**Important:** Calculate size factors BEFORE subsetting to marker genes!

### Marker Matrix Requirements

| Requirement | Description |
|-------------|-------------|
| Binary values | Only 0 and 1 |
| Gene names | Must match expression data exactly |
| Cell types | Column names become predicted labels |
| Specificity | More specific markers = better results |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_epochs` | 400 | Maximum training iterations |
| `early_stopping` | True | Stop when validation loss plateaus |

## Best Practices

1. **Marker Selection**
   - Use 3-10 markers per cell type
   - Choose specific, well-established markers
   - Avoid housekeeping genes
   - Validate markers are expressed in your data

2. **Size Factors**
   - Always compute before gene subsetting
   - Use total UMI counts (not normalized)
   - Store in `adata.obs` for reproducibility

3. **Gene Matching**
   - Ensure gene name format matches (symbols vs Ensembl)
   - Check for case sensitivity issues
   - Verify sufficient overlap exists

4. **Model Training**
   - Use early stopping to prevent overfitting
   - Monitor ELBO loss for convergence
   - Check training history plot

5. **Result Interpretation**
   - Examine probability distributions
   - Flag low-confidence assignments
   - Validate with known marker expression
   - Use UMAP to check spatial consistency

6. **Common Issues**
   - All cells assigned one type: Check marker specificity
   - Low confidence: May need more/better markers
   - Missing types: Verify markers are expressed

## Comparison with Other Methods

| Method | Input | Probabilistic | Training Data |
|--------|-------|---------------|---------------|
| CellAssign | Marker matrix | Yes | Not required |
| Seed Labeling | Marker genes | Yes | Auto-selected |
| Label Transfer | Reference data | Yes | Labeled reference |
| CellTypist | Pre-trained | Yes | Pre-built models |
| Manual | Clustering | No | Expert annotation |

**Use CellAssign when:**
- You have well-defined marker genes
- You want probabilistic confidence scores
- No labeled training data available
- Tissue has established cell type definitions

## Reference Materials

For detailed methodology and troubleshooting, see `references/cellassign_guide.md`. This provides:
- Mathematical foundations of CellAssign
- Marker gene selection strategies
- Troubleshooting common issues
- Comparison with related methods

## Next Steps After Annotation

Typical downstream analysis:
- Validate predictions with marker expression plots
- Analyze cell type proportions across samples
- Differential expression between cell types
- Cell-cell interaction analysis
- Export annotations for further analysis
