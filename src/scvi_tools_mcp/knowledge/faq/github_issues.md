# scvi-tools GitHub Issues Snapshot

Fetched top 31 issues by comment count.

## #3806: feat: add harreman for metabolic exchange inference in spatial transcriptomics
**Comments:** 1
**Body:** ## Description
 This PR adds Harreman (`scvi.external.harreman`), a toolkit for inferring
 metabolic exchanges in tissues using spatial transcriptomics data.

 ## Changes
 - Add `scvi.external.harreman` with submodules:
   - `tl` (tools): KNN graph, cell communication, gene pairs
   - `hs` (hotspot): local autocorrelation, local correlation, gene modules
   - `pp` (preprocessing): AnnData setup, interaction database loading
   - `ds` (datasets): Visium and Slide-seq example datasets
   - `pl`

## #3823: scVI-X release
**Comments:** 1
**Body:** Do not merge or review yet.

## #3620: feat: Adding support for Annbatch
**Comments:** 3
**Body:**

## #3571: model: SENAVAE
**Comments:** 4
**Body:**

## #2257: MultiVI with Poisson/NB likelihood for ATAC?
**Comments:** 8
**Body:** Hi @martinkim0 and all

 Similarly to https://github.com/scverse/scvi-tools/pull/2249 by @lauradmartens would be great to have a MultiVI version with Poisson or even NB likelihood for ATAC data. How hard do you @martinkim0 think it is to add such option to MultiVI?

## #3674: Resolvi.load overflows memory
**Comments:** 6
**Body:** <!-- Describe the bug -->  When I load a saved model via RESOLVI.load, the memory consumption to just load the model is higher than while the model was being trained. I am using a 256gb ram and 22 GB GPU. While loading, the model, the GPU only uses about 200 MB VRAM while the RAM overshoots the 256 GB limit. During training, model used about 180 GB RAM and 2-5 GB VRAM.   Xenium dataset, 200k cells 5k genes  <!-- To reproduce -->  ```python RESOLVI.load(/path/to/model, data, accelerator='gpu') ``

## #1038: Faster NB LL computation if data is known to be sparse
**Comments:** 6
**Body:** We should add an `is_sparse` param to our distributions (at least [NB](https://github.com/YosefLab/scvi-tools/blob/0ef7ff0e9a06d65cd458b59c516971099bb55756/scvi/distributions/_negative_binomial.py#L236-L280), with LL computation [here](https://github.com/YosefLab/scvi-tools/blob/0ef7ff0e9a06d65cd458b59c516971099bb55756/scvi/distributions/_negative_binomial.py#L67-L102))

 As an example in Pyro for Poisson, see [here](https://github.com/pyro-ppl/pyro/pull/2802/files)

 If X is known to be spars

## #3786: refactor: Dropping Jax from scvi-tools
**Comments:** 2
**Body:**

## #3834: MultiVI MuData setup rejects unpaired observations despite model supporting missing modalities
**Comments:** 4
**Body:** <!-- Describe the bug -->  When trying to use MultiVI with a MuData object containing unpaired observations (cells missing from some modalities), scvi-tools now raises:  ``` ValueError: Detected unpaired observations in modality rna. Please make sure that data is fully paired in all MuData inputs. Either pad the unpaired modalities or take the intersection with muon.pp.intersect_obs(). ```  This is surprising, as MultiVI is designed to handle missing modalities during modeling, yet the data vali

## #2736: Training models with torch.Tensor input
**Comments:** 4
**Body:** **Is your feature request related to a problem? Please describe.**
 It is not currently straightforward to pass external dataloaders to train a model. In particular, loading `torch.Tensor` data and directly feeding it to a model as input doesn't seem possible because `scvi.data._utils._check_nonnegative_integers` does not handle `torch.Tensor`.

 It would be very useful to be able to feed a custom dataloader, dictionary or AnnData as direct input to model.train() without having to copy `torch.

