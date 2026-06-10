# DIAGVI — User Guide

**Class:** `scvi.external.DIAGVI`

## Overview

**DiagVI** (Diagonal multi-modal integration Variational Inference) is a deep generative model for diagonal integration of unpaired multi-modal single-cell data. Uses prior knowledge about cross-modal feature correspondences encoded in a guidance graph. Aligns modalities using Unbalanced Optimal Transport (UOT) via Sinkhorn divergence.

**Advantages:**

- Flexible two-modality integration (scRNA-seq, spatial transcriptomics, spatial proteomics)
- Full feature utilization via guidance graph
- Biologically informed alignment using prior feature correspondences
- Robust integration of modality-specific/rare populations via UOT
- Scalable to >1 million cells

**Limitations:**

- Two modalities only
- Requires prior cross-modal feature correspondence information
- May require loss weight tuning
- Effectively requires GPU

**Tutorials:**

- `tutorials/notebooks/multimodal/DiagVI_spatial_transcriptomics`
- `tutorials/notebooks/multimodal/DiagVI_spatial_proteomics`

**Extra dependencies:** `pip install scvi-tools[diagvi]` (requires `geomloss`, `torch_geometric`)

## Preliminaries

**Input:** Two expression matrices $\mathbf{X}_1 \in \mathbb{R}^{N \times G}$ and $\mathbf{X}_2 \in \mathbb{R}^{M \times P}$ from unpaired modalities.

- **Count data** (scRNA-seq): raw counts, NB likelihood recommended
- **Continuous data** (antibody-based): arcsinh-transformed + feature-wise min-max scaled, Normal likelihood recommended

**Optional:** batch annotations, cell label annotations (per modality independently).

## Model Components

1. **Modality-specific VAEs**: project each modality to shared latent space $z \in \mathbb{R}^d$
1. **Guidance graph** $\mathcal{G} = (\mathcal{V}, \mathcal{E})$: feature correspondences with weights $w_{ij} \in (0,1]$ and signs $\sigma_{ij} \in \{-1,1\}$
1. **Unbalanced Optimal Transport**: Sinkhorn divergence aligns latent distributions across modalities
1. **Classifier** (optional, semi-supervised): predicts cell type labels from latent embeddings

## Generative Process

Linear predictor: $\eta_{ng} = \alpha_{s_n,g} \mathbf{z}_n^\top \mathbf{v}_g + \beta_{s_n,g}$

**Count data (NB):**

- $\rho_{ng} = \text{softmax}(\eta_{ng})$ — normalized proportions
- $\mu_{ng} = l_n \rho_{ng}$
- $x_{ng} \sim \text{NB}(\mu_{ng}, \theta_{s_n,g})$

**Continuous data (Normal):**

- $x_{ng} \sim \mathcal{N}(\eta_{ng}, \sigma_{s_n,g}^2)$

**Supported likelihoods:** `nb`, `zinb`, `nbmixture`, `normal`, `log1pnormal`, `ziln`, `zig`

## Training Objective

Weighted sum of:

- `lam_data`: reconstruction loss per modality
- `lam_kl`: KL divergence from prior
- `lam_graph`: graph reconstruction loss (biological consistency)
- `lam_sinkhorn`: UOT alignment loss across modalities
- `lam_class`: classification loss (optional, semi-supervised)

**Tuning guidance:**

- Very different modalities (scRNA-seq + spatial proteomics): higher `lam_sinkhorn`, lower `lam_class`
- Similar modalities (scRNA-seq + spatial transcriptomics): lower `lam_sinkhorn`, higher `lam_class`
- Recommended range for both: 1–100

## Guidance Graph Creation

Three ways to specify:

1. **Automatic**: overlapping feature names across modalities (default if no graph provided)
1. **Custom DataFrame**: `mapping_df` with columns per modality, rows as feature pairs
1. **Explicit graph**: `torch_geometric.data.Data` object

```python
# Custom graph with DIAGVI.construct_custom_guidance_graph
graph = scvi.external.DIAGVI.construct_custom_guidance_graph(mapping_df=df)
```

## Tasks

### Dimensionality reduction

```python
latents = model.get_latent_representation()
adata_mod1.obsm["X_diagvi"] = latents["mod1"]
adata_mod2.obsm["X_diagvi"] = latents["mod2"]

# Joint analysis
import scanpy as sc

adata_combined = sc.concat(
    [adata_mod1, adata_mod2],
    axis=0,
    join="inner",
    label="modality",
    keys=["mod1", "mod2"],
)
sc.pp.neighbors(adata_combined, use_rep="X_diagvi")
sc.tl.umap(adata_combined)
```

### Cross-modal feature imputation

```python
imputed_protein = model.get_imputed_values(query_name="rna", query_adata=adata_rna)
adata_rna.obsm["imputed_protein"] = imputed_protein

# Counterfactual imputation under specific batch/libsize
imputed_rna = model.get_imputed_values(
    query_name="protein", reference_batch="batch_1", reference_libsize=10000
)
```

### Cell label transfer

```python
# Using DiagVI's classifier
preds = model.predict_celltype(labeled_modality="rna")
adata_protein.obs["celltype_pred"] = preds["predictions"]
adata_protein.obs["celltype_conf"] = preds["confidence"]
```

## References

- Cao, Gao (2022), *Multi-omics single-cell data integration and regulatory inference with graph-linked embedding*, Nature Biotechnology. (GLUE)
- Séjourné et al. (2023), *Sinkhorn Divergences for Unbalanced Optimal Transport*, arXiv.
- Ingelfinger et al. (2025), *CytoVI: Deep generative modeling of antibody-based single cell technologies*, bioRxiv.
- Ergen, Yosef (2025), *ResolVI - addressing noise and bias in spatial transcriptomics*, bioRxiv.
