# Isolating perturbation-induced variations with contrastiveVI

Perturb-seq is a platform for conducting large scale CRISPR-mediated gene perturbation screens in single-cells. A major goal of Perturb-seq experiments is to gain new insights as to gene functions (e.g. pathway membership) and the relationships between different genes. Unfortunately, analyzing the effects of CRISPR perturbation in Perturb-seq experiments can be confounded by sources of variation shared with control cells (e.g. cell-cycle-related variations).

Here we illustrate how contrastiveVI's explicit deconvolution of shared and perturbed-cell-specific variations can overcome such challenges in the analysis of Perturb-seq data. For this case study, we'll consider data from a large-scale Perturb-seq experiment originally collected in [Norman et al.](https://www.science.org/doi/10.1126/science.aax4438) In this study the authors assessed the effects of 284 different CRISPR-mediated perturbations on the growth of K562 cells, where each perturbation induced the overexpression of a single gene or a pair of genes.

If you use contrastiveVI in your work, please consider citing:

- Weinberger, E., Lin, C. & Lee, SI. Isolating salient variations of interest in single-cell data with contrastiveVI. Nature Methods 20, 1336–1345 (2023).

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

## Imports and data loading

```python
import os
import tempfile

import numpy as np
import requests
import scanpy as sc
import scvi
import seaborn as sns
import torch
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```{note}
You can modify `save_dir` below to change where the data files for this tutorial are saved.
```

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

This dataset was filtered as described in the contrastiveVI manuscript (low quality cells filtered out, high variable gene selection, etc.). Normalized, log-transformed values can  be found in `adata.X`, while raw counts can be found in `adata.layers['count']`.

```python
adata_path = os.path.join(save_dir.name, "norman_2019.h5ad")

adata = sc.read(
    adata_path,
    backup_url="https://exampledata.scverse.org/scvi-tools/norman_2019_adata.h5ad",
)
adata.var_names = adata.var["gene_name"]

del adata.raw  # Save memory to stay within Colab free tier limits
```

As an extra preprocessing step, we'll calculate cell cycle labels to be used later in our analysis:

```python
def get_cell_cycle_genes() -> list:
    # Canonical list of cell cycle genes
    url = "https://raw.githubusercontent.com/scverse/scanpy_usage/master/180209_cell_cycle/data/regev_lab_cell_cycle_genes.txt"
    cell_cycle_genes = requests.get(url).text.split("\n")[:-1]
    return cell_cycle_genes
```

```python
cell_cycle_genes = get_cell_cycle_genes()

s_genes = cell_cycle_genes[:43]
g2m_genes = cell_cycle_genes[43:]
cell_cycle_genes = [x for x in cell_cycle_genes if x in adata.var_names]

sc.tl.score_genes_cell_cycle(adata, s_genes=s_genes, g2m_genes=g2m_genes, use_raw=False)
```

Now let's briefly take a look at our data. In their original work Norman et al. labeled groups of perturbations with similar induced gene programs (e.g. inducing expression of megakaryocyte markers). Thus, we would expect perturbed cells to separate by these program labels (found in `adata.obs['gene_program']`).

However, contrary to our prior knowledge, we find that perturbed cells do not clearly separate by our gene program labels, and instead separate by confounding variations shared with controls, such as cell cycle phase.

```python
perturbed_adata = adata[adata.obs["gene_program"] != "Ctrl"]  # Only consider perturbed cells

sc.pp.neighbors(perturbed_adata)
sc.tl.umap(perturbed_adata)
sc.pl.umap(perturbed_adata, color=["phase", "gene_program"])
```

In the next section, we'll see how to use contrastiveVI to alleviate such issues

## Prepare and run model

```python
scvi.external.ContrastiveVI.setup_anndata(adata, layer="count")
```

contrastiveVI explicitly isolates perturbed-cell-specific variations from variations shared with controls by assuming that the data is generated from two sets of latent variables. The first, called the **_background_** variables, are shared across perturbed and control cells. The second, called the **_salient_** variables, are only active in perturbed cells and are fixed at 0 for controls.

Because contrastiveVI uses a single decoder network to reconstruct all cells, the background variables are naturally encouraged during training to capture patterns shared across all cells, while the salient variables instead pick up the remaining perturbed-cell-specific variations (see the contrastiveVI manuscript for additional details).

```python
contrastive_vi_model = scvi.external.ContrastiveVI(
    adata, n_salient_latent=10, n_background_latent=10, use_observed_lib_size=False
)
```

Before training, we thus need to tell contrastiveVI which cells are only generated from background (i.e., control cells), and which cells are our target (i.e., perturbed cells).

```python
background_indices = np.where(adata.obs["gene_program"] == "Ctrl")[0]
target_indices = np.where(adata.obs["gene_program"] != "Ctrl")[0]
```

```python
contrastive_vi_model.train(
    background_indices=background_indices,
    target_indices=target_indices,
    early_stopping=True,
    max_epochs=500,
)
```

Now let's get the salient representation of our perturbed cells.

```python
perturbed_adata.obsm["salient_rep"] = contrastive_vi_model.get_latent_representation(
    perturbed_adata, representation_kind="salient"
)
```

Visualizing these salient representations, we find that they're invariant to the confounding cell-cycle-related variations and now separate clearly by gene program label as desired.

```python
sc.pp.neighbors(perturbed_adata, use_rep="salient_rep")
sc.tl.umap(perturbed_adata)
sc.pl.umap(perturbed_adata, color=["phase", "gene_program"])
```