## #2616: PyroModelGuideWarmup fails on GPU - probably need to be manually run before `trainer.fit()`
**Comments:** 4
**Body:** <!-- Describe the bug -->

 PyroModelGuideWarmup fails on GPU probably because `Callback.setup()` is called in the accelerator environment in the latest PyTorch Lightning.

 <!-- To reproduce -->
 This test fails on GPU:
 ```python
 pytest tests/model/test_pyro.py::test_pyro_bayesian_regression_low_level --accelerator 'gpu'
 ```

 <!-- Put your Error output in this code block (if applicable, else delete the block): -->

 ```pytb
 (cell2state_cuda118_torch22) vk7@farm22-gpu0203:.../software/t

## #1859: Model request: non-negative spatial factorization (NSF)
**Comments:** 4
**Body:** Is anyone currently working on implementing NSF? It's a nice probabilistic method designed with spatial transcriptomics in mind. https://www.nature.com/articles/s41592-022-01687-w

 It'd be nice to work with this here, within `scvi-tools`. The authors' implementation (@ https://github.com/willtownes/nsf-paper) is a little hard to parse and implemented with Tensorflow as a backend (which I don't work in).

## #1840: Finalize scBasset
**Comments:** 4
**Body:** - [x] Verify that all parameters are being initialized equivalently, alter the ones used here if needed
 - [x] Add more content to the tutorial that reproduces their results, allowing us to have some form of reproducibility
 - [ ] Complete the user guide

## #3827: feat: scvix reformat
**Comments:** 1
**Body:**

## #3821: feat: add rapids singlecell support for cytovi
**Comments:** 1
**Body:**

## #3759: Direct `csr` sparse ops support
**Comments:** 3
**Body:** **Is your feature request related to a problem? Please describe.** I think there are performance gains to be had by not densifying inputs from minibatches when possible and instead doing backprop on the sparse matrix directly yielded from the loader at the level of sparsity we sometimes see (~2%) in full-feature-space RNA-seq data at least. In this notebook, it's 2X for a MLP classifier. IIUC, this same trick applies to the loss function as well as the ELBO i.e., use the sparse matrix directly i

## #3600: Use scverse template
**Comments:** 3
**Body:** Hey,  from what I can see, you're currently not (fully) using the scverse template. Would it be possible to do so, please? I'd be happy of we could converge on a more consistent developer experience across all of our repositories.  Then we can also enable the sync.

## #1789: Some suggestion about GNN
**Comments:** 3
**Body:** **Is your feature request related to a problem? Please describe.**
 I want to develop a new model with Pytorch Geometric  which is a GNN library based on Pytorch. I hope you can develop some api to make it more easier.

 **Describe the solution you'd like**
 1. Please **develop a obsm_field for AnnDataManager to register obsm(n_obs*n_obs) attribute**. Because [scanpy neighbors](https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.neighbors.html#scanpy.pp.neighbors) save the graph adjace

## #3819: Add `weighted_knn_trainer`/`weighted_knn_transfer` utilities from scArches
**Comments:** 2
**Body:** Hello!   **Is your feature request related to a problem? Please describe.** I am migrating a workflow from scArches to scvi-tools for the sc-best-practice. Most functionality has a clear equivalent in scvi-tools, but `scarches.utils.weighted_knn_trainer` and `weighted_knn_transfer` have no counterpart.  **Describe the solution you'd like** Would it be possible to add the functions to e.g. `scvi.tools`? Thank you so much!

## #3798: feat: Add RESOLVI graph dataloader integration and benchmark CI
**Comments:** 1
**Body:**

## #3748: feat: JointEmbeddingSCVI
**Comments:** 2
**Body:** added files from Valentine's repo

## #3702: Feat: Asymmetric n_layers for  encoder/decoder
**Comments:** 2
**Body:** close https://github.com/scverse/scvi-tools/issues/3698

## #3699: Add DRVI
**Comments:** 1
**Body:** Dear Maintainers,

 Here, I have prepared [DRVI](https://github.com/theislab/drvi) for contribution as an external model, matching the latest version of scvi-tools.
 In short, it contains:

 - DRVI models with all the required PyTorch modules I wrote. Specifically,
   - FCLayers are modified to decode multiple parallel splits of the latent space at once. For this, we have a factory that generates hidden layers based on user setup.
   - The scArches Q2R mapping is implemented differently but s

## #3607: refactor: Use scverse template
**Comments:** 1
**Body:** Updated several missing files per the cookicutter template
 close https://github.com/scverse/scvi-tools/issues/3600

## #1456: Within cluster DE test
**Comments:** 2
**Body:** scVI used to have a within cluster DE test that I used often, but I no longer see this functionality in scvi-tools. Is it possible to add it back?

 This would be a differential expression function where a "groupby" argument would specify a set of groups (e.g., cell clusters) and a "states" argument would specify the relevant comparison to make (e.g., case vs control). The output would include the DE test results from a comparison of cases vs controls within each specified group.


## #3830: refactor(external): share cyclic loader for GIMVI and DIAGVI
**Comments:** 1
**Body:**

## #3824: First draft of scPoli
**Comments:** 1
**Body:** Draft of scPoli. Review with care.

## #3754: feat: add shared memory for DDP data deduplication
**Comments:** 1
**Body:**

## #3734: Improving SCVI for low-count cells through self-supervised augmentation
**Comments:** 1
**Body:** Hi,  A paper has recently been written about improving scVI for low count cells using binomial thinning and a cross-correlation loss. It looks like this extension of scVI improves on the integration of low count cells based on the paper results. I thought this may be of interest for you and that you may consider incorporating this into scvi-tools at some point.  Paper link: https://www.biorxiv.org/content/10.64898/2026.02.11.705441v1.full.pdf

## #3647: Allow custom label_key for scib-metrics in scvi.autotune
**Comments:** 1
**Body:** **Is your feature request related to a problem? Please describe.** When using `scvi.autotune.run_autotune` with scIB metrics for multi-modal integration, I cannot specify which .obs columns should be used as labels for autotune with scib-metrics. The autotune framework only uses the model's internally registered labels fields from the data manager. `setup_mudata` does not support `labels_key`, so label-dependent scib metrics cannot access biologically meaningful labels like tissue or cell type t

## #1177: User guide: gimVI
**Comments:** 0
**Body:**
