# scverse/scvi-tutorials GitHub Pull Requests

129 pull requests (open, closed and merged, bots excluded) from scverse/scvi-tutorials with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; PRs are only removed once they age out of that window.

## #578: Update the default python version and add py 3.15
**PR:** #578 | **Last activity:** 2026-10-28T08:46:59Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 3 | **Created:** 2026-10-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/578

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis on `.github/workflows/run_notebook.yaml`:** True for now, but we are going to release a new scvi-tools version that will build it with py3.14 and cu13 so it will be ok

**@ori-kron-wis on `.github/workflows/run_linux_cuda.yml`:** Will fix it.

**@ori-kron-wis on `.github/workflows/run_linux_cuda.yml`:** Same like in above

## #575: cytovi tutos updates
**PR:** #575 | **Last activity:** 2026-10-14T07:25:43Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2026-10-06 | **URL:** https://github.com/scverse/scvi-tutorials/pull/575

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** We used to compare recent changes in cytoVI and its the same, so no need to merge it now.

## #571: update VIVS tutorial
**PR:** #571 | **Last activity:** 2026-09-09T10:54:39Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-09-09 | **URL:** https://github.com/scverse/scvi-tutorials/pull/571

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #566: Perturbation tutorial with pertpy and scib-metrics new addition
**PR:** #566 | **Last activity:** 2026-09-02T07:39:12Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-08-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/566

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #422: Ori update intrepability tutorial with fastshap
**PR:** #422 | **Last activity:** 2026-07-28T06:40:56Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-03-24 | **URL:** https://github.com/scverse/scvi-tutorials/pull/422

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #400: [WIP] MrVI 1k tutorial draft
**PR:** #400 | **Last activity:** 2026-07-27T11:34:37Z
**State:** open | **Author:** @PierreBoyeau | **Comments:** 0 | **Created:** 2025-02-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/400

Solves #399

Requires changes introduced in https://github.com/scverse/scvi-tools/pull/3146 to run properly.

## #557: Refactor [WIP]: Removed the spatial folder from scvi-tutorials in v1.6
**PR:** #557 | **Last activity:** 2026-07-27T11:33:33Z
**State:** open | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-09 | **URL:** https://github.com/scverse/scvi-tutorials/pull/557

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #491: refactor: updates to backend files to match scverse template cookiecutter
**PR:** #491 | **Last activity:** 2026-07-26T12:45:31Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 2 | **Created:** 2025-11-20 | **URL:** https://github.com/scverse/scvi-tutorials/pull/491

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@Zethson (review, approved):** Great, thank you very much!

**@ori-kron-wis:** @Zethson should we merge?

## #561: Fix typo in LDVAE tutorial
**PR:** #561 | **Last activity:** 2026-07-26T12:29:19Z
**State:** merged | **Author:** @NiskyLe | **Comments:** 0 | **Created:** 2026-07-23 | **URL:** https://github.com/scverse/scvi-tutorials/pull/561

Loadings explanation fix, now for a given cell x, the expression of the gene g correctly starts at dimension 0 instead of 1:

- before:  x_g = w\_(1, g) * z_1 + ..
- after typo fix: x_g = w\_(0, g) * z_0 + ..

## #562: docs: fix the Sphinx warnings these notebooks raise in scvi-tools
**PR:** #562 | **Last activity:** 2026-07-26T11:54:26Z
**State:** merged | **Author:** @Zethson | **Comments:** 0 | **Created:** 2026-07-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/562

scvi-tools renders this repository as part of its documentation and is switching to a `-W` Sphinx build in scverse/scvi-tools#3607, where these warnings become errors. This fixes all 33 of them; the changes are cosmetic and do not touch any code cell or output apart from the two noted below.

- **Heading levels** in 11 notebooks skipped a level (H1 → H3, or H2 → H4). Demoted the offending headings so each notebook has a contiguous hierarchy. No headings were removed or renamed.
- **`use_cases/interpretability.ipynb`** and **`r/api_overview_in_R.ipynb`** had a link target wrapped in quotes — `[text]("https://…")` — which markdown does not treat as a URL. Removed the quotes.
- **`hub/scvi_hub_intro_and_download.ipynb`** linked to `#Download-models`; the generated anchor is lowercase, so the link was dead.
- **`custom_dl/api_overview_annbatch.ipynb`** linked to `quick_start/api_overview.ipynb`, which resolves relative to `custom_dl/`. Made it `../quick_start/api_overview.ipynb`.
- **`r/python_in_R.ipynb`** has an intentional error output demonstrating a `reticulate` type mismatch. Its R traceback cannot be parsed by the `ipythontb` lexer, so the notebook now sets `render_error_lexer` in its `mystnb` metadata.
- **`scbs/MethylVI_batch.ipynb`** had a `---` transition directly below its title; docutils rejects a document that begins with one. Removed it.

Verified by building the scvi-tools documentation with `-W` against this branch: it now completes with zero warnings.

