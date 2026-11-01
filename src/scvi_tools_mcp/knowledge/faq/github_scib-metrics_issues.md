# YosefLab/scib-metrics GitHub Issues Q&A

32 issues (open and closed, bots excluded) from YosefLab/scib-metrics with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; issues are only removed once they age out of that window.

## #58: Error when there is only one batch
**Issue:** #58 | **Last activity:** 2026-08-13T11:30:12Z
**State:** closed | **Author:** @justjhong | **Comments:** 4 | **Created:** 2022-11-29 | **URL:** https://github.com/YosefLab/scib-metrics/issues/58

silhouette_batch errors when there is only one batch:
`ValueError: No objects to concatenate`

We should check this edge case for the other metrics as well.

**@adamgayoso:** this should also be a part of #62

**@Layne-Huang:** How can we ignore the batch metrics when we only have one batch here?

**@wen-zy:** > How can we ignore the batch metrics when we only have one batch here?

@Layne-Huang  I'm wondering if you've found a way to ignore batch metrics when there's only one batch? 🧐If you have successfully solved this problem, could you please tell me how you did it? Thank you very much! 😃

**@jkobject:** use `batch_correction_metrics=None,`

## #62: Util to validate input data
**Issue:** #62 | **Last activity:** 2026-08-13T11:30:11Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2022-12-09 | **URL:** https://github.com/YosefLab/scib-metrics/issues/62

- We should always change batch and label inputs to pandas categorical codes
- Check graph inputs have K neighbors

etc.

Perhaps a decorator?

## #100: Font colors in Aggregate score
**Issue:** #100 | **Last activity:** 2026-08-13T11:30:10Z
**State:** closed | **Author:** @alitinet | **Comments:** 2 | **Created:** 2023-08-10 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/100

### Description of feature

Hi,

The values in the Aggregate Score of the results table are really hard to read when the score is high and the background color gets very dark, it would be nice if the font color was set to white depending on the value like it is in Bio conservation and Batch correction metrics. That would be super useful, thank you!

**@martinkim0:** Thanks for your feature request, I'll look into this.

**@adamgayoso:** We'd be happy to accept a PR if you are able to make the change @alitinet

## #32: param naming
**Issue:** #32 | **Last activity:** 2026-08-13T10:10:11Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 1 | **Created:** 2022-10-14 | **URL:** https://github.com/YosefLab/scib-metrics/issues/32

Maybe we should use `embedding` and `neighbor_distances` and `neighbor_connectivities` explictly?

_Originally posted by @adamgayoso in https://github.com/YosefLab/scib-metrics/issues/30#issuecomment-1275449141_

**@ori-kron-wis:** The underlying design tension (embeddings vs. neighbor-graph inputs sharing a generic name) was resolved differently in PR #129, which introduced the NeighborsResults
  dataclass bundling distances+indices — so graph metrics take one typed object instead of separate neighbor_distances/neighbor_connectivities params. The literal rename to embedding never
  happened, but I'd call this closed-by-design;

## #144: Add workflow for running tutorials in containers
**Issue:** #144 | **Last activity:** 2026-07-28T07:46:45Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-23 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/144

### Description of feature

Should be similar to scvi-tutorials

**@ori-kron-wis:** running in YosefLab

## #231: Return ndarray with lisi score per cell
**Issue:** #231 | **Last activity:** 2025-10-07T12:17:22Z
**State:** closed | **Author:** @LuLeom | **Comments:** 2 | **Created:** 2025-09-17 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/231

### Description of feature

Hi, thanks for your work!

