# Advanced Tutorial: Multi-Panel Integration and Downstream Analysis with CytoVI

In this tutorial, we demonstrate advanced functionality of **CytoVI**, a deep generative model for protein expression measurements from technologies such as flow cytometry, mass cytometry, or CITE-seq. Building on the quick start tutorial, we now explore how CytoVI can be used to integrate multiple cytometry panels, impute missing markers, transfer annotations between datasets, and uncover biological differences through differential expression and abundance analysis.

If you are new to CytoVI or unfamiliar with data loading, preprocessing, or training the model, we recommend starting with the [quick start tutorial](./CytoVI_batch_correction_tutorial.ipynb) where these fundamental steps are introduced in detail. In this tutorial, we will work with preprocessed and partially annotated data to focus on the advanced use cases of the model.

Specifically, we analyze conventional flow cytometry data of tumor-infiltrating T cells obtained from patients with B-cell non-Hodgkin lymphoma (BNHL). These samples were profiled using two distinct antibody panels, which share a subset of common markers. Using CytoVI, we will integrate both panels into a shared representation space, infer missing marker expression, and perform downstream biological analysis to gain insights into T cell heterogeneity across patients.

Plan for this tutorial:

1. Load and inspect preprocessed data
2. Train a CytoVI model that integrates both antibody panels
3. Visualize the joint latent space and evaluate panel integration
4. Impute non-overlapping protein markers and assess imputation quality
5. Automatically annotate immune cell types via label transfer
6. Quantify differential protein expression across clusters
7. Detect disease-associated T cell states using label-free differential abundance analysis

```python
# Install from GitHub for now
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import os
import random
import tempfile

import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import scanpy as sc  # type: ignore
import scvi
import seaborn as sns  # type: ignore
import torch  # type: ignore
from rich import print  # type: ignore
from scipy.stats import mannwhitneyu
from scvi.external import cytovi  # type: ignore
from sklearn.cluster import KMeans  # type: ignore

os.environ["SCIPY_ARRAY_API"] = "1"

sc.set_figure_params(figsize=(4, 4))

scvi.settings.seed = 0
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
print("Last run with scvi-tools version:", scvi.__version__)
```

## Loading the data

