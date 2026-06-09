# Joint analysis of paired and unpaired multiomic data with MultiVI

MultiVI is used for the joint analysis of scRNA and scATAC-seq datasets that were jointly profiled (multiomic / paired) and single-modality datasets (only scRNA or only scATAC). MultiVI uses the paired data as an anchor to align and merge the latent spaces learned from each individual modality.

This tutorial walks through how to read multiomic data, create a joint object with paired and unpaired data, set-up and train a MultiVI model, visualize the resulting latent space, and run differential analyses.

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import os
import tempfile

import muon
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

## Data acquisition

First we download a sample multiome dataset from 10X, which we have preprocessed in a way similar to what is demonstrated in the scvi-tools [preprocessing tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/use_cases/preprocessing.html#multiome) (Note: the exact dataset was not used in the preprocessing tutorial). We'll use this throughout this tutorial.
Importantly, MultiVI assumes that there are shared features between the datasets. This is trivial for gene expression datasets, which generally use the same set of genes as features. For ATAC-seq peaks, this is less trivial, and often requires preprocessing steps with other tools to get all datasets to use a shared set of peaks. That can be achieved with tools like SnapATAC, ArchR, and CellRanger in the case of 10X data.

```{important}
MultiVI requires the datasets to use shared features. scATAC-seq datasets need to be processed to use a shared set of peaks.
```

```{note}
The original 10X dataset has been modified to remove some modality specific data such that 1/3 of the cells contain just gene expression data, 1/3 contain both gene expression and peaks data, and the remaining 1/3 of cells contain just peaks. The modification was done in order to demonstrate MultiVI's ability to mix multimodal and single-modal data. The dataset has 12012 cells total
```

Below we download the already preprocessed dataset.

```python
# download preprocessed dataset
mdata_path = os.path.join(save_dir.name, "pbmc_10k_preprocessed.h5mu")

# direct download URL
url = "https://exampledata.scverse.org/scvi-tools/pbmc_10k_preprocessed.h5mu"

# Download only if file doesn't already exist
if not os.path.exists(mdata_path):
    print(f"Downloading MuData file to {mdata_path}...")
    r = requests.get(url)
    with open(mdata_path, "wb") as f:
        f.write(r.content)

# Load the MuData object
mdata = muon.read_h5mu(mdata_path)
```

```python
# alternatively load the local preprocessed multivi data
# mdata_path = "scvi-tutorials/use_cases/pbmc_multi_preprocessed.h5mu" #preprocessed file
# Load the MuData object
# mdata = muon.read_h5mu(mdata_path)
```

```{important}
MultiVI requires the features to be ordered so that genes appear before genomic regions. This must be enforced by the user.
```

## Setup and Training MultiVI

We can now set up and train the MultiVI model!

First, we need to setup the Anndata object using the `setup_mudata` function. At this point we specify any batch annotation that the model would account for.
**Importantly**, the main batch annotation, specific by `batch_key`, should correspond to the modality of the cells.

Other batch annotations (e.g if there are multiple ATAC batches) should be provided using the `categorical_covariate_keys`.

The actual values of categorical covariates (include `batch_key`) are not important, as long as they are different for different samples.
I.e it is not important to call the expression-only samples "expression", as long as they are called something different than the multi-modal and accessibility-only samples.

```{important}
MultiVI requires the main batch annotation to correspond to the modality of the samples. Other batch annotation, such as in the case of multiple RNA-only batches, can be specified using `categorical_covariate_keys`.
```

```python
mdata
```

```python
scvi.model.MULTIVI.setup_mudata(
    mdata,
    modalities={
        "rna_layer": "rna_subset",
        "atac_layer": "atac_subset",
    },
)
```

When creating the object, we need to specify how many of the features are genes, and how many are genomic regions. This is so MultiVI can determine the exact architecture for each modality.

```python
model = scvi.model.MULTIVI(
    mdata,
    n_genes=len(mdata.mod["rna_subset"].var),
    n_regions=len(mdata.mod["atac_subset"].var),
)

model.view_anndata_setup()
```

```python
# For our sparse matrices, we want CSR rather than CSC as training will be faster
# We convert here since our downloaded dataset uses CSC (might not be the case for other datasets)
mdata.mod["rna_subset"].X = mdata.mod["rna_subset"].X.tocsr()
mdata.mod["atac_subset"].X = mdata.mod["atac_subset"].X.tocsr()
mdata.update()
```

```python
model.train()
```

## Save and Load MultiVI models

Saving and loading models is similar to all other scvi-tools models, and is very straight forward:

```python
model_dir = os.path.join(save_dir.name, "multivi_pbmc10k")

model.save(model_dir, overwrite=True)
```

```python
model = scvi.model.MULTIVI.load(model_dir, adata=mdata)
```

```python
mdata = model.adata
```

```python
model = scvi.model.MULTIVI.load(model_dir, adata=mdata)
```

```python
mdata
```

## Extracting and visualizing the latent space

We can now use the `get_latent_representation` to get the latent space from the trained model, and visualize it using scanpy functions:

```python
# Below we an cell annotations for modality, so we can color the UMAP

MULTIVI_LATENT_KEY = "X_multivi"

mdata.obsm[MULTIVI_LATENT_KEY] = model.get_latent_representation()
sc.pp.neighbors(mdata, use_rep=MULTIVI_LATENT_KEY)
sc.tl.umap(mdata, min_dist=0.2)

n = mdata.n_obs // 3

# initialize the column first
mdata.obs["modality"] = ""

# set modality of first third to rna
mdata.obs.iloc[:n, mdata.obs.columns.get_loc("modality")] = "expression"

# set modality of second third to both
mdata.obs.iloc[n : 2 * n, mdata.obs.columns.get_loc("modality")] = "paired"

# set modality of last third to atac
mdata.obs.iloc[2 * n :, mdata.obs.columns.get_loc("modality")] = "accessibility"

sc.pl.umap(mdata, color="modality")
```

## Impute missing modalities

In a well-mixed space, MultiVI can seamlessly impute the missing modalities for single-modality cells.
First, imputing expression and accessibility is done with `get_normalized_expression` and `get_normalized_accessibility`, respectively.

We'll demonstrate this by imputing gene expression for all cells in the dataset (including those that are ATAC-only cells):

```python
imputed_expression = model.get_normalized_expression()
imputed_expression
```

```python
imputed_accesssibility = model.get_normalized_accessibility()
imputed_accesssibility
```

```python
model.differential_accessibility(groupby="modality", group1="accessibility").sort_values("prob_da")
```

We can demonstrate this on some known marker genes:

First, T-cell marker CD3.

```python
mdata.mod["rna_subset"].var.index
```

```python
np.where(mdata.mod["rna_subset"].var.index == "CD3G")
```

```python
gene_idx = np.where(mdata.mod["rna_subset"].var.index == "CD3G")[0]
mdata.obs["CD3G_imputed"] = imputed_expression.iloc[:, gene_idx]
sc.pl.umap(mdata, color="CD3G_imputed")
```

Next, NK-Cell marker gene NCAM1 (CD56):

```python
gene_idx = np.where(mdata.var.index == "NCAM1")[0]
mdata.obs["NCAM1_imputed"] = imputed_expression.iloc[:, gene_idx]
sc.pl.umap(mdata, color="NCAM1_imputed")
```

Finally, B-Cell Marker MS4A1:

```python
gene_idx = np.where(mdata.var.index == "MS4A1")[0]
mdata.obs["MS4A1_imputed"] = imputed_expression.iloc[:, gene_idx]
sc.pl.umap(mdata, color="MS4A1_imputed")
```

All three marker genes clearly identify their respective populations. Importantly, the imputed gene expression profiles are stable and consistent within that population, **even though many of those cells only measured the ATAC profile of those cells**.

Finaly lets see the most lowly expressed region as was found in the DE above:

```python
region_idx = np.where(mdata.var.index == "chr20:29124775-29125699")[0] - 4000
mdata.obs["chr20:29124775-29125699_imputed"] = imputed_accesssibility.iloc[:, region_idx]
sc.pl.umap(mdata, color="chr20:29124775-29125699_imputed")
```