In the current implementation of cLisi and iLisi the output is a `float` which [by looking at the source code](https://github.com/YosefLab/scib-metrics/blob/b82f1b916ec288ae6f1da67ce3fef512cd0adb9b/src/scib_metrics/metrics/_lisi.py#L74-L103), I presume is a median of all the -per cell lisi scores.

Would it be possible to have a parameter to actually get the `ndarray` of shape (n_cells,) with the -per cell lisi scores? (basically the output of [lisi_knn()](https://github.com/YosefLab/scib-metrics/blob/b82f1b916ec288ae6f1da67ce3fef512cd0adb9b/src/scib_metrics/metrics/_lisi.py#L98))

This addition would be super helpful when plotting results (e.g. in a UMAP )

**@canergen:** I think you want to just call `lisi_knn(X, labels, perplexity=perplexity)` directly on your data, which is an exposed method but might require some wrangling for the inputs.

**@LuLeom:** @canergen Indeed. I ended up using that solution. Thanks for replying :)

## #192: Use precomputed kNN graph
**Issue:** #192 | **Last activity:** 2025-09-29T11:11:58Z
**State:** closed | **Author:** @j-bac | **Comments:** 7 | **Created:** 2025-03-07 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/192

### Description of feature

It would be great to show how to use precomputed neighbors as input to Benchmarker. For example, when evaluating multiple cell type annotations for the same dataset, Benchmarker will recompute the kNN graph each time.

It's maybe already possible to do this manually by obtaining a NeighborsResults object and then applying individual metrics or by editing the Benchmarker attributes

**@ori-kron-wis:** Hey,
That's a good idea.
While it can be done technically by manipulating the benchmark attributes as you suggested, I added a variable "_compute_neighbors" to the benchmarker object, which is True by default; however, it can be manipulated after the Benchmarker was initialized to False (in the 2nd+ time your run it), and then KNN will not be computed when running.

You will obviously have to make sure there is knn graph computed in the adata.
So for example, you can extract them after the 1st benchmark iteration by:
`bm_new._emb_adatas['X_scVI'].uns = bm_old._emb_adatas['X_scVI'].uns
`where 'X_scVI' is the embedded layer key, and so on for the rest.

Then the 2nd benchmark will be running w/o the need to recompute the knn graph.

See this example:

<img width="873" height="763" alt="Imag …

**@wangflmi:** Sorry, I still don't know how to get the score of these metrics: "Isolated labels-F1 | KMeans NMI | KMeans ARI." I run on what you show us, but some results of metrics are the same as the unintegrated.

**@ori-kron-wis:** I didnt follow you,
Is that related to this issue? Did you update to the recent scib-metrics?
You can get the scores with `bm.get_results()` once the benchmarker finishes to run.

I checked again and the results differ between scvi embedded and PCA (for those metrics). Obiosuly it is data and model quality dependent.
See as an example that was running on scvi api overview tutorial (https://docs.scvi-tools.org/en/latest/tutorials/notebooks/quick_start/api_overview.html).

Attached image:

<img width="796" height="1178" alt="Image" src="https://github.com/user-attachments/assets/d1a546f1-565a-411b-ad09-1d9d00a1897e" />

**@wangflmi:** Sorry, I didn't express myself clearly. I want to evaluate the BBKNN results using scib-metrics, but the BBKNN results modify the Neighbors results. Setting “embedding_key” to “X_pca” yields the same results as those without integration. Setting it to ‘umap’ after sc.tl.umap seems inconsistent with the code's intended purpose. This is because the code defaults to using “X_pca” for ‘compute_neighbor’ and does not directly utilize the graph modified by BBKNN.

**@ori-kron-wis:** I understand now. The original aim of this issue was to be able to save runtime and not compute again the KNN graph if one to run more than 1 benchmarkers, to be compared by different labels.

But isn't this flow work for you as well? There are several options now:
Prepare the BBKNN results beforehand, add them to the obsm of the adata and run the benchmarker as usual (here BBKNN embedding will be regarded as "X_umap", which is the default):

<img width="1189" height="640" alt="Image" src="https://github.com/user-attachments/assets/e921250a-b8fd-4d69-8567-c7f80affc872" />

Or use BBKNN embedding pre-computed knn graph as the "dummy" X_PCA and recalculate, like above:

<img width="1188" height="766" alt="Image" src="https://github.com/user-attachments/assets/78e89c36-eb80-4f53-9c7f-bde66489 …

**@wangflmi:** Thank you for your reply. I apologize for disturbing you to confirm some additional information. I read the paper "Benchmarking atlas-level data integration in single-cell genomics".It shows some of metrics cannot be run on the corrected graph output .

<img width="1296" height="561" alt="Image" src="https://github.com/user-attachments/assets/0091f9b0-c534-4477-898e-0bafa228fed7" />

<img width="736" height="875" alt="Image" src="https://github.com/user-attachments/assets/f534789c-8bac-4d7d-8524-ec171301b4f3" />

So I think these suggestions you have provided will not work. I have tried to compute metrics separately ,using the old scib code as a reference. I use the isolated label (F1 score)  rather than the isolated label ASW score.  I set the "neighbors_within_batch" to [15,50.90] when I …

**@ori-kron-wis:** Let me read through this carefully and get back to you.
As said, not everything is currently feasible to do in scib-metrics.

## #97: test_benchmarker.py fails if dummy data has labels size == 1
**Issue:** #97 | **Last activity:** 2025-09-27T08:08:34Z
**State:** closed | **Author:** @elipapa | **Comments:** 0 | **Created:** 2023-07-18 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/97

### Report

Dummy test data should probably have more than one label.
When labels.shape == 1 the test_benchmarker.py fails.

https://github.com/YosefLab/scib-metrics/blob/5681f7ef6b6d4cfd04fda90d1d33fab1dbe1bb50/tests/utils/data.py#L12

### Version information

_No response_

## #133: the count matrices don't contain counts
**Issue:** #133 | **Last activity:** 2025-09-27T08:07:55Z
**State:** closed | **Author:** @jkobject | **Comments:** 4 | **Created:** 2024-01-31 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/133

### Report

Hello,

I am seeing that the benchmark datasets used mention that you are taking the "counts" layer from these datasets. However, when looking at this layer I see values being floats instead of ints. Meaning that they are not counts.

The tool I want to benchmark only takes count matrices.

How should I get the count data?

### Version information

_No response_

**@jkobject:** to verify that they don't contain counts: do
```python
adata = sc.read(
    "data/lung_atlas.h5ad",
    backup_url="https://figshare.com/ndownloader/files/24539942",
)
adata.layers['counts'].sum()
```

same thing for the pancreas dataset.

**@adamgayoso:** Just having a float dtype does not imply that they are not count data. Most datasets are stored in a float32 format.

For that particular dataset, I would encourage you to read the original [scib paper](https://www.nature.com/articles/s41592-021-01336-8) methods section.

If you're using a tool like scVI, it would technically work on data with decimals, like (1.03). The question is whether the non-count data are meant to represent count data. For example, pseudoaligners can provide probabilistic count values.

**@jkobject:** Hello Adam,

Thanks for the reply. I understand that even raw counts are often stored as float32, but here I see that some of the datasets used in this combined dataset have values that are not raw counts (meaning data with decimals).

I have not worked with probabilistic raw counts before. Are you saying that this is the reason why most of the 10x samples have decimal values?

Reading the methods section. It is saying that some datasets were unavailable as raw counts and they used the rpkm or tpms: so the counts also contain normalized data?

I am not sure how to continue with it if the data is depth normalized. I am working with my own model that is assuming that the counts are true counts..

**@canergen:** Files were taken from the original scib paper and questions are better handled there.

## #150: KBET (without labels) to BatchCorrection
**Issue:** #150 | **Last activity:** 2025-09-27T08:06:05Z
**State:** closed | **Author:** @lebelm | **Comments:** 2 | **Created:** 2024-02-27 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/150

### Description of feature

Hello,

I was wondering if it would be possible to add KBET to the list of metrics that can be selected in the BatchCorrection object ? Or maybe it is already possible and I didn't figure out how.

I saw that the function `scib_metrics.kbet()` is present in the API list and I would be interested in running it as it is label-free, though it would make sense to have it off by default.
Currently, it can be run it by itself but this is not as practical as it takes a NeighborsResults as input.

`scib_metrics.benchmark.BatchCorrection(silhouette_batch=True, ilisi_knn=True, kbet_per_label=True, graph_connectivity=True, pcr_comparison=True)`

Thank you for the nice package in any case !

**@QqQss:** Similar question here.
I'm wondering if there's a function that can automatically convert the graph in adata (adatar.obsp['connectivities'] and adata.obsp['distances']) to NeighborsResults?

**@ori-kron-wis:** You can do it already, but not from the Benchmarker (which expects labels) / put dummy labels.
see: test/test_metrics/test_kbet

## #232: How to use benchmark metrics to evaluate the adata after BBKNN integration.
**Issue:** #232 | **Last activity:** 2025-09-27T08:04:13Z
**State:** closed | **Author:** @wangflmi | **Comments:** 1 | **Created:** 2025-09-22 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/232

### Report

The paper showed we can use benchmark metrics to evaluate the adata after BBKNN integration. But I can only use some default functions in the benchmark-metrics package to get the batch-remove grades. For bio-conservation grades, I can’t find appropriate functions to apply.

### Version information

| Package   | Version |
| --------- | ------- |
| pycombat  | 0.20    |
| scanorama | 1.7.4   |

| Dependency               | Version             |
| ------------------------ | ------------------- |
| pickleshare              | 0.7.5               |
| nvidia-nvjitlink-cu12    | 12.8.93             |
| importlib_resources      | 6.5.2               |
| fbpca                    | 1.0                 |
| xarray                   | 2025.6.1            |
| torchmetrics             | 1.8.2               |
| wcwidth                  | 0.2.13              |
| sparse                   | 0.17.0              |
| annoy                    | 1.17.3              |
| nvidia-cuda-nvrtc-cu12   | 12.8.93             |
| debugpy                  | 1.8.16              |
| nvidia-cufft-cu12        | 11.3.3.83           |
| docrep                   | 0.3.2               |
| asttokens                | 3.0.0               |
| nvidia-cudnn-cu12        | 9.10.2.21           |
| setuptools               | 78.1.1              |
| pytz                     | 2025.2              |
| triton                   | 3.4.0               |
| nvidia-curand-cu12       | 10.3.9.90           |
| nvidia-cuda-runtim …

**@canergen:** Hi, you can pass in a UMAP generated with BBKNN as an embedding to scib-metrics when you follow our tutorials. Unfortunately, you can't plug in the NN graph.

## #218: rescale field in scib_metrics.bras()
**Issue:** #218 | **Last activity:** 2025-09-14T07:18:15Z
**State:** closed | **Author:** @LuLeom | **Comments:** 2 | **Created:** 2025-07-10 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/218

### Report

Hi,

I am trying to use the function `scib_metrics.bras` [according to the documentation](https://scib-metrics.readthedocs.io/en/stable/generated/scib_metrics.bras.html), however when the parameter `rescale` is specified the function returns the following:

```python
TypeError: bras() got an unexpected keyword argument 'rescale'
```

I tried some tests, and in my case the returned values are between 0 and 1.
Is the function now supposed to always behave like `rescale=True` ?


##### Version information
```
-----
anndata             0.11.4
pandas              2.3.1
scib_metrics        0.5.6
session_info        v1.0.1
-----
PIL                         11.1.0
absl                        2.3.1
anyio                       NA
appnope                     0.1.4
arrow                       1.3.0
asttokens                   NA
attr                        25.3.0
attrs                       25.3.0
babel                       2.17.0
certifi                     2025.01.31
cffi                        1.17.1
charset_normalizer          3.4.1
chex                        0.1.89
comm                        0.2.2
cycler                      0.12.1
cython_runtime              NA
dateutil                    2.9.0.post0
debugpy                     1.8.13
decorator                   5.2.1
defusedxml                  0.7.1
executing                   2.2.0
fastjsonschema              NA
filelock                    3.18.0
fqdn                        NA
h5py                        3.14.0 …

**@canergen:** Yes, it’s true by default, it’s not exposed and the function documentation is wrong here.
@prauten do you want this to be exposed or does it make no sense in BRAS? I would have to go through details to figure it out.

**@prauten:** Hi @LuLeom,

Thank you for identifying and bringing up this bug!

And thank you, @canergen, for notifying me.

I intentionally did not expose this parameter for BRAS, and it was an oversight not to remove it from the documentation.

In the provided implementations for BRAS and silhouette_batch, the values will always range between 0 and 1. If I had implemented the option to rescale, the interpretation would change: with `rescale=True`, higher values would be desirable, while with `rescale=False`, lower values would be preferred.

Personally, I would recommend not exposing this option and removing it from the function documentation to align with the behavior of the function and the implementation of BRAS as described in the corresponding manuscript. However, if there is a desire to includ …

## #186: `bm.benchmark()` fails to de-allocate GPU memory.  garbage collection fail?
**Issue:** #186 | **Last activity:** 2025-09-14T07:18:07Z
**State:** closed | **Author:** @ergonyc | **Comments:** 2 | **Created:** 2024-11-26 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/186

### Report

I'm running `bm.benchmark()` using three `embedding_obsm_keys` on 2.7m cell dataset.  It previously ran, albiet slowly on a smaller dataset using only two keys.
I can reproduce it on a local 4080, and on dual remote v100s.

CODE: ( almost directly from tutoral)
```python
adata_input = "artifacts/cohortv2.2.0/cohort.final_adata.h5ad" #~2.7m cells x 3k genes
# Set CPUs to use for parallel computing
sc._settings.ScanpyConfig.n_jobs = -1
batch_key = "sample"
label_key = "cell_type"
adata = sc.read_h5ad(adata_input)  # type: ignore

adata.obsm["Unintegrated"] = adata2.obsm["X_pca"]
biocons = BioConservation(isolated_labels=False)
bm = Benchmarker(
    adata,
    batch_key=batch_key,
    label_key=label_key,
    embedding_obsm_keys=["Unintegrated", "X_scvi", "X_pca_harmony"],
    pre_integrated_embedding_obsm_key="X_pca",
    bio_conservation_metrics=biocons,
    n_jobs=-1,
)
bm.prepare(neighbor_computer=faiss_brute_force_nn)  # full GPU half memory (scales with different GPUs)
bm.benchmark()
```


FAILURE:
```bash
Computing neighbors: 100%|██████████| 3/3 [04:21<00:00, 87.18s/it]
Embeddings:   0%|          | 0/3 [00:00<?, ?it/s]                                                2024-11-25 23:57:13.747881: W external/tsl/tsl/framework/bfc_allocator.cc:482] Allocator (GPU_0_bfc) ran out of memory trying to allocate 2.23GiB (rounded to 2395844096)requested by op
2024-11-25 23:57:13.748060: W external/tsl/tsl/framework/bfc_allocat …

**@ori-kron-wis:** Can you add gc.collect() before and after those commands to force the garbage collection?

**@ori-kron-wis:** added

## #224: Documentation and code mismatch
**Issue:** #224 | **Last activity:** 2025-08-11T18:23:16Z
**State:** closed | **Author:** @mvfki | **Comments:** 1 | **Created:** 2025-08-11 | **URL:** https://github.com/YosefLab/scib-metrics/issues/224

https://github.com/YosefLab/scib-metrics/blob/b9590642a65224e2888e28e0699e0b194ae8aefb/src/scib_metrics/metrics/_silhouette.py#L66-L67

Why not remove this documentation or add the `rescale` option in the function argument?

**@mvfki:** Sorry I didn't see #218

## #219: AttributeError: 'Series' object has no attribute 'nonzero'
**Issue:** #219 | **Last activity:** 2025-07-11T20:03:29Z
**State:** closed | **Author:** @royfrancis | **Comments:** 2 | **Created:** 2025-07-10 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/219

### Report

Error when running benchmark.

<details>
<summary>Reproducible example</summary>

```python
# https://datasets.cellxgene.cziscience.com/d8533311-eff4-4b9c-a1b2-6084ac39b65b.h5ad
# https://cellxgene.cziscience.com/e/ce5132bd-7600-4299-bb2c-2b00d409170f.cxg/

import scanpy as sc
import anndata as ad

adata = sc.read_h5ad("data/processed/test-scib/d8533311-eff4-4b9c-a1b2-6084ac39b65b.h5ad")

# preprocess
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key="tissue")
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)

# harmony integration
# import harmonypy
import scanpy.external as sce

adata1 = adata.copy()
sce.pp.harmony_integrate(adata1, 'tissue')
adata1.obsm['X_pca'] = adata1.obsm['X_pca_harmony']
sc.pp.neighbors(adata1)
sc.tl.umap(adata1)
adata.obsm['X_umap_harmony'] = adata1.obsm['X_umap']
del adata1

from scib_metrics.benchmark import Benchmarker

bm = Benchmarker(
    adata,
    batch_key="tissue",
    label_key="cell_type",
    embedding_obsm_keys=[
      "X_umap",
      "X_umap_harmony"
      ],
)
```

</details>

```
>>> bm.benchmark()
Computing neighbors: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:06<00:00,  3.10s/it]
Embeddings:   0%|                                                                                                            | 0/2 [00:00<?, ?it/s/opt/conda/lib/python3.10/si …

**@royfrancis:** A simpler reproducible example without downloading a dataset.

<details>

<summary>Click here</summary>

```python
import scanpy as sc
import anndata as ad
import numpy as np

adata = sc.datasets.pbmc3k_processed()
adata.obs['batch'] = np.random.choice(['A', 'B', 'C'], size=len(adata.obs))
adata.obs['cell_type'] = np.random.choice(['c1', 'c2', 'c3', 'c4', 'c5'], size=len(adata.obs))

# harmony integration
# import harmonypy
import scanpy.external as sce

adata1 = adata.copy()
sce.pp.harmony_integrate(adata1, 'batch')
adata1.obsm['X_pca'] = adata1.obsm['X_pca_harmony']
sc.pp.neighbors(adata1)
sc.tl.umap(adata1)
adata.obsm['X_umap_harmony'] = adata1.obsm['X_umap']
del adata1

from scib_metrics.benchmark import Benchmarker

bm = Benchmarker(
  adata,
  batch_key="batch",
  label_key="cell_typ …

**@canergen:** Hi, I‘m sooty your experiencing this. It’s a version conflict between scipy and pandas in your environment. I would recommend uninstalling scipy and reinstalling. If it’s not fixed, I would start in a new conda environment from scratch.

## #200: Initialize Benchmarker class from DataFrame
**Issue:** #200 | **Last activity:** 2025-07-08T11:32:55Z
**State:** closed | **Author:** @Marius1311 | **Comments:** 2 | **Created:** 2025-04-14 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/200

### Description of feature

Hi scib-metrics team! Thanks for this amazing package! I was wondering whether there's already a convenient way to initialize a Benchmarker object from an existing dataframe of scIB metrics. The use case is a hyperparameter sweep where I'm comparing different model variants with scIB metrics. Each job evaluates one combination of hyperparameters and computes scIB metrics on the results. The results are logged somewhere, and once all runs have finished, I want to aggregate them, apply min-max scaling to the columns, and visualize the table. I can hack my way by assigning to `bm._results` directly and making sure my DataFrame has the correct structure, but I was wondering whether there's a more convenient way of doing this.

**@ori-kron-wis:** Hey,
Sorry for late replay - the short answer is no theres no convenient way, altough what you do is perfectly fine and explolit the package functionality with "external data". This also relates to https://github.com/YosefLab/scib-metrics/issues/205 as you will need to run each experiment w/o the scaling.

2 suggestions I can add:

1. We have an option to optimise an SCVI-Tools model's hyperparameters based on one of scib-metrics "metrics" (see: https://docs.scvi-tools.org/en/latest/tutorials/notebooks/use_cases/autotune_scvi.html#tuning-over-integration-metrics-with-scib-metrics)
2. We can input several embeddings, originating from different model variants, into a single run of the benchmarker, it will compare them. See: https://scib-metrics.readthedocs.io/en/stable/notebooks/lung_example …

**@Marius1311:** Thanks @ori-kron-wis !

## #212: kBET filter cluster bug
**Issue:** #212 | **Last activity:** 2025-07-08T06:15:30Z
**State:** closed | **Author:** @qinzhu | **Comments:** 2 | **Created:** 2025-06-28 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/212

### Report

In current version:
    skipped = clusters[counts > 10]
    clusters = clusters[counts <= 10]

The good clusters seem got skipped, while the bad clusters got kept, leading to empty results for the column.

### Version information

_No response_

**@canergen:** @ori-kron-wis fixing this should trigger a release - the values are wrong currently.

**@ori-kron-wis:** Sure, Im working on having BRAS as well, then we will release.

## #205: min_max_scale=False should be default in .get_results
**Issue:** #205 | **Last activity:** 2025-07-07T12:39:48Z
**State:** closed | **Author:** @Xparx | **Comments:** 1 | **Created:** 2025-04-30 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/205

### Description of feature

Hello,

Would it be possible to set `min_max_scale=False` as the default. Simply becouse if you compile results from different tables and different runs with `min_max_scale=True` it is impossible to go back to `False` and you need to recompute everything. However, it's trivial to go from `False` to `True` after the fact.

**@ori-kron-wis:** Absolutely, it will be available in the next release.

## #193: Better scib metrics
**Issue:** #193 | **Last activity:** 2025-06-29T08:08:32Z
**State:** closed | **Author:** @j-bac | **Comments:** 1 | **Created:** 2025-03-07 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/193

### Description of feature

[A new preprint](https://www.biorxiv.org/content/10.1101/2025.01.21.634098v1.full.pdf) argues that original silhouette scib metrics can be misleading and suggests alternatives. This might be interesting for this package

**@ori-kron-wis:** BRAS was implemented

## #187: Metrics Overview
**Issue:** #187 | **Last activity:** 2025-06-29T08:07:29Z
**State:** closed | **Author:** @DarioS | **Comments:** 1 | **Created:** 2025-02-07 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/187

### Description of feature

It would be nice to see a summary table that shows the basics of all available metrics. For example,

![Image](https://github.com/user-attachments/assets/94f4be68-b205-4136-a13c-8e1e4aa8f0b4)

**@ori-kron-wis:** Please refer to this link:
https://scib.readthedocs.io/en/latest/index.html#metrics
Not all the bio conservations metrics there are part of scib-metrics though

all of them are ranged [0,1] and higher means better.

## #113: Incorrect return type in the documentation for ilisi/clisi
**Issue:** #113 | **Last activity:** 2024-11-04T08:46:06Z
**State:** closed | **Author:** @timtreis | **Comments:** 1 | **Created:** 2023-10-04 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/113

### Report

Extremely minor but I'm currently extracting a few bits from "under the hood". Noticed that the return type of the `ilisi_knn` and `clisi_knn` calculations are incorrect. According to https://scib-metrics.readthedocs.io/en/stable/generated/scib_metrics.ilisi_knn.html it's `ilisi Array of shape (n_cells,) with the iLISI score for each cell.` but due to https://github.com/YosefLab/scib-metrics/blob/9d109007d8b78ad2678342db6630cc355cfd1d0b/src/scib_metrics/_lisi.py#L66 it's a single float. Analog for clisi

### Version information

_No response_

**@adamgayoso:** Thanks! Happy to accept a PR with the change

## #157: bm.plot_results_table() fails when all batch correction metrics are set to False
**Issue:** #157 | **Last activity:** 2024-11-04T08:02:01Z
**State:** closed | **Author:** @soerenab | **Comments:** 5 | **Created:** 2024-03-20 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/157

### Report

I only want to run the bio conservation metrics, so I have initialized the Benchmarker as follows:

```python
batch_correction = BatchCorrection(
    silhouette_batch=False,
    ilisi_knn=False,
    kbet_per_label=False,
    graph_connectivity=False,
    pcr_comparison=False
)

bio_conservation = BioConservation(
    isolated_labels=True,
    nmi_ari_cluster_labels_leiden=False,
    nmi_ari_cluster_labels_kmeans=True,
    silhouette_label=True,
    clisi_knn=True
)

bm = Benchmarker(
    adata,
    batch_key="dummy_batch",
    label_key="cell_type",
    embedding_obsm_keys=embedding_obsm_keys,
    batch_correction_metrics=batch_correction,
    bio_conservation_metrics=bio_conservation,
    n_jobs=6,
)
```
Then, `bm.benchmark() ` runs fine, however, when I want to plot the results with `bm.plot_results_table()` I get the below error:

```python
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
File ~/miniconda3/envs/contrastive-transformer/lib/python3.10/site-packages/pandas/core/indexes/base.py:3802, in Index.get_loc(self, key, method, tolerance)
   3801 try:
-> 3802     return self._engine.get_loc(casted_key)
   3803 except KeyError as err:

File ~/miniconda3/envs/contrastive-transformer/lib/python3.10/site-packages/pandas/_libs/index.pyx:138, in pandas._libs.index.IndexEngine.get_loc()

File ~/miniconda3/envs/contrastive- …

**@martinkim0:** Thanks for bringing this up! I'll take a look at this

**@LArnoldt:** Hey @martinkim0 - Thank you for this great package!



The issue described above also appplies to the function `get_results `in `_core.py`, since function can't calculate:

`per_class_score["Total"] = 0.4 * per_class_score["Batch correction"] + 0.6 * per_class_score["Bio conservation"]`

since either "Batch correction" or "Bio conservation" is not available in df `per_class_score`, when disabling all metrics.

**@adamgayoso:** Hi @LArnoldt -- we are happy to accept a pull request to fix this.

Perhaps to the batch correction and bio conservation dataclasses we can add a helper fn that counts how many metrics are active. This can be then be used to control the plotting code and the total score.

**@SidSouthekal-Lilly:** same issue with get_results() and plot_results_table() if either Bio conservation or Batch corrrection is set to False. Any fix yet ?

**@LArnoldt:** Hi @adamgayoso @SidSouthekal-Lilly - please see PR #https://github.com/YosefLab/scib-metrics/pull/179.

## #122: Type error when running scib_metrics
**Issue:** #122 | **Last activity:** 2024-11-03T21:10:11Z
**State:** closed | **Author:** @HelloWorldLTY | **Comments:** 3 | **Created:** 2023-11-17 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/122

### Report

Hi, here is a bug when running:

bm.benchmark()

209 if not self._prepared:
    210     self.prepare()
    212 num_metrics = sum(
--> 213     [sum([v is not False for v in asdict(met_col)]) for met_col in self._metric_collection_dict.values()]
    214 )
    216 for emb_key, ad in tqdm(self._emb_adatas.items(), desc="Embeddings", position=0, colour="green"):
    217     pbar = tqdm(total=num_metrics, desc="Metrics", position=1, leave=False, colour="blue")

File ~/.conda/envs/tangram/lib/python3.8/dataclasses.py:1072, in asdict(obj, dict_factory)
   1053 """Return the fields of a dataclass instance as a new dictionary mapping
   1054 field names to field values.
   1055
   (...)
   1069 tuples, lists, and dicts.
   1070 """
   1071 if not _is_dataclass_instance(obj):
-> 1072     raise TypeError("asdict() should be called on dataclass instances")
   1073 return _asdict_inner(obj, dict_factory)

TypeError: asdict() should be called on dataclass instances

Could you please help me handle this bug? Thanks.

### Version information

_No response_

**@adamgayoso:** What version of python are you using?

**@HelloWorldLTY:** 1.1.4 I think.

**@adamgayoso:** Closed due to inactivity. Please reopen if you're still having an issue.

## #153: `Benchmarker`'s progress bar does not adjust based on `settings.progress_bar_style`
**Issue:** #153 | **Last activity:** 2024-11-03T21:09:35Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-29 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/153

### Description of feature

N/A

**@adamgayoso:** Closed by #152

## #175: progress bar not moving
**Issue:** #175 | **Last activity:** 2024-08-26T17:23:20Z
**State:** closed | **Author:** @Flu09 | **Comments:** 1 | **Created:** 2024-08-25 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/175

### Report

>>> bm = Benchmarker(
...     obj,
...     batch_key="dataset",
...     label_key="celltypes,
...     embedding_obsm_keys=["unintegrated", "cca", "rpca", "harmony", "scvi"],
...     n_jobs=29,
... )
>>> bm.benchmark()
Computing neighbors: 100%|██████████| 5/5 [41:56<00:00, 503.33s/it]
Embeddings:   0%|          | 0/5 [00:00<?, ?it/s]
Metrics:   0%|          | 0/10 [00:00<?, ?it/s]
Metrics:   0%|          | 0/10 [00:00<?, ?it/s, Bio conservation: isolated_labels]

It has been like that for 12 hours now. I am not sure how long it is supposed to take. The cells are 1.3 million.  I will appreciate it if you can help. Also how to import seurat v5 cca embedding into the adata object please ?

### Version information

scib-metrics: 0.5.1
anndata: 0.10.8
chex: 0.1.85
igraph: 0.10.8
jax: 0.4.25
jaxlib: 0.4.25
matplotlib: 3.8.3
numpy: 1.26.4
pandas: 2.2.1
plottable: 0.1.5
pynndescent: 0.5.11
rich: 13.7.1
scanpy: 1.9.8
scikit-learn: 1.4.1.post1
scipy: 1.11.4
tqdm: 4.66.2
umap-learn: 0.5.5
texttable: 1.7.0
get-annotations: 0.1.2
h5py: 3.10.0
joblib: 1.3.2
natsort: 8.4.0
networkx: 3.2.1
numba: 0.59.0
packaging: 23.2
patsy: 0.5.6
seaborn: 0.13.2
session-info: 1.0.0
statsmodels: 0.14.1
array-api-compat: 1.4.1
exceptiongroup: 1.2.0
contourpy: 1.2.0
cycler: 0.12.1
fonttools: 4.49.0
kiwisolver: 1.4.5
pillow: 10.2.0
pyparsing: 3.1.2
python-dateutil: 2.9.0.post0
importlib-resources: 6.1.2
pytz: 2024.1
tzdata: 2024.1
threadp …

**@canergen:** Hi, see my response on discourse.

## #104: Fix random seed in NMI/ARI
**Issue:** #104 | **Last activity:** 2024-08-22T07:29:16Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 2 | **Created:** 2023-08-29 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/104

### Description of feature

I think the clustering of NMI/ARI may currently not be fully reproducible due to the lack of setting the random seed.
I think I fixed it with the below:
```
    random.seed(0)
    labels_pred = sm._nmi_ari._compute_clustering_leiden(X, resolution)
```

**@adamgayoso:** if you seed your script or notebook before running any package code then it should be reproducible. I'm not sure we'd want to change the global seed inside a local function

**@adamgayoso:** I think something like

```
import random
rng = random.Random(42)
ig.set_random_number_generator(rng)
```

would solve it

## #154: Allow scArches to extend categorical covariates
**Issue:** #154 | **Last activity:** 2024-03-01T17:14:38Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-01 | **URL:** https://github.com/YosefLab/scib-metrics/issues/154

### Description of feature

N/A

## #138: Release scib-metrics 0.5.1
**Issue:** #138 | **Last activity:** 2024-02-23T22:19:33Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-22 | **URL:** https://github.com/YosefLab/scib-metrics/issues/138

https://github.com/YosefLab/scib-metrics/releases/tag/v0.5.1

https://pypi.org/project/scib-metrics/0.5.1/

## #109: different neighbors numbers for cells with clisi_knn
**Issue:** #109 | **Last activity:** 2024-01-04T17:32:06Z
**State:** closed | **Author:** @yuyanMaggieliu | **Comments:** 3 | **Created:** 2023-09-18 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/109

### Report

i am running scib_metrics benchmark with the tutorial(Benchmarking lung integration from [),](https://scib-metrics.readthedocs.io/en/stable/notebooks/lung_example.html) i have use run 4 methods  and save the embedding in obsm as the tutorial told. However, when i was using bm=Benchmarker(adata) and run bm.benchmark(), it raise the error from clisi_knn method that "ValueError: Each cell must have the same number of neighbors.".

The detail error message is

> File ~/.conda/envs/ju/lib/python3.9/site-packages/scib_metrics/benchmark/_core.py:226, in Benchmarker.benchmark(self)
    223 if isinstance(use_metric_or_kwargs, dict):
    224     # Kwargs in this case
    225     metric_fn = partial(metric_fn, **use_metric_or_kwargs)
--> 226 metric_value = getattr(MetricAnnDataAPI, metric_name)(ad, metric_fn)
    227 # nmi/ari metrics return a dict
    228 if isinstance(metric_value, dict):

File ~/.conda/envs/ju/lib/python3.9/site-packages/scib_metrics/benchmark/_core.py:88, in MetricAnnDataAPI.<lambda>(ad, fn)
     86 nmi_ari_cluster_labels_kmeans = lambda ad, fn: fn(ad.X, ad.obs[_LABELS])
     87 silhouette_label = lambda ad, fn: fn(ad.X, ad.obs[_LABELS])
---> 88 clisi_knn = lambda ad, fn: fn(ad.obsp["90_distances"], ad.obs[_LABELS])
     89 graph_connectivity = lambda ad, fn: fn(ad.obsp["15_distances"], ad.obs[_LABELS])
     90 silhouette_batch = lambda ad, fn: fn(ad.X, ad.obs[_LABELS], ad.obs[_BATCH])

File ~/.conda/envs/ju/lib/python3.9/site-packages …

**@mbuttner:** Hi, thank you for reporting this issue. I saw this usually happening when one used a subset of the populations without recomputing or extending the neighborhood graph. I hope that helps.

**@sebastianbirk:** I also ran into this issue in a case where some cells have additional neighbors (other than themselves) with distance 0. Adding a tiny value to the distances of those neighbors as follows resolved the issue:

```
neigh_output = pynndescent(
    adata.obsm[latent_key],
    n_neighbors=n_neighbors,
    random_state=random_state,
    n_jobs=n_jobs)
indices, distances = neigh_output.indices, neigh_output.distances

row_idx = np.where(distances == 0)[0]
col_idx = np.where(distances == 0)[1]
new_row_idx = row_idx[np.where(row_idx != indices[row_idx, col_idx])[0]]
new_col_idx = col_idx[np.where(row_idx != indices[row_idx, col_idx])[0]]
distances[new_row_idx, new_col_idx] = (distances[new_row_idx, new_col_idx] +
                                       np.nextafter(0, 1, dtype=np.floa …

**@ManarHashemTaha:** > I also ran into this issue in a case where some cells have additional neighbors (other than themselves) with distance 0. Adding a tiny value to the distances of those neighbors as follows resolved the issue:
>
> ```
> neigh_output = pynndescent(
>     adata.obsm[latent_key],
>     n_neighbors=n_neighbors,
>     random_state=random_state,
>     n_jobs=n_jobs)
> indices, distances = neigh_output.indices, neigh_output.distances
>
> row_idx = np.where(distances == 0)[0]
> col_idx = np.where(distances == 0)[1]
> new_row_idx = row_idx[np.where(row_idx != indices[row_idx, col_idx])[0]]
> new_col_idx = col_idx[np.where(row_idx != indices[row_idx, col_idx])[0]]
> distances[new_row_idx, new_col_idx] = (distances[new_row_idx, new_col_idx] +
> …

## #102: kBET colors are reversed?
**Issue:** #102 | **Last activity:** 2023-12-28T16:28:29Z
**State:** closed | **Author:** @andrewdchen | **Comments:** 1 | **Created:** 2023-08-15 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/102

### Report

Thanks for putting this package together! I have been using it in my own analysis of scRNAseq data. I just noticed that the kBET colors in the plotted table should be reversed? ([Example](https://scib-metrics.readthedocs.io/en/stable/_images/a01bae5e038ea8764ac529f1d66cfe30be9ebcf2bdf65f396917f80a1c6007da.png))

High values indicate high average rejection rate of the null hypothesis: batch distribution in a local neighborhood ~ batch distribution in a random neighborhood. So for a batch correction metric, low kbet values should be green instead of purple?

### Version information

_No response_

**@adamgayoso:** In this package, we use the non-rejection rate (colloquially the acceptance rate, though you can only reject the null hypothesis). See here

https://github.com/YosefLab/scib-metrics/blob/5681f7ef6b6d4cfd04fda90d1d33fab1dbe1bb50/src/scib_metrics/_kbet.py#L93

and here

https://github.com/YosefLab/scib-metrics/blob/5681f7ef6b6d4cfd04fda90d1d33fab1dbe1bb50/src/scib_metrics/_kbet.py#L131

## #96: ARPACK error when running `metrics.benchmark`
**Issue:** #96 | **Last activity:** 2023-12-28T16:27:59Z
**State:** closed | **Author:** @mairi-mcclean | **Comments:** 1 | **Created:** 2023-07-06 | **Labels:** bug | **URL:** https://github.com/YosefLab/scib-metrics/issues/96

### Report

Hello! Not sure if "bug" is the correct label, but it's an error I've been dealing with for a few days.

I am trying to optimise an scVI model for data integration, and using the `metrics.benchmark` to assess the different manifolds.

When I run:

```
bm = Benchmarker(adata,
                 batch_key="dataset",
                 label_key=['Model_1', 'Model_2', 'Model_3'],
                 embedding_obsm_keys=["X_scVI_1", "X_scVI_2", "X_scVI_3"],
                 n_jobs=6,
                 )
bm.benchmark()
```

I get the following output:

```
** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
[/Users/mairi.mcclean/mambaforge/envs/scvi_sccaf_local/lib/python3.8/site-packages/scanpy/preprocessing/_pca.py:283](https://file+.vscode-resource.vscode-cdn.net/Users/mairi.mcclean/mambaforge/envs/scvi_sccaf_local/lib/python3.8/site-packages/scanpy/preprocessing/_pca.py:283): RuntimeWarning: invalid value encountered in subtract
  return Xdot(x) - mdot(x)
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter number  4 had an illegal value
 ** On entry to SLASCL parameter num …

**@adamgayoso:** The issue has to do with scanpy pca. So I'd ensure scanpy pca works on your data

## #126: How to check if scib is using GPU accelerator?
**Issue:** #126 | **Last activity:** 2023-12-28T16:24:51Z
**State:** closed | **Author:** @zhenxingjian | **Comments:** 1 | **Created:** 2023-11-29 | **Labels:** enhancement | **URL:** https://github.com/YosefLab/scib-metrics/issues/126

### Description of feature

I would like to ask how can we check if scib is using GPU?

**@adamgayoso:** You can check utilization at the system level with `nvidia-smi`, but also if you run

```
import jax
jax.devices()
```

you should see a cuda device.

In general, if jax is using the gpu then this package will as well.