## #558: ci: update github workflows
**PR:** #558 | **Last activity:** 2026-07-12T13:32:59Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/558

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #556: fix: remove Tahoe100_mrVI_lamin.ipynb
**PR:** #556 | **Last activity:** 2026-07-09T06:24:36Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-09 | **URL:** https://github.com/scverse/scvi-tutorials/pull/556

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #548: fix tahoe mrvi tuto
**PR:** #548 | **Last activity:** 2026-07-08T14:57:16Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-07-08 | **URL:** https://github.com/scverse/scvi-tutorials/pull/548

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #539: Add DRVI general pipeline notebook
**PR:** #539 | **Last activity:** 2026-07-07T11:00:53Z
**State:** merged | **Author:** @moinfar | **Comments:** 4 | **Created:** 2026-07-02 | **URL:** https://github.com/scverse/scvi-tutorials/pull/539

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** Made some small changes:
1. Added RAPIDS-singlecell support.
2. Added support for google-colab.
3. Moved data to scverse S3 (we're not working with Figshare anymore).
4. Save paths to be the same as the rest of the tutorials, inc model save.
5. Github workflows.

Besides that, it finishes fast. All good!

**@moinfar:** Thanks.
All changes look good to me.

One issue with RAPIDS-singlecell is that we have observed it makes meaningless outliers on its UMAPs (scanpy's UMAP does not).
This sometimes makes users confused. Especially, they run DRVI for the first time and observe outliers and get disappointed, while this is a RAPIDS problem rather than DRVI's.

Are you aware if this issue is fixed?

**@ori-kron-wis:** > Are you aware if this issue is fixed?

Actually Im not. Feel free to revert the RAPIDS part. With my run I didn't see any changes.

**@moinfar:** Hi,

I made the final touches:
1. Removed rapids single cell (aforementioned issue).
2. Used `Immune_HVG_human.h5ad`, which is generated by the code below. This way, the notebook is not focused on pre-processing, which is independent of DRVI.
**Can you please also update this to Scverse S3? This makes the tutorial much cleaner.**
https://drive.google.com/file/d/1eZ1Mza_gnBRw9LqLeHAW6wZcCmBeeM97/view?usp=sharing

```{python}
## Imports

import os
import tempfile

import scanpy as sc

from drvi.utils.misc import hvg_batch

## Load / pre-process / save data

save_dir = tempfile.TemporaryDirectory()

adata_path = os.path.join(save_dir.name, "immune_all.h5ad")
adata = sc.read(
    adata_path, backup_url="https://exampledata.scverse.org/scvi-tools/Immune_ALL_human.h5ad" …

## #537: Harreman tutorials
**PR:** #537 | **Last activity:** 2026-07-06T12:54:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-30 | **URL:** https://github.com/scverse/scvi-tutorials/pull/537

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #535: update joint embeddings tutorial
**PR:** #535 | **Last activity:** 2026-06-28T15:18:47Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-28 | **URL:** https://github.com/scverse/scvi-tutorials/pull/535

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #534: Add JointEmbeddingSCVI tutorial for low-count cell embeddings
**PR:** #534 | **Last activity:** 2026-06-28T11:44:24Z
**State:** merged | **Author:** @vals | **Comments:** 0 | **Created:** 2026-06-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/534

Hi! This is the tutorial notebook for the JointEmbeddingSCVI model.

Demonstrates the bias-point collapse of standard SCVI on low-UMI cells and how JointEmbeddingSCVI (binomial-thinning + cross-correlation objective) preserves cell-type structure, on a depth-broadened PBMC dataset (GSE310923).

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #533: fix: Remove jax from toutorrial
**PR:** #533 | **Last activity:** 2026-06-25T11:52:41Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/533

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #530: Update run_notebook.yaml
**PR:** #530 | **Last activity:** 2026-06-22T08:27:34Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-22 | **URL:** https://github.com/scverse/scvi-tutorials/pull/530

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #529: TOTALANVI TUTORIALS
**PR:** #529 | **Last activity:** 2026-06-22T07:22:15Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-22 | **URL:** https://github.com/scverse/scvi-tutorials/pull/529

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #528: TOTALANVI TUTORIALS
**PR:** #528 | **Last activity:** 2026-06-21T17:29:11Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-21 | **URL:** https://github.com/scverse/scvi-tutorials/pull/528

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #527: fix: update several data sources to be scverse's + diagvi local runs
**PR:** #527 | **Last activity:** 2026-06-18T12:48:44Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-06-18 | **URL:** https://github.com/scverse/scvi-tutorials/pull/527

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #526: Annbatch tuto
**PR:** #526 | **Last activity:** 2026-06-17T14:30:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2026-06-17 | **URL:** https://github.com/scverse/scvi-tutorials/pull/526

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis on `.github/workflows/run_notebook_all.yaml`:** its ok we will push correct packages in the annbatch branch

## #508: DiagVI tutorials
**PR:** #508 | **Last activity:** 2026-04-29T09:18:16Z
**State:** merged | **Author:** @michelta00 | **Comments:** 2 | **Created:** 2026-02-21 | **URL:** https://github.com/scverse/scvi-tutorials/pull/508

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis on `multimodal/DiagVI_spatial_proteomics.ipynb`:** A few things:
1. I wouldn't commit with `warnings.filterwarnings("ignore")`
2. See other comments from the scvi-tools diagvi PR. e.g : compute_foscttm into a different location
3. Add convergence curves
4. Validate with the most recent scvi-tools/scib-metrics versions (from main branch)
5. Validate both CPU/GPU runs (even a few epochs to see it works logically)
6. Perhaps we want to compare to TotalVI and TotalANVI?. Both of them are multimodal for RNA and Protein data

**@michelta00 on `multimodal/DiagVI_spatial_proteomics.ipynb`:** Thanks for the feedback!

Regarding `warnings.filterwarnings("ignore")`, we use this setting to suppress warnings mainly from other packages that are not directly relevant to the user and clutter the notebook output. If you would still recommend removing it, we can of course do that.

And regarding the comparison with totalVI and totalANVI, we think this would be difficult due to two reasons. First, totalVI is designed for paired inputs, while DiagVI is designed for unpaired input, so we are not sure whether totalVI can be meaningfully applied in this setting. Second, in the spatial proteomics tutorial, we apply DiagVI to imaging-based spatial proteomics data which is represented as continuous values, but totalVI only supports NB and ZINB distributions as far as we can tell.

## #512: typo in totalvi tutorial
**PR:** #512 | **Last activity:** 2026-03-03T11:19:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-03-03 | **URL:** https://github.com/scverse/scvi-tutorials/pull/512

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #510: Tutorials general updates: mostly data moved scverse hosted s3 bucket and few api changes.
**PR:** #510 | **Last activity:** 2026-02-26T07:47:10Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-02-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/510

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #505: updates for hub tutorials
**PR:** #505 | **Last activity:** 2026-02-09T11:25:40Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2026-01-28 | **URL:** https://github.com/scverse/scvi-tutorials/pull/505

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #496: Add get_normalized_accesssibility in multivi tutorial + destvi tutorial updates + mrvi tutorial fixes
**PR:** #496 | **Last activity:** 2025-12-08T07:46:10Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-11-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/496

**@ori-kron-wis:** close https://github.com/scverse/scvi-tutorials/issues/494

## #495: updated destvi tutorial
**PR:** #495 | **Last activity:** 2025-11-26T15:16:42Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-11-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/495

support destvi v2
close https://github.com/scverse/scvi-tutorials/issues/357

## #487: R: updated R tutorials
**PR:** #487 | **Last activity:** 2025-11-06T10:14:10Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-11-03 | **URL:** https://github.com/scverse/scvi-tutorials/pull/487

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #476: Fix in autotune_scvi.ipynb
**PR:** #476 | **Last activity:** 2025-09-12T06:31:28Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-09-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/476

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #475: change the tests to be on py3.13 by default
**PR:** #475 | **Last activity:** 2025-09-09T11:23:58Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-09-09 | **URL:** https://github.com/scverse/scvi-tutorials/pull/475

to see all new installations are working

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #469: MRVI in torch tutorials + applied on Tahoe100
**PR:** #469 | **Last activity:** 2025-09-07T11:28:05Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-08-18 | **URL:** https://github.com/scverse/scvi-tutorials/pull/469

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #468: Add scarches functionality to sysVI tutorial
**PR:** #468 | **Last activity:** 2025-08-21T10:08:04Z
**State:** merged | **Author:** @Hrovatin | **Comments:** 0 | **Created:** 2025-08-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/468

Related to https://github.com/scverse/scvi-tools/pull/3448

## Formatting

- [x ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #471: mention that resolVI can be used as first embedding model
**PR:** #471 | **Last activity:** 2025-08-21T09:45:38Z
**State:** merged | **Author:** @LevyNat | **Comments:** 0 | **Created:** 2025-08-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/471

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #462: new tuto for mrvi in torch + an example on tahoe100m
**PR:** #462 | **Last activity:** 2025-08-18T13:54:37Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-07-24 | **URL:** https://github.com/scverse/scvi-tutorials/pull/462

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** close https://github.com/scverse/scvi-tutorials/issues/399

## #467: Integration of CytoVI tutorials
**PR:** #467 | **Last activity:** 2025-08-18T08:59:01Z
**State:** merged | **Author:** @florianingelfinger | **Comments:** 0 | **Created:** 2025-08-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/467

- adding CytoVI_batch_correction_tutorial.ipynb for basic use (preprocessing model training etc)
- adding CytoVI_advanced_tutorial.ipynb for more advanced use of CytoVI

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #464: update test yaml files
**PR:** #464 | **Last activity:** 2025-08-12T05:40:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-08-04 | **URL:** https://github.com/scverse/scvi-tutorials/pull/464

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #443: remove two_sided param in DA call
**PR:** #443 | **Last activity:** 2025-07-14T07:40:13Z
**State:** closed | **Author:** @lordy5 | **Comments:** 0 | **Created:** 2025-05-28 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/pull/443

I need to fix the existing tutorial errors before finalizing the preprocessing tutorial updates.

In the peakvi notebook, it currently uses the two_sided param when calling the differential accessibility method, and it looks like this param doesn't exist anymore.

There are 4 calls to differential_accessibility in the notebook, and two of them used two_sided=False, so by removing this parameter from those the results are now two sided instead of one sided, so the last plot looks different. I'm not sure if this is good enough or if we want to further modify the last section of the notebook.

## #450: docs: New AnnCollection Tutorial
**PR:** #450 | **Last activity:** 2025-07-06T13:11:24Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-05-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/450

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #456: fix bad tutorials file names
**PR:** #456 | **Last activity:** 2025-06-26T11:51:24Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-06-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/456

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #423: scVIVA tuto
**PR:** #423 | **Last activity:** 2025-06-26T09:19:07Z
**State:** merged | **Author:** @LevyNat | **Comments:** 0 | **Created:** 2025-03-24 | **URL:** https://github.com/scverse/scvi-tutorials/pull/423

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #398: add preprocessing tutorial with multiple examples
**PR:** #398 | **Last activity:** 2025-06-26T08:30:22Z
**State:** merged | **Author:** @lordy5 | **Comments:** 3 | **Created:** 2025-02-11 | **Labels:** documentation | **URL:** https://github.com/scverse/scvi-tutorials/pull/398

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@lordy5:** I still need to link to the preprocessing tutorial from the other relevant tutorials and remove the preprocessing sections from those, but first want to see if anything needs to be changed/added to the preprocessing tutorial.

**@ori-kron-wis:** Please run it with the most recent scvi-tools version (which is now 1.3v) .
Also use more TODO's on code so I can find the questions more easily.

For the concatenation of 2 datasets, I think you meant the old anndata preprocessing part, where the function pbmcs_10x_cite_seq downloads 2 adata , do preprocessing to them and concatenates them?.
I think the preprocess tutorial should replace that part now, no? so we will have just one place to download the already ready mudata from? In such case we will download only 1 file that is already preprocessed, it can have the same batch column like before, so we expect the same results but it can also have other columns as batch key

**@lordy5:** @ori-kron-wis Which tutorials should I remove the preprocessing sections from, now that there is the preprocessing notebook? I was thinking of removing it from the tutorials whose exact datasets I use in the preprocessing notebook, and keeping it for the others, but then still linking the preprocessing tutorial in all of them, so users know how to use their own datasets.

## #453: Taho100M cells Hub  tutorial
**PR:** #453 | **Last activity:** 2025-06-22T11:00:51Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-06-05 | **URL:** https://github.com/scverse/scvi-tutorials/pull/453

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #442: remove two_sided param in DA call
**PR:** #442 | **Last activity:** 2025-05-28T00:08:45Z
**State:** closed | **Author:** @lordy5 | **Comments:** 0 | **Created:** 2025-05-27 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/pull/442

I need to fix the existing tutorial errors before finalizing the preprocessing tutorial updates.

In the peakvi notebook, it currently uses the two_sided param when calling the differential accessibility method, and it looks like this param doesn't exist anymore.

There are 4 calls to differential_accessibility in the notebook, and two of them used two_sided=False, so by removing this parameter from those the results are now two sided instead of one sided, so the last plot looks different. I'm not sure if this is good enough or if we want to further modify the last section of the notebook.

## #439: updates
**PR:** #439 | **Last activity:** 2025-05-27T10:14:00Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-05-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/439

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #436: Tutorials New Location Because of New RTD tutorials Filtering Scheme
**PR:** #436 | **Last activity:** 2025-05-19T11:51:08Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-05-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/436

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #425: added custom dataloaders initial tutos
**PR:** #425 | **Last activity:** 2025-05-13T06:46:00Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-04-03 | **URL:** https://github.com/scverse/scvi-tutorials/pull/425

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #420: updated tuto with fast shap
**PR:** #420 | **Last activity:** 2025-03-13T16:04:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-03-13 | **URL:** https://github.com/scverse/scvi-tutorials/pull/420

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #418: Update interpretability.ipynb
**PR:** #418 | **Last activity:** 2025-03-05T11:39:55Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-03-05 | **URL:** https://github.com/scverse/scvi-tutorials/pull/418

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #415: add trademark
**PR:** #415 | **Last activity:** 2025-03-02T11:25:56Z
**State:** closed | **Author:** @melonora | **Comments:** 0 | **Created:** 2025-02-28 | **URL:** https://github.com/scverse/scvi-tutorials/pull/415

add statement of development and maintainance by scverse with trademark.

## #416: added scverse symbol
**PR:** #416 | **Last activity:** 2025-03-02T11:25:40Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-03-02 | **URL:** https://github.com/scverse/scvi-tutorials/pull/416

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #414: add tutorial for interpretability
**PR:** #414 | **Last activity:** 2025-02-27T16:18:50Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/414

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #412: docs: scib-autotune addition to tune tutorial
**PR:** #412 | **Last activity:** 2025-02-27T15:11:36Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/412

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #413: docs: change structure of tutorials
**PR:** #413 | **Last activity:** 2025-02-27T15:02:28Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-26 | **URL:** https://github.com/scverse/scvi-tutorials/pull/413

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #402: Updated tune tutorial with scib-metrics optimization
**PR:** #402 | **Last activity:** 2025-02-26T12:14:20Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2025-02-17 | **URL:** https://github.com/scverse/scvi-tutorials/pull/402

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@canergen:** Tutorial harmonization highlight that it uses multi-GPU now as a comment. Also a bunch of ValueErrors.
Autotune, I thought you wanted to highlight how to use scib-metrics during tuning.

## #401: Detached2
**PR:** #401 | **Last activity:** 2025-02-26T12:14:13Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-16 | **URL:** https://github.com/scverse/scvi-tutorials/pull/401

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #409: update tutorials
**PR:** #409 | **Last activity:** 2025-02-25T15:29:45Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/409

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #407: update tutorials
**PR:** #407 | **Last activity:** 2025-02-25T14:49:01Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/407

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #404: update tutorials
**PR:** #404 | **Last activity:** 2025-02-25T14:36:45Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-02-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/404

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #212: SysVI tutorial
**PR:** #212 | **Last activity:** 2025-02-25T08:47:03Z
**State:** merged | **Author:** @Hrovatin | **Comments:** 3 | **Created:** 2024-01-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/212

Associated with https://github.com/scverse/scvi-tools/issues/2383

## Formatting

- [ x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
Could you help with this?
- [x ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given
Data is normalized to fixed number of total counts as it was normalized separately for mouse and human. If median library size was used for normalization the two datasets would not be comparable.

**@martinkim0 (review, approved):** I'm approving this for now, but this needs to be run again once https://github.com/scverse/scvi-tools/pull/2421 is merged into main since we require that tutorials are run top to bottom in a container.

**@Hrovatin:** @ori-kron-wis @canergen I updated the tutorial now according to https://github.com/scverse/scvi-tools/pull/2421

**@Hrovatin:** I updated the SysVI tutorial after changes in https://github.com/scverse/scvi-tools/pull/3195

## #373: Basic Decipher Tutorial
**PR:** #373 | **Last activity:** 2025-02-18T22:18:36Z
**State:** merged | **Author:** @justjhong | **Comments:** 4 | **Created:** 2024-12-03 | **URL:** https://github.com/scverse/scvi-tutorials/pull/373

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- (N/A) For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

CC @ANazaret

**@canergen:** Can you add downstream functions? Can you explain NLL?

**@justjhong:** @canergen this is the basic version, i have a todo to extend to the downstream functions but it will be easier to review with a separate PR

**@canergen:** I can merge it, do you plan on adding it to the same tutorial (preferred)?

**@justjhong:** @canergen yes plan to add to this one!

## #394: updated with ext tutorial
**PR:** #394 | **Last activity:** 2025-01-27T12:24:36Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-01-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/394

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #391: `api_overview`: `latent_subset` fix
**PR:** #391 | **Last activity:** 2025-01-21T15:25:51Z
**State:** merged | **Author:** @ryan-williams | **Comments:** 0 | **Created:** 2025-01-16 | **URL:** https://github.com/scverse/scvi-tutorials/pull/391

This cell seemed to be erroneously showing the same `latent.shape` value from the previous cell

## #392: ResolVI tutorial.
**PR:** #392 | **Last activity:** 2025-01-20T10:12:20Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2025-01-17 | **URL:** https://github.com/scverse/scvi-tutorials/pull/392

## Formatting

- [X] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [X] My tutorial has been run and includes outputs (e.g. plots, tables)

## #390: totalvi update with explenations about pre filtering procedures
**PR:** #390 | **Last activity:** 2025-01-15T13:16:04Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-01-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/390

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #387: docs: Fix DE broken link
**PR:** #387 | **Last activity:** 2025-01-05T07:28:30Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2025-01-05 | **Labels:** documentation | **URL:** https://github.com/scverse/scvi-tutorials/pull/387

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #359: Add files via upload
**PR:** #359 | **Last activity:** 2024-12-31T10:12:42Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-30 | **URL:** https://github.com/scverse/scvi-tutorials/pull/359

direct download of files to cellassign tutorial

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #384: Update run_notebook_macos.yaml
**PR:** #384 | **Last activity:** 2024-12-19T12:45:35Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/384

## #382: Update run_notebook_macos.yaml
**PR:** #382 | **Last activity:** 2024-12-19T12:24:54Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/382

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #378: docs: updated tutorials without pymde + HF bug
**PR:** #378 | **Last activity:** 2024-12-19T12:17:45Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/378

This is related to https://github.com/scverse/scvi-tools/pull/2842

## #370: updated multivi tutorials with mudata and minification
**PR:** #370 | **Last activity:** 2024-12-19T12:17:41Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-11-21 | **URL:** https://github.com/scverse/scvi-tutorials/pull/370

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #381: Update run_notebook_macos.yaml
**PR:** #381 | **Last activity:** 2024-12-19T12:16:45Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/381

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #380: test: Added localy manual macos tests for mps
**PR:** #380 | **Last activity:** 2024-12-19T11:22:00Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/380

## #374: ci: Added run links for Methylvi
**PR:** #374 | **Last activity:** 2024-12-04T10:21:47Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-12-04 | **URL:** https://github.com/scverse/scvi-tutorials/pull/374

@ethanweinberger

## #363: MethylVI batch effect tutorial
**PR:** #363 | **Last activity:** 2024-11-27T13:33:25Z
**State:** merged | **Author:** @ethanweinberger | **Comments:** 21 | **Created:** 2024-10-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/363

Tutorial accompanies https://github.com/scverse/scvi-tools/pull/2834

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given (Note: not applicable to this tutorial as we're not using scRNA-seq)

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>Make consistent with other tutorials.</p>
<br/>

 _Reply via <a href='https://app.reviewnb.com/scverse/scvi-tutorials/pull/363/discussion/#comment-1792439828'>ReviewNB</a>_ <div id='ReviewNBCommentContext-DoNotDelete' style='display:none' data-state='RESOLVED' data-cellIndex='6'/>

**@canergen on `scbs/MethylVI_batch.ipynb`:** @ori-kron-wis can we use our download function instead?

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>jointly = one model but treat both seperately not add both and get one output? Maybe write "we'll jointly model both".</p><p>How would <code>modalities={"categorical_covariate_keys": "mCG"}</code>look like for two different fields. Please put in the comment.</p>
<br/>

 _Reply via <a href='https://app.reviewnb.com/scverse/scvi-tutorials/pull/363/discussion/#comment-1792439833'>ReviewNB</a>_ <div id='ReviewNBCommentContext-DoNotDelete' style='display:none' data-state='RESOLVED' data-cellIndex='19'/>

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>Maybe show get_normalized_methylation or DE additionally to go beyond latent space analysis? See our other tutorials for examples.</p>
<br/>

 _Reply via <a href='https://app.reviewnb.com/scverse/scvi-tutorials/pull/363/discussion/#comment-1792439834'>ReviewNB</a>_ <div id='ReviewNBCommentContext-DoNotDelete' style='display:none' data-state='RESOLVED' data-cellIndex='25'/>

**@canergen:** See comments overall looks fine. @ori-kron-wis can you help make the style consistent with other tutorials (I assume removing notebook style commands). These might change rendering on the webpage, which can end up ugly.

**@ethanweinberger on `scbs/MethylVI_batch.ipynb`:** <p>Once this notebook is merged in I plan to create a separate tutorial for feature-level analysis that will replicate the results from our (upcoming) preprint</p>

**@ethanweinberger on `scbs/MethylVI_batch.ipynb`:** <p>@canergen what exactly should I change here? I took this block of code from the Atlas integration tutorial at <a href="https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/harmonization.html" target="_blank">https://docs.scvi-tools.org/en/stable/tutorials/notebooks/scrna/harmonization.html</a></p>

**@ethanweinberger on `scbs/MethylVI_batch.ipynb`:** To make the description clearer, I changed the wording to "Here we'll jointly model both CpG and non-CpG methylation features" as suggested.

For the `modalities` argument, I added a {note} block similar to the one in the totalVI tutorial (https://docs.scvi-tools.org/en/stable/tutorials/notebooks/multimodal/totalVI.html)

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>Thanks and my bad. It was more a note to Ori to double-check once. Resolved.</p>

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>Please add the code that you would use if mCH and mCH in the note block below. It doesn't become clear to me.</p>

**@canergen on `scbs/MethylVI_batch.ipynb`:** <p>Can we have it in one notebook? I don't like bloating the number of tutorials. It's currently already quite painful to rerun and manually merge notebooks. Do you need different datasets for it?</p>

**@canergen on `scbs/MethylVI_batch.ipynb`:** Maybe you post here the code if both have different categories and then I can advise what's the minimum information required.

**@ethanweinberger on `scbs/MethylVI_batch.ipynb`:** For feature-level analysis I would prefer to use a different dataset (I don't have as good ground truths for the dataset here used for batch effect correction). I'm happy to put both analyses in a single notebook though if that's preferred. Let me know how you would prefer to proceed.

**@ethanweinberger on `scbs/MethylVI_batch.ipynb`:** @canergen what's the exact scenario you're thinking of?

I think I misunderstood your original comment, and I'm not sure what you're asking (was `if mCH and mCH` above a typo?). For example, by two different fields did you mean:

1. I have two categorical covariate fields, one if which lives in `mdata['mCG'].obs` and the other of which lives in `mdata['mCH'].obs`? In this case I believe the `MuDataCategoricalJointObsField` used in the `setup_mudata` function doesn't support this use case, and we would ask users to consolidate their categorical variables into one modality's `.obs` field.
2. Alternatively, do you mean one argument to the `setup_mudata` function is stored in one modality (e.g. `batch_key` is in `mCG`) while the other is in a different field (e.g. `categorical_covariate_ …

**@ori-kron-wis on `scbs/MethylVI_batch.ipynb`:** not sure, instead of what?

**@ori-kron-wis:** @canergen not so sure what is the problem/difference in style? care to give a few examples?
I could think about adding a save/load model part and also make a new line for each input parameter in a scanpy function (this is to be equivalent to other tutorials)

**@ethanweinberger:** Hi @canergen. Just wanted to check in to see if you had updates re: my and @ori-kron-wis's previous comments.

**@canergen on `scbs/MethylVI_batch.ipynb`:** No if it's using different datasets, make it different notebooks.

**@canergen (review, approved):** Please replace wget with pooch.

**@canergen:** @ori-kron-wis Please merge after adding pooch.

**@ori-kron-wis on `scbs/MethylVI_batch.ipynb`:** replaces wget with pooch

## #371: docs: Remove autotune hyperparameters info from tutorial
**PR:** #371 | **Last activity:** 2024-11-27T09:51:05Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2024-11-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/371

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** close https://github.com/scverse/scvi-tools/issues/3055

## #369: docs: bad link in minification.ipynb
**PR:** #369 | **Last activity:** 2024-11-12T10:14:59Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-11-12 | **Labels:** bug | **URL:** https://github.com/scverse/scvi-tutorials/pull/369

Fixing bad link in tutorial

## #361: fix in tangram - anndata uniq vars
**PR:** #361 | **Last activity:** 2024-09-30T17:11:22Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2024-09-30 | **URL:** https://github.com/scverse/scvi-tutorials/pull/361

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** close https://github.com/scverse/scvi-tutorials/issues/358

## #353: Update several tutorials so they will work in scvi-tools 1.2.0, py312…
**PR:** #353 | **Last activity:** 2024-09-25T18:29:52Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/353

… as well as on new servers

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #351: Update several tutorials so they will work in scvi-tools 1.2.0, py312…
**PR:** #351 | **Last activity:** 2024-09-25T17:05:28Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-25 | **URL:** https://github.com/scverse/scvi-tutorials/pull/351

… as well as on new servers

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #346: docs: updated several tutorials
**PR:** #346 | **Last activity:** 2024-09-23T18:32:17Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2024-09-23 | **URL:** https://github.com/scverse/scvi-tutorials/pull/346

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@canergen on `scrna/scanvi_fix.ipynb`:** I don't get this change. Rest approved.

## #322: Update pyproject.toml
**PR:** #322 | **Last activity:** 2024-09-22T10:24:52Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-22 | **URL:** https://github.com/scverse/scvi-tutorials/pull/322

changed the target version to be py312, like in scvi-tools repo

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #318: Update run_notebook.yaml
**PR:** #318 | **Last activity:** 2024-09-17T13:17:06Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-17 | **URL:** https://github.com/scverse/scvi-tutorials/pull/318

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #317: Drop Python 3.9
**PR:** #317 | **Last activity:** 2024-09-15T12:02:22Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-09-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/317

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #314: Changes scarches tutorial
**PR:** #314 | **Last activity:** 2024-09-02T11:46:56Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 1 | **Created:** 2024-09-02 | **Labels:** enhancement | **URL:** https://github.com/scverse/scvi-tutorials/pull/314

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@ori-kron-wis:** close https://github.com/scverse/scvi-tutorials/issues/294

## #310: Update cellassign_tutorial.ipynb with numpy dummy
**PR:** #310 | **Last activity:** 2024-08-27T14:26:14Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-08-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/310

just added a dummy usage of numpy so it wont be removed with pre-commits

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #303: cell assign tutorial update
**PR:** #303 | **Last activity:** 2024-08-19T15:20:37Z
**State:** closed | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-08-19 | **URL:** https://github.com/scverse/scvi-tutorials/pull/303

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #302: added numpy to cellassign tutorial
**PR:** #302 | **Last activity:** 2024-08-19T09:15:12Z
**State:** merged | **Author:** @ori-kron-wis | **Comments:** 0 | **Created:** 2024-08-19 | **Labels:** good first issue | **URL:** https://github.com/scverse/scvi-tutorials/pull/302

close https://github.com/scverse/scvi-tools/issues/2837

## #299: revert previous commit
**PR:** #299 | **Last activity:** 2024-07-12T23:59:03Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/299

## #298: ci: add notebooks yaml
**PR:** #298 | **Last activity:** 2024-07-12T23:43:55Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/298

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #295: ci: refactor run notebook workflows
**PR:** #295 | **Last activity:** 2024-07-12T22:37:01Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/295

## #292: ci: fix release workflow
**PR:** #292 | **Last activity:** 2024-07-08T20:39:58Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-08 | **URL:** https://github.com/scverse/scvi-tutorials/pull/292

## #291: ci: add release workflow
**PR:** #291 | **Last activity:** 2024-07-08T20:38:31Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-07-08 | **URL:** https://github.com/scverse/scvi-tutorials/pull/291

## #288: feat: update dev module tutorial for lossoutput
**PR:** #288 | **Last activity:** 2024-06-27T21:46:32Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-06-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/288

closes https://github.com/scverse/scvi-tools/issues/991

## #287: misc: update license
**PR:** #287 | **Last activity:** 2024-06-27T21:34:53Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-06-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/287

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #278: MrVI Quick Start Tutorial
**PR:** #278 | **Last activity:** 2024-05-01T17:25:55Z
**State:** merged | **Author:** @justjhong | **Comments:** 4 | **Created:** 2024-05-01 | **URL:** https://github.com/scverse/scvi-tutorials/pull/278

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@canergen:** Does the missing Colab check mean that it doesn't work or that it's not tested yet? In the first case can we make it pass? IMO it's the easiest way for reviewers to check algorithms and for users to get to know them.

**@martinkim0 (review, changes requested):** Thanks for much Justin! Overall looks great, just a couple of comments:

Could you change the first line to:

> MrVI (Multi-resolution Variational Inference) is a **model**...

and maybe put like 1-2 sentences summarizing for what kind of datasets MrVI is appropriate?

Would it also be possible to add a citation for the dataset, a quick description of how it was subsetted, as well as a summary of the different `obs` fields?

Finally, in `Visualize cell embeddings and sample distances`, could you summarize the difference between `u` and `z` (I guess I'm assuming a user who is going to this tutorial directly without having read the paper).

**@martinkim0 (review, approved):** LGTM!!

**@martinkim0:** While you're at it, would you mind updating https://github.com/scverse/scvi-tutorials/blob/main/.github/workflows/run_linux_cuda.yml and https://github.com/scverse/scvi-tutorials/blob/main/.github/workflows/run_linux_cuda_branch.yml to include the new file? Thanks

## #275: misc: manually update pre-commit versions
**PR:** #275 | **Last activity:** 2024-04-15T20:47:30Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-04-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/275

## #274: style: update pre-commit and run auto-fixes
**PR:** #274 | **Last activity:** 2024-04-15T20:43:14Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-04-15 | **URL:** https://github.com/scverse/scvi-tutorials/pull/274

## #268: CELLxGENE model.
**PR:** #268 | **Last activity:** 2024-04-06T21:25:46Z
**State:** closed | **Author:** @canergen | **Comments:** 1 | **Created:** 2024-03-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/268

## Formatting

- [x ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@martinkim0 (review, approved):** Looks great overall! I'm going to approve in order to get this in, but I'll change the loading part once we have a better way to deal with minified data in hubmodels.

## #270: Add botocore unsigned key
**PR:** #270 | **Last activity:** 2024-03-23T22:41:30Z
**State:** closed | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-03-16 | **URL:** https://github.com/scverse/scvi-tutorials/pull/270

Small fix to settings in boto3

## #271: Changes to not use secret keys
**PR:** #271 | **Last activity:** 2024-03-23T22:41:12Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-03-16 | **URL:** https://github.com/scverse/scvi-tutorials/pull/271

Small changes.

## #269: Updated census tutorial
**PR:** #269 | **Last activity:** 2024-03-16T05:17:41Z
**State:** merged | **Author:** @canergen | **Comments:** 0 | **Created:** 2024-03-16 | **URL:** https://github.com/scverse/scvi-tutorials/pull/269

## Formatting

- [X] My tutorial has only one top-level (`#`) header

## Reproducibility

- [X] My tutorial works on Google Colab
- [X] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [X] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [X] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [X] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #264: Use logging_dir for autotune
**PR:** #264 | **Last activity:** 2024-02-12T21:08:05Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-12 | **URL:** https://github.com/scverse/scvi-tutorials/pull/264

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #234: Add common notes to tutorials
**PR:** #234 | **Last activity:** 2024-02-11T17:26:11Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-11 | **URL:** https://github.com/scverse/scvi-tutorials/pull/234

## #221: Correct and rerun hub intro tutorial
**PR:** #221 | **Last activity:** 2024-02-02T17:23:51Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-02 | **URL:** https://github.com/scverse/scvi-tutorials/pull/221

Fixes #174

## #220: Update scanvi fix tutorial
**PR:** #220 | **Last activity:** 2024-02-01T20:25:40Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-02-01 | **URL:** https://github.com/scverse/scvi-tutorials/pull/220

## #217: Add benchmark tutorial for scANVI logits fix
**PR:** #217 | **Last activity:** 2024-01-31T22:40:00Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/217

## #219: Update README
**PR:** #219 | **Last activity:** 2024-01-29T20:58:27Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/219

## #218: Fix formatting of scanvi tutorial
**PR:** #218 | **Last activity:** 2024-01-29T19:26:06Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/218

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #216: Update pre-commit config
**PR:** #216 | **Last activity:** 2024-01-29T19:10:38Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/216

## #215: Update run workflows
**PR:** #215 | **Last activity:** 2024-01-29T19:06:03Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2024-01-29 | **URL:** https://github.com/scverse/scvi-tutorials/pull/215

## #63: Batch Embedding Tutorial
**PR:** #63 | **Last activity:** 2024-01-22T19:51:32Z
**State:** closed | **Author:** @wukathy | **Comments:** 0 | **Created:** 2022-04-17 | **URL:** https://github.com/scverse/scvi-tutorials/pull/63

draft of batch embedding / "scvi in large donor studies" tutorial (currently using the `batch_embedding` branch of scvi-tools)

## #208: Add rerun release checklist
**PR:** #208 | **Last activity:** 2023-12-07T20:24:29Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/208

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #207: Increase timeout minutes for workflows
**PR:** #207 | **Last activity:** 2023-12-07T20:14:05Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/207

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #206: Increase workflow timeout minutes
**PR:** #206 | **Last activity:** 2023-12-07T20:11:33Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/206

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #205: Increase workflow timeout
**PR:** #205 | **Last activity:** 2023-12-07T20:10:15Z
**State:** closed | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/205

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #203: Remove use_gpu from model user guide
**PR:** #203 | **Last activity:** 2023-12-07T19:54:40Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/203

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #202: Fix contrastivevi tutorial
**PR:** #202 | **Last activity:** 2023-12-07T19:42:46Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/202

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #200: Fix autotune tutorial
**PR:** #200 | **Last activity:** 2023-12-07T19:29:00Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/200

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #198: Fix gimvi tutorial
**PR:** #198 | **Last activity:** 2023-12-07T19:20:49Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/198

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #196: Fix stereoscope tutorial
**PR:** #196 | **Last activity:** 2023-12-07T19:05:03Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/196

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #193: Fix autotune tutorial
**PR:** #193 | **Last activity:** 2023-12-07T18:54:31Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/193

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #192: Fix stereoscope tutorial
**PR:** #192 | **Last activity:** 2023-12-07T18:51:29Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/192

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #191: Fix contrastivevi tutorial
**PR:** #191 | **Last activity:** 2023-12-07T18:44:03Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/191

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #173: Fix tutorials
**PR:** #173 | **Last activity:** 2023-12-07T00:33:53Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-07 | **URL:** https://github.com/scverse/scvi-tutorials/pull/173

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #164: Update workflow
**PR:** #164 | **Last activity:** 2023-12-06T19:48:33Z
**State:** merged | **Author:** @martinkim0 | **Comments:** 0 | **Created:** 2023-12-06 | **URL:** https://github.com/scverse/scvi-tutorials/pull/164

## Formatting

- [ ] My tutorial has only one top-level (`#`) header

## Reproducibility

- [ ] My tutorial works on Google Colab
- [ ] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [ ] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [ ] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [ ] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

## #162: contrastiveVI tutorial
**PR:** #162 | **Last activity:** 2023-12-05T19:03:35Z
**State:** merged | **Author:** @ethanweinberger | **Comments:** 1 | **Created:** 2023-12-02 | **URL:** https://github.com/scverse/scvi-tutorials/pull/162

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given

**@martinkim0 (review, approved):** LGMT, thanks a lot!

## #160: PoissonVI tutorial
**PR:** #160 | **Last activity:** 2023-11-28T17:41:35Z
**State:** merged | **Author:** @lauradmartens | **Comments:** 2 | **Created:** 2023-11-27 | **URL:** https://github.com/scverse/scvi-tutorials/pull/160

## Formatting

- [x] My tutorial has only one top-level (`#`) header

## Reproducibility

- [x] My tutorial works on Google Colab
- [x] My tutorial sets `scvi.settings.seed = 0` at the beginning of the notebook
- [x] My tutorial has been run and includes outputs (e.g. plots, tables)

## Other

- [x] Counts and normalized data should co-exist in the datasets, see the [API overview](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/api_overview.html) for an example
- [x] For scRNA-seq data, normalization should be counts per median library size and then log1p transformed -- if not, a reason should be given (not applicable here)

**@martinkim0 (review, approved):** Typo: "appraoches" in one the cells

Other than that, LGTM!

**@lauradmartens:** @martinkim0, fixed it!
