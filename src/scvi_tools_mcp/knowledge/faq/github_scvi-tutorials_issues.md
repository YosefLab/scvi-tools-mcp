# scverse/scvi-tutorials GitHub Issues Q&A

35 issues (open and closed, bots excluded) from scverse/scvi-tutorials with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; issues are only removed once they age out of that window.

## #273: Switch from using scrublet package to scanpy version
**Issue:** #273 | **Last activity:** 2026-07-28T06:43:50Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-04-03 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/273

**@ori-kron-wis:** exists in:
- scarches_scvi_tools
- totalvi_reference_mapping

## #356: Scbasset tutorial is not working due to connections issues in ucsc
**Issue:** #356 | **Last activity:** 2026-02-25T12:36:52Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 2 | **Created:** 2024-09-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/356

atac/scbasset.ipynb & atac/scbasset_batch.ipynb  used to run on Berkeley workstations, and it is also working running it locally, but it is not working now from WIS workstations due to some connectivity issues with UCSC.

For now we can upload running it localy


<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
File ~/.conda/envs/scvi/lib/python3.11/site-packages/mysql/connector/connection_cext.py:339, in CMySQLConnection._open_connection(self)
    337         self.converter.str_fallback = self._converter_str_fallback
    338 except MySQLInterfaceError as err:
