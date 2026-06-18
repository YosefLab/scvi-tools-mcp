# scvi-tools Discourse Forum Q&A

Top 30 threads by views (deduplicated across sources).

## Macbook M1 M2 mps acceleration with scVI
**Posts:** 11 | **Views:** 2184

**Question**: Has anyone recently gotten scVI (ideally 1.0.4) working with “GPU” (well, “mps”) acceleration with a Apple ARM M1, M2, or M3? I’ve tried a variety of incantations when installing torch and jax and it either doesn’t see the GPU or does and throws a tensor error which suggests something is very borked somewhere in the software chain. ValueError: Expected parameter loc (Tensor of shape (128, 30)) of distribution Normal(loc: torch.Size([128, 30]), scale: torch.Size([128, 30])) to satisfy the constraint Real(), but found invalid values: tensor([[nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], ..., [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan]], device='mps:0', grad_fn=<L …

**Reply (@TaniaThimraj)**: Same issue here. I am on a Mac M3

**Reply (@pckinnunen_lbl)**: I had similar issues and found this: M1 MAX: GPU available, but not used scvi-tools Hi, what kind of environment are you running this in? I would recommend using a conda version that is native for Mac M1 Miniconda — conda documentation I think this is a pytorch issue, not an scVI issue. I think this is the pytorch issue where they track mps compatibility: github.com/pytorch/pytorch General MPS op coverage tracking issue opened 06:12PM - 18 May 22 UTC albanD feature triaged module: mps ### This issue is to have a centralized place to list and track work on adding s … upport to new ops for the MPS backend. [**MPS operators coverage matrix**](https://qqaatw.github.io/pytorch-mps-ops-coverage/) - The matrix covers most of the supported operators but is not exhaustive. Before you comment below, …

**Reply (@martinkim0)**: I’ve tried testing out the nightly PyTorch versions with the MPS backend and have had no success. Technically it should work since they’ve implemented the lgamma kernel, which was the last one needed to fully support running scVI, but it looks like there might be issues with the implementation or numerical instabilities since I’ve also experienced NaNs in the first epoch of training. So yes, this is an issue on the PyTorch end - unfortunately there’s not much we can do to support the Metal backend.

**Reply (@davemcg)**: Thanks - I’ll keep track of this thread and I hope if anyone gets scVI working on a nightly (or better, stable) branch of pytorch they will report it here!

## MrVI input and interpretation
**Posts:** 29 | **Views:** 1883

**Question**: @Justin_Hong Thanks so much for the MrVI tool and preprint. Really enjoyed reading it. I am just wondering whether the input should be an anndata object of highly variable genes or just the whole cellxgene matrix? I presume hvg selection before hand will bias the analysis depending on what you use as the batch key for hvg selection? Also, any help of further documentation on interpretation of the output would be fab. As I understood it, the distance metrics can compare across samples, clusters or other condition variable, but it wasn’t clear if I can account for sample variation and across disease states at the same time? Thanks for any insight you can offer.

**Reply (@Justin_Hong)**: Hi @Nusob888 , I’m glad you like MrVI, and I hope you find it useful. In our experience using highly variable genes has been helpful to reduce noise in the latent space. We generally used 2000 genes (somewhat arbitrarily). Whether or not you use batch_key will also matter as you suggested, though we did not look into the effect of this closely for the the MrVI paper. Apologies for the sparse documentation. We will have better documentation in the future, but in the mean time feel free to ask questions about the model in discourse. To answer your question, the current model does not incorporate sample metadata (e.g. disease) during training. Rather, the model is only given categorical sample IDs with no groupings of samples otherwise. Then, the distance matrices can be evaluated based on gr …

**Reply (@Nusob888)**: Hi Justin, Thank you for the clarification. So am I right in thinking that the envisioned workflow might be to integrate the data with either another method (e.g. SCVI) or use mrVI. Cluster and annotate the cell types as metadata. Then proceed to look at distances as a guided analysis of cell type composition? Similarly, if one were interested in other sources of grouping such as by transcriptomic perturbations, one could create meta groupings of samples from the distances and then perform differential expression analysis thereafter across cell types of interest?

**Reply (@Justin_Hong)**: Yes, cell types can be annotated via another method or MrVI in the u latent space. The distances do not provide a guided analysis of cell type composition, since the model does not account for differences in sample abundance, just the sample-specific cell states. MrVI would be great for grouping transcriptomic perturbations or samples via the distances. Subsequently, you could take the grouped samples, and do DE analysis across the groups for different cell types of interest.

**Reply (@Nusob888)**: Thats great, thanks Justin. I have performed a test run. However, due to the sparse documentation, it is difficult for me to gauge how best to plot/cluster the data. Do you have idea how far things are from a guided tutorial?

## About the scvi-tools category
**Posts:** 1 | **Views:** 1224

**Question**: For questions about using scvi-tools .

## Using ResolVI’s Unsupervised Mode for Cell Annotation
**Posts:** 10 | **Views:** 537

**Question**: Hello, I apologize for reposting here—I initially submitted this as a GitHub issue, but was kindly redirected to ask usage questions on Discourse. I’m working with Xenium spatial transcriptomics data without any prior cell‐type labels. My core question is: Can ResolVI’s unsupervised mode serve as a reliable foundation for cell annotation? For datasets where no reference labels exist, what is the recommended workflow to apply ResolVI for accurate, unsupervised cell‐type identification? Any guidance on best practices, downstream clustering strategies, or examples of how others have approached annotation in a fully unsupervised setting would be greatly appreciated.

**Reply (@cane11)**: Hi, thanks for reposting. I would recommend using resolVI and do scVIVA on resolVI coordinates. I would potentially provide the labels to resolVI as supervised mode. However, you can also just run clustering on resolVI coordinates. In the cancer case study, we also provided very coarse labels and I think it will be fine. We used ProSeg estimated counts there. In my experience, they tend to produce quite well coarse clusters that can be used for supervised resolVI. Please don’t use resolVI corrected counts in another SCVI model. This can have negative effects and likely doesn’t help much with performance.

**Reply (@cane11)**: In most instances the gains using supervised resolVI are limited. It’s critical in my hands if segmentation is bad like in VisiumHD of spatially dense tissues like cancer tissue or original Xenium segmentation from a couple of Spaceranger versions ago.

**Reply (@qiuzc)**: Thank you for your guidance! To confirm, my planned workflow is: First‐round clustering : Run ResolVI in unsupervised mode, then perform Leiden clustering on the X_resolVI embedding to define coarse lineages. Second‐round subclustering : Input X_resolVI together with those coarse cluster labels into scVIVA to obtain fine‐grained cell‐type annotations. Does that accurately capture your recommendation? Thanks again for your help!

**Reply (@cane11)**: Yes. However, keep in mind that for scVIVA you will identify erroneous signal if segmentation is not optimized. We start there with optimized segmentation. Replacing scANVI with resolVI in scVIVA is safe though and if your segmentation is reasonably good this pipeline makes sense.

## Predict cell type with scANVI for spatial transcriptomics data (Xenium)
**Posts:** 8 | **Views:** 461

**Question**: Hi, Thanks so much for the amazing tools! I was hoping someone could help me. I have an in-house dataset of Xenium 5k data and I would like to predict the cell types using a reference dataset. As such, I am also trying to use scANVI to perform label transfer to improve the accuracy. However, I have a few questions and problems. Questions for scANVI: Should I be subsetting my reference data on just the HVG to improve the accuracy? Should I be subseting my reference data to only include the genes also found in my STx experiment? How the difference in raw counts for the scRNAseq reference and raw counts for the STx that have different expression/number of genes impacting the model? Can the model handle this? How can I adjust for these differences? Is there a better tool or approach I should b …

**Reply (@ori-kron-wis)**: Hey, yes no, that will be “peeking” into the query set (in such a case, you could just train the query set) This is what is scarches is all about, and then based on the trained reference model, you “fine-tune” it over the query data, despite their differences. I suggest following this manual: Reference mapping with SCVI-Tools — scvi-tools However, for more modern spatially methods, you might also try RESOLVI: ResolVI to address noise and biases in spatial transcriptomics — scvi-tools which works on Xenium data as well

**Reply (@spatts14)**: Thanks so much @ori-kron-wis ! I had read about those tools but am not sure if I am implementing them correctly. If this something you have expertise, would you willing to advise if I post the code I’m using?

**Reply (@ori-kron-wis)**: you can post, up to you

**Reply (@spatts14)**: def scVI_integration(config, adata_ref, adata, module_dir): """Integrates STx data with a reference scRNA-seq dataset using scVI. This function performs harmonizes a reference single-cell dataset (e.g., HLCA) to a STx dataset (e.g., Xenium). Args: config (SimpleNamespace or dict): Configuration object containing module-specific parameters, including the module name used to construct figure filenames. adata_ref (anndata.AnnData): Reference scRNA-seq AnnData object containing precomputed embeddings (PCA or UMAP) and cell-type annotations. Should have matching genes with adata_ingest. adata (anndata.AnnData): Spatial dataset formatted for integration, aligned by gene set with the reference (same genes, same order). module_dir (Path): Output directory for saving results Returns: tuple: (adata_ …

## Unstable result
**Posts:** 3 | **Views:** 356

**Question**: Hello, I’m going to analyze the single-cell RNA sequencing data using the scVI framework. After training the scVI model, I found that the result of model.differential_expression is unstable (specifically, it varies from seed to seed). I’ve been trying to solve this problem, but I still haven’t. Please tell me the expected cause. Thank you in advance.

**Reply (@maheshworpaudel5001)**: I am using scvi version 1.4.1 and I am facing the same problem. Any help would be really appreciated.

**Reply (@ori-kron-wis)**: GwangWooKim: Hello, I’m going to analyze the single-cell RNA sequencing data using the scVI framework. After training the scVI model, I found that the result of model.differential_expression is unstable (specifically, it varies from seed to seed). I’ve been trying to solve this problem, but I still haven’t. Please tell me the expected cause. Thank you in advance. The DE analysis is based on sampling, so there will be variability between runs. But given your model converged (check it) and that there is a real biological signal in the data (not just noise, do HVG) - you can run more MC samples to expect more stable results between seeds. Is it version-dependent?

## scVI batch correction clusters all cells from sample in a circle (potential artifact)
**Posts:** 15 | **Views:** 352

**Question**: When using scVI for batch correction and clustering on my single-cell data, I observed an unusual result: all cells from the same sample are clustered in a circle, separated from the rest. Changes to n_latent , training epochs, and HVG numbers did not resolve the circular artifact. The UMAP plot is attached for reference (see cluster 10) image 647×443 41.6 KB Below are my codes: import scanpy as sc import torch import seaborn as sns import numpy as np import matplotlib.pyplot as plt import pandas as pd import random from collections import defaultdict torch.set_float32_matmul_precision("high") pbmc = sc.read_h5ad('/data/work/data/raw_data/ESCC_PBMC_All_Basic_QC.h5ad') # downsample each sample for hvg calculation sample_key = 'sample_info' n_subsample = 5000 pbmc_list = [] for sample in pbm …

**Reply (@ori-kron-wis)**: Hi, Thank you for posting here. Given you have already performed quality control, including filtering out low-quality cells and genes with low expression levels and that the input matrix is indeed the count matrix before transformation (although I dont see you are preserving counts), I see that the actual selection of HVG’s is not really filtered. Try something like: pbmc[:, pbmc.var['highly_variable']] before setup anndata etc’.. You can also increase the number of neighbors in scanpy.pp.neighbors In addition, what we see in the UMAP is the leiden clusters colors, you might also want to compare when you add “sample_info” sc.pl.umap( pbmc, color=["leiden", "sample_info","tmp_info"], ncols=3, frameon=False, ) Then you should see the integration

**Reply (@CocoConstant)**: Hi, Thank you for your prompt reply and suggestions. I follow your suggestion subsetting the HVG and increasing the number of neighbors from 15 to 25. And I see the strange circle still here. hvg_genes = pbmc_meger.var[pbmc_meger.var['highly_variable']].index.tolist() pbmc.var['highly_variable'] = pbmc.var_names.isin(hvg_genes) pbmc = pbmc[:, pbmc.var['highly_variable']] sc.pp.normalize_total(pbmc, target_sum=1e4) sc.pp.log1p(pbmc) pbmc.raw = pbmc scvi.model.SCVI.setup_anndata(pbmc, layer="counts", batch_key="sample_info", continuous_covariate_keys=['doublet_score', 'n_genes_by_counts'], categorical_covariate_keys=['patient_num']) model = scvi.model.SCVI(pbmc, n_layers=2, n_latent=30, gene_likelihood="nb") model.train(batch_size=512, max_epochs=32) latent = model.get_latent_representation( …

**Reply (@ori-kron-wis)**: OK, so we do see integration of this circle from different samples. I see that you used the doublet score as a continuous covariate, why is that? usually it used to filter cells. I suspect that in your case those cells are exactly this circle. Can you repeat without those continuous covariates? (other option to color the UMP by doublet score)

**Reply (@CocoConstant)**: Actually, I’m afraid that the double score will affect my result after filtering out double cells, so I added it as a continuous covariate. But the issue still exists even after I delete all continuous covariates. scvi.model.SCVI.setup_anndata(pbmc, layer="counts", batch_key="sample_info", categorical_covariate_keys=['patient_num']) image 1124×478 72.9 KB image 572×440 42.5 KB I also tried using Harmony for batch correction, and it yielded good results. However, because of the matched downstream analysis and the rich set of functions, I prefer to use scVI to complete this task. But I truly don’t know how to fix this problem . I’m looking forward to your reply! the result of batch correction with Harmony image 1150×971 240 KB

## Domain adaptation to pre-train batch correction model using paired data
**Posts:** 13 | **Views:** 298

**Question**: Good afternoon scvi team! I am very new to the scvi tool and moslty have been working with scRNA-seq data within R environment. I came around a specific issue which scvi could potentially be well suited for so I would love to learn more and would appreciate any guidance. I would like to adapt scVI to learn a transformation between two batches being RNA sequencing protocols. I have data where both protocols were applied to cells from the same samples (so I have “ideal” comparison pairs between batches). Ideally, I’d like to pre-train a model on these “ideal” matched samples that could take the sample of one batch and map it into the “space” of another batch. I want to then save this model for further use on non-ideal/regular data to map it from one protocol space to the other. If this works …

**Reply (@ori-kron-wis)**: Hi Theres no out of the box function to do this, but I suggest to run a scarches method with a tweak at the end: For the reference: train a scvi model with tech/protocol as batch key with both protocols “matched” data. You can also do it as a scanvi model if you have the cell type labels data for each sample, it will be even more accurate, but not mandatory. For the query: you use the new data that came from just one of the protocols and run the scarches scheme on it to create a new, fine tuned model (it will still “remember” the missing protocol batch) Finally apply the fine tuned query model get_normalized_expression function with transform_batch to the missing protocol and library_size=“latent”. A sort of imputing (or reconstructing) the other protocol gene expression. You can validate …

**Reply (@Valerie)**: Dear Ori, Thank you so much for the detailed explanation — this approach makes a lot of sense. I had a follow-up question regarding the use of paired samples: as I understand, the model will learn from having both protocols represented in training via the batch_key , but is there a way to more directly leverage the fact that many of these samples are “paired” — they come from the same individual but were processed using two different protocols? In my dataset, most of these matched pairs come from different tissues, so while there’s substantial biological variation across sample_id s, within a given pair (same sample_id ) the main difference should only be the protocol. So is there a way to integrate sample_id into training — perhaps via additional conditioning or contrastive learning — hel …

**Reply (@cane11)**: Hi, this type of hierarchical batch effects can be modeled with MrVI. To improve integration of different technologies you might want to check sysVI.

**Reply (@Valerie)**: I see — I’ll definitely look into those suggestions! I think what I’m aiming for might be slightly different: I’d like to treat the paired samples as a kind of ideal supervision — where a sample from one protocol (e.g., batch 1 ) can be directly compared to its counterpart from the other protocol ( batch 2 ) because they come from the same individual. Rather than treating sample_id as a batch effect, I was thinking of using it to guide the model — so that batch 1 and batch 2 representations from the same sample are explicitly aligned or used in a loss. The unmatched samples from different individuals wouldn’t really need to “see” each other at all — the focus would just be on learning a mapping via those matched pairs. Does that sound reasonable, or would that require deeper customization? …

## Shared cell types not mixing when integrating datasets from different species
**Posts:** 5 | **Views:** 255

**Question**: Hello, I am attempting to integrate datasets of the same tissue from different species. Some of the datasets are single-cell while some are single-nucleus. I thought that SCVI would work well for this task, however, as seen in the UMAPs below there is almost no integration of the different datasets, even from the same species. Using the consolidated cell-type labels from the original datasets, it seems shared cell types are in the same region of the umap, but the common cells from the different datasets do not mix (bottom umap). Below I have the code I used to make the umaps, where I used Sample and Method (single-cell vs. single-nuc) as categorical covariates. However, I have also tried other models such as: scvi.model.SCVI.setup_anndata(adata, layer = "counts", categorical_covariate_keys …

**Reply (@fcaretti)**: Hi! It seems that the current default for scvi is that encode_covariates=False ( scvi-tools/src/scvi/module/_vae.py at main · scverse/scvi-tools · GitHub ) while it is True for the batch key. Try with encode_covariates = True so that also the encoder sees them, hope it solves it for you!

**Reply (@sandcell10)**: Hello, thank you for your reply! Interesting that the default for encode_covariates is false. I am surprised this is not mentioned in the scvi integration vignettes. I tried setting encode_covariates=True. From the documentation it seems I would set this in the scvi.model.SCVI command. I also tried setting sample to the batch key instead of a categorical covariate. The updated lines of code are below. Unfortunately, it seems that the datasets still did not integrate well for the most part. I ran my code on a subset of the datasets this time for simplicity and for speed. These three datasets are all single-cell and mouse, so there is less variation than in the example I posted previously. Any other suggestions of what could potentially be preventing the successful integration? Feel free to …

**Reply (@cane11)**: For cross-species and cross-technology integration you might want to check sysVI. This is out-of-scope for regular scVI due to drastic batch effects. Encode covariates is especially not part of the original scVI publication. I marked bad experiences adding many continuous covariates with worse latent space. Apart from that the training looks fine. Be aware that harmony directly targets integration and often integrates more with heavy batch effects, while scVI only integrates if cells are similar to each other.

**Reply (@sandcell10)**: Hi @cane11 , thank you for this information, it is very helpful! I was checking out sysVI and it looks like it will be better suited for these datasets. A few follow up questions: With regards to your comment about adding many continuous covariates, are you saying that sometimes more continuous covariates leads to worse integration? Does the same go with multiple categorical covariates? Basically, is it sometimes more beneficial to go with a simpler model? With regards to your comment about Harmony, would you say that Harmony prioritizes integration at the expense of real variation between batches? If so, would this be considered a bad thing? I would imagine it would depend on what the goals of the integration are, but would love some perspective. Feel free to let me know your thoughts and …

## Best practices for downstream analysis of Resolvi-corrected data
**Posts:** 3 | **Views:** 243

**Question**: Dear scverse team, Thank you for all your efforts in creating this incredible software library. I have a question about resolvi, which I am using to analyze and corrected batch effects for a set of Xenium datasets. Variants of this question have been asked before but from reading the responses I am still left a bit unsure. I have trained my resolvi model, something like this. import scvi from scvi.external import RESOLVI RESOLVI.setup_anndata(adata, layer='counts', batch_key="sample") resolvi = RESOLVI(adata, n_latent=30, semisupervised=False) resolvi.train(max_epochs=100, enable_progress_bar=True,accelerator="gpu") adata.obsm["X_resolVI"] = resolvae.get_latent_representation() # Create a name for your model folder model_dir = "resolvi_model_2M_cells" # Save the model resolvi.save(model_di …

**Reply (@ori-kron-wis)**: I don’t see any reason why sc.pl.dotplot running on the top genes selected from DE and using X_resolVI and dendrogram=True won’t work: sc.tl.dendrogram(ref_adata, groupby=“resolvi_predicted”, use_rep=“X_resolVI”) sc.pl.dotplot( adata=ref_adata, var_names=sel_markers, groupby=“resolvi_predicted”, dendrogram=True, color_map=“Blues”, swap_axes=True, use_raw=False, standard_scale=“var”, ) @cane11 Can you add your ideas here?

**Reply (@cane11)**: Hi Sam, to clean things up here. Throughout the manuscript we use posterior predictive samples (similar to model.posterior_predictive_sample in scVI). This generated data contains count data and then requires analogous steps to raw data such as count normalization and square root transformation. import numpy as np resolvae=resolvi samples_corr = resolvae.sample_posterior( model=resolvae.module.model_corrected,batch_size=65536, return_sites=["obs"], summary_fun={"post_sample_q50": np.median}, num_samples=3, summary_frequency=30, ) import pandas as pd samples_corr = pd.DataFrame(samples_corr).T adata.layers["generated_expression"] = samples_corr.loc["post_sample_q50", "px_rate"] ``` Instead px_rate are dense count normalized estimates of gene expression (analogous to get_normalized_expressio …

## Is the scVI model applicable to bulk RNA-seq data from cell lines?
**Posts:** 2 | **Views:** 205

**Question**: Hi guys, I know that scVI is primarily designed for modeling UMI-based single-cell RNA-seq counts, but I’m wondering whether it might also be applicable to bulk RNA-seq data from homogeneous cell lines. Since bulk RNA-seq typically uses full-length sequencing protocols, I was thinking it might be possible to preprocess it similarly to Smart-seq2 data. After reviewing the scVI parameters ( scVI — scvi-tools ), I’m curious — if we consider bulk RNA-seq data as essentially the sum of a large number of identical cells, dropout events should be rare. In that case, would I need to adjust any specific parameters related to dropout modeling (e.g. disable zero inflation or tweak dispersion priors) to make scVI suitable for this type of data? Would appreciate any thoughts or suggestions on this.

**Reply (@cane11)**: Hi, you don’t need any adjustment. The division by gene length in some of our tutorials is just so that Smart-Seq2 and 10X become more similar. I would use the default of ZINB reconstruction loss. However, keep in mind that for low sample number (cell number in single cell studies) the model will not generalize well (if you have beyond 500 bulk samples the limitation shouldn’t matter much).

## Deconvolute spatial transcriptomics (visium) with unannotated single-cell (10x)
**Posts:** 4 | **Views:** 194

**Question**: I have a spatial transcriptomics dataset (10x visium) of a tumour microarray and some of the samples have matched single-cell RNA-seq data (10x). I would like to annotate my spatial data with the single-cell data. However the single-cell data is not annotated. Can this be done with any scverse tool?

**Reply (@ori-kron-wis)**: Not sure I followed. Do you have any annotations at all? whether on the spatial data or the single cell data? Basically you can use scvi-tools for annotate your data as a query data but only given you have some suitable reference data which is annotated (scvi/scanvi). Following that you can use other tools to also try to annotate that overlapping part of your spatial data. But you can perhaps auto-annotate your spatial data using tools like cell2location.

**Reply (@cell_kc)**: Hi @ori-kron-wis The matched single-cell data does not have any annotations and is just processed to GEX count matrices. I understand that this needs to be annotated first in order to transfer labels? Does cell2location annotate spatial data based on a single-cell reference? Thanks

**Reply (@ori-kron-wis)**: cell_kc: The matched single-cell data does not have any annotations and is just processed to GEX count matrices. I understand that this needs to be annotated first in order to transfer labels? Yes. I suggested that it will be annotated using a model like scanvi (if you have similar annotated data as references) or cellassign (if you know whether or not each given gene is a marker of different cell types you think you have). cell_kc: Does cell2location annotate spatial data based on a single-cell reference? Yes. that will be the 2nd part , if your RNA-seq data will be annotated you will be able to use it and estimate the annotation of the spatial part with cell2location based on location of cells. I guess there are other tools for that.

## Ablating latent variables in LinearSCVI
**Posts:** 6 | **Views:** 190

**Question**: Hello, and thank you for these amazing and very useful packages. I have trained a series of LDVAE models and suspect that a particular latent variable is driving performance in a subset of evaluation cells. To test this hypothesis, I would like to set that latent variable equal to zero and attempt reconstruction, to see how reconstruction error changes. However, when I naively tried to write my own modifiable reconstruction script, trying to match get_normalized_expression, with something like: latent_rep = np.array(model.get_latent_representation(adata)) loadings = np.array(model.get_loadings()) reconstruction = latent_rep @ loadings.T # as in Svensson 2020 I found that the resulting reconstruction values, which in my understanding are \rho, would often be negative; these appear not to be …

**Reply (@cane11)**: Hi, in the LDVAE model itself, a softmax activation function is used at the output. This makes the model not strictly linear but makes it similar to scVI. Ypu need to use this activation as well. You might want to check out DrVI if you require a strictly linear model (more complex decoder though).

**Reply (@ajaynadig)**: Thank you for the reply! That makes sense and I have implemented the softmax on the decoded expression. The output is correlated with the output of get_normalized_expression, but I am worried that the outputs are still not exactly the same. Below is a minimal example with some simulated expression data that shows the issue: import numpy as np import scanpy as sc import scvi import anndata as ad import matplotlib.pyplot as plt import seaborn as sns import os import pandas as pd # Set random seed for reproducibility np.random.seed(42) scvi.settings.seed = 42 # Generate synthetic data n_cells = 1000 n_genes = 200 n_latent = 10 # Create random count data from negative binomial raw_counts = np.random.negative_binomial(5, 0.3, size=(n_cells, n_genes)) # Create AnnData object with raw counts adat …

**Reply (@cane11)**: There is another batchnorm in the decoder before applying the softmax by default, though you can disable it by setting batchnorm to „encoder“. Also see: scvi-tools/src/scvi/nn/_base_components.py at 2f1611c5d14392fc5b0e7e9706e2b9d80b20e1d5 · scverse/scvi-tools · GitHub

**Reply (@nbnbhwyy)**: I apologize for bothering you here, and thank you for the excellent tool your team developed. I urgently need to solve this problem. The first step is to match the results of get_normalized_expression . I’ve browsed many related questions, but none have provided a good solution. Therefore, I chose to ask the question in the place that best matches my problem. I’m using the following code to reproduce the results of get_normalized_expression : model.module.generative( z=latent_tensor, library=library_tensor, batch_index=batch_tensor) where z is extracted from the trained scVILD model using the get_latent_representation() function. model.module.generative has four outputs, where px_rate should be the reconstructed representation I need. I’m getting inconsistent results and have encountered s …

## Excluding Ig and ribosomal genes from HVG selection in scVI, best practice?
**Posts:** 2 | **Views:** 171

**Question**: Hi everyone, I’m working with single-cell RNA-seq data from CD45⁺ immune cells (mostly lymphoid lineages) and integrating multiple batches using scVI , which so far has given the best batch correction results. We’re now reprocessing the data after adjusting QC thresholds, and I came across some recent papers where they state: “Prior to PCA, nearest neighbor clustering, and UMAP representations, some genes were filtered from inclusion including those associated with Ig loci (Igk, Igl, or Igh), ribosomal proteins (Rps or Rpl), mitochondrial (mt-), sex (Xist),…” My questions are: Would it make sense to exclude these genes before computing HVGs , so that they never influence the latent space learned by scVI? Or is it better to compute HVGs normally, then remove these specific genes after HVG s …

**Reply (@ori-kron-wis)**: Hey, Generally, the latter is the way to go to not affect the biological signal and other downstream tasks, such as DE. So, keeping them, but not letting them affect the latent space. However, the decision may also be influenced by the problem you are trying to solve. I think you can only gain by performing this, considering (1). In any case, you can always compare the different strategies by running scib-metrics on the generated latent space(s) and DE to validate your expected results.

## How to handle batch effects within the query dataset when using scArches + SCVI?
**Posts:** 2 | **Views:** 155

**Question**: Hello everyone, I’m new to scArches and currently exploring how it works in combination with SCVI , particularly for integrating new datasets into a reference atlas. I’m following this tutorial , where a SCVI model is first trained on a reference dataset and then extended using treeArches to incorporate a new query dataset. From what I understand, the entire query dataset is treated as a single new batch during this “surgery” step when adapting the model. Also, it seems that SCVI expects raw count data for both training and mapping steps. This leads me to a my question: What if my query dataset contains multiple batches itself (for example, samples from different sources or sequencing runs)? Should I split the query dataset by batch and integrate each one individually into the reference? O …

**Reply (@ori-kron-wis)**: Hey, I think the tutorial you linked to is a bit old and perhaps confusing (it uses batch column as “batch_key” but this column is also equal to “study” column, which is used to separate query and reference). Anyway, You can check this tutorial: Reference mapping with SCVI-Tools — scvi-tools Where the query dataset consists of several “tech” batches, and they are all used together as the query data. Obviously your query data should be close to your reference (in terms of species, tissue, cell types and so on) for good reference mapping (“surgery”). However, there are more models beyond SCVI, that might be helpful for you if you want to integrate a query that is very different, such as SysVI. It might help in your flow (however scarches not fully supported in this model yet)

## Scvi package can't be installed into google colab?
**Posts:** 7 | **Views:** 147

**Question**: image 1185×666 66.2 KB It was working two weeks ago, but now it just doesn’t work.

**Reply (@ori-kron-wis)**: theres a temporary problem with the uv package (not scvi-tools) please add this line, before running the install of scvi_colab and it will work: #A Manual fix to uv issue in Colab, see: https://github.com/astral-sh/uv/issues/12724 import os os.environ["UV_CONSTRAINT"] = os.environ["UV_BUILD_CONSTRAINT"] = ""

**Reply (@cane11)**: Could we add this to the scVI-colab package or does it need to be called outside of it?

**Reply (@Jihua-Liu)**: image 805×877 76.2 KB Not exactly sure why this doesn’t work for me.

**Reply (@ori-kron-wis)**: image 1688×538 58.2 KB try it after the installation of scvi-colab, and restart your session. (I installed a specific branch here, but try it with just install()) but youre right, it is not working right now (it worked for me yesterday), I guess their on the fix, at least from what I see in the discussion of the issue Google colab issue · Issue #12724 · astral-sh/uv · GitHub you can still install with !pip install --quiet scvi-tools make no sense to add to the package, its not related to scvi-colab, any package will not work with uv in colab now (also numpy…) w/o the fix.

## Question about get_normalized_expression computation
**Posts:** 4 | **Views:** 133

**Question**: I have trained a TOTALVI model and I am using the get_normalized_expression function to get imputed values for one gene and one protein. It is using mostly CPUs (128 threads) and not the GPU (Volatile GPU-Util = 8%, 2391 Mb). Is it correct that it is a CPU instead of GPU heavy calculation?

**Reply (@ori-kron-wis)**: Generally, yes, but the ratio of how much CPU will work vs GPU depends on the get_normalized_expression function parameters. If, for example, you increase the batch_size and reduce the n_samples, I expect you will see more traffic on GPU than CPU. But it also depends on other parameters such as: transform_batch, indices,… anything really. You can follow it if you set the silent parameter to False and track CPU and GPU usage.

**Reply (@racng)**: Thanks for the suggestion. I have increased batch size and have noticed more traffic on GPU than CPU. CPU usage is now around the n_samples, and there is more GPU memory being used. Is silent a parameter for get_normalized_expression or some other function? I am also concerned that get_normalized_expression might use mdata[‘rna’].X instead of mdata[‘rna’].layers[rna_layer] (whatever rna_layer we specified when we called scvi.model.TOTALVI.setup_mudata ). On github , it says: post = self._make_data_loader(adata=adata, indices=indices, batch_size=batch_size) ... for tensors in post: x = tensors[REGISTRY_KEYS.X_KEY] y = tensors[REGISTRY_KEYS.PROTEIN_EXP_KEY] I think REGISTRY_KEYS.X_KEY = ‘X’? Does self._make_data_loader know to load the specified rna_layer ?

**Reply (@ori-kron-wis)**: silent is for get_normalized_expression, it will just show you the progress bar of the function, as it works per batch; it might correlate to the GPU and CPU usage. Its ok in terms of the backend. REGISTRY_KEYS.X_KEY = ‘X’ indeed, but it is used with the tensors (or data loading) object, not the mudata. This can be done after model was registered and setup with the mudata/adata, so we know how to map RNA/protein data from this structure to the actual data loading and tensors (the actual thing that flows in the network).

## Issue with multiVI get_normalized_expression and get_normalized_accessibility
**Posts:** 6 | **Views:** 132

**Question**: Hi developers and the community, I’m getting this issue running the MultiVI as instructed in the tutorial: imputed_expression = model.get_normalized_expression() >>> imputed_expression chr1:181000-181500 chr1:191000-191500 chr1:191500-192000 ... chr17:40459500-40460000 chr17:40460000-40460500 chr17:40460500-40461000 A24-110:TATATCCTCATCCACC-1_1_1 5.421411e-06 0.000016 1.114787e-05 ... 1.362917e-06 0.000001 6.866701e-07 A24-236:CAAGAACCATAATCGT-1_1_1 5.591661e-06 0.000017 1.120139e-05 ... 1.344341e-06 0.000001 6.684292e-07 The returned dimension is 73236 x 61817 which matches the input “sc” layer, however, the label seems to be pulled from the input “atac” layer. Also, I tried to pull the normalized_accessibility and have the following error: imputed_accessibility = model.get_normalized_acc …

**Reply (@andywangzhou)**: I think I found a solution… First the get_normalized_expression() is only grabbing the gene_names from the FIRST mod in mudata. Thus if you reorder the rna to the first it solves the first problem. But the issue with get_normalized_accesssibility() persist. Here is a quick edit that solve the problem: else: if return_numpy: return imputed else: # Determine the actual number of columns in the imputed data actual_n_cols = imputed.shape[1] # Get region names from adata if isinstance(adata, MuData): # Try to get region names from atac modality first, then rna if "atac" in adata.mod: region_names = adata["atac"].var_names else: region_names = adata["rna"].var_names else: region_names = adata.var_names # Apply region_mask if it's not a slice if region_mask is not None and not isinstance(region_m …

**Reply (@ori-kron-wis)**: @andywangzhou thank you for this. It surfaced several issues. The order of modalities in which you setup the mudata is important, and we assume rna first. This also applies to Totalvi model as well. The issue with get_normalized_accesssibility size that was based on the rna mod is real and it needed a fix. I opened a PR. It was not used during the tutorial. Note that besides what you wrote, we can not hard-code “rna” or “atac” as a modality selection (although that is the default) as the user can call those modalities by any name.

**Reply (@ori-kron-wis)**: See the fix under this PR: fix: use the modality name and not hard coded "rna" or "atac" in multivi by ori-kron-wis · Pull Request #3622 · scverse/scvi-tools · GitHub

**Reply (@andywangzhou)**: ori-kron-wis: a PR. It was not used during the tutorial. Thank you so much! Yes I was doing a quick fix on the code so I can get my project going. But it is better to allow specify the modality names in the future. About the order of modalities in the mudata, it happened because I was trying to use concat, instead of just mudata. And I found that the order I put in md.concat doesn’t matter - it is going to sort the modalities alphabetically. So I had to flip it as the following. # merge mdata_atac and mdata_sc mdata = md.concat([mdata_sc, mdata_atac], label="dataset") md_atac = mdata.mod["atac"] md_rna = mdata.mod["rna"] md_mvi = md.MuData({"rna": md_rna, "atac": md_atac}) It’ll be helpful to be able to specify the main in the future too! Thank you so much for the well maintaining of the s …

## Is older advice for estimating optimal number of epochs for model training of scVI still recommended?
**Posts:** 7 | **Views:** 123

**Question**: Hi Team, Earlier docs for scVI mention that the number of epochs should scale downwards with number of obs/cells. E.g: “([For] > 100,000 cells) you may only need ~10 epochs.” I cannot find similar advice on the modern docs. Is this advice still valid and should even fewer epochs be used for even larger datasets? docs.scvi-tools.org test_size - 1. Introduction to single-cell Variational Inference (scVI) — scVI... In this introductory tutorial, we go through the different steps of a scVI workflow Thank you in advance, Tim

**Reply (@ori-kron-wis)**: I don’t think it’s relevant anymore, and it really depends on what you are doing. You will need to train until convergence, and you can use the early_stopping parameter for that, but if you are starting from an already trained large model and only finetune it with your cells, yes might be that only a few epochs will be enough.

**Reply (@timslittle)**: Thank you. If I am training a completely new model, what could be unintended consequences of not using the ‘early_stopping’ parameter to ensure convergence?

**Reply (@ori-kron-wis)**: It will just train for as many epochs as you enter, possibly leading to overfitting. You should check your loss curves while doing this.

**Reply (@cane11)**: Also for models trained on 30 million cells of the CELLxGENE census going below 10 epochs was not good for results. We saw little improvement beyond 10 epochs though but decided to train for 20 epochs.

## Issue with scVI VAE reconstruction: High sensitivity to library size and poor rank preservation
**Posts:** 2 | **Views:** 121

**Question**: Hello , I am running scVI VAE tool, with the goal of analyzing both the learned cell embeddings and the reconstructed gene expression. ( i have merfish sample ) I want to verify if the gene ranking is preserved within each reconstructed cell . To do so, i compared the reconstructed profile (R’) vs. Ground Truth (R) for each cell , using Spearman correlation score to assess this rank preservation , and numerous problem arise from that ! the first thing i figure out is that there is a huge bias Toward High Expression/Library Size I observed that the model is extremely sensitive to library size and gene abundance: The higher a gene’s expression (and the higher the cell’s library size), the better the ranking is preserved. ( plot 1 & 2 ) . And overall i have a low rank correlation between R’ a …

**Reply (@ori-kron-wis)**: What you see is largely expected behavior for scVI VAEs on noisy count data like merfish, and given the metric you chose to compare with. The reconstruction loss naturally gives more weight to highly expressed genes, so the model knows to reconstruct them better, while in the lowly expressed ones, relative noise is large. You can, however, tune the KL weight in the loss function to prefer a better reconstruction loss, but as noted, it is also partially an inherent thing with your data (did you select HVG before analysis?). Perhaps also increase the latent space size? Yes, parameters can surely be optimized here better than the default ones. Either way, the model should still be good at batch integration, cell clustering, and noise removal, and you can check it with UMAP, given it converged …

## Corrected count for resolvi
**Posts:** 2 | **Views:** 120

**Question**: Hi, I am wondering what would be the right way of generating a corrected count matrix for downstream analysis from resolvi. The tutorial uses the median of px_rate as generated_expression , while the preprint computed corrected_counts by multiplying counts and px_rate_q25 / (1 + px_rate_q25 + mean_poisson) . From my understanding, the corrected_counts should be the right way to go, is it correct? Thanks in advance!

**Reply (@cane11)**: Throughout the manuscript, I’m using p25 of ‚obs‘ using the corrected model, where I sample only from true expression and set diffusion and background to zero. I think this is a good starting point. In the tutorial, I’m outputting estimated counts using px_rate. If you are afraid of removing expression of some genes, the formula for corrected counts might be beneficial.

## Resolvi differential test does not converge (?)
**Posts:** 6 | **Views:** 118

**Question**: Hi, Thanks for the great tool! I have been using Resolvi to correct for batch effects in my single cell spatial transcriptomics data. Additionally, I m also using it to check for differences between the nuclei-expanded and cellpose-segmented sample datasets. The concatenated dataset is quite large ~ 1553536 cells. After training the model, I tried computing differential expression testing on leiden clusters but even after ~2 hours compute was not done. Additionally, the progress bar shows nothing. *In this screenshot I reran the cell after specifying group1. Is this to be expected since the dataset is large or is there something abnormal happening? Just to mention, I don’t see a spike/change in my GPU/CPU usage after running differential test. Thank you so much for your help!

**Reply (@zimmerma)**: I also have the same problem. Then, I ran scVIVA on the same set of cells (using the resolVI embeddings as suggested in another post) and was able to run differential expression in a much shorter amount of time.

**Reply (@ori-kron-wis)**: It shouldn’t be that slow, but can you verify if you run without batch_correction=True (the default is False)

**Reply (@jairaj-mathur)**: I have experienced the same, differential expression takes 9 hours, where as the step before, resolvi training finishes in 1.5 hours. About 300k cells x 5000 genes

**Reply (@jairaj-mathur)**: @zimmerma Could you please elaborate on how you ran scViva on resolvi for running differential expression?

## Error in training resolvi model
**Posts:** 6 | **Views:** 113

**Question**: Hello, I am running the tutorial for ResolVI. However when I get to the line of code supervised_resolvi.train(max_epochs=50) I get the following error. Exception raised during training. <class ‘NameError’> Input arguments must all be instances of Number, torch.Tensor or objects implementing _ torch_function _. Does anyone know what the issue could be? I am using version 2.9.1+cu128 of torch and 1.4.1 in scvi tools. Thank you for your help and happy holidays. Best Regards, Sam

**Reply (@ori-kron-wis)**: It exists for me as well. Im not sure which package update is responsible for this (numpy, torch, pyro, and so on), but a simple fix exists: github.com/scverse/scvi-tools Fix: Resolvi module lognormal calculation main ← Ori-resolvi-lognormal-fix opened 01:43PM - 28 Dec 25 UTC ori-kron-wis +5 -1

**Reply (@cane11)**: Thanks for fixing. Please keep in mind that we have seen similar issues in the past when not filtering out low counts cells (less than 10 counts). Also in an updated guideline downsample counts should be False by default for sequencing based approaches (by experience).

**Reply (@zimmerma)**: Thank you both very much for your quick responses. Setting downsample to False worked. However, I have Xenium data which is probe based. Would you still recommend setting downsample to False? Also, I know this is a naive question, but could you provide instructions on how to install the latest branch of scvi-tools so I can have the fix ori-kron-wis mentioned above? Thank you very much!

**Reply (@ori-kron-wis)**: it is actually part of the main branch already, so you can install it with: pip install git+https://github.com/scverse/scvi-tools@main

## Does MultiVI support using tile matrix directly instead of peak calling for ATAC input?
**Posts:** 3 | **Views:** 109

**Question**: Hi all, I’m working with 10x multiome data and have processed the ATAC and RNA modalities separately: For ATAC, I used tile matrix (e.g., 5kb bins) and trained a peakVI model. For RNA, I used scVI. Now, I’m planning to use MultiVI for integrative analysis. I have two options: Option A: Use the clusters derived from peakVI to perform peak calling per cluster, merge the peaks, build a unified peak matrix across all cells, and then feed that into MultiVI. Option B (preferred): Skip peak calling entirely, and directly use the tile matrix as input for MultiVI. My questions are: Does MultiVI officially support the use of tile matrix as input for ATAC modality? Would the integration performance or downstream analyses (e.g., latent space, cell type separation) be significantly affected? Any insigh …

**Reply (@ori-kron-wis)**: MultiVI will support any count-based ATAC matrix for this modality. If possible try both ways and compare the downstream analyses results.

**Reply (@Captain_Pam)**: Thank you for your suggestion. I will try both.

## Getting normalized expression
**Posts:** 14 | **Views:** 104

**Question**: Hi, I am working on a big sized scRNAseq atlas with 2 million cells. I want to get the normalized expression. However, since it returns a data frame/numpy array, I run out of memory every time I am trying to retrieve the normalized expressions. I need it for performing DE. Is there any other way to get it? or perform DE between clusters without using it? Thanks, Kam

**Reply (@ori-kron-wis)**: Yes, of course, there’s a direct way to run DE from a scVI-trained model, without the need to get_normalization_expression first: model.differential_expression(…), and you can state if you want to do group vs group, group vs all , by which groups, and so on.. If you still need the whole normalized expression itself, and do not have enough memory, you can extract it in smaller chunks of adatas.

**Reply (@Kray)**: Hi, Thanks for your response. I tried the direct way using model.differential_expression. It throws an out of memory error due to the size of the adata probably. Is there a way to resolve this? or may be extracting the normalized data in smaller chunks might be useful, could you please guide me on how to do it?

**Reply (@ori-kron-wis)**: should be something like: import numpy as np import scipy.sparse as sp chunk_size = 50000 all_chunks = [] for start in range(0, adata.n_obs, chunk_size): end = min(start + chunk_size, adata.n_obs) x = model.get_normalized_expression( adata=adata[start:end], return_numpy=True, ) all_chunks.append(sp.csr_matrix(x)) which will store it in a sparse matrix. Do you really need to run DE on all cells? usually we run group vs all/group, e.g: de_df = model.differential_expression( groupby="cell_type", group1="B_cell", group2="T_cell", )

**Reply (@Kray)**: Thanks a lot! I am looking for cell specific markers so I have generated clusters and performing DE between each cluster vs other clusters.

## Training not using the full GPU
**Posts:** 4 | **Views:** 100

**Question**: So I have been running training couple models recently and I encountered this one problem. scvi has no problem detecting CUDA or the GPU. But the problem is that it is using about 25% of GPU and 20% of VRAMs. Have any of y’all encountered a problem like this? Do you have any tricks to increase the utilization rate? This is a screenshot of nvtop when I am autotuning for hyperparameters. image 1160×770 213 KB

**Reply (@ori-kron-wis)**: Increase your batch_size during training, and the GPU will be more utilized. You will also save runtime.

**Reply (@mys_721tx)**: Thanks for the tip! I was able to get twice the utilization with batch size of 1024. As of 1.4.0.post1 the autotuner somehow does not respect scvi.settings.batch_size and has to be passed as a train_params . image 1160×770 217 KB

**Reply (@ori-kron-wis)**: It’s fine, it is a train parameter. As for the settings batch_size, it is used only if the model’s input is None (the default is a number), but mainly used for the downstream analysis functions. The model expect a valid batch_size, has one as input and you can tune it as you saw. Note to use ray<2.5.1 (as the most recent version has some issue with scvi-tools right now)

## Question about complex experiment
**Posts:** 2 | **Views:** 88

**Question**: Hi everyone, I’m starting a fairly complex experiment that includes 10x single-cell, single-nucleus, and 10x multiome (snRNA-seq + scATAC-seq from the same nucleus), with control and treatment groups spread across all three modalities. I also have some patients for whom I’ve generated two modalities (sc + sn), in case that could be useful for any type of training or modeling. I’d like to run the standard analyses (integration, differential expression, differential abundance, and differential accessibility), but I’m unsure about the best strategy to handle all modalities together. Any recommendations or best practices would be really helpful.

**Reply (@cane11)**: Hi @dackjames unfortunately there is no guide here. This is a hard experimental setup that I would as a first step try to reconsider. It will require major effort to get it working. MultiVI can train on multi-ome data and might do well and integrate RNA and paired RNA/ATAC data. I’m not sure whether snRNA-sequencing and scRNA-sequencing will be integrated well though and sometimes this is challenging. Some ideas: it’s usually good to select shared HVGs, encoding batch key will be helpful, it’s easier if the cell-type composition is the same across experiments. Trying harmony on this might also be a good chance. Beforehand annotate the data separately to verify meaningful integration. Good luck with your project!

## Scvi 1.4.0. model.differential_expression outputs
**Posts:** 2 | **Views:** 85

**Question**: Hello, I am using the scvi version 1.4.0.post1. The model.differential_expression function gives proba_m1, proba_m2, bayes_factor, scale1, scale2, raw_mean1, raw_mean2, non_zeros_proportion1, non_zeros_proportion2, raw_normalized_mean1, raw_normalized_mean2 as output without is_de_fdr_0.05 and lfc_mean columns. How can I filter the results? I have tried the following, which filtered out all of the genes. I appreciate any help, thanks! scvi_de[‘lfc’] = np.log2((scvi_de[‘raw_mean1’] + 1e-6) / (scvi_de[‘raw_mean2’] + 1e-6)) scvi_de[‘proba_de’] = 1 - np.exp(-scvi_de[‘bayes_factor’]) scvi_de[‘pseudo_pval’] = 1 - scvi_de[‘proba_de’] scvi_de[‘pseudo_fdr’] = multipletests(scvi_de[‘pseudo_pval’], method=‘fdr_bh’)[1]

**Reply (@ori-kron-wis)**: You can run it with mode=“change” (default is “vanilla”), it will give you proba_de, lfc, etc and is_de_fdr_0.05, which is how we usually filter by.

## Implementing Warmup to a component based on epoch
**Posts:** 3 | **Views:** 85

**Question**: Hi, This might be a silly question, but I’m trying to implement a warmup schedule for one of the components of my model. I’ve implemented some make-shift solution, but was hoping to avoid digging through the codebase if someone already knows the clean way to do this. For example, is there a straightforward way to access the current epoch from within the module class during training? Thanks in advance!

**Reply (@cane11)**: The correct PyTorch manner is a custom callback with functions like on_epoch_end. For many use cases, it should suffice to just reuse the kl warmup value though.

**Reply (@dbdimitrov)**: Hi, yeah, kl weight was my make-shift solution. Thanks, I will check the existing callback functions

## DestVI.from_rna_model RuntimeError: Error(s) in loading state_dict for FCLayers
**Posts:** 2 | **Views:** 85

**Question**: Hi. I am getting an error running DestVi (scvi-tools 1.3.0). I am basically importing a single cell reference AnnData, subsetting to keep just variable genes, and then finding shared genes with my spatial AnnData. I then fit the scLVM to this subset of my single cell reference data, and finally run DestVI on my spatial data using the single cell model. This is my code: # Import single cell reference anndata adata_ref= sc.read_h5ad('scadata_ref.h5ad') # Filter cells with at least 10 genes sc.pp.filter_genes(adata_ref, min_counts=10) # Save raw counts adata_ref.layers["counts"] = adata_ref.X.copy() # Total-count normalize (library-size correct) sc.pp.normalize_total(adata_ref, target_sum=1e4) # normalize to 10,000 reads per cell # Apply log transformation sc.pp.log1p(adata_ref) # Find highly …

**Reply (@ori-kron-wis)**: Hey, You can perhaps use batch_key=“SampleCondition” for your pre and post process analysis of the data, but the current destVI model requires that its scLVM model will not run with batch_key provided, therefore remove the “batch_key” from CondSCVI.setup_anndata and try again. batch_key applies only to the scRNA, not the spatial data. But this is something we might add in a future upgrade of destVI model (then you will add it to the destVI setup_anndata - but its not ready yet).
