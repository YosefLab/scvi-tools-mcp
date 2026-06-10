from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from scvi_tools_mcp.mcp import mcp
from scvi_tools_mcp.tools import utils
from scvi_tools_mcp.tools._constants import MODEL_NAMES

WORKFLOW_TEMPLATES: dict[str, dict[str, str]] = {
    "batch_integration": {
        "scvi": """# Batch Integration with scVI

```python
import scvi
import scanpy as sc

# 1. Load your data (must be raw counts)
adata = sc.read_h5ad("your_data.h5ad")

# 2. Basic QC filter (adjust thresholds to your data)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 3. Setup AnnData for scVI (raw counts must be in adata.X)
scvi.model.SCVI.setup_anndata(adata, batch_key="batch")

# 4. Create and train model
model = scvi.model.SCVI(adata, n_latent=30)
model.train(max_epochs=400, early_stopping=True)

# 5. Get batch-corrected latent representation
adata.obsm["X_scVI"] = model.get_latent_representation()

# 6. Downstream: clustering on corrected space
sc.pp.neighbors(adata, use_rep="X_scVI")
sc.tl.umap(adata)
sc.tl.leiden(adata)

# 7. Save model
model.save("scvi_model/")
```""",
        "scanvi": """# Batch Integration + Label Transfer with SCANVI

```python
import scvi
import scanpy as sc

# adata.obs['cell_type'] must have labels; use 'Unknown' for unlabeled cells
scvi.model.SCVI.setup_anndata(adata, batch_key="batch", labels_key="cell_type")
vae = scvi.model.SCVI(adata, n_latent=30)
vae.train(max_epochs=400)

scanvae = scvi.model.SCANVI.from_scvi_model(vae, unlabeled_category="Unknown")
scanvae.train(max_epochs=200)

adata.obsm["X_scANVI"] = scanvae.get_latent_representation()
adata.obs["predicted_label"] = scanvae.predict()
```""",
    },
    "cell_type_annotation": {
        "scanvi": """# Cell Type Annotation with SCANVI

```python
import scvi

# adata.obs['cell_type'] must have labels for some cells, 'Unknown' for unlabeled
scvi.model.SCVI.setup_anndata(adata, batch_key="batch", labels_key="cell_type")
vae = scvi.model.SCVI(adata, n_latent=30)
vae.train(max_epochs=400)

scanvae = scvi.model.SCANVI.from_scvi_model(vae, unlabeled_category="Unknown")
scanvae.train(max_epochs=200)

adata.obs["predicted_label"] = scanvae.predict()
adata.obs["confidence"] = scanvae.predict(soft=True).max(axis=1)
```""",
    },
    "deconvolution": {
        "destvi": """# Spatial Deconvolution with DestVI

```python
import scvi

# Step 1: Train CondSCVI on single-cell reference
scvi.external.CondSCVI.setup_anndata(sc_adata, labels_key="cell_type")
sc_model = scvi.external.CondSCVI(sc_adata, weight_obs=True)
sc_model.train(max_epochs=300)

# Step 2: Train DestVI on spatial data
scvi.external.DestVI.setup_anndata(sp_adata)
sp_model = scvi.external.DestVI.from_rna_model(sp_adata, sc_model)
sp_model.train(max_epochs=2500)

sp_adata.obsm["proportions"] = sp_model.get_proportions()
```""",
    },
    "multimodal_integration": {
        "totalvi": """# Multimodal Integration (RNA + Protein) with TotalVI

```python
import scvi

# adata.obsm['protein_expression'] must contain raw protein counts
scvi.model.TOTALVI.setup_anndata(
    adata,
    batch_key="batch",
    protein_expression_obsm_key="protein_expression"
)
model = scvi.model.TOTALVI(adata)
model.train(max_epochs=400)

# Get latent representation and normalized expression
adata.obsm["X_totalVI"] = model.get_latent_representation()
rna_norm, protein_norm = model.get_normalized_expression()
```""",
    },
    "chromatin_accessibility": {
        "peakvi": """# Chromatin Accessibility with PeakVI

```python
import scvi

# adata.X must be binary (0/1) accessibility matrix
scvi.model.PEAKVI.setup_anndata(adata, batch_key="batch")
model = scvi.model.PEAKVI(adata)
model.train(max_epochs=500)

adata.obsm["X_PeakVI"] = model.get_latent_representation()
accessibility = model.get_accessibility_estimates()
```""",
    },
}