--> 339     raise get_mysql_exception(
    340         msg=err.msg, errno=err.errno, sqlstate=err.sqlstate
    341     ) from err
    343 self._do_handshake()
    345 if (
    346     not self._ssl_disabled
    347     and hasattr(self._cmysql, "get_ssl_cipher")
   (...)
    352
    353     # `get_ssl_cipher()` returns the name of the cipher being used.

DatabaseError: 2003 (HY000): Can't connect to MySQL server on 'genome-mysql.soe.ucsc.edu:3306' (110)
```

#### Versions:

1.2

**@ori-kron-wis:** didn't work with other genome providers as well.

**@ori-kron-wis:** see https://github.com/scverse/scvi-tools/issues/3253

## #213: Support running R tutorials
**Issue:** #213 | **Last activity:** 2025-12-10T09:33:58Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-22 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/213

Requires building an R Docker container with the required dependencies and figuring out if `nbconvert` works with R notebooks (or otherwise find an alternative to run R notebooks top to bottom).

## #494: > We see that B cells, despite being low for DE attributed to COVID, are enriched in COVID patients.
**Issue:** #494 | **Last activity:** 2025-12-08T07:46:24Z
**State:** closed | **Author:** @canergen | **Comments:** 1 | **Created:** 2025-11-26 | **URL:** https://github.com/scverse/scvi-tutorials/issues/494

> We see that B cells, despite being low for DE attributed to COVID, are enriched in COVID patients.

To me, the two B cell clusters do not appear to have a higher density of red dots than any other cell type cluster.

<img width="860" height="838" alt="Image" src="https://github.com/user-attachments/assets/47d2a6eb-7eae-45a4-9f71-bdd83d2dc5f9" />

What is this example trying to convey to the reader?

_Originally posted by @DarioS in https://github.com/scverse/scverse-tutorials/issues/253_

@ori-kron-wis we should change plot to sort_order False and likely remove the comment and display a violin plot by cell-type similar to the manuscript.

**@ori-kron-wis:** added here: https://github.com/scverse/scvi-tutorials/pull/496

The effect of B-cells should be clearer (I removed the comment), and match the DE

<img width="693" height="663" alt="Image" src="https://github.com/user-attachments/assets/dfe04b55-e601-4dc3-b8a4-c498690718e3" />

<img width="764" height="668" alt="Image" src="https://github.com/user-attachments/assets/e7760616-a0cc-476c-a586-3cc5ecea31a2" />

## #357: DestVI tutorial is not running
**Issue:** #357 | **Last activity:** 2025-11-26T15:16:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2024-09-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/357

There is several logic issues with the current destVI version tutorial that need to be taken care of.

There is something wrong there towards end of tutorial, every step starting destvi_utils.explore_gamma_space is not working

```python

---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[28], line 1
----> 1 destvi_utils.explore_gamma_space(st_model,sc_model,ct_list=ct_list,ct_thresholds=ct_thresholds)

File /usr/local/lib/python3.12/site-packages/destvi_utils/_destvi_utils.py:295, in explore_gamma_space(st_model, sc_model, st_adata, ct_thresholds, output_file, ct_list, key_proportions, key_spatial)
    291 sc_adata_slice = sc_adata[
    292     sc_adata.obs[sc_model.registry_["setup_args"]["labels_key"]] == name_ct
    293 ].copy()
    294 is_sparse = issparse(sc_adata_slice.X)
--> 295 normalized_counts = sc_adata_slice.X.A if is_sparse else sc_adata_slice.X
    296 indices_ct = np.where(
    297     sc_adata.obs[sc_model.registry_["setup_args"]["labels_key"]] == name_ct
    298 )[0]
    300 sc_latent = sc_model.get_latent_representation(indices=indices_ct)

AttributeError: 'csr_matrix' object has no attribute 'A'
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[Paste the error output produced by the above code here]
```

#### Versions:
1.2

**@ori-kron-wis:** We will wait for DestVI-v2 as @canergen suggested and will update tutorial then

## #492: MrVI Tutorial Fails on Large Data
**Issue:** #492 | **Last activity:** 2025-11-22T23:34:38Z
**State:** closed | **Author:** @DarioS | **Comments:** 2 | **Created:** 2025-11-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/492

The journal article claims that MrVI scales to hundreds of samples. Doesn't seem to, though.

```python
>>> sc.pp.highly_variable_genes(adata, n_top_genes = 4000)
scipy/sparse/_data.py:144: RuntimeWarning: overflow encountered in expm1
Traceback (most recent call last):
...        ...
ValueError: cannot specify integer `bins` when input data contains infinity
```

`adata` has 975 patients and 2.7 million cells.

```python
>>> adata
AnnData object with n_obs × n_vars = 2690210 × 38592
```

**@canergen:** Hi. Please check your input data and consider changing the flavor for highly variable genes in **scanpy**. Rest assured highly variable genes works on 100 million cells. However, this is not an issue of MrVI (you are not even calling it in your snippet). For 1000 samples, you might need to consider downstream analysis after generating the sample-sample distances though and summarize distances across cells (otherwise this matrix is n_cellsXn_samplesXn_samples).

**@DarioS:** Ah, I copied `flavor = "seurat_v3"` and then it was fine. Perhaps tutorial could explain reasons for non-default values.

## #480: sceasy outdated
**Issue:** #480 | **Last activity:** 2025-11-03T13:34:00Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 6 | **Created:** 2025-09-18 | **URL:** https://github.com/scverse/scvi-tutorials/issues/480

I think the `sceasy` is no longer up to date with recent Seurat developments ([see this issue](https://github.com/cellgeni/sceasy/issues/98)).

This may be issue for this [tutorial](https://docs.scvi-tools.org/en/1.0.0/tutorials/notebooks/scvi_in_R.html).
I did not try it out exactly as I do not have all packages installed, but I followed your example for converting on a different seurat object (see above issue).

**@ori-kron-wis:** We need to make sure all R tutorials are working. All of them use sceasy BTW.

**@Hrovatin:** I was trying a few packages recently, and it seems `zellkonverter` was most up to date - if that helps.

**@canergen:** Please use anndataR. We are well connected with the developers and it’s an R native solution, which makes it less likely to break. However, there’a currently no MuData and AnnData Zarr support. The first one might be an issue - is there an R totalVI tutorial?

**@Hrovatin:** Thank you for the suggestion - I did not know about that package before.

Re installation, that may be a bit more complicated as it requires R4.5 which is not yet on conda (will be hopefully soon).

**@ori-kron-wis:** relates to https://github.com/scverse/scvi-tutorials/issues/213

**@ori-kron-wis:** The SeuratV5 issue is real, but I can confirm that all R tutorials can still work with the latest Seurat and scVI-tools (with sceasy).

There was a need for minor updates to the tutorials to use `UpdateSeuratObject`, a different way to load and save files, and how to use reticulate, but other than that, and the fact that it's not trivial to ramp up an environment to run all of these tutorials, it's working. see: https://github.com/scverse/scvi-tutorials/pull/487

Im saying let's keep the tutorials we have now (with the new adjustments) and move on to work with anndataR, but with new tutorials; potentially with no need for Seurat at all. It will be too complex to change what we have now to anndataR; better to do it from scratch, in a new PR.

## #435: #2 DestVI tutorial is not running
**Issue:** #435 | **Last activity:** 2025-11-03T07:48:07Z
**State:** closed | **Author:** @lordy5 | **Comments:** 2 | **Created:** 2025-05-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/435

<!-- Describe the bug -->

I get an AttributeError when calling explore_gamma_space caused by the fact that the code uses append on a dataframe, which is no longer supported. I think this is caused by scvi version 1.3.0 using a newer pandas version.

<!-- To reproduce -->

```python
destvi_utils.explore_gamma_space(st_model, sc_model, ct_list=ct_list, ct_thresholds=ct_thresholds)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
[<ipython-input-30-ceebccb51f08>](https://localhost:8080/#) in <cell line: 0>()
----> 1 destvi_utils.explore_gamma_space(st_model, sc_model, ct_list=ct_list, ct_thresholds=ct_thresholds)

3 frames
[/usr/local/lib/python3.11/dist-packages/destvi_utils/_destvi_utils.py](https://localhost:8080/#) in explore_gamma_space(st_model, sc_model, st_adata, ct_thresholds, output_file, ct_list, key_proportions, key_spatial)
    338                     ranking = ranking[::-1]
    339                 gl = list(st_adata.var.index[ranking[:50]])
--> 340                 enr = gseapy.enrichr(
    341                     gene_list=gl,
    342                     description="pathway",

[/usr/local/lib/python3.11/dist-packages/gseapy/enrichr.py](https://localhost:8080/#) in enrichr(gene_list, gene_sets, organism, description, outdir, background, cutoff, format, figsize, …

**@ori-kron-wis:** Not related to scvi-version, as this point in tutorials fails for long time and relates to a fix needed in https://github.com/YosefLab/destvi_utils (possibly to package updates and CI/CD).
We can put this part of tutorial under comment for now

**@ori-kron-wis:** duplicate

## #399: MrVI tutorial for 1K+ samples
**Issue:** #399 | **Last activity:** 2025-10-15T07:45:25Z
**State:** closed | **Author:** @PierreBoyeau | **Comments:** 1 | **Created:** 2025-02-15 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/399

We need to add a tutorial to guide the usage of MrVI for large single-cell RNA-seq datasets containing 1K+ samples.
In particular, we should explain what hyperparameters users should be careful about.

**@ori-kron-wis:** It will be done over the Tahoe100M cells in the mrVI pyTorch version

## #460: ResolVI tutorial fails at query transfer step (load_query_data)
**Issue:** #460 | **Last activity:** 2025-07-15T08:04:06Z
**State:** closed | **Author:** @Ci-TJ | **Comments:** 1 | **Created:** 2025-07-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/460

<!-- Describe the bug -->

I followed the official tutorial to reproduce the code, but encountered the following errors during execution. It seems the issue occurs in `load_query_data`, possibly related to `torch.cat` trying to concatenate mismatched tensor sizes.

<!-- To reproduce -->

```python
query_adata.obs["predicted_celltype"] = "unknown"
query_adata.obs_names = [f"query_{i}" for i in query_adata.obs_names]

supervised_resolvi.prepare_query_anndata(query_adata, reference_model=supervised_resolvi)
query_resolvi = supervised_resolvi.load_query_data(query_adata, reference_model=supervised_resolvi)

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
INFO     Found 100.0% reference vars in query data.
D:\anaconda3\Lib\site-packages\scvi\data\fields\_dataframe_field.py:227: UserWarning: Category 66457 in adata.obs['_scvi_ind_x'] has fewer than 3 cells. Models may not train properly.
  new_mapping = _make_column_categorical(
---------------------------------------------------------------------------
RuntimeError                              Traceback (most recent call last)
Cell In[33], line 2
      1 supervised_resolvi.prepare_query_anndata(query_adata, reference_model=supervised_resolvi)
----> 2 query_resolvi = supervised_resolvi.load_query_data(query_adata, reference_model=supervised_resolvi, inplace_subset_query_vars=False)

File D:\anaconda3\Lib\site-pac …

**@ori-kron-wis:** Thank you @Ci-TJ , we are aware of this and it be resolved in the next version.
See: https://github.com/scverse/scvi-tools/pull/3417
You can install from this branch to solve it https://github.com/scverse/scvi-tools/tree/Ori-test-resolvi-scarches

## #122: Add scvi-criticism tutorial
**Issue:** #122 | **Last activity:** 2025-05-29T11:58:55Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 1 | **Created:** 2023-05-24 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/122

The plotting code can live here for now, let's use hugging face to pull the model and make sure it runs in colab.

**@ori-kron-wis:** We added a user guide doc in scvi-tools RTD

## #434: DestVI tutorial is not running
**Issue:** #434 | **Last activity:** 2025-05-28T10:56:32Z
**State:** closed | **Author:** @lordy5 | **Comments:** 2 | **Created:** 2025-05-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/434

<!-- Describe the bug -->

I get an AttributeError when calling the explore gamma space method towards the end of the notebook.

The error occurs because X is sparse and the method tries to convert it to a dense matrix using X.A, but this doesn't work for a CSR matrix. I can get around the error for now by just converting X to a dense matrix before calling the explore_gamma_space method. However, maybe the code should be updated to include the CSR matrix case.

<!-- To reproduce -->

```python
destvi_utils.explore_gamma_space(st_model, sc_model, ct_list=ct_list, ct_thresholds=ct_thresholds)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
[<ipython-input-28-ceebccb51f08>](https://localhost:8080/#) in <cell line: 0>()
----> 1 destvi_utils.explore_gamma_space(st_model, sc_model, ct_list=ct_list, ct_thresholds=ct_thresholds)

[/usr/local/lib/python3.11/dist-packages/destvi_utils/_destvi_utils.py](https://localhost:8080/#) in explore_gamma_space(st_model, sc_model, st_adata, ct_thresholds, output_file, ct_list, key_proportions, key_spatial)
    293         ].copy()
    294         is_sparse = issparse(sc_adata_slice.X)
--> 295         normalized_counts = sc_adata_slice.X.A if is_sparse else sc_adata_slice.X
    296         indices_ct = np.where(
    297             sc_adata.ob …

**@lordy5:** Just realized there is an identical issue already. Keeping this for now since it has a workaround included.

**@ori-kron-wis:** closing, a replicate of https://github.com/scverse/scvi-tutorials/issues/357

## #433: PeakVI tutorial is not running
**Issue:** #433 | **Last activity:** 2025-05-28T10:26:31Z
**State:** closed | **Author:** @lordy5 | **Comments:** 1 | **Created:** 2025-05-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/433

<!-- Describe the bug -->

I get a TypeError when calling the differential accessibility method, that seems to be caused by using the two_sided parameter.

<!-- To reproduce -->

```python
# (1.1) using a known factor to compare two clusters
## two-sided is True by default, but included here for emphasis
da_res11 = model.differential_accessibility(
    groupby=PEAKVI_CLUSTERS_KEY, group1="3", group2="0", two_sided=True
)

# (1.2) using a known factor to compare a cluster against all other clusters
## if we only provide group1, group2 is all other cells by default
da_res12 = model.differential_accessibility(
    groupby=PEAKVI_CLUSTERS_KEY, group1="3", two_sided=False
)

# (2.1) using indices to compare two clusters
## we can use boolean masks or integer indices for the `idx1` and `idx2` arguments
da_res21 = model.differential_accessibility(
    idx1=adata.obs[PEAKVI_CLUSTERS_KEY] == "3",
    idx2=adata.obs[PEAKVI_CLUSTERS_KEY] == "0",
    two_sided=True,
)
# (2.2) using indices to compare a cluster against all other clusters
## if we don't provide idx2, it uses all other cells as the contrast
da_res22 = model.differential_accessibility(
    idx1=np.where(adata.obs[PEAKVI_CLUSTERS_KEY] == "3"),
    two_sided=False,
)

da_res22.head()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent ca …

**@ori-kron-wis:** relates to https://github.com/scverse/scvi-tools/pull/3139/files

need to replace two_sided with test_mode="two", where is was true (already done)

@canergen suggested to remove this part completely and do volcano plot

## #445: totalVI tutorial is not running
**Issue:** #445 | **Last activity:** 2025-05-28T10:25:54Z
**State:** closed | **Author:** @lordy5 | **Comments:** 1 | **Created:** 2025-05-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/445

<!-- Describe the bug -->

When creating a dendrogram with scipy towards the end of the notebook, I get an ImportError related to not being able to import the name 'size'.

<!-- To reproduce -->

```python
sc.tl.dendrogram(rna, groupby=TOTALVI_CLUSTERS_KEY, use_rep=TOTALVI_LATENT_KEY)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
[<ipython-input-37-6b8fd6b16633>](https://localhost:8080/#) in <cell line: 0>()
----> 1 sc.tl.dendrogram(rna, groupby=TOTALVI_CLUSTERS_KEY, use_rep=TOTALVI_LATENT_KEY)
      2 # This is a bit of a hack to be able to use scanpy dendrogram with the protein data
      3 protein.obs[TOTALVI_CLUSTERS_KEY] = rna.obs[TOTALVI_CLUSTERS_KEY]
      4 protein.obsm[TOTALVI_LATENT_KEY] = rna.obsm[TOTALVI_LATENT_KEY]
      5 sc.tl.dendrogram(protein, groupby=TOTALVI_CLUSTERS_KEY, use_rep=TOTALVI_LATENT_KEY)

3 frames
[/usr/local/lib/python3.11/dist-packages/legacy_api_wrap/__init__.py](https://localhost:8080/#) in fn_compatible(*args_all, **kw)
     80         def fn_compatible(*args_all: P.args, **kw: P.kwargs) -> R:
     81             if len(args_all) <= n_positional:
---> 82                 return fn(*args_all, **kw)
     83
     84             args_pos: P.args

[/usr/local/lib/python3.11/dist-packages/scanpy/tools/_dendrogram.py](https://localhost:8080/ …

**@ori-kron-wis:** I ran with scipy 1.14.1, scanpy 1.11.1 and it worked.
But also github runner succeeded (after a small fix).

## #432: Atlas level integration of lung data tutorial is not running
**Issue:** #432 | **Last activity:** 2025-05-28T04:45:20Z
**State:** closed | **Author:** @lordy5 | **Comments:** 1 | **Created:** 2025-05-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/432

<!-- Describe the bug -->

There is a RuntimeError when using the Benchmarker from the scib-metrics package towards the end of the notebook.

Using ```os.environ["JAX_PLATFORMS"] = "cpu"``` seems to fix the issue but not sure if this is a good solution.

<!-- To reproduce -->

```python
bm = Benchmarker(
    adata,
    batch_key="batch",
    label_key="cell_type",
    embedding_obsm_keys=["X_pca", SCVI_LATENT_KEY, SCANVI_LATENT_KEY],
    n_jobs=-1,
)
bm.benchmark()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
XlaRuntimeError                           Traceback (most recent call last)
[/usr/local/lib/python3.11/dist-packages/jax/_src/xla_bridge.py](https://localhost:8080/#) in backends()
    895
--> 896         backend = _init_backend(platform)
    897         _backends[platform] = backend

21 frames
XlaRuntimeError: INVALID_ARGUMENT: Unexpected PJRT_Client_Create_Args size: expected 88, got 72. The plugin is likely built with a later version than the framework. This plugin is built with PJRT API version 0.67.

During handling of the above exception, another exception occurred:

RuntimeError                              Traceback (most recent call last)
[/usr/local/lib/python3.11/dist-packages/jax/_src/xla_bridge.py](https://localhost:8080/#) in backends()
    910           else:
    911             err_msg += " (you may need to uninstall the …

**@lordy5:** This error no longer occurs

## #267: Add VELOVI tutorial
**Issue:** #267 | **Last activity:** 2025-05-13T13:47:02Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-03-11 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/267

https://github.com/YosefLab/velovi/blob/main/docs/tutorial.ipynb

cc @adamgayoso and @WeilerP

**@martinkim0:** New tutorial should ideally address https://github.com/YosefLab/velovi/issues/19, https://github.com/YosefLab/velovi/issues/15, and https://github.com/YosefLab/velovi/issues/18

## #293: Add tutorial with custom Census dataloader
**Issue:** #293 | **Last activity:** 2025-05-13T13:46:54Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-10 | **URL:** https://github.com/scverse/scvi-tutorials/issues/293

## #266: Rewrite autotune tutorials
**Issue:** #266 | **Last activity:** 2025-02-25T10:28:15Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-27 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/266

https://github.com/scverse/scvi-tools/pull/2561

**@canergen:** @ori-kron-wis Close this?

## #358: logic issue with tangram_scvi_tools tutorial
**Issue:** #358 | **Last activity:** 2024-09-30T17:11:32Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/358

spatial/tangram_scvi_tools.ipynb is not running to some logic issue with mudata:


<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
InvalidIndexError                         Traceback (most recent call last)
Cell In[12], line 8
      6 mdata.mod["sp_train"] = mdata.mod["sp"][:, genes].copy()
      7 mdata.mod["sc_train"] = mdata.mod["sc"][:, genes].copy()
----> 8 mdata.update()

File /usr/local/lib/python3.12/site-packages/mudata/_core/mudata.py:1725, in MuData.update(self)
   1719 def update(self):
   1720     """
   1721     Update both .obs and .var indices of MuData with the data from all the modalities
   1722
   1723     NOTE: From v0.4, it will not pull columns from modalities by default.
   1724     """
-> 1725     self.update_var()
   1726     self.update_obs()

File /usr/local/lib/python3.12/site-packages/mudata/_core/mudata.py:1531, in MuData.update_var(self)
   1527 """
   1528 Update global .var_names according to the .var_names of all the modalities.
   1529 """
   1530 join_common = self.axis == 0
-> 1531 self._update_attr("var",axis=0,join_common=join_common)

File /usr/local/lib/python3.12/site-packages/mudata/_core/mudata.py:579, in MuData._update_attr(self, attr, axis, **kwargs)
    577     if "join_common" in kwargs:
    578         join_common = kwargs.pop("join_common")
--> 579     self._update_at …

## #355: Cellassign tutorial is not working due to gdrive permissions
**Issue:** #355 | **Last activity:** 2024-09-30T15:48:54Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 3 | **Created:** 2024-09-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/355

Cellassign tutorial was used to work on Berkeley workstations, but now from WIS it has a permission error to access gdrive to fetch the data.
One possible solution is to re create those files:

To demonstrate CellAssign, we use the data from the original publication, which we converted into h5ad format. The data are originally available from here:

https://zenodo.org/record/3372746


<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
File /usr/local/lib/python3.12/site-packages/gdown/download.py:278, in download(url, output, quiet, proxy, speed, use_cookies, verify, id, fuzzy, resume, format, user_agent, log_messages)
    268     except FileURLRetrievalError as e:
    269         message = (
    270             "Failed to retrieve file url:\n\n{}\n\n"
    271             "You may still be able to access the file from the browser:"
   (...)
    276             url_origin,
    277         )
--> 278         raise FileURLRetrievalError(message)
    280 filename_from_url = None
    281 last_modified_time = None

FileURLRetrievalError: Failed to retrieve file url:

	Cannot retrieve the public link of the file. You may need to change
	the permission to 'Anyone with the link', or have had many accesses.
	Check FAQ in https://github.com/wkentaro/gdown?tab=readme-ov-file#faq.

You may still be able to access the file from the browser:

	https://drive.google.com/uc?id=10l6m2KKKioCZnQlRHomheappHh-jTFmx

but …

**@ori-kron-wis:** The original files in Zenodo (https://zenodo.org/record/3372746) are in R and we need to convert them to h5ad somehow. I tried different methods but none worked (zellkonverter <-> SingleCellExperiment). Also, I was looking for those temp files downloaded from gdrive in s133 during the run, but no luck either. I also tried to run the tutorial myself on s133 and gdrive was restricted again but this was from my user, I couldn't do it from Martin's (not sure it will help either).

So we kinda stuck with no files for this tutorial.

**@adamgayoso:** I believe they should be accessible as done here:

https://yoseflab.github.io/scvi-tools-reproducibility/cell_assign_hgsc_and_follicular_data/

**@ori-kron-wis:** thanks, this is what I was looking for

## #281: Quick Start Tutorial Code Error
**Issue:** #281 | **Last activity:** 2024-09-26T07:47:30Z
**State:** closed | **Author:** @DrNamwob | **Comments:** 1 | **Created:** 2024-05-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/281

<!-- Describe the bug -->
In the quickstart tutorial, scvi.settings.seed = 0 should be:

scvi._settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)

I apologize if my issue / bug reporting is not in the correct format. Completely new to this field. Just trying my best to help out.

<img width="606" alt="image" src="https://github.com/scverse/scvi-tutorials/assets/136391240/720c1d25-d3d8-44f6-a075-f9b7082fd9d5">
<img width="948" alt="image" src="https://github.com/scverse/scvi-tutorials/assets/136391240/befa2946-6592-455b-9bc8-55c4b9f85e0d">

**@ori-kron-wis:** Hi @DrNamwob it is true the file is called _settings.py as this is the very basic internal settings of scvi, but the actual handler to this settings class in this file is called settings, which is initialized during scvi import. So the tutorial is fine.

What version are you using? How did you install the package?
(might be that under conda env we do experience such issues)

Thanks

## #313: Fix the progress bar during training models trough tout the tutorials
**Issue:** #313 | **Last activity:** 2024-09-04T06:58:53Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-08-28 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/313

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

We would like to be able to show the tqdm progress bar in our RTD , but not as it shown now where every epoch is shown interactively. We do want to keep the bottom line of training bar.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

We would want to re check the custom progress bar code . the reason that code exists is because the docs used to not render the tqdm notebook mode and it used to be that when you saved a jupyter notebook and reopened the fancier progress bar disappears
Not sure if it’s still a problem

## #294: Update scArches tutorials to discuss encode_covariates
**Issue:** #294 | **Last activity:** 2024-09-02T11:47:08Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-12 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/294

https://github.com/scverse/scvi-tools/issues/2331

## #272: reference mapping
**Issue:** #272 | **Last activity:** 2024-08-28T07:04:47Z
**State:** closed | **Author:** @Sirin24 | **Comments:** 4 | **Created:** 2024-03-20 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/272

i am following https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scarches_scvi_tools.html#reference-mapping-with-scanvi

>>> import os
>>> import tempfile
>>> import anndata
>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> import pandas as pd
>>> import scanpy as sc
>>> import scrublet as scr
>>> import scvi
>>> import seaborn as sns
>>> import torch

>>> scvi_model = SCVI(adata, **arches_params)
Traceback (most recent call last):
  File "<string>", line 1, in <module>
NameError: name 'SCVI' is not defined

**@martinkim0:** Oh, I think we have a typo in that code block. It should be:
```
scvi_model = scvi.model.SCVI(adata, **arches_params)
```
Thanks for bringing this up!

**@Sirin24:** thank you for the fast response. i want to ask another question regarding the same vignette.
why we trained the model without normalizing, logP or scaling the the reference ?

**@martinkim0:** Hi, this is because scVI and scANVI expect the input to be raw counts. This is necessary because the generative portions of the models use distributions that only support non-negative integers (Poisson and negative binomial).

**@ori-kron-wis:** there is currently a bug in https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scarches_scvi_tools.html#reference-mapping-with-scanvi for v1.1.x that will be solved in v1.2.x

see
https://github.com/scverse/scvi-tools/issues/2934

## #210: Release 1.1.0
**Issue:** #210 | **Last activity:** 2024-04-10T21:39:38Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tutorials/issues/210

### atac

- [x] PeakVI #236
- [x] PoissonVI #235
- [ ] scbasset_batch https://github.com/scverse/scvi-tutorials/actions/runs/7876877984/job/21491824752#step:5:186
- [ ] scbasset

### dev

- [x] data_tutorial #237
- [x] model_user_guide #238
- [x] module_user_guide #239

### hub

- [x] minification #242
- [x] scvi_hub_intro_and_download #240
- [x] scvi_hub_upload_and_large_files #241

### multimodal

- [x] cite_scrna_integration_w_totalVI #243
- [x] MultVI_tutorial #244
- [x] totalVI_reference_mapping #248
- [x] totalVI #245

### quick_start

- [x] api_overview #246
- [x] data_loading #247

### scrna

- [x] amortized_lda #251
- [x] AutoZI_tutorial #249
- [x] cellassign_tutorial #250
- [x] contrastiveVI_tutorial #255
- [x] harmonization #252
- [x] linear_decoder #253
- [x] query_hlca_knn #254
- [ ] scarches_scvi_tools https://github.com/scverse/scvi-tutorials/actions/runs/7875696105/job/21488129760#step:5:391
- [x] scanvi_fix #256
- [x] scVI_DE_worm #258
- [x] seed_labeling #257
- [x] tabula_muris #260

### spatial

- [ ] cell2location_lymph_node_spatial_tutorial https://github.com/scverse/scvi-tutorials/actions/runs/7875700829/job/21488144818#step:5:142
- [ ] DestVI_tutorial https://github.com/scverse/scvi-tutorials/actions/runs/7875702231/job/21488150334#step:5:123
- [x] gimvi_tutorial #259
- [x] stereoscope_heart_LV_tutorial #261
- [ ] tangram_scvi_tools https://github.com/scverse/scvi-tutorials/actions/runs/7875705031/job …

## #174: Address Pandas compat error in Hub intro tutorial
**Issue:** #174 | **Last activity:** 2024-02-02T17:23:52Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/174

https://github.com/scverse/scvi-tutorials/actions/runs/7120160533/job/19386836764

## #157: setting seed=0 could not reproduce same UMAP embeddings
**Issue:** #157 | **Last activity:** 2024-01-22T19:51:22Z
**State:** closed | **Author:** @Lijunyao8 | **Comments:** 1 | **Created:** 2023-10-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/157

<!-- Describe the bug -->

[TEXT HERE]

<!-- To reproduce [-->]([url]([url](url)))

```python
scvi.settings.seed = 0
subcluster_res = 0.8

sca.models.SCVI.setup_anndata(t_adata,
                             layer = 'counts',
                             batch_key=batch_key,
                             continuous_covariate_keys=['percent_mt'],
                             #categorical_covariate_keys=['USUBJID']
                             )

vae = sca.models.SCVI(t_adata,
                      n_layers=2,
                      n_latent=30,
                      dispersion = 'gene-batch',
                      gene_likelihood="nb"
                     )

vae.train(use_gpu=True, #train_size=0.8,
           early_stopping= True,
#            lr_patience=20,
           max_epochs=100,
           early_stopping_monitor = 'elbo_validation',
           plan_kwargs={"n_epochs_kl_warmup":25}
           )
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
![Screen Shot 2023-10-11 at 3 16 19 PM](https://github.com/scverse/scvi-tutorials/assets/32940798/d8541730-93dc-4a04-8b4f-add3740656cb)

[Paste the error output produced by the above code here]
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION

<!-- Relevant screenshots -->

**@Lijunyao8:** I got different UMAP embeddings everytime I run scVI even if I don’t change any code. Is that what I should expect? or there is a parameter where I can set? I guess the deafult seeding is 0, right? so theoretically it should reproduce results everytime? scvi.settings.seed = 0 Thank you!

## #38: new rna + protein dataset
**Issue:** #38 | **Last activity:** 2024-01-22T19:51:01Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2021-11-22 | **URL:** https://github.com/scverse/scvi-tutorials/issues/38

https://figshare.com/projects/Single-cell_proteo-genomic_reference_maps_of_the_human_hematopoietic_system/94469

https://www.nature.com/articles/s41590-021-01059-0#Abs1

## #116: use cellxgene census in tutorials
**Issue:** #116 | **Last activity:** 2024-01-22T19:50:57Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2023-05-04 | **URL:** https://github.com/scverse/scvi-tutorials/issues/116

https://chanzuckerberg.github.io/cellxgene-census/index.html

## #77: multimodal integrated dataset from multiVI on tutorial of Joint analysis of paired and unpaired multiomic data with MultiVI
**Issue:** #77 | **Last activity:** 2024-01-22T19:50:51Z
**State:** closed | **Author:** @yulijia | **Comments:** 0 | **Created:** 2022-09-16 | **URL:** https://github.com/scverse/scvi-tutorials/issues/77

Hi,

I have a question about the `MULTIVI.get_latent_representation` on the tutorials of [Joint analysis of paired and unpaired multiomic data with MultiVI](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/MultiVI_tutorial.html).

Follow the tutorial, I run my demo data with multiVI and get the latent space matrix  via `get_latent_representation` function.
My latent representation result includes 3 times the total cells of my original datasets ( original 1000 cells, latent space 3000 cells).
I think that may be because for the multiVI we concatenate 3 anndata
`adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired, adata_rna, adata_atac)`.
If I want to get the multimodal integrated dataset from multiVI, should I only use the first 1000 rows (in my example) as the integrated result of RNA and ATAC modality?

## #41: gene length
**Issue:** #41 | **Last activity:** 2024-01-22T19:50:36Z
**State:** closed | **Author:** @ZeitgeberH | **Comments:** 0 | **Created:** 2022-02-03 | **URL:** https://github.com/scverse/scvi-tutorials/issues/41

Hello,
I am trying to follow the tutorial "Integration and label transfer with Tabula Muris" in which you provided a text file for gene length.
The total number of genes is about 20k.
However my sequencing data has about 30k genes. I trying to get an estimate of those gene's length by looking at them in the gtf reference file i used. The length of gene does not match with that in your file.
Could you provide more details on how you calculate gene length.
Thanks very much!

## #92: Write a CI workflow to ensure that notebooks only have one # level heading
**Issue:** #92 | **Last activity:** 2024-01-22T19:50:17Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2023-01-13 | **URL:** https://github.com/scverse/scvi-tutorials/issues/92

## #209: Release 1.1.0-rc.1
**Issue:** #209 | **Last activity:** 2023-12-07T22:57:20Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2023-12-07 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tutorials/issues/209

### atac

- [x] PeakVI #165
- [x] PoissonVI #179
- [x] scbasset_batch #166
- [ ] scbasset https://github.com/scverse/scvi-tutorials/actions/runs/7133507513

### dev

- [x] data_tutorial #180
- [x] model_user_guide #167
- [x] module_user_guide #168

### hub

- [x] minification #169
- [ ] scvi_hub_intro_and_download #174
- [x] scvi_hub_upload_and_large_files #170

### multimodal

- [x] cite_scrna_integration_w_totalVI #171
- [x] MultVI_tutorial #172
- [x] totalVI_reference_mapping #175
- [x] totalVI #176

### quick_start

- [x] api_overview #177
- [x] data_loading #178

### scrna

- [x] amortized_lda #181
- [x] AutoZI_tutorial #182
- [x] cellassign_tutorial #190
- [x] contrastiveVI_tutorial #204
- [x] harmonization #186
- [x] linear_decoder #183
- [x] query_hlca_knn #184
- [ ] scarches_scvi_tools https://github.com/scverse/scvi-tutorials/actions/runs/7133671731/job/19426842721
- [x] scVI_DE_worm #185
- [x] seed_labeling #187
- [x] tabula_muris #189

### spatial

- [ ] cell2location_lymph_node_spatial_tutorial https://github.com/scverse/scvi-tutorials/actions/runs/7122671576/job/19394075468
- [ ] DestVI_tutorial https://github.com/scverse/scvi-tutorials/actions/runs/7122672392/job/19394077690
- [x] gimvi_tutorial #199
- [x] stereoscope_heart_LV_tutorial #197
- [ ] tangram_scvi_tools https://github.com/scverse/scvi-tutorials/actions/runs/7122675417/job/19394086030

### tuning

- [x] autotune_new_mod …

**@martinkim0:** Remaining tutorials will be fixed and rerun for either 1.1.0-rc.2 or 1.1.0

## #132: Remove `use_gpu` in tutorials
**Issue:** #132 | **Last activity:** 2023-12-07T19:54:40Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-07-07 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/issues/132

## #123: Rerun scanvi tutorials that use subsampling
**Issue:** #123 | **Last activity:** 2023-12-07T19:53:29Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-05-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/issues/123

<!-- Describe the bug -->

[TEXT HERE]

<!-- To reproduce -->

```python
# Your code here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[Paste the error output produced by the above code here]
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION

<!-- Relevant screenshots -->
