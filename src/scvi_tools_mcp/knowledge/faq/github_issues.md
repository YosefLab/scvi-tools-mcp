# scvi-tools GitHub Issues Q&A

Top 17 issues by discussion volume (PRs excluded).

## #2257: MultiVI with Poisson/NB likelihood for ATAC?
**State:** open | **Comments:** 8 | **Labels:** enhancement, P1

Hi @martinkim0 and all

Similarly to https://github.com/scverse/scvi-tools/pull/2249 by @lauradmartens would be great to have a MultiVI version with Poisson or even NB likelihood for ATAC data. How hard do you @martinkim0 think it is to add such option to MultiVI?

**@canergen:** Hi @vitkl I'm linking @marianogabitto here as he developed multiVI and was also working on a different implementation of PoissonPeakVI. What's your opinion on this request?

**@lauradmartens:** Yes, I also think it should be relatively straightforward and also remember that @marianogabitto already had an implementation

**@vitkl:** Thanks for getting back to me about this! If you @marianogabitto have an implementation of this - would be great if you could share it or add it to scvi-tools (if makes sense for @canergen)

**@canergen:** Happy to review the PR.

**@vitkl:** I don't understand the implementations well enough to easily try implementing this - but I can do a PR if I see the example implementation from @marianogabitto

## #3674: Resolvi.load overflows memory
**State:** open | **Comments:** 6 | **Labels:** bug

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

## #1038: Faster NB LL computation if data is known to be sparse
**State:** open | **Comments:** 6 | **Labels:** enhancement, P2

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

## #3834: MultiVI MuData setup rejects unpaired observations despite model supporting missing modalities
**State:** open | **Comments:** 4 | **Labels:** bug

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

## #2736: Training models with torch.Tensor input
**State:** open | **Comments:** 4 | **Labels:** enhancement, P1

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

## #2616: PyroModelGuideWarmup fails on GPU - probably need to be manually run before `trainer.fit()`
**State:** open | **Comments:** 4 | **Labels:** bug, P0

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

## #1859: Model request: non-negative spatial factorization (NSF)
**State:** open | **Comments:** 4 | **Labels:** enhancement, new model, backlog

Is anyone currently working on implementing NSF? It's a nice probabilistic method designed with spatial transcriptomics in mind. https://www.nature.com/articles/s41592-022-01687-w

