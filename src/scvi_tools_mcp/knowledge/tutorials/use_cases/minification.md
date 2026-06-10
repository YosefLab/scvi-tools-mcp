# Minification

Minification refers to the process of reducing the amount of content in your dataset in a smart way. This can be useful for various sorts of reasons and there can be different ways you might want to do this (we call these minification types). Currently, the only type of minification we support is one where we replace the count data with the parameters of the latent posterior distribution, estimated by a trained model. We will focus this tutorial on this type of minification.

There are multiple motivations for minifying the data in this way:

- The data is more compact, so it takes up less space on disk and in memory.
- Data transfer (share, upload, download) is more smooth owing to the smaller data size.
- By using the latent posterior parameters, we can skip the encoder network and save on computation time.

The reason why this is that most post-training routines for scvi-tools models do not in fact require the full counts. Once your model is trained, you essentially only need the model weights and the pre-computed embeddings to carry out analyses. There are certain exceptions to this, but those routines will alert you if you try to call them with a minified dataset.

<img src="https://raw.githubusercontent.com/scverse/scvi-tutorials/main/figures/minification.svg?raw=true" alt="Minification overview" />

Moreover, you can actually use the latent posterior and the decoder network to estimate the original counts! This is of course not the exact same thing as using your actual full counts, but we can show that it is a good approximation using posterior predictive metrics (paper link tbd).

Let's now see how to minify a dataset and use the corresponding model.


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

## Get the data and model

Here we use the data and pre-trained model obtained from running [this](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/quick_start/api_overview.html) scvi-tools tutorial.

The dataset used is a subset of the heart cell atlas dataset:\
Litviňuková, M., Talavera-López, C., Maatz, H., Reichart, D., Worth, C. L., Lindberg, E. L., … & Teichmann, S. A. (2020). Cells of the adult human heart. Nature, 588(7838), 466-472.

Let's train the model as usual. Also save the model and data on disk as we'll need them later.

```python
adata = scvi.data.heart_cell_atlas_subsampled(save_path=save_dir.name)
```

```python
sc.pp.filter_genes(adata, min_counts=3)
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=1200,
    subset=True,
    layer="counts",
    flavor="seurat_v3",
    batch_key="cell_source",
)
```

```python
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",
    categorical_covariate_keys=["cell_source", "donor"],
    continuous_covariate_keys=["percent_mito", "percent_ribo"],
)
model = scvi.model.SCVI(adata)
```

```python
model.train(max_epochs=20)
```

```python
model_path = os.path.join(save_dir.name, "scvi_hca")
model.save(model_path, save_anndata=True, overwrite=True)
```

```python
model = scvi.model.SCVI.load(model_path)
model
```

Note that, as expected, "Model's adata is minified" is False.

```python
model.adata
```

Notice that in addition to `adata.X`, we also have a layer (`counts`) and a `raw` attribute.

```python
model.adata.raw
```

Let's also save a reference to `model.adata`. We'll see later that this remains unchanged because **minification is not an inplace procedure**.

```python
bdata = model.adata
bdata is model.adata  # this should be True because we didn't copy the anndata object
```

## Minify

To minify the data, all we need to do is:

1. get the latent representation and store it in the adata
1. call `model.minify_adata()`

```python
qzm, qzv = model.get_latent_representation(give_mean=False, return_dist=True)
model.adata.obsm["X_latent_qzm"] = qzm
model.adata.obsm["X_latent_qzv"] = qzv

model.minify_adata()
```

```python
model
```

As expected, "Model's adata is minified" is now True. Also, we can check the model's `minified_data_type`:

```python
model.minified_data_type
```

Let's check out the data now:

```python
model.adata
```

First, let's check that the original adata was not modified (minification is not inplace):

```python
model.adata is bdata
```

Next, we see that we still have the same number of obs and vars: 18641 × 1200. This seems strange! Didn't we say we minized the data? We did. The way we did that is we "emptied" the contents of `adata.X`, `adata.layers["counts"]`, and `adata.raw`. Instead, we cached the much smaller latent posterior parameters in `adata.obsm["_scvi_latent_qzm"]` and `adata.obsm["_scvi_latent_qzv"]`. Let's double check that:

```python
model.adata.X
```

```python
model.adata.layers["counts"]
```

```python
model.adata.raw is None
```

```python
bdata
```

Everything else is the same, all the other metadata is there.

But is the data really smaller now? Let's check:

```python
minified_model_path = os.path.join(save_dir.name, "scvi_hca_minified")
model.save(minified_model_path, save_anndata=True, overwrite=True)
```

```python
before = os.path.getsize(os.path.join(model_path, "adata.h5ad")) // (1024 * 1024)
after = os.path.getsize(os.path.join(minified_model_path, "adata.h5ad")) // (1024 * 1024)

print(f"AnnData size before minification: {before} MB")
print(f"AnnData size after minification: {after} MB")
```

We also see a a new uns key called `_scvi_adata_minify_type`. This specifies the type of minification. It's the same as `model.minified_data_type`. In fact this is a quick way to tell if your data is minified. We also expose a utility function to check that quickly.

```python
model.adata.uns["_scvi_adata_minify_type"]
```

```python
scvi.data._utils._is_minified(model.adata)
```

Last but not least, you might have noticed that there is a new obs columns called `_scvi_observed_lib_size`. We add the pre-computed per-cell library sizes to this column and use it during inference, because the minified data is deprived of the full counts.

Another claim we made earlier is that analysis functions are faster if you use the minified data. Let's time how much they take. Here we'll look at the `get_likelihood_parameters` method.

```python
model_orig = scvi.model.SCVI.load(model_path)

print("Running `get_likelihood_parameters` without minified data...")
%timeit model_orig.get_likelihood_parameters(n_samples=3, give_mean=True)
```

```python
print("Running `get_likelihood_parameters` with minified data...")
%timeit model.get_likelihood_parameters(n_samples=3, give_mean=True)
```

Time savings are not very sharp in the case of this dataset, but there are some marginal savings regardless.

## Save and load

Just like a regular model, you can save the model and its minified data, and load them back in:

```python
model.save(minified_model_path, overwrite=True, save_anndata=True)

# load saved model with saved (minified) adata
loaded_model = scvi.model.SCVI.load(minified_model_path)
loaded_model
```

Next, let's load the model with a non-minified data.

```python
loaded_model = scvi.model.SCVI.load(model_path, adata=bdata)
loaded_model
```

So if you want to "undo" the minification procedure, so to speak, you can always load your model with the non-minified data (if you still have it), or any other non-minified data for that matter, as long as it's compatible with the model of course.

```python
scvi.data._utils._is_minified(model.adata)
```

## Support

Minification is not supported for all models yet. A model supports this functionality if and only if it inherits from the `BaseMinifiedModeModelClass` class. A model that does not support this:

- does not have a `minify_adata()` method
- cannot be loaded with a minified data. If you try to do this you will see this error:
  "The MyModel model currently does not support minified data."

To support minification for your own model, inherit your model class from the `BaseMinifiedModeModelClass` and your module class from the `BaseMinifiedModeModuleClass`.
