# Integrating single-cell methylation data from different scBS-seq experiments with methylVI

---

A common problem when analyzing single-cell omics datasets across multiple experiments is the presence of batch effects (i.e., systematic variations due to differences in sequencing platform). Here we demonstrate how methylVI can be used to integrate data from different single-cell bisulfite sequencing platforms. As an example, we'll consider single-cell methylomes from the dentate gyrus region of the brain collected in ["DNA methylation atlas of the mouse brain at single-cell resolution"](https://www.nature.com/articles/s41586-020-03182-8) (Liu et al., Nature, 2021) using two sequencing protocols: snmC-seq2 and snm-3C-seq.

If you use methylVI in your work, please consider citing

* Weinberger, E. and Lee, S.I. A deep generative model of single-cell methylomic data. NeurIPS 2023 Generative AI and Biology (GenBio) Workshop.

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

## Imports and Data Loading

```python
import tempfile

import matplotlib.pyplot as plt
import mudata
import numpy as np
import pooch
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.external import METHYLVI
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

You can modify `save_dir` below to change where the data files for this tutorial are saved.

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

This dataset was preprocessed as described in the methylVI manuscript. In particular ALLC files containing methylation reads at individual cytosines were aggregated into gene body methylation features using [ALLCools](https://lhqing.github.io/ALLCools/intro.html). Due to their distinct regulatory roles, CpG methylation and CpH methylation (i.e., non-CpG methylation) were considered separately. The resulting methylation count features were stored in a `MuData` object with separate modality fields for each methylation context: `mCG` (for CpG methylation) and `mCH` for CpH methylation.

```python
mdata = mudata.read_h5mu(
    pooch.retrieve(
        url="https://exampledata.scverse.org/scvi-tools/Liu2021_batch.h5mu",
        known_hash="9fc5980fa807151ce983309af1011949fa0b2b746c13c2960f4b4768b0a3172c",
        fname="Liu2021_batch.h5mu",
        path=save_dir.name,
        progressbar=True,
    )
)
```

```python
mdata.mod
```

Within the modality-specific `AnnData` objects, the coverage (i.e., number of measured cytosines) within each gene body region for a cell can be found in the `cov` layer, while the number of methylated cytosines can be found in the `mc` layer.

```python
mdata["mCG"].layers
```

Finally, normalized methylation counts for each region (computed using the `add_mc_frac` function in ALLCools) can be found in the `AnnData` objects' `.X` fields.

```python
mdata["mCG"].X
```

Now we'll briefly explore our data. To do so, we'll follow the ALLCools workflow detailed [here](https://lhqing.github.io/ALLCools/cell_level/basic/mch_mcg_100k_basic.html) to combine information from the two methylation contexts (i.e., CpG and CpH methylation). In particular, we'll apply principal component analysis (PCA) to each modality, and then aggregate the resulting PCs.

```python
sc.tl.pca(mdata["mCG"])
sc.tl.pca(mdata["mCH"])

ch_pcs = mdata["mCH"].obsm["X_pca"]
cg_pcs = mdata["mCG"].obsm["X_pca"]

# standardize the values of PCs from both modalities
cg_pcs = cg_pcs / cg_pcs.std()
ch_pcs = ch_pcs / ch_pcs.std()

# total_pcs
total_pcs = np.hstack([ch_pcs, cg_pcs])

mdata.obsm["X_pca"] = total_pcs
```

Now we'll visualize our data with UMAP. We find that there exist clear batch effects between the two sequencing protocols, with clear separation by protocol (left) in addition to variations due to cell type differences (right).

```python
sc.pp.neighbors(mdata)
sc.tl.umap(mdata)

fig, ax = plt.subplots(1, 2, figsize=(11, 5))

sc.pl.umap(mdata, color="mCG:Platform", ax=ax[0], show=False, title="Sequencing protocol")
sc.pl.umap(mdata, color="mCG:CoarseType", ax=ax[1], show=False, title="Cell type")

plt.subplots_adjust(wspace=0.5)
```

In the next section, we'll see how methylVI can alleviate these issues.

## Prepare and run model

Before training our model, we'll use methylVI's `setup_mudata` function to prepare our `MuData` object for training.

First, we need to tell methylVI which modalities in our MuData object to consider via the `methylation_contexts` argument. Here we'll jointly model both CpG and non-CpG methylation features, so we'll set this argument to a list containing the names of both modalities. Next, methylVI directly models the total coverage and number of methylated cytosines in each region. Thus, for each modality in our `MuData` object, we need layers containing the coverage in each region (specified by `cov_layer`) and layers with the number of methylated cytosines (specified by `mc_layer`). Finally, we'll provide methylVI with a categorical covariate specifying the sequencing protocol used for each cell.


```python
METHYLVI.setup_mudata(
    mdata,
    mc_layer="mc",
    cov_layer="cov",
    methylation_contexts=["mCG", "mCH"],
    categorical_covariate_keys=["Protocol"],
    modalities={"categorical_covariate_keys": "mCG"},
)
```

```{note}
Specify the modality of each argument via the `modalities` dictionary, which maps layer/key arguments to MuData modalities. In our case, both the `mCG` and `mCH` modalities contain the all of the fields specified in the `categorical_covariate_keys` argument (i.e., `Protocol`) in their respective `.obs`, so we arbitrarily choose `mCG` here
```

Next, we declare a `METHYLVI` model object with 20 latent variables as done in the methylVI manuscript, and train our model with early stopping.

```python
model = METHYLVI(
    mdata,
    n_latent=20,
)

model.train(max_epochs=500, early_stopping=True)
```

Now that our model is trained, we'll obtain latent representations of each cell.

```python
mdata.obsm["methylVI"] = model.get_latent_representation()
```

Visualizing these representations, we find that cells now mix across protocol (left) while separating by cell type (right).

```python
sc.pp.neighbors(mdata, use_rep="methylVI")
sc.tl.umap(mdata)

fig, ax = plt.subplots(1, 2, figsize=(11, 5))

sc.pl.umap(mdata, color="mCG:Platform", ax=ax[0], show=False, title="Sequencing protocol")
sc.pl.umap(mdata, color="mCG:CoarseType", ax=ax[1], show=False, title="Cell type")

plt.subplots_adjust(wspace=0.5)
```