DOWNSTREAM_GUIDES: dict[str, dict[str, str]] = {
    "de": {
        "scvi": """# Differential Expression with scVI

```python
# Cluster A vs cluster B
de_df = model.differential_expression(
    adata,
    groupby="leiden",
    group1="0",
    group2="1",
)
# Key columns: lfc_mean (log fold change), is_de_fdr_0.05 (True if DE at 5% FDR)
significant = de_df[de_df["is_de_fdr_0.05"]]
top_genes = significant.sort_values("lfc_mean", ascending=False).head(10)
```""",
        "default": "Use `model.differential_expression()`. See get_api_reference(symbol='SCVI') for full params.",
    },
    "embedding": {
        "default": """# Getting the Latent Embedding

```python
Z = model.get_latent_representation()  # shape: (n_cells, n_latent)
adata.obsm["X_latent"] = Z

import scanpy as sc
sc.pp.neighbors(adata, use_rep="X_latent")
sc.tl.umap(adata)
sc.pl.umap(adata, color=["batch", "cell_type"])
```""",
    },
    "clustering": {
        "default": """# Clustering on scVI Latent Space

```python
import scanpy as sc

adata.obsm["X_scVI"] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=30)
sc.tl.leiden(adata, resolution=0.5)
sc.tl.umap(adata)
sc.pl.umap(adata, color=["leiden", "batch"])
```""",
    },
    "transfer_labels": {
        "default": """# Label Transfer with SCANVI

```python
# After training SCANVI:
adata.obs["predicted_label"] = scanvae.predict()
adata.obs["confidence"] = scanvae.predict(soft=True).max(axis=1)
# Filter high-confidence predictions
high_conf = adata[adata.obs["confidence"] > 0.9]
```""",
    },
    "deconvolution": {
        "default": """# Getting Deconvolution Proportions

```python
# After training DestVI or Stereoscope:
sp_adata.obsm["proportions"] = sp_model.get_proportions()
# proportions shape: (n_spots, n_cell_types)
```""",
    },
}


class WorkflowResult(BaseModel):
    content: str | None = None
    truncated: bool = False
    error: str | None = None


@mcp.tool()
def get_workflow_template(
    task: Literal[
        "batch_integration",
        "dimensionality_reduction",
        "differential_expression",
        "cell_type_annotation",
        "deconvolution",
        "spatial_mapping",
        "chromatin_accessibility",
        "multimodal_integration",
        "reference_mapping",
        "perturbation_modeling",
    ],
    model_name: MODEL_NAMES | None = None,
) -> WorkflowResult:
    """Get a complete, runnable code template for a scvi-tools analysis task.

    Returns a step-by-step commented Python script the user can adapt to their data.
    The code is returned as a string — it is NOT executed. Always show the user this
    template after recommending a model.

    Args:
        task: The analysis task (e.g. 'batch_integration', 'cell_type_annotation').
        model_name: Optional specific model. If None, uses the recommended default for the task.
    """
    try:
        task_templates = WORKFLOW_TEMPLATES.get(task, {})
        template = None
        if model_name and model_name in task_templates:
            template = task_templates[model_name]
        elif "default" in task_templates:
            template = task_templates["default"]
        elif task_templates:
            template = next(iter(task_templates.values()))
        if template is None:
            knowledge_dir = utils.get_knowledge_dir()
            ug_files = list((knowledge_dir / "user_guide").glob("*.md"))
            lines = [
                f"# Workflow Template — {task}",
                "",
                f"No pre-built template for task='{task}'. Refer to these guides:",
                "",
            ] + [f"- {f.stem}" for f in ug_files[:5]]
            lines.append("\nUse search_tutorials(query='" + task + "') to find relevant notebooks.")
            template = "\n".join(lines)
        result = utils.truncate(template)
        return WorkflowResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return WorkflowResult(error=str(e))


@mcp.tool()
def get_downstream_guide(
    model_name: MODEL_NAMES,
    task: Literal["de", "embedding", "clustering", "deconvolution", "transfer_labels"],
) -> WorkflowResult:
    """Get a guide and code snippet for downstream analysis after training a scvi-tools model.

    Use this after a model is trained to show the user how to extract results.
    Common tasks: differential expression (de), latent embedding, clustering,
    deconvolution, and label transfer.

    Args:
        model_name: The trained scvi-tools model name.
        task: The downstream analysis task.
    """
    try:
        task_guides = DOWNSTREAM_GUIDES.get(task, {})
        guide = task_guides.get(model_name) or task_guides.get("default")
        if guide is None:
            return WorkflowResult(
                error=f"No downstream guide for task='{task}' with model='{model_name}'. "
                f"Try search_knowledge(query='{task} {model_name}')."
            )
        result = utils.truncate(guide)
        return WorkflowResult(content=result.content, truncated=result.truncated)
    except Exception as e:
        return WorkflowResult(error=str(e))