In this tutorial, we will work with a curated, lightweight subset of flow cytometry data from the BNHL study by Roider et al. 2024 (Nature Cell Biology, https://doi.org/10.1038/s41556-024-01358-2). The dataset includes flow cytometry measurements of T cells from 33 donors across two distinct antibody panels, each profiling 12 protein markers along with morphological features such as forward and side scatter (FSC and SSC). Samples were acquired across four independent experimental batches. For ease of use, the data have been preprocessed to correct for fluorescent spillover, restricted to live single-cell events, and transformed using a hyperbolic arcsin transformation, scaled and subsampled to ~5000 cells per panel. We will access the dataset as preprocessed .h5ad files. For demonstration purposes data from one of the panels comes with cell type annotations.

```python
temp_dir_obj = tempfile.TemporaryDirectory()

adata_p1_path = os.path.join(temp_dir_obj.name, "Roider_et_al_BNHL_panel1.h5ad")
adata_p1 = sc.read(
    adata_p1_path,
    backup_url="https://exampledata.scverse.org/scvi-tools/Roider_et_al_BNHL_panel1.h5ad",
)

adata_p2_path = os.path.join(temp_dir_obj.name, "Roider_et_al_BNHL_panel2.h5ad")
adata_p2 = sc.read(
    adata_p2_path,
    backup_url="https://exampledata.scverse.org/scvi-tools/Roider_et_al_BNHL_panel2.h5ad",
)
```

```python
adata_p1
```

As the data has been preprocessed already, we can directly merge the two panels into one anndata object using `cytovi.merge_batches()`. This will automatically register a `nan_layer` that will handle the modeling of missing markers under the hood.

```python
adata = cytovi.merge_batches([adata_p1, adata_p2], batch_key="panel_batch")
adata
```

Inspection of the histograms for each marker demonstrates that some proteins, such as CD4, CD3, CD45RA, CD69, were detected in both antibody panels, while four markers were unique to batch one (e.g. CD25, CXCR5) and four additional markers were unique to batch two (e.g. CD244 and TIM-3).

```python
cytovi.plot_histogram(adata, layer_key="scaled", groupby="panel")
```

Additionally, we see that CD69 demonstrates a batch effect in one of the four batches.

```python
cytovi.plot_biaxial(adata, marker_x="CD69", marker_y="CD4", layer_key="scaled", color="batch")
```

## Training a CytoVI model

In the next step, we will train a CytoVI model to control for technical variation between the batches. As our dataset consists of multiple patients of different B cell lymphoma diagnoses, we will additionally specify a `sample_key`, which will be used for downstream application such as performing differential expression across patients or for the identification of disease-associated T cell states. If using CytoVI's `cytovi.merge_batches` function to combine both panels, CytoVI will automatically register a `nan_layer` and handle imputation of missing proteins. In this case only the shared backbone markers are encoded into the latent representation, while the decoder network reconstructs the full protein panel.

```python
cytovi.CYTOVI.setup_anndata(adata, layer="scaled", batch_key="batch", sample_key="PatientID")
model = cytovi.CYTOVI(adata)
model.train(n_epochs_kl_warmup=50)
```

```python
model
```

```python
plt.plot(model.history["elbo_train"], label="Train")
plt.plot(model.history["elbo_validation"], label="Validation")
plt.xlabel("Epochs")
plt.ylabel("ELBO")
plt.legend()
plt.title("Training vs Validation ELBO")
plt.show()
```

## Visualize the joint latent space

Next, we get the latent representation of our cells while controlling for batch and panel variation and visualize the joint latent space using UMAP.

```python
adata.obsm["X_CytoVI"] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_CytoVI", transformer="pynndescent")
sc.tl.umap(adata, min_dist=0.4)
sc.pl.umap(adata, color=["batch", "panel", "Entity"])
```

We can see that this latent representation effectively controlled for batch and panel variation and yielded a cell representation that still maintains the variability between the different disease entities.

## Impute non-overlapping protein markers

Next, we obtain the batch corrected protein expression from the CytoVI model that automatically imputes non-overlapping protein markers. Here, we will sample ten times from the posterior distribution and generate the imputed protein expression ten times in order to assess the imputation uncertainty. We take the mean over these ten samples as our estimate for the imputed protein expression.

```python
imp_expr = model.get_normalized_expression(n_samples=10, return_mean=False)
adata.layers["imputed"] = imp_expr.mean(axis=0).copy()
```

Inspection of the marker histograms now shows the complete imputed protein expression for all proteins present in the combined set of the two antibody panels. Additionally, we can now query markers that were unique for each of the panels, and display for example the expression of the costimulatory protein CD244 versus the IL-2 high affinity chain CD25.

```python
cytovi.plot_histogram(adata, layer_key="imputed", groupby="panel")
```

```python
cytovi.plot_biaxial(adata, marker_x="CD25", marker_y="CD244", layer_key="imputed", color="panel")
```

Next, we compute the coefficient of variation across the ten imputed expression estimates as a measure of uncertainty of the posterior samples and visualize the uncertainty across the cell and feature axes to judge imputation performance.

```python
adata.layers["imputed_cv"] = 100 * imp_expr.std(axis=0).copy() / imp_expr.mean(axis=0).copy()

adata.var["var_imp_uncertainty"] = adata.layers["imputed_cv"].mean(axis=0).copy()
adata.obs["obs_imp_uncertainty"] = adata.layers["imputed_cv"].mean(axis=1).copy()
```

```python
uncertainty = adata.var["var_imp_uncertainty"].sort_values()

plt.figure(figsize=(6, 5))
plt.barh(uncertainty.index, uncertainty.values, color="steelblue")
plt.xlabel("Imputation Uncertainty")
plt.ylabel("Protein")
plt.title("Imputation Uncertainty per Protein")
plt.tight_layout()
plt.show()
```

This analysis demonstrated that the model was less certain when imputing Ki67 expression (even though it was measured in both of the panels) compared to CD25 or CD244 that were only measured in one of the panels.

```python
sc.pl.umap(adata, color=["obs_imp_uncertainty", "batch"])
```

Visualizing the aggregated imputation uncertainty per cell provides an estimate of how reliably missing markers can be imputed. In this example, the uncertainty plot reveals that the model is especially uncertain for cells in regions of CytoVI’s latent space where batch representation is imbalanced. This underscores the importance of imputing markers only when integrating biologically comparable studies. 
We can also query and visualize the imputation uncertainty of individual markers to judge how much we can trust the imputation results in downstream analyses.

```python
sc.pl.umap(adata, color="Ki67", layer="imputed", title="Imputed Ki67 Expression")
sc.pl.umap(adata, color="Ki67", layer="imputed_cv", title="Uncertainty of Ki67 Imputation")
```

## Label transfer

In our example, cells from one antibody panel were already annotated, whereas data from the second panel lacked annotations. We will demonstrate how the integrated CytoVI latent space can be used to transfer labels—such as cell type annotations—from the annotated panel to the unannotated dataset.

```python
for panel in adata.obs["panel"].drop_duplicates():
    adata_panel = adata[adata.obs["panel"] == panel].copy()
    sc.pl.umap(adata_panel, color="cell_type", title=panel)
```

```python
adata_ref = adata[adata.obs["panel"] == "panel1"].copy()
adata.obs["cell_type_predicted"] = model.impute_categories_from_reference(
    adata_reference=adata_ref, cat_key="cell_type"
)
```

```python
sc.pl.umap(adata, color="cell_type_predicted")
```

Since both antibody panels were applied to the same patients we expect a similar proportion of cell types across both panels and can use this as a quick sanity check.

```python
adata.obs.groupby(["panel", "cell_type_predicted"]).size().unstack().plot(kind="bar", stacked=True)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()
```

We can then visualize the expression profile of the transferred cell type labels across the combined marker space of both antibody panels.

```python
sc.pl.matrixplot(
    adata,
    var_names=adata.var_names,
    groupby="cell_type_predicted",
    layer="imputed",
    dendrogram=True,
    standard_scale="var",
    cmap="mako",
)
```

## Differential expression

We can now directly query the generative model to find differentially expressed proteins for each of the transferred cell type labels in relation to all other cells.

```python
de_res = model.differential_expression(groupby="cell_type_predicted", delta=0.1)
```

```python
de_res
```

These results demonstrate that CD45RA is enriched in Naive T helper cells versus all other cells, while PD-1 is decreased, which is in line with our understanding of these marker proteins.

## Label-free differential abundance

Next, we will use CytoVI's label-free differential abundance analysis to automatically detect positions in latent space that are associated with a covariate of interest. In this case we will apply the `model.differential_abundance` method to identify T cell states that are associated with the different lymphoma entities (one versus all). This will for each cell and each lymphoma entity yield a differential abundance (DA) score that estimates how strongly the cell is associated with the respective lymphoma entity compared to all other entities. We can then visualize the DA scores on the latent space to identify regions characteristic for disease.

```python
da_res = model.differential_abundance(groupby="Entity")
```

```python
da_res
```

```python
adata.obs = pd.concat(
    [adata.obs, pd.DataFrame(da_res.values, columns=da_res.columns, index=adata.obs.index)], axis=1
)
sc.pl.umap(adata, color=da_res.columns, cmap="icefire", ncols=3, vmin=-3, vmax=3)
```

In a next step we want to use these DA scores to determine differentially abundant clusters that are associated with disease. For this we will concatenate the DA scores for each tumor entity to the CytoVI latent space and perform Kmeans clustering.  

```python
da_latent = np.hstack((da_res, adata.obsm["X_CytoVI"]))

kmeans = KMeans(n_clusters=13, random_state=0).fit(da_latent)
adata.obs["da_cluster"] = kmeans.labels_.astype("str")
```

```python
sc.pl.umap(adata, color="da_cluster", title="Differential Abundance Clusters")
```

Next, we will compute the relative frequency of the DA clusters per patient and test for differential abundance compared to the control group using a Mann-Whitney U test. We will do this for the cluster that showed highest DA scores for follicular lymphoma (FL) patients. Note: in this case it is cluster 0 but it can change depending on the runtime environment of the notebook.

```python
freq_table = adata.obs.groupby(["PatientID", "da_cluster"]).size().unstack(fill_value=0)
freq_table_normalized = freq_table.div(freq_table.sum(axis=1), axis=0) * 100
res = pd.merge(
    freq_table_normalized.reset_index("PatientID"),
    adata.obs[["PatientID", "Entity"]].drop_duplicates(),
    on="PatientID",
)
```

```python
cluster_oi = "0"
control = "rLN"
group_order = ["rLN", "DLBCL", "MCL", "FL", "MZL"]
control_vals = res.loc[res["Entity"] == control, cluster_oi]

plt.figure(figsize=(6, 4))
sns.violinplot(res, x="Entity", y=cluster_oi, hue="Entity", inner="box", order=group_order)
plt.ylim(0, None)
plt.ylabel(f"Frequency of cluster {cluster_oi} (%)")

y_max = res[cluster_oi].max()
for i, entity in enumerate(group_order):
    if entity != control:
        p = mannwhitneyu(control_vals, res.loc[res["Entity"] == entity, cluster_oi]).pvalue
        if p < 0.05:
            plt.text(i, y_max + 2, f"p={p:.3e}", ha="center", fontsize=8)

plt.tight_layout()
plt.show()
```

This analysis demonstrates that we indeed retrieved T cell states that were differentially abundant for the lymphoma entity. In a last step we compute the confusion matrix with the predicted cell type labels in order to assign these cells to a canonical T cell lineage.

```python
conf_mtx = sc.metrics.confusion_matrix(adata.obs["cell_type_predicted"], adata.obs["da_cluster"])
conf_clust_oi = conf_mtx[cluster_oi].sort_values()

plt.figure(figsize=(6, 4))
plt.barh(conf_clust_oi.index, conf_clust_oi.values)
plt.xlabel("Cluster Cverlap")
plt.ylabel("Predicted Cell Type Label")
plt.title(f"Cell Type Correspondence of Cluster {cluster_oi}")
plt.tight_layout()
plt.show()
```

This analysis demonstrates that the differentially abundant T cell cluster we identified using our label-free DA analysis appear to be mainly comprised of T follicular helper cells - a subpopulation of T helper cells that stimulate B cell responses and has been associated with Follicular Lymphoma in the original study by Roider et al.