It'd be nice to work with this here, within `scvi-tools`. The authors' implementation (@ https://github.com/willtownes/nsf-paper) is a little hard to parse and implemented with Tensorflow as a backend (which I don't work in).

**@adamgayoso:** I think this would be a nice addition. It might be easiest to implement using tensorflow probability and jax as the kernel functions should be the same; unless of course it's also straightforward in pytorch. Are you willing to contribute this?

**@aribenjamin:** Yes, I'm happy to go for it. It'd be good practice contributing. I can't guarantee any timeline, though, so if someone wants this sooner please ping me.

**@adamgayoso:** Looking into this more, it should be possible with just PyTorch, or just jax+numpyro (which we already depend on), without the introduction of tensorflow probability. @martinkim0 do you want to try this model? It looks both fairly straightforward and fun.

**@aribenjamin:** fyi I have back-burnered this to the point of inaction. If you want to work on this, know that I'm not working in parallel. I'll update this when and if I begin.

## #1840: Finalize scBasset
**State:** open | **Comments:** 4 | **Labels:** enhancement, help wanted, backlog

- [x] Verify that all parameters are being initialized equivalently, alter the ones used here if needed
- [x] Add more content to the tutorial that reproduces their results, allowing us to have some form of reproducibility
- [ ] Complete the user guide

**@martinkim0:** @adamgayoso Thoughts on adding a batch correction portion to the tutorial using the buenrostro dataset from the original manuscript?

**@adamgayoso:** I think we should and the maybe use scib metrics on it

**@martinkim0:** I'm wondering whether we should add an option in `setup_anndata` to indicate whether the data is transposed already or not, where if it's not transposed, we do it on our end. It might be confusing for users when you have to `bdata = adata.transpose()` but then the latent space is saved back into the original `adata`.

**@adamgayoso:** I agree this needs improvement. I'm a fan of what you see is what you get and it would be confusing if `model.adata` was transposed

## #3759: Direct `csr` sparse ops support
**State:** open | **Comments:** 3 | **Labels:** enhancement

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

## #3600: Use scverse template
**State:** open | **Comments:** 3 | **Labels:** refactor

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

## #1789: Some suggestion about GNN
**State:** open | **Comments:** 3 | **Labels:** enhancement, data, P2

**Is your feature request related to a problem? Please describe.**
I want to develop a new model with Pytorch Geometric  which is a GNN library based on Pytorch. I hope you can develop some api to make it more easier.

**Describe the solution you'd like**
1. Please **develop a obsm_field for AnnDataManager to register obsm(n_obs*n_obs) attribute**. Because [scanpy neighbors](https://scanpy.readthedocs.io/en/stable/generated/scanpy.pp.neighbors.html#scanpy.pp.neighbors) save the graph adjacency matrix in obsm as key "connectivities".
2. **DataSplitter in scvi.dataloaders  maybe also should be updated to support minibatch operation**. This minibatch operation is similar to subgraph extraction.

**@adamgayoso:** Thank you for the request.

We are interested in this but have no estimated timeline for when this would be available.

**@HuangDDU:** Is there anyone involved in solving this problem? If not, **can I join this project and solve this problem?** I am interested in **graph deep learning** and hope to integrate this technology into scvi-tools.

**@canergen:** Hi, happy to discuss further. Especially with spatial data graphs are critical but also for single-cell it would be cool. I think best way to get started would be to implement a model in external that uses graph. E.g. https://brbiclab.epfl.ch/projects/stellar/ could be a nice start.

## #3819: Add `weighted_knn_trainer`/`weighted_knn_transfer` utilities from scArches
**State:** open | **Comments:** 2 | **Labels:** enhancement

Hello!

**Is your feature request related to a problem? Please describe.**
I am migrating a workflow from scArches to scvi-tools for the sc-best-practice. Most functionality has a clear equivalent in scvi-tools, but `scarches.utils.weighted_knn_trainer` and `weighted_knn_transfer` have no counterpart.

**Describe the solution you'd like**
Would it be possible to add the functions to e.g. `scvi.tools`? Thank you so much!

**@ori-kron-wis:** Yes, however, this is not in our plan currently.
Would you like to contribute a pull request for that?
Thank you

**@seohyonkim:** yes sure! I'll ping you in the PR once I have it ready. Thank you!

## #1456: Within cluster DE test
**State:** open | **Comments:** 2 | **Labels:** enhancement, good first issue, differential expression, P2

scVI used to have a within cluster DE test that I used often, but I no longer see this functionality in scvi-tools. Is it possible to add it back?

This would be a differential expression function where a "groupby" argument would specify a set of groups (e.g., cell clusters) and a "states" argument would specify the relevant comparison to make (e.g., case vs control). The output would include the DE test results from a comparison of cases vs controls within each specified group.

**@adamgayoso:** @PierreBoyeau what do you think?

**@PierreBoyeau:** It sounds like it would be relevant to include it back. Do you remember why we removed this feature?

## #3839: Model request: scPhere (hyperspherical / hyperbolic latent embedding for scRNA-seq)
**State:** open | **Comments:** 1 | **Labels:** enhancement

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

## #3734: Improving SCVI for low-count cells through self-supervised augmentation
**State:** open | **Comments:** 1 | **Labels:** enhancement

Hi,

A paper has recently been written about improving scVI for low count cells using binomial thinning and a cross-correlation loss. It looks like this extension of scVI improves on the integration of low count cells based on the paper results. I thought this may be of interest for you and that you may consider incorporating this into scvi-tools at some point.

Paper link: https://www.biorxiv.org/content/10.64898/2026.02.11.705441v1.full.pdf

**@ori-kron-wis:** Thank you @chelseabright96 , we are well aware of it and have been collaborating with Valentine for a long time, so we might as well implement it.

## #3647: Allow custom label_key for scib-metrics in scvi.autotune
**State:** open | **Comments:** 1 | **Labels:** enhancement

**Is your feature request related to a problem? Please describe.**
When using `scvi.autotune.run_autotune` with scIB metrics for multi-modal integration, I cannot specify which .obs columns should be used as labels for autotune with scib-metrics. The autotune framework only uses the model's internally registered labels fields from the data manager. `setup_mudata` does not support `labels_key`, so label-dependent scib metrics cannot access biologically meaningful labels like tissue or cell type that exist in my data but were not registered during model setup. This makes it impossible to tune hyperparameters using tissue-aware integration quality metrics, even though those labels are available in the dataset.

**Describe the solution you'd like**
I would like `scvi.autotune.run_autotune` and AutotuneExperiment to accept optional `scib_label_key` parameters or allow me to use `label` in the setup process

**@ori-kron-wis:** Hey @catheriz, you are correct with your observation.
However, the best way to deal with this is to implement the label_key into the multi-modal model, running a setup_mudata. We already have the TOTALANVI, and we are working on MULTIANVI (MULTIVI + class label support).

Trying to forcefully fix and have the tuner accept even a different label (say, the above-mentioned solution is done) in a mudata settings is problematic as the tuner gets its inputs from the outputs of a trained model, which are already shuffled and the size of it also depends if a validation was done and so on, so this information has to come from whithin the model, which is either way something we need to do, not only for scib optimization.

Having said that, you can run the tuner without shuffling the data and no val …

## #1177: User guide: gimVI
**State:** open | **Comments:** 0 | **Labels:** user guide, P1, backlog
