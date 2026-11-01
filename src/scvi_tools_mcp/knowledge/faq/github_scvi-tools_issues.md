# scverse/scvi-tools GitHub Issues Q&A

411 issues (open and closed, bots excluded) from scverse/scvi-tools with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; issues are only removed once they age out of that window.

## #4086: log_nb_positive: float32 d(log_prob)/d(mu) carries 6-28% relative error and reaches exactly 0.0; logsigmoid rate terms fix it
**Issue:** #4086 | **Last activity:** 2026-10-30T05:08:19Z
**State:** open | **Author:** @mahdi-shafiei | **Comments:** 0 | **Created:** 2026-10-30 | **URL:** https://github.com/scverse/scvi-tools/issues/4086

## Versions

- scvi-tools 1.5.2 (PyPI), torch 2.15.0, scipy 1.18.1, CPython 3.12, Linux x86_64, CPU
- `log_nb_positive` is unchanged on `main` at 38b216a, `src/scvi/distributions/_negative_binomial.py` L111-147

## What happens

`log_nb_positive` — reached from the public `NegativeBinomial(mu=, theta=).log_prob()` via
`NegativeBinomial.log_prob` (L451-465) — forms the two rate terms by subtracting logarithms:

```python
log_theta_mu_eps = log(theta + mu + eps)
res = (
    theta * (log(theta + eps) - log_theta_mu_eps)
    + x * (log(mu + eps) - log_theta_mu_eps)     # <- nearly equal logs, then scaled by x
    + lgamma(x + theta) - lgamma(theta) - lgamma(x + 1)
)
```

In float32 this costs **the gradient**, not just some accuracy in the loss. `d log_prob / d mu`
depends only on those rate terms — the `lgamma` normalizer has no `mu` in it — so the subtraction
is the whole story for backprop:

| `x / theta` | scvi `dL/dmu` rel. error |
|---|---|
| 1e4 | 0.46% |
| 1e5 | **6.24%** |
| 1e6 | **27.88%** |
| ≥1e7 | **100%** — float32 returns exactly `0.0` where the true gradient is `-8.3e-09` |

Taking the same two terms from `F.logsigmoid(±logits)` instead makes the gradient error **0.00% at
every point on the grid**, including the ones above. That is what PyTorch's own
`torch.distributions.NegativeBinomial.log_prob` already does, so it is not a new technique.

The controlling quantity is `x / theta`, not `x` alone: the error is identical at `(x=1e4,
theta=0.1)`, `(1e5, 1.0)` and `( …

## #4071: SCBASSET training crashes on MPS: torchmetrics binary AUROC is broken for batches >= 65,536 logits
**Issue:** #4071 | **Last activity:** 2026-10-25T14:40:20Z
**State:** closed | **Author:** @AqibHasnain | **Comments:** 0 | **Created:** 2026-10-23 | **URL:** https://github.com/scverse/scvi-tools/issues/4071

### Report

`SCBASSET.train(accelerator="mps")` crashes or silently logs an AUROC of 0.0 on Apple Silicon once a batch's logits exceed roughly 65,536 elements. `SCBASSETModule.loss` computes `torchmetrics.functional.auroc(torch.sigmoid(logits).ravel(), target.int().ravel(), task="binary")` on the full `batch_size x n_cells` logits tensor, and that call is broken on MPS for large inputs.

Observed on a 98,507-region x 11,898-cell dataset with `batch_size=128` (1,522,944 logits per batch). Training aborts in the first epoch:

```
  File ".../scvi/external/scbasset/_module.py", in loss
    auroc = torchmetrics.functional.auroc(
  ...
  File ".../torchmetrics/functional/classification/roc.py", line 60, in _binary_roc_compute
    if fps[-1] <= 0:
torch.AcceleratorError: index -5259567894776221620 is out of bounds for dimension 0 with size 1522944
```

#### Minimal reproduction (no scvi-tools needed)

```python
import warnings
import torch
from torchmetrics.functional import auroc

warnings.filterwarnings("ignore")
torch.manual_seed(0)
for n in (65534, 66000, 100000, 1522944, 1522944):
    preds = torch.sigmoid(torch.randn(n))
    target = (torch.rand(n) < 0.05).int()
    cpu = auroc(preds, target, task="binary").item()
    try:
        mps = auroc(preds.to("mps"), target.to("mps"), task="binary").item()
    except Exception as e:
        mps = f"{type(e).__name__}: {e}"
    print(n, f"cpu={cpu:.4f}", f"mps={mps}")
```

Output:

```
65534 cpu=0.5007 mps=0.5006563663482666
66000 cpu …

## #4055: pbmc_dataset: 4k/8k barcode collision gives 48 cells another cell's counts
**Issue:** #4055 | **Last activity:** 2026-10-20T09:55:36Z
**State:** closed | **Author:** @nc1m | **Comments:** 1 | **Created:** 2026-10-13 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/4055

### Report

## Summary

`scvi.data.pbmc_dataset()` joins the 10x **pbmc8k** + **pbmc4k** runs to
`pbmc_metadata.pickle` **by barcode string alone**. 51 barcodes occur in both runs, for
unrelated cells. The metadata renames the 4k twin `-1` → `-11`; the count matrices are not
renamed, so:

- **48 rows hold the 4k cell's counts under the 8k cell's label, `design` row and QC.**
  On those rows `obs["batch"] == 1` but `obsm["design"]["batchpbmc4k"] == 0`. In 39 of 47
  labelled pairs the twins' labels differ.
- **49 metadata rows (the `-11` twins) are dropped.** The code comment says they were
  "filtered on 10X website", but they are in the filtered 4k matrix under `-1`.

Result: 11,990 cells instead of the documented 12,039.

## Root cause

`scvi/data/_built_in_data/_pbmc.py` (scvi-tools 1.5.1), `_load_pbmc_dataset`:

```python
barcodes = np.concatenate((pbmc8k.obs_names, pbmc4k.obs_names))          # L75
dict_barcodes = dict(zip(barcodes, np.arange(len(barcodes)), strict=True)) # L80
for barcode in barcodes_metadata:
    if barcode in dict_barcodes:  # barcodes with end -11 filtered on 10X website (49 cells)
        subset_cells += [dict_barcodes[barcode]]
```

For a barcode `X-1` in both runs, `dict(zip(...))` silently keeps the later (4k) index
(`strict=True` only checks lengths). Metadata row `X-1` (8k cell, label *a*) picks the 4k
cell's counts; metadata row `X-11` (4k cell, label *b*) matches nothing and is skipped,
and the `endswith("11")` mask drops it consistently, so …

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/pull/4058

## #4022: TOTALVI.get_normalized_expression omits learned protein capture efficiency
**Issue:** #4022 | **Last activity:** 2026-09-23T11:42:19Z
**State:** open | **Author:** @arberqoku | **Comments:** 1 | **Created:** 2026-09-16 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/4022

### Report

### Problem

`TOTALVI.get_normalized_expression()` appears to omit the learned per-protein, per-batch capture-efficiency term from its protein readout. There is no separate public `get_normalized_protein_intensity()` method.

The public method computes protein values from unscaled `py_` rates:

https://github.com/scverse/scvi-tools/blob/1.5.1/src/scvi/model/_totalvi.py#L544-L550

### Minimal reproduction

Reproduced with `scvi-tools==1.5.1` in a fresh Python 3.12.7 environment.

```python
import anndata as ad
import numpy as np
import scvi
import torch

adata = ad.AnnData(np.ones((8, 3), dtype=np.float32))
adata.obs["batch"] = "batch_0"
adata.obsm["protein_expression"] = np.ones((8, 2), dtype=np.float32)

scvi.model.TOTALVI.setup_anndata(
    adata,
    batch_key="batch",
    protein_expression_obsm_key="protein_expression",
)

model = scvi.model.TOTALVI(adata, n_latent=1)

# set a non-unit efficiency deterministically to isolate the readout scale.
with torch.no_grad():
    model.module.log_per_batch_efficiency.fill_(np.log(2.0))

model.module.eval()

torch.manual_seed(123)
_, public_protein = model.get_normalized_expression(
    adata=adata,
    include_protein_background=True,
    sample_protein_mixing=False,
    n_samples=1,
    return_mean=True,
    return_numpy=True,
    silent=True,
)

# reconstruct the same forward pass and compare unscaled and scaled rates.
torch.manual_seed(123)
tensors = next(iter(model._make_data_loader(adata=adata, batch_size=8)))

wit …

**@ori-kron-wis:** Thanks @arberqoku , I added a flag to incorporate this normalization in get_normalized_expression.
The fix is in this PR (not the automatic bot one from before): https://github.com/scverse/scvi-tools/pull/4033

## #4006: Runing multi-Panel Integration in CytoVI with Beta likelihood was unable to train
**Issue:** #4006 | **Last activity:** 2026-09-09T07:37:36Z
**State:** closed | **Author:** @shihsama | **Comments:** 1 | **Created:** 2026-09-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/4006

### Report

Hi,
Recently I was working on CytoVI to integrate multiple antibody panels. I was wondering whether the Beta likelihood is fully compatible with multi-panel integration in CytoVI, since the tutorial only demonstrates the Normal likelihood.
When I set protein_likelihood="beta", the model initialization succeeded, but training stopped immediately with:

```python
Monitored metric elbo_validation = nan is not finite.
Previous best value was inf. Signaling Trainer to stop.
```

I checked the scaled expression matrix and found that the lower bound was exactly 0, although the observed values had been scaled into the expected open interval close to (0, 1).

After further inspection, the exact zeros were not observed protein values. They were the placeholder values introduced during multi-panel merging for proteins that were missing from one panel. merge_batches() first creates NaNs for missing proteins and then register_nan_layer() replaces these NaNs with 0, while storing _nan_mask to exclude them from the reconstruction loss.

This seems problematic for the Beta likelihood because Beta.log_prob(0) is not finite. Even though those entries are masked later by _nan_mask, the log probability is apparently evaluated before masking, which can result in NaN values in the ELBO.

As a workaround, I replaced only the missing-protein placeholder values with 0.5 while keeping _nan_mask unchanged:


```python
mask = adata.layers["_nan_mask"].astype(bool)
adata.layers["scaled"][~mas …

**@ori-kron-wis:** Hey @shihsama , Thank you for catching this, it was not well covered before.
While your diagnosis is correct, the robust fix is at the likelihood evaluation site, not the preprocessing step.
See the relevant PR.

## #3980: MPS accuracy warning in parse_device_args() is not supported by measurement
**Issue:** #3980 | **Last activity:** 2026-09-07T07:57:52Z
**State:** closed | **Author:** @BenjaminDEMAILLE | **Comments:** 1 | **Created:** 2026-09-01 | **URL:** https://github.com/scverse/scvi-tools/issues/3980

### Summary

`parse_device_args()` warns that MPS models "might be slower and **less accurate** than
usual" ([`src/scvi/model/_utils.py:129`](https://github.com/scverse/scvi-tools/blob/main/src/scvi/model/_utils.py#L129)).
I measured this and could not reproduce an accuracy penalty: on the ops that matter for
SVI, MPS float32 is indistinguishable from CPU float32 relative to a float64 reference,
and on the ELBO gradient it was marginally *closer* to the reference.

The warning was added in #2045 (May 2023), when MPS was much less mature, and it points
at [pytorch#77764](https://github.com/pytorch/pytorch/issues/77764), which tracks
**operator coverage**, not numerics. I think the coverage half is still worth warning
about and the accuracy half is no longer supported by evidence.

### Measurements

M4 Max, macOS 26.6.2, torch 2.10.0, pyro 1.9.1. Max absolute error against a CPU
float64 reference, 4096x512 inputs:

| Op | CPU fp32 | MPS fp32 |
|---|---|---|
| `lgamma` | 3.6e-07 | 8.9e-07 |
| `digamma` | 3.9e-06 | 5.4e-06 |
| `log` | 1.8e-07 | 3.3e-07 |
| `exp` | 1.6e-05 | 1.9e-05 |
| `softmax(-1)` | 4.3e-09 | 3.6e-09 |
| `sum(-1)` | 1.8e-04 | 1.7e-04 |
| `matmul` 1024x1024 | 2.07e-06 | 2.07e-06 |

The figure that actually governs training, the gradient of a negative-binomial ELBO
term w.r.t. an AutoNormal location (262k parameters, gradient scale 125):

```
cpu32   max relative deviation from float64   3.8e-07
mps32   max relative deviation from float64   3.7e-07
```

Transcend …

**@ori-kron-wis:** @BenjaminDEMAILLE Thank you so much for supporting the MPS/torch integration in scvi-tools and for showing this accuracy stability between devices.
Can you please add this small to the PR you already opened here: https://github.com/scverse/scvi-tools/pull/3981?

## #3977: RESOLVI._prepare_data stores incorrect spatial neighbors due to sparse matrix power and CSR row ordering
**Issue:** #3977 | **Last activity:** 2026-09-02T17:22:18Z
**State:** open | **Author:** @kwangdol | **Comments:** 2 | **Created:** 2026-08-30 | **URL:** https://github.com/scverse/scvi-tools/issues/3977

Hi, I ran into what looks like a correctness bug in `RESOLVI._prepare_data` while checking the spatial neighbors generated for a Xenium dataset.

The relevant code on `main` is:

```python
scanpy.pp.neighbors(
    sub_data,
    n_neighbors=n_neighbors + 5,
    use_rep=spatial_rep,
    method=method,
)
distances = sub_data.obsp["distances"] ** 2

distance_neighbor[index, :], index_neighbor_batch = _kneighbors_from_graph(
    distances, n_neighbors, return_distance=True
)
```

I think there are two interacting issues here.

### 1. `** 2` is matrix power for scipy sparse matrices

For `scipy.sparse` matrices, `D ** 2` is matrix multiplication (`D @ D`), not element-wise squaring.

So this line:

```python
distances = sub_data.obsp["distances"] ** 2
```

produces a two-hop product graph, where

```text
(D^2)[i,j] = sum_k D[i,k] * D[k,j]
```

rather than squared Euclidean distances.

Those values are then stored in `distance_neighbor`, used to derive `median_distance`, and passed into the diffusion kernel. The expression of the selected neighbors is also read directly into the diffusion component, so both the neighbor identity and the kernel calibration are affected.

### 2. Fixing this to `.power(2)` is not sufficient by itself

`_kneighbors_from_graph` truncates each CSR row in storage order. In my environment, Scanpy's raw `obsp["distances"]` is distance-ordered, but calling `.power(2)` canonicalizes the CSR matrix and reorders entries by column index.

So after the obvious fix …

**@ori-kron-wis:** Hey @kwangdol , thank you for supporting scvi-tools and ResolVI and Yes, I would like to have the fix PR and regression test.

I assume you missed it, but we are moving ResolVI and the rest of the spatial support models into the scviva-tools package, and as of v1.5.0 of scvi-tools, ResolVI is no longer maintained here, but in this repo: https://github.com/YosefLab/scviva-tools. It will be removed later from scvi-tools in future versions. Thus, please open the PR in scviva-tools.

**@kwangdol:** Thanks, and sorry, I did miss the migration to scviva-tools.

I confirmed that the same code path is present there (`src/scviva/model/_resolvi.py`, in `_prepare_data`), and the issue reduces to a 500-cell example with no Scanpy dependency:

```python
import numpy as np
from sklearn.neighbors import kneighbors_graph, NearestNeighbors
from sklearn.neighbors._base import _kneighbors_from_graph

rng = np.random.default_rng(0)
n, k = 500, 10
X = rng.uniform(0, 100, (n, 2)).astype("float32")

G = kneighbors_graph(
    X,
    n_neighbors=k + 5,
    mode="distance",
    include_self=False,
)

i_true = (
    NearestNeighbors(n_neighbors=k + 1)
    .fit(X)
    .kneighbors(X)[1][:, 1:]
)

def overlap(A):
    return np.mean([
        len(set(A[i]) & set(i_true[i])) / k
        for i in range(n)
    ]) …

## #3984: Is there a reason `cd4_t_helper` appears twice in `PurifiedPBMCDataset.h5ad`?
**Issue:** #3984 | **Last activity:** 2026-09-02T11:31:53Z
**State:** closed | **Author:** @nc1m | **Comments:** 1 | **Created:** 2026-09-02 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3984

### Report

`PurifiedPBMCDataset.h5ad` has **11 batches but only 10 cell types** — `cd4_t_helper` is both batch `0` and batch `7`. The two batches aren't independent samples of the same population; they're the same 11,213 cells, byte-identical and in the same order.

Is this intentional (e.g. a technical replicate for integration demos), or an artifact of how the file was assembled?

## Reproduction

```python
import anndata as ad
import numpy as np

adata = ad.read_h5ad("PurifiedPBMCDataset.h5ad")   # raw download, no scvi-tools involved
print(adata.obs["batch"].nunique(), adata.obs["cell_types"].nunique())   # 11 10

b = adata.obs["batch"].astype(str).to_numpy()
i0, i7 = np.flatnonzero(b == "0"), np.flatnonzero(b == "7")
bc = adata.obs["barcodes"].astype(str).to_numpy()

print(i0.size, i7.size)                   # 11213 11213
print((bc[i0] == bc[i7]).all())           # True -- same barcodes, same order
print((adata.X[i0] - adata.X[i7]).nnz)    # 0    -- identical counts
```

Hashing all 105,868 rows finds 11,213 duplicate pairs, all spanning batch 0↔7 and none within a batch — one population concatenated twice, not scattered repeats. Note `obs_names` is unique (105,868/105,868), so an `obs_names.is_unique` check doesn't catch it.

## Why it looks unintended

Zheng et al. 2017 ([doi:10.1038/ncomms14049](https://doi.org/10.1038/ncomms14049)) sorted **10** subpopulations.

The docstring list in `_built_in_data/_pbmc.py:21-33` also has 11 entries with `"cd4_t_helper"` at indice …

**@ori-kron-wis:** Thanks. A fix will be issued in the next release of scvi-tools.

## #3600: Use scverse template
**Issue:** #3600 | **Last activity:** 2026-07-28T09:32:54Z
**State:** closed | **Author:** @Zethson | **Comments:** 3 | **Created:** 2025-11-14 | **Labels:** refactor | **URL:** https://github.com/scverse/scvi-tools/issues/3600

Hey,

from what I can see, you're currently not (fully) using the scverse template. Would it be possible to do so, please? I'd be happy of we could converge on a more consistent developer experience across all of our repositories.

Then we can also enable the sync.

**@ori-kron-wis:** @Zethson can you elaborate or share an example? Ill be happy to do it. Not so sure what is missing currently.

**@Zethson:** Sure! So almost all (we're catching up at the moment) of our core packages use https://github.com/scverse/cookiecutter-scverse as the basis for their package. It'd be awesome if you could recreate scvi-tools based on the template. This will ensure that the template sync will be enabled for scvi-tools so that your kept up to date with our joint structure an best practices.

I understand that scvi-tools has a little bit of customization and repository history so there's a chance that you'll need to adapt a few things down the road but I'd be super happy if it were based on the template.

So
1. Create a new branch here
2. Create a new package based on the template
3. Slowly start copying the code from main over to this branch until code & docs work as expected
4. Ask one of Gregor, Phil, or m …

**@ori-kron-wis:** I think most of the things are there. I opened a PR with some missing files. There might be other things.
Perhaps we can pinpoint exactly what is not working or missing?, as I believe most things are fine.

## #3819: Add `weighted_knn_trainer`/`weighted_knn_transfer` utilities from scArches
**Issue:** #3819 | **Last activity:** 2026-07-22T10:16:08Z
**State:** closed | **Author:** @seohyonkim | **Comments:** 3 | **Created:** 2026-05-19 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3819

Hello!

**Is your feature request related to a problem? Please describe.**
I am migrating a workflow from scArches to scvi-tools for the sc-best-practice. Most functionality has a clear equivalent in scvi-tools, but `scarches.utils.weighted_knn_trainer` and `weighted_knn_transfer` have no counterpart.

**Describe the solution you'd like**
Would it be possible to add the functions to e.g. `scvi.tools`? Thank you so much!

**@ori-kron-wis:** Yes, however, this is not in our plan currently.
Would you like to contribute a pull request for that?
Thank you

**@seohyonkim:** yes sure! I'll ping you in the PR once I have it ready. Thank you!

**@ehvr20:** The package [cellmapper](https://github.com/quadbio/cellmapper) has the scArches label transfer implementation as well as several alternative weighting schemes.

From personal experience, I recommend exploring the other weighting schemes as I find the scArches implementation too close to a naïve majority vote and highly k-dependant.

## #3449: pip install creates conflits between jax and jaxlib
**Issue:** #3449 | **Last activity:** 2026-07-06T06:13:31Z
**State:** closed | **Author:** @osmanmerdan | **Comments:** 3 | **Created:** 2025-07-31 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3449

I have created a new conda environment with Python 3.12.11 and installed scvi tools with the recommended command in the installation page:
`pip install -U scvi-tools[cuda]`
Importing JAX produces the following error:
```python
>>> import jax
```


```pytb
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/myname/miniconda3/envs/scrnaseq/lib/python3.12/site-packages/jax/__init__.py", line 39, in <module>
    from jax import config as _config_module
  File "/home/myname/miniconda3/envs/scrnaseq/lib/python3.12/site-packages/jax/config.py", line 15, in <module>
    from jax._src.config import config as _deprecated_config  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/myname/miniconda3/envs/scrnaseq/lib/python3.12/site-packages/jax/_src/config.py", line 28, in <module>
    from jax._src import lib
  File "/home/myname/miniconda3/envs/scrnaseq/lib/python3.12/site-packages/jax/_src/lib/__init__.py", line 74, in <module>
    version = check_jaxlib_version(
              ^^^^^^^^^^^^^^^^^^^^^
  File "/home/myname/miniconda3/envs/scrnaseq/lib/python3.12/site-packages/jax/_src/lib/__init__.py", line 66, in check_jaxlib_version
    raise RuntimeError(
RuntimeError: jaxlib version 0.6.2 is newer than and incompatible with jax version 0.4.21. Please update your jax and/or jaxlib packages.
```
**The problem can be solved by reinstalling JAX for CUDA after installing SCVI:**
`pip install --upgrade jax[cuda12]==0.6 …

**@ori-kron-wis:** Jax can cause issues with installation, we are well aware, but the solution is as simple as you saw.
Yet, we will remove Jax as mandatory for v1.4, because all of those installation issues.

**@qwelongh:** @ori-kron-wis
Hi, thanks for the previous response mentioning that JAX would be removed as a mandatory dependency in v1.4.
However, I'm reporting that in the latest release, JAX is still being imported as a mandatory dependency.


RuntimeError: jaxlib version 0.10.2 is newer than and incompatible with jax version 0.4.21. Please update your jax and/or jaxlib packages.

**@ori-kron-wis:** This is something internal to your environment and not related to scvi-tools. Use a new env with the updated version of scvi-tools (there is no place for jax version 0.4.21 and jaxlib version 0.10.2 anywhere, except manualy done)

## #3734: Improving SCVI for low-count cells through self-supervised augmentation
**Issue:** #3734 | **Last activity:** 2026-06-28T15:27:45Z
**State:** closed | **Author:** @chelseabright96 | **Comments:** 2 | **Created:** 2026-03-02 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3734

Hi,

A paper has recently been written about improving scVI for low count cells using binomial thinning and a cross-correlation loss. It looks like this extension of scVI improves on the integration of low count cells based on the paper results. I thought this may be of interest for you and that you may consider incorporating this into scvi-tools at some point.

Paper link: https://www.biorxiv.org/content/10.64898/2026.02.11.705441v1.full.pdf

**@ori-kron-wis:** Thank you @chelseabright96 , we are well aware of it and have been collaborating with Valentine for a long time, so we might as well implement it.

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/pull/3884

## #3674: Resolvi.load overflows memory
**Issue:** #3674 | **Last activity:** 2026-06-28T10:57:10Z
**State:** closed | **Author:** @jairaj-mathur | **Comments:** 9 | **Created:** 2026-01-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3674

<!-- Describe the bug -->

When I load a saved model via RESOLVI.load, the memory consumption to just load the model is higher than while the model was being trained. I am using a 256gb ram and 22 GB GPU. While loading, the model, the GPU only uses about 200 MB VRAM while the RAM overshoots the 256 GB limit. During training, model used about 180 GB RAM and 2-5 GB VRAM.

Xenium dataset, 200k cells 5k genes

<!-- To reproduce -->

```python
RESOLVI.load(/path/to/model, data, accelerator='gpu')
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
The python process exited with exit code 137 (SIGKILLED: Killed). This may have been caused by an OOM error. Check your commands memory usage.
```

#### Versions:

<!-- Output of scvi.__version__ -->

> 1.4.1

**@canergen:** I actually assumed this was fixed. Did you run with the most recent scvi-tools version?

**@ori-kron-wis:** @jairaj-mathur please use the branch I suggested in the other issue, see if this issue is solved as well.

**@LizEve:** @ori-kron-wis I'm a coworker of @jairaj-mathur. I think our issue is that Databricks upgraded to scipy==1.17.0 recently. Setting scipy==1.16.3 seems to solve my OOM issue when loading models.

**@ori-kron-wis:** @LizEve Thanks for letting us know.
I can confirm the memory footprint increased by 10% on my test of loading resolvi model with scipy 1.17.

**@canergen:** @ori-kron-wis do we need a fix for it or do we hope scipy will fix it upstream? My intuition is that the error comes from https://github.com/scverse/scvi-tools/blob/54fd6135263b02d803ff07fa653267d3635ca51a/src/scvi/model/base/_archesmixin.py#L240.

**@ori-kron-wis:** It's up to you, I guess. It's a minor bug, not affecting logic.
If we can improve the memory consumption of this or any other model, of course, it's a good thing.

**@Qiaoli-Li-Res:** I identified two sources of excess memory during `RESOLVI.load()` and opened a PR in #3886:

1. `setup_anndata()` was re-running `_prepare_data()` on every load, causing an unnecessary `adata.copy()` + `sc.pp.neighbors()` call.
2. `on_load()` was running `train(max_steps=1)` unnecessarily — `RESOLVAE` uses a manually-written guide, so the Pyro param store can be restored directly.

Tested with 20k cells: tracemalloc peak was reduced by 66%. Full validation with a large Xenium dataset would be appreciated.

**@ori-kron-wis:** @Qiaoli-Li-Res Thank you very much. This is a real engineering bug you found. I will test and add it.
Added a slightly revised version of this fix here: https://github.com/scverse/scvi-tools/pull/3887

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/pull/3887

## #1177: User guide: gimVI
**Issue:** #1177 | **Last activity:** 2026-06-23T12:50:14Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2021-09-27 | **Labels:** user guide, P1, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1177

## #1456: Within cluster DE test
**Issue:** #1456 | **Last activity:** 2026-06-23T11:01:16Z
**State:** closed | **Author:** @zoesteier | **Comments:** 2 | **Created:** 2022-03-22 | **Labels:** enhancement, good first issue, differential expression, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1456

scVI used to have a within cluster DE test that I used often, but I no longer see this functionality in scvi-tools. Is it possible to add it back?

This would be a differential expression function where a "groupby" argument would specify a set of groups (e.g., cell clusters) and a "states" argument would specify the relevant comparison to make (e.g., case vs control). The output would include the DE test results from a comparison of cases vs controls within each specified group.

**@adamgayoso:** @PierreBoyeau what do you think?

**@PierreBoyeau:** It sounds like it would be relevant to include it back. Do you remember why we removed this feature?

## #3865: AttributeError: module 'scvi.model.utils' has no attribute 'mde'
**Issue:** #3865 | **Last activity:** 2026-06-19T22:50:53Z
**State:** closed | **Author:** @EfraMP | **Comments:** 2 | **Created:** 2026-06-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3865

<!-- Describe the bug -->

When trying to use minimum-distortion embedding on my data and custom model, following the example of the  [documentation](https://docs.scvi-tools.org/en/1.0.0/api/reference/scvi.model.utils.mde.html), unexpectedly I got `
AttributeError: module 'scvi.model.utils' has no attribute 'mde'`

<!-- To reproduce -->

To reproduce:

```python
adata.obsm["X_mde_scvi"] = scvi.model.utils.mde(adata.obsm["X_scVI"])
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[51], line 1
----> 1 adata.obsm["X_mde_scvi"] = scvi.model.utils.mde(adata.obsm["X_scVI"])

AttributeError: module 'scvi.model.utils' has no attribute 'mde'
```

Which is extremely weird for me.

When running

```python
dir(scvi.model.utils)
```
Indeed I get:
```pytb
['__all__',
 '__builtins__',
 '__cached__',
 '__doc__',
 '__file__',
 '__loader__',
 '__name__',
 '__package__',
 '__path__',
 '__spec__',
 '_minification',
 'get_minified_adata_scrna',
 'get_minified_mudata']
```


#### Versions:


<!-- Output of scvi.__version__ -->
```python
1.4.3
```

**@ori-kron-wis:** `mde` is not part of the package dependency or tutorial anymore. You linked for version 1.0.0 (did you also use it?), but in more recent versions, this is gone, see: https://docs.scvi-tools.org/en/latest/changelog.html#id45

**@EfraMP:** I see, makes sense!

Somehow I ended up in the linked tutorial without double-checking the version.

Thanks!

## #3839: Model request: scPhere (hyperspherical / hyperbolic latent embedding for scRNA-seq)
**Issue:** #3839 | **Last activity:** 2026-06-10T07:43:19Z
**State:** open | **Author:** @nataliaMalicka | **Comments:** 1 | **Created:** 2026-06-09 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3839

**Is your feature request related to a problem? Please describe.**
Many core scvi-tools VAE models, including SCVI, use Euclidean latent variables with Gaussian priors. For datasets with many cell types, multi-level batch effects, or hierarchical/continuous structure, very low-dimensional Euclidean embeddings can suffer from crowding and distortion, making interpretation and inter-cluster relationships less reliable when the goal is a 2D/3D representation. I am not aware of a scvi-tools model whose primary latent space is non-Euclidean (hyperspherical or hyperbolic).

**Describe the solution you'd like**
I would like to add scPhere, a deep generative VAE that embeds scRNA-seq profiles on hyperspheres or in hyperbolic space rather than a Euclidean Gaussian latent. It was designed to reduce crowding/distortion, jointly model multiple batch/confounding vectors, and give interpretable low-dimensional visualizations.

- **Paper:** Ding & Regev, Nature Communications (2021). https://www.nature.com/articles/s41467-021-22851-4
- **Reference implementation:** https://github.com/Ding-Group/scPhere

**Additional context**
I'm part of Jiarui Ding's research group (the lab behind scPhere), and will keep the implementation faithful to the original method. I'm interested in implementing this and opening a PR. Would this be of interest to add to scvi-tools?

Thanks!
Natalie Malicka

**@ori-kron-wis:** Hey @nataliaMalicka

That sounds great!
Several tips:
-  Please put it under external and use the model-module design principle (as in the reference implementation, it is compact right now). Start with the inheritance of the base model, which brings core scvi-tools functionality.
- Try to reuse as much code as possible (e.g : scvi decoder likely can be used, Anndata manager, trainer- UnsupervisedTrainingMixin and trainingPlan), but for mixins, be aware that they might assume Euclidean-like posterior distributions (mostly Normal, e.g, get_latent() from VAEmixin), so a local implementation of some of the functions is needed, while others might work. Add proper unit testing for all of that (inc core functionality).
- Do not change scvi-tools core functions unless it's a very minor change an …

## #3834: MultiVI MuData setup rejects unpaired observations despite model supporting missing modalities
**Issue:** #3834 | **Last activity:** 2026-06-08T15:54:04Z
**State:** open | **Author:** @catheriz | **Comments:** 4 | **Created:** 2026-06-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3834

<!-- Describe the bug -->

When trying to use MultiVI with a MuData object containing unpaired observations (cells missing from some modalities), scvi-tools now raises:

```
ValueError: Detected unpaired observations in modality rna. Please make sure that data is fully paired in all MuData inputs. Either pad the unpaired modalities or take the intersection with muon.pp.intersect_obs().
```

This is surprising, as MultiVI is designed to handle missing modalities during modeling, yet the data validation enforces fully paired MuData objects.

**Relevant code:**
- `src/scvi/data/_manager.py`: validates MuData via `_check_mudata_fully_paired`
- `src/scvi/data/_utils.py`: raises error if any modality is structurally unpaired
- Recent commit possibly implicated: `1a2d127c1f7e364e21ea92e92c99ee844016a114` ("fix: AttributeError after rich upgrade and MultiVI errors after Mudata upgrade (#3776)")

<!-- To reproduce -->

```python
# Prepare a MuData with unpaired observations
# This used to run (<=2024), but now fails immediately after upgrade
# ...
import muon as mu
# mdata: MuData with unpaired cells between rna & atac modalities
...
# Setup for MultiVI:
from scvi.model import MULTIVI
MULTIVI.setup_mudata(mdata)
# Exception raised here
```

**@ori-kron-wis:** I think there is some confusion here with the definition of what is "unpaired".
From what I understand, MultiVI is designed to handle and integrate both paired multiomic data (like RNA and ATAC simultaneously) and single-modality unpaired data (only RNA or only ATAC) - but always when the same cells exist for all modalities. i.e, not in the case of missing cells from one of the datasets.

In such a case, you can easily impute the missing cells with 0's (manually), and it will still work for you. Previosuly, was done automatically with Anndata, which is no longer supported.

MultiVI can impute missing expression and accessibility for the modalities that miss them (see tutorial) - perhaps that's what causes the confusion with the word "unpaired".

Are you familiar with other things?

The l …

**@canergen:** I assume the confusion comes from originally using AnnData, where we padded missing observations with zeros. In MuData, obs can be missing in one modality. However, the dataloader expects all obs to exist and so just pad with zeros. There is no plan to change this behavior so we have consistent positions across modalities.
To clarify one point: MultiVI can handle mosaic integration (one modality is shared such as RNA+ATAC/RNA+protein/ATAC is fine) but not diagonal (no cells with overlapping modality).

**@catheriz:** Thanks for the previous support. My data is a mosaic integration. After patching the missing entries with 0, MultiVI setup works. However, I noticed that since v1.4.2, the model itself takes up a large amount of memory, about 35GB.

Is this expected after using zeros to patch missing modalities in MuData? Did the model or default storage approach change in v1.4.2 or later that would lead to such large memory usage? Any advice for reducing memory consumption? I think previous issue also mentioned about downgrading version of scipy would help a bit?

**@ori-kron-wis:** No, there is no change in storage approach AFAIK. It can be related to other packages, yes.
What is the difference in memory consumption if you compare it apples to apples to a previous scvi-tools versions?

## #3759: Direct `csr` sparse ops support
**Issue:** #3759 | **Last activity:** 2026-05-18T18:19:57Z
**State:** open | **Author:** @ilan-gold | **Comments:** 3 | **Created:** 2026-03-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3759

**Is your feature request related to a problem? Please describe.**
I think there are performance gains to be had by not densifying inputs from minibatches when possible and instead doing backprop on the sparse matrix directly yielded from the loader at the level of sparsity we sometimes see (~2%) in full-feature-space RNA-seq data at least. In this notebook, it's 2X for a MLP classifier. IIUC, this same trick applies to the loss function as well as the ELBO i.e., use the sparse matrix directly instead of densifying.

It's possible (likely) that at higher values, this benefit either decreases or becomes 0.

See https://colab.research.google.com/drive/14cjQkQ2lO9wT7BpcfLfYCUY40GncXesh?authuser=3 for something runnable, if not old given the antiquated colab GPU

The implementation is based on https://github.com/rusty1s/pytorch_sparse


**Describe the solution you'd like**
I think the answer is a sort of runtime setting enum with three options:

1. `auto` tries to detect sparsity and at some cutoff uses the sparse accelerator
2. `sparse_direct` will replace the first layer with a sparse-linear layer (i.e., one that does matmul on a sparse input) as well as the other applicable locations with their respective ops
3. `densify` densifies all inputs

**@ori-kron-wis:** Hey @ilan-gold
I like this approach, and this topic, which we already discussed a bit, became relevant again with this issue https://github.com/scverse/scvi-tools/issues/1038
However, the colab link is not working for me. Can you attach the notebook here?

**@ilan-gold:** I'll edit the permissions @ori-kron-wis  - I do remember discussing but wanted to open this anyway since it came up in some benchmarks for annbatch :)

**@ilan-gold:** @ori-kron-wis I am able to open the notebook in a private window.....I'll send you the downloaded version on zulip

## #3815: Separate `mlx` from `cuda`/`cuda13` extras
**Issue:** #3815 | **Last activity:** 2026-05-17T11:46:38Z
**State:** closed | **Author:** @jpintar | **Comments:** 1 | **Created:** 2026-05-16 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3815

Currently, the `cuda`/`cuda13` extras call for `mlx[cuda]`/`mlx[cuda13]`. However, since MLX wheels are only available for `manylinux_2_31` and `manylinux_2_35`, this is a barrier to simple installation on older Linux systems (e.g. HPC clusters still running RHEL 8, which is my own use-case), where MLX is not going to be as useful to end-users anyway.

Of course, one can always just not use the `cuda`/`cuda13` extras and add `torchvision`, `torchaudio`, and `jax[cuda]`/`jax[cuda13]` to one's project requirements manually, but it would be more convenient if a non-MLX CUDA extra were also defined.

**@ori-kron-wis:** Understood, I will remove it as well (really needed for MAC OS)

## #3814: Secondary metrics not recorded by `autotune.run_autotune`
**Issue:** #3814 | **Last activity:** 2026-05-17T11:46:38Z
**State:** closed | **Author:** @jpintar | **Comments:** 1 | **Created:** 2026-05-16 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3814

<!-- Describe the bug -->

As of ec2ff107f8f6febd2e0b909d985f96fe1af4fb34, when a list is passed to `metrics` in `scvi.autotune.run_autotune`, only the values of the primary metric (i.e. the first element in the list) are recorded. It looks like the cause is [this change](https://github.com/scverse/scvi-tools/commit/ec2ff107f8f6febd2e0b909d985f96fe1af4fb34#diff-b86986b18b6f828ad1f5920c06a325319de0fc8fcad523e15544c8a29e86abf3R724) in the definition of `metrics_callback`, where `self.metrics[0]` is passed instead of `self.metrics`.

<!-- To reproduce -->

```python
import scanpy as sc
import scvi
from ray import tune
from scvi import autotune


scvi.settings.seed = 12345

adata = scvi.data.heart_cell_atlas_subsampled()
adata.layers["counts"] = adata.X.copy()
sc.pp.filter_genes(adata, min_counts=3)
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=1200,
    subset=True,
    layer="counts",
    flavor="seurat_v3",
    batch_key="cell_source",
)

model_cls = scvi.model.SCVI
model_cls.setup_anndata(
    adata,
    layer="counts",
    labels_key="cell_type",
    batch_key="cell_source",
    categorical_covariate_keys=["donor"],
    continuous_covariate_keys=["percent_mito", "percent_ribo"],
)

search_space = {
    "model_params": {
        "n_hidden": tune.choice([64, 128]),
        "n_layers": tune.choice([2, 3]),
    },
    "train_params": {
        "max_epochs": 10,
        "plan_kwargs": {"lr": tune.loguniform(1e-4, 1e-2)},
    },
}

tuning_results = autotune.run_autotune( …

**@ori-kron-wis:** Thanks, fix added.

## #2889: scvi-tools 1.2.0 release
**Issue:** #2889 | **Last activity:** 2026-05-12T13:04:01Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 4 | **Created:** 2024-07-11 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2889

- [x] Bump version in `pyproject.toml`
- [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new
    branch off `main` with the appropriate rules
- [ ] Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker)
    targeting the release branch
- [ ] After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials)
    using the new image
- [ ] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged
- [ ] Create a new branch off `main` in the main repo and run `git submodule update --remote`, and
    then merge the PR, with an appropriate backport as needed
- [ ] Make sure scvi-colab install from release branch
- [ ] Run the release workflow
- [ ] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/)
- [ ] Build new Docker images with the `stable` and semantic versioning tags
- [ ] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly
- [ ] (Optional) Post threads on Discourse and Twitter

**@Rafael-Silva-Oliveira:** Hey @martinkim0 just out of curiosity, when is v 1.2 going to release? :) Would love to test the hyperparameter tuning with Ray for some label transferring

Thanks!

**@martinkim0:** Hi @Rafael-Silva-Oliveira, right now it's looking like the end of the month. Regarding #2895, it's a deprecation warning, so it should be OK to use the current version of Ray hyperparameter tuning with no problem :)

**@Rafael-Silva-Oliveira:** > Hi @Rafael-Silva-Oliveira, right now it's looking like the end of the month. Regarding #2895, it's a deprecation warning, so it should be OK to use the current version of Ray hyperparameter tuning with no problem :)

Thank you for the reply, I think I'll wait for the new version since it just keeps giving me errors such as this one:

```

>>> results = tuner.fit(
...     adata=adata_to_annotate,
...     metric="validation_loss",
...     search_space=search_space,
...     num_samples=100,
...     max_epochs=20,
... )
2024-08-06 17:37:58,737 ERROR services.py:1329 -- Failed to start the dashboard , return code 1
2024-08-06 17:37:58,739 ERROR services.py:1354 -- Error should be written to 'dashboard.log' or 'dashboard.err'. We are printing the last 20 lines for you. See 'https …

**@raozuming:** Copied to #2992

## #3804: SCANVI bug — classify_helper divides logits by their sum
**Issue:** #3804 | **Last activity:** 2026-05-12T12:38:47Z
**State:** closed | **Author:** @marianogabitto | **Comments:** 1 | **Created:** 2026-05-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3804

<!-- Describe the bug -->

  - Classifier.__init__ default = logits=False
  - SCANVAE explicitly overrides the default to logits=True at _scanvae.py:142
  - Therefore SCANVAE's self.classifier(z) returns raw logits
  - Therefore the classify_helper factoring divides raw logits (which can be negative) by their sum (lines 779-791 in _base_module.py)
            @auto_move_data
              def classify_helper(self, z):
                  if self.use_labels_groups:
                      w_g = self.classifier_groups(z)
                      unw_y = self.classifier(z)
                      w_y = torch.zeros_like(unw_y)
                      for i, group_index in enumerate(self.groups_index):
                          unw_y_g = unw_y[:, group_index]
                          w_y[:, group_index] = unw_y_g / (unw_y_g.sum(dim=-1, keepdim=True) + 1e-8)
                          w_y[:, group_index] *= w_g[:, [I]]
                  else:
                      w_y = self.classifier(z)
                  return w_y

<!-- To reproduce -->

```python
# Your code here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[Paste the error output produced by the above code here]
```

#### Versions:

1.4.2

> VERSION

**@ori-kron-wis:** @marianogabitto thanks. Looks like an old legacy bug (not because of creating the SupervisedModuleClass class) which only happens when use_labels_groups is True and logits is True also. I did not see such a case in our backtests so it was missed, I guess. Why did you need to use that?

I would assume the logits will be a parameter to the modules (scanvi/totalanvi/methylanvi) - but its hard coded inside, and I don't want to change it now (will perhaps impact existing pipelines ). They are True mainly for cross-entropy calculation.

Therefore, we removed the use_labels_groups logic in this PR. it looks redundant nowadays.

## #3792: [Feature]: Masking missing features from scArches loss calculation.
**Issue:** #3792 | **Last activity:** 2026-04-29T08:54:35Z
**State:** closed | **Author:** @ehvr20 | **Comments:** 3 | **Created:** 2026-04-27 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3792

**Is your feature request related to a problem? Please describe.**
I have a single cell reference atlas consisting of the integration of several datasets using scVI. I am attempting to project a spatial transcriptomic dataset (1000 gene panel) via scArches/load_query. These investigations show the general poor mapping of spatial transcriptomic cells into the single cell latent space.

**Describe the solution you'd like**
A major candidate for this is that only 1000 genes out of the 4500 reference model input genes exist. Reading further into the implementation, I see that the missing genes expression is simply padded as zeros. As such during the learning of scArches the ELBO loss is heavily swayed by the reconstruction between the predicted profile the artificial zeros, far deviating from the single cell. The feature I would like to request, is the ability to mask missing features from the reconstruction loss calculation and subsequent ELBO computation during scArches training.

Do you foresee this being difficult to implement? Has this already been tried before?

**@ehvr20:** I implemented a test of this myself by adding a monkey patch to the `vae.loss` method to use a boolean feature mask. Results present zero change to result latent embedding despite changes to loss metric in `SCVI.history`.

I am leaving a note of my implementation below in case anyone is curious and I am closing this issue.

**Monkey patch function**
```python
import torch
import numpy as np

from scvi import REGISTRY_KEYS
from scvi.model import SCVI
from scvi.module.base import LossOutput
from scvi.module._constants import MODULE_KEYS
from scvi.utils import unsupported_if_adata_minified

@unsupported_if_adata_minified
def masked_loss(self, tensors, inference_outputs, generative_outputs, kl_weight=1.0):
    from torch.distributions import kl_divergence

    x = tensors[REGISTRY_KEYS.X_K …

**@ori-kron-wis:** Thanks @ehvr20 , can you emphasize if this addition helped in your case and in what sense? Losses and latent space remained the same? what did it improve exactly

**@ehvr20:** Apologies for not being more clear. A personal theory of mine was that padding missing features with zeros as is the current scArches implementation would bias the reconstruction loss computation and subsequent ELBO loss, reducing overall quality of transfer learning. My initial look into how to test this theory was very daunting as such I submitted the issue hoping for guidance. Taking another look at it again, I realised the loss function is exposed close to the surface in the API and could be adjusted using a relatively crude monkey patch.

The function above is the monkey patch I used, which simply masked out all reconstruction losses from missing features. I then ran the model with and without masking saving each to `adata.obsm['X_scvi_masked']` and `adata.obsm['X_scvi']` respectively …

## #3782: SysVI .get_normalized_expression fails to run.
**Issue:** #3782 | **Last activity:** 2026-04-19T12:02:19Z
**State:** closed | **Author:** @craniolab | **Comments:** 1 | **Created:** 2026-04-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3782

<!-- Describe the bug -->

When I try to run model.differential_expression() on a SysVI model it fails on the .get_normalized_expression function.

<!-- To reproduce -->

Create a SysVI model and run
```python
model.get_normalized_expression()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[57], line 1
----> 1 model.get_normalized_expression()

File [~/micromamba/envs/scanpy_2026/lib/python3.11/site-packages/torch/utils/_contextlib.py:124](http://localhost/user/seton/lab/tree/Cranio_Lab/Louk_Seton/4_species_project/notebooks/micromamba/envs/scanpy_2026/lib/python3.11/site-packages/torch/utils/_contextlib.py#line=123), in context_decorator.<locals>.decorate_context(*args, **kwargs)
    120 @functools.wraps(func)
    121 def decorate_context(*args, **kwargs):
    122     # pyrefly: ignore [bad-context-manager]
    123     with ctx_factory():
--> 124         return func(*args, **kwargs)

File [~/micromamba/envs/scanpy_2026/lib/python3.11/site-packages/scvi/model/base/_rnamixin.py:310](http://localhost/user/seton/lab/tree/Cranio_Lab/Louk_Seton/4_species_project/notebooks/micromamba/envs/scanpy_2026/lib/python3.11/site-packages/scvi/model/base/_rnamixin.py#line=309), in RNASeqMixin.get_normalized_expression(self, adata, indices, transform_batch, gene_list, library_size …

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/pull/3783

## #3769: MrVI documentation
**Issue:** #3769 | **Last activity:** 2026-04-09T12:09:38Z
**State:** closed | **Author:** @ddiez | **Comments:** 1 | **Created:** 2026-04-08 | **URL:** https://github.com/scverse/scvi-tools/issues/3769

There are two URLs with scvi-tools documentation. I think one is the old one at readthedocs and the new one is hosted at https://docs.scvi-tools.org. I found that the documentation at https://docs.scvi-tools.org is lacking information for methods. In particular:

https://docs.scvi-tools.org/en/latest/api/reference/scvi.external.MRVI.html#methods-table

Does not list the method differential_expression, and the entry for differential_abundance is empty. This information is found on the readthedocs site:

https://scvi-tools.readthedocs.io/en/latest/api/reference/scvi.external.MRVI.html#methods-table

There could be other things missing and this may be affecting to other models. But because MrVI model has both torch and jax implementations, and the documentation about those methods lives in mrvi_torch and mrvi_jax folders, while some common stuff is in mrvi, this layout may be messing with how the documentation is generated. But this is only a guess.

**@ori-kron-wis:** @ddiez Thank you for noticing it, although Im not sure what the old read the docs and the latter link you suggested is broken for me.
Either way, you should work with the most updated RTD, and a recent version selection (stable/latest), which you can select in the bottom right corner button.
I made a small fix with the methods section, and for MRVI please use the backend-related version of it.

## #3770: ValueError: Making .obs["condition"] categorical failed.
**Issue:** #3770 | **Last activity:** 2026-04-08T11:41:29Z
**State:** closed | **Author:** @linjing-lab | **Comments:** 5 | **Created:** 2026-04-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3770

<!-- Describe the bug -->

When I was training [Srivatsan](https://zenodo.org/records/13350497/files/SrivatsanTrapnell2020_sciplex3.h5ad?download=1)'s comparison method, only the scVI based method reported an error.

<!-- To reproduce -->

```python
train = train.copy()
model = scVI(train, key_dic['condition_key'], model_path="./model/")
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[8], line 2
      1 train = train.copy()
----> 2 model = scVI(train, key_dic['condition_key'], model_path="./model/")

File ~/perturb/scVI/models.py:51, in scVI.__init__(self, adata, condition_key, **kwargs)
     47 self.condition_key = condition_key
     49 self.model_path = kwargs.get("model_path", "./")
---> 51 SCVI.setup_anndata(
     52     self.adata,
     53     batch_key=self.condition_key
     54 )
     56 self.__create_network()

File ~/anaconda3/envs/pytorch_gpu/lib/python3.10/site-packages/scvi/model/_scvi.py:211, in SCVI.setup_anndata(cls, adata, layer, batch_key, labels_key, size_factor_key, categorical_covariate_keys, continuous_covariate_keys, **kwargs)
    207     anndata_fields += cls._get_fields_for_adata_minification(adata_minify_type)
    208 adata_manager = AnnDataManager(
    209     fields=anndata_fields, setup_method_args=setup_method_args
    210 )
--> 211 a …

**@canergen:** Is there NAN one of the values in that column? Can you call `train.obs[key_dic['condition_key']].astype("category")` outside of scvi-tools and verify that it works?

**@linjing-lab:** There is no NAN value in the column, and after calling `train.obs[key_dic['condition_key']].astype("category")`, the same error still occurs.

**@canergen:** Does the error occur when calling `train.obs[key_dic['condition_key']].astype("category")`? Or when setting up the model. What's the output on: `train.obs[key_dic['condition_key']].isna().sum()`

**@linjing-lab:** When setting up the model. The output of `train.obs[key_dic['condition_key']].isna().sum()` is 40, what should I fill in the NAN value?

**@linjing-lab:** I uses the following code to temporarily solve the problem, thanks.
```python
mode_val = train.obs[key_dic['condition_key']].dropna().mode()[0]
train.obs[key_dic['condition_key']] = train.obs[key_dic['condition_key']].fillna(mode_val)
```

## #2779: Jax version of VAEMixin
**Issue:** #2779 | **Last activity:** 2026-04-08T10:36:21Z
**State:** closed | **Author:** @justjhong | **Comments:** 1 | **Created:** 2024-05-06 | **Labels:** enhancement, good first issue, jax, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2779

Should be easy to reimplement VAEMixin for JAX models. Will require a whole new class since the forward pass call is completely different.

Example implementation of `get_reconstruction_error`:
```python
 def get_reconstruction_error(
        self,
        adata: AnnData | None = None,
        indices: list[int] | None = None,
        batch_size: int | None = None,
        **kwargs,
    ) -> dict[str, float]:
        adata = self._validate_anndata(adata)
        dataloader = self._make_data_loader(
            adata=adata, indices=indices, batch_size=batch_size, iter_ndarray=True
        )

        reconstruction_loss_sum = 0.0
        for batch in dataloader:
            vars_in = {"params": self.module.params, **self.module.state}
            outputs = self.module.apply(vars_in, batch, rngs=self.module.rngs, **kwargs)
            rec_loss_output = outputs[2].reconstruction_loss_sum.item()
            reconstruction_loss_sum += rec_loss_output

        return -(reconstruction_loss_sum / len(dataloader.dataset))
```

**@ori-kron-wis:** As we made Jax optional dependency , this is not likely to be implemented anytime soon

## #3762: import scvi fails when jax+optax installed without flax (guard mismatch in _trainingplans.py)
**Issue:** #3762 | **Last activity:** 2026-03-28T13:56:41Z
**State:** closed | **Author:** @Marius1311 | **Comments:** 3 | **Created:** 2026-03-24 | **URL:** https://github.com/scverse/scvi-tools/issues/3762

### Bug

`import scvi` fails with `ImportError: cannot import name 'JaxBaseModuleClass'` when `jax` and `optax` are installed but `flax` is not.

### Cause

Guard mismatch between `_trainingplans.py` and `_base_module.py`:

- [`_trainingplans.py`](https://github.com/scverse/scvi-tools/blob/main/src/scvi/train/_trainingplans.py#L1617-L1622) guards the `JaxTrainingPlan` block with:
  ```python
  if is_package_installed("jax") and is_package_installed("optax"):
      from scvi.module.base._base_module import JaxBaseModuleClass, TrainStateWithState
  ```
- [`_base_module.py`](https://github.com/scverse/scvi-tools/blob/main/src/scvi/module/base/_base_module.py#L448) only defines `JaxBaseModuleClass` when:
  ```python
  if is_package_installed("jax") and is_package_installed("flax"):
  ```

When `jax + optax` are present (e.g., via `ott-jax`) but `flax` is not installed, `_trainingplans.py` tries to import `JaxBaseModuleClass` from `_base_module.py`, where it was never defined.

Note: `module/base/__init__.py` already handles this correctly via lazy `__getattr__` that checks for `flax`, but `_trainingplans.py` bypasses it by importing directly from `_base_module`.

### Suggested fix

Add `flax` to the guard in `_trainingplans.py`:

```python
if is_package_installed("jax") and is_package_installed("optax") and is_package_installed("flax"):
```

### Reproduction

```bash
pip install scvi-tools jax ott-jax  # installs jax + optax, but NOT flax
python -c "import scvi"
```

### Tracebac …

**@ori-kron-wis:** @Marius1311 very clear, however, this is why we now have scvi-tools[jax] wouldn't this be enough?

**@Marius1311:** For the installation yes, but shouldn't the import still work, even if you have your environment setup without the [jax] extra?

**@ori-kron-wis:** added is_package_installed("flax")

## #1038: Faster NB LL computation if data is known to be sparse
**Issue:** #1038 | **Last activity:** 2026-03-22T12:12:28Z
**State:** open | **Author:** @adamgayoso | **Comments:** 6 | **Created:** 2021-04-26 | **Labels:** enhancement, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1038

We should add an `is_sparse` param to our distributions (at least [NB](https://github.com/YosefLab/scvi-tools/blob/0ef7ff0e9a06d65cd458b59c516971099bb55756/scvi/distributions/_negative_binomial.py#L236-L280), with LL computation [here](https://github.com/YosefLab/scvi-tools/blob/0ef7ff0e9a06d65cd458b59c516971099bb55756/scvi/distributions/_negative_binomial.py#L67-L102))

As an example in Pyro for Poisson, see [here](https://github.com/pyro-ppl/pyro/pull/2802/files)

If X is known to be sparse, we'd only have to compute the middle term for those 0 entries (r is inv. disp., m is mean, k is x).

![Screen Shot 2021-04-25 at 8 11 43 PM](https://user-images.githubusercontent.com/10859440/116025375-2de59500-a605-11eb-856e-cc0361f80340.png)

**@LiudengZhang:** Hi, I'd be interested in picking this up if it's still desired in the current codebase. The approach would be to add an `is_sparse` flag to `log_nb_positive` and `log_zinb_positive` that short-circuits the `lgamma(x + theta)` computation for zero entries (since it simplifies to `lgamma(theta)` and cancels with the existing `-lgamma(theta)` term), following the pattern in the Pyro implementation. Is this optimization still relevant given how the codebase has evolved since 2021?

**@ori-kron-wis:** Hey @LiudengZhang ,
Im not sure this is still relevant in the current codebase, unless we do a major refactor:
By default, the data is already dense by the time it hits log_nb_positive, and there are many places in the codebase where we do .toarray(), which converts sparse scipy arrays to dense numpy arrays if needed, before making them as tensors.

We do have the input of `load_sparse_tensor` which should take care of it, so perhaps you can exploit it to the change in the distribution function as well (instead of another flag), but even then, you need to probably take care of the indexing (masking) of zero values and not zero values, which makes things more complicated, like https://github.com/scverse/scvi-tools/pull/1052/changes suggested. Perhaps it will be fine for the CPU run, but it' …

**@canergen:** Hi @ori-kron-wis I think you're mixing things up here. Sparse tensor and simplified computation of reconstruction loss if expression is zero are separate things.
I'm not sure about the speed-up though and whether implementation with torch.mask will be efficient (pyro internally uses this simplified computation if values are zero). Please create a PR if you want to dig into it @LiudengZhang, we can have a look at benchmarking then.

**@ori-kron-wis:** @canergen If there will be a good solution to run sparse tensors on GPUs efficiently, with anndata support, I expect our loss calculation to be tuned as well. But that's not the point of this issue.

**@LiudengZhang:** Thanks for the thorough context, both of you. After digging into the data flow I can see this is a bigger lift than I initially scoped — the dense conversion before the loss function means a simple flag won't cut it. Going to hold off on a PR for now, but I may circle back if I find a clean approach that shows a real speedup.

**@ori-kron-wis:** yep, makes sense. Will keep it open

## #3742: the problem about sc.pp.highly_variable_genes
**Issue:** #3742 | **Last activity:** 2026-03-17T09:43:49Z
**State:** closed | **Author:** @yuu342 | **Comments:** 9 | **Created:** 2026-03-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3742

I run the procedure but failed. sc.pp.highly_variable_genes(
    adata_sub,
    n_top_genes=2000,
    flavor="seurat_v3",
    layer="counts",
    subset=True,
    batch_key="batch"  # Change depending on the batch key for your dataset
)
The kernel automatically restarted.And when I don't set the batch_key,it can run successfully.So i wonder whether deleting the batch_key can influence the result.And if not, could youplease help me solve the problem.there are 110000 cells and 100 batches.I have retained the genes that are expressed in > 10%cells

**@ori-kron-wis:** Hard to say what went wrong. what exactly are you trying to do?
Is this a scanpy/anndata issue or scvi-tools issue and if so, why?

**@yuu342:** Thank you for your reply. I plan to use the scvi-tool to reduce the batch effect.
After selecting the highly variable genes and subset the adata,
I hope to run scvi.model.SCVI.setup_anndata(adata_sub, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata_sub, n_layers=2, n_latent=30, gene_likelihood="nb").But when I added the batch key ,I can't run the  sc.pp.highly_variable_genes.So I am considering whether I need to set the batch key.

**@ori-kron-wis:** it still not so clear to me.
are you trying to run HVG after registering the model with the same subset adata?
Usually, we run HVG before that (see our tutorials). Either way it will work.

It might be that you have a memory issue that caused the script to crash. I can't help you with that, but you can verify if you run a smaller adata of cells and batches. Also, make sure your "counts" layer is populated.

Anyway, something like this should work (verify at your end and adjust):

```
from scvi.data import synthetic_iid
import scanpy as sc
from scvi.model import SCVI

adata = synthetic_iid(n_batches=100,n_genes=10000, n_labels=10,batch_size=1000)
adata.layers["counts"] = adata.X.copy()

sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat_v3",
    layer="counts" …

**@yuu342:** Thank you for your reply.
My desired code are as you have mentioned.
adata.layers["counts"] = adata.X.copy()

sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat_v3",
    layer="counts",
    subset=True,
    batch_key=‘batch' # Change depending on the batch key for your dataset
)

SCVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    labels_key="labels",
)
model = SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
However,I cannot run the highly_variable_genes,so I cannot use the subseted adata to set up the model and train the model.And considering the memory , can I  set the batch_key =none , and then use the subseted adata to set up the model and train? Like the following code
adata.layers["counts"] = adata.X.copy()

sc.pp.hig …

**@ori-kron-wis:** I see. Yes, you should be able to still run despite you didn't set batch_key in scanpy HVG.
Whether this will be worse than running with it, its a quality of your data. So either you get a stronger machine, or run like you already did.

**@yuu342:** Thank you very much for your explanation and help!

**@ori-kron-wis:** @yuu342 I will just add that it can also be the result of numerical instability in the Seurat v3 HVG implementation used by Scanpy when fitting the LOESS curve.
If was not added before, this might also help:
`sc.pp.filter_genes(adata, min_counts=5)`
but if that still doesn't work and your dataset is large, atlas scale, yes,` batch=None` is fine

**@yuu342:** Hello,I tried your method and it still didn't work.When I changed the span to 0.8,then it(the batch_key='batch') did work .Thank you for your suggestions!

**@ori-kron-wis:** great! It probably means that some of your batch group are very small

## #838: Is there an upper bound to how many experiment batches it is practical to train at once?
**Issue:** #838 | **Last activity:** 2026-03-12T06:54:53Z
**State:** closed | **Author:** @Munfred | **Comments:** 8 | **Created:** 2020-10-19 | **Labels:** question | **URL:** https://github.com/scverse/scvi-tools/issues/838

I was wondering if there is any clear limitation to how many separate batches it is practical to train at once?

For example, I typically train scVI on datasets with ~30 batches from multiple papers each with several experiments. In my case, I'm actually using all of C. elegans scRNseq datasets (there are only 5 papers out!), and I never had a problem. The really great advantage of using scVI to do the data integration for C. elegans is that I can train it once on all the public data, and then do DE on the cells of interest forever. I would like to be able to continue training scVI on all the data of the world rather than having to choose :)

However, I know that each additional batch is another neural network, and even while the minibatches allow indefinite scaling of the number of cells, I'm not sure how the memory scaling works as I increase the number of batches. Thus I imagine that at some point I'd have to reduce the number of batches (eg treating experiments from the same paper as one batch) in order to keep fitting it on the GPU memory.

Another strategy that I imagine would allow for scaling would be to train on CPU, which is a few times slower, but in which case I can easily run jobs with hundreds of GB of RAM available.

Thoughts?

**@romain-lopez:** If you have a dataset with more than 100 batches I'd be happy to help. I think the "right" way to do this is to have a hierarchical model with a batch embedding learned along the cell embeddings and have the conventional neural nets use the embedding instead of the one-hot encoding.

**@romain-lopez:** Once you do this, it can work again on CPU, GPU, anything you would like 💯

**@adamgayoso:** I'll close this issue. @Munfred , if you'd like to make the first post on our new discourse server (discourse.scvi-tools.org) with this discussion that would be great! Probably goes in the models category if so.

**@Munfred:** Yeah I wanna be the first poster! I'll do that now :D

**@chansigit:** > If you have a dataset with more than 100 batches I'd be happy to help. I think the "right" way to do this is to have a hierarchical model with a batch embedding learned along the cell embeddings and have the conventional neural nets use the embedding instead of the one-hot encoding.

it's 2026 now, what would be the best solution now? is there any ready-to-use hierarchical models for us?

**@ori-kron-wis:** The idea discussed in the forum (learning a hierarchical batch representation instead of one-hot encoding batches) remains mostly conceptual rather than a production model. See more info here: https://discourse.scverse.org/t/models-for-handling-hundreds-of-batches/24/3

However, MrVI (multi-resolution VI), designed specifically for many samples/batches, can effectively handle a large number of samples/batches without needing an explicit hierarchical batch model. If your batches have a nested structure, I would go with that first.

I believe that with modern HW, compared to 2020, and perhaps with using our custom dataloaders, we can definitely train even a standard SCVI model on a large number of batches.

**@chansigit:** > The idea discussed in the forum (learning a hierarchical batch representation instead of one-hot encoding batches) remains mostly conceptual rather than a production model. See more info here: https://discourse.scverse.org/t/models-for-handling-hundreds-of-batches/24/3论坛中讨论的想法（学习分层批次表示而不是对批次进行独热编码）仍然主要停留在概念阶段，而不是生产模型。更多信息请参见：https://discourse.scverse.org/t/models-for-handling-hundreds-of-batches/24/3
>
> However, MrVI (multi-resolution VI), designed specifically for many samples/batches, can effectively handle a large number of samples/batches without needing an explicit hierarchical batch model. If your batches have a nested structure, I would go with that first.然而，MrVI（多分辨率变分推断）专门为处理许多样本/批次而设计，可以有效地处理大量样本/批次，而无需显式的分层批次模型。如果你的批次具有嵌套结构，我会首先选择该方法。
>
> I believe that with modern HW, comp …

**@canergen:** There's also embedding instead of one-hot for scVI (pass batch_representation='embedding' when setting up a model). This has been extensively evaluated for scPoli, and also performs well in terms of integration for scVI. However, in our experience the embeddings themselves are not meaningful representations to e.g. cluster diseased samples but contain in majority other nuisance variables.

## #3744: regress out cell-cycling score
**Issue:** #3744 | **Last activity:** 2026-03-09T07:12:02Z
**State:** closed | **Author:** @yuu342 | **Comments:** 2 | **Created:** 2026-03-09 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3744

My data is being highly influenced by cell-cycle score .Could you please provide codes to correctly regress out the
G2M.score and S.score?

**@ori-kron-wis:** Please share your questions at our discourse forum; this is not a scvi-tools issue.
Per your question, you should put them as covariates; see our documentation on this matter: https://docs.scvi-tools.org/en/latest/index.html

**@yuu342:** Thank you for your reply and guidance!

## #3738: `pip install` error in the docs
**Issue:** #3738 | **Last activity:** 2026-03-03T11:40:02Z
**State:** closed | **Author:** @flying-sheep | **Comments:** 1 | **Created:** 2026-03-03 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3738

See https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/totalVI.html


<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
 error: subprocess-exited-with-error

  × Preparing metadata (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [47 lines of output]
      + meson setup […]
      The Meson build system
      […]
      ../scipy/meson.build:216:9: ERROR: Dependency "OpenBLAS" not found, tried pkgconfig
      […]

× Encountered error while generating package metadata.
╰─> scipy
```

**@ori-kron-wis:** @flying-sheep thanks, missed that in the release, and it is fixed now (no need for older scipy version of course, as it's part of the mandatory packages of scvi-tools)

## #3623: HuggingFace scvi-hub models incompatible with scvi-tools >= 1.4
**Issue:** #3623 | **Last activity:** 2026-03-01T11:02:32Z
**State:** closed | **Author:** @nick-youngblut | **Comments:** 6 | **Created:** 2025-11-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3623

## Description

The scANVI models on HuggingFace (scvi-hub) are incompatible with scvi-tools >= 1.4 when using `SCANVI.load_query_data` directly from scvi-tools.

This is distinct from #3029 which was dismissed as a scArches issue. I am using scvi-tools directly.

## Environment

- scvi-tools version: 1.4.x (also reproducible with recent 1.3.x)
- Python: 3.12
- OS: Linux

## Minimal Reproduction
```python
from scvi.model import SCANVI
import scanpy as sc

# Load query data (e.g., PBMC 3K)
adata = sc.read_h5ad("query_data.h5ad")

# Download model from HuggingFace
model_dir = "path/to/tabula-sapiens-blood-scanvi"  # or any scvi-hub model

# Prepare query
SCANVI.prepare_query_anndata(adata, model_dir)

# This fails
model = SCANVI.load_query_data(adata, model_dir)
```

## Error
```
Traceback (most recent call last):
  File ".../scvi/model/base/_archesmixin.py", line 167, in load_query_data
    if registry[_SETUP_METHOD_NAME] != "setup_datamodule":
       ~~~~~~~~^^^^^^^^^^^^^^^^^^^^
KeyError: 'setup_method_name'
```

## Root Cause

The models on HuggingFace were saved with an older version of scvi-tools that did not include `setup_method_name` in the model registry. The current `load_query_data` implementation in `_archesmixin.py` expects this key to exist.

## Affected Models

All models on https://huggingface.co/scvi-tools including:
- `scvi-tools/human-lung-cell-atlas-scanvi`
- `scvi-tools/tabula-sapiens-*-scanvi` (24 tissue models)
- Likely all other scvi-hub models

## Sugge …

**@nick-youngblut:** Also, is the Tabula Sapiens kidney model missing from Huggingface?

 The Tabula Sapiens paper includes kidney, but there's no Tabula Sapiens kidney model on Huggingface, that I can find

**@ori-kron-wis:** Thanks, @nick-youngblut, the issue is real, but apparently happens only when you try to load a query from a model hub path. It's not exactly the same as loading from model object.
If you separate the downloaded Hub object to model and adata and use those (as suggested in the hlca hub [tutorial](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/hub/query_hlca_knn.html#download-the-reference-files)), it will work.
Nevertheless, the option you suggested should work, and I added a fix that will take care of it (it's probably happening way before v1.4). It was about a small fix in _archesmixin.py

**@ori-kron-wis:** Re Tabula Sapiens kidney model, @canergen can you help?

**@canergen:** We should retrain those models on Tabula sapiens v2 and then include kidney. I excluded for model upload all models that had only a single donor. If you want a scANVI model trained with a more recent scvi-tools version, those are available in the popV HuggingFace repository. @ori-kron-wis we should define an update schedule for scVI-hub models internally and announce here.

**@nick-youngblut:** @ori-kron-wis the models at https://huggingface.co/collections/scvi-tools/scanvi are dated to 2024. Where are the updated models:

> We should retrain those models on Tabula sapiens v2 and then include kidney

**@ori-kron-wis:** @nick-youngblut all TM models were updated in scvi-hub. Please check them.

relate to https://github.com/scverse/scvi-tools/pull/3733

## #3709: Issues arising from running multiple cards in heterogeneous accelerator cards
**Issue:** #3709 | **Last activity:** 2026-02-27T07:41:27Z
**State:** closed | **Author:** @YuZhengM | **Comments:** 8 | **Created:** 2026-02-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3709

<!-- Describe the bug -->

Using NVIDIA graphics cards, this issue does not occur. However, when using multiple cards in heterogeneous cards, an error is reported.

<!-- To reproduce -->

Below is the code section:

```python
scvi.external.POISSONVI.setup_anndata(adata, layer="fragments", batch_key=batch_key)
_model_ = scvi.external.POISSONVI(adata)
data_splitter_kwargs = {"drop_dataset_tail": True, "drop_last": False}
_model_.train(
    max_epochs=int(max_epochs),
    check_val_every_n_epoch=1,
    accelerator="gpu",
    devices=-1,
    datasplitter_kwargs=data_splitter_kwargs,
    strategy="ddp_notebook_find_unused_parameters_true",
    lr=lr,
    batch_size=int(batch_size),
    eps=eps,
    early_stopping=early_stopping,
    early_stopping_patience=int(early_stopping_patience)
)
```

<!-- Output of scvi.__version__ -->

> Version
> scvi-tools: 1.3.3

Does SCVI's distributed code support the use of multiple heterogeneous cards?

Thank you.

**@ori-kron-wis:** Hello @YuZhengM , I cant say that we can support multiple heterogeneous GPU runs, as in fact I don't have a way to test it.

What GPU cards are you trying to use together, and why its important for you to have them different?

Lets try to tackle this bug, there are many options here, as you are using many parameters in an environment that hasn't been tested by us:
What kind of errors do you get? I assume the HW is configured correctly and that you see all GPUs
I would try to avoid validation as a first step, lets focus on 1 epoch of training and no early stopping.
did you try to decrease the batch size?
did you try to change the flags here: `data_splitter_kwargs = {"drop_dataset_tail": True, "drop_last": False}`
tried a different strategy? only "ddp" or running not from a notebook (cli/s …

**@YuZhengM:** The error message is displayed below:

```
RuntimeError: HIP driver initialization failed. you might not have a HIP gpu.
```

or

```
RuntimeError: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method
```

Regarding the specific and detailed settings for the parameters of datasplitter_kwargs and strategy, could you please provide a reference link?
I will try all your suggestions. Thank you for your help.

**@ori-kron-wis:** I would just try to change False to True with drop last to see if it helps somehow. No reference.

The errors you show here hint that you might need to run this thing from script and command line and not from an interactive session like Jupyter. This is something I would check.

I dont think I ever tried to run on HIP GPU (we dont have one).

**@canergen:** Out of curiosity. HIP means that you are using an AMD GPU? Does it work for a single GPU to get acceleration. @ori-kron-wis do we test this somewhere? I'm not sure we are able to test it though.

**@YuZhengM:** Through troubleshooting, we identified the root cause. Inconsistent DDP strategies were affecting multi-GPU recognition. We modified the strategy to be compatible with Jupyter Notebook, and it now runs successfully on multiple GPUs.

**@ori-kron-wis:** Thanks, can you elaborate on what strategy you used?

**@YuZhengM:** We can run it by changing the value of the strategy parameter to "ddp_find_unused_parameters_true".

**@YuZhengM:** > We can run it by changing the value of the strategy parameter to "ddp_find_unused_parameters_true".

Later, we realized that this setting didn't feel right. When executing the script, it would launch a completely independent Python process for each graphics card. We're still investigating it!

## #3578: Clarify usage of get_normalized_expression(transform_batch= ...) in “Atlas-level integration of lung data” tutorial
**Issue:** #3578 | **Last activity:** 2026-02-25T09:56:37Z
**State:** closed | **Author:** @Siyutex | **Comments:** 1 | **Created:** 2025-10-29 | **URL:** https://github.com/scverse/scvi-tools/issues/3578

Dear scvi-tools team,

I recently used the “Atlas-level integration of lung data” tutorial (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/harmonization.html) and found it very helpful in walking through how to run the latent embedding with SCVI.

However, I encountered a common pitfall when I attempted to extract a batch-corrected full gene-space matrix via `SCVI.get_normalized_expression()`. It turned out I was getting per-batch decoded expression rather than a harmonized expression across batches because I did not use the `transform_batch` parameter—something I did not realize until afterwards.

**Suggested documentation improvement:**

* Right after `model.get_latent_representation()`, add a clear **note or warning box** explaining that:

  > “If you wish to obtain a full gene-space matrix with batch correction (for downstream processing such as trajectory inference or model training), you must use
  > `model.get_normalized_expression(..., transform_batch=<reference_batch>)`.
  > Without specifying `transform_batch`, the default decoded matrix is conditioned on each cell’s *own* batch and will therefore **not** remove batch effects.”

* Possibly include a minimal code snippet in the tutorial showing how to obtain the batch-corrected expression matrix (for example:

  ```python
  expr_df = model.get_normalized_expression(
      adata,
      transform_batch=0,
  )
  ```

  and then show how the full gene space expression might be used. Personally, I use it …

**@ori-kron-wis:** Thank you for this, @Siyutex , and sorry it was not clear beforehand.
Yes, please add your suggestion and we will merge it to the repo.
Note that for other tutorials, we put similar notes (it was just not used in this specific tutorial) - most notably the api_overview tutorial which is where people starts usually.

## #3179: MrVI slowdown due to JAX compilation update
**Issue:** #3179 | **Last activity:** 2026-02-25T07:11:35Z
**State:** closed | **Author:** @justjhong | **Comments:** 10 | **Created:** 2025-02-10 | **Labels:** bug, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/3179

<!-- Describe the bug -->

With recent updates to JAX, MrVI trains significantly slower than before. We suspect it is due to the new AOT compilation strategy (https://jax.readthedocs.io/en/latest/aot.html).

<!-- To reproduce -->

Any basic training with MrVI with a fresh install. Reproduced by @PierreBoyeau and myself.

**@ori-kron-wis:** @justjhong lmk if you want me to upper bound jax for now and to which version.
We will probably have a release in the coming week or so, so it can get into there.

**@justjhong:** Hi @ori-kron-wis, thanks for checking. I took some time this morning to try to debug it but was not able to find a solution.
I was able to figure out that the problems arise starting from jax==0.4.36. So for now, let's upper bound to jax<0.4.36 (non-inclusive).

**@PierreBoyeau:** Hi, here are a few more details about my understanding of the problem.
It seems that lightning introduces a significant overhead when training the model, [here](https://github.com/scverse/scvi-tools/blob/50e8bab7fdd983e384291f96e1e3ece37099c856/src/scvi/model/base/_jaxmixin.py#L113) and [there](https://github.com/scverse/scvi-tools/blob/main/src/scvi/train/_trainrunner.py#L96) for instance.
MrVI is notably faster at this stage without the lightning wrapper.

**@canergen:** For now pinning jax<0.4.36. Potentially related to https://github.com/jax-ml/jax/issues/26162. Check again when this is adressed. Leaving this open as pinning circumvents it but might create issues in the near future.

**@canergen:** @ori-kron-wis can you try with the fix suggested in https://github.com/jax-ml/jax/issues/26162? We can also wait for the next jax release that contains it.

**@ori-kron-wis:** The fix is about the XLA compiler used for JAX (i.e jaxlib), we can't just implement it out of the box. It is not merged yet AFAIK.

I did try Jax nightly release (consists of jaxlib nightly), but the issue remains.
pip install -U --pre jax jaxlib "jax-cuda12-plugin[with_cuda]" jax-cuda12-pjrt -f https://storage.googleapis.com/jax-releases/jax_nightly_releases.html

We need to wait for the next version that contains it unfortunately.

**@ori-kron-wis:** We also found the Jax 0.4.35 can't work for CUDA12.6+. So need to use CUDA12.4
For newer version of Jax (0.6) it works with CUDA12.6+, but is still slower than before.

**@ori-kron-wis:** Also, we are limited with jax<0.7.0 (not installed).
Jax will become optional in next version.

**@ori-kron-wis:** relates also to: https://github.com/scverse/scvi-tools/pull/3482

**@ori-kron-wis:** limit was removed. Not sure it is still slow, but Jax is either way Optional now.

## #3688: Training models on google colab TPU fail
**Issue:** #3688 | **Last activity:** 2026-02-20T11:36:04Z
**State:** closed | **Author:** @Denebium | **Comments:** 9 | **Created:** 2026-01-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3688

<!-- Describe the bug -->

Dear scVI-tools team,
First of all, thanks a lot for this wonderful package ! It is really helpful for integrating Atlases, especially the sysVI method that I discovered recently.

I have quite some big datasets, and I planned to analyse the run time comparing my local GPU and Google Colab GPU and TPU to see if it would be a viable solution to accelerate analysis on public datasets. So I tried to compare the sysVI colab notebook (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/sysVI.html) on a GPU and TPU, but the model won't train on a TPU (please see error below). From what I've seen, it need to add xla to make it able to run on a tpu (https://github.com/pytorch/xla) ?

On a classical GPU training it indicate this following statement. It mean it should be able to run on a TPU or am I missing something in the training parameters?

GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs


Best

<!-- To reproduce -->

```python
# Initialise the model
model = SysVI(adata=adata)
# Train
model.train()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
INFO     The model has been initialized
---------------------------------------------------------------------------
RuntimeError                              Tracebac …

**@ori-kron-wis:** @Denebium Thanks!, As you saw, `tpu` has not been extensively tested in scvi-tools.
I now have a branch you can install from, which will solve the issue. It will be released soon.
In colab you can install it with:
```
from scvi_colab import install
install(branch="Ori-3688-TPU-support")
```

Validation on TPU causes additional XLA graph compilations (separate from training), and switching between train/val modes can trigger recompilation. Each unique computation path needs to be compiled separately.
I recommend running TPU with early_stopping False or at a least larger number for check_val_every_n_epoch than 1

**@Denebium:** @ori-kron-wis thanks for this incredibly fast and detailed answer!
I'll test it now.

**@Denebium:** Hi again, I ran the branch with the mentioned parameters. I have interesting results if anyone find this github issue.

TLDR:
- CPU took 30mins, GPU, 5.5min and TPU 40mins of training scVI model
- sysVI was unable to run on TPU, but looking at the performances of scVI, I don't know if it even interesting to fix it



On the same notebook as before, I ran the GPU and TPU version of scVI to test the differences. The line I ran:
```
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
model.train(early_stopping =False)
```
TPU  results (v5e-1, System RAM 47.0 GB, Disk 225.3 GB): 40 mins

```
/usr/local/lib/python3.12/dist-packages/scvi/train/_trainrunner.py:98: UserWarning: The selected accelerato …

**@ori-kron-wis:** Can it be related to the validation step? Will training with train_size=1 make a difference?

**@Denebium:** Sorry for the late answer, I didn't had the time to test it and was blocked by Collab allocations of TPU.

Using `model.train(early_stopping =False, train_size=1)` on the scVI model with v5e-1 TPU on the same notebook it still take around ~40mins.

I also tested on the sysVI to see if it fixed the weird error, but with no luck.

**@ori-kron-wis:** Did you install torch_xla[tpu]? its now a requirement

**@Denebium:** Yes I believe it's installed by default in a TPU session.

Running `!pip install torch_xla[tpu]` raises this message `Requirement already satisfied: torch_xla[tpu]` before installing any package and loading the branch you mentioned Ori-3688-TPU-support.

I reran it again to see if expliciting the installation of torch xla would work but it didn't change anything in the runtime.

**@ori-kron-wis:** Did you update you installations? any other thing that might affect it? batch_size  perhaps? whats the error with sysvi?

**@Denebium:** Yes I'm reinstalling all packages on the beginning of each run to ensure to not have any out-of-date dependency problem on collab.

Changing the batch size indeed works well! It went down to less than 16min on TPU using a arbitrary (very) large batch_size of 400. It's still better than before, but approx. 3 time worse than only GPU on default settings. A bach_size of 300 still takes around 20 mins. Maybe is there a sweet spot to find for this specific problem? So autotuning when it will be finalized could be a solution there? Furthermore I didn't tested the quality of training, just the run time.
It is maybe also a underoptimization with xla https://github.com/pytorch/xla/issues/2383.
For others parameters that would impact it, I'm not knowledgeable enough in this particular topic to sug …

## #3268: Error when trying to feature native MLX accelerated scvi
**Issue:** #3268 | **Last activity:** 2026-02-19T13:58:42Z
**State:** closed | **Author:** @c0nleyinnnn | **Comments:** 4 | **Created:** 2025-03-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3268

**Description:**

Before the recent update to PyTorch's MPS support, using PyTorch MPS to accelerate scVI would result in NaN values in the returned matrix. For more details, see: [Error when training model on M3 Max MPS](https://discourse.scverse.org/t/error-when-training-model-on-m3-max-mps/1896).

I attempted to port the MLX framework to scVI by following the `simple-scvi` guide. I rewrote `_mlxvae.py`, `_mlxscvi.py`, and `_mlxmixin.py` to enable backend calls to the MLX framework for Metal acceleration. This decision was influenced by findings that the MLX framework can invoke Metal GPU computations at a higher frequency compared to PyTorch MPS. For more information, see: [phi2-llm-on-MLX-vs-Pytorch-MPS](https://github.com/mihasK/phi2-llm-on-MLX-vs-Pytorch-MPS).

With the help of various development tools and AI, the code now runs in Python using MLX. However, the returned latent matrix exhibits a similar issue to the previous PyTorch MPS problem:

```python
latent
array([[nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       ...,
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan],
       [nan, nan, nan, ..., nan, nan, nan]])
```

Due to my limited mathematical and programming skills, I am unable to resolve this issue or even identify where to start. A previous issue mentioned problems with `lgamma`, but I couldn't find the corresponding part in my code.

Addit …

**@canergen:** I really like this idea and look forward how it goes. It will most probably be faster than metal PyTorch. It’s a major undertaking to do this port though and I’m not familiar with mlx.
The lgamma thing is a PyTorch issue (we use broadcasting for the reconstruction loss and broadcasting is currently not handled correctly by metal PyTorch). Do you get None values at the first step or how long does it take to get None values?

**@c0nleyinnnn:** > I really like this idea and look forward how it goes. It will most probably be faster than metal PyTorch. It’s a major undertaking to do this port though and I’m not familiar with mlx. The lgamma thing is a PyTorch issue (we use broadcasting for the reconstruction loss and broadcasting is currently not handled correctly by metal PyTorch). Do you get None values at the first step or how long does it take to get None values?

Yes, the problem and workload were much more difficult than I thought. I mainly referred to the work of jaxscvi, but in actual operation, nan values ​​appeared in the first round. Until the end, when I tried to add some defensive numerical processing, although the values ​​were generated, the subsequent plots showed that the results were unreliable and the running spe …

**@c0nleyinnnn:** > I really like this idea and look forward how it goes. It will most probably be faster than metal PyTorch. It’s a major undertaking to do this port though and I’m not familiar with mlx. The lgamma thing is a PyTorch issue (we use broadcasting for the reconstruction loss and broadcasting is currently not handled correctly by metal PyTorch). Do you get None values at the first step or how long does it take to get None values?


An update for u: I have now basically reproduced the core module of SCVI, but the code is currently running very slowly and with a significantly abnormal loss, after some troubleshooting I think it's due to the lack of a native mlx.lgamma function, but rather a lanczos approximation built in python. I've now put in an official request at mlx, and until it responds I …

**@ori-kron-wis:** @c0nleyinnnn note I added your code + several fixes into a PR of our repo, feel free to contribute to it by forking this branch.

## #3711: Potential Library Size Distribution Inconsistency: Documentation vs Implementation
**Issue:** #3711 | **Last activity:** 2026-02-12T12:35:02Z
**State:** closed | **Author:** @LangtianM | **Comments:** 1 | **Created:** 2026-02-12 | **URL:** https://github.com/scverse/scvi-tools/issues/3711

# Potential Library Size Distribution Inconsistency: Documentation vs Implementation

## Summary

The scVI paper specifies that library size $\ell_n$ should follow a LogNormal distribution **independent of observed data** $x_n$:

$$\ell_n \sim \log \text{Normal}\left(\ell_\mu^{\top} s_n, \ell_{\sigma^2}^{\top} s_n\right)$$

**potential issue**: **Library size depends on observed counts** $x_n$ via `l_encoder(encoder_input)`, where `encoder_input` contains $\log(x_n + 1)$


## Issue: Library Size Depends on Observed Data $x_n$

According to the generative model, $\ell_n$ should only depend on:
- Batch information $s_n$
- Learned model parameters $\ell_\mu, \ell_{\sigma^2}$

It should **NOT** depend on observed counts $x_{ng}$.

### Evidence: `l_encoder` Uses Observed Data

**Location:** `src/scvi/module/_vae.py`, lines 370-400

```python
def _regular_inference(self, x, batch_index, ...):
    x_ = x
    if self.log_variational:
        x_ = torch.log1p(x_)  # x_ depends on observed counts

    # encoder_input contains the observed data!
    encoder_input = x_  # or torch.cat((x_, cont_covs), dim=-1)

    # l_encoder takes encoder_input as input
    if not self.use_observed_lib_size:
        ql, library_encoded = self.l_encoder(encoder_input, batch_index, ...)
        library = library_encoded
```

**Problem:**
- `encoder_input` contains $\log(x_n + 1)$ (the observed gene expression)
- `l_encoder` uses this to infer library size
- This means $\ell_n$ is **conditioned o …

**@canergen:** $$\ell_n \sim \log \text{Normal}\left(\ell_\mu^{\top} s_n, \ell_{\sigma^2}^{\top} s_n\right)$$ doesn't mean that $$\ell_n$$ is independent of $$x_n$$ but that the prior of $$\ell_n$$ is independent of $$x_n$$. Similar to this the prior distribution of z is $$z \sim N(0, 1)$$.

## #3669: Incorrect autotune checkpoint frequency
**Issue:** #3669 | **Last activity:** 2026-02-11T07:50:06Z
**State:** closed | **Author:** @FrenkT | **Comments:** 5 | **Created:** 2026-01-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3669

Hi,

I noticed that the autotune pipeline saves checkpoints only at the end of training with `save_checkpoints=True`, which was unexpected.

I am running the following:
```python
autotune.run_autotune(
    TorchMRVI,
    data=adata,
    mode="min",
    metrics="elbo_validation",
    search_space=search_space,
    num_samples=10,
    resources={"cpu": 10, "gpu": 1},
    logging_dir=out_dir,
    save_checkpoints=True,
    log_to_driver=True
)
```
I think that this line of code might be causing the issue, because `self.metrics` is a list and so `"elbo_validation"` (or even `"validation_loss"` like in the tutorial) would not be matched:
https://github.com/scverse/scvi-tools/blob/d01e8ec34a525e73e9bbbd111ec1671f4834a638/src/scvi/autotune/_experiment.py#L722

Is this intentional? I am also not sure on whether this might be causing other issues with metrics reporting.
Happy to open a PR based on feedback.

#### Versions:
`1.4.1`

**@ori-kron-wis:** Hey @FrenkT ,
It is not entirely clear to me if you are also asking to put the option to save checkpoints also between batches/epochs? Right now we support validation or train end, based on the metric you chose.

**@FrenkT:** I think that this is what confuses me:
> Right now we support validation or train end, based on the metric you chose.

Is validation end really possible? The `on = "validation_end" if "validation" in self.metrics else "train_end"` would require having a metric called (exactly) `"validation"`, but for example MRVI doesn't have a `"validation"` alias.
For scib-based optimisation it is possible to specify the callback frequency.

So I was reporting this mainly because it seemed like an unwanted behaviour.

On a separate note (happy to open a separate issue for that), it looks like in all cases (both validation_end and train_end) we would not checkpoint the best model in a set up where we have `early_stopping=True`. That would probably require using `ray.train.CheckpointConfig`.

**@ori-kron-wis:** I think that we might have missed [0] to self.metrics, so:
`on = "validation_end" if "validation" in self.metrics[0] else "train_end"`
should solve it.

But this checkpoint is an internal Ray checkpoint; it is not intended to save your best model during the run.

I don't see any reason why using early stopping with ray autotune will not work in that sense (you will get the best params while using early stopping, then train the model with those exact same parameters).

I don't understand why scib metrics should have a higher frequency in its callback, either; it will be much slower. It takes far more time to calculate a scib metric then the losses during training.

You are welcome to suggest a PR for additional fixes you might see as relevant, and we will review it.

**@FrenkT:** > I think that we might have missed [0] to self.metrics, so: `on = "validation_end" if "validation" in self.metrics[0] else "train_end"` should solve it.
>
Yes, that's what I was trying to report originally.

> But this checkpoint is an internal Ray checkpoint; it is not intended to save your best model during the run.
>
> I don't see any reason why using early stopping with ray autotune will not work in that sense (you will get the best params while using early stopping, then train the model with those exact same parameters).

Maybe I am confused by the use-case of checkpointing for autotune. I was trying to let autotune train N models and let it save the best checkpoint for each one of them on disk. I can then decide which one to load and use for further analysis, without having to ret …

**@ori-kron-wis:** No worries. I see what you mean. Perhaps early_stopping + patience=0 or 1 will still be good enough, given the validation metric fix, just to find the optimal set of parameters, then, add another train session.

## #3672: Resolvi differential expression takes long time to run
**Issue:** #3672 | **Last activity:** 2026-02-11T07:47:57Z
**State:** closed | **Author:** @jairaj-mathur | **Comments:** 7 | **Created:** 2026-01-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3672

<!-- Describe the bug -->

Differential expression with group by as leiden_resolvi (one vs none for all Leiden clusters) takes 30 minutes per cluster. Even if run for a single comparison (one vs all) it takes 30 minutes.

My dataset is Xenium 5k, 200k cells. Is this normal?

<!-- To reproduce -->

```python
# Your code here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[Paste the error output produced by the above code here]
```

#### Versions:

1.4.1

<!-- Relevant screenshots -->

**@ori-kron-wis:** Please post your code here so we can review it.
How many clusters do you have?
Did you try with batch_correction=False (like I suggested in discourse)

**@jairaj-mathur:** Hi Ori, it was ran with

```
RESOLVI.setup_anndata(concat_adata, categorical_covariate_keys=["region"], batch= None, layer= "counts")
model= RESOLVI(concat_adata, semisupervised=false downsample_counts=false)
model.train(batch_size=256, max_epochs=100)
adata= model.adata.copy()
adata.obsm[X_resolvi] = model.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_resolvi")
sc.pl.umap(adata)
sc.tl.leiden(adata, resolution=0.75, flavor="igraph", niter=-1)
results=model.differential_expression(adata, groupby=leiden)
```

This yielded 22 clusters, and took 9.5 hours

From your discourse post, I believed that batch_correction is set to False by default , thus didn't run. I can try again and let you know.

**@canergen:** I'm sorry for this issue. The likely reason is that importance sampling in pyro can be slow. Apparently, currently importance sampling can't be disabled: https://github.com/scverse/scvi-tools/blob/14daf4729b9ce36102eed964d8bc3adc1c1223bc/src/scvi/external/resolvi/_model.py#L471. We should fix this and add an option to use get_normalized_expression instead for a faster computation.

**@jairaj-mathur:** No worries, thank you for your time to get into the root of this. I will close this issue for now.

**@canergen:** Reopened as I would argue we should harmonize behavior to other models.

**@ori-kron-wis:** @jairaj-mathur, please see this branch: https://github.com/scverse/scvi-tools/tree/Ori-3672-Resolvi-DE-IS-flag
It consists of 2 new parameters for the RESOLVI DE, n_samples and run_IS_DE. They will both control the speed (but also accuracy) of the DE.
Try to run the DE from this branch with `run_IS_DE=False` and a lower number of n_samples (1-3), which should improve speed drastically.
Can you confirm it does?

**@ori-kron-wis:** Made a revision to this issue correction that can be found here: https://github.com/scverse/scvi-tools/pull/3708

It might be that we need to add a fix to other model sampling behavior, but this one deals specifically with the pyro IS function, which ResolVI is the only model to be using, so let's concentrate only on this here.

## #3655: Error when downsample_counts=True
**Issue:** #3655 | **Last activity:** 2026-02-11T07:29:59Z
**State:** closed | **Author:** @plezar | **Comments:** 5 | **Created:** 2025-12-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3655

<!-- Describe the bug -->

I am running RESOLVI on Xenium data generated using a targeted panel of ~300 genes. I have confirmed that there are no cells with zero expression and that each cell has a minimum of 11 detected transcripts, which I considered a reasonable threshold given the limited panel size.

I suspect the issue I am encountering may be related to issue #3416 , where one of the maintainers recommended setting `downsample_counts = False` for sequencing-based data, in addition to ensuring that there are no empty cells or spots. Following this suggestion, I trained the model without downsampling, which resulted in good alignment of batches in the latent space.

In the attached figure, the middle column shows the data before applying RESOLVI, and the right column shows the data after RESOLVI correction. Although Xenium data are not sequencing-based, I am wondering what impact disabling count downsampling has in this context and whether using `downsample_counts = False` is appropriate for my data.

Thank you for maintaining scvi!

<!-- To reproduce -->

```python
import numpy as np
import scanpy as sc
import scvi

adata = sc.read("mydata.h5ad")
adata.obsm["X_spatial"] = adata.obsm["spatial"].copy()

print("Minimum number of transcripts: " + str(np.min(np.sum(adata.layers["counts"].toarray(), axis=1))))
```
Minimum number of transcripts: 11.0

```
scvi.external.RESOLVI.setup_anndata(adata, layer="counts", batch_key = "batch")
unsupervised_resolvi = scvi.external.RESOLV …

**@ori-kron-wis:** Im not sure if this relates to https://discourse.scverse.org/t/error-in-training-resolvi-model/3904, but we made a fix recently, so I suggest rerunning with the updated main branch of scvi-tools. Otherwise, there's a problem with your data/environment (pyro or lightning versions).

**@plezar:** I can confirm that updating scvitools using `pip install -U "scvi-tools[cuda] @ git+https://github.com/scverse/scvi-tools.git@main"` worked and I am no longer getting this error

**@LizEve:** I keep getting the same User Warning about too few cells for column. I'm curious why this warning shows up and if it affects the model results at all. I'm using the most recent main branch. And my data has been filtered. The setup_anndata seems to have created adata.obs['_scvi_ind_x'] which is a column with a unique number for each cell in the dataset.

My model runs fine, I just want to understand why the error is showing up. Thanks!

`RESOLVI.setup_anndata(adata, layer="counts", batch_key="batch")`

```
INFO     Generating sequential column names
INFO     Generating sequential column names
/local_disk0/.ephemeral_nfs/envs/pythonEnv-7494aa1c-812b …

**@14lwt1:** Hi,

I would like to follow up on the same warning brought up by LizEve.
I have downloaded the dataset in the tutorial (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/resolVI_tutorial.html) and gone through the same steps.
Nonetheless, the warning "UserWarning: Category 0 in adata.obs['_scvi_ind_x'] has fewer than 3 cells. Models may not train properly." still shows up.
I have also tried it with other datasets and made sure that cells with low expression are removed.
All of them result in the same warning.
Allowing downsample in the following step (scvi.external.RESOLVI) results in the following error when training the model:
Exception raised during training. <class 'NameError'> Input arguments must all be instances of Number, torch.Tensor or objects implementing __torch …

**@ori-kron-wis:** I can confirm this error reappeared, probably related to other packages updates. A fix is issued in this PR:  https://github.com/scverse/scvi-tools/pull/3697
It might also have to do with python 3.13

## #3698: [Bug/Feature] Asymmetric `n_layers` for encoder and decoder.
**Issue:** #3698 | **Last activity:** 2026-02-09T13:41:09Z
**State:** closed | **Author:** @ehvr20 | **Comments:** 2 | **Created:** 2026-02-03 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3698

<!-- Describe the bug -->

I am attempting to experiment with a weakened decoder as a means of reducing latent variable collapse in my scVI model. The idea being to have the **encoder use 4 hidden layers** and the **decoder use 1 hidden layers**. I have been combing the documentation for a means of doing this and intuitive it appeared to be possible via: [VAE.extra_encoder_kwargs and VAE. extra_decoder_kwargs](https://docs.scvi-tools.org/en/stable/api/reference/scvi.module.VAE.html#scvi.module.VAE). However upon implementing this I was met with the error shown below. I went digging into the source code and found that the `n_layers` argument is explicitly passed from scVI to the VAE and again explicitly passed to the Encoder/SCVIDecoder even when not specified globally.

Whilst asymmetric VAE is not by any means a default users should start with, the flexibility to make one should arguably be possible. The framework to allow it exists and is specified in the API as a potential possibility as such a refactor for the implicit communication of `n_layers` would be great. Alternatively `kwargs` could be given priority when passed to encoder/decoder.

If you have any suggestions for any simple workarounds that I could otherwise try in the short term, I would love to hear them.

<!-- To reproduce -->

```python
...

model = scvi.model.SCVI(
      adata,
      ...
      extra_encoder_kwargs={'n_layers': 4},
      extra_decoder_kwargs={'n_layers': 1}
)

...
```

```pytb
TypeError: scv …

**@ori-kron-wis:** @ehvr20, you can check the fix in the PR, see if it works for you

**@ehvr20:** Perfect, thank you!

## #3682: Integration Testing CI Test Failure on python 3.12
**Issue:** #3682 | **Last activity:** 2026-02-02T08:49:29Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 1 | **Created:** 2026-01-22 | **URL:** https://github.com/scverse/scvi-tools/issues/3682

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/21232717210) to review. @scverse/anndata

**@ori-kron-wis:** This waits for the Anndata release following Scvi-Tools release that will support Pandas3 and Python 3.14

## #3683: Integration Testing CI Test Failure on python 3.13
**Issue:** #3683 | **Last activity:** 2026-02-02T08:49:21Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 1 | **Created:** 2026-01-22 | **URL:** https://github.com/scverse/scvi-tools/issues/3683

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/21232717210) to review. @scverse/anndata

**@ori-kron-wis:** This waits for the Anndata release following Scvi-Tools release that will support Pandas3 and Python 3.14

## #3687: Integration Testing CI Test Failure on python 3.13 with prerelease dependencies
**Issue:** #3687 | **Last activity:** 2026-02-02T08:49:11Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 5 | **Created:** 2026-01-28 | **URL:** https://github.com/scverse/scvi-tools/issues/3687

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/21421446277) to review. @scverse/anndata

**@ori-kron-wis:** This waits for the Anndata release following Scvi-Tools release that will support Pandas3 and Python 3.14

**@ilan-gold:** @ori-kron-wis I think the point of this test is to highlight how you might be able to prepare for that release in advance.  Can you not use `if version("pandas") >= Version("3")`, then do thing? Or you're blocked by not having a test against `anndata` `main` in this repo?

**@ori-kron-wis:** No worries, @ilan-gold , as we speak, Im just merging a PR that will fix all pandas3 anndata clashes in scvi-tools so the main branch of scvi-tools will be ready for Anndata pandas 3 release, and all integration tests should pass following that with no pinned versions or anything.

not sure about `if version("pandas") >= Version("3")` - we dont use that

**@ilan-gold:** > not sure about if version("pandas") >= Version("3") - we dont use that

Ah yea, just something we use for turning behavior on-off depending on runtime deps, like: https://github.com/scverse/anndata/blob/2a2c0e3198c298a5c80a73ac343c63203b5ca133/src/anndata/compat/__init__.py#L99-L101 which allows us to call different APIs based on different versions.  But maybe you don't need this to smooth things out.

Sorry for all the hooplah!

**@ori-kron-wis:** Integration tests passes so Im closing now.

## #2904: Use explicit configs instead of kwargs
**Issue:** #2904 | **Last activity:** 2026-01-29T14:08:37Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-18 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2904

Currently we use kwargs plumbing extensively to route different sets of arguments to model parameters, training, dataloaders, etc. For example, for `SCVI`:
```
model = SCVI(**kwargs) <- kwargs for VAE
model.train(
    datasplitter_kwargs=... <- kwargs for DataSplitter
    plan_kwargs=... <- kwargs for TrainingPlan
    **kwargs <- kwargs for Trainer
)
```
All these different sets of kwargs can be confusing since users need to refer to different parts of the documentation, and they might not know where a certain parameter should go (_e.g._ should learning rate go to the `Trainer` or `TrainingPlan`?)

One way to address this would be to use configs defined by dataclasses. For example:
```
@dataclass
class VAEConfig:
    n_hidden: int = 128
    n_latent: int = 10
    ...
```
So just initializing `SCVI()` would use the default config, but in order to change a parameter, a user would have to define a new dataclass `VAEConfig(n_hidden=256)` that can automatically check arguments. The advantage here would be even more clear for the train function, where the docstring would only contain descriptions for `DataSplitterConfig`, `TrainingPlanConfig`, and `TrainerConfig`. This means that all models using, _e.g._ `TrainingPlan`, will only have one config, leading to less redundancy.

## #3611: Fail to create reproducible model
**Issue:** #3611 | **Last activity:** 2026-01-29T14:08:17Z
**State:** closed | **Author:** @JoseSanchezVillicana | **Comments:** 9 | **Created:** 2025-11-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3611

<!-- Describe the bug -->

Hi scivi-tools team,

I am currently working on an MrVI model using scRNA-Seq data from two different publications. I was following the [Quick Start Tutorial](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/scrna/MrVI_tutorial.html) and I set the random seed just like it is recommended there. But I run my code two times one after the other and I get two different outputs for the local sample distances. These distances do not vary too much, but there is clearly a difference between them.

I have even attempted to set other possible sources of randomness manually using the same seed, but this results in the same problem.

I am working for an upcoming publication and reproducibility is really important. I would really appreciate if anyone could tell me whether I am missing something or how to fix the problem.

<!-- To reproduce -->

These are the potential sources of randomness I am attempting to manually control.

```python
# For reproducibility purposes
seed = 42

# Python / NumPy / Random
random.seed(seed)
np.random.seed(seed)
os.environ["PYTHONHASHSEED"] = str(seed)

# PyTorch
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# JAX
jax.random.PRNGKey(seed)
os.environ['JAX_ENABLE_X64'] = '0'
os.environ['JAX_PLATFORM_NAME'] = 'gpu'

# scivi-tools global seed
scvi.settings.seed = seed

# Disable JAX async dispatch (prevents nondeterminism)
os.environ[' …

**@ori-kron-wis:** When you say you run them one after the other, did you completely clear your session between runs? i.e, restart the notebook and clear all cache and outputs if working on a notebook, and/or close the console and start a Python session again if from CLI or IDE. You need to run the whole code once, start to end, is the only way to be sure if there are reproducible results.

If you are under the same session and running the same code w/o a restart it or cell by cell if on a notebook - the results will not be reproducible, despite those many seeds you made, they will be close though.

**@JoseSanchezVillicana:** > When you say you run them one after the other, did you completely clear your session between runs? i.e, restart the notebook and clear all cache and outputs if working on a notebook, and/or close the console and start a Python session again if from CLI or IDE. You need to run the whole code once, start to end, is the only way to be sure if there are reproducible results.
>
> If you are under the same session and running the same code w/o a restart it or cell by cell if on a notebook - the results will not be reproducible, despite those many seeds you made, they will be close though.

Hey, thank you for the quick response! I am working on a notebook, and I restarted the kernel and cleared all outputs between runs. Indeed, the results are close, but for some cell types, the variation is s …

**@ori-kron-wis:** @JoseSanchezVillicana I verified that our mrvi tutorial reproduces fully if I rerun it after restarting and clearing the cache. That includes get_local_sample_distances part, there was no need for additional seeding.

What I can suggest is to update to most recent version and run the mrvi torch version (as we stopped supporting the jax version). Plus, verify that the tutorial reproduces as well at your side, like i did.

After that, continue with your personal analysis.

Is there any additional functions you want me to check?

**@JoseSanchezVillicana:** @ori-kron-wis I have rerun the analysis using the torch backend, but it is still not the same results between them.

Also, I have come up with this message (when running the get_local_samples method) I thought to share: `/home/villicana/.conda/envs/plotting_app/lib/python3.11/site-packages/torch/nn/functional.py:6487: UserWarning: There is a performance drop because we have not yet implemented the batching rule for aten::_scaled_dot_product_flash_attention_for_cpu. Please file us an issue on GitHub so that we can prioritize its implementation. (Triggered internally at /pytorch/aten/src/ATen/functorch/BatchedFallback.cpp:81.)`

**@ori-kron-wis:** Can you please attach what exactly is different that you see (images of it)?

**@JoseSanchezVillicana:** I forgot to mention I am also unable to reproduce the tutorial you have.

These are the plots I generate to check if the models are reproduced the same way. I restarted and cleared all outputs between runs. I am now running the v: 1.4.0.post1 (because I updgraded as you recommended). I am running the MrVI with Torch backend. The code I use to generate the plots is exactly the same between runs.

The distances should be the same everytime, right?

Distance dist across cell types (1st run & 2nd run):
<img width="722" height="517" alt="Image" src="https://github.com/user-attachments/assets/17a82217-402c-41c3-b8d9-80934e9e18a5" />

<img width="1048" height="531" alt="Image" src="https://github.com/user-attachments/assets/d1196f35-24e6-4f66-90a0-d4a6864bb3a5" />

Counterfactual distance from al …

**@ori-kron-wis:** Can you share your code here or privately (at least the downstream plotting)? I want to see what exactly you did and apply it also to see if I get changes as well

**@JoseSanchezVillicana:** After the training (just the first plot I shared):

```
# Retaining cell to cell distances
dists = model.get_local_sample_distances(
    adata,
    keep_cell= True,
    groupby= 'subannotation',
    normalize_distances= False,
    use_mean= True
)

# Avg distance from other samples per cell: vector to quantify sample effect heterogeneity within cell populations
cell_dists = dists['cell']
dist_vec = []
celltype_anno = []
sample_anno = []
target_anno = []

for i in range(cell_dists.shape[0]):
    subannot_temp = adata.obs['subannotation'].iloc[i]
    subannot_temp_index = np.where(cell_dists['sample_x'].to_numpy() == subannot_temp)[0][0]
    vec_temp = cell_dists[i, subannot_temp_index, :].to_numpy()
    dist_vec.append(vec_temp)
    celltype_anno.append([subannot_temp]*len(vec_temp))
    sa …

**@ori-kron-wis:** > Distance dist across cell types (1st run & 2nd run):

Well, here you have a completely different kind of plots. So what exactly are you comparing? As I said, in a jupyter setting, everything is important for reproducibility. You need to run **exactly** the same thing. Right now, I see different figures, resulting from different methods or scripts (?) so all other things are not reproducible just because of that (and probably there are other things).

Having said that, we don't expect large differences even for different environments and settings, and here we see large differences. Has your model even converged? seem other issues might exist before we even try to take care of the reproducibility thing. For me, 1st plot is like model stopped training before convergence.
I think what we see …

## #3684: Can't save SCVI model if using custom datamodule
**Issue:** #3684 | **Last activity:** 2026-01-27T23:19:37Z
**State:** closed | **Author:** @deto | **Comments:** 4 | **Created:** 2026-01-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3684

<!-- Describe the bug -->

I'm currently experimenting with providing a custom, scDataset-based, datamodule in order to alleviate on-disk dataloading bottlenecking when training on large datasets with scVI.  However, It looks like you are unable to save the model if it is initialized without an anndata file.

It seems the issue is that self.adata _should_ be None, but the backing attribute self._adata is never initialized.  And even if that is fixed, I believe there will still be issues because self.registry is similarly not initialized when using a custom datamodule.

<!-- To reproduce -->

```python

# My custom datamodule
dm = scvi_datamodule.scDatasetModule(
    ad_paths=ad_paths,
    batch_key="sample_id",
    batch_size=512,
    num_workers=8,
    val_proportion=0.05,
    test_proportion=0.0,
    var_indices=var_indices,
    obs_indices=obs_indices,
)


model = SCVI(adata=None, n_latent=100, gene_likelihood="nb")

model.train(
    max_epochs=1,  # 1 for testing
    datamodule=dm,
    early_stopping=True,
    early_stopping_warmup_epochs=10,
    plan_kwargs=dict(
        n_epochs_kl_warmup=10,
        reduce_lr_on_plateau=True,
        lr_patience=5,
        lr=0.01,
    ),
)

model.save(scvi_model_dir)  # error here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError                            Traceback (most recent call last)
Cell In[1], line 64
     49 model = SCVI(adata=None, n_latent=100, gene_likeli …

**@ori-kron-wis:** Hey @deto,
You can check our code to see how we deal with custom dataloaders save/load, see the tests here: https://github.com/scverse/scvi-tools/blob/main/tests/dataloaders/test_custom_dataloader.py inc save/load

Basically, I would expect this command to work:
```
    # save
    model.save("custom_model", save_anndata=False, overwrite=True, datamodule= dm)
    # load it back
    loaded_model = scvi.model.SCVI.load("custom_model", adata=False, datamodule= dm)
```

**@deto:** Still fails on the self.get_var_names call [here](https://github.com/scverse/scvi-tools/blob/3b856b5fb30905177e732b9c3552a70724e2922f/src/scvi/model/base/_base_model.py#L769)

Though if it didn't fail there, I think it'd fail on line 776: 1 `method_name = self.registry.get(_SETUP_METHOD_NAME, "setup_anndata")` because there is no self.registry

**@ori-kron-wis:** This is something that needs to be implemented in your custom datamodule (which I don't know of, but I don't think scdataset will be different), as we did for the others (lamin, cellxgene etc). Follow what we did there and it should be fine.

I don't think the base model need to change, but if you think otherwise, please suggest a PR, and Ill take a look.

**@deto:** Thanks for your help!  I've implemented the registry and then passed the datamodule registry to the model class when initializing.  Now it looks like saving is working correctly.  For loading, I can get it to work if I omit the datamodule parameter on-load.  If I provide it, it looks like it passes it all the way into the model (and then the module) constructor and that yields an error as it is not an expected parameter (maybe this is for other model types than SCVI though?).

Thanks again!

## #3676: RuntimeError (Long vs Float) when using dispersion='gene-batch' in SCVIVA
**Issue:** #3676 | **Last activity:** 2026-01-18T10:04:14Z
**State:** closed | **Author:** @hangyinn | **Comments:** 2 | **Created:** 2026-01-17 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3676

Hi Team,

I encountered a RuntimeError when initializing `scvi.external.SCVIVA` with `dispersion="gene-batch"`. The error occurs in `_module.py` during the forward pass, specifically when handling batch-specific dispersion.

The issue appears to be a dtype mismatch between the generated one-hot encoding (Long) and the dispersion parameter `px_r` (Float) during matrix multiplication.

```python
nichevae = scvi.external.SCVIVA(
    ref_adata,
    n_hidden=128,
    n_latent=30,
    n_layers=2,
    gene_likelihood="nb",
    dispersion="gene-batch",
    dropout_rate=0.1,
)

plan_kwargs = {
    "lr": 1e-3,                     # Default is usually fine, reduce to 5e-4 if loss is unstable
    "reduce_lr_on_plateau": True,   # Reduces LR when learning stalls
    "lr_patience": 15,              # How many epochs to wait before reducing LR
    "lr_factor": 0.5,               # Cut LR in half when stalled
}

nichevae.train(
    max_epochs=600,
    early_stopping=True,
    accelerator="gpu",
    check_val_every_n_epoch=1,
    batch_size=4096,
    early_stopping_patience=15,
    early_stopping_warmup_epochs=50,
    early_stopping_monitor="elbo_validation",
    plan_kwargs=plan_kwargs,
)
```

The error:

```python
INFO: GPU available: True (cuda), used: True
INFO:lightning.pytorch.utilities.rank_zero:GPU available: True (cuda), used: True
INFO: TPU available: False, using: 0 TPU cores
INFO:lightning.pytorch.utilities.rank_zero:TPU available: False, using: 0 TPU cores
INFO: LOCAL_RANK: 0 - C …

**@ori-kron-wis:** Thanks @hangyinn , this can be easily fixed by adding a float where relevant, and I added more tests to make sure of different dispersion inputs (for other models as well).
However, @LevyNat should SCVIVA support all possible dispersion inputs, or is that a legacy from previous models? In Resolvi, for example, we can only support "gene" or "gene-batch" and not "gene-cell" or "gene-label" as dispersion inputs

**@LevyNat:** @ori-kron-wis yes, it should support all dispersion inputs.
In the paper we only worked with Poisson so we did not have this bug.

## #3673: Imputation/denoise output
**Issue:** #3673 | **Last activity:** 2026-01-15T07:05:53Z
**State:** closed | **Author:** @Huiyueli | **Comments:** 1 | **Created:** 2026-01-15 | **URL:** https://github.com/scverse/scvi-tools/issues/3673

Dear authors,

When using the code below for data denoise/imputation, how to set the library_size in get_normalized_expression()? to obtain the output in count-scale, rather than normalized output?

scvi.model.SCVI.setup_anndata(adata,layer="counts")
vae = scvi.model.SCVI(adata)
vae.train()
vae.get_latent_representation()
vae.get_normalized_expression()

Also, are there any recommendations for parameters in vae.train(),e.g., max_epochs and train_size=0.9; as well as n_samples in get_normalized_expression()?

If I have multiple samples in adata, may I input the whole dataset together to do denoise? or do denoise for each sample, then combine the results?

Thank you!

**@ori-kron-wis:** Answering in the discourse forum.

## #823: DE on data subset
**Issue:** #823 | **Last activity:** 2026-01-06T13:06:37Z
**State:** closed | **Author:** @chenlingantelope | **Comments:** 8 | **Created:** 2020-10-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/823

<!-- Describe the bug -->
When running DE on a subset of a dataset with lots of batches, seems like I need to re-index the batches of subsets so that it is consecutive from 0 ~ n_batches. Perhaps this can be done automatically within the DE function.

<!-- To reproduce -->
```python
de_celltype = {}
for tissue in np.unique(adata.obs["tissue"]):
    sub_adata = adata[adata.obs["tissue"] == tissue]
    de_celltype[tissue] = vae.differential_expression(
        sub_adata, groupby="Propagated.Annotation", batch_correction=True
    )
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->
```pytb
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-143-b1df721788f5> in <module>
      2 for tissue in np.unique(adata.obs['tissue']):
      3     sub_adata = adata[adata.obs['tissue']==tissue]
----> 4     de_celltype[tissue] = vae.differential_expression(sub_adata, groupby = 'Propagated.Annotation', batch_correction=True)

/data/yosef2/users/chenling/miniconda3/envs/scvi-tools/lib/python3.8/site-packages/scvi/core/models/rnamixin.py in differential_expression(self, adata, groupby, group1, group2, idx1, idx2, mode, delta, batch_size, all_stats, batch_correction, batchid1, batchid2, **kwargs)
    187             batch_size=batch_size,
    188         )
--> 189         result = _de_core(
    190             ada …

**@galenxing:** Hi @chenlingantelope!

I think my open PR #817 fixes this.

Can you pip install that branch and let me know?
`pip install git+https://github.com/yoseflab/scvi-tools.git@transformbatch_fix`

Thanks!

**@dKlee99:** Hi,
I have experienced the same issue above when I tried to extract batch corrected scvi normalized expression using transform_batch option. Here is the command I ran.

```adata_scvi.layers["scvi_normalized"] = model_scvi.get_normalized_expression(adata_scvi,library_size = 10e3, batch_key="library", transform_batch=['my_batch'])```
I have installed scvi-tools using following commands
```git clone https://github.com/scverse/scvi-tools```
```pip install -e .```

Installed scvi-tools is version 1.1.3
any ideas how to solve this issue?
below is error message

---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[62], line 1
----> 1 adata_scvi.layers["scvi_normalized"] = mod …

**@canergen:** Hi, the issue points to that `transform_batch=['CHR0211']` is not an existing batch category. The function has changed in the meantime from the error message above. Please provide adata.obs[batch_key].value_counts if you think the category should exist.

**@dKlee99:** Hi,
Thanks for the reply.
I used library as batch_key and here is the result for `adata.obs[batch_key].value_counts` .
<img width="256" alt="image" src="https://github.com/scverse/scvi-tools/assets/82995207/cddaf495-33ff-40be-8a76-b721af6f9e9d">

**@canergen:** Can you check the version of scvi-tools installed?

**@LitalBarak96:** i have the same problem. it dont recognize the batch key›

<img width="535" height="331" alt="Image" src="https://github.com/user-attachments/assets/e76c757a-2c8f-4fdc-9206-0d743f804471" />

<img width="1150" height="1016" alt="Image" src="https://github.com/user-attachments/assets/317ac80c-080e-4838-81a0-a2f5725e7311" />

**@ori-kron-wis:** Im not so sure on the context of your latest post here, but _scvi_batch is an internal coding for the model registry.

When you run get_norm with transform_batch you should use your original batch_key values (can be other things- likely not 1 2 3 4 5 or 6 but a meaningful name), Im not sure what you used.

**@LitalBarak96:** okay thank you for that, what i didn't understood is how to write my batch key . if it will help someone in the future i wrote the batch key ["my_batch_key"]
again thank you

## #192: Saving a trained model?
**Issue:** #192 | **Last activity:** 2025-12-22T13:34:00Z
**State:** closed | **Author:** @vals | **Comments:** 18 | **Created:** 2018-09-18 | **URL:** https://github.com/scverse/scvi-tools/issues/192

Hi,

After training a large model on a large data set, it would be nice if I could save it so I could re-use it for e.g. future DE analysis, or maybe to warm-start with new data, or to send to collaborators.

Is there any way to save a model for future loading? Is using pickle the best way to go about this?

Best,
/Valentine

**@jeff-regier:** That functionality is pytorch but we haven't made a nice wrapper for it yet in scVI. We should. In the meantime, this works:
```
model = MyModel()
# ... after training, save your model
model.save_state_dict('mytraining.pt')

# .. to load your previously training model:
model.load_state_dict(torch.load('mytraining.pt'))
```

**@vals:** Thanks! This is easy enough!

It didn't work directly as written here though, it seems you need to do
```
...
torch.save(model.state_dict(), 'mytraining.pt')
```

**@wikiselev:** I am now in 2022 and none of the above worked for me... Only this worked with `scvi-tools==0.17.1`:
```
model.save(path_to_model_folder)
```
To load the model:
```
model = scvi.model.SCVI.load(path_to_model_folder, adata)
```
where adata is AnnData object organized in the same way as data used to train model.

**@adamgayoso:** Hi @wikiselev thanks for using scvi-tools. Just want to highlight this info is readily available in the documentation/tutorials, and that the code in this issue doesn't work because we added another layer on top of PyTorch Modules

**@wikiselev:** Thanks @adamgayoso! Could you provide a link to the documentation where it is mentioned as I can't find it anywhere?

**@adamgayoso:** 1. https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html#Saving-and-loading
2. https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html#save

**@shashkat:** Hello there, I have followed the links above, but upon loading the data, I am getting an error. I don't know what is wrong. Any help would be highly appreciated.

i saved using:

model.save('/content/ldvae')

my load command:
model = scvi.model.LinearSCVI.load('/content/ldvae', adata = adata)

The error:

INFO     No backup URL provided for missing file /content/ldvae/model.pt
---------------------------------------------------------------------------
FileNotFoundError                         Traceback (most recent call last)
[/usr/local/lib/python3.7/dist-packages/scvi/model/base/_utils.py](https://localhost:8080/#) in _load_saved_files(dir_path, load_adata, prefix, map_location, backup_url)
     68         _download(backup_url, di …

**@wikiselev:** Hi @shashkat , looks like you've used a wrong function for loading, try using `scvi.model.SCVI.load` instead of `scvi.model.LinearSCVI.load`.

**@shashkat:** <img width="258" alt="Screenshot 2022-09-30 at 9 13 33 PM" src="https://user-images.githubusercontent.com/72993520/193307472-ffe64fc8-3c63-4e78-a768-6c9b9dac2370.png">
>

Hi @wikiselev, thanks for the quick reply. I tried using `scvi.model.SCVI.load` instead of `scvi.model.LinearSCVI.load`, but am still getting the exact same error:

I have also attached a picture of contents of the folder where i saved the model.

Error-

INFO     No backup URL provided for missing file /content/ldvae/model.pt
---------------------------------------------------------------------------
FileNotFoundError                         Traceback (most recent call last)
[/usr/local/lib/python3.7/dist-packages/scvi/model/base/_utils.py](https://localhost:8080/#) …

**@adamgayoso:** It appears the names of the files have changed inside the ldvae directory, as well as some other folders like assets and variables that should not be there.

**@vttrifonov:** The interface that has the training data as part of loading the model feels awkward to me. If feature names is all that is needed perhaps they can be included as part of the model metadata being saved and then read at load time. In fact I would like to be able to query this metadata after loading. I am running into this issue because I was handed an scvi saved pt file but do not have access to the training data (or the features used).

`SCVI.prepare_query_anndata` is able to work only with a file name but load is not. This is strange: I should be able to load and then prepare.

`prepare_query_anndata` also has an argument which lets you get the features: so this function returns either an index or an anndata object! This is also strange: how is returning an index preparing the annd …

**@canergen:** Hi, it's a closed issue of two years ago and your request is somewhat confusing to me. If you want to get the feature names, you can read the saved model with torch.load and access all fields including the var_names. If you are trying to do something else, please open a new issue and give a clear description.

**@vttrifonov:** Apologies for the confusing comment. My point is that the load interfaces are a bit confusing. For example,

I tried `scvi.model.SCVI.load("model.pt")` but got `ValueError: Save path contains no saved anndata and no adata was passed`. On the other hand, `scvi.model.prepare_query_anndata(new_data, 'model.pt')` works and it does not complain about anything. It just seemed to me I should be able to do `load` and then `prepare_query_anndata` with loaded model.

The second comment was that `prepare_query_anndata` returns either an index or anndata which seemed to me a bit odd as a function interface. For example, If I want the features needed by the model perhaps a property that gives me that will be more appropriate than the prepare_query_anndata method with return_feature_vars=True which …

**@canergen:** Indeed we are currently looking into supporting loading models without AnnData. It's not as straightforward as the model classes were assumed to always contain a registered AnnData object. It is part of the roadmap for scVI-tools v1.3.
I assume we can deprecate the return_feature_vars option then (I wasn't aware of this feature and used torch.load).

**@Eddie-Kngtlo:** Hi, I have came across a problem with loading a saved model. After training my model, I ran:
`scvi.model.SCVI.save(model, "path_to_model/")`
Then there is a model.pt file in the new directory. Then I tried loading my model:
`model_test = scvi.model.SCVI.load("model_untagged_3.17/", data)`
where data is the same data I used to train the model. (I just wanted to save the model to produce some repeatable results after changing parameters of the model)
This is the error message reported:

---------------------------------------------------------------------------
UnpicklingError                           Traceback (most recent call last)
Cell In[97], line 1
----> 1 model_test = scvi.model.SCVI.load("model_untagged_3.17/", data)

File ~/(current directory)/.venv/lib/python3.9/site-packages/scv …

**@canergen:** This is fixed in the most recent scvi-tools version (torch by default only load weights, we need to load more than the weights from the pt file).

**@LitalBarak96:** i also have the same problem,  am trying to
scvi.model.SCVI.prepare_query_anndata(adata_BA, scvi_ref_path)

as you say in the manuel but get the same error

---------------------------------------------------------------------------
UnpicklingError                           Traceback (most recent call last)
Cell In[15], line 1
----> 1 scvi.model.SCVI.prepare_query_anndata(adata_BA, scvi_ref_path)

File ~/.local/lib/python3.9/site-packages/scvi/model/base/_archesmixin.py:190, in ArchesMixin.prepare_query_anndata(adata, reference_model, return_reference_var_names, inplace)
    159 @staticmethod
    160 def prepare_query_anndata(
    161     adata: AnnData,
   (...)
    164     inplace: bool = True,
    165 ) -> Optional[Union[AnnData, pd.Index]]:
    166     """Prepare data for query integr …

**@ori-kron-wis:** @LitalBarak96 seems you run an old version (as you run python 3.9) . This issue is fixed in a later version of scvi-tools, so I suggest you to just upgrade it in an updated environment.

## #3626: Batch_size setting problem
**Issue:** #3626 | **Last activity:** 2025-12-19T08:12:29Z
**State:** closed | **Author:** @xinliangSun | **Comments:** 0 | **Created:** 2025-11-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3626

[Batch_size]

When calling the ContrastiveDataLoader to split the data, the batch_size is passed via self.data_loader_kwargs. However, when the parent class ConcatDataLoader(DataLoader) is invoked, batch_size is defined again with a fixed value. This causes a problem: the batch size configured for the model cannot be changed by the external parameter.

## #3650: Enabling checkpointing throws an error for totalVI
**Issue:** #3650 | **Last activity:** 2025-12-18T13:24:18Z
**State:** closed | **Author:** @alitinet | **Comments:** 1 | **Created:** 2025-12-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3650

<!-- Describe the bug -->

Hi, when setting `enable_checkpointing=True` in `model.train()` in totalVI, the trainer throws an error. I think it broke with scvi-tools>=1.0 because `training_step` returns `None` now?

<!-- To reproduce -->

```python
scvi.model.TOTALVI.setup_mudata(
    mdata,
    rna_layer="counts",
    protein_layer="counts",
    modalities={
        "rna_layer": "rna",
        "protein_layer": "prot",
    },
)

model = scvi.model.TOTALVI(mdata)

model.train(max_epochs=2, early_stopping=True, enable_checkpointing=True)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[41], line 1
----> 1 model.train(max_epochs=2, early_stopping=True, enable_checkpointing=True)

File ~/miniforge3/envs/multigrate/lib/python3.12/site-packages/scvi/model/_totalvi.py:358, in TOTALVI.train(self, max_epochs, lr, accelerator, devices, train_size, validation_size, shuffle_set_split, batch_size, early_stopping, check_val_every_n_epoch, reduce_lr_on_plateau, n_steps_kl_warmup, n_epochs_kl_warmup, adversarial_classifier, datasplitter_kwargs, plan_kwargs, external_indexing, **kwargs)
    346 training_plan = self._training_plan_cls(self.module, **plan_kwargs)
    347 runner = self._train_runner_cls(
    348     self,
    349     training_plan=training_plan,
   (...)    356     **k …

**@ori-kron-wis:** The fix will be ready for the next release. Thanks.

## #3647: Allow custom label_key for scib-metrics in scvi.autotune
**Issue:** #3647 | **Last activity:** 2025-12-16T17:22:43Z
**State:** open | **Author:** @catheriz | **Comments:** 1 | **Created:** 2025-12-14 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3647

**Is your feature request related to a problem? Please describe.**
When using `scvi.autotune.run_autotune` with scIB metrics for multi-modal integration, I cannot specify which .obs columns should be used as labels for autotune with scib-metrics. The autotune framework only uses the model's internally registered labels fields from the data manager. `setup_mudata` does not support `labels_key`, so label-dependent scib metrics cannot access biologically meaningful labels like tissue or cell type that exist in my data but were not registered during model setup. This makes it impossible to tune hyperparameters using tissue-aware integration quality metrics, even though those labels are available in the dataset.

**Describe the solution you'd like**
I would like `scvi.autotune.run_autotune` and AutotuneExperiment to accept optional `scib_label_key` parameters or allow me to use `label` in the setup process

**@ori-kron-wis:** Hey @catheriz, you are correct with your observation.
However, the best way to deal with this is to implement the label_key into the multi-modal model, running a setup_mudata. We already have the TOTALANVI, and we are working on MULTIANVI (MULTIVI + class label support).

Trying to forcefully fix and have the tuner accept even a different label (say, the above-mentioned solution is done) in a mudata settings is problematic as the tuner gets its inputs from the outputs of a trained model, which are already shuffled and the size of it also depends if a validation was done and so on, so this information has to come from whithin the model, which is either way something we need to do, not only for scib optimization.

Having said that, you can run the tuner without shuffling the data and no val …

## #3624: MrVI's differential_abundance Function Crashes Python Interpreter
**Issue:** #3624 | **Last activity:** 2025-12-09T17:04:23Z
**State:** closed | **Author:** @DarioS | **Comments:** 7 | **Created:** 2025-11-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3624

I use `screen` to keep my session active on the mathematics department's Debian Linux server.

```python
>>> da_res = model.differential_abundance(sample_cov_keys=sample_cov_keys)
100%|██████████████████████████████████████████| 975/975 [18:22:14<00:00, 67.83s/it]
>>> XIO:  fatal IO error 0 (Success) on X server "albona.maths.usyd.edu.au:10.0"
      after 1811 requests (1811 known processed) with 1 events remaining.
(MrViPy) $
```

This causes a fatal problem upon completion, which ends the Python session, losing all progress.

**@ori-kron-wis:** Hey, this function is supposed to work, but I am missing more info to understand what is wrong.
Is that a recent version of scvi-tools? Which mrvi backend is that (torch or jax)?
Is a smaller-sized dataset works for you?
do you think its a memory issue or something else?

**@DarioS:** scVI Tools is 1.4.0.post1. Backend is Torch. Small COVID-19 dataset in tutorial works without error. Plenty of RAM.

```
$ free -h --giga | head -n 2
               total        used        free      shared  buff/cache   available
Mem:            810G        233G        278G        358M        303G        576G
```

**@ori-kron-wis:** So if that is a RAM issue, I can suggest using gc.collect() before and after the differential_abundance use and also reduce your batch_size. If the data is large and not enough memory, we will reduce the computation size in favour of speed.

You can also check the Jax version to see if there are any differences.
Obviously clear everything else that runs on that machine.

**@DarioS:** I would be surprised if a server with 768 GB RAM was unable to handle the data., particularly because it reached 100%.

>  batch_size: Mini-batch size for computing log-probabilities. Default: `128`.

Also, there is no guidance for choosing batch size. A formula to estimate from RAM and samples should be provided.

**@canergen:** Hi, it is unusual to give clear guidance on setting hardware specific things as it depends on VRAM, RAM, number of genes, number of samples.
This is a specific problem with your model and dataset. The function itself runs just fine. If you want help debugging it, please share code and data to reproduce (can be a subset or toy data) and I will see which parameters work on a smaller server. Otherwise, we unfortunately need to consider it not reproducible as on our test data it works.

**@DarioS:** It works fine on a subset of eleven samples and twenty thousand cells.

```python
>>> da_res
<xarray.Dataset> Size: 2MB
Dimensions:          (cell_name: 20000, sample: 11, phase: 3)
Coordinates:
  * cell_name        (cell_name) object 160kB 'AAACCCAAGACTCGAG_S0084' ... 'C...
  * sample           (sample) category 99B CT_2322 CT_1999 ... CT_2423 CT_1469
  * phase            (phase) object 24B 'G1' 'S' 'G2M'
Data variables:
    log_probs        (cell_name, sample) float32 880kB 10.67 4.534 ... 9.038
    phase_log_probs  (cell_name, phase) float64 480kB 2.758 2.025 ... 11.15
```

The full data set will be published in a journal in a few weeks' time, so I can soon share it for testing.

**@canergen:** We will soonish release code that allows defining a subset AnnData for storing the DA results while the full AnnData is used for calculation (the resulting array is n_cellsXn_samples large which can be large).

## #3541: pass custom pytorch dataset with custom __get_item__ method to the SCVI
**Issue:** #3541 | **Last activity:** 2025-12-08T08:19:27Z
**State:** closed | **Author:** @igor-sadalski | **Comments:** 2 | **Created:** 2025-09-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3541

While there are some ways to pass custom data loaders (https://docs.scvi-tools.org/en/1.3.2/user_guide/use_case/custom_dataloaders.html) these approaches seem a bit of an overkill. On the other hand needing to concatenate your data (if you have multiple datasets) gets very cumbersome very quickly.

t would be nice if you can just create a custom pytorch dataset and pass it to the SCVI api. This dataset would have the __get_item___ method that just returns the needed transcriptome and say batch etc.

**@ori-kron-wis:** Hey @igor-sadalski ,
Can you elaborate on your use case? Why can't it be handled with the recent version API (note 1.4v is out)?

We gave several examples of common custom dataloaders implementations use cases (tiledb, lamin, anncollection) but you can also use your wildcard dataloader in the same manner (but you will have to develop it).

**@ori-kron-wis:** Note we are also working on annbatch right now, which will be a solution for case of multiple datasets and files. https://github.com/scverse/scvi-tools/pull/3620
Closing for now.

## #3442: Multi GPU inference support
**Issue:** #3442 | **Last activity:** 2025-12-08T08:17:38Z
**State:** closed | **Author:** @alehuerta1 | **Comments:** 3 | **Created:** 2025-07-25 | **URL:** https://github.com/scverse/scvi-tools/issues/3442

Is there support for multi-GPU inference in SCVI? Say I wanted to add distributed_sampler=True to the arguments in make_data_loader in get_latent_representation(). Is this possible? If not, how would you go about implementing this functionality?

**@ori-kron-wis:** Hey,
There isnt right now, and its a very simple solution to add it so its a good idea.
You will have to add a **data_loader_kwargs parameter to the get_latent_representation, or any other downstream function that will use it in the make_data_loader generic function calling.

See: https://github.com/scverse/scvi-tools/pull/3443

**@canergen:** Is the order still correct of cells? Or do you have to reorder your cells to align with adata.obs_names (this step is not trivial as we don't track indices).

**@ori-kron-wis:** @alehuerta1 can we close?

## #3419: scANVI CPU memory peak during training
**Issue:** #3419 | **Last activity:** 2025-12-08T08:15:24Z
**State:** closed | **Author:** @jan-engelmann | **Comments:** 3 | **Created:** 2025-07-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3419

<!-- Describe the bug -->

scANVI goes out of memory for training on 6.6 million cells.
Anndata is 22GB with 5,000 highly variable genes but watching htop during training I see peaks of CPU memory:
164GB virtual and 145GB RES towards the end of the epoch. I have now fixed the issue by requesting 400GB memory but that should not be necessary.



<!-- To reproduce -->
I am training from a pre-trained scVI model

```python
model = scvi.model.SCVI(
    adata, n_latent=50, dropout_rate=0.2, n_layers=2, gene_likelihood="nb"
)
tparams = {
    "max_epochs": 30,
    "early_stopping": True,
    "early_stopping_patience": 5,
    "simple_progress_bar": True,
    "batch_size": 1024,
    "check_val_every_n_epoch": 1,
    "enable_model_summary": True,
    "enable_checkpointing": True,
}
model.train(**tparams)

scvi.settings.seed = 0

scanvi_model = scvi.model.SCANVI.from_scvi_model(
    model,
    adata=adata,
    labels_key="lineage_2",
    unlabeled_category="nan",
)
scanvi_tparams = {
    "batch_size": 2048,
    "early_stopping": True,
    "early_stopping_patience": 3,
    "check_val_every_n_epoch": 1,
    "early_stopping_monitor": "validation_loss",
    "max_epochs": 20,
}
scanvi_model.train(**scanvi_tparams)
```

`"lineage_2"` contains the following cell type counts:

celltype counts:
T                                        3900338
Monocyte/DC/basophil    1329707
NK/ILC                                770840
B/plasma                            376316
nan …

**@ori-kron-wis:** Hey @jan-engelmann ,
While you can expect a 3-5X times RAM size to run a scvi-tools model on an AnnData object of size X, you can still control it:
If possible, Reduce batch size, Reduce n_latent, n_hidden, HVG number and add gc.collect() between different lines of code to clean unused memory. Of course, that might affect runtime and overall performance.

End of end-of-epoch RAM is due to the validation step.

What is the memory consumption when running just the SCVI part? is it much lower? I suspect it was not cleaned before running the SCANVI and they accumulated. In any case, you can start again from loading the scVI model and run only the SCANVI part.

enable_checkpointing might lead to unnecessary overhead when running with early stopping, especially for such large model.

**@jan-engelmann:** Thanks!

> What is the memory consumption when running just the SCVI part? is it much lower?

yes lower. Runs through with 100GB memory

> In any case, you can start again from loading the scVI model and run only the SCANVI part.

I am already doing that

Ok will try with `enable_checkpointing=False`

It's still surprising isn't it?

**@canergen:** I don't think it's the validation loop. You can check it by setting validation_size to zero and disabling early stopping. I would expect it to happen due to the SemisupervisedDataloader resampling labeled tensors in https://github.com/scverse/scvi-tools/blob/main/src/scvi/dataloaders/_semi_dataloader.py. It looks unreasonably high. However, how much memory do you need when running PCA (plain arpack one) to have some realistic comparison. If you want to drastically reduce memory use, using custom dataloaders within e.g. laminDB might be the best option going ahead.

## #3627: Request: flip `model.save()` argument `save_anndata` default to True
**Issue:** #3627 | **Last activity:** 2025-12-08T07:24:38Z
**State:** closed | **Author:** @aowenson-imm | **Comments:** 2 | **Created:** 2025-11-28 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3627

#### Problem

I think this code should just work:

```
# mod = SCVI model create with AnnData
mod.save(path)
mod = <BaseModelClass or child class>.load(path)
```

But the load will fail:
> ValueError: Save path contains no saved anndata and no adata was passed.

It seems really odd that SCVI default behaviour is to fail loading a file that it just created.

Context: I'm working on a Jupyter Magic tool and it would really help if save -> load would work with defaults, excluding path argument of course.

#### Solution

In `BaseModelClass.save`:
```
    def save(
        ...
        save_anndata: bool = False,
```

Just flip `save_anndata` default to True. If users are deliberately providing the AnnData via load argument `adata`, then they can deliberately set  `save_anndata=False`.

**@ori-kron-wis:** @aowenson-imm I understand what you are saying.

I think that the idea behind this is that there might be cases where anndata can be very large, and perhaps some users will not want to store it each time, to save space. Hence, the save_anndata is False by default, unless specified.

Given that, if you want to load a model with adata=None (its default) and adata is not saved, it will break as you saw, and you will have to provide an adata object or just load the model without adata, potentially set it up later on (otherwise no reason to load it).

However, given this mechanism, I don't see a reason to still break the code with this message, but to succeed in loading the model without anndata (just as would happen if you load with adata=False). So model will be loaded with its saved weights …

**@aowenson-imm:** > but to succeed in loading the model without anndata

I would be happy with this. As I hear your point on anndata size.

## #1935: MultiVI changes
**Issue:** #1935 | **Last activity:** 2025-12-02T16:25:24Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 3 | **Created:** 2023-03-01 | **Labels:** enhancement, multivi | **URL:** https://github.com/scverse/scvi-tools/issues/1935

- [x] LossOutput should record all reconstruction loss and KL terms, including paired KL #1936
- [x] Code should be optimized for when modalities are missing
- [x] Mudata support [#1937 ](https://github.com/scverse/scvi-tools/pull/3038)
- [x] Deprecate setup_anndata
- [x] Minified mode support

**@ori-kron-wis:** Mudata support https://github.com/scverse/scvi-tools/pull/3038

**@ori-kron-wis:** https://github.com/scverse/scvi-tools/pull/3039 - done

**@ori-kron-wis:** https://github.com/scverse/scvi-tools/pull/3622 - also related

## #3625: model load: `Missing key(s) in state_dict`
**Issue:** #3625 | **Last activity:** 2025-11-27T12:08:57Z
**State:** closed | **Author:** @aowenson-imm | **Comments:** 1 | **Created:** 2025-11-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3625

`RegressionModel.load` fails on a save that I have just created.

#### Code

```python
import pandas as pd
import anndata as ad
import scanpy as sc
import cell2location
from cell2location.models import RegressionModel
import scvi

adata = sc.datasets.visium_sge(sample_id="V1_Human_Lymph_Node")
adata.obs['sample'] = list(adata.uns['spatial'].keys())[0]
adata.var['SYMBOL'] = adata.var_names
adata.var.set_index('gene_ids', drop=True, inplace=True)
# find mitochondria-encoded (MT) genes
adata.var['MT_gene'] = [gene.startswith('MT-') for gene in adata.var['SYMBOL']]
# remove MT genes for spatial mapping (keeping their counts in the object)
adata.obsm['MT'] = adata[:, adata.var['MT_gene'].values].X.toarray()
adata = adata[:, ~adata.var['MT_gene'].values]

adata_ref = sc.read(
    f'./data/sc.h5ad',
    backup_url='https://cell2location.cog.sanger.ac.uk/paper/integrated_lymphoid_organ_scrna/RegressionNBV4Torch_57covariates_73260cells_10237genes/sc.h5ad'
)
adata_ref.var['SYMBOL'] = adata_ref.var.index
# rename 'GeneID-2' as necessary for your data
adata_ref.var.set_index('GeneID-2', drop=True, inplace=True)
# delete unnecessary raw slot (to be removed in a future version of the tutorial)
del adata_ref.raw
# filter the object
selected = cell2location.utils.filtering.filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03, nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()

cell2location.models.RegressionModel.setup_anndata(
    adata=adata_ref,
    bat …

**@aowenson-imm:** Whoops, wrong package.

## #1826: Spatial deconv models from rna model should also work with paths
**Issue:** #1826 | **Last activity:** 2025-11-26T15:19:28Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2022-12-21 | **Labels:** spatial, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1826

https://github.com/scverse/scvi-tools/blob/9e13c6e6d2b12de3afe5f9ec5bb4b69e19b4be64/scvi/external/stereoscope/_model.py#L211

https://github.com/scverse/scvi-tools/blob/59145024bd94f3d506c04db13ab347fee9e1d398/scvi/model/_destvi.py#L102

This will allow us to pre-train the scRNA models without also uploading the data used for that training as we will never need to put that model into memory again, which is a current requirement.

## #3599: SemiSupervisedDataSplitter fails with IndexError when external_indexing provides only train/val splits
**Issue:** #3599 | **Last activity:** 2025-11-18T09:52:11Z
**State:** closed | **Author:** @ncaptier | **Comments:** 1 | **Created:** 2025-11-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3599

<!-- Describe the bug -->

When using scvi.model.SCANVI.train(), if external_indexing is passed via datasplitter_kwargs with only two elements (training and validation indices), the training fails with an IndexError.

It appears that SemiSupervisedDataSplitter (used by SCANVI) tries to access external_indexing[2] without first validating and padding the list to a length of three (e.g., by adding an empty array for the test set) thanks to validate_data_split_with_external_indexing, which DataSplitter seems to do.

<!-- To reproduce -->

```python
import scvi
import numpy as np
import anndata

# 1. Create dummy data
adata = anndata.AnnData(np.random.randint(0, 100, size=(100, 50)))
adata.obs["batch_name"] = "batch1"
adata.obs["celltype_name"] = "cellA"
adata.obs["celltype_name"].iloc[10:20] = "Unknown"

# 2. Get train/val splits
train_indexes = np.arange(0, 90)
val_indexes = np.arange(90, 100)

# 3. Setup SCVI and train
scvi.model.SCVI.setup_anndata(adata, batch_key="batch_name", labels_key="celltype_name")
scvi_model = scvi.model.SCVI(adata, n_latent=10, n_layers=2)
scvi_model.train(10, train_size=0.9)

# 4. Setup SCANVI and train with external_indexing
scanvi_model = scvi.model.SCANVI.from_scvi_model(scvi_model, "Unknown")
scanvi_model.train(
    max_epochs=10,
    early_stopping=True,
    datasplitter_kwargs={'external_indexing': [train_indexes, val_indexes]} # This line causes the error
)
```

<!-- Put your Error output in this code block (if applicable, else delete the blo …

**@ori-kron-wis:** Thanks @ncaptier , a fix will be release in next version

## #3470: Unable to define `categorical_covariate_keys` for `scvi.model.LinearSCVI`
**Issue:** #3470 | **Last activity:** 2025-11-11T10:30:43Z
**State:** closed | **Author:** @marcfranquesa | **Comments:** 1 | **Created:** 2025-08-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3470

<!-- Describe the bug -->

I am able to set `categorical_covariate_keys` for SCVI but not for LinearSCVI. Is this the intended behavior?

Thank you!

<!-- To reproduce -->

```python
Model = scvi.model.LinearSCVI

Model.setup_anndata(
    adata,
    layer="counts",
    categorical_covariate_keys=["gene"], # works for SCVI
)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Traceback (most recent call last):
  File ".../src/train.py", line 67, in <module>
    fire.Fire(main)
  File ".../.venv/lib/python3.10/site-packages/fire/core.py", line 135, in Fire
    component_trace = _Fire(component, args, parsed_flag_args, context, name)
  File ".../.venv/lib/python3.10/site-packages/fire/core.py", line 468, in _Fire
    component, remaining_args = _CallAndUpdateTrace(
  File ".../.venv/lib/python3.10/site-packages/fire/core.py", line 684, in _CallAndUpdateTrace
    component = fn(*varargs, **kwargs)
  File ".../src/train.py", line 54, in main
    Model.setup_anndata(
  File ".../.venv/lib/python3.10/site-packages/scvi/model/_linear_scvi.py", line 180, in setup_anndata
    adata_manager.register_fields(adata, **kwargs)
  File ".../.venv/lib/python3.10/site-packages/scvi/data/_manager.py", line 177, in register_fields
    raise TypeError(
TypeError: register_fields() got unexpected keyword arguments {'categorical_covariate_keys': ['gene']} passed without a source_registry.
```

#### Versions:

1.3.3

> VERSION

<!-- Relevant screen …

**@ori-kron-wis:** Yes. It was never implemented.
LinearSCVI is strictly linear: its latent representation is a linear projection of the input gene expression matrix.
The model does not provide hooks to ingest or adjust for covariates the way SCVI does.
You can go ahead and try to implement it
Why not using SCVI in the meantime?

## #3537: autotune over scib-metrics failed with setup_mudata()
**Issue:** #3537 | **Last activity:** 2025-11-11T10:28:12Z
**State:** closed | **Author:** @catheriz | **Comments:** 11 | **Created:** 2025-09-19 | **URL:** https://github.com/scverse/scvi-tools/issues/3537

Hi,

I'm encountering a `TypeError: cannot create weak reference to 'NoneType' object` when using` autotune.run_autotune()` with scib-metrics after updating to the latest scvi-tools. The issue appears to be related to the transition from `setup_anndata()` to `setup_mudata()` for multimodal RNA+ATAC data.

What works:
Manual training: `model.train() `works perfectly with the same `setup_mudata()` configuration (following the tutorial) shown below

```
{
│   'rna_layer': None,
│   'atac_layer': None,
│   'protein_layer': None,
│   'batch_key': 'modality',
│   'size_factor_key': None,
│   'categorical_covariate_keys': ['sample'],
│   'continuous_covariate_keys': None,
│   'idx_layer': None,
│   'modalities': {'rna_layer': 'rna', 'atac_layer': 'atac'}
}
```
Previous versions: autotune worked with `setup_anndata()` in older scvi-tools

Question: Is `autotune.run_autotune()` fully compatible with MULTIVI's `setup_mudata()` for multimodal data?
Any guidance would be appreciated.

Thanks!

**@ori-kron-wis:** Thank you for raising this, seems indeed `autotune.run_autotune()` is not compatible with  `setup_mudata()` at the moment, so we will work on a fix for next release.

**@ori-kron-wis:** The feature was added.

**@catheriz:** Thanks, looking forward to the new release.

**@catheriz:** Hi, I noticed the recent release scvi-tools 1.4.0.post1 — thank you for the update! Could you confirm if the previous issue was fixed? I tried running it again but encountered a `FileNotFoundError: No such file or directory: 'mydata.h5mu'`. I can work around it by moving the file manually to the desired location.

In `autotune/_experiment.py` (lines 357–359), the script saves the MuData object to mymudata.h5mu in a fixed directory. It would be great if this path could be made configurable, or if saving to disk were optional.

Thanks for your help!

**@ori-kron-wis:** Yes, it should be part of the release. There is no other option but to work with files, unfortunately, because of how mudata is structured.
Can you confirm that it works if you manually move it? We have a test that verifies it does, but we might want to add an option to the file path as well.

**@catheriz:** Yes, it works after manually moving the `mydata.h5mu` file. Thanks! It would be great if the output path were configurable, as I plan to run parallel jobs with large files and hardcoded names could cause conflicts.

Also, if I load pre-saved .h5mu files for autotune, it seems the script still writes them again to `mydata.h5mu` ?

Thank you for your help!

**@ori-kron-wis:** I put the mudata filename to be configurable with the parameter `mudata_file_name`, with the default as "mydata.h5mu".
But the actual path is controllable already. Check the `logging_dir` parameter. ray will create the run instances under this path and save the mudata file created for each one there (perhaps with the configurable name you gave)
You can also use the parameter `experiment_name` if you don't want to use a random ID.

So `mudata_file_name` + `logging_dir` parameters are all you need to have full control.

These changes apply in this branch: https://github.com/scverse/scvi-tools/tree/Ori-3537-configurable-mudata-file-autotune
Can you verify it works for you?

**@ori-kron-wis:** Also note that Ray has released a new version, 2.51, which does not seem too stable now, and we do not support it. Use<2.5.1.

**@catheriz:** Thanks for making this change. I have tested it and it works.

**@catheriz:** I tested other metrics and received `KeyError: 'Silhouette batch' `when using `metrics="Silhouette batch"` with autotune.run_autotune() for MULTIVI. However, metrics="Batch correction" works fine and runs all batch correction metrics together. I also tested other metrics such as `"Silhouette label"`, and it works.

Are all the correct metric names listed [here](https://scib.readthedocs.io/en/latest/api/scib.metrics.ilisi_graph.html) (the same link as in the tutorial)?

Thanks!

**@ori-kron-wis:** Yes, we actually changed `Silhouette batch` to `BRAS` on scib-metrics latest version and forgot to do so in scvi-tools, so now it's fixed as well (in this branch).

The list of metrics is the one that is shown on scib-metrics plot, the values of this dict:

```
metric_name_cleaner = {
    "silhouette_label": "Silhouette label",
    "isolated_labels": "Isolated labels",
    "nmi_ari_cluster_labels_leiden_nmi": "Leiden NMI",
    "nmi_ari_cluster_labels_leiden_ari": "Leiden ARI",
    "nmi_ari_cluster_labels_kmeans_nmi": "KMeans NMI",
    "nmi_ari_cluster_labels_kmeans_ari": "KMeans ARI",
    "clisi_knn": "cLISI",
    "ilisi_knn": "iLISI",
    "kbet_per_label": "KBET",
    "bras": "BRAS",
    "graph_connectivity": "Graph connectivity",
    "pcr_comparison": "PCR comparison",
}

+ "Total" (all) …

## #3546: Implement get_normalized to MrVI in pytorch
**Issue:** #3546 | **Last activity:** 2025-11-11T10:16:26Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-09-29 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3546

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

## #3585: TorchMRVI GPU issues
**Issue:** #3585 | **Last activity:** 2025-11-11T10:01:21Z
**State:** closed | **Author:** @FrenkT | **Comments:** 2 | **Created:** 2025-11-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3585

Hi,

I am trying the new `TorchMRVI` implementation (scvi-tools v1.4.0) and I am having a few issues running inference on GPU (training works fine):
1. First of all, I am not sure why but the `to_device` method is not implemented. This means that running `TorchMRVI.load("my_model.pt", adata=adata_hvg, accelerator=device, device=1)` doesn't result in the model being loaded on GPU. I have to force it using `model.module.to(device)`. Is this intentional? Am I missing something?
2. If I force the module to GPU, then `model.get_latent_representation()` runs correctly on GPU. However, I get an error when running `model.differential_expression(sample_cov_keys=["disease"], store_lfc=True, use_vmap=False)`.  It looks like some tensors are not moved to GPU. This is the stack trace:

```
File ~/.pixi/envs/gpu/lib/python3.12/site-packages/scvi/external/mrvi_torch/_model.py:1476, in TorchMRVI.differential_expression(self, adata, sample_cov_keys, sample_subset, batch_size, use_vmap, normalize_design_matrix, add_batch_specific_offsets, mc_samples, store_lfc, store_lfc_metadata_subset, store_baseline, eps_lfc, filter_inadmissible_samples, lambd, delta, **filter_samples_kwargs)
   1472         raise RuntimeError(
   1473             "Out of memory. Try setting use_vmap=False."
   1474         ) from e  # TODO: update error msg
   1475     else:
-> 1476         raise e
   1478 beta.append(np.array(res["beta"].detach().cpu()))
   1479 effect_size.append(np.array(res["effect_size"].detach().cp …

**@ori-kron-wis:** Thanks @FrenkT; there are some decorators to take of this that were missed, please see a fix PR here: https://github.com/scverse/scvi-tools/pull/3586
Could you validate it works from your side as well (install this branch, undo your changes)

**@FrenkT:** Hi @ori-kron-wis , thank you for the quick fix. I just tried it, and it seems to fix the issue.

## #3589: ResolVI.train() has its train_size parameter hardcoded
**Issue:** #3589 | **Last activity:** 2025-11-10T21:37:38Z
**State:** closed | **Author:** @jberkh | **Comments:** 1 | **Created:** 2025-11-10 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3589

**Is your feature request related to a problem? Please describe.**
In the `RESOLVI.train` method, `super().train` is called with a hardcoded `train_size=1.0`. This prevents the use of a validation set and effectively disables trainer parameters that rely on validation loss (e.g., early stopping).

**Describe the solution you'd like**
Unless there’s a specific reason for fixing train_size at 1.0, this parameter should be configurable.

A simple solution would be to either:
- Add `train_size` as an argument to the method and pass that, or
- Use `kwargs.get("train_size", 1.0)` when calling `super().train`.

**@canergen:** Hi, the diffusion proportions per neighboring cell can't be amortized (are learned as a free parameter for each cell). This is required as the list of neighbors of each cell are not ordered. Thus using a validation set doesn't make sense. The prediction for these cells would be inaccurate. We don't recommend early stopping due to this limitation.

## #2908: ModelTuner.fit Returns error: The `RunConfig(local_dir)` argument is deprecated.
**Issue:** #2908 | **Last activity:** 2025-11-08T08:33:56Z
**State:** closed | **Author:** @osmanmerdan | **Comments:** 15 | **Created:** 2024-07-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2908

<!-- Describe the bug -->
I was trying out autotune. I ran ModelTuner.fit, and I encountered the following error.
It may be related to changes in the ray package:
https://docs.ray.io/en/latest/train/user-guides/persistent-storage.html#setting-the-local-staging-directory
<!-- To reproduce -->

```python
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata=adata_scvi, batch_key=batch_key, layer="counts")
scvi_tuner = autotune.ModelTuner(model_cls)
#scvi_tuner.info()

search_space = {
    "n_hidden": tune.choice([92, 128, 192, 256]),
    "n_latent": tune.choice([10, 20, 30, 40, 50, 60]),
    "n_layers": tune.choice([1, 2, 3]),
    "lr": tune.loguniform(1e-4, 1e-2),
    "gene_likelihood": tune.choice(["nb", "zinb"])}

results = scvi_tuner.fit(
    adata_scvi,
    metric="validation_loss",
    search_space=search_space,
    num_samples=5,
    max_epochs=100,
    resources={"cpu": 10, "gpu": 1},
    #logging_dir='/content/logging'
)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[/usr/local/lib/python3.10/dist-packages/scvi/autotune/_tuner.py](https://localhost:8080/#) in fit(self, adata, **kwargs)
    113             A dataclass containing the results of the tuning experiment.
    114         """
--> 115         tuner, config = self._manager._get_tuner(adata, **kwargs)
    116         results = tuner.fit()
    117         return self._manager._get_analysis(results, config)

[/usr …

**@canergen:** This is a deprecation warning and not an error, so the results will all be correct. In our current main branch, this deprecation warning will not be raised and it contains a fully remodelled backend for autotuning.

**@Sporgelum:** Hi @canergen.
I followed the instructions and got the newest scvi-tools from the main branch, but I am not able to solve it...
The goal is the following code:

```
# Check if 'raw_counts' is a valid key
if 'raw_counts' not in adata_horses.layers:
    scvi.model.SCVI.setup_anndata(adata_horses, batch_key="bio_batch")
else:
    scvi.model.SCVI.setup_anndata(adata_horses, layer="raw_counts", batch_key="bio_batch")


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
torch.set_float32_matmul_precision("high")
save_dir = "/data/projects/p918_Horse_Dendritic_Cells_Comparison/Analysis_STARsolo_samples/Load_and_Integrate/adatas/autotune"
scvi.settings.logging_dir = save_dir

# Initialize Ray
ray.init(log_to_driver=False)


search_space = {
    "n_ …

**@Sporgelum:** Hi @canergen ,

Very quick update, for me it was working if I just went to the `scvi/autotune/manager.py` and I changed it to
```
558         run_config = air.config.RunConfig(
559             name=_experiment_name,
560             storage_path=_logging_dir,
561             progress_reporter=_reporter,
562             log_to_file=True,
563             verbose=1,
564         )
```

**@canergen:** Hi, somehow your installation went wrong. `/data/...../lib/python3.9/site-packages/scvi/autotune/_manager.py` doesn't exist anymore in main. Autotune is fully refactored. Unfortunately, `raise DeprecationWarning` is not a preferred way to mark deprecations as it throws an exception (my response above was obviously wrong in that regard). I would suggest to otherwise downgrade ray to 2.23: [release notes](https://github.com/ray-project/ray/releases).

**@osmanmerdan:** > Hi @canergen ,
>
> Very quick update, for me it was working if I just went to the `scvi/autotune/manager.py` and I changed it to
>
> ```
> 558         run_config = air.config.RunConfig(
> 559             name=_experiment_name,
> 560             storage_path=_logging_dir,
> 561             progress_reporter=_reporter,
> 562             log_to_file=True,
> 563             verbose=1,
> 564         )
> ```

I did the same thing to make it work.  I had installed scVI with pip.

**@sunhollyjolly:** > Hi @canergen ,
>
> Very quick update, for me it was working if I just went to the `scvi/autotune/manager.py` and I changed it to
>
> ```
> 558         run_config = air.config.RunConfig(
> 559             name=_experiment_name,
> 560             storage_path=_logging_dir,
> 561             progress_reporter=_reporter,
> 562             log_to_file=True,
> 563             verbose=1,
> 564         )
> ```

Had same issue, and this solved the problem.

**@canergen:** @ori-kron-wis can you do a patch fix as 1.11.6 as discussed.

**@Pinolinoo:** that worked too, is finally running now! thanks so much for your help!

**@ori-kron-wis:** 1.1.6 is released

**@ori-kron-wis:** In addition to the above note for v1.1.6 you will need to use setuptools <=69.5.1

**@dawood2303:** import scanpy as sc
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scvi
from ray import tune
from scvi.autotune import ModelTuner
import ray
from ray import air
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata, categorical_covariate_keys = ['Patient'],
                             continuous_covariate_keys=['pct_counts_mt', 'pct_counts_ribo'])

tuner = ModelTuner(model_cls)
tuner.info()
search_space = {
    "n_hidden": tune.choice([92, 128, 192, 256]),
    "n_latent": tune.choice([10, 20, 30, 40, 50, 60]),
    "n_layers": tune.choice([1, 2, 3]),
    "lr": tune.loguniform(1e-4, 1e-2),
    "gene_likelihood": tune.choice(["nb", "zinb"])}
results = tuner.fit(adata,
                     metric="validation_loss", …

**@canergen:** Please post scVI version together with this. It’s fixed in our recent releases.

**@dawood2303:** Thanks i think Modeltuner is outdated now i am using autotune for the same purpose. i am using 1.2.0 scvi version with Python = 3.12.3 and Ray version  = 2.39.0

**@mys721tx:** `Ray==2.51.1` and `scvi-tools==1.4.0.post1` is causing a similar problem. It might warrant a revisit.

**@ori-kron-wis:** Yes, we saw that, they made some major changes for us, although at a very minor release fix. Right now, use ray<2.5.1
https://github.com/scverse/scvi-tools/issues/3537#issuecomment-3477826605

## #2244: Error `TypeError: '<' not supported between instances of 'str' and 'float'` raised when I run `scvi.model.SCVI.load_query_data`
**Issue:** #2244 | **Last activity:** 2025-11-03T18:37:40Z
**State:** closed | **Author:** @lconan | **Comments:** 5 | **Created:** 2023-08-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2244

<!-- Describe the bug -->

Hi,
I'm tring to map the data to tabula-sapien dataset, so I followed the tutorial[Reference mapping with scvi-tools](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scarches_scvi_tools.html).
Basically,

- The 2 datasets were loaded
- Keep only the interception of the genes in both datasets
- HVG called from reference dataset, and trained the model
- subset the query dataset to the same HVGs

Error raised when I run `scvi.model.SCVI.load_query_data`
I'm not familiar with coding, only see that might be caused by field registration(?)
Thanks.
<!-- To reproduce -->

```python
scvi_query = scvi.model.SCVI.load_query_data(
    query_adata,
    scvi_ref,
)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[30], line 1
----> 1 scvi_query = scvi.model.SCVI.load_query_data(
      2     query_adata,
      3     scvi_ref,
      4 )

File ~/software/scvi-tools/scvi/model/base/_archesmixin.py:107, in ArchesMixin.load_query_data(cls, adata, reference_model, inplace_subset_query_vars, accelerator, device, unfrozen, freeze_dropout, freeze_expression, freeze_decoder_first_layer, freeze_batchnorm_encoder, freeze_batchnorm_decoder, freeze_classifier)
    101 if _SETUP_ARGS_KEY not in registry:
    102     r …

**@martinkim0:** Hi, are you using the datasets in the tutorial or different ones. If so, could you link the data you're using?

**@lconan:** > Hi, are you using the datasets in the tutorial or different ones. If so, could you link the data you're using?

the reference: https://zenodo.org/api/files/fd2c61e6-f4cd-4984-ade0-24d26d9adef6/TS_Bone_Marrow_filtered.h5ad
query data is [here](https://drive.google.com/file/d/1TcVWC0Dx1ZBw7fPRBLFFrU--hBKFfgLT/view?usp=sharing)
the query data is large with 600k cells, merged from 3 datasets, only 5k HVGs are in it now

thanks

**@martinkim0:** Hi, I wasn't able to reproduce the error here. Did you use a batch key for this?

**@martinkim0:** Closing due to inactivity

**@racng:** I encountered this error when trying to load a query dataset. The error disappeared after I converted the data type of the batch  key in the query dataset from a categorical type to str type, though I don't understand why that fixes the problem.

## #3574: MRVI get_normalized_expression implementation
**Issue:** #3574 | **Last activity:** 2025-10-27T11:56:52Z
**State:** closed | **Author:** @skamboj26 | **Comments:** 1 | **Created:** 2025-10-27 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3574

**Is your feature request related to a problem? Please describe.**
I am running into the following when trying to utilize the get_normalized_expression function within MRVI

Traceback (most recent call last):
  File "/quobyte/dfoxgrp/BACKED-UP/datasets/sequencing/cynthia_parse_7_2024/notebooks/scvi_mrvi_processing_ce_fixed.py", line 491, in <module>
    adata_dict[name] = run_analysis(
                       ^^^^^^^^^^^^^
  File "/quobyte/dfoxgrp/BACKED-UP/datasets/sequencing/cynthia_parse_7_2024/notebooks/scvi_mrvi_processing_ce_fixed.py", line 451, in run_analysis
    adata.layers["denoised"] = model.get_normalized_expression(library_size=1e4)
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/quobyte/dfoxgrp/BACKED-UP/snRNAseq/env/uv_scvi/lib/python3.12/site-packages/scvi/model/base/_base_model.py", line 1189, in get_normalized_expression
    raise NotImplementedError(msg)
NotImplementedError: get_normalized_expression is not implemented for JaxMRVI.

**Describe the solution you'd like**
I wanted to inquire if get_normalized_expression is currently implemented within MRVI.
If it is not yet available, would it be possible to add support for it? Possibly something similar to how this method is implemented in other scvi-based models?

**@ori-kron-wis:** This is still under development.
Duplicate of https://github.com/scverse/scvi-tools/issues/3546. Closing

## #1553: Granular device management for Jax
**Issue:** #1553 | **Last activity:** 2025-10-20T12:48:20Z
**State:** closed | **Author:** @justjhong | **Comments:** 2 | **Created:** 2022-06-02 | **Labels:** enhancement, good first issue, jax, P1, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1553

The jax backend currently has a very simple device management option. We would like to improve it such that users can specify specific devices to run on like with our Pytorch models. This should automatically move jax numpy arrays using `jax.device_put` in a similar way the `@auto_move_data` decorator does.

Helpful issue https://github.com/google/jax/issues/1914

Will need a way to move an existing train state across devices: https://github.com/google/flax/discussions/1783

**@martinkim0:** Including multi-device here too

**@ori-kron-wis:** As we made Jax optional dependency, this is not likely to be implemented anytime soon

## #2109: Add support for `SpatialData`
**Issue:** #2109 | **Last activity:** 2025-10-20T12:44:41Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2023-06-23 | **Labels:** enhancement, spatial, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2109

https://spatialdata.scverse.org/en/latest/

#1859

**@ori-kron-wis:** We will consider this in spatial-vi package

## #3539: Problem with model.train() in scVI - Training Stuck at 0%
**Issue:** #3539 | **Last activity:** 2025-10-19T14:05:56Z
**State:** closed | **Author:** @JCSun510 | **Comments:** 10 | **Created:** 2025-09-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3539

Dear,
I encountered the following issue: when running model.train(), the training gets stuck at 0%. At this point, I checked my GPU and found that no process was running. The error message is similar to issue #3094, but unlike that issue, there is no subsequent message indicating that the model was trained.

<img width="847" height="260" alt="Image" src="https://github.com/user-attachments/assets/e04d3dcd-5ea6-4664-bf0f-96938ec87849" />

My training dataset contains 160,000 cells.
GPU information: memory: 16 GB HBM2,Driver version: 550.144.03,CUDA version: 12.4
Please let me know if you need further details about my setup or code.
Thanks

**@deto:** I also had a similar (?) problem.  .train() would just finish instantly.  Also accompanied by the warning:

```
Found 31 module(s) in eval mode at the start of training. This may lead to unexpected behavior during training. If this is intentional, you can ignore this warning.
```

I think there's a bug where the module isn't being set into .train() mode correctly.  For me, downgrading scvi-tools to 1.3.0 fixed it (I did not test other 1.3.x versions).

**@canergen:** Hi, indeed there seems to be an issue for some datasets with negative binomial gene likelihood in scVI-tools 1.4.0, where the model doesn’t train but stops after a few steps. Easiest workaround for now is scVI-tools<1.4.0 or to use another gene_likelihood (in the cases where I experienced it).
I'm looking into it but it poses difficult as it only happens with some datasets and is not caught by our tests.

**@ori-kron-wis:** This issue is not so clear right now, and Im not sure every participant in this discussion face the same reason for it.

@JCSun510, we are having difficulty reproducing this issue and thus fix it. Can you send more information? What version of scvi-tools are you running and also, if you can send me your code and preferably a data snippet that reproduces the problem (will it work if you just use a smaller data?) it will be great.

@deto what exactly are you running and in which version? if 1.3.0 works, does also 1.3.3? (there were quite a few changes from 1.3.0 to 1.4.0, so harder to pinpoint exactly what happened). Again, code snippet and data will help a lot. Would smaller data work?

In previous cases like this, we found that updating to recent packages and CUDA kernels helps, as the env …

**@canergen:** So as an update to above, the issue appeared for me in a hatch session and I can't reproduce it anymore with the same data (and tried like 50 different datasets that worked just fine). I guess it was a version issue and getting the output of pip freeze might also help in reproducing it.

**@danieljgorski:** I also encountered a similar problem when attempting to train a MrVI model with scvi-tools v1.4.0. I tried to create a reproducible example below, working with a fresh environment and following the MrVI quick start tutorial from the docs (stable release):

https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/MrVI_tutorial.html

### Reproducible example

```python
# mrvi-test.py

import scvi
from scvi.external import MRVI
import scanpy as sc
import time


print("="*50)

# Read in haniffa tutorial subset data
adata = sc.read("data/haniffa_tutorial_subset.h5ad")

# Subset inplace to highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=10000, inplace=True, subset=True, flavor="seurat_v3")
print(adata)

# Set up anndata
sample_key = "patient_id"
MRVI.setup_anndata(ad …

**@ori-kron-wis:** Hey @danieljgorski ,
Thank you for all this information; it helped me make some progress.
It is not data-related as you see this issue with a tutorial that I managed to reproduce.
It is not model-related either as we see this for both SCVI and MRVI in torch.

With the exact package versions as yours, I am also getting the warning (pytorch/loops/fit_loop.py:527), but it still trains for me on the GPU (NVidia RTX 6000 Ada 48GB GDDR6, CUDA version 12.4, driver 550.163.01).
The warning is about the validation step, I wouldn't be worried about it.
Im not sure yet why it trains for me and not for you with these exact settings. I would also check if running from CLI breaks for you, as there can also be things related to the Jupyter itself.

However, when I downgrade to **lightning==2.5.2**, I …

**@danieljgorski:** Hi @ori-kron-wis, thanks for the help! Unfortunately none of those suggestions worked for me:

- Downgrading lightning from 2.5.5 to 2.5.2 while still running scvi-tools 1.4.0 had the same behavior
- Installing the current main branch directly (6fc1538) with lightning 2.5.5 or 2.5.2 had the same behavior

**@ori-kron-wis:** @danieljgorski Thank you for your help. Appreciate it.
So it means we still not pinpointed the issue. At least I can't reproduce it yet.

I added a branch that might help us to better understand the error. Can you install from here: https://github.com/scverse/scvi-tools/tree/Ori-3539-jupyter-termination-at-train-start. It will give the most elaborate traceback when it crashes.

Can you double-verify for another type of data and model, say the api_overview tutorial?
Did eventually downgrading to scvi-tools 1.3.3 solve this for you? In this case, you will not have mrvi in torch, though...
Can you share more info on what system and GPU you use?

This might be related: https://github.com/Lightning-AI/pytorch-lightning/pull/21052

**@danieljgorski:** @ori-kron-wis thanks again for your continued help! Oddly enough, I was playing around with jax installs in my main project and noticed that the training started working again.

When I added `jax` to my testing environment, the training proceeded as expected, even though I am specifying a 'torch' backend.


### Reproducible example

```python
# mrvi-test.py

import scvi
from scvi.external import MRVI
import scanpy as sc
import time


print("="*50)

# Read in haniffa tutorial subset data
adata = sc.read("data/haniffa_tutorial_subset.h5ad")

# Subset inplace to highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=10000, inplace=True, subset=True, flavor="seurat_v3")
print(adata)

# Set up anndata
sample_key = "patient_id"
MRVI.setup_anndata(adata, sample_key=sample_key, back …

**@ori-kron-wis:** @danieljgorski ,
Thank you again for helping with this.
This is exactly the issue, and I added a fix to main. We will also release a new version of scvi-tools because of this (1.4.0.post1).

## #3499: pymde package wrapper dcvi-tools outdated
**Issue:** #3499 | **Last activity:** 2025-10-19T14:00:08Z
**State:** closed | **Author:** @osperloff | **Comments:** 1 | **Created:** 2025-09-03 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3499

<!-- Describe the bug -->

In the training for scRNA-seq Atlas-level integration of lung data, the scvi.model.utils import mde is outdated and running the code with data.obsm["X_mde"] = mde(data.obsm["X_scVI"]) script no longer works to visualize the scI learned embedding tool.

<!-- To reproduce -->

```python
# from scvi.model.utils import mde

# adata.obsm["X_mde"] = mde(adata.obsm["X_scVI"])
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
TypeError                                 Traceback (most recent call last)
[/tmp/ipython-input-4087221807.py](https://8cqq6ratxu-496ff2e9c6d22116-0-colab.googleusercontent.com/outputframe.html?vrz=colab_20250829-060119_RC00_800847669#) in <cell line: 0>()
----> 1 adata.obsm["X_mde"] = mde(adata.obsm["X_scVI"])

TypeError: 'module' object is not callable
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION

<!-- Relevant screenshots -->

**@ori-kron-wis:** You are probably seeing an older version of the tutorial; it has been updated since. mde is not been used for several months. It was replaced with umap ever since

## #3557: the bug of reference mapping with totalVI
**Issue:** #3557 | **Last activity:** 2025-10-19T13:24:36Z
**State:** closed | **Author:** @tang2552 | **Comments:** 0 | **Created:** 2025-10-17 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3557

<!-- Describe the bug -->

When I use the totalVI to do reference mapping, I encountered the following problem. Whether I got the wrong version of scvi-tools or not?

<!-- To reproduce -->

```python
def download_model(save_path: str, fname: str = "legacy_seurat_reference_model"):
    """Download the pre-trained model."""
    paths = pooch.retrieve(
        url="https://figshare.com/ndownloader/files/30929902",
        known_hash="422706d6af4ec6b3b91f547d7e8c97812b86a548e0d19b1d85d9cfed686a5130",
        fname=fname,
        path=save_path,
        processor=pooch.Unzip(),
    )
    paths.sort()
    return str(Path(paths[0]).parent)


legacy_model_dir = download_model(save_dir.name)
print(legacy_model_dir)
model_dir = os.path.join(save_dir.name, "seurat_reference_model")
print(model_dir)
TOTALVI.convert_legacy_save(legacy_model_dir, model_dir)

model = TOTALVI.load(model_dir, adata=adata)
```

```
RuntimeError                              Traceback (most recent call last)
Cell In[26], line 7
      4 print(model_dir)
      5 TOTALVI.convert_legacy_save(legacy_model_dir, model_dir)
----> 7 model = TOTALVI.load(model_dir, adata=adata)

File G:\anaconda\conda\envs\scvi_env\lib\site-packages\scvi\model\base\_base_model.py:852, in BaseModelClass.load(cls, dir_path, adata, accelerator, device, prefix, backup_url, datamodule)
    850 else:
    851     model.module.on_load(model, pyro_param_store=pyro_param_store)
--> 852 model.module.load_state_dict(model_state_dict)
    854 model.to …

## #3536: MultiVI, MuData, and Mono-modal Use Case: Issues Encountered
**Issue:** #3536 | **Last activity:** 2025-10-15T08:30:22Z
**State:** closed | **Author:** @s-canchi | **Comments:** 1 | **Created:** 2025-09-18 | **URL:** https://github.com/scverse/scvi-tools/issues/3536

**Problem**

I am running joint analysis on snRNA-seq data from mouse and human samples, focusing on integration and cross-species annotation transfer. I am interested in MultiVI specifically because my data exhibit significant technical bias (e.g., variation in nUMI-depth, batch, species), and the adversarial integration achieved by the model’s GAN component is appealing for assessing tightness of integration, even in mono-modal scenarios.

When using `MULTIVI.setup_mudata`, I encounter errors such as:

```
ValueError: Modalities cannot be None.
```
```
KeyError: 'batch not found in adata.obs.'
(Note: this column does exist as verified by .columns)
```

This suggests the model may require two modalities or there's a problem with reading metadata from the MuData/AnnData objects.

As a workaround, I tried using `setup_anndata` (with an AnnData input; RNA only), which completes setup but fails with a tensor dimension mismatch error during training. The same AnnData object works perfectly with scVI/scANVI.

All datasets, MuData, and AnnData objects are constructed following best practices (batch/species/UMI columns present and non-missing, feature sets harmonized, etc).

**Code (abbreviated for clarity)**
```
import scanpy as sc
import scvi
import numpy as np
import scipy.sparse

# Load harmonized mouse+human AnnData, only shared genes, CSR matrix
adata = sc.read_h5ad("combined_rna_only.h5ad")
# Check input
print(adata.shape)  # (N_cells, N_shared_genes)
for k in ["species", "b …

**@ori-kron-wis:** Hey @s-canchi , As for scvi-tools v.1.4 (most recent), Multivi does not support using anndata, so I suggest using mudata with single modality, like you initially tried, as it should work.

Let's see a naiveexample:

```
mdata = synthetic_iid(return_mudata=True,n_regions=0,n_proteins=0)
mdata["rna"].layers["counts"] = mdata["rna"].X.copy()
mdata.update()
mdata
```

>
> MuData object with n_obs × n_vars = 400 × 100
>   obs:	'batch', 'labels'
>   1 modality
>     rna:	400 x 100
>       layers:	'counts'

```
MULTIVI.setup_mudata(
       mdata,
       batch_key="batch",
       modalities={"rna_layer": "rna"},
  )
model = MULTIVI(mdata, n_latent=n_latent)
model.train(1, check_val_every_n_epoch=1)
```

> Epoch 1/1: 100%|██████████| 1/1 [00:00<00:00, 21.82it/s, v_num=1, train_loss=3.5e+3]


You …

## #3552: cannot import name 'mde' from 'scvi.model.utils'
**Issue:** #3552 | **Last activity:** 2025-10-12T10:31:14Z
**State:** closed | **Author:** @TranThiHang97 | **Comments:** 2 | **Created:** 2025-10-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3552

<!-- Describe the bug -->

I am learning the scANVI following this tutorial: https://docs.scvi-tools.org/en/1.1.0/tutorials/notebooks/scrna/tabula_muris.html
When I tried to run `from scvi.model.utils import mde` I got the error below. I tried to search but I think no one get this error before. I do not know how to solve this problem so please help me. Thank you very much. I also provide the way that I install scVI tools. I use Mac Silicon Chip.



<!-- To reproduce -->

import os
import tempfile

import anndata
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.model.utils import mde

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

> ---------------------------------------------------------------------------
> ImportError                               Traceback (most recent call last)
> Cell In[14], line 12
>      10 import seaborn as sns
>      11 import torch
> ---> 12 from scvi.model.utils import mde
>
> ImportError: cannot import name 'mde' from 'scvi.model.utils' (/opt/homebrew/Caskroom/mambaforge/base/envs/scvi-env-py3.11/lib/python3.11/site-packages/scvi/model/utils/__init__.py)

>How I install scVI

- Install brew via the website: https://brew.sh/ by paste the code into the terminal
- Run:` brew install --cask mambaforge`
- Create a new env using mamba because cannot use the env in conda for scvi: `mamba create -n scvi-env-py3.1 …

**@canergen:** Hi, you are combining a tutorial for scVI-tools 1.1.0 with an installed version of 1.4.0. This is not a good idea and specifically the MDE function was removed as the package is not actively maintained. In addition, rapidssinglecell UMAP performs favorably even on large data.
See the updated tutorial at: https://docs.scvi-tools.org/en/1.4.0/tutorials/notebooks/scrna/tabula_muris.html

**@TranThiHang97:** Thank you very much!!! I understand now.

## #3549: MRVI has no attribute backend
**Issue:** #3549 | **Last activity:** 2025-10-07T00:47:55Z
**State:** closed | **Author:** @rastogiruchir | **Comments:** 2 | **Created:** 2025-09-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3549

On the `main` branch, I receive the error that MRVI has no attribute `backend` when trying to load a trained model. This happens because the current class doesn't have a class variable called `backend`. Could you please add that?


Can reproduce by running

```python
adata = sc.read_h5ad(ADATA_PATH)
model = MRVI.load(MODEL_PATH, adata=adata)
```

I get the following error

```pytb
File /oak/stanford/groups/akundaje/rrastogi/repos/scvi-tools/src/scvi/external/mrvi/_model.py:175, in MRVI.load(cls, dir_path, adata, accelerator, device, prefix, backup_url, datamodule)
    131 @classmethod
    132 @devices_dsp.dedent
    133 def load(
   (...)    141     datamodule: LightningDataModule | None = None,
    142 ):
    143     """Instantiate a model from the saved output.
    144
    145     Parameters
   (...)    173     >>> model.get_....
    174     """
--> [175](https://vscode-remote+ssh-002dremote-002bhanuman.vscode-resource.vscode-cdn.net/oak/stanford/groups/akundaje/rrastogi/repos/scvi-tools/src/scvi/external/mrvi/_model.py:175)     if cls.backend == "torch":
    176         warnings.warn(
    177             "MRVI model is being loaded with PyTorch backend",
    178             UserWarning,
    179             stacklevel=settings.warnings_stacklevel,
    180         )
    182         registry = peek_loaded_model_registry(dir_path, prefix)

AttributeError: type object 'MRVI' has no attribute 'backend'
```

#### Versions:

Cloned from main on 9/29 (fb2c50c6f3c21768914eab88a7b65 …

**@ori-kron-wis:** Can you send the full code, not just the loading part?

Since v1.4 (also in main) we have 2 versions of MRVI with a selected backend: Jax (the default), or Torch.
If you haven't stated backend="torch" when you set up the anndata and initialized the model you are trying to load now, then its still all JAX.
But because of this change, you will need to set up the model again (not necessarily train it).

so what I suspect you need to do is to just before loading , init the model again and setup its anndata:
```
    MRVI.setup_anndata(adata, batch_key=..., backend="jax")
    model = MRVI(adata, backend="jax")
```

Then load it.

But seeing the full code will be clearer to me.

We would recommend start using MRVI with the torch version as the JAX one will not be supported in scvi-tools version …

**@rastogiruchir:** That worked, thanks!

## #3535: UnboundLocalError for sliced_data in AnnTorchDataset.__getitem__
**Issue:** #3535 | **Last activity:** 2025-09-29T11:23:24Z
**State:** closed | **Author:** @SaiRecursion | **Comments:** 0 | **Created:** 2025-09-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3535

When using a custom DataLoader that triggers certain code paths, an UnboundLocalError: cannot access local variable 'sliced_data' where it is not associated with a value occurs inside the AnnTorchDataset.__getitem__ method.

This bug is present within 1.4.0, main branch.

The issue is located in the scvi/data/_anntorchdataset.py file, within the __getitem__ method.

Cause:
The local variable sliced_data is assigned inside a series of if/elif blocks within a for loop. However, one of the conditions handles a specific metadata key (REGISTRY_KEYS.MINIFY_TYPE_KEY) and uses continue to skip to the next iteration.

If this condition is met on an iteration before sliced_data has been assigned, the variable is never created, leading to an UnboundLocalError when it is accessed later in the loop.

Fix:
Pretty simple, initialize sliced_data to None before the for loop so its always in scope.
```
# In scvi/data/_anntorchdataset.py, inside __getitem__

def __getitem__(self, indexes: ...):
    # ...
    data_map = {}
    sliced_data = None  # <-- Add this

    for key, dtype in self.keys_and_dtypes.items():
        # ... rest of the loop
```

## #2953: Incompatibility with new anndata 0.10.9
**Issue:** #2953 | **Last activity:** 2025-09-22T04:35:33Z
**State:** closed | **Author:** @mehrankr | **Comments:** 13 | **Created:** 2024-08-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2953

# Issue

There is a new anndata release incompatible with scVI

# Error message

```
> import scvi
ImportError: cannot import name 'AlignedViewMixin' from 'anndata._core.aligned_mapping' (/local_disk0/.ephemeral_nfs/envs/pythonEnv-41a17f4f-ae47-4ddc-a406-410dcbd282df/lib/python3.10/site-packages/anndata/_core/aligned_mapping.py)
```
# Temporary fix

Pin down anndata:

`pip install anndata==0.10.8`

**@canergen:** Hi, thanks for posting this. Please post the full error as it makes it easier to figure out what's causing this. I opened the issue for MuData as it seems like this is causing the issue: https://github.com/scverse/mudata/issues/77.

**@canergen:** Fixed in MuData.

**@jflusche:** Hello, I hope this message finds you well. I am getting the same error message having to do with scvi and anndata package incompatibilities when importing the newest version of both packages. I tried the temporary fix of downgrading anndata to version 0.10.8 but then got a message saying:

`ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
scvi-tools 1.3.0 requires anndata>=0.11, but you have anndata 0.10.8 which is incompatible.`

Any suggestions here? Thank you for taking the time to read this.

The entire original error message is pasted below for reference.
`---------------------------------------------------------------------------
ImportError …

**@ori-kron-wis:** please start a clean new conda env and install scvi-tools 1.3 , it will install the needed packages and should be ok

**@jflusche:** Hello, thanks for the response! I tried this and after re-installing scvi (version 1.3.0) and anndata (version 0.11.3) I still am getting the same error. Do you have any other suggestions? Thanks.

**@canergen:** Your issue here is MuData and not AnnData or scvi-tools. Can you verify that the issue arises when you just import MuData and then follow their installation guideline?

**@jflusche:** The same issue does arise when I import MuData.

`import mudata as md

from mudata import MuData`

ImportError: cannot import name 'AlignedViewMixin' from 'anndata._core.aligned_mapping' (/home/jupyter/.local/lib/python3.10/site-packages/anndata/_core/aligned_mapping.py)

**@jflusche:** Hi! Just following up on this issue. Do you have any suggestions on where to go from here? I get the same error when I follow MuData installation guideline. Should I reach out to the MuData team for assistance? Thank you for your help thus far.

`ImportError: cannot import name 'AlignedViewMixin' from 'anndata._core.aligned_mapping'`

**@ori-kron-wis:** Like I suggested before, please start a clean new conda env and install scvi-tools 1.3 , it will install the needed packages for both anndata and mudata and should be ok. Use python 3.12.

**@jflusche:** Hi, thank you for your suggestions! I wanted to follow up with what worked for solving this issue. I upgraded MuData to the newest version 0.3.1, which is compatible with scvi version 1.3.0. I also wanted to note that in order to load existing scvi models I had to downgrade pandas to version 1.5.3.

**@joeyQX:** I have the same error, and there is no use of pip install anndata==0.10.8. Moreover, my MuData is the newest version 0.3.2

**@ori-kron-wis:** @joeyQX Im not quite following,  but anndata 0.10.x is at least 1 year old, and we can make certain it will be supported with most recent scvi-tools (e.g 1.4.x).
I suggest starting a clean environment and setting up scvi-tools, which will automatically install all other needed packages correct versions.
Let me know if you have other questions.

**@joeyQX:** > [@joeyQX](https://github.com/joeyQX) Im not quite following, but anndata 0.10.x is at least 1 year old, and we can make certain it will be supported with most recent scvi-tools (e.g 1.4.x). I suggest starting a clean environment and setting up scvi-tools, which will automatically install all other needed packages correct versions. Let me know if you have other questions.

thx!

## #3252: RESOLVI: sample_posterior fails with default return_sites argument
**Issue:** #3252 | **Last activity:** 2025-09-18T12:50:25Z
**State:** closed | **Author:** @luisa-cusick | **Comments:** 6 | **Created:** 2025-03-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3252

<!-- Describe the bug -->

The sample_posterior method fails when the return_sites argument is omitted or set to None (the default).

<!-- To reproduce -->

Load a RESOLVI model:

```resolvae = RESOLVI.load(model_save_path + '/resolvae/', adata=adata)```

Run sample_posterior without setting return_sites:

```
resolvae.sample_posterior(
        model=resolvae.module.model_residuals,
        num_samples=30,
        return_samples=False,
        batch_size=1000)
```


```pytb
  File "./00_resolVI/resolvi_pp.py", line 48, in <module>
    samples = resolvae.sample_posterior(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/projects/b1038/Pulmonary/lcusick/.conda/scvi-env/lib/python3.12/site-packages/scvi/model/base/_pyromixin.py", line 690, in sample_posterior
    results = self._posterior_samples_minibatch(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/projects/b1038/Pulmonary/lcusick/.conda/scvi-env/lib/python3.12/site-packages/scvi/model/base/_pyromixin.py", line 559, in _posterior_samples_minibatch
    np.concatenate(
numpy.exceptions.AxisError: axis -2 is out of bounds for array of dimension 1
```

I first noticed this bug when following the steps in the reproducibility repo: https://github.com/YosefLab/resolvi-reproducibility/blob/main/training_scripts/run_model.py

The exact same error occurred when I ran the command like this:

```
samples = resolvae.sample_posterior(
        model=resolvae.module.model_residuals,
        num_samples=30,
        return_sites= …

**@canergen:** I’ll have a look soon‘ish. I had to hack a solution that understands batch dimensions of pyro sites. Likely this fails here. For now, it should be safe to define return_sites.

**@canergen:** I can't reproduce it locally and assume that we already fixed it. Please reopen if you still face this issue.

**@LouisK92:** Hey @canergen
I'm finally getting to adding resolvi to our benchmark. On a smaller test data set I didn't have problems, but on a full dataset I run into the above described error. However, the proposed trick/fix doesn't work for me.

To reproduce the error:
```python
import anndata as ad
import scvi
import pandas as pd
import scanpy as sc
import numpy as np

adata_sp = ad.read_h5ad("./resolvi_adata.h5ad")

sc.pp.filter_cells(adata_sp, min_genes=5)

spatial_array = np.stack([adata_sp.obs['centroid_x'].values, adata_sp.obs['centroid_y'].values], axis=1)
adata_sp.obsm['X_spatial'] = spatial_array

scvi.external.RESOLVI.setup_anndata(adata_sp, labels_key='cell_type', layer="counts")

supervised_resolvi = scvi.external.RESOLVI(adata_sp, semisupervised=True,
  n_hidden = 32,
  encode_covari …

**@luisa-cusick:** Hi @LouisK92 ,

I'm not sure if there's a permanent solution to this, but I found that excluding `diffusion_mixture_proportion` from the return_sites argument to scvi.external.RESOLVI.sample_posterior solved the problem.

So change the second to last line to:

```
samples = supervised_resolvi.sample_posterior(
    model=supervised_resolvi.module.model_residuals,
    return_sites=[
        'mixture_proportions', 'mean_poisson', 'per_gene_background',
        'per_neighbor_diffusion', 'px_r_inv'
        ],
    num_samples=20, return_samples=False, batch_size=4000)
```

**@LouisK92:** Hi @luisa-cusick,

Awesome! This worked, thank you:)

**@canergen:** Hi, I misused tensor shapes apparently and it's fixed in https://github.com/scverse/scvi-tools/tree/resolvi_fix. However, just not using diffusion_mixture_proportion will give you the same result. The shape needs to be n_cells x 1, while it currently is n_cells.

## #3521: tuning over integration metrics
**Issue:** #3521 | **Last activity:** 2025-09-14T07:47:52Z
**State:** closed | **Author:** @catheriz | **Comments:** 2 | **Created:** 2025-09-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3521

Hi, I followed the tutorial on tuning over integration metrics using `scib-metrics` with` scvi-tools`, as described in https://docs.scvi-tools.org/en/stable/tutorials/notebooks/use_cases/autotune_scvi.html

Does autotune support hyperparameter tuning using integration metrics?

When I tried running the example, I encountered the following error during execution:

> `2025-09-11 22:53:32,413	ERROR tune_controller.py:1331 -- Trial task failed for trial _trainable_0b417c82
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/dist-packages/ray/air/execution/_internal/event_manager.py", line 110, in resolve_future
    result = ray.get(future)
             ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/ray/_private/auto_init_hook.py", line 22, in auto_init_wrapper
    return fn(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/ray/_private/client_mode_hook.py", line 104, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/ray/_private/worker.py", line 2882, in get
    values, debugger_breakpoint = worker.get_objects(object_refs, timeout=timeout)
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/ray/_private/worker.py", line 968, in get_objects
    raise value.as_instanceof_cause()
ray.exceptions.RayTaskError(ArpackError): ray::ImplicitFunc.train() (pid=3 …

**@canergen:** Can you verify that scib-metrics works outside of tune?
Apart from this it might also be that your trained model is degenerate, e.g returning all zeros. Not sure ARPACK would handle it well. @ori-kron-wis if this is the case we should put the block in an exception and assign bad values if it fails computing.

**@ori-kron-wis:** Yes, @catheriz @canergen I will expose the solver parameter selection to the next release, which will solve it. The tutorial will be updated. Stay tuned.

## #3320: make scarches work with proteins, not only genes, in totalvi/anvi
**Issue:** #3320 | **Last activity:** 2025-09-12T15:30:45Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 7 | **Created:** 2025-05-13 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3320

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**@MPebworthEpana:** I'd second this. This seems like a critical feature, alongside just getting scArches to work with higher versions of python so it can be used alongside rapids-single cell and other modern packages.
And TotalVI has been generating issues when I use proteins. It's related to OpenPM and LLVM packages being loaded at the same time. ThreadPooler crashes and the model refuses to initialize.

I just switched to MultiVI.

**@canergen:** @ori-kron-wis any update on this?

**@racng:** I was able to use a MuData object with rna and protein to train TotalVI and then use `scvi.model.TOTALVI.load_query_data()` for scarches and trained the query model.

Here are some relevant packages versions in my environment:

```
# Name                    Version                   Build  Channel
python                    3.11.13         h9e4cc4f_0_cpython    conda-forge
pytorch                   2.4.0           py3.11_cuda12.4_cudnn9.1.0_0    pytorch
scanpy                    1.11.4             pyhd8ed1ab_0    conda-forge
scvi-tools                1.3.2              pyhd8ed1ab_0    conda-forge
muon                      0.1.6              pyhd8ed1ab_0    conda-forge
mudata                    0.3.1              pyhd8ed1ab_1    conda-forge
```

**@ori-kron-wis:** @racng that's great! can to share your code? did you have any additions to contribute?
However, are you sure scarches worked for both modalities as it works for genes only right now? perhaps your query was with the exact same protein list so it didnt affect anything? Please elaborate.

**@canergen:** Hi Ori, scArches also doesn’t work if you add new genes. It just that the prepare function removes those. Adding new proteins is not surgery anymore (small adaptation) but requires actually updating the network (which we don’t allow - not sure we should though). So we need to fix the prepare query function to remove additional proteins?

**@racng:** Yes, I always need to make the set of genes and proteins the same as the original reference model, fill in zeros for missing genes/proteins, and make the protein matrix dense.

**@ori-kron-wis:** Yes, in that case that's exactly what we want to be able to solve automatically using the prepare query function (for each modality in the mudata). In Totalvi you need to measure all your ref markers, redundant markers will be removed. MultiVI is more acceptable of other markers, so it works.

## #2281: Make JAX an optional dependency
**Issue:** #2281 | **Last activity:** 2025-09-11T11:55:22Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 5 | **Created:** 2023-10-10 | **Labels:** enhancement, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2281

**@racng:** I would find this very helpful.
I keep getting this error when trying to import scvi-tools
```
ImportError: cannot import name 'ShapedArray' from 'jax' (/users/rng/mambaforge/envs/scai-v4/lib/python3.10/site-packages/jax/__init__.py)
```
I try making jax=0.4.13 but its keeps getting replaced with v0.4.20 because it is required by dependencies in pertpy and also scvi-tools is a requirement for pertpy.
I can't figure out an environment where scvi-tools, scarches, and pertpy can co-exist.
Would appreciate it if anyone can share working combination of package versions, especially for these packages:
```
python
pytorch
torchvision
torchaudio
pytorch-cuda
jax
jaxlib
chex
flax
scvi-tools
scarches
pertpy
```
Thanks!

**@martinkim0:** Hi, sorry that you're running into this issue - we're working on making this available in #2318 as part of our next scvi-tools release (v1.1). However, I'm unable to reproduce the `ImportError` you're getting with JAX 0.4.20. Could you post the full traceback you're seeing? Thanks.

**@Jingyao12:** I am running the same issue. My Jax version is 0.4.23
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
Cell In[8], line 1
----> 1 import scvi

File ~/mambaforge/mambaforge/envs/scvi/lib/python3.9/site-packages/scvi/__init__.py:10
      7 from ._settings import settings
      9 # this import needs to come after prior imports to prevent circular import
---> 10 from . import data, model, external, utils
     12 # https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
     13 # https://github.com/python-poetry/poetry/issues/144#issuecomment-623927302
     14 try:

File ~/mambaforge/mambaforge/envs/scvi/lib/python3.9/site-packages/scvi/model/__init__.py:2 …

**@Jingyao12:** It was fixed by install flax see #2216

**@ori-kron-wis:** flax, jax and jaxlib recent versions are mandatory installations with scvi-tools (better to install <0.4.35) but we still want to make it optional after mrVI torch implementation

## #3020: Support metric and loss loging on step
**Issue:** #3020 | **Last activity:** 2025-09-11T10:37:24Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 3 | **Created:** 2024-10-19 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3020

In large datasets, the training may take only 1-2 epochs, meaning that the loss profile should be inspected on the step. Thus, it would be great to add an option to log losses and metrics on steps instead of epochs. I would suggest this for both training and validation losses, as in some pathological cases where there was sth wrong with the data setup, the training and validation losses actually did not match.

**@canergen:** Can you create a PR for this (can be in just the regular Training code)? Do you have some benchmarking for training time to add validation loss at each step?

**@Hrovatin:** I dont have benchmarks for the validation set - maybe getting just one batch of validation set would be good to speed it up as a proxy?

**@ori-kron-wis:** Added

## #3483: Issue with model history after multiGPU training
**Issue:** #3483 | **Last activity:** 2025-09-11T10:36:36Z
**State:** closed | **Author:** @plezar | **Comments:** 0 | **Created:** 2025-08-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3483

<!-- Describe the bug -->

When using multiGPU training, `model.history` returns an empty dictionary:

<!-- To reproduce -->

```python
scvi.model.SCVI.setup_anndata(
    ad,
    layer="counts",
    categorical_covariate_keys=["Cohort", "library_preparation_protocol__ontology_label"],
    continuous_covariate_keys=["Mitochondial_Percentage"],
)

model_scvi = scvi.model.SCVI(ad)

scvi.settings.dl_num_workers = 2
scvi.settings.dl_persistent_workers = True
datasplitter_kwargs = {}
datasplitter_kwargs["drop_dataset_tail"] = True
datasplitter_kwargs["drop_last"] = False

model_scvi.train(accelerator="gpu",
                 check_val_every_n_epoch=1,
                 early_stopping=True,
                 devices=-1,
                 datasplitter_kwargs=datasplitter_kwargs,
                 strategy="ddp_notebook_find_unused_parameters_true",
                 max_epochs=10)

model_scvi.history
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
{}
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION 1.3.3

<!-- Relevant screenshots -->

## #2349: Implement conditional batch/layer normalization
**Issue:** #2349 | **Last activity:** 2025-09-11T09:10:12Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2023-12-06 | **Labels:** enhancement, good first issue, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2349

**@canergen:** You can copy this one from the muANVI repo and I would add a second batch key in the AnnData setup, only used for conditional norm in the encoder. We should also copy the MoG prior from there.

## #3453: Docker images with trailing dash
**Issue:** #3453 | **Last activity:** 2025-09-10T09:54:08Z
**State:** closed | **Author:** @nictru | **Comments:** 3 | **Created:** 2025-08-03 | **URL:** https://github.com/scverse/scvi-tools/issues/3453

Hey, I was trying to use a runtime docker image of a specific release. Given your overall naming schema, I would have expected this to be called `py3.12-cu12-1.3.3-runtime`. However, such an image does not exist. I think, the correct one would be [`py3.12-cu12-1.3.3-`](https://github.com/scverse/scvi-tools/pkgs/container/scvi-tools/468547615?tag=py3.12-cu12-1.3.3-).

Is this supposed to be with a trailing dash, or is the `runtime` missing?

**@ori-kron-wis:** Hey,
It is probably a bug and `runtime` is missing, The reason is the empty quotation mark string in this line:

<img width="1542" height="1052" alt="Image" src="https://github.com/user-attachments/assets/c8298082-e8cd-4e58-9521-54b2f7bc5436" />

Im not entirely sure I want to change that, as other systems might be affected. Lets keep it with the trailing dash for now but will keep this open.

You can see all images here: https://github.com/scverse/scvi-tools/pkgs/container/scvi-tools/versions

**@nictru:** Maybe future releases could also appear with the proper `runtime` tag (in addition to the trailing dash one), so that newly joing users can use it accordingly?
With the trailing dash images it is not very clear what they contain

**@ori-kron-wis:** added

## #3500: Easy addition of parameters for checkpointing to trainer.fit
**Issue:** #3500 | **Last activity:** 2025-09-10T06:40:28Z
**State:** closed | **Author:** @alehuerta1 | **Comments:** 5 | **Created:** 2025-09-05 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3500

Currently, there is no straightforward way to pass a custom Lightning checkpoint containing optimizer and learning rate scheduler states to trainer.fit.

I propose updating the training runner’s  __call__ method to accept a ckpt_path argument, which can then be passed to trainer.fit for resuming training from a specific checkpoint:


    def __call__(self, ckpt_path = None):
        """Run training."""
        if hasattr(self.data_splitter, "n_train"):
            self.training_plan.n_obs_training = self.data_splitter.n_train
        if hasattr(self.data_splitter, "n_val"):
            self.training_plan.n_obs_validation = self.data_splitter.n_val
        try:
            if ckpt_path is not None:
                self.trainer.fit(self.training_plan, self.data_splitter, ckpt_path=ckpt_path)
            else:
                self.trainer.fit(self.training_plan, self.data_splitter)

**@marianogabitto:** Ori, Can,
        can we add this to the codebase? This will really help us and it is exposing a minimal number of parameters.

Best,
Mariano

**@ori-kron-wis:** @marianogabitto , @alehuerta1
Technically, in scvi-tools you can use a callback that is called SaveCheckpoint, which is a pytorch' ModelCheckpoint wrapper to resume your work from a specific checkpoint (it can also check for runtime model crash)
e.g:
```
from scvi.model import SCVI
from scvi.train import SaveCheckpoint

adata = scvi.data.synthetic_iid()
scvi.model.SCVI.setup_anndata(
        adata,
        labels_key="labels",
        batch_key="batch",
)

model = SCVI(adata)
cb = SaveCheckpoint(
    dirpath="scvi_ckpts/",
    monitor="validation_loss",  # pick a metric your model logs
    load_best_on_end=True,      # optional: load best state into model at end
)
model.train(max_epochs=200, callbacks=[cb],enable_checkpointing=True,)

best_path = cb.best_model_path  # path for the best sa …

**@marianogabitto:** Ori,
       I don't think that the way you are using checkpoint in scvi, neither save nor load the parameters and the state of the optimizer. We developed a way, convoluted so it does not merit a post, to save the optimizer state and load it if we have this option.

     We will add a unit test !

Thanks,
M

**@ori-kron-wis:** Indeed, we do not save or load the optimizer state in this mechanism.
Please contribute to this PR.

**@ori-kron-wis:** @alehuerta1 Once we will merge the PR this issue will automatically close.
I left you a small remark there.

## #3472: POISSONVI: `model.differential_accessibility` function has encountered an error
**Issue:** #3472 | **Last activity:** 2025-08-19T11:35:48Z
**State:** closed | **Author:** @YuZhengM | **Comments:** 4 | **Created:** 2025-08-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3472

<!-- Describe the bug -->

When performing differential peak analysis of clusters after training scATAC-seq data with PoissonVI, I encountered the following error.

<!-- To reproduce -->

```python
da_peaks = model.differential_accessibility(adata, groupby="clusters", delta=dp_delta, group1=cluster, mode="vanilla", two_sided=False)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
2025-08-19 15:52:46 notebook-1957674591385907201-ac1dyrvmyl-33676 SCIV_preprocessing_scvi[20293] INFO Start difference peak: 0/(0, 1, 2, 3, 4, 5)
DE...:   0%|                                                                                                                                                                               | 0/1 [00:14<?, ?it/s]
Traceback (most recent call last):
  File "/root/private_data/keti/project_code/sciv_reproducibility/GSE184462/__init__.py", line 57, in <module>
    trs = sciv.ml.core(
  File "/opt/conda/envs/yzm_py310/lib/python3.10/site-packages/sciv/model/_core_.py", line 463, in core
    ) = _check_and_run_two_step_(
  File "/opt/conda/envs/yzm_py310/lib/python3.10/site-packages/sciv/model/_core_.py", line 301, in _check_and_run_two_step_
    da_peaks = poisson_vi(adata, max_epochs=max_epochs, batch_key=batch_key, resolution=resolution, model_dir=model_dir)
  File "/opt/conda/envs/yzm_py310/lib/python3.10/site-packages/sciv/preprocessing/_scvi_.py", line 172, in poisson_vi
    da_peaks = model.differential_a …

**@YuZhengM:** I didn’t have this issue in version 1.2.0, but it appeared when I upgraded to version 1.3.3 while using multi-GPU for data processing. I checked the code and it seems that the **two_sided** parameter defines an **m1_domain_fn function** (which returns one parameter) that gets passed in, causing the newly created **m1_domain_fn function** (which returns two parameters) to become invalid. As a result, receiving one parameter with two parameter receivers led to this error. If you have time, could you please fix this? I need to use it, thank you very much.

**@YuZhengM:** I have changed the code in the file `scvi/external/poissonvi/_model.py` to the following content. I’m not sure if it’s correct or if this modification is appropriate?

> The original content:

```python
        if two_sided:

            def m1_domain_fn(samples):
                return np.abs(samples) >= delta

        else:

            def m1_domain_fn(samples):
                return samples >= delta
```

> After the modification:

```python
        if two_sided:

            def m1_domain_fn(samples):
                return np.abs(samples) >= delta, np.abs(samples) < delta

        else:

            def m1_domain_fn(samples):
                return samples >= delta, samples < delta
```


> After the modification, it ran smoothly without any errors.

```pytb
INFO     File /public/home …

**@ori-kron-wis:** Thank you @YuZhengM !. We went through some changes in that part of the code base and missed it.
I have a fixed ready and it be released soon (you can install from that branch for now).

**@YuZhengM:** You are welcome.

## #3465: Pyro error when LogNormal downsampling in resolVI training
**Issue:** #3465 | **Last activity:** 2025-08-18T07:52:52Z
**State:** closed | **Author:** @Part-coder-part-batman | **Comments:** 0 | **Created:** 2025-08-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3465

<!-- Describe the bug -->
Hello, I am running resolVI on scvi 1.3.3, python=3.13


<!-- To reproduce -->

I am running the tutorial
Any ideas on how to fix this? :)


<!-- Put your Error output in this code block (if applicable, else delete the block): -->

File ~/miniforge3/envs/scvi_py312/lib/python3.12/site-packages/scvi/external/resolvi/_module.py:854, in RESOLVAEGuide.forward(self, x, ind_x, library, y, batch_index, cat_covs, x_n, distances_n, n_obs, kl_weight)
    845 per_neighbor_diffusion = pyro.param(
    846     "per_neighbor_diffusion_map",
    847     self.per_neighbor_diffusion_init,
    848     constraint=constraints.interval(-10.0, 10.0),
    849     event_dim=1,
    850 )
    852 if self.downsample_counts_mean is not None:
    853     downsample_counts = (
--> 854         int(LogNormal(self.downsample_counts_mean, self.downsample_counts_std).sample())
    855         + 10
    856     )
    858 with pyro.plate("obs_plate", size=n_obs or self.n_obs, subsample=ind_x, dim=-1):
    859     # Dispersion of NB for counts.
    860     px_r_mle = pyro.param(
    861         "px_r_mle",
    862         self.px_r,
    863         constraint=constraints.greater_than(self.eps),
    864         event_dim=len(self.px_r.shape),
    865     )

File ~/miniforge3/envs/scvi_py312/lib/python3.12/site-packages/pyro/distributions/distribution.py:26, in DistributionMeta.__call__(cls, *args, **kwargs)
     24     if result is not None:
     25         return result
---> 26 return su …

## #3460: `SCVI.load` fails with VAE size mismatch when using extra covariates with custom datamodule
**Issue:** #3460 | **Last activity:** 2025-08-11T11:18:33Z
**State:** closed | **Author:** @aagrande | **Comments:** 1 | **Created:** 2025-08-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3460

<!-- Describe the bug -->

When training an SCVI model via a `TileDBDataModule` that includes an additional categorical or continuous covariate, saving and then reloading raises a size‐mismatch error in the decoder. If only the batch key is provided (no extra covariates), `SCVI.load` succeeds. It appears that the extra covariate dimensions recorded in the data module registry aren’t being applied when the VAE is reinitialized during load.

<!-- To reproduce -->

```python
import numpy as np
import pandas as pd
import scvi
import tiledbsoma
import tiledbsoma.io

from anndata import AnnData
from scvi.dataloaders import TileDBDataModule

n_cells, n_genes = 100, 50
counts = np.random.poisson(lam=1.0, size=(n_cells, n_genes))
obs = pd.DataFrame(
    {
        "batch": np.random.choice(["A", "B"], size=n_cells),
        "cat_cov": np.random.choice(["A", "B"], size=n_cells),
        "cont_cov": np.random.normal(size=n_cells),
    }
)
adata = AnnData(X=counts, obs=obs)
adata.layers["counts"] = counts.copy()

EXPERIMENT_URI = "soma"
tiledbsoma.io.from_anndata(EXPERIMENT_URI, adata, measurement_name="RNA")
exp = tiledbsoma.Experiment.open(EXPERIMENT_URI)
query = exp.axis_query(measurement_name="RNA")

datamodule = TileDBDataModule(
    query,
    layer_name="counts",
    batch_size=32,
    shuffle=True,
    batch_column_names=["batch"],
    categorical_covariate_keys=["cat_cov"],
    continuous_covariate_keys=["cont_cov"],
    dataloader_kwargs={"num_workers": 0, "persistent_workers": …

**@ori-kron-wis:** Thank you, the fix will be merged in main branch, and will be available for next release.

## #3459: How to use ResolVI and scVIVA for cell annotation on Xenium data
**Issue:** #3459 | **Last activity:** 2025-08-06T06:00:10Z
**State:** closed | **Author:** @qiuzcsysucc | **Comments:** 2 | **Created:** 2025-08-06 | **URL:** https://github.com/scverse/scvi-tools/issues/3459

Dear SCVI development team,

First of all, thank you for all the powerful tools you’ve contributed to the community. I’m working with multiple tumor Xenium samples—over 5 million cells profiled on a 5 000-gene panel, with default multimodal marker–based cell segmentation—and would greatly appreciate your advice on using ResolVI and scVIVA for cell annotation.

Current workflow and challenges
Integration & clustering with SCVI + Leiden
I applied SCVI to integrate all samples, then performed Leiden clustering. In the first round of clustering I could recover major cell types (epithelial, T, B, myeloid, endothelial, fibroblast), but in the second round (subtyping) I encountered extensive noise/contamination: clusters co-express markers of tumor cells together with T, B, myeloid, endothelial, and fibroblast markers, making accurate sub-annotation impossible.

No reference scRNA-seq or label transfer
I do not have a matching scRNA-seq reference and do not plan to use label transfer, since Xenium often detects cell types that are not captured by scRNA-seq in equivalent samples. I expect label transfer would not improve annotation.

Questions
Unsupervised annotation with ResolVI

Option A: Use the latent embedding X_resolVI directly for dimensionality reduction, clustering, and annotation.

Option B: Use ResolVI’s generated_expression matrix as input to SCVI (another SCVI‐based workflow), then reduce dimensionality, cluster, and annotate.

Are these two workflows reasonable and corr …

**@canergen:** Hi, please post usage question in discourse and use GitHub for issues.
M that being said, I would recommend using resolVI then and do scVIVA on resolVI coordinates. I would potentially provide the labels to resolVI as supervised mode. In the cancer case study, we also provided very coarse labels and I think it will be fine. Please don’t use corrected counts in another SCVI model. This can have negative effects and likely doesn’t help much.

**@qiuzcsysucc:** > Hi, please post usage question in discourse and use GitHub for issues. M that being said, I would recommend using resolVI then and do scVIVA on resolVI coordinates. I would potentially provide the labels to resolVI as supervised mode. In the cancer case study, we also provided very coarse labels and I think it will be fine. Please don’t use corrected counts in another SCVI model. This can have negative effects and likely doesn’t help much.

Thank you for the clarification and recommendations!

I’ll move any future usage questions over to Discourse. Just to clarify—when you recommend providing coarse lineage labels to ResolVI, do you mean I should first use PCA (or another DR/clustering method) to assign major cell-lineage labels and then run ResolVI? Or is it preferable to let ResolVI id …

## #3383: Interpretability of SCANVI model predictions
**Issue:** #3383 | **Last activity:** 2025-08-06T05:41:41Z
**State:** closed | **Author:** @Tijs-dot | **Comments:** 2 | **Created:** 2025-06-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3383

<!-- Describe the bug -->

Hi, I am trying out the tutorial on adding interpretability to the predictions made by a SCANVI model I trained. I am very new to these types of analyses, so feel free to ask for any additional information. I have trained a scanvi model. Next, I load that model and try to make predictions for a query anndata object. This works fine when I do it just like that. However, when trying to also add interpretability (following [Using SHAP values and IntegratedGradients for cell type classification interpretabilty](https://docs.scvi-tools.org/en/1.3.0/tutorials/notebooks/use_cases/interpretability.html)) I run into issues with both approaches.

<!-- To reproduce -->

```
# Label transfer
vae_q = scvi.model.SCANVI.load_query_data(
    query_adata,
    model_dir_path,
)

vae_q.train(
    max_epochs=100,
    plan_kwargs=dict(weight_decay=0.0),
    check_val_every_n_epoch=10,
)

query_adata.obsm["X_scANVI"] = vae_q.get_latent_representation()

predictions, attributions = vae_q.predict(ig_interpretability=True, soft=True)
```


<!-- Error: -->

```pytb
ValueError: cat not provided while n_cat != 0 in init. params.
```

When I try instead using:

```
shap_values = vae_q.shap_predict()
```

Memory usage rises very quickly and I have to cancel to avoid OOM after less than 10 iterations.

My anndata is quite large, 10000 genes and 55k cells.

Any suggestions or insights are very much appreciated!

Best wishes,
Tijs

#### Versions:

<!-- Output of scvi.__version__ - …

**@ori-kron-wis:** Hey,

1. For IntegratedGraidents, we had a bug in 1.3.0 with this.
Given your query and ref has the same labels, it should work, but please update to a recent scvi-tools version (1.3.1 +)

You can also try to run without the query fine-tuning:
`predictions, attributions = model.predict(query_adata, ig_interpretability=True)
`
With your original model, to see there's no structure difference

If still not working, we need to understand what your ref and data look like.

2. Yes, SHAP has a huge memory consumption for large datasets. We are working on a new, approximated, thin & fast version to run SHAP. In the meantime, use the 1st option.

**@canergen:** Closed due to inactivity

## #3416: [RESOLVI] ValueError in train() with semisupervised=True due to invalid broadcast in LogNormal (scvi-tools 1.3.x, scanpy 1.11.x)
**Issue:** #3416 | **Last activity:** 2025-08-06T05:40:28Z
**State:** closed | **Author:** @MasumiO | **Comments:** 2 | **Created:** 2025-07-10 | **URL:** https://github.com/scverse/scvi-tools/issues/3416

**Summary**
I tried running the official RESOLVI tutorial below to perform semi-supervised training:
https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/resolVI_tutorial.html
However, I encountered a ValueError during train() that blocks execution.

**Environment**
- scvi-tools versions tried:
 　- 1.3.0
 　- 1.3.1.post1
- scanpy: 1.11.3
- Python: 3.10
- Running on AWS EC2 Ubuntu (no GPU available, CPU-only)

**What I did**
Following the tutorial:
```
scvi.external.RESOLVI.setup_anndata(ref_adata, labels_key="predicted_celltype", layer="counts")

supervised_resolvi = scvi.external.RESOLVI(ref_adata, semisupervised=True)
supervised_resolvi.train(max_epochs=50)
```
**What happened**
The following error occurs during `train()`:

```
ValueError: Input arguments must all be instances of Number, torch.Tensor or objects implementing __torch_function__.

...
File ~/miniforge3/envs/scvi-1.3.1/lib/python3.10/site-packages/scvi/external/resolvi/_module.py:856, in RESOLVAEGuide.forward(...)
    downsample_counts = (
-->         int(LogNormal(self.downsample_counts_mean, self.downsample_counts_std).sample())
            + 10
    )
...
File ~/miniforge3/envs/scvi-1.3.1/lib/python3.10/site-packages/torch/distributions/utils.py:43, in broadcast_all(*values)
     raise ValueError(
         "Input arguments must all be instances of Number, torch.Tensor or objects implementing __torch_function__."
     )
```
**Possibly related warning**

Prior to the error, I get this warning during …

**@canergen:** Hi, thanks for trying out resolVI. Can you check that you filter spots/cells without any expression out before initializing resolVI. The model looks at mean and variance of total counts during setup and performs downsampling. For sequencing based platforms, I would suggest disabling it and using downsample_counts=False.

**@ori-kron-wis:** I can confirm the tutorial trains on colab .
I was using:
scvi-tools: 1.3.2
scanpy: 1.11.3
decoupler: 1.9.2
Python: 3.11
I suggest using GPU

You can try to do the same:

<img width="1327" height="841" alt="Image" src="https://github.com/user-attachments/assets/b9732d7c-b098-4076-b006-0fd20d9a2dfb" />

## #2580: Enable checkpointing with autotune
**Issue:** #2580 | **Last activity:** 2025-08-04T11:35:03Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-29 | **Labels:** good first issue, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2580

## #1744: Manager summary stats should be per field
**Issue:** #1744 | **Last activity:** 2025-08-04T11:35:03Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 3 | **Created:** 2022-10-16 | **Labels:** AnnDataManager, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1744

Because of this line summary stats can be overwritten if two fields use the same name. Summary stats should be a dict with keys being the unique registry keys of the field and values being the summary stats

https://github.com/scverse/scvi-tools/blob/00e03420c5b7b59bd9ae57238bbfe431d9ab8865/scvi/data/_manager.py#L315

**@adamgayoso:** what do you think @justjhong?

**@justjhong:** It's a logical change, but also results in verbose access to the field-specific summary stats. If we could create an API to easily fetch summary stats (e.g. get_summary_stat(field name, stat key)) then it could work well enough. Mainly was being conservative about the structure of summary stats as a single high-level object when I implemented this.

**@martinkim0:** I think we should be raising an error here instead if someone has two fields with the same name.

## #1906: library_size argument not used fully in TOTALVI get_normalized_expression
**Issue:** #1906 | **Last activity:** 2025-08-04T11:35:02Z
**State:** closed | **Author:** @deto | **Comments:** 1 | **Created:** 2023-02-15 | **Labels:** totalvi, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1906

Doesn't multiply the scale values as it does with SCVI model

https://github.com/scverse/scvi-tools/blob/bf2121975bdfc31bfb1f6feb6446c331188b47dd/scvi/model/_totalvi.py#L481

**@yuanx749:** +1, seems missing `* library_size`
https://github.com/scverse/scvi-tools/blob/b3648e082800fedcdaf01bea1464c0485d5a9c82/src/scvi/model/_totalvi.py#L524

## #1784: Loss formulation in SCANVI
**Issue:** #1784 | **Last activity:** 2025-08-03T12:02:38Z
**State:** closed | **Author:** @haoyang-insitro | **Comments:** 5 | **Created:** 2022-11-10 | **Labels:** bug, scanvi, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1784

<!-- Describe the bug -->

It looks like in SCANVI, [when labels are provided](https://github.com/scverse/scvi-tools/blob/main/scvi/module/_scanvae.py#L294), the KL divergence related loss (for z2 and l specfically) are not added to the total loss. Could you confirm and help clarify? Thanks!

#### Versions:

<!-- Output of scvi.__version__ -->

0.19.0

<!-- Relevant screenshots -->

**@haoyang-insitro:** I also checked [the original SCANVI implemtation](https://github.com/chenlingantelope/HarmonizationSCANVI/blob/master/scvi/models/scanvi.py#L183). The KL loss is included as output for both labeled and unlabeled data.

**@adamgayoso:** We've been aware of this for quite some time:

https://github.com/scverse/scvi-tools/issues/841

However at this point it would be a breaking change to "fix" that issue. We can certainly make it an option, what do you think?

**@haoyang-insitro:** Thanks for the reply. The code link in #841 no longer works, so it is hard for me to gauge if it is the same issue just from the description which seems to highlight a different problem. The issue I pointed out is more about the missing KL divergence term that regularizes the latent space. If you think they are the same issue, could you further clarify? Thanks!

> only computes the ELBO without relying on the cell states' knowledge for labeled examples

**@PierreBoyeau:** Thanks so much for raising this point. @NathanAzoL worked on reimplementing scANVI that computes the mentioned kl term [here](https://github.com/NathanAzoL/scvi-tools/pull/1). He observed promising results hinting that this correction could be beneficial for annotation. That being said, we need to better assess the performance of the implementation. We need to clean this code and document the performance differences.
@NathanAzol could you take care of this?

**@LevyNat:** Thanks @PierreBoyeau. Indeed the missing kl term has been recently added on this new version. Our next step is to carry out a comprehensive benchmark.

## #1903: `use_observed_lib_size=False` fails with NaN for some datasets
**Issue:** #1903 | **Last activity:** 2025-08-03T12:02:25Z
**State:** closed | **Author:** @vitkl | **Comments:** 6 | **Created:** 2023-02-11 | **Labels:** bug, nan, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/1903

Hi,

I see that `use_observed_lib_size=False` fails with NaN for some datasets. I would like to use `use_observed_lib_size=False` to estimate the technical normalisation effect per cell - which does not necessarily match the total count per cell, especially in more complex data from multiple tissues and cell types. For one dataset, a few attempts to restart the notebook and run all cells help. For the same dataset, it also helps to reduce n_hidden 1024 -> 512. For a different dataset, even n_hidden=128 and n_latent=30 don't work. It would be hard to provide a reproducible example because I observed this issue using unpublished snRNA-seq data.

My guess would be that `use_observed_lib_size=False` is not particularly numerically stable. I observed a similar issue with other models when priors are selected in suboptimal ways. Which prior is used for this technical normalisation effect?

I generally use a batch-specific prior that regularises the model to keep the cell-specific normalisation `y_c` close to 1 (e.g. in cell2location package):
```
y_c ~ Gamma(a, a / y_e)
y_e ~ Gamma(10, 10)
```
which regularises `y_e` batch-specific normalisation effect to be close to 1, and regularises `y_c` cell-specific normalisation effect to be close to the average for each batch `y_e` using hyperparameter `a`.

Please let me know what you think is going on with this NaN `use_observed_lib_size=False` issue and what do you think about using more regularised priors.

**@canergen:** Can you provide what the minimum of your library size (and maximum) is and whether this behavior is dependent on this? I have observed this when not filtering for _min_counts_. I am not sure the problem is the range or the absolute value. It might be not what you are searching for but could help figuring out the problem.

**@adamgayoso:** This is why we switched the default. I imagine the problem exists because we use an exp to transform the log library size, where we could instead consider using softplus.

The prior is described [here](https://docs.scvi-tools.org/en/stable/user_guide/models/scvi.html). It's designed so that $\ell_n$ is on the same scale as the observed library size

**@vitkl:** After reviewing this more carefully, I think

1. the prior `l_sigma` is an overestimate of the total variance that can be attributed to the technical effect. A potential fix (and an easy fix) would be to add a hyper parameter to allows the user to reduce variance prior using a simple weight.

3. Indeed it is possible that softplus would make the computation more stable. Is it easy to change to softplus exclusively for size factors? Is this the operation here https://github.com/scverse/scvi-tools/blob/library_stability/scvi/nn/_base_components.py#L290?

4. I assume that the encoder network size, n_hidden is the same both for `z` and `l` which in my example is a pretty large number. This would mean that the network is massively overparameterised. In my trials of amortizing inference …

**@vitkl:** This line https://github.com/scverse/scvi-tools/blob/library_stability/scvi/module/_vae.py#L218 means that `softplus` is used here https://github.com/scverse/scvi-tools/blob/library_stability/scvi/nn/_base_components.py#L406 only when `use_size_factor_key == True`. This doesn't make sense - it should be `"softplus" if (use_size_factor_key or not use_observed_lib_size) else "softmax"`.

If you `softmax` transform gene expression prediction, it doesn't matter if the library size is estimated or "observed total count" - it has to match the same total count per cell.

**@adamgayoso:** > only when use_size_factor_key == True. This doesn't make sense - it should be "softplus" if (use_size_factor_key or not use_observed_lib_size) else "softmax".

We need to preserve backwards compatibility. scVI was originally described with a latent library size and softmax transformation

**@vitkl:** Ok, I can define an option to use softplus but keep the rest the same.

## #1549: Labels Key in totalVI
**Issue:** #1549 | **Last activity:** 2025-08-03T11:50:23Z
**State:** closed | **Author:** @StefanMDPhD | **Comments:** 8 | **Created:** 2022-06-01 | **Labels:** enhancement, totalvi, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1549

I've written this a few times in the past, but I can't say this often enough: Thank you for sharing your excellent analysis software with the community!

I'm writing to inquire about the possibility of exposing the labels_key in the totalVI model.

My reason for coveting this feature is the following: I have CITE-seq data from cells for which I have some a priori information on coarse cell type, i.e. my libraries consist of two different cell types that I've sorted (via FACS) and labeled with hash tag olives before multiplexing them into a single library.

[Perhaps anecdotally] I notice that when I integrate several of these libraries via scVI, using batch and label keys, the boundary between the two cell types remain crisp.  When I try this with totalVI, using batch key [and the additional CITE-seq data] there is more mixing between the [closely related] cell types.

Thanks in advance for considering this request.

**@adamgayoso:** Sorry I missed this, indeed this is something we would like to add but haven't gotten to yet.

**@lior-ness:** I second @StefanMDPhD! Thank you for the effort you put in this excellent package.

Exposing `labels_key` in totalVI is a highly desired feature on my end as well. I hope it's a simple enough addition.
I too noticed that cell-type-aware-embedding clusters much better compared with using batch keys alone.

**@ChrisMBrooks:** This would be a highly advantageous feature for my team as well.

@canergen, I've noticed this enhancement was assigned to yourself recently. Does this mean the feature is actively in development and can be expected in an upcoming release?

Thanks for the great software and for all the hard work that goes into it.

**@canergen:** Yes, the branch can_totalanvi pretty much contains the full model. However, I have currently a bit of backlog on other projects and won’t create a tutorial in the near future.

**@ChrisMBrooks:** @canergen,

Again, thank you kindly for the hard work on this and my apologies for the delayed response. Had to step away from work for personal reasons, but am now back to investigating the fitness of TOTALANVI for my team's needs. I've had success in installing from the can_totalanvi branch and performing a test run, but I had one quick follow-up question. How straight forward would it be, within this branch, to also wire up / expose the n_layers and n_hidden parameters so that they can be configured when instantiating the scvi.external.TOTALANVI model? This added flexibility would mean my team has everything we need to meet out needs.

Cheers,
Chris

**@ori-kron-wis:** Hey Chris,

Those parameters are actually exposed using the kwargs parameter of the model.
So you can technically init the model with something like:
`TOTALANVI(adata, n_hidden=512, n_latent=30, n_layers_encoder=3, n_layers_decoder=2)`
To bypass the default values of n_layers and n_hidden, or any other default parameter

Good luck!

**@ChrisMBrooks:** Hi @ori-kron-wis,

Ah, okay this is clear now. I had of course tried this, as I assumed the kwargs would handle the extra params but got an error, but it looks like I was tripped up by using  the "n_layers" keyword instead of "n_layers_encoder" and "n_layers_decoder". A quick test and it all seems to be working accordingly. Great!

Thanks Again,
Chris

**@ori-kron-wis:** Totalanvi was introduced in scvi-tools 1.3.x

## #2635: torch.distributed.DistBackendError when training on multiple GPUs
**Issue:** #2635 | **Last activity:** 2025-08-03T11:18:30Z
**State:** closed | **Author:** @CytoLiorG | **Comments:** 6 | **Created:** 2024-03-28 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2635

scvi crashes when trying to train on multiple GPUs (2x Tesla P100-PCIE-16GB)

As attempt to work around https://github.com/Lightning-AI/pytorch-lightning/issues/17212 issue `strategy='ddp_find_unused_parameters_true'` was set.


```python
def annotate(adata: AnnData, geneset: Dict, out_dir: str = 'out', epochs: int = None, visualize: bool = False, save: bool = False, random_seed=None) -> pd.Series:
    normalized = adata.copy()
    sc.pp.normalize_total(normalized, target_sum=1e4)
    sc.pp.log1p(normalized)
    normalized = normalized[:, geneset['gene_subset']].copy()
    sc.pp.scale(normalized)
    adata.obs["seed_labels"] = generate_seed_labels(normalized, geneset['cell_geneset'])
    base_model_train_ratio, transfer_model_train_ratio = get_train_ratio(adata, unconstrained_train_ratio=0.9)
    torch.set_float32_matmul_precision("medium")
    scvi.model.SCVI.setup_anndata(adata, batch_key=None, labels_key="seed_labels")
    if random_seed is not None:
        scvi.settings.seed = random_seed
    scvi_model = scvi.model.SCVI(adata, n_latent=30, n_layers=2)
    scvi_model.train(max_epochs=epochs, train_size=base_model_train_ratio, accelerator='gpu', devices=-1, strategy='ddp_find_unused_parameters_true')

    scanvi_model = scvi.model.SCANVI.from_scvi_model(scvi_model, 'unknown')
    print('Training transfer model:')
    scanvi_model.train(max_epochs=epochs, train_size=transfer_model_train_ratio, accelerator='gpu', devices=-1, strategy='ddp_find_unused …

**@agonencyto:** any update ?

**@martinkim0:** It looks like the issue is referring to a timeout in the NCCL library. Could you paste the installed versions of PyTorch, Lightning, and NCCL? Also, are any training steps being run or is it crashing right from the start (I see that it doesn't go past the first training epoch)?

**@martinkim0:** OK looking at the traceback further, looks like there's an issue with syncing losses to display it in the progress bar. Could you try passing in `enable_progress_bar=False` to `scanvi_model.train(...)`?

**@CytoLiorG:** Here is the log with `enable_progress_bar=False`:

```
2024-06-13 09:03:53.504676: I external/xla/xla/stream_executor/cuda/cuda_[executor.cc:991](http://executor.cc:991/)] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero. See more at https://github.com/torvalds/linux/blob/v6.0/Documentation/ABI/testing/sysfs-bus-pci#L344-L355
2024-06-13 09:03:53.509353: I external/xla/xla/stream_executor/cuda/cuda_[executor.cc:991](http://executor.cc:991/)] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero. See more at https://github.com/torvalds/linux/blob/v6.0/Documentation/ABI/testing/sysfs-bus-pci#L344-L355
2024-06-13 09:03:53.510154: …

**@CytoLiorG:** > It looks like the issue is referring to a timeout in the NCCL library. Could you paste the installed versions of PyTorch, Lightning, and NCCL? Also, are any training steps being run or is it crashing right from the start (I see that it doesn't go past the first training epoch)?

installed versions:

_lightning - 2.1.4
pytorch-lightning - 2.2.1
nvidia-nccl-cu12 - 2.19.3
torch - 2.2.1_

Yes, please see in the (more complete) log attached above, base training succeeds, it's the transfer training after that crashes.

**@ori-kron-wis:** MultiGPU was solved in scvi-tools 1.3

## #3299: Can't save model after multi-GPU training.
**Issue:** #3299 | **Last activity:** 2025-08-03T11:10:37Z
**State:** closed | **Author:** @alexanderchang1 | **Comments:** 14 | **Created:** 2025-04-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3299

<!-- Describe the bug -->
Hi,

I'm using mutli-GPU for training and it's causing me to be unable to save the model. Any advice on how to fix?

<!-- To reproduce -->

```python
print("Training scVI model...")
vae = scvi.model.SCVI(
    adata_combined,
    n_hidden=256,
    n_latent=50,
    n_layers=2
)

vae.train(max_epochs=400, accelerator="gpu", devices=-1, strategy="ddp_find_unused_parameters_true")

vae.save(dir_path="SCVI_Model_integrated_before_clustering", save_anndata=True, overwrite=True)
adata_combined.write('Total_Dataset_SCVI_integrated_before_clustering.h5ad')


```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
`Trainer.fit` stopped: `max_epochs=400` reached.
[rank3]: Traceback (most recent call last):
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/LobularTumorigenesisProject/scvi_processing.py", line 500, in <module>
[rank3]:     adata_combined.write('Total_Dataset_SCVI_integrated_before_clustering.h5ad')
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_jupyter/lib/python3.9/site-packages/anndata/_core/anndata.py", line 1929, in write_h5ad
[rank3]:     write_h5ad(
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_jupyter/lib/python3.9/site-packages/anndata/_io/h5ad.py", line 77, in write_h5ad
[rank3]:     with h5py.File(filepath, mode) as f:
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_jupyter/lib/python3 …

**@ori-kron-wis:** Can you try it with a recent version of scvi-tools?

**@alexanderchang1:** Hi, my institutional HPC has issues installing jax and scvi, so I'm loathe to attempt messing with it. Wrapping the save block of code with this line fixed the issue for me.

`

    if vae.trainer.is_global_zero:
        # Save results
        print("Saving results before clustering (rank 0)...")

        vae.save(dir_path="SCVI_Model_integrated_before_clustering", save_anndata=True, overwrite=True)
        adata_combined.write('Total_Dataset_SCVI_integrated_before_clustering.h5ad')

        # Perform clustering
        sc.pp.neighbors(adata_combined, use_rep="X_scVI")
        sc.tl.leiden(adata_combined)

        # Save final results
        print("Saving final results (rank 0)...")
        adata_combined.write('Total_Dataset_SCVI_integrated.h5ad')
        vae.save(dir_path="SCVI_Mode …

**@alexanderchang1:** In the name of scientific purity I tried updating it and re-running the code and it spawned a new error

`
[rank3]: Traceback (most recent call last):
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/LobularTumorigenesisProject/scvi_processing.py", line 1038, in <module>
[rank3]:     main()
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/LobularTumorigenesisProject/scvi_processing.py", line 1008, in main
[rank3]:     vae.train(max_epochs=max_epochs, accelerator="gpu", devices=-1, strategy="ddp_find_unused_parameters_true")
[rank3]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_jupyter/lib/python3.9/site-packages/scvi/model/base/_training_mixin.py", line 143, in train
[rank3]:     return runner()
[rank3]:   File "/ix1/alee/LO_LAB/Perso …

**@ori-kron-wis:** Im not sure what is that, but the latest works with python 3.10 +,  so perhaps need to update it first (and I would recommend to start a new env during this process)

**@alexanderchang1:** I upgraded to python 3.10 scvi-tools 1.3.0 and this error persists, the fix I mentioned above still works though.

`
`Trainer.fit` stopped: `max_epochs=400` reached.
[rank2]: Traceback (most recent call last):
[rank2]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/LobularTumorigenesisProject/scvi_processing.py", line 1132, in <module>
[rank2]:     main()
[rank2]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/LobularTumorigenesisProject/scvi_processing.py", line 1112, in main
[rank2]:     vae.save(dir_path="SCVI_Model_integrated_before_clustering", save_anndata=True, overwrite=True)
[rank2]:   File "/ix1/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_gpu_3_10/lib/python3.10/site-packages/scvi/model/base/_base_model.py", line 627, in save
[rank2]:     self.adata. …

**@ori-kron-wis:** It should be working. Im attaching a notebook that shows the basic tutorial is trained using multiGPU then saved and loaded again. https://app.reviewnb.com/scverse/scvi-tutorials/blob/Ori-custom-dataloaders-tutos/use_cases/multiGPU.ipynb/
(the same works from non jupyter also)

I suspect some environment/infrastructure issues:
You mentioned you have problems updating packages? what about other packages that are used in the process such as anndata and torch. You mentioned Jax. -How is it related?
Is saving and loading failed only after using multiGPU or also with non multigpu training?
Did you start a new env? What is you multi-GPU infra?

**@alexanderchang1:** Hi,

I started a new environment. Here's my full conda list. Saving and loading is only failing after multiGPU training on 4 A100s, it may be an infrastructure issue with how my institution has set up the multi gpu cluster. I've also included my linux distro information in case that's the source, as that has happened with other softwares due to glibc distribution problems etc.

```
NAME="Red Hat Enterprise Linux Server"
VERSION="7.9 (Maipo)"
ID="rhel"
ID_LIKE="fedora"
VARIANT="Server"
VARIANT_ID="server"
VERSION_ID="7.9"
PRETTY_NAME="Red Hat Enterprise Linux"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:redhat:enterprise_linux:7.9:GA:server"
HOME_URL="https://www.redhat.com/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"

REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
REDHAT_BUGZILLA_PRODUCT_V …

**@ori-kron-wis:** My only guess right now is the infrastructure.
We work with Ubuntu here.
We need to make sure its working for Red Hat also (although I think it's not the OS in your case)

**@canergen:** To clarify, it runs smoothly with a single GPU. @ilan-gold to me this looks more like an AnnData issue. It’s trying to use multiple file streams to write the file(?). Any recommendation to avoid this?

**@ilan-gold:** Without knowing anything about the issue, Can, I don't think h5 is threadsafe (and using it in processes for writing is probably also not safe).  But I would need to dig into the issue to know more.

**@alexanderchang1:** Yes it runs smoothly with a single GPU. I believe the distribution across 4 GPUs means they don't all exit at the same time, and at somepoint in the code two different GPUs try to get to the save code at the same time and that's where it breaks, I don't know enough about the ddp parallelization to read deeper than that.

**@ilan-gold:** BTW I'm not saying it won't work with processes, it's just that I don’t know.  We work read (not write) h5 in processes by reopening the file  which bypasses the lock (meant for preventing threaded usage).  But I dont know what happens when you write from multiple processes.  I could come up with scenarios where it might work and where it might not

**@ilan-gold:** Zarr would be my recommendation for avoiding the issue but writing into one store with from multiple sources is tricky independent of the file backend

**@ori-kron-wis:** Im closing it here, but keeping this remark if such a thing happens again:

> Hi, my institutional HPC has issues installing jax and scvi, so I'm loathe to attempt messing with it. Wrapping the save block of code with this line fixed the issue for me.
>
> `
>
> ```
> if vae.trainer.is_global_zero:
>     # Save results
>     print("Saving results before clustering (rank 0)...")
>
>     vae.save(dir_path="SCVI_Model_integrated_before_clustering", save_anndata=True, overwrite=True)
>     adata_combined.write('Total_Dataset_SCVI_integrated_before_clustering.h5ad')
>
>     # Perform clustering
>     sc.pp.neighbors(adata_combined, use_rep="X_scVI")
>     sc.tl.leiden(adata_combined)
>
>     # Save final results
>     print("Saving final results (rank 0)...")
>     adata_combined.write('Tot …

## #2774: Consider non-jitting MRVI tests/long tests pytest flag
**Issue:** #2774 | **Last activity:** 2025-08-03T06:35:29Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-05-02 | **Labels:** P2, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2774

**@ori-kron-wis:** We put tags on relevant long tests

## #2551: Assess whether we should deprecate more `scvi.data` functions
**Issue:** #2551 | **Last activity:** 2025-08-03T06:34:16Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-25 | **Labels:** enhancement, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2551

**@ori-kron-wis:** We keep them as long as they are working based on our scheduled integration tests.
Once we know that a service is failing, we look into it.

## #2543: Remove `scvi.data.cellxgene`
**Issue:** #2543 | **Last activity:** 2025-08-03T06:32:45Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-21 | **Labels:** P2, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2543

Deprecated in 1.2, needs to be removed in 1.3.

**@ori-kron-wis:** Adding here that cellxgene-census still requires numpy<2.0, and only once this constraint will be removed we could also remove it. scvi-tools 1.3 does not have this constraint.

## #2311: Separate out unit and integration tests
**Issue:** #2311 | **Last activity:** 2025-08-03T06:29:01Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 2 | **Created:** 2023-10-30 | **Labels:** good first issue, tests, CI/CD, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2311

Our current test suite that runs for every PR takes about 10-15 min. It doesn't need to be the case that all tests should be run for every change, though. It would be nice to separate out unit and integration tests, where unit tests run for every change and integration tests run on a schedule or on dispatch.

**@ori-kron-wis:** this helps: https://github.com/scverse/scvi-tools/pull/3111

**@ori-kron-wis:** Closing here as we have several new testing tags, which take care of it, while we keep our dispatch testing strictly under 10min.

## #3445: criticism module not available in scvi-tools 1.3.3
**Issue:** #3445 | **Last activity:** 2025-08-03T05:59:29Z
**State:** closed | **Author:** @sjspielman | **Comments:** 2 | **Created:** 2025-07-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3445

I have installed `scvi-tools` version `1.3.3` in a conda environment (via PyPI) and am attempting to use the new `criticism` module to assess model quality and convergence. However, it does not appear this module has been fully initialized/integrated into the package for use? I see the `criticism` module is indeed included in the `src` directory of this release and it's included in documentation (e.g. [here](https://docs.scvi-tools.org/en/1.3.3/api/reference/scvi.criticism.PosteriorPredictiveCheck.html#)), but it does not appear this module is ready for use.


## Reproduce bug

Output from my environment:

```
$ conda list scvi-tools
# Name                     Version          Build            Channel
scvi-tools                 1.3.3            pypi_0           pypi
```

When attempting to use in Python:


```python
Python 3.11.13 | packaged by conda-forge | (main, Jun  4 2025, 14:52:34) [Clang 18.1.8 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import scvi
>>> scvi.criticism # can this be found?
```

Output from above:

```pytb
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'scvi' has no attribute 'criticism'
```

#### Versions:

<!-- Output of scvi.__version__ -->

```
>>> scvi.__version__
'1.3.3
```

**@ori-kron-wis:** Hey,

Thanks for noticing, there is a current issue where we need to explicitly import it.
But it shouldnt hold you back:
scvi.criticism is an index of 2 functions basically: create_criticism_report and PosteriorPredictiveCheck (PPC). by itself, it will not give you anything (but it shouldn't produce an error either)

So if you wish to use it, import by:
from scvi.criticism import PosteriorPredictiveCheck as PPC
and/or
from scvi.criticism import create_criticism_report

afterwards you will also see scvi.criticism works (or not produce an error)

It will be fixed for next release.

**@sjspielman:** Thanks very much for your reply @ori-kron-wis, this is working for me!

## #3421: scVIVA: early stopping works as intended?
**Issue:** #3421 | **Last activity:** 2025-07-25T08:09:01Z
**State:** closed | **Author:** @dbdimitrov | **Comments:** 6 | **Created:** 2025-07-11 | **URL:** https://github.com/scverse/scvi-tools/issues/3421

Hi,

I've been running scVIVA on some cosmx data and I've noticed that if I use early stopping, it would essentially always stop at 1 + `early_stopping_patience`.

I'm currently travelling and I don't have the time to sit down and check in detail, but it's likely that the (negative) sign of the loss is leading to it stopping prematurely.

Might be a good idea to check.

Daniel

**@dbdimitrov:** PS. I'm running this on the latest version of scvi-tools: i.e. `1.3.2`

**@canergen:** Thanks. I assume you used elbo_validation loss as the criterion for early stopping? @LevyNat I think we did all experiments without early stopping and the issue might be that additional losses tend to let ELBO increase over time. Easiest suggestion we should just check for it in model.train and throw an error (so early_stopping not supported in scVIVA).

**@dbdimitrov:** Hi @canergen,

Thanks for the prompt response. Yes, I was using elbo_validation as criterion.

From what I'm getting, I should avoid using early stopping for now, but please do let me know if there is a val loss that would work better than the ELBO :)

I'm mostly asking since I'm doing some method comparisons and trying to give each method it's best chance to do well.

**@canergen:** Looking forward to the benchmark. Feel free to contact us with issues (errors or performance issues) that arise using scVIVA. We are happy to improve tools based on solid benchmarks.

**@LevyNat:** Hi, @canergen it is true that the current criterion is the elbo without the niche losses. It means that at some point, the elbo might stop decreasing and increase a bit. But if @dbdimitrov says that the training stops at epoch 1+patience, it means that the elbo does not decrease at the beginning of the training, which is not expected. I'd be happy to debug this with you, best thing is to start by using the same parameters as in the tutorial (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/spatial/scVIVA_tutorial.html) and plot the losses, then we'll see what goes wrong. You can send me privately

**@dbdimitrov:** Hi @LevyNat,

I changed a bit the parameters and specifically halving the default learning rate (as in the tutorial) seems to fix it.

I thought that not negating the ELBO (or the reported loss) might've been the reason - it was a bit suspicious that it was stopping exactly at the patience threshold, while e.g. SCANVI took much longer to early stop with essentailly the same hyperparams.

Thanks for the responses!

## #3431: Integration Testing CI Test Failure on python 3.11
**Issue:** #3431 | **Last activity:** 2025-07-23T12:41:32Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-07-23 | **URL:** https://github.com/scverse/scvi-tools/issues/3431

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/16459276101) to review. @scverse/anndata

## #3432: Integration Testing CI Test Failure on python 3.12
**Issue:** #3432 | **Last activity:** 2025-07-23T12:41:20Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 1 | **Created:** 2025-07-23 | **URL:** https://github.com/scverse/scvi-tools/issues/3432

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/16459276101) to review. @scverse/anndata

**@ori-kron-wis:** https://github.com/pyro-ppl/numpyro/issues/2051

## #3429: Pretrained SOLO model does not load
**Issue:** #3429 | **Last activity:** 2025-07-23T04:54:05Z
**State:** closed | **Author:** @maupagas | **Comments:** 2 | **Created:** 2025-07-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3429

<!-- Describe the bug -->

Hello,

I am running a single-cell analysis, and I ran a SOLO model for doublet detection. After running the model, I saved it for future reloading if needed in the following directory:

```
../models/cellranger_output/sample_0013/solo_model/solo_model.pt
../models/cellranger_output/sample_0013/solo_model/solo_adata.h5ad
```

However, I am unable to reload the model with the following commands:

```python

solo_model_dir = "../models/cellranger_output/sample_0013/solo_model/"
solo_model = scvi.external.SOLO.load(solo_model_dir, prefix="solo_")
```

The following error is shown:

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: 'Classifier' object has no attribute 'on_load'
```

Apparently, the load module from the documentation requires a classifier, cls, to load?

#### Versions:

I am currently using this version:

scvi-tools version: 1.3.2


Any workarounds to load a pretrained SOLO model with saved adata?

**@ori-kron-wis:** Thanks for catching this.
We had to add SupervisedModuleClass to the classifier, see:
https://github.com/scverse/scvi-tools/pull/3430

**@maupagas:** Thanks for the quick reply and fix! Wii try the updated file.

## #3347: MrVI - minimal number of genes
**Issue:** #3347 | **Last activity:** 2025-07-07T15:40:33Z
**State:** closed | **Author:** @dansteiert | **Comments:** 3 | **Created:** 2025-05-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3347

<!-- Describe the bug -->

Hey,
I am running MrVI on two datasets - a scRNAseq dataset (~30k genes) and a protein dataset (~40 genes).
With the scRNAseq Dataset everything is working very well!
The 40gene dataset does not unfortunately.
-> Training actually finishes (over multiple iterrations)
-> looking into the losses (e.g. model.history()) are all nan.

Is there a lower threshold for number of genes the model wants to learn on - e.g. first layer has higher dimensions as the input layer?

could these be datatype issues?

or do I need to pass specific parameters to the model - currently I am running this with no additional arguments
```
MRVI.setup_anndata(adata, sample_key=sample_key, batch_key=batch_key)
model = MRVI(adata)
```
Very thankful for your insights!

**@ori-kron-wis:** Can you show a snippet of your model history loss numbers to show if it was from the beginning or just in the last epoch? (How many epochs did he go with loss = Nan)


There is no minimum number of genes needed, but you can check for some default training parameters in the code:
```
    n_latent: int = 30
    n_latent_u: int = 10
    encoder_n_hidden: int = 128
    encoder_n_layers: int = 2
    z_u_prior: bool = True
    z_u_prior_scale: float = 0.0
    u_prior_scale: float = 0.0
    u_prior_mixture: bool = True
    u_prior_mixture_k: int = 20
```
```
DEFAULT_TRAIN_KWARGS = {
    "max_epochs": 100,
    "early_stopping": True,
    "early_stopping_patience": 15,
    "check_val_every_n_epoch": 1,
    "batch_size": 256,
    "train_size": 0.9,
    "plan_kwargs": {
        "lr": 2e-3,
        "n …

**@dansteiert:** To the model history, it is NaN everywhere from the first epoch.

Thank you I will have a look into the autotune function and see If I can find something there, to make it work for this dataset

**@PierreBoyeau:** Thanks a lot for your interest in this model.
MrVI has not been tested on data with that few features, let alone on protein data. For this reason, I would advise against using MrVI on such data. To work with protein data, I'd probably 1. make sure that the protein data corresponds to raw and untransformed count data (otherwise, training and inference will definitely raise NaN errors), and 2. adjust MrVI likelihood taking inspiration from TOTALVI, for instance.
I am closing this, but feel free to reopen if you have follow-up questions!

## #2602: Failing to train on multiple GPUs in jupyter notebook
**Issue:** #2602 | **Last activity:** 2025-07-07T10:33:09Z
**State:** closed | **Author:** @chem1kal1 | **Comments:** 6 | **Created:** 2024-03-06 | **Labels:** bug, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2602

<!-- Describe the bug -->

After running SCVI.setup_anndata and creating the model, when training the model with devices != 1 (ex devices = 2) an error occurs:

RuntimeError: CUDA error: initialization error
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1.
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.
<!-- To reproduce -->
import your h5ad data,
```python
scvi.model.SCVI.setup_anndata(adata, layer = "counts", categorical_covariate_keys=['Sample'],
                             continuous_covariate_keys=['pct_counts_mt', 'total_counts', 'pct_counts_ribo'])
model = scvi.model.SCVI(adata)
model.train(devices = 2)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
RuntimeError: CUDA error: initialization error
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1.
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.
```

#### Versions:

scvi-tools '1.1.2'
torch '2.2.1+cu118'

OS is ubuntu 22.04


I have tested ddp_notebook_find_unused_parameters_true
and it does not work either.
In fact, providing a strategy parameter causes it to fail.

Running on 1 gpu works fine. Sometime last year I was able to run on two gpu …

**@martinkim0:** Hi, sorry you're running into this issue. Did you happen to try running multi-GPU training outside of the notebook? Does it work then or is it the same error?

**@chem1kal1:** It is the same error when running it in a .py file.

**@martinkim0:** Apologies for the delay. Is there a different error when passing in a strategy parameter? Could you try passing in the DDPStrategy using the spawn start method?

**@Bo-UT:** Got the exactly same error here

**@ori-kron-wis:** to run multi GPU in jupyter notebook use strategy="ddp_notebook_find_unused_parameters_true"

**@canergen:** We have made several changes to multi-GPU support and it is now supported on our end in the main branch (and will be released with scvi-tools 1.3.0). Please give it a try!

## #3391: peakVI: effect_size calculation discrepancy: est_prob2 - est_prob1 vs doc's est_prob1 - est_prob2
**Issue:** #3391 | **Last activity:** 2025-07-07T10:29:24Z
**State:** closed | **Author:** @Xiao123368 | **Comments:** 1 | **Created:** 2025-06-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3391

In the PeakVI differential accessibility analysis, the official documentation states that effect_size is calculated as est_prob1 - est_prob2 (where est_prob1 corresponds to the target group, e.g., Cluster 0, and est_prob2 corresponds to the contrast group). However, in my results, the effect_size values appear to be calculated as est_prob2 - est_prob1 (i.e., the sign is reversed)，as shown below:

![Image](https://github.com/user-attachments/assets/deb8707c-d981-4b7f-af70-a499539b9c0c)
![Image](https://github.com/user-attachments/assets/d84fae89-44db-4695-9a8b-daeeaf8d88e0)

Is the effect_size calculation intentionally reversed (i.e., est_prob2 - est_prob1)?

**@ori-kron-wis:** Thanks for noticing, its a typo in the tutorial and will be fixed in the next release.

## #3390: peakVI: two_sided argument not recognized in differential_accessibility() despite tutorial usage
**Issue:** #3390 | **Last activity:** 2025-07-07T10:17:51Z
**State:** closed | **Author:** @Xiao123368 | **Comments:** 2 | **Created:** 2025-06-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3390

When using PEAKVI for differential accessibility analysis, I encounter an error where the two_sided argument is not recognized, even though it's used in the official scvi-tools peakVI tutorial.

da_res22 = model.differential_accessibility(
    idx1=np.where(adata.obs[PEAKVI_CLUSTERS_KEY] == "0"),
    two_sided=False,
)

da_res22.head()
TypeError: DifferentialComputation.get_bayes_factors() got an unexpected keyword argument 'two_sided'

**@canergen:** We are about to release a tutorial without this plot. It will be part of a new release latter this week. The DE test is now three sided and you want to only look a upregulated peaks by filtering after the procedure.

**@Xiao123368:** Thanks a lot for the prompt clarification! Looking forward to the updated tutorial and new features.

## #3364: `MULTIVI.get_protein_foreground_probability` raises AttributeError
**Issue:** #3364 | **Last activity:** 2025-07-07T10:15:25Z
**State:** closed | **Author:** @ilia-kats | **Comments:** 1 | **Created:** 2025-05-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3364

<!-- Describe the bug -->
After training a MultiVI model on CITE-seq data, `get_protein_foreground_probability` raises an exception

<!-- To reproduce -->
mdata is the 10x PBMC 5k dataset
```python
scvi.model.MULTIVI.setup_mudata(mdata, rna_layer="counts", protein_layer="counts", modalities={"rna_layer": "rna", "protein_layer": "prot"})
vae = scvi.model.MULTIVI(mdata, gene_likelihood="nb")
vae.train(max_epochs=500, train_size=1, datasplitter_kwargs={"num_workers": 4, "pin_memory": True}, early_stopping=False, batch_size=1000)
vae.get_protein_foreground_probability(mdata)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError                            Traceback (most recent call last)
Cell In[22], line 1
----> 1 vae.get_protein_foreground_probability(mdata)

File [/data/ilia/multiomicscourse/env/lib/python3.11/site-packages/torch/utils/_contextlib.py:116](http://localhost:8889/lab/tree/env/lib/python3.11/site-packages/torch/utils/_contextlib.py#line=115), in context_decorator.<locals>.decorate_context(*args, **kwargs)
    113 @functools.wraps(func)
    114 def decorate_context(*args, **kwargs):
    115     with ctx_factory():
--> 116         return func(*args, **kwargs)

File [/data/ilia/multiomicscourse/env/lib/python3.11/site-packages/scvi/model/_multivi.py:1059](http://localhost:8889/lab/tree/env/lib/python3.11/site-packages/scvi/model/_multivi.py#line=1058), in MULTIVI.get_protein_foreground_probability(self, …

**@ori-kron-wis:** yes this was solved recently and merged to main , see: https://github.com/scverse/scvi-tools/issues/3335
so please install from main and try again

## #3352: batch projection for posterior predictive samples
**Issue:** #3352 | **Last activity:** 2025-06-05T12:25:42Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-05-25 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3352

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
[Based on this post](https://discourse.scverse.org/t/domain-adaptation-to-pre-train-batch-correction-model-using-paired-data/3633/9)

## #3266: Training time of MrVI is too long, I am not sure if it is using GPU accelerator
**Issue:** #3266 | **Last activity:** 2025-05-29T06:28:32Z
**State:** closed | **Author:** @Kassab11 | **Comments:** 3 | **Created:** 2025-03-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3266

<!-- Describe the bug -->

When trying to train MrVI on batch correction, I face this note "Jax module moved to cuda:0.Note: Pytorch lightning will show GPU is not being used for the Trainer. ". And following that is this:

GPU available: True (cuda), used: False
TPU available: False, using: 0 TPU cores
HPU available: False, using: 0 HPUs
/home/kassab/miniconda3/envs/CB803/lib/python3.12/site-packages/lightning/pytorch/trainer/setup.py:177: GPU available but not used. You can set it by doing `Trainer(accelerator='gpu')`.


So I ran watch -n1 nvidia-smi to ensure if its using GPU or not, my GPU shows that its active (GPU power ~65 and memory allocated around 2GB) However, from the training time (~40-60 minutes) on a dataset (AnnData object with n_obs × n_vars = 32826 × 12303) I suspected that maybe something is wrong. On scVI with the same dataset it takes (10-15 minutes).

I have tried:

from lightning.pytorch import Trainer

trainer = Trainer(accelerator="gpu", devices=1, strategy="ddp_notebook")

which shows:

GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
HPU available: False, using: 0 HPUs

I also tried updating Jax to version 0.5.1 but then compatibility issues arised. so I have reused jax==0.4.35

my system info:
python == 3.12
CUDA Version: 12.2
scvi.__version__  == '1.3.0'
Cuda compilation tools, release 12.8, V12.8.93
pytorch.__version__ == 2.6.0+cu124
pl.__version__ == 2.5.0.post0

<!-- To reproduce -->

```python
# Your code here …

**@ori-kron-wis:** > When trying to train MrVI on batch correction, I face this note "Jax module moved to cuda:0.Note: Pytorch lightning will show GPU is not being used for the Trainer. ". And following that is this:
>
> GPU available: True (cuda), used: False TPU available: False, using: 0 TPU cores HPU available: False, using: 0 HPUs /home/kassab/miniconda3/envs/CB803/lib/python3.12/site-packages/lightning/pytorch/trainer/setup.py:177: GPU available but not used. You can set it by doing `Trainer(accelerator='gpu')`.

It's okay. in JAX, it means GPU is being used (you also monitored nvidia-smi)
re MRVI, there is an open issue about this slowness: https://github.com/scverse/scvi-tools/issues/3179
We hope it will be solved in a fix JAX needs to issue (https://github.com/jax-ml/jax/issues/26162)
We recommend …

**@ori-kron-wis:** We also found the Jax 0.4.35 can't work for CUDA12.6+. So need to use CUDA12.4
For newer version of Jax (0.6) it works with CUDA12.6+, but is still slower than before.

I also think you shouldnt use strategy="ddp_notebook" during training on single GPU

**@ori-kron-wis:** Im closing this issue, as we are aware of mrVI training slowness and working to improve it.
Right now the solution is to work with jax=0.4.35 and cuda 12.4 or cuda 12.2 . it will be faster than latest versions of both.

## #3359: can't save anndata with new integrated gradients output
**Issue:** #3359 | **Last activity:** 2025-05-29T06:00:51Z
**State:** closed | **Author:** @cvduffy | **Comments:** 3 | **Created:** 2025-05-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3359

Currently, `None` values can't be serialized to .h5ad using `anndata.write()` (though this is supposed to be fixed in an upcoming update to the anndata package). After #3264 , which adds a `modality` field with default value `None` to the integrated gradients output, inference routines that store integrated gradients results to the anndata object (e.g. in `uns`) break when trying to write the anndata object to disk.

**@ori-kron-wis:** Hey @cvduffy, will changing it to "None"  (string) be enough?

**@cvduffy:** Yes, that would fix it - thanks!

(On a separate but related note - the `marker`/`marker_idx` columns might be better named `feature`/`feature_idx` since the attribution functionality is not necessarily used in the context of selecting markers)

**@ori-kron-wis:** Thanks for the suggestion.
We will add the fix for the next release. in the meantime, please fix it manually.

## #3335: MultiVI: Easy-to-fix error around getting protein probabilities
**Issue:** #3335 | **Last activity:** 2025-05-25T10:42:03Z
**State:** closed | **Author:** @MPebworthEpana | **Comments:** 2 | **Created:** 2025-05-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3335

<!-- Describe the bug -->

MultiVI claims to be about the extract protein probabilities via get_protein_foreground_probability, but it fails due to an inability to get the protein names.

Essentially, when return_numpy = True, the function work. When return_numpy = False, it fails.

The error is likely on like 1059 of _multivi.py, where the function tries to pull self.protein_state_registry.
Which the MultiVI class does not initialize, unlike TotalVI and others. I'm not sure what the best way is, but the pro_names just needs to come from a different place. I've tried other ways to pull out the protein names, but MultiVI doesn't seem to like it. No matter what I do.

Also, line 1003 may causes errors, because I wasn't able to access scvi_setup_dict_ for a MultiVI model. It doesn't seem to exist. (

Code from 1059:

        if return_numpy is True:
            return 1 - py_mixings
        else:
            pro_names = self.protein_state_registry.column_names #THIS HERE FAILS
            foreground_prob = pd.DataFrame(
                1 - py_mixings,
                columns=pro_names[protein_mask],
                index=adata.obs_names[indices],
            )
            return foreground_prob

Line 1003:
all_proteins = self.scvi_setup_dict_["protein_names"]

Is there another way to pull protein names from a multiVI model?

**@ori-kron-wis:** Thank you for catching this. Indeed, the protein_state_registry was missing in multivi and it is fixed.
Can you install scvi-tools from the fix branch? It will take a while until we release a new version again.

Dont you have the list of protein names before you train your model? In such case, you can extract it with Numpy and manually do the post-processing of transferring to pd.dataframe and add those names as columns, exactly like in code above.

**@MPebworthEpana:** Great, thank you so much for fixing it so quickly!
Yes, I can manually patch it like this, but I was just hoping to use the internal-portions of a MultiVI model in order to guarantee that the protein-name order is correct.

## #3342: scVI batch correction clusters all cells from sample in a circle (potential artifact)
**Issue:** #3342 | **Last activity:** 2025-05-22T16:35:55Z
**State:** closed | **Author:** @CocoConstant | **Comments:** 3 | **Created:** 2025-05-21 | **URL:** https://github.com/scverse/scvi-tools/issues/3342

<!-- Describe the bug -->

When using scVI for batch correction and clustering on my single-cell data, I observed an unusual result: all cells from the same sample are clustered in a circle, separated from the rest. Changes to `n_latent`, training epochs, and HVG numbers did not resolve the circular artifact. The UMAP plot is attached for reference (see cluster 10)<img alt="image1" width="647" src="https://github.com/user-attachments/assets/ef8acf71-c7dc-43f8-a5b1-0a31f24c5dc3" />.

<!-- To reproduce -->
Below are my codes:
```python
import scanpy as sc
import torch
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
from collections import defaultdict

torch.set_float32_matmul_precision("high")

pbmc = sc.read_h5ad('/data/work/data/raw_data/ESCC_PBMC_All_Basic_QC.h5ad')

# downsample each sample for hvg calculation
sample_key = 'sample_info'
n_subsample = 5000
pbmc_list = []

for sample in pbmc.obs[sample_key].unique():
    pbmc_sample = pbmc[pbmc.obs[sample_key] == sample].copy()
    n_cells = pbmc_sample.shape[0]
    if n_cells > n_subsample:
        idx = np.random.choice(n_cells, size=n_subsample, replace=False)
        pbmc_sub = pbmc_sample[idx, :].copy()
        pbmc_list.append(pbmc_sub)
    else:
        pbmc_list.append(pbmc_sample)

pbmc_meger = sc.concat(pbmc_list, label='tmp_info')

sc.pp.highly_variable_genes(
    pbmc_meger,
    flavor="seurat_v3",
    n_top_genes=3000,
    batch_key="tmp_info", …

**@ori-kron-wis:** Hi,

When you downsample, can you also choose cells with information and not just randomly:
`sc.pp.filter_cells(adata, min_counts=3)
`

Also, before selecting HVG for merged data, choose genes with meaning:
`sc.pp.filter_genes(adata, min_counts=3)
`

Keep the raw data before doing the normalization and transformation:
`pbmc.layers["counts"] = pbmc.X.copy()
`

And try the updated version of scvi-tools also (1.3.1)

Lastly, please post this question in our discourse Q&A forum, so other users will also be able to see it (https://discourse.scverse.org/c/help/scvi-tools/7).

Thanks

**@CocoConstant:** > Hi,
>
> When you downsample, can you also choose cells with information and not just randomly: `sc.pp.filter_cells(adata, min_counts=3) `
>
> Also, before selecting HVG for merged data, choose genes with meaning: `sc.pp.filter_genes(adata, min_counts=3) `
>
> Keep the raw data before doing the normalization and transformation: `pbmc.layers["counts"] = pbmc.X.copy() `
>
> And try the updated version of scvi-tools also (1.3.1)
>
> Lastly, please post this question in our discourse Q&A forum, so other users will also be able to see it (https://discourse.scverse.org/c/help/scvi-tools/7).
>
> Thanks

Thank you for your prompt reply and suggestions! Before calculating HVGs, I have already performed basic quality control, including filtering out low-quality cells and genes with low expres …

**@ori-kron-wis:** closed here, continue in discourse

## #2949: Bugs related to MultiVI
**Issue:** #2949 | **Last activity:** 2025-05-16T03:10:12Z
**State:** closed | **Author:** @GoldenCaterpie | **Comments:** 7 | **Created:** 2024-08-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2949

<!-- Describe the bug -->

Hello! When running the MultiVI_tutorial.ipynb, I encountered a strange bug.
```python
# We can now use the organizing method from scvi to concatenate these anndata
# adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired, adata_rna, adata_atac)
adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired, None, None)
```
If I modify the code here to only use Multiome data (Gene Expression and Chromatin Accessibility), an error will occur during the subsequent model training regardless of the size of adata_paired. This error always happens under these conditions. However, if adata_rna or adata_atac is added, even with just one cell's information, the model can be trained normally.

I tested this bug in both my environment (Python 3.11) and Google Colab, and it appeared in both.

I would appreciate any guidance on this issue. Thank you very much!

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[/usr/local/lib/python3.10/dist-packages/scvi/model/_multivi.py](https://localhost:8080/#) in train(self, max_epochs, lr, accelerator, devices, train_size, validation_size, shuffle_set_split, batch_size, weight_decay, eps, early_stopping, save_best, check_val_every_n_epoch, n_steps_kl_warmup, n_epochs_kl_warmup, adversarial_mixing, datasplitter_kwargs, plan_kwargs, **kwargs)
    339             **kwargs,
    340         )
--> 341         return runner()
    342
    343     @torch …

**@canergen:** Hi. Potential duplicate of: https://github.com/scverse/scvi-tools/issues/2262 can you disable adversarial mixing? This change will be released in version 1.2y

**@GoldenCaterpie:** > Hi. Potential duplicate of: #2262 can you disable adversarial mixing? This change will be released in version 1.2y

It seems to work! Thank you very much!

**@canergen:** The post above doesn't make sense. @GoldenCaterpie is this related to your issue? It doesn't make sense to me to even have an installer (haven't downloaded due to this). Could the users otherwise provide the issue that they are getting?

**@Josh65-2201:** It malware that spammed all over GitHub, don't downloaded it and report the user

**@canergen:** Thanks. Reported it and deleted the post and to reduce risk for other users.

**@GoldenCaterpie:** > The post above doesn't make sense. @GoldenCaterpie is this related to your issue? It doesn't make sense to me to even have an installer (haven't downloaded due to this). Could the users otherwise provide the issue that they are getting?

It was indeed virus and my account was hacked too :(

**@MPebworthEpana:** This error continues to be an issues in scVI v 1.3. And I need adversarial_mixing on, because the CITE-seq and scRNA-seq data simply aren't mixing. It's a near perfect seperation.

Turns out - I just needed to drop the learning rate to 1e-6.....

## #3322: Integration Testing CI Install Failure on python 3.12
**Issue:** #3322 | **Last activity:** 2025-05-15T15:43:17Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-05-14 | **URL:** https://github.com/scverse/scvi-tools/issues/3322

The daily CI failed on install for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/15010075672) to review. @scverse/anndata

## #3321: Integration Testing CI Install Failure on python 3.11
**Issue:** #3321 | **Last activity:** 2025-05-14T19:53:49Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-05-14 | **URL:** https://github.com/scverse/scvi-tools/issues/3321

The daily CI failed on install for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/15010075672) to review. @scverse/anndata

## #2907: Fix custom dataloader registry
**Issue:** #2907 | **Last activity:** 2025-05-13T13:28:00Z
**State:** closed | **Author:** @canergen | **Comments:** 3 | **Created:** 2024-07-23 | **Labels:** enhancement, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2907

CustomDataloaders currently don't support advanced capabilities like scArches or celltype prediction in scANVI. We have to create a registry without setup_anndata that contains the same elements (see below).
https://github.com/chanzuckerberg/cellxgene-census/blob/222efddf2ce82f93f76329aa353962c1dc2400ac/api/python/notebooks/experimental/pytorch_loader_scvi.ipynb is the first working example. Currently, they use the following code to save the model:
```
user_attributes = model._get_user_attributes()
user_attributes = {a[0]: a[1] for a in user_attributes if a[0][-1] == "_"}

user_attributes.update(
    {
        "n_batch": datamodule.n_batch,
        "n_extra_categorical_covs": 0,
        "n_extra_continuous_covs": 0,
        "n_labels": 1,
        "n_vars": datamodule.n_vars,
    }
)
```
We want to create a new function that fills out the registry and passes it to the model at: `model = scvi.model.SCVI(n_layers=n_layers, n_latent=n_latent, gene_likelihood="nb", encode_covariates=False)`. You can see all necessary entries and the structure at: `scvi.adata_manager.get_state_registry(scvi.REGISTRY_KEYS.X_KEY).to_dict()`.
After fixing this, all uses of `_module_init_on_train` throughout the codebase should be removed as they are not necessary anymore.

**@gokceneraslan:** Is there some documentation on what is expected of the custom dataloader's collate function? I can imagine a dict with keys like `X`, `batch` and `labels` just by following up on the different types of exceptions I am getting. But for poor souls like us who are not familiar with the codebase, it'd be amazing to have some documentation of what type of keys a collate function should return in the dictionary to work.

**@canergen:** Hi, we are currently still exchanging ideas with lamin and CZI to make the implementation better (and hopefully work towards support throughout all models - currently scVI works). Overall, the final requirement will be that a registry as a dictionary is created similar to https://colab.research.google.com/drive/10sXec_TicMKtLA6hMcgfkado-FgoNKxw#scrollTo=e8vZgceklGdH. We use as a discussion channel https://github.com/laminlabs/lamindb/issues/1826 to work together on a better implementation. Happy to connect offline (best case scverse Zulip) to see how we can support your work.

**@ori-kron-wis:** https://github.com/scverse/scvi-tools/pull/2932

## #3208: RESOLVI: rapids deprecated in scanpy 1.10
**Issue:** #3208 | **Last activity:** 2025-05-08T12:14:28Z
**State:** closed | **Author:** @j-bac | **Comments:** 1 | **Created:** 2025-02-25 | **URL:** https://github.com/scverse/scvi-tools/issues/3208

@canergen
Using 'rapids' option is deprecated in latest scanpy in favor of rapids_singlecell. While 'rapids' is still supported, this creates issues for small samples (<8192). scanpy throws an error:
`--> 670             assert transformer in {None, "sklearn"}`

https://github.com/scverse/scvi-tools/blob/9f210c73333584b42a5479442244b4d2da3a0f84/src/scvi/external/resolvi/_model.py#L368-L371

**@canergen:** Oh. So basically while it’s deprecated, for samples with more than 8000 cells it’s more than deprecated (not supported anymore) for small datasets? It sounds like a scanpy bug. Overall, I assume that I should change this sloppy usage.

## #3283: RESOLVI: using `num_samples > 1` in `get_normalized_expression` fails
**Issue:** #3283 | **Last activity:** 2025-05-08T12:14:18Z
**State:** closed | **Author:** @abs51295 | **Comments:** 2 | **Created:** 2025-04-03 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3283

<!-- Describe the bug -->

I am trying to get normalized expression from resolVI model. If I pass `num_samples` > 1 it fails.

<!-- To reproduce -->

```python
resolvae = RESOLVI.load(args.scvi_output_dir, adata=adata)

adata.layers['generated_counts'] = scp.csr_matrix(resolvae.get_normalized_expression(batch_size=5000, n_samples=30, library_size=10000))

Traceback (most recent call last):
  File "/common/knottsilab/MET_analysis/MET_analysis_2025/neoadjuvant_cagra_outputs/run_resolVI_downstream.py", line 91, in <module>
    adata.layers['generated_counts'] = scp.csr_matrix(resolvae.get_normalized_expression(batch_size=5000, n_samples=3, library_size=10000))
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/shaha4/miniforge3/envs/rapids-24.12-stable/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 116, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/shaha4/miniforge3/envs/rapids-24.12-stable/lib/python3.11/site-packages/scvi/external/resolvi/_utils.py", line 341, in get_normalized_expression
    return pd.DataFrame(
           ^^^^^^^^^^^^^
  File "/home/shaha4/miniforge3/envs/rapids-24.12-stable/lib/python3.11/site-packages/pandas/core/frame.py", line 827, in __init__
    mgr = ndarray_to_mgr(
          ^^^^^^^^^^^^^^^
  File "/home/shaha4/miniforge3/envs/rapids-24.12-stable/lib/python3.11/site-packages/pandas …

**@abs51295:** also, this might sound like a stupid question but is using this method equivalent to getting generated counts from `sample_posterior`?

```python

 sample_quantile = 'post_sample_q25'

 samples_corr = resolvae.sample_posterior(
                   model=resolvae.module.model_corrected,
                   return_sites=['px_rate', 'obs'],
                   num_samples=30, return_samples=False, batch_size=6000)

samples_corr = pd.DataFrame(samples_corr).T

 adata.layers["generated_expression"] = scp.csr_matrix(samples_corr.loc[sample_quantile, 'obs'])```

**@canergen:** Yes it is the same, if you set return_samples and use the samples. It's not exactly the same as sample_posterior as this function computes summary statistics in addition. As per the issue, I'm working on fixing it.

## #3289: RESOLVI RuntimeError: dtype mismatch when dispersion set to "gene-batch"
**Issue:** #3289 | **Last activity:** 2025-05-08T11:46:12Z
**State:** closed | **Author:** @tsvvas | **Comments:** 1 | **Created:** 2025-04-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3289

Hi team,

I'm running into a PyTorch dtype mismatch error when training the RESOLVI model. The traceback suggests a matrix multiplication is being attempted between a LongTensor and a FloatTensor.

```python
params = {
        "n_hidden": 32,
        "dropout_rate": 0.05,
        "dispersion": "gene-batch",
        "downsample_counts": False,
    }

scvi.external.RESOLVI.setup_anndata(
    adata,
    layer=LAYER_KEY,
    batch_key=BATCH_KEY,
    prepare_data_kwargs={"spatial_rep": "spatial"},
)
model = scvi.external.RESOLVI(adata, **params)
model.to_device(device)

model.train(**train_params)
```

The final and most important part of the error is:

```pytb
File /opt/conda/envs/spatial/lib/python3.11/site-packages/scvi/external/resolvi/_module.py:870, in RESOLVAEGuide.forward(self, x, ind_x, library, y, batch_index, cat_covs, x_n, distances_n, n_obs, kl_weight)
    862 px_r_mle = pyro.param(
    863     "px_r_mle",
    864     self.px_r,
    865     constraint=constraints.greater_than(self.eps),
    866     event_dim=len(self.px_r.shape),
    867 )
    869 if self.dispersion == "gene-batch":
--> 870     px_r_inv = F.linear(
    871         torch.nn.functional.one_hot(batch_index.flatten(), self.n_batch), px_r_mle
    872     )
    873 elif self.dispersion == "gene":
    874     px_r_inv = px_r_mle

RuntimeError: expected mat1 and mat2 to have the same dtype, but got: long int != float
```

Proposed solution:

The issue seems to be solved by casting the dtype of the result of ` …

**@canergen:** Yes, this is correct and fix will be pushed latter.

## #3267: RESOLVI error
**Issue:** #3267 | **Last activity:** 2025-05-08T10:56:31Z
**State:** closed | **Author:** @christophechu | **Comments:** 2 | **Created:** 2025-03-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3267

When I want to setup anndata,  it's error. but no error information.
scvi 1.3.0
---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
Cell In[22], line 1
----> 1 scvi.external.RESOLVI.setup_anndata(adata, layer="counts", batch_key="sample",
      2                                     labels_key='coarse_celltype_level2',
      3                                     prepare_data=True,
      4                                     unlabeled_category='Unknown')
      5 model = scvi.external.RESOLVI(adata, n_layers=2, n_latent=30, n_hidden=256, gene_likelihood='zinb', semisupervised=True)
      6 model.train()

File /rsrch8/scratch/genomic_med/tchu1/conda/envs/rapids_singlecell/lib/python3.12/site-packages/scvi/external/resolvi/_model.py:330, in RESOLVI.setup_anndata(cls, adata, layer, batch_key, labels_key, categorical_covariate_keys, prepare_data, prepare_data_kwargs, unlabeled_category, **kwargs)
    328     if prepare_data_kwargs is None:
    329         prepare_data_kwargs = {}
--> 330     RESOLVI._prepare_data(adata, batch_key=batch_key, **prepare_data_kwargs)
    332 anndata_fields = [
    333     LayerField(REGISTRY_KEYS.X_KEY, layer, is_count_data=True),
    334     CategoricalObsField(REGISTRY_KEYS.BATCH_KEY, batch_key),
   (...)
    339     CategoricalJointObsField(REGISTRY_KEYS.CAT_COVS_KEY, categorical_covariate_keys),
    340 ]
    341 adata_manager = AnnDataManager(fields …

**@canergen:** Hi. Potential duplicate of https://github.com/scverse/scvi-tools/issues/3208. Can you verify and close here? I should be able to fix it next week.

**@christophechu:** Thanks. Directly using rapids single cell is more robust. But its a little bit hard to install it.

## #3303: ImportError for fresh install of scvi-tools
**Issue:** #3303 | **Last activity:** 2025-04-30T09:32:01Z
**State:** closed | **Author:** @fbnrst | **Comments:** 4 | **Created:** 2025-04-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3303

<!-- Describe the bug -->

I got an `ImportError` on a fresh install of `scvi-tools 1.3.0`.
The installed `lightning` version was `2.0.4`.
I could fix it by `installing` lightning `2.5.1.post0`.

This happened inside a [Docker container](https://github.com/fbnrst/sequencing-docker-stacks/blob/main/images/singlecell-notebook/Dockerfile) that I was building. In there, I use a complex mamba environment. I did not try to reproduce this in a minimal environment.

<!-- To reproduce -->

```python
import scvi
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/opt/conda/lib/python3.12/site-packages/scvi/__init__.py", line 8, in <module>
      from ._settings import settings
    File "/opt/conda/lib/python3.12/site-packages/scvi/_settings.py", line 9, in <module>
      from lightning.pytorch import seed_everything
    File "/opt/conda/lib/python3.12/site-packages/lightning/__init__.py", line 18, in <module>
      from lightning.app import storage  # noqa: E402
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/opt/conda/lib/python3.12/site-packages/lightning/app/__init__.py", line 24, in <module>
      from lightning.app import components  # noqa: E402, F401
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/opt/conda/lib/python3.12/site-packages/lightning/app/components/__init__.py", line 1, in <module>
      from lightning.app.components.d …

**@ori-kron-wis:** There is no pinning for lightning in SCVI, so it had to do with the "complex mamba environment" that force it to install this version.
Dont think we can/should do anything.

**@fbnrst:** I thought it is pinned to >2.0:
https://github.com/scverse/scvi-tools/blob/fbc35980f1293e24913eb8b5fc6fa9cef98d1077/pyproject.toml#L40

Also, I forgot to link this previous issue:
https://github.com/scverse/scvi-tools/issues/2183

This is why I tried with upgrading lightning.

**@ori-kron-wis:** Yes, I meant no pinning to an old version like 2.0.4 (its from 2 years ago...)

When we write "lightning>=2.0" it will take the newest it can, larger than version 2.0, but given other restrictions in your env, not due to scvi-tools, which are probably caused by other packages in your Mamba env.
You can validate with a fresh environment.

**@fbnrst:** I was not able to reproduce in a fresh environment. So agree, nothing needs to be changed.

## #3253: Unable to run scBasset to integrate scATACseq data
**Issue:** #3253 | **Last activity:** 2025-04-29T07:32:37Z
**State:** closed | **Author:** @alifarhat40 | **Comments:** 11 | **Created:** 2025-03-16 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3253

<!-- Describe the bug -->

[TEXT HERE]

I am unable to run this tutorial here:
https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/scbasset_batch.html#quantifying-integration-performance

especially the code in

```
scvi.data.add_dna_sequence(
    adata,
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
    genome_name="hg19",
    genome_dir="data",
)
adata

I get an error saying:

```
File /mnt/RAID5/miniforge/envs/scvi-env/lib/python3.12/site-packages/scvi/utils/_dependencies.py:24, in dependencies.<locals>.decorator.<locals>.wrapper(*args, **kwargs)
     21 @wraps(fn)
     22 def wrapper(*args, **kwargs):
     23     error_on_missing_dependencies(*modules)
---> 24     return fn(*args, **kwargs)

File /mnt/RAID5/miniforge/envs/scvi-env/lib/python3.12/site-packages/scvi/data/_preprocessing.py:432, in add_dna_sequence(adata, seq_len, genome_name, genome_dir, genome_provider, install_genome, chr_var_key, start_var_key, end_var_key, sequence_varm_key, code_varm_key)
    429     genome_dir = tempdir.name
    431 if install_genome:
--> 432     g = genomepy.install_genome(genome_name, genome_provider, genomes_dir=genome_dir)
    433 else:
    434     g = genomepy.Genome(genome_name, genomes_dir=genome_dir)
...
    873         value,
    874     ),
    875 )

OperationalError: no such column: "size" - should this be a string literal in single-quotes?
```

#### Versions:

I have the most recent versions of anything. I have set up scvi last week wit …

**@ori-kron-wis:** Hello @alifarhat40 ,
I think that there are some issues not exactly with scvi-tools but with the genomepy package itself, and/or its dependencies, as some have not been updated for a long time and still require python 3.9.
My suggestion is to check that on python 3.10 (or even 3.9) and with previous versions of scvi-tools to understand where it breaks. I will try do the same.

**@alifarhat40:** Thanks. I tried several versions of genomepy and scvi, but that part of the code fails.

However, I tried integrating RNA using scvi inside seurat and scvi on its own and it works.

Its just that scBasset is not working, because it needs genomepy. I would love to try to integrate my ATACseq data using it.

**@ori-kron-wis:** Hey @alifarhat40 thanks. That might be exactly what we need to change.
Can you share with us the piece of code from Seurat where you did the integration? We will apply the same for scvi-tools, and drop genomepy.

**@alifarhat40:** Well, scvi for scATACseq integration is different from scRNAseq integration since RNA integration does not need genomepy.

scvi on its own works for other tasks, but it is scBasset that relies on genomepy that is giving problems.

This tutorial here does not work:
https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/scbasset_batch.html#quantifying-integration-performance

at this step it cannot download:

```
scvi.data.add_dna_sequence(
    adata,
    chr_var_key="chr",
    start_var_key="start",
    end_var_key="end",
    genome_name="hg19",
    genome_dir="data",
)
adata
```


integrating scATACseq does not use seurat. I was just saying that I have tried scvi in several other ways for RNAseq that works. But scvi that needs genomepy is giving problems.

If it is just a matter …

**@ori-kron-wis:** Sorry, I thought you meant that you overcame this issue by running something from Seurat.
Yes, we know the issue is with Genomepy and scATACseq integration, and we need to replace its use.

**@ori-kron-wis:** Hey @alifarhat40,
I gave it another try, seems that the only problem I had is with package versions, as genomepy is a bit complicated with this.
This combination of packages worked for me to run scbasset and rest of the add_dna_sequence tests:
Last run with genomepy version: 0.16.1
Last run with biothings_client: 0.4.1
Last run with mygene: 3.2.2
Last run with biopython: 1.85
Last run with mysql version: 9.1.0
Last run with diskcache version: 5.6.3
Last run with scvi-tools version: 1.3.0

You can see the rest of the package versions that made this work here: https://github.com/scverse/scvi-tools/actions/runs/13943969022/job/39026803652

<img width="1272" alt="Image" src="https://github.com/user-attachments/assets/229ee754-8853-4a1c-a76b-e18fc14b4b74" />

**@alifarhat40:** Great. I will look into it. Is there an easy way for me to match all those package versions?

**@alifarhat40:** Hm does not work still.
Actually I have all these package versions:
genomepy version: 0.16.1
biothings_client version: 0.4.1
mygene version: 3.2.2
biopython version: 1.85
diskcache version: 5.6.3
scvi-tools version: 1.3.0
mysql version: 9.1.0

I think it might be something else. Because even doing something as simple as `genomepy search zebrafish` in the linux terminal based on this: [link](https://github.com/vanheeringen-lab/genomepy?tab=readme-ov-file#quick-usage) then I get the same error:
`sqlite3.OperationalError: no such column: "size" - should this be a string literal in single-quotes?`

**@ori-kron-wis:** You can copy paste that list into a requirements.txt and install on a fresh env.
the "size" issue is something else, looks like an sql thing.

**@alifarhat40:** Unfortunately still gives same issue.

**@ori-kron-wis:** Do think it is scvi-tools related? seems to me an issue with running genomepy on your machine.
If its just data, couldn't you get it in another way than the scvi api?

## #3295: Integration Testing CI Test Failure on python 3.12
**Issue:** #3295 | **Last activity:** 2025-04-29T07:20:23Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-04-24 | **URL:** https://github.com/scverse/scvi-tools/issues/3295

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/14631293734) to review. @scverse/anndata

## #3296: Integration Testing CI Test Failure on python 3.11
**Issue:** #3296 | **Last activity:** 2025-04-29T07:20:17Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-04-24 | **URL:** https://github.com/scverse/scvi-tools/issues/3296

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/14631293734) to review. @scverse/anndata

## #3287: ImportError: cannot import name 'REGISTRY_KEYS' from 'scvi._constants'
**Issue:** #3287 | **Last activity:** 2025-04-10T09:00:08Z
**State:** closed | **Author:** @liukeweiaway | **Comments:** 1 | **Created:** 2025-04-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3287

ImportError                               Traceback (most recent call last)
/lustre/home/acct-medfzx/medfzx-lkw/project/single_cell_tutorial_chinese/docs/preprocess/2-5.ipynb Cell 2 in <module>
      [1](vscode-notebook-cell://studio.hpc.sjtu.edu.cn/lustre/home/acct-medfzx/medfzx-lkw/project/single_cell_tutorial_chinese/docs/preprocess/2-5.ipynb#Y121sdnNjb2RlLXJlbW90ZQ%3D%3D?line=0) print('ok')
----> [2](vscode-notebook-cell://studio.hpc.sjtu.edu.cn/lustre/home/acct-medfzx/medfzx-lkw/project/single_cell_tutorial_chinese/docs/preprocess/2-5.ipynb#Y121sdnNjb2RlLXJlbW90ZQ%3D%3D?line=1) import scvi

File ~/miniforge3/envs/singleGpu/lib/python3.12/site-packages/scvi/__init__.py:7, in <module>
      4 import logging
      5 import warnings
----> 7 from ._constants import REGISTRY_KEYS
      8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import

ImportError: cannot import name 'REGISTRY_KEYS' from 'scvi._constants'

**@ori-kron-wis:** its not so clear from what you wrote what are you trying to do.
are you in an interactive session? or under a project (this is the only way you can use relative imports) and what are you running? generally, the init files are using relative locations so they can't be run as is (unless you are in project and defined the source directories).

this will work:
import scvi
from scvi._settings import settings
from scvi._constants import REGISTRY_KEYS

another option is that you have a problem in the environment and installation

## #3278: function to decode latent representations direcly.
**Issue:** #3278 | **Last activity:** 2025-04-04T09:37:28Z
**State:** closed | **Author:** @ivichadriana | **Comments:** 2 | **Created:** 2025-03-26 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3278

**Is your feature request related to a problem? Please describe.**
I think it used to be an earlier version feature to be able to encode-decode count data using get_normalized_expression(use_latent=True). I can't find info or a way to do this. I end up calling the decoder, but get many errors with mismatch library size, parameters, etc.

**Describe the solution you'd like**
Including an option to only pass the given latent space through the decoder, like get_normalized_expression() but not counts to counts, make it latent representation to counts. (like use_latent = True)

**@ori-kron-wis:** it is not implemented.
you will need to run the generative part only over your latent tensor.

you can do something like this (see generic_forward.py):

generative_inputs need to be supported, where:
`generative_inputs.keys() is dict_keys(['z', 'library', 'batch_index', 'y', 'cont_covs', 'cat_covs', 'size_factor'])
`
and z is your latent space which can get extracted from model get_latent_representation (although other things are not mandatory and depends on your modelling)

then,
`generative_outputs = module.generative(**generative_inputs)
`
will give you  "px" the reconstructed counts

then you will need to re scale it to counts. See get_normalized_expression.py
```
px_generative = generative_outputs["px"]
exp_ = px_generative.get_normalized("scale")
```

you might also need to take the …

**@canergen:** Hi, some models support minified models, so it stores the latent codes in obsm of the AnnData and then only calls the decoder on these latent parameters. Similarly, you could hijack this mechanism (if you actually want to do something else like taking random samples from latent space and decode them).

## #3282: Warning Message Related to DOCstring
**Issue:** #3282 | **Last activity:** 2025-04-02T05:13:08Z
**State:** closed | **Author:** @marianogabitto | **Comments:** 1 | **Created:** 2025-04-01 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3282

When I import scvi I get a warning message related to the doctoring. It will be great to remove it.

Code:
import scvi
Output
../python3.12/site-packages/docrep/decorators.py:43: SyntaxWarning: 'param_categorical_covariate_keys' is not a valid key!
  doc = func(self, args[0].__doc__, *args[1:], **kwargs)
../python3.12/site-packages/docrep/decorators.py:43: SyntaxWarning: 'param_continuous_covariate_keys' is not a valid key!
  doc = func(self, args[0].__doc__, *args[1:], **kwargs)

<!-- To reproduce -->


```python
# import scvi
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
../python3.12/site-packages/docrep/decorators.py:43: SyntaxWarning: 'param_categorical_covariate_keys' is not a valid key!
  doc = func(self, args[0].__doc__, *args[1:], **kwargs)
../python3.12/site-packages/docrep/decorators.py:43: SyntaxWarning: 'param_continuous_covariate_keys' is not a valid key!
  doc = func(self, args[0].__doc__, *args[1:], **kwargs)
```

#### Versions:

python 3.12
scvi 1.3.0

**@ori-kron-wis:** it will be removed in the next release.

## #3251: SysVI attributes listed in API don't appear in trained model
**Issue:** #3251 | **Last activity:** 2025-03-24T08:32:49Z
**State:** closed | **Author:** @danieljrichard | **Comments:** 13 | **Created:** 2025-03-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3251

<!-- Describe the bug -->

Hello, I was working through this example for running SysVI:

(https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/sysVI.html)

And tried running get_normalized expression. However, I get this error:
AttributeError: ‘SysVI’ object has no attribute ‘get_normalized_expression’

However, the API indicates this is an attribute:
(https://docs.scvi-tools.org/en/latest/api/reference/scvi.external.SysVI.html#scvi.external.SysVI.get_normalized_expression)

Am I doing something wrong, or do I somehow need to convert this SysVI object to a scvi object?

Any help would be greatly appreciated!
<!-- To reproduce -->

```python
SysVI.setup_anndata(
    adata=adata,
    batch_key="system",
    categorical_covariate_keys=["batch"],
)

model = SysVI(
    adata=adata)
scvi.settings.num_threads = 20
scvi.settings.dl_num_workers = 20

model.train(
    plan_kwargs={
        "kl_weight": 1,
        "z_distance_cycle_weight": 5
        # Add additional parameters, such as number of epochs
    }

normalized_out = model.get_normalized_expression(adata, transform_batch="mouse", library_size = 'latent')

)```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: 'SysVI' object has no attribute 'get_normalized_expression'
```

#### Versions:

<!-- Output of scvi.__version__ -->

> '1.2.0'

<!-- Relevant screenshots -->

**@ori-kron-wis:** It is not implemented yet, you are correct.
It is in the API because of RNAseqMIXIN inheritance, but the function is not working out of the box.

We will fix it.

**@danieljrichard:** Thanks for the update - much appreciated!
In the meantime, might there be any hints/ways to coerce the model into a scvi-like object to access those attributes, or is it more complicated than I'm imagining?

**@ori-kron-wis:** @danieljrichard We fixed this, and can be used from the main branch.
It will take us a few more weeks to release it as a version.

**@danieljrichard:** Fantastic - thank you so very much for doing this, it's truly appreciated!

**@Hrovatin:** Hi @ori-kron-wis  @danieljrichard, sorry for the late reply. - I sometimes run out of time for SysVI as it is not part of my current position.

We did not implement normalised expression access on purpose. I personally do not believe that people should use it. I would always recommend a.) working with raw counts and appropriate statical test that accounts for batch covariates or b.) performing DE per batch and then combining the DE results from individual batches. There a few issues of working with corrected expression:
- It will always contain some artifacts, which are also not well understood.
- It is available only for the HVG subset.
- If you can not design a meaningful DE test with classical statistical approaches (or if it does not work for whatever reason) then I would be sceptical …

**@ori-kron-wis:** @Hrovatin its fine. We can easily add the NotImlementedError for a local implementation of get_normalized_expression in sysvi.
If you will look at the PR that fixed that its mainly generic stuff that were missing (https://github.com/scverse/scvi-tools/pull/3260/files), and as a result the model now inherits get_normalized_expression from the rnamixin.

I did not see a NotImlementedError in the previous SYSVI, so we thought it was missing.  Eventually Can and I decided to have it for the sake API consistency, as this issue is about this.

As said, the proper way to disable it is to strictly add a get_normalized_expression implementation for sysvi with a NotImlementedError.

**@Hrovatin:** Hi, sorry for looking at the PR too briefly and misinterpreting what was done.
I though I had  `NotImlementedError ` in at some point in SysVI, but maybe we decided for a different solution at the time. I know I added this test which I thought would help: https://github.com/Hrovatin/scvi-tools/blob/6a2e3ebd1d331350ea31c8e0a0fe72a0294502cf/tests/external/sysvi/test_sysvi.py#L206

Then lets to the suggested:
> As said, the proper way to disable it is to strictly add a get_normalized_expression implementation for sysvi with a NotImlementedError.

**@canergen:** For consistency it is there. I told you in our first discussion that it will likely be added after merging and we took over maintenance as this is one of the purposes of a consistent API - if a model is generative we have an API to generate counts.
I agree with you that generated expression should generally be used carefully and there is some overuse, which is part of the posterior predictive checks in scVI-criticism and can now be also executed on sysVI outputs. Part of these tests is to check for reproducibility of DE results on these generated counts.

**@Hrovatin:** Ok fair point. Then I would suggest adding the explanation warning against misuse to the tutorial and the API docs. Would that be ok?

**@canergen:** We are working on our tutorials currently. I think this is a general issue that we should address and highlight better that researchers need to better validate its use for each trained model. Models with good latent spaces can be pretty bad in generating and vice versa. Currently most users validate their latent space but not their generated counts.

**@Hrovatin:** Great. Then this should be no longer an issue for SysVI, if you add that as a general guideline.

**@danieljrichard:** Hello - just to follow up on this discussion. I was planning on training the SysVI model on scRNA and snRNA (from the same tissue), then using the normalized-expression for the snRNA (with scRNA as the reference batch) as input into a previously-published scRNA single-cell clock. Not planned to do anything like DE analysis (for which I know normalized counts are discouraged).
Would something like this be reasonable, or would you just generally recommend never using the normalized counts from SysVI (as recently implemented - thanks!) for anything?

**@Hrovatin:** @danieljrichard I never properly evaluated the decoded counts so I can not guarantee they would behave. While they can be used in the cycle-consitency pass to get a similar embedding to the other batch/system, this does not guarantees taht your classifier would be able to give a reliable prediction with them. Of course, it may work, but I would not dare to say it is definitely going to work and you would need to evaluate whether the result makes sense.

If your scRNA and snRNA data cover the same "space" (e.g. the whole clock trajectory) what may be an alternative is to use the clock to predict scRNA data and then use the integrated embedding to transfer the annotation to snRNA data (e.g. with nearest-neighbour classifier) - similar as you would usually do with cell types. As with any inte …

## #3263: ```ModuleNotFoundError: No module named 'dask._task_spec'``` when running ```scvi.external.RESOLVI.setup_anndata```
**Issue:** #3263 | **Last activity:** 2025-03-20T20:43:51Z
**State:** closed | **Author:** @ashx56 | **Comments:** 7 | **Created:** 2025-03-20 | **URL:** https://github.com/scverse/scvi-tools/issues/3263

Hi,

I encounter the following error when trying to run RESOLVI's setup: ``` ModuleNotFoundError: No module named 'dask._task_spec' ```

This error occurs when executing ```scvi.external.RESOLVI.setup_anndata(ref_adata, layer="counts")``` even though I have installed scvi-tools and dask in my environment following exactly the instructions in the tutorial.

Any help would be appreciated.
Thanks!
Ashish

**@canergen:** Hi, can you paste the complete error message?

Thanks!

**@ashx56:** Absolutely, here it is! I'm running this on Colab if that makes a difference.

```---------------------------------------------------------------------------
ModuleNotFoundError                       Traceback (most recent call last)
[<ipython-input-7-23015a10eaef>](https://localhost:8080/#) in <cell line: 0>()
----> 1 scvi.external.RESOLVI.setup_anndata(ref_adata, layer = 'counts')

16 frames
[/usr/local/lib/python3.11/dist-packages/scvi/external/resolvi/_model.py](https://localhost:8080/#) in setup_anndata(cls, adata, layer, batch_key, labels_key, categorical_covariate_keys, prepare_data, prepare_data_kwargs, unlabeled_category, **kwargs)
    328             if prepare_data_kwargs is None:
    329                 prepare_data_kwargs = {}
--> 330             RESOLVI._prepare_data(adata, b …

**@canergen:** Hi, apparently you can't run sc.pp.neighbors on your object. From the error message, I assume you can't even import dask_cudf. I would highly suggest to not use dask for the AnnData object as input to RESOLVI. The issue should be solved then.

**@ashx56:** Thank you for explaining the error. However, I'm not exactly sure where in my pipeline I'm using dask for my AnnData object. I am reading the object using the standard ```scanpy.read_h5ad```. The object itself is a binned dataset of originally Visium HD spatial sequencing data, which is why I am using RESOLVI to remove noise.

**@canergen:** Can you try calling:
`from cuml.neighbors import NearestNeighbors` directly, which is currently the line creating an import error. It points to issues with your cuml installation (likely incompatible version of cudf and dask.

**@ashx56:** I just tried that, and now I get the same error at the import step itself. I think you're right, it's a compatibility issue. Do you have any recommended solution? I'm posted the full error message again if that helps!

```ModuleNotFoundError                       Traceback (most recent call last)
[<ipython-input-2-67aa95eed6ed>](https://localhost:8080/#) in <cell line: 0>()
      8 import scvi
      9
---> 10 from cuml.neighbors import NearestNeighbors
     11
     12 sc.set_figure_params(figsize=(8, 8))

10 frames
[/usr/local/lib/python3.11/dist-packages/cuml/__init__.py](https://localhost:8080/#) in <module>
     25     del libcuml
     26
---> 27 from cuml.internals.base import Base, UniversalBase
     28 from cuml.internals.available_devices import is_cuda_available
     29

[/usr/ …

**@canergen:** Either don’t install cuml and use a CPU NN method from scanpy or follow the installation guideline from rapidssinglecell and then install scvi-tools in this environment: https://rapids-singlecell.readthedocs.io/en/latest/Installation.html

## #3240: DestVI: how to load a DestVI model that was saved as a pickle
**Issue:** #3240 | **Last activity:** 2025-03-09T13:45:34Z
**State:** closed | **Author:** @jliu678 | **Comments:** 2 | **Created:** 2025-03-06 | **URL:** https://github.com/scverse/scvi-tools/issues/3240

Hi scvi team,

DestVI model was saved as a pickle as below:

```
DestVI.setup_anndata(st_adata, layer="counts")
st_model = DestVI.from_rna_model(st_adata, sc_model)
st_model.view_anndata_setup()
st_model.train(max_epochs=2500)

with open("st_model.pkl", "wb") as f:
    pickle.dump(st_model, f)
```

And error is
 ```
Traceback (most recent call last):
  File "/data/wanglab_mgberis/UT_scRNAseq/./cuda_to_cpu.py", line 39, in <module>
    st_adata.obsm["proportions"] = st_model.get_proportions()
  File "/usr/local/lib/python3.10/dist-packages/scvi/model/_destvi.py", line 198, in get_proportions
    stdl = self._make_data_loader(adata=self.adata, indices=indices, batch_size=batch_size)
  File "/usr/local/lib/python3.10/dist-packages/scvi/model/base/_base_model.py", line 431, in _make_data_loader
    raise AssertionError(
AssertionError: AnnDataManager not found. Call `self._validate_anndata` prior to calling this function.
```
when i tried to load it to proceed downstream analysis as blow.

```
print('.1')
import pickle
with open("st_adata.pkl", "rb") as f:
    st_adata = pickle.load(f)

with open("sc_model.pkl", "rb") as f:
    sc_model = pickle.load(f)

print(sc_model)

DestVI.setup_anndata(st_adata, layer="counts")
st_model = DestVI.from_rna_model(st_adata, sc_model)
st_model.view_anndata_setup()

with open("st_model.pkl", "rb") as f:
    st_model = pickle.load(f)

print('.2')
st_model._validate_anndata(st_adata)

print('.3')
st_adata.obsm["proportions"] = st_model.get_pro …

**@jliu678:** I re-train it and save using below codes:
```
import tempfile
import destvi_utils
import matplotlib.pyplot as plt
import numpy as np
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.model import CondSCVI, DestVI
torch.set_float32_matmul_precision("high")
import pickle
with open("st_adata.pkl", "rb") as f:
    st_adata = pickle.load(f)
with open("sc_model.pkl", "rb") as f:
    sc_model = pickle.load(f)
print(sc_model)
DestVI.setup_anndata(st_adata, layer="counts")
st_model = DestVI.from_rna_model(st_adata, sc_model)
st_model.view_anndata_setup()
st_model.train(max_epochs=2500)
print('Saving a model')
st_model.save("st_model.pt")
```
but scvi.model.DestVI.load still cannot load the model. Code and err msg shown below:
```
import pickle;
with open("st_adata.pkl", " …

**@ori-kron-wis:** answered in discourse

## #3223: Error when assigning train_size=1.0 to a scVI/scANVI model.
**Issue:** #3223 | **Last activity:** 2025-02-28T15:40:52Z
**State:** closed | **Author:** @deontaepharr | **Comments:** 2 | **Created:** 2025-02-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3223

<!-- Describe the bug -->


I am trying to train a scVI + scANVI model with training size = 1.0 but continue to get met with error:
TypeError: An invalid dataloader was returned from `DataSplitter.val_dataloader()`. Found None.

I have to use a workaround of train_size=0.99 but that isn't okay to continue using.

Using version 1.2.2
Python 3.11.7

<!-- To reproduce -->

```python
scvi_model = scvi.model.SCVI(adata,
                             n_hidden=n_hidden,
                             n_layers=n_layers,
                             n_latent=n_latent,
                             dropout_rate=0.5,
                             gene_likelihood="zinb")

scvi_model.train(shuffle_set_split=True,
                 batch_size=batch_size,
                 train_size=1.0,
                 max_epochs=scvi_max_epochs,
                 early_stopping=True)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Traceback (most recent call last):
  File "scIntegration.py", line 42, in <module>
    scvi_model.train(shuffle_set_split=True,
  File "/.local/lib/python3.11/site-packages/scvi/model/base/_training_mixin.py", line 145, in train
    return runner()
           ^^^^^^^^
  File "/.local/lib/python3.11/site-packages/scvi/train/_trainrunner.py", line 96, in __call__
    self.trainer.fit(self.training_plan, self.data_splitter)
  File "/.local/lib/python3.11/site-packages/scvi/train/_trainer.py", line 201, in fit
    super().fit(*ar …

**@ori-kron-wis:** Hey, Train size==1.0 means theres no validation set, however, you also used early_stopping=True, which by default use the elbo_validation metric, but here theres no validaiton, hence the bug.
Could you run with early_stopping=False, change your early_stopping metric or train_size?

Either way, I agree this is something we need to take better care with an error message.

**@deontaepharr:** That makes sense. I have changed early stopping to false and it works! Thank you!

## #2541: Consider adding tensor/array shape annotations with jaxtyping
**Issue:** #2541 | **Last activity:** 2025-02-27T08:32:03Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-21 | **Labels:** backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2541

See #2496

## #2256: Using torch.compile in Pyro models
**Issue:** #2256 | **Last activity:** 2025-02-27T08:31:34Z
**State:** closed | **Author:** @vitkl | **Comments:** 11 | **Created:** 2023-09-05 | **Labels:** enhancement, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2256

Hi @adamgayoso and others (also cc @fritzo, @martinjankowiak @eb8680)

It would be great if the new `torch.compile` function could be used with the Pyro model and guide in scvi-tools.

I am happy to contribute this functionality, however, I need your recommendations on what to do with the following problem. Suppose we create add `torch.compile` as shown below:

```python
class MyBaseModule(PyroBaseModuleClass):
    def __init__(
        self,
        model,
        guide_class,  # such as AutoNormalMessenger
        **kwargs,
    ):
        """
        Module class which defines AutoGuide given model.
        """
        super().__init__()
        self.hist = []

        _model = model(**kwargs)
        self._model = torch.compile(_model)
        _guide = guide_class(**guide_kwargs)
        self._guide = torch.compile(_guide)
```

The problem is that Pyro creates guide parameters when they are first needed - requiring these callbacks https://github.com/scverse/scvi-tools/blob/a210867bf54c43283e14b553cff473ba2c7080c5/scvi/model/base/_pyromixin.py#L19-L71. My understanding is that this means that `torch.compile(_guide)` should similarly be called only after the parameters are created.

I see one solution to this. Run the following code https://github.com/scverse/scvi-tools/blob/a210867bf54c43283e14b553cff473ba2c7080c5/scvi/model/base/_pyromixin.py#L65-L71 in `model.train()` manually without using a callback after creating data loaders but before cr …

**@canergen:** Hi @vitkl,
What's the purpose of the request?
In our hands, speed-up was not reproducibly high. Have you made other experience?
We see larger speed-up using JAX, so if it's about speed rewriting in numpyro should be the best option.

**@vitkl:** The purpose is to enable general support for Pyro scvi-tools models. It is possible that some models benefit from this more than other models but it's good to have this option. Pyro adds additional challenges to using `torch.compile` (as mentioned above) - so I was not able to try using `torch.compile` without additional input on how to solve those issues. Once, I understand how to implement this, I will test this for cell2location and other unpublished models which both use all GPU memory (incl multi-GPU) as opposed to scVI which mostly uses a few GB.

Re-implementation of models in numpyro is not always practical because i) numpyro doesn't cover all functionality and because ii) we observed in the past that JAX uses 2-4x of GPU memory for the same data size -meaning> less practical to …

**@canergen:** I agree that speed-up is expected to be largely model-dependent and that scVI is small and might be a bad proxy. Adam and Martin experimented with torch.compile, however, only in the pytorch models. I would expect it's more straightforward to train the model/guide for one step (similar to our current load procedure)  https://github.com/scverse/scvi-tools/blob/4965279f9606216dffaa45f851e1d1ae7c886879/scvi/module/base/_base_module.py#L388. Afterwards the guide can be compiled.

**@vitkl:** Do you suggest to modify `model.train()` as shown below?

```python
self.module.on_load(self)
self.module._model = torch.compile(self.module.model)
self.module._guide = torch.compile(self.module.guide)
```

Are `self.module.model` and `self.module.guide` modifyable as shown here?

**@vitkl:** As a proxy for compilation effect on cell2location, I can mention that our old theano+pymc3 implementation was 2-4 times faster for the same number of training steps. Would be great to see what happens here. A 2-4x speedup would be really nice.

**@canergen:** I tried it out on my side and got some cryptic error messages (it was on a private repo with a not published model though). My idea was to call self.train(max_steps=1) once and afterwards compile. So using the guide warmup by running a single train step. I'm happy to review if you have a PR.

**@vitkl:** I will try your suggestion. Do I get this right that you suggest to

```python
def train(self, ...):

    self.train(..., max_steps=1)
    self.module._model = torch.compile(self.module.model)
    self.module._guide = torch.compile(self.module.guide)
    self.train(...)

```
?

**@canergen:** Yes, that's my understanding of how we do guide warmups for Pyro (e.g. during loading a trained model). I don't think pyro.clear_param_store() is necessary here.

**@vitkl:** This is a good point. I will test this. Lets see what happens with cell2location.

**@vitkl:** Looks like `torch.compile` works for cell2location using the modified train method below. Code runs but there is no speed benefit (5h12min with, 5h25min without, using `torch.set_float32_matmul_precision('high')` on A100 is more impactful -> 4h45min).

```python
def MyModelClass(PyroSampleMixin, PyroSviTrainMixin, BaseModelClass):
    def train_compiled(self, **kwargs):
        import torch
        self.train(**kwargs, max_steps=1)
        self.module._model = torch.compile(self.module.model)
        self.module._guide = torch.compile(self.module.guide)
        self.train(**kwargs)
```

The model and guide are successfully replaced:
```
LocationModelLinearDependentWMultiExperimentLocationBackgroundNormLevelGeneAlphaPyroModel(
  (dropout): Dropout(p=0.0, inplace=False)
)
Au …

**@canergen:** Supported in scvi-tools 1.3.

## #1801: Posterior sampling with Messenger Pyro guides -> huge memory use.
**Issue:** #1801 | **Last activity:** 2025-02-27T08:27:22Z
**State:** closed | **Author:** @vitkl | **Comments:** 6 | **Created:** 2022-11-21 | **Labels:** bug, pyro, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1801

Hi

Posterior sampling with Messenger Pyro guides does not remove observed variables leading to huge memory use.
https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_pyromixin.py#L184
I don't know whether when sampling from Messenger guides it is possible to easily detect and exclude observed variables. @fritzo any recommendations?

This can be addressed
1. By adding an additional variable which allows users to exclude observed variables by name (like done here https://github.com/BayraktarLab/cell2location/blob/improved_posterior_quantile/cell2location/models/base/_pyro_mixin.py#L250).
2. By deleting https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_pyromixin.py#L182-L185

Related to https://github.com/BayraktarLab/cell2location/pull/144/

**@fritzo:** Hi @vitkl, Could you provide more details about the memory leak?  Does memory use happen during training/inference or during prediction?  Where are the observed data being saved?  Are you `poutine.trace`ing the guide or somehow saving sample statements beyond the invocation of a single `.guide()`?  Could you point to some places in the code where the problem occurs?

EDIT to clarify this bug, is it an issue with prediction in `.median()` and `.quantiles()`, or is it an issue with the usual training method `.__call__()`?

**@vitkl:** The goal of this function is to generate samples from the posterior, however, the same problem exists with `.median()` and `.quantiles()`.

This is not really a memory leak (GPU memory use doesn't increase with time). It's simply that
```
if isinstance(self.module.guide, poutine.messenger.Messenger):
            # This already includes trace-replay behavior.
            sample = self.module.guide(*args, **kwargs)
```
returns all sites including observed sites. For gene expression data, that means returning the densified count matrix n_samples number of times. That's a huge matrix. During training, the model obviously needs to compute the likelihood of this data and that's not a problem because of minibatch training and because during training only one sample is generated. However, …

**@canergen:** To add my "solution" to this which uses infer.Predictive and checks once that the variable is on a per cell basis and not a global parameter. It records all samples. I am not sure what problem there is with `.median()`

        adata = self._validate_anndata(adata)
        train_dl = self._make_data_loader(
            adata=adata, indices=indices, shuffle=False, batch_size=batch_size
        )

        self.to_device(device)
        model = model if model else self.module.model

        # sample local parameters
        for tensor_dict in track(
            train_dl,
            style="tqdm",
            description="Sampling local variables, batch: ",
        ):
            args, kwargs = self.module._get_fn_args_from_batch(tensor_dict)
            args = [a.to(device) f …

**@vitkl:** The code in scvi-tools already checks which variables are in minibatch plate and aggregates minibatched variables along the correct dimensions in https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_pyromixin.py#L357-L409. This code also copies each sample to CPU to avoid keeping 1000 samples on GPU:  https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_pyromixin.py#L210 .

You code assumes that presence of a plate means that this variable is minibatched and assumes -1 dimension. The code above implements a more general solution that checks plate name and fetches dimension.

I don't see how your code solves the problem of not saving observed variables. Does `infer.Predictive` return only unobserved variables?

When I was implementing this @martinjankowiak recommende …

**@vitkl:** There is an additional bug: `_get_obs_plate_sites` correctly excludes observed variables from its list of obs_plate_sites - which means that observed sites are treated as global variables. This might explain why memory use increased from 3.8GB to 40GB rather than >> 40GB. Created a PR to fix both issues: https://github.com/scverse/scvi-tools/pull/1805

**@canergen:** adressed in https://github.com/scverse/scvi-tools/pull/3144

## #1718: scvi-tools Jax support
**Issue:** #1718 | **Last activity:** 2025-02-27T08:25:25Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 3 | **Created:** 2022-10-06 | **Labels:** enhancement, new model, meta, jax, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1718

This issue will serve as a parent thread for all issues related to supporting Jax-backend for scvi-tools models.

- [x] `FCLayers` analog #1620
- [ ] `PeakVI` implementation #1578
- [ ] Granular device management #1553
- [x] Default Jax seed #1584

**@martinkim0:** I think in the long term, it would be useful if our high-level API is framework-agnostic. Something like the following:
```
model = scvi.model.SCVI(adata, backend="jax")
```
or
```
model = scvi.model.SCVI(adata, backend="torch")
```

**@adamgayoso:** > I think in the long term, it would be useful if our high-level API is framework-agnostic

We thought about this but it requires matching features exactly, which might be hard. But we should continue to evaluate this option.

**@martinkim0:** > We thought about this but it requires matching features exactly, which might be hard. But we should continue to evaluate this option.

Oh I see, yeah in that case we can revisit this when more code is implemented.

## #2175: Multi-GPU support tracker
**Issue:** #2175 | **Last activity:** 2025-02-27T08:25:02Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-07-10 | **Labels:** enhancement, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2175

- [x] Batch distributed sampler for efficient distributed sparse batching #2102
- [ ] Jax multi-device with `pmap`
- [x] Multi-device flag in pytest
- [ ] Integrate with Lightning CI for Azure GPU resources #1314

## #1578: Implementation of PeakVI in Jax
**Issue:** #1578 | **Last activity:** 2025-02-27T08:23:40Z
**State:** closed | **Author:** @justjhong | **Comments:** 0 | **Created:** 2022-06-23 | **Labels:** new model, jax, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1578

Reimplementation of PeakVI in Jax. This is meant to both see if we can get a similar speed up in PeakVI, as well as understanding the limitations of the `JaxModuleWrapper` abstraction.

## #2364: multi-GPU vs. single GPU - scvi 1.1.x branch
**Issue:** #2364 | **Last activity:** 2025-02-27T08:22:49Z
**State:** closed | **Author:** @zhenxingjian | **Comments:** 4 | **Created:** 2023-12-08 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2364

I've successfully installed the scvi==1.1.x (main branch) and tested that I can train the model on 1 GPU.
However, when using multi-GPU, here's the error I'm facing at.

Batch_size = 512.
for 1 GPU:
x.shape = (512, 1178)
for 2 GPUs:
x.shape = (1, 512, 1178)

This causes almost everything cannot run in the code due to the dimension mismatch.
For example, one_hot function or FCLayers.

Do you have a quick fix for this or I should manually change everything of the dimension in the code (maybe x.squeeze(0) in the outer-most nn.Module) to match it?

**@martinkim0:** Hi @zhenxingjian, what model are you using for this? I'll note that we have only tested multi-GPU training on scVI.

**@canergen:** Hi @martinkim0 scVI is working with multiple samples (like n_samples_per_mc_run). Those look similar like the multi-GPU structure (n_samples, n_batch, n_genes). Quite some other functions like scANVI are not handling n_samples correctly (dimension errors). It's major work to adapt this. I was so confused by it today and made scANVI instead work with n_samples=1.

**@zhenxingjian:** > Hi @zhenxingjian, what model are you using for this? I'll note that we have only tested multi-GPU training on scVI.

I'm following the setup of multiVI.
If you've tested that scVI is working with multi-GPU training, I can try to modify the code following the same setup in scVI from my end to see if it can support multi-GPU training.

**@canergen:** Improved support is available in scvi-tools 1.3 (current main), see also our user guide on multi-GPU training.

## #2383: Adding cycle consistency loss and VampPrior to scVI
**Issue:** #2383 | **Last activity:** 2025-02-27T08:21:20Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 23 | **Created:** 2024-01-09 | **Labels:** enhancement, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2383

We were considering adding cycle-consistency loss and VampPrior as described in [Integrating single-cell RNA-seq datasets with substantial batch effects | bioRxiv](https://www.biorxiv.org/content/10.1101/2023.11.03.565463v1)) to scvi-tools package, preferably directly into scVI.

The current implementation is based on a cVAE that works with normalized+log transformed data: https://github.com/theislab/cross_system_integration/blob/main/cross_system_integration/model/_xxjointmodel.py

Adding VampPrior would require changes in Model to initialise VampPrior pseudoinputs https://github.com/theislab/cross_system_integration/blob/322549224cddcd5d375f8b49cb9f0e0e77c2be1f/cross_system_integration/model/_xxjointmodel.py#L87C10-L87C10 and in module to replace prior: https://github.com/theislab/cross_system_integration/blob/322549224cddcd5d375f8b49cb9f0e0e77c2be1f/cross_system_integration/module/_xxjointmodule.py#L165C11-L165C11

Adding cycle consistency would require changes in adata setup to specify which batch covariate should be used as the "system" that is specifically corrected for with Lcyc - we specify systems and batches within systems (not corrected by Lcyc) for which batch_key and categorical/continous_covariate_keys could be used respectively. Besides, changes in the forward pass and an additional loss would need to be added, see this file: https://github.com/theislab/cross_system_integration/blob/multiple_sys_model/cross_system_integration/module/_xxjointmodule.py#L235 …

**@martinkim0:** Hi, thanks for this suggestion. I think adding these changes would be a great addition to the codebase. However, for now I am opposed to adding them to the scVI model directly for two reasons:

1. Backward compatibility: We can't change the defaults in the scVI model due to compatibility and reproducibility with previous versions of scvi-tools
2. Visibility: If your goal is to increase visibility for the publication, then it's more beneficial to implement and announce this as a new model under `scvi.external`

What do you think? Are you interested in contributing code directly or wanted us to add the changes? Either works, but the latter might take a bit longer.

**@Hrovatin:** I was initially thinking that this could be an optional extension of scVI, making both not used by default (via new parameters with defaults being False). The users could then decide to enable it in their new code. I thought this would be much easier for maintenance than adding a new model and would also improve outreach as anyone using scVI could directly test it.

Alternatively, I could also add it as a new model - the current code is anyway based on scvi-tools although with quite some modifications. However, I am not sure that adding a new model would make sense as I will not be able to maintain it in the future and it is directly compatible with scVI anyways.

I can help contribute to some extent as I am familiar with the implementation, but support on your side would also be appre …

**@canergen:** Hi, I really enjoyed reading your preprint. It's interesting to see your good results with CycleConsistencyLoss as it was overintegrating in some examples in our hand (slightly different implementation and this might be the reason). I think CycleConsistencyLoss should be in an external model. It requires major changes to the model and will blow up the code. We currently make sure that external models are compatible with recent code changes. It's not excluded that in the future, external models that are not used after integration into scvi-tools might be depreciated. I don't see this coming before scvi-tools v2.0 though. For VAMPprior, we have MoG priors (similar to VAMP but logits are learnable) in scvi-tools (developed for MrVI) but used in several unpublished new scvi-tools models. Addin …

**@Hrovatin:** Agreed that cycle consistency adds quite an overhead. Will probably proceed with making it external then, making minimal adaptations to make it compatible with the latest scvi version. We can then later discuss if some code needs to be improved to reduce repetition etc.

For us using an appropriate distance in cycle consistency made an important impact - [we tested a few](https://github.com/theislab/cross_system_integration/blob/322549224cddcd5d375f8b49cb9f0e0e77c2be1f/cross_system_integration/module/_xxjointmodule.py#L489). - What was different in your implementation?

For priors, I already have [an implementation like you suggest](https://github.com/theislab/cross_system_integration/blob/main/cross_system_integration/module/_priors.py) (for standard normal, Vamp, and GMM), although s …

**@Hrovatin:** @canergen I now added the model [here](https://github.com/Hrovatin/scvi-tools/tree/main/scvi/external/csi).
I still need to make a tutorial and make sure that the integration still looks ok after re-implementation (for now I only did basic tests that it runs).
After I add the tutorial should I just open a PR or is there you want me to already adapt before?

Also, for the tutorial if I have a small data object (38.2 MB). - Where should it be stored? In scvi/external/mypackage/data/?
And where in the tutorials folder would you suggest me to put the tutorial? In scRNA-seq?

**@canergen:** @PierreBoyeau used cycle consistency loss in our hands, do you see substantial differences to our trials?
In which cases do you recommend GMM over VAMP?
@martinkim0 Can you review the code? I would suggest to have the function to multiple priors in the CycleConsistency external model and then we can port it to the other scVI models from there. Does it sound reasonable to you?

**@Hrovatin:** @martinkim0 I was also asked to add existing scArches functionality (probably from ArchesMixin) into my model. Would this be currently even possible given that my covariate structure is so different?

**@martinkim0:** @Hrovatin For scArches, compatibility mostly depends on how you register covariates with `AnnDataManager` as well as the names of the base neural net components used in the model. Feel free to open a PR from your fork, and I can take a look/review. You can also add tests to preliminarily see if scArches works out-of-the-box with your model.

@canergen Sounds good, we can keep the priors code in external for now.

**@Hrovatin:** In that case I assume it will not be compatible - are you planing to extend scArches to be more flexible wrt covariates?

I now also made the PR and added a tutorial here: https://github.com/scverse/scvi-tutorials/pull/212

**@Hrovatin:** We will be hopefully re-submitting our manuscript next week. Is it ok if we write that we added our model to scvi-tools external and it is still under review?

**@martinkim0:** Sorry for the late response. Totally fine with me, please go ahead!

**@Hrovatin:** I was wondering when the PR for the code & the tutorial could be merged? - I have a talk about this work at M2D2 series from Valence labs/MILA next Tuesday and it would be great if I could provide links to the scvi-tools repo rather than my fork.

**@canergen:** Hi, to do some expectation management. The code will be part of a stable relese with version 1.2. We are currently finishing version 1.1. Timeline for version 1.2 is on the order of 4 months. This timeline is long as we for example work with precommits to make sure every change works within the scverse ecosystem.
I would recommend using the branch for reproducibility purposes or the original repository before version 1.2 is released even after the branch is merged into main. We will not merge it into main before version 1.1 is released.

**@martinkim0:** @Hrovatin Sorry for the delay in reviewing - I've taken another pass at it now. I think we'll need to add a couple more changes and trim down code where needed before merging into main. We can try our best to get it in before Tuesday, but no promises. In terms of linking to the scvi-tools repo, feel free to reference the PR.

**@Hrovatin:** Thank you for letting me know - I just wanted to make sure to share a link version that is not on my own fork which will not be maintained in the future. I will then add links to the PR if we cant merge into main beforehand.

**@moinfar:** @martinkim0
Hi,
I am Amir from sysVI project.
Is there any major problem with sysVI that caused you to postpone the sysVI merge to 1.3?
Do you have any estimate on when it will be merged?

**@canergen:** Hi @moinfar and @Hrovatin we're sorry for the long time it takes us to integrate the changes. Unfortunately, we were not able to understand all parts of the code yet (I currently can't review it myself), which makes it difficult to take over maintenance after merging. We are currently restructuring our team (switch in SWE) and have to push this to the latter release. We will update you after another round of reviewing the PR with remaining questions/requests about the structure.

**@Hrovatin:** Dear @canergen do you have any more exact estimates on when the merge will happen? Is this planned in the timeline of weeks or months?
If you have truble understanding the code me or @moinfar can meet up with your team to guide you through.

**@canergen:** Reviewed it now. Numerous comments from the last reviews are not addressed. please try to reduce the amount of new functions and highlight for all functions, why a new implementation is necessary and what part is missing in our implementation (we might add those). Currently, the overhead to maintain this code is large and I/Martin are pretty certain that we can help you to reduce it.

**@canergen:** I don't think understanding is the problem. I was puzzled by two implementation details and requested for citations there as it will make it easier for users in the future to follow the design.

**@Hrovatin:** Thank you. We will look into them and try to resolve them.
@moinfar if you could help here https://github.com/scverse/scvi-tools/pull/2421#pullrequestreview-2262603379

**@Hrovatin:** @canergen It may take us a while to resolve the comments as we are currently working on the paper revision. - Let us know if there are any release dates we should be catching.

**@canergen:** No worries. We will release 1.2 in the coming weeks. 1.3 will be at the end of this year. We could also think about adding the model with a patch release in between.

## #2641: Mixed usage of `n_samples_overall` in `get_normalized_expression`
**Issue:** #2641 | **Last activity:** 2025-02-27T08:20:58Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 2 | **Created:** 2024-04-01 | **Labels:** P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2641

In [`TOTALVI.get_normalized_expression`](https://github.com/scverse/scvi-tools/blob/1.0.x/scvi/model/_totalvi.py#L435), [`MULTIVI.get_normalized_expression`](https://github.com/scverse/scvi-tools/blob/1.0.x/scvi/model/_multivi.py#L657), and [`ContrastiveVI.get_normalized_expression`](https://github.com/scverse/scvi-tools/blob/1.1.x/scvi/external/contrastivevi/_model.py#L385), `n_samples_overall` just downsamples `indices`, while in [`RNASeqMixin.get_normalized_expression`](https://github.com/scverse/scvi-tools/blob/1.1.x/scvi/model/base/_rnamixin.py#L221), it's used for the number of MC inference samples. This might be confusing for users who expect the argument to mean and do the same thing across methods.

**@canergen:** @PierreBoyeau  Currently this means that these other function don't use importance weighting? I assume it would make sense to add it to these models as well?

**@canergen:** I think we can improve the naming as well (but that's styling and I would stick to n_samples_overall for number of mc_samples and n_samples to number of samples for a single input cell in a forward pass.

## #3021: Inconsistency in covariate injection into layer
**Issue:** #3021 | **Last activity:** 2025-02-27T08:19:23Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 4 | **Created:** 2024-10-19 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3021

The FCLayers enable the re-inject of covariates in every layer. However, this is enabled only for categorical cov with one hot encoding. This is now inconsistent with other covariates (continuous, embedded) that get simply concat to the input before being passed to the layers and thus not re-injected.
For SysVI I will make a new Layers class that will directly follow the FCLayers, but will have another input for continuous covariates, so that these can be likewise injected. - You could consider fixing the above inconsistency in scvi-tools in the same way I guess.
@canergen

**@canergen:** @ori-kron-wis can you please fix this? It should behave similarly for all types of covariates.
It needs a legacy load though similarly to the fix in scANVI. Maybe the better option would be deeply_inject=‘all’ and clarify in the documentation the difference.

**@Hrovatin:** Great, then I can just re-use your layers if this will be implemented from your side - for sysVI maybe I will already add an updated Layers version myself so that I can then be more easily switched with your new layers, else the rest of the code would also need to be adapted later

**@Hrovatin:** @ori-kron-wis I added my implementation [here](https://github.com/scverse/scvi-tools/blob/7743c1923913b43d77be23199dbb434ebb64ae59/src/scvi/external/sysvi/_base_components.py#L98) - Maybe you will need to adjust slightly as I changed parameter signature to add the continuous kwarg `(x,cont=None,cat_list=None)` - I think you could change it to `(x,*cat_list,cont=None)` to reduce changes needed in other models.

**@canergen:** Adressed in sysVI merge https://github.com/scverse/scvi-tools/pull/3195

## #3186: scvi.model.SCVI.load error
**Issue:** #3186 | **Last activity:** 2025-02-27T08:13:40Z
**State:** closed | **Author:** @francicco | **Comments:** 2 | **Created:** 2025-02-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3186

Hi,

I'm trying to reload a saved model with the command:
`model.save('Diul_model/')`

This is how I'm trying to load it:
`model = scvi.model.SCVI.load('/Users/tk19812/Documents/scRNA-Project/H5AD_datssets/Diul_model/', adata)`

But I'm getting this error:

```
INFO     File /Users/tk19812/Documents/scRNA-Project/H5AD_datssets/Diul_model/model.pt already downloaded
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[56], line 7
      1 import torch
      3 torch.serialization.add_safe_globals({
      4     'numpy.core.multiarray._reconstruct': __import__('numpy.core.multiarray').core.multiarray._reconstruct
      5 })
----> 7 model = scvi.model.SCVI.load('/Users/tk19812/Documents/scRNA-Project/H5AD_datssets/Diul_model/', adata)

File ~/.pyenv/versions/3.10.12/lib/python3.10/site-packages/scvi/model/base/_base_model.py:699, in BaseModelClass.load(cls, dir_path, adata, accelerator, device, prefix, backup_url)
    686 load_adata = adata is None
    687 _, _, device = parse_device_args(
    688     accelerator=accelerator,
    689     devices=device,
    690     return_device="torch",
    691     validate_single_device=True,
    692 )
    694 (
    695     attr_dict,
    696     var_names,
    697     model_state_dict,
    698     new_adata,
--> 699 ) = _load_saved_files(
    700     dir_path,
    701     load_adata,
    702     map_location=device,
    703     pr …

**@canergen:** Hi, it looks like torch tries to load weights only. This is supposed to be fixed in the most recent versions of scvi-tools. I assume that you use an old version of scvi-tools and the most recent torch version. Can you update scvi-tools to 1.2.2?

**@canergen:** Closed due to inactivity.

## #3205: Unable to install SCVI
**Issue:** #3205 | **Last activity:** 2025-02-27T08:12:56Z
**State:** closed | **Author:** @noah132 | **Comments:** 1 | **Created:** 2025-02-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3205

<!-- Describe the bug -->

I've been trying to install SCVI for a week now with no success. After fixing a series of errors, I've finally gotten stuck.

<!-- To reproduce -->

I've tried installing using both pip in my own python environment and using a conda environment.

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

Using pip, I get this error:
Collecting scvi
  Using cached scvi-0.6.8-py2.py3-none-any.whl.metadata (12 kB)
Requirement already satisfied: numpy>=1.16.2 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (2.1.3)
Requirement already satisfied: torch>=1.3 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (2.6.0)
Requirement already satisfied: matplotlib>=3.1.2 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (3.10.0)
Requirement already satisfied: scikit-learn>=0.20.3 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (1.6.1)
Requirement already satisfied: h5py>=2.9.0 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (3.12.1)
Requirement already satisfied: pandas>=0.25 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (2.2.3)
Requirement already satisfied: tqdm>=4.31.1 in c:\users\kevin\appdata\local\programs\python\python313\lib\site-packages (from scvi) (4.67.1)
Collecting xlrd>=1.2.0 (from scv …

**@ori-kron-wis:** Hey,
I can see you are trying to install for py3.13, which we still not supported. Please use python 3.10-3.12
Also there is most likely some package mixup.

I suggest creating a new env, in linux (or do the same for windows from cli), e.g. for py3.10:

```
conda create --name scvi python=3.10
conda activate scvi
pip install scvi-tools
python
import scvi
```

## #3166: MrVI does not store temporary distance matrices efficiently
**Issue:** #3166 | **Last activity:** 2025-02-24T15:57:53Z
**State:** closed | **Author:** @PierreBoyeau | **Comments:** 1 | **Created:** 2025-01-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3166

MrVI temporarilly represents outputs as xarrays, typed not as numpy arrays, but as Jax arrays. This causes significant memory overhead, especially when computing cell-specific distance matrices for a large number of samples.

**@justjhong:** Resolved in #3146

## #3188: Potential bug in MRVI's get_aggregated_posterior
**Issue:** #3188 | **Last activity:** 2025-02-23T20:03:45Z
**State:** closed | **Author:** @rastogiruchir | **Comments:** 3 | **Created:** 2025-02-13 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3188

The MixtureSameFamily constructed in get_aggregated_posterior computes different log_probs from those I manually compute by iterating over the mixture components. On real datasets, I see that this manual computation shrinks the range of the log_probs calculated under a given sample. Not sure if I'm misunderstanding the intention of get_aggregated_posterior, and I haven't checked in detail why this discrepancy exists.

Here's a small notebook to reproduce: https://colab.research.google.com/drive/1tT8rbLnK5zJqNnZa_Fn5sUpcwNB8Ge90#scrollTo=Zn7z1tEB_zJz.

**@ori-kron-wis:** @PierreBoyeau @justjhong

**@justjhong:** Hey @rastogiruchir , thanks for raising this issue. I believe you are right, this is in fact a bug. I was able to figure out that if you don't indicate the event dimension of the Normal distribution, the mixture family is basically computing the mixture log probs over each dimension instead of over the full log probs.

In more detail:
Bugged version:
$$\log \Pi_{d}^{D} (\frac{\Sigma_{c}^{C} \mathcal{N}( \mu_{dc}, \sigma_{dc})}{C})$$

Correct version:
$$\log (\frac{\Sigma_{c}^{C} \Pi_{d}^{D} \mathcal{N}(\mu_{dc}, \sigma_{dc})}{C})$$

I was able to reproduce the fix you have with the Multivariate distribution using to_event on the original implementation:
```def mixture_of_gaussians_mrvi_to_eventfix(x, qu_locs, qu_scales):
  """Following the code in get_aggregated_posterior and differential …

**@canergen:** Thanks @rastogiruchir. To highlight Justin's suggested solution fixes it in jax: https://colab.research.google.com/drive/1tT8rbLnK5zJqNnZa_Fn5sUpcwNB8Ge90#scrollTo=Zn7z1tEB_zJz.
In addition, it highlights that MoG in torch were already correct. To note, torch.distributions.Normal requires standard deviation while MultiVariateNormal expects covariance matrices.

## #3197: Integration Testing CI Install Failure on python 3.10
**Issue:** #3197 | **Last activity:** 2025-02-23T20:02:19Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-02-21 | **URL:** https://github.com/scverse/scvi-tools/issues/3197

The daily CI failed on install for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/13447876828) to review. @scverse/anndata

## #3201: The availability of 'batch_embedding' branch or similar alternatives
**Issue:** #3201 | **Last activity:** 2025-02-23T20:02:05Z
**State:** closed | **Author:** @noranekonobokkusu | **Comments:** 1 | **Created:** 2025-02-23 | **URL:** https://github.com/scverse/scvi-tools/issues/3201

Hello,

Thank you for such a great tool!
I came across this thesis https://www2.eecs.berkeley.edu/Pubs/TechRpts/2022/EECS-2022-91.pdf which mentions the addition of the 'batch_embedding' branch to the repository, which doesn't exist anymore. I cannot find functionality like `use_batch_embedding` or `get_batchy_genes()` in the documentation and was wondering if it's still available somewhere. I would like to understand which genes are most affected by batch, and this branch sounded very relevant. If it's not available anymore, are there any alternatives in the current version of the package?
Thanks!

**@canergen:** Hi, you can enable using batch embeddings in scVI and other models: https://github.com/scverse/scvi-tools/blob/a9e45bf1404f64d81224fc7df10243679a47e65e/src/scvi/module/_vae.py#L164.
However, interpretability code including plotting is not intended in scvi-tools - I'm not aware of any location this code is still accessible at. You might want to check out scPoli that highlighted the use of batch embeddings though: https://www.nature.com/articles/s41592-023-02035-2. And might want to check out MrVI - our approach to interpretable insights from sample-level batch effects: https://www.biorxiv.org/content/10.1101/2022.10.04.510898v2, while it computes batch embeddings, we found those to perform worse in interpretability and this second latent space.

## #3198: Unable to load human-lung-cell-atlas-scanvi model
**Issue:** #3198 | **Last activity:** 2025-02-21T13:34:20Z
**State:** closed | **Author:** @tpjones15 | **Comments:** 2 | **Created:** 2025-02-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3198

<!-- Describe the bug -->

Hello, When following the tutorial for [Querying the Human Lung Cell Atlas](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/query_hlca_knn.html). I am unable to load the pre-trained scANVI model after successfully downloading from HuggingFace.

<!-- To reproduce -->

```python
import os
import tempfile

import anndata
import numba
import numpy as np
import pandas as pd
import pooch
import pynndescent
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.hub import HubModel
import mygene


scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)

args = parser.parse_args()

save_dir = "mapping_to_HLCA"
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")

# Step 1: Load the AnnData object
query_adata = sc.read_h5ad(args.input)

query_adata.layers["counts"] = query_adata.X.copy()

hubmodel = HubModel.pull_from_huggingface_hub(
    "scvi-tools/human-lung-cell-atlas-scanvi", cache_dir=save_dir
)

adata = hubmodel.adata
model = hubmodel.model
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
>>> model = hubmodel.model
INFO     Loading model...
Trainer will use only 1 of 4 GPUs be …

**@canergen:** Hi, could you update scvi-tools? The most recent version is 1.2.2.post2. I just checked in Colab and it works fine. Specifically, we changed that argument in https://github.com/scverse/scvi-tools/commit/337ec87289660fd6f40241c845e415bef0f200d6.
I will check with the next round of uploads in scvi-tools 1.3.0 that also the HuggingFace tag is correct (falsely reports 1.2.0 as I created the model files in my local modified code of 1.2.0).

**@tpjones15:** Yep, this has fixed it. Thanks very much!

## #3018: Support training from `AnnCollection`
**Issue:** #3018 | **Last activity:** 2025-02-21T10:07:05Z
**State:** closed | **Author:** @jacobkimmel | **Comments:** 4 | **Created:** 2024-10-17 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3018

**Is your feature request related to a problem? Please describe.**

- Currently, `scvi-tools` does not support training from the new `anndata.experimental.AnnCollection` API
- `AnnCollection` is great! For teams training models on large datasets, it's a game changer.

**Describe the solution you'd like**

- Support for training from `AnnCollection` objects through the existing API would be great.
- Ideally, users would not be required to make substantial changes to the existing `scvi-tools` workflow

**Question for maintainers**

- I've implemented a solution that achieves the desired outcome without modifying any existing `scvi-tools` code.
- In brief, I wrote a set of wrappers for `AnnCollection` that mimic the `anndata.AnnData` API in all the ways `scvi-tools` expects. We've successfully trained simple models with this solution.
- In practice, users wrap their collection objects (`wrapped_collection = Wrapper(collection)`) then proceed with the `scvi-tools` workflow as normal (`setup_anndata(wrapped_collection, ...)`, etc.).
- Would the team be interested in incorporating this interface into the main `scvi-tools`? If so, I can send in a PR. I'd imagine it living as a separate module under `.data`.

**@canergen:** Hi, thanks for the suggestion. We are currently looking into supporting MappedCollection from lamindb. However, AnnCollection works with setup_anndata while MappedCollection requires Custom Dataloaders. Do you used AnnCollection in disk-backed mode or are the datasets loaded to memory?
Could you provide the code and we can then discuss within scverse with the AnnData developers how to enable this and how stable AnnCollection is? We could have a similar function to e.g. the organize multiome function in multiVI https://github.com/scverse/scvi-tools/blob/c53efe06379c866e36e549afbb8158a120b82d14/src/scvi/data/_preprocessing.py#L283.

**@jacobkimmel:** > However, AnnCollection works with setup_anndata while MappedCollection requires Custom Dataloaders. Do you used AnnCollection in disk-backed mode or are the datasets loaded to memory?

I set it up to use `AnnCollection` with backed `AnnData` objects. I don't really see an advantage to using `AnnCollection` if everything is in memory anyway -- the overhead of `anndata.concat(...)` is pretty minimal.

Here's a sample snippet of how I created the objects.

```python
# get some data
gdown.download(url="https://drive.google.com/uc?id=1X5N9rOaIqiGxZRyr1fyZ6NpDPeATXoaC",
            output="pbmc_seurat_v4.h5ad", quiet=False)
gdown.download(url="https://drive.google.com/uc?id=1JgaXNwNeoEqX7zJL-jJD3cfXDGurMrq9",
            output="covid_cite.h5ad", quiet=False)

# load in backed
covid = sc.read( …

**@canergen:** Hi Jacob, the current AnnData developers have no plan to continue developing AnnCollection but the idea is to focus on the dask integration. This should handle it similarly. I'm a bit reluctant to built for an experimental feature that is currently not actively developed.
We are still working on MappedCollection support, which is an on-disk concatenation as well.
I hope that these cover your use case. Please reopen if you think it's critical to support AnnCollection over the other two solutions.

**@canergen:** To follow up on it, the MappedCollection release is now production ready (we still need to fix the tests there): https://github.com/scverse/scvi-tools/pull/3193/files. MappedCollection has several advantages over AnnCollection in terms of io but requires setting up a lamindb instance. We will post in the near future a small tutorial using this: test_lamindb_dataloader_scvi_scanvi contains the code to set this up.

## #3145: Adjust MrVI running hyperparameters for 1000s of samples
**Issue:** #3145 | **Last activity:** 2025-02-20T15:44:56Z
**State:** closed | **Author:** @PierreBoyeau | **Comments:** 7 | **Created:** 2025-01-14 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3145

The default execution of MrVI core functions relies on vmap, which fastens execution and increases memory usage.
This memory cost is not sustainable in scenarios with 1000s of samples.
A first step in this direction would be to disable vmap by default. @justjhong @canergen what do you think?

**@justjhong:** I think a majority of users will use defaults without paying attention to arguments like use_vmap. How about we do an automatic change to not use vmap when the number of samples exceeds 1000? Then, we can also display a warning message that we did so if the user didn't explicitly pass in use_vmap=True (e.g., "vmap parallelized execution has been disabled automatically since the number of samples exceeds 1000. If you would still like to use vmap, explicitly pass in use_vmap=True"). To get this behavior we have the default as use_vmap=None and treat this case differently.

**@canergen:** Best case you do a for loop over the array in the vmap dimension of 100 each (not sure there is a pre-specified subset for this thing). Just assume that you also have sped-up for large sample sizes but the speed up likely ceils for some size over vmap.

**@PierreBoyeau:** Thanks for the feedback. I added two things:
1. more informative tracebacks to let users know `use_vmap=False` could fix OOM errors.
2. a change in the default to `use_vmap='auto'` to automatically determine whether vmap makes sense.

@canergen I have tried these batched vmaps in the VIVS code. One problem is that this significantly affects the code readability. I prefer to avoid implementing these strategies, given how packed `_model.py` is. Let me know what you think!

**@canergen:** Sounds reasonable. How long does it take now for 1000 samples and 10k cells?

**@VladimirShitov:** Hey! I hope you don't mind me intervening in this discussion. I am running MrVI on large-scale datasets (700 k - 1.5 Mln cells, hundreds of samples). The method seems to be working nicely, but the scaling makes me very sad. Running `get_local_sample_distances()` often fails even on a powerful compute node (OOM), and the estimated running time is hours to tens of hours.

Do you have any recommendations on how to run the method efficiently?

Also related to https://github.com/scverse/scvi-tools/issues/3166

**@justjhong:** Hi @VladimirShitov, thanks for your comment. We think JAX updates have caused both issues (scaling wrt memory and time). I made an issue for the time scaling issue here https://github.com/scverse/scvi-tools/issues/3179. We will have to figure out how to debug the issue w/ JAX's updates or as a temporary fix pin to an older version of JAX.

**@VladimirShitov:** Thanks @justjhong ! Looking forward to the updates :) Also, lmk if I can help with testing scalability with the datasets I have at hand

## #3194: Integration Testing CI Install Failure on python 3.10
**Issue:** #3194 | **Last activity:** 2025-02-20T11:23:52Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-02-19 | **URL:** https://github.com/scverse/scvi-tools/issues/3194

The daily CI failed on install for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/13403296631) to review. @scverse/anndata

## #3183: Error in import scvi
**Issue:** #3183 | **Last activity:** 2025-02-12T18:15:25Z
**State:** closed | **Author:** @AdotaLover | **Comments:** 2 | **Created:** 2025-02-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3183

hi,i am new to scvi,when i'm trying to reuse it.There is an error in importing scvi
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[1], line 9
      7 import pooch
      8 import scanpy as sc
----> 9 import scvi
     10 import torch

File ~/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/__init__.py:11
      8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import
---> 11 from . import data, model, external, utils
     13 from importlib.metadata import version
     15 package_name = "scvi-tools"

File ~/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/data/__init__.py:26
      5 from ._datasets import (
      6     annotation_simulation,
      7     brainlarge_dataset,
   (...)
     23     synthetic_iid,
     24 )
     25 from ._manager import AnnDataManager, AnnDataManagerValidationCheck
---> 26 from ._preprocessing import (
     27     add_dna_sequence,
     28     organize_cite_seq_10x,
     29     organize_multiome_anndatas,
     30     poisson_gene_selection,
     31     reads_to_fragments,
     32 )
     33 from ._read import read_10x_atac, read_10x_multiome
     35 __all__ = [
     36     "AnnTorchDataset",
     37     "AnnDataManagerValidationCheck",
   (...)
     67     "cellxgene",
     68 ]

File ~/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/data/_preprocessing.py:12 …

**@AdotaLover:** (scanpy) ~# conda list
# packages in environment at /root/miniconda3/envs/scanpy:
#
# Name                    Version                   Build  Channel
_libgcc_mutex             0.1                        main    defaults
_openmp_mutex             5.1                       1_gnu    defaults
absl-py                   2.1.0                    pypi_0    pypi
aiobotocore               2.18.0                   pypi_0    pypi
aiohappyeyeballs          2.3.4                    pypi_0    pypi
aiohttp                   3.10.0                   pypi_0    pypi
aioitertools              0.12.0                   pypi_0    pypi
aiosignal                 1.3.1                    pypi_0    pypi
alabaster                 1.0.0                    pypi_0    pypi
anndata                   0.11.3 …

**@ori-kron-wis:** Hey,
There is most likely some package mixup.
I suggest creating a new env, in linux:
```
conda create --name scvi python=3.10
conda activate scvi
pip install scvi-tools
python
import scvi
```

## #3175: Jupyter kernel crashed when running MrVI's differential_expression function
**Issue:** #3175 | **Last activity:** 2025-02-11T02:41:57Z
**State:** closed | **Author:** @zitiansunshine | **Comments:** 6 | **Created:** 2025-02-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3175

Dear the developers of scvi-tools and MrVI:

Thank you very much for developing this amazing tool. I encountered an error when running MrVI.differential_expression(). I set use_vamp=False as suggested in the other thread, but still the jupyter kernel crashed, and gave the following error ([Canceled future for execute_request message before replies were done]). My dataset has 18 samples and around 6000 cells.  Would you mind looking into this? Thank you very much.

Best,
Andy

<!-- To reproduce -->

```python
sample_key = "PatientID"  # target covariate
batch_key="BatchID"  # nuisance variable identifier
MRVI.setup_anndata(adata, layer="counts",sample_key=sample_key,batch_key=batch_key)
model = MRVI(adata)
model.train(max_epochs=400,accelerator="gpu",devices=1)
sample_cov_keys = ["disease_label"]  # Replace with your sample covariate of interest
de_res = model.differential_expression(
   use_vamp=False,sample_cov_keys=sample_cov_keys,add_batch_specific_offsets=True,store_lfc=True,batch_size=64)
```
```Package version
absl-py                       2.1.0
accelerate                    1.2.1
accumulation_tree             0.6.4
aiobotocore                   2.13.3
aiohttp                       3.9.3
aiohttp-retry                 2.9.1
aioitertools                  0.12.0
aiosignal                     1.3.1
alabaster                     0.7.16
alembic                       1.14.0
amqp                          5.3.1
anndata                       0.11.3
annotated-types               0 …

**@canergen:** Hi, this looks like an out of memory issue. Can you track memory usage in htop/nvidia-smi (more likely GPU memory) and let us know how much memory is available? You are trying to use_vmap (you were writing vamp), this would also reduce memory usage as it reduces parallelization. My other suggestion would be to reduce batch_size further (if GPU memory is the issue or reduce mc_samples in this call): https://github.com/scverse/scvi-tools/blob/2f1611c5d14392fc5b0e7e9706e2b9d80b20e1d5/src/scvi/external/mrvi/_model.py#L1059. If you are out of memory in CPU, you would need to install from: https://github.com/scverse/scvi-tools/pull/3146/commits/e3e5ed61a203d5f2a10389816524097a2df61f12

**@zitiansunshine:** Hi Dr. Ergen,

Thank you very much for your fast response. I really appreciate it.

I tried to install the scvi-tools from the commit you mentioned, and reduced the batch_size and mc_samples.

```{python}
sample_cov_keys = ["disease_label"]  # Replace with your sample covariate of interest
de_res = model.differential_expression(
use_vamp=False,sample_cov_keys=sample_cov_keys,add_batch_specific_offsets=True,store_lfc=True,batch_size=2,mc_sample=20)
```

However, the same problem still happened and the kernel still crashed. My GPU memory size is 80GB, and I requested 196GB RAM on my HPC. The process did not take much GPU memory (~5GB), but the CPU memory is very high (~77GB).

Thank you very much for your help.

<img width="1300" alt="Image" src="https://github.com/user-attachments/assets …

**@canergen:** store_lfc=True requires storing a dense representation of the matrix. Could you retry with disabling this?

**@zitiansunshine:** Dear Dr. Ergen,

Thank you very much for your response. I tried with store_lfc=False, but it failed again.


<img width="1412" alt="Image" src="https://github.com/user-attachments/assets/b4616909-e174-4027-959c-5f39a5294266" />

**@canergen:** Can you disable map with `use_vmap=False`. There is still a typo.

**@zitiansunshine:** HI Dr. Ergen,

After completely reinstalling all packages, I do not have the crash anymore. Thank you very much for all of your help. I truly appreciate it.

## #3120: scvi doublet predictions seem off in comparison to four alternative tools
**Issue:** #3120 | **Last activity:** 2025-02-09T12:15:32Z
**State:** closed | **Author:** @robertzeibich | **Comments:** 4 | **Created:** 2025-01-02 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3120

<!-- Describe the bug -->

scvi doublet predictions seem off (too many cells that should not be doublets) in comparison to four alternative tools.

![Image](https://github.com/user-attachments/assets/734bf619-621e-492e-90ac-c5e7a7bf6183)

<!-- To reproduce -->

```python
    adata.obs.index.name = None
    scvi.model.SCVI.setup_anndata(adata)
    vae = scvi.model.SCVI(adata)
    vae.train() # batch_size=130

    solo = scvi.external.SOLO.from_scvi_model(vae)
    solo.train(batch_size=130) # batch_size=130
    # vae.train(batch_size=130) and solo.train(batch_size=130) # ValueError: Expected more than 1 value per channel when training, got input size torch.Size([1, 128])
    # change batch_size when error is thrown

    doublet_prediction = solo.predict()
    doublet_prediction['prediction'] = solo.predict(soft = False)

    adata.obs = adata.obs.reset_index().merge(doublet_prediction.reset_index(),on='index',how='left').set_index('index')
    adata.obs.index.name = None
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[Paste the error output produced by the above code here]
```

#### Versions:

<!-- Output of scvi.__version__ -->

1.2.0

**@canergen:** Hi, can you show the history of the solo model? Did it converge? I assume the data is from a single batch?

**@robertzeibich:** Thank you for getting back to me.

I am not entirely sure what you mean with converge.
Using solo on a single batches only.

I have attached one output file:
[log-3713343_20_scvi_doublets.txt](https://github.com/user-attachments/files/18369633/log-3713343_20_scvi_doublets.txt)

Is there a way to increase the number of workers?

I suspect that this is the same tool (https://github.com/calico/solo/tree/master). Is that correct?

**@ori-kron-wis:** Usually, we plot the convergence of train and validation loss curves during training (loss vs epochs).
This should give you something out of the box:
```
plt.plot(model.history["elbo_train"], label="train")
plt.plot(model.history["elbo_validation"], label="validation")
plt.title("Negative ELBO over training epochs")
plt.legend()
```
You should look that there is no overfit and that validation is converged (close to train, reach a plateau and not increasing)
Otherwise, you can use an earlystopping callback to stop the training at the optimal point.

This is true for both the scvi model and the solo model.

To increase the number of workers you can use:
scvi.settings.dl_num_workers = XXX
scvi.settings.dl_persistent_workers = True
in the beginning of script.
but why do you need this? it adds …

**@canergen:** Closing due to inactivity and this issue is not obvious in our use cases. However, we also observe that doublet detection tool performance is very dataset dependent and it makes sense to compare the output of different tools using ground truth markers.

## #3160: Why isn't it possible to run solo when there are categorical_covariate_keys?
**Issue:** #3160 | **Last activity:** 2025-02-09T12:10:29Z
**State:** closed | **Author:** @alexlenail | **Comments:** 2 | **Created:** 2025-01-22 | **URL:** https://github.com/scverse/scvi-tools/issues/3160

I have a large experiment in which multiple mice were each separately sequenced in multiple 10X channels. So each mouse has multiple channels. I created by model with:

```
scvi.model.SCVI.setup_anndata(
    adata,
    batch_key='channel',
    categorical_covariate_keys=["Mouse"],
)
```
And now I want to remove doublets, but just found out
```
ValueError: Initializing a SOLO model from SCVI with registered categorical covariates is currently unsupported.
```
Should I leave out the "Mouse" covariate? I don't understand what I'm supposed to do here.

**@ori-kron-wis:** Hey,

Sorry for late response.
Yes, leave out the mouse covariate. Our SOLO model does not support this option now.

When performing batch integration, both the channel ID and the donor ID (or any other relevant source of variation) should ideally be considered as part of the batch correction process, depending on your analysis needs.
For that manner, you can generate a new column in your concatenated adata as the batch key which is a concatenation between "channel" and "Mouse" and use that in the SCVI setup anndata to be later used in SOLO.
e.g:
'donor_1_channel1'
'donor_1_channel2'
'donor_2_channel1'
etc..

**@canergen:** Closing there. This is not planned. Solo also doesn’t support batch but instead we split by batches. It is not obvious how to handle covariates when simulating doublets.

## #3176: GPU underuse
**Issue:** #3176 | **Last activity:** 2025-02-08T13:54:57Z
**State:** closed | **Author:** @shanggutianzhen | **Comments:** 1 | **Created:** 2025-02-08 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3176

Hello, my GPU performance doesn't seem to be fully utilized in my data set
This is my code and my GPU usage at runtime
adata_B = adata[adata.obs['cell_type'] == 'B'].copy()
sc.pp.normalize_total(adata_B)
sc.pp.log1p(adata_B)
adata_B.layers['logcounts'] = adata_B.X.copy()
adata_B.raw = adata_B.copy()
#去批次尝试
batch_key = "sample"
label_key = "sample"
scvi.settings.seed = 39
sc.pp.highly_variable_genes(
    adata_B,
    flavor="seurat_v3",
    n_top_genes=1500,
    layer="counts",
    batch_key="sample",
    subset=True,
    span=0.5
)
scvi.model.SCVI.setup_anndata(adata_B, layer="counts", batch_key="sample")
model = scvi.model.SCVI(adata_B, n_layers=2, n_latent=30, gene_likelihood="nb")
model.train()
path = os.path.join("cellrange", "Bmodel")
model.save(path, overwrite=True)
SCVI_LATENT_KEY = "X_scVI"
adata_B.obsm[SCVI_LATENT_KEY] = model.get_latent_representation()
sc.pp.neighbors(adata_B, use_rep=SCVI_LATENT_KEY)
sc.tl.leiden(adata_B)
sc.tl.umap(adata_B, min_dist=0.3)

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.120                Driver Version: 550.120        CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         | …

**@canergen:** Hi, the models are small in general and parallelization can only happen within one minibatch so for most GPUs there is just not enough parallel compute taking place. You could spend the GPU into larger batch sizes (up to 1024) to speed up training. However, you will need to train for more epochs (look at loss curves).

## #2788: poor integration effect cross species
**Issue:** #2788 | **Last activity:** 2025-02-06T06:03:15Z
**State:** closed | **Author:** @GGboy-Zzz | **Comments:** 5 | **Created:** 2024-05-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2788

I am using scvi to integrate single-cell data from zebrafish and human embryos. According to the default parameters of SCVI, I obtained a very poor integrated UMap, similar to not integrated. Is there any parameter to adjust this result?
![image](https://github.com/scverse/scvi-tools/assets/76716539/4f729c93-3553-40ac-8a1e-d8adb56dda2f)
my code as belows,
[Untitled.md](https://github.com/scverse/scvi-tools/files/15270073/Untitled.md)

**@canergen:** Hi. Cross-species integration is not within the scope of scVI. For a similar model (VAE), optimized for cross-species integration, I would recommend looking into: https://www.nature.com/articles/s41592-024-02191-z.
If you still want to benchmark scVI within this framework, you can post a question on our discourse forum.

**@GGboy-Zzz:** ok, thanks for your answer, I will try to discuss it in discourse forum.

**@francicco:** Hi @GGboy-Zzz ,

I actually have the same problem, did you find a solution?
scVI and scANVI were used for cross-species integration https://www.nature.com/articles/s41467-023-41855-w
I'm so confused!
Cheers
F

**@canergen:** The code above was correct. While scVI/scANVI can be applied to integrate data across species (if gene names are harmonized), we can’t provide further guidance on it. IMO it is not the correct model (to little forced batch correction). SysVI which is an open PR in scVI-tools has some good benchmarks on cross-species integration: https://www.biorxiv.org/content/10.1101/2023.11.03.565463v2

**@GGboy-Zzz:** Yes, I found that scVI and scANVI can't work well in intetrating distance species. I think you can try other mthods such as Saturn or SAMap, Perhaps it is more suitable.

## #3171: Missing of cell marker across the dimensional space.
**Issue:** #3171 | **Last activity:** 2025-02-03T09:22:21Z
**State:** closed | **Author:** @CosterwellKhyriem | **Comments:** 3 | **Created:** 2025-02-02 | **URL:** https://github.com/scverse/scvi-tools/issues/3171

Hello,

I am trying to integrate several datasets together. In the embedding, I see a lot of leakage for cell-type marker mixing up with other cell types. It seems to be an over fitting issue.
Is there are a way to attenuate the gene leakage. Please help me with the any suggestion for an optimized set of parameters.
Please find the code and embedding the attachment for two samples.

sc.pp.highly_variable_genes(
    adata,
    flavor="cell_ranger",
    n_top_genes=3000,
    layer="counts",
    batch_key="dataset",
    subset=False,
)


scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="dataset")
vae = scvi.model.SCVI(adata, n_layers=2, n_latent=40, gene_likelihood="nb" , dispersion  = 'gene-label')
vae.train(max_epochs=500, early_stopping=True)



adata.obsm["X_scVI"] = vae.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI", knn=True, n_neighbors= 20)
sc.tl.leiden(adata,resolution=0.5) #set 1

adata.obsm["X_mde"] = mde(adata.obsm["X_scVI"])

1. Embedding highlighted by datasets
![Image](https://github.com/user-attachments/assets/7e2d470e-1119-41b0-bb49-481e77c1b011)

2. Embedding highlighted by leiden
![Image](https://github.com/user-attachments/assets/badcb8d9-487f-4838-b271-e3d9c61472b9)

3. Few cell markers embedding

![Image](https://github.com/user-attachments/assets/87b69e8b-1993-4525-b656-f4613438b8a0)

![Image](https://github.com/user-attachments/assets/4016a44d-6af3-42bb-9a44-bbf730ca46da)

**@ori-kron-wis:** Hi,
Can you share some additional info from the output of scvi.__version__ as well as your operating system/hardware you running it.
In the last few months, we dropped the use of pyMDE.

**@CosterwellKhyriem:** Hello,
Please find the information below.


OS:
windows 11.

Hardware:
CPU: AMD Ryzen AI 9 HX 370
GPU: NVIDIA GeForce RTX 4070
RAM: 64 GB


See the image below for the output of scvi.version.
![Image](https://github.com/user-attachments/assets/ccee4787-190c-4e95-b652-2fd79d3f05ec)


![Image](https://github.com/user-attachments/assets/3e909736-f501-4223-8de0-01a4ff4f1c8c)


Thank you in advance.

Regards
Costerwell

**@canergen:** Hi, just looking at the genes, is this Nanostring CosMX data? In that case you might want to try out resolVI for spatial transcriptomics.
Overintegration should be judged by clusters before and after integration. Here you only show after integration, this makes it difficult. Could you provide more background on your datasets and expected result?
In addition, our GitHub repo is for issue reports. Here this is a user question and we prefer using discourse for this. Please report there. Thank you!

## #3169: raw_means of DEGs are extremly low
**Issue:** #3169 | **Last activity:** 2025-01-30T12:51:01Z
**State:** closed | **Author:** @SimonE1220 | **Comments:** 1 | **Created:** 2025-01-29 | **URL:** https://github.com/scverse/scvi-tools/issues/3169

Dear all, I am new to the scverse.
If I performe a DEG analysis the significant DEGs is_de_fdr_0.05=True have a extremly low raw_mean1 and raw_mean2. If I plot the DEG genes in a violin side by side for a certain cell-type for both conditions, the expression is nealy 0 for both conditions even its a DEG do I do anything wrong ?
Thank you.

**@ori-kron-wis:** closing here. was answered in discourse

## #3142: Add continuous label embedding in scANVI model
**Issue:** #3142 | **Last activity:** 2025-01-21T20:44:02Z
**State:** closed | **Author:** @yxwucq | **Comments:** 2 | **Created:** 2025-01-13 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3142

Hello,
I've noticed that the current scANVI model only supports discrete label variables. I'm wondering if there are plans to support high-dimensional continuous variables as labels?

I'm currently researching potential approaches, and my idea is to keep the fully connected layers in the Classifier layer directly as predictors. Additionally, I plan to directly inject continuous variables in the second encoder-decoder layer.

**@ori-kron-wis:** Hi,
We currently don't have plans to turn SCANVI into a regression problem if that's what you meant.
Injecting covariates into the hidden layers is something that is planned. Please share your solution with us.
Thank you.

**@canergen:** For the z1 and z2 encoder decoder we don’t want covariates. This will lead to worse integration. ScANVI is for cell-type annotation and its loss requires categorical labels. Adding an MLP that predicts a continuous value is possible but not within the scope of scANVI.

## #3135: Integration Testing CI Test Failure on python 3.10
**Issue:** #3135 | **Last activity:** 2025-01-14T14:24:11Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-01-11 | **URL:** https://github.com/scverse/scvi-tools/issues/3135

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/12719575671) to review. @scverse/anndata

## #3136: Integration Testing CI Test Failure on python 3.12
**Issue:** #3136 | **Last activity:** 2025-01-14T14:24:09Z
**State:** closed | **Author:** @scverse-bot | **Comments:** 0 | **Created:** 2025-01-11 | **URL:** https://github.com/scverse/scvi-tools/issues/3136

The daily CI failed on test for scvi-tools failed.  Please go to [the logs of the integration testing repo](https://github.com/scverse/integration-testing/actions/runs/12719575671) to review. @scverse/anndata

## #3131: Docker images not updated
**Issue:** #3131 | **Last activity:** 2025-01-14T12:32:24Z
**State:** closed | **Author:** @nictru | **Comments:** 3 | **Created:** 2025-01-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3131

Hello everyone,
thanks for your effort. I just wanted to point out that the [official docker images](https://hub.docker.com/r/scverse/scvi-tools) apparently have not been updated in six months. Since this is an official installation method ([docs](https://docs.scvi-tools.org/en/stable/installation.html#docker)), would it be possible to update them?

**@ori-kron-wis:** Hey @martinkim0 , could you assist with this issue?

**@nictru:** Ah I just saw [this](https://github.com/YosefLab/scvi-tools-docker?tab=readme-ov-file#docker-images):

> IMPORTANT: This repository is deprecated. Please see the updated images in the [GitHub Container Registry](https://github.com/scverse/scvi-tools/pkgs/container/scvi-tools)

So it is probably more a documentation problem. Maybe the [documentation section](https://docs.scvi-tools.org/en/stable/installation.html#docker) could point to GHCR instead of Dockerhub?
Right now it is a bit hard to find out that one should check there instead

**@ori-kron-wis:** You are correct. We will change the documentation. thanks!

## #3129: Integration Causes Women to have High chrY Gene Abundances
**Issue:** #3129 | **Last activity:** 2025-01-08T21:45:31Z
**State:** closed | **Author:** @DarioS | **Comments:** 3 | **Created:** 2025-01-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3129

In the raw count data from Cell Ranger, we see that, because women don't have chromosome Y, they have zero read counts for chrY genes.

![Image](https://github.com/user-attachments/assets/ec38d41c-0b96-4871-b403-5f7ef763e3f4)

However, scVI gets this basic textbook biology wrong and claims that women have higher chrY gene expression than men do.

![Image](https://github.com/user-attachments/assets/184803be-36f9-4bfe-922c-e1f45538731f)

The dataset used is unpublished and can't be used for a minimal, reproducible example. But, it ought to be seen in other datasets with gender. It seems that scVI is attempting to make samples more similar to each other even when they should not be; a case of overcorrection. These values were obtained by `model$get_normalized_expression()` after executing `model$train()`.

**@canergen:** Hi, I agree that it's weird that y-chromosome genes are predicted to be expressed higher in female samples. I would first highlight that other methods for integration and imputation of counts might suffer from similar effects. The estimates bring samples closer together in expression - I would argue that it is more likely that a cell expresses a gene if similar cells in other batches express a gene - scVI predicts the likelihood of expression give a certain cell state and batch. The batch effect is here not learnt correctly.
You usually get a better picture of what the model has learned by using posterior predictive samples and scvi.criticism allows evaluating how good the model is (see tutorials). The key aspect is here likely what value you have used as batch_key. You could also add sex …

**@DarioS:** > The key aspect is likely what value you have used as `batch_key`.

I left `batch_key` unspecified.

> You could also add sex as categorical covariate when setting up the model.

It seems that is _not_ what I ought to do.

> `categorical_covariate_keys`: These should not be used for biologically-relevant factors that you do _not_ want to correct for.

**@canergen:** I get your misunderstanding, we specify here the effect on the latent code: If categorical_covariate_key is added, the latent space is by design independent of this covariate. However, you're complaining here about the predicted gene expression, this one will improve when adding a batch key and/or a categorical_covariate_key. You expect your latent space to reflect sex differences and want the model to correctly predict batch-specific expression. This is difficult for any latent-space model. Please use a batch key to better preserve batch-specific expression.
Closing here, please open a thread on Discourse if further discussion is needed. We intend GitHub for bug reports.

## #3123: Training iterations are way slower when upgrading to 1.2.1 as compared to 1.2.0
**Issue:** #3123 | **Last activity:** 2025-01-08T08:16:02Z
**State:** closed | **Author:** @abs51295 | **Comments:** 2 | **Created:** 2025-01-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3123

Training iterations are way slower when upgrading to 1.2.1 as compared to 1.2.0. I suspect that it doesn't take into account the explicit `batch_size` parameter passed to `train` method.

```python

# For the exact same dataset and model, here's the code snippet:

data_splitter_kwargs = {
     "external_indexing": [train_indices, validation_indices, test_indices]
}

early_stopping_kwargs = {
    'early_stopping': True,
    'early_stopping_monitor': 'elbo_validation',
    'early_stopping_patience': 10,
    'early_stopping_min_delta': 0.0,
    'check_val_every_n_epoch': 1
}

plan_kwargs = {
    "reduce_lr_on_plateau": True,
    "lr_patience": 8,
    "lr_factor": 0.1,
}

model.train(max_epochs=500,  accelerator='gpu', devices=[int(index_of_gpu)], shuffle_set_split=True, batch_size=2048, load_sparse_tensor=True, plan_kwargs = plan_kwargs, datasplitter_kwargs = data_splitter_kwargs, **early_stopping_kwargs)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb

Output from v1.2.0:
Epoch 2/500:   0%|▎                                                                                                    | 1/500

[00:42<5:53:51, 42.55s/it, v_num=1, train_loss_step=133, train_loss_epoch=143]


Output from v1.2.1:
Epoch 500/500: 100%|██████████| 500/500 [73:58:08<00:00, 538.26s/it, v_num=1, train_loss_step=171, train_loss_epoch=169]
```

#### Versions:

1.2.1

**@ori-kron-wis:** Hey @abs51295,
Thank you for noticing it.
It happens due to a fix re this going from v1.2.0 to v1.2.1 (and is more clear to exhibit with external indices and large batch size)
We will fix it

**@ori-kron-wis:** This is released now in scvi-tools 1.2.2.post2, please update your installation.
Thanks again for noticing it!

## #2215: ValueError with NaN tensors in gimVI training
**Issue:** #2215 | **Last activity:** 2025-01-05T06:36:54Z
**State:** closed | **Author:** @sunericd | **Comments:** 17 | **Created:** 2023-07-28 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2215

<!-- Describe the bug -->

When training the gimVI model, I am running into a ValueError in the first epoch for some datasets and not others. In all cases, the inputs are AnnData objects with raw counts for both the RNAseq and for the spatial data (dtype=float64). I have tried filtering out cells with zero counts and/or normalizing the RNAseq data but am still running into the same error. Strangely, gimVI seems to be able to train successfully on one dataset but when I remove 4 genes from the spatial data (32 -> 28 genes), it fails on that dataset. Happy to share data if that would be helpful and if there are suggestions for doing so (screenshots of basic data info below).

<!-- To reproduce -->

```python
    import scvi
    from scvi.external import GIMVI

    # preprocessing of data
    spatial_adata = spatial_adata[:, spatial_adata.var_names.isin(RNAseq_adata.var_names)]

    # indices for filtering out zero-expression cells
    filtered_cells_spatial = (spatial_adata.X.sum(axis=1) > 1)
    filtered_cells_RNAseq = (RNAseq_adata.X.sum(axis=1) > 1)

    # make copies of subsets
    spatial_adata = spatial_adata[filtered_cells_spatial,:].copy()
    RNAseq_adata = RNAseq_adata[filtered_cells_RNAseq,:].copy()

    # setup anndata for scvi
    GIMVI.setup_anndata(spatial_adata)
    GIMVI.setup_anndata(RNAseq_adata)

    # train gimVI model
    model = GIMVI(RNAseq_adata, spatial_adata, **kwargs)
    model.train(200)
```

<!- …

**@martinkim0:** Hi, thanks for bringing up this up and sorry you're running into this issue.

One possible source for these NaN errors are the exponential activations in the model - we've had similar issues before with other models depending on the dataset used as well as any non-default arguments that are passed during model initialization. Unfortunately, there's no straightforward way to modify these at the moment, and we cannot change them on our end because of reproducibility with the original manuscript.

Would you be able to share the dataset as well as a reproducible notebook?

**@sunericd:** Thanks for the fast response. Here is a link to a minimal notebook and data files for reproducing the errors (when I tested it today, gimVI seems to fail on the 32 gene data and succeeds on the 28 gene data, so maybe there are some variable behaviors there):

[https://www.dropbox.com/sh/5smbltpudpntmh4/AABrxiGL8jlNxdq3dvHOx3bga?dl=0](https://www.dropbox.com/sh/5smbltpudpntmh4/AABrxiGL8jlNxdq3dvHOx3bga?dl=0)

**@martinkim0:** Thanks! I'll try to get this running and get back to you

**@izabellaleahz:** Hello, I am also running into the same issue. Is there a way steps to modifying could be publicly posted?

**@james-cranley:** any news on this? I am also experiencing the same error (mine is when running `mvi.train()`)

**@james-cranley:** PS I tried with the same code and same object using an old environment (with scvi 0.2.3 installed) and it ran. the env where I was getting this error had 1.0.3 installed

**@james-cranley:** with the environment which previously gave this issue activated, I ran:

```bash
pip uninstall scvi-tools
pip install scvi-tools==0.20.3
```

then restarted the kernel and the notebook ran without error.

**@lila167:** With `scvi-tools==1.0.3` installed, I got a similar error while training MultiVI and could fix the problem by installing `scvi-tools==0.20.3`.

**@Accelerator-thu:** One possible cause of this issue is invalid data input, I guess the input needs to be a non-negative matrix.

BTW, it would be reasonable to add an assert line at the outer modules, avoiding misdirections like this.

**@sunericd:** Has there been any updates on this? I have tried running different versions (0.19.0, 0.20.3, and most recently 1.0.4) but none of them consistently work for the test data and notebook. Using scanpy==1.9.6 and scvi-tools==1.0.4, I did notice that if I restart the kernel a few times, sometimes it is able to complete the model.train(200) call successfully so perhaps it is due to some stochastic part of the model?

**@Dana162001:** Hi, I would also like to hear if someone solved the problem, in my case model.train() function runs with 2 epochs but everything more than that and I am getting the same value error:
ValueError: Expected parameter loc (Tensor of shape (128, 10)) of distribution Normal(loc: torch.Size([128, 10]), scale: torch.Size([128, 10])) to satisfy the constraint Real(), but found invalid values:
tensor([[nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        ...,
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan]], device='cuda:0',

**@ktpolanski:** Same story here - downgraded from 1.0.4 to 0.20.3 and MultiVI ran fine. Dropping a comment mostly to be notified if something budges on this front.

**@adamdingliang:** Running into the same issue, there seems to be some randomness depending on the number of genes or cells, as mentioned above. Tried different version of scvi-tools, is there any workaround?

**@canergen:** A lot of those issues should be fixed in the recent release in 1.2.0. Do you use the recent version?
Have you removed cells with less than 20 counts (these add some instability). Adding drop_last=True to the datasplitter_kwargs might help additionally.

**@adamdingliang:** We are using version 1.1.6.post2, we haven't tried 1.2.0. Yes, for scRNAseq, we removed cells with less than 100 counts; for spatial data, we removed cells with less than 20 counts. Thanks for the suggestions.

**@ori-kron-wis:** Hey @adamdingliang , can you keep us posted on where this stands? can we close this issue?

**@adamdingliang:** Hi, was on vacation. Yeah, we tried to impute a subset of missing genes (our customers don't usually need to impute all the missing genes) in release 1.2.1, and it worked fine. It's still unclear to us whether the bug was fixed in the new release, or some missing gene caused the error.

## #3109: Decipher - CUDA tests failure
**Issue:** #3109 | **Last activity:** 2024-12-24T21:39:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3109

Hi @justjhong ,

We merged https://github.com/scverse/scvi-tools/pull/3091, and it didn't run CUDA tests.
On other branches that ran the merged decipher tests on CUDA, we got 2 failures:

![Image](https://github.com/user-attachments/assets/985f7b3f-2387-4096-be00-c9ea47baf285)

![Image](https://github.com/user-attachments/assets/acbcbddd-f9af-43ae-884b-dacf30c5edac)

See for example: https://github.com/scverse/scvi-tools/actions/runs/12458060589/job/34773264674?pr=3100

Basically its about GPU-CPU integration issues.

You can go ahead and run CUDA tests on the PR fix: https://github.com/scverse/scvi-tools/pull/3110

## #1586: Model creation fixtures
**Issue:** #1586 | **Last activity:** 2024-12-23T09:57:49Z
**State:** closed | **Author:** @RK900 | **Comments:** 0 | **Created:** 2022-06-28 | **Labels:** bug, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1586

When using pytest fixtures to create simple SCVI models in test_model, the runtime of the suite increases from 4 -> 14 seconds, as reported in #1576

## #2390: Add support for NumPy 2
**Issue:** #2390 | **Last activity:** 2024-12-22T18:59:49Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-11 | **Labels:** enhancement, dependencies, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2390

https://pythonspeed.com/articles/numpy-2/

## #3106: scvi-tool 0.20.3 is using deprecated np.str type causing errors
**Issue:** #3106 | **Last activity:** 2024-12-22T00:21:45Z
**State:** closed | **Author:** @Dennis-Bersenev | **Comments:** 1 | **Created:** 2024-12-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3106

<!-- Describe the bug -->

Need to modify line 81 of scvi/data/_built_in_data/_pbmc.py  because the current implementation is using a deprecated NumPy string type np.str.
Proposed solution involves replacing np.str lines with the code shown below:
barcodes_metadata = pbmc_metadata["barcodes"].index.values.ravel().astype(str)

<!-- To reproduce -->

```python
scvi.data.pbmc_dataset()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
python3.10/site-packages/scvi/data/_built_in_data/_pbmc.py", line 81, in loadpbmc_dataset
    barcodes_metadata = pbmc_metadata["barcodes"].index.values.ravel().astype(np.str)
  File "/home/ubuntu/SBI/rna_fm/scgpt-env/lib/python3.10/site-packages/numpy/init.py", line 324, in getattr
    raise AttributeError(former_attrs[attr])
AttributeError: module 'numpy' has no attribute 'str'.
```

#### Versions:

<!-- Output of scvi.__version__ -->
Name: scvi-tools
Version: 0.20.3

**@canergen:** Please follow the instructions in our docs and install the most recent version 1.2.1. This version is compatible with numpy<2.0. 2.0 is not supported by dependencies. 1.3 will drop these dependencies.

## #3105: Error MPS
**Issue:** #3105 | **Last activity:** 2024-12-20T18:40:45Z
**State:** closed | **Author:** @SimonE1220 | **Comments:** 1 | **Created:** 2024-12-20 | **URL:** https://github.com/scverse/scvi-tools/issues/3105

Dear all,
I am new to programming and have a apple M3.
The Backend MPS is found but if I use it I have this error:

tensor([[nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        ...,
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan]], device='mps:0',
       grad_fn=<LinearBackward0>)

But with CPU it works could you please help me.
Thank you.

**@canergen:** Hi, MPS has a very free interpretation of memory pointers, which leads to accessing wrong values and NaN errors. Unfortunately, this doesn't produce errors and debugging it is not straightforward (see https://github.com/pytorch/pytorch/issues/132605). However, we have a PR with all models passing tests. However, testing reproducibility across all different configurations will be hard to perform, consider it experimental. For scVI, scANVI and DestVI results suggest that running the model on MPS gives the same results. We will likely merge the PR next week and in the next release models are trained by default on MPS.

## #3094: Issue with model.train() in scVI - Training Stuck at 0%
**Issue:** #3094 | **Last activity:** 2024-12-17T16:48:15Z
**State:** closed | **Author:** @Ares1314 | **Comments:** 3 | **Created:** 2024-12-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3094

Dear：
I am encountering an issue while using scvi-tools for cell integration. Specifically, when I run model.train(), the training progress remains stuck at 0%, and no iterations occur despite the GPU being detected and utilized. Below is the log output:

![Image](https://github.com/user-attachments/assets/aebf9a06-b533-4f4e-b1dc-d5132b03eca4)

I have tried the following steps to troubleshoot the issue:
1. Verified that the dataset is loaded correctly and passed to the model.
2. Ensured that the GPU is available and CUDA is functional.
3. Adjusted training parameters such as max_epochs and learning rate.

Despite these efforts, the problem persists. I would greatly appreciate your guidance on how to resolve this issue. Please let me know if you need further details about my setup or code.

Thank you！

**@Ares1314:** At the same time, after a few minutes, the following error appears:
Trainer.fit stopped: max_epochs=246 reached.
![Image](https://github.com/user-attachments/assets/a41fc43c-ceff-436b-aa02-9dd64a132db2)

**@ori-kron-wis:** The last message is not an error, but a message that the model was trained.
You can verify this with checking if model.is_trained and continuing your downstream analysis.
If this is ok, then there is some issue with the interactive progress bar of your jupyter nb.

**@canergen:** I guess it’s some issue with your Jupyter installation. I’m closing here as I’m afraid that we won’t be able to debug it.
Model.history should contain metrics for all 246 epochs and then you are safe to use this model and only the progress bar is broken.
If more users face this issue, please reopen here and we’ll try to match versions and recreate.

## #3093: error when loading model
**Issue:** #3093 | **Last activity:** 2024-12-16T09:04:03Z
**State:** closed | **Author:** @wddyzxxx | **Comments:** 2 | **Created:** 2024-12-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3093

<!-- Describe the bug -->

always meet error when loading saved models. Personally, I think it's torch 's problem

<!-- To reproduce -->

```python
scanvi_ref_path = os.path.join("ref_scanvi", "2024_12_14_forquery_scanvi_ref")
scanvi_ref.save(scanvi_ref_path, overwrite=True, save_anndata = True)

scvi.model.SCANVI.prepare_query_anndata(query, scanvi_ref) # this works since it directly uses the model in the environment
scvi.model.SCANVI.prepare_query_anndata(query, scanvi_ref_path) # this fails

scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref) # this works
scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref_path) # this fails
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
UnpicklingError                           Traceback (most recent call last)
Cell In[243], [line 1](vscode-notebook-cell:?execution_count=243&line=1)
----> [1](vscode-notebook-cell:?execution_count=243&line=1) scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref_path)

File ~/miniforge3/lib/python3.10/site-packages/scvi/model/base/_archesmixin.py:92, in ArchesMixin.load_query_data(cls, adata, reference_model, inplace_subset_query_vars, accelerator, device, unfrozen, freeze_dropout, freeze_expression, freeze_decoder_first_layer, freeze_batchnorm_encoder, freeze_batchnorm_decoder, freeze_classifier)
     [54](https://file+.vscode-reso …

**@canergen:** Hi, is it possible that this is a nightly build of torch? There's a deprecation warning for this error since a couple of weeks but it's a very quick transition to remove it. Anyhow @ori-kron-wis Can you explicitly add `weights_only=True` to all torch.load calls. We store non-custom parameters in these pickle files and weights_only is not expected to work. We would otherwise store them as a separate pkl file so the potential danger remains. @ori-kron-wis Up-to-you but we could put warnings to some location that it is potentially dangerous and should only be executed from trusted sources.

**@ori-kron-wis:** I couldn't reproduce it, @wddyzxxx can you confirm that adding weights_only=False/True will solve it? were you using the nightly of torch?

## #1577: Support to build NumPyro models.
**Issue:** #1577 | **Last activity:** 2024-12-12T06:24:00Z
**State:** closed | **Author:** @justjhong | **Comments:** 1 | **Created:** 2022-06-23 | **Labels:** enhancement, jax, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1577

Support for NumPyro as detailed in https://github.com/scverse/scvi-tools/issues/1366.

https://github.com/scverse/scvi-tools/pull/1495 can be used as a starting point.

**@canergen:** Not planned

## #2073: Deprecate multivi setup anndata
**Issue:** #2073 | **Last activity:** 2024-12-12T06:23:33Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 2 | **Created:** 2023-05-31 | **Labels:** P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2073

One thing we may need to consider is a util to patch loading old saves of multivi models if we remove setup anndata

**@marianogabitto:** Guys, can you comment on slack what are the plans for removing the setup_anndata. I have not heard about them and even if I want to help, I am not going to be able.

**@canergen:** Will be adressed with HuggingFace MultiVI. See https://github.com/scverse/scvi-tools/pull/3039 for a suggestion.

## #2645: Use TensorBoard as default logger
**Issue:** #2645 | **Last activity:** 2024-12-12T06:21:05Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-04-02 | **Labels:** enhancement, good first issue, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2645

**@canergen:** As custom logger is preferred. I still like to plot it in basic runs. See huggingface TS models for tensorboard logging.

## #3083: Anndata 0.11.1 Warnings
**Issue:** #3083 | **Last activity:** 2024-12-11T18:54:05Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 2 | **Created:** 2024-12-08 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/3083

There are many anndata import warnings (for >=v0.11) in case we run it with python 3.12.
this affects many read functions throughout the code which should be changed now.

See example:
![Image](https://github.com/user-attachments/assets/cb8525cb-e7c8-4b80-9462-d6f2256e48ef)

**@ori-kron-wis:** @ilan-gold Can you see the above warnings? will changing the imports be enough ? (i.e I want to make sure there is no logic change)

**@ilan-gold:** >  will changing the imports be enough ? (i.e I want to make sure there is no logic change)

Yes, just changing the import locations should be fine!

## #3047: Multi-GPU fails when using ConcatDataLoader
**Issue:** #3047 | **Last activity:** 2024-12-09T11:43:12Z
**State:** closed | **Author:** @absudabsu | **Comments:** 4 | **Created:** 2024-11-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3047

<!-- Describe the bug -->

When utilizing multi-gpu training with DDP, e.g. with a `SemiSupervisedDataLoader` and subsequently `ConcatDataLoader`, an error is raised because `distributed_sampler` keyword argument required for `AnnDataLoader` is not explicit in the class definition of `ConcatDataLoader`.  Passing this keyword argument in using the wildcard allows `AnnDataLoader` to be initialized properly, but throws an error for initializing the parent class `torch.util.DataLoader` using the same `distributed_sampler` keyword argument.

<!-- To reproduce -->

```python
datasplitter_kwargs = {}
datasplitter_kwargs['distributed_sampler'] = True
data_splitter = SemiSupervisedDataSplitter(
            adata_manager=self.adata_manager,
            train_size=train_size,
            validation_size=validation_size,
            shuffle_set_split=shuffle_set_split,
            n_samples_per_label=n_samples_per_label,
            batch_size=batch_size,
            **datasplitter_kwargs,
        )
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
2024-11-18T23:06:15.416Z [rank1]:   File "/stage/env/lib/python3.11/site-packages/scvi/train/_trainrunner.py", line 98, in __call__
2024-11-18T23:06:15.416Z [rank1]:     self.trainer.fit(self.training_plan, self.data_splitter)
2024-11-18T23:06:15.416Z [rank1]:   File "/stage/env/lib/python3.11/site-packages/scvi/train/_trainer.py", line 219, in fit
2024-11-18T23:06:15.416Z [rank1]:     supe …

**@canergen:** Hi, multi-GPU support is still experimental. We need to include tests using multiple GPUs and need to test it more. Timeline is Q1 2025 and it's planned to be released with 1.3.

**@ori-kron-wis:** @absudabsu can you please check if you are getting the same error with this branch: https://github.com/scverse/scvi-tools/tree/Ori-Distributed-Sampler-Fix. Note it is checkout from main and version 1.2.0

**@heeler:** Hi @ori-kron-wis I'm working on the same project with @absudabsu. I gave the code a try last night but it raised exceptions due to the `pin_memory` and `num_workers` kwargs that eventually get passed into `AnnDataLoader` and cause an exception within the class when  `super().init(**kwargs)` was called as DataLoader only has keywords defined. I was able to get it to get past that problem in the code by filtering the args.  I did add some hacks that could be wrong.

The changes are here: https://github.com/heeler/scvi-tools/tree/Ori-Distributed-Sampler-Fix-Octo

Unfortunately the changes don't seem to get picked up properly by lightning. By this I mean that the shape of the data chunks is wrong in the training step. Instead of the batch being 128x6000 (batch size x genes) it has the shape 1x …

**@ori-kron-wis:** Thanks I will take a look.
I did make many code changes yesterday with this branch, as we had other issues regarding the github runner on the multigpu workstation. See the updated branch code.

We only have multi-GPU support for SCVI modelling, so the problem you described is something we still need to fix (rise in SCANVI for example). This is planned for v1.3

Perhaps you can share the exact code you are working on?

## #3057: gimVI - multi-GPU support?
**Issue:** #3057 | **Last activity:** 2024-12-02T20:05:12Z
**State:** closed | **Author:** @jachou1 | **Comments:** 8 | **Created:** 2024-11-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3057

<!-- Describe the bug -->

I'm currently running gimVI on 14K genes to impute spatial expression from scRNA-seq data. My model trains, but then I can't get the imputed expression using model.get_imputed_values(). My 1 GPU has ran out of memory.

<!-- To reproduce -->

```python
imputed_spatial_rates = model.get_imputed_values(normalized= False)[1]
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB. GPU 0 has a total capacity of 44.53 GiB of which 448.00 KiB is free. Including non-PyTorch memory, this process has 44.52 GiB memory in use. Of the allocated memory 36.12 GiB is allocated by PyTorch, and 7.91 GiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid fragmentation.  See documentation for Memory Management  (https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION
1.2.0


<!-- Relevant screenshots -->

Question: Can I run on multi-GPUs to get the learned expression for GIMVI to overcome this out-of-memory problem?

Thank you.!

[Image](https://github.com/user-attachments/assets/e6ae4441-56b2-4530-956f-d9710f60bb3b)

**@canergen:** Multi-GPU might help here, but looking at the numbers, it’s more likely a coding error. We should fetch mini-batches to CPU in https://github.com/scverse/scvi-tools/blob/bcd7e6722d43dfdec4e9b63d5f650a638202c124/src/scvi/external/gimvi/_model.py#L366 instead of first collecting all and then transferring to CPU. @ori-kron-wis Can you create a PR?

**@ori-kron-wis:** The gimVI implementation of get_latent and get_imputed does differ from the regular VAEmixin implementation in terms of appending on the CPU first and it should be fixed. I have a suggested PR here: https://github.com/scverse/scvi-tools/pull/3058

However, Im not sure this will solve your problem, as from the testing I made there is no tremendous difference in GPU memory usage between those implementations (although this might depend on many factors).

In your case, from what I see, the GPU was fully loaded with 44.5GB and nothing was left to even allocate 20MB. Perhaps there was some legacy data there?

MultiGPU support will be available only starting from 1.3v and might help, but in the meantime, I can suggest decreasing your mini batch size/train_size, reducing your input size and model …

**@canergen:** To explain the error a bit more, GIMVI was taking up the 44GB:
`this process has 44.52 GiB memory in use. Of the allocated memory 36.12 GiB is allocated by PyTorch`
The simple model shouldn’t use up that much memory. If it still fails in the branch. Can you share memory usage after model training, dataset size and perform inference using a subset of the data using a subset AnnData object?

**@jachou1:** Hi, apologies for delay in response. It was Thanksgiving in the states, and I hadn't expected such a quick response and turnaround. Thanks so much for fixing it. But I'm having difficulty getting your latest code change. I see you've already merged the change to the main branch of this repo. I tried installing using pip install git+https://github.com/scverse/scvi-tools.git@main, but I get the following error. ![Image](https://github.com/user-attachments/assets/05a1fe02-877d-4490-8a94-0a3fb9aaf07a)
What's the best way for me to get this changed code? Thank you!

**@ori-kron-wis:** @jachou1 Thank you for catching this. Indeed, in our latest merge, we mistakenly merged a bad legacy link of the scvi-tutorials, which has since then been changed. I've updated the main branch and you should be able to install scvi-tools from this branch.

Having said that, Im not sure this little gimVI fix will solve the problems you described. Take a took at what @canergen  and I wrote.
Let us know if you manage.

**@jachou1:** @ori-kron-wis Yes, it still fails. It seems the model still takes up too much memory. ![Image](https://github.com/user-attachments/assets/941bbcfb-a43d-41fd-acbc-4b8d2ed22ba0)

So the model finished training for this large dataset. Spatial_ad: 830K cells x 427 genes, and single_cell_ad: 300K x 14K genes. I'm trying to impute the spatial data from the single-cell reference dataset. Is this just too large of a dataset for the model to handle?

I then tried to subset the data to just 1 tissue in the spatial_ad. So it's 48K cells x 427 genes (spatial_ad) and single_cell_ad: 300K cells x 14K, but I run into an error with NaNs in the tensor. ![Image](https://github.com/user-attachments/assets/87d1ac1e-75b7-4f55-8403-c5b1a4541ed1)

I saw this error has popped up previously.

Is the issue with CU …

**@canergen:** The screenshot is without the fix. It’s still cpu transfer after concatenating. Can you try to install from main again?
I thought the NaN error was fixed (adversarial classifier with a single batch) and have to check why it’s still popping up.

**@jachou1:** Tried installing from main, and it is resolved in terms of CUDA out of memory error. Thank you. Not sure the source of the NaN error. It happens sporadically during training. Could you comment on whether using 200 epochs is necessary to reach convergence for gimVI? Or is it dependent on the dataset at-hand?

## #3055: Model hyperparameter tuning with autotune fails on colab tutorial
**Issue:** #3055 | **Last activity:** 2024-11-27T09:51:25Z
**State:** closed | **Author:** @alexclarke7 | **Comments:** 5 | **Created:** 2024-11-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3055

<!-- Describe the bug -->

Model hyperparameter tuning with scVI tutorial fails to run on colab tutorial page (https://docs.scvi-tools.org/en/1.0.0/tutorials/notebooks/autotune_scvi.html).

<!-- To reproduce -->

```python
!pip install --quiet hyperopt
!pip install --quiet "ray[tune]"
!pip install --quiet scvi-colab
from scvi_colab import install

install()

model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata)

scvi_tuner = autotune.ModelTuner(model_cls)


```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[180], line 1
----> 1 tuner = autotune.ModelTuner(model_cls)

AttributeError: module 'scvi.autotune' has no attribute 'ModelTuner'
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION

1.2.0

<!-- Relevant screenshots -->

**@canergen:** Hi, could you please refer to the tutorial for 1.2.0: https://docs.scvi-tools.org/en/1.2.0/tutorials/notebooks/tuning/autotune_scvi.html.

Best!

**@alexclarke7:** Thank you.

I am trying to discover the tunable parameters for a model according to the tutorial as below:

### 'Our main entry point to the autotune module is the ModelTuner class, a wrapper around [ray.tune.Tuner](https://docs.ray.io/en/latest/tune/api_docs/execution.html#tuner) with additional functionality specific to scvi-tools. We can define a new ModelTuner by providing it with our model class.

ModelTuner will register all tunable hyperparameters in SCVI – these can be viewed by calling info(). By default, this method will display three tables:

Tunable hyperparameters: The names of hyperparameters that can be tuned, their default values, and the internal classes they are defined in.
Available metrics: The metrics that can be used to evaluate the performance of the model. One of …

**@canergen:** You can now tune all model parameters. It is not required anymore to define a parameter as tunable in the model. The tutorial that I shared highlights how to set up the search space.

**@alexclarke7:** Thanks

previously tuner.info() had created a nice table of default values for a given model, which was helpful to choose the search space, which is mentioned in the tutorial page you linked, but I can't access it. Is that paragraph of the tutorial still correct?

**@canergen:** This function is not supported anymore and now that all arguments are accessible it doesn't make sense anymore as the table will get quite large. We prefer exposing every parameter to ray.tune.
@ori-kron-wis Can you remove this sentence from the tutorial?

## #3052: TotalVI duplicate label on axis error while running differential_expression after model training
**Issue:** #3052 | **Last activity:** 2024-11-22T18:32:18Z
**State:** closed | **Author:** @HChungLab | **Comments:** 1 | **Created:** 2024-11-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3052

<!-- Describe the bug -->
 We trained CITE-seq data with TotalVI, the model converged and ran successfully, but we are running into issues when using the differential_expression function

<!-- To reproduce -->

```python
de_df = model.differential_expression(
    groupby="rna_subset:leiden_totalVI", delta=0.5, batch_correction=False
)
de_df.head(5)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
DE...:   0%|          | 0/12 [00:00<?, ?it/s]
/gpfs/gibbs/project/chung/ah2636/envs/TotalVI_env4/lib/python3.12/site-packages/scvi/model/_totalvi.py:433: UserWarning: Make sure the registered protein expression in anndata contains unnormalized count data.
  adata = self._validate_anndata(adata)
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[94], line 1
----> 1 de_df = model.differential_expression(
      2     groupby="rna_subset:leiden_totalVI", delta=0.5, batch_correction=False
      3 )
      4 de_df.head(5)

File /gpfs/gibbs/project/chung/ah2636/envs/TotalVI_env4/lib/python3.12/site-packages/scvi/model/_totalvi.py:774, in TOTALVI.differential_expression(self, adata, groupby, group1, group2, idx1, idx2, mode, delta, batch_size, all_stats, batch_correction, batchid1, batchid2, fdr_target, silent, protein_prior_count, scale_protein, sample_protein_mixing, include_protein_background, **kwargs)
    760 model_fn = partia …

**@canergen:** Please use different names for genes and proteins by adding e.g. "cite-" to all proteins. You can do so after training the model by changing model.adata.

## #3035: Training fails with mini-batch size of one sample
**Issue:** #3035 | **Last activity:** 2024-11-19T08:10:29Z
**State:** closed | **Author:** @LeonHafner | **Comments:** 3 | **Created:** 2024-10-31 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3035

<!-- Describe the bug -->
This bug has already been reported in several issues and on discourse: #2314 #2214 #221  #426
SCVI training fails if the `ceil(n_cells * 0.9) % 128 == 1`, where 0.9 is the training split and 128 the batch size.
I thought the bug should be fixed with 1.2.0, but unfortunately it still occurs.

It would be very cool, if you could find a fix for that, as that would allow users to remove unnecessary try-except blocks that change the batch size if the error occurs.

Thanks a lot!

<!-- To reproduce -->

```python
import numpy as np
import anndata as ad
from scvi.model import SCVI


num_cells = 143
num_genes = 1000

shape_param = 2.0
scale_param = 1.0

gamma_rates = np.random.gamma(shape=shape_param, scale=scale_param, size=(num_cells, num_genes))
data = np.random.poisson(gamma_rates)

adata = ad.AnnData(X=data)

print(adata.shape)

SCVI.setup_anndata(adata)
model = SCVI(adata)
model.train()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Traceback (most recent call last):
  File "/nfs/home/students/l.hafner/nf-core/scvi_test/test_scvi.py", line 21, in <module>
    model.train()
  File "/nfs/home/students/l.hafner/miniforge3/envs/scvi_test/lib/python3.12/site-packages/scvi/model/base/_training_mixin.py", line 145, in train
    return runner()
           ^^^^^^^^
  File "/nfs/home/students/l.hafner/miniforge3/envs/scvi_test/lib/python3.12/site-packages/scvi/train/_trainrunner.py", line 96, in __call__ …

**@ori-kron-wis:** Hi @LeonHafner thanks for posting this.
Currently, apparently, we issue a warning in such cases, see https://github.com/scverse/scvi-tools/pull/2916 and the changelog. There is no logic fix. Will this not be enough for your case?

Otherwise, see my suggested fix here:  https://github.com/scverse/scvi-tools/pull/3036
The idea is that in this case we will artificially add +1 to n_train and remove 1 from n_val, if possible (i.e if n_val by itself is larger than 2)

**@LeonHafner:** Hi @ori-kron-wis, thanks for the quick reply.
for me the quickest fix was to pass `datasplitter_kwargs={"drop_last": True}` to the `model.train` function. This simply drops the cell that remains in the last batch.

But as this is not a very nice solution, I would appreciate some logic being implemented into scVI to fix this. Your suggested fix is a great idea, hope you will be able to get it merged!

Best,
Leon

**@canergen:** @ori-kron-wis I didn’t come to fix it.  I think we should add the cells to validation (and I would do it for less than 3 cells - sounds safer). We should set by default train_size and validation_size to None. If it’s None we change these small batches. If the user sets a custom value like 0.9 (old behavior), we don’t change the train cells and it still fails.

## #1789: Some suggestion about GNN
**Issue:** #1789 | **Last activity:** 2024-11-13T09:35:35Z
**State:** open | **Author:** @HuangDDU | **Comments:** 3 | **Created:** 2022-11-16 | **Labels:** enhancement, data, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1789

**Is your feature request related to a problem? Please describe.**
I want to develop a new model with Pytorch Geometric  which is a GNN library based on Pytorch. I hope you can develop some api to make it more easier.

**Describe the solution you'd like**
1. Please **develop a obsm_field for AnnDataManager to register obsm(n_obs*n_obs) attribute**. Because [scanpy neighbors](https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.neighbors.html#scanpy.pp.neighbors) save the graph adjacency matrix in obsm as key "connectivities".
2. **DataSplitter in scvi.dataloaders  maybe also should be updated to support minibatch operation**. This minibatch operation is similar to subgraph extraction.

**@adamgayoso:** Thank you for the request.

We are interested in this but have no estimated timeline for when this would be available.

**@HuangDDU:** Is there anyone involved in solving this problem? If not, **can I join this project and solve this problem?** I am interested in **graph deep learning** and hope to integrate this technology into scvi-tools.

**@canergen:** Hi, happy to discuss further. Especially with spatial data graphs are critical but also for single-cell it would be cool. I think best way to get started would be to implement a model in external that uses graph. E.g. https://brbiclab.epfl.ch/projects/stellar/ could be a nice start.

## #1073: adding validation ELBO loss for pyro models
**Issue:** #1073 | **Last activity:** 2024-11-13T09:31:31Z
**State:** closed | **Author:** @vitkl | **Comments:** 3 | **Created:** 2021-05-24 | **Labels:** enhancement, pyro, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1073

Would be great to have validation set ELBO loss for pyro models. As discussed with Adam here https://github.com/YosefLab/scvi-tools/pull/1059#discussion_r633935024
@adamgayoso I can implement this, but could you point me where this belongs?

**@vitkl:** A related warning:

```
  /Users/vk7/anaconda3/envs/scvi-tools-dev/lib/python3.7/site-packages/pytorch_lightning/utilities/distributed.py:69: UserWarning: you passed in a val_dataloader but have no validation_step. Skipping val loop
    warnings.warn(*args, **kwargs)
```

**@adamgayoso:** We need to add a function to this class

https://github.com/YosefLab/scvi-tools/blob/14ac97718c7d50470bf0db25aa7dd6d4f4a245c6/scvi/train/_trainingplans.py#L581

with this signature

https://github.com/YosefLab/scvi-tools/blob/14ac97718c7d50470bf0db25aa7dd6d4f4a245c6/scvi/train/_trainingplans.py#L517

that

1.  runs `evaluate_loss` and then `self.log(..)` it, or
2. returns the loss evaluation then additionally write a method with signature

https://github.com/YosefLab/scvi-tools/blob/14ac97718c7d50470bf0db25aa7dd6d4f4a245c6/scvi/train/_trainingplans.py#L563

That sums over the accumulation of the loss. This would be analogous to what we discussed with averaging/summing during minibatching

**@canergen:** The implementation in https://github.com/scverse/scvi-tools/pull/3015 is correct and can be adjusted for other models.

## #1620: Jax analog for FCLayers
**Issue:** #1620 | **Last activity:** 2024-11-13T09:29:57Z
**State:** closed | **Author:** @RK900 | **Comments:** 0 | **Created:** 2022-07-30 | **Labels:** enhancement, good first issue, jax, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1620

Mentioned by @jjhong922 in #1608 - need a Jax equivalent of the PyTorch FCLayers to reduce redundancy in FlaxEncoder/Decoder

## #3028: TOTALVI.train() Model training has an invalid value error
**Issue:** #3028 | **Last activity:** 2024-11-13T03:10:08Z
**State:** closed | **Author:** @raozuming | **Comments:** 3 | **Created:** 2024-10-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3028

<!-- Describe the bug -->

<!-- To reproduce -->

```python
scvi.model.TOTALVI.setup_mudata(
    mdata,
    rna_layer="counts" if rna_use_raw else None,
    protein_layer="counts" if protein_use_raw else None,
    modalities={
        "rna_layer": "multiomics" if self._use_hvg else "rna",
        "protein_layer": "protein",
    })

total_vi = scvi.model.TOTALVI(mdata, **kwags)
total_vi.train(accelerator=accelerator, devices=devices, **train_kwargs)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
.conda/envs/py310/lib/python3.10/site-packages/mudata/_core/mudata.py:931: UserWarning: Cannot join columns with the same name because var_names are intersecting.
  warnings.warn(
INFO     Computing empirical prior initialization for protein background.
INFO: GPU available: True (cuda), used: True
INFO:lightning.pytorch.utilities.rank_zero:GPU available: True (cuda), used: True
INFO: TPU available: False, using: 0 TPU cores
INFO:lightning.pytorch.utilities.rank_zero:TPU available: False, using: 0 TPU cores
INFO: HPU available: False, using: 0 HPUs
INFO:lightning.pytorch.utilities.rank_zero:HPU available: False, using: 0 HPUs
INFO: LOCAL_RANK: 0 - CUDA_VISIBLE_DEVICES: [0,1,2,3]
.conda/envs/py310/lib/python3.10/site-packages/lightning/pytorch/core/optimizer.py:316: The lr scheduler dict contains the key(s) ['monitor'], but the keys will be ignored. You need to call `lr_scheduler.step()` manually in manual optimization.
.conda/envs …

**@canergen:** Hi, thanks for reporting the issue. Indeed, there's no epsilon on the scale in the decoder and therefore it can get equal to zero. I created a PR with a fix for this. Can you install from this branch and check that it's fixed? https://github.com/scverse/scvi-tools/tree/can_totalvi_decoder_eps

**@raozuming:** @canergen
Thank you, the model training did not go wrong, but the following error occurred: Monitored metric elbo_validation = nan is not finite. Previous best value was inf. Signaling Trainer to stop. The results of protein-related differential analysis are all 0.00000000. Is it because the data is too poor that the results are abnormal? The log is as follows:

.conda/envs/py310/lib/python3.10/site-packages/docrep/decorators.py:43: SyntaxWarning: 'param_categorical_covariate_keys' is not a valid key!
  doc = func(self, args[0].__doc__, *args[1:], **kwargs)
.conda/envs/py310/lib/python3.10/site-packages/mudata/_core/mudata.py:931: UserWarning: Cannot join columns with the same name because var_names are intersecting.
  warnings.warn(
INFO     Computing empirical prior initialization for p …

**@canergen:** This looks like an error that was fixed in scVI-tools 1.2.0. can you please confirm that your installation went correct and you get scVI-tools 1.2.0 as version? Happy to have a look at the data. I don’t think it’s about poor quality, but might be sparsity in one protein.

## #3029: KeyError: 'setup_method_name'
**Issue:** #3029 | **Last activity:** 2024-11-13T03:09:27Z
**State:** closed | **Author:** @ramadatta | **Comments:** 1 | **Created:** 2024-10-24 | **URL:** https://github.com/scverse/scvi-tools/issues/3029

Hi, thank you for the scVI tools.

I am trying to do label transfer as mentioned [here](https://docs.scarches.org/en/latest/hlca_map_classify.html):

I am getting following error with new conda environment and pip installation of scarches.

May I know how this can be resolved? Many thanks in advance!

```
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Cell In[89], line 1
----> 1 surgery_model = sca.models.SCANVI.load_query_data(
      2     adata_query,
      3     ref_model_dir, #reference_model
      4     freeze_dropout=True,
      )

File [~/.local/lib/python3.12/site-packages/scvi/model/base/_archesmixin.py:122](http://127.0.0.1:8888/lab/tree/dir/~/.local/lib/python3.12/site-packages/scvi/model/base/_archesmixin.py#line=121), in ArchesMixin.load_query_data(cls, adata, reference_model, inplace_subset_query_vars, accelerator, device, unfrozen, freeze_dropout, freeze_expression, freeze_decoder_first_layer, freeze_batchnorm_encoder, freeze_batchnorm_decoder, freeze_classifier)
    116 if _SETUP_ARGS_KEY not in registry:
    117     raise ValueError(
    118         "Saved model does not contain original setup inputs. "
    119         "Cannot load the original setup."
    120     )
--> 122 setup_method = getattr(cls, registry[_SETUP_METHOD_NAME])
    123 setup_method(
    124     adata,
    125     source_registry=registry,
   (...)
    128     **registry[_SETUP_ARGS_KEY] …

**@canergen:** Hi, we can't provide support for scArches use of our models. It's better to ask their developers for help. You might want to check our tutorial for the HLCA using Arches mapping: https://docs.scvi-tools.org/en/latest/tutorials/notebooks/scrna/query_hlca_knn.html. Please update if this tutorial doesn't work.

## #3031: Problems of torchmetrics
**Issue:** #3031 | **Last activity:** 2024-10-26T23:37:28Z
**State:** closed | **Author:** @HelloWorldLTY | **Comments:** 3 | **Created:** 2024-10-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3031

### Report

Hi, I notice that the default setting will lead to a problem caused by torchmetrics when importing pertpy:

https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/11648

To fix it, we should use:  torchmetrics==0.11.4

I can create a pull request if necessary.

### Version information

_No response_

**@Zethson:** Dear @HelloWorldLTY,

This might be an issue that you should report to the scvi-tools developers. Torchmetrics is a transitive dependency that we get from them. I'll transfer this to the scvi-tools repository.

**@canergen:** Can you expand on what the issue is with torchmetrics>0.11.4?
I think in our tests it works without the version restriction. Generally, we try to avoid version pinning and fix the underlying issue that is incompatible.
Torch and torchmetrics need to have corresponding versions - conda/pip should handle this. If you use custom install commands, can you share these?

**@HelloWorldLTY:** Hi, I notice that this issue can be resolved by upgrading the version of python to 3.10/3.11. The problem is mentioned here:

https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/11648

## #3022: Cateorical covariate setup
**Issue:** #3022 | **Last activity:** 2024-10-26T04:43:27Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 3 | **Created:** 2024-10-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3022

IGNORE THIS, SEE 2nd COMMENT BELOW

Setting up SCVi with categorical covariates does not seem to work for me. I pulled `main` a few hours ago, working on my SysVI fork - but there are no changes introduced outside of "external"

Minimal reproducibility example:
```
import scanpy as sc
import pandas as pd
import numpy as np
from scvi.model import SCVI

# Setup categorical

a=sc.AnnData(np.zeros((2,3)),obs=pd.DataFrame({'a':[1,2],'b':[3,4]}))

/Users/karin.hrovatin/miniconda3/envs/scvi/lib/python3.10/site-packages/anndata/_core/aligned_df.py:68: ImplicitModificationWarning: Transforming to str index.
  warnings.warn("Transforming to str index.", ImplicitModificationWarning)

SCVI.setup_anndata(a,batch_key='a',categorical_covariate_keys='b')

/Users/karin.hrovatin/Documents/GitHub/scvi-tools-Hrovatin/src/scvi/data/fields/_dataframe_field.py:186: UserWarning: Category 0 in adata.obs['_scvi_batch'] has fewer than 3 cells. Models may not train properly.
  categorical_mapping = _make_column_categorical(
/Users/karin.hrovatin/Documents/GitHub/scvi-tools-Hrovatin/src/scvi/data/fields/_dataframe_field.py:186: UserWarning: Category 0 in adata.obs['_scvi_labels'] has fewer than 3 cells. Models may not train properly.
  categorical_mapping = _make_column_categorical(
Traceback (most recent call last):
  File "/Users/karin.hrovatin/miniconda3/envs/scvi/lib/python3.10/site-packages/IPython/core/interactiveshell.py", line 3577, in run_code
    exec(code_obj, self.user_global_ns, self.user_n …

**@Hrovatin:** Ok, the categorical one was just me being stupid and passing in a wrong input type - a conversion or more meaningful warning would be helpful.

```
>>> a=sc.AnnData(np.zeros((4,3)),obs=pd.DataFrame({'a':[1,2,11,22],'b':[3,4,33,44]}))
/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/anndata/_core/aligned_df.py:67: ImplicitModificationWarning: Transforming to str index.
  warnings.warn("Transforming to str index.", ImplicitModificationWarning)
>>> SCVI.setup_anndata(a,batch_key='a',categorical_covariate_keys=['b'])
/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/scvi/data/fields/_dataframe_field.py:186: UserWarning: Category 0 in adata.obs['_scvi_batch'] has fewer than 3 cells. Models may not train properly.
  categorical_mapping = _mak …

**@canergen:** The typing of the function is correct: categorical_covariate_keys: list[str]. This is also correctly rendered in the API documentation. It expects a list of strings. I don't like loose conversions as what is the conversion of "batch" one can argue that it's ["b", "a", "t", "c", "h"] or ["batch"]. Having a clear API and expecting input that aligns with this is much cleaner.

**@Hrovatin:** @canergen Agree it is correct, but when I messed it up, I took me a while to figure it out since the error you get is way downstream. So maybe adding an error message if the passed object is not a list (or if it is a str/int) would be really useful.

## #3023: Installation jax related packages errs due to deprecations
**Issue:** #3023 | **Last activity:** 2024-10-20T06:59:59Z
**State:** closed | **Author:** @Hrovatin | **Comments:** 3 | **Created:** 2024-10-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3023

I tried installing a fresh scvi env via conda, as per install guide, but got bellow wee on scvi-tools import
```
>>> from scvi.model import SCVI

/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/flax/struct.py:132: FutureWarning: jax.tree_util.register_keypaths is deprecated, and will be removed in a future release. Please use `register_pytree_with_keys()` instead.
  jax.tree_util.register_keypaths(data_clz, keypaths)
/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/flax/struct.py:132: FutureWarning: jax.tree_util.register_keypaths is deprecated, and will be removed in a future release. Please use `register_pytree_with_keys()` instead.
  jax.tree_util.register_keypaths(data_clz, keypaths)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/scvi/__init__.py", line 11, in <module>
    from . import data, model, external, utils
  File "/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/scvi/data/__init__.py", line 25, in <module>
    from ._preprocessing import (
  File "/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/scvi/data/_preprocessing.py", line 12, in <module>
    from scvi.model._utils import parse_device_args
  File "/Users/karin.hrovatin/miniconda3/envs/scvi-test/lib/python3.9/site-packages/scvi/model/__init__.py", line 2, in <module>
    from ._amortizedlda i …

**@canergen:** Hi. Chex is no requirement anymore (is my understanding). Can you print the version of scVI-tools? You want to update to Python>3.9 to install the most recent release.

**@Hrovatin:** The installation guide has python 3.9 fixed: https://docs.scvi-tools.org/en/1.0.4/installation.html#conda
After creating the env I followed the tutorial to install from ` conda-forge`

scvi-tools                1.1.6.post2        pyhd8ed1ab_1    conda-forge

**@canergen:** You should look at the **latest** installation guide (set to 3.12): https://docs.scvi-tools.org/en/latest/installation.html. I looked again at your message and the issue is within optax. It's not on our end to fix it but it's raised in optax https://github.com/google-deepmind/optax/issues/995 and it is their thing to fix it (apparently requirements are ignored by conda).

## #3019: AttributeError: 'Poisson' object has no attribute 'mu' in POISSONVI get_accessibility_estimates
**Issue:** #3019 | **Last activity:** 2024-10-18T15:58:13Z
**State:** closed | **Author:** @shahrozeabbas | **Comments:** 1 | **Created:** 2024-10-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3019

Hello,

I am trying to generate "raw denoised" counts from a trained `POISSONVI` model. This is working for any value set for `library_size` except for when it is set to `latent`.

My understanding is that the counts scaled to the `latent` library size should represent raw counts as much as possible and would like to sum these values for pseudobulk analysis.

Here is my code used to generate the counts as well as the error:

```
model = scvi.external.poissonvi.POISSONVI.load(
    dir_path='models/atac/VC/', adata=adata, accelerator='gpu', device=1
)

adata.layers[counts_layer] = model.get_accessibility_estimates(
    adata=adata, n_samples=2, library_size='latent', return_mean=True,
)
```

Which produces:

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/abbass2/.local/lib/python3.9/site-packages/torch/utils/_contextlib.py", line 116, in decorate_context
    return func(*args, **kwargs)
  File "/home/abbass2/.local/lib/python3.9/site-packages/scvi/external/poissonvi/_model.py", line 215, in get_accessibility_estimates
    accs = super().get_normalized_expression(
  File "/home/abbass2/.local/lib/python3.9/site-packages/torch/utils/_contextlib.py", line 116, in decorate_context
    return func(*args, **kwargs)
  File "/home/abbass2/.local/lib/python3.9/site-packages/scvi/model/base/_rnamixin.py", line 268, in get_normalized_expression
    exp_ = getattr(generative_outputs["px"], generative_output_key)
AttributeError: 'Poisson' object …

**@canergen:** Hi, this should be fixed in scVI-tools 1.2.0.
However, it is not compatible with Python 3.9 anymore so you will need to update your environment. Please reopen if you still experience this issue.

## #3013: Autotune doesn't seem to be able to take learning rate argument anymore
**Issue:** #3013 | **Last activity:** 2024-10-09T05:05:15Z
**State:** closed | **Author:** @LinearParadox | **Comments:** 3 | **Created:** 2024-10-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3013

<!-- Describe the bug -->

Before you could sample LR from a distribution. WHen I try to reimplement similar behavior with autotune, it throws an error on model training.
<!-- To reproduce -->

```python
model_cls = scvi.model.SCVI

model_cls.setup_anndata(adata, layer="counts", batch_key='sample_id')

search_space = {
    "model_params": {"n_hidden": tune.choice([64, 128, 256]),
                     "n_layers": tune.choice([1, 2, 3, 4]),
                     "n_latent": tune.choice([10, 20, 30, 40, 50]),
                     "gene_likelihood": tune.choice(["nb", "zinb"])
                    },
    "train_params": {"max_epochs": 100,
                    "lr":tune.loguniform(1e-4, 1e-2)}
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
(raylet) Traceback (most recent call last):
  File "python/ray/_raylet.pyx", line 1807, in ray._raylet.execute_task
  File "python/ray/_raylet.pyx", line 1908, in ray._raylet.execute_task
  File "python/ray/_raylet.pyx", line 1813, in ray._raylet.execute_task
  File "python/ray/_raylet.pyx", line 1754, in ray._raylet.execute_task.function_executor
  File "/home/ubuntu/miniconda3/envs/scanpy/lib/python3.10/site-packages/ray/_private/function_manager.py", line 726, in actor_method_executor
    return method(__ray_actor, *args, **kwargs)
  File "/home/ubuntu/miniconda3/envs/scanpy/lib/python3.10/site-packages/ray/util/tracing/tracing_helper.py", line 467, in _resume_span
    return method(self …

**@ori-kron-wis:** Hi @LinearParadox ,
Try to do something like:
```
search_space = {
    "model_params": {"n_hidden": tune.choice([64, 128, 256]),
                     "n_layers": tune.choice([1, 2, 3, 4]),
                     "n_latent": tune.choice([10, 20, 30, 40, 50]),
                     "gene_likelihood": tune.choice(["nb", "zinb"])
                    },
    "train_params": {"max_epochs": 100,
                    "plan_kwargs": {"lr": tune.loguniform(1e-4, 1e-2)}}}
```
Should work

**@LinearParadox:** Got it, that worked! I think the tutorial for autotune may have a slight typo related to this:

The search space is:
```
search_space = {
    "model_params": {"n_hidden": tune.choice([64, 128, 256]), "n_layers": tune.choice([1, 2, 3])},
    "train_params": {"max_epochs": 100},
}
```
It says we might get 2 models if we run 2 samples:

```
model1 = {
    "n_hidden": 64,
    "n_layers": 1,
    "lr": 0.001,
}
model2 = {
    "n_hidden": 64,
    "n_layers": 3,
    "lr": 0.0001,
}
```
The learning rate is not set in the search space, however these two seem to have different learning rates. I'm not sure if it's an extra zero, or whether it automatically varies the learning rate.

**@ori-kron-wis:** You are correct, we will change that, thanks for notice!

## #3008: scvi.model.PEAKVI.setup_anndata(adata): AttributeError: type object 'PEAKVI' has no attribute 'setup_anndata'
**Issue:** #3008 | **Last activity:** 2024-10-02T21:05:26Z
**State:** closed | **Author:** @danli349 | **Comments:** 3 | **Created:** 2024-10-02 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/3008

Hello

When I run the code in tutorial https://docs.scvi-tools.org/en/stable/tutorials/notebooks/atac/PeakVI.html

How can I solve this error?
```{python}
scvi.model.PEAKVI.setup_anndata(adata)

---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[11], line 1
----> 1 scvi.model.PEAKVI.setup_anndata(adata)

AttributeError: type object 'PEAKVI' has no attribute 'setup_anndata'
```

```{python}

import os
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pooch
import scanpy as sc
import scvi
import torch

sc.logging.print_header()

2024-10-02 16:02:05.284971: W tensorflow/stream_executor/platform/default/dso_loader.cc:64] Could not load dynamic library 'libcudart.so.11.0'; dlerror: libcudart.so.11.0: cannot open shared object file: No such file or directory; LD_LIBRARY_PATH: /usr/local/lib
2024-10-02 16:02:05.285046: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
scanpy==1.9.8 anndata==0.8.0 umap==0.5.3 numpy==1.23.4 scipy==1.8.1 pandas==1.4.2 scikit-learn==1.3.2 statsmodels==0.12.1 igraph==0.10.8 louvain==0.8.1 pynndescent==0.5.8
```

Thanks a lot

**@canergen:** Please install the most recent version of scvi-tools 1.2.0. We changed the API in (I'm guessing a bit here) 0.16.

**@danli349:** @canergen Why when I use `python -m pip install scvi-tools` to install `scvi-tools`, I can only install ` scvi-tools 0.20.3`?
and can't import it:

```{python}
import scvi
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[4], line 9
      7 import pooch
      8 import scanpy as sc
----> 9 import scvi
     10 import torch
     12 sc.logging.print_header()

File [~/miniconda3/lib/python3.8/site-packages/scvi/__init__.py:7](http://localhost:8888/~/miniconda3/lib/python3.8/site-packages/scvi/__init__.py#line=6)
      4 import logging
      6 from ._constants import REGISTRY_KEYS
----> 7 from ._settings import settings
      9 # this import needs to come after prior im …

**@canergen:** I assume that you use Python 3.8. Please use at least Python 3.10 for the newest release. It looks like your torch installation is broken. Please set up a new environment and follow our installation guideline.

## #2981: total_vi.train()  ValueError: Expected parameter loc (Tensor of shape (256, 20)) of distribution Normal(loc: torch.Size([256, 20]), scale: torch.Size([256, 20])) to satisfy the constraint Real()
**Issue:** #2981 | **Last activity:** 2024-09-26T14:29:50Z
**State:** closed | **Author:** @raozuming | **Comments:** 9 | **Created:** 2024-09-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2981

<!-- Describe the bug -->

[TEXT HERE]

<!-- To reproduce -->

```python
 scvi.model.TOTALVI.setup_mudata(
            mdata,
            rna_layer="counts" if rna_use_raw else None,
            protein_layer="counts" if protein_use_raw else None,
            modalities={
                "rna_layer": "multiomics" if self._use_hvg else "rna",
                "protein_layer": "protein",
            })

  total_vi = scvi.model.TOTALVI(mdata, **kwags)
  total_vi.train()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Traceback (most recent call last):
  File "../../saw_multianalysis/multiAnalysis.py", line 410, in <module>
    run()
  File "../../saw_multianalysis/multiAnalysis.py", line 405, in run
    main(rna_path, protein_path, bin_size, protein_list, out_dir, convert_py_bool(use_gpu), gpu, num_threads,
  File "../../saw_multianalysis/multiAnalysis.py", line 309, in main
    totalVI(rna_data, protein_data, prefix, proteins, out_dir, use_gpu, gpu, num_threads, report)
  File "../../saw_multianalysis/multiAnalysis.py", line 176, in totalVI
    total_vi = ms_data.tl.total_vi(
  File ".conda/envs/multiAnalysis/lib/python3.8/site-packages/stereo/algorithm/total_vi.py", line 142, in main
    total_vi.train(use_gpu=use_gpu, **train_kwargs)
  File ".conda/envs/multiAnalysis/lib/python3.8/site-packages/scvi/model/_totalvi.py", line 299, in train
    return runner()
  File ".conda/envs/multiAnal …

**@canergen:** Please try out our recent changes by installing scvi-tools from the main branch. I hope this is fixed there. Those will be released with scvi-tools 1.2

**@raozuming:** @canergen Thank you for your reply. Since scvi-tools 1.2 requires python > 3.8, I cannot upgrade the python version. Secondly, I tried to manually update the commit you fixed (https://github.com/scverse/scvi-tools/pull/2632/files) to _trainingplans.py, and the problem still occurs.
![image](https://github.com/user-attachments/assets/bb983c86-fe05-4063-ae4e-01285417bd49)

**@mt1022:** I am using python 3.12 and have the same problem when training a `scvi.model.SCVI` model. I tried to install the main branch or the 1.2.x branch and the same error was met.

cmd:

```python
model.train(early_stopping=True, accelerator='cpu')    # same error with "mps"
```

error:
```
File [~/miniforge3/envs/sc/lib/python3.12/site-packages/torch/distributions/distribution.py:70](http://localhost:8890/lab/tree/~/miniforge3/envs/sc/lib/python3.12/site-packages/torch/distributions/distribution.py#line=69), in Distribution.__init__(self, batch_shape, event_shape, validate_args)
     68         valid = constraint.check(value)
     69         if not valid.all():
---> 70             raise ValueError(
     71                 f"Expected parameter {param} "
     72                 f"({ …

**@canergen:** @raozuming We don’t support the use of outdated Python versions. There was an unfortunate stack of activation functions. It is safe to try several runs to get one that succeeds (like 10). If the issue persists, please set up a new environment with a supported Python version 3.10-3.12.
@mt1022 It’s a different issue as it’s a different model. Please check out: https://docs.scvi-tools.org/en/latest/faq.html. It is usually a problem with low count cells that give bad gradients. Please share your dataset size, all parts of your code and verify that your AnnData contains counts.

**@raozuming:** @canergen Thanks for your suggestion, I tried to use python 3.10 version + scvi-tools main branch code, and the related problems were fixed.
![image](https://github.com/user-attachments/assets/6dc9af55-5040-4f81-90b8-b14d768e1ab7)

**@mt1022:** I  reinstalled latest release of scvi-tools and rerun the notebook. The model was successfully trained when setting "accelerator" to cpu. Therefore, the previous error is probably not related to my data. The same error will occur if mps was used. When I rerun only the train line with cpu after mps error, I got the same error too.
Anyway, I can keep using the cpu mode. My dataset has only 40k cells and it took about 20min to train with cpu.

**@canergen:** Unfortunately MPS is not correctly implemented in pytorch and broadcasting is broken: https://github.com/pytorch/pytorch/issues/132605. Training doesn't fail if you use dispersion='gene_label' or similar. However, I don't trust MPS in its current state as we use broadcasting (repeating/reshaping without creating a new object) at several locations in the code. Replacing this would increase runtime and memory consumption. A longer description and the not recommended fix are described at: https://discourse.scverse.org/t/macbook-m1-m2-mps-acceleration-with-scvi/2075/7.

**@raozuming:** @canergen Hello, regarding issue #2981, since it occasionally occurs in the same batch of data, could you please describe the specific reason? Is it caused by the fact that the data of the shape (256, 20) in the protein data is all 0? If it is a data problem, could you provide the filtering conditions to filter the abnormal data externally? Thank you!

**@canergen:** @raozuming Please see https://github.com/scverse/scvi-tools/pull/2913 if you still have this issue in our main branch, please create a new issue and share more information about your data (n_protein, n_cells, n_genes).

## #2257: MultiVI with Poisson/NB likelihood for ATAC?
**Issue:** #2257 | **Last activity:** 2024-09-25T17:29:23Z
**State:** open | **Author:** @vitkl | **Comments:** 8 | **Created:** 2023-09-06 | **Labels:** enhancement, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2257

Hi @martinkim0 and all

Similarly to https://github.com/scverse/scvi-tools/pull/2249 by @lauradmartens would be great to have a MultiVI version with Poisson or even NB likelihood for ATAC data. How hard do you @martinkim0 think it is to add such option to MultiVI?

**@canergen:** Hi @vitkl I'm linking @marianogabitto here as he developed multiVI and was also working on a different implementation of PoissonPeakVI. What's your opinion on this request?

**@lauradmartens:** Yes, I also think it should be relatively straightforward and also remember that @marianogabitto already had an implementation

**@vitkl:** Thanks for getting back to me about this! If you @marianogabitto have an implementation of this - would be great if you could share it or add it to scvi-tools (if makes sense for @canergen)

**@canergen:** Happy to review the PR.

**@vitkl:** I don't understand the implementations well enough to easily try implementing this - but I can do a PR if I see the example implementation from @marianogabitto

**@canergen:** I'm sorry for the confusion that was a comment to @marianogabitto to assign me the PR if he creates one.

**@judilly:** Hi all, I am very interested in this implementation and I'm curious to know if there is any updates on it?
Thanks!

**@canergen:** @lauradmartens congrats on the new manuscript: https://www.biorxiv.org/content/10.1101/2024.09.19.613754v2. Any plan to continue with the Poisson MultiVI branch.

## #2992: Device management
**Issue:** #2992 | **Last activity:** 2024-09-24T22:52:45Z
**State:** closed | **Author:** @canergen | **Comments:** 5 | **Created:** 2024-09-23 | **URL:** https://github.com/scverse/scvi-tools/issues/2992

1. Use TOTALVI.train(accelerator = 'cpu', devices = 1), the program detects the GPU environment, and still uses the GPU for training. As shown in the figure below, due to my GPU driver, the GPU reports an error, indicating that the program still uses GPU resources for training instead of CPU resources
![30F79B4C-0EEC-47af-B4FF-9B3CE725E988](https://github.com/user-attachments/assets/7effd33d-2c09-4723-a5f0-44516ab24c87)

2. How to use multi-core CPU for model training

_Originally posted by @raozuming in https://github.com/scverse/scvi-tools/issues/2889#issuecomment-2367582829_

**@canergen:** Please don't post issues that are unrelated. Especially not in releases. Torch uses by default multiple workers. I can't reproduce that using accelerator='cpu' doesn't disable the GPU. Which version of scvi-tools are you using? You can also set cuda visible devices to `os.environ["CUDA_VISIBLE_DEVICES"]=""` at the top of your script. Lastly, I would not recommend installing a CUDA version of torch and don't install correct drivers and would recommend updating CUDA drivers to a more recent version.

**@raozuming:** @canergen
Hello, Since the use_gpu parameter in TOTALVI.train() has been cancelled, I can only use the accelerator and devices parameters to replace the previous function. However, according to the maintainer, accelerator='cpu', devices=1 will schedule CPU resources for model training, but I cannot achieve it at present.
![9E62E543-62F1-4989-A9CE-CEE7D73B37D8](https://github.com/user-attachments/assets/84f064f5-6d37-4699-b8f1-020dd614a7cb)


python：3.10
scvi-tools: 1.2.x  commit: df33149

**@canergen:** It will train using the CPU (you can see in your screenshot that it is correctly set). However, you are using a broken CUDA (outdated) and torch tries using CUDA as it’s installed with CUDA support. This doesn’t work. Please fix your CUDA or reinstall torch without CUDA support. I highlighted above ways to fix it. Please follow those.

**@raozuming:** Thanks

**@canergen:** Assuming it’s fixed.

## #2941: lightning dependency critical CVE - Update dependency list, especially for conda which is pinned below the CVE patch
**Issue:** #2941 | **Last activity:** 2024-09-23T15:39:45Z
**State:** closed | **Author:** @pranavmishra90 | **Comments:** 4 | **Created:** 2024-08-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2941

<!-- Describe the bug -->

conda package feedstock has a `lightning` package dependency of "[lightning >=2.0,<2.1](https://github.com/conda-forge/scvi-tools-feedstock/blob/main/recipe/meta.yaml)" which is different from the pypi dependency of "[lightning>=2.0](https://github.com/scverse/scvi-tools/blob/main/pyproject.toml)".

`lightning` has a a critical level of CVE reported https://github.com/advisories/GHSA-mr7h-w2qc-ffc2, with a patch in version 2.3.3. Recommend bumping the dependency for scvi-tools before v1.2 (#2889) after testing.

The pip package may automatically pick up the latest version of `lightning`. However, the conda package installer is preventing it from being installed

<!-- To reproduce -->

```yaml
 ## snippet of environment.yaml
  - python=3.11
  - lightning>=2.3.3
  - scvi-tools=1.1
```
```bash
## generating a conda-lock file
conda-lock --mamba --kind lock -p linux-64 -f environment.yml --with-cuda 12.4 --lockfile ./tmp/conda-lock.yml
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```bash
└─ scvi-tools 1.1**  is not installable because it requires
   └─ lightning >=2.0,<2.1 , which conflicts with any installable versions previously reported.
```

This is expected because:

```bash
conda search scvi-tools=1.1.5 --info -c conda-forge

Loading channels: done
scvi-tools 1.1.5 pyhd8ed1ab_0
-----------------------------
file name   : scvi-tools-1.1.5-pyhd8ed1ab_0.conda
na …

**@ori-kron-wis:** For SCVI-tools v1.1 we have "lightning>=2.0,<2.2"  so that might be the root cause for the thing you see in the feedstock repo for v1.1.6

We now aim to release scvi-tools v1.2

Their most updated version in conda is indeed 2.4v

I updated the version localy in both 1.2.x and 1.1.x and all PR tests passed, but we need to have more thorough tests before we update this version, @canergen we can re-run all notebooks with this update and see. what do you say?

**@canergen:** Fixed in scvi-tools 1.1.6

**@jdblischak:** To clarify:

* The `lightning<2.1` upper bound was removed in [1.1.6.post1](https://github.com/scverse/scvi-tools/releases/tag/1.1.6.post1) (xref: https://github.com/conda-forge/scvi-tools-feedstock/issues/54#issuecomment-2351483316)
* To install the latest lightning, please install either 1.1.6.post1 or preferably 1.1.6.post2 (available via conda-forge or PyPI)

**@canergen:** To clarify, post2 upper bounds AnnData. The upper bound will be removed in scVI-tools 1.2. This was necessary to remain compatible with Python 3.9.

## #2432: Update typing in all files to match new format
**Issue:** #2432 | **Last activity:** 2024-09-21T04:42:17Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 2 | **Created:** 2024-01-25 | **Labels:** enhancement, good first issue, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2432

**@ori-kron-wis:** This issue is solved to large extent in PR https://github.com/scverse/scvi-tools/pull/2932 (custom dataloaders). So following that there will be less places to fix.

**@canergen:** Addressed in #2956. Rule introduced to keep this formatting in the future.

## #2262: MultiVI Tensor shape invalid values nan
**Issue:** #2262 | **Last activity:** 2024-09-21T04:41:48Z
**State:** closed | **Author:** @bhhlee | **Comments:** 4 | **Created:** 2023-09-13 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2262

I am trying to use multivi on a paired 10x multiome (rna+atac) dataset. I've taken the mudata object with raw counts and made it into an anndata object for MultiVI. However, when I get to training the model, it fails before the first epoch. I've seen several similar issues here, but none of those solutions seem to be working.

I have a 161598 cells x 195122 obs matrix with only paired data.

```
adata_paired = ad.concat([rna.copy().T, atac.copy().T]).T
adata_paired.obs = adata_paired.obs.join(rna.obs['sample'])
adata_paired.obs["modality"] = "paired"
adata_paired
```
```
CPU times: user 49.5 s, sys: 8.99 s, total: 58.5 s
Wall time: 58.5 s
AnnData object with n_obs × n_vars = 161598 × 195122
    obs: 'sample', 'modality'
    var: 'gene_ids', 'feature_types', 'genome', 'interval'
```

```
mvi = scvi.model.MULTIVI(
    adata_paired,
    n_genes=n_genes,
    n_regions=n_regions,
)
mvi.view_anndata_setup()
```
![image](https://github.com/scverse/scvi-tools/assets/41644247/47b02ff4-96a9-4e12-bd74-5a22be6a6f1d)

```
mvi.train(use_gpu=False)
```
```
GPU available: True (cuda), used: False
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
Epoch 1/10:   0%|                                        | 0/10 [00:00<?, ?it/s]
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
File <timed eval …

**@martinkim0:** Hi, if you're able to, could you please share the data you're using?

**@Xinle-Deng:** I encountered the same error. The issue might be associated with the 'adversarial_mixing' argument in the 'train' method which is set to 'True' by default. In your scenario, as the dataset contains only one batch, there is no need to do adversarial training. Therefore, it is advisable to manually set 'adversarial_mixing' to 'False'. When 'adversarial_mixing' is set to 'True,' 'n_class – 1' equals 0. Division by zero leads to the occurrence of NaN.

**@WeilerP:** @martinkim0, you can reproduce the issue with the data used in the MultiVI tutorial:

```python
import gzip
from pathlib import Path

import pooch

import scanpy as sc
import scvi

save_dir = tempfile.TemporaryDirectory()

def download_data(save_path: str, fname: str = "pbmc_10k"):
    data_paths = pooch.retrieve(
        url="https://cf.10xgenomics.com/samples/cell-arc/2.0.0/pbmc_unsorted_10k/pbmc_unsorted_10k_filtered_feature_bc_matrix.tar.gz",
        known_hash="872b0dba467d972aa498812a857677ca7cf69050d4f9762b2cd4753b2be694a1",
        fname=fname,
        path=save_path,
        processor=pooch.Untar(),
        progressbar=True,
    )
    data_paths.sort()

    for path in data_paths:
        with gzip.open(path, "rb") as f_in:
            with open(path.repl …

**@canergen:** Fixed in main and will be released with 1.2.0 next week.

## #2968: ValueError: "high is out of bounds for int32" when running setup_anndata on large AnnData object
**Issue:** #2968 | **Last activity:** 2024-09-21T04:37:20Z
**State:** closed | **Author:** @Ron-bio | **Comments:** 10 | **Created:** 2024-09-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2968

<!-- Describe the bug -->

I encountered a `ValueError: high is out of bounds for int32` when using `scvi.model.SCVI.setup_anndata` on a large AnnData object that contains more than 200,000,000 cells. If I subset the anndata, the error no longer exists.
<!-- To reproduce -->

```python
scvi.model.SCVI.setup_anndata(adata, layer='counts', batch_key="batch")
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[
...scvi\data\_utils.py:271, in _check_nonnegative_integers(data, n_to_check)
    269 ret = True
    270 if len(data) != 0:
--> 271     inds = np.random.choice(len(data), size=(n_to_check,))
    272     check = jax.device_put(data.flat[inds], device=jax.devices("cpu")[0])
    273     negative, non_integer = _is_not_count_val(check)...

ValueError: high is out of bounds for int32]
```

#### Versions:

<!-- Output of scvi.__version__ -->

> Last run with scvi-tools version: 1.1.6

<!-- Relevant screenshots -->

**@canergen:** Hi, curious to hear more about the performance of scvi-tools on this huge dataset and am happy to give more guidance on running it. It looks like you use a 32-bit python here. Can you confirm this with:
```
import platform
platform.architecture()[0]
```
If the error persists on a 64-bit python version. Can you also update to the most recent scvi-tools version from main? This code block was slightly updated for our 1.2 release and the error might be fixed there.

**@Ron-bio:** Hi @canergen,

Thank you so much for your prompt response and the guidance!

I have tried the ```platform.architecture()[0]``` command, and the output is ```64bit```, so it seems the issue is not related to a 32-bit Python version.
As for the scvi-tools version, I noticed that the 1.2 version is currently in an unreleased state. The 1.1.6 version was installed through ```pip install scvi-tools```
Looking forward to your advice and suggestions!

**@canergen:** In a 64-bit numpy the error is (so 200 million cells would be no issue):
```
np.random.choice(2000000000000000000000000, size=(100,))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "numpy/random/mtrand.pyx", line 997, in numpy.random.mtrand.RandomState.choice
  File "numpy/random/mtrand.pyx", line 781, in numpy.random.mtrand.RandomState.randint
  File "numpy/random/_bounded_integers.pyx", line 1332, in numpy.random._bounded_integers._rand_int64
ValueError: high is out of bounds for int64
```
It's pretty clearly a numpy problem that assumes 32bit on your end. This is usually a 32bit python in your container. Can you run the specific line in python and see whether you get an error (it's important to run in the same session and same interpreter).
In …

**@Ron-bio:** Hi @canergen,

Thank you for your help. After checking my environment, I found that while my Python installation is 64-bit, Numpy appears to be 32-bit. I suspect this mismatch is causing the issue. I'm using Anaconda on Windows, which might be the source of the problem. I'll try running this on a Linux platform to see if that resolves it.

**@ilan-gold:** @Ron-bio @canergen I think this is a windows issue, see: https://github.com/scverse/scanpy/issues/2969 and https://github.com/scverse/scanpy/pull/2976

**@canergen:** I'm sorry, this message was wrong. @ilan-gold Thanks for the pointer. Does np.Generator fix it? I commented out the formatting rule that is enforcing its use as I find it quite bulky.
In the bigger picture, I think both of us have the same "issue" that we can't test Windows-specific things and Windows support therefore is limited. Given scanpy doesn't support working with large data on Windows, we won't fix it for now. CustomDataloader in scvi-tools, which are currently experimental, will allow training models on large data.

**@Ron-bio:** @canergen Thank you for the prompt response! I resolved the previous error by creating a new Anaconda environment on windows and installing the latest version of scvi-tools. I’m now able to proceed with the subsequent analyses without any issues. Only one warning was encountered that does not affect the analysis:
```..\Anaconda3\envs\scvi\lib\site-packages\lightning\pytorch\trainer\connectors\data_connector.py:424: The 'train_dataloader' does not have many workers which may be a bottleneck. Consider increasing the value of the `num_workers` argument` to `num_workers=15` in the `DataLoader` to improve performance.```

```../Anaconda3/envs/scvi/lib/site-packages/lightning/pytorch/trainer/connectors/data_connector.py:424): The 'val_dataloader' does not have many workers which may be a bot …

**@canergen:** Can you provide any differences between both environments? This might be helpful if the same issue arises for other users.
This num_worker warning is a PyTorch thing. Before the release of scVI-tools 1.2 and allowing persistent workers more workers might actually be slower as our models are quite small.

**@Ron-bio:** Here are the env info that may be relevent:
The current env info:
```
name: scvi
dependencies:
  - python=3.9.19=h4de0772_0_cpython
  - pip:
      - numba==0.60.0
      - numpy==1.26.4
      - pandas==2.2.2
      - scanpy==1.10.3
      - scvi-tools==1.1.6.post2
```
The info from env pysc with int32 error:
```
name: pysc
dependencies:
  - python=3.9.17=h4de0772_0_cpython
  - pip:
      - numba==0.57.1
      - numpy==1.24.4
      - pandas==2.2.2
      - scanpy==1.9.3
      - scvi-tools==1.1.6
```

**@canergen:** Thanks for reporting. Great that it's working now. Closing here.

## #2331: batch and max_kl_weight parameters ignored when mapping to scvi reference
**Issue:** #2331 | **Last activity:** 2024-09-19T16:38:19Z
**State:** closed | **Author:** @LisaSikkema | **Comments:** 8 | **Created:** 2023-11-22 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2331

Hi! I have been trying to map data to scvi-integrated embeddings using scArches, and have noticed that for the two scVI-based reference models I have used, setting the `max_kl_weight` parameter differently has no effect on the output. The same holds for changing the batch assignment of the query cells (e.g. using sample rather than dataset as batch covariate). I do not see the same problem with an scANVI-model I have used.

Here's a reproducible example of the first issue:

```python
import scarches as sca
import scanpy as sc
ref_model_dir = "./ref_model"
adata_query_unprepped = sc.read_h5ad("./PeerMassague2020_subset_for_testing.h5ad")
mapped_embeddings = dict()
kl_weights_to_test = [0.1, 1, 2]
# map with three different max_kl_weights:
for max_kl_weight in kl_weights_to_test:
    adata_query = sca.models.SCVI.prepare_query_anndata(
        adata=adata_query_unprepped, reference_model=ref_model_dir, inplace=False
    )
    surgery_model = sca.models.SCVI.load_query_data(
        adata_query,
        ref_model_dir,
        freeze_dropout=True,
    )
    surgery_model.train(plan_kwargs={"weight_decay": 0.0, "max_kl_weight":max_kl_weight})
    mapped_embeddings[max_kl_weight] = sc.AnnData(surgery_model.get_latent_representation(adata_query))
# compare output embeddings:
print((mapped_embeddings[0.1].X == mapped_embeddings[1].X).all())
print((mapped_embeddings[0.1].X == mapped_embeddings[2].X).all())
```

Which outputs the following (most importantly, …

**@martinkim0:** Hi, thank you for your question. This is because, based on our current defaults, the scVI encoder does not receive batch assignments ([`encode_covariates=False`](https://docs.scvi-tools.org/en/stable/api/reference/scvi.module.VAE.html)) such that changing the batch covariate will not affect the latent representation.

In addition, scArches by default freezes pretrained model parameters (_i.e._ parameters not related to covariates), which is why training the reference model on the query data with different max KL weights does not change the latent representation (see the last section in our [user guide](https://docs.scvi-tools.org/en/stable/user_guide/background/transfer_learning.html)).

These should both, however, have an effect on the decoder output (normalized expression).

**@LisaSikkema:** Thanks a lot for the quick response!

I'm not sure if I understand though: I get that the model parameters for calculating the reference embedding aren't changed, but this should still allow for changing parameters specific for the query right? That's also how I read the user guide you linked to:
>the training of the model with the query data is performed with respect to only the new query-category specific parameters.

As for the batch covariate not affecting the latent representation of the query: how could we still expect the mapping to perform any batch correction in that case?

Is there any way in which I can still change these settings at the stage of mapping, or should it have been done already when the reference model was trained?

**@martinkim0:** > I get that the model parameters for calculating the reference embedding aren't changed, but this should still allow for changing parameters specific for the query right?

Right - since the only query-specific parameters added during transfer learning (by default) are the parameters accommodating the new batch covariate categories, these will be updated. Admittedly, this seems a little limited since we end up only updating the decoder, so not exactly sure why we can expect the model to batch correct query data well. But this is the default we have and are currently not changing it due to backwards compatibility.

Pre reference model training, you can change this behavior by specifying `encoder_covariates=True` during model initialization, the result being that part of the encoder (and …

**@LisaSikkema:** Okay interesting!
It actually sounds like the current default defeats the purpose of scArches as a whole, with no batch correction being performed during the mapping (at least at the level of the latent embedding). Probably also relevant for @M0hammadL to be aware of.
Maybe good to at least stress this very clearly this in the scVI tutorials, to explain that query-to-reference mapping is only really possible later on if `encoder_covariates=True` has been set during reference model training.

I'm not so much interested in re-training the reference model, but more in being able to set the way the query model is trained (i.e. including batch already in the encoder, and changing the max_kl_weight setting). If I understand the documentation correctly, that is not really possible with the …

**@martinkim0:** Good point - probably a good idea to point this out in the tutorials. I wasn't involved in writing this part of scvi-tools, so I'll also double check that this is actually what is happening, but from what I recall, this is the case with our defaults.

Yeah, encoding batch information when the reference model has already been trained without it is not possible yet. For max KL weight, I do believe the changes should be reflected during query training, but let me double check.

**@canergen:** Getting into the thread here, in all scArches tutorials it's highlighted that covariates are encoded. In our hands it doesn't make a difference for most datasets. OOD things shouldn't be done (like taking an sc model and using sn query). However, generally when reusing a model it always makes sense to check that integration was working and posterior predictive checks look good (in short reconstruction loss in query and reference is similar). This will be stressed in our publication encompassing scVI-criticism.

**@LisaSikkema:** Thanks for your responses!

Right yes in the scArches tutorials the covariates are set that way (although not explained as far as I remember, so it might not be clear to users that those settings are important not to change), but they're not set that way nor discussed in the scVI /scANVI tutorials I think. Most people won't go through an scArches tutorial already when they're still integrating the data, and will only realize that their model isn't really scArches-friendly once they have already done a lot of quality checks and downstream analysis on their integration, and don't want to re-do it anymore. I have already experienced it with two large atlas integrations that I worked with in the past weeks.

Also, for me it makes quite a large difference to set parameters differently in th …

**@canergen:** We added a comment to the tutorial to highlight this.

## #2955: installation error when import scvi in conda/pip
**Issue:** #2955 | **Last activity:** 2024-09-19T16:36:39Z
**State:** closed | **Author:** @biobai | **Comments:** 3 | **Created:** 2024-08-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2955

Hi all
I follow the Installation (https://docs.scvi-tools.org/en/stable/installation.html)
```bash
mamba create -n scvi-env python=3.9
mamba activate scvi-env
mamba install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
mamba install jax jaxlib -c conda-forge
mamba install scvi-tools -c conda-forge
```
or
```bash
pip install scvi-tools
```
How to fix this error?
```python
Python 3.9.19 | packaged by conda-forge | (main, Mar 20 2024, 12:50:21)
Type 'copyright', 'credits' or 'license' for more information
IPython 8.18.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import scvi
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[1], line 1
----> 1 import scvi

File ~/miniforge3/envs/scvi-env/lib/python3.9/site-packages/scvi/__init__.py:11
      8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import
---> 11 from . import data, model, external, utils
     13 from importlib.metadata import version
     15 package_name = "scvi-tools"

File ~/miniforge3/envs/scvi-env/lib/python3.9/site-packages/scvi/data/__init__.py:3
      1 from anndata import read_csv, read_h5ad, read_loom, read_text
----> 3 from ._anntorchdataset import AnnTorchDataset
      4 from ._datasets import (
      5     annotation_simulation,
      6     brainlarge_dataset, …

**@canergen:** Hi, it looks like you don’t have a working JAX installation? Can you follow their installation guide and quick start guide: https://jax.readthedocs.io/en/latest/quickstart.html. Please let us know if your JAX installation is good and scVI-tools creates the problems. Specifically it looks like you installed a JAX TPU version. We never tested scVI-tools on TPUs but only on CUDA and CPU.

**@yz3n18:** Hi! I had a similar problem while following the installation tutorial.
Reinstalling the flax package with version 0.8.5 solved the issue. You can do this by running:
`pip install flax==0.8.5`
Hope this helps.


> TypeError                                 Traceback (most recent call last)
> Cell In[1], line 4
>       2 import tempfile
>       3 import scanpy as sc
> ----> 4 import scvi
>       5 import seaborn as sns
>       6 import torch
>
> File ~/.conda/envs/scvi-env/lib/python3.9/site-packages/scvi/__init__.py:11
>       8 from ._settings import settings
>      10 # this import needs to come after prior imports to prevent circular import
> ---> 11 from . import data, model, external, utils
>      13 from importlib.metadata import version
>      15 package_name = "sc …

**@canergen:** Thanks. I think both are unrelated (the one you are highlighting is in flax and the one originally described is in device management). Unfortunately, jax and its subpackages sometimes create version conflicts. There is little we can do to fix it except being compatible with the most recent jax version. If jax is correctly installed those issues both should be gone.

## #1176: User guide: Counterfactuals
**Issue:** #1176 | **Last activity:** 2024-09-19T16:35:16Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 2 | **Created:** 2021-09-27 | **Labels:** user guide, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/1176

**@martinkim0:** For this, we can discuss how to use `transform_batch`. Also discuss mrVI.

**@canergen:** Adressed by #2960

## #2958: Fix the progress bar during training models trough tout the tutorials
**Issue:** #2958 | **Last activity:** 2024-09-17T21:08:22Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-04 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2958

Is your feature request related to a problem? Please describe.
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

We would like to be able to show the tqdm progress bar in our RTD , but not as it shown now where every epoch is shown interactively. We do want to keep the bottom line of training bar.

Describe the solution you'd like
A clear and concise description of what you want to happen.

We would want to re check the custom progress bar code . the reason that code exists is because the docs used to not render the tqdm notebook mode and it used to be that when you saved a jupyter notebook and reopened the fancier progress bar disappears
Not sure if it’s still a problem

We will have to create a branch and fix the code while testing it by running a test notebook in the scvi-tutorials repo running this branch

## #2967: change 1.1.6 release requirements
**Issue:** #2967 | **Last activity:** 2024-09-16T16:16:04Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 5 | **Created:** 2024-09-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2967

we should re-release 1.1.6. with 2 changes to able to meet RTD autotune requirements as well as the conda forge recipe:
- Drop lightning upper bound -  see https://github.com/conda-forge/scvi-tools-feedstock/issues/54
- Add optional setuptools<=69.5.1 for tune parrt so RTD will work for the autotune version that is still in use for scvi 1.1.x
- finally, we should also increment this build number to 2 (if continue the same release, otherwise, we can release as 1.1.6.post1)

**@jdblischak:** > we should re-release 1.1.6. with 2 changes

Just to clarify what you mean by "re-release 1.1.6", you are going to bump the version number, right? Something like 1.1.6.1 or 1.1.7?

**@canergen:** @jdblischak Our idea was to release 1.1.6.post1. Would this work for conda or should we change the build of 1.1.6 and release 1.1.7 without those requirements? I'm slightly puzzled about the feedstock rules.

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/pull/2969

**@jdblischak:** > Our idea was to release 1.1.6.post1. Would this work for conda

@canergen Yes, that version number is fine. Any valid Python package version should also be a valid [conda recipe version](https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#package-version).

**@jdblischak:** Confirming my understanding.

1.1.6post1 dropped the `lightning<2.2` upper bound via https://github.com/scverse/scvi-tools/pull/2969:

https://github.com/scverse/scvi-tools/compare/1.1.6...1.1.6.post1

And 1.1.6post2 also added the upper bound `anndata<=0.10.8` via https://github.com/scverse/scvi-tools/pull/2971:

https://github.com/scverse/scvi-tools/compare/1.1.6.post1...1.1.6.post2

## #2966: Drop python 3.9 and replace with python 3.12
**Issue:** #2966 | **Last activity:** 2024-09-16T09:30:36Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2966

As python 3.9 is not scientifically supported anymore, we should remove it and replace it with Python 3.12 both in the requirement and in the automated tests for v1.2
See https://scientific-python.org/specs/spec-0000/

## #2965: potential issue with zinb / nb loss
**Issue:** #2965 | **Last activity:** 2024-09-15T03:39:34Z
**State:** closed | **Author:** @jkobject | **Comments:** 3 | **Created:** 2024-09-10 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2965

Hi,

I have had some issues using the zero inflated negative binomial as well as the negative binomial loss from scvi. They seem to have issues of convergence and overflow. I have made an example notebook here [test_zinb.ipynb](https://scverse.zulipchat.com/user_uploads/41224/OKtSWovIUA-aVxp0rYTWm-p5/test_zinb.ipynb) but also talk about it in my the methods section of my manuscript: https://www.biorxiv.org/content/10.1101/2024.07.29.605556v1

It seems that there cannot be convergence to 0 but roughly 1.1 (depending on read depth) and that the model is not pushed to predict the exact values as the loss values don't change around some prediction accuracy. Worse, the loss can get even better with some error in the prediction of the mu. (see example with an error) Worse even, above some values of inverse dispersion (10_000), the use of logGamma causes overflow error and the loss to be nonsensical.

There might be something I did not understood on my end or don't do right. But I think the fact that the log gamma are used is an issue and causes imprecisions. I would be happy to work on this otherwise as I think it is quite important to get right.

Best,

**@jkobject:** reuploading the notebook: https://gist.github.com/jkobject/35eefa7ca3c314e6d13bbc1070d4c15b

**@canergen:** Continuing the discussion in our Zulip chat.

**@canergen:** Closing here. If anyone wants to follow it, you can join the scverse Zulip channel. To summarize, our loss provides similar results to the torch NB loss. This is not an implementation error but it's not clear that NB is optimal for all applications.

## #2393: Multimodal reference mapping with MuData objects
**Issue:** #2393 | **Last activity:** 2024-09-12T15:21:05Z
**State:** closed | **Author:** @ethanweinberger | **Comments:** 6 | **Created:** 2024-01-17 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2393

In the current (1.0.4) version of scvi-tools, multimodal models (e.g. totalVI) can be set up and trained with either AnnData or MuData objects. Thus, it would be nice to be able to perform reference atlas mapping using either workflow (i.e., using an AnnData-based totalVI or MuData-based totalVI model). However, it appears that the [ArchesMixin API](https://docs.scvi-tools.org/en/1.0.2/api/reference/scvi.model.base.ArchesMixin.html) was designed only to handle AnnData objects. Indeed, when attempting to naively pass MuData objects into the ArchesMixin functions to perform reference mapping with totalVI I quickly ran into errors (notebook reproducing my results available here: https://colab.research.google.com/drive/1lL1JJ3bdG6UU3XVjA0tLvp1V2QLWihuI?usp=sharing).

@martinkim0 I'd be happy to take this on since I don't think it should be too much work to handle the MuData case- would you prefer to keep the current two function user-facing API (i.e., `load_query_data` and `prepare_query_anndata`) and handle the MuData case internally or explicitly have separate functions for MuData objects (e.g. `prepare_query_mudata`)?

**@martinkim0:** Thanks for bringing up this issue! I think it makes sense based on how we've named our `ArchesMixin` API to implement `prepare_query_mudata`, which I anticipate will have much different code from `prepare_query_anndata`, and add MuData support to the existing `load_query_data`, since this method mostly deals with freezing network layers.

Let me know what you think, and we can go forward from there.

**@ethanweinberger:** Makes sense to me! I've added this to my to-do list, and should hopefully have an initial implementation ready for review within the next week or two.

**@ethanweinberger:** Hey @martinkim0! Apologies for the (large) delay here. I just opened an initial PR addressing this (#2578) though I think my current way of accomplishing this is too hacky and would love to hear your thoughts on a more elegant way forward.

**@tomsing1:** @martinkim0  and @ethanweinberger Thanks a lot for working on this issue. I just tried to run the [example notebook](https://colab.research.google.com/drive/1lL1JJ3bdG6UU3XVjA0tLvp1V2QLWihuI?usp=sharing) with version with `scvi-tools` version 1.1.6 and still got the same error @ethanweinberger originally reported:

```
query_model = scvi.model.TOTALVI.load_query_data(
    mdata_query,
    ref_model,
)

[stack truncated]

TypeError: TOTALVI.setup_anndata() missing 1 required positional argument: 'protein_expression_obsm_key'
```

Perhaps `TOTALVI.load_query_data()` is still not ready to accept a MuData query? Maybe this issue needs to be reopened?

**@canergen:** Hi, this change is not part of 1.1.6 but will be part of 1.2.0. You can test it by installing from our main branch. Please reopen, if it’s not working for you. Thanks!

**@tomsing1:** Oh, I see - thanks for the clarification. And many thanks for creating such an amazing toolkit!

## #1992: MultiVI for trimodal integration
**Issue:** #1992 | **Last activity:** 2024-09-11T09:39:30Z
**State:** closed | **Author:** @tt2190 | **Comments:** 10 | **Created:** 2023-04-04 | **Labels:** enhancement, multivi | **URL:** https://github.com/scverse/scvi-tools/issues/1992

Thanks so much for developing the scVI tools.

I have CITE-seq, 10x multiome and unimodal scATAC data from the corresponding tissue of multiple donors and hope to put them together and perform an integrated analysis of the trimodal (RNA, protein, ATAC) data.

I was considering [Multigate](https://github.com/theislab/multigrate) from Theis Lab, but I have just realised that MultiVI has been trying to support protein information (#1712) and [_multivi.py](https://github.com/scverse/scvi-tools/blob/main/scvi/model/_multivi.py) has been updated to accept protein input.

I would be grateful if you could enlighten me on the current recommendation regarding the use of MultiVI for this trimodal integration scenario.

**@marianogabitto:** Hello tt (not sure your name),
                             is there anything that you would like to know? MultiVI works for protein information.

Cheers,
Mariano

**@tt2190:** Hi Mariano,

Thank you very much for your reply. My apologies for not being clear in my original post.

I wanted to ask if MultiVI works for trimodal integration scenarios, as the MultiVI [paper](https://www.biorxiv.org/content/10.1101/2021.08.20.457057v2) and [documentation](https://docs.scvi-tools.org/en/stable/user_guide/models/multivi.html) do not mention its applicability for protein data or for integration of three modalities.

Have you released any tutorial for trimodal integration (e.g. CITE-seq + 10x multiome)?

Many thanks,
Tomo

**@marianogabitto:** Hi Tomo,
           protein information has to enter as in TotalVI, in the .obsm field of the anndata. Can you give it a try and let me know?

M

**@tt2190:** Hi Mariano,

Thank you for clarifying this point. I will let you know once I get the results!

Many thanks,
Tomo

**@tt2190:** Hi Mariano,

I have tried integration of CITE-seq + multiome using the datasets used in the totalVI and MultiVI tutorials:
CITE-seq: scvi.data.pbmcs_10x_cite_seq()
multiome: https://cf.10xgenomics.com/samples/cell-arc/2.0.0/pbmc_unsorted_10k/pbmc_unsorted_10k_filtered_feature_bc_matrix.tar.gz

I have specified `protein_expression_obsm_key="protein_expression"` when I setup the anndata with `scvi.model.MULTIVI.setup_anndata`. However, it seems that the protein_foreground_probability has not been computed.
Could you please give me some additional guidance on how to integrate protein information into the MultiVI workflow?

My analysis notebook is available from the following link:
https://www.dropbox.com/s/n8uzw2wfzoqnlnu/trimodal_MultiVI_test.ipynb?dl=0

I have also realised that …

**@marianogabitto:** Hi Tomo,
        sorry for the delay. We are running the last edits on the manuscript and I will work on the tutorial soon. I will based it on your notebook actually ! Thanks for sharing it.

        At a first pass, you did everything right. Let me work on the example myself and get back to you in 2 days.

Thanks,
Mariano

**@tt2190:** Hi Mariano,

Thank you for your reply.

Performance-wise, as shown in my notebook, the CITE-seq and multiome data were completely separated (not integrated) after model training. This may be because I don't currently have GPU available and I tested with max_epochs=150 to save runtime on CPU, but I was also concerned if I was doing something wrong other than #epochs. Therefore, it would be very helpful if I could learn from your tutorial.

Thank you for your time and help and I look forward to hearing from you soon!

Thanks,
Tomo

**@marianogabitto:** Tomo, I will work on this and I should cite you as a reference in the tutorial for helping with this. We should connect outside this thread to make the tutorial happen !

**@fimunty:** Hello there,

Is there an update on this issue?

I see that it has been marked as completed, but I can't find the mentioned tutorial anywhere on the scvi website. Further, when trying to use ~~`setup_multiome_anndatas`~~ `organize_multiome_anndatas` with an anndata with protein I encouter an error since the index of the protein data doesn't match the obs_names of the newly created anndata anymore.
I understand that I can work around using ~~`setup_multiome_anndatas`~~ `organize_multiome_anndatas`, but what is the intended way of preparing data with protein expression for MultiVI?

Thank you and best,
Fiona

Edit: Correct function name.

**@canergen:** There exists no tutorial. I was suggesting how to fix it. We have an open issue to switch to MuData which would be the correct way IMO to fix this. However, there is no timeline for this. @marianogabitto Any suggestions?

## #2963: I am getting ZeroDivisionError, any solution in solving this?
**Issue:** #2963 | **Last activity:** 2024-09-09T17:49:25Z
**State:** closed | **Author:** @yojetsharma | **Comments:** 4 | **Created:** 2024-09-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2963

```
lvae = scvi.model.SCANVI.from_scvi_model(
    vae,
    adata=data,
    labels_key="celltype_scanvi",
    unlabeled_category="Unknown",
)
File ~/miniconda3/envs/scvi-env/lib/python3.10/site-packages/scvi/module/_scanvae.py:170, in SCANVAE.__init__(self, n_input, n_batch, n_labels, n_hidden, n_latent, n_layers, n_continuous_cov, n_cats_per_cov, dropout_rate, dispersion, log_variational, gene_likelihood, y_prior, labels_groups, use_labels_groups, linear_classifier, classifier_parameters, use_batch_norm, use_layer_norm, **vae_kwargs)
    147 self.encoder_z2_z1 = Encoder(
    148     n_latent,
    149     n_latent,
   (...)
    156     return_dist=True,
    157 )
    159 self.decoder_z1_z2 = Decoder(
    160     n_latent,
    161     n_latent,
   (...)
    166     use_layer_norm=use_layer_norm_decoder,
    167 )
    169 self.y_prior = torch.nn.Parameter(
--> 170     y_prior if y_prior is not None else (1 / n_labels) * torch.ones(1, n_labels),
    171     requires_grad=False,
    172 )
    173 self.use_labels_groups = use_labels_groups
    174 self.labels_groups = np.array(labels_groups) if labels_groups is not None else None

ZeroDivisionError: division by zero
```

**@canergen:** Hi, have you set y_prior? What value does n_labels have? I assume you used a column without cell-type labels (like all labels 'unknown'). Can you otherwise send adata.obs[YOUR_LABEL_KEY].value_counts() and adata.obs[YOUR_LABEL_KEY].dtype().

**@yojetsharma:** I am running snapatac2 tutorial wherein scvi-tools are used to map reference to query (so I am a new scvi-tools at the moment). Reference is a scRNA dataset and query is an atac seq:
```
query= snap.pp.make_gene_matrix(atac, snap.genome.hg38)
query
AnnData object with n_obs × n_vars = 58534 × 60606
    obs: 'sample', 'leiden'
reference=snap.read("GEX.h5ad", backed=None)
AnnData object with n_obs × n_vars = 187285 × 2000
    obs: 'sample', 'cell_type'
    var: 'highly_variable'
query.obs['cell_type']=pd.NA
data = ad.concat(
    [reference, query],
    join='inner',
    label='batch',
    keys=["reference", "query"],
    index_unique='_',
)
data
AnnData object with n_obs × n_vars = 245819 × 1397
    obs: 'sample', 'cell_type', 'batch'
sc.pp.filter_genes(data, min_cells=5 …

**@canergen:** Transferring labels from ATAC to RNA is not supported. Please check out our tutorials. For user questions, we recommend our discourse forum: https://discourse.scverse.org. I'm closing here.

**@yojetsharma:** No, no, I am transferring from RNA to ATAC, which also has a gene activity matrix. I was able to successfully transfer labels from one of the scRNA seq dataset to atac data.

## #2583: Allow scArches to extend categorical covariates
**Issue:** #2583 | **Last activity:** 2024-09-09T16:06:23Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-03-01 | **Labels:** good first issue, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2583

**@ori-kron-wis:** from @canergen

Currently, in Archesmixin we use the following:

```
if model.summary_stats[f'n_{REGISTRY_KEYS.CAT_COVS_KEY}'] > 0:
            raise NotImplementedError(
                "scArches currently does not support models with extra categorical covariates."
            )

```
We need to change the datafield to allow extension also for categorical covariate keys.

## #2952: n_proteins Parameter in MultiVI Class
**Issue:** #2952 | **Last activity:** 2024-09-05T18:04:50Z
**State:** closed | **Author:** @GoldenCaterpie | **Comments:** 3 | **Created:** 2024-08-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2952

<!-- Describe the bug -->

Hello! I am currently conducting research on single-cell multimodal data. I accessed the code for the paper "MultiVI: deep generative model for the integration of multimodal data" published on [Zenodo](https://zenodo.org/records/5762077). In the file Protein_update_3_TESTING, I found the following code:

```python
# ######################################################################################################################
# TRAIN ALL 3 MODALITIES
adata = anndata.read("dogma_all_genes_cells_dig_ctrl_annotated.h5ad.gz")
adata = adata.copy()
scvi.data.setup_anndata(adata, protein_expression_obsm_key='protein_expression')

n_genes = (adata.var.modality == 'Gene Expression').sum()
n_regions = (adata.var.modality == 'Peaks').sum()
n_proteins = adata.obsm['protein_expression'].shape[1]

os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '1'

mvi = scvi.model.MULTIVI(adata, n_genes=n_genes, n_regions=n_regions, n_proteins=n_proteins)
testing(mvi, save_path="trained_models/Test3Mod_DIGCTRL75b_211020", pdf_path="Test3Mod_DIGCTRL75B_")
# ######################################################################################################################
```

In this code, I noticed that a parameter called 'n_proteins' is set when creating the MULTIVI model.

However, in version 1.1.6 of scvi-tools, when I input similar code attempting to specify the n_proteins parameter, such as:

```pytho …

**@canergen:** Yes, we changed the multiVI code after the initial release. The correct version of multiVI for reproducibility should be defined there. @marianogabitto can you otherwise suggest the correct versions.

**@GoldenCaterpie:** > Yes, we changed the multiVI code after the initial release. The correct version of multiVI for reproducibility should be defined there. @marianogabitto can you otherwise suggest the correct versions.

Thx. And does this mean that current version of MultiVI is now specifically designed to handle multiome datasets and no longer supports protein data? If that’s not the case, could you plz provide some corresponding tutorials?🧐

**@canergen:** Hi, you have to add protein_expression_obsm_key to setup_anndata when setting up the model to use the protein data. MultiVI can handle RNA+protein+ATAC and any combination of these. There is no tutorial beyond RNA+ATAC.

## #2607: TypeError with model.train() using R reticulate
**Issue:** #2607 | **Last activity:** 2024-08-30T17:06:32Z
**State:** closed | **Author:** @jdownie2389 | **Comments:** 2 | **Created:** 2024-03-08 | **Labels:** bug, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2607

<!-- Describe the bug -->

When attempting to integrate several samples with scVI within an R environment, I'm running into an error that I'm pretty stumped about:  "Error in py_call_impl(callable, call_args$unnamed, call_args$named) :
  TypeError: Cannot cast scalar from dtype('float64') to dtype('int64') according to the rule 'safe'"

<!-- To reproduce -->

```R
# merging together several seurat objects stored as .rds files
merged_srt <- merge(x = rds_vector[[1]], y = rds_vector[-1], merge.data=TRUE)

# second step of merge
merged_srt[["RNA"]] <- JoinLayers(merged_srt[["RNA"]])

# Identify genes that are expressed in at least 3 cells
genes_to_keep <- rowSums(merged_srt[["RNA"]]$counts > 0) >= 3

# remove non-expressed genes
merged_srt <- subset(merged_srt, features = names(genes_to_keep)[genes_to_keep])

merged_srt <- NormalizeData(merged_srt)
merged_srt <- FindVariableFeatures(merged_srt, selection.method = "vst", nfeatures = 2000)
top2k <- head(VariableFeatures(merged_srt), 2000)

merged_srt_2k <- merged_srt[top2k]
merged_srt_2k_new <- merged_srt_2k

#convert seurat v5 to v3/v4
merged_srt_2k_new[["RNA"]] <- as(object = merged_srt_2k[["RNA"]], Class = "Assay")

# convert to adata object
adata <- sceasy::convertFormat(merged_srt_2k_new,
                              from="seurat",
                              to="anndata",
                              main_layer="data",
                              transfer_layer = "counts", …

**@canergen:** Can you share the full code. It looks like you have defined a custom seed like scvi.settings.seed = 2. This 2 is interpreted as a float in R. However, scvi-tools requires an integer there. You have to case the type in R.
If you haven't set a custom seed. Can you try doing so and see whether it's fixed?

**@canergen:** Closed due to inactivity.

## #2837: CellAssign tensor size error
**Issue:** #2837 | **Last activity:** 2024-08-29T08:28:01Z
**State:** closed | **Author:** @andrewjkwok | **Comments:** 9 | **Created:** 2024-06-11 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2837

<!-- Describe the bug -->

Hello,

I'm trying to use CellAssign as implemented within scvi-tools to map a query dataset onto my annotated reference. However, I am running into an error when trying to train the CellAssign model. I follow the tutorial in making sure library size is calculated, and subsetting the anndata object to only include genes in my marker gene list binary table. I have a list of 225 markers which I want to assign cells based on - but somehow there's a "tensor b" which has a dimension of 363 when I try to run the training?

I tried following the tutorial with the sample follicular lymphoma data and it worked, so I suppose it is not an issue with the package versions? Any help would be much appreciated.

<!-- To reproduce -->

```python
CSFadata_Heming_T.obs.index = CSFadata_Heming_T.obs.index.astype('str')
CSFadata_Heming_T.var.index = CSFadata_Heming_T.var.index.astype('str')
CSFadata_Heming_T.var_names_make_unique()
CSFadata_Heming_T.obs_names_make_unique()

lib_size = CSFadata_Heming_T.X.sum(1)
CSFadata_Heming_T.obs["size_factor"] = lib_size / np.mean(lib_size)

bdata = CSFadata_Heming_T[:, Tcelltype_markers_CellAssign_filtered.index].copy()

CellAssign.setup_anndata(bdata, size_factor_key="size_factor")
integration_model = CellAssign(bdata, Tcelltype_markers_CellAssign_filtered)
integration_model.train()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
RuntimeError: The …

**@canergen:** Hi, for the tutorial: We don't run the numpy function so I guess it's fine. @ori-kron-wis: Can you add for scvi-tools 1.2.0 release an `import numpy as np` to the tutorial?
For the error, I can't reproduce it, as you already mentioned that also for you the tutorial is working. I assume it's a problem with the data setup. If you share your AnnData object and the marker.csv file, I will give it a try on this dataset and try to reproduce it and fix it. Otherwise, can you share the adata summary (just print adata). Thanks!

**@Landau1994:** I have enconder the same error

**@canergen:** I wasn’t able to reproduce it. Do you also get it with our tutorial? Can you otherwise please share your data? Which version of scvi-tools are you using? Do you experience the error also on Colab within the tutorial using your data?

**@ori-kron-wis:** > CellAssign
@canergen
I Dont have permission to push to scverse/scvi-tutorials. I need to be added to https://github.com/orgs/scverse/teams/scvi-tools/members but before that I need to be added to the scverse GH org

**@Pahi95:** Hi!
I have the same problem with my batch. I have followed the tutorial on https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/cellassign_tutorial.html, and with the demo data it works.
I made a test marker gene set with only 3 genes, and it works. Now I used the full marker gene list I have. All stepps are completed but when coming to the model training I get the same error mentioned above.
Marker gene set:
![kép](https://github.com/user-attachments/assets/1b77726c-66e0-4247-a6b4-aac095ba997e)
Anndata object:
![kép](https://github.com/user-attachments/assets/dabe2ce8-5ff3-4085-94b6-96faeb130a04)
Model:
![kép](https://github.com/user-attachments/assets/6775dc80-c4a5-4e37-a83b-bbcc5439b2e8)
Error:
![kép](https://github.com/user-attachments/assets/b7b720e1-ce94-4b07-bb7 …

**@canergen:** Hi, thanks for sharing more input. First weird thing is to have NKX2-2 twice in the table. To my knowledge, CellAssign expects exclusive marker genes or at least have it in the same row. Are you able to share a small test dataset (best case just 200 cells) and after setting up the data with setup_anndata.

**@Pahi95:** > Hi, thanks for sharing more input. First weird thing is to have NKX2-2 twice in the table. To my knowledge, CellAssign expects exclusive marker genes or at least have it in the same row. Are you able to share a small test dataset (best case just 200 cells) and after setting up the data with setup_anndata.

Thank you for pointing this out. I have deleted the repetitive gene names and put them in 1 row. Now I don't get the error!

**@canergen:** Great. @andrewjkwok Can you check for similar issues? @ori-kron-wis it would be good to add a test for duplicated row labels.

**@Landau1994:** > > Hi, thanks for sharing more input. First weird thing is to have NKX2-2 twice in the table. To my knowledge, CellAssign expects exclusive marker genes or at least have it in the same row. Are you able to share a small test dataset (best case just 200 cells) and after setting up the data with setup_anndata.
>
> Thank you for pointing this out. I have deleted the repetitive gene names and put them in 1 row. Now I don't get the error!
I checked, and find I also have duplicated rows, when I remove duplicated rows in gene markers table, it worked, erros disappear, thanks a lot!

## #2341: I get error 'warnings.warn("Initializing zero-element tensors is a no-op") ' when looking at 10x multiom data
**Issue:** #2341 | **Last activity:** 2024-08-27T17:15:41Z
**State:** closed | **Author:** @jeffpkamp | **Comments:** 2 | **Created:** 2023-12-04 | **Labels:** bug, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2341

When I am trying to analyze a large file created from an aggregate 10x multiom data with multiVI I receive an error when I run scvi.model.MULTIVI

NOTE:  This is a very large file made by running cellranger_arc on multiple Multiome data sets to merge the ATAC regions.  Samples have a batch_id in the obs fields

```>>> adata.obs
                         batch_id modality  _indices  _scvi_batch  _scvi_labels
AAACAGCCAAACTAAG_paired        10   paired         0            0             0
AAACAGCCAAAGGCCA_paired         9   paired         1            0             0
AAACAGCCAACAACAA_paired         4   paired         2            0             0
AAACAGCCAACTAGAA_paired        10   paired         3            0             0
AAACAGCCAACTAGCC_paired        13   paired         4            0             0
...                           ...      ...       ...          ...           ...
TTTGTTGGTGTTTGAG_paired         7   paired     66517            0             0
TTTGTTGGTTAAATGC_paired        10   paired     66518            0             0
TTTGTTGGTTAACACG_paired        13   paired     66519            0             0
TTTGTTGGTTGTGATG_paired         2   paired     66520            0             0
TTTGTTGGTTTAACGG_paired         7   paired     66521            0             0
```


<-- To reproduce -->


CODE
```
import gzip
import os
import tempfile
from pathlib import Path

import pandas as pd
import numpy as np
import pooch
import scanpy as sc
i …

**@martinkim0:** Hi, sorry for following up late. Were you able to address the warning, and did the model train correctly after this?

**@canergen:** Closing due to inactivity and not reproducibile in our hands.

## #1568: [TOTALVI] NaN values during training when `empirical_protein_background_prior=True`
**Issue:** #1568 | **Last activity:** 2024-08-27T17:14:40Z
**State:** closed | **Author:** @justjhong | **Comments:** 4 | **Created:** 2022-06-15 | **Labels:** bug, nan, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/1568

<!-- Describe the bug -->
First reported in https://discourse.scverse.org/t/totalvi-nan-loss-with-few-proteins/45/3, this bug was recently reproduced in a dataset with 300 proteins. The cause of the issue is unknown, but setting `empirical_protein_background_prior=False` results in proper training.

Associated code: https://github.com/scverse/scvi-tools/blob/master/scvi/model/_totalvi.py#L1073


#### Versions:
<!-- Output of scvi.__version__ -->
> v0.16.4

**@RK900:** @jjhong922 @romain-lopez  I'm unable to reproduce this error when using < 10 proteins.

Code:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import scvi
import scanpy as sc

adata = scvi.data.pbmcs_10x_cite_seq()

n_proteins = 1 # can vary this number
adata.obsm['protein_expression'] = adata.obsm['protein_expression'].iloc[:, :n_proteins]

adata.layers["counts"] = adata.X.copy()
adata.raw = adata

sc.pp.highly_variable_genes(
    adata,
    n_top_genes=4000,
    flavor="seurat_v3",
    batch_key="batch",
    subset=True,
    layer="counts"
)

scvi.model.TOTALVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein_expression",
    layer="counts",
    batch_key="batch"
)

vae = scvi.model.TOTALVI(adata, lat …

**@adamgayoso:** 300 proteins sounds like a lot and I suspect many of them are not detected well. I would try filtering proteins first and then trying, it could be throwing off the heuristics used in this initialization

**@romain-lopez:** yes that sounds like a good advice, it'd be great to put this in the tutorial maybe?

**@canergen:** Fixed NaN values in current main. We used a bad combination of exponential activation that randomly produced NaN.

## #2935: Memory error running CellAssign depending on size of marker gene set reference
**Issue:** #2935 | **Last activity:** 2024-08-21T16:18:47Z
**State:** closed | **Author:** @sjspielman | **Comments:** 8 | **Created:** 2024-08-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2935

<!-- Describe the bug -->

I am trying to use CellAssign with GPU to varying success. I am finding that CellAssign is giving memory availability errors (`torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 6.57 GiB. GPU 0 has a total capacity of 14.58 GiB of which 3.35 GiB is free` etc.....) based on the size of the marker gene reference file. The reference I have prepared for use is 2274 genes x ~70 cell types. I can only get CellAssign to run without a memory allocation error if I drop the number of genes to ~400. The size of the AnnData itself don't seem to cause this problem, but larger reference files do.

I am wondering if this is a known issue, or you have any recommendations for preparing marker gene reference sets that will not cause this sort of error? Thanks very much! The file whi


<!-- To reproduce -->

I am attaching here a version of the reference gene file that runs for me and one that does not -

- [brain-reference-runs.tsv.txt](https://github.com/user-attachments/files/16587910/brain-reference-runs.tsv.txt)
- [brain-reference-fails.tsv.txt](https://github.com/user-attachments/files/16587947/brain-reference-fails.tsv.txt)

I can't directly attach the dataset I am running it with due to sharing restrictions, but the dataset is freely available for download here. It's the `SCPCL000001_processed_rna.h5ad` file associated with the download for sample `SCPCS000001`: https://scpca.alexslemonade.org/projects/SCPCP000001. Note that I have en …

**@canergen:** Hi. It says 3.5GB is free on the GPU which is very little. Can you use an empty GPU? A free Colab GPU would be sufficient for your purpose. I assume we could optimize RAM use but this won’t be a priority in the coming months if it works fine on 16GB of VRAM.

**@canergen:** I assume it happens during the predict function. If it still fails can you verify it. I don’t plan changing the model but changing inference would be straightforward (and we have two solutions to it).

**@sjspielman:** Hi @canergen, thanks for having a look! Indeed, I'm not at all sure why this GPU isn't empty to begin with. I have tried adding `torch.cuda.empty_cache()` into my code before running CellAssign, but it doesn't make a difference. This is something I will look into locally since I don't imagine it's related to `scvi-tools`. I will give it a go on Google Colab as well; if it runs there, the issue is definitely with my GPU setup.

But, it does seem that the error is happening earlier at the `.train()` step, not predict. Here's my full output:

```
GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
LOCAL_RANK: 0 - CUDA_VISIBLE_DEVICES: [0]
/home/lightsail-user/.conda/envs/gpu/lib/pyth …

**@sjspielman:** Hello, wanted to share a quick update. I have been for now working locally to figure out when the GPU is filling up, running line-by-line in an interactive python session with `nvidia-smi -l i` running so I can monitor usage.

The GPU indeed appears essentially free until I run the `.train()` line, at which point it starts ramping up and fills up. This is what I see up through and including the line `model = CellAssign(subset_adata, ref_matrix)`:

```
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 545.23.06              Driver Version: 545.23.06    CUDA Version: 12.3     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A …

**@canergen:** Hi, can you pass a smaller batch_size like `model.train(accelerator="gpu", batch_size=32)`. You can then increase it to maximize usage of GPU RAM. The current default is 1024. However, it creates several tensors of n_cellsXn_genesXn_celltypes and this is apparently too large in your case.

**@sjspielman:** > Hi, can you pass a smaller batch_size like model.train(accelerator="gpu", batch_size=32).

Thank you @canergen, this worked for me to get CellAssign running with my full marker genes set (and if not the most efficiently, at least more efficiently than CPU). Appreciate the help!

**@canergen:** Great, 128 will likely still work but you can see your memory use (consumption will be roughly linear with the batch side).

**@sjspielman:** > Great, 128 will likely still work but you can see your memory use (consumption will be roughly linear with the batch side).

💯 , I was able to get up to 128, but not >=256

## #2934: error in scanvi_ref
**Issue:** #2934 | **Last activity:** 2024-08-19T15:28:46Z
**State:** closed | **Author:** @AdotaLover | **Comments:** 8 | **Created:** 2024-08-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2934

<!-- Describe the bug -->

[TEXT HERE]

<!-- To reproduce -->

```python
# scanvi_ref.train(max_epochs=20, n_samples_per_label=100)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
[{
	"name": "ValueError",
	"message": "If `preds` have one dimension more than `target`, `preds` should be a float tensor.",
	"stack": "---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[30], line 1
----> 1 scanvi_ref.train(max_epochs=20, n_samples_per_label=100)

File ~/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/model/_scanvi.py:434, in SCANVI.train(self, max_epochs, n_samples_per_label, check_val_every_n_epoch, train_size, validation_size, shuffle_set_split, batch_size, accelerator, devices, datasplitter_kwargs, plan_kwargs, **trainer_kwargs)
    422     trainer_kwargs[\"callbacks\"] = sampler_callback
    424 runner = TrainRunner(
    425     self,
    426     training_plan=training_plan,
   (...)
    432     **trainer_kwargs,
    433 )
--> 434 return runner()

File ~/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/train/_trainrunner.py:98, in TrainRunner.__call__(self)
     95 if hasattr(self.data_splitter, \"n_val\"):
     96     self.training_plan.n_obs_validation = self.data_splitter.n_val
---> 98 self.trainer.fit(self.training_plan, self.data_splitter)
     99 self._update …

**@canergen:** Can you provide your version of torchmetrics and torch and provide the model celltype labels with model. _label_mapping

**@AdotaLover:** > Can you provide your version of torchmetrics and torch and provide the model celltype labels with model. _label_mapping

Torch version: 2.4.0+cu121 and Torchmetrics version: 1.4.0.post0 .i am new to scvi,the model celltype labels with model. _label_mapping means scanvi_ref._label_mapping?it shows like this_<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-weight: bold">[</span><span style="color: #008000; text-decoration-color: #008000">'acinar'</span> <span style="color: #008000; text-decoration-color: #008000">'activated_stellate'</span> <span style="color: #008000; text-decoration-color: #008000">'alpha'</span> <span style="color: #008000; text-decoration-color: #008000">'beta'</spa …

**@canergen:** Labels look right. Thanks for providing. @ori-kron-wis my best bet is the torchmetrics version is the issue. Can you check and follow-up here?

**@AdotaLover:** Torchmetrics version: 1.4.0.post0

**@AdotaLover:** i notice that when i run `scanvi_ref = scvi.model.SCANVI.from_scvi_model(
    scvi_ref,
    unlabeled_category="Unknown",
    labels_key=SCANVI_LABELS_KEY,
)`,there is a warning **/root/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/data/fields/_base_field.py:64: UserWarning: adata.layers[counts] does not contain unnormalized count data. Are you sure this is what you want?
  self.validate_field(adata)
**

**@AdotaLover:** > Labels look right. Thanks for providing. @ori-kron-wis my best bet is the torchmetrics version is the issue. Can you check and follow-up here?

Torchmetrics version: 1.4.0.post0 and i notice that when i run scanvi_ref = scvi.model.SCANVI.from_scvi_model( scvi_ref, unlabeled_category="Unknown", labels_key=SCANVI_LABELS_KEY, ),there is a warning **/root/miniconda3/envs/scanpy/lib/python3.10/site-packages/scvi/data/fields/_base_field.py:64: UserWarning: adata.layers[counts] does not contain unnormalized count data. Are you sure this is what you want?
self.validate_field(adata)
**

**@ori-kron-wis:** I'm getting the same thing with torch=2.4.0 and any version Torchmetrics starting with 0.11, so theres some bug here

**@ori-kron-wis:** The problem was related to the fact that during SemiSupervisedDataSplitter there was a batch with 1 sample per one of the classes (and there were 14 in this case), which resulted in some multiclass accuracy calculation instability.
This is fixed by adding -1 to the squeeze when extracting the true labels per class.

Funny thing is that this was happening only because of a combination of data + n_samples_per_label==100. Choose 99, or any other number, and it will work.

Nevertheless, it is a bug and should be fixed. @canergen I suggest having it in 1.1.6

## #2529: Unable to retrieve region factors for PoissonVI model
**Issue:** #2529 | **Last activity:** 2024-08-19T12:55:20Z
**State:** closed | **Author:** @duyguk | **Comments:** 1 | **Created:** 2024-02-21 | **Labels:** bug, good first issue, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2529

<!-- Describe the bug -->

Hi! I am unable to retrieve region factors with `model.get_region_factors()` for PoissonVI models (one trained on my own dataset, another trained on a subset of the tutorial PBMC data). The call instead returns the following error:

<!-- To reproduce -->

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: 'VAE' object has no attribute 'region_factors'
```

#### Versions:

<!-- Output of scvi.__version__ -->
> 1.1.1
> 1.1.0.post2

<!-- Relevant screenshots -->

**@ori-kron-wis:** Originally This is a PEAKVI thing but PoissonVI didn't have get_region_factors cause it uses the VAE module.
I added that function to it.
There will be a fix for 1.2.0

## #2581: multiVI fails with invalid tensor
**Issue:** #2581 | **Last activity:** 2024-08-16T10:55:32Z
**State:** closed | **Author:** @bio-la | **Comments:** 11 | **Created:** 2024-03-01 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2581

Hi scvi team, thanks for the excellent tools!  I'm reaching out with an issue running MultiVI with versions scvi-tools >=0.20.3
the error is the same reported [here](https://discourse.scverse.org/t/error-when-training-model-on-m3-max-mps/1896/2) and [here](https://discourse.scverse.org/t/macbook-m1-m2-mps-acceleration-with-scvi/2075/4).

i set up two actions to reproduce the error. I'm running the same script with the same toy dataset, only changing the scvi-tools version in the environment. (you can see all the dependencies in the conda list step). the action is ran on ubuntu but i have the same issue on an intel chip.

this action, with scvi-tools=1.1.1 fails with the same error as described before
https://github.com/DendrouLab/panpipes/actions/runs/8114022415/job/22178710942?pr=201

this action, with scvi-tools=0.20.3, runs successfully. https://github.com/DendrouLab/panpipes/actions/runs/8114022411/job/22178710284?pr=201

thanks for your help!

**@canergen:** Hi, the errors you are referring to are issues about MPS Apple hardware. We have seen the issue you are facing in multiVI in newer scvi-tools version. The main reason in our hands is that we have changed the default see in newer scvi-tools version. Do you fix the seed and still face the problem? Can you share the toy dataset (how large is it - ncells and file size)? It would be interesting to explore what updates in the TrainingPlan remove these errors.

**@bio-la:** thanks for your answer! [here is the toy dataset](https://figshare.com/ndownloader/files/44796985) (approx 2000 cells by 4000 features)

i didn't include a seed but i will try that and let you know.

**@bio-la:** Unfortunately, no success with explicit scvi.settings.seed
https://github.com/DendrouLab/panpipes/actions/runs/8114593332/job/22180588924?pr=201

**@martinkim0:** Hi @bio-la, sorry you're running into this issue. It looks like the issue might be slightly different than the Discourse threads you linked since the CI is running on Ubuntu, not macOS, so I'm guessing this is an issue unrelated to a PyTorch MPS build.

Could you try passing in a lower learning rate (maybe `lr=1e-5` or `lr=1e-6`) and see if that helps? Also, is this error occurring in the first epoch of training or later on? I wasn't able to find that info in the logs.

**@bio-la:** thanks for your suggestions. here are my comments:

- i get the same error message on Ubuntu and Macos Intel chip. I wouldn't know why the effect is the same on M3 chips, if you speculate that the cause is not the same.
- the error appears at the first epoch of training
- changing lr from `1e-3` to `1e-5` doesn't solve the issue, `scvi 0.20.3` still works with the lower lr
- i noticed that the conda install is now pulling `scvi 1.1.2`, still failing here.

I'm using [this dataset](https://figshare.com/ndownloader/files/44796985)
with the following parameters for Multivi:

```
MultiVI:
    batch_covariate: dataset
    model_args:
      n_hidden : None
      n_latent :  None
      #(bool,default: True)
      region_factors : True
       #{‘normal’, ‘ln’} (default: 'nor …

**@bio-la:** Hi, @martinkim0 any news on this? thanks!

**@canergen:** We are on it. I have one solution (gradient clipping) that solves similar problems in totalVI  (AdversarialTrainingplan is not stable). We first need to make sure that it doesn't reduce quality in downstream tasks.
I would assume adversarial_mixing=False will solve it for now in your tests but will reduce integration.
Last question: Can you tell me the AnnData version used to save the object above? I had issues in my testing environment opening the file (likely outdated AnnData on my end).

**@canergen:** Hi @bio-la, currently we enable an adversarial classifier even if only a single batch is present in the dataset. This is a bug. We will have a fix soonish. To overcome the error for now, you can pass `mvi.train(adversarial_mixing=False)`. Please let us know, if you are still facing the issue.

**@bio-la:** awesome! will wait for the changes to be merged and let you know. thank you!

**@canergen:** Fixed in #2914 and will be released with scvi-tools 1.2.

**@wlason:** Hi @canergen! Thank you for providing the fix. I would like to use multiVI for my project, I was wondering if you have any indication of when scvi-tools 1.2 will be released?

## #2933: How to increase num_workers in pytorch DataLoader?
**Issue:** #2933 | **Last activity:** 2024-08-10T15:45:54Z
**State:** closed | **Author:** @winglet0996 | **Comments:** 1 | **Created:** 2024-08-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2933

<!-- Describe the bug -->

Hi, I am following the [scRNA-seq tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/harmonization.html).

<!-- To reproduce -->
After running
```python
model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
model.train()
```
I got
<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
LOCAL_RANK: 0 - CUDA_VISIBLE_DEVICES: [0]
/home/winglet/Data/apps/micromamba/envs/scanpy/lib/python3.9/site-packages/lightning/pytorch/trainer/connectors/data_connector.py:441: The 'train_dataloader' does not have many workers which may be a bottleneck. Consider increasing the value of the `num_workers` argument` to `num_workers=87` in the `DataLoader` to improve performance.
```
When I set this at the very beginning
```python
scvi.settings.dl_num_workers = 87
```
I got tons of
```pytb
/home/winglet/Data/apps/micromamba/envs/scanpy/lib/python3.9/multiprocessing/popen_fork.py:66: RuntimeWarning: os.fork() was called. os.fork() is incompatible with multithreaded code, and JAX is multithreaded, so this will likely lead to a deadlock.
self.pid = os.fork()
```
and the training speed was much slower than the previous one (time/iter increaesd 5x).
#### Versions:

<!-- Output of scvi.__version__ -->
scvi …

**@canergen:** Hi, indeed we usually see a slowdown when using multiple workers. In the next release (or current main branch), we will add a persistent worker flag. We haven’t benchmarked in depth how the speed compares with this setting (if you try it out please report it). For the JAX warning, you can ignore it. JAX is not called during training so it shouldn’t increase your runtime.
To sum it up, PyTorch Lightning has some ideas to maximize performance that don’t necessarily improve performance.

## #2917: In Jupyter Notebook on Windows, the kernel keeps crashing when running Model hyperparameter tuning with scVI.
**Issue:** #2917 | **Last activity:** 2024-08-07T16:44:45Z
**State:** closed | **Author:** @GLking123 | **Comments:** 22 | **Created:** 2024-07-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2917

Hi

The running code is as follows：

`model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata, categorical_covariate_keys = ['Sample'],
                             continuous_covariate_keys=['pct_counts_mt'])

tuner = ModelTuner(model_cls)

search_space = {
    "n_hidden": tune.choice([92, 128, 192, 256]),
    "n_latent": tune.choice([10, 20, 30, 40, 50, 60,70,80]),
    "n_layers": tune.choice([1, 2, 3]),
    "lr": tune.loguniform(1e-4, 1e-2),
    "gene_likelihood": tune.choice(["nb", "zinb"])}

results = tuner.fit(
    adata,
    metric="validation_loss",
    search_space=search_space,
    num_samples=30，
    max_epochs=20,
    resources={"cpu": 10, "gpu": 1},
)
`

The following error message is displayed：
`symbolize_win32.inc : 53] raw: syminitialize() failed: 87 fatal python error: aborted`

For the above question, could you provide some debugging suggestions? Thank you for your valuable time and assistance. I sincerely look forward to your response！

**@canergen:** Hi, it's hard for me to test except our CI tests for Windows in GitHub. Let's try to reduce the reasons for failure. Can you provide whether just the below raises the issue or the train runner:
```
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata, categorical_covariate_keys = ['Sample'],
continuous_covariate_keys=['pct_counts_mt'])

tuner = ModelTuner(model_cls)

search_space = {
"n_hidden": tune.choice([92, 128, 192, 256]),
"n_latent": tune.choice([10, 20, 30, 40, 50, 60,70,80]),
"n_layers": tune.choice([1, 2, 3]),
"lr": tune.loguniform(1e-4, 1e-2),
"gene_likelihood": tune.choice(["nb", "zinb"])}
```

I would then disable the GPU. Can you train a model using GPU only in the same environment? Does the same code run in a Colab environment? The error code tells us th …

**@GLking123:** **The issue with RunConfig(local_dir) argument** is deprecated is due to the Ray version being too high.
 When I downgraded to version 1.12.0, the error didn't occur.
However, with version 1.12.0, running ray.init() causes the kernel to crash and displays:
`2024-07-29 19:41:51,397	INFO worker.py:1752 -- Started a local Ray instance.`
After that, the kernel crashes. When I run the above code in the command prompt, it shows:
`symbolize_win32.inc: 53] raw: syminitialize() failed: 87 fatal python error: aborted`


**I used resources={"gpu": 1} and got the same result.**

The following is a more detailed error report：
`2024-07-29 17:16:11,242 INFO worker.py:1752 -- Started a local Ray instance.
[symbolize_win32.inc : 53] RAW: SymInitialize() failed: 87
Fatal Python error: Aborted …

**@canergen:** So does initializing ray also create this error outside of scvi-tools? So just running `ray.init()` throws this error?
If ray is correctly installed and you can follow their tutorials, can you try installing from our main branch? The whole function is rewritten and it might be things are working there.

**@GLking123:** Hi

Thank you for your explanation. As long as I run ray.init(), an error is thrown. I will try installing the latest main branch. Thank you again.

**@canergen:** It looks like a problem with your ray installation then. Please try running one of their cases first like https://docs.ray.io/en/latest/tune/getting-started.html. If it fails, please request more information from the ray[tune] developers. Closing here. Please reopen if the tutorials works but scvi-tools hypertuning fails.

**@Pinolinoo:** Hi, I have a similar issue.

When I run:
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata_subset, categorical_covariate_keys = ['Sample'],continuous_covariate_keys=['pct_counts_mt', 'pct_counts_ribo'])

The kernel dies when I perform the setup_anndata.
I run on a cluster with GPU and the OS is RHEl9.

ray.init() works fine!

Thanks very much in advance for your help!

**@canergen:** Hi. This looks like a different issue (the first one is supposedly an error within ray).
Can you first try one of our tutorials to exclude it’s something with your specific data. There’s not much happening at setup_anndata. Do you get any message in the command line instance that runs the notebook? Could you check the code directly in command line to provide more insights?

**@Pinolinoo:** Hi can, thanks so much for your reply.
I tried with an adata from your tutorials

(adata_path = os.path.join(save_dir.name, "lung_atlas.h5ad")

adata = sc.read(
    adata_path,
    backup_url="https://figshare.com/ndownloader/files/24539942",
)

I get the same kernel crash when I do:
model_cls.setup_anndata(adata, categorical_covariate_keys = ['batch'],continuous_covariate_keys=['percent.mito'])

All I get in the terminal from the jupyter session is:
WARNING:root:kernel 829f8cb5-256f-431c-84bf-e54521da75c0 restarted

Right now I unfortunately don't have time to test the code directly in the command line, will do this next though if the others infos aren't enough for now! Thank you so much!

Best
Philipp

**@Pinolinoo:** Ok update:

I tried again directly in the command line with the scvi tutorials lung atlas dataset and the error I get is: Segmentation fault (core dumped)

I have 100GB free Memory however in the interactive session and when I tried on a Jupyter Kernel Session with 512GB free Memory the kernel also crashed.

**@canergen:** Thanks it’s a hard one to debug. Can you paste the output when enabling faulthandler: e.g. python3 -q -X faulthandler

**@Pinolinoo:** Sure, here you go!
Thanks a lot for your hard work!

`Thread 0x00007fa883d91640 (most recent call first):
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/threading.py", line 359 in wait
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/threading.py", line 655 in wait
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/site-packages/tqdm/_monitor.py", line 60 in run
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/threading.py", line 1073 in _bootstrap_inner
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/threading.py", line 1030 in _bootstrap

Current thread 0x00007fa98c397740 (most recent call first):
  File "/fast/AG_Metzger/philipp/b …

**@canergen:** Thanks, we’re getting there. It looks like your JAX installation is broken. Can you try:

```
def selu(x, alpha=1.67, lmbda=1.05):
  return lmbda * jnp.where(x > 0, x, alpha * jnp.exp(x) - alpha)

x = jnp.arange(5.0)
print(selu(x))
```

**@canergen:** And:
```
from jax import jit

selu_jit = jit(selu)
_ = selu_jit(x)  # compiles on first call
%timeit selu_jit(x).block_until_ready()

```

**@Pinolinoo:** def selu(x, alpha=1.67, lmbda=1.05):
...   return lmbda * jnp.where(x > 0, x, alpha * jnp.exp(x) - alpha)
...
>>> x = jnp.arange(5.0)
Fatal Python error: Segmentation fault

Current thread 0x00007f3597f0d740 (most recent call first):
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/site-packages/jax/_src/xla_bridge.py", line 704 in register_plugin
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/site-packages/jax_plugins/xla_cuda12/__init__.py", line 79 in initialize
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/site-packages/jax/_src/xla_bridge.py", line 623 in discover_pjrt_plugins
  File "/fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.12/site-packages/jax/_src/xla_brid …

**@Pinolinoo:** Seems like just the jnp.arrang() gives the mistake already!

**@canergen:** I would recommend to set up a new conda environment and follow the installation instructions on the JAX homepage (CPU version will be more stable if you only need it for scVI). If this doesn’t fix it, can you create an issue there. Can you install scVI after installing and testing JAX?

**@Pinolinoo:** Ok I will do that. I want to use scVI for an integration of datasets and wanted to perform a hyperparameter search before.
Wouldn't it be better to do that on the gpu and thus also use JAX for gpu?

**@canergen:** JAX is used for the MrVI model and JaxSCVI, all other models don't benefit from a GPU-enabled JAX (installing CUDA-enabled JAX is sometimes a bit of a pain). However, it should also work to use a GPU-enabled version of JAX. They have guides on how to install it on their webpage. Please follow this and verify your installation. Closing here as it is an issue not related to scvi-tools.

**@Pinolinoo:** I did like you suggested and installed Jax first. The tests were then working however when I install scvi afterwards and then try to import scvi I get this error:

RuntimeError                              Traceback (most recent call last)
Cell In[1], [line 1](vscode-notebook-cell:?execution_count=1&line=1)
----> [1](vscode-notebook-cell:?execution_count=1&line=1) import scvi
      [2](vscode-notebook-cell:?execution_count=1&line=2) from scvi.autotune import ModelTuner
      [3](vscode-notebook-cell:?execution_count=1&line=3) from ray import tune

File /fast/AG_Metzger/philipp/bins/miniforge3/envs/scvi_ray/lib/python3.11/site-packages/scvi/__init__.py:11
      [8](https://vscode-remote+ssh-002dremote-002bmax-002dlogin-002emdc-002dberlin-002enet.vscode-resource.vscode-cdn.net/fast …

**@canergen:** It seems the Windows prebuilt are experimental for jax. You have to install jaxlib and jax in the same version `pip install jaxlib==0.4.27`. It's not straightforward to track this in the pyproject.toml file as far as I'm aware.

**@Pinolinoo:** Thank you, I managed to get everything installed and the setup.anndata() works now however later when I run

```
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata, categorical_covariate_keys = ['Sample'],continuous_covariate_keys=['pct_counts_mt', 'pct_counts_ribo'])

tuner = ModelTuner(model_cls)

results = tuner.fit(adata, metric="validation_loss",
                    resources = {'gpu': 1}, #have to specify gpu or might not use
                    search_space = search_space,
                    num_samples = 100,
                    max_epochs = 20)
```

I get this error:

```
---------------------------------------------------------------------------
DeprecationWarning                        Traceback (most recent call last)
Cell In[16], [line 1](vscode-n …

**@canergen:** Great that it worked. This is a duplicate of #2908. Please see there for fixes.

## #2448: Make `drop_last` configurable in data loaders
**Issue:** #2448 | **Last activity:** 2024-08-07T15:45:35Z
**State:** closed | **Author:** @aksarkar | **Comments:** 9 | **Created:** 2024-01-29 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2448

**Is your feature request related to a problem? Please describe.**

A common gotcha with SCVI, etc. is encountering the following error in `BatchNorm1D`

```
Expected more than 1 value per channel when training, input size torch.Size([1, 128])
```

when the dimension of the data is such that the last minibatch has size 1. See for example #221, #426, #2214, #2314.

The previously accepted solutions have been to change the `batch_size` parameter to some value such that there is no batch of size 1.

However, this is not so easily accomplished for models like `scvi.external.SOLO`, where the actual training data size is not easily computed from the original data size unless one knows the technical details or follows the code very closely.

**Describe the solution you'd like**

The simplest solution to the problem would be to configure the training/validation data loaders with `drop_last=True`, since it is only the last batch that could have size 1.

Right now, this argument is hard-coded

https://github.com/scverse/scvi-tools/blob/9b5f5537ff5f8f1066e6a6170c4d5e6660b56793/scvi/dataloaders/_data_splitting.py#L488

Changing the default would eliminate a commonly occurring and confusing error.

As an alternative, making it configurable via a keyword argument would provide a simpler solution to users who encounter the problem.

**@martinkim0:** Hi, thanks for the suggestion. Unfortunately, we aren't planning on changing the default value of `drop_last` because of backwards compatibility. However, we do currently allow users to pass in this argument via `datasplitter_kwargs` (see [here](https://github.com/scverse/scvi-tools/blob/main/scvi/external/solo/_model.py#L302)), which will be passed in to the `AnnDataLoader` constructor. Let me know if this works for you.

**@martinkim0:** Closing as the issue is addressed

**@iyhaoo:** Hi, this issue doesn't solve yet, since in the latest version, it still make drop_last as false, then I cannot assign it as true...
https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/dataloaders/_data_splitting.py#L145

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/dataloaders/_data_splitting.py#L158

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/dataloaders/_data_splitting.py#L173

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/dataloaders/_data_splitting.py#L336

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/dataloaders/_data_splitting.py#L348

https://github.com/scverse/ …

**@schroeme:** Hi @martinkim0, where can we pass drop_last=True in the SCVI model? It doesn't work if I pass it to `model.train()` or when setting up or initiating the model. I am having the same issue @aksarkar mentioned above with an `scvi.external.SOLO` model, where I can't tell what the minibatch size is (the number of cells in the batch % 128 is not 1). Thanks!

**@schroeme:** After reading a bit more, I tried passing `drop_last=True` into `scvi.external.SOLO.train` via `datasplitter_kwargs` like so:

```
datasplitter_dict = {
  "drop_last": True
}
scvi.external.SOLO.train(solobatch, early_stopping = False,datasplitter_kwargs=datasplitter_dict)
```
and I get the following error:
`TypeError: scvi.dataloaders._data_splitting.DataSplitter() got multiple values for keyword argument 'batch_size'`.

I think this means `drop_last=False` is still hard-coded, no?

**@seyoon-lee:** I am stuck exactly where @schroeme is right now as well. Just trying to pass datasplitter_kwargs={"drop_last":True}.

**@rlinder02:** Hi @martinkim0, I'm having this issue too (I can't seem to find a place to add `drop_last=True`). The link you posted for `datasplitter kwargs` seems to be broken. Thanks!

**@canergen:** Hi, I will push a fix later today (will be released in version 1.2). Sorry for the issues reported here. Please reopen issues when posting in closed issues. It is otherwise difficult to track these.

**@rlinder02:** Thanks so much!

## #2911: Reproducibility issue of MRVI
**Issue:** #2911 | **Last activity:** 2024-08-07T08:22:09Z
**State:** closed | **Author:** @justjhong | **Comments:** 4 | **Created:** 2024-07-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2911

Moving issue reported by @Nusob888 from [mrvi](https://github.com/YosefLab/mrvi/issues/105) for tracking.

> Dear Yosef lab members,
>
> Thanks for MRVI, I have been trying it out finally.
>
> Unfortunately I am experiencing some reproducibility issues. I first noticed this when I accidentally refreshed a Jupyter notebook and re-ran the code. The embeddings were very different.
> Since then I have tried a numerous amount of methods to set seed and I cannot seem to produce anything consistent.
>
> This would be a big issue for reproducibility if the u embeddings were ever to be used for clustering (which I had hoped to do) and I presume it would also effect how the abundance and differential expression analysis perform?
>
> I have attached 4 htmls of my code run on the PBMC 3K dataset.
>
> Any updates on this would be great to help me keep track of the tool, as I would very much like to use it, but have concerns around this issue.
>
> [SCVI_MRVI_reproducibility_scvi_1.pdf](https://github.com/user-attachments/files/16378329/SCVI_MRVI_reproducibility_scvi_1.pdf)
> [SCVI_MRVI_reproducibility_mrvi_2.pdf](https://github.com/user-attachments/files/16378330/SCVI_MRVI_reproducibility_mrvi_2.pdf)
> [SCVI_MRVI_reproducibility_mrvi_1.pdf](https://github.com/user-attachments/files/16378331/SCVI_MRVI_reproducibility_mrvi_1.pdf)
> [SCVI_MRVI_reproducibility_scvi_2.pdf](https://github.com/user-attachments/files/16378332/SCVI_MRVI_reproducibility_scvi_2.pdf)

**@justjhong:** Found the solution. This only occurs on CUDA, not on CPU. I was able to reproduce the issue then solve it using the solution posted here: https://github.com/google/jax/issues/13672.

`
os.environ['XLA_FLAGS'] = '--xla_gpu_deterministic_ops=true'
`

I also tested this after removing all the lines fixing seeds except for scvi.settings.seed, and this was sufficient with the flag to achieve determinism. Closing now, but feel free to open if the issue persists.

@Nusob888

**@canergen:** Thanks @justjhong. Should we maybe provide the flag inside scvi-tools or add it to the tutorial?

**@justjhong:** sure, let's add it into the seed function of the scviconfig. I think it slows down performance a little so it should only be applied when setting seed manually

**@Nusob888:** Amazing! thank you both!

## #2545: is  there any way to sepcific the number of workers when using scvi  in R ?
**Issue:** #2545 | **Last activity:** 2024-08-07T03:02:22Z
**State:** closed | **Author:** @lwlive | **Comments:** 2 | **Created:** 2024-02-22 | **Labels:** enhancement, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/2545

when I integrating datasets with scVI in R (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scvi_in_R.html), it reports the following warnings. I am wondering how could I  set the num_workers in   R? Could  you give some suggestions?

python3.9/site-packages/lightning/pytorch/trainer/connectors/data_connector.py:441: The 'train_dataloader' does not have many workers which may be a bottleneck. Consider increasing the value of the `num_workers` argument` to `num_workers=111` in the `DataLoader` to improve performance.

**@canergen:** Hi, I wouldn't worry to much about this message. The speed improvement by increasing num_worker is not high. @ori-kron-wis it's not high priority to look into this but it would be good to figure this one out.

**@ori-kron-wis:** Hi @lwlive yes, you can specify in your R code:

```
# run setup_anndata
scvi$model$SCVI$setup_anndata(adata)
scvi$settings$dl_num_workers = 7L #where here you will set your num of workers in R integer
scvi$settings$persistent_workers = TRUE #this will not be ready until scvi 1.2.0

# create the model
model = scvi$model$SCVI(adata)

# train the model
model$train()
```

## #2429: `SCANVI.loss` fails when `n_samples>1`
**Issue:** #2429 | **Last activity:** 2024-07-30T16:43:48Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-23 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2429

Reproducible script:
```
vae = SCANVAE(n_input=100, n_labels=1)
x = torch.randint(0, 100, (10, 100), dtype=torch.float32)
batch = torch.zeros(10, dtype=torch.long)
labels = torch.zeros(10, dtype=torch.long)
tensors = {
    REGISTRY_KEYS.X_KEY: x,
    REGISTRY_KEYS.BATCH_KEY: batch,
    REGISTRY_KEYS.LABELS_KEY: labels,
}

_ = vae.forward(
    tensors,
    inference_kwargs={"n_samples": 2}
)
```

## #2687: VeloVI uses np.argsort, does not work with sparse spliced/unspliced layers
**Issue:** #2687 | **Last activity:** 2024-07-29T22:41:08Z
**State:** closed | **Author:** @jberkh | **Comments:** 5 | **Created:** 2024-04-04 | **Labels:** bug, good first issue, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2687

#### Issue
The `scvi.external.velovi.VELOVI` class uses `np.argsort` on the spliced/unspliced matrices, but this returns `array([0])` when these matrices are sparse.

#### Minimally reproducible code
```python
import scvi
import anndata
from scipy.sparse import csr_matrix
import numpy as np

adata = anndata.AnnData(X = np.random.randint(0, 100, 10000).reshape(100, 100))
adata.layers["spliced"] = csr_matrix(adata.X.copy())
adata.layers["unspliced"] = csr_matrix(adata.X.copy())

scvi.external.velovi.VELOVI.setup_anndata(adata, "spliced", "unspliced")
model = scvi.external.velovi.VELOVI(adata)
model.train()
```

```pytb
IndexError                                Traceback (most recent call last)
Cell In[1], [line 11]
      [8] adata.layers["unspliced"] = csr_matrix(adata.X.copy())
     [10] scvi.external.velovi.VELOVI.setup_anndata(adata, "spliced", "unspliced")
---> [11] model = scvi.external.velovi.VELOVI(adata)
     [12] model.train()

File [~/miniconda3/envs/envSCVI-2/lib/python3.10/site-packages/scvi/external/velovi/_model.py:77] in VELOVI.__init__(self, adata, n_hidden, n_latent, n_layers, dropout_rate, gamma_init_data, linear_decoder, **model_kwargs)
     [75] sorted_unspliced = np.argsort(unspliced, axis=0)
     [76] ind = int(adata.n_obs * 0.99)
---> [77] us_upper_ind = sorted_unspliced[ind:, :]
     [79] us_upper = []
     [80] ms_upper = []

IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed
```

### …

**@martinkim0:** Thanks! I'll take a look at this

**@martinkim0:** Just to give a quick update on this, the simplest patch is to explicitly convert the unspliced data into a dense array when it comes in as sparse since there's no `argsort` equivalent for `csr_matrix`. I don't think this is the best solution because it will require more memory than necessary.

**@jberkh:** I figured as much, given that np.argsort by defnition returns a dense matrix since all the zero value return non-zero indices. Unfortunately, calling .todense() on too large datasets does blow up in memory quite a bit, possibly to the point of crashing.

Maybe solution could be to convert the matrices to dense in batches, something along these lines:

```python
if isinstance(unspliced, csr_matrix) or isinstance(unspliced, csr_matrix):
    sorted_unspliced = np.empty(unspliced.shape)
    # batch size of 1000 here
    for i in range(0, unspliced_shape.shape[1], 1000):
        sorted[:, i:i+1000] = np.argsort(unspliced[:, i:i+1000].todense(), axis = 0)
```

**@martinkim0:** Thanks for the suggestion. I'm personally leaning towards a solution that natively deals with the sparse matrix instead of having to implicitly convert to dense. I'm also looking into what might be a potential bug in this whole preprocessing step.

**@canergen:** I’m sorry for the long time it took us to get back. We expect users to preprocess data using: https://scvelo.readthedocs.io/en/stable/scvelo.pp.moments.html as highlighted in our tutorial. This function returns dense matrices. Please follow our tutorial. It should be safe to downsample n_cells after running the moments function, reduce highly variable genes to less genes or focus your analysis on several celltypes to overcome memory constraints.

## #2338: Model trained on 0.14 and model load on 0.20, error shows: no "ind_x"
**Issue:** #2338 | **Last activity:** 2024-07-26T20:18:21Z
**State:** closed | **Author:** @zhenxingjian | **Comments:** 3 | **Created:** 2023-11-27 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2338

---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Cell In[8], line 1
----> 1 RNA_ATAC_model = scvi.model.MULTIVI.load(os.path.join(model_path, cur_best_model_path), adata=data_train)

File ~/miniconda3/envs/py3/lib/python3.10/site-packages/scvi/model/base/_base_model.py:660, in BaseModelClass.load(cls, dir_path, adata, use_gpu, prefix, backup_url)
    656 # Calling ``setup_anndata`` method with the original arguments passed into
    657 # the saved model. This enables simple backwards compatibility in the case of
    658 # newly introduced fields or parameters.
    659 method_name = registry.get(_SETUP_METHOD_NAME, "setup_anndata")
--> 660 getattr(cls, method_name)(
    661     adata, source_registry=registry, **registry[_SETUP_ARGS_KEY]
    662 )
    664 model = _initialize_model(cls, adata, attr_dict)
    665 model.module.on_load(model)

File ~/miniconda3/envs/py3/lib/python3.10/site-packages/scvi/model/_multivi.py:1088, in MULTIVI.setup_anndata(cls, adata, layer, batch_key, size_factor_key, categorical_covariate_keys, continuous_covariate_keys, protein_expression_obsm_key, protein_names_uns_key, **kwargs)
   1074     anndata_fields.append(
   1075         ProteinObsmField(
   1076             REGISTRY_KEYS.PROTEIN_EXP_KEY,
   (...)
   1082         )
   1083     )
   1085 adata_manager = AnnDataManager(
   1086     fields=anndata_fields, setup_method …

**@martinkim0:** Hi, please use the [`convert_legacy_save`](https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.MULTIVI.html#scvi.model.MULTIVI.convert_legacy_save) method for models saved prior to 0.15.

**@zhenxingjian:** Hi,
I used
scvi.model.MULTIVI.convert_legacy_save(
     os.path.join(model_path, cur_best_model_path),
     os.path.join(model_path, cur_best_model_path),
     overwrite=True,
)
RNA_ATAC_model_raw = scvi.model.MULTIVI.load(os.path.join(model_path, cur_best_model_path))

But still get the same error.
KeyError: 'ind_x'

**@canergen:** I'm sorry you ran into this. MultiVI was reformatted after the initial release. We will update our release notes with scvi-tools 1.2. Specifically PR #1697 added indices to setup_anndata. This is a breaking change and models beforehand should be loaded with versions before this PR.

## #2631: Support `RNASeqMixin` methods in `CondSCVI`
**Issue:** #2631 | **Last activity:** 2024-07-26T08:26:02Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-25 | **Labels:** enhancement, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2631

## #2736: Training models with torch.Tensor input
**Issue:** #2736 | **Last activity:** 2024-07-26T04:56:57Z
**State:** open | **Author:** @j-bac | **Comments:** 4 | **Created:** 2024-04-22 | **Labels:** enhancement, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2736

**Is your feature request related to a problem? Please describe.**
It is not currently straightforward to pass external dataloaders to train a model. In particular, loading `torch.Tensor` data and directly feeding it to a model as input doesn't seem possible because `scvi.data._utils._check_nonnegative_integers` does not handle `torch.Tensor`.

It would be very useful to be able to feed a custom dataloader, dictionary or AnnData as direct input to model.train() without having to copy `torch.Tensor` back to numpy or pandas. Maybe this can be implemented using  `model.train(data_module=data_module)` ?

**Describe the solution you'd like**
```python
import torch
import scanpy as sc
import scvi

counts = torch.randint(0,10,(500, 10))

adata = sc.AnnData(scipy.sparse.csr_matrix(counts.shape), #AnnData does not allow torch.Tensor in .X field
                                 layers={'counts':counts})

scvi.model.SCVI.setup_anndata(adata,layer="counts")
model = scvi.model.SCVI(adata)
model.train()
```

**@canergen:** We cover the enhancement to use custom dataloader in the recent version of scVI-tools.
However, it is not clear yet which minimal checks (integer, gene names) we still want to perform.
About your example: @Intron7: Is this idea of having AnnData in torch recommended? What analysis capabilities are possible in this scenario? I thought this is meant to be done in rapids_singlecell. Does rapids copy back and forth between CPU and GPU or is the full data kept between processing steps on GPU?

**@j-bac:** Thanks! Is there already a link to an example usage of this new version?
AFAIK rapids_singlecell keeps matrices on GPU without back and forth, (not using torch though) [https://rapids-singlecell.readthedocs.io/en/latest/Usage_Principles.html](https://rapids-singlecell.readthedocs.io/en/latest/Usage_Principles.html)

**@Intron7:** We are still talking about how this would work. However at the moment whenever I use rsc I have to transform back to cpu and than use scvi. Rapids-singlecell really wants `.X` and `.layers` on the GPU so everything has to be in memory. I would really like if we used DLPack for this. DLPack allows for the 0 copy conversion from cupy and jax to torch.

**@martinkim0:** Hi @j-bac, thanks for the suggestion. We will be releasing a tutorial with our next release (v1.2) that covers a basic usecase with a custom dataloader. I'll note that we currently don't support inference methods yet (_e.g._ `get_latent_representation`), but it's something we're working on.

## #2785: Support for weighted loss either per-batch or per-cell?
**Issue:** #2785 | **Last activity:** 2024-07-26T04:56:17Z
**State:** closed | **Author:** @kamilkrukowski | **Comments:** 2 | **Created:** 2024-05-09 | **Labels:** enhancement, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2785

Could scVI models support weighed loss and weighing individual cells or batch_key groups?

**Some potential uses**
- Downweighing over-represented atlases with low interesting variation.
- Improving ELBO on poorly represented subsets of interest i.e. rare cell types or small samples.

**Comments**
To my knowledge, oversampling/undersampling is not a viable solution here because scvi-tools requires in-memory AnnData objects containing the entire dataset. Is there any way to "stream" data loading with meaningful oversampling that does not require holding all oversampled entries in memory for the entirety of training?

**@canergen:** Hi, thanks for your question. @martinkim0 we wanted to have a stratified validation/train splitter at some time point but never followed up on this. I guess this would yield a very similar result. Currently you can subset your object before running scVI.

**@canergen:** You can now used stratified train splitters in main (#2902, it will be released in scvi-tools 1.2). You can define a train set in which small cell-types are more abundant and will yield a similar increase of weights during training.

## #2906: autotune throws error for ContrastiveVI (and possibly other external modules)
**Issue:** #2906 | **Last activity:** 2024-07-26T04:54:00Z
**State:** closed | **Author:** @LinearParadox | **Comments:** 1 | **Created:** 2024-07-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2906

<!-- Describe the bug -->

When creating a tuner from a contrastiveVI object, an error is thrown due to the object missing the \_\_name\_\_ attribute.
<!-- To reproduce -->

```python

scvi.external.ContrastiveVI.setup_anndata(adata, layer="counts", batch_key='sample_id')
contrastive_vi_model = scvi.external.ContrastiveVI(
    adata,
    n_salient_latent=10,
    n_background_latent=10,
    use_observed_lib_size=False,
)
scvi_tuner = autotune.ModelTuner(contrastive_vi_model)

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: 'ContrastiveVI' object has no attribute '__name__'

```

#### Versions:

<!-- Output of scvi.__version__ -->

'1.1.2'

<!-- Relevant screenshots -->

**@canergen:** Hi, I can't reproduce this error in Colab (can you check my notebook below and see that it works for you).
However, be aware that several elements of ContrastiveVI are not setup to be tuned (all model parameters, while train parameters can be tuned).
https://colab.research.google.com/drive/18x9Nwh6Ql0_2MVMnjx2E00hJ8h8NPFOe
In case that it works for you, I would recommend updating scvi-tools or otherwise start with a fresh environment.

## #2909: Error in model training
**Issue:** #2909 | **Last activity:** 2024-07-26T04:53:36Z
**State:** closed | **Author:** @swasthadinakar | **Comments:** 2 | **Created:** 2024-07-24 | **URL:** https://github.com/scverse/scvi-tools/issues/2909

When I train my MULTIVI model on fully paired data, I am getting this error:

ValueError: Expected parameter loc (Tensor of shape (128, 18)) of distribution Normal(loc: torch.Size([128, 18]), scale: torch.Size([128, 18])) to satisfy the constraint Real(), but found invalid values:
tensor([[nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        ...,
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan]], grad_fn=<AddmmBackward0>)


I did not provide a batch_key for scvi.model.MULTIVI.setup_anndata as my entire dataset was paired and could not be separated into batches based on modality.

I have used the 10x PBMC multiome dataset for my work: https://www.10xgenomics.com/datasets/pbmc-from-a-healthy-donor-granulocytes-removed-through-cell-sorting-10-k-1-standard-1-0-0

How do I resolve this error?

**@canergen:** Hi. This is likely a duplicate of: https://github.com/scverse/scvi-tools/issues/2581#issuecomment-2019574427. Please follow the advices there. The fix is planned to be released with version 1.2

**@canergen:** Fixed in #2914, for now you can set `adversarial_mixing` in train to False. The fix will be release with scvi-tools 1.2

## #2142: Make Hub tests deterministic
**Issue:** #2142 | **Last activity:** 2024-07-25T21:08:13Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2023-07-04 | **Labels:** bug, hub, tests, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2142

A subset of the hub tests fail due to array differences. Need to find a way to make these deterministic or increase the tolerance. These tests don't fail on cpu but they do on CUDA.

**@canergen:** Fixed by increasing n_samples. PR #2910

## #2726: scvi tools train with multi gpus
**Issue:** #2726 | **Last activity:** 2024-07-25T18:19:07Z
**State:** closed | **Author:** @shanzha9 | **Comments:** 3 | **Created:** 2024-04-12 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2726

Hi, developers,

The datasets used in my study consisting of 2.6 M cells, so it will take a week to train. I wonder if scvi tools support multi gpus train and if there is an official tutorial.

Thank you!

**@canergen:** There is multi-GPU support. However, your calculation looks vastly off and I don't think your dataset is large enough to benefit largely from multi-GPU. E.g. on the human CELLXGENE census dataset of 35 million cells, training for 100 epochs took less than 2 days (we actually had strikingly similar results after a couple of hours and 20 epochs). I would recommend increasing batch_size to 1024 (time scales pretty linearly with batch size) and reducing train epochs to 50 (it's what I am usually using) and you should be able to train it in 2 hours. Let me know if it takes more than 8 hours (installation might be wrong or your object is not correctly formatted).

**@shanzha9:** @canergen Hi, thanks for your reply.

Could you please link the official multi gpus tutorial. The data to be train is raw counts. I set

`scvi.settings.dl_num_workers = 30
scvi.settings.num_threads = 30
scvi.settings.batch_size =  2048`

but, the %cpu only under 20% per process. There may somethingwrong with dataloader?

**@canergen:** Low CPU load is usually not a problem if you reach high GPU usage. It just tells you, that it's less work and doesn't require 30 workers. The copy speed to GPU is the limiting step and doesn't benefit much from more workers. Multi-GPU support is currently experimental and we will release a tutorial with scvi-tools 1.3 (planned for end of this year).

## #2547: Enable custom splits in `DataSplitter`
**Issue:** #2547 | **Last activity:** 2024-07-25T04:01:08Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-22 | **Labels:** enhancement, good first issue, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2547

See #1063. CC @canergen

Two ways we could implement this:

`train_indices`, `validation_indices`, and `test_indices`
- Need to validate that indices are within range and check for overlaps
- Easier to adjust splits by changing indices
- Requires manual tracking of indices

`set_split_obs_key` that specifies an obs column in the data that should contain the values `"train"`, `"validation"`, and `"test"`
- Need to validate that this column only contains the correct values
- Potentially expensive for disk-backed datasets as we would need to load in this column for all observations prior to training (if we want to perform validation of the values). If a user wants to change the splits, they'll also have to write to disk
- Ties in splitting logic in with data so that this information is carried along with the dataset downstream
- One argument vs. 3

This feature will be important for integrating scib-metrics with the training loop as we want good representation of batches and cell types in the validation set.

**@ori-kron-wis:** We'll go for the first option, as the user will just have to support his list of np.arrays of [train_idx,valid_idx,test_idx] by that order. He can leave any of them empty as well (as long as it makes sense).
I also added a flag for using external indexes. This will make sure the user wants to use those indexes, and it will bypass any logic we have today concerning splitting.

## #1765: Allow custom train/test/val splits
**Issue:** #1765 | **Last activity:** 2024-07-25T04:01:07Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 1 | **Created:** 2022-10-24 | **Labels:** enhancement, good first issue, data, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/1765

Right now we split the data randomly be a user specified proportion. We should provide api access to allow any custom splits.

A workaround right now is to train on a custom anndata and set train size to 1.0, and then use the fact that most model methods allow the ability to process held out anndatas.

E.g.,

```python
vae = scvi.model.SCVI(train_adata)
vae.train(train_size=1.0)
vae.get_elbo(test_adata)
```

however, you can't leverage things like early stopping this way.

**@ori-kron-wis:** Because we will give the user a wildcard option to insert its own set of train/valid/test indices, coming from whatever logic he wanted (for example any of the sklearn splitting techniques), I don't think this issue require actual code fix

## #1063: dataloader which stratifies train-validation split by adata.obs columns
**Issue:** #1063 | **Last activity:** 2024-07-25T04:01:07Z
**State:** closed | **Author:** @vitkl | **Comments:** 11 | **Created:** 2021-05-14 | **Labels:** enhancement, good first issue, data, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/1063

Would be great to have train validations split balanced by cell labels or batch - which is useful when there are rare populations.

This can be addressed by adding a 'stratify' option for dataloader and dataslitter like in `sklearn.model_selection.train_test_split(..., stratify=x)`.

**@adamgayoso:** What do you think @galenxing @romain-lopez ? The data splitters for training can have an `stratify_by_obs_key: str` argument.

**@adamgayoso:** I think the solution is to add a new parameter to `AnnDataLoader` called `stratify_by_obs_key` as well as `stratify_min_size` the minimum size of any category in the minibatch

**@adamgayoso:** @watiss we can also implement internally as an option if it works

**@vitkl:** So, do you think it is possible to add this feature?

**@vitkl:** Would be great to have this option as

```python
model = SCVI(...)
model.train(..., stratify_validation_split_by_obs_key='key')
```

**@martinkim0:** @vitkl We could definitely add this feature. Going off of Adam's comment previously, I think it makes sense to name it `stratify_by_obs_key` with an additional argument `stratify_min_size`, which should either raise an error or warning if the minimum split size cannot be achieved.

**@canergen:** To me it sounds most flexible to be able to pass an obs column with train_indices, valid_indices and test_indices and leave it up to the user/developer how to define those. I think other solutions will limit us to certain use cases. @vitkl Would it capture your use case?

**@vitkl:** Thanks for following up! An obs column with custom indices would indeed be great. You mean a column with categories named ['train_indices', 'valid_indices', 'test_indices'], right?

**@ori-kron-wis:** Hi @vitkl

We plan this for the next fix.

The idea is to have the data splitter now accepting also a list of np.arrays of indexes, corresponding to train/valid/test indexes, like this: [train_idx,valid_idx,test_idx].
Although there are some validations for the correctness of the passed indexes, the user is responsible for supporting them in the DataSplitter (as they can originate from many logic and scenarios).

e.g, consider passing stratified train/valid/test indexes based on some batch column (here we do it with sklearn)

`from sklearn.model_selection import train_test_split `

`adata = scvi.data.synthetic_iid()`

see that data is stratified is equal between the batches.
`adata.obs.batch.value_counts()`
Random selection will prevent it from being stratified between …

**@vitkl:** I need some time to understand what you are proposing properly. I am looking for a solution that would work with the default DataSplitter and scVI .train() - rather than implementing a new model to use it.

**@canergen:** Sorry for the confusion. The suggested change is still an open PR: https://github.com/scverse/scvi-tools/pull/2902. After merging, the command will be to call scVI.train(external_indexing=[np.array(train_indices), np.array(valid_indices), np.array(test_indices)]. The splitter will then use these splits instead of random splits. To yield stratified splitting, https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html will do the job.

## #2830: Expected value argument (Parameter of shape (7150,)) to be within the support (Real()) of the distribution Normal(loc: torch.Size([7150]), scale: torch.Size([7150])), but found invalid values: Parameter containing: tensor([nan, nan, nan,  ..
**Issue:** #2830 | **Last activity:** 2024-07-16T00:43:07Z
**State:** closed | **Author:** @Rafael-Silva-Oliveira | **Comments:** 10 | **Created:** 2024-06-06 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2830

<!-- Describe the bug -->

When training the DestVI model I get

Expected value argument (Parameter of shape (7150,)) to be within the support (Real()) of the distribution Normal(loc: torch.Size([7150]), scale: torch.Size([7150])), but found invalid values:
Parameter containing:
tensor([nan, nan, nan,  ..

<!-- To reproduce -->
Following exactly the same steps as this tutorial: https://docs.scvi-tools.org/en/0.18.0/tutorials/notebooks/DestVI_tutorial.html

but using VisiumHD data instead; the sc_model trains just fine with CondSCVI, but st_model fails to train
```python
st_adata = sc.read_h5ad(r".\raw_adata.h5ad")
st_adata.var_names_make_unique()

# sc.pp.filter_genes(st_adata, min_counts=15)
# sc.pp.filter_cells(st_adata, min_genes=5)
st_adata.layers["counts"] = st_adata.X.copy()

sc.pp.normalize_total(st_adata, target_sum=10e4)
sc.pp.log1p(st_adata)
st_adata.raw = st_adata

<605471x7150 sparse matrix of type '<class 'numpy.int32'>'
	with 102773773 stored elements in Compressed Sparse Row format>

st_adata.layers["counts"][150,10:150].toarray()
array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, …

**@canergen:** Hi, this is usually a problem with very low count input spots. It makes sense to remove these low count input spots before running the spatial model (below 20 counts should work, otherwise give it a try with filtering out below 50 counts). It is anyhow hard to imagine that you will get correct estimates or proportions below these numbers.

**@parkjosh-broadinstitute:** Hi @Rafael-Silva-Oliveira I have been running into this error as well. I was wondering if you were able to find a solution?

```
scanvi_ref_path = './models/scanvi_ref'

scvi.model.SCANVI.prepare_query_anndata(query, scanvi_ref_path)
scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref_path)
scanvi_query.train(
    max_epochs=150,
    plan_kwargs={"weight_decay": 0.0, "lr": 0.00001},
    check_val_every_n_epoch=10,
    batch_size=1024
)

query.obsm['X_scanvi'] = scanvi_query.get_latent_representation()
```

**@Rafael-Silva-Oliveira:** > Hi @Rafael-Silva-Oliveira I have been running into this error as well. I was wondering if you were able to find a solution?
>
> ```
> scanvi_ref_path = './models/scanvi_ref'
>
> scvi.model.SCANVI.prepare_query_anndata(query, scanvi_ref_path)
> scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref_path)
> scanvi_query.train(
>     max_epochs=150,
>     plan_kwargs={"weight_decay": 0.0, "lr": 0.00001},
>     check_val_every_n_epoch=10,
>     batch_size=1024
> )
>
> query.obsm['X_scanvi'] = scanvi_query.get_latent_representation()
> ```

It was basically what @canergen mentioned

I had to play around a bit with the QC settings (filter_genes and filter_cells) to find a balance between UMI counts per bin (I'm using 10X Visium HD data) so that each bin had en …

**@canergen:** It's very hard to get rid of this behaviour in DestVI as mentioned above. In our hands these spots are usually anyhow that low in quality. We are working on better support of HD data within a new model released in the coming months. Please stay tuned for the next releases.
@parkjosh-broadinstitute: You are using a different model (scANVI) here. I assume both problems are not related. Can you copy the full error message?

**@Rafael-Silva-Oliveira:** > It's very hard to get rid of this behaviour in DestVI as mentioned above. In our hands these spots are usually anyhow that low in quality. We are working on better support of HD data within a new model released in the coming months. Please stay tuned for the next releases. @parkjosh-broadinstitute: You are using a different model (scANVI) here. I assume both problems are not related. Can you copy the full error message?

Really good to know about the upcoming model! If you don't mind me asking, does it integrate spatial information as well (neighbouring bins, spatial connectivites, or any other spatial information) or will it be trained solely on information from an annotated scRNA?

**@canergen:** One is an updated DestVI designed for data like Curio that are closer to single-cell resolution. For StereoSEQ, we don't use any single-cell data but only spatial structure. I feel strong that these assays are now getting close to single-cell resolution and can actually capture cell-types that are hard to capture in dissociation (more extensive testing in which category HD falls is outstanding). https://www.nature.com/articles/s41587-024-02173-8 falls in the same category. It gets off-topic here and further discussion would be better on discourse.

**@Rafael-Silva-Oliveira:** > One is an updated DestVI designed for data like Curio that are closer to single-cell resolution. For StereoSEQ, we don't use any single-cell data but only spatial structure. I feel strong that these assays are now getting close to single-cell resolution and can actually capture cell-types that are hard to capture in dissociation (more extensive testing in which category HD falls is outstanding). https://www.nature.com/articles/s41587-024-02173-8 falls in the same category. It gets off-topic here and further discussion would be better on discourse.

Sounds promising! Excited to test the models out with the Visium HD data once they're ready. Awesome work!

**@parkjosh-broadinstitute:** Hi @canergen here's the error message that I am getting

```
ValueError                                Traceback (most recent call last)
Cell In[8], line 5
      3 scvi.model.SCANVI.prepare_query_anndata(query, scanvi_ref_path)
      4 scanvi_query = scvi.model.SCANVI.load_query_data(query, scanvi_ref_path)
----> 5 scanvi_query.train(
      6     max_epochs=150,
      7     plan_kwargs={"weight_decay": 0.0, "lr": 0.00001},
      8     check_val_every_n_epoch=10,
      9     batch_size=1024
     10 )
     12 query.obsm['X_scanvi'] = scanvi_query.get_latent_representation()
     13 # query.obs[SCANVI_PREDICTIONS_KEY] = scanvi_query.predict()

File /opt/conda/envs/scvi-env/lib/python3.11/site-packages/scvi/model/_scanvi.py:438, in SCANVI.train(self, max_epochs, n_samples_per_l …

**@canergen:** @parkjosh-broadinstitute this is usually dataset dependent. We find that using a Softplus activation function for the variance stabilizes this behavior. Pass `var_activation=torch.nn.functional.softplus` when you set up your initial scVI model. If the model still occurs, I would recommend to lower learning rate to 1e-4 and train for longer.

**@canergen:** @Rafael-Silva-Oliveira the updated DestVI is working under: https://github.com/scverse/scvi-tools/tree/can_destvi_v2. It will. be released latter this year.

## #2895: Autotuning with Ray: DeprecationWarning: The `RunConfig(local_dir)` argument is deprecated. You should set the `RunConfig(storage_path)` instead.
**Issue:** #2895 | **Last activity:** 2024-07-12T20:54:36Z
**State:** closed | **Author:** @Rafael-Silva-Oliveira | **Comments:** 2 | **Created:** 2024-07-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2895

<!-- Describe the bug -->

When trying to autotune a model, I get an deprecation error

<!-- To reproduce -->
Using this tutorial, but adjusted to my data:

https://docs.scvi-tools.org/en/stable/tutorials/notebooks/tuning/autotune_scvi.html

```python
from scvi.autotune import ModelTuner
from ray import tune
from scvi import autotune

# os.environ["RAY_CHDIR_TO_TRIAL_DIR"] = "0"
# ray.init(runtime_env={"working_dir": "/mnt/work/RO_src/Pipelines/STAnalysis/notebooks/downstream/scRNA"})
# ray.shutdown()
# ray.init(log_to_driver=False)

sc.pp.filter_genes(adata_to_annotate, min_cells=50)

min_cells=25,
min_genes=200
log1p=True
use_raw=False
pct_counts_mt=25
qc_vars=["Mt", "Ribo", "Hb"]

# mitochondrial genes
adata_to_annotate.var["Mt"] = adata_to_annotate.var_names.str.startswith("MT-")
# ribosomal genes
adata_to_annotate.var["Ribo"] = adata_to_annotate.var_names.str.startswith(("RPS", "RPL"))
# hemoglobin genes.
adata_to_annotate.var["Hb"] = adata_to_annotate.var_names.str.contains(
    ("^HB[^(p)]")
)  # adata.var_names.str.contains('^Hb.*-')

sc.pp.calculate_qc_metrics(
    adata=adata_to_annotate,
    qc_vars=qc_vars,
    log1p=log1p,
    use_raw=use_raw,
    percent_top=[20],
    inplace=True,
)
model_cls = scvi.model.SCVI
model_cls.setup_anndata(
    adata_to_annotate,
    categorical_covariate_keys=["Sample"],
    continuous_covariate_keys=["pct_counts_Mt", "pct_counts_Ribo"],
)

tuner = ModelTuner(model_cls=model_cls) …

**@martinkim0:** Thanks for the heads up! I've addressed the issue in #2831, which will be released in v1.2.

**@Rafael-Silva-Oliveira:** > Thanks for the heads up! I've addressed the issue in #2831, which will be released in v1.2.

Perfect! Do we have a release date planned ahead for that version? Thanks

## #2866: How to modify scANVI to handle continuous cell labels?
**Issue:** #2866 | **Last activity:** 2024-07-12T17:57:56Z
**State:** closed | **Author:** @patricks-lab | **Comments:** 1 | **Created:** 2024-06-27 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2866

**Is your feature request related to a problem? Please describe.**

Not a problem - mainly clarification questions. I am wondering how to modify scANVI to handle continuous prediction tasks.

Currently, scANVI assumes that the cell label is drawn from a categorical distribution (https://docs.scvi-tools.org/en/stable/user_guide/models/scanvi.html#generative-process), which is implemented in the code via a cross entropy loss https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/module/_scanvae.py#L271-L274 between the predicted and actual cell labels.

**Describe the solution you'd like**

For continuous prediction tasks, I thought of changing the above cross entropy loss to something like a MSELoss and swapping the `scvi.module.Classifier` with a `scvi.nn.Decoder` layer w/ one output neuron per continuous prediction task. However, I am not sure what other changes (e.g. in the VAE graphical model and/or code) need to be made to accommodate a continuous (e.g. normal) distribution on the cell type label.

(For example, I'd imagine that the derivation for the ELBO for the unobserved cell label case would change with a continuous distribution https://docs.scvi-tools.org/en/stable/user_guide/models/scanvi.html#training-details) but I'm not quite sure how to flesh out the details in such a case.

Alternatively, I also thought of the possibility of simply attaching a scvi.nn.Decoder head on top of scVI w/ MSE loss to predict a contin …

**@canergen:** The structure of scANVI relies on categorical covariates specifically the z1-z2 loss. I would start with scVI and add the continuous classifier using something like MSE loss. You might want to check scANVI if you only have a covariate for some of your cells as it demonstrates how to handle partially labeled data.

## #2628: `CondSCVI.posterior_predictive_sample` fails with `KeyError`
**Issue:** #2628 | **Last activity:** 2024-07-12T17:54:18Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-25 | **Labels:** bug, good first issue, P1 | **URL:** https://github.com/scverse/scvi-tools/issues/2628

This is because `VAEC.sample` [expects](https://github.com/scverse/scvi-tools/blob/main/scvi/module/_vaec.py#L220-L221) the keys `"px_r"` and `"px_rate"` in the generative output, but `generative` only returns the key `"px"`.

## #2622: Allow extending batch key from `CondSCVI` to `DestVI`
**Issue:** #2622 | **Last activity:** 2024-07-12T17:54:07Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-22 | **Labels:** enhancement, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2622

- [x] #2623
- [x] #2624
- [x] #2625

## #2625: Allow `DestVI.from_rna_model` to transfer and extend single-cell batch key
**Issue:** #2625 | **Last activity:** 2024-07-12T17:54:06Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-22 | **Labels:** P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2625

## #2624: Add support for batch embedding representations in `CondSCVI`
**Issue:** #2624 | **Last activity:** 2024-07-12T17:54:02Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-22 | **Labels:** P2 | **URL:** https://github.com/scverse/scvi-tools/issues/2624

## #2616: PyroModelGuideWarmup fails on GPU - probably need to be manually run before `trainer.fit()`
**Issue:** #2616 | **Last activity:** 2024-07-12T17:53:46Z
**State:** open | **Author:** @vitkl | **Comments:** 4 | **Created:** 2024-03-18 | **Labels:** bug, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/2616

<!-- Describe the bug -->

PyroModelGuideWarmup fails on GPU probably because `Callback.setup()` is called in the accelerator environment in the latest PyTorch Lightning.

<!-- To reproduce -->
This test fails on GPU:
```python
pytest tests/model/test_pyro.py::test_pyro_bayesian_regression_low_level --accelerator 'gpu'
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
(cell2state_cuda118_torch22) vk7@farm22-gpu0203:.../software/tests/scvi-tools$ pytest tests/model/test_pyro.py::test_pyro_bayesian_regression_low_level --accelerator 'gpu'
=================================================================== test session starts ===================================================================
platform linux -- Python 3.10.13, pytest-8.1.1, pluggy-1.4.0
rootdir: .../software/tests/scvi-tools
configfile: pyproject.toml
plugins: cov-4.1.0, anyio-4.3.0
collected 1 item

tests/model/test_pyro.py F                                                                                                                          [100%]

======================================================================== FAILURES =========================================================================
_________________________________________________________ test_pyro_bayesian_regression_low_leve …

**@vitkl:** This can probably be addressed using the following modification of the `TrainRunner` or to the `model.train()` method:

```python
class TrainRunner:

    def __call__(self):
        # other code .....

        from copy import copy
        dl = copy(self.data_splitter)
        dl.setup()
        dl = dl.train_dataloader()
        PyroModelGuideWarmup(dl).setup(
            self.trainer, self.training_plan, stage="fit"
        )

        self.trainer.fit(
            self.training_plan, self.data_splitter, ckpt_path=self.ckpt_path
        )
        # other code .....
```

At this stage `self.data_splitter.setup()` has not been called yet and PyTorch Lightning expects to call `self.data_splitter.setup()` later. So we need to copy `self.data_splitter`, call `self …

**@vitkl:** Would be great to hear what you think @martinkim0 and I can add the proposed changes

**@martinkim0:** Hey sorry, took a look at this and forgot to respond. I think it makes sense to add the fixes to `train` instead of the `TrainRunner` since this will be specific to Pyro models. Happy to take a PR if you'd like to take a stab at it!

**@vitkl:** Sounds good! Later this week, I will make a PR about this issue - as well as another issue with the second GuideWarmup callback (pyro doesn't track deterministic variables initialised after setup).

I think we need to get rid of both pyro GuideWarmup callbacks and just run guide once in `model.train()`. This would break how people use them now but IMO a better solution.

## #2546: Bug using "scvi-tools/tabula-sapiens-heart-stereoscope" hugging face scvi model - scvi-tools 1.0.4
**Issue:** #2546 | **Last activity:** 2024-07-12T17:51:12Z
**State:** closed | **Author:** @LysSanzMoreta | **Comments:** 1 | **Created:** 2024-02-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2546

Hi!

I followed this tutorial [scvi-hugging-face](https://colab.research.google.com/github/scverse/scvi-tutorials/blob/1.0.4/hub/scvi_hub_intro_and_download.ipynb#scrollTo=89938623) to load pre-trained scvi models and make some predictions/obtain the latent representation.

This is my current environment:

**env.yaml**

> name: base
> channels:
>   - conda-forge
>   - pytorch
>   - defaults
>   - nvidia
>   - bioconda
> dependencies:
>   - pyopenssl
>   - python=3.9
>   - requests
>   - pip:
>     - -r requirements.txt
>   - numpy
>   - pytorch::pytorch=2.1=py3.9_cuda12.1*
>   - torchvision=>0.16
>   - torchaudio
>   - biopython
>   - h5py
>   - scipy
>   - scikit-learn
>   - pandas
>   - matplotlib
>   - hdf5plugin
>   - pyro-ppl
>   - scanpy
>   - dill
>   - umap-learn
>   - seaborn
>   - dataframe_image
>   - xmltodict
>   - nbconvert
>   - bioconda::cellxgene
>   - conda-forge::lightning
>   - numba
>   - conda-forge::scvi-tools==1.0.4
>   - conda-forge::jax[cuda12_pip]
>   - conda-forge::jaxlib
>   - conda-forge::huggingface_hub
>   - conda-forge::leidenalg

**requirements.txt**

> gget
> cellxgene-census


I  decided to start with this example:

```python
from scvi.hub import HubModel
torch.set_float32_matmul_precision('high')
scvi.settings.seed = 0
repository = "scvi-tools/tabula-sapiens-heart-stereoscope"
hubmodel = HubModel.pull_from_huggingface_hub(repository, cache_dir=None, revision="main")
print(hubmo …

**@martinkim0:** This indeed an issue on our end, apologies. I'll get this fixed ASAP!

## #2471: mamba receipt to use gpu for scvitools
**Issue:** #2471 | **Last activity:** 2024-07-12T17:48:27Z
**State:** closed | **Author:** @qiyubio | **Comments:** 1 | **Created:** 2024-02-06 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2471

**Is your feature request related to a problem? Please describe.**
To make scvitools utilize gpus, Jax, cudatoolkit and torch all have to be installed without conflicts.

**Describe the solution you'd like**
Here is the receipt we used on our cluster, might save others some time:
```
mamba create -n scvi-env python=3.9
mamba activate scvi-env
# install cudatoolkit/11.8 with jax
pip install -U "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
mamba install cudatoolkit
# install torch
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121
# install scvi-tools with scanpy
pip install "scvi-tools[tutorials]"
```

**@martinkim0:** For anyone visiting this thread, please also refer to our [documentation](https://docs.scvi-tools.org/en/latest/installation.html#prerequisites) for how to correctly set up and environment with PyTorch and JAX.

## #2427: Tag commit for scvi-hub manuscript
**Issue:** #2427 | **Last activity:** 2024-07-12T17:46:28Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-22 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2427

## #2387: Incompability between Pandas <2 and >=2 saved models
**Issue:** #2387 | **Last activity:** 2024-07-12T17:46:11Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 3 | **Created:** 2024-01-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2387

Error occurs when a model is saved with Pandas <2 and is attempted to be loaded in with Pandas >=2
```
scvi/model/base/_base_model.py:691: in load
    ) = _load_saved_files(
scvi/model/base/_utils.py:68: in _load_saved_files
    model = torch.load(model_path, map_location=map_location)
../../.../python3.11/site-packages/torch/serialization.py:1014: in load
    return _load(opened_zipfile,
../../.../python3.11/site-packages/torch/serialization.py:1422: in _load
    result = unpickler.load()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <torch.serialization._load.<locals>.UnpicklerWrapper object at 0x7f25fc273b10>
mod_name = 'pandas.core.indexes.numeric', name = 'Int64Index'

    def find_class(self, mod_name, name):
        if type(name) is str and 'Storage' in name:
            try:
                return StorageType(name)
            except KeyError:
                pass
        mod_name = load_module_mapping.get(mod_name, mod_name)
>       return super().find_class(mod_name, name)
E       ModuleNotFoundError: No module named 'pandas.core.indexes.numeric'

../../.../python3.11/site-packages/torch/serialization.py:1415: ModuleNotFoundError
```

**@bio-la:** hey! still have this issue, is there a workaround to update older models? thanks!

**@martinkim0:** Hey! Unfortunately, right now, you'd have to load in older models with pandas<2.0 for it to work. I haven't gotten around to patching this yet, sorry!

**@martinkim0:** Following up on this, this issue is on the PyTorch side since they're not using the newer Pandas unpickler for loading files.

## #2089: ValueError: cannot reindex on an axis with duplicate labels when using DE method
**Issue:** #2089 | **Last activity:** 2024-07-12T17:21:01Z
**State:** closed | **Author:** @jjxia955 | **Comments:** 11 | **Created:** 2023-06-05 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2089

<!-- Describe the bug -->

when i follow try to perform differential expression by one vs the rest, I came across a ValueError like this


ValueError: cannot reindex on an axis with duplicate labels

<!-- To reproduce -->

```python
de_df = vae.differential_expression(
    groupby="rna_subset:leiden_totalVI", delta=0.5, batch_correction=True
)
de_df.head(5)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
DE...:   0%|          | 0/19 [00:03<?, ?it/s]
/usr/local/lib/python3.10/dist-packages/scvi/model/base/_utils.py:270: FutureWarning: reindexing with a non-unique Index is deprecated and will raise in a future version.
  res[f"is_de_fdr_{fdr}"] = _fdr_de_prediction(res["proba_de"], fdr=fdr)
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
[<ipython-input-84-a7e12cf462e5>](https://localhost:8080/#) in <cell line: 1>()
----> 1 de_df = vae.differential_expression(
      2     groupby="rna_subset:leiden_totalVI", delta=0.5, batch_correction=True
      3 )
      4 de_df.head(5)

12 frames
[/usr/local/lib/python3.10/dist-packages/pandas/core/indexes/base.py](https://localhost:8080/#) in _validate_can_reindex(self, indexer)
   4314         # trying to reindex on an axis with duplicates
   4315         if not self._index_as_unique and len(indexer):
-> 4316             raise ValueError("cannot re …

**@martinkim0:** Hi, would you be able to paste the full traceback here? It's hard to tell right now where the error is being raised. Thanks!

**@jjxia955:** ```pytb
DE...:   0%|          | 0/19 [00:03<?, ?it/s]
/usr/local/lib/python3.10/dist-packages/scvi/model/base/_utils.py:270: FutureWarning: reindexing with a non-unique Index is deprecated and will raise in a future version.
  res[f"is_de_fdr_{fdr}"] = _fdr_de_prediction(res["proba_de"], fdr=fdr)
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-84-a7e12cf462e5> in <cell line: 1>()
----> 1 de_df = vae.differential_expression(
      2     groupby="rna_subset:leiden_totalVI", delta=0.5, batch_correction=True
      3 )
      4 de_df.head(5)

12 frames
/usr/local/lib/python3.10/dist-packages/scvi/model/_totalvi.py in differential_expression(self, adata, groupby, gro …

**@jjxia955:** thanks!

**@martinkim0:** @PierreBoyeau could you take a look at this please?

**@PierreBoyeau:** I'm on it!

**@martinkim0:** Is there an update on a fix for this?

**@bfurtwa:** This works for me:

```
def _fdr_de_prediction(posterior_probas: pd.Series, fdr: float = 0.05) -> pd.Series:
    """Compute posterior expected FDR and tag features as DE."""
    if not posterior_probas.ndim == 1:
        raise ValueError("posterior_probas should be 1-dimensional")
    # make index unique
    posterior_probas = posterior_probas.copy().reset_index(drop=True)
    original_index = posterior_probas.index
    sorted_pgs = posterior_probas.sort_values(ascending=False)
    cumulative_fdr = (1.0 - sorted_pgs).cumsum() / (1.0 + np.arange(len(sorted_pgs)))
    d = (cumulative_fdr <= fdr).sum()
    is_pred_de = pd.Series(
        np.zeros_like(cumulative_fdr).astype(bool), index=sorted_pgs.index
    )
    is_pred_de.iloc[:d] = True
    is_pred_de = is_pred_de.loc[orig …

**@matq007:** Hey @jjxia955, make sure your gene names are unique both in `var_names` and `raw.var_names`, that's probably why you see this error. You can check it with

```python
np.sum(adata.var_names.duplicated()) == 0
np.sum(adata.raw.var_names.duplicated()) == 0
```

**@bfurtwa:** Hi @matq007, performing multiple group comparisons will result in genes tested multiple times. So it generates a new row with the same index for each group comparison.

**@racng:** I encounter the same error when using `TOTALVI.differential_expression()`.
I checked that my adata didn't have any duplicated variable names.
```python
# Nothing stored in query.raw
np.sum(query.var_names.duplicated()) == 0
np.sum(query.obsm['protein_counts'].columns.duplicated()) == 0
```

environment:
pandas=2.1.1
scvi=1.0.4

**@martinkim0:** For anyone visiting this thread, this error occurs because protein and genes have the same obs index names. The best way to fix this is to rename the proteins.

## #2033: Data loading and object construction
**Issue:** #2033 | **Last activity:** 2024-07-12T17:19:10Z
**State:** closed | **Author:** @ccruizm | **Comments:** 3 | **Created:** 2023-05-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2033

Good day!

I want to use `MultiVI` to integrate scRNA, scATAC and multiome (RNA+ATAC). I saw in the tutorial you read the files directly form the cellranger output directory, however, I have independent AnnData objects carrying the info for each modality. I tried to used `Muon` to create the paired modality but when trying `scvi.data.organize_multiome_anndatas`, I get an error.

The code I am using is:
```
adata_rna_multiome = sc.read('data/subset_rna_multi.h5ad')
adata_atac_multiome = sc.read('data/subset_atac_multi.h5ad')

adata_paired = mu.MuData({'rna': adata_rna_multiome, 'atac': adata_atac_multiome})

adata_rna = sc.read('data/subset_rna_only.h5ad')
adata_atac = sc.read('data/subset_atac_only.h5ad')

adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired, adata_rna, adata_atac)
```
and the error is:
```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[12], line 2
      1 # We can now use the organizing method from scvi to concatenate these anndata
----> 2 adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired, adata_rna, adata_atac)

File ~/miniconda3/envs/multi_integration/lib/python3.9/site-packages/scvi/data/_preprocessing.py:331, in organize_multiome_anndatas(multi_anndata, rna_anndata, atac_anndata, modality_key)
    328     return multi_anndata.concatenate(other, join="outer", batch_key=modality_key)
    330 if rna_ …

**@martinkim0:** Hi, thank you for your question. `organize_multiome_anndatas` expects all the inputs to be AnnDatas and returns AnnDatas as the final object, and one of your inputs is MuData, which is why it's throwing that error. I would recommend constructing the full MuData yourself as we don't have a function for that in `scvi` yet.

We plan on adding MuData support for MultiVI in v1.1, which won't be out for another couple weeks unfortunately.

**@ccruizm:** Thanks @martinkim0 for your speedy reply!

I have run the pipeline but could not get a proper integration of the different modalities. I want to make sure the input of the data is correct. To be sure, for RNA it receives raw counts and for ATAC is binary data? or does the ATAC data need any preprocessing?

**@martinkim0:** Hi, sorry for following up late. Correct - for RNA it expects raw counts and for ATAC binary. For future reference, we prefer having these types of usage questions in our Discourse forum.

## #2029: Allow SCANVI to operate in purely unsupervised setting
**Issue:** #2029 | **Last activity:** 2024-07-12T17:17:20Z
**State:** closed | **Author:** @aribenjamin | **Comments:** 1 | **Created:** 2023-05-10 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2029

I'd like to be able to use SCANVI for clustering – i.e. to learn this generative model in a purely unsupervised setting in which I do not yet have any cell type labels.

I believe this would be a rather straightforward application of the model. I don't believe any changes need to be made except that the user would need to manually set the number of discrete categories.

Currently, `n_labels` is currently set automatically from the AnnDataManager registered to the class:

```
        n_labels = self.summary_stats.n_labels - 1
```
(at https://github.com/scverse/scvi-tools/blob/cb17e10b2a82dc95c0c8c261e1aef7781c3b0df9/scvi/model/_scanvi.py#LL119C49-L119C50)

To allow `n_labels` to be set to some other value, I propose allowing a new optional argument to `SCANVI` that allows this manual setting, complete with a check that this is greater or equal to `self.summary_stats.n_labels - 1`.

Apart from this change, would anything else be required by the user in practice?

**@martinkim0:** Sorry for the late reply - scANVI is meant for semisupervised learning. An unsupervised model would be very different, happy to take a PR if you have ideas for a new model.

## #1859: Model request: non-negative spatial factorization (NSF)
**Issue:** #1859 | **Last activity:** 2024-07-12T17:09:06Z
**State:** open | **Author:** @aribenjamin | **Comments:** 4 | **Created:** 2023-01-18 | **Labels:** enhancement, new model, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1859

Is anyone currently working on implementing NSF? It's a nice probabilistic method designed with spatial transcriptomics in mind. https://www.nature.com/articles/s41592-022-01687-w

It'd be nice to work with this here, within `scvi-tools`. The authors' implementation (@ https://github.com/willtownes/nsf-paper) is a little hard to parse and implemented with Tensorflow as a backend (which I don't work in).

**@adamgayoso:** I think this would be a nice addition. It might be easiest to implement using tensorflow probability and jax as the kernel functions should be the same; unless of course it's also straightforward in pytorch. Are you willing to contribute this?

**@aribenjamin:** Yes, I'm happy to go for it. It'd be good practice contributing. I can't guarantee any timeline, though, so if someone wants this sooner please ping me.

**@adamgayoso:** Looking into this more, it should be possible with just PyTorch, or just jax+numpyro (which we already depend on), without the introduction of tensorflow probability. @martinkim0 do you want to try this model? It looks both fairly straightforward and fun.

**@aribenjamin:** fyi I have back-burnered this to the point of inaction. If you want to work on this, know that I'm not working in parallel. I'll update this when and if I begin.

## #1840: Finalize scBasset
**Issue:** #1840 | **Last activity:** 2024-07-12T17:07:46Z
**State:** open | **Author:** @adamgayoso | **Comments:** 4 | **Created:** 2023-01-09 | **Labels:** enhancement, help wanted, backlog | **URL:** https://github.com/scverse/scvi-tools/issues/1840

- [x] Verify that all parameters are being initialized equivalently, alter the ones used here if needed
- [x] Add more content to the tutorial that reproduces their results, allowing us to have some form of reproducibility
- [ ] Complete the user guide

**@martinkim0:** @adamgayoso Thoughts on adding a batch correction portion to the tutorial using the buenrostro dataset from the original manuscript?

**@adamgayoso:** I think we should and the maybe use scib metrics on it

**@martinkim0:** I'm wondering whether we should add an option in `setup_anndata` to indicate whether the data is transposed already or not, where if it's not transposed, we do it on our end. It might be confusing for users when you have to `bdata = adata.transpose()` but then the latent space is saved back into the original `adata`.

**@adamgayoso:** I agree this needs improvement. I'm a fan of what you see is what you get and it would be confusing if `model.adata` was transposed

## #1817: scvi-hub enhancements
**Issue:** #1817 | **Last activity:** 2024-07-12T17:06:07Z
**State:** closed | **Author:** @watiss | **Comments:** 0 | **Created:** 2022-12-10 | **Labels:** enhancement, hub | **URL:** https://github.com/scverse/scvi-tools/issues/1817

See [this](https://github.com/scverse/scvi-tools/pull/1812) PR for more context

- [x] Account for data/model prefixes -> we chose not to do this to keep naming cohesive across the board (+ given that we control both saving and loading from this api)
- [x] Do we need to use a different name than "Large data"?
- [x] There might be a more efficient way of reading the latent property from adata that doesn't require reading the file. Note that this would only matter for datasets with large metadata (obs/obsm/etc.) since .X is anyways backed on disk. So for most datasets this would bring a marginal improvement.
- [x] Consider using an enum or named tuple for constants
- [x] [functools.cached_property](https://docs.python.org/3/library/functools.html#functools.cached_property) might help cleaning up some code -> since I evaluate the `None`-ness of those attributes (see `eval_obj`) inside `__repr__`, I think I would prefer to avoid using `cached_property` in this case.
- [ ] Can we make a hf space to help query hf?
- [ ] Make an issue in [huggingface_hub](https://github.com/huggingface/huggingface_hub/issues) to provide an API for retrieving a pandas DataFrame of all ModelInfo's, rather than lose string representations.

## #841: scANVI does not compute the conditioned ELBO
**Issue:** #841 | **Last activity:** 2024-07-12T17:04:21Z
**State:** closed | **Author:** @PierreBoyeau | **Comments:** 1 | **Created:** 2020-10-27 | **Labels:** bug, scanvi, P0 | **URL:** https://github.com/scverse/scvi-tools/issues/841

<!-- Describe the bug -->
The current implementation of scANVI only computes the ELBO without relying on the cell states' knowledge for labeled examples (see [here](https://github.com/YosefLab/scvi-tools/blob/master/scvi/core/trainers/annotation.py#L200)).
We should fix this behavior and treat labeled and unlabelled examples separately.

There are two options to consider to code this. The first one would use only one data loader, and compute the proper ELBO for each data-point. In the other option, in phase with the current codebase, we would compute the marginalized ELBO for a minibatch of unlabelled cells, and the conditioned ELBO for labelled cells. The overall ELBO would be weighted out based on the labelled fraction of the training data. I would opt for the second option.

However, I don't know which default behavior and training options we should provide. Should the current behavior still be an option?

#### Versions:
<!-- Output of scvi.__version__ -->
> VERSION

<!-- Relevant screenshots -->

**@martinkim0:** Closing this in favor of #1784

## #1640: additive effects for background RNA correction in scVI
**Issue:** #1640 | **Last activity:** 2024-07-12T17:01:20Z
**State:** closed | **Author:** @vitkl | **Comments:** 5 | **Created:** 2022-08-17 | **Labels:** enhancement, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/1640

## Introduction

I would argue that after 5+ years of analysing droplet-based sc/snRNA-seq data, we know the top-N technical RNA detection effects:

1. Per-batch (10x reaction/inlet) detection rate originating from PCR+sequencing step, in part due to the sequencing budget normally allocated to 10x reactions.
2. Within-batch per cell RNA detection efficiency originating from RT variability between droplets.
3. Background RNA contamination originating from free-floating/ambient/soup RNA, cell barcode swapping, other mechanisms as described in detail by CellBender authors (https://github.com/broadinstitute/CellBender). This effect is specific to batch (10x reaction/inlet).
4. Technology and gene-specific RNA detection efficiency. For example, 5' vs 3' 10x technology. Other technologies such as probe-hybridisation-based methods could have the more complex gene- and batch-specific RNA detection efficiency effects.
5. Add yours

Note that here, the goal is to enumerate and correct for as many technical effects as possible retaining all other heterogeneity as biology - even if the biological change in expression is induced by experiment factors such as cell dissociation-induced stress or disease effects.

![image](https://user-images.githubusercontent.com/22567383/185010417-df2701e0-71f8-4038-bf3f-fab8be5aca8a.png)

Effects 1, 2 and 4 are multiplicative in nature because they change RNA detection rates - while effect 3 is inherently additive, because ambient RNA is phy …

**@adamgayoso:** I think I need more time to digest this! But would you be willing to move it over to [discourse](https://discourse.scverse.org/)? You can use $ $ for inline math and $$ $$ for math blocks there with latex rendering.

**@ricomnl:** I've implemented a working version of this [paper](https://www.biorxiv.org/content/10.1101/2022.01.14.476312v4.full.pdf) in an external scvi module: https://github.com/ricomnl/scvi-ar/pull/1/files. Am currently running some tests but I will create a PR to merge this in

**@vitkl:** Thank you @ricomnl ! I will read that paper. One common issue is assuming that the background RNA constitute the same proportion rather than the same absolute number. This is a problem because cell types with more RNA are assumed to have more background which is not true for free-floating RNA. Cell barcode swapping can indeed lead to a higher background in cell types with more RNA - but barcode swapping seems to be lower than snRNA free-floating contamination. How does this paper address this?

scVI model is quite popular so there is also an argument for including background correction directly into scVI.

Another issue is that we don't have count matrices for empty droplets for many multi-atlas integration projects. Those are possible to generate by completely remapping data but that …

**@vitkl:** @adamgayoso As we discussed elsewhere, the reason I created an issue rather than scverse discussion is that I think this is a very concrete implementable suggestion. However, I need some explanation of how to add/modify variables in scVI code.

**@martinkim0:** We have a version of this implemented in `scvi.external.SCAR`.

## #1545: scANVI classification uncertainty extraction method
**Issue:** #1545 | **Last activity:** 2024-07-12T16:52:44Z
**State:** closed | **Author:** @LuckyMD | **Comments:** 3 | **Created:** 2022-05-23 | **Labels:** enhancement, scanvi | **URL:** https://github.com/scverse/scvi-tools/issues/1545

It would be very useful to have some quantification of model uncertainty for the scANVI cell type classification output. In the simplest form this could be the softmax output from the penultimate layer. Ideally, it would be a separately trained linear activation function output as softmax will probably exaggerate the differences in uncertainties leading to poor calibration. The simple output would already be useful I think.

**@PierreBoyeau:** Hi, it sounds like [this](https://github.com/scverse/scvi-tools/blob/cc38acc8d72d1b03ef3592cb1699114dcd040438/scvi/model/_scanvi.py#L259) already returns the softmax outputs.

**@LuckyMD:** Ah, I must have missed that, thanks! I'll test it out soon! I guess then my feature request slims down to the calibrated linear layer for probabilities :).

**@martinkim0:** With the fixed scANVI released with v1.1, we are seeing better calibration performance in the classifier.

## #1086: scANVI predict method should return observed labels instead of predicted
**Issue:** #1086 | **Last activity:** 2024-07-12T16:48:44Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 1 | **Created:** 2021-06-02 | **Labels:** enhancement, scanvi | **URL:** https://github.com/scverse/scvi-tools/issues/1086

Right now, scANVI returns the prediction for both the cells with unobserved labels and observed labels. We should add a parameter (and default True) to return the observed labels for cells with observed labels.

Related to this discourse [post](https://discourse.scvi-tools.org/t/scanvi-relables-known-cells-with-known-types-incorrectly/98/6)

**@martinkim0:** For anyone visiting this thread, we'd recommend subsetting the observations after running the `predict` method. It can also be useful to predict labels for observed cells for certain use cases.

## #1083: Parallelizable differential expression
**Issue:** #1083 | **Last activity:** 2024-07-12T16:46:51Z
**State:** closed | **Author:** @Munfred | **Comments:** 1 | **Created:** 2021-05-31 | **Labels:** enhancement, differential expression | **URL:** https://github.com/scverse/scvi-tools/issues/1083

I find myself frequently doing pairwise differential expression for all clusters in the data, and sometimes I end up running it as an overnight job.

It would be very handy if the DE could be parallelizable on the CPUs available, since DE is fairly fast on CPU already (in my experience doing DE on CPU only is about half as fast as when a GPU is available).

**@martinkim0:** For anyone visiting this thread - we recommend doing one vs. all comparisons for differential expression since there's fewer computations. And you can do pairwise comparisons for close cell types, but not for all of them.

## #696: Possibility of having different number of units in the hidden layers
**Issue:** #696 | **Last activity:** 2024-07-12T16:37:16Z
**State:** closed | **Author:** @gprashant17 | **Comments:** 1 | **Created:** 2020-07-04 | **Labels:** enhancement, good first issue, P2 | **URL:** https://github.com/scverse/scvi-tools/issues/696

<!-- Describe the question, be sure to specify which model you're referring to -->
I would like to know if it is possible for the VAE model (in scVI) to have different number of hidden units in each hidden layer. Currently, I am assuming that there can only be one or more hidden layers with the same number of hidden units, as the argument `n_hidden` takes only one integer value rather than a list of values.

**@adamgayoso:** This is not currently possible, but if you would like to make a PR implementing this, we can probably benefit from this functionality.

## #2784: AttributeError: module 'scvi' has no attribute 'autotune'
**Issue:** #2784 | **Last activity:** 2024-07-12T16:29:14Z
**State:** closed | **Author:** @itamarb-cgen | **Comments:** 4 | **Created:** 2024-05-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2784

<!-- Describe the bug -->

autotune fails with an error message _no attribute 'autotune'_.
I created a fresh conda environment with the latest scvi-tools on python 3.11.
Please advise,
Itamar
<!-- To reproduce -->

```python
tuner = scvi.autotune.ModelTuner(model_cls)
tuner
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[15], line 1
----> 1 tuner = scvi.autotune.ModelTuner(model_cls)
      2 tuner

AttributeError: module 'scvi' has no attribute 'autotune'
```

#### Versions:
```python
print (scvi.__version__)
```
> 1.1.2
```python
sc.logging.print_header()
```
> scanpy==1.10.1 anndata==0.10.7 umap==0.5.5 numpy==1.26.4 scipy==1.13.0 pandas==2.2.2 scikit-learn==1.4.2 statsmodels==0.14.1 igraph==0.11.5 pynndescent==0.5.12
<!-- Relevant screenshots -->

**@martinkim0:** Hi, please try `from scvi.autotune import ModelTuner`

**@itamarb-cgen:** Thank you Martin!
This indeed helped proceed.
Note that a few more installations are needed:
`conda install hyperopt
pip install "ray[tune]"
`
with
`from ray import tune`

Unfortunately, I encounter another error later in `tuner.fit`:
'ValueError: Grid search parameters cannot be automatically converted to a HyperOpt search space.'
What can be the problem here?
Best regards,
Itamar

**@martinkim0:** Hi, sorry forgot to mention, you can install all autotune dependencies with
```bash
pip install -U "scvi-tools[autotune]"
```

For the error message, could you share the code you're running? Thanks

**@martinkim0:** Closed due to inactivity

## #2810: bug for custom classifier in adversarial training plan
**Issue:** #2810 | **Last activity:** 2024-07-05T19:41:14Z
**State:** closed | **Author:** @SabrinaRichter | **Comments:** 2 | **Created:** 2024-05-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2810

<!-- Describe the bug -->

When trying to use a custom classifier in the adversarial training plan, i get an `scvi 'AdversarialTrainingPlan' object has no attribute 'n_output_classifier'` error, I think because it's not set here https://github.com/scverse/scvi-tools/blob/dcadecbc26979af916b92ba07c979535a4a32a48/src/scvi/train/_trainingplans.py#L526 similar to the case above, but it's used 6 lines further down.

**@canergen:** Hi, thanks for trying to build on top of scVI-tools. To give a reasonable response, we will need more background than ‚custom classifier‘. What are you trying to do and how do you define it?
The easiest would be to add an additional batch key for adversarial training and I can share code for this.

**@canergen:** Closed due to inactivity.

## #2836: Trying to run PeakVI model returns mpi4py error
**Issue:** #2836 | **Last activity:** 2024-07-05T19:41:01Z
**State:** closed | **Author:** @Sun-storm | **Comments:** 2 | **Created:** 2024-06-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2836

<!-- Describe the bug -->
Whenever I try to run the model or (after having run the model somewhere else) I try to access it with `model = scvi.model.PEAKVI.load(model_dir, adata=adata)` I get the bug shown bellow. I've tried installing openMPI and quite a few other things, but nothing seems to work.


<!-- To reproduce -->

```python
python
Python 3.12.2 | packaged by conda-forge | (main, Feb 16 2024, 20:50:58) [GCC 12.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> import tempfile
>>> from pathlib import Path
>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> import pooch
>>> import scanpy as sc
>>> import scvi
>>> import torch
>>> os.chdir('/home/.../data')
5ad')
model_dir = os.path.join("model/peakvi_trained", "model.pt")
model = scvi.model.PEAKVI.load(model_dir, adata=adata)
>>> adata = scvi.data.read_h5ad('combined_seurat_object.h5ad')
>>> model_dir = os.path.join("model/peakvi_trained", "model.pt")
>>> model = scvi.model.PEAKVI.load(model_dir, adata=adata)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb

/services/tools/scvi-tools/1.1.2/lib/python3.12/site-packages/torch/cuda/__init__.py:619: UserWarning: Can't initialize NVML
  warnings.warn("Can't initialize NVML")

--------------------------------------------------------------------------------
<stdin> 1 <module>
1

_base_model.py 662 load
_, _, device = pa …

**@canergen:** This seems to be a problem with your CUDA installation on a specific workstations. Actually torch can't initialize. Can you check that: `nvidia-smi` works within the command line and that functions like:
`>>> import torch

>>> torch.cuda.is_available()
True

>>> torch.cuda.device_count()
1

>>> torch.cuda.current_device()
0

>>> torch.cuda.device(0)
<torch.cuda.device at 0x7efce0b03be0>

>>> torch.cuda.get_device_name(0)
'GeForce GTX 950M'`

If these don't work and you can't set up a new environment with only installing a CUDA enabled torch, you might want to check with your system administrator or update your CUDA drivers yourself.

**@canergen:** Closed due to inactivity.

## #2851: AttributeError: module 'numpy' has no attribute 'str'.
**Issue:** #2851 | **Last activity:** 2024-07-04T10:39:15Z
**State:** closed | **Author:** @klshen8386 | **Comments:** 5 | **Created:** 2024-06-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2851

seeing AttributeError: module 'numpy' has no attribute 'str'. when running code below (loading pbmc dataset)

<!-- To reproduce -->

```python
adata = scvi.data.pbmc_dataset()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: module 'numpy' has no attribute 'str'.
`np.str` was a deprecated alias for the builtin `str`. To avoid this error in existing code, use `str` by itself. Doing this will not modify any behavior and is safe. If you specifically wanted the numpy scalar type, use `np.str_` here.
The aliases was originally deprecated in NumPy 1.20; for more details and guidance see the original release note at:
    https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
```

#### Versions:

<!-- Output of scvi.__version__ -->

> 0.20.3

<!-- Relevant screenshots -->

**@martinkim0:** Hi, does the error replicate with scvi-tools >= 1.0.0? If you need 0.20.3 for reproducibility purposes, I would downgrade numpy to 1.20 or below.

**@klshen8386:** Hello, for dependency reasons I require scvi-tools < 1.0.0 > 0.16.0, however when I attempt to downgrade numpy below 1.20 (in this case, 1.19), I am receiving the error RuntimeError: Running cythonize failed! error: metadata-generation-failed

**@martinkim0:** Can you try numpy 1.23 instead? I believe np.str was removed in 1.24.

**@klshen8386:** Issue fixed - numpy 1.23 was compatible with scvi-tools 0.20.3. Thank you!

**@Skyer19:** > Can you try numpy 1.23 instead? I believe np.str was removed in 1.24.

Hi, I also have the same issue these days.
I installed both numpy==1.23 and scvi-tools 0.20.3 with Python3.9.19 but it did not work. :(

```
AttributeError: module 'numpy' has no attribute 'str'.
`np.str` was a deprecated alias for the builtin `str`. To avoid this error in existing code, use `str` by itself. Doing this will not modify any behavior and is safe. If you specifically wanted the numpy scalar type, use `np.str_` here.
The aliases was originally deprecated in NumPy 1.20; for more details and guidance see the original release note at:
    https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
```

## #2880: Update release checklist and documentation for new release workflow
**Issue:** #2880 | **Last activity:** 2024-07-03T16:02:07Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-06-30 | **URL:** https://github.com/scverse/scvi-tools/issues/2880

**@martinkim0:** Closed via #2882

## #824: AttributeError: module 'scvi' has no attribute 'data'
**Issue:** #824 | **Last activity:** 2024-07-03T15:03:50Z
**State:** closed | **Author:** @aralbright | **Comments:** 32 | **Created:** 2020-10-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/824

<!-- Describe the bug -->
Hi, I've got my data to a point where I'd like to use scVI for batch correction, but for some reason it's not working properly. scVI by itself imports just fine, but I'm not sure why it's not recognizing any scvi functions.

<!-- To reproduce -->
```python
scvi.data.setup_anndata(data, layer="raw")
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->
```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
<ipython-input-36-294ac6c9fc9d> in <module>
----> 1 scvi.data.setup_anndata(data, layer="raw")

AttributeError: module 'scvi' has no attribute 'data'

```

#### Versions:
<!-- Output of scvi.__version__ -->
> scvi-tools 0.7.0a5

Thanks!

Ashley

**@galenxing:** Hi @aralbright!

We changed the file structure on the backend when going from our alpha to beta release, so you'll need to upgrade scvi via:

`pip install scvi-tools -U`

or

`conda update scvi-tools`

depending on how you installed.

Best,
Galen

**@aralbright:** Thanks! I used pip to install it yesterday so I assumed everything was up to date, was this a _super_ recent change and I just got unlucky?

**@galenxing:** Huh, thats weird, the latest version was released 9/28. But hopefully just running the upgrade commend should work then!

**@aralbright:** It did, thanks! Running ```model.train()``` now :)

**@slagtermaarten:** Hi, I'm currently experiencing the same problem. I have scvi-tools 7.1 (newest according to pip), any ideas? Thanks!

**@galenxing:** @slagtermaarten Sorry to hear that!

Can you provide the output of:
`import scvi; print(scvi.__version__)`

**@slagtermaarten:** @galenxing Thanks for you quick reply!

I resolved the problem. Even though I had activated my new conda env, starting the python interpreter actually started a wrong version of python (3.7.6), in which I guess the old version of scvi was installed. If I start `python3.8` in a yet another newly created environment, I do manage to get past this step -- I get `scvi.__version__ == 7.1`

**@galenxing:** @slagtermaarten Glad to hear!

**@DRSEI:** > Hi, I've got my data to a point where I'd like to use scVI for batch correction, but for some reason it's not working properly. scVI by itself imports just fine, but I'm not sure why it's not recognizing any scvi functions.
>
> ```python
> scvi.data.setup_anndata(data, layer="raw")
> ```
>
> ```
> ---------------------------------------------------------------------------
> AttributeError                            Traceback (most recent call last)
> <ipython-input-36-294ac6c9fc9d> in <module>
> ----> 1 scvi.data.setup_anndata(data, layer="raw")
>
> AttributeError: module 'scvi' has no attribute 'data'
> ```
>
> #### Versions:
> > scvi-tools 0.7.0a5
>
> Thanks!
>
> Ashley

Hello Everyone I am having the same issue.

import scvi; print(scvi.__version__)  0.1 …

**@adamgayoso:** @DRSEI we have since updated the API such that the code you are trying no longer works.

Please see the new workflow

https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html

**@DRSEI:** hi @adamgayoso  Thank you so much

**@bigtimecodersean:** Hey guys, I am running into a similar issue. I am trying to run the introductory tutorial: https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html

I am getting stuck on loading the data in the Colab tutorial. Keep getting the error that:

"module 'scvi' has no attribute 'data'"

when I run:

"adata = scvi.data.heart_cell_atlas_subsampled()"

Anything / dependencies that I might be missing ?

**@bigtimecodersean:** To add one additional variable to the above ^. Throughout my code, in the first few cells of the tutorial, I am getting the message:

 WARNING: Ignoring invalid distribution -orch (/usr/local/lib/python3.7/dist-packages)

**@adamgayoso:** @bigtimecodersean how did you install scvi-tools?

**@bigtimecodersean:** Thanks for the quick response.
I tried installing scvi and scvi-tools today using

pip install scvi
pip install scv -U
pip install scvi-tools

**@adamgayoso:** Please install using the instructions [here](https://docs.scvi-tools.org/en/stable/installation.html). Specifically, do not use `pip install scvi` as this is an old unmaintained package.

**@royfrancis:** I am confused. Do we need both scvi and scvi-tools? The [installation page](https://docs.scvi-tools.org/en/stable/installation.html) only mentions scvi-tools but [other pages](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) mentions `import scvi`. Does `import scvi` import `scvi-tools`?

```
>>> import scvi
>>> scvi.model.SCVI.setup_anndata(adata, layer="counts", categorical_covariate_keys="donor_id")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'scvi' has no attribute 'model'

>>> scvi.__version__
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'scvi' has no attribute '__version__'
```

From `conda list`, I can see that I have **scvi-tools 0.8.1** …

**@adamgayoso:** installing scvi-tools allows `import scvi`. This would be similar for scikit-learn and `sklearn`.

The old `scvi` package that you see is a previous iteration of this work that you *do not* want

**@royfrancis:** Ok. I have removed scvi and only have scvi-tools. I still get this error:

```
>>> scvi.model.SCVI.setup_anndata(adata, layer="counts", categorical_covariate_keys="donor_id")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'scvi' has no attribute 'model'
```

**@royfrancis:** Hmm.. I see that the scvi-tools version I got is **0.8.1** while [conda](https://anaconda.org/conda-forge/scvi-tools) seems to have **0.20.1**. Perhaps that's why. And for me, conda refuses to update this package. Possibly conflicting with some other package.

Update: Ok. cellxgene was messing up the conda env. Removed that, updated fsspec, pytorch-lightning and finally scvi-tools to **0.20.1** which solved this issue.

**@Agamart:** Edit: downgrading anndata to 0.8 version solved the problem.

Dear all, I am running into a similar issue. Installation of scvi-tools was a bit problematic for me (Apple Silicon, M1 max), I installed it on miniforge3 venv with arm64 architecture. now I have problem with 'import scvi' command. My error message:
AttributeError: module 'anndata.compat' has no attribute 'Literal'
I have tried the newest version of scvi-tools 0.20 (but also 0.19 and 0.18 gives the same error).
Can somebody please help me? Thank you!

**@hongruhu:** similar issue when I ran `scvi.model.SCVI.setup_anndata(adata_concat, layer="counts", batch_key="batch")`
the error is `AttributeError: module 'scvi' has no attribute '__version__'`
`scvi.__version__ = '0.20.3'`

**@adamgayoso:** @hongruhu can you provide the full traceback?

**@hongruhu:** @adamgayoso here you go, thanks!
```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Input In [169], in ()
----> 1 scvi.model.SCVI.setup_anndata(adata_concat, layer="counts")

File [/share/miniconda3/envs/tangram/lib/python3.8/site-packages/scvi/model/_scvi.py:208](https://file+.vscode-resource.vscode-cdn.net/share/miniconda3/envs/tangram/lib/python3.8/site-packages/scvi/model/_scvi.py:208), in SCVI.setup_anndata(cls, adata, layer, batch_key, labels_key, size_factor_key, categorical_covariate_keys, continuous_covariate_keys, **kwargs)
    206 if adata_minify_type is not None:
    207     anndata_fields += cls._get_fields_for_adata_minification(adata_minify_type)
--> 208 adata_m …

**@adamgayoso:** @hongruhu how did you install scvi? Do you happen to be in a python file called scvi.py?

**@hongruhu:** @adamgayoso I did pip install and I could print `scvi.__version__`

**@ShaowenJ:** @Agamart Hi, I am encountering the same issue, how did you solve this previously?

**@canergen:** Hi, this points to a wrong installation. Can you share your Python version and whether you followed our tutorials to install scVI-tools. Please also provide the exact error message.

**@emdann:** This issue still lives.

Just trained a model, loading with
```python
model = scvi.model.SCVI.load(model_path)
```
throws
```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[7], line 1
----> 1 model = scvi.model.SCVI.load(f"{data_dir}/{dataset_name}_model_scvi/")

File /oak/stanford/groups/pritch/users/emma/miniforge3/envs/perturb-vs-tissue-env/lib/python3.10/site-packages/scvi/model/base/_base_model.py:706, in BaseModelClass.load(cls, dir_path, adata, accelerator, device, prefix, backup_url)
    702 # Calling ``setup_anndata`` method with the original arguments passed into
    703 # the saved model. This enables simple backwards compatibility in the case of …

**@canergen:** Hi, have you modified the code? Sometimes when I modify code, the version is not correctly loaded. Another problem is jupyter notebooks autoreload that can throw these problems. Otherwise, how have you installed scvi-tools?

**@emdann:** No autoreload or changes to the code here.

I installed on a conda env running:
```
pip install scvi-tools
```

**@canergen:** This is weird. Is it dependent on loading this specific model and can you initialize a model without problems and afterwards load it?

## #2869: solo.predict() should take an argument to return Non-softmax transformed values, and return logits like previous iterations to allow for non-breaking change that was implemented in 1.1.3
**Issue:** #2869 | **Last activity:** 2024-06-30T19:47:54Z
**State:** closed | **Author:** @barstuart | **Comments:** 2 | **Created:** 2024-06-30 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2869

**Is your feature request related to a problem? Please describe.**
Previous fixes for solo (https://github.com/scverse/scvi-tools/pull/2689) and issue reported https://github.com/scverse/scvi-tools/issues/2688 , implemented a breaking change with no way to return logits. Some of us still use non-probability values in their pipelines.

**Describe the solution you'd like**
I have implemented a quick fix for the above by creating a new argument for the solo.predict() function that allows users to return non-softmax normalized probabilities, and return the logits as in previous iterations, thus allowing a non-breaking fix in 1.1.3.

Here is the relevant code that i suggest be implemented

```

    @torch.inference_mode()
    def predict(self, soft: bool = True, include_simulated_doublets: bool = False, return_logits: bool = False) -> pd.DataFrame:
        """Return doublet predictions.

        Parameters
        ----------
        soft
            Return probabilities instead of class label.
        include_simulated_doublets
            Return probabilities for simulated doublets as well.
        return_logits
            Return logits instead of probabilities.

        Returns
        -------
        DataFrame with prediction, index corresponding to cell barcode.
        """
        warnings.warn(
            "Prior to scvi-tools 1.1.3, `SOLO.predict` with `soft=True` (the default option) "
            "returned logits instead of probabilities. Th …

**@martinkim0:** I think this change makes sense for reproducibility with previous versions, thanks for the suggestion. I'll add this change.

**@martinkim0:** The change will be released with 1.1.4!

## #991: Module tutorial should discuss LossRecorder
**Issue:** #991 | **Last activity:** 2024-06-27T21:46:31Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2021-03-06 | **Labels:** tutorials | **URL:** https://github.com/scverse/scvi-tools/issues/991

Galen recently added functionality to store arbitrary things there too. There should be a few sentences about what it does.

## #1613: Improve documentation on `batch_key` vs `categorical_covariate_keys`
**Issue:** #1613 | **Last activity:** 2024-06-27T18:27:48Z
**State:** closed | **Author:** @justjhong | **Comments:** 2 | **Created:** 2022-07-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1613

The documentation differentiating batch_key and categorical_covariate_keys currently does not clarify the difference between them well.

From chat with Allon:

1. is there a difference if I add a discrete batch ID under the batch_key or the categorical_covariate_keys arguments of setup_anndata?
2. Is the labels_key argument used in any way?

1. with the default settings the batch key and categorical covariate keys behave the same. However, if dispersion="gene-batch"  the model will learn batch-specific dispersion parameters (px_r in the codebase). Additionally if use_observed_lib_size=False the model will treat library size as a random variable and the prior distribution is set to a normal distribution with mean variance computed specific to each batch.
2. labels_key is only used if dispersion="gene-label" which learns label-specific dispersion parameters. Otherwise, it is mostly kept as a convenience for this from_scvi_model [method](https://github.com/scverse/scvi-tools/blob/master/scvi/model/_scanvi.py#L162) in scanvi. Not a great reason, but it would most likely break pipelines if removed now.

**@canergen:** I think the main difference is that there is transform_batch in generating the posterior expression, while there is no transform_covariate.
In line of this, px_r doesn't support gene times other obs. I generally use it mainly when there are different technologies present. Setting batch to the technology ignores all patient batches and disables projecting to a single experimental batch while setting batch to patient_id gives higher chances of overfitting px_r (e.g. 2 technologies and 50 batches in total). One can set label to technology and use gene-label for px_r (I dislike the naming though).

**@martinkim0:** closed via #2865

## #2288: Add FAQ page in documentation
**Issue:** #2288 | **Last activity:** 2024-06-27T18:21:07Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-10-11 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2288

Ideas:

- BatchNorm error with 1 obs in batch
- NaNs during training
- Difference between batch and categorical covariates #1613

## #2337: question on mismatch peak to gene association
**Issue:** #2337 | **Last activity:** 2024-06-27T17:10:32Z
**State:** closed | **Author:** @marjorieb12345 | **Comments:** 1 | **Created:** 2023-11-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2337

<!-- Describe the bug -->

Hello,

I would like to know how MultiVI associates ATACseq peaks to genes. Does it associate it to TSS up/down some specific distance, or does it associate it to to the full gene including introns?
We run MultiVI on multiomics (TEAseq) data but found that in many cases the open chromatin regions do not match with the regions of gene expression on the joint UMAP representation.

Also, in your tutorial you say: In a well-mixed space, MultiVI can seamlessly impute the missing modalities for single-modality cells. First, imputing expression and accessibility is done with get_normalized_expression and get_accessibility_estimates, respectively. Does that mean for paired data, we still also need to use those function to get the gene expression and the accessibility for   the same gene? Let's say if i want to plot the gene expression and the accessibility of the gene POLR2A on the same latent space, could you provide a code to complete the tutorial?

We noticed that in the tutorial, there is no information on the genome database (e.g. hg38 or hg19). Does the program knows what database to use?

Thank you for your help

Marjorie

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

<!-- Relevant screen …

**@canergen:** @marianogabitto Can you provide insights?

## #2434: Add user API for using arbitrary dataloaders
**Issue:** #2434 | **Last activity:** 2024-06-27T17:10:14Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-25 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2434

Model spec:

- Make `adata` an optional argument for model initialization
- Set a lazy module init flag if `adata` is not passed as we won't know parameters like `n_batch` and `n_labels` until the dataloader is specified
- `train` method takes in an optional `datamodule` argument that corresponds to a `LightningDataModule`. If this is the case, then the module is initialized here

Datamodule spec:

- Subclasses `LightningDataModule`
- Must define properties such as `n_batch`, `n_vars`, `n_labels`, etc.
- `train_dataloader` and `val_dataloader` must return dataloaders that yield dictionaries with registry keys
- Can define a `pack_tensors_into_dict` static method that organizes outputs from dataloaders into dictionary with registry keys if dataloaders don't directly yield in this format

## #2619: Add torch neuron support for scvi tools
**Issue:** #2619 | **Last activity:** 2024-06-27T17:09:58Z
**State:** closed | **Author:** @LinearParadox | **Comments:** 3 | **Created:** 2024-03-19 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2619

Torch neuron is a PyTorch architecture that enables it to use AWS based Trainium and Inferentia gpu instances. Since these are somewhat cheaper, especially for large models that may be a little too large for GPUs such as T4s, but also not worth an A100. It would be a nice addition

**@martinkim0:** I'm not familiar with torch-neuron, what sort of changes would be necessary in order to enable this?

**@LinearParadox:** I think there would likely have to be some analogous code added. For example something like:
```
if use_neuron:
    Neuron training code
else:
    normal training code
```

The API seems pretty analogous to PyTorch:

https://awsdocs-neuron.readthedocs-hosted.com/en/latest/frameworks/torch/torch-neuronx/programming-guide/training/pytorch-neuron-programming-guide.html#pytorch-neuronx-programming-guide

I'm not super experienced with torch, but I can also try to dig in after this week to try and see if it's a trivial modification or entails a larger redesign.

The one major difference that might pose an issue is that neuron builds graphs lazily, while PyTorch doesn't. Not sure how impactful this will be practically though

**@martinkim0:** Let me know if you're able to look into this! Would be happy to take a PR if it's a small modification. If it seems like it's going to be a larger redesign, I think it would make sense for us to discuss it internally before anything is implemented.

## #2716: Update CI description in maintenance guide
**Issue:** #2716 | **Last activity:** 2024-06-27T16:59:32Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-04-10 | **URL:** https://github.com/scverse/scvi-tools/issues/2716

**@martinkim0:** closed via #2858

## #2819: Release 1.1.3
**Issue:** #2819 | **Last activity:** 2024-06-27T04:24:53Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-05-29 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2819

-   [x] Bump version in `pyproject.toml` #2704
-   [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules #2705
-   [ ] ~Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch~
-   [ ] ~After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image~
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged https://github.com/scverse/scvi-tutorials/releases/tag/1.1.3
-   [x] Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed #2852
-   [x] Create a new GitHub release targeting the release branch with the same body as the previous release https://github.com/scverse/scvi-tools/releases/tag/1.1.3
-   [x] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/) https://pypi.org/project/scvi-tools/1.1.3/
-   [ ] ~Build new Docker images with the `stable` and semantic versioning tags~
-   [x] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly https://github.com/conda-forge/scvi-tools-feedstock/pull/43
-   [ ] ~(Optional) Post threads on Discourse and Twitter~

## #2562: Enable custom dataloader usage with autotune
**Issue:** #2562 | **Last activity:** 2024-06-26T23:06:28Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-27 | **URL:** https://github.com/scverse/scvi-tools/issues/2562

**@martinkim0:** Closed via #2605

## #2537: Add workflow for releases
**Issue:** #2537 | **Last activity:** 2024-06-26T23:05:16Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-02-21 | **Labels:** CI/CD, releases | **URL:** https://github.com/scverse/scvi-tools/issues/2537

- Take as input the release tag
- Run PyPI publishing workflow
- Build Docker images on success

**@martinkim0:** see
https://github.com/astral-sh/ruff/blob/main/.github/workflows/release.yaml

https://github.com/softprops/action-gh-release

## #2849: Error in py_call_impl(callable, call_args$unnamed, call_args$named)
**Issue:** #2849 | **Last activity:** 2024-06-24T06:05:50Z
**State:** closed | **Author:** @Ares1314 | **Comments:** 2 | **Created:** 2024-06-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2849

Hi,
When I use scvi in R, errors occur when I set the parameters as follows; however, when I cancel these parameter settings and use the default parameters, the errors disappear. How can I resolve this issue?

> model = scvi$model$SCVI(adata, gene_likelihood = "nb", n_latent = 50, n_layers = 2)
Show Traceback Rerun with Debug
Error in py_call_impl(callable, call_args$unnamed, call_args$named) :
 TypeError: can't multiply sequence by non-int of type 'float' Run `reticulate::py_last_error()` for details.
> reticulate::py_last_error()
── Python Exception Message ──────────────────────────────────────────────────────────────────────────────
Traceback (most recent call last):
File "/home/data/t170403/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/model/_scvi.py", line 158, in __init__     self.module = self._module_cls(
File "/home/data/t170403/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/module/_vae.py", line 175, in __init__     self.z_encoder = Encoder(
File "/home/data/t170403/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/nn/_base_components.py", line 239, in __init__     self.encoder = FCLayers(
File "/home/data/t170403/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/nn/_base_components.py", line 67, in __init__     layers_dim = [n_in] + (n_layers - 1) * [n_hidden] + [n_out]
TypeError: can't multiply sequence by non-int of type 'float'
 ── R Traceback ────────────────────────────────────────────────────────── …

**@canergen:** This look to me like n_layers=2 is interpreted as a float value. Can you remove the optional argument? To cast a value as an integer in R my understanding is that you need to explicitly call: as.integer(2)

**@Ares1314:** > This look to me like n_layers=2 is interpreted as a float value. Can you remove the optional argument? To cast a value as an integer in R my understanding is that you need to explicitly call: as.integer(2)

Yes, that's correct. I made the modifications according to the method you described, and it is now running successfully with the error resolved! I am very grateful for your response!

## #2610: Transfer veloVI to external
**Issue:** #2610 | **Last activity:** 2024-06-21T16:09:37Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-11 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2610

For users transferring from the original [`velovi`](https://github.com/YosefLab/velovi) package, the public API has been kept identical in the following locations:
- `velovi.VELOVI` -> `scvi.external.VELOVI`
- `velovi.VELOVAE` -> `scvi.external.velovi.VELOVAE`
- `velovi.get_permutation_scores` -> `scvi.external.velovi.get_permutation_scores`
- `velovi.preprocess_data` -> `scvi.external.velovi.preprocess_data`

This will be available starting with scvi-tools v1.2.0.

## #2601: Add feature to generate coordinates for `synthetic_iid`
**Issue:** #2601 | **Last activity:** 2024-06-21T16:09:37Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-03-06 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2601

**@martinkim0:** Addressed via #2603

## #2573: Release scvi-tools 1.1.2
**Issue:** #2573 | **Last activity:** 2024-06-21T16:09:34Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-27 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2573

-   [x] Bump version in `pyproject.toml` #2538
-   [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules #2539
-   [x] ~Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch~
-   [x] ~After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image~
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged https://github.com/scverse/scvi-tutorials/releases/tag/1.1.2
-   [x] ~Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed~ no tutorial changes
-   [x] Create a new GitHub release targeting the release branch with the same body as the previous release https://github.com/scverse/scvi-tools/releases/tag/1.1.2
-   [x] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/) https://pypi.org/project/scvi-tools/1.1.2/
-   [x] Build new Docker images with the `stable` and semantic versioning tags https://github.com/YosefLab/scvi-tools-docker/actions/runs/8115195278
-   [x] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly https://github.com/conda-forge/scvi-tools-feedstock/pull/42
-   [x] ~(Optional) Post threads on Di …

## #2430: Replace `scvi.nn._utils.one_hot` in favor of the PyTorch version
**Issue:** #2430 | **Last activity:** 2024-06-21T16:09:33Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 6 | **Created:** 2024-01-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2430

No deprecation as it is part of the internal API

**@erleholgersen:** Hi @martinkim0! I took a look at this (hoping to start contributing here!) and I noticed there is a difference in behaviour between these two functions when the input has more than one column.

For example, consider the following input tensor:
```
x = tensor([[2, 1],
        [1, 2],
        [0, 2]])
```
The PyTorch version `one_hot` will one-hot encode each element of this tensor, resulting in a 3 x 2 x 3 tensor as output:
```
import torch.nn.functional as F
y_torch = F.one_hot(x, 3)
```
returns
```
tensor([[[1, 0, 0],
         [0, 1, 0]],

        [[0, 1, 0],
         [0, 0, 1]],

        [[0, 1, 0],
         [1, 0, 0]]])
```
The scvi-tools version of `one_hot` will jointly one-hot encode each row and return a 3 x 3 tensor as output. If a row has two different ele …

**@martinkim0:** @erleholgersen Thanks for taking a look at this! This is insightful - I didn't realize that the behaviors between our implementation and the torch one were different in this way.

To confirm what you mentioned, I took a skim of instances of `scvi.nn.one_hot` in our codebase, and it looks like we always apply it to categorical tensors of shape `(n,)` or `(n, 1)`. If we want to replace these instances with the torch version, I think the most straightforward way then is to call `flatten` or `squeeze` so that the input is always of shape `(n,)` and the output is of shape `(n, n_categories)`.

Also I misspoke - I didn't realize this was in our public API, so there has to be a deprecation. It also looks like several [repos](https://github.com/search?q=from+scvi.nn+import+one_hot&type=code) …

**@erleholgersen:** Oh great, that makes sense! And yes, I'd love to take a stab at this – will aim to have a PR by the end of the week.

**@erleholgersen:** Hi @martinkim0! I now have a local branch for this. Would you be able to give me write access to the repository so I can open a PR? Thank you!

**@martinkim0:** Hi, are you working on a clone of the main repository or off a fork? If the former, I'd recommend doing the latter, and then you should be able to open a PR without write access. We typically don't give write permissions to contributors.

**@erleholgersen:** Oh sorry, my bad! Will move to a fork.

## #2568: Deprecate `scvi.train.SaveBestState` and `save_best` argument
**Issue:** #2568 | **Last activity:** 2024-06-21T16:09:31Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-27 | **URL:** https://github.com/scverse/scvi-tools/issues/2568

## #2840: Discussion thread: New DestVI model that supports Visium HD (single-cell spatial transcriptomics) data - Timeline, releases and alternatives
**Issue:** #2840 | **Last activity:** 2024-06-17T17:38:17Z
**State:** closed | **Author:** @Rafael-Silva-Oliveira | **Comments:** 2 | **Created:** 2024-06-17 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2840

Hey everyone!

In this thread https://github.com/scverse/scvi-tools/issues/2830 with @canergen it was mentioned a release of a new DestVI model that would be compatible with single-cell spatial data (such as Visium HD that has 2 micron bins/spots, resulting in well over 650k bins/observations). The current model seems to not be able to capture this sparse data and I don't think it has been optimized for this much data either (I tried training 15 epochs with GPU and it took 2 hours with the 8 micron resolution - 580k bins/"spots").

I've been testing my own implementations on "deconvolution" using annotated scRNA datasets and the new HD data (10X Visium datasets) doing:
- Extracting top cell markers from the reference scRNA for each cell type, and identify these same markers on the sc-ST data, take the average of them and then associate the cell type for that given bin with the highest average of log norms. This does capture the patterns, but it doesn't seem to be the best optimal way to go about this. I've also tried adjusting the lognorms by the spatial connectivities so it captures some spatial information in the mix, and this increased the "intensity" of the bins (bins that are closer together, will have their adjusted log norms uplifted by the spatial connectivities which consider neighbor bins)
- I've tried using LGBM models and using once again cell markers extraction methods as a method of dimensionality reduction. This way I go from 15k genes + to around 400 gen …

**@canergen:** Hi, DestVI also after enhancements is still an expensive algorithm (for each spot it has to decode to each cell-type leading to a high compute time). Increasing batch size also has it's limitations specifically in DestVI.
TACCO (https://www.nature.com/articles/s41587-023-01657-3) is the most scalable deconvolution algorithm to my knowledge and it might be a good starting point. I think identifyinf marker genes is a justified approach though. Also the Visium HD preprint uses publication and it might be a good starting point to do the analysis (https://www.biorxiv.org/content/10.1101/2024.06.04.597233v1).
Timelines are somewhat hard to predict. We will post it on X/biorxiv.

**@Rafael-Silva-Oliveira:** > Hi, DestVI also after enhancements is still an expensive algorithm (for each spot it has to decode to each cell-type leading to a high compute time). Increasing batch size also has it's limitations specifically in DestVI. TACCO (https://www.nature.com/articles/s41587-023-01657-3) is the most scalable deconvolution algorithm to my knowledge and it might be a good starting point. I think identifyinf marker genes is a justified approach though. Also the Visium HD preprint uses publication and it might be a good starting point to do the analysis (https://www.biorxiv.org/content/10.1101/2024.06.04.597233v1). Timelines are somewhat hard to predict. We will post it on X/biorxiv.

Thank you for the reply! I've read their preprint paper, but they use very little amount of samples and they do a …

## #2838: Question about the output of scVI and scANVI
**Issue:** #2838 | **Last activity:** 2024-06-13T22:56:39Z
**State:** closed | **Author:** @ngvananh2508 | **Comments:** 2 | **Created:** 2024-06-11 | **URL:** https://github.com/scverse/scvi-tools/issues/2838

Hi,
Thank you for your wonderful libraries.
I have questions related to the output of scVI or scANVI. After doing integration, should I get model_scanvi.get_latent_represention() or model_scanvi.get_normalized_expression() as a new X matrix to do downstream analysis such as DGE or GSEA? When I plotted the UMAP of get_normalized_expression() method, the result is not really integrated in the right way.
![2810431ba209a65aa1258db09a9689f5dee7b0b0](https://github.com/scverse/scvi-tools/assets/130348585/48772dbf-4ba4-4b35-b103-18f992fc3b44)
The output matrix of get_latent_representation() has negative values. If we should take this matrix as X  matrix of annotated data, how can we avoid these negative values (by setting some parameters of scANVI or scVI)
Thank you so much for helping me!
(I saw the discourse forum and it did not work for a long time. I am sorry if I make the questions in the wrong position.)

**@canergen:** Hi. This is a question that should go into our discourse forum, so I'm closing here (sorry if we were lacking there with a response). You want to store model_scanvi.get_latent_represention() as an obsm (similar to PCA) to perform clustering and UMAP (our tutorials have extensive examples). I would recommend against performing GSEA/DE on the normalized expression but rather only use it for display purposes. Those values have different structure (dense and this can lead to DE results of genes that are actually not expressed). Within scvi-tools, we have our own DE function that makes use of the generative part of the model: https://docs.scvi-tools.org/en/1.1.2/user_guide/background/differential_expression.html

**@ngvananh2508:** Thank you very much for your response.

## #2627: TotalVI unexpected behaviour in differential expression function
**Issue:** #2627 | **Last activity:** 2024-06-13T18:01:40Z
**State:** closed | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-03-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2627

If defining protein_names_uns_key the DE function fails. This is unexpected behaviour.

```
def test_totalvi_de_error(save_path):
    adata = synthetic_iid()
    TOTALVI.setup_anndata(
        adata,
        batch_key="batch",
        protein_expression_obsm_key="protein_expression",
    )
    model = TOTALVI(adata)
    model.train(1, train_size=0.5)
    model.differential_expression(groupby="labels", group1="label_1")

    adata = synthetic_iid()
    TOTALVI.setup_anndata(
        adata,
        batch_key="batch",
        protein_expression_obsm_key="protein_expression",
        protein_names_uns_key="protein_names",
    )
    model = TOTALVI(adata)
    model.train(1, train_size=0.5)
    model.differential_expression(groupby="labels", group1="label_1")
```

ValueError("cannot reindex on an axis with duplicate labels")

## #2800: Issues installing recommended packages
**Issue:** #2800 | **Last activity:** 2024-06-13T18:00:50Z
**State:** closed | **Author:** @bykovam | **Comments:** 4 | **Created:** 2024-05-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2800

<!-- Describe the bug -->

I'm trying to follow installation requirements and recommendations for scvi-tools, and I'm installing packages within Anaconda Prompt on a Windows system. The readout as as follows when trying to run "conda install jax jaxlib -c conda-forge"

(Scvi_Tools_V_05_15_2024) C:\Users\BYKOVAM>conda install jax jaxlib -c conda-forge
Collecting package metadata (current_repodata.json): done
Solving environment: unsuccessful initial attempt using frozen solve. Retrying with flexible solve.
Collecting package metadata (repodata.json): done
Solving environment: unsuccessful initial attempt using frozen solve. Retrying with flexible solve.

PackagesNotFoundError: The following packages are not available from current channels:

  - jaxlib

Current channels:

  - https://conda.anaconda.org/conda-forge/win-64
  - https://conda.anaconda.org/conda-forge/noarch
  - https://repo.anaconda.com/pkgs/main/win-64
  - https://repo.anaconda.com/pkgs/main/noarch
  - https://repo.anaconda.com/pkgs/r/win-64
  - https://repo.anaconda.com/pkgs/r/noarch
  - https://repo.anaconda.com/pkgs/msys2/win-64
  - https://repo.anaconda.com/pkgs/msys2/noarch
  - https://conda.anaconda.org/bioconda/win-64
  - https://conda.anaconda.org/bioconda/noarch

In addition, running "conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia" produces

Collecting package metadata (current_repodata.json): done
Solving environment: unsuccessful initial …

**@martinkim0:** Hi, I've generally had more success these days relying on pip for installing PyTorch and JAX. I think the following should work on a Windows machine (if you don't intend on using an Nvidia GPU):
```bash
pip install -U "jax[cpu]"
pip install -U torchvision torchaudio torchvision
```
If you're attempting to use a GPU, [JAX](https://jax.readthedocs.io/en/latest/installation.html#supported-platforms) does not have a stable build currently while for PyTorch, the command would be:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# or depending on your cuda version
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**@bykovam:** Thanks! I'll test it out later and report back on the results.

**@bykovam:** Unrelated, but I love the tracksuit Shiba Inu profile pic

**@canergen:** Closed due to inactivity.

## #2806: cannot import name 'MRVI' from 'scvi.external'
**Issue:** #2806 | **Last activity:** 2024-06-13T18:00:22Z
**State:** closed | **Author:** @zy-fang | **Comments:** 2 | **Created:** 2024-05-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2806

Hi,

I am unable to import the name 'MRVI' from 'scvi.external'. I am currently using scvi version 1.1.2. I found that the mrVI tutorial (https://docs.scvi-tools.org/en/latest/tutorials/notebooks/scrna/MrVI_tutorial.html) uses scvi version 1.1.3. However, I cannot install version 1.1.3 as the highest available version is 1.1.2.

zhaoyu

**@martinkim0:** Hi, thank you for your interest in using `MRVI`. The model is set to be released with v1.2 (the tutorial shows `1.1.3` because the `main` branch is set to that version), so the only way to install it currently is from the `main` branch with the following command:
```
pip install "scvi-tools @ git+https://github.com/scverse/scvi-tools"
```
Sorry about that! We're still applying some changes to the code prior to a stable release.

**@zy-fang:** Thank you for your reply. It works for me.

## #2820: Error computing posterior predictive check `calibration_error`
**Issue:** #2820 | **Last activity:** 2024-06-13T17:58:26Z
**State:** closed | **Author:** @jpintar | **Comments:** 1 | **Created:** 2024-06-03 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2820

Using `scvi.criticism`, I can successfully perform all available posterior predictive checks on my scANVI model (`coefficient_of_variation`, `zero_fraction`, `differential_expression`) except for `calibration_error`.

When I try
```python
from scvi.criticism import PosteriorPredictiveCheck
ppc = PosteriorPredictiveCheck(
    adata,
    models_dict={'scANVI': scanvi_model},
    count_layer_key='raw',
    n_samples=10,
)
ppc.calibration_error()
```
I get the following error:
```pytb
AttributeError                            Traceback (most recent call last)
Cell In[90], line 1
----> 1 ppc.calibration_error()

File [/<envpath>/lib/python3.10/site-packages/scvi/criticism/_ppc.py:240](http://localhost:9998/<envpath>/python3.10/site-packages/scvi/criticism/_ppc.py#line=239), in PosteriorPredictiveCheck.calibration_error(self, confidence_intervals)
    238 end = interval[1]
    239 true_width = ps[end] - ps[start]
--> 240 greater_than = (quants[DATA_VAR_RAW] >= quants.model1.isel(quantile=start)).data
    241 less_than = (quants[DATA_VAR_RAW] <= quants.model1.isel(quantile=end)).data
    242 # Logical and

File [/<envpath>/lib/python3.10/site-packages/xarray/core/common.py:286](http://localhost:9998/<envpath>/lib/python3.10/site-packages/xarray/core/common.py#line=285), in AttrAccessMixin.__getattr__(self, name)
    284         with suppress(KeyError):
    285             return source[name]
--> 286 raise AttributeError(
    287     f"{type(self).__name …

**@canergen:** This function is currently not implemented. It exists in the code base but was never used. We are currently reworking the criticism module and will likely remove this metric in the future package.

## #2839: Specifying cell types in the new MRVI tool
**Issue:** #2839 | **Last activity:** 2024-06-13T17:46:05Z
**State:** closed | **Author:** @jindalk | **Comments:** 1 | **Created:** 2024-06-13 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2839

<!-- Describe the bug -->

I'm trying to use the new MRVI model, from ```scvi.external```, how do I bias the model with existing cell type annotations? I've posted my code below, but wasn't sure if this was correct

<!-- To reproduce -->

```python
sc.pp.highly_variable_genes(adata, n_top_genes=10000,
                            flavor="seurat", batch_key="batch",
                            inplace=True, subset=True)

sample_key = "sampleID_study"  # target covariate
batch_key= "batch"  # nuisance variable identifier
MRVI.setup_anndata(adata, sample_key=sample_key, batch_key=batch_key, labels_key="celltype")

model = MRVI(adata, u_prior_mixture_k=13)
model.train(max_epochs=400)
```

**@canergen:** Hi, thanks for trying out MrVI. This is not a bug (so closing here). Please restrict the label to real bugs (unexpected behaviour). For user questions, we prefer our scverse discourse forum. To the original question: yes, and you don't have to worry u_prior_mixture_k. It automatically sets it to the number of celltypes in your study (so `model = MRVI(adata)` is safe.

## #2833: Exception has occurred: ImportError cannot import name 'REGISTRY_KEYS' from 'scvi'
**Issue:** #2833 | **Last activity:** 2024-06-12T18:36:55Z
**State:** closed | **Author:** @Rafael-Silva-Oliveira | **Comments:** 3 | **Created:** 2024-06-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2833

<!-- Describe the bug -->

Whenever I try to import scvi in a remote explorer (in a server) I get the error below; Happens with both venv and conda install via pip

<!-- To reproduce -->
Nothing to reproduce, simply importing it causes this error

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Exception has occurred: ImportError cannot import name 'REGISTRY_KEYS' from 'scvi'
```

#### Versions:

<!-- Output of scvi.__version__ -->

> latest version of scvi and scvi-tools (already reinstalled it)

<!-- Relevant screenshots -->

**@martinkim0:** Hi, could you try clearing the conda/pip cache (``conda clean -ayf`` and ``pip cache purge``) and reinstalling again? If this doesn't work, I can help further debug this.

**@Rafael-Silva-Oliveira:** > Hi, could you try clearing the conda/pip cache (`conda clean -ayf` and `pip cache purge`) and reinstalling again? If this doesn't work, I can help further debug this.

Hey, I got it fixed already, I think I had both scvi and scvi-tools installed (scvi is no longer being used from what I was reading) and I just crated a brand new venv and reinstalled everything (without scvi) and it's working now, thank you

**@martinkim0:** Great to hear! I'm going to go ahead and close the issue then.

## #2814: ImportError: cannot import name 'packaging' from 'pkg_resources' for Model Tuning using Ray
**Issue:** #2814 | **Last activity:** 2024-06-12T15:52:38Z
**State:** closed | **Author:** @shahrozeabbas | **Comments:** 4 | **Created:** 2024-05-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2814

Hello,

I am trying to use the `autotune` module for a parameter search but am getting an error that `packaging` cannot be imported. I'm using a `conda` environment and `pkg_resources` is installed. I used`pip` to install `scvi` with the autotune dependencies. Below is a copy of my script and the error message.
```
adata = scanpy.read_h5ad('anndata_object.h5ad')

scvi.data.poisson_gene_selection(adata, accelerator='gpu', n_top_genes=2000, subset=True)

adata.layers['counts'] = adata.X.copy()

model = scvi.model.SCVI
model.setup_anndata(adata, layer='counts')

tuner = autotune.ModelTuner(model)

search_space = {
    "n_latent": ray.tune.choice([10, 20, 30]),
    "n_layers": ray.tune.choice([1, 2]),
    "lr": ray.tune.loguniform(1e-4, 1e-2),
    "gene_likelihood": ray.tune.choice(['zinb', 'nb']),
    "lr_factor": ray.tune.loguniform(0.01, 0.05, 0.1)
}

ray.init(log_to_driver=False)

results = tuner.fit(
    adata,
    metric="validation_loss",
    search_space=search_space,
    num_samples=10,
    max_epochs=300,
    resources={"cpu": 2, "gpu": 1},
)
```

When initializing `ray`:

```
/data/abbass2/miniforge3/envs/scvi-tune/lib/python3.9/subprocess.py:1770: RuntimeWarning: os.fork() was called. os.fork() is incompatible with multithreaded code, and JAX is multithreaded, so this will likely lead to a deadlock.
  self.pid = _posixsubprocess.fork_exec(
2024-05-29 10:45:09,740 ERROR services.py:1329 -- Failed to start the dashboard
2024-05 …

**@martinkim0:** Hi, could you try downgrading `setuptools` from `70.0.0` to `69.5.1` (following the pointers [here](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/15903)):
```
pip install -U setuptools==69.5.1
```

**@shahrozeabbas:** Success! Thank you

**@shahrozeabbas:** `autotune` should work with other models like `poissonvi` right? Just to confirm.

**@martinkim0:** Yes (sorry for the delay)!

## #1634: gimVI gene imputation error
**Issue:** #1634 | **Last activity:** 2024-06-06T10:42:25Z
**State:** closed | **Author:** @giovp | **Comments:** 4 | **Created:** 2022-08-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1634

<!-- Describe the bug -->
the `get_imputed_values` method from gimvi not working?

<!-- To reproduce -->
```python
from scvi.external import GIMVI

GIMVI.setup_anndata(adata_sp_train, layer="counts")
GIMVI.setup_anndata(adata_sc, layer="counts")
model = GIMVI(adata_sc, adata_sp_train)
model.train(10, batch_size=256)
imputed = model.get_imputed_values(normalized=True, batch_size=256)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->
```pytb
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Input In [11], in <cell line: 1>()
----> 1 imputed = model.get_imputed_values(normalized=True, batch_size=256)

File ~/miniconda3/envs/moscot/lib/python3.9/site-packages/torch/autograd/grad_mode.py:27, in _DecoratorContextManager.__call__.<locals>.decorate_context(*args, **kwargs)
     24 @functools.wraps(func)
     25 def decorate_context(*args, **kwargs):
     26     with self.clone():
---> 27         return func(*args, **kwargs)

File ~/miniconda3/envs/moscot/lib/python3.9/site-packages/scvi/external/gimvi/_model.py:341, in GIMVI.get_imputed_values(self, adatas, deterministic, normalized, decode_mode, batch_size)
    333 (
    334     sample_batch,
    335     batch_index,
    336     label,
    337     *_,
    338 ) = _unpack_tensors(tensors)
    339 if normalized:
    340     imputed_value.append(
--> 341 …

**@adamgayoso:** Hmmm, the colab tutorial we have seems to work just fine, can you share on colab?

**@martinkim0:** Closing due to inactivity

**@HelloWorldLTY:** Hi, I think it is still a bug. Sometime if the input x only has one observation, we will receive such error. I think this bug can be addressed by changeing the batch size in the inference process, but I do not know why batch norm are called in the inference proecss, since the model is set as eval() mode.

**@hannshu:** Hi, this issue arises when the input data (from one of sc, st, or both) has the characteristic where 1 == (input_cell/spot_count % batch_size). In the functions `get_latent_representation` or `get_imputed_values`, the first step involves running the `_unpack_tensors` function, where a dimension of size 1 in the dimension 0 of the input tensor will be removed. Normally, this is a standard operation to refine the input shape. However, when there is only one cell or spot in the batch, the squeeze() operator eliminates the 0-dimension, which represents the batch count. Consequently, the BatchNorm function in PyTorch raises an error due to the incorrect input shape.

For users, this can be easily resolved by adjusting the batch size so that 1 != (input_cell/spot_count % batch_size).

For de …

## #2813: Error saving MrVI model
**Issue:** #2813 | **Last activity:** 2024-06-05T17:00:52Z
**State:** closed | **Author:** @lior-ness | **Comments:** 2 | **Created:** 2024-05-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2813

<!-- Describe the bug -->

Training and inferring an MrVI model from `scvi.external` works, but saving it raises a TypeError. This happens whether trained using GPU or CPU, but does NOT happen with the legacy package from https://github.com/YosefLab/mrvi.


<!-- To reproduce -->

```python
# Savable model
from mrvi import MrVI   # https://github.com/YosefLab/mrvi

# Unsavable model (imported as MrVI to match legacy name)
from scvi.external import MRVI as MrVI

adata = ad.read_h5ad('/home/jovyan/adata.h5ad')
MrVI.setup_anndata(adata, sample_key='sample_id')
model = MrVI(adata)
model.train(max_epochs=400, accelerator='gpu', batch_size=1024)

# This will raise Exception if imported from scvi.external but not from legacy repo
model.save('/home/jovyan/mrvi_model3')

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb

Traceback (most recent call last)

----> 1 model.save('/home/jovyan/mrvi_model3')

File ~/git/scvi-tools/src/scvi/model/base/_base_model.py:632, in BaseModelClass.save(self, dir_path, prefix, overwrite, save_anndata, save_kwargs, legacy_mudata_format, **anndata_write_kwargs)
    629 # only save the public attributes with _ at the very end
    630 user_attributes = {a[0]: a[1] for a in user_attributes if a[0][-1] == "_"}
--> 632 torch.save(
    633     {
    634         SAVE_KEYS.MODEL_STATE_DICT_KEY: model_state_dict,
    635         SAVE_KEYS.VAR_NAMES_KEY: var_names,
    636 …

**@jindalk:** I'm running into the same issue, a quick workaround is to use the `dill` module to save and load trained models:

```
import dill

model = MRVI(adata)
model.train(max_epochs=400)

#write
with open("abc.pkl","wb")as f:
    dill.dump(model, f)

#read
with open("abc.pkl", "rb") as f:
    model2 = dill.load(f)
```

**@martinkim0:** Hi, thanks for reporting this error. I've looked into this and added a fix here: #2828. Please install from `main` again!

## #2609: AttributeError: module 'numpy' has no attribute 'str
**Issue:** #2609 | **Last activity:** 2024-05-31T19:54:43Z
**State:** closed | **Author:** @sainsachiko | **Comments:** 2 | **Created:** 2024-03-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2609

<!-- Describe the bug -->
Get `AttributeError: module 'numpy' has no attribute 'str'` when trying to load pbmc data

<!-- To reproduce -->

```python
adata = scvi.data.pbmc_dataset()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
INFO     File data/gene_info_pbmc.csv already downloaded
INFO     File data/pbmc_metadata.pickle already downloaded
INFO     File data/pbmc8k/filtered_gene_bc_matrices.tar.gz already downloaded
INFO     Extracting tar file
INFO     Removing extracted data at data/pbmc8k/filtered_gene_bc_matrices
INFO     File data/pbmc4k/filtered_gene_bc_matrices.tar.gz already downloaded
INFO     Extracting tar file
INFO     Removing extracted data at data/pbmc4k/filtered_gene_bc_matrices
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
[<ipython-input-9-2b688d4bab92>](https://localhost:8080/#) in <cell line: 1>()
      1 if dataset_name == "PBM …

**@martinkim0:** Hi, could you double check what scvi-tools version you have installed and let me know? Our latest release is 1.1.2. Thanks!

**@martinkim0:** Closing due to inactivity

## #2729: SemiSupervisedDataSplitter not properly separating unlabelled cells into train/val/test
**Issue:** #2729 | **Last activity:** 2024-05-29T17:43:52Z
**State:** closed | **Author:** @ethanweinberger | **Comments:** 1 | **Created:** 2024-04-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2729

<!-- Describe the bug -->

When splitting datasets into train/validation/test sets, I would expect that the union of train/validation/test samples should be equal to the full dataset. Moreover, data points should only be present once in one of train/validation/test. However, for splits produced by the `SemiSupervisedDataSplitter` class with shuffling turned on this is not the case, and some unlabeled points are excluded from all splits (i.e., they belong to none of train/val/test) while others are repeated multiple times.

I believe the issue is that sampling is performed with replacement [here](https://github.com/scverse/scvi-tools/blob/main/src/scvi/dataloaders/_data_splitting.py#L300) when shuffling the unlabelled points, causing some unlabelled points to be repeated while others are never sampled. On the other hand, for [labelled points](https://github.com/scverse/scvi-tools/blob/main/src/scvi/dataloaders/_data_splitting.py#L278) sampling is properly done without replacement.

I've included a colab notebook [here](https://colab.research.google.com/drive/1HVkdNtmiZ8zoj_DwXVT9kFBBrsYPoECW?usp=sharing) reproducing the issue. Happy to take this on myself since the fix should be straightforward.

#### Versions:

scvi-tools 1.1.2

**@martinkim0:** Hmm thanks for pointing this out, this is an unfortunate issue. It's been on our roadmap to refactor the data splitter classes, so I can take a look at this + fix it.

## #2815: Issues in  Load Dataset with SeuratData and convert to adata
**Issue:** #2815 | **Last activity:** 2024-05-29T16:44:28Z
**State:** closed | **Author:** @GischD | **Comments:** 2 | **Created:** 2024-05-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2815

<!--  -->
Dear scvi-tools team,
Thank you for all your hard work to keep the tool working well.
I have a script in R using the reticulate.
The script works for one Seurat object but not for another.
I try to inspect both objects, but I don't find any differences.

I appreciate your thoughts about what is causing the issue.

Best Regards,
Debora



<!-- To reproduce -->

```R

library(Seurat)
library(Signac)
library(SeuratDisk)
library(SeuratData)
library(Gviz)
library(GenomicRanges)
library(rtracklayer)
library(dplyr)
library(reticulate)
library(sceasy)
reticulate::virtualenv_list()
## Change the Path
Sys.setenv(RETICULATE_PYTHON="/home/.virtualenvs/r-reticulate_3p10/bin/python")
## Use the virtualenv
reticulate::use_virtualenv("r-reticulate_3p10")

  sc <- import("scanpy", convert = FALSE)
  scvi <- import("scvi", convert = FALSE) #chech if the sc
  i <- "S16.RDA"
  name <- "S16"
  load(i)
  DefaultAssay(obj) <- "RNA"
  adata <- convertFormat(obj, from="seurat", to="anndata", main_layer="counts",drop_single_values=FALSE,outFile = paste0(name,".h5ad"))

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
── Python Exception Message ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Traceback (most recent call last):
  File "/home/.virtualenvs/r-reticulate_3p10/lib/python …

**@canergen:** Hi, thanks for using scVI-tools. This is more a question to sceasy for converting Seurat to AnnData. So I’m closing here.
Your issue is: `Error raised while writing key 'v1_barcode' of <class 'h5py._hl.group.Group'> to /obs`. I assume there are Boolean or None values in this column of adata.obs. You can either change the values in this column to string or delete this column.

**@GischD:** Thanks for the quick answer. 👍
Works nicely!

## #2803: Support the latest version of torchmetrics
**Issue:** #2803 | **Last activity:** 2024-05-24T19:41:40Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-05-15 | **URL:** https://github.com/scverse/scvi-tools/issues/2803

See #2783

## #2549: Transfer mrVI to external
**Issue:** #2549 | **Last activity:** 2024-05-20T17:36:10Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2549

No milestone yet - will assess once we get started.

## #2804: different hidden unit in each layer
**Issue:** #2804 | **Last activity:** 2024-05-17T15:24:17Z
**State:** closed | **Author:** @verao-amy | **Comments:** 1 | **Created:** 2024-05-17 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2804

Is it possible to use different number of hidden units in different layers? For example, 128 hidden unites in layer1, 64 hidden units in layer2 and 30 latent variables.
How should we code that?

**@martinkim0:** Hi, for number of latent variables, you may pass in `n_latent=30` to the constructor of most models. For specifying different number of hidden units in each hidden layer, this is currently not possible. We've decided not to support this for the sake of simplicity of the user API. If you'd like to implement this for your purposes, it should be straightforward to modify [`FCLayers`](https://github.com/scverse/scvi-tools/blob/main/src/scvi/nn/_base_components.py#L15) using an [editable install](https://docs.scvi-tools.org/en/latest/developer/code.html) of scvi-tools.

## #2782: flax: Trying to access a property that is accessing a non-existent attribute. - JaxBaseModuleClass
**Issue:** #2782 | **Last activity:** 2024-05-16T20:43:34Z
**State:** closed | **Author:** @Zethson | **Comments:** 2 | **Created:** 2024-05-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2782

<!-- Describe the bug -->

```
self = <flax.linen.module.create_descriptor_wrapper.<locals>._DescriptorWrapper object at 0x7f896ff65410>
args = (JaxSCGENVAE(
    # attributes
    n_input = 100
    n_hidden = 800
    n_latent = 100
    n_layers = 2
    dropout_ra...e_layer_norm = 'none'
    kl_weight = 5e-05
    training = True
), <class 'pertpy.tools._scgen._scgenvae.JaxSCGENVAE'>)
kwargs = {}

    def __get__(self, *args, **kwargs):
      # here we will catch internal AttributeError and re-raise it as a
      # more informative and correct error message.
      try:
>       return self.wrapped.__get__(*args, **kwargs)

../../miniconda3/envs/pertpy/lib/python3.11/site-packages/flax/linen/module.py:927:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = JaxSCGENVAE(
    # attributes
    n_input = 100
    n_hidden = 800
    n_latent = 100
    n_layers = 2
    dropout_rat...ribution = 'normal'
    use_batch_norm = 'both'
    use_layer_norm = 'none'
    kl_weight = 5e-05
    training = True
)

    @property
    def device(self):
>       return self.seed_rng.device()
E       AttributeError: 'jaxlib.xla_extension.ArrayImpl' object has no attribute 'device'

../../miniconda3/envs/pertpy/lib/python3.11/site-packages/scvi/module/base/_base_module.py:584: AttributeError

The above exception was th …

**@martinkim0:** Looks like this is being caused by the newest JAX 0.4.27 release. Looking into this rn

**@martinkim0:** Closed via #2787

## #2792: The scrna_raw_counts_properties method has an error in the calculation method of the raw_normalized_mean2 field, causing the raw_normalized_mean2 indicator to be invalid.
**Issue:** #2792 | **Last activity:** 2024-05-16T01:58:50Z
**State:** closed | **Author:** @raozuming | **Comments:** 4 | **Created:** 2024-05-13 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2792

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

np.asarray(data.sum(axis=1)).ravel().reshape(-1, 1) has 0 elements in the matrix, causing the raw_normalized_mean2 field calculation to fail.
**Describe the solution you'd like**
A clear and concise description of what you want to happen.

raw_normalized_mean2 is calculated correctly

**@canergen:** Hi, thank you for reporting it. First question: I assume correctly that you don’t get incorrect values but you get a ValueError as you have a shape mismatch. This is happening during construction of the pandas.DataFrame. Can you copy the exact error message? It should happen for raw_normalized_mean but also the two other means in the function (or are your size factors zero?)

**@raozuming:** RuntimeWarning: divide by zero encountered in divide
  scaling_factor = 1 / np.asarray(data.sum(axis=1)).ravel().reshape(-1, 1)


I think np.divide(np.asarray(data.sum(axis=1)).ravel().reshape(-1, 1), 1) should be used to replace 1 / np.asarray(data.sum(axis=1 )).ravel().reshape(-1, 1) to avoid this error

**@canergen:** This means that your data contains cells without any count. Is it meaningful for your model to input cells without counts (I assume it’s due to your highly variable gene selection)? I would highly recommend to filter to min_counts before training the model as otherwise training might be unstable.
@martinkim0 We could add a check and print a warning when setting up a model if cells contain less than let’s say 30 counts.

**@raozuming:** Thanks

## #2755: Can we have a scVI with reconstruction distirbution as normal distribution?
**Issue:** #2755 | **Last activity:** 2024-05-15T22:05:57Z
**State:** closed | **Author:** @HelloWorldLTY | **Comments:** 4 | **Created:** 2024-04-27 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2755

Hi, I am interested in the implementation of scVI with normal distirbution as reconstruction distribution. I think this setting is meaningful for the dataset that we can only retrieve the normalized results. If I directly replace the reonstruction distribution with normal distribution, there will be an error. Thanks a lot.

**@martinkim0:** We don't plan on implementing this for now as we haven't tested or benchmarked it on our end. Would be happy to take a PR with an implementation if you're willing to contribute, though!

**@HelloWorldLTY:** Thanks. I will consider implementing it. I think it should be similar to VeloVI.

**@canergen:** Hi, you might want to check e.g. scGEN from Theis lab, which uses MSE as the default and only loss. I don't want to include a model that starts with some transformed data. The issue in my opinion is that we can't cover all types of data preprocessing and ensure that it works (scaling, log1p, Poisson residual, and others).

**@martinkim0:** Closed via #2780

## #2781: Scvi in R doesn't update to scvi-tools even after uninstalling and reinstalling (I think :)
**Issue:** #2781 | **Last activity:** 2024-05-08T15:48:37Z
**State:** closed | **Author:** @Sun-storm | **Comments:** 3 | **Created:** 2024-05-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2781

Hi!

<!-- Describe the bug -->

I'm trying to use SCVI for the first time, following the "ATAC-seq analysis in R", and first installed scvi by typing `-m pip install scvi `. When I tried to use it on R I got this deprecation message:

`/x/y/z/python3.12/site-packages/scvi/__init__.py:31: DeprecationWarning: scvi is deprecated, please uninstall scvi via `pip uninstall scvi` and install the new scvi-tools package at github.com/YosefLab/scvi-tools warnings.warn(deprecation_msg, DeprecationWarning)`

I thus uninstalled scvi and installed scvi-tools. But even after running `scvi <- import("scvi-tools", convert = FALSE)` on R again, I am still left with the deprecated SCVI.

I've tried uninstalling and reinstalling scvi several times but that doesn't solve the issue. What should I do?


<!-- To reproduce -->

```
UNIX
`-m pip install scvi `

R (with Reticulate to bridge the gap with python)
scvi <- import("scvi", convert = FALSE)

UNIX
`-m pip uninstall scvi `
`-m pip install scvi-tools `

R (with Reticulate to bridge the gap with python)
scvi <- import("scvi", convert = FALSE)

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```
> scvi$model$PEAKVI$setup_anndata(adata)
Error in py_get_attr(x, name, FALSE) :
  AttributeError: module 'scvi' has no attribute 'model'
Run `reticulate::py_last_error()` for details.
```

#### Versions:

<!-- Output of scvi.__version__ -->

> '0.6.8'

<img width …

**@canergen:** Can you check that scVI is imported from the same environment in which you are uninstalling it? It would be easier to check that you can uninstall and the import fails and the reinstall.
However, PyPI might create issues in this environment and using a new environment would then be the easiest way to fix it.

**@Sun-storm:** Okay, so I tried to check the python environment R is using, which I believe should be this:

`> py_config()
python:         /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
libpython:      /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/config-3.12-darwin/libpython3.12.dylib
pythonhome:     /Library/Frameworks/Python.framework/Versions/3.12:/Library/Frameworks/Python.framework/Versions/3.12
version:        3.12.1 (v3.12.1:2305ca5144, Dec  7 2023, 17:23:39) [Clang 13.0.0 (clang-1300.0.29.30)]
numpy:          /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/numpy
numpy_version:  1.26.3
scanpy:         [NOT FOUND]

NOTE: Python version was forced by use_python() function`

And compared it to the environment I install …

**@Sun-storm:** I created a new environment with Conda, reinstalled scvi-tools and now it works. Thank you for your suggestions and help :))

## #2452: Index error when using totalVI
**Issue:** #2452 | **Last activity:** 2024-04-29T16:22:24Z
**State:** closed | **Author:** @HafsaKM | **Comments:** 4 | **Created:** 2024-01-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2452

< I am trying to analyse my CITE seq data using the tutorial on totalVI.>
I set up the mudata exactly as described.


```python
adata_sommarin_protein = adata_sommarin[:, adata_sommarin.var["Feature types"].isin(["Antibody capture", "Antibody capture 2"])].copy()
adata_sommarin_rna = adata_sommarin[:, adata_sommarin.var["Feature types"] == "Gene Expression"].copy()

# rna preprocessing
adata_sommarin_rna.layers["counts"] = adata_sommarin_rna.X.copy()
sc.pp.normalize_total(adata_sommarin_rna, target_sum = 1e4)
sc.pp.log1p(adata_sommarin_rna)
adata_sommarin_rna.obs_names_make_unique()

adata_sommarin_protein.obs_names_make_unique()

mdata = md.MuData({"rna": adata_sommarin_rna, "protein": adata_sommarin_protein})

mdata.mod['protein'].layers['counts'] = adata_sommarin_protein.X.copy()

# high var on log of counts instead of counts
sc.pp.highly_variable_genes(
    mdata.mod["rna"],
    n_top_genes=4000,
    batch_key="Sample"
)
# Place subsetted counts in a new modality
mdata.mod["rna_subset"] = mdata.mod["rna"][
    :, mdata.mod["rna"].var["highly_variable"]
].copy()

mdata.update()

scvi.model.TOTALVI.setup_mudata(
    mdata,
    rna_layer="counts",
    protein_layer=None,
    batch_key="Sample",
    modalities={
        "rna_layer": "rna_subset",
        "protein_layer": "protein",
        "batch_key": "rna_subset",
    },
)

# run model
model = scvi.model.TOTALVI(mdata, override_missing_proteins=True)
```

<!-- Put your Err …

**@HafsaKM:** Solved this by converting the protein anndata frame to a df first and then converting back to anndata. Not sure how that helped, would appreciate an explanation

**@martinkim0:** Hey! Sorry you ran into this issue. Could you let me know the code you ran in order to solve it? Thanks!

**@cb11711211:** Same issue when using TotalVI. Making the mdata could not be updated and saved. This could be resulted by the conversion of var_names for both rna and protein adata.

**@martinkim0:** @cb11711211 I think the original issue was caused because the protein modality layer contained a sparse matrix. Could you check if this is the case for your dataset?
```
print(mdata.mod["protein"].X)
```
and checking if it says something like `sparse matrix`

## #2754: Assistance Required with scvi-tools GPU Setup on Ubuntu
**Issue:** #2754 | **Last activity:** 2024-04-28T03:50:55Z
**State:** closed | **Author:** @qweasdf1354 | **Comments:** 7 | **Created:** 2024-04-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2754

<!-- Describe the bug -->

Dear scvi-tools Team,

I am currently experiencing issues with setting up scvi-tools to run on a GPU on my Ubuntu system, and I am seeking your assistance to resolve this problem.

I have successfully installed scvi-tools and am able to import the package and run models using CPU. However, I am unable to utilize the GPU capabilities, and the issue appears to be related to JAX and CUDA compatibility.

My system details are as follows:

OS: Ubuntu 22.04
Python environment: Miniforge3
CUDA versions tried: 11.8, 12.0, 12.1, 12.2
Despite trying multiple versions of CUDA, I am encountering an issue with cuSPARSE version mismatches. The error indicates that JAX requires cuSPARSE version 12200, but my setup only supports version 12002. I have been unable to find a solution through online installation guides.

Could you please advise on the recommended installation procedure for ensuring scvi-tools works with GPU acceleration on my system? Any specific versions of CUDA, cuDNN, or other dependencies that you recommend would be greatly appreciated.

Thank you for your assistance and for the excellent work on scvi-tools.

Best regards,

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

<!-- Releva …

**@qweasdf1354:** I just follow the latest installation guide page and i turn to the JAX page to install jax using the following
pip install -U "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

and
pip install "scvi-tools[tutorials]"

it could not using GPU in my computuer.

**@martinkim0:** Take this with a grain of salt since we may have different system packages, but I'm on Ubuntu 22.04.4 with Nvidia driver version 550.54.15 and CUDA 12.4, and the following commands give me a working scvi-tools GPU environment in Miniforge3 (checked today using a cold cache):
```
conda create -n scvi-env python=3.11
conda activate scvi-env

pip install -U uv
uv pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
uv pip install --upgrade torch torchvision torchaudio
uv pip install --upgrade scvi-tools
```
Note that I'm using uv here for installation, but it should be the same with pip.

Is there a particular reason that you're also installing all the tutorial dependencies? Sometimes installing these extra dependencies can …

**@martinkim0:** Also for future reference, this would be a great question to post on our [Discourse](https://discourse.scverse.org/)! We prefer to have bug reports and feature requests only on GitHub issues.

I'm going to go ahead and close this issue then, but please feel free to follow up, and I'll try to help.

**@qweasdf1354:** Thank you so much for your prompt help. I appreciate your suggestion and understand your reasoning. Initially, I chose to use "scvi-tools[tutorials]" primarily for its convenience, as it comes with Jupyter notebooks integrated, which simplifies my workflow. However, I agree with your perspective and will attempt the approach you recommended.

Thank you once again for providing such an excellent tool. I will make sure to keep you updated with any feedback or issues as I proceed.

**@qweasdf1354:** I am successfully install and train without error. However, the GPU utility is remain low about 5-8%. A dataset around 20000*2000 will take 14 minutes. I am not sure is that normal. Thanks!

**@canergen:** Both numbers are reasonable. You can increase the batch_size in train (which is safe up to 1024 cells for large datasets). This increases GPU usage. Warning: For small datasets (below 200k cells), this is not extensively tested and might reduce performance. You could also reduce the number of epochs. However, I would suggest waiting for the time it takes to train the model. ScVI is a small model that doesn't fully use a single GPU (it's due to the number of parameters). Downstream steps like clustering and annotating datasets is significantly more time-consuming in most applications.

**@qweasdf1354:** Thank you!

## #2740: 'SCVI' object has no attribute 'eval'
**Issue:** #2740 | **Last activity:** 2024-04-23T10:01:15Z
**State:** closed | **Author:** @FZ-hajji | **Comments:** 2 | **Created:** 2024-04-22 | **URL:** https://github.com/scverse/scvi-tools/issues/2740

Hello ,


I used the following code to save and load scvi model:
model.save("my_model/")
model = scvi.model.SCVI.load("my_model/", adata=adata)
model.eval()

But when I apply eval() to the model I get this error:
'SCVI' object has no attribute 'eval'

**@martinkim0:** Hi, this is because `SCVI` is not an instance of `torch.nn.Module`. For this, you would need to call `model.module.eval`. However, this is not necessary in this case as we already call `eval` in our `load` function [here](https://github.com/scverse/scvi-tools/blob/main/src/scvi/model/base/_base_model.py#L717).

**@FZ-hajji:** Thank you so much

## #2720: benign typo in kwarg
**Issue:** #2720 | **Last activity:** 2024-04-11T19:57:56Z
**State:** closed | **Author:** @ghwatson | **Comments:** 1 | **Created:** 2024-04-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2720

<!-- Describe the bug -->

typo in this line for a kwarg: https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/train/_callbacks.py#L112

note this doesn't manifest as a bug. the default behaviour for save has save_anndata set to False already.

**@martinkim0:** Thanks for pointing that out! Not sure how that made past our tests...

## #2709: Fail to accerlerate scvi analysis using gpu on mac M1
**Issue:** #2709 | **Last activity:** 2024-04-10T08:33:30Z
**State:** closed | **Author:** @xylinwc | **Comments:** 7 | **Created:** 2024-04-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2709

<!-- Describe the bug -->
As a Mac user, I have found the inconvenience of using GPU acceleration during scvi analysis... When attempting to set accelerator="gpu" in model.train() to enable GPU acceleration, I encountered the following error. I suspect this may be due to insufficient compatibility between PyTorch and Mac, which has led me to consider using TensorFlow for acceleration in scvi, as I have successfully used TensorFlow for acceleration in VeloVI.

<!-- To reproduce -->

```python
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="group")
model = scvi.model.SCVI(adata, n_layers=2, n_latent=300, gene_likelihood="nb")
model.train(accelerator="gpu")
adata.obsm["X_scVI"] = model.get_latent_representation()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
ValueError                                Traceback (most recent call last)
Cell In[7], [line 4](vscode-notebook-cell:?execution_count=7&line=4)
      [2](vscode-notebook-cell:?execution_count=7&line=2) scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="group")
      [3](vscode-notebook-cell:?execution_count=7&line=3) model = scvi.model.SCVI(adata, n_layers=2, n_latent=300, gene_likelihood="nb")
----> [4](vscode-notebook-cell:?execution_count=7&line=4) model.train(accelerator="gpu")
      [5](vscode-notebook-cell:?execution_count=7&line=5) adata.obsm["X_scVI"] = model.get_latent_representation()

File [/opt/miniconda3 …

**@canergen:** This is a problem on the MPS PyTorch side and not much we can do about it. While lgamma is implemented now (this is the most likely source as e.g. PeakVI, which uses a reconstruction loss without lgamma, worked in the past with MPS). The current lgamma implementation is in beta state and in our hands we also yield None errors.

**@xylinwc:** > This is a problem on the MPS PyTorch side and not much we can do about it. While lgamma is implemented now (this is the most likely source as e.g. PeakVI, which uses a reconstruction loss without lgamma, worked in the past with MPS). The current lgamma implementation is in beta state and in our hands we also yield None errors.

I was thinking whether it might be possible to support TensorFlow for GPU invocation... Although the speed and performance may not be as good as PyTorch, it is still significantly faster than computing with only a CPU.

**@canergen:** If you want to implement tensorflow scVI, I would point to https://github.com/scverse/simple-scvi. It will require major engineering and there's no intention from our side to develop this, especially as it is easy running code on Google Colab to get hardware acceleration with Nvidia GPUs (for larger datasets Mac hardware will also not be sufficient, it's still considerably slower compared to dedicated GPUs). I think when looking at macOS - MLX sounds like the way to go. I would be curious to see an implementation of scVI in MLX. Closing here as not planned.

**@martinkim0:** > as I have successfully used TensorFlow for acceleration in VeloVI

Could you elaborate on this please? VeloVI is written using scvi-tools and only supports PyTorch. Did you rewrite the module to use TensorFlow?

**@martinkim0:** Just to reiterate what @canergen mentioned, this is fundamentally an issue on the PyTorch side. It does look like they are working on adding better support for the Metal backend, so it's likely that we will see stable support for this in an upcoming PyTorch release. Please hold tight until then!

Alternatively, you may wish to use our experimental JAX implementation with `scvi.model.JaxSCVI` and pairing that with a [`jax-metal`](https://developer.apple.com/metal/jax/) installation. I can't comment on how stable this is vs. PyTorch, but it may be worth trying out if you'd like to take full advantage of the Metal backend.

**@xylinwc:** > > as I have successfully used TensorFlow for acceleration in VeloVI
>
> Could you elaborate on this please? VeloVI is written using scvi-tools and only supports PyTorch. Did you rewrite the module to use TensorFlow?

I apologize for the confusion. It is true that Velovi did not utilize GPU acceleration. However, I employed another velocity analysis software called UNITvelo, which successfully invoked the GPU. The code and output are as follows:
```
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.chdir("/Users/myapple/Documents/RStudio/Single_cell/myproject-1209")
import numpy as np
np.random.seed(520)
import unitvelo as utv
import tensorflow as tf
import scvelo as scv
print ("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
velo_config = utv.conf …

**@xylinwc:** > Just to reiterate what @canergen mentioned, this is fundamentally an issue on the PyTorch side. It does look like they are working on adding better support for the Metal backend, so it's likely that we will see stable support for this in an upcoming PyTorch release. Please hold tight until then!
>
> Alternatively, you may wish to use our experimental JAX implementation with `scvi.model.JaxSCVI` and pairing that with a [`jax-metal`](https://developer.apple.com/metal/jax/) installation. I can't comment on how stable this is vs. PyTorch, but it may be worth trying out if you'd like to take full advantage of the Metal backend.

By the way, I used the function scvi.model.JaxSCVI and still encountered an error：
```
XlaRuntimeError: UNKNOWN: [/var/folders/ww/75_k3cyx02j9mydt1qpsk5_r0000g …

## #2694: SCVI can no longer be imported in R studio via reticulate
**Issue:** #2694 | **Last activity:** 2024-04-07T08:06:52Z
**State:** closed | **Author:** @CCCC1800 | **Comments:** 2 | **Created:** 2024-04-06 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2694

<!-- Describe the bug -->
Hi,

I was using SCVI in R studio via reticulate (as shown in https://docs.scvi-tools.org/en/1.0.1/tutorials/notebooks/scvi_in_R.html). It didn't show bugs until recently, when I tried again, the SCVI can no longer be imported in R via reticulate. Except SCVI, other python packages I used can be imported in R as usual, so I guess this is a bug relating to SCVI itself.

Thank you
<!-- To reproduce -->

```python
##In R studio:
library(reticulate)
sc <- import('scanpy', convert = FALSE)
scvi <- import('scvi', convert = FALSE)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
Error in py_module_import(module, convert = convert) : AssertionError
Run `reticulate::py_last_error()` for details.
> reticulate::py_last_error()

── Python Exception Message ─────────────────────────────────────────────────────────────────────────────────────────────
Traceback (most recent call last):
  File "/home/ubuntu/chenlab_deeplearning/chenlab_deeplearning_V2/anaconda3/envs/SCANVI/lib/R/library/reticulate/python/rpytools/loader.py", line 119, in _find_and_load_hook
    return _run_hook(name, _hook)
  File "/home/ubuntu/chenlab_deeplearning/chenlab_deeplearning_V2/anaconda3/envs/SCANVI/lib/R/library/reticulate/python/rpytools/loader.py", line 93, in _run_hook
    module = hook()
  File "/home/ubuntu/chenlab_deeplearning/chenlab_deeplearning_V2/anaconda3/envs/SCANVI/lib/R/library/reticulate/pyt …

**@canergen:** Hi, can you confirm that you currently can't import pyro in your environment? `import pyro` is failing above. The issue is that your pyro version is old and requires pytorch<2.0. This is likely not the case. You will need to update pyro. How have you set up the environment?

**@CCCC1800:** Thank you for pointing out. Yes after downgrading the PyTorch version the code can work again.

## #2693: Jax dependency error, solution other than downgrade?
**Issue:** #2693 | **Last activity:** 2024-04-06T23:54:59Z
**State:** closed | **Author:** @gouinK | **Comments:** 6 | **Created:** 2024-04-06 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2693

I know this issue has been raised in other issues (#2501 #2530), but downgrading `jax` causes other packages in my environment to throw errors, which seems like a rabbit hole to go down. Are there plans to fix this in a near-future release? Thanks!

For reference I am using scvi-tools `1.1.2`, and am receiving the import error that others have reported:
`"AttributeError: module 'jax.random' has no attribute 'KeyArray'"`

See full traceback below.

```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[1], line 11
      9 import gc
     10 import os
---> 11 import scvi
     12 import rapids_singlecell as rsc
     13 import matplotlib.pyplot as plt

File ~/miniconda3/envs/test_env/lib/python3.10/site-packages/scvi/__init__.py:11
      8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import
---> 11 from . import data, model, external, utils
     13 from importlib.metadata import version
     15 package_name = "scvi-tools"

File ~/miniconda3/envs/test_env/lib/python3.10/site-packages/scvi/data/__init__.py:25
      4 from ._datasets import (
      5     annotation_simulation,
      6     brainlarge_dataset,
   (...)
     22     synthetic_iid,
     23 )
     24 from ._manager import AnnDataManager, AnnDataManagerValidationCheck
---> 25 from ._preprocessing import (
     26     add …

**@canergen:** Hi. Can you please verify the installed version? Since scvi-tools 1.1.0, there is no explicit dependency in scvi-tools on chex anymore. It seems that flax is causing this ImportError. Can you import `from flax.training import train_state`? If you can't import flax correctly, the easiest solution would be to set up a new conda environment. Fixing these dependency issues can unfortunately otherwise be a lengthy process.

**@gouinK:** Thank you for the quick response!

I have confirmed the version:
```
scvi-tools                1.1.2                    pypi_0    pypi
```

And running `from flax.training import train_state` does indeed throw the same error, see traceback below:

```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[1], line 1
----> 1 from flax.training import train_state

File ~/miniconda3/envs/test_env/lib/python3.10/site-packages/flax/training/train_state.py:17
      1 # Copyright 2024 The Flax Authors.
      2 #
      3 # Licensed under the Apache License, Version 2.0 (the "License");
   (...)
     12 # See the License for the specific language governing permissions and …

**@canergen:** Flax is used within scvi-tools. There isn't a specific requirement for the Flax version. However, there is a mismatch in your environment in the JAX and Flax version installed (Flax is older than JAX) and this is causing issues. If you install JAX from scratch in a new environment using pypi, the error shouldn't occur. You can try uninstalling Flax and JAX in the current environment and reinstall JAX (will install a correct version of Flax) and hope that it's fixed. My own experience is that it's easier to set up a new environment.

**@gouinK:** Thanks, I will give that a try!

**@gouinK:** Looking into the versions, this is what I have - both flax and jax seem to be the latest versions shown on their respective github pages, so I'm not sure that is the issue here.

```
flax                      0.8.2
jax                       0.4.26
jaxlib                    0.4.26
chex                      0.1.7
optax                     0.2.1
```

I went ahead and uninstalled flax, jax, and jaxlib. Then ran this
`pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html`, which resulted in this:
```
scvi-tools 1.1.2 requires flax, which is not installed.
Successfully installed jax-0.4.26 jaxlib-0.4.26+cuda12.cudnn89 nvidia-cuda-nvcc-cu12-12.4.131
```

**@canergen:** I'm sorry and you need to also install Flax. Can you please check in a new environment to install JAX and Flax and see that it works. It's very difficult to fix a conda environment with wrong dependencies. We can support that creating a new conda environment and following the installation works: https://docs.scvi-tools.org/en/stable/installation.html.

## #2639: conda issue-  import scvi
**Issue:** #2639 | **Last activity:** 2024-04-06T18:33:01Z
**State:** closed | **Author:** @Sirin24 | **Comments:** 5 | **Created:** 2024-03-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2639

I tried multiple times to install scvi through. I still have an issue with import scvi. Nothing happens when i  try to import it.



#
# Name                    Version                   Build  Channel
_libgcc_mutex             0.1                 conda_forge    conda-forge
_openmp_mutex             4.5                       1_gnu    conda-forge
_pytorch_select           0.2                       gpu_0    anaconda
alabaster                 0.7.12                   pypi_0    pypi
anndata                   0.7.4            py38h32f6830_0    conda-forge
appdirs                   1.4.3                      py_1    conda-forge
argon2-cffi               20.1.0           py38h1e0a361_2    conda-forge
assorthead                0.0.11                   pypi_0    pypi
astroid                   2.4.1                    pypi_0    pypi
async_generator           1.10                       py_0    anaconda
attrs                     20.2.0             pyh9f0ad1d_0    conda-forge
babel                     2.8.0                    pypi_0    pypi
backcall                  0.2.0              pyh9f0ad1d_0    conda-forge
backports                 1.0                        py_2    anaconda
backports.functools_lru_cache 1.6.1                      py_0    anaconda
biocframe                 0.5.9                    pypi_0    pypi
biocutils                 0.1.5                    pypi_0    pypi
black                     20.8b1                     py_1    conda-forge
blas …

**@martinkim0:** Hi, what kind of import error are you getting?

**@Sirin24:** Thank you for your fast reply. I copied it below. I am not sure why when I try to import scvi it attempts to read an h5ad file.

[sir@lm602-20 scvi_folder]$ conda activate py-env
(/user/conda-environments/py-env) [sir@lm602-20 scvi_folder]$ python
Python 3.8.6 | packaged by conda-forge | (default, Oct  7 2020, 19:08:05)
[GCC 7.5.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
import scanpy as sc
 import scvi
Traceback (most recent call last):
  File "/user/conda-environments/py-env/lib/python3.8/site-packages/anndata/_io/utils.py", line 156, in func_wrapper
    return func(elem, *args, **kwargs)
  File "/user/conda-environments/py-env/lib/python3.8/site-packages/anndata/_io/h5ad.py", line 510, in read_group
    EncodingVersions[encoding_type …

**@martinkim0:** What version of scvi-tools is it installing? We don't support Python 3.8 in our latest versions. This might be the source of the issue, I'd recommend making sure that you're installing scvi-tools>=1.1.0

**@canergen:** It says that you have a file called scvi in your folder. Please rename this file: `/user/brainref/scvi_folder/scvi.py`. Local files have a higher priority during import than installed modules.

**@canergen:** To add, you currently can't read this file as there is a version conflict between anndata (likely your current environment has an older version of anndata than the one used to create the file).

## #2688: Document `SOLO.predict()` return values better.
**Issue:** #2688 | **Last activity:** 2024-04-05T16:23:53Z
**State:** closed | **Author:** @alexlenail | **Comments:** 9 | **Created:** 2024-04-04 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2688

The [documentation](https://docs.scvi-tools.org/en/stable/api/reference/scvi.external.SOLO.html#scvi.external.SOLO.predict
) reads:

> soft ([bool](https://docs.python.org/3/library/functions.html#bool) (default: True)) – Return probabilities instead of class label

However, the return values are not probabilities -- they range from -30 to 30 in my case. How should I interpret these?

<img width="599" alt="image" src="https://github.com/scverse/scvi-tools/assets/2761597/aadcdd4f-4a2c-4c6c-b6e5-6ffd1f81dc2f">

**@canergen:** It's indeed the logits on a per cell level. You can transform them with scipy.special.softmax(x, axis=1) to probabilities. @martinkim0 Can you fix the documentation?

**@alexlenail:** `softmax` or `idxmax`?

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/external/solo/_model.py#L427-L430

**@martinkim0:** @alexlenail Thanks for bringing this up! I'll take a look

**@canergen:** Softmax. I assume that you want to get probabilities.

**@alexlenail:** I raised this issue because I got this strange result: the cells with the very smallest values of `doublet` and largest values of `singlet` appear to _also_ be doublets, by careful inspection. i.e. my cells appear to most likely be doublets if they are extreme values on either side of the distribution SOLO returns. This suggests the possibility of a deep issue in this implementation of SOLO. Is this the original implementation?

**@martinkim0:** This is not the original implementation. You can find the original one here: https://github.com/calico/solo

**@martinkim0:** > the cells with the very smallest values of doublet and largest values of singlet appear to also be doublets, by careful inspection. i.e. my cells appear to most likely be doublets if they are extreme values on either side of the distribution SOLO returns

I need to look into this more since I didn't implement `SOLO` in the codebase, but from my intuition this is the desired behavior. Since the `SOLO` classifier will output two logits (one for singlets and one for doublets), we expect cells predicted to be doublets to have large values for one logit (the doublet one) and small values for the other logit (the singlet one).

Is this what you were referring to or another issue? Feel free to share any plots/data if possible, and I can look into this on my end. Are you getting predictions …

**@alexlenail:** hi @martinkim0
Alas it's worse than that. The cells which have the highest values of `doublet` (e.g. 10) _and_ the lowest values of `doublet` (e.g. -30) appear to be the credible doublets.

**@canergen:** Is the original SOLO doing better or is this a problem with SOLO? I myself found scrublet to perform better in some datasets (it's very much dataset dependent in my hands). You should see smooth values in cellular neighborhoods (similar cells should have values close to each other).

## #2134: Clean up loss computation in SCANVI
**Issue:** #2134 | **Last activity:** 2024-04-03T00:19:45Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 8 | **Created:** 2023-07-03 | **Labels:** enhancement, scanvi | **URL:** https://github.com/scverse/scvi-tools/issues/2134

There are currently conditional cases that are never reached based on the arguments that are passed into `scvi.module.SCANVAE.loss`.

**@canergen:** Hi Martin, can you refine which one? I wasn't getting to the same conclusion some weeks ago.

**@martinkim0:** I took a brief look the other day and it seems that `feed_labels` is always `False` for the loss function. This means that `is_labelled` is always `False` too, which would remove one of the conditionals.

https://github.com/scverse/scvi-tools/blob/main/scvi/train/_trainingplans.py#L793 (`training_step`)
https://github.com/scverse/scvi-tools/blob/main/scvi/train/_trainingplans.py#L820 (`validation_step`)
https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_log_likelihood.py#L5-L27 (`feed_labels` is not passed in here, so it defaults to `False`)

We can remove these lines then: https://github.com/scverse/scvi-tools/blob/main/scvi/module/_scanvae.py#L309-L337

**@canergen:** It's True inside compute_elbo. The idea is that compute_elbo computes elbo on the original labels without the classifier. I wouldn't remove this part.

**@martinkim0:** Yes, it's just that `feed_labels` is not passed into the forward pass inside `compute_elbo`, so we don't really use that argument.

**@martinkim0:** You can also see in one of our recent [test coverage reports](https://app.codecov.io/gh/scverse/scvi-tools/commit/450e6c0ceceb5fc147bc4668e01efc0fb11bcbcc/blob/scvi/module/_scanvae.py#L310) that this block is never reached

**@adamgayoso:** cc @PierreBoyeau -- at this point I would be careful because we don't want to "correct" something in a way that changes what the default is

**@PierreBoyeau:** I agree. From our previous discussions and due to the current usage of scanvi, I feel like we would need a very good reason - an overwhelming evidence of improvement in terms of integration, to justify “fixing” the scANVI code in scvi-tools.

Pierre
On Jul 3, 2023 at 9:10 PM +0200, Adam Gayoso ***@***.***>, wrote:
> cc @PierreBoyeau -- at this point I would be careful because we don't want to "correct" something in a way that changes what the default is
> —
> Reply to this email directly, view it on GitHub, or unsubscribe.
> You are receiving this because you were mentioned.Message ID: ***@***.***>

**@martinkim0:** Yes, we certainly don't want to change the default behavior of scanvi, I agree with that.

My point is that `feed_labels=True` is not the default case in the scanvi loss function, and the only way a user would modify this would be by passing in `SCANVI.train(plan_kwargs={"feed_labels": True}`. I'm not sure how likely someone is to do this considering there isn't documentation for it.

It also looks like we don't use that argument internally (`compute_elbo` has that argument defaulted to `True` but never passes it into scanvae's forward pass). If this isn't intended, then we should be changing this [line](https://github.com/scverse/scvi-tools/blob/main/scvi/model/base/_log_likelihood.py#L18) to:
```
_, _, scvi_loss = vae(tensors, loss_kwargs={"feed_labels": True}, **kwargs)
```
Le …

## #2634: No library_size argument in get_normalized_expression for MultiVI
**Issue:** #2634 | **Last activity:** 2024-04-01T23:11:03Z
**State:** closed | **Author:** @aakashsur | **Comments:** 1 | **Created:** 2024-03-28 | **URL:** https://github.com/scverse/scvi-tools/issues/2634

https://github.com/scverse/scvi-tools/blob/95f2e1d2fa921c6433a04e257d844280ba0c25e5/scvi/model/_multivi.py#L621

library_size is referenced in the docstring for the function but not in the list of arguments

**@martinkim0:** Indeed, thanks for pointing this out! Will fix this asap.

## #2623: Add support for `batch_key` in `CondSCVI`
**Issue:** #2623 | **Last activity:** 2024-03-26T19:39:57Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-03-22 | **URL:** https://github.com/scverse/scvi-tools/issues/2623

Need to ensure that not passing in a `batch_key` replicates the old code path.

## #2614: No search space autotune error
**Issue:** #2614 | **Last activity:** 2024-03-20T03:23:41Z
**State:** closed | **Author:** @mousepixels | **Comments:** 8 | **Created:** 2024-03-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2614

Autotune is telling me there is no search space. I have tried the default search space and a custom one. Both give the same error.


```python
from scvi.autotune import ModelTuner
#other imports

param_space = {...}

adata = sc.read_h5ad('adata.h5ad')
scvi.model.SCVI.setup_anndata(adata)
tuner = ModelTuner(model)

results = tuner.fit(adata, metric="validation_loss", search_space = param_space)
#results = tuner.fit(adata, metric="validation_loss") #also throws error

```


```pytb
---------------------------------------------------------------------------
RuntimeError                              Traceback (most recent call last)
Cell In[21], line 3
      1 tuner = ModelTuner(model)
----> 3 results = tuner.fit(adata, metric="validation_loss", search_space = param_space)

File ~/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/autotune/_tuner.py:116, in ModelTuner.fit(self, adata, **kwargs)
     34 """Run a specified hyperparameter sweep for the associated model class.
     35
     36 Parameters
   (...)
    113     A dataclass containing the results of the tuning experiment.
    114 """
    115 tuner, config = self._manager._get_tuner(adata, **kwargs)
--> 116 results = tuner.fit()
    117 return self._manager._get_analysis(results, config)

File ~/miniconda3/envs/scvi/lib/python3.9/site-packages/ray/tune/tuner.py:381, in Tuner.fit(self)
    379 if not self._is_ray_client:
    380     try:
--> 381         return self._local_tuner.fi …

**@martinkim0:** Hi, sorry you're experiencing this issue. Could you paste the search space you are trying out?

**@mousepixels:** I also tried the default with just:

`tuner.fit(adata, metric="validation_loss")
`

param_space = {
    'n_hidden': {
        'distribution': 'choice',
        'choices': [64, 128, 256, 512],
    },
    'n_latent': {
        'distribution': 'choice',
        'choices': [5, 10, 20, 30],
    },
    'n_layers': {
        'distribution': 'choice',
        'choices': [1, 2, 3],
    },
    'dropout_rate': {
        'distribution': 'uniform',
        'low': 0.0,
        'high': 0.5,
    },
    'gene_likelihood': {
        'distribution': 'choice',
        'choices': ['zinb', 'nb'],
    }
}

**@mousepixels:** I am also a little confused because in the model.history there is no validation loss even after successful training. Only reconstruction_loss_train.

(only shows up when early_stopping = True)

**@mousepixels:** I checked earlier versions of scvi-tools:
1.0.4 did not work
0.20.3 does work

**@martinkim0:** It's possible that this is due to a new release of Ray. Could you pass in `param_space` formatted using the tune search API:
```
from ray import tune

param_space = {
  'n_hidden': tune.choice([64, 128, 256, 512]),
  'n_latent': tune.choice([5, 10, 20, 30]),
  'n_layers': tune.choice([1, 2, 3]),
  ... # other params
}
```

**@martinkim0:** Regarding validation loss, our default is set to not run validation steps. This can be enabled with passing in `check_val_every_n_epoch=1` to the train method.

**@mousepixels:** Ok, great. That fixed it. I was a little confused because the default search_space was returning the same error. Thanks!

**@martinkim0:** Yeah we format the default search space a little differently because of the way we parse it internally. That might have been a bit confusing, sorry.

## #2613: reference mapping  using the original umap
**Issue:** #2613 | **Last activity:** 2024-03-15T16:05:33Z
**State:** closed | **Author:** @Sirin24 | **Comments:** 1 | **Created:** 2024-03-15 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2613

Hello, I would appreciate your help.
I was following https://docs.scvi-tools.org/en/1.0.1/tutorials/notebooks/scarches_scvi_tools.html

I would like to use the umap which came with an h5ad reference for reference mapping because upon computing the following, the resulting umap is different:
#obtain latent representation
adata.obsm["X_scVI"] = vae_ref.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI")
sc.tl.leiden(adata)
sc.tl.umap(adata)
sc.pl.umap(
    adata,
    color=["supercluster_term"],
    frameon=False,
    ncols=1,
)

is there a way to preserve it or infere the parameters of an already existing umap to carry those parameters to the new umap?

**@canergen:** Hi, my understanding is that you downloaded a reference dataset and want your test dataset to have a similar UMAP embedding. UMAP is not a part of scVI-tools. Therefore this is not a bug. Please use our discourse forum for feature requests. You might want to look into https://umap-learn.readthedocs.io/en/latest/transform.html to compute the same UMAP for reference and query data, but there is no way to yield this from an h5ad with an existing UMAP.

## #2597: ParserError: Error tokenizing data. C error: Expected 1 fields in line 52, saw 3
**Issue:** #2597 | **Last activity:** 2024-03-03T23:43:54Z
**State:** closed | **Author:** @aakashsur | **Comments:** 1 | **Created:** 2024-03-03 | **URL:** https://github.com/scverse/scvi-tools/issues/2597

Using `scvi.data.read_10x_atac(folder)` with files generated through the multiome pipeline throws the following error when using the `atac_peaks.bed` file as the `peaks.bed` file -

```
ParserError: Error tokenizing data. C error: Expected 1 fields in line 52, saw 3
```

This comes from the following line -
https://github.com/scverse/scvi-tools/blob/afa62c88e08015a08e8cfc36116f366920b63128/scvi/data/_read.py#L19

and it is because there are comments at the start of this file which should and can be ignored using the `comment = '#'` parameter in `pandas.read_csv()`. I don't think adding this should change the intended behavior of the function.

**@aakashsur:** Looks like the `atac_peaks.bed` file might contain an unfiltered set of peaks and doesn't work with the filtered files.

Work around might be to load as multiome and just dump the gene expression if using PeakVI.

## #2582: scvi ignoring GPU because of jax
**Issue:** #2582 | **Last activity:** 2024-03-02T00:54:21Z
**State:** closed | **Author:** @bio-la | **Comments:** 6 | **Created:** 2024-03-01 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2582

hey scvi team,
one of our users reported that they need to explicitly install jax after installation of `scvi-tools 1.1.1` to ensure the GPU is visible.
https://github.com/DendrouLab/panpipes/issues/204
can you recommend what packages and in which order I need to install them in the environment?

thank you!

**@canergen:** Is our installation guide failing? https://docs.scvi-tools.org/en/stable/installation.html

**@bio-la:** The instructions are correct, but explicitly installing transitive dependencies (jax) that are already in the environment after installing scvi is the only way to fix the issue. is this behaviour expected?

**@martinkim0:** Hi @bio-la, thanks for bringing up this issue. This is expected behavior because, by default, our dependencies don't specify the CUDA build of JAX as a direct dependency since not everyone will be running JAX on GPUs. So if users want CUDA-enabled installations of JAX (and PyTorch!), they should ideally be installing these _before_ scvi-tools.

**@martinkim0:** Also I believe pip doesn't auto-detect whether CUDA is available in the system, so calling `pip install jax` will always resolve to the CPU build. Not 100% sure about this though.

**@bio-la:** thanks for the clarification!

**@martinkim0:** I'll go ahead and close the issue if there's no additional questions

## #2217: AttributeError: module 'scvi' has no attribute 'model'
**Issue:** #2217 | **Last activity:** 2024-02-29T17:54:36Z
**State:** closed | **Author:** @183136 | **Comments:** 8 | **Created:** 2023-07-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2217

Good day,
I am having problems running `scvi$model$SCVI$setup_anndata(adata).`  And I do it get Error in py_get_attr_impl(x, name, silent) :
  AttributeError: module 'scvi' has no attribute 'model'.
Also, I tried the ``scvi.model.SCVI.setup_anndata`, but I got the same results.
So, how should I make change to resolve this problem?

```
library(reticulate)
library(sceasy)

reticulate::py_config()
reticulate::use_python("C:\\Users\\DELL\\anaconda3\\python.exe")
conda_create(envname = "scvi-env", python_version = "3.11")
py_install("scvi", pip = TRUE)
py_install("scvi-tools", pip = TRUE)

conda install -c conda-forge r-base r-essentials r-reticulate

sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)

adata <- convertFormat(WM82_Mock, from="seurat", to="anndata", main_layer="counts", drop_single_values=FALSE)
print(adata) # Note generally in Python, dataset conventions are obs x var

#Setup our AnnData for training
# run setup_anndata
scvi$model$SCVI$setup_anndata(adata)
```

**@martinkim0:** Hi, could you provide the scvi-tools version you have installed?

**@martinkim0:** Closing due to inactivity

**@Yapingli11026383:** @martinkim0 I encountered the same problem when running scvi.model,like"AttributeError: module 'scvi' has no attribute 'model'",how should I solve it?

**@martinkim0:** Are you also using scvi-tools in R? The best first step typically is to reinstall libraries in a fresh virtual environment, and that usually fixes issues like these.

**@Yapingli11026383:** > Are you also using scvi-tools in R? The best first step typically is to reinstall libraries in a fresh virtual environment, and that usually fixes issues like these.

I use scvi in jupyter and install the latest version of scvi-Tools, but there are always such errors, is it the version installed wrong

**@martinkim0:** Did you try reinstalling scvi-tools in a fresh environment after clearing the cache? Let me know.

**@martinkim0:** Closing due to inactivity

**@alicekao1118:** Hi Martin,

I got the same error while using scvi-tools in R. I used the latest scvi-tools (1.1.1). Below is the error message in R.

```
> reticulate::py_last_error()
AttributeError: module 'scvi' has no attribute 'model'

R Traceback
 1. Seurat::IntegrateLayers(...)
 2.   └─SeuratWrappers (local) method(...)
 3.     ├─scvi$model
 4.     └─reticulate:::`$.python.builtin.module`(scvi, "model")
 5.       └─reticulate:::`$.python.builtin.object`(x, name)
 6.         └─reticulate:::py_get_attr_or_item(x, name, TRUE)
 7.           └─reticulate::py_get_attr(x, name)
 8.             └─reticulate:::py_get_attr_impl(x, name, silent)
 ```

Thanks,
Alice

## #1616: New defaults
**Issue:** #1616 | **Last activity:** 2024-02-28T21:56:12Z
**State:** closed | **Author:** @watiss | **Comments:** 1 | **Created:** 2022-07-26 | **Labels:** enhancement, help wanted | **URL:** https://github.com/scverse/scvi-tools/issues/1616

- "zinb" vs "nb". Negative binomial seems more sensible of a default. Stipulation of changing will be rerunning all tutorials.
- encode_covariates=True/False. Typically we set this to True to improve mixing, but would like to check with Pierre since apparently there was a discussion about this before with Pierre and Jonas, and the conclusion was to leave it as False.

**@justjhong:** We can use the ray tune PR to test for the best hyperparameter settings once it gets in: https://github.com/scverse/scvi-tools/pull/1565

## #1955: Silence verbose logging during scVI training
**Issue:** #1955 | **Last activity:** 2024-02-28T21:55:27Z
**State:** closed | **Author:** @mxposed | **Comments:** 4 | **Created:** 2023-03-12 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1955

I would like to be able to silence metric improvement logging during scVI training.
These are shown in red here:
![logging](https://global.discourse-cdn.com/standard17/uploads/forum11/original/1X/a7fd25fd3c7ea001d503a6c07532d31518da7473.png)

These tend to make ipynb files on github hard to read (no collapsing in the viewer).

The solution could be a kwarg passed to `train` method.

Thank you

**@adamgayoso:** Can you provide your training code?

you should be able to currently add `enable_progress_bar=False` to disable the bar. Is the other printed value from early stopping?

**@mxposed:** Sure. Yes, we use early stopping

```python
model_adata = scvi.model.SCVI(adata, n_layers=2, dropout_rate=0.2, n_latent=10)
model_adata.train(
    max_epochs=400,
    use_gpu=True,
    check_val_every_n_epoch=2,
    early_stopping=True
)
```

**@martinkim0:** Is this issue resolved? I can't seem to replicate it when passing in the same arguments to `train`.

**@martinkim0:** Closing due to inactivity

## #2099: scvi.autotune.ModelTuner errors with scvi.model.SCVI
**Issue:** #2099 | **Last activity:** 2024-02-28T21:55:03Z
**State:** closed | **Author:** @bkmartinjr | **Comments:** 0 | **Created:** 2023-06-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2099

I have an autotune script and test dataset which errors out reliably (number of trails will vary likely due to random seed differences).
 The dataset in question has a lot of zeros, but no NaN data.  The same dataset seems to train fine with the base model, and I have only seen failures when using autotune/ray.tune

To reproduce - the following code, and a dataset I'll send to @martinkim0 via another channel.

```python
import ray
import anndata
import scvi

ray.init(log_to_driver=False)

adata = anndata.read_h5ad("homo_sapiens_hundreth.h5ad")
model_cls = scvi.model.SCVI
model_cls.setup_anndata(adata, layer="counts", batch_key="batch")
tuner = scvi.autotune.ModelTuner(model_cls)
tuner.info()

search_space = {
    "gene_likelihood": "nb",
    "n_hidden": ray.tune.choice([2048]),
    "n_latent": 50,
    "n_layers": 1,
}

results = tuner.fit(
    adata,
    metric="validation_loss",
    max_epochs=50,
    resources={"gpu": 0.5},
    search_space=search_space,
    num_samples=1,
)
```

```pytb
  File "/home/bruce/scvi/venv/lib/python3.10/site-packages/torch/distributions/distribution.py", line 62, in __init__
    raise ValueError(
ValueError: Expected parameter loc (Tensor of shape (128, 50)) of distribution Normal(loc: torch.Size([128, 50]), scale: torch.Size([128, 50])) to satisfy the constraint Real(), but found invalid values:
tensor([[nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan …

## #2473: Add back cellxgene-census as optional dep
**Issue:** #2473 | **Last activity:** 2024-02-27T22:15:28Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-07 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2473

See #2472

## #1721: scvi-tools autotuning with Ray Tune
**Issue:** #1721 | **Last activity:** 2024-02-27T17:20:52Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2022-10-06 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1721

This issue will serve as a parent thread for all issues related to supporting autotuning with Ray Tune.

### Basic
- [x] Implement a basic working `ModelTuner` API #1720

### Docs and tutorials
- [x] Add autotune to docs
- [x] Add tutorial: basic usage with scVI
- [x] Add tutorial: advanced usage with new model class

### Metrics
- [ ] Refactor PL logged metric keys for better visibility and consistency #1798
- [ ] Allow usage of scib-metrics
- [x] Allow for custom metrics with a callback

### Miscellaneous
- [x] Refactor training mixins for consistency #1796
- [x] Define tunables at the base class level for simplicity #1799
- [x] More comprehensive testing for the module
- [x] Enable logging with wandb for monitoring
- [ ] Discover better defaults for models #1616

## #1798: Refactor Lightning logged metrics
**Issue:** #1798 | **Last activity:** 2024-02-27T17:20:44Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2022-11-18 | **Labels:** enhancement, autotune | **URL:** https://github.com/scverse/scvi-tools/issues/1798

Currently, the metric keys that are logged with Lightning are defined within `TrainingPlan` methods. This makes it complicated to discover all the metrics that would be logged with a model class without actually going through a training loop. It would be beneficial if these metrics were exposed through a `classproperty` or something similar in order to discover them through `autotune.ModelTuner`.

## #2141: Interface `scvi.autotune.ModelTuner` with Lightning `accelerator` and `devices`
**Issue:** #2141 | **Last activity:** 2024-02-27T17:20:36Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-07-04 | **Labels:** enhancement, autotune, lightning | **URL:** https://github.com/scverse/scvi-tools/issues/2141

We need a clean way of translating between how Ray detects resources and how Lightning does it.

## #2550: ImportError: cannot import name 'sparse_csc_tensor' from 'torch'
**Issue:** #2550 | **Last activity:** 2024-02-25T15:03:39Z
**State:** closed | **Author:** @chelseabright96 | **Comments:** 2 | **Created:** 2024-02-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2550

<!-- Describe the bug -->
Good day!
When starting up my docker container, where sparse_csc_tensor is being imported in scvi/data/_utils.py, I am getting the following ImportError. I am not sure if this is due to the new version of scvi-tools== 1.1.1, as I was not getting this issue a few weeks ago. I have Torch==1.11.0 in my docker container. I would appreciate any help you could give! Thanks in advance!

File "/app/scarches_api/api.py", line 3, in
import init as scarches
File "/app/scarches_api/init.py", line 8, in
from scvi_hub.scvi_hub import ScviHub
File "/app/scvi_hub/scvi_hub.py", line 1, in
import scarches
File "/usr/local/lib/python3.9/site-packages/scarches/init.py", line 1, in
from . import dataset, metrics, trainers, models, zenodo, plotting, utils, classifiers
File "/usr/local/lib/python3.9/site-packages/scarches/models/init.py", line 1, in
from .trvae.trvae import trVAE
File "/usr/local/lib/python3.9/site-packages/scarches/models/trvae/trvae.py", line 9, in
from .losses import mse, mmd, zinb, nb
File "/usr/local/lib/python3.9/site-packages/scarches/models/trvae/losses.py", line 1, in
from scvi.distributions import NegativeBinomial
File "/usr/local/lib/python3.9/site-packages/scvi/init.py", line 11, in
from . import data, model, external, utils
File "/usr/local/lib/python3.9/site-packages/scvi/data/init.py", line 3, in
from ._anntorchdataset import AnnTorchDataset
File "/usr/local/lib/python3.9/site-packages/scvi/data/_anntorchdataset.py", li …

**@martinkim0:** This is most likely due to the new version of scvi-tools that adds some sparse tensor functionality. Could you try upgrading to a newer version of pytorch (at least 2.0) and see if the issue persists?

**@chelseabright96:** Hi Martin! Yes upgrading to the newest version worked. Thanks very much for your help!

## #2530: AttributeError: module 'jax.random' has no attribute 'KeyArray'
**Issue:** #2530 | **Last activity:** 2024-02-23T22:20:18Z
**State:** closed | **Author:** @FlowerPurr | **Comments:** 8 | **Created:** 2024-02-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2530

<!-- Describe the bug -->
Hello, maintainer,

I am hoping you can assist me with a problem I am facing. I have installed the latest version of scvi-tools, but I am still encountering an error when running the example code.


<!-- To reproduce -->

```python
import scanpy as sc
import scvi
from rich import print
from scib_metrics.benchmark import Benchmarker
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[4], line 1
----> 1 from scib_metrics.benchmark import Benchmarker

File ~/.local/lib/python3.9/site-packages/scib_metrics/__init__.py:4
      1 import logging
      2 from importlib.metadata import version
----> 4 from . import nearest_neighbors, utils
      5 from ._graph_connectivity import graph_connectivity
      6 from ._isolated_labels import isolated_labels

File ~/.local/lib/python3.9/site-packages/scib_metrics/nearest_neighbors/__init__.py:2
      1 from ._dataclass import NeighborsResults
----> 2 from ._jax import jax_approx_min_k
      3 from ._pynndescent import pynndescent
      5 __all__ = [
      6     "pynndescent",
      7     "jax_approx_min_k",
      8     "NeighborsResults",
      9 ]

File ~/.local/lib/python3.9/site-packages/scib_metrics/nearest_neighbors/_jax.py:7
      4 import jax.numpy as jnp …

**@martinkim0:** Looks like this is coming from the scib-metrics package - could you file the issue in that repository please?

**@FlowerPurr:** > Looks like this is coming from the scib-metrics package - could you file the issue in that repository please?

Thank you for your response. Following the error message and your guidance, I have identified that the issue lies with the _types.py file in the scib-metrics package. I have checked the GitHub repository for this file and found that the problem I encountered has already been addressed by you, the author.I am now facing the challenge of updating the _types.py file in the scib-metrics package to the correct version. Would you recommend downloading the new _types.py file and replacing the old one, or should I update the scib-metrics package itself? Could you please advise which method would be more appropriate?

**@canergen:** Please update the scib-metrics package. Updating the package is the safer process and should be preferred over generating your own version of a package (combining files from different releases generates a new version of a software package without any guarantees).

**@FlowerPurr:** > Please update the scib-metrics package. Updating the package is the safer process and should be preferred over generating your own version of a package (combining files from different releases generates a new version of a software package without any guarantees).

Thank you very much for your response. I will try to update the scib-metrics package to see if that resolves the issue.

**@FlowerPurr:** > Please update the scib-metrics package. Updating the package is the safer process and should be preferred over generating your own version of a package (combining files from different releases generates a new version of a software package without any guarantees).

Hello, author. I have checked my scib-metrics package, and it is indeed the latest version 0.5.0. However, I am still encountering the same error. Could you please provide some suggestions on how to resolve this issue?

**@FlowerPurr:** > Looks like this is coming from the scib-metrics package - could you file the issue in that repository please?

Thank you for your response. I have resolved the issue by referring to your handling of this problem on GitHub in the scib-metrics repository and modifying the source file. Additionally, I have a suggestion that it would be great to release a new version of scib-metrics to fix this bug.

**@martinkim0:** Hi, so sorry about this. We haven't released since the patch - I'll go ahead and do this. For now, please install from the main branch of the package.

**@martinkim0:** Hi, I've just released scib-metrics 0.5.1 with the fix. Thanks for your patience!

## #2516: Unable to set n_latent for PoissonVI
**Issue:** #2516 | **Last activity:** 2024-02-20T16:07:07Z
**State:** closed | **Author:** @shahrozeabbas | **Comments:** 3 | **Created:** 2024-02-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2516

Hello,

Thanks for your help in the recent months regarding other issues.

I have been testing `poissonvi` and noticed that I am unable to set `n_latent` for the model prior to training. It seems to always use the default calculation, both in the pre-release and the recent version from yesterday.

I was wondering if I am missing something and this is by design or a potential bug.

Let me know if you need to see an example, thanks.

@lauradmartens

**@martinkim0:** Hi @shahrozeabbas, sorry about this issue. Indeed, it looks like the model does not correctly apply a user-supplied `n_latent`. I'll go ahead and fix this and release it with 1.1.1.

**@martinkim0:** @shahrozeabbas Just released the fix with 1.1.1, let me know if this works on your end!

**@shahrozeabbas:** Working as expected, thanks so much! @martinkim0

## #2501: AttributeError: module 'jax.random' has no attribute 'KeyArray'
**Issue:** #2501 | **Last activity:** 2024-02-20T13:04:36Z
**State:** closed | **Author:** @christophechu | **Comments:** 4 | **Created:** 2024-02-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2501

<!-- Describe the bug -->

can not import scvi

<!-- To reproduce -->

```python
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
  File "<stdin>", line 1, in <module>
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/scvi/__init__.py", line 11, in <module>
    from . import autotune, data, model, external, utils, criticism
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/scvi/autotune/__init__.py", line 1, in <module>
    from ._manager import TuneAnalysis, TunerManager
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/scvi/autotune/_manager.py", line 11, in <module>
    from chex import dataclass
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/chex/__init__.py", line 17, in <module>
    from chex._src.asserts import assert_axis_dimension
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/chex/_src/asserts.py", line 26, in <module>
    from chex._src import asserts_internal as _ai
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/chex/_src/asserts_internal.py", line 34, in <module>
    from chex._src import pytypes
  File "/data/person/wup/public/miniconda3/envs/sc-python/lib/python3.11/site-packages/chex/_src/pytypes.py", line 54, in <module>
    PRNGKey = jax.random.KeyArra …

**@martinkim0:** Hi, this has been fixed with #2482 and will be available as part of our 1.1.0 release soon.

**@RijndertAriese:** Hi,

Running into similar issue, even with the update.

ImportError: cannot import name 'linear_util' from 'jax' (/Users/rijndertariese/mambaforge/envs/scanpy/lib/python3.11/site-packages/jax/__init__.py)

jax==0.4.24
jaxlib==0.4.24
scvi-tools==1.1.1

Am I missing something?

Thanks in advance

**@christophechu:** use jax==0.4.19

**@RijndertAriese:** downgraded both jax and jaxlib to 0.4.19, but this throws a new error related to jax:

ImportError: cannot import name 'random' from 'jax' (unknown location)

## #2523: Release scvi-tools 1.1.1
**Issue:** #2523 | **Last activity:** 2024-02-20T00:05:03Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-19 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2523

-   [x] Bump version in `pyproject.toml` #2514
-   [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules #2515
-   [x] ~Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch~ not rerunning
-   [x] ~After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image~ not rerunning
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged https://github.com/scverse/scvi-tutorials/releases/tag/1.1.1
-   [x] ~Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed~ no changes in tutorials
-   [x] Create a new GitHub release targeting the release branch with the same body as the previous release https://github.com/scverse/scvi-tools/releases/tag/1.1.1
-   [x] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/) https://pypi.org/project/scvi-tools/1.1.1/
-   [x] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly https://github.com/conda-forge/scvi-tools-feedstock/pull/41
-   [x] ~(Optional) Post threads on Discourse and Twitter~

## #2490: scvi modules not able to import
**Issue:** #2490 | **Last activity:** 2024-02-16T17:18:29Z
**State:** closed | **Author:** @scarlettcanny | **Comments:** 5 | **Created:** 2024-02-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2490

<!-- Describe the bug -->

Hi I am a new user to scvi, I tried to install scvi-tools from this installation manual: https://docs.scvi-tools.org/en/stable/installation.html, followed every step, and failed to import scvi sub-modules such as scvi.models, scvi.metrics, scvi.inference and scvi.dataset. ALL FAILED. only **import scvi** works.

Thanks for your help and any response is highly appreciated!


<!-- To reproduce -->

```python
#
import scvi
from scvi.dataset.dataset import GeneExpressionDataset
from scvi.inference.posterior import *
from scvi.metrics.clustering import select_indices_evenly, clustering_scores, entropy_batch_mixing
from scipy import sparse
from scvi.models.vae import VAE

```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
In [3]: import scvi

In [4]: from scvi.inference.posterior import *
   ...: from scvi.metrics.clustering import select_indices_evenly, clustering_scores, entropy_batch_mixing
---------------------------------------------------------------------------
ModuleNotFoundError                       Traceback (most recent call last)
Cell In[4], line 1
----> 1 from scvi.inference.posterior import *
      2 from scvi.metrics.clustering import select_indices_evenly, clustering_scores, entropy_batch_mixing

ModuleNotFoundError: No module named 'scvi.inference'

In [5]: from scvi.metrics.clustering import select_indices_evenly, clustering_scores, entropy_batch_mix …

**@martinkim0:** Hi, sorry you're experiencing this issue. Where did you get your code from? It looks like it's referencing the old API. We don't have a lot of those submodules anymore, and this has been the case for a while now.

**@scarlettcanny:** Hi Martin,

The code is coming from:
https://github.com/chenlingantelope/HarmonizationSCANVI/blob/master/notebooks/harmonization-CitePure-SCANVI.ipynb

Just wondering if I can still reproduce the main functions in the code?

Thanks!

**@martinkim0:** Unfortunately that notebook is outdated, and we don't have a corresponding current tutorial that goes through exactly what that notebook does. However, we do have various newer tutorials for [`scANVI`](https://docs.scvi-tools.org/en/latest/tutorials/index_scrna.html), such as [this](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/scrna/harmonization.html) one, that recapitulate the main analyses. It also looks like that tutorial uses a CITE-seq dataset. If you're interested, we also have [totalVI](https://docs.scvi-tools.org/en/latest/tutorials/notebooks/multimodal/totalVI.html), a model similar to scANVI that was primarily intended for CITE-seq. Let me know if this helps!

**@scarlettcanny:** Hi, thanks a lot for your info. Just wondering for batch removal which specific tutorial might be the most helpful one to try scanvi?

Best,
S

**@martinkim0:** Hi, you may refer to [this tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/tabula_muris.html) for how to perform batch removal with scANVI.

I'm also going to go ahead and close this issue since it's resolved, but feel free to follow up here in the future.

## #2449: UserWarning: The value argument must be within the support of the distribution   reconst_loss = -px.log_prob(x).sum(-1)
**Issue:** #2449 | **Last activity:** 2024-02-14T00:22:44Z
**State:** closed | **Author:** @FZ-hajji | **Comments:** 1 | **Created:** 2024-01-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2449

Hello,

I am using the scANVI model for batch correction of pancreas cell data, as demonstrated in this [tutorial.](https://docs.scvi-tools.org/en/0.15.1/tutorials/notebooks/scarches_scvi_tools.html) However, during the training of my model, I encountered the following warning: "The value argument must be within the support of the distribution. Reconst_loss = -px.log_prob(x).sum(-1)."

Here is the code snippet I used:
url = "https://figshare.com/ndownloader/files/24539828"
raw_adata = sc.read("raw_scib_pancreas.h5ad", backup_url=url)
sc.pp.highly_variable_genes(raw_adata, n_top_genes=2000,batch_key="tech")
scvi.model.SCANVI.setup_anndata(raw_adata, batch_key="tech", labels_key="celltype",unlabeled_category="Unknown")
vae = scvi.model.SCANVI(raw_adata)
vae.train()
adata.obsm["X_scVI"] = vae.get_latent_representation()

My question is : could this warning affect my results afterward ?

**@martinkim0:** Hi, this means that your data does not exclusively contain non-negative integers. This will most likely affect the training of your model, so we recommend that you only use raw counts for scANVI.

## #2411: Release scvi-tools 1.1.0
**Issue:** #2411 | **Last activity:** 2024-02-14T00:22:36Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-18 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2411

-   [x] Bump version in `pyproject.toml` #2462
-   [ ] ~If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules~
-   [x] Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch https://github.com/YosefLab/scvi-tools-docker/actions/runs/7863237209
-   [x] After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image https://github.com/scverse/scvi-tutorials/issues/210
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged https://github.com/scverse/scvi-tutorials/releases/tag/1.1.0
-   [x] Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed #2508 #2509
-   [x] Create a new GitHub release targeting the release branch with the same body as the previous release https://github.com/scverse/scvi-tools/releases/tag/1.1.0
-   [x] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/) https://pypi.org/project/scvi-tools/1.1.0.post1/
-   [x] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly https://github.com/conda-forge/scvi-tools-feedstock/pull/40
-   [x] (Optional) Post threads on Discourse and Twitter

## #1800: Wrong figure of observed/predicted in scANVI
**Issue:** #1800 | **Last activity:** 2024-02-14T00:21:13Z
**State:** closed | **Author:** @melancholy12 | **Comments:** 2 | **Created:** 2022-11-19 | **Labels:** bug, scanvi | **URL:** https://github.com/scverse/scvi-tools/issues/1800

![image](https://user-images.githubusercontent.com/97800939/202839631-c7a7511e-411d-431b-810a-346da8fd731b.png)

**@adamgayoso:** Can you please provide more detail of what's going on here? I reproduced the original tutorial and get the same results as in the tutorial

**@melancholy12:** Do we need to provide our observed cell_type? In this matrix, it will compare the observed with predicted.
But in fact, if we want to use it as the annotation transfer, the observed cell_type should be "unknown". I think that is why the matrix look like this.

## #2093: Update HLCA tutorial with new version
**Issue:** #2093 | **Last activity:** 2024-02-14T00:20:27Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-06-08 | **Labels:** enhancement, tutorials | **URL:** https://github.com/scverse/scvi-tools/issues/2093

https://cellxgene.cziscience.com/collections/6f6d381a-7701-4781-935c-db10d30de293

## #2101: autotune.ModelTuner reports metric as `nan` when tuning JaxSCVI
**Issue:** #2101 | **Last activity:** 2024-02-14T00:20:15Z
**State:** closed | **Author:** @bkmartinjr | **Comments:** 1 | **Created:** 2023-06-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2101

Possibly related to #2099 as it occurs on the same dataset.

When using scvi.autotune.ModelTuner with scvi.model.JaxSCVI, the metric is incorrectly reported as `nan` in some cases.  For most configs it works fine.  I was able to narrow it down to a small test case.


```python
import ray
import anndata
import scvi

ray.init(log_to_driver=False)

adata = anndata.read_h5ad("homo_sapiens_hundreth.h5ad")
model_cls = scvi.model.JaxSCVI
model_cls.setup_anndata(adata, layer="counts", batch_key="batch")
tuner = scvi.autotune.ModelTuner(model_cls)
tuner.info()

search_space = {
    "gene_likelihood": "nb",
    "n_hidden": ray.tune.choice([2048]),
    "n_latent": 50,
    "n_layers": 1,
}

results = tuner.fit(
    adata,
    metric="validation_loss",
    max_epochs=50,
    resources={"gpu": 0.5},
    search_space=search_space,
    num_samples=1,
)
```

Example output (CLI reporter):

```
== Status ==
Current time: 2023-06-12 20:18:38 (running for 00:01:25.51)
Using AsyncHyperBand: num_stopped=0
Bracket: Iter 64.000: None | Iter 32.000: None | Iter 16.000: None | Iter 8.000: None | Iter 4.000: None | Iter 2.000: None | Iter 1.000: nan
Logical resource usage: 0/48 CPUs, 0.5/4 GPUs (0.0/1.0 accelerator_type:A10G)
Result logdir: /home/bruce/scvi/ray/tune_jaxscvi_2023-06-12-20:17:12
Number of trials: 1/1 (1 RUNNING)
+---------------------+----------+--------------------+-------------------+------------+------------+------------+----------------- …

**@bkmartinjr:** As an aside, if this is a user error or there is a way to work around this, I would appreciate a pointer.  The model tuner runs these cases to max_epochs, which slows down the tuning search.  Thanks!

## #1343: Differential expression decision function
**Issue:** #1343 | **Last activity:** 2024-02-14T00:19:13Z
**State:** closed | **Author:** @vals | **Comments:** 1 | **Created:** 2022-02-09 | **Labels:** enhancement, differential expression | **URL:** https://github.com/scverse/scvi-tools/issues/1343

Hi,

I was investigating a case where the mean fold change was very small, but the `proba_de` was relatively large.

The current decision function to consider a posterior sample to support a DE hypothesis is `np.abs(lfc_sample) >= delta`. If the posterior distribution of `lfc` is wide and centered around 0 this assigns a large number of samples as DE. I see how this makes sense: if the posterior is uncertain there's a large chance the gene was actually DE, but we can't say in which direction.

In this example the mean of the fold changes is very small, but `proba_de` is 0.7.
![image](https://user-images.githubusercontent.com/668803/153129965-94a60201-6d6b-4b0b-95ea-2c7646838871.png)

I think it might make more sense to test two different hypotheses for each gene: `lfc_sample <= -delta`, `-delta < lfc_sample < delta`, and `delta < lfc_sample`. Samples then fall in three different classes, two of which are interesting DE cases:
![image](https://user-images.githubusercontent.com/668803/153130302-b8afd611-bdc0-4d76-bd44-edbf0674d09c.png)

Now the hypothesis "Is negative DE" has probability 0.26, and the hypothesis "Is positive DE" has probability 0.45.

To simplify results I think the output could return `max(is_negative_de, is_positive_de)` as `proba_de`.

What do you think?

/Valentine

**@PierreBoyeau:** Hi Valentine, this is a really useful feature to filter out pathological genes. I am reordering the codebase related to DE to prepare for upcoming changes and included your feature here: #1360

## #1782: CellAssign does not produce the expected output when trying to separate simulated data
**Issue:** #1782 | **Last activity:** 2024-02-14T00:18:30Z
**State:** closed | **Author:** @AiCurious | **Comments:** 2 | **Created:** 2022-11-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1782

CellAssign does not produce the expected output when trying to separate simulated data. I have simulated two "cell types" which have different proportions of "Gene A" and "Gene B" (simulated as multivariate normal).

The `marker_gene_mat` is defined as (essentially only one gene contributes to each cell type):
```
[[1, 0]
 [0, 1]]
```

I would expect this to correctly separate the two simulated cell types, but it doesn't (see below). However, if I change the mean used to generate one of the cell types very slightly (from 30 -> 35) then the two cell types are completely separated.

<!-- To reproduce -->

```python
from scvi.external import CellAssign
import scvi
import scanpy as sc
import pandas as pd
import seaborn as sns
import numpy as np

import anndata as ad
import matplotlib.pyplot as plt

from matplotlib.lines import Line2D

rho = np.array([[1, 0], [0, 1]], dtype=np.float64)

# Generate 2 cell types - this will result in all cells being assigned the cell type
mean_1 = np.array([30, 15])  #<--- but, change this to [35, 15] and you get perfect recovery of the simulated cell types
cov_1 = np.array([[15, 0.1], [0.1, 5]])

mean_2 = np.array([15, 40])
cov_2 = np.array([[5, 0.1], [0.1, 10]])

# Sample from the two different cell types
samples_1 = np.random.multivariate_normal(mean_1, cov_1, 1000)
samples_2 = np.random.multivariate_normal(mean_2, cov_2, 1000)

# Combine the two sets of samples into our simulated dataset
data = np.vstack(( …

**@adamgayoso:** CellAssign assumes a negative binomial observation model. Can you try the simulation with a poission lognormal model? Sample the log means from a MVN, take the exp, and then simulate poisson noise.

**@martinkim0:** Closing due to inactivity

## #2493: use_observed_lib_size in LDVAE
**Issue:** #2493 | **Last activity:** 2024-02-10T02:28:00Z
**State:** closed | **Author:** @psl-schaefer | **Comments:** 1 | **Created:** 2024-02-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2493

Why is `use_observed_lib_size=False` hardcoded into the LDVAE class? I.e. when specifying `use_observed_lib_size=True` in `scvi.model.LinearSCVI(...)` this leads to `TypeError: __init__() got multiple values for keyword argument 'use_observed_lib_size'`

Whereas for the VAE class (standard SCVI model) the default is `use_observed_lib_size=True`.

See https://github.com/scverse/scvi-tools/blob/b1e2aab74a60661ced5aad00dc99a7136cc4e759/scvi/module/_vae.py#L703

**@martinkim0:** I'm not sure actually - I think the original manuscript specifies that it learns a latent library size, and thus it was hardcoded to have that default. However, in principle I don't see an issue with making this adjustable by the user. I'll go ahead and add the changes!

## #2302: ImportError when Installing scvi-colab: Cannot Import 'Doc' from 'typing_extensions'
**Issue:** #2302 | **Last activity:** 2024-02-09T04:32:12Z
**State:** closed | **Author:** @aasingh2 | **Comments:** 4 | **Created:** 2023-10-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2302

<!-- Describe the bug -->

Hi scvi team,

I encountered an ImportError when trying to install and run scvi-colab. The code and  error message with  traceback are as follows:

<!-- To reproduce -->

```python
!pip install --quiet scvi-colab
from scvi_colab import install
install()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
INFO     scvi-colab: Installing scvi-tools.
INFO     scvi-colab: Install successful. Testing import.
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
[<ipython-input-8-87955b66e060>](https://localhost:8080/#) in <cell line: 3>()
      1 get_ipython().system('pip install --quiet scvi-colab')
      2 from scvi_colab import install
----> 3 install()

15 frames
[/usr/local/lib/python3.10/dist-packages/fastapi/exceptions.py](https://localhost:8080/#) in <module>
      4 from starlette.exceptions import HTTPException as StarletteHTTPException
      5 from starlette.exceptions import WebSocketException as StarletteWebSocketException
----> 6 from typing_extensions import Annotated, Doc  # type: ignore [attr-defined]
      7
      8

ImportError: cannot import name 'Doc' from 'typing_extensions' (/usr/local/lib/python3.10/dist-packages/typing …

**@martinkim0:** Hi, thank you for bringing up this issue. Looks like the Google Colab environment comes installed with `typing_extensions 4.5.0` already, which is conflicting with `fastapi`'s requirement for `typing-extensions >= 4.8.0`. For now, you can solve this issue by running `!pip uninstall -y typing_extensions` before installing `scvi_colab`.

Edit: Looks like restarting the runtime (Runtime > Restart runtime) after installing also solves the issue. Most likely due to some package management issue in the environment.

**@canergen:** It seems like a new "feature" on Colab's side. Do we have to rewrite the tutorials including this change or can we include it in the scvi_colab package?

**@aasingh2:** Uninstalling `typing_extensions` did the trick. Appreciate the prompt response! It might be a good idea to consider bundling it with the package itself.

Additionally, this problem seems to be stemming from the fact that `typing-extensions >= 4.8.0` is incompatible with `tensorflow-probability 0.22.0`, which was recently updated in the Colab environment.

**@mashrufehsan:** > Hi, thank you for bringing up this issue. Looks like the Google Colab environment comes installed with `typing_extensions 4.5.0` already, which is conflicting with `fastapi`'s requirement for `typing-extensions >= 4.8.0`. For now, you can solve this issue by running `!pip uninstall -y typing_extensions` before installing `scvi_colab`.
>
> Edit: Looks like restarting the runtime (Runtime > Restart runtime) after installing also solves the issue. Most likely due to some package management issue in the environment.

It worked! Thanks a lot man.

## #2388: Segmentation error on scvi-tools
**Issue:** #2388 | **Last activity:** 2024-02-05T15:36:02Z
**State:** closed | **Author:** @alexanderchang1 | **Comments:** 22 | **Created:** 2024-01-10 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2388

<!-- Describe the bug -->

I'm working on a large set of 900,000 cells, trying to run scvi on a HPC a100 GPU. But I keep getting a segmentation error.

<!-- To reproduce -->

```python
import sys
import os
import scanpy as sc
import numpy as np
import pandas as pd
from anndata import AnnData
import anndata as ad
from scipy.io import mmread
import scipy
import gc
import scvi
import os
import pandas as pd
import scanpy as sc
import scipy
import torch

scvi.model.SCVI.setup_anndata(adata_combined, batch_key ='donor_id')

vae = scvi.model.SCVI(adata_combined, n_hidden=256, n_latent=50, n_layers=2)

vae.train(accelerator = 'auto', devices ='auto',max_epochs=400, early_stopping=True)

adata_combined.obsm["X_scVI"] = vae.get_latent_representation()


```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
For instance checks, use `isinstance(X, (anndata.experimental.CSRDataset, anndata.experimental.CSCDataset))` instead.

For creation, use `anndata.experimental.sparse_dataset(X)` instead.

  return _abc_instancecheck(cls, instance)
An NVIDIA GPU may be present on this machine, but a CUDA-enabled jaxlib is not installed. Falling back to cpu.
GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
LOCAL_RANK: 0 - CUDA_VISIBLE_DEVICES: [0]
SLURM auto-requeueing enabled. Setting signal handlers. …

**@martinkim0:** Hi, are you getting the segfault during training or when calling `get_latent_representation`?

**@alexanderchang1:** During training. I had some issues with different versions of pytorch, torchaudio, torchvision cuda, so I could get it to set up the VAE model but as soon as it starts the training loop -> segmentation error. My HPC admin said this might be an issue with conda pytorch on A100 GPUs, but i reinstalled with pip in a fresh environment, and still got the same error.

**@martinkim0:** Are you able to run another PyTorch (non scvi-tools) model using that environment? Or do any simple PyTorch ops such as matmul, etc?

**@alexanderchang1:** Let me try. Give me ten minutes.

**@alexanderchang1:** Hi,

Sorry for the delay, my task got pushed back in the queue for Resources.

I ran this test and it worked.

```python
import torch

def gpu_test():
    """
    python -c "import uutils; uutils.torch_uu.gpu_test()"
    """
    from torch import Tensor
    if torch.cuda.is_available():
        device_name = lambda: torch.cuda.get_device_name(torch.cuda.current_device())
    else:
        device_name = lambda: "CUDA not available"

    print(f'device name: {device_name()}')
    x: Tensor = torch.randn(2, 4).cuda()
    y: Tensor = torch.randn(4, 1).cuda()
    out: Tensor = (x @ y)
    assert out.size() == torch.Size([2, 1])
    print(f'Success, no Cuda errors means it worked see:\n{out=}')

gpu_test()
```
```
device name: NVIDIA A100-PCIE-40GB
Success, no Cuda …

**@martinkim0:** Thanks! Could you check if the following snippet runs without errors? Trying to determine if there's an issue with the installed libraries or the data itself:
```
adata = scvi.data.synthetic_iid()
scvi.model.SCVI.setup_anndata(adata)
model = scvi.model.SCVI(adata)
model.train(max_epochs=10)
```
If this runs without errors, it's likely that you need to perform additional preprocessing on your dataset such as removing cells with low counts.

**@alexanderchang1:** Ok, running now.

**@alexanderchang1:** Hi, complete error message below:

```unix
Warning: When compiling code please add the following flags to nvcc:
         -gencode arch=compute_35,code=[compute_35,sm_35] \
         -gencode arch=compute_61,code=[compute_61,sm_61]
         -gencode arch=compute_70,code=[compute_70,sm_70]
/bgfs/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_gpu/lib/python3.9/site-packages/scvi/_settings.py:63: UserWarning: Since v1.0.0, scvi-tools no longer uses a random seed by default. Run `scvi.settings.seed = 0` to reproduce results from previous versions.
  self.seed = seed
/bgfs/alee/LO_LAB/Personal/Alexander_Chang/alc376/envs/scvi_gpu/lib/python3.9/site-packages/scvi/_settings.py:70: UserWarning: Setting `dl_pin_memory_gpu_training` is deprecated in v1.0 and will be removed in v1.1. …

**@martinkim0:** Would it be possible to determine which line of code within our library is causing this issue? There doesn't seem to be a full traceback.

**@alexanderchang1:** Hi,

Apologies for my inexperience, how do I get a full trace back? I'm using SLURM sbatch.

Best,
Alex

**@alexanderchang1:** Hi,

Sorry for the bother. I just wanted to follow up on this.

Best,
Alex

**@martinkim0:** Hey, do you happen to have a log file that was outputted by SLURM? This might be your best bet for determining what line of code is causing the segfault.

**@alexanderchang1:** Hi,

Please find attached.

[scvi_processing_gpu_758026.zip](https://github.com/scverse/scvi-tools/files/13955363/scvi_processing_gpu_758026.zip)

**@martinkim0:** Sorry, doesn't look like the log files provide any useful additional info. It's hard to debug this since we don't know what exactly is causing this segfault, so it really could be one of SLURM, the GPU itself, our library, the other libraries you have installed, etc, or a combination of all of these. Without any additional info, I wouldn't be able to provide any specific pointers. You could try one of the following and see if it fixes your issue or gives you additional pointers as to what could be causing this:

- Run on the same hardware but without SLURM
- Run on a different GPU
- Reinstall libraries _after_ deleting conda and pip caches as there could be a problematic version that's being cached
- Install previous versions of scvi-tools to see if the issue reproduces

**@alexanderchang1:** Hi,

Ok thank you, I will let you know how that goes.

**@alexanderchang1:** Hi,

Just a brief update.

- I tried running it in a jupyter notebook with a small test set of 20,000 cells. Still segmentation error (or the equivalent cause the kernel dies without saying segmentation error)
- I tried running it on both an A100 and a GTX1080, both failed, same error.
- I created a brand new environment and installed only what was necessary, although that still had some issues.
- I tried some previous versions of scvi-tools but those ran into other issues with other packages that have since been updated.

Any help would be greatly appreciated.

Best,
Alex

**@martinkim0:** One last thing I can suggest trying is just going through the code line-by-line using a debugger to determine what line is being executed before the segfault.

**@canergen:** I would suggest using faulthandler to get more insights. https://docs.python.org/3/library/faulthandler.html. At least we then now the exact line. You will likely get an easier error by following: https://www.cs.jhu.edu/~aadelucia//2021/08/24/pytorch-errors/

**@alexanderchang1:** Hi,

We isolated the problem to the latest version of PyTorch specifically. It must be installed like this.

pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117

**@martinkim0:** Hmm interesting, do you happen to know what was going on with the newest release of PyTorch that was causing this issue?

**@martinkim0:** I'll also go ahead and close this issue since it was resolved on your end

**@alexanderchang1:** We never went down to that level, sorry.

## #2370: PoissonVI Error in Pre-release
**Issue:** #2370 | **Last activity:** 2024-01-31T14:29:40Z
**State:** closed | **Author:** @shahrozeabbas | **Comments:** 14 | **Created:** 2023-12-13 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2370

Hello,

I recently posted about using `PoissonVI` and was pointed to the pre-release verison using `pip`. I am currently running that version and have run into an error that I suspect may be from the software. The error is not raised right away but after a few training epochs which is strange.

```
ValueError: Expected parameter loc (Tensor of shape (128, 16)) of distribution Normal(loc: torch.Size([128, 16]), scale: torch.Size([128, 16])) to satisfy the constraint Real(), but found invalid values:
tensor([[nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        ...,
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan],
        [nan, nan, nan,  ..., nan, nan, nan]], device='cuda:0',
       grad_fn=<AddmmBackward0>)
```

**@shahrozeabbas:** Quick update: I have updated some of my `jax` libraries and tried on a subset of the full data. It seems to be working fine now, but I will try with the entire dataset and close the issue if the problem is no longer occurring.

**@shahrozeabbas:** Still having issues with this it seems, please let me know if there's further information I need to provide to solve this, thanks!

**@martinkim0:** Hi @shahrozeabbas, sorry you're experiencing this issue. Could you try passing in `POISSONVI(var_activation=torch.nn.functional.softplus)` and see if that fixes it? ccing @lauradmartens

**@lauradmartens:** Hi @shahrozeabbas! Indeed sorry that you are experiencing issues. To try to reproduce your error, I reinstalled the pre-release sci-tools in a new conda environment and ran the model on the data from the tutorial but everything works fine there. Which dataset are you using? Did you try to run the tutorial? Does that work for you?

**@shahrozeabbas:** @lauradmartens Everything works fine from the tutorial as well as when I try with a single dataset or just a few datasets merged together. I am using unpublished dataset so can't point to anything for you to reproduce unfortunately.

The error is occuring once I feed in all ~200 samples. I am pasting the whole error message below to provide some insight. The weird thing is that it fails after 6% of the training, so it's not right away, but it runs for a bit then fails.

```
File "/vf/users/CARD_singlecell/brain_atlas_wnn/.snakemake/scripts/tmp90vs87w0.atac_model.py", line 21, in <module>
    model.train(accelerator='gpu', max_epochs=1000, devices=1, plan_kwargs={'lr_factor': 0.1})
  File "/vf/users/CARD_singlecell/brain_atlas_wnn/.snakemake/conda/7eb17e13d8955d4ba42eb01fc9666aaf_/ …

**@shahrozeabbas:** @martinkim0 it seems that did not work unfortunately, same error :(

**@canergen:** Possibly you have cells with very few ATAC reads. In my experience, this can lead to instabilities. Try filtering out cells with very low read counts (it's doesn't effect stability above 100 reads).

**@martinkim0:** Could you also try setting `scvi.settings.seed = 0` as well as passing in `train_size=1.0` to `train`?

**@shahrozeabbas:** I will try @martinkim0's suggestions which I can do immediately. If that doesn't work, will go back and try removing cells with low read counts @canergen and update as soon as I can. Thanks for all your help!

**@shahrozeabbas:** Hello,

I have gone back to the filtering step to make sure cells with low read counts are not included. Just changing that and running default settings resulted in the same error.

I tried again using the previously suggested tips, but it doesn't seem to have worked. Using `train_size=1.0` has introduced a different error regarding the data loader. I assume that it expects some sort of split to take place. I have pasted my script below just in case.

I wonder if it has something to do with the environment set up using `mamba`.

```
import scvi
import muon
import torch

scvi.settings.seed = 0
torch.set_float32_matmul_precision('high')


adata = muon.read_anndata(filename=snakemake.input.muon_object, mod=snakemake.params.assay) # type: ignore


noise = ['nucleosome_pe …

**@martinkim0:** Hey @shahrozeabbas, so sorry you're still experiencing this issue. Is there a particular reason that you're using a non-default value of `n_latent`? Could you also check if not passing in `batch_key` and `continuous_covariate_keys` changes anything? Thanks.

**@shahrozeabbas:** @martinkim0 thanks for the suggestion I will give it a try. It seems you are suggesting to just try the defaults and see if it works? Should I also try with or without `POISSONVI(var_activation=torch.nn.functional.softplus)`?

Admittedly, my understanding of the latent space is naive, but there isn't a particular reason for not using the default of `n_latent`. I've used a handful of the `scvi` models many times and typically try different values then compare the results. The dataset is 1.5 million cells and so my intuition was to increase the number. Have not explored the autotuner yet.

**@shahrozeabbas:** @canergen Is the 100 reads lower limit potentially a standard for `poissonvi` or could it vary per dataset? Below is the histogram of my data. I wondered if bumping it up to 1000 would help.

![reads_count_histogram](https://github.com/scverse/scvi-tools/assets/28969387/1cb12728-ffd2-4283-ba17-8a093fe2dc18)

**@shahrozeabbas:** Well after weeks of trying many, many things....I think I figured out what was causing the issue. I am calculating the 95% most commonly observed peaks across all samples and taking the union when calling `concat` to combine samples. I changed this to the intersection, basically an inner join of all peaks and `poissonvi` works as expected. Whatever the issue was when taking the union was not observed in only a few datasets and so everything would work fine. However, across all samples some artifact was appearing and creating a problem.

If there are any thoughts or ideas as to what was specifically happening, would greatly appreciate your insight. Otherwise I can close this issue. Thanks again for your time!

## #2273: Observed a bug in GimVI
**Issue:** #2273 | **Last activity:** 2024-01-29T17:38:38Z
**State:** closed | **Author:** @HelloWorldLTY | **Comments:** 2 | **Created:** 2023-10-04 | **Labels:** bug, gimvi | **URL:** https://github.com/scverse/scvi-tools/issues/2273

Hi, I observed a bug in GimVI. That happened when I define a GimVI model and then re-define it:
```
# create our model
model = GIMVI(seq_data, spatial_data_partial)

# train for 200 epochs
model.train(200, batch_size = len(spatial_data_partial))
```
---------------------------------------------------------------------------
IndexError                                Traceback (most recent call last)
Cell In[13], line 2
      1 # create our model
----> 2 model = GIMVI(seq_data, spatial_data_partial)
      4 # train for 200 epochs
      5 model.train(200, batch_size = len(spatial_data_partial))

File /gpfs/gibbs/project/zhao/tl688/conda_envs/scgpt/lib/python3.8/site-packages/scvi/external/gimvi/_model.py:139, in GIMVI.__init__(self, adata_seq, adata_spatial, generative_distributions, model_library_size, n_latent, correlation_const, **model_kwargs)
    137 library_log_vars = []
    138 for adata_manager in self.adata_managers.values():
--> 139     adata_library_log_means, adata_library_log_vars = _init_library_size(
    140         adata_manager, n_batches
    141     )
    142     library_log_means.append(adata_library_log_means)
    143     library_log_vars.append(adata_library_log_vars)

File /gpfs/gibbs/project/zhao/tl688/conda_envs/scgpt/lib/python3.8/site-packages/scvi/model/_utils.py:292, in _init_library_size(adata_manager, n_batch)
    286         warnings.warn(
    287             "This dataset has some empty cells, this might fail inference." …

**@martinkim0:** Hi, I was able to reproduce your error. I'm working on a fix, but meanwhile you can fix it by rerunning `setup_anndata` prior to re-defining the model.

**@HelloWorldLTY:** Thanks a lot!

## #2312: ImportError: cannot import name 'Doc' from 'typing_extensions'
**Issue:** #2312 | **Last activity:** 2024-01-26T19:12:42Z
**State:** closed | **Author:** @jheonsuh | **Comments:** 4 | **Created:** 2023-10-31 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2312

Hi, everyone

I am a beginner to python and i'm trying to follow single cell rna seq. tutorials with scanpy.

Then, i came across an error as follows.
After installing scvi-tools,
Import scvi did not work... showing importError

Any advises would be sincerely thankful..

My entire code

!pip install scanpy
import scanpy as sc

adata = sc.read_csv('GSM5226574_C51ctr_raw_counts.csv.gz').T

!pip install scvi-tools
!pip install typing-extensions --upgrade
import scvi


-->
---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
Cell In[12], line 1
----> 1 import scvi

File ~\miniconda3\Lib\site-packages\scvi\__init__.py:8
      5 import warnings
      7 from ._constants import METRIC_KEYS, REGISTRY_KEYS
----> 8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import
     11 from . import autotune, data, model, external, utils, criticism

File ~\miniconda3\Lib\site-packages\scvi\_settings.py:8
      5 from typing import Literal, Optional, Union
      7 import torch
----> 8 from lightning.pytorch import seed_everything
      9 from rich.console import Console
     10 from rich.logging import RichHandler

File ~\miniconda3\Lib\site-packages\lightning\__init__.py:17
     15 from lightning.__about__ import *  # noqa: E402, F401, F403
     16 from lightning.__version__ import version as _ …

**@martinkim0:** Hi, are you running this on Colab by chance? If so, please refer to #2302

**@panktigosar:** I am facing the same issue. !pip uninstall -y typing_extensions before installing scvi_colab worked for typing_extensions but then I got a new error. This is the whole error that I got:

NameError                                 Traceback (most recent call last)
Cell In[10], line 1
----> 1 import scvi

File ~/anaconda3/lib/python3.11/site-packages/scvi/__init__.py:8
      5 import warnings
      7 from ._constants import METRIC_KEYS, REGISTRY_KEYS
----> 8 from ._settings import settings
     10 # this import needs to come after prior imports to prevent circular import
     11 from . import autotune, data, model, external, utils, criticism

File ~/anaconda3/lib/python3.11/site-packages/scvi/_settings.py:7
      4 from pathlib import Path
      5 from typing import Literal, Op …

**@martinkim0:** What version of PyTorch do you have installed? Are you also using Cython?

**@martinkim0:** Closing due to inactivity

## #2433: AttributeError: module 'optax' has no attribute 'additive_weight_decay'
**Issue:** #2433 | **Last activity:** 2024-01-25T17:49:00Z
**State:** closed | **Author:** @Zethson | **Comments:** 1 | **Created:** 2024-01-25 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2433

<!-- Describe the bug -->

```
    def test_scgen():
        adata = scvi.data.synthetic_iid()
        pt.tl.SCGEN.setup_anndata(
            adata,
            batch_key="batch",
            labels_key="labels",
        )

        scg = pt.tl.SCGEN(adata)
>       scg.train(max_epochs=1, batch_size=32, early_stopping=True, early_stopping_patience=25)

tests/tools/test_jax_scgen.py:16:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/scvi/model/base/_jaxmixin.py:110: in train
    runner()
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/scvi/train/_trainrunner.py:99: in __call__
    self.trainer.fit(self.training_plan, self.data_splitter)
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/scvi/train/_trainer.py:186: in fit
    super().fit(*args, **kwargs)
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/lightning/pytorch/trainer/trainer.py:532: in fit
    call._call_and_handle_interrupt(
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/lightning/pytorch/trainer/call.py:43: in _call_and_handle_interrupt
    return trainer_fn(*args, **kwargs)
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packages/lightning/pytorch/trainer/trainer.py:571: in _fit_impl
    self._run(model, ckpt_path=ckpt_path)
/opt/hostedtoolcache/Python/3.10.13/x64/lib/python3.10/site-packag …

**@martinkim0:** Addressed here: #2394. Unfortunately the optax team added a backward incompatible change with a patch release. I won't be patching 1.0 since the fix will be part of 1.1.0. This can be fixed on the user side for now by downgrading to optax 0.1.7

## #2243: AttributeError: 'NoneType' object has no attribute 'numel'
**Issue:** #2243 | **Last activity:** 2024-01-23T16:23:08Z
**State:** closed | **Author:** @simomounir | **Comments:** 18 | **Created:** 2023-08-17 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2243

<!-- Describe the bug -->

Hi,

I have been running into this bug for a while. All I did was to download new data and try to get a latent space projection with GIMVI model, but it fails as soon as I want to start training with **model.train()**.

I followed the same exact steps almost as the jupyter notebook under this link below:

https://docs.scvi-tools.org/en/0.19.0/tutorials/notebooks/gimvi_tutorial.html

I only replaced the cortext() and smfish() data with my own test data (an sc-rnaseq reference dataset and a spatial smfish dataset generated by collaborators. The same preprocessing methods were performed.

<!-- To reproduce -->

```python
# Your code here
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
**AttributeError: 'NoneType' object has no attribute 'numel'**
```

#### Versions:

<!-- Output of scvi.__version__ -->

> '1.0.2'

<!-- Relevant screenshots -->

**@martinkim0:** Hi, could you paste the full traceback of the error here? Thanks!

**@simomounir:** Traceback:
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[66], line 3
      1 #model = GIMVI(seq_data_0, spatial_data_0)
      2 # train for 200 epochs
----> 3 model.train(200)

File [c:\User\.conda\envs\scvi-env\lib\site-packages\scvi\external\gimvi\_model.py:250](file:///C:/Users/.conda/envs/scvi-env/lib/site-packages/scvi/external/gimvi/_model.py:250), in GIMVI.train(self, max_epochs, use_gpu, accelerator, devices, kappa, train_size, validation_size, shuffle_set_split, batch_size, plan_kwargs, **kwargs)
    247     self.trainer.fit(self._training_plan, train_dl)
    248 else:
    249     # accepts list of val dataloaders
--> 250     self.trainer.fit(self._training …

**@martinkim0:** Looks like this might be an issue with Lightning. What version of Lightning do you have installed?

**@simomounir:** Also i need to mention that I try with the example data of cortex() and smfish() and the notebook works just fine.

Find below some prints and system info:

print(lightning.__version__)
print(torch.__version__)

2.0.7
2.0.1+cu117

Is this version problematic?

Here are some specs:

**System Information**

System: Windows
Release: 10
Version: 10.0.14393
Machine: AMD64
Processor: Intel64 Family 6 Model 85 Stepping 4, GenuineIntel

and more gpu info here:

__CUDNN VERSION: 8500
__Number CUDA Devices: 1
__CUDA Device Name: Quadro P6000
__CUDA Device Total Memory [GB]: 25.769607168


On another note, I get this warning when importing torchaudio (1) and when I call the GIMVI setup function (2):

**1** [c:\Users\.conda\envs\scvi-env-2\lib\site-packages\torchaudio\ …

**@simomounir:** Any updates on this maybe? Thanks a lot :)

**@martinkim0:** Hey sorry I wasn't able to respond to this. Were you able to resolve this? If not, could you share the data you're using? Thanks

**@simomounir:** No I was not able to resolve it as I just gave up using it since I did not hear back from anyone.

I can send you instances of the objects I am using before running **GIMVI.setup_anndata()**.

**@luschaef:** Got the same error with a simple scvi model (from here https://github.com/scverse/simple-scvi/ ). So I also would be very happy to hear something back about this issue :)

**@MatteoSpatuzzi:** Hi, I'm experiencing the same issue with a very simple dataset. Are there any updates?

**@martinkim0:** What version of scvi-tools and PyTorch Lightning do you have installed?

**@MatteoSpatuzzi:** scvi-tools                1.0.4              pyhd8ed1ab_0    conda-forge
pytorch-lightning         2.1.3              pyhd8ed1ab_0    conda-forge

**@martinkim0:** @simomounir @MatteoSpatuzzi @luschaef sorry for the delay, looks like this is an error on the PyTorch side. I'm submitting an issue in their repo and will link it here

**@MatteoSpatuzzi:** Thank you!

**@luschaef:** Thanks!

**@canergen:** @martinkim0 can you point to the PyTorch version that doesn't have this bug? Should we fix this in the requirements for now? I guess it can take a while until it's merged into PyTorch.

**@martinkim0:** It's been in the PyTorch [codebase](https://github.com/pytorch/pytorch/blob/main/torch/distributions/distribution.py#L330-L335) for a while (a couple of years). It just hasn't popped up on our end since the following need to occur:

- Model uses our implementations of negative binomial or zinb distributions
- Dataset has invalid values (non-integer and/or negative)
- Model does not pass in the `scale` argument to the distribution constructor

I've put in a pull request for PyTorch but it might just be easier and quicker to patch it on our end.

**@MatteoSpatuzzi:** Hello, are there any updates on this?

**@martinkim0:** It's fixed and will be available in the next release (1.1.0)

## #2424: Error Importing - dadapt_adamw; 'type' object is not subscriptable
**Issue:** #2424 | **Last activity:** 2024-01-20T23:49:22Z
**State:** closed | **Author:** @rigelsison | **Comments:** 2 | **Created:** 2024-01-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2424

I was trying to import and then came across this error. I'm not sure how to address this and any help would be appreciated.

```python
import os
import numpy as np
import pandas as pd
import scipy
import anndata
import scanpy as sc
import pybiomart
import scvi
import torch
import random
import seaborn as sns
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[24], line 8
      6 import scanpy as sc
      7 import pybiomart
----> 8 import scvi
      9 import torch
     10 import random

File ~/Library/jupyterlab-desktop/jlab_server/lib/python3.8/site-packages/scvi/__init__.py:10
      7 from ._settings import settings
      9 # this import needs to come after prior imports to prevent circular import
---> 10 from . import autotune, data, model, external, utils
     12 from importlib.metadata import version
     14 package_name = "scvi-tools"

File ~/Library/jupyterlab-desktop/jlab_server/lib/python3.8/site-packages/scvi/autotune/__init__.py:1
----> 1 from ._manager import TuneAnalysis, TunerManager
      2 from ._tuner import ModelTuner
      3 from ._types import Tunable, TunableMixin

File ~/Library/jupyterlab-desktop/jlab_server/lib/python3.8/site-packages/scvi/autotune/_manager.py:22
     20 from scvi._types import AnnOrMuDat …

**@martinkim0:** Hi, looks like you are trying to use scvi-tools with Python 3.8. We don't support that version anymore with our newer releases, and this is likely the source of the issue. I would suggest updating to Python 3.9 - 3.11.

**@rigelsison:** That fixed the issue, thank you!

## #2399: poisson_gene_selection
**Issue:** #2399 | **Last activity:** 2024-01-19T18:38:45Z
**State:** closed | **Author:** @xianjieshen | **Comments:** 6 | **Created:** 2024-01-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2399

<!-- Describe the bug -->
When running your tutorial, I encountered some errors. It is indicating that my 'anndata' is not recognized as raw data. However, my 'anndata' file contains raw data, and even when I use the raw matrix, it still doesn't work. Here are the details of the issue:
ValueError when using` poisson_gene_selection`
When attempting to use the `poisson_gene_selection function` from `scvi-tools`, a ValueError is raised indicating that 'raw count data' is expected. This occurs even when a dataset is loaded that I believe to be in the correct format.


<!-- To reproduce -->


```
import os
import tempfile
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotnine as p9
import scanpy as sc
import scvi
import torch
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
adata=sc.read('/home/xjs/h5ad/adata.h5ad')
scvi.data.poisson_gene_selection(adata)
adata.var.head()
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```
Global seed set to 0
/home/bachelortwo/miniconda3/envs/scanpy/lib/python3.9/site-packages/anndata/__init__.py:51: FutureWarning: `anndata.read` is deprecated, use `anndata.read_h5ad` instead. `ad.read` will be removed in mid 2024.
/home/bachelortwo/miniconda3/envs/scanpy/lib/python3.9/site-packages/anndata/_core/anndata.py:1906: UserWarning: Observation names are not unique. To make them unique, call …

**@martinkim0:** In which layer is your raw count data? If it's not `adata.X`, then please pass in the `layer` argument into the function. Could you also run `np.all(a >= 0) & np.all(a % 1 == 0)` on your array to double-check?

**@xianjieshen:** > In which layer is your raw count data? If it's not `adata.X`, then please pass in the `layer` argument into the function. Could you also run `np.all(a >= 0) & np.all(a % 1 == 0)` on your array to double-check?

My raw data has undergone[`Deepimpute`](https://github.com/lanagarmire/DeepImpute).
Should there be zero values in this context?After imputation, can the function not be used if zero values have been filled?

**@martinkim0:** I'm not familiar with DeepImpute, but the only restriction we put on this function is that values need to be non-negative integers. Are the zero values filled with non-integer numbers? If so, it's probably more suitable to use the pre-imputation raw counts.

**@xianjieshen:** > I'm not familiar with DeepImpute, but the only restriction we put on this function is that values need to be non-negative integers. Are the zero values filled with non-integer numbers? If so, it's probably more suitable to use the pre-imputation raw counts.

I understand, thank you ! You've resolved my question.

**@martinkim0:** I also realized that the error message could be more descriptive instead of just saying "raw count data". I'll go ahead and update this.

**@martinkim0:** Addressed in #2422

## #2420: `Trainer.fit` stopped: `max_epochs=1` reached.
**Issue:** #2420 | **Last activity:** 2024-01-19T18:03:51Z
**State:** closed | **Author:** @yubin-ai | **Comments:** 4 | **Created:** 2024-01-19 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2420

<!-- Describe the bug -->

[`Trainer.fit` stopped: `max_epochs=1` reached.]

<!-- To reproduce -->

```python
scvi.model.SCVI.setup_anndata(
ad,
layer="raw",
categorical_covariate_keys=['block_id','tma'])
model = scvi.model.SCVI(ad, n_layers=2, n_latent=30)

model.train(enable_progress_bar=False)
SCVI_LATENT_KEY = "X_scVI"
```

GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
You are using a CUDA device ('NVIDIA A10G') that has Tensor Cores. To properly utilize them, you should set `torch.set_float32_matmul_precision('medium' | 'high')` which will trade-off precision for performance. For more details, read https://pytorch.org/docs/stable/generated/torch.set_float32_matmul_precision.html#torch.set_float32_matmul_precision
LOCAL_RANK: 0 - CUDA_VISIBLE_DEVICES: [0]
`Trainer.fit` stopped: `max_epochs=1` reached.


#### Versions:
'1.0.2'

> VERSION

in scvi.train.Trainer,   max_epochs is the  Number of passes through the dataset. If None, defaults to np.min([round((20000 / n_cells) * 400), 400]). so when the dataset is larger than 20k*400 it will be 1. I have a very large dataset and I assume it leads to max_epochs =1 .

is this ok or this is wrong?

**@canergen:** I recommend setting it manually to 20. With 20 epochs we have good experience on large datasets. You might want to increase batch size to 1024 to increase train speed and enable early stopping, see documentation on how to enable it.
Changing the default creates backwards incompatibility and I am not eager to change it for now.

**@yubin-ai:** > I recommend setting it manually to 20. With 20 epochs we have good experience on large datasets. You might want to increase batch size to 1024 to increase train speed and enable early stopping, see documentation on how to enable it. Changing the default creates backwards incompatibility and I am not eager to change it for now.

This is super helpful! Thanks.
I understand the concern on changing the default. How about adding a detection step on the cell number and then add a warning there to inform the user this potential issue. I had a hard time understanding the results due to its super weird looking umap and did not realize this issue until several rounds of debugging. and the dataset is so big, it can be hard to debug. Appreciate it!

**@martinkim0:** Thanks for the suggestion! We're are aware of this potential issue - it's been addressed in the latest version (#2083) that is set to release soon (1.1.0). It will warn when `max_epochs=1` due to a larger number of observations.

**@martinkim0:** Closing since this is addressed in the new release.

## #2360: Release scvi-tools 1.1.0-rc.2
**Issue:** #2360 | **Last activity:** 2024-01-18T18:19:51Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2360

-   [x] Bump version in `pyproject.toml`. #2400
-   [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules. #2401
-   [x] Create a new GitHub draft release targeting the release branch with the same body as the previous release (don't release yet). https://github.com/scverse/scvi-tools/releases/tag/untagged-6d79987a12fca006b79a
-   [ ] ~Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch.~
-   [ ] ~After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image.~
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged. https://github.com/scverse/scvi-tutorials/releases/tag/1.1.0rc2
-   [x] Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed. #2402 #2403
-   [x] Double check everything and then publish the draft release on the main repo. https://github.com/scverse/scvi-tools/releases/tag/1.1.0rc2
-   [ ] ~Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly.~
-   [x] Check that the version updates correctly on [PyPI](https://pypi.org/project/scvi-tools/). https://pypi.org/project/scvi-tools/1.1.0rc2/
-   [ ] ~(Optional) Post threads on Discou …

## #2392: PyTorch distribution `__repr__` error with custom distributions
**Issue:** #2392 | **Last activity:** 2024-01-17T22:48:21Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2392

When a dataset contains values outside of the support values for either the negative binomial or zero-inflated negative binomial, this leads to an `AttributeError` in the following line: https://github.com/pytorch/pytorch/blob/main/torch/distributions/distribution.py#L332.

This happens in some models (GIMVI, simple-scvi) where `scale` is passed in as `None`, and thus the `__repr__` method attempts to call `.numel()` on that but fails.  Reported in #2243. Simplest fix is to have a default value for `scale` when it is not passed in or override the `__repr__` method.

## #2394: Support Optax 0.1.8
**Issue:** #2394 | **Last activity:** 2024-01-17T21:43:42Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-17 | **Labels:** enhancement, dependencies | **URL:** https://github.com/scverse/scvi-tools/issues/2394

Optax 0.1.8 breaks tests as `additive_weight_decay` cannot be imported anymore.

https://github.com/scverse/scvi-tools/actions/runs/7554257121/job/20566735530#step:6:1680
https://github.com/google-deepmind/optax/releases

## #2246: Type error when I run vae.train()
**Issue:** #2246 | **Last activity:** 2024-01-17T01:26:56Z
**State:** closed | **Author:** @Huiflorazhan | **Comments:** 6 | **Created:** 2023-08-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2246

<when I run the following codes, there is a type error>
I'm using Mac to run the codes, I don't know how to solve this problem. Could you help me with this? Thank you in advance.

#scvi.model.SCVI.setup_anndata(adata)
#vae = scvi.model.SCVI(adata)
#vae.train()


---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[16], line 3
      1 scvi.model.SCVI.setup_anndata(adata)
      2 vae = scvi.model.SCVI(adata)
----> 3 vae.train()

File [~/anaconda3/.conda/lib/python3.11/site-packages/scvi/model/base/_training_mixin.py:78](https://file+.vscode-resource.vscode-cdn.net/Users/huizhan/anaconda3/python_learning/~/anaconda3/.conda/lib/python3.11/site-packages/scvi/model/base/_training_mixin.py:78), in UnsupervisedTrainingMixin.train(self, max_epochs, use_gpu, accelerator, devices, train_size, validation_size, shuffle_set_split, batch_size, early_stopping, plan_kwargs, **trainer_kwargs)
     74 es = "early_stopping"
     75 trainer_kwargs[es] = (
     76     early_stopping if es not in trainer_kwargs.keys() else trainer_kwargs[es]
     77 )
---> 78 runner = self._train_runner_cls(
     79     self,
     80     training_plan=training_plan,
     81     data_splitter=data_splitter,
     82     max_epochs=max_epochs,
     83     use_gpu=use_gpu,
     84     accelerator=accelerator,
     85     devices=devices,
     86     **trainer_kwargs,
     87 )
     88 …

**@jxtngx:** can you please share your trainer configuration? it appears that maybe you've set devices to `-1` to use all devices, or the argument has accidentally been passed in as something other than an `int`.

**@martinkim0:** This is definitely an issue from our side, I've added a fix in #2247

**@Huiflorazhan:** Thank you so much!

**@martinkim0:** You can fix this for now by passing in `vae.train(accelerator="cpu", devices=1)`

**@Huiflorazhan:** > You can fix this for now by passing in `vae.train(accelerator="cpu", devices=1)`

It works! Thanks!

**@Rachel-LiJ:** Write it this way `vae.train(use_gpu=True)`，and it also runs

## #2391: AttributeError occurred when I use scVI method in R
**Issue:** #2391 | **Last activity:** 2024-01-12T03:46:03Z
**State:** closed | **Author:** @redtorrentCN | **Comments:** 2 | **Created:** 2024-01-11 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2391

<!-- Describe the bug -->

Hi, all. I'm just a fresh man using scVI-tools in R env. when I try to integrate my data using scVI method, an error occurred as following:

<!-- To reproduce -->
#### my code:
```
library(Seurat)
options(Seurat.object.assay.version = "v5")
library(SeuratData)
obj <- LoadData("ifnb")
obj <- subset(obj, nFeature_RNA > 1000)
obj[["RNA"]] <- split(obj[["RNA"]], f = obj$stim)
obj <- NormalizeData(obj)
obj <- FindVariableFeatures(obj)
```
```library(sceasy)
library(reticulate)
Sys.setenv(RETICULATE_PYTHON="C:\\Miniconda\\envs\\py311scvi\\python.exe")
sc <- import("scanpy", convert = FALSE)
scvi <- import("scvi", convert = FALSE)
new_obj<-obj
new_obj[["RNA"]] <- as(object = obj[["RNA"]], Class = "Assay")
top2000 <- head(VariableFeatures(new_obj), 2000)
new_obj <- new_obj[top2000]
andata_obj <- sceasy::convertFormat(new_obj,
                                    from="seurat",
                                    to="anndata",
                                    main_layer="counts",
                                    drop_single_values=FALSE)
scvi$model$SCVI$setup_anndata(andata_obj,batch_key = 'stim')
model = scvi$model$SCVI(andata_obj)
model$train()
```
#### Error
```GPU available: False, used: False
TPU available: False, using: 0 TPU cores
Error in py_call_impl(callable, call_args$unnamed, call_args$named) :
  AttributeError: 'DataSplitter' object has no attribute '_has_setup_TrainerFn.FITTING'

── Python Except …

**@martinkim0:** Hi, it's likely that you will need to update PyTorch Lightning. You can do so with `pip install -U lightning`

**@redtorrentCN:** > Hi, it's likely that you will need to update PyTorch Lightning. You can do so with `pip install -U lightning`

Thank you ,sir. I'll try it.

## #2333: scvi-tools fails
**Issue:** #2333 | **Last activity:** 2024-01-11T19:59:01Z
**State:** closed | **Author:** @joseagraz | **Comments:** 14 | **Created:** 2023-11-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2333

scvi-tools installation fails on ubuntu 20. I've tried the installation two different ways (see below), but did not get far. Any suggestions how install scvi-tools properly?
GPU: NVIDIA RTX A4000

**1st SCVI installation fail:** See atached scvi-env_lib_list_version.txt for environment libraries installed

conda create -n scvi-env python=3.9
conda activate scvi-env
conda install -c anaconda pip
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
conda install jax jaxlib -c conda-forge
conda install scvi-tools -c conda-forge

Error:
/python3.9/site-packages/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameEv

**2nd SCVI installation fail:** See atached scvi-env-p310_lib_list_version.txt for environment libraries installed
conda create -n scvi-env-p310 python=3.10
conda activate scvi-env-p310
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
conda install anndata -c conda-forge
conda install scvi-tools -c conda-forge
conda install -c conda-forge scanpy python-igraph leidenalg
conda install jax jaxlib -c conda-forge

Error:
libtorch_cuda.so: cannot open shared object file: No such file or directory

reinstalling torch produces:
lib/python3.10/site-packages/torchaudio/lib/libtorchaudio.so: undefined symbol: _ZNK5torch8autograd4Node4nameEv
[scvi-env_lib_list_version.txt](https://github.com/scverse/scvi-tools/files/13444319/scvi-env_lib_list_version.txt)
[s …

**@martinkim0:** Could you try installing PyTorch and JAX dependencies as follows and seeing if it works:
```
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 cuda-nvcc=11.8 -c pytorch -c nvidia -c conda-forge
pip install jax[cuda11_pip] -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```
and then
```
pip install scvi-tools
```
We've had some issues with our conda install in the past, so please give pip a try!

**@robinfallegger:** Jumping on this issue as well. I have tried installing scvi-tools in many ways but always bump into variations of the following error:
`CUDA backend failed to initialize: Found cuSOLVER version 11305, but JAX was built against version 11401, which is newer.`

This is after installing it the way @martinkim0 suggested. I have not found a way yet to match cuda, cudnn etc with jax and jaxlib... Would be extremely grateful for a combination that works

**@robinfallegger:** Manually upgrading seems to work 👍
Would be great if you could update the installation section in the docs :)

**@martinkim0:** Hey @demian1, glad you got it to work! What package did you manually upgrade that led to the fix?

**@joseagraz:** I've tried the suggested recipe including scanpy, but get the error below. Reinstalling scvi-tools did not help. Have any other suggestions to try? Thank you

conda install pytorch torchvision torchaudio pytorch-cuda=11.8 cuda-nvcc=11.8 -c pytorch -c nvidia -c conda-forge
pip install jax[cuda11_pip] -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
pip install scvi-tools
pip install scanpy

OSError: libtorch_cuda.so: cannot open shared object file: No such file or directory

**@martinkim0:** Hi, please see https://github.com/pytorch/pytorch/issues/91186 and see if any of the fixes work for you

**@ghar1821:** Ran into few errors (different from the ones described above) installing scVI using the tutorial on the website. This solution below from @martinkim0 works for me in conjunction with cuda/11.7.1 and python 3.9.

> Could you try installing PyTorch and JAX dependencies as follows and seeing if it works:
>
> ```
> conda install pytorch torchvision torchaudio pytorch-cuda=11.8 cuda-nvcc=11.8 -c pytorch -c nvidia -c conda-forge
> pip install jax[cuda11_pip] -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
> ```
>
> and then
>
> ```
> pip install scvi-tools
> ```
>
> We've had some issues with our conda install in the past, so please give pip a try!

**@joseagraz:** This installation below worked for me. I'm still getting some CUDA errors, but things are moving.

Unable to initialize backend 'rocm': NOT_FOUND: Could not find registered platform with name: "rocm". Available platform names are: CUDA
Unable to initialize backend 'tpu': INTERNAL: Failed to open libtpu.so: libtpu.so: cannot open shared object file: No such file or directory

**Installation:**
git clone https://github.com/scverse/scvi-tools.git
conda create -n scvi-pip-p310 python=3.10
conda activate scvi-pip-p310
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
cd scvi-tools
pip install .
pip install scanpy
pip install jax[cuda11_pip] -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
pip install --user scikit-mis …

**@robinfallegger:** @martinkim0 After setting it up as explained in your previous comment, I needed to upgrade
`pip install nvidia-cusolver-cu11==11.4.1.48`

**@frac2738:** I managed to fix all the compatibility issues by running
  `conda install jaxlib=*=*cuda* jax cuda-nvcc -c conda-forge -c nvidia` ,
which took care of selecting the right version based on the cuda version I have installed

This is the full code:

    conda create -n scvi-env python=3.9
    conda activate scvi-env

    # check cuda version
    nvidia-smi
    +---------------------------------------------------------------------------------------+
    | NVIDIA-SMI 545.23.08              Driver Version: 545.23.08    CUDA Version: 12.3     |
    |-----------------------------------------+----------------------+----------------------+
    | GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp   Perf          Pwr:Usage/Cap | …

**@joseagraz:** @frac2738, tried your recipe and worked great getting the same output as your. However, I also received a warning on JAX and cuDNN conflict. Any suggestions on how to resolve this new issue?

Unable to initialize backend 'cuda': Found cuDNN version 8700, but JAX was built against version 8800, which is newer. The copy of cuDNN that is installed must be at least as new as the version against which JAX was built.

![Screenshot from 2024-01-11 13-47-08](https://github.com/scverse/scvi-tools/assets/2177473/6b9d5ae4-2196-4046-a490-cbc5afc3ce07)

**@joseagraz:** Actually, the warning went away after executing the command below. Any suggestion how to resolve the other warning? I'm using a nVidia RTXA4000 GPU

"pip install --upgrade "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html"

2024-01-11 13:52:13,509 - INFO - Unable to initialize backend 'rocm': NOT_FOUND: Could not find registered platform with name: "rocm". Available platform names are: CUDA
2024-01-11 13:52:13,520 - INFO - Unable to initialize backend 'tpu': INTERNAL: Failed to open libtpu.so: libtpu.so: cannot open shared object file: No such file or directory

**@martinkim0:** @joseagraz I wouldn't worry about the JAX warning if you don't intend on using any of our JAX models. The additional warning messages are saying that there's no support for AMD and TPU accelerators, which shouldn't be an issue since you're using NVIDIA.

**@joseagraz:** Great, thanks.
I put together these two repositories with the info gathered here. I hope it helps others!

https://github.com/Kidney-Science/python_single_cell_analisys
https://github.com/Kidney-Science/install_RTXA4000_Driver_CUDA_cudNN_Ubuntu_22

## #2092: [minor] Spurious warning when using JaxSCVI
**Issue:** #2092 | **Last activity:** 2024-01-11T04:50:38Z
**State:** closed | **Author:** @bkmartinjr | **Comments:** 2 | **Created:** 2023-06-07 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2092

When triaining JaxSCVI model on a GPU-enabled host, there is a spurious warning emitted:

> .../lightning/pytorch/trainer/setup.py:176: PossibleUserWarning: GPU available but not used. Set `accelerator` and `devices` using `Trainer(accelerator='gpu', devices=1)`.

There are similar warnings filtered - I thought you might want to add this one as well.

I ran on a AWS g5 instance (A10)

```python
scvi.model.JaxSCVI.setup_anndata(adata, layer="counts", batch_key="batch")
vae = scvi.model.JaxSCVI(adata)

# when on a g5 instance, with A10G TensorCores, torch requires that we specify desired precision.
torch.set_float32_matmul_precision("high")

vae.train(max_epochs=100, early_stopping=True, batch_size=4096)
```


#### Versions:

scvi version:  1.0.0
Ubuntu 22
Python 3.10
cuda 11.8

**@adamgayoso:** this must be a generic torch/lightning warning as jaxscvi technically doesn't use torch as a backend

**@bkmartinjr:** it seems to be harmless, so no urgency from my viewpoint

## #2340: Add indices to scvi criticism if using other subset AnnData object
**Issue:** #2340 | **Last activity:** 2024-01-11T00:03:13Z
**State:** closed | **Author:** @canergen | **Comments:** 0 | **Created:** 2023-11-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2340

Add indices here.

https://github.com/scverse/scvi-tools/blob/021fc36a75fc0b825f306133eba908cc7c6b2215/scvi/criticism/_ppc.py#L94C49-L94C49

## #2275: ImportError: cannot import name 'settings' from 'scvi' (unknown location)
**Issue:** #2275 | **Last activity:** 2024-01-10T20:32:00Z
**State:** closed | **Author:** @Kiliankleemann | **Comments:** 4 | **Created:** 2023-10-06 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2275

<!-- Describe the bug -->

Importing and loading scvi in jupyter notebook

<!-- To reproduce -->

```python
import scvi
import torch
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
from scvi.model.utils import mde
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
AttributeError: module 'scvi' has no attribute 'settings'
ImportError: cannot import name 'settings' from 'scvi' (unknown location)
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION
pip install
scvi-tools                    1.0.3

<!-- Relevant screenshots -->

**@martinkim0:** Hi, can you check whether this issue reproduces in a fresh Python environment and re-installing scvi-tools?

**@naveedaq91:** Hi,

i am facing the same issue, has anyone been able to resolve this ?

**@martinkim0:** Hi, could you also check if the issue reproduces in a fresh environment? Thanks

**@martinkim0:** Closing due to inactivity

## #2386: Address xarray sparse issues in criticism
**Issue:** #2386 | **Last activity:** 2024-01-10T17:33:24Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 1 | **Created:** 2024-01-09 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2386

https://github.com/pydata/xarray/issues/8602

**@martinkim0:** Fixed in sparse==0.15.1

## #1610: DestVI log-variational for Vamp_prior
**Issue:** #1610 | **Last activity:** 2024-01-05T19:40:55Z
**State:** closed | **Author:** @canergen | **Comments:** 0 | **Created:** 2022-07-22 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1610

In models/_condscvi.py line 139, we don't check for log_variational (default is true in CondSCVI). The input for the decoder at inference is therefore different from the training input. Effect is not clear, but most likely unwanted.

```
for tensors in scdl:
    x = tensors[REGISTRY_KEYS.X_KEY]
    y = tensors[REGISTRY_KEYS.LABELS_KEY]
    out = self.module.inference(x, y)
```

Fix is straightforward but leads to breaking change.
It should be similar to model.get_latent_representation() meaning:

```
inference_inputs = self.module._get_inference_input(tensors)
out = self.module.inference(**inference_inputs)
```

## #2376: No validation_step for scANVI
**Issue:** #2376 | **Last activity:** 2024-01-04T22:01:06Z
**State:** closed | **Author:** @marcovarrone | **Comments:** 3 | **Created:** 2024-01-04 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2376

I am trying to log the validation loss and accuracy during the fitting of scANVI.
However, I noticed that the function `validation_step` of `SemiSupervisedTrainingPlan` is never called.

I am following the [seed labeling tutorial](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/seed_labeling.html) using version 1.0.4 of scvi-tools.

Is this something expected?

Thank you very much!

**@martinkim0:** Hi, thanks for your question. Yes, by default we don't run the validation loop during training. You can change this behavior by passing in `check_val_every_n_epoch=1` to the training method.

**@marcovarrone:** Thank you very much! I didn't notice
Shouldn't it be the default if `train_size != 1.0` ?

**@martinkim0:** Yeah, technically we should be running validation by default since `train_size != 1.0` (or alternatively setting train_size=1.0), but we haven't done so because of backwards compatibility reasons. Sorry for the confusion!

## #2375: Cannot train model
**Issue:** #2375 | **Last activity:** 2024-01-03T17:13:51Z
**State:** closed | **Author:** @stefraptis | **Comments:** 3 | **Created:** 2023-12-30 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2375

<!-- Describe the bug -->

While I am am trying to run the differential expression test using the tutorial found https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/scVI_DE_worm.html the model cannot be trained.
<!-- To reproduce -->

model = scvi.model.SCVI(
    adata, gene_likelihood="nb"
)  # We use Negative Binomial count likelihoods, following Boyeau et al., 2023.
model.train(
    check_val_every_n_epoch=1,
    max_epochs=400,
    early_stopping=True,
    early_stopping_patience=20,
    early_stopping_monitor="elbo_validation",
)

INFO: GPU available: False, used: False
INFO:lightning.pytorch.utilities.rank_zero:GPU available: False, used: False
GPU available: False, used: False
INFO: TPU available: False, using: 0 TPU cores
INFO:lightning.pytorch.utilities.rank_zero:TPU available: False, using: 0 TPU cores
TPU available: False, using: 0 TPU cores
INFO: IPU available: False, using: 0 IPUs
INFO:lightning.pytorch.utilities.rank_zero:IPU available: False, using: 0 IPUs
IPU available: False, using: 0 IPUs
INFO: HPU available: False, using: 0 HPUs
INFO:lightning.pytorch.utilities.rank_zero:HPU available: False, using: 0 HPUs
HPU available: False, using: 0 HPUs
/usr/local/lib/python3.10/dist-packages/lightning/pytorch/loops/fit_loop.py:281: PossibleUserWarning: The number of training batches (5) is smaller than the logging interval Trainer(log_every_n_steps=10). Set a lower value for log_every_n_steps if you want to see logs for the trai …

**@martinkim0:** I've never seen this particular error. Are you using the dataset from the tutorial or your own data? Also, are you on Linux or Mac?

**@stefraptis:** Hello, thanks for your reply. I am using Windows and working on Google Colab. However, I found the cause of the error, which seems to be due to inconsistency between SCVI and PyTorch. I had installed the latest edition of PyTorch, while version 2.1.0 was needed. Downgrading to 2.1.0 solved the issue!

**@martinkim0:** Great, glad you were able to resolve the issue! I'll be closing this thread.

## #1464: Importerror for scVI in tutorials
**Issue:** #1464 | **Last activity:** 2024-01-02T15:17:32Z
**State:** closed | **Author:** @Zethson | **Comments:** 21 | **Created:** 2022-03-26 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1464

# Describe the bug
```
Importerror for scVI.
```

# To reproduce
Execute your very own tutorial: https://colab.research.google.com/github/scverse/scvi-tutorials/blob/0.15.3/api_overview.ipynb

```
ImportError                               Traceback (most recent call last)

[<ipython-input-4-c98868e3b7fa>](https://localhost:8080/#) in <module>()
----> 1 import scvi
      2 import scanpy as sc
      3 import matplotlib.pyplot as plt
      4
      5 sc.set_figure_params(figsize=(4, 4))

12 frames

[/usr/local/lib/python3.7/dist-packages/torchtext/vocab/vocab_factory.py](https://localhost:8080/#) in <module>()
      2 from typing import Dict, Iterable, Optional, List
      3 from collections import Counter, OrderedDict
----> 4 from torchtext._torchtext import (
      5     Vocab as VocabPybind,
      6 )

ImportError: /usr/local/lib/python3.7/dist-packages/torchtext/_torchtext.so: undefined symbol: _ZNK3c104Type14isSubtypeOfExtERKSt10shared_ptrIS0_EPSo
```

#### Versions:
Latest stable


I suspect that this is some missmatch of incompatible versions of PyTorch and torchtext.

**@adamgayoso:** If I had to guess it's because the latest pyro version lower bounds torch to 1.11.0 and somehow the colab environment has an older version of torchtext, which I believe may be required by pytorch lightning

**@adamgayoso:** I think our options are to either wait for this https://github.com/googlecolab/colabtools/issues/2668 or to upper bound pyro. I'm inclined to wait.

**@DRSEI:** Hi @adamgayoso  so are you saying that I cant use the SCVI at this stage?

**@Zethson:** @adamgayoso I don't think that Google is known for solving their issues fast. IMO working tutorials (with collab) are very important and I would suggest to upper bound pyro instead of waiting.

Choice is yours ofc.

**@rangan2510:** Presently this works:

!pip install scvi-tools==0.15.1 pyro-ppl==1.8.0 umap-learn scanpy scikit-misc leidenalg --quiet

**@adamgayoso:** Indeed the problem is solved if the very first thing that is done is `pip install pyro-ppl==1.8.0`.

@Zethson I think the solution is a `scvi-colab` package that is pip installed and runs the installation steps for colab...

**@adamgayoso:** Done.

```
!pip install --quiet scvi-colab
from scvi_colab import install
install()
```

This will install scvi-tools for you in google colab. We will update all the tutorials in a patch release to reflect this.

**@DRSEI:** hi @adamgayoso  I am still getting the same error even through I have follow your suggestion.

%%capture
import sys

#if branch is stable, will install via pypi, else will install from source
branch = "stable"
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB and branch == "stable":
    !pip install scvi-tools==0.15.1
    !pip install pyro-ppl==1.8.0
    !pip install --quiet git+https://github.com/theislab/scib.git
elif IN_COLAB and branch != "stable":
    !pip install --quiet --upgrade jsonschema



ImportError                               Traceback (most recent call last)
[<ipython-input-28-22222d567b66>](https://localhost:8080/#) in <module>()
      5 import scanpy as sc
      6 import scib
----> 7 import scvi
      8 sc.set_figure_params(figsize=(4, 4)) …

**@adamgayoso:** @DRSEI please check the tutorials again in a few minutes

**@DRSEI:** Thank you @adamgayoso

**@bigtimecodersean:** I am running into the exact same problem as DRSEI describes above:
Running:


%%capture
import sys

#if branch is stable, will install via pypi, else will install from source
branch = "stable"
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB and branch == "stable":
    !pip install --quiet scvi-tools[tutorials]
elif IN_COLAB and branch != "stable":
    !pip install --quiet --upgrade jsonschema
    !pip install --quiet git+https://github.com/yoseflab/scvi-tools@$branch#egg=scvi-tools[tutorials]

!pip install --quiet scvi-colab
from scvi_colab import install
install()

gives me the following error:

ImportError: /usr/local/lib/python3.7/dist-packages/torchtext/_torchtext.so: undefined symbol: _ZNK3c104Type14isSubtypeOfExtERKSt10shared_ptrIS0_EPSo


Any ideas …

**@rangan2510:** Check the previous comments, a workaround has been proposed.

Get Outlook for Android<https://aka.ms/AAb9ysg>
________________________________
From: bigtimecodersean ***@***.***>
Sent: Tuesday, March 29, 2022 9:22:50 AM
To: scverse/scvi-tools ***@***.***>
Cc: Rangan Das ***@***.***>; Comment ***@***.***>
Subject: Re: [scverse/scvi-tools] Importerror for scVI in tutorials (Issue #1464)


I am running into the exact same problem as DRSEI describes above:
Running:

%%capture
import sys

#if branch is stable, will install via pypi, else will install from source
branch = "stable"
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB and branch == "stable":
!pip install --quiet scvi-tools[tutorials]
elif IN_COLAB and branch != "stable":
!pip install --quiet --upgrade jsonschema
!pip install --qu …

**@bigtimecodersean:** @rangan2510  I believe I am using the proposed workaround:

!pip install --quiet scvi-colab
from scvi_colab import install
install()

But I still get the import error?

**@rangan2510:** >

For me, this worked on Kaggle. You may try it out.
`!pip install scvi-tools==0.15.1 pyro-ppl==1.8.0 umap-learn scanpy scikit-misc leidenalg --quiet`

**@bigtimecodersean:** Thanks, I successfully ran the above ^:
!pip install scvi-tools==0.15.1 pyro-ppl==1.8.0 umap-learn scanpy scikit-misc leidenalg --quiet

However the following:


import scvi
import scanpy as sc
import matplotlib.pyplot as plt

sc.set_figure_params(figsize=(4, 4))

# for white background of figures (only for docs rendering)
%config InlineBackend.print_figure_kwargs={'facecolor' : "w"}
%config InlineBackend.figure_format='retina'

As well as:

!pip install --quiet scvi-colab
from scvi_colab import install
install()

Both give me the import error.

I am thinking it might have something to do with a PyTorch dependency?

<img width="1275" alt="Screenshot 2022-03-28 at 21 07 11" src="https://user-images.githubusercontent.com/85389086/160531227-d2dc74bf-a366-4218-8 …

**@rangan2510:** @bigtimecodersean I believe it's something else. I am sharing a link to a notebook I have on Colab and it works fine. Did a !pip freeze so you can check the versions: [scVI import.ipynb](https://colab.research.google.com/drive/1vpMcsE2NiIEonKePZOeJe03lnRNEJ5tn?usp=sharing)

**@bigtimecodersean:** @rangan2510 Thanks for the help. I just ran your code line by line and got the exact same import error on the:

"import scvi" line in your second block. Bizarre

**@bigtimecodersean:** Starting a new notebook solved the problem with your solution @rangan2510 Thank you so much!!!

**@adamgayoso:** @bigtimecodersean

```
%%capture
import sys

#if branch is stable, will install via pypi, else will install from source
branch = "stable"
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB and branch == "stable":
!pip install --quiet scvi-tools[tutorials]
elif IN_COLAB and branch != "stable":
!pip install --quiet --upgrade jsonschema
!pip install --quiet git+[https://github.com/yoseflab/scvi-tools@$branch#egg=scvi-tools[tutorials]](https://github.com/yoseflab/scvi-tools@$branch#egg=scvi-tools%5Btutorials%5D)

!pip install --quiet scvi-colab
from scvi_colab import install
install()
```

should instead only be

```
!pip install --quiet scvi-colab
from scvi_colab import install
install()
```

I don't believe this new code will work in kaggle unless you run it …

**@rangan2510:** Do a pip freeze and cross-check the versions once.

Get Outlook for Android<https://aka.ms/AAb9ysg>
________________________________
From: bigtimecodersean ***@***.***>
Sent: Tuesday, March 29, 2022 9:50:27 AM
To: scverse/scvi-tools ***@***.***>
Cc: Rangan Das ***@***.***>; Mention ***@***.***>
Subject: Re: [scverse/scvi-tools] Importerror for scVI in tutorials (Issue #1464)


@rangan2510<https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2Frangan2510&data=04%7C01%7C%7Cc9c652d6f7774358ea0f08da113b7495%7C84df9e7fe9f640afb435aaaaaaaaaaaa%7C1%7C0%7C637841244295175513%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000&sdata=hmdO2tW5yVUCez7Tb6yjKeqjjU2qzy8sVFe22XAmpAI%3D&reserved=0> Thanks for the help. I just ran your cod …

**@michaelmather15:** Hi. I am hoping to ask a question related to the above point please. I had scVI working fine in Colab a few months ago but when I have come back to it today, when I run
```
!pip install --quiet scvi-colab
from scvi_colab import install
install()
```
I get the following message:

> INFO     scvi-colab: Installing scvi-tools.
> INFO     scvi-colab: Install successful. Testing import.
> ---------------------------------------------------------------------------
> AssertionError                            Traceback (most recent call last)
> [<ipython-input-4-87955b66e060>](https://kk2ywy4psum-496ff2e9c6d22116-0-colab.googleusercontent.com/outputframe.h …

## #2327: Release scvi-tools 1.1.0-rc.1
**Issue:** #2327 | **Last activity:** 2023-12-18T18:28:16Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-11-22 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2327

-   [x] Bump version in `pyproject.toml`. #2358
-   [x] If patch release, backport version bump PR into the appropriate branch. Else, create a new branch off `main` with the appropriate rules. https://github.com/scverse/scvi-tools/tree/1.1.x
-   [x] Create a new GitHub draft release targeting the release branch with the same body as the previous release (don't release yet). https://github.com/scverse/scvi-tools/releases/tag/untagged-ae349b909e1ef23aba36
-   [x] Trigger a Docker image build in [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker) targeting the release branch. https://github.com/YosefLab/scvi-tools-docker/actions/runs/7119951398
-   [x] After image builds and pushes to the registry, run the [tutorials](https://github.com/scverse/scvi-tutorials) using the new image. https://github.com/scverse/scvi-tutorials/issues/209
-   [x] Publish a new release on the tutorials repo off `main` after all tutorials changes have been merged. https://github.com/scverse/scvi-tutorials/releases/tag/1.1.0rc1
-   [x] Create a new branch off `main` in the main repo and run `git submodule update --remote`, and then merge the PR, with an appropriate backport as needed. #2356 #2357
-   [x] Double check everything and then publish the release on the main repo. https://github.com/scverse/scvi-tools/releases/tag/1.1.0rc1
-   [ ] Check that the [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock) updates correctly.
-   [x] Check that the version upd …

## #2372: PyMDE seed fixation suggestion
**Issue:** #2372 | **Last activity:** 2023-12-18T18:27:13Z
**State:** closed | **Author:** @seyoon-lee | **Comments:** 1 | **Created:** 2023-12-18 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2372

Hello,

I've been trying out different dimension reduction methods mostly for visualization purpose.
scvi.model.utils.mde seems to be a very interesting and useful feature added in the ecosystem, but I realized while I was playing around few parameters like neighbors and repulsive_fraction that the random seed is not fixed nor it could be fixed with a global seed in my script.
Could we just add a quick feature like scvi.model.utils.mde(seed=42) and add the pymde.seed(seed) calling right around there?

in _mde.py
 ```
    try:
         import pymde
         pymde.seed(seed)
```

Thank you for all your work!
Seyoon

**@martinkim0:** Thanks for the suggestion, we can definitely add this as part of the next release!

## #2198: Pretrained scvi-tools Hugging Face models mismatches
**Issue:** #2198 | **Last activity:** 2023-12-15T04:10:04Z
**State:** closed | **Author:** @juliebehr | **Comments:** 3 | **Created:** 2023-07-21 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2198

<!-- Describe the bug -->

Hi! I am trying to use the incredibly helpful pretrained models at [huggingface.co/scvi-tools](https://huggingface.co/scvi-tools), but have found there to be many mismatches between the model name and the actual uploaded models. For instance, `scvi-tools/tabula-sapiens-vasculature-scanvi` loads the `scvi-tools/tabula-sapiens-trachea-scanvi` model. This issue is based on the models on the hub last updated March 24, 2023.

<!-- To reproduce -->

```python
import scvi
from scvi.hub import HubModel

## Attempting to load the vasculature model
ref_model = "scvi-tools/tabula-sapiens-vasculature-scanvi"
hubmodel = HubModel.pull_from_huggingface_hub(ref_model)
hubmodel.adata.obs

```
returns:
```pytb
                                                   tissue_in_publication donor_id       free_annotation  compartment cell_type_ontology_term_id  ... assay_correct      donor_assay _scvi_batch _scvi_labels _scanvi_observed_lib_size
cell_id                                                                                                                                          ...
AAACCCAGTTCTCCAC_TSP6_Trachea_NA_10X_1_1                         Trachea     TSP6            macrophage       immune                 CL:0000235  ...     10x 3' v3   TSP6_10x 3' v3           0            9                       0.0
AAACGCTGTAGAATGT_TSP6_Trachea_NA_10X_1_1 …

**@martinkim0:** Hi, thanks for raising this issue, I'll take a look at it ASAP.

**@canergen:** @martinkim0 Is this one fixed?

**@canergen:** Fixed now in my hands.

## #2335: Possible mistake in error formating - `scvi.data.fields._layer`
**Issue:** #2335 | **Last activity:** 2023-12-13T00:58:30Z
**State:** closed | **Author:** @yotamcons | **Comments:** 3 | **Created:** 2023-11-23 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2335

<!-- Describe the bug -->

I have a model trained on 5k hvgs, and i tried to load it with the full Anndata object. The error text replaces the input and output


<!-- To reproduce -->

```python
model_dir = test
scvi.model.SCVI.setup_anndata(adata[:, adata.var.highly_variable].copy())
vae = scvi.model.SCVI(adata[:, adata.var.highly_variable].copy())
vae.save(model_dir, overwrite=True)
vae = scvi.model.SCVI.load(model_dir, adata=adata)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb
File conda/envs/pp_t/lib/python3.9/site-packages/scvi/data/fields/_layer_field.py:116, in LayerField.transfer_field(self, state_registry, adata_target, **kwargs)
    114 target_n_vars = adata_target.n_vars
    115 if target_n_vars != n_vars:
--> 116     raise ValueError(
    117         "Number of vars in adata_target not the same as source. "
    118         + f"Expected: {target_n_vars} Received: {n_vars}"
    119     )
    121 return self.register_field(adata_target)

ValueError: Number of vars in adata_target not the same as source. Expected: 16964 Received: 5000
```

#### Versions:

<!-- Output of scvi.__version__ -->

> VERSION '1.0.4'

<!-- Relevant screenshots -->

**@canergen:** The problem is how you instantiate the model with 'adata[:, adata.var.highly_variable].copy()'
Please create a copy of your anndata as bdata and load the model using the subset object. We don't modify datasets during model load.

**@yotamcons:** I think @canergen you did not understand my issue at all, the problem is the error message i got, not that i got the error

**@martinkim0:** Hey so sorry, you're right, the error message is formatted incorrectly. I'll get this fixed!

## #2355: multi-GPU support?
**Issue:** #2355 | **Last activity:** 2023-12-08T20:08:14Z
**State:** closed | **Author:** @zhenxingjian | **Comments:** 4 | **Created:** 2023-12-07 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2355

I would like to ask if we're supporting multi-GPU training now?
I'm testing the scvi version 1.0.4.
Shall I try 1.1.x?

**@zhenxingjian:** I've changed the devices=-1 (from lightning.pytorch, this means to use all GPU)
I got the following messages:

2023-12-07 12:20:22.818922 -- 0
An NVIDIA GPU may be present on this machine, but a CUDA-enabled jaxlib is not installed. Falling back to cpu.
GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
Initializing distributed: GLOBAL_RANK: 0, MEMBER: 1/2
/miniconda3/envs/scvi_latest/lib/python3.10/site-packages/scvi/_settings.py:63: UserWarning: Since v1.0.0, scvi-tools no longer uses a random seed by default. Run `scvi.settings.seed = 0` to reproduce results from previous versions.
  self.seed = seed
/miniconda3/envs/scvi_latest/lib/python3.10/site-packages/scvi/_settings.py: …

**@martinkim0:** Hi, multi-GPU training is not available in 1.0.4 but will be in 1.1.0, so please hold tight! We'll be releasing a release candidate soon for it. Feel free to also install from main and try it out.

**@zhenxingjian:** > Hi, multi-GPU training is not available in 1.0.4 but will be in 1.1.0, so please hold tight! We'll be releasing a release candidate soon for it. Feel free to also install from main and try it out.

Hi Martin,

I've tried the scvi==1.1.0 (built from main), but I got the same error.
All GPUs shows 100% GPU-Util but not training at all.

2023-12-08 11:07:59.989550 -- 0
GPU available: True (cuda), used: True
TPU available: False, using: 0 TPU cores
IPU available: False, using: 0 IPUs
HPU available: False, using: 0 HPUs
Initializing distributed: GLOBAL_RANK: 0, MEMBER: 1/2
2023-12-08 11:08:42.294553 -- 0
Initializing distributed: GLOBAL_RANK: 1, MEMBER: 2/2
----------------------------------------------------------------------------------------------------
distributed_backend= …

**@zhenxingjian:** > > Hi, multi-GPU training is not available in 1.0.4 but will be in 1.1.0, so please hold tight! We'll be releasing a release candidate soon for it. Feel free to also install from main and try it out.
>
> Hi Martin,
>
> I've tried the scvi==1.1.0 (built from main), but I got the same error. All GPUs shows 100% GPU-Util but not training at all.
>
> ## 2023-12-08 11:07:59.989550 -- 0
> GPU available: True (cuda), used: True
> TPU available: False, using: 0 TPU cores
> IPU available: False, using: 0 IPUs
> HPU available: False, using: 0 HPUs
> Initializing distributed: GLOBAL_RANK: 0, MEMBER: 1/2
> 2023-12-08 11:08:42.294553 -- 0
> Initializing distributed: GLOBAL_RANK: 1, MEMBER: 2/2
> ## distributed_backend=nccl
> All distributed processes registered. Starting with 2 proce …

## #2363: POISSONVI Availability
**Issue:** #2363 | **Last activity:** 2023-12-08T18:35:03Z
**State:** closed | **Author:** @shahrozeabbas | **Comments:** 2 | **Created:** 2023-12-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2363

Hello - quick question,

I am trying to use `POISSONVI` using the `external` module from `scvi`. I am using version 1.0.4 which I believe is the latest but it seems to not be available. Am I missing something?

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: module 'scvi.external' has no attribute 'POISSONVI'
```

Versions Check:

```
scvi.__version__
'1.0.4'
```

Thanks.

**@martinkim0:** Hi, PoissonVI will be available starting with scvi-tools 1.1.0. We have a pre-release available as of yesterday (1.1.0rc1) which you can install via (`pip install --pre scvi-tools`).

**@shahrozeabbas:** ahh that makes sense, thank you for clearing that up. I will take a look at the pre-release.

## #2253: Long (never ending???) runtime of scvi.model.SCVI.differential_expression with "weights = 'importance'"
**Issue:** #2253 | **Last activity:** 2023-12-08T05:54:47Z
**State:** closed | **Author:** @MaximilianNuber | **Comments:** 2 | **Created:** 2023-08-31 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2253

<!-- Describe the bug -->

Hello everyone,

Thanks for the great tool, scvi has become my bread and butter.

I would like to ask about the option "weights = 'importance'" in the differential expression method of scvi.

I set up the model training just like I described here: #2236
However, I went further to test for differential genes.

Whenever weights = "uniform", I get my results within a few minutes.
For weights = "importance", I let the function run for around 4 hours, and less for a few times, but it never terminated successfully.
As compared to the successful run, the only thing I changed was weights = "uniform" to weights = "importance.
Again, I tried to follow the C.elegans tutorial with my own data.


Is there something I am doing wrong, or is the runtime expected?


Thank you for any help

<!-- To reproduce -->

```python

# continued after my previous post #2236

cell_idx1 = adata.obs["cell type"] == "ct_1"
print(sum(cell_idx1), "cells of type", "ct_1")

cell_idx2 = adata.obs["cell type"] == "ct_2"
print(sum(cell_idx2), "cells of type", "ct_2")


# simple example from the tutorial

de_change = model.differential_expression(idx1=cell_idx1, idx2=cell_idx2)
de_change

# uniform weights is successful
de_change_uniform = model.differential_expression(
    idx1=cell_idx1,  # we use the same cells as chosen before
    idx2=cell_idx2,
    weights="uniform",
    batch_correction=True,
)

# importance-weights runs forever

d …

**@canergen:** Hi @MaximilianNuber, how much RAM is used? Is the CPU/GPU busy? It could be that it's caching and this leads to the slowdown but it's very hard to tell from the provided information.

**@canergen:** Closed due to inactivity

## #2238: CUDA memory error in lvm-DE
**Issue:** #2238 | **Last activity:** 2023-12-08T05:53:22Z
**State:** closed | **Author:** @joseph-siefert | **Comments:** 4 | **Created:** 2023-08-14 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2238

<!-- Describe the bug -->

I can run `differential_expression()` with `weights="uniform"` without issue. However, if i try to run lvm-DE by setting `weights="importance"` I get a CUDA memory error. I get the same error whether `batch_correction` is True or False, and whether `filter_outlier_cells` is True or False. The dataset is 70,000 cells by 36,600 genes. I can run much larger datasets with `weights="uniform"` without any errors.

<!-- To reproduce -->

```
de_df = scVI_model.differential_expression(
    groupby = "stage",
    idx1=idx1,
    idx2=idx2,
    batch_correction = True,
    weights="importance",
    filter_outlier_cells = True
)
```

<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```
DE...:   0%|          | 0/1 [01:09<?, ?it/s]
---------------------------------------------------------------------------
OutOfMemoryError                          Traceback (most recent call last)
Cell In[25], line 2
      1 #perform differential expression from scVI model
----> 2 de_df = scVI_model.differential_expression(
      3     groupby = "stage",
      4     idx1=idx1,
      5     idx2=idx2,
      6     batch_correction = True,
      7     weights="importance",
      8     filter_outlier_cells = True
      9 )
     10 de_df.head()

File /mambaforge/envs/scanpy/lib/python3.9/site-packages/scvi/model/base/_rnamixin.py:377, in RNASeqMixin.differential_expression(self, adata, groupby, group1, gr …

**@martinkim0:** Hi, could you try rerunning this after freeing up some CUDA memory? That seems to be the main issue here. What is the size of your dataset?

**@joseph-siefert:** Yes, I have run after restarting kernel, loading only the dataset and model, and removing the dataset and freeing up memory. As I mentioned, the dataset is 70,000 cells by 36,600 genes, but I can easily run much larger datasets (>1M cells) when `weights="uniform"`

**@martinkim0:** cc @PierreBoyeau would you be able to look into this?

**@canergen:** @martinkim0: As we discussed it today based on our code either anchor_cells (max_cells) is to high. I don't think so with 1024 cells and I would not reduce this as it can have bad side-effects. It's completely fine though to lower `n_mc_samples_per_pass`. Memory usage should scale linearly with reducing it. As far as I can tell, it's not exposed though. Can you expose it? And best case catch the OOM and suggest lowering this value. The issue here is that we usually do highly_variable_gene filtering prior to training the model. Here the DE function is executed on all 36k genes. The number of cells doesn't matter for memory usage. https://github.com/scverse/scvi-tools/blob/0731833a548a8b91fcf9c47c9d7a972716c0d92d/scvi/model/base/_rnamixin.py#L50C9-L50C42

Edit: It's exposed in main

## #2336: Unable to change gene_likelihood in scvi.model.SCVI.setup_anndata
**Issue:** #2336 | **Last activity:** 2023-11-24T17:40:14Z
**State:** closed | **Author:** @gamabunta313 | **Comments:** 1 | **Created:** 2023-11-24 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2336

<!-- Unable to change gene_likelihood in scvi.model.SCVI.setup_anndata -->

[I am using scvi in google colab to integrate different scRNA datasets.
I successfully installed scvi-colab (v. 1.0.4). I also installed scvi in local (v. 1.0.4)
When I am trying to make data setup (scvi.model.SCVI.setup_anndata(adata, layer = "counts", batch_key="Source") ) I am unable to set any gene_likelihood ('zimb','nb',poisson')]

<!-- To reproduce -->

```python
# adata=import_adata
summary=pd.read_csv
adata.layers['counts']=adata.X.toarray()
max_epochs_scvi = np.min([round((20000 / adata.n_obs) * 400), 400])

scvi.model.SCVI.setup_anndata(adata, layer = "counts", batch_key="Source", gene_likelihood='nb')

```

<!-- NameError  -->

```pytb
TypeError                                 Traceback (most recent call last)
[<ipython-input-26-ed94d36b577a>](https://localhost:8080/#) in <cell line: 1>()
----> 1 scvi.model.SCVI.setup_anndata(adata, layer = "counts", batch_key="Source", gene_likelihood='nb')

1 frames
[/usr/local/lib/python3.10/dist-packages/scvi/data/_manager.py](https://localhost:8080/#) in register_fields(self, adata, source_registry, **transfer_kwargs)
    172
    173         if source_registry is None and transfer_kwargs:
--> 174             raise TypeError(
    175                 f"register_fields() got unexpected keyword arguments {transfer_kwargs} passed without a source_registry."
    176             )

TypeError: register_fields() got unexpected …

**@canergen:** Hi. It's not an argument to setup_anndata but to the next model class(one step further in tutorials). https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.SCVI.html

## #1167: LDA Incremental Updates
**Issue:** #1167 | **Last activity:** 2023-11-23T02:33:19Z
**State:** closed | **Author:** @justjhong | **Comments:** 1 | **Created:** 2021-09-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1167

WIth the addition of AmortizedLDA, we would like to make incremental updates to improve the model. This issue will serve as the parent issue for a bunch of small features we would like add to the LDA model.

- [x] Tutorial for LDA #1195
- [x] User Guide for Amortized LDA #1178
- [ ] Automated selection of n_topics
- [ ] Non-amortized LDA model
- [ ] prodLDA flavor of LDA
- [ ] correlated topic model
- [ ] Integrate with enrichR or expose an API for enrichment analysis of LDA topics

**@adamgayoso:** Also if the normal prior has a full covariance matrix it becomes the correlated topic model...

## #661: add random state functionality
**Issue:** #661 | **Last activity:** 2023-11-23T02:32:39Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2020-04-26 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/661

There should be a straightforward way to add a random state functionality to scVI with minimal code duplication. This will be helpful in ensuring posterior predictive quantities and de, etc are reproducible with respect to any given trained model.

```python
In [34]: g_cpu = torch.Generator()
    ...: g_cpu.manual_seed(2147483647)
Out[34]: <torch._C.Generator at 0x13ce7db30>

In [36]: torch.normal(torch.tensor(0.), torch.tensor(1.), generator=g_cpu)
Out[36]: tensor(-0.9800)

In [38]: g_cpu = torch.Generator()
    ...: g_cpu.manual_seed(2147483647)
Out[38]: <torch._C.Generator at 0x13ce7df30>

In [39]: torch.normal(torch.tensor(0.), torch.tensor(1.), generator=g_cpu)
Out[39]: tensor(-0.9800)
```

## #1185: Implement scHPF
**Issue:** #1185 | **Last activity:** 2023-11-23T02:32:09Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 3 | **Created:** 2021-09-29 | **Labels:** new model | **URL:** https://github.com/scverse/scvi-tools/issues/1185

Proposal to implement scHPF.

1. Code: https://github.com/simslab/scHPF
2. Paper: https://www.embopress.org/doi/full/10.15252/msb.20188557

Level of difficulty: Intermediate/advanced. Probably best to use Pyro for this one.

**@vitkl:** I translated this model to pymc3 at some point. It was fairly straightforward because the model does not have that many variables (just 4 if I remember correctly). In the original implementation, they use various tricks to set priors based on data. If I remember correctly, they do full data training. The original implementation doesn't account for batch effects in any way so not straightforward to apply to many datasets. I would be interested to see how well it works in pyro with VI (compared to EM) both when training on full data, in mini-batches and using amortised inference. Cell2location repo defines a useful class (https://github.com/BayraktarLab/cell2location/blob/master/cell2location/distributions/AutoNormalEncoder.py) for doing amortisation with a convenient interface (https://gith …

**@adamgayoso:** @vitkl the advantage of their implementation which we can't match is that they can handle data in sparse format because a lot of the actual computation can be amortized for 0 counts. So I don't expect we would be faster than their implementation.  Even if we could, their closed form VI updates are likely to outperform BBVI in pyro.

But that said, we could offer amortized inference (encoder), and even extend it to handle batch effects. I intended the initial implementation of this to be an exercise for @watiss. I anticipate we will have something before end of January.

**@vitkl:** I see. I would be quite curious to see how it works. I wish there was more work explicitly comparing pyro/VI/amortized inference to closed-form updates - to help decide how much worse exactly amortized inference is in comparison and when it is worth investing in deriving closed-form VI updates (+sticking to simpler models where that can be done).

## #1184: Implement Prescient
**Issue:** #1184 | **Last activity:** 2023-11-23T02:31:32Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 3 | **Created:** 2021-09-29 | **Labels:** help wanted, new model | **URL:** https://github.com/scverse/scvi-tools/issues/1184

Proposal to implement Prescient.

1. Code: https://github.com/gifford-lab/prescient
2. Paper: https://www.nature.com/articles/s41467-021-23518-w

Level of difficulty: Intermediate, the model is already written with PyTorch. A custom training plan is probably necessary.

**@PierreBoyeau:** In addition to having the model, I think this is an opportunity to use cases of exotic data handling approaches.
Do you think we should get in touch with their lab?

**@adamgayoso:** Yes I think it's a good stress test. Would be great if you contacted them.

**@PierreBoyeau:** Ok let me contact them, I'll cc-you!

## #1293: Implement VITAE
**Issue:** #1293 | **Last activity:** 2023-11-23T02:31:08Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2021-12-17 | **Labels:** enhancement, help wanted, new model | **URL:** https://github.com/scverse/scvi-tools/issues/1293

https://www.biorxiv.org/content/10.1101/2020.12.26.424452v1

## #2294: scvi.settings.seed cannot generate same UMAP embeddings.
**Issue:** #2294 | **Last activity:** 2023-11-23T02:27:50Z
**State:** closed | **Author:** @Lijunyao8 | **Comments:** 5 | **Created:** 2023-10-16 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2294

I cannot generate the same UMAP embeddings even if I set seed. I used max_epochs=150, which should be enough given train_loss_step is at 130.

```
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
           max_epochs=150,
           early_stopping_monitor = 'elbo_validation',
           plan_kwargs={"n_epochs_kl_warmup":25}
           )
```

Out put
Epoch 100/100: 100%|██████████| 100/100 [10:11<00:00,  6.11s/it, v_num=1, train_loss_step=130, train_loss_epoch=127]

**@martinkim0:** Hi, could you check whether running scVI twice with the same seed gives the same latent representation? If it does, then it is likely a seed issue with Scanpy.

**@canergen:** Can you also provide the UMAP line of code and just compare the latent code you are receiving. E.g. RAPIDS has reproducibility problems.

**@Lijunyao8:** Hi, how to check if I have the same latent representation? Also, do you think the max_epoches parameter matters? how should I adjust that?

```
t_adata.obsm["X_scVI"] = vae.get_latent_representation()
t_adata.layers["normalized_scVI"] = vae.get_normalized_expression(library_size=10e4)

sc.pp.neighbors(t_adata, use_rep="X_scVI")
sc.tl.leiden(t_adata, key_added=("leiden_scVI_" + str(subcluster_res)), resolution=subcluster_res)
sc.tl.umap(t_adata)
```

**@martinkim0:** `max_epochs` matters a lot for the final model performance. Since you're using early stopping based on the ELBO validation and early stopping is not triggered prior to `max_epochs=150` in your run, I would recommend setting it to a larger value and seeing if it terminates early then, maybe something like `max_epochs=300`. Ideally you also check `model.history["elbo_validation"]` and seeing whether the model converges.

You can check that the latent representation is the same between different model runs by saving the array and then using something like `numpy.array_equal`. With the same `scvi.setting.seed`, the models should be the same, but I would double check.

**@martinkim0:** Closing due to inactivity

## #2266: Load model don't use the GPU
**Issue:** #2266 | **Last activity:** 2023-11-23T02:26:24Z
**State:** closed | **Author:** @Quentin-bioinfo | **Comments:** 2 | **Created:** 2023-09-18 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2266

I use scvi tools 1.0.3 in a conda env.

When i use the command :

```
scvi.model.SCVI.setup_anndata(RRSO_data, layer = "counts",
                             categorical_covariate_keys=["sample"],
                             continuous_covariate_keys=['pct_counts_mt', 'total_counts'])

```
it says that there is no gpu but finally when i use:

`model.train()`

it says
`GPU available: True (cuda), used: True`


But then after saving it with `model.save(dir_path)`, when i try to load it with

`model = scvi.model.SCVI.load(dir_path, adata) `

it says no gpu and take a very long time to load it, it's acctually longer than created the model...

Any idea of the issue and what i can do ?

I already try to add the option `accelarator = 'gpu' ` but it doesn't change anything

**@martinkim0:** Hi, can you try loading the model onto CPU first and then moving it to GPU to see if that changes anything?

**@martinkim0:** Closing due to inactivity

## #1590: Error when updating format
**Issue:** #1590 | **Last activity:** 2023-11-22T12:49:09Z
**State:** closed | **Author:** @ccruizm | **Comments:** 5 | **Created:** 2022-07-02 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/1590

Good day,

I am trying to update a model I created with an older version of scvi `scvi.model.SCVI.convert_legacy_save('./results/reference_signatures/', './results/eference_signatures_updated/')` but get the error below:
```
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
Input In [12], in <cell line: 1>()
----> 1 scvi.model.SCVI.convert_legacy_save('./results/gbm_all_cell2location_gbmverse/reference_signatures/',
      2                          './results/gbm_all_cell2location_gbmverse/reference_signatures_updated/')

File ~/miniconda3/envs/cell2loc_env/lib/python3.9/site-packages/scvi/model/base/_base_model.py:673, in BaseModelClass.convert_legacy_save(cls, dir_path, output_dir_path, overwrite, prefix)
    671     unlabeled_category_key = "unlabeled_category_"
    672     unlabeled_category = attr_dict.get(unlabeled_category_key, None)
--> 673     attr_dict["registry_"] = registry_from_setup_dict(
    674         cls,
    675         scvi_setup_dict,
    676         unlabeled_category=unlabeled_category,
    677     )
    679 model_save_path = os.path.join(output_dir_path, f"{file_name_prefix}model.pt")
    680 torch.save(
    681     dict(
    682         model_state_dict=model_state_dict,
   (...)
    686     model_save_path,
    687 )

File ~/miniconda3/envs/cell2loc_env/lib/python3.9/site-packages/scvi/data/_compat.py:130, in registry_from_ …

**@adamgayoso:** Was the original model an SCVI model? Or was it e.g., stereoscope, etc.

**@ccruizm:** Sorry forgot to mention, it was a model generated using cell2location

**@ccruizm:** I am trying now to generate the model again with the new version but once I reach `scvi.data.setup_anndata` I get the error below:
```
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Input In [22], in <cell line: 2>()
      1 # prepare anndata for the regression model
----> 2 scvi.data.setup_anndata(adata=adata_ref,
      3                         # 10X reaction / sample / batch
      4                         batch_key='author',
      5                         # cell type, covariate used for constructing signatures
      6                         labels_key='cell_type',
      7                         # multiplicative technical effects (platform, 3' vs 5', donor effect) …

**@adamgayoso:** was this resolved?

**@martinkim0:** Closing due to inactivity

## #1780: Implement batch effect normalization
**Issue:** #1780 | **Last activity:** 2023-11-22T12:48:35Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2022-11-07 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1780

It would be interesting to see if [batch effect normalization](https://www.biorxiv.org/content/10.1101/2022.10.14.512286v1) can also improve batch correction in scVI.

This would involve implementing an experimental batch-aware AnnData loader that ensures individual training batches only consist of observations coming from one experimental batch.

## #1926: Implement PoissonVI to model scATAC-seq fragment counts
**Issue:** #1926 | **Last activity:** 2023-11-22T12:34:03Z
**State:** closed | **Author:** @lauradmartens | **Comments:** 15 | **Created:** 2023-02-23 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1926

**Is your feature request related to a problem? Please describe.**
PeakVI currently only supports modelling of binarized scATAC-seq data. In our [preprint](https://www.biorxiv.org/content/10.1101/2022.05.04.490536v1), we showed that it can be beneficial to actually model the scATAC-seq fragment counts.

**Describe the solution you'd like**
As previously discussed with @adamgayoso, it would be good to add the PoissonVI model to scvi, that users can also model the fragment count data.

**@adamgayoso:** Hi @lauradmartens, can you please describe again the difference between scVI with a poisson likelihood and the poissonVI model?

**@lauradmartens:** Hi Adam!

The model itself is similar but with some changes:
* AnnData setup checks that users input fragment counts and not binarized counts or read counts
* Function `reads_to_fragments` to approximately convert read counts to fragment counts
* Default architecture (number of layers etc.) and training procedure (learning rate etc.) is the one of PeakVI for ATAC data
* Function names as in PeakVI and adapted to ATAC terminology `get_accessibility_estimates`, `differential_accessibility`
* Possibility to output an accessibility probability from the Poisson rate parameter estimations in `get_accessibility_estimates`
*  And lastly but I have not implemented this yet, it might be interesting to exclude the region-specific bias (bias in the last layer) from the normalized accessibility …

**@marianogabitto:** Laura,
      I have already implemented but never push the commit. Let me know what you want to do about this.

Mariano

**@lauradmartens:** Hi Mariano,

Cool to hear that! Sure, if this makes things easier! I am happy to help with input and documentation.

**@adamgayoso:** I need to think more about it, but perhaps we can add the poisson functionality directly into PeakVI, and then have the option to create a PoissonPeakVI model that just inherits peakvi and sets poisson to true.

The second part would increase expose for people to cite your publication, but isn't strictly necesary code wise

**@lauradmartens:** Thanks Adam! In this case, I think I would prefer the second option.

**@marianogabitto:** In my code, I included in MultiVI. To be sincere, I did not see a major difference compared to PeakVI. A couple of thoughts (caveat, I read the paper and implemented a while ago so I might be wrong in my comments):
- Laura, can you paste the code to preprocess the reads before analysis?, I remember something about multiplying by 2 or dividing by 2 the number of reads per cell per peak.
- The poisson likelihood is cool because it has a normalized mean expression, independent from library size (like scvi). However, I remember that your implementation does not allow you to separate the regions factor from the mean expression. can you comment about this? (Basically, I am saying that to be able to get the normalized mean expression you need to correct for the region-specific factor)

**@lauradmartens:** Yes, correct. As Adam said, the PoissonPeakVI would be for citation reasons. The main difference are in the decoder, the conversion step that you mention and the normalized accessibility.

> * Laura, can you paste the code to preprocess the reads before analysis? I remember something about multiplying by 2 or dividing by 2 the number of reads per cell per peak.

In my pull request (#1927, I tagged you), I implemented the conversion code and also I check in setup_anndata that users don't provide the read counts or binarized data. Of course, this conversion is an approximation of the real number of fragments ber peak and ideally, users would count fragments in their preprocessing pipeline but for 10x read count matrices, this approximation works well and is very similar to actually coun …

**@adamgayoso:** I think to get things started it might be easier to work in pieces.

@lauradmartens would you be able to make a PR into `scvi.data` to add the reads to fragments as a preprocessing function?

https://github.com/scverse/scvi-tools/pull/1927#discussion_r1120435473

This can live in the `_preprocessing.py` file.

After that I just want to better understand how exactly your poisson model is written. It's my understanding that running scvi.model.SCVI with poisson likelihood is the same generative model as what you proposed, perhaps with a different architecture because peakvi uses different activation, number of units etc.

**@marianogabitto:** Adam,
        there are simple things to do like modifying the _preprocessing.py file or making PeakVI chose between the Binary and the Poisson likelihood (I have done this actually). Should I start a new pull request with the data processing part alone? (tackling one issue at the time?

<

**@adamgayoso:** I would first want to see if @lauradmartens would like to contribute this PR. Either way we should make it clear in that docstring that the procedure comes from the poisson vi paper

**@lauradmartens:** Hi Adam, hi Mariano, sorry for not getting back earlier. I added the preprocessing function as you suggested @adamgayoso. As mentioned before I also wrote a function to check that the `anndata` object does actually contain read counts (more even than uneven counts) and non-binarized data. Should that also go in the preprocessing function?

**@adamgayoso:** thanks @lauradmartens I don't think that should go into the preprocessing function.

Ideally we would subclass our `LayerField` object to add a validation check for this. But let me keep thinking about this

**@lauradmartens:** Hi, I wanted to revive this conversation because the PoissonVAE paper has now been accepted and it would be nice to refer to scvi for the model. @adamgayoso, could you tell me what is missing to include it in PeakVI? Would be happy to include it in the next PR.

**@martinkim0:** Hi @lauradmartens, Adam graduated from the lab recently and is thus no longer actively developing scvi-tools. I'd be happy to help out with getting the model into the codebase. For now, I think it makes sense to implement a new model class under `scvi.external` that inherits from `PeakVI` and adds the necessary changes. I can provide more feedback once there's a PR.

## #2324: Release scvi-tools 1.1
**Issue:** #2324 | **Last activity:** 2023-11-22T05:50:28Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-11-22 | **Labels:** releases | **URL:** https://github.com/scverse/scvi-tools/issues/2324

-   [ ] Bump version in `pyproject.toml`.
-   [ ] If patch release, backport version bump PR into the appropriate branch.
        Else, create a new branch off `main` with the appropriate rules.
-   [ ] Create a new GitHub draft release targeting the release branch with the
        same body as the previous release (don't release yet).
-   [ ] Trigger a Docker image build in
        [`scvi-tools-docker`](https://github.com/YosefLab/scvi-tools-docker)
        targeting the release branch.
-   [ ] After image builds and pushes to the registry, run the
        [tutorials](https://github.com/scverse/scvi-tutorials) using the new
        image.
-   [ ] Publish a new release on the tutorials repo off `main` after all
        tutorials changes have been merged.
-   [ ] Create a new branch off `main` in the main repo and run
        `git submodule update --remote`, and then merge the PR, with an
        appropriate backport as needed.
-   [ ] Double check everything and then publish the draft release on the main
        repo.
-   [ ] Check that the
        [feedstock repo](https://github.com/conda-forge/scvi-tools-feedstock)
        updates correctly.
-   [ ] Check that the version updates correctly on
        [PyPI](https://pypi.org/project/scvi-tools/).
-   [ ] (Optional) Post threads on Discourse and Twitter!

## #2242: Implement contrastiveVI
**Issue:** #2242 | **Last activity:** 2023-11-20T23:23:10Z
**State:** closed | **Author:** @chris522229197 | **Comments:** 1 | **Created:** 2023-08-16 | **URL:** https://github.com/scverse/scvi-tools/issues/2242

Proposal to implement contrastiveVI.

1. Code: https://github.com/suinleelab/contrastiveVI
2. Paper: https://www.nature.com/articles/s41592-023-01955-3

I can take on this issue since I know the implementation details of contrastiveVI. Are there things I should be aware of before submitting a pull request (e.g., an upcoming major release)?

**@martinkim0:** Hi Chris, it'd be great to have contrastiveVI in the codebase. Feel free to put in an initial PR and I can give feedback then. I'm thinking this can be included in our v1.1 release.

## #2259: ModuleNotFoundError: No module named 'anndata._io.specs'
**Issue:** #2259 | **Last activity:** 2023-11-14T23:36:00Z
**State:** closed | **Author:** @zhangnan0107 | **Comments:** 2 | **Created:** 2023-09-08 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2259

<!-- Describe the bug -->

Dear scvi group,

Thanks for developing such a useful tool!

I recently got an error when trying importing `scvi` package. Please see below for more details. Would be grateful if you could provide some suggestions!

Thanks and best,
Nan

<!-- To reproduce -->
#### To reproduce:
```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()

import numba
import numpy as np
import pandas as pd
import pynndescent
import scanpy as sc
import scvi
from scvi.hub import HubModel
from scvi.model.utils import mde
```

#### Error info:
<!-- Put your Error output in this code block (if applicable, else delete the block): -->

```pytb

---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
File ~/.conda/envs/HLCA_mapping_env/lib/python3.8/site-packages/scvi/data/_utils.py:17
     16 try:
---> 17     from anndata.experimental import read_elem
     18 except ImportError:

ImportError: cannot import name 'read_elem' from 'anndata.experimental' (/home/n853g/.local/lib/python3.8/site-packages/anndata/experimental/__init__.py)

During handling of the above exception, another exception occurred:

ModuleNotFoundError                       Traceback (most recent call last)
Cell In[8], line 6
      4 import pynndescent
      5 import scanpy as sc
----> 6 import scvi
      7 from scvi.hub import HubModel …

**@martinkim0:** Can you try reinstalling scvi-tools in a fresh virtual environment and check if this issue reproduces? Thanks!

**@martinkim0:** Is there an update to this issue? If not, I'll be closing it.

## #1147: Lightning Tutorials
**Issue:** #1147 | **Last activity:** 2023-11-14T23:32:42Z
**State:** closed | **Author:** @tchaton | **Comments:** 3 | **Created:** 2021-09-06 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/1147

Dear scvi-tools Team,

My name is Thomas Chaton and I am part of the PyTorch Lightning Team.

I dived into this framework while investigating speed drop (here is the tracking issue: https://github.com/PyTorchLightning/pytorch-lightning/issues/9304). We apologise for this.

We are planning a Community Sprint for building high quality tutorial: https://github.com/PyTorchLightning/lightning-tutorials.
Currently, Deep Learning Course of University of Ámsterdam is been added.

We would like to invite your team to contribute a course / notebook on probabilistic model from scratch and then with scvi-tools library. We will heavily promote this notebook within the Lightning documentation.

Would anyone interested to make this contribution ?

Best,
T.C

**@adamgayoso:** Hi @tchaton thank you for helping with the pytorch lightning issues. We would be interested in contributing here, maybe we can show latent dirichlet allocation three ways:

1. Pure lightning
2. Scvi-tools
3. Scvi-tools with Pyro backend (still trained with lightning)

I would estimate it would take us several months to make this contribution however.

**@tchaton:** Sounds great ! Any chance it could be slightly faster ?

**@adamgayoso:** we can try :)

## #1462: Refactor tests
**Issue:** #1462 | **Last activity:** 2023-11-14T23:32:25Z
**State:** closed | **Author:** @adamgayoso | **Comments:** 0 | **Created:** 2022-03-25 | **Labels:** refactor, tests | **URL:** https://github.com/scverse/scvi-tools/issues/1462

Our tests are a bit of a mess, we should figure out a more logical way to test everything.

## #2022: Refactor `dataloaders` module
**Issue:** #2022 | **Last activity:** 2023-11-14T23:23:13Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-05-04 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2022

- [ ] Merge `AnnTorchDataset` and `DeviceBackedDataset` into a single class
- [ ] `AnnDataLoader` that accepts custom samplers
- [ ] `ConcatDataLoader` and `SemiSupervisedDataLoader`
- [ ] `DataSplitter` that accepts splitting indices

Related issues/PRs:

- #1995
- #1919
- #1987
- #1706

## #2218: Conda recipe broken due to flax
**Issue:** #2218 | **Last activity:** 2023-11-14T23:20:47Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 3 | **Created:** 2023-07-29 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2218

Installing via conda will fail due to the latest jax release (0.4.14) that deprecates `jax.ShapedArray`. This is causing flax to fail since its conda and pypi releases are out of sync (0.6.1 vs. 0.7.1) due to its newer dependencies not being on conda: https://github.com/conda-forge/flax-feedstock/pull/24

**@MishalAshraf:** Any idea how to work around this for the time being? install with pip?

**@martinkim0:** Yep! Installing with just pip will work. Alternatively, you can pip install flax before installing scvi-tools with conda

**@martinkim0:** Fixed now as the latest version of Flax is on conda forge.

## #2264: Add changes to make saving intermediate checkpoints easier
**Issue:** #2264 | **Last activity:** 2023-11-14T23:15:02Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-09-14 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tools/issues/2264

https://discourse.scverse.org/t/how-to-save-intermediate-checkpoints/1720

## #2314: ValueError: Expected more than 1 value per channel when training, got input size torch.Size([1, 128])
**Issue:** #2314 | **Last activity:** 2023-11-08T23:54:21Z
**State:** closed | **Author:** @Huiflorazhan | **Comments:** 2 | **Created:** 2023-11-06 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tools/issues/2314

When I try to use scvi to train the model, I got the following error. Could you please help me to solve this problem? Thank you for your time!
![image](https://github.com/scverse/scvi-tools/assets/139293021/bd0cb813-e5d8-4ef4-bcd6-2ed593d2df4f)

ValueError("Expected more than 1 value per channel when training, got input size {}".format(size))
ValueError: Expected more than 1 value per channel when training, got input size torch.Size([1, 128])

My code:
![image](https://github.com/scverse/scvi-tools/assets/139293021/cd7af8f2-e00d-4038-8a5f-7306854e4084)



scvi-tools version 1.0.4

**@martinkim0:** Hi, this unfortunately occurs when the last batch of the training set contains one observation, leading to the batch norm layer complaining. You can solve this by passing in a `batch_size` to the `train` method that is different than the default one.

**@Huiflorazhan:** > Hi, this unfortunately occurs when the last batch of the training set contains one observation, leading to the batch norm layer complaining. You can solve this by passing in a `batch_size` to the `train` method that is different than the default one.

It works. Thank you so much!
