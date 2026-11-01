# scvi-tools Discourse Forum Q&A

264 threads from the scvi-tools category and `scvi` tag with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; threads are only removed once they age out of that window.

## Request for an end-to-end ResolVI tutorial on Visium HD cell segmentation data
**Topic:** 4060 | **Last activity:** 2026-10-11T16:46:04Z
**Posts:** 3 | **Views:** 59 | **Created:** 2026-10-02 | **URL:** https://discourse.scverse.org/t/request-for-an-end-to-end-resolvi-tutorial-on-visium-hd-cell-segmentation-data/4060

**Question**: Dear ResolVI developers, Thank you for developing such a great tool as ResolVI! I am trying to use ResolVI on my Visium HD data. My data has undergone cell segmentation with ProSeg, but I find the ResolVI tutorials somewhat difficult to read, especially for data without pre-existing reference cell types. I have browsed various issues about using ResolVI, including suggestions to combine it with scVIVA. Would the authors consider creating an end-to-end analysis tutorial that starts from ProSeg results and uses ResolVI and scVIVA to complete cell type annotation? This would be very helpful for promoting these two high-resolution spatial transcriptomics algorithms! Thanks a lot! Yuanshui Long

**Reply (@ori-kron-wis)**: Dear Yuanshui, thank you for raising this. We are definitely working on such a tutorial, and an overall walkthrough of both ResolVI and scVIVA will be shown at the upcoming scverse conference workshop on scviva-tools!

**Reply (@longyuanshui1231)**: Dear Ori Keronfeld，thank you very much, I’m really looking forward to it! ---- 回复的原邮件 ---- 发件人 | Ori Kronfeld notifications@forum11.discoursemail.com | | - | 发送日期 | 2026年10月12日 00:29 | 收件人 | longyuanshui1231 longyuanshui1231@163.com | 主题 | scverse: Request for an end-to-end ResolVI tutorial on Visium HD cell segmentation data | Someone replied to your post. | ori-kron-wis October 11 | | - | Dear Yuanshui, thank you for raising this. We are definitely working on such a tutorial, and an overall walkthrough of both ResolVI and scVIVA will be shown at the upcoming scverse conference workshop on scviva-tools!

## Can scVI take as input SCT-normalized data?
**Topic:** 4042 | **Last activity:** 2026-09-08T08:53:42Z
**Posts:** 3 | **Views:** 127 | **Created:** 2026-08-13 | **URL:** https://discourse.scverse.org/t/can-scvi-take-as-input-sct-normalized-data/4042

**Question**: Hi all, i am trying to perform scVI integration on a merged dataset processed in R and normalized with scTransform. I want to use native Python implementation rather than Seurat wrapper, since i want to play around with the actual model, so I converted my object to AnnData. Can I use scVI on SCT-corrected ‘counts’ (not log1p-ed) as input? There is little information around: Seurat purposely allows for SCT assays as scVI input ( see this PR ), while reading from here it seems the exact opposite.

**Reply (@ori-kron-wis)**: Theoretically, it probably won’t break, but SCVI is not designed to have corrected SCT counts, but only to use raw counts for integration (there is an a priori assumption on the input data distribution, and SCVI does its own normalization). You can try, of course, and compare results. The 2 sources do not really contradict each other; it’s just that the Seurat wrapper can’t really give what you need (raw counts) to you - it doesn’t mean that forcing it with its approx counts is the way to go.

**Reply (@gboscagli)**: Hi @ori-kron-wis , Out of curiosity, I tried using scVI with SCT-corrected counts and it doesn’t break indeed. We are currently comparing performance to other integration methods, together with a scVI run on raw counts. The 2 sources do not really contradict each other; it’s just that the Seurat wrapper can’t really give what you need (raw counts) to you - it doesn’t mean that forcing it with its approx counts is the way to go. I understand what you are saying. FYI, I also found this issue in which a contributor admittedly use scVI on SCT. However, regardless of what other people are doing out there, i think that the reason you gave me (unmet data distribution assumptions post-SCT) is enough to resort to the raw counts.

## How to install solo-sc or use hashsolo from scvi?
**Topic:** 1702 | **Last activity:** 2026-08-18T12:23:42Z
**Posts:** 6 | **Views:** 971 | **Created:** 2023-08-21 | **URL:** https://discourse.scverse.org/t/how-to-install-solo-sc-or-use-hashsolo-from-scvi/1702

**Question**: When I attempt to install solo in conda environment lately, I have been encountering the following error. pip install solo-sc Collecting solo-sc Using cached solo-sc-1.3.tar.gz (18 kB) Preparing metadata (setup.py) ... done Collecting ConfigArgParse (from solo-sc) Obtaining dependency information for ConfigArgParse from https://files.pythonhosted.org/packages/6f/b3/b4ac838711fd74a2b4e6f746703cf9dd2cf5462d17dac07e349234e21b97/ConfigArgParse-1.7-py3-none-any.whl.metadata Using cached ConfigArgParse-1.7-py3-none-any.whl.metadata (23 kB) Collecting pandas (from solo-sc) Obtaining dependency information for pandas from https://files.pythonhosted.org/packages/4a/f6/f620ca62365d83e663a255a41b08d2fc2eaf304e0b8b21bb6d62a7390fe3/pandas-2.0.3-cp310-cp310-macosx_11_0_arm64.whl.metadata Downloading pan …

**Reply (@martinkim0)**: Hi, Hashsolo is available through scanpy: scanpy.external.pp.hashsolo — Scanpy 1.9.3 documentation

**Reply (@hmnzo5gy)**: With scanpy.external.pp.hashsolo, I can’t seem to demultiplex because the hashing counts is in .var instead of .obs for the outputs from cellranger multi. How can I modify the cellranger multi/count output to fit the scanpy.external.pp.hashsolo requirement? similar questions has also been asked on the biostars. How to demultiplex data with totalseq B antibodies using hashsolo?

**Reply (@martinkim0)**: I’m assuming that the hashtag oligo (HTO) names are in .var , which means that the hashing counts themselves are in adata.X . If this is the case, you can format your AnnData for hashsolo doing something like the following: Get the list of HTOs in your data: htos = list(adata.var[adata.var["feature_types"] == "Antibody Capture"].index.unique()) Iterate through each HTO, extract counts, and place in .obs : for hto in htos: adata.obs[hto] = adata.X[:, adata.var.index == hto].toarray() No guarantees this will work exactly with your data, you might have to change some variable names, etc.

**Reply (@hmnzo5gy)**: Thank you. It worked for my dataset. The semicolon might be a typo. The code is as the following: import scanpy as sc adata=sc.read_10x_h5("filtered_feature_bc_matrix.h5",gex_only=False) htos = list(adata.var[adata.var["feature_types"] == "Multiplexing Capture"].index.unique()) for hto in htos: adata.obs[hto] = adata.X[:,adata.var.index == hto].toarray() import scanpy.external as sce sce.pp.hashsolo(adata, ['hash1', 'hash2', 'hash3','hash4'])

**Reply (@flying-sheep)**: I’m moving Hashsolo into scanpy.pp and adding a new API that handle the hashtags being anywhere: feat: move hashsolo to `sc.pp` by flying-sheep · Pull Request #4303 · scverse/scanpy · GitHub

## Allowed downstream analysis with get_normalized_expression?
**Topic:** 4039 | **Last activity:** 2026-07-30T09:06:34Z
**Posts:** 7 | **Views:** 230 | **Created:** 2026-07-29 | **URL:** https://discourse.scverse.org/t/allowed-downstream-analysis-with-get-normalized-expression/4039

**Question**: Greetings all, Hope I won’t be redundant with this issue. I am interested in finding an integration tool which returns a full gene-space batch-corrected matrix to use for downstream analysis, and I bumped into scVI’s get_normalized_expression . Reading from other issues , I fully get how this matrix is obtained and what it mathematically means, but the potential usability remains unclear to me. Is this matrix meant to be used for visualization/exploratory analysis only, or can it be used to perform some more advanced downstream tasks at the gene level, such as DE or CNV inference ( as suggested here , even if most methods assume raw counts)? Best, Gabriele

**Reply (@ori-kron-wis)**: It can be used for both, as well as other downstream tasks like imputation, denoising, and counterfactual prediction. When you run scvi’ DE it already uses get_normalized_expression. See our tutorials for more info: Documentation — scvi-tools

**Reply (@gboscagli)**: Thank you for the prompt response. What about running external DE analysis on the extracted matrix instead of native scVI function? From this issue , I see that some statistical frameworks are not recommended with this kind of data.

**Reply (@ori-kron-wis)**: The key issue is not normalization itself: scVI returns model-estimated, denoised expression, rather than directly observed expression data, so classical p-value tests (Wilcoxon, Student t) lose their usual interpretation. You are welcome to try, of course. The DE of scvi does not extract the full matrix, but samples decoded expression values under the fitted posterior distributions of the two populations; that’s the main difference. Besides that, as you saw, it will be more memory-heavy for large-scale data unless using a threshold to make it sparse.

**Reply (@gboscagli)**: I understood the difference between the two approaches. Is it then possible to compute “integrated” clusters on the matrix extracted with get_normalized_expression() and use them as input for differential_expression() in a one-vs-all fashion?

**Reply (@ori-kron-wis)**: Theoretically, yes. DE of scvi will just require you to specify the column name of groups (usually cell types but can also be your very own clusters, achieved in any way you want). We usually cluster based on the latent space, though (memory-efficient and batch denoised). See our tutorials for more information.

**Reply (@gboscagli)**: You are right, that is much more easy. Thank you @ori-kron-wis !

## Within-individual DE/DA with MrVI
**Topic:** 4024 | **Last activity:** 2026-07-15T08:55:44Z
**Posts:** 2 | **Views:** 62 | **Created:** 2026-07-09 | **URL:** https://discourse.scverse.org/t/within-individual-de-da-with-mrvi/4024

**Question**: Hi all, I am running MrVI on data with repeated measures per donor across timepoints. I want to test differential abundance across timepoints while accounting for donor IDs. Current setup_anndata config: MRVI.setup_anndata( adata, layer = "counts", sample_key = "final_label", # combination of donor x timepoint batch_key = "batch", ) Current DA call: da_res = model.differential_abundance(sample_cov_keys=["batch", "donor", "timepoint"\]) My question is: can I interpret donor_log_probs like it has been conditioned on batch and donor IDs? Thanks in advance! Best, Mikhael

**Reply (@ori-kron-wis)**: mdmanurung: donor_log_probs like it has been conditioned on batch and donor IDs? It is not. However, you might artificially achieve that if you select the batch key of MRVI to be a combination of batch and donor. Either way, you can also check it yourself by running the DA with “compute_log_enrichment”: True and see if their patterns correlates (donor and batch)

## SCVI view_anndata_setup causes AttributeError with rich.pretty
**Topic:** 4022 | **Last activity:** 2026-07-08T06:45:06Z
**Posts:** 2 | **Views:** 73 | **Created:** 2026-07-07 | **URL:** https://discourse.scverse.org/t/scvi-view-anndata-setup-causes-attributeerror-with-rich-pretty/4022

**Question**: Hello, I was trying to look at my scvi model using view_anndata_setup , but got the error below that says ‘rich has no attribute pretty’. I was actually able to do everything else, like train my model completely fine. Eventually, I was able to solve the error by calling importing rich.pretty . Looking at the source code of view_anndata_setup , it seems rich is imported, but rich.pretty is not, but I think maybe it should be at least in my case, given my versions (see below). Error: AttributeError: module 'rich' has no attribute 'pretty' Version Info: python 13.3.0, scvi-tools 1.4.1, rich 15.0.0 Installation steps: mamba install conda-forge::scvi-tools pip install --upgrade "jax[cuda12]" pip install --upgrade torch --extra-index-url https://download.pytorch.org/whl/cu126 pip install --upgra …

**Reply (@ori-kron-wis)**: The fix you made was already included in scvi-tools 1.4.3 (rich updated their API), so you can just upgrade your scvi-tools version.

## mrVI and groupby=None
**Topic:** 4017 | **Last activity:** 2026-06-25T06:32:55Z
**Posts:** 3 | **Views:** 96 | **Created:** 2026-06-24 | **URL:** https://discourse.scverse.org/t/mrvi-and-groupby-none/4017

**Question**: Hi, I am fairly new to data analysis and therefore there might be an obvious answer to this, but I hope you can help me figure this out. I have a dataset of immune cells with samples from many different predefined disease “states” within the same disease. I want to figure out of the unsupervised approach mrVI offers is able to group the samples based on these states, or if rather there are other biological groupings that appear instead. But I don’t want to get one clustermap per cell type as the tutorial examplifies, I would like to get one clustermap for the entire dataset, and therefore have set dists = model.get_local_sample_distances(keep_cell=False, groupby=None) . However, I then get the error “ValueError: Undefined computation because not keep_cell and no groupby”. And it seems I do …

**Reply (@cane11)**: Thanks for your interest in MrVI. There is some confusion here (keep_cell keeps the values for each single cell, while groupby defines the summary groups). We provided some evidence in the manuscript that sample stratification of different cell-types can be meaningful and I would recommend to first check the per cell-type stratification. To get a single summary statistic, you can pass in a cell-type key with a unique value for all cells.

**Reply (@mmartimis)**: Thank you for the clarification and quick response! I will try out your suggestions!

## Choosing number of latent variables
**Topic:** 4000 | **Last activity:** 2026-05-26T15:31:09Z
**Posts:** 4 | **Views:** 131 | **Created:** 2026-05-26 | **URL:** https://discourse.scverse.org/t/choosing-number-of-latent-variables/4000

**Question**: Hi, Is there a way to choose between the number of latent variables when doing scvi integration? Does the hyperparameter tuning provide this option? Thanks, Kamalika

**Reply (@ori-kron-wis)**: Yes, of course. You set it when defining the model: SCVI(adata, n_latent=x) In our hyperparameters tuner, one can do: run_autotune( SCVI, adata, metrics=["elbo_validation"], mode="min", search_space={ "model_params": { "n_latent": tune.choice([10, 20]), }, }, ...)

**Reply (@Kray)**: Thanks a lot for your response. Do I need anymore dependencies for running autotune? I have used the following from scvi import autotune from ray import tune and results = autotune.run_autotune( SCVI, adata, metrics=[“elbo_validation”], mode=“min”, search_space={ “model_params”: { “n_latent”: tune.choice([10, 20]), }, }, …) It’s throwing an error regarding hyperopt library. raise ModuleNotFoundError(f"Please install {missing_modules} to use this functionality.") ModuleNotFoundError: Please install [‘hyperopt’] to use this functionality.

**Reply (@ori-kron-wis)**: You need to install hyperopt: pip install hyperopt or originally: pip install scvi-tools[autotune]

## Getting normalized expression
**Topic:** 3976 | **Last activity:** 2026-05-13T09:54:49Z
**Posts:** 14 | **Views:** 399 | **Created:** 2026-05-06 | **URL:** https://discourse.scverse.org/t/getting-normalized-expression/3976

**Question**: Hi, I am working on a big sized scRNAseq atlas with 2 million cells. I want to get the normalized expression. However, since it returns a data frame/numpy array, I run out of memory every time I am trying to retrieve the normalized expressions. I need it for performing DE. Is there any other way to get it? or perform DE between clusters without using it? Thanks, Kam

**Reply (@ori-kron-wis)**: Yes, of course, there’s a direct way to run DE from a scVI-trained model, without the need to get_normalization_expression first: model.differential_expression(…), and you can state if you want to do group vs group, group vs all , by which groups, and so on.. If you still need the whole normalized expression itself, and do not have enough memory, you can extract it in smaller chunks of adatas.

**Reply (@Kray)**: Hi, Thanks for your response. I tried the direct way using model.differential_expression. It throws an out of memory error due to the size of the adata probably. Is there a way to resolve this? or may be extracting the normalized data in smaller chunks might be useful, could you please guide me on how to do it?

**Reply (@ori-kron-wis)**: should be something like: import numpy as np import scipy.sparse as sp chunk_size = 50000 all_chunks = [] for start in range(0, adata.n_obs, chunk_size): end = min(start + chunk_size, adata.n_obs) x = model.get_normalized_expression( adata=adata[start:end], return_numpy=True, ) all_chunks.append(sp.csr_matrix(x)) which will store it in a sparse matrix. Do you really need to run DE on all cells? usually we run group vs all/group, e.g: de_df = model.differential_expression( groupby="cell_type", group1="B_cell", group2="T_cell", )

**Reply (@Kray)**: Thanks a lot! I am looking for cell specific markers so I have generated clusters and performing DE between each cluster vs other clusters.

**Reply (@Kray)**: Can I store the normalized expression as a sparse matrix in h5ad object for future use?

**Reply (@ori-kron-wis)**: Yes, that’s the idea. For the clusters, then just replace groupby to the “cluster_column” and group 1 and 2 to the clusters ids

**Reply (@cane11)**: You will want to add a filter to set counts to zero below a certain threshold like 1e-5 to increase sparsity. However, we usually do not recommend using normalized counts for downstream tasks such as Wilcoxon or t-test.

**Reply (@Kray)**: Is there an option to do that when getting the normalized expression?

**Reply (@ori-kron-wis)**: you need to do that on raw data, as preprocessing with scanpy/anndata, before training the model

**Reply (@cane11)**: ori-kron-wis: x = model.get_normalized_expression( adata=adata[start:end], return_numpy=True, ) I meant at this step for x you can set a filter and set counts to zero below this threshold.

**Reply (@cane11)**: It might be also worth to compute posterior predictive samples - those are the counts sampled from the negative binomial distribution using the learned parameters from scVI.

**Reply (@Kray)**: Thanks a lot! Could you please tell me the use of computing the posterior predictive samples? I am new to this topic and learning about it.

**Reply (@cane11)**: scvi.model.SCVI — scvi-tools and we described the use of it in the scvi-hub manuscripthttps://www.nature.com/articles/s41592-025-02799-9.

## Using curated marker genes together with HVGs for scVI feature selection in adult skeletal muscle snRNA-seq
**Topic:** 3983 | **Last activity:** 2026-05-12T05:43:38Z
**Posts:** 2 | **Views:** 80 | **Created:** 2026-05-11 | **URL:** https://discourse.scverse.org/t/using-curated-marker-genes-together-with-hvgs-for-scvi-feature-selection-in-adult-skeletal-muscle-snrna-seq/3983

**Question**: Hi scvi-tools team, I would like to ask whether it is methodologically appropriate to train scVI using a feature set that combines highly variable genes with a small number of curated marker genes. I have been working with multiple adult human skeletal muscle single-nucleus RNA-seq datasets. In our datasets, the majority of nuclei are myonuclei, usually more than 85 percent, which makes the data structure quite different from more heterogeneous datasets such as PBMCs. Some biologically important structures that we know are present in the data, such as fiber-type differences, hybrid myonuclei, NMJ-related myonuclei, MTJ-related myonuclei, and atrophic-like myonuclei, may depend on known skeletal muscle marker genes that are not always selected by a standard HVG workflow. I noticed that the …

**Reply (@cane11)**: This is completely fine in my experience. It can be a lot of effort though and might be biased (maybe you missed some cell-types). To make you less biased would stratified downsampling and traditional HVG not be also an option here - take 10k cells from each coarse cluster before running scVI and use Seurat HVG selection on this balanced subset of the data.

## Using ResolVI’s Unsupervised Mode for Cell Annotation
**Topic:** 3762 | **Last activity:** 2026-05-07T12:36:53Z
**Posts:** 10 | **Views:** 775 | **Created:** 2025-08-06 | **URL:** https://discourse.scverse.org/t/using-resolvi-s-unsupervised-mode-for-cell-annotation/3762

**Question**: Hello, I apologize for reposting here—I initially submitted this as a GitHub issue, but was kindly redirected to ask usage questions on Discourse. I’m working with Xenium spatial transcriptomics data without any prior cell‐type labels. My core question is: Can ResolVI’s unsupervised mode serve as a reliable foundation for cell annotation? For datasets where no reference labels exist, what is the recommended workflow to apply ResolVI for accurate, unsupervised cell‐type identification? Any guidance on best practices, downstream clustering strategies, or examples of how others have approached annotation in a fully unsupervised setting would be greatly appreciated.

**Reply (@cane11)**: Hi, thanks for reposting. I would recommend using resolVI and do scVIVA on resolVI coordinates. I would potentially provide the labels to resolVI as supervised mode. However, you can also just run clustering on resolVI coordinates. In the cancer case study, we also provided very coarse labels and I think it will be fine. We used ProSeg estimated counts there. In my experience, they tend to produce quite well coarse clusters that can be used for supervised resolVI. Please don’t use resolVI corrected counts in another SCVI model. This can have negative effects and likely doesn’t help much with performance.

**Reply (@cane11)**: In most instances the gains using supervised resolVI are limited. It’s critical in my hands if segmentation is bad like in VisiumHD of spatially dense tissues like cancer tissue or original Xenium segmentation from a couple of Spaceranger versions ago.

**Reply (@qiuzc)**: Thank you for your guidance! To confirm, my planned workflow is: First‐round clustering : Run ResolVI in unsupervised mode, then perform Leiden clustering on the X_resolVI embedding to define coarse lineages. Second‐round subclustering : Input X_resolVI together with those coarse cluster labels into scVIVA to obtain fine‐grained cell‐type annotations. Does that accurately capture your recommendation? Thanks again for your help!

**Reply (@cane11)**: Yes. However, keep in mind that for scVIVA you will identify erroneous signal if segmentation is not optimized. We start there with optimized segmentation. Replacing scANVI with resolVI in scVIVA is safe though and if your segmentation is reasonably good this pipeline makes sense.

**Reply (@qiuzc)**: Thank you! I will try proseg to get optimized segmentation.

**Reply (@ynanli)**: cane11: Please don’t use resolVI corrected counts in another SCVI model. This can have negative effects and likely doesn’t help much with performance. Hi, thanks for the nice discussion, enjoyed very much. I am thinking of the potential usage of resolVI corrected counts and wonder why it is not recommended to use it on other SCVI models. My first thought is that the recon loss is inaccurate since it is based on NB/ZINB? Take the task of mapping scRNA-Seq to Xenium for instance, could we then use the normalized counts and resolVI corrected counts in models take normalized counts, such as trVAE with MSE loss? Or you don’t see any gains here?

**Reply (@cane11)**: Hi, the generated counts are again distributed as a negative binomial (or Poisson) distribution as we use posterior predictive samples in resolVI. In general predictions of a model contain biases not present in the original data (e.g. 5000 genes are compressed to 10 dimensions). Training a second model on generated counts can increase these biases. For a general discussion, AI models collapse when trained on recursively generated data | Nature provides some ideas. Developing a joint model of scRNA-seq and spatial data is likely more promising. However, in my opinion there is currently no joint model that I can recommend without reservations and we can identify cell-types to a higher resolution in scRNA-seq data compared to spatial data. Transferring labels at this granular resolution will …

**Reply (@litingchen)**: Hi, Happy to see this thread. We are using proseg proceeding resolvi, which we used to generate a 10 dimension latent space for cell type annotation. Since proseg produces transcript counts as float, and resolvi requires intergers as input. @cane11 , can you share what’s your approach?

**Reply (@cane11)**: I don’t use the estimated expression from ProSeg but their assigned counts. I found the estimated counts to sometimes falsely reduce true coexpressed genes.

## Integration challenges in a multi-dataset single cell type maturation atlas
**Topic:** 3969 | **Last activity:** 2026-04-24T15:40:41Z
**Posts:** 3 | **Views:** 107 | **Created:** 2026-04-23 | **URL:** https://discourse.scverse.org/t/integration-challenges-in-a-multi-dataset-single-cell-type-maturation-atlas/3969

**Question**: Hi scverse community, I’m building a single-cell maturation atlas integrating 23 publicly available and in-house datasets spanning embryonic day 7.75 through postnatal day 84 in mice (~58,000 cells after QC). I’m running into a classic biology vs. batch correction tradeoff and would appreciate any advice. Dataset composition: My atlas spans 6 distinct sequencing chemistries: 10x Chromium (whole tissue dissociation) Drop-seq (whole tissue) SCRB-seq / mcSCRB-seq (LP-FACS isolated CMs) 8bp-STRT-seq (manually picked cells) iCell8 Parse Biosciences (split-pool combinatorial indexing) Cell counts per batch group are highly imbalanced — from 48 cells (smallest dataset) to ~16,500 (largest dataset). HVG selection: I selected 3,987 HVGs using scanpy’s highly_variable_genes across all datasets befor …

**Reply (@cane11)**: Hi, in my opinion those cases are very difficult. You can check the organoid atlases HNOCA and HEOCA that dealt with similar problems and came up with a solution and apply this to your data.

**Reply (@grad_student_01)**: thank you, I’ll look into that and give it a shot

## MrVI input and interpretation
**Topic:** 901 | **Last activity:** 2026-04-23T16:42:19Z
**Posts:** 29 | **Views:** 2291 | **Created:** 2022-11-05 | **URL:** https://discourse.scverse.org/t/mrvi-input-and-interpretation/901

**Question**: @Justin_Hong Thanks so much for the MrVI tool and preprint. Really enjoyed reading it. I am just wondering whether the input should be an anndata object of highly variable genes or just the whole cellxgene matrix? I presume hvg selection before hand will bias the analysis depending on what you use as the batch key for hvg selection? Also, any help of further documentation on interpretation of the output would be fab. As I understood it, the distance metrics can compare across samples, clusters or other condition variable, but it wasn’t clear if I can account for sample variation and across disease states at the same time? Thanks for any insight you can offer.

**Reply (@Justin_Hong)**: Hi @Nusob888 , I’m glad you like MrVI, and I hope you find it useful. In our experience using highly variable genes has been helpful to reduce noise in the latent space. We generally used 2000 genes (somewhat arbitrarily). Whether or not you use batch_key will also matter as you suggested, though we did not look into the effect of this closely for the the MrVI paper. Apologies for the sparse documentation. We will have better documentation in the future, but in the mean time feel free to ask questions about the model in discourse. To answer your question, the current model does not incorporate sample metadata (e.g. disease) during training. Rather, the model is only given categorical sample IDs with no groupings of samples otherwise. Then, the distance matrices can be evaluated based on gr …

**Reply (@Nusob888)**: Hi Justin, Thank you for the clarification. So am I right in thinking that the envisioned workflow might be to integrate the data with either another method (e.g. SCVI) or use mrVI. Cluster and annotate the cell types as metadata. Then proceed to look at distances as a guided analysis of cell type composition? Similarly, if one were interested in other sources of grouping such as by transcriptomic perturbations, one could create meta groupings of samples from the distances and then perform differential expression analysis thereafter across cell types of interest?

**Reply (@Justin_Hong)**: Yes, cell types can be annotated via another method or MrVI in the u latent space. The distances do not provide a guided analysis of cell type composition, since the model does not account for differences in sample abundance, just the sample-specific cell states. MrVI would be great for grouping transcriptomic perturbations or samples via the distances. Subsequently, you could take the grouped samples, and do DE analysis across the groups for different cell types of interest.

**Reply (@Nusob888)**: Thats great, thanks Justin. I have performed a test run. However, due to the sparse documentation, it is difficult for me to gauge how best to plot/cluster the data. Do you have idea how far things are from a guided tutorial?

**Reply (@Justin_Hong)**: For now, the best thing to do is to plot both the u and z latent representations to get an understanding of how the data integrates, then to look at the average distance matrix in different clusters if your data. We will likely not have a guided tutorial for this version of MrVI in the near future since we are working hard on the next version of it. We will have more documentation for the next version!

**Reply (@shobhitagrawal1)**: Hi Justin, Again thanks for this great tool. Along the lines of this conversation, I just need a bit of clarity regarding the cell, sample,sample distances. For each cell i get a square matrix of sample, sample representation, I was wondering how to obtain the column and rownames for each matrix, given that the diagonal for each matrix is 0 irrespective of which sample/subject the cell originates from. Sorry for the bother.Thanks

**Reply (@Justin_Hong)**: Sorry for the super late response! This is something we will add with the next version of this package, but in the mean time you can get it like this sample_order = adata.obs.loc[ lambda x: ~x[sample_key].duplicated(keep="first") ].sort_values("_scvi_sample")[sample_key].values

**Reply (@mihem)**: @Justin_Hong thanks for this super useful package. You mentioned elsewhere that there will be a new version including tutorials of MrVI, are there any news on that? Maybe in the meantime, could you more specifically tell us how you would visualize the resulting cell_sample_sample_distances (and/or cell_sample_sample_representations?) So how can they be used to create a heatmap or some other form of visualization to understand how the samples group together? Thank you !!

**Reply (@Justin_Hong)**: @mihem thanks for your interest in MrVI. We’re hoping to get our work soon in the coming months along with all the code. For the cell_sample_sample_distances, we typically use a seaborn clustermap to organize the samples based on the MrVI distances. We also usually average the distance matrices over cells known to belong to some homogenous population (e.g. based on cell type labels). Although we now have some ways of arriving at these groups from the distances themselves by grouping the cells with similar distance matrices. After performing this, it’s a good first step to look at the metadata of the samples within the groups. It can tell you which metadata have the strongest correlation with the MrVI distances.

**Reply (@mihem)**: @Justin_Hong Thank you so much for your quick response! I understand your explanations but have difficulties applying them. cell_sample_sample_distances is a three dimensional array of dimension of shape 22691, 37, 37 in may case. Could you provide some code to produce a heatmap in the way you explained it? Sorry, I am mostly working with dataframe in R (obviously 2D), and don’t find this super obvious how to arrive at a heatmap based on this output (seaborn expect a 2day array). Thanks a lot!

**Reply (@Justin_Hong)**: @mihem Yes, so each element along the first axis of your output represents the sample x sample distance matrix implied by one of the cells in the input. So here you would either take the mean across the entire first axis, or if you believe there to be cell-state-specific heterogeneity in the nature of sample effects, you would split the first axis into groups based on, say cell types, before taking the mean and plotting heatmaps for each of those groups. Does that make sense?

**Reply (@mihem)**: Yes, thank you for the explanation.

**Reply (@Justin_Hong)**: Hi @mihem just to update here in case you missed it, we the new manuscript is up on biorxiv along with an updated version in scvi-tools. You can see all the details in the tweetorial: x.com

**Reply (@Nusob888)**: Hi Justin, Love the updated manuscript. I am looking to revisit MrVI. I still had a few questions, some of which are the same as my prior questions: hvg selection. I note on the quick start tutorial, you have taken the top 10,000 genes and not assigned a batch variable. I note that previously you stated you did not benchmark how this affects the model, but I wonder whether this is a crucial thing to clarify. Reasons being: hvgs selected with a batch label can ignore batch specific hvgs, I would anticipate that this removes sample level variability depending on how you select batch labels for non-multiplexed data globally selecting hvgs also seems like it would ignore batch specific bias. e.g. if one dataset is hugely over-represented, then would this not bias the hvg selection method? On t …

**Reply (@Justin_Hong)**: Hi @Nusob888 , Thanks for revisiting our package, and thank you for the questions. I have just made our reproducibility repo public here: GitHub - YosefLab/mrvi-reproducibility: Nextflow pipeline for MrVI pipelines . The crohn’s analysis is in the notebooks folder in a ipynb. The HVG selection is described in the methods section of the manuscript as: We selected 10,000 highly variable genes using “seurat_v3” flavor in scanpy and using the respective 10X chemistry as batch key. We also filtered cells expressing more than 300 genes, 1K counts, or more than 20 mitochondrial reads, as these cells contained low-quality events. We found that adding the batch key actually would overly index on the batch specific HVGs and miss sample subset specific genes. So other approaches may serve as a compro …

**Reply (@Nusob888)**: Hi @Justin_Hong , Do you know if MRVI has been taken off scvi-tools? I can no longer find it in scvi.external.MRVI since I updated scvi-tools

**Reply (@Nusob888)**: Apologies I figured this out. I forgot it had to be installed from the GitHub. On a side note, is MRVI compatible with scarches? if not, will this be adapted in future versions?

**Reply (@Justin_Hong)**: Hi @Nusob888 , glad you were able to resolve your issue. MRVI is not compatible with scarches and there are no plans at the moment to support it. However, we acknowledge this could be a very valuable direction to take this work!

**Reply (@Nusob888)**: Thanks Justin. Can I just check another aspect of the tutorial. I am trying to do abundance analysis for healthy vs disease 1 (our of 5 disease states). How can we do this with the code provided? sample_cov_keys = ["Status"] # Replace with your sample covariate of interest model.sample_info["Status"] = model.sample_info["Status"].cat.reorder_categories( ["Healthy", "Covid"] ) # Reorder categories such that the coefficient corresponds to Covid de_res = model.differential_expression( sample_cov_keys=sample_cov_keys, store_lfc=True, ) It seems this can only handle two labels is that correct? do you have any case use examples for multiple labels? The reproducibility code is not yet available for: https://www.biorxiv.org/content/10.1101/2024.01.03.573877v2.supplementary-material but it seems li …

**Reply (@cane11)**: Hi, I’m slightly confused because you ask for abundance but copied the code for expression. Can you clarify? Abundance is meant for pairwise comparisons, similar to tools like milo. What type of output would you expect for more than two groups? For expression, you get DE estimates for the learnt linear model coefficient in latent space, which is also always pairwise in comparison to the reference category similar to tools like classical DE.

**Reply (@Nusob888)**: Ah thanks, sorry for the code error. Yes, agree the abundance is always going to be pairwise, but I was wondering if there is a way to perform this without having to subset the data and regenerated the u embeddings for a subset of the data? I guess I am thinking of examples where people might generate a multi-disease atlas. It would be a useful feature to have. on another note, I have been having issues with reproducibility of MRVI described here: Reproducibility issue of MRVI · Issue #105 · YosefLab/mrvi · GitHub Thanks a bunch in advance

**Reply (@Justin_Hong)**: Hi @Nusob888 , thanks for your question. What do you mean exactly by performing DA without having to subset the data an regenerating the u embeddings? Technically you can get a log density score for every cell and sample then just cache these to compute the final DA comparisons for any given subset of cells. Did you want something like this to be exposed to the user? Also, aware of your issue. I moved it to the scvi-tools repo since we have deprecated the mrvi repo entirely. I will be investigating it this week.

**Reply (@Nusob888)**: That’s amazing thanks. And I hadn’t realised this, yes I guess something in the API that allows the user to select the conditions they want to do either DA or DE. Currently if I make an MrVI model of let’s say 16 datasets across 6 disease labels and 1 control label, when I run the following code from the quick start tutorial, I get an error. model.sample_info["Status"] = model.sample_info["Status"].cat.reorder_categories( ["Healthy", "Covid"] I will try to get the exact error message to you when I can, unfortunately our clusters GPU nodes are in demand. But essentially, it cannot reorder two labels from 7. Since we can only do pairwise comparisons, I couldn’t quite see how I can isolate my two labels of interest, without having to re-run a less complex model. I am probably just being a bit …

**Reply (@ggruenhagen3)**: Hello! Reading through the MRVI tutorials and this thread, I have two questions that I think are relevant here: Is it recommended to run MRVI with a high # of variable features? I noticed in the quickstart tutorial 10k genes were used and in the analysis of Tahoe100M, 15k genes were used. This is much greater than the 2-3k typically used in scRNAseq analysis, so I was wondering if that’s due to MRVI working best with large #’s of genes or if it was just a coincednce. I take it from the tutorial and this thread that MRVI is best run on an adata subset by the variable features. However, doesn’t that mean that it won’t be possible to detect differential expression in other genes? If just 2-3k genes are used as variable features, that leaves ~30k genes that won’t be used during in MRVI’s diffe …

**Reply (@ori-kron-wis)**: I think that the number of HVG you keep is a function of the diversity in your data, but also poses a computational limitation. You can do several trials and errors with this number. Noise and uninformative genes will not help for modeling, nor appear as significant in a DE analysis.

**Reply (@cane11)**: Hi, I generally agree. When developing MrVI we realized that it’s performance doesn’t drop as quickly when selecting more hvg compared to a standard scVI model, where selecting 10k genes usually leads to much worse batch integration. It is not entirely clear, why we see this improvement. For downsteam applications, it is desired to have more genes and be able to check e.g. differential expression for those genes. We also have one application, where we skipped hvg entirely and got good results, however, this comes with additional computational costs and batch integration performance might be worse than on e.g. 10k genes.

**Reply (@ggruenhagen3)**: Thank you for the explanation. If I don’t subset the adata by the HVG, but instead keep the HVG encoded in adata.var, it seems that will that allow me to use just HVG during MrVI batch integration while retaining all genes for differential expression analysis. Are there any potential downsides to this or is this not recommended?

**Reply (@cane11)**: To train only on hvg, you have to subset the AnnData file. However, you can create one subset data and then put the results back in the full AnnData. However, genes not used for training can’t be used for downstream functions in MrVI such as differential expression.

## ResolVI Corrected Counts for Segmented Visium HD Data
**Topic:** 3948 | **Last activity:** 2026-04-23T16:40:50Z
**Posts:** 4 | **Views:** 215 | **Created:** 2026-03-27 | **URL:** https://discourse.scverse.org/t/resolvi-corrected-counts-for-segmented-visium-hd-data/3948

**Question**: Hi, I’m trying to understand the correct method for running ResolVI on Visium HD data that has been segmented using proseg as opposed to 8μM bins used in the reproducibility jupyter notebooks. I’m currently following the tutorial which creates the generated expression as follows: samples_corr = resolvi.sample_posterior( model = resolvi.module.model_corrected, return_sites = [‘px_rate’], summary_fun = {‘post_sample_q50’: np.median}, num_samples = 3, summary_frequency = 30, ) samples_corr = pd.DataFrame(samples_corr).T samples = resolvi.sample_posterior( model = resolvi.module.model_residuals, return_sites = [‘mixture_proportions’], summary_fun = {‘post_sample_means’: np.mean}, num_samples = 3, summary_frequency = 100, ) samples = pd.DataFrame(samples).T adata.layers[“generated_expression”] …

**Reply (@cane11)**: Hi, if you want to have an output that can be treated similar to original counts (such as using screen), use “obs” instead of “px_rate”. “px_rate” are the generated counts similar to what we propose to use in scVI. I wouldn’t feed those into scran. For spatial clustering you can use both of these counts, however I would usually recommend getting the latent representation and use this as replacement for steps such as PCA. You might want to check some of our scVI and scANVI tutorials to get a better overview of scvi-tools.

**Reply (@dow527)**: resolvae = resolvi samples_corr = resolvae.sample_posterior( model = resolvae.module.model_corrected, return_sites = [“obs”], summary_fun = {“post_sample_q50”: np.median}, num_samples = 3, summary_frequency = 30, ) samples_corr = pd.DataFrame(samples_corr).T If I run this the samples_corr dataframe returned is empty. Is there something wrong with my input?

**Reply (@cane11)**: Almost: samples_corr = resolvae.sample_posterior( model=resolvae.module.model_corrected, return_sites=['obs'], num_samples=10, return_samples=False, batch_size=1000, summary_frequency=10, return_observed=True, summary_fun=summary_fun) Will do the trick, so just setting return_observed and it will output obs (this variable is observed during training - pyro computes a reconstruction loss and returning it has to be manually defined).

## Correct way to run SOLO for doublet detection
**Topic:** 3949 | **Last activity:** 2026-04-23T09:29:07Z
**Posts:** 3 | **Views:** 141 | **Created:** 2026-03-27 | **URL:** https://discourse.scverse.org/t/correct-way-to-run-solo-for-doublet-detection/3949

**Question**: Hi everyone, I am trying to run SOLO for doublet detection. However, I am not sure what is the correct way. At first, I thought I have to run Solo after sc.pp.highly_variable_genes(adata), but later I realized it makes more sense if I ran Solo in the unfiltered raw dataset. Also, I was not sure if I had to remove the empty droplets, and if this has an effect in the solo training. Another thing I did since I do not have much resources is to train solo in 30 percent of the data and then transfer the training weights to predict the doublets in the whole dataset. Is this a reliable option? Could someone help me to clarify this matter?

**Reply (@ori-kron-wis)**: Remove empty droplets. Try to increase the data you use as much as possible. Limited resources in what way? If you mean it’s a too large adata to fit your memory - you can run with adata backed from disk or use a custom dataloader. Otherwise, if it’s the GPU memory, decrease the batch size. Also just use the raw counts, so no metadata is needed in adata (take more space) Of course, you can split your data to train and test and predict doublets on test. No need to transfer weights. Check you training and validation curves to see if your model works with no overfit. But even then I would choose at least 60% for training (20% validation,20% test).

**Reply (@cane11)**: To add to this, you can definitely run hvg and run SOLO on this smaller data. Keeping all genes is not a requirement of SOLO and might actually be bad for its performance.

## Mapping 10X Xenium 5k data to scRNA-seq reference
**Topic:** 3953 | **Last activity:** 2026-04-23T09:26:33Z
**Posts:** 4 | **Views:** 239 | **Created:** 2026-04-01 | **URL:** https://discourse.scverse.org/t/mapping-10x-xenium-5k-data-to-scrna-seq-reference/3953

**Question**: Hello everyone, I’m desperately trying to create a latent space from my scRNA-seq reference and map my Xenium cells to that. “Reference mapping with scvi-tools” worked well for each dataset individually, but together, results in basically both UMAPs next to each other. Does anyone have any suggestions on how to embed my Xenium data into my scRNA-seq reference UMAP? Thank you so much for any suggestions and experiences! Best regards,

**Reply (@ori-kron-wis)**: Not so sure why to query Xenium cells from scRNA-seq reference and not train a new model from scratch, but you can do several things that might improve your integration (if not done already): Make sure to use the same gene list. Use SCVI.prepare_query_anndata to align the Xenium gene names to the reference. If the Xenium assay measures many fewer genes than the reference, consider down-sampling the reference gene set to the intersection to avoid poor performance. Make sure the reference model converged afterwards. When calling SCVI.load_query_data , set unfrozen=True or selectively unfreeze parts of the network (e.g. freeze_expression=False , freeze_batchnorm_encoder=False ). This allows more of the network to adapt to Xenium‐specific effects instead of only fitting the newly‑added weights …

**Reply (@Furbelox)**: @ori-kron-wis Thank you! My goal was to improve the notoriously flawed Xenium annotations and “dusty” UMAP by using a single cell RNA-seq reference, annotating that first, then mapping the Xenium cells to that and annotating them via scANVI or a nearest neighbor approach to get cleaner cluster separation (from scRNA-seq) and more valid and finer cell type and cell state annotations. This is a summary of the 2 approaches i tried so far: For the first approach i used the scANVI reference mapping, with a shared embedding space of Xenium and scRNA-seq (HVG 2000 and subsampled to shared genes). vae_ref = scvi.model.SCVI.load(X…”scvi_model_scseq", adata=adata_ref) scanvi_ref = scvi.model.SCANVI.from_scvi_model(vae_ref, labels_key=“celltype”, unlabeled_category=“Unknown”) scanvi_ref.train(acceler …

**Reply (@cane11)**: To address these bleed (or “diffusion”) errors, we developed the resolVI model. However, resolVI doesn’t allow mapping single-cell to spatial data and in my hands this doesn’t work quite well. So instead of relying on this, I usually recomputed cell-type annotations on the spatial data. I have seen convincing applications using scArches to map spatial on single-cells and guess that segmentation errors were minor for these scenarios. However, I did not access raw data there and can’t provide good guidance.

## PeakVI preprocessing for multi-timepoint scATAC-seq when peak coordinates differ slightly across samples
**Topic:** 3967 | **Last activity:** 2026-04-23T09:19:24Z
**Posts:** 3 | **Views:** 83 | **Created:** 2026-04-20 | **URL:** https://discourse.scverse.org/t/peakvi-preprocessing-for-multi-timepoint-scatac-seq-when-peak-coordinates-differ-slightly-across-samples/3967

**Question**: I am working with a scATAC-seq / multi-timepoint reprogramming dataset and want to run PeakVI on a combined AnnData object across samples/timepoints. The issue is that peaks were called separately for each sample, so the peak coordinates differ slightly between samples even when they appear to represent the same biological region. For example, for what looks like the same locus, I see: * Day0: chr1:3210643-3211508 * Day4: chr1:3210640-3211510 * Day7: chr1:3210651-3211509 When I compare exact peak names across samples, the overlap is almost zero, even though biologically these regions seem to correspond to the same accessible site. Example overlap counts: * total peaks: * Day0: 292,251 * Day4: 253,628 * Day7: 198,323 * exact intersections: * Day0 ∩ Day4: 20 * Day0 ∩ Day7: 14 * Day4 ∩ Day7: …

**Reply (@ori-kron-wis)**: I can only suggest posting on scATAC-seq - scverse , as this is more of a pre-processing question rather than scvi per se.

**Reply (@cane11)**: Please check SnapATAC2 tutorials for coherent peak calling across your different samples: Standard pipeline: analyzing 5K PBMC dataset from 10X genomics — SnapATAC2 2.9.0 documentation .

## MRVI Jax Error "Invalid component distribution"
**Topic:** 3959 | **Last activity:** 2026-04-13T14:27:55Z
**Posts:** 4 | **Views:** 108 | **Created:** 2026-04-10 | **URL:** https://discourse.scverse.org/t/mrvi-jax-error-invalid-component-distribution/3959

**Question**: Hello! I am trying to run MRVI on some scRNAseq data and ran into an error (listed below) during model.train() . I initially ran into this error when using jax version 0.9.2 and I saw in the first line of output from model.train() “ UserWarning: Running mrVI with Jax version larger 0.4.35 can cause performance issues ”, so I tried switching jax version 0.4.35, but that caused a different problem where numpyro could no longer be loaded (see error below). Does anyone know what to do to solve these errors? Original Error: AssertionError: Invalid component distribution: Independent. The mixture components must have a support that does not depend on their parameters (expected ParameterFreeConstraint, but found IndependentConstraint(Real(), 1)). Error after trying to switch versions: from model …

**Reply (@ori-kron-wis)**: Can you move on to running it with the “torch” backend? We are dropping the support of Jax backend for MRVI , and the rest of the models, because of those reasons. Running with PyTorch should give the same performance, faster. The 4.3.5 warning is old. We will drop it as well.

**Reply (@ggruenhagen3)**: Wow that worked, thank you so much! I used the scvi.external.TorchMRVI class instead of scvi.external.MRVI and it worked like a charm.

**Reply (@ggruenhagen3)**: Oh I see and setting the backend parameter to “torch” in the normal scvi.external.MRVI class works too.

## CPU memory usage in multi-GPU training
**Topic:** 3944 | **Last activity:** 2026-04-04T08:44:57Z
**Posts:** 7 | **Views:** 220 | **Created:** 2026-03-18 | **URL:** https://discourse.scverse.org/t/cpu-memory-usage-in-multi-gpu-training/3944

**Question**: Hello, I’ve been exploring multi-GPU training in the hopes it’ll speed analysis of our larger (~15-20 million nuclei) datasets. In my initial testing in scvi-tools version 1.4.2, it seems activating multi-GPU training duplicates the process under the hood. For a node with 8 GPUs, CPU memory usage also increases roughly 8-fold. It looks like 8 independent processes are being initialized based on repeated printing of things like the scvi-tools version. Is that the expected behavior? If so, could you explain why its necessary/if there are workarounds? Here is the basic script I’m using: ###################### Load packages ###################### import scvi import torch import scanpy as sc import numpy as np import pandas as pd from datetime import datetime import warnings ################### …

**Reply (@ori-kron-wis)**: @ktravaglini , You are correct. There are X independent Python processes, and each runs the script from line 1 and also loads the full anndata to its memory. This is expected DDP behavior in pytorch. There’s no way around it right now, unless we change the engineering of how we train the models and run multiGPUs. You can, however, run it with smaller memory footprint by reading the adata with on-disk mode ( “backed='r'“ ), but this will be a bit slower overall runtime. Also, make sure that: - scvi.settings.dl_num_workers=0 - scvi.settings.dl_persistent_workers=False

**Reply (@ktravaglini)**: Hello @ori-kron-wis , Thanks for the quick reply, good to know this expected behavior and I haven’t mucked anything up! I suspected we’d have to use backed mode in the end, even with higher memory nodes. Are there recommendations on I/O paradigms for training datasets of this scale? We are running this on AWS and currently streaming the h5ad file into memory from s3 via an s3-fuse mechanism (OK with smaller scale data and even medium scale on a single GPU). I was planning to benchmark downloading the files to solid state scratch drives and running everything as either h5ad or zarr files in backed mode. I’ve also been tracking remote streaming via zarr-v3 Guide/Roadmap — anndata 0.12.10 documentation . Any advice you have here would be extremely helpful! Thanks, Kyle

**Reply (@ori-kron-wis)**: Yes! A few options in fact: Use one of our custom dataloader for reading very large data from disk (e.g: Lamin) Use annbatch ( annbatch — annbatch ) zarr based custom dataloader, still under development, but shows great promise for very large adata. The branch to use it is here: GitHub - scverse/scvi-tools at Ori-annbatch · GitHub , and check out its test function to see how to run it. Annbatch is created by the folks from Anndata. I actually did manage to make today a shared DDP multiGPU addition, given your question. See it in this branch: GitHub - scverse/scvi-tools at Ori-reduce-DPP-memory-footprint · GitHub . you can use it with model.train(…, datasplitter_kwargs={“share_memory”: True}) .It will save memory You will need to install scvi-tools from those branches in order to use those …

**Reply (@ktravaglini)**: Awesome. I’ll look through/try all three and let you know how it goes/if I have any questions. Thank you! -Kyle

**Reply (@ktravaglini)**: Hi Ori, I ran into errors when I initially tried your shared memory branch and wanted to set aside some time to understand what happened. Had some more time today to dive deeper and the outcome always appears to be (base) root@3fce2f775bac:~/capsule/code# ./run + python -u run_mapping_one_donor.py Seed set to 0 2026-04-03 22:17:08.053822 -- scvi-tools version: 1.4.2 2026-04-03 22:21:42.624367 -- Loaded reference dataset /src/scvi-tools/src/scvi/train/_trainrunner.py:116: UserWarning: early_stopping was automatically disabled due to the use of DDP self.trainer = self._trainer_cls( GPU available: True (cuda), used: True TPU available: False, using: 0 TPU cores 💡 Tip: For seamless cloud logging and experiment tracking, try installing [litlogger](https://pypi.org/project/litlogger/) to enable …

**Reply (@ori-kron-wis)**: Ok, let’s continue the discussion in the PR itself (I updated it), as it has become a development thread. Can you try to release the zombie processes in the code? Feel free to add your commits to it.

## How to use GPU partitions (MIGs)?
**Topic:** 3951 | **Last activity:** 2026-03-28T13:13:33Z
**Posts:** 2 | **Views:** 65 | **Created:** 2026-03-27 | **URL:** https://discourse.scverse.org/t/how-to-use-gpu-partitions-migs/3951

**Question**: Hi everyone, I am trying to run scvi as followed, but I wan to speed up by using several GPUs. However, my cluster only gives me MIG partitions from GPUs. Even tho I can request several, when feeding the MIGs to scvi it only recognizes the one in position [0], but it does not recognize the rest, is there any way around, so I can use several devices? scvi.model.SCVI.setup_anndata(adata) vae = scvi.model.SCVI(adata_hvg, n_hidden=128, n_layers=2, n_latent=20, ) vae.train(accelerator=“gpu”, devices=3)

**Reply (@ori-kron-wis)**: I don’t think it’s a scvi-tools API issue, or at least not something that is solvable right now, based on how it is implemented now with torch, lightning and CUDA. Perhaps try to define it before you run the scvi-tools pipeline ( CUDA_VISIBLE_DEVICES ?) I can only suggest using devices=-1. Try to see if the multigpu tutorial works in your case: Train SCVI model with multi-GPU support — scvi-tools

## Unstable result
**Topic:** 1090 | **Last activity:** 2026-03-27T15:54:08Z
**Posts:** 3 | **Views:** 393 | **Created:** 2023-02-01 | **URL:** https://discourse.scverse.org/t/unstable-result/1090

**Question**: Hello, I’m going to analyze the single-cell RNA sequencing data using the scVI framework. After training the scVI model, I found that the result of model.differential_expression is unstable (specifically, it varies from seed to seed). I’ve been trying to solve this problem, but I still haven’t. Please tell me the expected cause. Thank you in advance.

**Reply (@maheshworpaudel5001)**: I am using scvi version 1.4.1 and I am facing the same problem. Any help would be really appreciated.

**Reply (@ori-kron-wis)**: GwangWooKim: Hello, I’m going to analyze the single-cell RNA sequencing data using the scVI framework. After training the scVI model, I found that the result of model.differential_expression is unstable (specifically, it varies from seed to seed). I’ve been trying to solve this problem, but I still haven’t. Please tell me the expected cause. Thank you in advance. The DE analysis is based on sampling, so there will be variability between runs. But given your model converged (check it) and that there is a real biological signal in the data (not just noise, do HVG) - you can run more MC samples to expect more stable results between seeds. Is it version-dependent?

## Macbook M1 M2 mps acceleration with scVI
**Topic:** 2075 | **Last activity:** 2026-03-03T11:43:54Z
**Posts:** 11 | **Views:** 2371 | **Created:** 2024-02-09 | **URL:** https://discourse.scverse.org/t/macbook-m1-m2-mps-acceleration-with-scvi/2075

**Question**: Has anyone recently gotten scVI (ideally 1.0.4) working with “GPU” (well, “mps”) acceleration with a Apple ARM M1, M2, or M3? I’ve tried a variety of incantations when installing torch and jax and it either doesn’t see the GPU or does and throws a tensor error which suggests something is very borked somewhere in the software chain. ValueError: Expected parameter loc (Tensor of shape (128, 30)) of distribution Normal(loc: torch.Size([128, 30]), scale: torch.Size([128, 30])) to satisfy the constraint Real(), but found invalid values: tensor([[nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], ..., [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan], [nan, nan, nan, ..., nan, nan, nan]], device='mps:0', grad_fn=<L …

**Reply (@TaniaThimraj)**: Same issue here. I am on a Mac M3

**Reply (@pckinnunen_lbl)**: I had similar issues and found this: M1 MAX: GPU available, but not used scvi-tools Hi, what kind of environment are you running this in? I would recommend using a conda version that is native for Mac M1 Miniconda — conda documentation I think this is a pytorch issue, not an scVI issue. I think this is the pytorch issue where they track mps compatibility: github.com/pytorch/pytorch General MPS op coverage tracking issue opened 06:12PM - 18 May 22 UTC albanD feature triaged module: mps ### This issue is to have a centralized place to list and track work on adding s … upport to new ops for the MPS backend. [**MPS operators coverage matrix**](https://qqaatw.github.io/pytorch-mps-ops-coverage/) - The matrix covers most of the supported operators but is not exhaustive. Before you comment below, …

**Reply (@martinkim0)**: I’ve tried testing out the nightly PyTorch versions with the MPS backend and have had no success. Technically it should work since they’ve implemented the lgamma kernel, which was the last one needed to fully support running scVI, but it looks like there might be issues with the implementation or numerical instabilities since I’ve also experienced NaNs in the first epoch of training. So yes, this is an issue on the PyTorch end - unfortunately there’s not much we can do to support the Metal backend.

**Reply (@davemcg)**: Thanks - I’ll keep track of this thread and I hope if anyone gets scVI working on a nightly (or better, stable) branch of pytorch they will report it here!

**Reply (@jan-engelmann)**: I ran into the same issue with torch 2.2.2 on mps backend where torch.lgamma produces -inf very confusing to debug. Thanks for tracking it here!

**Reply (@cane11)**: Hi, thanks for the pointer. We tried it beforehand and got Nan errors (that was in the not released torch version). I looked deeper into it, it’s a very strange one. Apparently MPS handles broadcast_all weirdly (and the line torch.lgamma(theta) is producing inf values). This is an example of the behavior: b = torch.full((5, 3), 1., device='mps') c = torch.full((5, 1), 1., device='mps') b, c = broadcast_all(b, c) torch.lgamma(b), torch.lgamma(c) (tensor([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.], [0., 0., 0.], [0., 0., 0.]], device='mps:0'), tensor([[ 0.0000, 0.0000, 0.0000], [ 0.0000, 0.0000, -0.0906], [-0.0906, -0.0906, -0.0906], [-0.0906, -0.0906, -0.0906], [-0.0906, -0.0906, -0.0906]], device='mps:0')) While the actual issue is something the MPS-torch team has to look into (I guess it’s …

**Reply (@cane11)**: I would conclude that the use of MPS even with the proposed change should be only experimental, as we use broadcasting at various locations and different models and there is an issue in pytorch MPS with this: MPS lgamma function changes results when using broadcasting · Issue #132605 · pytorch/pytorch · GitHub

**Reply (@timslittle)**: Hi folks, I was exploring this topic recently and wondering if there have been any updates at all? It looks like the PyTorch lgamma issue is still open so I assume that running scVI with Mac MPS is still out of the questions? Thanks

**Reply (@cane11)**: Hi, yes the most recent scVI-tools supports MOS. However, we needed to explicitly reshape instead of broadcasting, which likely comes with added computational costs.

**Reply (@ori-kron-wis)**: Whoever still sees the posts, the recent scvi-tools version (1.4.2) now supports both MPS and MLX (via model mlxscvi) for MAC. Both show much better performance in terms of runtime vs CPU when running on M3,M4 Pro/Max.

## Regarding resolvi reproducibility scripts and fov for xenium
**Topic:** 3939 | **Last activity:** 2026-03-02T20:11:56Z
**Posts:** 3 | **Views:** 144 | **Created:** 2026-02-24 | **URL:** https://discourse.scverse.org/t/regarding-resolvi-reproducibility-scripts-and-fov-for-xenium/3939

**Question**: Hi, I was going through the resolvi reproducibilty scripts, and for xenium, it seems like fov as batch was used. I was wondering how you were able to get that information in your anndata object, as the table from spatial object from import segmentation does not have fov attached to the obs. Thank you and warm regards Jairaj Mathur

**Reply (@cane11)**: Hi, I’m not sure what “as the table from spatial object from import segmentation” refers to. I’m pretty sure that I didn’t do anything fancy to get the FOV information and believe it was just part of the download from 10X. Did they change the underlying files maybe? In terms of results it does not really matter here and running it without FOV should yield very comparable results.

**Reply (@jairaj-mathur)**: To clarify, when the spatialdata object is created from sdata_io.xenium, the table (anndata object) within that spatialdata object doesnt seem to have the FOV information associated with each cell. I was wondering how did you insert the fov column into the anndata object, which you eventually passed to resolvi.

## Is older advice for estimating optimal number of epochs for model training of scVI still recommended?
**Topic:** 3932 | **Last activity:** 2026-03-01T08:13:51Z
**Posts:** 7 | **Views:** 298 | **Created:** 2026-02-05 | **URL:** https://discourse.scverse.org/t/is-older-advice-for-estimating-optimal-number-of-epochs-for-model-training-of-scvi-still-recommended/3932

**Question**: Hi Team, Earlier docs for scVI mention that the number of epochs should scale downwards with number of obs/cells. E.g: “([For] > 100,000 cells) you may only need ~10 epochs.” I cannot find similar advice on the modern docs. Is this advice still valid and should even fewer epochs be used for even larger datasets? docs.scvi-tools.org test_size - 1. Introduction to single-cell Variational Inference (scVI) — scVI... In this introductory tutorial, we go through the different steps of a scVI workflow Thank you in advance, Tim

**Reply (@ori-kron-wis)**: I don’t think it’s relevant anymore, and it really depends on what you are doing. You will need to train until convergence, and you can use the early_stopping parameter for that, but if you are starting from an already trained large model and only finetune it with your cells, yes might be that only a few epochs will be enough.

**Reply (@timslittle)**: Thank you. If I am training a completely new model, what could be unintended consequences of not using the ‘early_stopping’ parameter to ensure convergence?

**Reply (@ori-kron-wis)**: It will just train for as many epochs as you enter, possibly leading to overfitting. You should check your loss curves while doing this.

**Reply (@cane11)**: Also for models trained on 30 million cells of the CELLxGENE census going below 10 epochs was not good for results. We saw little improvement beyond 10 epochs though but decided to train for 20 epochs.

**Reply (@timslittle)**: Thank you, is it normal for it to keep improving for hundreds of epochs? I used early_stopping=True but it still did all 400 epochs. The loss curves seem quite normal to me: image 540×393 23.8 KB

**Reply (@ori-kron-wis)**: The curves you attached actually show overfit. However, the reconstruction loss doesn’t tell the whole story as it is only one part of ELBO (the other is KL divergence), so probably the general loss or negative ELBO is still decreasing, and this is why, despite you using early_stopping, it made the whole 400 epochs.

## Ablating latent variables in LinearSCVI
**Topic:** 3476 | **Last activity:** 2026-02-24T13:30:57Z
**Posts:** 6 | **Views:** 263 | **Created:** 2025-02-06 | **URL:** https://discourse.scverse.org/t/ablating-latent-variables-in-linearscvi/3476

**Question**: Hello, and thank you for these amazing and very useful packages. I have trained a series of LDVAE models and suspect that a particular latent variable is driving performance in a subset of evaluation cells. To test this hypothesis, I would like to set that latent variable equal to zero and attempt reconstruction, to see how reconstruction error changes. However, when I naively tried to write my own modifiable reconstruction script, trying to match get_normalized_expression, with something like: latent_rep = np.array(model.get_latent_representation(adata)) loadings = np.array(model.get_loadings()) reconstruction = latent_rep @ loadings.T # as in Svensson 2020 I found that the resulting reconstruction values, which in my understanding are \rho, would often be negative; these appear not to be …

**Reply (@cane11)**: Hi, in the LDVAE model itself, a softmax activation function is used at the output. This makes the model not strictly linear but makes it similar to scVI. Ypu need to use this activation as well. You might want to check out DrVI if you require a strictly linear model (more complex decoder though).

**Reply (@ajaynadig)**: Thank you for the reply! That makes sense and I have implemented the softmax on the decoded expression. The output is correlated with the output of get_normalized_expression, but I am worried that the outputs are still not exactly the same. Below is a minimal example with some simulated expression data that shows the issue: import numpy as np import scanpy as sc import scvi import anndata as ad import matplotlib.pyplot as plt import seaborn as sns import os import pandas as pd # Set random seed for reproducibility np.random.seed(42) scvi.settings.seed = 42 # Generate synthetic data n_cells = 1000 n_genes = 200 n_latent = 10 # Create random count data from negative binomial raw_counts = np.random.negative_binomial(5, 0.3, size=(n_cells, n_genes)) # Create AnnData object with raw counts adat …

**Reply (@cane11)**: There is another batchnorm in the decoder before applying the softmax by default, though you can disable it by setting batchnorm to „encoder“. Also see: scvi-tools/src/scvi/nn/_base_components.py at 2f1611c5d14392fc5b0e7e9706e2b9d80b20e1d5 · scverse/scvi-tools · GitHub

**Reply (@nbnbhwyy)**: I apologize for bothering you here, and thank you for the excellent tool your team developed. I urgently need to solve this problem. The first step is to match the results of get_normalized_expression . I’ve browsed many related questions, but none have provided a good solution. Therefore, I chose to ask the question in the place that best matches my problem. I’m using the following code to reproduce the results of get_normalized_expression : model.module.generative( z=latent_tensor, library=library_tensor, batch_index=batch_tensor) where z is extracted from the trained scVILD model using the get_latent_representation() function. model.module.generative has four outputs, where px_rate should be the reconstructed representation I need. I’m getting inconsistent results and have encountered s …

**Reply (@ori-kron-wis)**: If you train without batch covariate, you will get: adata.obs["_scvi_batch"] == 0 So use batch_index as 0 tensor when run generative() In terms of library size, did you try to apply log on it first? No, do not normelize the latent space you got from get_latent_representation. The decoder do not assume it.

## Scvi-tools not allowing me to download cellxgene census data
**Topic:** 3926 | **Last activity:** 2026-01-28T20:21:22Z
**Posts:** 3 | **Views:** 97 | **Created:** 2026-01-28 | **URL:** https://discourse.scverse.org/t/scvi-tools-not-allowing-me-to-download-cellxgene-census-data/3926

**Question**: Hi there, I am trying to follow the tutorial here: Project name not set Use pretrained models of scVI-hub for CELLxGENE This notebook was contributed by Can Ergen and Martin Kim. Original article: Scvi-hub: an actionable repository for model-driven single cell analysis https://www.biorxiv.org/content/10.1101/2024.03... I basically want to take the census data and query my own dataset against all the census data. I am running into the following error when I try to do the tutorial’s step model.load_model(adata=adata[adata.obs["is_primary_data"]].copy()) ValueError: It appears you are trying to load a non-minified model with minified adata This seems like maybe it’s an issue that was introduced in a recent scvi-tools update? The tutorial specifically says that we are going to use minified ada …

**Reply (@ori-kron-wis)**: Hey @igrisch , You are correct, it was a bug in the latest versions. I added a fix which you can see and install from here: GitHub - scverse/scvi-tools at Ori-minified-model-load-bug , it will be released in the next version soon. Tutorials will also be updated with minor fixes and work afterwards. As for the other question, we have several tutorials that show how to query from cellxgene , which is TiledbSoma database. There are also online interactive tools to do it ( AI-Supported Virtual Cells Platform From Biohub ), if this is what you asked for.

**Reply (@igrisch)**: Thank you so much for the prompt response! I will look into the interactive tool.

## Does Decipher require cell type annotation
**Topic:** 3920 | **Last activity:** 2026-01-28T09:54:26Z
**Posts:** 7 | **Views:** 178 | **Created:** 2026-01-21 | **URL:** https://discourse.scverse.org/t/does-decipher-require-cell-type-annotation/3920

**Question**: Hello, I am planning to use decipher to batch correct my single cell embryo data across developmental stage, and i was wondering if the method requires annotation since i only have an adata.obs column for sample stage.

**Reply (@ori-kron-wis)**: No, you dont. You can use it for plotting. @Justin_Hong any other thoughts?

**Reply (@BiggusDikkusMaximus)**: can i use for batch correction across developmental stages? and how does it compare to other scVI tools in that regard?

**Reply (@ori-kron-wis)**: Right now, the implementation in scvi-tools, doesnt support setup_anndata with batch_key, so that’s the main difference.

**Reply (@Justin_Hong)**: Ori is correct in that decipher is not intended to explicitly use a batch key to correct for batch correct. Instead, it relies on the data bottleneck to prioritize biological variation over batch variation. For a biological covariate like developmental stage I would recommend using a different model like scVI to correct these effects.

**Reply (@BiggusDikkusMaximus)**: Thank you for the response, but the assumption i got from decipher that it does take into account transcription change that would occur in different developmental stage. or am i missing something? for scVI, i have different embryo some from the same developmental stage, each embryo part (e.g. Limb, Head) was sequenced as a different sample. would the following be correct as a setup: SysVI.setup_anndata( adata=adata, batch_key=“embryo”, categorical_covariate_keys=[“sample”], )

**Reply (@ori-kron-wis)**: for sysvi, it seems correct, although if it will not work you can also try to use a combination of all embryo-tissue couples as batch_key as they both have substantial batch effects.

## Best practices for downstream analysis of Resolvi-corrected data
**Topic:** 3906 | **Last activity:** 2026-01-27T05:09:35Z
**Posts:** 3 | **Views:** 405 | **Created:** 2026-01-02 | **URL:** https://discourse.scverse.org/t/best-practices-for-downstream-analysis-of-resolvi-corrected-data/3906

**Question**: Dear scverse team, Thank you for all your efforts in creating this incredible software library. I have a question about resolvi, which I am using to analyze and corrected batch effects for a set of Xenium datasets. Variants of this question have been asked before but from reading the responses I am still left a bit unsure. I have trained my resolvi model, something like this. import scvi from scvi.external import RESOLVI RESOLVI.setup_anndata(adata, layer='counts', batch_key="sample") resolvi = RESOLVI(adata, n_latent=30, semisupervised=False) resolvi.train(max_epochs=100, enable_progress_bar=True,accelerator="gpu") adata.obsm["X_resolVI"] = resolvae.get_latent_representation() # Create a name for your model folder model_dir = "resolvi_model_2M_cells" # Save the model resolvi.save(model_di …

**Reply (@ori-kron-wis)**: I don’t see any reason why sc.pl.dotplot running on the top genes selected from DE and using X_resolVI and dendrogram=True won’t work: sc.tl.dendrogram(ref_adata, groupby=“resolvi_predicted”, use_rep=“X_resolVI”) sc.pl.dotplot( adata=ref_adata, var_names=sel_markers, groupby=“resolvi_predicted”, dendrogram=True, color_map=“Blues”, swap_axes=True, use_raw=False, standard_scale=“var”, ) @cane11 Can you add your ideas here?

**Reply (@cane11)**: Hi Sam, to clean things up here. Throughout the manuscript we use posterior predictive samples (similar to model.posterior_predictive_sample in scVI). This generated data contains count data and then requires analogous steps to raw data such as count normalization and square root transformation. import numpy as np resolvae=resolvi samples_corr = resolvae.sample_posterior( model=resolvae.module.model_corrected,batch_size=65536, return_sites=["obs"], summary_fun={"post_sample_q50": np.median}, num_samples=3, summary_frequency=30, ) import pandas as pd samples_corr = pd.DataFrame(samples_corr).T adata.layers["generated_expression"] = samples_corr.loc["post_sample_q50", "px_rate"] ``` Instead px_rate are dense count normalized estimates of gene expression (analogous to get_normalized_expressio …

## Resolvi differential test does not converge (?)
**Topic:** 3907 | **Last activity:** 2026-01-15T19:36:24Z
**Posts:** 6 | **Views:** 220 | **Created:** 2026-01-02 | **URL:** https://discourse.scverse.org/t/resolvi-differential-test-does-not-converge/3907

**Question**: Hi, Thanks for the great tool! I have been using Resolvi to correct for batch effects in my single cell spatial transcriptomics data. Additionally, I m also using it to check for differences between the nuclei-expanded and cellpose-segmented sample datasets. The concatenated dataset is quite large ~ 1553536 cells. After training the model, I tried computing differential expression testing on leiden clusters but even after ~2 hours compute was not done. Additionally, the progress bar shows nothing. *In this screenshot I reran the cell after specifying group1. Is this to be expected since the dataset is large or is there something abnormal happening? Just to mention, I don’t see a spike/change in my GPU/CPU usage after running differential test. Thank you so much for your help!

**Reply (@zimmerma)**: I also have the same problem. Then, I ran scVIVA on the same set of cells (using the resolVI embeddings as suggested in another post) and was able to run differential expression in a much shorter amount of time.

**Reply (@ori-kron-wis)**: It shouldn’t be that slow, but can you verify if you run without batch_correction=True (the default is False)

**Reply (@jairaj-mathur)**: I have experienced the same, differential expression takes 9 hours, where as the step before, resolvi training finishes in 1.5 hours. About 300k cells x 5000 genes

**Reply (@jairaj-mathur)**: @zimmerma Could you please elaborate on how you ran scViva on resolvi for running differential expression?

**Reply (@zimmerma)**: Sorry for the delay. I followed the directions from this post: ode-for-cell-annotation/3762 What I did was run Resolvi in unsupervised mode and perform leiden clustering on the X_resolVI embeddings to get clusters. Then I used the X_resolVI embeddings along with the cluster labels as input to scVIVA. From there I used the differential_expression module scVIVA uses.

## Data scaling for cytovi
**Topic:** 3911 | **Last activity:** 2026-01-15T15:16:40Z
**Posts:** 3 | **Views:** 144 | **Created:** 2026-01-11 | **URL:** https://discourse.scverse.org/t/data-scaling-for-cytovi/3911

**Question**: Hi guys, In cytovi tutorial, i see a data scaling step for each batch cytovi.scale(adata_batch1) which by default scale the data to range between 0-1 using sklearn’s MinMaxScaler . Post correction, what is the best way to “untransform” the range to match the original range? One can run transform using the fitted MinMaxScaler object, but then should we: Run transform per batch using the MinMaxScaler object fitted for that batch? Or Fit (but not transform) a new MinMaxScaler object based on data from all batches, then post correction run transform using this fitted MinMaxScaler object? Or Some other suggestion Thanks!

**Reply (@ori-kron-wis)**: In my opinion, you should save MinMaxScaler objects per batch before you continue to use the internal cytovi scale function, then you can use them to untransform per batch, post-analysis. Of course, you can also have this kind of object for all data put together; it all depends on what you want to do following it. @florianingelfinger , any other thoughts?

**Reply (@SofieVG)**: The problem with untransforming per batch, post-analysis, is that then differences between batches are re-introduced (i.e. by applying a different transformation on each batch, the batches will not look similar anymore, even if they were well aligned by cytovi). What we are considering now, is to apply batch specific scaling, do the alignment with cytovi, and then untransform with the scaler object from one of the batches. In theory, if you suggest that can be used on the data from that specific batch, it should also be suited to untransform the others as those will look very similar after the alignment. This avoids learning a separate scaler, and feels closer to the recommended pipeline of first applying a scaling step per batch rather than doing a single scaling across all samples. Furth …

## Imputation/Denoise output
**Topic:** 3913 | **Last activity:** 2026-01-15T07:22:32Z
**Posts:** 2 | **Views:** 121 | **Created:** 2026-01-15 | **URL:** https://discourse.scverse.org/t/imputation-denoise-output/3913

**Question**: When using the code below for data denoise/imputation, how to set the library_size in get_normalized_expression()? to obtain the output in count-scale, rather than normalized output? scvi.model.SCVI.setup_anndata(adata,layer=“counts”) vae = scvi.model.SCVI(adata) vae.train() vae.get_latent_representation() vae.get_normalized_expression() Also, are there any recommendations for parameters in vae.train(),e.g., max_epochs and train_size=0.9; as well as n_samples in get_normalized_expression()? If I have multiple samples in adata, may I input the whole dataset together to do denoise? or do denoise for each sample, then combine the results? Thank you!

**Reply (@ori-kron-wis)**: You can use library_size=“latent” in get_normalized_expression to get count-like output, which is the “closest” to the denoised real counts. Recommended parameters for training really depend on the problem, we set the default max_epochs=400 and train_size=0.9, batch size should be optimal for your GPU memory. But it doesnt have to be like this. What you care about is for model convergence and that it is not overfitting. You can use early stopping for this. See our different tutorials for reference. Increasing n_samples will result in more accurate outputs, but will take more time. You should use sample_id as batch_key when setup the SCVI model, and denoise them jointly (unless the samples really differ in their genes/from different tissues or census completely - there are other models for …

## SCANVI Model Loading Issue: Partial Data and Workaround
**Topic:** 3910 | **Last activity:** 2026-01-11T12:32:23Z
**Posts:** 2 | **Views:** 84 | **Created:** 2026-01-08 | **URL:** https://discourse.scverse.org/t/scanvi-model-loading-issue-partial-data-and-workaround/3910

**Question**: SCANVI Model Loading Issue: Partial Data and Workaround Hello, I’m experiencing an issue when trying to load a pre-trained SCANVI model with partial/incomplete data. The data I used is fully labeled. The model is trained/initiated with the data fully labeled, with all cell types present, and then saved. But when I try to load it with partial data (some cell types missing, but fully labeled), I get a size mismatch error. As a workaround, I noticed that if I add a single placeholder value labeled as the unlabeled_category used for the SCANVI model in the partial dataset, the model loads without issues and can be trained. The placeholder value is simply the last row of the dataset duplicated with the cell type changed to the unlabeled category. So I have these scenarios when I load the model: …

**Reply (@ori-kron-wis)**: When you load the model expects the same registry, inc the same labels, so this won’t work. However, you can query your new data, and it will work, even with fewer labels than originally: SCANVI.load_query_data(adata2, model_path) Where adata2 has partial cell types than original (with/without the original unlabelled category)

## Error in training resolvi model
**Topic:** 3904 | **Last activity:** 2026-01-05T21:10:39Z
**Posts:** 6 | **Views:** 193 | **Created:** 2025-12-24 | **URL:** https://discourse.scverse.org/t/error-in-training-resolvi-model/3904

**Question**: Hello, I am running the tutorial for ResolVI. However when I get to the line of code supervised_resolvi.train(max_epochs=50) I get the following error. Exception raised during training. <class ‘NameError’> Input arguments must all be instances of Number, torch.Tensor or objects implementing _ torch_function _. Does anyone know what the issue could be? I am using version 2.9.1+cu128 of torch and 1.4.1 in scvi tools. Thank you for your help and happy holidays. Best Regards, Sam

**Reply (@ori-kron-wis)**: It exists for me as well. Im not sure which package update is responsible for this (numpy, torch, pyro, and so on), but a simple fix exists: github.com/scverse/scvi-tools Fix: Resolvi module lognormal calculation main ← Ori-resolvi-lognormal-fix opened 01:43PM - 28 Dec 25 UTC ori-kron-wis +5 -1

**Reply (@cane11)**: Thanks for fixing. Please keep in mind that we have seen similar issues in the past when not filtering out low counts cells (less than 10 counts). Also in an updated guideline downsample counts should be False by default for sequencing based approaches (by experience).

**Reply (@zimmerma)**: Thank you both very much for your quick responses. Setting downsample to False worked. However, I have Xenium data which is probe based. Would you still recommend setting downsample to False? Also, I know this is a naive question, but could you provide instructions on how to install the latest branch of scvi-tools so I can have the fix ori-kron-wis mentioned above? Thank you very much!

**Reply (@ori-kron-wis)**: it is actually part of the main branch already, so you can install it with: pip install git+https://github.com/scverse/scvi-tools@main

**Reply (@zimmerma)**: Thank you very much!

## Predict cell type with scANVI for spatial transcriptomics data (Xenium)
**Topic:** 3867 | **Last activity:** 2025-12-28T14:31:08Z
**Posts:** 8 | **Views:** 755 | **Created:** 2025-11-18 | **URL:** https://discourse.scverse.org/t/predict-cell-type-with-scanvi-for-spatial-transcriptomics-data-xenium/3867

**Question**: Hi, Thanks so much for the amazing tools! I was hoping someone could help me. I have an in-house dataset of Xenium 5k data and I would like to predict the cell types using a reference dataset. As such, I am also trying to use scANVI to perform label transfer to improve the accuracy. However, I have a few questions and problems. Questions for scANVI: Should I be subsetting my reference data on just the HVG to improve the accuracy? Should I be subseting my reference data to only include the genes also found in my STx experiment? How the difference in raw counts for the scRNAseq reference and raw counts for the STx that have different expression/number of genes impacting the model? Can the model handle this? How can I adjust for these differences? Is there a better tool or approach I should b …

**Reply (@ori-kron-wis)**: Hey, yes no, that will be “peeking” into the query set (in such a case, you could just train the query set) This is what is scarches is all about, and then based on the trained reference model, you “fine-tune” it over the query data, despite their differences. I suggest following this manual: Reference mapping with SCVI-Tools — scvi-tools However, for more modern spatially methods, you might also try RESOLVI: ResolVI to address noise and biases in spatial transcriptomics — scvi-tools which works on Xenium data as well

**Reply (@spatts14)**: Thanks so much @ori-kron-wis ! I had read about those tools but am not sure if I am implementing them correctly. If this something you have expertise, would you willing to advise if I post the code I’m using?

**Reply (@ori-kron-wis)**: you can post, up to you

**Reply (@spatts14)**: def scVI_integration(config, adata_ref, adata, module_dir): """Integrates STx data with a reference scRNA-seq dataset using scVI. This function performs harmonizes a reference single-cell dataset (e.g., HLCA) to a STx dataset (e.g., Xenium). Args: config (SimpleNamespace or dict): Configuration object containing module-specific parameters, including the module name used to construct figure filenames. adata_ref (anndata.AnnData): Reference scRNA-seq AnnData object containing precomputed embeddings (PCA or UMAP) and cell-type annotations. Should have matching genes with adata_ingest. adata (anndata.AnnData): Spatial dataset formatted for integration, aligned by gene set with the reference (same genes, same order). module_dir (Path): Output directory for saving results Returns: tuple: (adata_ …

**Reply (@cane11)**: I would also train on shared genes. However, scRNA is usually sparser so it might be that you lose some resolution when performing gene subsetting. The code seems correct but a bit bloated. Try adding new columns before concatenating and remove layers before concatenating. It’s make it less error prone. You can transfer labels using the scANVI approach. However for some data we find a kNN classifier in scANVI latent space to perform better. ResolVI only supports spatial data and not integration of spatial and scRNA data. I tend to perform clustering on spatial data after training ResolVI and let an LLM help with annotation or do it manually and I would encourage to do both and double check the results for the integrated space.

**Reply (@spatts14)**: Thanks so much for your feedback! What do you mean by “Try adding new columns before concatenating and remove layers before concatenating.”? Would you recommend using ResoIVI instead or scVI/scANVI or do you typically run both and compare the annotations?

**Reply (@cane11)**: ResolVI is only working to transfer between two spatial datasets and then yes I would recommend it. I recommend to delete adata.layers before concatenation of two datasets if I don’t need the layers downstream.

## Issue with scVI VAE reconstruction: High sensitivity to library size and poor rank preservation
**Topic:** 3883 | **Last activity:** 2025-12-09T14:58:30Z
**Posts:** 2 | **Views:** 188 | **Created:** 2025-12-01 | **URL:** https://discourse.scverse.org/t/issue-with-scvi-vae-reconstruction-high-sensitivity-to-library-size-and-poor-rank-preservation/3883

**Question**: Hello , I am running scVI VAE tool, with the goal of analyzing both the learned cell embeddings and the reconstructed gene expression. ( i have merfish sample ) I want to verify if the gene ranking is preserved within each reconstructed cell . To do so, i compared the reconstructed profile (R’) vs. Ground Truth (R) for each cell , using Spearman correlation score to assess this rank preservation , and numerous problem arise from that ! the first thing i figure out is that there is a huge bias Toward High Expression/Library Size I observed that the model is extremely sensitive to library size and gene abundance: The higher a gene’s expression (and the higher the cell’s library size), the better the ranking is preserved. ( plot 1 & 2 ) . And overall i have a low rank correlation between R’ a …

**Reply (@ori-kron-wis)**: What you see is largely expected behavior for scVI VAEs on noisy count data like merfish, and given the metric you chose to compare with. The reconstruction loss naturally gives more weight to highly expressed genes, so the model knows to reconstruct them better, while in the lowly expressed ones, relative noise is large. You can, however, tune the KL weight in the loss function to prefer a better reconstruction loss, but as noted, it is also partially an inherent thing with your data (did you select HVG before analysis?). Perhaps also increase the latent space size? Yes, parameters can surely be optimized here better than the default ones. Either way, the model should still be good at batch integration, cell clustering, and noise removal, and you can check it with UMAP, given it converged …

## Issue with multiVI get_normalized_expression and get_normalized_accessibility
**Topic:** 3878 | **Last activity:** 2025-12-07T07:22:37Z
**Posts:** 6 | **Views:** 194 | **Created:** 2025-11-25 | **URL:** https://discourse.scverse.org/t/issue-with-multivi-get-normalized-expression-and-get-normalized-accessibility/3878

**Question**: Hi developers and the community, I’m getting this issue running the MultiVI as instructed in the tutorial: imputed_expression = model.get_normalized_expression() >>> imputed_expression chr1:181000-181500 chr1:191000-191500 chr1:191500-192000 ... chr17:40459500-40460000 chr17:40460000-40460500 chr17:40460500-40461000 A24-110:TATATCCTCATCCACC-1_1_1 5.421411e-06 0.000016 1.114787e-05 ... 1.362917e-06 0.000001 6.866701e-07 A24-236:CAAGAACCATAATCGT-1_1_1 5.591661e-06 0.000017 1.120139e-05 ... 1.344341e-06 0.000001 6.684292e-07 The returned dimension is 73236 x 61817 which matches the input “sc” layer, however, the label seems to be pulled from the input “atac” layer. Also, I tried to pull the normalized_accessibility and have the following error: imputed_accessibility = model.get_normalized_acc …

**Reply (@andywangzhou)**: I think I found a solution… First the get_normalized_expression() is only grabbing the gene_names from the FIRST mod in mudata. Thus if you reorder the rna to the first it solves the first problem. But the issue with get_normalized_accesssibility() persist. Here is a quick edit that solve the problem: else: if return_numpy: return imputed else: # Determine the actual number of columns in the imputed data actual_n_cols = imputed.shape[1] # Get region names from adata if isinstance(adata, MuData): # Try to get region names from atac modality first, then rna if "atac" in adata.mod: region_names = adata["atac"].var_names else: region_names = adata["rna"].var_names else: region_names = adata.var_names # Apply region_mask if it's not a slice if region_mask is not None and not isinstance(region_m …

**Reply (@ori-kron-wis)**: @andywangzhou thank you for this. It surfaced several issues. The order of modalities in which you setup the mudata is important, and we assume rna first. This also applies to Totalvi model as well. The issue with get_normalized_accesssibility size that was based on the rna mod is real and it needed a fix. I opened a PR. It was not used during the tutorial. Note that besides what you wrote, we can not hard-code “rna” or “atac” as a modality selection (although that is the default) as the user can call those modalities by any name.

**Reply (@ori-kron-wis)**: See the fix under this PR: fix: use the modality name and not hard coded "rna" or "atac" in multivi by ori-kron-wis · Pull Request #3622 · scverse/scvi-tools · GitHub

**Reply (@andywangzhou)**: ori-kron-wis: a PR. It was not used during the tutorial. Thank you so much! Yes I was doing a quick fix on the code so I can get my project going. But it is better to allow specify the modality names in the future. About the order of modalities in the mudata, it happened because I was trying to use concat, instead of just mudata. And I found that the order I put in md.concat doesn’t matter - it is going to sort the modalities alphabetically. So I had to flip it as the following. # merge mdata_atac and mdata_sc mdata = md.concat([mdata_sc, mdata_atac], label="dataset") md_atac = mdata.mod["atac"] md_rna = mdata.mod["rna"] md_mvi = md.MuData({"rna": md_rna, "atac": md_atac}) It’ll be helpful to be able to specify the main in the future too! Thank you so much for the well maintaining of the s …

**Reply (@ori-kron-wis)**: Absolutely, the ordering will be taken care of as well during the setup_mudata of multivi.

## Scvi 1.4.0. model.differential_expression outputs
**Topic:** 3893 | **Last activity:** 2025-12-07T07:21:00Z
**Posts:** 2 | **Views:** 141 | **Created:** 2025-12-06 | **URL:** https://discourse.scverse.org/t/scvi-1-4-0-model-differential-expression-outputs/3893

**Question**: Hello, I am using the scvi version 1.4.0.post1. The model.differential_expression function gives proba_m1, proba_m2, bayes_factor, scale1, scale2, raw_mean1, raw_mean2, non_zeros_proportion1, non_zeros_proportion2, raw_normalized_mean1, raw_normalized_mean2 as output without is_de_fdr_0.05 and lfc_mean columns. How can I filter the results? I have tried the following, which filtered out all of the genes. I appreciate any help, thanks! scvi_de[‘lfc’] = np.log2((scvi_de[‘raw_mean1’] + 1e-6) / (scvi_de[‘raw_mean2’] + 1e-6)) scvi_de[‘proba_de’] = 1 - np.exp(-scvi_de[‘bayes_factor’]) scvi_de[‘pseudo_pval’] = 1 - scvi_de[‘proba_de’] scvi_de[‘pseudo_fdr’] = multipletests(scvi_de[‘pseudo_pval’], method=‘fdr_bh’)[1]

**Reply (@ori-kron-wis)**: You can run it with mode=“change” (default is “vanilla”), it will give you proba_de, lfc, etc and is_de_fdr_0.05, which is how we usually filter by.

## Corrected count for resolvi
**Topic:** 3870 | **Last activity:** 2025-11-25T19:42:09Z
**Posts:** 2 | **Views:** 214 | **Created:** 2025-11-19 | **URL:** https://discourse.scverse.org/t/corrected-count-for-resolvi/3870

**Question**: Hi, I am wondering what would be the right way of generating a corrected count matrix for downstream analysis from resolvi. The tutorial uses the median of px_rate as generated_expression , while the preprint computed corrected_counts by multiplying counts and px_rate_q25 / (1 + px_rate_q25 + mean_poisson) . From my understanding, the corrected_counts should be the right way to go, is it correct? Thanks in advance!

**Reply (@cane11)**: Throughout the manuscript, I’m using p25 of ‚obs‘ using the corrected model, where I sample only from true expression and set diffusion and background to zero. I think this is a good starting point. In the tutorial, I’m outputting estimated counts using px_rate. If you are afraid of removing expression of some genes, the formula for corrected counts might be beneficial.

## Question about complex experiment
**Topic:** 3864 | **Last activity:** 2025-11-25T19:39:01Z
**Posts:** 2 | **Views:** 147 | **Created:** 2025-11-14 | **URL:** https://discourse.scverse.org/t/question-about-complex-experiment/3864

**Question**: Hi everyone, I’m starting a fairly complex experiment that includes 10x single-cell, single-nucleus, and 10x multiome (snRNA-seq + scATAC-seq from the same nucleus), with control and treatment groups spread across all three modalities. I also have some patients for whom I’ve generated two modalities (sc + sn), in case that could be useful for any type of training or modeling. I’d like to run the standard analyses (integration, differential expression, differential abundance, and differential accessibility), but I’m unsure about the best strategy to handle all modalities together. Any recommendations or best practices would be really helpful.

**Reply (@cane11)**: Hi @dackjames unfortunately there is no guide here. This is a hard experimental setup that I would as a first step try to reconsider. It will require major effort to get it working. MultiVI can train on multi-ome data and might do well and integrate RNA and paired RNA/ATAC data. I’m not sure whether snRNA-sequencing and scRNA-sequencing will be integrated well though and sometimes this is challenging. Some ideas: it’s usually good to select shared HVGs, encoding batch key will be helpful, it’s easier if the cell-type composition is the same across experiments. Trying harmony on this might also be a good chance. Beforehand annotate the data separately to verify meaningful integration. Good luck with your project!

## Loss_z1_weight and loss_z1_unweight in scANVI
**Topic:** 364 | **Last activity:** 2025-11-25T19:32:13Z
**Posts:** 4 | **Views:** 640 | **Created:** 2022-03-21 | **URL:** https://discourse.scverse.org/t/loss-z1-weight-and-loss-z1-unweight-in-scanvi/364

**Question**: In the scANVI implementation, there are two losses I don’t quite understand: scvi-tools/_scanvae.py at d636093bc8d49c8e03fcb4bc0a8bc8130cb29fe2 · scverse/scvi-tools · GitHub loss_z1_unweight = -Normal(pz1_m, torch.sqrt(pz1_v)).log_prob(z1s).sum(dim=-1) loss_z1_weight = Normal(qz1_m, torch.sqrt(qz1_v)).log_prob(z1).sum(dim=-1) Given that these are directly added to the loss function, isn’t this saying that we want P(z1| pz1) to be high and P(z1| qz1) to be low? But z1 is generated (via reparameterization trick) from qz1 so how is this possible? Additionally: I presume understanding those two losses would also answer why the encoder_z2_z1 and decoder_z1_z2 part of the architecture is necessary. If not, what is this additional encoder and decoder used for? Thanks in advance, Yuge

**Reply (@Justin_Hong)**: Hi Yuge, Thank you for using scvi-tools. These lines are easier to understand as the KL divergence term for z_1 . Specifically KL(q_\eta(z)||p_\theta(z)) = loss_z1_weight + loss_z1_unweight . The second encoder and decoder pair are additional networks that break down z_1 per cell type. This is the defining difference between scVI and scANVI. The math is detailed in our user guide: scANVI - scvi-tools . Let me know if this helps!

**Reply (@alitinet)**: Hi @Justin_Hong , can I follow up on this and ask a few questions about how z2 is used. From what I got from the code, z2 or rather the mean and variance of encoder_z2_z1 are only used to calculate the KL loss. But to calculate the reconstruction and the classification loss, z1, i.e. the direct output of the encoder, is used. Could you please clarify if that’s correct? If z2 is only used in the KL calculation, why is it needed in the first place? Thanks!

**Reply (@cane11)**: Hi, motivation comes from the stacked M1+M2 model in: https://arxiv.org/pdf/1406.5298 . I hope this helps to understand the structure. It encourages integration of each cell-type by mapping z1 to z2 and back to z1.

## Inquiry Regarding DRVI Model Compatibility with scANVI for Embedding Optimization?
**Topic:** 3876 | **Last activity:** 2025-11-25T19:21:12Z
**Posts:** 2 | **Views:** 105 | **Created:** 2025-11-25 | **URL:** https://discourse.scverse.org/t/inquiry-regarding-drvi-model-compatibility-with-scanvi-for-embedding-optimization/3876

**Question**: I am writing to inquire about the compatibility of the DRVI model with scANVI for embedding optimization. Specifically, I would like to know: Whether the DRVI model supports using scANVI to optimize embeddings, and if so, how this integration can be implemented. Whether this approach is recommended (e.g., for improving latent representations, scalability, or downstream tasks like clustering or visualization). I have reviewed the DRVI documentation and codebase but could not find explicit information on this combination. Thank you for your time and contributions to the community. I look forward to your guidance.

**Reply (@cane11)**: Hi, thanks for your interest. These are two distinct models and DrVI is not part of scvi-tools. So they are not compatible with each other and reaching out to the DrVI developers directly on their GitHub, might actually help you to understand whether they are planning for a (semi-)supervised model in the future.

## Clarification on the random variable W in the decoder
**Topic:** 3860 | **Last activity:** 2025-11-11T13:33:45Z
**Posts:** 3 | **Views:** 90 | **Created:** 2025-11-10 | **URL:** https://discourse.scverse.org/t/clarification-on-the-random-variable-w-in-the-decoder/3860

**Question**: Hello, So I’ve been doing a deep dive into the technical aspects of this software for my dissertation project. Something that I noticed while going through the decoder algorithm was the following: w is defined as Gamma(f_w(z,s), theta). However, in the supplemental section, it is mentioned that w is defined to be a gamma variable with shape parameter r and scale p/1-p. Additionally in that section, when the ZINB model is shown, following statement is made: image 1219×270 37.4 KB However, wouldn’t the mean of w be f_w(z)theta (or even yet, rp/1-p)? I’ve been trying to figure out why the mean of w is just the decoder output, but I haven’t seen any clear answers online on why this is so. I hope this can be clarified.

**Reply (@ori-kron-wis)**: See if this helps: The mean of the the scVI ZINB model distribution (related to supplementary note 3) scvi-tools To bring more explanation in the supplement the definition is the logits total_counts convention for a negative binomial (r, p and lambda instead of rho, theta and l_n). See our code on how this changes computation: scvi-tools/src/scvi/distributions/_negative_binomial.py at main · scverse/scvi-tools · GitHub . To make it very short, theta is the mean variance relationship and the mean is independent of theta. In short, there is some confusion of the notations of the supplemental section

**Reply (@jcara514)**: So w is distributed as a gamma variable with shape theta and rate theta/mu? I guess now I’m confused on why w~Gamma(shape = theta, theta/mu) and w~Gamma(shape= rho, theta) are equivalent.

## Training not using the full GPU
**Topic:** 3857 | **Last activity:** 2025-11-10T14:35:50Z
**Posts:** 4 | **Views:** 164 | **Created:** 2025-11-10 | **URL:** https://discourse.scverse.org/t/training-not-using-the-full-gpu/3857

**Question**: So I have been running training couple models recently and I encountered this one problem. scvi has no problem detecting CUDA or the GPU. But the problem is that it is using about 25% of GPU and 20% of VRAMs. Have any of y’all encountered a problem like this? Do you have any tricks to increase the utilization rate? This is a screenshot of nvtop when I am autotuning for hyperparameters. image 1160×770 213 KB

**Reply (@ori-kron-wis)**: Increase your batch_size during training, and the GPU will be more utilized. You will also save runtime.

**Reply (@mys_721tx)**: Thanks for the tip! I was able to get twice the utilization with batch size of 1024. As of 1.4.0.post1 the autotuner somehow does not respect scvi.settings.batch_size and has to be passed as a train_params . image 1160×770 217 KB

**Reply (@ori-kron-wis)**: It’s fine, it is a train parameter. As for the settings batch_size, it is used only if the model’s input is None (the default is a number), but mainly used for the downstream analysis functions. The model expect a valid batch_size, has one as input and you can tune it as you saw. Note to use ray<2.5.1 (as the most recent version has some issue with scvi-tools right now)

## How to use totalVI denoised protein measurements
**Topic:** 3850 | **Last activity:** 2025-11-09T12:58:56Z
**Posts:** 2 | **Views:** 101 | **Created:** 2025-11-06 | **URL:** https://discourse.scverse.org/t/how-to-use-totalvi-denoised-protein-measurements/3850

**Question**: Hi! I have a sort of theoretical question about the totalVI denoised protein measurements. From the paper, it seems like for the RNA modality, there is a specific library size-based scaling factor, but it doesn’t seem like there’s something equivalent for the protein modality in the model. I was wondering if the resulting denoised protein measurements take some metric of per cell library size into account, or if they should be treated more like raw counts and if I should normalize them by some size factor?

**Reply (@ori-kron-wis)**: There’s no protein scaling library size analogous to RNA, as normalization is learned internally, by tuning a mixture factor of the foreground and background proteins, per cell, in the latent space. You should not apply additional size factor normalization then.

## Question about get_normalized_expression computation
**Topic:** 3842 | **Last activity:** 2025-11-05T08:14:27Z
**Posts:** 4 | **Views:** 211 | **Created:** 2025-10-29 | **URL:** https://discourse.scverse.org/t/question-about-get-normalized-expression-computation/3842

**Question**: I have trained a TOTALVI model and I am using the get_normalized_expression function to get imputed values for one gene and one protein. It is using mostly CPUs (128 threads) and not the GPU (Volatile GPU-Util = 8%, 2391 Mb). Is it correct that it is a CPU instead of GPU heavy calculation?

**Reply (@ori-kron-wis)**: Generally, yes, but the ratio of how much CPU will work vs GPU depends on the get_normalized_expression function parameters. If, for example, you increase the batch_size and reduce the n_samples, I expect you will see more traffic on GPU than CPU. But it also depends on other parameters such as: transform_batch, indices,… anything really. You can follow it if you set the silent parameter to False and track CPU and GPU usage.

**Reply (@racng)**: Thanks for the suggestion. I have increased batch size and have noticed more traffic on GPU than CPU. CPU usage is now around the n_samples, and there is more GPU memory being used. Is silent a parameter for get_normalized_expression or some other function? I am also concerned that get_normalized_expression might use mdata[‘rna’].X instead of mdata[‘rna’].layers[rna_layer] (whatever rna_layer we specified when we called scvi.model.TOTALVI.setup_mudata ). On github , it says: post = self._make_data_loader(adata=adata, indices=indices, batch_size=batch_size) ... for tensors in post: x = tensors[REGISTRY_KEYS.X_KEY] y = tensors[REGISTRY_KEYS.PROTEIN_EXP_KEY] I think REGISTRY_KEYS.X_KEY = ‘X’? Does self._make_data_loader know to load the specified rna_layer ?

**Reply (@ori-kron-wis)**: silent is for get_normalized_expression, it will just show you the progress bar of the function, as it works per batch; it might correlate to the GPU and CPU usage. Its ok in terms of the backend. REGISTRY_KEYS.X_KEY = ‘X’ indeed, but it is used with the tensors (or data loading) object, not the mudata. This can be done after model was registered and setup with the mudata/adata, so we know how to map RNA/protein data from this structure to the actual data loading and tensors (the actual thing that flows in the network).

## Batch key and categorical variables for get_normalized_expression()
**Topic:** 3841 | **Last activity:** 2025-11-04T11:01:55Z
**Posts:** 3 | **Views:** 209 | **Created:** 2025-10-29 | **URL:** https://discourse.scverse.org/t/batch-key-and-categorical-variables-for-get-normalized-expression/3841

**Question**: Hi. many thanks for the nice tool. I have combined multiple public scRNA-seq data and used scvi-tool for integration. scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="Project", categorical_covariate_keys=['Patient','Sex']) vae = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb") vae.train(accelerator='gpu') vae.save('../data/scvi_models/scvi_integration_model_project_sample_sex') Then, I clustered the data based on scvi latent space adata.obsm["X_scVI"] = vae.get_latent_representation() sc.pp.neighbors(adata, use_rep="X_scVI") sc.tl.umap(adata) sc.tl.leiden(adata,resolution=0.3) Now, my aim is to go with downstream analysis such as defining markers, DEGs (using different techniques like MAST in R), infercnvpy, (liana+) cell-cell communication analysis, per …

**Reply (@cane11)**: Hi. For none of the mentioned tools you would want to use normalized expression.

**Reply (@munta)**: Thank you for your answer. But, MAST, cellchat, nichenet they all need normalized counts … Anyway, my question is, in order to get the batch-corrected counts, I should set the transform_batch parameter in vae.get_normalized_expression. Is it ok to use the largest batch I have in the data? Otherwise, I am not sure how to choose the “preferable” batch! thanks in advance

## Same scVI model with different values on mac silicon and linux?!
**Topic:** 3846 | **Last activity:** 2025-11-04T07:09:02Z
**Posts:** 2 | **Views:** 105 | **Created:** 2025-11-03 | **URL:** https://discourse.scverse.org/t/same-scvi-model-with-different-values-on-mac-silicon-and-linux/3846

**Question**: Hi. I have used scvi model to integrate data from different batches. I used HPC cluster and gpu for that. when I checked the data on cluster adata.layers['scvi_norm'] = vae.get_normalized_expression(adata=adata,library_size=1e4) >>> adata.layers['scvi_norm'].min() 3.869816e-10 >>> adata.layers['scvi_norm'].max() 1822.8737 but when I analyse the data locally on mac (M silicon) I got different values? >>> adata.layers['scvi_norm'] = vae.get_normalized_expression(adata=adata,library_size=1e4) >>> adata.layers['scvi_norm'].min() 7.775142e-10 >>> adata.layers['scvi_norm'].max() 1753.7305 is this normal? thanks

**Reply (@ori-kron-wis)**: It’s definitely normal to get slightly different results between different OS and HW you run on. The question if the model was also trained on different machines (in that case, it’s even more likely to be different) also scvi tools compute normalized gene expression for each cell by sampling from the latent variables of your trained model. So that sampling can inject randomness to it. And above all make sure you set the seed in order to try to reproduce your results.

## Excluding Ig and ribosomal genes from HVG selection in scVI, best practice?
**Topic:** 3833 | **Last activity:** 2025-10-22T09:15:23Z
**Posts:** 2 | **Views:** 267 | **Created:** 2025-10-21 | **URL:** https://discourse.scverse.org/t/excluding-ig-and-ribosomal-genes-from-hvg-selection-in-scvi-best-practice/3833

**Question**: Hi everyone, I’m working with single-cell RNA-seq data from CD45⁺ immune cells (mostly lymphoid lineages) and integrating multiple batches using scVI , which so far has given the best batch correction results. We’re now reprocessing the data after adjusting QC thresholds, and I came across some recent papers where they state: “Prior to PCA, nearest neighbor clustering, and UMAP representations, some genes were filtered from inclusion including those associated with Ig loci (Igk, Igl, or Igh), ribosomal proteins (Rps or Rpl), mitochondrial (mt-), sex (Xist),…” My questions are: Would it make sense to exclude these genes before computing HVGs , so that they never influence the latent space learned by scVI? Or is it better to compute HVGs normally, then remove these specific genes after HVG s …

**Reply (@ori-kron-wis)**: Hey, Generally, the latter is the way to go to not affect the biological signal and other downstream tasks, such as DE. So, keeping them, but not letting them affect the latent space. However, the decision may also be influenced by the problem you are trying to solve. I think you can only gain by performing this, considering (1). In any case, you can always compare the different strategies by running scib-metrics on the generated latent space(s) and DE to validate your expected results.

## Potential bug in scvi.model.TOTALVI.setup_mudata
**Topic:** 3822 | **Last activity:** 2025-10-10T16:30:03Z
**Posts:** 3 | **Views:** 89 | **Created:** 2025-10-09 | **URL:** https://discourse.scverse.org/t/potential-bug-in-scvi-model-totalvi-setup-mudata/3822

**Question**: Hi there, I am using the most recent github version of scvi and have been running into this potential bug when I try to set up my data. It occurs when I use mudata or anndata. image 1827×612 118 KB Basically, it looks like something is happening in the setup that causes the function to cut off the column name of my batch/covariate variable at the first letter. Some other things that may help: Removing both the batch and covariate parameters resolves the bug. However, my data has strong batch effect, so I need to be able to use those parameters. Renaming my batch/covariate columns to be single-letter does actually get me a step further, but then I get a separate bug: ValueError: Obsm ‘_scvi_extra_categorical_covs’ needs to be of one of <class ‘numpy.ndarray’>, <class ‘numpy.ma.core.MaskedAr …

**Reply (@cane11)**: Hi, categorical_covariate_key is supposed to be a list. It otherwise treats the string as an iterative of single letters.

**Reply (@igrisch)**: Fixed it, thank you so much!

## Is Gaussian mixture VAE implemented in scVI-tools?
**Topic:** 3809 | **Last activity:** 2025-09-25T20:29:56Z
**Posts:** 4 | **Views:** 156 | **Created:** 2025-09-24 | **URL:** https://discourse.scverse.org/t/is-gaussian-mixture-vae-implemented-in-scvi-tools/3809

**Question**: Hi, Is Gaussian mixture VAE framework (GMVAE), one used in e.g. scVAE ( scVAE: Single-cell variational auto-encoders — scVAE 2.1.4 documentation ), also implemented in scVI-tools? Thanks!

**Reply (@ori-kron-wis)**: Hey, No, it is not implemented in base models there.

**Reply (@ViolaChenYT)**: If I’m interested in implementing it with scVI-tools, would such a contribution be welcomed? on a high level, I am thinking of the following Create a GMMVAE Model: create a new model class, probably inheriting from scvi.model.VAEC , __init__ method would define the GMM prior parameters (means, variances, and mixture weights) as learnable torch.nn.Parameter tensors. Implement Custom KL Divergence: we would need to calculate the KL divergence between the encoder’s Gaussian posterior and the Gaussian mixture prior. This would replace the standard KL term in the loss function. API: wrap it in a user-friendly class (e.g., scvi.model.SCVI_GMM ) that inherits from the existing API (Mike and I work together, and I just had this random thought about whether it’d be meaningful to implement it with s …

**Reply (@cane11)**: Hi, it is used in sysVI and also MrVI. Called Mixture-of-Gaussian prior. It is a quite general implementation and can be easily plugged into other models (see sysVI).

## Preprocess of scATAC use for peakVI or MultiVI
**Topic:** 3691 | **Last activity:** 2025-09-03T21:39:39Z
**Posts:** 6 | **Views:** 298 | **Created:** 2025-06-19 | **URL:** https://discourse.scverse.org/t/preprocess-of-scatac-use-for-peakvi-or-multivi/3691

**Question**: Hi, Many thanks for providing scvi-tools, it do helps a lot when I integrate multiple datasets. I processed scATAC data with snapatac2, but snapatac2 output scATAC in bin counts (not peak counts). I tired many tools to integrate scRNA and scATAC with bin couns (5k) or gene activity matrix generated from bin counts (5k). I could not get proper integration results. Could you suggest some about this? Do you think bin count could be used for peakVI or multiVI or could you suggest some preprocess pipeline used to merge multi scATAC data? Many thanks, Xuan

**Reply (@cane11)**: Hi, multiVI is intended to integrate e.g. multiome with RNA or ATAC data but not to integrate RNA with ATAC data. Most other models also require some cells with joint measurements. I’m not aware of other tools that I would recommend for this task.

**Reply (@Xuann)**: Many thanks for your quick reply. I am integrating scRNA scATAC with multiomic data, so I first try integration with multiVI. I went through the tutorial of multiVI, but in the tutorial, the test data (scRNA, scATAC and multiomic) are both subset of one multiomic dataset which means it will have the same var names. If I run multiVI with my data, should I align each sample with same var names or some overlapping between scATAC and multiomic is sufficient? Best, Xuan

**Reply (@cane11)**: Hi, you want to do peak calling across those datasets to have a joint set of features in your ATAC data. E.g. Atlas-scale Analysis: a cell atlas of human chromatin accessibility. — SnapATAC2 2.8.0 documentation provides guidelines to identify joint peaks.

**Reply (@Xuann)**: Hi, Thanks for your reply. I also tried snapatac2, now I generate matrix from cellranger aggr, becasue snapatac2 will generate bin matrix. Best, Xuan

**Reply (@MP_Epana)**: Bin counts should work just as well as peak counts. In my experience at least, integration depends on which peaks to use (assuming you are using MultiVI or other similar VAE approaches). If you use bulk peak calling to identify regions to count, you are more likely to miss key regions that are more cell type selective, especially in smaller populations. Junk in, Junk out. In contrast, I’ve been able to integrate scRNA and scATAC relatively well in MultiVI, if I select the correct regions via non-bulk peak calling methods. Here’s an example of an approach that does not rely on bulk peak calling (as well as a discussion as to why it matters). https://www.nature.com/articles/s41467-024-50612-6

## Get_normalized_expression causes my kernel to disconnect
**Topic:** 3778 | **Last activity:** 2025-08-19T07:13:21Z
**Posts:** 2 | **Views:** 119 | **Created:** 2025-08-18 | **URL:** https://discourse.scverse.org/t/get-normalized-expression-causes-my-kernel-to-disconnect/3778

**Question**: Hey everyone! fairly new user of scvi-tools and sCANVI here. Every time I run get_normalized_expression on my sCANVI query model, my kernel says it disconnects (which I believe is likely a memory issue?) This is actually my second time running the model; the first time, get_normalized_expression ran with no issues. Between running the models, I updated my scvi from 1.3.1.post1 to 1.3.3. The main changes I implemented between the new and old models are: the new model has linear_classifier = True the new model has max_epochs = 100 instead of 20 (I implemented both of these changes in the sCANVI reference model, but I am running get_normalized_expression on the query model. I made these changes due to suggestions I saw, because previously my prediction accuracy on reference data was quite low …

**Reply (@ori-kron-wis)**: Hello, I understand from you that the model was trained successfully (on ref? query? both?) and the issue is with memory during get_normalized_expression on the query. Reducing number of genes helps and this strengthen the reason its a memory issue . I wouldn’t reduce it that much though, a common practice is to select the top ~2000 Highly variable genes. In order to save memory, first of all you can separate your scripts to 2 parts (even 3) for the training and query part. Once your model is trained (seems it does), Save it and clear the memory of that script/notebook (and any other redundant thing on the machine). Then load it back and continue on a fresh script. If you insist on doing it all in same script, you can delete redundant objects or do gc.collect() during the code. it helps. A …

## How to Correct for Intra-Organ Batch Effects Without Removing Inter-Organ Differences?
**Topic:** 3731 | **Last activity:** 2025-08-05T11:11:34Z
**Posts:** 7 | **Views:** 235 | **Created:** 2025-07-29 | **URL:** https://discourse.scverse.org/t/how-to-correct-for-intra-organ-batch-effects-without-removing-inter-organ-differences/3731

**Question**: Dear Community, I’m currently working on integrating a single-cell RNA-seq dataset of human mesenchymal stem cells (MSCs) using scvi-tools . The dataset includes 11 samples, each from a different donor, across four tissue types : A : Adipose (A01–A03) B : Bone marrow (B01–B03) D : Dermis (D01–D03) U : Umbilical cord (U01–U02) Each sample corresponds to one patient, so I’ve been using the sample ID (e.g., A01, B02) as the batch_key in SCVI.setup_anndata . My goal is to mitigate donor-specific batch effects within each tissue , but preserve the biological differences between tissues (since tissue-of-origin is an important axis of variation here). I’ve followed the scvi-tools tutorials, but after integration, the tissue-specific structure seems to be partially lost. My Questions: Is using bat …

**Reply (@ori-kron-wis)**: You can try the 2nd option, although I think it will just integrate your tissue type as well. Can you share UMAPs? Or why do you say that “the tissue-specific structure seems to be partially lost”. Can you share more info on your data? its size? Maybe a stratification issue? Is there any other information that can help in batch integration besides donor (e.g are donors from different studies or do some overlap?, Perhaps sample is not the best choice)

**Reply (@dacon06)**: Hi, Thanks for your response! I’d be happy to share my UMAP plots. My dataset consists of 132,706 cells and 33,694 genes . The only metadata I have for each cell is the patient ID and the organ from which the sample was taken. Please let me know if you need any more details. Best regards UMAP before Integration 1241×860 82.6 KB

**Reply (@dacon06)**: UMAP after Integration 1241×860 135 KB

**Reply (@ori-kron-wis)**: I guess the 2nd image is with the tissue as a covariate. Re the 1st figure, can it be that A02 & A03 are from same study and A01 is from a different place? Same goes for D01 & D03 vs. D02? How do training/validation loss curves look? Have you tried other models than SCVI? SysVI or MrVI?

**Reply (@dacon06)**: Thank you for your feedback! The second image shows the result using only Sample as the batch correction variable. All samples are from the same study . The training and validation loss curves behave normally, with no signs of overfitting or divergence. I haven’t tried other models yet, if you have any recommendations, I’d be happy to explore them!

**Reply (@ori-kron-wis)**: Yes, you might try ScanVI (with tissue types as labels) or SysVI or MrVI, in the same manner. What makes you say the 1st image doesnt preserve biological difference? It’s not that bad… maybe its the best you could do with SCVI.

## Conduct SCANVI after running SysVI on multi-platform data
**Topic:** 3745 | **Last activity:** 2025-08-03T16:34:52Z
**Posts:** 4 | **Views:** 119 | **Created:** 2025-08-02 | **URL:** https://discourse.scverse.org/t/conduct-scanvi-after-running-sysvi-on-multi-platform-data/3745

**Question**: Hi, I really appreciate the power of SysVI to correct large batch effects between different platforms. Once SysVI has been run between a reference on one platform and an unnanoted dataset on a second platform, how can we run SCANVI to conduct cell type labeling? Thank you Cristian

**Reply (@cane11)**: Hi, this is not supported and would require actually establishing the model, e.g. cycle-consistency loss should be guaranteed to provide same cell-type label. However, you can run a simple kNN classifier in latent space as done in our tutorials to perform cell-type transfer, see e.g. https://www.biorxiv.org/content/10.1101/2024.09.19.613883v3

**Reply (@coarfa)**: Thank you very much, will try knn since sysVI did a much better job of integrating the datasets than anything else I tried. Best regards Cristian

**Reply (@cane11)**: For completeness, Querying the Human Lung Cell Atlas — scvi-tools provides a tutorial for a kNN classifier.

## How to handle batch effects within the query dataset when using scArches + SCVI?
**Topic:** 3728 | **Last activity:** 2025-07-31T12:14:23Z
**Posts:** 2 | **Views:** 224 | **Created:** 2025-07-28 | **URL:** https://discourse.scverse.org/t/how-to-handle-batch-effects-within-the-query-dataset-when-using-scarches-scvi/3728

**Question**: Hello everyone, I’m new to scArches and currently exploring how it works in combination with SCVI , particularly for integrating new datasets into a reference atlas. I’m following this tutorial , where a SCVI model is first trained on a reference dataset and then extended using treeArches to incorporate a new query dataset. From what I understand, the entire query dataset is treated as a single new batch during this “surgery” step when adapting the model. Also, it seems that SCVI expects raw count data for both training and mapping steps. This leads me to a my question: What if my query dataset contains multiple batches itself (for example, samples from different sources or sequencing runs)? Should I split the query dataset by batch and integrate each one individually into the reference? O …

**Reply (@ori-kron-wis)**: Hey, I think the tutorial you linked to is a bit old and perhaps confusing (it uses batch column as “batch_key” but this column is also equal to “study” column, which is used to separate query and reference). Anyway, You can check this tutorial: Reference mapping with SCVI-Tools — scvi-tools Where the query dataset consists of several “tech” batches, and they are all used together as the query data. Obviously your query data should be close to your reference (in terms of species, tissue, cell types and so on) for good reference mapping (“surgery”). However, there are more models beyond SCVI, that might be helpful for you if you want to integrate a query that is very different, such as SysVI. It might help in your flow (however scarches not fully supported in this model yet)

## Unexpected DE test results in scvi version 1.3.0 (as compared with version 1.1.2)
**Topic:** 3598 | **Last activity:** 2025-07-31T10:47:19Z
**Posts:** 16 | **Views:** 550 | **Created:** 2025-04-10 | **URL:** https://discourse.scverse.org/t/unexpected-de-test-results-in-scvi-version-1-3-0-as-compared-with-version-1-1-2/3598

**Question**: Hello! I recently upgraded scvi from version 1.1.2 to 1.3.0 and attempted to reproduce a one vs all DE test across different cell types. I got drastically different results. I noticed in the release notes that there were changes made to the implementation of the DE test and was wondering if those changes affected the results. I saw that the default mode was changed to “change” but I had been manually setting mode=“change” all along, so I don’t believe this is the source of the difference. Here is the code I used for the original results (with version 1.1.2) and the new results (with version 1.3.0) (same code for both). de_df = model.differential_expression( adata=adata_filtered, groupby='cell_type', mode = "change", delta = 0.25, fdr_target = 0.05 ) The original results (version 1.1.2) of …

**Reply (@joseph-siefert)**: I am also experiencing issues with Bayes factor and lfc in the latest version and posted about this yesterday ( Problems with Bayes factors and LFC changes using model.differential_expression() ). Hoping we can get an update to fix rather than rollback, but you should also be able to do that

**Reply (@cane11)**: Let me get back tomorrow with the kwargs for DE to fully reproduce the old results. Those are still an option. To figure better guidelines, could you also post the other columns of the DE table, especially mean expression in scVI and top20 genes in the old and new scVI version. Changes are: Change mode is now the default (I don’t think this is the issue here), pseudocounts added before LFC computation are much larger (this was a typo in the function percentile instead of quantile but maybe they are to large now likely the issue for IL21 above), beforehand p-value was counted for down- and upregulated together (this is quite confusing as a highly varying signal was reported as significant and the report was about up- or downregulation). All of these are still options (where the old two-way …

**Reply (@jflusche)**: Thanks for looking into this! I have attached the full DE result dataframe for the top 20 genes using the old scvi version and the new. Old DE (1) 1924×1176 339 KB Old DE (2) 1976×1212 300 KB New DE (1) 1848×1192 320 KB New DE (2) 1974×1224 312 KB

**Reply (@cane11)**: You can manually set the pseudocount to 1e-7 and some of the genes should be there again. It’s biased towards highly expressed now. I should rethink whether this bug (0.9 percentile instead of quantile) was to much to fix and we actually need a lower quantile. Genes like PRG4 in the previous version were actually not really expressed but reported by the DE function.

**Reply (@jflusche)**: Thanks for this suggestion. I wanted to report the results after manually setting pseudocounts=1e-7. The gene list now contains most of the same genes as the original DE test (scvi version 1.1.2). The bayes factors are just slightly lower. Attached are the new top 20 results for the Tfh cell type. NEW DE pseudocount (1) 1886×1124 331 KB NEW DE pseudocount (2) 1978×1130 295 KB

**Reply (@jflusche)**: Hi there, wanted to follow up here! Adjusting the pseudocounts did result in a DE genes list that I expected to see biologically but did not reproduce the original results. If possible, it would be great if you’re able to share recommended guidelines for how to fully reproduce the old results when working with the new DE test updates. Thank you.

**Reply (@aj95b)**: I am facing similar issues with the new scVI version. Except in my case the situation is even more dire. All the significant results are gone! I have tried many permutations of the kwargs including setting pseudocounts to zero, nothing seems to work.

**Reply (@ori-kron-wis)**: have you tried it with both mode=“vanilla” and mode=“change”?

**Reply (@aj95b)**: Yes I have. It didn’t work either. By the way, I think that mode “change” may have been default since before. Because when I ran it with “vanilla” it didn’t give me the attribute termed “proba_not_de” (it used a different name for a second probability attribute), which I always used to get even earlier, without specifying mode.

**Reply (@kateaugustyn)**: Hi! I also recently upgraded scvi from version 1.2.0 to version 1.3.1 and have been seeing some of the same changes already mentioned here such as fewer total number of DE genes, lower bayes factor, and lower lfc magnitudes. I tried the suggestion of adjusting the pseudocounts to 1e-7. I noticed a brief mention of updates to the new test in the scvi release notes but have not found further information in any of the documentation pages about how the new test works, how I should be running it, and how I should be interpreting the results differently than in the older version. Any help would be appreciated.

**Reply (@ori-kron-wis)**: We are looking into the DE discrepancies we have in the current scvi-tools release vs the previous ones. In the meantime, Can you both try to run DE with test_mode=“two”, mode=“change” and pseudocounts=0 ? Another option is to run with mode=“vanilla” and pseudocounts=0

**Reply (@kateaugustyn)**: Thanks for your suggestions. I ran the same DE test four times with different scvi versions and different values of pseudocounts and mode. The tests I ran were as follows: scvi version 1.2.0 with mode=“change” scvi version 1.3.1 with mode=“change” and pseudocounts=1e-7 scvi version 1.3.2 with mode=“change”, test_mode=“two” and pseudocounts=0 scvi version 1.3.2 with mode=“vanilla” and pseudocounts=0 The DE test with version 1.3.2 where mode=“vanilla” had no column with LFC information in the results. The results of each test are summarized in plots. The volcano plots show the lfc_median and bayes_factors for each gene. Points in red are genes for which is_de_fdr_0.05=True. The histograms are showing the distribution of the bayes factor values. Untitled presentation 768×960 50.5 KB The resul …

**Reply (@ori-kron-wis)**: Hey, We are aware we have issues with the 1.3.2 “change” mode version (three sided). We have a fix under the branch: Fix: DE by ori-kron-wis · Pull Request #3418 · scverse/scvi-tools · GitHub , you might want to try to repeat your analysis with this update (soon to be released) In short: Vanilla should give you the same results in both 1.3.2 and 1.2.X mode=“change”, test_mode=“two” (and pseudocounts=0 or None) is the preferred way to go currently in 1.3.2, until we release the fix

**Reply (@kateaugustyn)**: Hi, Thanks for this information! I just ran a DE test with scvi version 1.3.3 and the results seem more reasonable to me in terms of having a positive bayes factor for significant DE genes. image 846×629 46.1 KB image 790×490 14 KB Any guidance on how to interpret the differences in the newest version of scVI would be appreciated. Thanks!

**Reply (@ori-kron-wis)**: I assume you ran mode=”change”. The fix was in the bayes_factors sign for test_mode=” three” (the default for mode=“change”), so like you see, significant LFC will have positive bayes factor, plus the estimation of pseudocounts (default None, which will make it estimated using the non significant gene in order to correctly estimate the LFC, in mode “change”) offsets was made smaller thus smaller subset of genes will regard as back noise, but it can still give inflated LFC values. by default, the newest scvi-tools version runs the DE with mode “vanilla” and pseudocounts None. We plan to make the default mode “change” once we are sure everything works.

## Implementing Warmup to a component based on epoch
**Topic:** 3736 | **Last activity:** 2025-07-31T06:43:05Z
**Posts:** 3 | **Views:** 100 | **Created:** 2025-07-30 | **URL:** https://discourse.scverse.org/t/implementing-warmup-to-a-component-based-on-epoch/3736

**Question**: Hi, This might be a silly question, but I’m trying to implement a warmup schedule for one of the components of my model. I’ve implemented some make-shift solution, but was hoping to avoid digging through the codebase if someone already knows the clean way to do this. For example, is there a straightforward way to access the current epoch from within the module class during training? Thanks in advance!

**Reply (@cane11)**: The correct PyTorch manner is a custom callback with functions like on_epoch_end. For many use cases, it should suffice to just reuse the kl warmup value though.

**Reply (@dbdimitrov)**: Hi, yeah, kl weight was my make-shift solution. Thanks, I will check the existing callback functions

## Error when trying to use scvi.model.SCANVI.from_scvi_model
**Topic:** 2322 | **Last activity:** 2025-07-22T17:06:17Z
**Posts:** 8 | **Views:** 475 | **Created:** 2024-06-06 | **URL:** https://discourse.scverse.org/t/error-when-trying-to-use-scvi-model-scanvi-from-scvi-model/2322

**Question**: Hi I am trying to do label transfer using scvi, however when I try to run scanvi_model = scvi.model.SCANVI.from_scvi_model( scvi_model, adata=reference_adata, unlabeled_category="Unknown", labels_key=SCANVI_CELLTYPE_KEY, ) I got the following error --------------------------------------------------------------------------- ValueError Traceback (most recent call last) Cell In[8], line 1 ----> 1 scanvi_model = scvi.model.SCANVI.from_scvi_model( 2 scvi_model, 3 adata=reference_adata, 4 unlabeled_category="Unknown", 5 labels_key=SCANVI_CELLTYPE_KEY, 6 ) File scanvi/label_transfer/lib/python3.11/site-packages/scvi/model/_scanvi.py:244, in SCANVI.from_scvi_model(cls, scvi_model, unlabeled_category, labels_key, adata, **scanvi_kwargs) 242 if scvi_labels_key is None: 243 scvi_setup_args.update({"l …

**Reply (@cane11)**: Hi, can you make the column categorical before inputting to scANVI. This will create an error message that is easier to debug.

**Reply (@hariesramdhani)**: Hi @cane11 thanks for the reply, sorry I somehow missed this reply notification, also I ended up solving my problem a while back by just retraining the model using the newer version of scvi. So I think we can close this topic. Thanks again.

**Reply (@eviezh)**: Hi everyone, relatively new user here and I’m having the exact same error as the original post while trying to do label transfer. I did try making my labels_key column categorical but nothing seemed to change. I would also strongly prefer not to retrain the scvi model, if possible. Anyone have any suggestions? Thanks in advance! Some additional info–when I run scvi_epithelial.view_anndata_setup(adata_epithelial) the output is as follows: Anndata setup with scvi-tools version 1.3.1.post1. Setup via `SCVI.setup_anndata` with arguments: { │ 'layer': 'counts', │ 'batch_key': '_scvi_batch', │ 'labels_key': '_scvi_labels', │ 'size_factor_key': None, │ 'categorical_covariate_keys': ['version_10x'], │ 'continuous_covariate_keys': None } Summary Statistics ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓ ┃ Su …

**Reply (@ori-kron-wis)**: Hey, Not entirely sure what is the failure? you did not attached the error message/log or reproduction code. Is it because you upgraded scvi-tools after 1st modelling and now want to do the label transfer? Did you use special parametrization during modelling or initialization? Is your reference data has the same categorical_covariate? More information will be helpful.

**Reply (@eviezh)**: hey, thanks for the response! here’s some more information that will hopefully be helpful the code i ran: scanvi_ref_epithelial = scvi.model.SCANVI.from_scvi_model( scvi_epithelial, unlabeled_category="Unknown", labels_key=SCANVI_LABELS_KEY,) the error: --------------------------------------------------------------------------- ValueError Traceback (most recent call last) Cell In[58], line 4 1 # unlabeled category does not exist in adata.obs[labels_key] 2 # so all cells are treated as labeled ----> 4 scanvi_ref_epithelial = scvi.model.SCANVI.from_scvi_model( 5 scvi_epithelial, 6 unlabeled_category="Unknown", 7 labels_key=SCANVI_LABELS_KEY,) File ~/.local/lib/python3.10/site-packages/scvi/model/_scanvi.py:283, in SCANVI.from_scvi_model(cls, scvi_model, unlabeled_category, labels_key, adata, …

**Reply (@ori-kron-wis)**: Hey, I was able to reproduce it. It not version dependent. Basically I think that your original model was trained with labels as integer (0) and the new one has them as strings (“0”), or vice versa. They both should be string though, like: “label_0” Are there any Nan’s on any of the labels column - change to to what is the unlabeled_category you gave (“Unknown”, in your case). Try to see those things that I mentioned solve this, otherwise, retrain it.

**Reply (@eviezh)**: thanks for your suggestions! I did end up re-running the scVI model. The main change was that my batch variable was placed under "batch_key" instead of "categorical_covariate_keys". Interestingly, although "labels_key" was set to the default (no parameter was specified) in both model initializations, the original model had 'labels_key': _scvi_labels while this model had 'labels_key': None when viewing model.view_anndata_setup . This time, the label transfer with scANVI ran without issue. This does make sense, since the specific column where the error was occurring with the original model was '_scvi_labels.' The first time the error occurred, I did go in and manually convert the integer values in '_scvi_labels.' into strings, similar to your suggestion. (The column is all 0s, nothing else.) …

## Discrepancy between raw mean/non-zero proportion and LFC with model.differential_expression
**Topic:** 3674 | **Last activity:** 2025-07-10T12:10:37Z
**Posts:** 3 | **Views:** 162 | **Created:** 2025-05-29 | **URL:** https://discourse.scverse.org/t/discrepancy-between-raw-mean-non-zero-proportion-and-lfc-with-model-differential-expression/3674

**Question**: Dear totalVI community, I’m encountering a puzzling issue while analyzing my Spatial CITE_seq data (P_CD8) with totalVI, and I hope someone can help me interpret the results. Here’s the key data for the gene/protein of interest: plaintext Comparison: group1 (12) vs group2 (Rest) raw_mean1: 1.038232 (group1) raw_mean2: 0.351163 (group2) non_zeros_proportion1: 0.567503 (group1) non_zeros_proportion2: 0.266475 (group2) lfc_mean: -0.094309 (close to zero) bayes_factor: -1.45131 (supporting no difference) is_de_fdr_0.05: False (not significant) delta: 0.25 sample_protein_mixing: True (background set to zero) Key observations: Raw mean expression in group1 is ~3x higher than group2, and non-zero proportions differ by ~30% (0.56 vs. 0.26). However, the LFC mean is negligible (-0.09), and the baye …

**Reply (@ori-kron-wis)**: Can you share more information on how did you run this? scvi-version and how specifically you ran the DE function, as we might have an issue in most recent scvi-tools version.

**Reply (@cane11)**: I would assume the model likely learns that this is agreeable with background. This can e.g. be the case when comparing cells with Fc receptors and high unspecific antibody binding to cells with low unspecific antibody binding. Overall, if you expect differences and a more simple approach like t-test DE provides you a reasonable difference, totalVI not reporting it, is a weak argument. Experimental validation would be key in these instances.

## Deconvolute spatial transcriptomics (visium) with unannotated single-cell (10x)
**Topic:** 3694 | **Last activity:** 2025-07-10T08:10:36Z
**Posts:** 4 | **Views:** 252 | **Created:** 2025-06-24 | **URL:** https://discourse.scverse.org/t/deconvolute-spatial-transcriptomics-visium-with-unannotated-single-cell-10x/3694

**Question**: I have a spatial transcriptomics dataset (10x visium) of a tumour microarray and some of the samples have matched single-cell RNA-seq data (10x). I would like to annotate my spatial data with the single-cell data. However the single-cell data is not annotated. Can this be done with any scverse tool?

**Reply (@ori-kron-wis)**: Not sure I followed. Do you have any annotations at all? whether on the spatial data or the single cell data? Basically you can use scvi-tools for annotate your data as a query data but only given you have some suitable reference data which is annotated (scvi/scanvi). Following that you can use other tools to also try to annotate that overlapping part of your spatial data. But you can perhaps auto-annotate your spatial data using tools like cell2location.

**Reply (@cell_kc)**: Hi @ori-kron-wis The matched single-cell data does not have any annotations and is just processed to GEX count matrices. I understand that this needs to be annotated first in order to transfer labels? Does cell2location annotate spatial data based on a single-cell reference? Thanks

**Reply (@ori-kron-wis)**: cell_kc: The matched single-cell data does not have any annotations and is just processed to GEX count matrices. I understand that this needs to be annotated first in order to transfer labels? Yes. I suggested that it will be annotated using a model like scanvi (if you have similar annotated data as references) or cellassign (if you know whether or not each given gene is a marker of different cell types you think you have). cell_kc: Does cell2location annotate spatial data based on a single-cell reference? Yes. that will be the 2nd part , if your RNA-seq data will be annotated you will be able to use it and estimate the annotation of the spatial part with cell2location based on location of cells. I guess there are other tools for that.

## Does MultiVI support using tile matrix directly instead of peak calling for ATAC input?
**Topic:** 3701 | **Last activity:** 2025-07-09T16:26:22Z
**Posts:** 3 | **Views:** 146 | **Created:** 2025-06-25 | **URL:** https://discourse.scverse.org/t/does-multivi-support-using-tile-matrix-directly-instead-of-peak-calling-for-atac-input/3701

**Question**: Hi all, I’m working with 10x multiome data and have processed the ATAC and RNA modalities separately: For ATAC, I used tile matrix (e.g., 5kb bins) and trained a peakVI model. For RNA, I used scVI. Now, I’m planning to use MultiVI for integrative analysis. I have two options: Option A: Use the clusters derived from peakVI to perform peak calling per cluster, merge the peaks, build a unified peak matrix across all cells, and then feed that into MultiVI. Option B (preferred): Skip peak calling entirely, and directly use the tile matrix as input for MultiVI. My questions are: Does MultiVI officially support the use of tile matrix as input for ATAC modality? Would the integration performance or downstream analyses (e.g., latent space, cell type separation) be significantly affected? Any insigh …

**Reply (@ori-kron-wis)**: MultiVI will support any count-based ATAC matrix for this modality. If possible try both ways and compare the downstream analyses results.

**Reply (@Captain_Pam)**: Thank you for your suggestion. I will try both.

## DestVI.from_rna_model RuntimeError: Error(s) in loading state_dict for FCLayers
**Topic:** 3711 | **Last activity:** 2025-07-09T16:20:58Z
**Posts:** 2 | **Views:** 126 | **Created:** 2025-07-09 | **URL:** https://discourse.scverse.org/t/destvi-from-rna-model-runtimeerror-error-s-in-loading-state-dict-for-fclayers/3711

**Question**: Hi. I am getting an error running DestVi (scvi-tools 1.3.0). I am basically importing a single cell reference AnnData, subsetting to keep just variable genes, and then finding shared genes with my spatial AnnData. I then fit the scLVM to this subset of my single cell reference data, and finally run DestVI on my spatial data using the single cell model. This is my code: # Import single cell reference anndata adata_ref= sc.read_h5ad('scadata_ref.h5ad') # Filter cells with at least 10 genes sc.pp.filter_genes(adata_ref, min_counts=10) # Save raw counts adata_ref.layers["counts"] = adata_ref.X.copy() # Total-count normalize (library-size correct) sc.pp.normalize_total(adata_ref, target_sum=1e4) # normalize to 10,000 reads per cell # Apply log transformation sc.pp.log1p(adata_ref) # Find highly …

**Reply (@ori-kron-wis)**: Hey, You can perhaps use batch_key=“SampleCondition” for your pre and post process analysis of the data, but the current destVI model requires that its scLVM model will not run with batch_key provided, therefore remove the “batch_key” from CondSCVI.setup_anndata and try again. batch_key applies only to the scRNA, not the spatial data. But this is something we might add in a future upgrade of destVI model (then you will add it to the destVI setup_anndata - but its not ready yet).

## The best practice for detecting differential gene expression between 2 types of samples
**Topic:** 221 | **Last activity:** 2025-07-09T13:53:10Z
**Posts:** 5 | **Views:** 1243 | **Created:** 2021-11-12 | **URL:** https://discourse.scverse.org/t/the-best-practice-for-detecting-differential-gene-expression-between-2-types-of-samples/221

**Question**: Dear community, The datasets I have come from WT or KO animals, each with multiple batches. They contain roughly the same cell types, although KO samples have very few cells in certain cell types. The goal is to match all datasets by cell type, and detect gene expression dysregulation in KO cells for each cell type. The classic Seurat pipeline would first run CCA to align all datasets, and then use the uncorrected (but normalized) counts for differential expression between WT and KO. I was wondering how to approach this within the scVI-tools framework. Should I use batch corrected data for DEG detection or uncorrected values? Also, is there a way to identify a KO cells specific gene expression signature without running DEG detection? I’m asking because there are cases where genes in an ent …

**Reply (@adamgayoso)**: Changxu_Fan: The goal is to match all datasets by cell type, and detect gene expression dysregulation in KO cells for each cell type. The classic Seurat pipeline would first run CCA to align all datasets, and then use the uncorrected (but normalized) counts for differential expression between WT and KO. Generally, the scvi-tools approach would be the same, except you would use SCVI to integrate the datasets. @Valentine_Svensson might have better insight on your DE questions.

**Reply (@Valentine_Svensson)**: The key is that you want the cell labels to be consistent between the datasets. I have seen many papers where people annotate cells independently in WT and KO datasets before combining them and then running DE for KO vs WT. This has the problem that you can’t be sure that the labeling (which I prefer to call ‘stratification’) puts e.g. ‘B cell’ on a consistent population in the two datasets. There are many cases where classical cell type markers are perturbed by treatment. You won’t know if you are actually doing ‘cell type marker discovery DE’ or ‘per cell type perturbation DE’ (which is what you want to do). Your proposed workflow of integration with Seurat to stratify cells, then taking the observed counts to do per-group (“cell type”) DE is reasonable (actually much more reasonable tha …

**Reply (@aj95b)**: Do you recommend setting up anndata and training the scVI model, subsetted for different samples to perform cell-type specific differential expression analysis? Or is it better to only train one model and just use model.differential_expression module for different cell-types?

**Reply (@ori-kron-wis)**: Train one model. There is importance for more samples for global batch correction, noise removal and statistical power, especially if one of your cell_type groups is small.

## Wrong log-fold change estimation?
**Topic:** 3696 | **Last activity:** 2025-07-09T12:44:09Z
**Posts:** 4 | **Views:** 166 | **Created:** 2025-06-24 | **URL:** https://discourse.scverse.org/t/wrong-log-fold-change-estimation/3696

**Question**: Hello, after using model.differential_expression(), for a specific gene of interest I get the following outcome: proba_de 0.9724 proba_not_de 0.0276 bayes_factor 3.561951 scale1 0.000764 scale2 0.000962 pseudocounts 0.0 delta 0.15 lfc_mean 0.612965 lfc_median 0.933985 lfc_std 2.177583 lfc_min -5.728889 lfc_max 6.05063 raw_mean1 0.4188 raw_mean2 0.502647 non_zeros_proportion1 0.1432 non_zeros_proportion2 0.234677 raw_normalized_mean1 3.688732 raw_normalized_mean2 8.833171 is_de_fdr_0.05 True How can it be that the lfc_mean is positive (0.61), whereas the gene is clearly more expressed in the second group?

**Reply (@ori-kron-wis)**: Hey, Remember the DE in scvi-tools approximate the LFC and its not a deterministic calculation over the raw count data, although here bayes_factor is high and I wouldn’t expect lfc mean to be positive. Can you share more info on what you ran? scvi-tools version, what is your model and data, and how did you run the differential_expression function. Some parameters to think about when running DE: mode, pseudocounts (small epsilon), delta and whether you are running group wise or index wise to compare groups of genes.

**Reply (@Christos)**: Hello thanks for your reply! This is how I run the method: df=model.differential_expression(groupby=‘NR_pos’, group1=‘NR_R_post_Non_responder’, group2=‘NR_NR_post_Non_responder’, mode=“change”, delta=0.1,batch_correction=True,pseudocounts=1e-7 ) Even with a simple Violin Plot we can see that the gene is more expressed in the second group. Screenshot 2025-07-09 at 15.29.52 552×338 33.4 KB

**Reply (@ori-kron-wis)**: Thank you. What is the results running with mode=“vanilla”, pseudocounts=0? Other option is to run with mode=“change”, pseudocounts=0 and test_mode = “two”

## Problems with Bayes factors and LFC changes using model.differential_expression()
**Topic:** 3604 | **Last activity:** 2025-07-09T12:36:31Z
**Posts:** 9 | **Views:** 412 | **Created:** 2025-04-12 | **URL:** https://discourse.scverse.org/t/problems-with-bayes-factors-and-lfc-changes-using-model-differential-expression/3604

**Question**: Has something changed for the differential expression in the most recent version of scvi-tools? Previously, plots of bayes_factor vs. lfc_median were very similar to plots of prob_de vs. lfc_median. prob_de plots still look ok, but bayes_factor plots look like this: image 1096×896 105 KB Additionally, comparing lfc changes to ground truth simulated data gives wildly inaccurate results. Pseudobulk differential expression on the same dataset gives a perfect correlation (pearson=1.0) image 546×564 55.4 KB

**Reply (@cane11)**: Does the second plot look better in the old scVI-tools version? See other post about changes. Could you try with a manual very small pseudocounts like 1e-10? The Bayes factor plot likely looks find for a two-way comparison (change or not change vs the new three way comparison up/unchanged/down). There might be something wrong in computation there.

**Reply (@joseph-siefert)**: Changing pseudo counts gives the same results. Changing test_mode=‘two’ does reproduce the bayes factor plots as before, but the lfc estimates are still off. I applied the LFC changes to only genes expressed in >10% of cells and this increased the correlation to ~0.75, but I am still getting better LFC estimates with pseudobulk. I don’t have the plot on the bottom from a previous version (it was years ago I first tested this), but the results were certainly more accurate. I’ll keep an eye on the other post for the kwargs to reproduce previous versions

**Reply (@joseph-siefert)**: I found the issue, it has to do with total counts per celltype. If there are not at least 10 counts for a gene in a given cell type then the lfc estimates are off: image 1826×448 134 KB

**Reply (@joseph-siefert)**: I forgot to mention that is on the log1p scale, so the model seems to require a fairly high number of counts per cell type for accurate LFC estimates. There also seem to be a high number of false positive detected as well. Pseudobulk does not suffer from either of these issues. Any suggestions or solutions from the developers here? image 875×368 41.9 KB

**Reply (@joseph-siefert)**: Regarding the false positives, it seems to be that genes altered in one cell type are showing up as differentially expressed in other cell types they are not altered in. This appears to be due to the normalization. Here are 3 example false positive genes, the top are library size normalized and log1p transformed and the bottom are normalized values extracted from the scVI model. The raw counts and all associated metadata are identical between batches for these genes in this cell type. These genes are altered in other cell types, and that appears to affect the normalization in this cell type. I have many examples of this. image 1920×758 197 KB

**Reply (@joseph-siefert)**: One month later and still no response or solution from the developers. 750/783 false positive genes have LFC changes in another cell type, but not the cell type they are being identified as differentially expressed in. This is clearly due to the normalization as I showed in the previous post. The normalization procedure appears to be borrowing information from other cell types, leading to skewed normalization and incorrect differential expression in cell types for which there are no changes. Can the developers please address this issue?

**Reply (@sulfur)**: Relatively new user here, but thankful for these detailed and readily applicable toolkits and workflows! Similar to Joseph’s original post, I have been noticing a lot of negative bayes_factor values in recent results from my group when previous iterations only had almost exclusively positive bayes_factor results. We believe that what we are seeing are the log of the Bayes factor. The is_de_fdr_0.05 are showing as True for the results with highly negative bayes_factor values. Untitled-1 copy 1500×1207 201 KB From the extended table above, which only includes is_de_fdr_0.5 True genes (corresponding to the labeled green dots in the volcano plot), proba_de does seem to be much greater than proba_not_de. With potential recent updates to the DE test, is it possible that something has changed wit …

**Reply (@ori-kron-wis)**: Thank you for raising this and sorry for late response. bayes_factor should be positive for expressed genes, but can get negative for highly underexpressed (with pseudocounts>0). We are checking what is wrong with current default settings of the DE. For the meanwhile, I can suggest running the DE function with mode=“vanilla” and pseudocounts=0? Other option is to run with mode=“change” (default now) and force pseudocounts=0 and test_mode = “two”

## Documentation for training with multiple GPUs
**Topic:** 2309 | **Last activity:** 2025-07-09T10:23:59Z
**Posts:** 6 | **Views:** 548 | **Created:** 2024-05-31 | **URL:** https://discourse.scverse.org/t/documentation-for-training-with-multiple-gpus/2309

**Question**: Is there any official tutorial or documentation around how to train with multiple GPUs? I’ve found various issues on github and here, but I didn’t find anything on scvi-tools.org outside of the API documentation.

**Reply (@martinkim0)**: Hi, multi-GPU support is still experimental so we don’t have official documentation or a tutorial yet. You may try out this functionality with the following: model = scvi.model.SCVI(adata) model.train(accelerator="gpu", devices=-1, strategy="ddp_find_unused_parameters_true") but note that the behavior might be buggy.

**Reply (@agdenadel)**: Thanks this is helpful, I had not included strategy="ddp_find_unused_parameters_true" in my attempt to use multiple GPUs.

**Reply (@zEpoch)**: image 640×370 22.4 KB # come to train DestVI.setup_anndata(st_adatas, layer="counts") st_model = DestVI.from_rna_model(st_adatas, sc_model) st_model.train(max_epochs=1200, batch_size = 512, devices=-1, accelerator = 'gpu'， strategy="ddp_find_unused_parameters_true") i have set the strategy="ddp_find_unused_parameters_true" , but it looks like nn.DataParallel rather than ddp

**Reply (@ori-kron-wis)**: Hi , multi-GPU is still under development, we aim to reach that in the coming few weeks. Thanks

**Reply (@ori-kron-wis)**: For anyone checking this post: Project name not set Train SCVI model with multi GPU support SCVI-Tools v1.3.0 now support training on a multi GPU system, which can significantly speed up training and allow you to handle larger datasets. It is supported only on Nvidia GPUs and DDP with CUD...

## Shared cell types not mixing when integrating datasets from different species
**Topic:** 3685 | **Last activity:** 2025-06-19T19:02:10Z
**Posts:** 5 | **Views:** 332 | **Created:** 2025-06-14 | **URL:** https://discourse.scverse.org/t/shared-cell-types-not-mixing-when-integrating-datasets-from-different-species/3685

**Question**: Hello, I am attempting to integrate datasets of the same tissue from different species. Some of the datasets are single-cell while some are single-nucleus. I thought that SCVI would work well for this task, however, as seen in the UMAPs below there is almost no integration of the different datasets, even from the same species. Using the consolidated cell-type labels from the original datasets, it seems shared cell types are in the same region of the umap, but the common cells from the different datasets do not mix (bottom umap). Below I have the code I used to make the umaps, where I used Sample and Method (single-cell vs. single-nuc) as categorical covariates. However, I have also tried other models such as: scvi.model.SCVI.setup_anndata(adata, layer = "counts", categorical_covariate_keys …

**Reply (@fcaretti)**: Hi! It seems that the current default for scvi is that encode_covariates=False ( scvi-tools/src/scvi/module/_vae.py at main · scverse/scvi-tools · GitHub ) while it is True for the batch key. Try with encode_covariates = True so that also the encoder sees them, hope it solves it for you!

**Reply (@sandcell10)**: Hello, thank you for your reply! Interesting that the default for encode_covariates is false. I am surprised this is not mentioned in the scvi integration vignettes. I tried setting encode_covariates=True. From the documentation it seems I would set this in the scvi.model.SCVI command. I also tried setting sample to the batch key instead of a categorical covariate. The updated lines of code are below. Unfortunately, it seems that the datasets still did not integrate well for the most part. I ran my code on a subset of the datasets this time for simplicity and for speed. These three datasets are all single-cell and mouse, so there is less variation than in the example I posted previously. Any other suggestions of what could potentially be preventing the successful integration? Feel free to …

**Reply (@cane11)**: For cross-species and cross-technology integration you might want to check sysVI. This is out-of-scope for regular scVI due to drastic batch effects. Encode covariates is especially not part of the original scVI publication. I marked bad experiences adding many continuous covariates with worse latent space. Apart from that the training looks fine. Be aware that harmony directly targets integration and often integrates more with heavy batch effects, while scVI only integrates if cells are similar to each other.

**Reply (@sandcell10)**: Hi @cane11 , thank you for this information, it is very helpful! I was checking out sysVI and it looks like it will be better suited for these datasets. A few follow up questions: With regards to your comment about adding many continuous covariates, are you saying that sometimes more continuous covariates leads to worse integration? Does the same go with multiple categorical covariates? Basically, is it sometimes more beneficial to go with a simpler model? With regards to your comment about Harmony, would you say that Harmony prioritizes integration at the expense of real variation between batches? If so, would this be considered a bad thing? I would imagine it would depend on what the goals of the integration are, but would love some perspective. Feel free to let me know your thoughts and …

## SMART-seq and MARS-seq pipelines
**Topic:** 3681 | **Last activity:** 2025-06-19T17:56:00Z
**Posts:** 2 | **Views:** 173 | **Created:** 2025-06-10 | **URL:** https://discourse.scverse.org/t/smart-seq-and-mars-seq-pipelines/3681

**Question**: Hi all, I’ve been working on a Python-based single-cell pipeline for cross-study integration built around the scverse ecosystem. So far, it works well for 10x Genomics data, but I’m now looking to expand support to other technologies like MARS-seq and SMART-seq. I am facing some challenges with MARS-seq: using similar QC pipeline to what I use for 10x data (even with adjusted thresholds) seems to be too stringent, I suspect this is due to lower UMI complexity and transcript capture efficiency in MARS-seq compared to droplet-based methods. SMART pseudo-bulk nature also poses some challenges. Has anyone here successfully used scverse-based tools on MARS-seq or SMART-seq data? Interested in ways to adapt QC, ambient removal (SCAR particularly) to work with these. Any insights or examples woul …

**Reply (@cane11)**: SMART-seq, yes definitely in e.g. Tabula sapiens. We also provide tutorials for Smart-Seq2 in scVI-tools and I also used MARS. However, I never combined it with SCAR and obviously changed the QC thresholds for these datasets. Could you provide a clearer error m?

## Workflow advice for totalVI in CITE-seq Multiplexed data
**Topic:** 3613 | **Last activity:** 2025-06-19T17:53:52Z
**Posts:** 4 | **Views:** 252 | **Created:** 2025-04-17 | **URL:** https://discourse.scverse.org/t/workflow-advice-for-totalvi-in-cite-seq-multiplexed-data/3613

**Question**: Hi all, I’m working with CITE-seq data where 4 samples were multiplexed, stained with antibodies in a single tube, and then distributed across 4 sequencing lanes . I’d like advice on the optimal analysis workflow. Specifically: At which step should I split by lanes and then merge adata objects from the same biological sample? Is the following processing order reasonable? Ambient RNA removal (CellBender) Doublet removal QC Protein normalization (DSB) HVG selection totalVI integration (raw count) Since CellBender, DSB, and totalVI all perform some form of denoising, are there any conflicts between them ? Should I use DSB normalization before totalVI, or instead normalize denoised_protein values from totalVI afterwards? Any recommendations, best practices, or reference papers would be greatly …

**Reply (@cane11)**: Cellbender and totalVI are fully compatible. TotalVI expects unnormalized counts and does its own normalization. So you shouldn’t combine DSB and totalVI in the same pipeline.

**Reply (@easyeryiji)**: eason-sjtu: At which step should I split by lanes What’s the purpose of splitting your sequencing lanes data?

**Reply (@cane11)**: Batch effect between lanes is indeed minimal in my hands and also for Cellbender it doesn’t make much difference. I usually run it on the sample directly.

## Amortized LDA Topic Modeling - picking the right number of topics
**Topic:** 3624 | **Last activity:** 2025-06-04T10:49:37Z
**Posts:** 9 | **Views:** 345 | **Created:** 2025-04-25 | **URL:** https://discourse.scverse.org/t/amortized-lda-topic-modeling-picking-the-right-number-of-topics/3624

**Question**: Hi, thank you for incorporating the LDA topic modeling module into scvi. I was curious if folks had suggestions on what would be a good approach to picking the number of topics for topic modeling? My first thought was to run LDA topic modeling on a range of n_topics from 3-100. And then try and use an unbiased approach to get a ballpark of the number of topics, followed by a more supervised approach by looking at the genes in each topic and assessing if they fit what I knew biologically. For the unbiased approach, based on the documentation, I thought to use the ELBO and perplexity scores, but I’m unsure how to interpret these values. I also have quite a few cases where they’re NA or Inf and I’m unsure what to make of that. I was wondering if anyone else had experience with this, and if I’ …

**Reply (@ori-kron-wis)**: I think you are going the correct way. I would also suggest to use scib-metrics to compare the topic integration in the “topic space”. It might take a while to produce. Generally I think you can run the 3-100 by steps of 3-5 then fine tune inside, to save time.

**Reply (@ksinghal28)**: Hi @ori-kron-wis , thank you for your quick response, and the suggestion to run in steps of 3-5- I have quite a few cells so it indeed does take quite a while to run! My dataset is all tumor cells from a group of samples. To get a sense of scib-metrics, I ran topic modeling for a subset of my cells for K values of 5, 10, 15, 20. And then used the scib-metrics Benchmarker function. I crudely assigned each cell to a topic based on the maximum topic value for that cell, and used that dominant topic assignment as the label_key . I used my sample identifier for the batch_key and X_LDA embedding for embedding_obsm_key for the Benchmarker inputs. Is it appropriate to assign a topic to a cell and use that for the label_key in this use-case? bm = Benchmarker( adata_subsample, batch_key="sample_id", …

**Reply (@ori-kron-wis)**: Hi, My idea was to use the topic per cell as label_key, yes. However perhaps there is a way to use the embedding formed on the topic space (see for example this: Topic Modeling with Amortized LDA — scvi-tools You used several embedding keys in the benchmarker but we see only 1 trend line.maybe better to overlay them all on top of each other. I hoped to see a more clear case of optimal topic number that will dominate whole metrics. But we dont see this (perhaps the optimal is between 1-5 though, or need to use other embedding as stated) Re the metrics used in scib-metrics, There are several sources online, mainly GitHub - theislab/scib: Benchmarking analysis of data integration tools which is what scib-metrics is based on

**Reply (@ksinghal28)**: Hi, Thank you for the suggestions! I modified my subsetting strategy to subset by samples instead of cells in the hope that might make it a little easier to find topics across samples. I also ran with a larger range of topics starting from 2. I have overlayed the following 4 embeddings- X_pca- original sc.tl.pca() on scanpy object X_umap- original sc.tl.umap() on scanpy object X_LDA- the LDA topic modeling weights per cell per topic X_umap_LDA- the umap embedding calculated based on the topic space using- #Calculate UMAP in topic space sc.pp.neighbors(adata_topic, use_rep="X_LDA", n_neighbors=20, metric="hellinger") sc.tl.umap(adata_topic) I am a little surprised these change based on the number of topics because I don’t recalculate them for each topic. Do we expect this part of the code t …

**Reply (@ori-kron-wis)**: ksinghal28: I am a little surprised these change based on the number of topics because I don’t recalculate them for each topic. Do we expect this part of the code to modify the X_pca and X_umap values? X_pca and X_umap should not change, given your ran arpack solver, but even so its all deterministic. only if you change the n_neighbors, which I dont think you did. . Are you sure theres not code issue? Yes there some random effect of the session and all, but I wouldn’t think it will be that much. X_LDA and X_umap_LDA will change of course (thats what we check). ksinghal28: Nonetheless, I think this is representative of the kind of outputs I can expect when I run this on my entire dataset. Would these curves match our expectations for evaluating an appropriate ballpark for the number of topi …

**Reply (@ksinghal28)**: Got it, 6 topics for these plots makes sense, thank you for all your help! Closing the loop on the X_pca/X_umap changing and the perplexity and ELBO values: For the X_pca and X_umap, I’m not quite sure- I looped through all the values of K, made a copy of my original anndata object before running topic modeling on it, and then stored the various metrics for all 4 embeddings in a separate dataframe. And to be safe, I stashed the original X_umap embedding to avoid it getting overwritten. For the elbo and perplexity values- All the elbo values except 4 and 6 were between 249,154,710 and 273,089,479. And the value for k=4 was 5.78961E+11 and k=6 was 36,848,271,738 All the perplexity values except 4 and 6 were between ~188 and ~313. And the value for k=4 was 4.32E+196 and k=6 was Inf

**Reply (@ori-kron-wis)**: ELBO although super high, make sense to be optimal on k=6, but perplexity should have been the other way (smaller is better). I think the total_counts (see code) got really small for k=4 or 6, in any case it still point that k=6 is optimal perhaps you can drawn the figures on log scale to see better.

**Reply (@ori-kron-wis)**: Actually with another check, I think the LDA perplexity calculation is missing a (-) before ELBO.

## scVI batch correction clusters all cells from sample in a circle (potential artifact)
**Topic:** 3664 | **Last activity:** 2025-06-03T09:05:55Z
**Posts:** 15 | **Views:** 476 | **Created:** 2025-05-21 | **URL:** https://discourse.scverse.org/t/scvi-batch-correction-clusters-all-cells-from-sample-in-a-circle-potential-artifact/3664

**Question**: When using scVI for batch correction and clustering on my single-cell data, I observed an unusual result: all cells from the same sample are clustered in a circle, separated from the rest. Changes to n_latent , training epochs, and HVG numbers did not resolve the circular artifact. The UMAP plot is attached for reference (see cluster 10) image 647×443 41.6 KB Below are my codes: import scanpy as sc import torch import seaborn as sns import numpy as np import matplotlib.pyplot as plt import pandas as pd import random from collections import defaultdict torch.set_float32_matmul_precision("high") pbmc = sc.read_h5ad('/data/work/data/raw_data/ESCC_PBMC_All_Basic_QC.h5ad') # downsample each sample for hvg calculation sample_key = 'sample_info' n_subsample = 5000 pbmc_list = [] for sample in pbm …

**Reply (@ori-kron-wis)**: Hi, Thank you for posting here. Given you have already performed quality control, including filtering out low-quality cells and genes with low expression levels and that the input matrix is indeed the count matrix before transformation (although I dont see you are preserving counts), I see that the actual selection of HVG’s is not really filtered. Try something like: pbmc[:, pbmc.var['highly_variable']] before setup anndata etc’.. You can also increase the number of neighbors in scanpy.pp.neighbors In addition, what we see in the UMAP is the leiden clusters colors, you might also want to compare when you add “sample_info” sc.pl.umap( pbmc, color=["leiden", "sample_info","tmp_info"], ncols=3, frameon=False, ) Then you should see the integration

**Reply (@CocoConstant)**: Hi, Thank you for your prompt reply and suggestions. I follow your suggestion subsetting the HVG and increasing the number of neighbors from 15 to 25. And I see the strange circle still here. hvg_genes = pbmc_meger.var[pbmc_meger.var['highly_variable']].index.tolist() pbmc.var['highly_variable'] = pbmc.var_names.isin(hvg_genes) pbmc = pbmc[:, pbmc.var['highly_variable']] sc.pp.normalize_total(pbmc, target_sum=1e4) sc.pp.log1p(pbmc) pbmc.raw = pbmc scvi.model.SCVI.setup_anndata(pbmc, layer="counts", batch_key="sample_info", continuous_covariate_keys=['doublet_score', 'n_genes_by_counts'], categorical_covariate_keys=['patient_num']) model = scvi.model.SCVI(pbmc, n_layers=2, n_latent=30, gene_likelihood="nb") model.train(batch_size=512, max_epochs=32) latent = model.get_latent_representation( …

**Reply (@ori-kron-wis)**: OK, so we do see integration of this circle from different samples. I see that you used the doublet score as a continuous covariate, why is that? usually it used to filter cells. I suspect that in your case those cells are exactly this circle. Can you repeat without those continuous covariates? (other option to color the UMP by doublet score)

**Reply (@CocoConstant)**: Actually, I’m afraid that the double score will affect my result after filtering out double cells, so I added it as a continuous covariate. But the issue still exists even after I delete all continuous covariates. scvi.model.SCVI.setup_anndata(pbmc, layer="counts", batch_key="sample_info", categorical_covariate_keys=['patient_num']) image 1124×478 72.9 KB image 572×440 42.5 KB I also tried using Harmony for batch correction, and it yielded good results. However, because of the matched downstream analysis and the rich set of functions, I prefer to use scVI to complete this task. But I truly don’t know how to fix this problem . I’m looking forward to your reply! the result of batch correction with Harmony image 1150×971 240 KB

**Reply (@cane11)**: This is usually an issue with low quality samples (like very few expressed genes or counts after hvg gene filtering). Can you check for this? In my experience, it’s usually about filtering stricter for this specific sample (maybe even excluding it).

**Reply (@CocoConstant)**: yes, I checked the circle samples separatally, and their quality is ok. here is a sample in the circle image 1862×746 80.2 KB and here is another sample not in the circle image 1789×756 82.9 KB

**Reply (@ori-kron-wis)**: is this circle still appears when changing the random state of scvi, sc.tl.umap and sc.pp.neighbors?

**Reply (@CocoConstant)**: yes, I changed the random state, it still exist image 834×640 106 KB

**Reply (@cane11)**: Are these counts before or after highly variable gene filtering? Can you display expression of a couple of cell-type marker genes?

**Reply (@CocoConstant)**: there counts are filtered before highly variable gene. there are some cell-type marker genes exhibited in UMAP image 1785×434 149 KB

**Reply (@cane11)**: Indeed very weird. I have only seen strange behavior when using encode_covariate=True, which you are not passing. Could you display the same markers in PCA (harmony space for this sample and all other samples)? Do you see much lower scVI.criticism scores or reconstruction loss for this specific sample?

**Reply (@CocoConstant)**: I’m sorry for the late reply. there are the same markers in PCA harmony all sample all samples 1850×477 153 KB circle samples circle samples 1849×573 203 KB normal samples normal samples 1847×526 182 KB scvi all samples all samples 1826×484 143 KB circle samples circle samples 1813×516 155 KB normal samples normal samples 1829×514 152 KB examining the reconstruction loss, I noticed that the circle samples with a higher loss value than normal samples, and their values are same. circle_list = ['S-CTF_2426926-2', 'S-CTF_2426926-1', 'B-YPF_2446426-1', 'B-YPF_2446426-2', 'S-PZY_2426498-1', 'S-PZY_2426498-2', 'B-HDY_2447253-1', 'B-HDY_2447253-2', 'B-MXZ_1884381-1', 'B-XLP_2446851-2', 'B-XLP_2446851-1', 'B-YGQ_2425678-2', 'B-YGQ_2425678-1'] for i in circle_list: sub_pbmc = pbmc[pbmc.obs['sample_i …

**Reply (@abs51295)**: Hey, I was just curious. Is the scVI run on raw counts? I see that you assign the .raw attribute after normalizing counts.

**Reply (@ori-kron-wis)**: it is a bit confusing but yes it uses .raw attributes for down stream analysis (usually log normalized etc..), but trains with real raw counts, found in .X attributes (or a custom layer), if using adata.

## Domain adaptation to pre-train batch correction model using paired data
**Topic:** 3633 | **Last activity:** 2025-05-27T06:44:23Z
**Posts:** 13 | **Views:** 438 | **Created:** 2025-04-30 | **URL:** https://discourse.scverse.org/t/domain-adaptation-to-pre-train-batch-correction-model-using-paired-data/3633

**Question**: Good afternoon scvi team! I am very new to the scvi tool and moslty have been working with scRNA-seq data within R environment. I came around a specific issue which scvi could potentially be well suited for so I would love to learn more and would appreciate any guidance. I would like to adapt scVI to learn a transformation between two batches being RNA sequencing protocols. I have data where both protocols were applied to cells from the same samples (so I have “ideal” comparison pairs between batches). Ideally, I’d like to pre-train a model on these “ideal” matched samples that could take the sample of one batch and map it into the “space” of another batch. I want to then save this model for further use on non-ideal/regular data to map it from one protocol space to the other. If this works …

**Reply (@ori-kron-wis)**: Hi Theres no out of the box function to do this, but I suggest to run a scarches method with a tweak at the end: For the reference: train a scvi model with tech/protocol as batch key with both protocols “matched” data. You can also do it as a scanvi model if you have the cell type labels data for each sample, it will be even more accurate, but not mandatory. For the query: you use the new data that came from just one of the protocols and run the scarches scheme on it to create a new, fine tuned model (it will still “remember” the missing protocol batch) Finally apply the fine tuned query model get_normalized_expression function with transform_batch to the missing protocol and library_size=“latent”. A sort of imputing (or reconstructing) the other protocol gene expression. You can validate …

**Reply (@Valerie)**: Dear Ori, Thank you so much for the detailed explanation — this approach makes a lot of sense. I had a follow-up question regarding the use of paired samples: as I understand, the model will learn from having both protocols represented in training via the batch_key , but is there a way to more directly leverage the fact that many of these samples are “paired” — they come from the same individual but were processed using two different protocols? In my dataset, most of these matched pairs come from different tissues, so while there’s substantial biological variation across sample_id s, within a given pair (same sample_id ) the main difference should only be the protocol. So is there a way to integrate sample_id into training — perhaps via additional conditioning or contrastive learning — hel …

**Reply (@cane11)**: Hi, this type of hierarchical batch effects can be modeled with MrVI. To improve integration of different technologies you might want to check sysVI.

**Reply (@Valerie)**: I see — I’ll definitely look into those suggestions! I think what I’m aiming for might be slightly different: I’d like to treat the paired samples as a kind of ideal supervision — where a sample from one protocol (e.g., batch 1 ) can be directly compared to its counterpart from the other protocol ( batch 2 ) because they come from the same individual. Rather than treating sample_id as a batch effect, I was thinking of using it to guide the model — so that batch 1 and batch 2 representations from the same sample are explicitly aligned or used in a loss. The unmatched samples from different individuals wouldn’t really need to “see” each other at all — the focus would just be on learning a mapping via those matched pairs. Does that sound reasonable, or would that require deeper customization? …

**Reply (@ori-kron-wis)**: is sample_id the same as donor_id (individual)? is the same donor samples comes from the same tissue? otherwise you can use donor_id as the batch key together with protocol Im not so sure I understand what is “paired” here (like in the typical sense that we want to isolate the effect a specific gene) except that each of the donor’s samples were running in 2 protocols. Is it a case where the counts of one protocol always > than the other protocol counts? if it does, does also modelling of the difference signal between their expressions make sense? I think the method I suggested before, perhaps after modelling with sysvi (not scvi), will be interesting to watch

**Reply (@Valerie)**: Sorry, yes, the sample_id I was talking about is the donor_id (same individual). The same donor samples for batch 1 and batch 2 are from the same tissue. In terms of “paired”, I meant that for each donor_id, this dataset has two samples - one sequence with protocol A (batch 1) and the other with protocol B (batch 2). The whole dataset is a combination of such matched/paired samples from many donors. Thus, I thought if I could pre-train the model on matched donor samples (since the only difference between them should technically be the protocol), it would be more accurate. It is not necessary the case that the counts of one protocol are always greater than the other, it depends on a gene. My apologies for the confusion, I am very new to this but very interested in possibility of this projec …

**Reply (@Valerie)**: Good afternoon Dear Ori, I wanted to thank you for your help as I did end up using your approach to get the “reconstructed” gene expression of the other protocol. Now I want to compare that expression to the actual expression, which I have in a “raw” format. I was wondering if I should also preprocess it with a model or run a standard log transformation to be able to compare it to the “reconstructed” gene expression? Thank you!

**Reply (@ori-kron-wis)**: Here we’ll need to think a bit: You basically made a transfer learning + batch projection. get_normalized_expression function returns the normalized gene expression, so in order to return to the original “Raw counts” (of that batch transform) you need to reverse the same normalization and transformation (usually you normalised the counts of original adata , e.g by 1e4 and might did a log1p transform, so you need to use library_size=1e4 and potentially exp(x)-1). But this will still be an approximation . I would also check what library_size=“latent” will bring you. Theoretically in order to generate the raw gene counts from a trained model, we should use the posterior_predictive_sample() function over the trained model, but in this case we dont have the option to do the batch projection, bu …

**Reply (@cane11)**: @ori-kron-wis can you create a PR to do batch projection for posterior predictive samples? Pretty much in line with another private request from last week. Thanks!

**Reply (@ori-kron-wis)**: Yes I wasnt sure if this is possible, but it will be a great addition.

**Reply (@Valerie)**: Thank you, Ori! I will try both approaches, starting from the simpler one first. So, to reiterate, you are saying that the output of the get_normalized_expression is approximately equivalent to scaling by library size (typically 1e4, but as I understood I could change the parameter library_size to desired scale) and then performing log1p? I have check the summary statistics (row sums and column means) of the output and it doesn’t look like it has been log1p transformed, however the row sums range around the library_size specified. Is it possible that the get_normalized_expression returns expression where each cell are divided by the total counts for that cell and multiplied by the scale.factor (library_size that is chosen in this case)? I appreciate all your help! Apologies for so many que …

**Reply (@ori-kron-wis)**: yes, this is what happens. we usually normalized the total cell counts before running the model (sc.pp.normalize_total) and also do log1p over the raw data (sc.pp.log1p), see our quick start tutorial . so the scaling you do now in get_normalized_expression (library size) dependes on that. It is possible you havent done any normalization before modelling, so it will stay 1. Also the total counts might be not exactly the same size (like you said its in “around the range”) as you probably ran HVG selection before modelling. So for summary, Its a reverse transformation. This will bring you the estimated raw counts eventually. no worries with too many questions, we are always happy to help

## Help on MultiVI for data modality
**Topic:** 2134 | **Last activity:** 2025-05-16T01:33:04Z
**Posts:** 2 | **Views:** 311 | **Created:** 2024-02-29 | **URL:** https://discourse.scverse.org/t/help-on-multivi-for-data-modality/2134

**Question**: In the published manuscript published in Nature Methods, it was demonstrated that MultiVI can be used on multi-omics data that include protein abundance measurements (e.g. CITE-seq). However, the tutorial on scvi-tools only shows its use on scRNA-seq and scATAC-seq data. My question is, if I want to use Multi-VI with protein dat, how should I proceed?

**Reply (@MP_Epana)**: If you review the MultiVI documentation, you’ll see that there’s a protein key, which will point to your protein matrix, just like TotalVI. If you have questions, you can review the TotalVI tutorial and verify that the same logic and parameters work.

## Protocol for model optimization (currently focused on MultiVI)
**Topic:** 305 | **Last activity:** 2025-05-14T21:53:35Z
**Posts:** 4 | **Views:** 731 | **Created:** 2022-02-28 | **URL:** https://discourse.scverse.org/t/protocol-for-model-optimization-currently-focused-on-multivi/305

**Question**: Hi there - first, I am simply blown away by the suite of tools you have assembled. It is truly awe-inspiring and sets the bar for any other python / comp-bio developers. My question (and please assist me if I have placed this on the forum in an undesired location): Do you have a general protocol for model optimization? In this instance, I am particularly interested in using MultiVI to integrate cells from the same sample measured by scRNA-seq and scATAC-seq. After following the tutorial , I have been playing around with the model parameters such as the # of hidden units / latent variables. Despite some initial attempts at tuning parameters, etc., I have only obtained results that show a sub-optimal co-embedding: 'MultiVI Model with INPUTS: n_genes:7213, n_regions:28053\nn_hidden: 187, n_la …

**Reply (@adamgayoso)**: mvinyard: It is truly awe-inspiring and sets the bar for any other python / comp-bio developers. Thank you mvinyard: I am particularly interested in using MultiVI to integrate cells from the same sample measured by scRNA-seq and scATAC-seq. After following the tutorial , I have been playing around with the model parameters such as the # of hidden units / latent variables. MultiVI requires to have some data where ATAC + RNA are measured simultaneously. It doesn’t look like you have that here?

**Reply (@mvinyard)**: Ah, I see - I misread the intention of the example notebook. You are correct: I do not have data where each modality is measured simultaneously in the same cell (just the same sample). That brings me to two questions: If I paired (same-cell) RNA/ATAC data from a model cell line of the same disease, do you think this could serve as an anchor point along which we might integrate other samples measured by the same assays for which we have separate but matched modality measurements? Perhaps this question involves too many unknowns from your end to say yes or no. Do you have any other recommendations given matched (but not paired) scRNA-seq and scATAC-seq samples using your framework? I could use PeakVI and scvi to analyze the modalities independently, but I would be curious to know if there is …

**Reply (@MP_Epana)**: This is crazy old, but I’ll respond for the record: I’ve seen pretty good integration for unpaired data when the peaks actually reflect the same amount of diversity as the scRNA. Frequently, the 10x peak matrix and other peak matrices based on bulk peak-calling will miss the diversity of peaks necessary for good integration. Working with peak calls from a scATAC-seq peak calling, like MOCHA, can help immensely, and anchoring points of RNA/ATAC can also help, though it can’t completely overcome it.

## How to interpret reconstruction loss increase but elbo loss decrease on trained scvi and scanvi models
**Topic:** 3642 | **Last activity:** 2025-05-11T09:19:46Z
**Posts:** 2 | **Views:** 380 | **Created:** 2025-05-09 | **URL:** https://discourse.scverse.org/t/how-to-interpret-reconstruction-loss-increase-but-elbo-loss-decrease-on-trained-scvi-and-scanvi-models/3642

**Question**: Hi, I am trying to use lung cancer single cell atlas ( https://luca.icbi.at/ ) to annotate a Xenium experiment. Given Xenium is gene-panel based (~400 genes), I retrained atlas by subsetting features to 400, first training scvi model to integrate, then using semi-supervised scanvi model with cell type as label key. For both model, I trained 300 epochs. However, when examining the model metrics, I noticed elbo loss decrease but reconstruction loss increase. Here are the plots luca_ref_404var_lungOnly.model_metrics 1500×1000 97.6 KB I am wondering: Is my planned workflow (subset features - reference scvi training- reference scanvi training - query-reference mapping) valid? how do we interpret “reconstruction loss increase”? I am a little suspicious that the features from Xenium gene panel ar …

**Reply (@ori-kron-wis)**: yes the problem where reconstruction loss increase and KL loss keep decreasing (or vice versa), is something known for cVAE’s.. and is a result of optimal parameters being optimzie “better” in the direction of one of those losses only (i.e other directions). however, the global ELBO is what you really need to look for and it does optimize to a final plateau. Having said that, you can decide to stop the training after certain number of epochs and it may depends on your downstream task whether you prefer low reconstruction loss (a good generative model) or low KL local (likely better integration). In your case, increase in reconstruction loss means the model relays less on encoder latent variables and more on the decoder mapping (a sort of overfit). I would suggest to play of some of the tra …

## Nan values in the latent of scanvi_query
**Topic:** 3619 | **Last activity:** 2025-04-23T11:50:46Z
**Posts:** 2 | **Views:** 108 | **Created:** 2025-04-22 | **URL:** https://discourse.scverse.org/t/nan-values-in-the-latent-of-scanvi-query/3619

**Question**: Hi I’m trying to do a label transfer using SCANVI using the following script: import scanpy as sc import scvi # scvi==1.0.4 from scvi.model import SCVI from scvi.model import SCANVI import rapids_singlecell as rsc pancreas_full = sc.read_h5ad('./data/t2d/pancreas_full_v2.h5ad') rmask = pancreas_full.obs['batch']=='reference' rdata = pancreas_full[rmask].copy() qdata = pancreas_full[~rmask].copy() rdata.obs['cell_type_scanvi'] = rdata.obs["cell_type"].values scvi.model.SCVI.setup_anndata(rdata, layer="counts", batch_key="batch") scvi_ref = scvi.model.SCVI(rdata, n_layers=2, n_latent=30, gene_likelihood="nb") scvi_ref.train( max_epochs=1000, check_val_every_n_epoch=10 ) scanvi_ref = scvi.model.SCANVI.from_scvi_model(scvi_ref, labels_key='cell_type_scanvi', unlabeled_category="Unknown") scanv …

**Reply (@ori-kron-wis)**: Hi, Why not working with most recent version of scvi? many things have changed since, and it will be not so easy to tackle your issue, if it relates to that version alone. Having said that, seems your process is ok. But getting a fail on the first epoch usually means something is wrong in setup of data or data quality itself. see Frequently asked questions — scvi-tools given you haven’t selected your highly variables genes before training, you how big is you data? can it be related to memory issues? how did you make layer “counts” ? note that in the tutorial we train scvi for scArches with additional parameters which tend to work well with scArches (although its not mandatory): scvi_ref = scvi.model.SCVI(rdata, n_layers=2, n_latent=30, gene_likelihood="nb", use_layer_norm="both", use_batch …

## Modify gene identifiers stored in existing scVI model
**Topic:** 3602 | **Last activity:** 2025-04-20T13:59:04Z
**Posts:** 2 | **Views:** 126 | **Created:** 2025-04-11 | **URL:** https://discourse.scverse.org/t/modify-gene-identifiers-stored-in-existing-scvi-model/3602

**Question**: Hi! I trained a lot of scVI models with different parameters to asses their impact, however I realised at the end of the exercise that the original AnnData file was indexed in var through a simple numeric index (so the index wasn’t either gene identifiers nor gene symbols). It took quite a while to train all the models. Is it possible to modify, perhaps loading as a torch object, the models so that I can only change the gene labels used in the model (so that I can use them for cell type labelling with other datasets)? If I load the model through torch: model = torch.load(f"{model_path}/model.pt", map_location=torch.device("cpu")) I can see these two dictionary elements with arrays containing my gene indices: >> model['var_names'] array(['67', '83', '125', ..., '60058', '60060', '60159'], d …

**Reply (@ori-kron-wis)**: if I understood you correctly, you can load the saved model simply with model = SCVI.load(pretrained_scvi_path, adata=adata_tmp) and adata_tmp will be the other adata you use, where its var_names might be different than originally trained, like other indices(although it should be the same number of genes and order matters). The rest of registry for model will initialise correctly. You should be able to fine tune training then. I think you method will work also though. you can compare them. Not sure it will help here but another more general option will be to use prepare_query_anndata and than load_query_data with the new dataset, but here it will look for common gene indices between the model and new adata, order them as the model expect and pad with 0 those that are missing. You might use …

## Anndata Manager Store
**Topic:** 3594 | **Last activity:** 2025-04-20T07:52:04Z
**Posts:** 12 | **Views:** 334 | **Created:** 2025-04-09 | **URL:** https://discourse.scverse.org/t/anndata-manager-store/3594

**Question**: Hi, I have a basic question about the procedure to run scvi models. When a model is created and trained, we run 3 instructions, 1) setup_anndata, 2) instantiate the model, 3) model.train() My understanding is that when we run setup anndata, we registered some fields in the anndata and a “AnndataManager is stored in the AnndataManager Store” . So, my question are: A) let’s say that I run step 1, setup_anndata, where is the anndatamanager store? B) can I access the anndatamanager without going to step 2 and creating a model? C) after step 1, we have the fields encoded and written to the anndata.obs, but where is the state registry? Thanks

**Reply (@ori-kron-wis)**: Hi, AnndataManager is hidden at this point but you can extract it by its pointer that is the scvi_uuid or scvi_manager_uuid you added to adata while doing the setup anndata, like so: SCVI._get_most_recent_anndata_manager(adata) . Then, the state registries exists in any field that will be including in the AnndataManager registry.field_registries, e.g: AnndataManager.registry['field_registries']['batch']['state_registry'] and so on..

**Reply (@Mariano)**: Two points: From a software engineering point. Where is the AnndataManager is store? What does it mean is hidden? I want to learn how this is store within the python environment. Another software engineering point. I want to know if data is duplicated and where. So, after my point 1), data resides in the anndata object and the AnndataManager does not have the anndata object linked to it. After point 2. Is the anndata duplicated inside the scvi object and in the anndata object itself. During point 3, when the AnndataManager convert to andtorchdataset, is the data duplicated? Thanks !

**Reply (@ori-kron-wis)**: AnndataManager Store it is a dictionary initialized per model type (e.g SCVI) which hold those uuid’s. see this in the base_model class (which every model inherits from), _setup_adata_manager_store and _per_instance_manager_store. it is not exposed during the setup anndata directly, only those mapping (but you can fetch it, see previous answer). its a kind of lazy initialization for the model. So its there in memory and yes AnnDataManager link to that adata (a reference copy, not value), as well as each instance of the model holds a copy of it when initialized. so thats a duplication and the reason is that each model can ran with its own scenario and can add more information on top of that duplicated adata (like latent layer), later to be saved and used elsewhere perhaps. as for AnnTorchDa …

**Reply (@Mariano)**: Hi Ori, thank you so much. A) This is clear now. During my step 1, setup_anndata, scvi writes class variables even when the class is not initialized. This is some behavior from python that I was not aware. B) This is also clear. During my step 2, anndata is duplicated, so in principle, I can remove from memory the first one without affecting the model. Two more questions, For AnnTorchDataset, why do you say that data duplication is “train time duplication” and does not consume memory? Is this because this is happening on a batch of data? Can you give me a really brief overview of how you are thinking of handling the AnndataManager and the Data in the class duplication with a CustomDataloader? Thanks !

**Reply (@ori-kron-wis)**: oh it consume memory, but only a batch of data, and then released (unlike the previous duplication). in custom dataloaders, in which I believe you meant we don’t use adata, we dont run the setup_anndata, and the model is initialized without adata. instead we use a pre-defined registry, which suits the custom dataloader and the model of interest and it is part of the custom dataloader class initialization. so no lazy init here. than we use the registry to init the model and the dataloader to create batches and run the training. its a parallel, bypass, mechanism to the AnndataManager. actually this is something that we are now adding officially to next release of scvi-tools (we have a custom dataloader for LaminAI and one for Census data based on TileDB).

**Reply (@Mariano)**: Hi Ori Do you have the example of the custom data loader ? Is it in the branch? Best

**Reply (@ori-kron-wis)**: yes its in the custom dataloaders registry branch

**Reply (@Mariano)**: Hi Ori, I gave it a try and made some comments on the branch, there was an error on the tutorial. I want to help with this so, is there any chat that you are having Can and you about this? Also, I compare head to head the TileDB and the regular anndata loaders and Tile is 50% slower.

**Reply (@Mariano)**: One more thing… how do I do get_latent() with the TileDB data module?

**Reply (@Mariano)**: Last thing. I tested the TileDB dataloader ir regular and DDP mode and what is causing the delay is the slow access to data. GPU peaks and process super fast but in between batches there is a long waiting time.

**Reply (@ori-kron-wis)**: @Mariano thanks for all the help. you will be able to see how we use get_latent in the corresponding custom dataloders tutorial which has a PR in scvi-tools-tutorials ( added custom dataloaders initial tutos by ori-kron-wis · Pull Request #425 · scverse/scvi-tutorials · GitHub ) because those are all development specific questions, for a version that is not released yet, I suggest to continue this discussion on the relevant branch/PR.

## Scvi package can't be installed into google colab?
**Topic:** 3600 | **Last activity:** 2025-04-20T07:17:49Z
**Posts:** 7 | **Views:** 191 | **Created:** 2025-04-11 | **URL:** https://discourse.scverse.org/t/scvi-package-cant-be-installed-into-google-colab/3600

**Question**: image 1185×666 66.2 KB It was working two weeks ago, but now it just doesn’t work.

**Reply (@ori-kron-wis)**: theres a temporary problem with the uv package (not scvi-tools) please add this line, before running the install of scvi_colab and it will work: #A Manual fix to uv issue in Colab, see: https://github.com/astral-sh/uv/issues/12724 import os os.environ["UV_CONSTRAINT"] = os.environ["UV_BUILD_CONSTRAINT"] = ""

**Reply (@cane11)**: Could we add this to the scVI-colab package or does it need to be called outside of it?

**Reply (@Jihua-Liu)**: image 805×877 76.2 KB Not exactly sure why this doesn’t work for me.

**Reply (@ori-kron-wis)**: image 1688×538 58.2 KB try it after the installation of scvi-colab, and restart your session. (I installed a specific branch here, but try it with just install()) but youre right, it is not working right now (it worked for me yesterday), I guess their on the fix, at least from what I see in the discussion of the issue Google colab issue · Issue #12724 · astral-sh/uv · GitHub you can still install with !pip install --quiet scvi-tools make no sense to add to the package, its not related to scvi-colab, any package will not work with uv in colab now (also numpy…) w/o the fix.

**Reply (@cane11)**: We should then disable uv until Colab fixes it. It’s annoying but more annoying for users to first need to find this issue and then install it correctly.

**Reply (@ori-kron-wis)**: seems the issue is solved with colab/uv integraion: image 2456×708 82.9 KB

## Is the scVI model applicable to bulk RNA-seq data from cell lines?
**Topic:** 3610 | **Last activity:** 2025-04-16T05:27:00Z
**Posts:** 2 | **Views:** 256 | **Created:** 2025-04-16 | **URL:** https://discourse.scverse.org/t/is-the-scvi-model-applicable-to-bulk-rna-seq-data-from-cell-lines/3610

**Question**: Hi guys, I know that scVI is primarily designed for modeling UMI-based single-cell RNA-seq counts, but I’m wondering whether it might also be applicable to bulk RNA-seq data from homogeneous cell lines. Since bulk RNA-seq typically uses full-length sequencing protocols, I was thinking it might be possible to preprocess it similarly to Smart-seq2 data. After reviewing the scVI parameters ( scVI — scvi-tools ), I’m curious — if we consider bulk RNA-seq data as essentially the sum of a large number of identical cells, dropout events should be rare. In that case, would I need to adjust any specific parameters related to dropout modeling (e.g. disable zero inflation or tweak dispersion priors) to make scVI suitable for this type of data? Would appreciate any thoughts or suggestions on this.

**Reply (@cane11)**: Hi, you don’t need any adjustment. The division by gene length in some of our tutorials is just so that Smart-Seq2 and 10X become more similar. I would use the default of ZINB reconstruction loss. However, keep in mind that for low sample number (cell number in single cell studies) the model will not generalize well (if you have beyond 500 bulk samples the limitation shouldn’t matter much).

## How should I calculate the knn entropy using the leiden clusters?
**Topic:** 3537 | **Last activity:** 2025-04-10T07:55:39Z
**Posts:** 2 | **Views:** 95 | **Created:** 2025-03-11 | **URL:** https://discourse.scverse.org/t/how-should-i-calculate-the-knn-entropy-using-the-leiden-clusters/3537

**Question**: Hello: How should I calculate the knn entropy using the leiden clusters? https://arxiv.org/pdf/1506.06501v1 Thanks a lot

**Reply (@ori-kron-wis)**: you will need to measure how much the points in each leiden cluster differ from the surrounding points in the KNN graph. given you are working with adata and scvi latent space: knn graph can be computed with: sc.pp.neighbors(adata, use_rep=SCVI_LATENT_KEY) leiden clusters can be made with: sc.tl.leiden(adata, key_added="leiden_scVI") then use this information to perform: For each data point in the dataset, find its K-nearest neighbors from the KNN graph. For each cluster, calculate how many of its K-nearest neighbors belong to the same cluster and how many belong to other clusters. Calculate Entropy per cluster by −∑p_i*log(p_i) , where p_i is the probability of a point being in a specific cluster (based on its KNN neighbours).

## How to fix number of nodes used in HPC environment with scvi.train (via R & reticulate)?
**Topic:** 3579 | **Last activity:** 2025-04-10T06:01:55Z
**Posts:** 9 | **Views:** 195 | **Created:** 2025-03-28 | **URL:** https://discourse.scverse.org/t/how-to-fix-number-of-nodes-used-in-hpc-environment-with-scvi-train-via-r-reticulate/3579

**Question**: Hi, I’m using scvi via R using reticulate. All cpu nodes of the clusters are used, I would like to restrain this behavior when I call model$train function. Also I wanted to know if I should start the integration from counts or log normalized counts. It’s not clear to me. Any ideas would be more than welcome, thanks ! In fact I’m looking for an integration with singlecellexperiments and not the the seurat approach as described here library(reticulate) library(sceasy) ## subset to predefine list of HVGs sce.combined <- sce.combined[top_hvgs,] sc <- import("scanpy", convert = FALSE) scvi <- import("scvi", convert = FALSE) ## transform sce to anndata adata <- sceasy::convertFormat(sce.combined, from="sce", to="anndata", main_layer="counts",transfer_layers = c("logcounts", "normcounts"), drop_s …

**Reply (@ori-kron-wis)**: Hey @ZheFrench scvi-tools models require the raw counts for integration. other downstream analysis tasks might require the log-normalized (like in seurat or scanpy) The trainer complains is about the dataloading number of workers. You can set it up with something like: run setup_anndata and adjust backend settings scvi$model$SCVI$setup_anndata(adata) scvi$settings$dl_num_workers = 79L scvi$settings$persistent_workers = ‘True’ #try also with False scvi$settings$num_threads = 3 #num cpus create the model model = scvi$model$SCVI(adata) train the model model$train() This will run 3 cpu nodes. There is some overhead for using workers and also the persistent workers might still be left alive and you’ll need to kill them manually. Not sure if it will bring you any added advantage, but try it.

**Reply (@ZheFrench)**: Thanks. It gives me the following message and all the cores are still actived even setting dl_num_workers to a lower value : Epoch 5/50: 8%| | 4/50 [01:01<12:41, 16.54s/it, v_num=1, train_loss_step=7.86e+3, train_loss/data2/USERS/anaconda3/envs/R-4.4.1/lib/python3.12/multiprocessing/popen_fork.py:66: RuntimeWarning: os.fork() was called. os.fork() is incompatible with multithreaded code, and JAX is multithreaded, so this will likely lead to a deadlock.

**Reply (@ori-kron-wis)**: run with dl_num_workers=1 and num_threads=1. do you see any change? how do you see all cores are taken? in what operating system are you?

**Reply (@ZheFrench)**: Nope there is no impact setting one everywhere ,all cores run ~ 100 % . I work on a Ubuntu 18.04.6 LTS (GNU/Linux 5.4.0-150-generic x86_64) system with 80 cores and no job scheduler.

**Reply (@cane11)**: Can you check CPU use with: export OMP_NUM_THREADS=8 export MKL_NUM_THREADS=8 import torch import time a = torch.randn(5000, 5000) b = torch.randn(5000, 5000) start = time.time() for _ in range(20): torch.mm(a, b) print("Done in", time.time() - start, "seconds")

**Reply (@ZheFrench)**: Yep this work on 8 cpus as expected. import os os.environ[“OMP_NUM_THREADS”] = “8” os.environ[“MKL_NUM_THREADS”] = “8”

**Reply (@ZheFrench)**: Still SCVI doesn"t want to work only on the 8 cores only. os$environ[“OMP_NUM_THREADS”] = “8” os$environ[“MKL_NUM_THREADS”] = “8” scvi$settings$dl_num_workers = 8L #(defautl 0) scvi$settings$persistent_workers = ‘True’ #try also with False that is default scvi$settings$num_threads = 8L #num cpus tc$set_num_interop_threads = 8L

**Reply (@ori-kron-wis)**: to change a system environment in R do it with Sys.setenv(OMP_NUM_THREADS = "8") Sys.setenv(MKL_NUM_THREADS = "8") and not through the reticulate package and using os (a python package)

## Understanding scVI integration inside R with Seurat v5 & SCTransform
**Topic:** 3588 | **Last activity:** 2025-04-06T08:52:48Z
**Posts:** 2 | **Views:** 660 | **Created:** 2025-04-04 | **URL:** https://discourse.scverse.org/t/understanding-scvi-integration-inside-r-with-seurat-v5-sctransform/3588

**Question**: I have a set of single-cell libraries from an drug treatment experiment - early timepoint, treatment/DMSO at 3 timepoints (21 libraries total). I have preprocessed each library separately with Seurat using SCTransform v2 additionally regressing out cell cycle, MT genes and Ribosomal genes. I now have a list object of normalised and transformed libraries. I want to run integration as per Integrating datasets with scVI . I have a few questions regarding methodology: Is it OK to use SCTransform-ed counts or should I still feed in log-normalised counts from NormalizeData() instead? How should I select the HVG for feeding into the model? Currently my approach is to take all unique genes from the set of HVG defined for all of my libraries in the list (21 sets of slightly differet HVG). When I se …

**Reply (@ori-kron-wis)**: Hey @y.grabovska Thank you for posting here. I think your analysis is correct. For integration SCVI-Tools need to have the raw counts. You can also think about the union of HVG’s per group, not only intersection. how much they differ? But, there are method that also compensate for the group size or batch like Scanpy’s highly_variable_genes() with batch_key (Python) or Seurat’s SelectIntegrationFeatures() (R). You can downsample the groups sizes to match each other and repeaet this process several times. Its ok to manually remove HVG that are known to be in fact, noise.

## inferCNVpy after running scVI with batch as key
**Topic:** 848 | **Last activity:** 2025-03-24T07:19:32Z
**Posts:** 6 | **Views:** 1155 | **Created:** 2022-10-20 | **URL:** https://discourse.scverse.org/t/infercnvpy-after-running-scvi-with-batch-as-key/848

**Question**: Hi scverse community, I have at my disposal a bunch of datasets, of which one is a cancer patient while the other ones are the same organ but in a healthy condition. The idea is to use the cell types of the healthy samples as reference cells for inferCNVpy, but I first want to integrate them with the basic script for scVI. Now, I have some questions that originate from basically being a newbie in working in the scverse ecosystem (I’ve always used R/Bioc tools) but I think this could be useful for many users. The history of the samples is the following: read alignment and quantification with cell ranger QC, normalization, HVF selection, dim. reduction, clustering and annotation in R/Bioc (scater + Seurat) 3a. Merge all healthy samples in a single Seurat object 3a. Convert both (tumor + heal …

**Reply (@zvittorio)**: Update. Now I know that: scVI is not going to alter the adata.X matrix (unless I indicate to do so, I guess) infercnvpy works on adata.X by default, but it has the layer argument (in infercnvpy.tl.infercnv ) to take different layers as input infercnvpy expect a “gene expression matrix, appropriately preprocessed” in the adata layer it is going to work on I am still open to comments on the steps I list in the original post The open questions that sums it up is the following: does it make sense to run infercnvpy on the normalized (decoded) gene expression from scVI? (basically the output of scvi.model.SCVI.get_normalized_expression ) Again, thanks a lot to anyone that can provide comments, help or answers! Kind regards Vittorio

**Reply (@adamgayoso)**: Thanks for the post. I’m trying to understand where scvi-tools fits into this pipeline. Do you want to smooth the gene expression values?

**Reply (@zvittorio)**: Sorry for the late reply, I must have missed the notification. I don’t want to smooth gene expression necessarily. My doubt is what and how should I use the results from scvi model training for further analysis? I have seen that the scvi normalized expression values are took into account for visualization across all batches. But can you use the same values as input for other tools? (in this example, infercnv)

**Reply (@jpagolia)**: I am encountering a similar issue and wanted to follow up on this question. In a typical tumor atlas project, you would want to verify your annotations of tumor cells by CNV. But the tumor samples are typically run in multiple batches, and infercnvpy (as well as inferCNV and other CNV inference packages) is susceptible to batch effect. I’d like to be able to use scvi.model.SCVI.get_normalized_expression() with the transform_batch parameter to obtain a batch-corrected gene expression matrix for direct input into infercnvpy. I’ve done this, but the results look much worse (overly smoothed, without clear CNV clusters) than the original non-batch-corrected results. Has anyone used scVI output as input for infercnvpy? How did you do it? Does the strategy above make sense? Any alternatives that …

**Reply (@grst)**: Sorry, I haven’t attempted yet to use infercnv with batch correction. The best approach would probably be a dedicated model that learns the copy number variations taking batch effects into account, but that would be a research project by itself.

## Suggestions for training on xenium spatial transcriptomics dataset
**Topic:** 3394 | **Last activity:** 2025-03-22T19:51:20Z
**Posts:** 6 | **Views:** 449 | **Created:** 2024-12-21 | **URL:** https://discourse.scverse.org/t/suggestions-for-training-on-xenium-spatial-transcriptomics-dataset/3394

**Question**: Hey @cane11 , We have been using baysor followed by scVI so far for batch correction on Xenium datasets. It’s working fine out of the box where it’s able to discern major cell populations. One problem we see frequently is the mixtures of mis-segmented cells (T cells with macrophages for example). Is there any way of changing the model parameters for scVI that can help mitigate the issue? Thanks

**Reply (@cane11)**: Hi, I reacted to this privately. In the mean time, resolVI is released that addresses this and other problems with ST data.

**Reply (@abs51295)**: Hey @cane11 , I got access to it but haven’t tried it yet. We just ended up using scVI for our current dataset. Is the run time of resolVI similar to scVI? Thank you for the access.

**Reply (@abs51295)**: Hey @cane11 . Is there a way to set batch for spatial coordinates differently than for batch correction for resolVI? My issue is I have individual TMA cores that I want to compute spatial neighbors on but I want to use TMA slides as a batch for batch correction.

**Reply (@cane11)**: Hi, it’s quite straightforward to change the code to allow for it. However, are your TMA not spaced in a manner that you anyhow only get neighbors within each TMA and not across? You can also set the data up manually and skip the resolVI step: scvi-tools/src/scvi/external/resolvi/_model.py at 9396c33f82193e8e23ddbfbf27921d7fd2972078 · scverse/scvi-tools · GitHub

**Reply (@abs51295)**: Yeah, I ended up copying the _prepare_data function and change it myself. When you say TMA, I assume you mean individual punches (cores) that are far enough on a single TMA slide; yes they are for the most part but there might be some edge effects or just cores that end up getting squished together. Also, I see that the parameters in the reproducibility repository aren’t the default ones in resolVI. Do you prefer one over the other?

## Scvi-tools solo return synthetic doublets
**Topic:** 3545 | **Last activity:** 2025-03-18T20:55:02Z
**Posts:** 4 | **Views:** 152 | **Created:** 2025-03-15 | **URL:** https://discourse.scverse.org/t/scvi-tools-solo-return-synthetic-doublets/3545

**Question**: Is it possible to return the synthetic doublets with solo. I would like to be able to run pca on my adata with the synthetic doublets and visualize what my cell clusters look like relative to the stimulated doublets.

**Reply (@ori-kron-wis)**: Yes I believe using SOLO in the regular way on your adata and color your PCA clusters based on the SOLO prediction will do the trick.

**Reply (@v3ritatis)**: I believe SOLO_prediction just tells you which cells in your data were classified as being doublets. I would like to be able to visualize the simulated doublet that get generated in order to determine that the cells in my data are doublets

**Reply (@cane11)**: Hi, model.adata should contain also the synthetic doublets?

## Error when running scvi.data.add_dna_sequence
**Topic:** 3549 | **Last activity:** 2025-03-18T08:08:00Z
**Posts:** 2 | **Views:** 99 | **Created:** 2025-03-15 | **URL:** https://discourse.scverse.org/t/error-when-running-scvi-data-add-dna-sequence/3549

**Question**: Hello, I am getting an error when running simple commands like: import genomepy # Define genome directory genome_dir = "data" # Install mm10 genomepy.install_genome("mm10",provider="ensembl", genomes_dir=genome_dir) Even when doing scvi.data.add_dna_sequence( adata, chr_var_key="chr", start_var_key="start", end_var_key="end", genome_name="hg19", genome_dir="data", ) adata I get an error in them all. File /mnt/RAID5/miniforge/envs/scvi-env/lib/python3.12/site-packages/scvi/utils/_dependencies.py:24, in dependencies.<locals>.decorator.<locals>.wrapper(*args, **kwargs) 21 @wraps(fn) 22 def wrapper(*args, **kwargs): 23 error_on_missing_dependencies(*modules) ---> 24 return fn(*args, **kwargs) File /mnt/RAID5/miniforge/envs/scvi-env/lib/python3.12/site-packages/scvi/data/_preprocessing.py:432, …

**Reply (@ori-kron-wis)**: See discussion in GitHub issue. Unable to run scBasset to integrate scATACseq data · Issue #3253 · scverse/scvi-tools · GitHub

## SysVI model and normalized expression
**Topic:** 3543 | **Last activity:** 2025-03-15T07:32:36Z
**Posts:** 2 | **Views:** 244 | **Created:** 2025-03-14 | **URL:** https://discourse.scverse.org/t/sysvi-model-and-normalized-expression/3543

**Question**: Hello, I was working through this example for running SysVI: Project name not set Integration of scRNA-seq data with substantial batch effects using sysVI This tutorial shows how to integrate scRNA-seq datasets with substantial batch effects (here referred to as systems), such as cross-species, cross-technology (e.g. cells and nuclei), and primary ti... And tried running get_normalized expression. However, I get this error: AttributeError: ‘SysVI’ object has no attribute ‘get_normalized_expression’ However, the API indicates this is an attribute: Project name not set scvi.external.SysVI Attributes table: Methods table: Attributes: Methods: Am I doing something wrong, or do I somehow need to convert this SysVI object to a scvi object? Any help would be greatly appreciated!

**Reply (@cane11)**: See GitHub issue. Please mark if you double post this makes it easier for the community.

## Scvi-tools and xenium
**Topic:** 2450 | **Last activity:** 2025-03-13T17:58:30Z
**Posts:** 8 | **Views:** 1021 | **Created:** 2024-08-15 | **URL:** https://discourse.scverse.org/t/scvi-tools-and-xenium/2450

**Question**: Hi, Can I use scvi-tools to process 10x genomics xenium spatial transcriptome dataset ? The following adata is an anndata object from xenium dataset. # Registering the data scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="library_id") # Creating and training a model model = scvi.model.SCVI(adata, n_hidden=128, n_latent=30, n_layers=2, dispersion='gene') model.train()

**Reply (@cane11)**: Hi, yes it works. However, this data contains less counts per cell than standard single-cell data and is more noisy (e.g. background). We will release hopefully latter this month an adapted model that works with image-based spatial transcriptomics and has an improved framework to model this data. In the meantime, I would recommend looking into ProSeg for segmentation.

**Reply (@wangjiawen2013)**: I have tested scvi with a xenium dataset. when there is only one sample (~250,000 cells, ~100 genes), the umap and leiden clustering looks good. But when I integrated two xenium datasets with scvi, there are a lot of tiny clusters (~40 cells per cluster) except two major clusters ! This has never been occurred when intergrating multiple single cell datasets. So it looks there are many differences between xenium and single cell datasets, the data struct of xenium is not compatible well with scvi.

**Reply (@cane11)**: These isolated islands are a problem with low count data and UMAP not so much with scVI. You can mitigate this by either stricter filtering to filter out low count cells. I assume your second sample has lower quality and if you run it seperately you will see similar behavior. You can also reduce this behavior by increasing n_neighbors before running UMAP. You get pretty similar behavior if you run scVI with very poor quality (low library complexity) single-cell data. The reason is just that in these cases 40 cells can have exactly the same expression values.

**Reply (@wangjiawen2013)**: Thanks, the isolated islands was indeed caused by the low library complexity. In my case, the two datasets were both in good quality. However, the datasets were from different source, the genes became two few when integrating, becuase only the genes expressed in both datasets were kept, a lot of genes were filtered.

**Reply (@reinertanalytics)**: Hi, thanks for a great package and good discussion here. An adapted model for image based spatial transcriptomics would be fantastic! Any ETA on release?

**Reply (@pgd)**: Hi there, Great to hear there is other people trying to use scvi to integrate samples in a Xenium analysis. I am currently trying to make it work on 15 samples as well, but it isn’t going too well… Is there any update on this adapted model that works with image-based spatial transcriptomics? Thanks a lot! Best wishes

**Reply (@cane11)**: It is released and called resolVI. See the scVI-Tools docs. I hope to also release a tutorial for Visium HD soon‘ish with a slightly modified approach by training a model on 2mum data and inference on 8mum data (pretty sure it can be optimized by using cell segmentation).

## Unexpected exception formatting exception when prepare_query_anndata
**Topic:** 3533 | **Last activity:** 2025-03-11T13:45:51Z
**Posts:** 5 | **Views:** 331 | **Created:** 2025-03-10 | **URL:** https://discourse.scverse.org/t/unexpected-exception-formatting-exception-when-prepare-query-anndata/3533

**Question**: Hello, thanks for the tool! I’m trying to do the label transfer from a ref data to my query data. I’m following this turorial: Human Endometrial Cell Atlas (HECA): a step-by-step guide to mapping query endometrial datasets to the reference atlas. Everything goes well, but when I run sca.models.SCANVI.prepare_query_anndata(query_adata, scanvae) , it announced: INFO Found 96.39999999999999% reference vars in query data. Unexpected exception formatting exception. Falling back to standard exception Traceback (most recent call last): File "/dssg/opt/icelake/linux-centos8-icelake/gcc-11.2.0/miniconda3-4.10.3-f5dsmdmzng2ck6a4otduqwosi22kacfl/lib/python3.9/site-packages/IPython/core/interactiveshell.py", line 3398, in run_code exec(code_obj, self.user_global_ns, self.user_ns) File "/tmp/ipykernel_ …

**Reply (@ori-kron-wis)**: Hey @SherylShaw Hard to say what is going on cause there is some preprocess before as the failure begin with this line: SherylShaw: ValueError: Value passed for key 'PCs' is of incorrect shape. Values of varm must match dimensions ('var',) of parent. Value had shape (58903,) while it should have had (38678,). I did notice you are using python3.9, which is not support in recent scvi-tools versions. My suggestion to you is to update to most recent version in a new python 3.12 env and try again. Having less genes in query than reference shouldn’t be the cause of problem as we reorder the genes and pads any missing genes with 0s when running prepare_query_anndata

**Reply (@SherylShaw)**: Thanks! I update my python version and rerun it but it still doesn’t work. For adata, I did the ordinary quality control, doublet detection, normalization, feature selection, dimensionality reduction, and Nearest neighbor graph constuction followed by scanpy tutorial . This is my adata : AnnData object with n_obs × n_vars = 20297 × 38606 obs: 'sample', 'Binary_Stage', 'Age', 'dataset', 'Hormonal_treatment', 'Biopsy_type', 'Tissue_sampled', 'Endometrial_pathology', '10x_kit', 'age_group', 'n_genes_by_counts', 'total_counts', 'pct_counts_mt', 'n_genes', 'doublet_score', 'predicted_doublet' var: 'n_cells_by_counts', 'highly_variable', 'means', 'dispersions', 'dispersions_norm', 'highly_variable_nbatches', 'highly_variable_intersection' uns: 'scrublet', 'log1p', 'hvg', 'pca', 'sample_colors', …

**Reply (@ori-kron-wis)**: Looking at this error: SherylShaw: ValueError: Value passed for key 'PCs' is of incorrect shape. Values of varm must match dimensions ('var',) of parent. Value had shape (58903,) while it should have had (38678,). and adata_out = anndata.concat( 459 [adata, adata_padding], 460 axis=1 what I infer is that the issue is with the adata concat which is a result of the padding we do due to missing genes in referece. But than the problem is that the query data had varm “PCs” that is not like its parent adata “var” gene counts (58903 vs 38678). Do we need to use the PCs here (coming from Nearest neighbor graph)? can you verify that indeed we get : adata.varm.parent.shape==adata.shape I think that the query might have selected different number of PCs and this is why it got so confused. If you dont …

**Reply (@SherylShaw)**: Thanks!!! I calculated PCs when I dealt with the batch effect to compared the effects from different methods. I delete it by del query_adata.varm['PCs'] and the error solved! By the way , I run adata.varm.parent.shape==adata.shape . It returns TRUE. And I checked my anndata version, which is ‘0.11.3’, the recent one. Thank you again for your suggestion and kindness!!

## DestVI: how to load a DestVI model that was saved as a pickle
**Topic:** 3530 | **Last activity:** 2025-03-09T13:44:59Z
**Posts:** 2 | **Views:** 116 | **Created:** 2025-03-07 | **URL:** https://discourse.scverse.org/t/destvi-how-to-load-a-destvi-model-that-was-saved-as-a-pickle/3530

**Question**: Hi scvi team, DestVI model was saved as a pickle as below: DestVI.setup_anndata(st_adata, layer="counts") st_model = DestVI.from_rna_model(st_adata, sc_model) st_model.view_anndata_setup() st_model.train(max_epochs=2500) with open("st_model.pkl", "wb") as f: pickle.dump(st_model, f) And below error occurs Traceback (most recent call last): File "/data/wanglab_mgberis/UT_scRNAseq/./cuda_to_cpu.py", line 39, in <module> st_adata.obsm["proportions"] = st_model.get_proportions() File "/usr/local/lib/python3.10/dist-packages/scvi/model/_destvi.py", line 198, in get_proportions stdl = self._make_data_loader(adata=self.adata, indices=indices, batch_size=batch_size) File "/usr/local/lib/python3.10/dist-packages/scvi/model/base/_base_model.py", line 431, in _make_data_loader raise AssertionError( A …

**Reply (@ori-kron-wis)**: Hey @jliu678 What version of SCVI are you running? If its not the latest please update to the most recent version and try again as we had changes in the exact same spot of your error. You can also save the model with save_anndata=True,overwrite=True and then wont need to load the adata from pickle.

## Parameters in training model for integrating datasets with scVI in R
**Topic:** 3522 | **Last activity:** 2025-03-09T12:36:23Z
**Posts:** 14 | **Views:** 355 | **Created:** 2025-03-01 | **URL:** https://discourse.scverse.org/t/parameters-in-training-model-for-integrating-datasets-with-scvi-in-r/3522

**Question**: Thanks for developing this tool!! I was trying to use scVI to integrate my datasets. Following the instructions ( Integrating datasets with scVI in R — scvi-tools ), I was able to run the script successfully without changing any parameters in the training model. My next step was trying to change some parameters in the training model, but I encountered errors. Could you please help me resolve these issues? Thanks! ============ model ← scvi$model$SCVI(adata_5_in_1, n_latent = 5) Error in py_call_impl(callable, call_args$unnamed, call_args$named) : TypeError: empty() received an invalid combination of arguments - got (tuple, dtype=NoneType, device=NoneType), but expected one of: (tuple of ints size, *, tuple of names names, torch.memory_format memory_format = None, torch.dtype dtype = None, t …

**Reply (@cane11)**: Hi, I assume reticulate has issues interpreting 5. Can you try: n_latent_value <- as.integer(5) model <- scvi$model$SCVI(adata_5_in_1, n_latent = n_latent_value)

**Reply (@joweihsieh)**: Hi, n_latent_value ← as.integer(5) model ← scvi$model$SCVI$create(adata_5_in_1, n_latent = n_latent_value) I tried but still have errors. Error in py_get_attr(x, name) : AttributeError: type object ‘SCVI’ has no attribute ‘create’ Run reticulate::py_last_error() for details. reticulate::py_last_error() ── Python Exception Message ────────────────────────────────────────────────────────────────────────────────────── AttributeError: type object ‘SCVI’ has no attribute ‘create’ ── R Traceback ─────────────────────────────────────────────────────────────────────────────────────────────────── ▆ ├─scvi$model$SCVI$create └─reticulate::: $.python.builtin.object (scvi$model$SCVI, create) └─reticulate:::py_get_attr_or_item(x, name, TRUE) └─reticulate::py_get_attr(x, name) See reticulate::py_last_err …

**Reply (@cane11)**: See edit above. Sorry for the typo.

**Reply (@joweihsieh)**: It works!! Thank you!!

**Reply (@joweihsieh)**: Could you please share some suggestions on which parameters we can adjust to enhance the integration performance? I am planning to try n_hidden, n_layers and n_latent_value. Thanks!!

**Reply (@ori-kron-wis)**: Hi, Practically all model/training parameters are open for tune and can affect the integration performance. Also the selection of batch key is a crucial factor of course. You can use our autotune to try to find an optimal set of parameters, check our documentation in the subject.

**Reply (@joweihsieh)**: Hi, I would like to use GPU to speed up the process. I got some errors…It seems to result from PyTorch and CUDA so I tried to re-install PyTorch. But it still failed… Just wonder if you have any idea? Thanks!!! ======== Sys.setenv(CUDA_VISIBLE_DEVICES = “1”) torch$cuda$is_available() [1] TRUE scvi$model$SCVI$setup_anndata(adata_5_in_1, batch_key = “batch”) model ← scvi$model$SCVI(adata_5_in_1) model$train(accelerator=“gpu”) GPU available: True (cuda), used: True TPU available: False, using: 0 TPU cores HPU available: False, using: 0 HPUs Error in py_call_impl(callable, call_args$unnamed, call_args$named) : torch.cuda.DeferredCudaCallError: CUDA call failed lazily at initialization with error: device >= 0 && device < num_gpus INTERNAL ASSERT FAILED at “…/aten/src/ATen/cuda/CUDAContext.cpp”: …

**Reply (@ori-kron-wis)**: kinda hard for me to understand whats going on. I do see some anndata related messages. My suggestion to you is to: create a new clean environment, install scvi-tools v1.3 on python 3.12 backend & make sure you can run code (any simple code, not scvi) on the GPU, given this torch + cuda settings you have in your R env, then move to try to run a scvi code, and start from a very basic dummy test. does the same code trains on the cpu? so we will know there no data issues

**Reply (@joweihsieh)**: ori-kron-wis: does the same code trains on the cpu? so we will know there no data issues Yes! The data is able to be trained on cpu. scvi$model$SCVI$setup_anndata(adata_5_in_1, batch_key = “batch”) model ← scvi$model$SCVI(adata_5_in_1) model$train()

**Reply (@joweihsieh)**: ori-kron-wis: My suggestion to you is to: create a new clean environment, install scvi-tools v1.3 on python 3.12 backend & make sure you can run code (any simple code, not scvi) on the GPU, given this torch + cuda settings you have in your R env, then move to try to run a scvi code, and start from a very basic dummy test. Thanks for the suggestions!!! It works!!

**Reply (@joweihsieh)**: ori-kron-wis: You can use our autotune to try to find an optimal set of parameters, check our documentation in the subject Hi, I tried running the autotune method you suggested, but I couldn’t get it to work. === Here is my script === Import the necessary Python modules scvi ← import(“scvi”) scvi_data ← import(“scvi.data”) # Import scvi.data for datasets torch ← import(“torch”) anndata ← import(“anndata”) tune ← import(“ray.tune”) ray ← import(“ray”) adata_5_in_1 ← anndata$read_h5ad(“adata_5_in_1.h5ad”) py$adata_5_in_1 ← adata_5_in_1 py_run_string(" from scvi.model import SCVI from ray import tune SCVI.setup_anndata(adata_5_in_1, batch_key=‘batch’) def train_scvi(config): model = SCVI( adata_5_in_1, n_hidden=config[‘n_hidden’], n_layers=config[‘n_layers’], n_latent=config[‘n_latent’], gene …

**Reply (@cane11)**: Hi, could you train directly in Python? This would make the error log much simpler and avoid some errors like wrong type setting that come with reticulate.

**Reply (@ori-kron-wis)**: hey @joweihsieh I agree to try to run this directly on python, especially also because in the R code you run most of it in python code… In any case, using scvi-tools 1.3v, we run the autotune code a bit different now. For example this was working for me in R env (just replace to your adata): library(reticulate) options(reticulate.verbose = TRUE) py_module_available('scvi') scvi <- import('scvi') ray <- import('ray') adata <- scvi$data$synthetic_iid() py$adata <- adata py_run_string(" from scvi.model import SCVI from ray import tune from scvi.data import synthetic_iid from scvi.autotune import run_autotune SCVI.setup_anndata(adata) experiment = run_autotune( SCVI, adata, metrics=['elbo_validation'], mode='min', search_space={ 'model_params': { 'n_hidden': tune.choice([64, 128, 256]), 'n_lay …

## Understanding batch-corrected counts in scVI
**Topic:** 3526 | **Last activity:** 2025-03-09T00:39:13Z
**Posts:** 7 | **Views:** 981 | **Created:** 2025-03-04 | **URL:** https://discourse.scverse.org/t/understanding-batch-corrected-counts-in-scvi/3526

**Question**: Hi, Thank you for such a great tool! I’m analyzing transcriptional heterogeneity in a single cell type associated with a condition of interest. I have multiple scRNA-seq datasets, each containing samples from both conditions, but some datasets are quite small (~300 cells or less). I’m using scVI for dataset integration and generating batch-corrected counts with get_normalized_expression() . When sampling counts, I specify a list of samples from the three largest datasets as the batch (to average across them). My main concerns: Could this procedure introduce artificial signal, particularly affecting the smaller datasets when using larger datasets as the batch? What would be a reasonable correlation between original and batch-corrected counts? Should a certain threshold indicate potential is …

**Reply (@ori-kron-wis)**: Hey @noraneko I refer you to here: Project name not set scvi.model.SCVI Attributes table: Methods table: Attributes: Methods: For additional info on get_normalized_expression And here: Project name not set Joint analysis of paired and unpaired multiomic data with MultiVI MultiVI is used for the joint analysis of scRNA and scATAC-seq datasets that were jointly profiled (multiomic / paired) and single-modality datasets (only scRNA or only scATAC). MultiVI uses the pa... About how to see the quality of it in terms of imputed genes. Besides that, if you want to compare the quality of your batch integration and parhaps bio conservations of the orignal counts and the batch-corrected counts you did in your method, you can use scib-metrics (see Atlas-level integration of lung data — scvi-tools )

**Reply (@noraneko)**: Hi @ori-kron-wis , Thanks for your response! I’ve checked out the documentation, tutorials, and scib-metrics. However, these approaches don’t apply to me. I’m working with a single cell type, so I don’t have distinct clusters that could serve as labels in Benchmarker methods. Additionally, I don’t expect clear spatial separation between my conditions. My goal is to identify subpopulations of cells within this cell type and compare them between conditions, so I would like to ensure that my batch correction hasn’t artificially imposed structure. Do you have any suggestions for evaluating batch effects or unintended signal introduction in this context? Thank you!

**Reply (@cane11)**: I would apply a DE method orthogonal to scVI-Tools and compare your identified cell populations. In the end, it will come down to either prior knowledge or validation experiments. To check whether the trained model makes sense, you can also use scVI criticism that tests whether generated and raw data are similar.

**Reply (@noraneko)**: @cane11 , thanks! Could you clarify what you mean by ‘cell populations’ - are you referring to e.g. Leiden clusters derived from scVI’s latent variables, or the clusters I identified independently using a different algorithm on scVI-corrected counts? scVI-criticism sounds really cool - I hadn’t come across it before. Do you know if it can be applied to batch-corrected counts sampled with get_normalized_expression() ? I’ve started developing similar metrics to compare raw and corrected counts, but using PPC from the package would be a more robust approach.

**Reply (@cane11)**: Yes your Leiden clusters are what I referred to as “cell populations”. No, it can’t be applied to batch-corrected counts directly as it requires corresponding raw data. However, if the generated data without projection is bad, it is likely the same for the batch projected ones (doesn’t approximate real data well) and I wouldn’t trust it.

**Reply (@noraneko)**: @cane11 , thanks again for your suggestions! I’m still exploring the criticism module; the tutorial seems a bit outdated, and I’m not sure which metrics are the most informative for my case. Proper DE analysis (e.g., pseudobulked DESeq2) isn’t feasible for the small clusters, but comparing top markers per cluster per dataset before and after correction looks good. As I would expect, larger datasets show higher agreement, likely due to lower noise. I realized that my original concern about the validity of analysis involving batch-corrected counts can be also asked in the context of DE analysis performed by scVI. From other forum discussions (e.g., here ), I learned that batch-corrected counts can be used for DE. Additionally, from this documentation , I saw that in Scenario 2, we can specif …

## Add new data to existing integration
**Topic:** 3495 | **Last activity:** 2025-03-07T08:04:27Z
**Posts:** 4 | **Views:** 253 | **Created:** 2025-02-19 | **URL:** https://discourse.scverse.org/t/add-new-data-to-existing-integration/3495

**Question**: Hi all, I have a large integrated adata (~4M cells) through SCVI (with 2K HVG) and now I am going to add a small new single-cell data (28K cells) into the large integration. Is there a quick way to “project” the large integration to the smaller new data? Or do I have to start from the beginning, concatenate original full set and then select HVG and retraining for SCVI and SCANVI label transferring?

**Reply (@ori-kron-wis)**: I think you are looking for scarches, where the ref data is your large integrated model and the query data is that small new single cell. please follow this tutorial: Project name not set Reference mapping with scvi-tools This tutorial covers the usage of the scArches method with SCVI, SCANVI, and TOTALVI. This particular workflow is useful in the case where a model is trained on some data (called reference here) an...

**Reply (@tangxj)**: I tried the scArches for scVI and it worked fine. However, I got errors when I used scArches for scANVI, it did not work. could you please see where might be wrong? code: # scANVI arches # start from scvi model as trained for scArches above. scvi_model=scvi.model.SCVI.load("scvi-model_nb_scArches", adata_ref) SCANVI_LABELS_KEY = "C_scANVI" adata_ref.obs[SCANVI_LABELS_KEY] = adata_ref.obs["celltype_manual"].values scanvi_model=scvi.model.SCANVI.from_scvi_model(scvi_model,unlabeled_category="Unknown",labels_key=SCANVI_LABELS_KEY) scvi.settings.seed = 0 torch.set_float32_matmul_precision("high") scanvi_model.train(max_epochs=20, n_samples_per_label=100) scvi.model.SCANVI.prepare_query_anndata(adata_query, scanvi_model) #INFO Found 100.0% reference vars in query data. scanvi_query = scvi.model …

**Reply (@cane11)**: Hi, please set nans in your cell-type obs columm to the unlabeled category of your model or remove the column. Currently you are passing in a cell-type named „NaN“, which is not intended.

## Issue with retrain scANVI model
**Topic:** 3523 | **Last activity:** 2025-03-03T09:06:43Z
**Posts:** 2 | **Views:** 162 | **Created:** 2025-03-03 | **URL:** https://discourse.scverse.org/t/issue-with-retrain-scanvi-model/3523

**Question**: Hi, all After reanno all cells, I reloaded scVI model (setting labels_key=‘anno’) and set cell_type_key = 'FinalLv1' . Then setting scanvi_model = sca.models.SCANVI.from_scvi_model( vae_model, adata=source_adata, labels_key=cell_type_key, unlabeled_category="Unknown", ) to train a new scANVI model to predict other data. But, when predicting query adata, model.predict() returned labels were anno category. Is it possible to retrain a scANVI model? Is there anything wrong with the scVI model?

**Reply (@ori-kron-wis)**: Hey, I think you shouldn’t use the labels_key in the scVI model. Please also validate your query data with prepare_query_anndata before applying the trained scANVI from the scVI. See this tutorial that might help: Reference mapping with scvi-tools — scvi-tools

## Issue with scVI model device
**Topic:** 3520 | **Last activity:** 2025-03-03T05:18:05Z
**Posts:** 3 | **Views:** 126 | **Created:** 2025-02-28 | **URL:** https://discourse.scverse.org/t/issue-with-scvi-model-device/3520

**Question**: Hi, all When training scVI models, I wanted to change the device used. So, I set vae.to_device(‘cuda:1’) to use another gpu. However, it didn’t work as the warning info showed LOCALRNAK:0. How could I use other divices for training?

**Reply (@ori-kron-wis)**: Hi, In the train function, you can specify the device id you wish to train the model on. For example: model.train( max_epochs=100, train_size=0.5, check_val_every_n_epoch=1, accelerator="gpu", devices=[1], #strategy="ddp_find_unused_parameters_true", #for multiGPU ) Will run it on gpu #1 . Regardless, in scvi-tools v1.3.0 we now have the option to train models in multiGPU (just use the strategy parameter like in the comment above, but then remove the devices), if that is relevant for you ,give it a try!

**Reply (@Xicici-Yan)**: Thanks, it does work!

## In which direction is the LCF calculated when using the function differential_expression?
**Topic:** 3514 | **Last activity:** 2025-03-02T14:52:14Z
**Posts:** 2 | **Views:** 105 | **Created:** 2025-02-26 | **URL:** https://discourse.scverse.org/t/in-which-direction-is-the-lcf-calculated-when-using-the-function-differential-expression/3514

**Question**: I am sorry if this sounds like a stupid question, but I looked around and I could not find a proper answer. Given idx1, idx2 as parameters to my my model.differential_expression , if I find that for a given gene the LFC is positive, does it mean that it is over expressed in idx1 or idx2 ? In this tutorial it is stated that Positive values of the LFC signify that the gene is upregulated in idx1 . However, looking in the documentation it is reported that the LFC is equal to log(B) - log(A) with idx1 indicated as A and idx2 indicated as B. Following, I attach the corresponding pictures for clarity: Screenshot From 2025-02-26 20-04-23 640×114 10.4 KB Screenshot From 2025-02-26 20-04-49 651×241 18.8 KB So, which one is correct? Looking at my data, it seems to that the second option (B over A, i …

**Reply (@ori-kron-wis)**: Hey, The scvi-tools code base is calculating idx1 over idx2, see: model.base._differential.py I agree the doc needs to be other way around. However LFC is a symmetrical metric, so it doesn’t really matter how you use that as long as you keep it consist. Usually one set the idx1 group as the one represent the phenomena class (like cases, or effect) and the idx2 group represent the controls/no-effect.

## GIMVI genes imputation
**Topic:** 3507 | **Last activity:** 2025-02-26T09:47:51Z
**Posts:** 2 | **Views:** 231 | **Created:** 2025-02-25 | **URL:** https://discourse.scverse.org/t/gimvi-genes-imputation/3507

**Question**: Hello ! I have a very basic question on GIMVI model. This model is designed to “input missing genes on spatial data”, based on a single-cell reference. However, the tutorial resitricts the single-cell reference to genes present in the spatialdata: seq_data = seq_data[:, spatial_data.var_names].copy() Thus, the predicted genes are only genes already present in the spatialdata, which does not make sense. Did I miss some point on GIMVI model ? Thank you very much, Alexis

**Reply (@ori-kron-wis)**: Hi, This line in the tutorial is not mandatory at all. You can still impute other genes. However, for the sake of the tutorial there is no real reason to impute another 2000 gene which cant be compared to ground truth. But you can definitely do it in your own analysis.

## Function in scanvi that can help compute the probability of having a latent cell state given a cell type
**Topic:** 3511 | **Last activity:** 2025-02-26T08:46:02Z
**Posts:** 2 | **Views:** 124 | **Created:** 2025-02-26 | **URL:** https://discourse.scverse.org/t/function-in-scanvi-that-can-help-compute-the-probability-of-having-a-latent-cell-state-given-a-cell-type/3511

**Question**: Hi, I would like to compute p(z|c) from a trained scanvi model where z represents a latent state and c represents a cell-type. I know in the scanvi framework there is a learnable probability p(z|c,u) where u is just a latent cell-type specific state sampled from N(0,1), so I think based on that, computing p(z|c) is possible. Could you tell me which function I need to call to compute p(z|c,u) in scanvi? Thanks!

**Reply (@ori-kron-wis)**: I think you are looking for something like: model.get_latent_representation(return_dist=True,indices=cell_type_indices) it will return a tuple of mean and variance of z, for the specific cell_type_indices you will insert (e.g np.where(adata.obs.labels==“label_1”) will give the indices for label_1 cell type class in the adata)

## Set of guidelines for SCVI and VisiumHD data
**Topic:** 3508 | **Last activity:** 2025-02-25T15:28:54Z
**Posts:** 1 | **Views:** 232 | **Created:** 2025-02-25 | **URL:** https://discourse.scverse.org/t/set-of-guidelines-for-scvi-and-visiumhd-data/3508

**Question**: Hello everyone, I am using a lot the high quality models provided in the scvi ecosystem. I am using scvi models for various tasks: deconvolution, integration, dimensionality reduction … However, I am not sure to what extent these models can be used on VisiumHD data, since VisiumHD is very different from Visium V2: high number of observations (~700 000 for 8um bins), and low number of counts per bin (~50-100 for 8um bins). I am not an expert, but this might impact both the statistical models of variational autoencoding bayes models, and the way to train/retrain the model. So, if someone has already thought about how to adapt models designed for Visium data to VisiumHD data, do you have a set of recommandations regarding statistical modelling/model training that you could share ? Thank you v …

## Differential Expression and Batch Correction
**Topic:** 3492 | **Last activity:** 2025-02-20T15:17:05Z
**Posts:** 2 | **Views:** 408 | **Created:** 2025-02-17 | **URL:** https://discourse.scverse.org/t/differential-expression-and-batch-correction/3492

**Question**: Hello, thank you for this excellent tool! I’ve reviewed the online documentation and many posts (e.g. 57 ) on this forum regarding batch correction and the .differential_expression() method, but I’m still confused about its application to our analysis. We are running a typical scRNA-seq atlas analysis made up of multiple batches of samples from multiple patients that share a rare disease. Some of these batches are replicates from different patients for technical reasons, but do not have any relevant biological differences. For example, Batch1: patient1, patient2, patient3 (hashed) Batch2: patient 3 Batch3: patient 4 Batch4: patient 5 Batch5: patient 5 We preprocess and then integrate with scVI, providing batch and patient as two categorical_covariate_keys in the model. We then perform leid …

**Reply (@cane11)**: Hi, in the initial model I recommend setting batch_id to the individual samples (setting it to something else leads to less integration due to e.g. sex, but also ambient counts etc). Whether you want to include batch correction in DE depends on the case: While for DE between cell-types or clusters (your analysis here) it can make sense, it’s not good to study between group (like healthy and diseased) genes. If you correct for batch, cells are projected to each batch and differential expression for these projected cells is computed. I would recommend to disable correcting for batch and only enable it if you find expected between group genes significantly DE (happens e.g. if group A contains 95% cells from female donor and group B 95% cells from male donors that X chromosome genes are marker …

## SOLO/scVI .train() error related to batch_size?
**Topic:** 1591 | **Last activity:** 2025-02-20T13:26:12Z
**Posts:** 7 | **Views:** 1541 | **Created:** 2023-07-07 | **URL:** https://discourse.scverse.org/t/solo-scvi-train-error-related-to-batch-size/1591

**Question**: I am getting this error when i run vae.train() ultimately for SOLO “ValueError: Expected more than 1 value per channel when training, got input size torch.Size([1, 128])” I found a few posts on github, but i’m too daft to understand how to apply this to my code github.com/scverse/scvi-tools training fails for certain dataset size opened 09:46PM - 18 Jul 19 UTC closed 06:57PM - 22 Jul 19 UTC coh-racng Issue similar to #221 My dataset has 57345 cells and it so happens that 57345% … 128 == 1. so I end up with a batch that has size 1 during training, raising an error ```python Traceback (most recent call last): File "../code/CAR_T.py", line 37, in <module> correct.run_scvi() File "/net/isi-dcnl/ifs/user_data/vjonsson/racng/singlecell/code/scvi_analysis/batch_correct.py", line 80, in run_scvi s …

**Reply (@martinkim0)**: Ah yes, my guess is that this is occurring because the size of your dataset modulo the default batch size (128) is 1, so the last minibatch during an epoch only has one cell. Thus, the batch norm layer is complaining since it can’t compute normalization statistics on just one observation. The simplest fix for this would be to be pass in some batch size other than 128 to train . Hope this helps!

**Reply (@bennjmo)**: That worked, thanks!!

**Reply (@schroeme)**: Hi! I’m getting this error (exact message below) even when n_cells%128 is not 1. ValueError Traceback (most recent call last) Cell In[28], line 7 5 print((adata_subset[adata_subset.obs['10x_batch']==batch].n_obs)%128) 6 solobatch = scvi.external.SOLO.from_scvi_model(model, restrict_to_batch = batch) ----> 7 scvi.external.SOLO.train(solobatch, early_stopping = False,batch_size=256)#note changed from 128 to 64 8 predictions = scvi.external.SOLO.predict(solobatch, soft = False) 9 predictions_all.append(predictions) File ~/anaconda3/envs/scvi-scanpy/lib/python3.9/site-packages/scvi/external/solo/_model.py:385, in SOLO.train(self, max_epochs, lr, accelerator, devices, train_size, validation_size, shuffle_set_split, batch_size, datasplitter_kwargs, plan_kwargs, early_stopping, early_stopping_pat …

**Reply (@Florian_Deckert)**: I have the same problem with scvi 1.1.6.post2 when scvi.model.SCVI(bdata). Would it be possible to drop the 1 cell instead of changing batch_size?

**Reply (@ori-kron-wis)**: @Florian_Deckert please update to most recent scvi-tools. This problem was addressed in scvi-tools >1.2. You will have adaptive handling for last training minibatch of 1-2 cells, and it will not fail.

**Reply (@Florian_Deckert)**: @ori-kron-wis Thank you very much. I updated to 1.2 and it resolved the issue.

## Question about interpreting the DEGs associated with disease changes using MrVI
**Topic:** 3480 | **Last activity:** 2025-02-11T07:46:11Z
**Posts:** 3 | **Views:** 196 | **Created:** 2025-02-11 | **URL:** https://discourse.scverse.org/t/question-about-interpreting-the-degs-associated-with-disease-changes-using-mrvi/3480

**Question**: Dear the developers of MrVI, Thank you very much for developing this amazing tool. I am confused on the output from DE analysis, and how DEGs are defined. From the manuscript, the DEG was selected based on both p-value<0.05 and absolute log fold change>0.5 or 1. I understand that the model estimates each gene’s log fold change in each cell, but I did not understand why each cell only has 1 p-value for each covariate. (i.e. why there is no p-value for each gene in each cell) Are you keeping the cells whose adjusted p-values with respect to the covariate of interest are <0.05, and selecting the genes among these cells with absolute log fold change >0.5 as DEGs of that trait? Thank you very much for your explanation. Screenshot 2025-02-10 at 11.20.08 PM 1394×984 63.8 KB

**Reply (@cane11)**: Hi, pvalue and padj are p-values of the covariate specific effect sizes in z-space using a Chi2 statistic. pde is similar to a p-value on the gene-by-cell level (how many random samples generated an LFC above 0.5). It is not uniform under the null hypothesis of no differential expression and is therefore not a p-value but highlights the significance of a result. See lvm-DE for a deeper discussion of this aspect: https://www.pnas.org/doi/10.1073/pnas.2209124120 .

**Reply (@zitiansunsh1ne)**: cane11: re p-values of the covariate specific effect sizes in z-space using a Chi2 statistic. pde is similar to a p-value on the gene-by-cell level (how many random samples generated an LFC above 0.5). It is not uniform under the null hypothesis of no differential expression and is therefore not a p-value but highlights the significance of a result. See lvm-DE for a deeper discussion of this aspect: https://www.pnas.org/doi/10.1073/pnas.2209124120 . Thank you very much for your response. I am still confused about this. In the manuscript of MrVI, when the DEG is defined as “p-value<0.05 and absolute logFC>1”, is the p-value referring to the pde? Then with the pde, how does MrVI select the optimal pde threshold to control FDR<0.05 and output significant DEGs, which lvm-DE takes care of? Shal …

## TotalVI not fully integrating CITEseq cells with GEX and missing protein values
**Topic:** 3473 | **Last activity:** 2025-02-06T16:38:49Z
**Posts:** 2 | **Views:** 145 | **Created:** 2025-02-06 | **URL:** https://discourse.scverse.org/t/totalvi-not-fully-integrating-citeseq-cells-with-gex-and-missing-protein-values/3473

**Question**: Hi Team, Apologies if I’m doing something wrong here! I have a CITEseq dataset in which some cells have good quality RNAseq values but poor quality ADT, so these ADT values have been removed. I tried using TotalVI to integrate (with batch effects independent of the missing ADT values) which worked brilliantly in every regard except that the cells with missing ADT values were clustered separately from the other cells with ADT present. The tutorial shows successful integration of missing ADT data cells, however in this example all cells with missing ADT are part of one batch. I tested the tutorial again but removing ADT values from the same number of random cells: #Remove ADT from random cells random_indices = np.random.permutation(adata.shape[0]) random_indices = random_indices[range(0,adat …

**Reply (@cane11)**: Hi, indeed cells without ADT need to be their own batch. We apply an adversarial classifier on the batch ID to integrate those. This doesn’t work when using the same batch ID for cells with and without protein data. In an open PR, we have the option to add an adversarial key (but the assumption is still that one batch only contains one assay).

## Differential gene expression shows very low raw_means
**Topic:** 3465 | **Last activity:** 2025-01-30T15:24:43Z
**Posts:** 3 | **Views:** 142 | **Created:** 2025-01-29 | **URL:** https://discourse.scverse.org/t/differential-gene-expression-shows-very-low-raw-means/3465

**Question**: Dear all, I used the differential gene expression function, however I only get a very little amount of DEGs and they have a very low raw_mean1 and 2. If I use MAST for example I get much more DEGs de_results_HFD_L1 = model_scvi.differential_expression( subset, groupby=“Sample”, group1=“A”, group2=“B”, mode=“change”, filter_outlier_cells=True, batch_correction=False, delta=0.15, fdr_target=0.05, all_stats=True, )

**Reply (@cane11)**: Hi, most benchmarks show that MAST inflates the number of detected genes. However, we changed our default DE function in our current main branch to filter more of these lowly expressed genes. We will release it with scVI-tools 1.3. Pseudobulk methods (especially DESeq2) are current top-performers in DE benchmarks and I would consider using those. ScVI-tools DE serves its purposes if the data is not very trustworthy (large sample variation or very small dataset), see our scVI-hub preprint for a case of this.

**Reply (@SimonE1220)**: Thank you very much. Would it help to filter the sc data in a certain way bevor training the model for DEG analysis.

## The mean of the the scVI ZINB model distribution (related to supplementary note 3)
**Topic:** 3459 | **Last activity:** 2025-01-29T17:00:29Z
**Posts:** 5 | **Views:** 223 | **Created:** 2025-01-26 | **URL:** https://discourse.scverse.org/t/the-mean-of-the-the-scvi-zinb-model-distribution-related-to-supplementary-note-3/3459

**Question**: Thanks for the great tool. I had a subtle question about the the scVI model. In supplementary note 3 the mean of the ZINB (ignoring the zero inflated portion) comes to r * \lambda * \frac{p}{p+1} . Given that the (r, \lambda, \frac{p}{p+1}) = (\rho^g_n, l_n, \theta) doesn’t this imply the mean of the ZINB is \rho^g_n * l_n * \theta ? This is different form the method section of the main text (Fast inference via stochastic optimization) that states the mean is l_n * \rho^g_n, (no \theta ). Screenshot 2025-01-26 at 7.04.53 pm 655×161 26.9 KB

**Reply (@ori-kron-wis)**: Hey, I believe l_n is the scaling factor, just like p/(1-p) is the scale parameter in the supplementary and λ is just a general scalar there. θ is the dispersion parameter and its a kinda another way to represent the ZINB. So, just remove λ and θ from that equation you made. rest of things are fine

**Reply (@Sandeep-S-K)**: Hi, thanks for the response! Sorry for the typo in my post, it should be \frac{p}{1-p} instead of \frac{p}{p+1} . I see that l_n and \frac{p}{1-p} are scaling factors and the gamma distribution has a scaling property (if X \sim \mathrm{Gamma}(\alpha, \theta) , for c> 0 then cX \sim \mathrm{Gamma}(\alpha, c\,\theta) ), so they are interchangeable. But if the the model is described as such image 696×634 22 KB then ist it implied that the mean will be \theta*l_n*\rho_n^g and not just l_n * \rho_n^g ? irrespective of how the ZINB is parameterised.

**Reply (@ori-kron-wis)**: Its a bit confusing indeed. It depended on what is θ, if its the dispersion parameter than it is not part of the mean calculation showed, if it is a scalar like you are showing, then yes it should be part of the mean calculation of the Gamma distribution. However I think the author wanted to give a sense that the distribution has a close form based on the reference he gave in the “Fast inference via stochastic optimization” part and perhaps that doesn’t 100% match the previous paragraphs.

**Reply (@cane11)**: To bring more explanation in the supplement the definition is the logits total_counts convention for a negative binomial (r, p and lambda instead of rho, theta and l_n). See our code on how this changes computation: scvi-tools/src/scvi/distributions/_negative_binomial.py at main · scverse/scvi-tools · GitHub . To make it very short, theta is the mean variance relationship and the mean is independent of theta.

## Tensor nan error when training scANVI model
**Topic:** 1677 | **Last activity:** 2025-01-29T16:20:53Z
**Posts:** 7 | **Views:** 986 | **Created:** 2023-08-11 | **URL:** https://discourse.scverse.org/t/tensor-nan-error-when-training-scanvi-model/1677

**Question**: Hi, I ran into tensor nan error when using scANVI set up with scVI model, hope someone can help me~ setup anndata with scvi.model.SCVI.setup_anndata(combined_adata, layer = "counts", categorical_covariate_keys=["Batch"], continuous_covariate_keys=['pct_counts_mt', 'total_counts']) hyperparameter tuning: search_space = { "n_hidden": tune.choice([128, 256, 512, 1024]), "n_layers": tune.choice([1, 2, 3, 4, 5]), "lr": tune.loguniform(1e-4, 1e-2), "n_latent":tune.choice([10, 15, 20, 30, 50]), "gene_likelihood": tune.choice(["nb", "zinb"]), } # ray.init(log_to_driver=False) results = scvi_tuner.fit( combined_adata, metric="validation_loss", search_space=search_space, num_samples=60, max_epochs=35, resources={"cpu": 40, "gpu": 2,"memory":4e11 }, ) tensor nan error occur for the first time here wh …

**Reply (@tangxj)**: Hi, I have the same error. After training the scvi model with best param tuning, initialize a scANVI model with it. And after 14 epochs I got the same tensor nan error. Are you able to find a solution finally?

**Reply (@cane11)**: Hi, it’s a long time after the first post. However, we have a FAQ in the meantime for NaN errors: https://docs.scvi-tools.org/en/1.2.0/faq.html/ Specifically, for scANVI. Check once that your data has no very low count cells (in standard 10X below 200 counts after hvg filtering) and that you use count data as input. If the issues persists, you can set var_activation=torch.nn.softplus to increase stability during model training.

**Reply (@tangxj)**: Thanks. I indeed found the discussion in scvi github. and did use var_activation=torch.nn.softplus as well as a very small learning rate. The problem is that I could not train for too many epochs and had to do an early stop otherwise the training and validation loss went up. I had to stop at around 86 epochs.

**Reply (@tangxj)**: also, how do I make sure I used count data as input? the counts data is in the adata.layer[‘counts’] My code is: scanvi_model = scvi.model.SCANVI.from_scvi_model( scvi_model, adata=adata, unlabeled_category=“unknown”, labels_key=SCANVI_CELLTYPE_KEY, linear_classifier=True, var_activation=torch.nn.functional.softplus, )

**Reply (@cmb22)**: @cane11 By chance does this FAQ still exist? The link provided gives a 404 error and I’m running into similar NaN errors for both scANVI and totalANVI models. I was hoping to consult it before posting any questions that could be redundant. Thanks, Chris

**Reply (@cane11)**: Frequently asked questions — scvi-tools We are working on a more graceful shutdown when NaN are encountered. The layer argument, you have to define this in the corresponding scVI model in setup-anndata. All models/datasets afterwards have to be consistent.

## How to appropriately transfer annotations from anndata to seurat
**Topic:** 3457 | **Last activity:** 2025-01-24T23:44:41Z
**Posts:** 3 | **Views:** 506 | **Created:** 2025-01-24 | **URL:** https://discourse.scverse.org/t/how-to-appropriately-transfer-annotations-from-anndata-to-seurat/3457

**Question**: Hi, I processed my rna seq data and annotated them using scvi, and I would like to integrate the data using R. Specifically, this is my anndata structure: AnnData object with n_obs × n_vars = 16712 × 10494 obs: 'sex', 'region', 'subcluster', 'cluster', 'nCount_RNA', 'nFeature_RNA', 'leiden', 'dataset', 'orig_ident', 'broad_names', 'simple_name', 'integrated_snn_res_1', 'integrated_snn_res_0_8', 'integrated_snn_res_1_2', 'broad_names2', '_scvi_batch', '_scvi_labels', 'cell type' var: 'ensembl_common_ID' obsm: 'X_pca', 'X_umap' layers: 'counts' Which contains the two datasets I want to integrate (annotated under the obs ‘dataset’). So I am importing this anndata in R using the following: library(Seurat) library(SeuratData) library(SeuratDisk) library(rhdf5) # Load my data ------------------- …

**Reply (@cane11)**: Hi, I would highly recommend against doing it manually. You can check out sceasy and zellkonverter for this purpose. As a sanity check though, I would recommend first doing a UMAP plot in Python using scanpy.

**Reply (@Slack90)**: Hi @cane11 Thank you so much, that worked perfectly!

## Best practice for handling custom points during SCVI training
**Topic:** 3418 | **Last activity:** 2025-01-24T10:37:57Z
**Posts:** 5 | **Views:** 171 | **Created:** 2025-01-13 | **URL:** https://discourse.scverse.org/t/best-practice-for-handling-custom-points-during-scvi-training/3418

**Question**: Hi everyone, I’m working on a custom implementation with scvi-tools and have a design question regarding the best way to handle specific points selected during training. In my setup, at the end of each epoch, I select a subset of points that will be used for loss calculation in the subsequent epoch (using the loss method of the VAE module). The selection of these points is implemented through a custom TrainingPlan . I’m considering three possible approaches to manage these points throughout the training process: Add them as attributes of the VAE module. For instance, during the initialization of the SCVI model, this would look like: self.module.new_points = new_pts . Store them in adata using something like: adata.uns['_scvi_new_points'] . Add a field to the adata_manager via: adata_manage …

**Reply (@cane11)**: Hi, you would want to use a custom lightning callback for this (I understand correctly that after each epoch you select a new set of cells for the subsequent epoch). This lightning callback has to create a new datasplit and dataloader using custom indices (passed to datasplitter). I would recommend using Callback — PyTorch Lightning 2.5.0.post0 documentation on_epoch_start which sounds like the correct handle here.

**Reply (@alessimichele)**: Hi Can, Thank you for your response and suggestion! Let me clarify my use case a bit further: The selected points are not directly used for training, so they don’t need to be included in the training data loader. Instead, these points are specifically used to calculate some parameters at the beginning of each epoch, which are then utilized in the loss calculation throughout the current epoch. Therefore, I need access to these points at the start of every epoch to compute the necessary parameters. At the end of each epoch, these points are updated. They are generated using the decoder and exist in the data space (with a shape of (K, n_cells) ), but there’s no guarantee that they correspond to actual points in the training set. Given this setup, do you think the custom Lightning callback is …

**Reply (@cane11)**: Yes, everything you want to do at the beginning of each epoch (or step) should be handled by a Callback (and by lightning in general). It creates the smallest overhand and you don’t want to modify the module or the data during training. Another option would be to generate them during each step and define it in the decoder call. If you define them per epoch, just pass them to the loss function (you can check our current kl_weight schedule on how to implement the Callback).

**Reply (@alessimichele)**: Hi Can, after a few days of coding, everything is now working, thanks to your suggestions. Thank you very much! Michele

## Workflow to integrate dataset from two different species
**Topic:** 3432 | **Last activity:** 2025-01-21T11:18:40Z
**Posts:** 2 | **Views:** 228 | **Created:** 2025-01-17 | **URL:** https://discourse.scverse.org/t/workflow-to-integrate-dataset-from-two-different-species/3432

**Question**: Hi, I’d like to use scvi to integrate data from the same brain region in two different species. By using clustering and manual annotation I could identify that both datasets contain the same clusters (each cluster corresponding to a cell type). Now I would like to use scvi to integrate both dataset. So first I find the orthologue genes to both datasets, and then I subsample only the genes are orthologue between the two species. Then I do some filtering and normalization as follows: adata = filtered_anndata adata.var_names_make_unique() sc.pp.filter_cells(adata, min_genes=2) #get rid of cells with fewer than 200 genes sc.pp.filter_genes(adata, min_cells=1) #get rid of genes that are found in fewer than 3 cells adata.var['mt'] = adata.var_names.str.startswith('mt-') # annotate the group of m …

**Reply (@ori-kron-wis)**: Hi, I dont see the full pipeline of your analysis here, From what I see you should do the preprocessing above without scaling the data after datasets were concatenated with the same genes See our documentation for similar tutorials

## Scvi embedding from Census API by CellxGene
**Topic:** 3437 | **Last activity:** 2025-01-20T18:02:48Z
**Posts:** 2 | **Views:** 141 | **Created:** 2025-01-20 | **URL:** https://discourse.scverse.org/t/scvi-embedding-from-census-api-by-cellxgene/3437

**Question**: Hi there, I’m quite new to scvi. So please excuse if there is some notion mistake. What I try to achieve is accessing the full dataset’s scvi embeddings from the model page of Census by CellxGene platform(s3://cellxgene-contrib-public/models/scvi/2024-07-01/mus_musculus/model.pt) Then, using this pretrained embeddings (if possible) to predict the cell types of my query dataset. The given example on the Census is for small slice of the anndata object from Census. For the full model of the ‘model.pt’ file I could not find a working approach to predict the cell types of my query anndata object (actually, converted Seurat object).

**Reply (@cane11)**: Hi, please direct user questions of the CELLxGENE page to the CELLxGENE team. While we help with model training and review their pipeline, it is different to ours at Querying the Human Lung Cell Atlas — scvi-tools (smaller dataset but I would run similar a KNN on the whole data as was done in: https://www.biorxiv.org/content/10.1101/2024.03.01.582887v1 (see reproducibility for running kNN on GPU.

## How to convert R matrix to anndata
**Topic:** 3427 | **Last activity:** 2025-01-17T20:27:46Z
**Posts:** 5 | **Views:** 264 | **Created:** 2025-01-15 | **URL:** https://discourse.scverse.org/t/how-to-convert-r-matrix-to-anndata/3427

**Question**: Hi, I want to processed the raw RNAseq data deposited here in as “GSE165371_cb_adult_mouse.tar.gz” GEO Accession viewer Here a screenshot of the folder content: image 523×195 6.33 KB As tiy can see it contains two text files and a .matrix file. I want to use python for further processing, so I need to convert their raw data from .matrix to anndata object. Does anyone know how to do it? I previously converted a Seurat object into AnnData, but I am not sure what to do when starting from a .matrix

**Reply (@gtca)**: Hey @Slack90 , I think scanpy.read_10x_mtx() is what you’re looking for — it will load gene / cell IDs as well when all three files are in one folder.

**Reply (@Slack90)**: Thanks for the reply Yes that seems pretty much what I was looking for, however when I tested it, I got into some issue, I tried to rename the files, so they contain the suffix _matrix: adata = sc.read_10x_mtx('/home/GSE165371_cb_adult_mouse/', prefix = 'cb_adult_mouse_', cache_compression= 'gzip') But I get the error: --------------------------------------------------------------------------- FileNotFoundError Traceback (most recent call last) Cell In[6], line 1 ----> 1 adata = sc.read_10x_mtx('/home/slacava3/data_jkebsch1/salvo/Xenopus_levis/code/GSE165371_cb_adult_mouse/', prefix = 'cb_adult_mouse_', cache_compression= 'gzip') File ~/.conda/envs/MyEnv/lib/python3.11/site-packages/legacy_api_wrap/__init__.py:82, in legacy_api.<locals>.wrapper.<locals>.fn_compatible(*args_all, **kw) 79 @w …

**Reply (@Slack90)**: I also tried to convert the .txt files to .tsv.gz, and then rerun sc.read_10_mtx, but I get the following error: --------------------------------------------------------------------------- KeyError Traceback (most recent call last) File ~/.conda/envs/MyEnv/lib/python3.11/site-packages/pandas/core/indexes/base.py:3805, in Index.get_loc(self, key) 3804 try: -> 3805 return self._engine.get_loc(casted_key) 3806 except KeyError as err: File index.pyx:167, in pandas._libs.index.IndexEngine.get_loc() File index.pyx:196, in pandas._libs.index.IndexEngine.get_loc() File pandas/_libs/hashtable_class_helper.pxi:2606, in pandas._libs.hashtable.Int64HashTable.get_item() File pandas/_libs/hashtable_class_helper.pxi:2630, in pandas._libs.hashtable.Int64HashTable.get_item() KeyError: 1 The above exception …

**Reply (@gtca)**: Hey @Slack90 , where it should be .csv The default format for the cell barcode and feature information files is .tsv.gz as specified in the CellRanger documentation . You can always read the .mtx file and metadata independently to construct an AnnData object with AnnData(X=X, obs=cell_barcodes, var=features) : from scipy.io import mmread import pandas as pd X = mmread("cb_adult_mouse.mtx") cell_barcodes = pd.read_csv("cb_adult_mouse_barcodes.tsv.gz", compression="gzip", sep="\t") features = pd.read_csv("cb_adult_mouse_genes.tsv.gz", compression="gzip", sep="\t")

## Model cannot be initialized and return error
**Topic:** 3413 | **Last activity:** 2025-01-15T23:46:22Z
**Posts:** 7 | **Views:** 197 | **Created:** 2025-01-11 | **URL:** https://discourse.scverse.org/t/model-cannot-be-initialized-and-return-error/3413

**Question**: Hello, I am running scvi 1.2.1 on jupyter notebook and I want to integrate two datasets using scvi. I checked and the count RNA does not contain NaN values, however when I run “model.train()”, I get the error below. Similar to what was reported here https://github.com/DendrouLab/panpipes/issues/306 . However I am using the latest version of scvi. This is my code prior to the starting the model concatenated_anndata.obs.groupby('dataset').count() sc.pp.filter_genes(concatenated_anndata, min_counts=3) concatenated_anndata.layers["counts"] = concatenated_anndata.X.copy() # preserve counts sc.pp.normalize_total(concatenated_anndata, target_sum=1e4) sc.pp.log1p(concatenated_anndata) concatenated_anndata.raw = concatenated_anndata # freeze the state in `.raw` sc.pp.highly_variable_genes( concaten …

**Reply (@cane11)**: Hi, your min_genes filter is very low with 3. afterwards you perform hvg filtering to few genes. Can you please check the count distribution after this step. Especially, whether you end up with any cells with zero counts. These are not supported in scVI. You can perform the filtering to 3 genes after hvg filtering. However results are usually bad for cells with less than ~500 counts (for standard 10X sequencing on ‚normal‘ cells.

**Reply (@Slack90)**: Hi, Thanks for your reply. I checked the RNAcount and it looks good to me, and there is no 0 value: Screenshot 2025-01-11 at 10.55.08 1492×1080 34.1 KB I also tried to perform only hvg filtering: concatenated_anndata.obs.groupby('dataset').count() concatenated_anndata.layers["counts"] = concatenated_anndata.X.copy() # preserve counts sc.pp.normalize_total(concatenated_anndata, target_sum=1e4) sc.pp.log1p(concatenated_anndata) concatenated_anndata.raw = concatenated_anndata # freeze the state in `.raw` sc.pp.highly_variable_genes(concatenated_anndata,n_top_genes=10000,subset=True,layer="counts",batch_key="dataset") And again I checked the distribution of RNA count before initializing the model and there is no zero values. However I still get the same error when starting the model…

**Reply (@ori-kron-wis)**: Hey @Slack90 Seems your input is ok. the issue might be due to exploding gradients during training, you can set gradient clipping in the train function and it should help, e.g: model.train(…,gradient_clip_val=1) the default is 0. of course that might also affect the results. there is no rule of thumb on the exact number needed, but trial and error. Also run with early stopping and large max epochs.

**Reply (@Slack90)**: Hi @ori-kron-wis , Thanks for the reply. I ran it again with gradient_clip_val =1 (I also tried =10 and other values). I also added early stoppings and large max epochs as follows: model.train(gradient_clip_val=1, max_epochs=4000, early_stopping=True)``` But I get the same error --------------------------------------------------------------------------- ValueError Traceback (most recent call last) Cell In[23], line 2 1 # model.train(accelerator="gpu", devices="auto", gradient_clip_val=10) ----> 2 model.train(gradient_clip_val=1, max_epochs=400, early_stopping=True) File ~/.conda/envs/MyEnv/lib/python3.11/site-packages/scvi/model/base/_training_mixin.py:145, in UnsupervisedTrainingMixin.train(self, max_epochs, accelerator, devices, train_size, validation_size, shuffle_set_split, load_sparse …

**Reply (@cane11)**: Hi, to me it still looks like it doesn’t even train one step (no progress bar). This only happens if the initialization is off. To help you with this, access to the dataset is necessary (count filtering would be the most common issue but you checked it). If training fails latter during training (model.history will contain losses for several epochs) other tricks might be helpful described here: Frequently asked questions — scvi-tools .

**Reply (@cane11)**: If others look here, it turned out the count data was actually scaled. So it was a dataset problem and not an scvi-tools problem.

## Error loading someone else's SCVI model: no such file (attr.pkl)
**Topic:** 3419 | **Last activity:** 2025-01-13T20:14:00Z
**Posts:** 2 | **Views:** 79 | **Created:** 2025-01-13 | **URL:** https://discourse.scverse.org/t/error-loading-someone-elses-scvi-model-no-such-file-attr-pkl/3419

**Question**: Hello, I am trying to load a model created by a labmate. I have both the .h5ad file and the model folder: dir_path = “Models/Example_model/” adata = sc.read_h5ad(‘Data/Example.h5ad’) vae = scvi.model.SCVI.load(dir_path, data) However, I get the following errors: FileNotFoundError: [Errno 2] No such file or directory: ‘Models/Exmaple_model/var_names.csv’ FileNotFoundError: [Errno 2] No such file or directory: ‘Models/Example_model/attr.pkl’ When I examine previous SCVI models that I have generated, the model folders have three files (model_params.pt, attr.pkl, var_names.csv). However, the models that my labmates generate only have model_params.pt. The only difference we can think of is that they use Mac OS while I use Windows. Is there any way we can resolve this discrepancy? Thanks in adva …

**Reply (@cane11)**: Hi, I would recommend to create a new environment with an updated version of scvi-tools. The version you are using is several years old, while your colleague uses a more recent version.

## Impact of batch on TotalVI results
**Topic:** 3404 | **Last activity:** 2025-01-05T10:32:03Z
**Posts:** 2 | **Views:** 173 | **Created:** 2025-01-04 | **URL:** https://discourse.scverse.org/t/impact-of-batch-on-totalvi-results/3404

**Question**: Good evening, thank you for maintaining TotalVI! We are applying a pre-existing model and classifier built from TotalVI to a new dataset. This new dataset includes samples across several different cancer types, patients, techniques (multiome, single-cell, single-nuclei), and labs. Some cancers have samples from multiple techniques while others do not. We would like to compare our cell types across cancers as best as possible. When we run with batch set to different variables, we obtain very different results. Since our conclusions will differ based upon what we ultimately choose as batch, we would like to understand better what the batch variable is doing. Are you able to provide guidance or information on what the batch variable is doing in the model to help us to select the best batch op …

**Reply (@ori-kron-wis)**: Hey Jennifer, Selecting best batch option might depend also on what you are looking for, as for example if you are analysing the biological aspect of your data, you should use only the technical data as batch (donor, sites etc…), on the other hand you can also use a flag to indicate which techniques even exists per sample , as this might also be a source of bias. As to what specifically batch_key is doing, well, that depends on each model but overall in all cases its try to remove the noise originated in a technical aspects, or the removal of unwanted variation. See the following resources for more information: Project name not set User guide scvi-tools is composed of models that can perform one or many analysis tasks. In the user guide, we provide an overview of each model with emphasis o …

## Differential expression analysis
**Topic:** 1651 | **Last activity:** 2025-01-05T08:23:00Z
**Posts:** 5 | **Views:** 1266 | **Created:** 2023-07-31 | **URL:** https://discourse.scverse.org/t/differential-expression-analysis/1651

**Question**: Hi, I have integrated multiple sc datasets using scvi. Now I’m working on annotating the data. The first step of manual annotation is to conduct differential expression analysis between cluster. It seems that SCVI.differential_expression by default conducts differential expression analysis on the original expression matrix (X), though the clusters are assigned according to the latent space embedding. I wonder if this makes sense since the batch effect that lies in X hasn’t been removed. Should I instead force SCVI.differential_expression to conduct differential expression analysis on the corrected expression matrix (Expected frequency fw(zn, sn) in the paper)? Thanks, Yuqi

**Reply (@martinkim0)**: Hi, thank you for your question. SCVI uses the batch-corrected normalized expression values (denoted as \rho_n in the manuscript) for computing differentially expressed genes. You can see the relevant code portion here

**Reply (@jolespin)**: I had no idea scanpy had differential expression. That would be awesome if I never had to leave Python to get differential expression. What method does it use for the algorithm?

**Reply (@Dario)**: Is it possible to get a batch-adjusted gene-wise matrix for manual exploration? I read the tutorial titled Integrating Datasets with scVI in R , but I could not see how to get the genes by cells batch-corrected values matrix, but only how to do the subsequent step of differential expression analysis. The tutorial also does not explicitly state whether batch-corrected or uncorrected values are being used. Based on the wording in the tutorial, I have the same misunderstanding as Yuqi and I think that the batch correction is only used for assigning cells to clusters. It would be worthwhile to state it explicitly to avoid doubt. I am interested to see the gene values for genes on chrY for women, who do not have that chromosome and hence have zero counts in the Cell Ranger output matrix for wom …

**Reply (@ori-kron-wis)**: Hey @Dario As @martinkim0 previously mentioned, SCVI uses the batch-corrected normalized expression values for performing DE. Sorry It might be misunderstood from tutorials but we can infer that with the fact that we use the trained model to perform the actual DE with the use of the function get_normalized_expression (see code), which is the one you need in order to get your genes by cells batch-corrected values matrix, also in R. just use: model$get_normalized_expression()

## What training datasets are used in the scVI pretrained model (version 2024-07-01)?
**Topic:** 3399 | **Last activity:** 2024-12-23T05:34:06Z
**Posts:** 3 | **Views:** 178 | **Created:** 2024-12-23 | **URL:** https://discourse.scverse.org/t/what-training-datasets-are-used-in-the-scvi-pretrained-model-version-2024-07-01/3399

**Question**: Hi there! I’m looking to create a testing dataset to benchmark a series of integration methods, and I want to avoid using datasets that were included in the training phase. However, I couldn’t find any detailed information about the training datasets abouts scVI pretrained model (version 2024-07-01) on the scVI tutorial page. Could anyone help me with this or point me in the right direction?

**Reply (@cane11)**: Hi, CZI and specifically the CELLxGENE team has full responsibility to train these models. However, all data in the LTS of the specified date are included for training. You can access the dataset ID column (however, it’s hard to track datasets outside of CELLxGENE census using this information as it’s a hash). I would recommend computing the diff between current releases and this LTS and use one of the new datasets as the test dataset as we have done in scvi-hub .

**Reply (@Ringo)**: Thanks for your kind response! I’ll follow the steps outlined in scvi-hub .

## Issue with model.train() in scVI - Training Stuck at 0%
**Topic:** 3382 | **Last activity:** 2024-12-15T07:57:40Z
**Posts:** 2 | **Views:** 279 | **Created:** 2024-12-15 | **URL:** https://discourse.scverse.org/t/issue-with-model-train-in-scvi-training-stuck-at-0/3382

**Question**: Dear： I am encountering an issue while using scvi-tools for cell integration. Specifically, when I run model.train(), the training progress remains stuck at 0%, and no iterations occur despite the GPU being detected and utilized. Below is the log output image 1336×380 24.5 KB I have tried the following steps to troubleshoot the issue: Verified that the dataset is loaded correctly and passed to the model. Ensured that the GPU is available and CUDA is functional. Adjusted training parameters such as max_epochs and learning rate. Despite these efforts, the problem persists. I would greatly appreciate your guidance on how to resolve this issue. Please let me know if you need further details about my setup or code. and,at the same time, after a few minutes, the following error appears: Trainer. …

**Reply (@ori-kron-wis)**: Hi @Ares , As discussed on Issue with model.train() in scVI - Training Stuck at 0% · Issue #3094 · scverse/scvi-tools · GitHub Apriori, seems like a problem in that the interactive progress bar of your jupyter nb is not progressing, as the final message is that the model was trained (this is not an error). So a problem in the jupyter nb widgets I suspect. Can you check if model.is_trained gives you True (you can run 1 epoch just to debug this).

## Train scVI on a sampled dataset
**Topic:** 3302 | **Last activity:** 2024-12-06T00:13:18Z
**Posts:** 9 | **Views:** 429 | **Created:** 2024-10-17 | **URL:** https://discourse.scverse.org/t/train-scvi-on-a-sampled-dataset/3302

**Question**: Hey, We recently started using Leverage score sampling from Seurat that samples large datasets in a way that preserves rare cell types. Assuming I sampled 10% of cells from every scVI batch that I have and trained an scVI model using it, how do I project the remaining 90% of the cells? Since the scVI model has already learned “batch effects” from my sampled data, is it possible to do a forward pass of the trained model to get latent space for the remaining 90% of cells per batch? Thanks

**Reply (@cane11)**: We support now passing train and validation indices. We would be very excited to see some benchmarking with passing stratified indices and model performance. I would assume one could speed up training quite significantly. You can enable it by defining validation_indices to datasplitter_kwargs in model.train. Please update about the results as we might be interested to highlight it as a tutorial.

**Reply (@abs51295)**: So, just to be clear I understand, we are passing 10% of the sampled data for training and the remaining as a validation set?

**Reply (@cane11)**: You can also add cells to the test_set. The validation set is evaluated once per epoch. Adding them to the test_set means they are not used during the full training run. The second one would be more efficient. I would still keep 10% validation cells - maybe using the same splitting technique.

**Reply (@abs51295)**: Okay, I would try with 10% training, 10% validation and 80% test. I am curious though is it the same as Train + Prediction Split ?

**Reply (@cane11)**: Yes, until recently the split was always random. Now you can provide a custom split to the dataloader.

**Reply (@abs51295)**: Hey Cane, Passing stratified indices worked out pretty well. I had a huge dataset of 15M cells and a normal scVI run with fp16 precision and batch size of 2048 would take ~9 hours. I sketched the dataset to downsample while preserving the manifold and had that as an input to the train and validation set. Specifically, I downsampled to 20% of data which is 3M cells and split them half way across train and validation. Remaining 80% were passed as test. The model then took ~3 hours to converge. I compared the UMAPs of both the runs and they looked very similar to me. image 520×257 79 KB

**Reply (@cane11)**: Nice. Do you subset to the same cells for UMAP? Could you share losses? Plotting them would be sufficient. Scib-metrics would also be great. Though looking at UMAPs can be misleading, it gives me the impression that the second one actually looks better (no gradient from blue to orange cells etc) - not sure whether this is expected though.

**Reply (@abs51295)**: Yes, the UMAP is on all cells. My understanding is that when you pass the data as test it’s never used in training but just passed through the model to get the latent space at the end when using model.get_latent_representation() . Here are the loss plots: image 571×453 20.7 KB image 571×453 21.1 KB

## Error loading previously saved scVI model after updating packages / cloud environment
**Topic:** 2306 | **Last activity:** 2024-12-05T05:12:28Z
**Posts:** 7 | **Views:** 804 | **Created:** 2024-05-30 | **URL:** https://discourse.scverse.org/t/error-loading-previously-saved-scvi-model-after-updating-packages-cloud-environment/2306

**Question**: Hello. I recently updated my environment due to server issues which resulted in having to install new package versions (scvi-tools, pandas, etc). I was unable to check the package versions I was using prior to updating the environment before I updated it. I do believe I was using a version of scvi-tools newer than v0.15.0 because my model has the structure ‘model.pt’ (I believe an older version would have the structure ‘model_params.pt’). In the updated environment I get an error when trying to load a previously saved scVI model using scvi.model.SCVI.load() . The error is as follows: TypeError: Argument 'placement' has incorrect type (expected pandas._libs.internals.BlockPlacement, got slice) . I do not think that I can use convert_legacy_save to fix this error due to the format the model …

**Reply (@martinkim0)**: Hi, sorry you’re experiencing this issue. What library is raising the TypeError ? Feel free to past the full traceback of the error.

**Reply (@jflusche)**: Here’s the whole error: TypeError Traceback (most recent call last) Cell In[13], line 5 1 # tutorial section is called "train reference" 2 # reference scVI model was trained in scVI with batch_key & EPI annotation notebook 3 # here, load the trained model ----> 5 model = scvi.model.SCVI.load(working_path + "scvi_model_FGID_and_Healthy_version10x_batch_using_batchkey/", 6 adata, accelerator = 'gpu') 7 #use_gpu=True File ~/.local/lib/python3.10/site-packages/scvi/model/base/_base_model.py:674, in BaseModelClass.load(cls, dir_path, adata, accelerator, device, prefix, backup_url) 661 load_adata = adata is None 662 _, _, device = parse_device_args( 663 accelerator=accelerator, 664 devices=device, 665 return_device="torch", 666 validate_single_device=True, 667 ) 669 ( 670 attr_dict, 671 var_name …

**Reply (@cane11)**: It looks like an inconsistency in pandas versions. This is not strictly an error in scVI-tools but PyTorch unpickling expects the same version of pandas is my understanding (correct me if I’m wrong @martinkim0 ).

**Reply (@kateaugustyn)**: Hi Martin and Can, I am experiencing a similar issue after updating my scvi-tools version from 0.19.0 to 1.1.2. My current version of pandas is 2.0.3 and I am not sure what my old version was. Here is the code I am trying to run: model = scvi.model.SCVI.load(working_path + "/new_scvi_model_Epithelial_batch10x/", adata) Here is the error I am getting: INFO File /home/jupyter/new_scvi_model_Epithelial_batch10x/model.pt already downloaded --------------------------------------------------------------------------- ModuleNotFoundError Traceback (most recent call last) Cell In[70], line 1 ----> 1 model = scvi.model.SCVI.load(working_path + 2 "/new_scvi_model_Epithelial_batch10x/", 3 adata) 4 #accelerator='gpu') File ~/.local/lib/python3.10/site-packages/scvi/model/base/_base_model.py:674, in Bas …

**Reply (@martinkim0)**: Ah yeah, ModuleNotFoundError: No module named 'pandas.core.indexes.numeric' is because the model was previously saved with pandas < 2.0 but loaded with pandas >= 2.0. You can fix this by downgrading to pandas < 2.0.

**Reply (@cane11)**: If people get here, a simple fix is adding the following to your script before loading a model (the issue are integer as pandas Index in model.history). Fixing this is not straightforward (pandas <2.0 handles integer indices differently). However, the fix does not apply to old saved models but only to newly stored models. import sys import pandas sys.modules['pandas.core.indexes.numeric'] = pandas.core.indexes.base pandas.core.indexes.base.Int64Index = pandas.core.indexes.base.Index

## CUDA is available but Training scVI models is too slow
**Topic:** 3371 | **Last activity:** 2024-12-04T08:32:28Z
**Posts:** 5 | **Views:** 394 | **Created:** 2024-12-04 | **URL:** https://discourse.scverse.org/t/cuda-is-available-but-training-scvi-models-is-too-slow/3371

**Question**: image 663×317 8.59 KB As shown in the figure. I am planning to use scvi to train models and integrate single-cell data on WSL on my new Windows 11 computer (RTX 4060Ti, i9-14900k). I installed scvi-tools under Python 3.10 and checked that torch.cuda.is_available() is True . However, when I started vae.train() , I was prompted that cuda had been called and the graphics card memory was already occupied. But the training speed is not as expected. I waited 5 minutes and still did not complete an epoch . For comparison, a similar amount of data has been completed in 5 minutes (Python 3.8, on another computer, RTX 4060Ti). My colleagues and I both had the same problem, we tried Python 3.8 and 3.9 and both failed. In addition, we also installed cuda plug-ins for jax. We are not professional techn …

**Reply (@cane11)**: It looks like the GPU is used. Can you confirm that nvidia-smi shows activity and actually initializes the model? How large is your dataset?

**Reply (@Joe)**: Hi, Here’s my data situation: AnnData object with n_obs × n_vars = 16000 × 3000 obs: 'sample', 'group1', 'group2', 'batch', 'decontX_contamination', 'n_genes_by_counts', 'log1p_n_genes_by_counts', 'total_counts', 'log1p_total_counts', 'pct_counts_in_top_20_genes', 'total_counts_mt', 'log1p_total_counts_mt', 'pct_counts_mt', 'total_counts_ribo', 'log1p_total_counts_ribo', 'pct_counts_ribo', 'total_counts_hb', 'log1p_total_counts_hb', 'pct_counts_hb', 'passing_mt', 'passing_nUMIs', 'passing_ngenes', 'passing_decontX', 'predicted_labels', 'over_clustering', 'majority_voting', 'conf_score', 'leiden', 'annotation_level1', 'annotation_level2', 'annotation_level3', 'main_celltype', '_scvi_batch', '_scvi_labels' var: 'gene_ids', 'feature_types', 'symbol', 'mt', 'ribo', 'hb', 'n_cells_by_counts', ' …

**Reply (@Joe)**: After I updated the nvidia driver, I was able to train quickly, it looks like it is related to the driver? I still don’t get it too clear. But it’s already working normally. [in VSCode] image 1018×269 14.9 KB now my driver version is the latest 566.14

**Reply (@cane11)**: Great that it’s working. It’s likely an underlying torch/CUDA thing and very hard for us to give a good explanation.

## scVI: effect of unbalanced number of cells in batches
**Topic:** 3346 | **Last activity:** 2024-11-27T06:51:51Z
**Posts:** 2 | **Views:** 226 | **Created:** 2024-11-19 | **URL:** https://discourse.scverse.org/t/scvi-effect-of-unbalanced-number-of-cells-in-batches/3346

**Question**: I was wondering whether imbalance in the number of cells in different cell types, batches or datasets will significantly impact scVI training. For example, subsetting a large atlas to have maximum 10k cells for each cell type and roughly the same number of cells as other datasets, I seem to obtain better results. Is this expected or normally handled by scVI loss functions ?

**Reply (@cane11)**: I don’t think that we have extensive testing for this. Since 1.2.0 you can define custom train indices, which would allow testing stratified sampling, but we haven’t done so yet. We don’t see significantly worse performance in lowly abundant cell-types in scvi.criticism compared to downsampling highly abundant cells after training (the metrics are slightly noisy and values increase with more cells).

## Zero value with scvi normalisation
**Topic:** 3352 | **Last activity:** 2024-11-27T06:39:48Z
**Posts:** 2 | **Views:** 106 | **Created:** 2024-11-20 | **URL:** https://discourse.scverse.org/t/zero-value-with-scvi-normalisation/3352

**Question**: Hello, I did a normalisation with scvi-tools. Now I want to use the dotplot function of scanpy. Unfortunatly, the normalisation seems to have modified all the zero value to non zero. Thus when using the dotplot function I do not have anymore information about the % of cells expressing the genes. There si no more zero value so 100% of cells express each genes. How would you deal with that ?

**Reply (@cane11)**: Hi, you can use the expression_cutoff argument in scanpy.pl.dotplot and adjust it or you can use the posterior_predictive_sample function to actually generate count data. However, this function does not support projecting to batches.

## Getting the parameters and their names of scVI
**Topic:** 815 | **Last activity:** 2024-11-27T03:04:15Z
**Posts:** 4 | **Views:** 493 | **Created:** 2022-10-11 | **URL:** https://discourse.scverse.org/t/getting-the-parameters-and-their-names-of-scvi/815

**Question**: Hi, I used to use model.named_parameters in pytorch to get the model’s parameters and their names. I found the analogous in scvi scvi.module.SCANVAE.named_parameters but I could not understand the provided example for name, param in self.named_parameters(): if name in [‘bias’]: print(param.size()) I am not sure how to use it to get the parameters of the scVI model I am using. For example, I am calling the scVI model ‘MODEL’. How can I get the ‘MODEL’ parameters and their names? Thanks in advance

**Reply (@adamgayoso)**: You want to do something like model = scvi.model.SCVI(adata) model.module # this is a pytorch module model.module.named_parameters()

**Reply (@nh-codem)**: Hi, I am trying to trace back the parameters set during scvi_model.train() . Is there a way to retrieve this information from the trained model? Specifically, I want to confirm whether I had set parameters like batch_size , max_epochs , and early_stopping during training. Because, I suspect I may have modified some code in the notebook.

**Reply (@cane11)**: No these are not stored and once trained you can’t look them up. You can call train on an existing model several times. This would lead to inconsistencies. We store however the indices of train and validation cells (in adata.obs) as well as the learning rate and kl_weight if these are adjusted during model training (adoptive lr or kl warmup).

## Scvi-tools: different DEGs when comparing same data
**Topic:** 3350 | **Last activity:** 2024-11-19T16:26:32Z
**Posts:** 3 | **Views:** 269 | **Created:** 2024-11-19 | **URL:** https://discourse.scverse.org/t/scvi-tools-different-degs-when-comparing-same-data/3350

**Question**: Hello everybody, I am new to single cells and differential analysis, so I am sorry if this question may sound stupid. However, I used scvi-tools to perform a differential expression analysis on the same cluster but across cells affected by two different conditions. After setting the seed using scvi.settings.seed = 42 , my code looks like: idx1 = (adata.obs['leiden'] == 0) & (adata.obs['Response'] == 'No') idx2 = (adata.obs['leiden'] == 0) & (adata.obs['Response'] == 'Yes') scvi_de_noresp_vs_resp = model.differential_expression(idx1=idx1, idx2=idx2, batch_correction=True) Then, I focused only on genes for which is_de_fdr_0.05' is True (referred to as “significant genes” from now on) . Now, the thing is: if I redo the same analysis, on the same exact data and with the same exact seed, just i …

**Reply (@cane11)**: Hi, DEG in scvi-tools are computed by random sampling from the underlying distribution. Fixing the random seed yields the same result for the same computation. However switching indices yields slightly different results (similar to another seed). Especially for very lowly expressed genes our estimates can be noisy and I would recommend manually removing them (maximum across both groups of estimated scale smaller than 1e-5 should be fine to filter).

**Reply (@ashenflower)**: Thank you very much for this quick answer, this is extremely helpful. So, in theory, it would be correct to expect the same results in both condition ( IImean, that the log fold change should be symmetric), right?

## Error training MrVI: Backend 'cuda' failed to initialize
**Topic:** 3339 | **Last activity:** 2024-11-18T16:07:59Z
**Posts:** 3 | **Views:** 318 | **Created:** 2024-11-15 | **URL:** https://discourse.scverse.org/t/error-training-mrvi-backend-cuda-failed-to-initialize/3339

**Question**: Hi, I am eager to try out the new MrVI (scVI tools version 1.2.0) on my data, but I am running into the following error. Here is how I set up the model: MRVI.setup_anndata(adata_immune, sample_key= 'sample', batch_key = "version_10x", layer = 'counts') model = MRVI(adata_immune) The error occurs when training the model. model.train(max_epochs=400) Trainer will use only 1 of 2 GPUs because it is running inside an interactive / notebook environment. You may try to set `Trainer(devices=2)` but please note that multi-GPU inside interactive / notebook environments is considered experimental and unstable. Your mileage may vary. --------------------------------------------------------------------------- RuntimeError Traceback (most recent call last) Cell In[43], line 1 ----> 1 model.train(max_epo …

**Reply (@cane11)**: Hi, thanks for trying out MrVI. It uses Jax and not PyTorch as the GPU platform. Please install a GPU-enabled version of Jax. Installation — JAX documentation

**Reply (@kateaugustyn)**: Hi, Thank you! Installing Jax allowed the model to run.

## Integrating different tissues with scVI
**Topic:** 3324 | **Last activity:** 2024-11-15T16:05:18Z
**Posts:** 4 | **Views:** 378 | **Created:** 2024-11-07 | **URL:** https://discourse.scverse.org/t/integrating-different-tissues-with-scvi/3324

**Question**: Hi, I would like to integrated data from three different studies using scVI. These data only contain T cells from two different tissues (blood and tumour location), and one of these datasets only has T cells from blood, another one only has T cells from tumour and the other one has T cells from both blood and tissue. To do train the model, I use the tissue covariate as a covariate to regress in the integration and trained the model using the following code: epochs = 40 scvi.model.SCVI.setup_anndata(ref, layer="raw_counts", batch_key="batch", categorical_covariate_keys=["tissue", "dataset_patient_id"]) # correct for tissue and patient covariates ref_model = scvi.model.SCVI(ref, n_layers=2, n_latent=30, gene_likelihood="nb") # not default values but work well in the integration task accordin …

**Reply (@cane11)**: Hi, I would recommend performing clustering and analyzing differentially expressed genes between these clusters. Gut feeling - the scVI results look closer to my prior expectation of T cell biology. Most T cell states in cancer can’t be found in healthy blood. The rPCA will likely throw together well described populations like activated and naive-like TREG. Both models should correct for tissue (categorical covariate key and batch key is the same). The first one looks better. I’m a bit confused by the many clusters in scVI especially within blood (lower right). This might be bad integration but hard to tell without seeing sample IDs and sample covariatesand DE genes.

**Reply (@martibonomi)**: Hi, thank you for your fast reply. Anyway, these are the clusters for the scVI model using a resolution of 0.5 (the one for which I used the categorical covariate key): Screenshot 2024-11-08 at 8.07.08 AM 1246×1220 251 KB While these are the clusters for the RPCA UMAP: Screenshot 2024-11-08 at 8.07.49 AM 1426×1320 201 KB However, I still haven’t performed DGE between the clusters. I am a bit confused: what do you mean by saying that categorical covariate key and batch key are the same? These parameters correct for the same thing? Batch key should be the parameter that takes into consideration each batch (each experiment/sample) to remove indeed batch effects due to technical variation in performing the experiments, while the categorical covariate key should take into consideration other va …

**Reply (@cane11)**: I would highly suggest to check DEG and potentially use batch key when filtering highly variable genes or to stick with this integration if the clusters are meaningful. I would expect few immune cells in peripheral blood from most cancers. Categorical covariate and batch key is both meant to integrate out the respective key. They are treated similar within the network.

## Integration with or without covariate
**Topic:** 3333 | **Last activity:** 2024-11-11T08:49:46Z
**Posts:** 2 | **Views:** 193 | **Created:** 2024-11-08 | **URL:** https://discourse.scverse.org/t/integration-with-or-without-covariate/3333

**Question**: Hello, I just did two run of scvi with our without covariate. Below is the codes I used. Without covariates : scvi.model.SCVI.setup_anndata(sco, layer = ‘raw_counts’) norm = scvi.model.SCVI(sco) norm.train() sco.obsm[‘norm_scVI’] = norm.get_latent_representation() sco.layers[‘scvi_normalized’] = norm.get_normalized_expression() sc.pp.scale(sco, zero_center=False, layer=‘scvi_normalized’) and with covariates : scvi.model.SCVI.setup_anndata(sco, layer = ‘raw_counts’,categorical_covariate_keys=[‘infection’, ‘timepoint’]) corr = scvi.model.SCVI(sco) corr.train() sco.obsm[‘integrated_scVI’] = corr.get_latent_representation() sco.layers[‘scvi_integrated’] = corr.get_normalized_expression(library_size = 1e4) sc.pp.scale(sco, zero_center=False, layer=‘scvi_integrated’) Of course, the results are d …

**Reply (@ori-kron-wis)**: Hi, Im not sure about the meaning of approximation of reality & what is your further analysis , but here The 2nd option is the way to go if you want to correct the batch effect that was caused because of the categorial covariates [‘infection’, ‘timepoint’] , although we generally state a batch_key parameter in the setup_anndata, which here is missing in both cases (thus in the 2nd case, the categ covariates function in the same manner). so the 2nd option fix the batch effect because of the covariates and this is the main difference between them as I see it

## scVI 21618 problem
**Topic:** 2294 | **Last activity:** 2024-11-07T16:39:45Z
**Posts:** 6 | **Views:** 453 | **Created:** 2024-05-21 | **URL:** https://discourse.scverse.org/t/scvi-21618-problem/2294

**Question**: I found a strange problem when using scVI to remove batch effects. It report a “ValueError: Expected more than 1 value per channel when training, got input size torch.Size([1, 128])” when I deal with totally 21618 cells with 3 batches. However, this problem disappears if I just remove any one cells from the whole dataset. I also tried more cells in one dataset and it works well. However, if I just remove some cells and keep 21618 cells left, the problem comes again. It seems the problem just comes with 21618 cells. I also tried both GPU and CPU and just got the same result. I don’t understand this problem

**Reply (@martinkim0)**: Hi, sorry you’re running into this issue. This is because the batch normalization layer in scVI requires more than one observation in a mini-batch to work properly, and the specific number of observations in your dataset is leading to the last mini-batch having only one cell. This can be fixed by changing batch_size from the default of 128 to something else, or passing in drop_last=True to the datasplitter.

**Reply (@ycliu137)**: Thanks for your answer.

**Reply (@Mikhail)**: Martinkim0 I am new to scvi-tools and have the same problem. Currenly, I am not aware how to use DataSplitter and lost myself in manual. Can you please show an example? I am using very basic model. scvi.model.SCVI.setup_anndata(adata, layer=“counts”, batch_key=“sample_id”) ? AnnDataManager(adata) ? scvi.dataloaders.DataSplitter(adata) model = scvi.model.SCVI(adata, n_hidden = 128, n_layers=2, n_latent=30, gene_likelihood=“nb”) model.train()

**Reply (@cane11)**: Hi, just add datasplitter_kwargs={“drop_last”: True} to model.train. It should skip the last batch. This is only supported in scVI-tools 1.2 and latter.

**Reply (@Mikhail)**: Thank you, Cane11. I would never guess myself!

## Iteration consumes memory
**Topic:** 3310 | **Last activity:** 2024-11-07T11:38:44Z
**Posts:** 6 | **Views:** 247 | **Created:** 2024-10-22 | **URL:** https://discourse.scverse.org/t/iteration-consumes-memory/3310

**Question**: Dear all, I have a AnnData object with data from six patients. When I loop through the patient ids, subset the data, and compute the standard scVI workflow the first patient id needs about 3 minutes to complete. However, the second patient subset takes hours. But if I just run the second patient id on its own it only takes 3 minutes as well. I think that issue is similar to the circular referencing problem with AnnData. ( Anndata not properly garbage collected · Issue #360 · scverse/anndata · GitHub ). I highly appreciate your input on how to ensure that a scVI process is removed from memory. For example in the setting when I looping through patient ids. Many thanks for your help! Best, Florian

**Reply (@cane11)**: Hi, I don’t think your workflow becomes clear. Why do you want to run it seperately per patient? Do you see full GPU or system RAM? This could explain the slowdown. Disabling pinning of memory on GPU would then help.

**Reply (@Florian_Deckert)**: Hi @cane11 , thank you very much for your time. I run scVI per patient and use the model for SOLO doublet detection. Currently I use CPU on our HPC (python v.3.9.19, scvi-tools v.1.1.6.post2). With scvi.settings.num_threads=38 and in the Slurm --nodes=1, --ntasks=1, --cpus-per-task 38. It feels like that after the training the model for the first patient id the CPU resources are still occupied. Do you have any idea what I could try to free the resources? Many thanks, Florian

**Reply (@Florian_Deckert)**: I don’t know if that is good coding practice but importing scvi within the function and using Process seems to free up the CPU after training a model. def scvi_worflow(adata, patient_id): import scvi # Import modules scvi.settings.num_threads=8 # Set SCVI threads adata_i = adata[adata.obs['patient_id']==patient_id] [...] # Train model etc. del adata_i, model_i gc.collect() return None from multiprocessing import Process for patient_id in adata.obs[‘patient_id’].cat.categories: p = Process(target=scvi_worflow, args=(adata, patient_id)) p.start() p.join()

**Reply (@cane11)**: My first intuition is: Do you enable persistent workers? Without it using multiple jobs doesn’t really speed things up, with setting it the workers stay persistent even after training as we don’t kill the dataloader. Deleting the model should be sufficient though - is the gc step really needed? See What are the (dis) advantages of persistent_workers - #8 by albanD - vision - PyTorch Forums for a longer discussion. It would be helpful to get a more complete set of the script.

**Reply (@Florian_Deckert)**: Hi @cane11 , thank you very much for the pointers! I successfully failed to replicate the behavior with other and my own data. However, I realized that there were server updates running regarding the CPU distribution while the problem occurred. Maybe that caused the behavior but I can’t be sure. My apologies.

## Inconsistency of scvi/SOLO in predicting doublets?
**Topic:** 3316 | **Last activity:** 2024-11-07T05:02:49Z
**Posts:** 6 | **Views:** 182 | **Created:** 2024-11-03 | **URL:** https://discourse.scverse.org/t/inconsistency-of-scvi-solo-in-predicting-doublets/3316

**Question**: I’m using colab to run my analysis, and since the session is restarted every time you logged out, or terminated due to long pause, i have come to realization on how the inconsistency of the doublets prediction is affecting my analysis. This is most evidenced when I perform clustering, each restart generated different UMAP profile. Should i implement random seed ?? Or is this normal??? (im newbie in this field) I would highly appreciate any advice I could get in this forum.

**Reply (@ori-kron-wis)**: You should run with scvi.settings.seed = 0 at the beginning (see any of our tutorials), but its not enough. You will only get the exact same UMAPs when comparing 2 runs done after restarting their sessions (under interactive session). In other words, you might get different UMAPs even if you are running the exact same code but under the same session and even after setting that seed. Only setting seed + restarting session each time will guarantee reproducible results (of course given you are running with the same logic)

**Reply (@yiwei24)**: Does this mean i must return the session to a clean slate every time i run scvi?? Would running multiple samples in the same session affect the consistency??

**Reply (@ori-kron-wis)**: when you need to exactly reproduce your UMAPs and results, yes. And this general rule of thumb is true to any statistical code, not just SCVI. if not, you should still get similar results, just a bit different due to the random nature in the process. I didn’t see exactly what you did, but having multiple samples should not the reason.

**Reply (@yiwei24)**: Thank you for your thorough explanation.

**Reply (@cane11)**: It’s unfortunately slightly worse on Colab. There is no guarantee that you get exactly the same plots in Colab. Some additional variation is due to the used GPU (CUDA on two different devices is not deterministic) and Colab sometimes switches the GPU or updates their cuDNN library. I don’t find differences in downstream analysis of results but sometimes in number of Leiden clusters etc. Reproducibility — PyTorch 2.5 documentation gives a short overview.

## Why totalvi can be used as denoising data?
**Topic:** 3323 | **Last activity:** 2024-11-07T04:55:20Z
**Posts:** 2 | **Views:** 174 | **Created:** 2024-11-07 | **URL:** https://discourse.scverse.org/t/why-totalvi-can-be-used-as-denoising-data/3323

**Question**: Hi, I have a quick question about the principle of scVI and totalvi. When considering the decoder of totalvi, it seems that the paper claimed that their proposed method can denoise the rna and protein dataset. I wonder how to interpret the principle of such design, as the reconstruction is still between the generated data and observed data. Furthermore, can we also use the outputs from scVI as denoised feature?

**Reply (@cane11)**: Hi, totalVI models the protein as a mixture of foreground and background. To denoise the expression, we just use the foreground signal so it derives from the best reconstruction. Similarly in scVI and totalVI for the RNA part we sample only the estimated rate of the decoder (see definition of negative binomial in our webpage). For a ZINB reconstruction loss, this estimated rate can strongly differ from the reconstructed signal (removal of zero inflation).

## Autotune failed due to "h5py objects cannot be pickled"
**Topic:** 3308 | **Last activity:** 2024-10-23T16:16:54Z
**Posts:** 5 | **Views:** 222 | **Created:** 2024-10-20 | **URL:** https://discourse.scverse.org/t/autotune-failed-due-to-h5py-objects-cannot-be-pickled/3308

**Question**: Hi, I am trying to tune the parameters. However it failed due to an error saying that “h5py objects cannot be pickled”. I read some related posts saying similar failure due to multiprocessing and reduced the GPU to only 1. But it still failed. Also the tutorial seems doing file with multiple CPUs or GPUs. What should I do to avoid the problem? I also have the same error (h5py objects cannot be pickled) when I tried to save models using pickle on the cluster, but it worked in the standard python environment. model_cls = scvi.model.SCVI model_cls.setup_anndata(adata, layer="counts", batch_key="source", size_factor_key="size_factors") # search space search_space = { "model_params": {"n_hidden": tune.choice([64, 128, 256]), "n_layers": tune.choice([1, 2, 3]),"n_latent": tune.choice([25, 30, 40 …

**Reply (@cane11)**: Hi, you use AnnData object in backed mode. Can you verify this? ** FailTuple(_abc_impl [obj=<_abc._abc_data object at 0x150a689b8e00>, parent=CSRDataset: backend hdf5, shape (3967777, 2000), data_dtype float64])** Ray can‘t handle backed data. You might be more successful with the dask backend (but it’s not tested in scVI-tools and will likely require work on our end to support).

**Reply (@tangxj)**: ah yes. I did used backed when I loaded the data. Thank you! Now I remove the backed mode and keep everything else. I got a new error saying “TypeError: VAE. init () got an unexpected keyword argument ‘lr’”. Am I doing it correctly with “lr”: tune.loguniform(1e-4, 1e-2) in the search_space statement?

**Reply (@ori-kron-wis)**: @tangxj we had similar issue posted in our github repo 2 weeks ago. you should check something similar to: search_space = { "model_params": {"n_hidden": tune.choice([64, 128, 256]), "n_layers": tune.choice([1, 2, 3, 4]), "n_latent": tune.choice([10, 20, 30, 40, 50]), "gene_likelihood": tune.choice(["nb", "zinb"]) }, "train_params": {"max_epochs": 100, "plan_kwargs": {"lr": tune.loguniform(1e-4, 1e-2)}}} and it should work

**Reply (@tangxj)**: @ori-kron-wis @cane11 Thank you both for the suggestion very much! It worked and the job has been running for two days and still keeps on running. I examined the current results in the log file (experiment_state_***.json), it is interesting that the one with minimal validation_loss out of the 21 runs is: Item 20: validation_loss = 1388.1212158203125, experiment_tag = 21_gene_likelihood=zinb,n_hidden=256,n_latent=60,n_layers=2,max_epochs=200,lr=0.0007 The validation_loss ranged from 1388 to 1459. Does that mean I should take zinb as the gene likelihood as well as other params? It seems I was greedy and gave too many options in the search space while I had no idea how long it would take. It seems I might not be able to get the whole tuning finished (my wall time limit was set to 4 days). Wha …

## Fine-Tuning scVI Model
**Topic:** 3281 | **Last activity:** 2024-10-23T03:57:56Z
**Posts:** 3 | **Views:** 208 | **Created:** 2024-10-08 | **URL:** https://discourse.scverse.org/t/fine-tuning-scvi-model/3281

**Question**: Can you in effect drop genes to a subset of interest when fine-tuning a pre-trained scVI model? I’m curious if this could be accomplished maybe by setting the contribution to the reconstruction error to zero for dropped genes? Or maybe create a new model for the gene subset and then pre-initialize the model weights using the matched dimensions in prior models’ module.state_dict()? For some background, I’m using scVI to help model a single-cell atlas I’m working with and it has worked very well to remove technical variation from batch and cell quality. I think this is in part due to the large number of cells included in the atlas. Now I’d like to build scVI models for tailored subsets of celltypes (e.g. macrophages and monocytes) and filter to relevant genes, but I’d like to still leverage …

**Reply (@cane11)**: We train models from scratch in this scenario. It is usually helpful to also include genes that weren’t included in the full model.

**Reply (@mmagzoub)**: Thanks for the clarification, I was just curious if there was a validated approach for this use-case. In case anyone’s interested I gave it a shot fine-tuning my model to my compartments of interest while retaining all genes and making no modification to my scANVI model architecture. Here are the loss curves Major Compartment image 560×435 19.5 KB image 556×435 21.2 KB Minor Compartment image 560×435 18.5 KB image 556×435 21.9 KB

## Transferring lables from refrence dataset to query dataset with a more diverse cell population using scANVI
**Topic:** 2413 | **Last activity:** 2024-10-17T07:53:51Z
**Posts:** 9 | **Views:** 355 | **Created:** 2024-07-25 | **URL:** https://discourse.scverse.org/t/transferring-lables-from-refrence-dataset-to-query-dataset-with-a-more-diverse-cell-population-using-scanvi/2413

**Question**: Hello, Firstly, thank you for providing such an excellent set of tools and tutorials. I’m currently using scANVI to transfer cell labels from a reference dataset of NK cells (labeled according to NK cell subtypes) to a query dataset consisting of CD45+ cells from peripheral blood. In the initial results, all cells in the query dataset have been labeled as different NK cell subtypes. I have a few questions regarding this process: Is it problematic to use a reference dataset with a much narrower variety of cells than the query dataset? Ideally, I only want to label the NK cells in the query dataset. Can I restrict the labeling to cells that meet a higher probability threshold? When using scanvi.predict to return probabilities, what would be a reliable probability threshold to consider the la …

**Reply (@cane11)**: Hi, scANVI is not developed for this use case. Specifically, probabilities are not calibrated and can’t predict an unobserved cell-type. The number of tools that can detect query-specific cell-types is quite limited. To address this need, we have developed popV and have tested it in similar cases beyond the actual manuscript with good results. GitHub - YosefLab/PopV . You will likely need to disable using a cell ontology as the NK cell subsets are not part of the Cell Ontology. We have tested it in these settings and it was rather straightforward to find a good decision boundary (usually >5/7 algorithms will highlight a confident transferred label).

**Reply (@pouria)**: Thank you so much, will give this a try!

**Reply (@pouria)**: Do you think ther would be any added value in annotating NK cells first using PopV with the built in cell onotology to narrow the query dataset down to only NK cells and in a second run, not use cell ontology, but use the refrence dataset and >5/7 algorithm boundary as you suggest?

**Reply (@cane11)**: I think both results will be best case very similar. I assume NK cells are defined more stringently in your dataset as you are interested in these cells. I would directly go towards your reference dataset as in Tabula sapiens I disagreed with some Tcell labels.

**Reply (@pouria)**: Read you’re paper on BioArchive, I appreciate the work, and would love to use PopV. For some reason my installation doesn’t work. Can’t find the proper modules when following you tutorials. Also the google collab notebooks don’t work. Do you have any suggestions? Thank you for all your help thus far.

**Reply (@pouria)**: Have to emphasise that I’m an MD and not a bioinformatician, could be a very easy fix, because I lack basic coding skills.

**Reply (@cane11)**: Thank for your interest in using it. I’m likewise an MD and no worries. There were some outdated Colab notebooks circulation. Can you try: Google Colab . I just ran it on Colab an no issues were showing up. Can you confirm that you use the same link?

**Reply (@pouria)**: Sorry for my lag in response, have been occupied with experiments in the lab. Thank you for sending the the latest google colab, I will try it out and get back to you when I find the time. Really appreciate all your help!

## SCANVI inferred cell types don't make sense
**Topic:** 3300 | **Last activity:** 2024-10-17T03:33:28Z
**Posts:** 2 | **Views:** 210 | **Created:** 2024-10-16 | **URL:** https://discourse.scverse.org/t/scanvi-inferred-cell-types-dont-make-sense/3300

**Question**: Hi, I used scANVI to infer unknown cells from a trained scVi model. I then checked a small cluster to compare the original cell type “celltype_manual” and the inferred cell type ‘C_scANVI’ > adata.obs[adata.obs['leiden_0.2']=='19'][['celltype_manual','C_scANVI']].drop_duplicates() |celltype_manual|C_scANVI| |---|---| |Neuron|Endothelial| |Neuron|Ependymal| |Neuron|SMC| |Neuron|Neuron| |Neuron|Fibroblast| |Neuron|OPC| |unknown|Endothelial| |unknown|Ependymal| |unknown|Immune_cells| |unknown|SMC| |unknown|Oligodendrocyte| |unknown|Astrocyte| |Oligodendrocyte|Endothelial| |Oligodendrocyte|Oligodendrocyte| The celltype_manual came from the original meta data of published data sets, so should be taken as truth here. However the inferred cell type by scANVI looks like random. And even if that’s …

**Reply (@cane11)**: Please also try a KNN classifier in latent space (see e.g. PopV code for a simple classifier). We and others found that the scANVI classifier sometimes doesn’t perform well. This is especially true before release 1.1 of scVI-tools.

## Using low precision matrix multiplication to boost performance
**Topic:** 2522 | **Last activity:** 2024-10-17T02:50:22Z
**Posts:** 7 | **Views:** 858 | **Created:** 2024-09-19 | **URL:** https://discourse.scverse.org/t/using-low-precision-matrix-multiplication-to-boost-performance/2522

**Question**: Hey, I was wondering if we could use Speed Up Model Training — PyTorch Lightning 2.4.0 documentation for GPUs to speed up training. Do we need to modify the training code of scVI in order to use that or should it be usable out of the box? Thanks

**Reply (@cane11)**: Hi, for integration my experience is that torch.set_float32_matmul_precision("medium") is safe to use. For downstream analysis like differential gene expression this might not be the case as these are more sensitive. It is unfortunately very hard to test in a manner to give good guarantees about it.

**Reply (@abs51295)**: Thanks. The speedup in integration is significant (at least 2x) by setting torch.set_float32_matmul_precision("medium") . Can we suggest to use this in scvi docs somewhere when you have millions of cells and want to speed things up?

**Reply (@cane11)**: No, recommending it would require more extensive testing, and I’m not sure how similar we would expect things to be. To get, major speed-up, set batch_size to 1024/2048 (pretty linear in speed). We will have torch.compile support soon’ish (another 50% speed-up)

**Reply (@abs51295)**: How do I track the training so that I know that changing to low precision did/didn’t work? What would you look for? Also in Increase scVI integration speed - #2 by Valentine_Svensson @Valentine_Svensson didn’t see any significant increase by changing batch_size. Is it still the case?

**Reply (@cane11)**: For things like DE, it’s pretty hard to tell as two very similar reconstruction losses might still yield different results (as it’s not very sensitive for e.g. low rates (whether it’s 1e-5 or 1e-6 yields almost the same loss but is different for DE). We are working on making downstream analysis more robust. For integration quality, just check that the embedding makes sense (your cell-types are well separated and your batches mix well). We tested large batch sizes for CELLXGENE census (30 million cells) and found that increasing batch size was helpful for speed. Also when tracking losses. The effect might be smaller on other datasets but I still think it’s now the default for many labs doing large integration.

**Reply (@abs51295)**: Thanks @cane11 I did try increasing batch size and it does speed things up linearly as you said. Although, one thing I noticed is that the embedding is more sensitive to batch size rather than floating point precision.

## Model Training got only 2 epochs
**Topic:** 3284 | **Last activity:** 2024-10-14T19:21:46Z
**Posts:** 5 | **Views:** 465 | **Created:** 2024-10-09 | **URL:** https://discourse.scverse.org/t/model-training-got-only-2-epochs/3284

**Question**: Hi, I am trying to integrate a 4-million cells scRNA data set. The adata has been subset to top 2000 highly variable genes. I set up the model use almost default parameters. model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood=“nb”) model.train() But I got only 2 epochs for the training. What decides the number of epochs for the training?

**Reply (@cane11)**: Hi. We have a heuristic that sets the number of epochs. However, I would recommend to use 20 epochs (max_epochs=20) in model.train. You should check model convergence afterwards (see tutorials for plotting losses).

**Reply (@tangxj)**: Thank you. I set the max_pochs to 100 and early stopping true. It stops at 34 epochs. Now I have another question. I am trying to plot the embeddings. Due to the large amount of cells, I used the following settings sc.set_figure_params(figsize=(6, 6), frameon=False) sc.set_figure_params(vector_friendly=True, dpi_save=300). But the umap plot is centered and the legend on the right side is cut out. I changed the figure size to (12,6) but it only elongated the umap plot horizontally. How should I adjust the parameters to make the legend visible? image 745×500 43.5 KB

**Reply (@cane11)**: It might be that there are single cells that are outliers in UMAP, so the plot doesn’t populate the whole area. If you save as png the legend should be within the plot. I’m not exactly sure why in PDF the legend is outside of the plot. You can set tight_layout before saving it in Matplotlib. If things are not working, please share your full code for plotting.

**Reply (@tangxj)**: Thanks for the help. I removed 5 cells as outliers and used tight_layout. It works beautifully.

## Trouble integrating my dataset into a reference dataset
**Topic:** 2514 | **Last activity:** 2024-10-11T19:07:52Z
**Posts:** 17 | **Views:** 734 | **Created:** 2024-09-12 | **URL:** https://discourse.scverse.org/t/trouble-integrating-my-dataset-into-a-reference-dataset/2514

**Question**: Hello! I’m trying to integrate my query dataset (~13000 cells) into a larger reference dataset (OMG database). I’ve selected cells from E11.5 embryos, matching my sample. I select 5,000 highly variable genes using the pearson residuals. However, my resulting UMAP shows me that they are clearly not integrated at all. I’ve tried downsampling the reference dataset (200,000 cells → 30,000 cells), but it doesn’t help at all. Here’s the UMAP: Untitled 1668×1384 203 KB Some information about my dataset: it’s generated from a transgenic mouse embryo E11.5 which have been FACSed for mCherry expression. It’s a mix of cell types which I only vaguely know the composition of (should contain primarily brain, heart, limb tissue). Additionally, there are 30 artificial genes which I’ve inserted into the ge …

**Reply (@cane11)**: Can you share results with other integration methods like BBKNN or harmony (both available in scanpy). Reducing the number of latent dimensions will likely help with integration. The n_layers is quite high and together with encode_covariates this can create issues. I would turn off encode_covariates, reduce n_latent to 10 and check how well it integrates first.

**Reply (@joshuak94)**: Hi Can! Thanks for the prompt response. Here are three UMAPS. Integrated using SCVI, n_layers = 10, encode_covariates = False. Untitled 1668×1384 257 KB Integrated using Harmony, default parameters. Untitled-1 1668×1384 219 KB Integrated using BBKNN, also default settings.| Untitled 1668×1384 337 KB Integrated using BBKNN, but with ridge regression on the scaled data prior. As explained here . Untitled 1668×1384 330 KB Lastly, for thoroughness’ sake, I used scanpy’s ingest function. First did PCA reduction, calculated neighbors and UMAP representation on the reference, then called ingest. Untitled 1616×1384 253 KB It looks like ingest does the best job, followed by BBKNN with ridge regression, then BBKNN & Harmony tied, then SCVI unable to integrate any of the cells. Additionally, here’s t …

**Reply (@joshuak94)**: Additionally, I had a quick question. The integration of the two datasets doesn’t have an effect on the downstream SCANVI label transfer, does it? I wasn’t sure if these two tasks were dependent on each other or independent.

**Reply (@yojetsharma)**: Could ‘flavour’ parameter be the one causing this? Have you tried “seurat_v3” or playing around with this?

**Reply (@cane11)**: It’s hard to judge whether BBKNN with ridge regression is overintegrating.Likely you will have the easiest time working with the harmony integration (colored by prior cell-type labels might help to decide on this). Both datasets seem to have strong differences. Harmony performs stronger in batch correction while scVI performs better in cell-type preservation in numerous benchmarks, so I think your results agree with this. Reducing the number of highly variable genes (maybe 1000) might help to better integrate them. Yes, if your integration is not good. scANVI will be also worse for transfering labels.

**Reply (@joshuak94)**: Originally I had done my analyses with seurat_v3. I tried switching to pearson_residuals after reading that maybe this captures better biological variance. But at least between these two options I didn’t see any difference using the original parameters (n_latent = 50, 5000 HVG).

**Reply (@yojetsharma)**: Then, could it because of the non-matching categorical labels in the query wrt your reference?

**Reply (@joshuak94)**: Sorry, I’m not sure I know which categorical labels you mean. Do you mean the celltype labels? In the query I set the celltype to “Unknown”, but I thought this is common procedure for doing the label transfer.

**Reply (@joshuak94)**: Hmmm I see. Changing the number of HVGs did seem to help a bit with the integration. Continuing my analyses with the harmony integration would be less than ideal, because as far as I’m aware, harmony does not support label transfer/annotation of the query dataset. I was hoping to use SCANVI to map my query to the reference and get the cell types that way.

**Reply (@cane11)**: Have you tried this: cane11: I would turn off encode_covariates, reduce n_latent to 10 and check how well it integrates first. You can run a kNN classifier, see e.g. my PopV package how to perform label annotation with harmony integration: GitHub - YosefLab/PopV .

**Reply (@joshuak94)**: I tried reducing the n_latent, the resulting UMAP is the first in the list of UMAPs I uploaded above. I will check out PopV soon! I noticed however that there are only pretrained models for the tabula sapiens datasets. Is there a tutorial available for training my own models? Since I’m interested in mouse embryonic data, I guess a reference dataset like the Ontogeny of Mouse Graphed, or Mouse organogenesis cell atlas would be better sources.

**Reply (@cane11)**: Sorry for the confusion. I don’t think you should run popV here (while you could). It just contains code to classify celltypes based on harmony integration (k-nearest neighbors).

**Reply (@joshuak94)**: Thanks for the pointers! Is there a reason you don’t think popV should be run in this case? From what I understand, it’s a consensus based method for generating cell type labels using a variety of different models, right? It sounds like it could get the most robust/accurate labeling of my dataset.

**Reply (@cane11)**: I would assume consensus scores will be low as integration is not working very well and also classifiers on gene expression might have high uncertainty. My approach here would be. A marker gene based approach for cell-typing and then perform (semi)supervised integration like scANVI or semisupervised MrVI to do comparative analysis.

**Reply (@dacho)**: I don‘t know if you have any update on this issue, because I am having similiar issue when integrating my query to the reference. Reducing the HVGs to 1000 only helepd a bit. When I downsampled my reference (using same qc criteria based on my query n_genes_by_counts and total_counts), it also got bit better. So, I am now trying to approach in consensus way as well. I used rough manual annotation, Cellassign, Celltypist and SCANVI to annotate and compare the output of these methods. I don‘t know if this is something that we could do, but around 70% of cells seems to agree on the cell type. And I think here you could see how you could create your own reference in popV: github.com/YosefLab/PopV How to create pre-trained models opened 10:07AM - 11 Feb 23 UTC closed 08:37PM - 16 Jun 23 UTC ccru …

**Reply (@cane11)**: Hi @dacho welcome to the forum. Without more information it is difficult to provide a good response - experimental setup, how many cells, do you expect it to be integrated. Running PopV will work for most cases, here I was questioning the approach as it will highlight that it’s difficult to annotate a query using a reference dataset if they are very distinct. PopV should output in this case, that you better annotate it manually and won’t provide much help.

## Is it possible to add extra covariate categories to a trained SCVI model?
**Topic:** 3276 | **Last activity:** 2024-10-04T14:56:12Z
**Posts:** 4 | **Views:** 278 | **Created:** 2024-10-02 | **URL:** https://discourse.scverse.org/t/is-it-possible-to-add-extra-covariate-categories-to-a-trained-scvi-model/3276

**Question**: I execute the following steps to predict cell types in a query dataset using a reference dataset: Train an SCVI model on a reference dataset with categorical covariates. Concatenate query and reference datasets. Create a SCANVY model using the concatenated dataset and the SCVI model above. Train the SCANVY model. During the creation of the SCANVY model I get an error saying that the covariate categories of the query dataset are different from that of the reference. The only workaround to this problem that I’ve found is to add the query categories to the reference adata object before training the reference. But it does not seem like a sustainable solution as I will need to retrain the SCVI model for every new query dataset. Is there any way to add extra covariate categories to an already tr …

**Reply (@cane11)**: Hi, we added support for scArches and categorical covariates in 1.2 (extending categorical covariates). However, the from_scvi_model function doesn’t extend batches or covariates but you would need to use load_query_data . For this you should first convert your SCVI model to a SCANVI model (from_scvi_model) and can then without training use the load_query_data function. This API is meant so across models only load_query_data extend categories.

**Reply (@wikiselev)**: Great, many thanks for your answer, it helped a lot! However, I did need to train SCANVI model before load_query_data , otherwise the predictions did not work. I’ve also found this resource , which also suggests to train the SCANVI model.

**Reply (@cane11)**: After initializing the SCANVI model, you can also train it and afterwards integrate query data with load_query_data. In the approach above, you have to unfreeze the network using unfrozen=False in load_query_data otherwise it doesn’t train the SCANVI model (sorry for the oversight).

## Error in MrVI differential abundance
**Topic:** 2486 | **Last activity:** 2024-09-27T17:20:51Z
**Posts:** 2 | **Views:** 119 | **Created:** 2024-09-02 | **URL:** https://discourse.scverse.org/t/error-in-mrvi-differential-abundance/2486

**Question**: Hi, In the function ''differential_abundance, there is one line which generates error because n_cov_values is an integer: f"It has {len(n_cov_values)} unique values, which exceeds one half of the total samples ({n_samples})." TypeError: object of type ‘int’ has no len() Thanks, Yun-Ching

**Reply (@Justin_Hong)**: Thanks for raising this, we will make this fix asap!

## Scale for predicted vs observed plot in SCVI-SCANVI mapping?
**Topic:** 2534 | **Last activity:** 2024-09-25T17:14:29Z
**Posts:** 3 | **Views:** 108 | **Created:** 2024-09-24 | **URL:** https://discourse.scverse.org/t/scale-for-predicted-vs-observed-plot-in-scvi-scanvi-mapping/2534

**Question**: I’m curious to know: is the plot generated in scanvi mapping where yellow and green I assume are signifying similarities—publishable? If so, would adding a scale bar which could tell for eg yellow being the most similar and green almost similar help the readers? I was able to map my in vitro dataset to an in vivo dataset. Among these, can I annotate my unlabelled clusters with the ones that have yellow/green level similarity with the in vivo dataset? Overall it had an accuracy of 62%. IMG_6676 1179×1158 163 KB

**Reply (@cane11)**: These signify confusions. Generally high confusion means similar cell-types. However, it doesn’t need to be that all cells are similar but can also mean that some cells within a celltype are more similar and some are less or that the frequency of this celltype was low in the reference data. I would recommend using a heatmap of marker genes to distinguish these cases

**Reply (@yojetsharma)**: A follow up question: if the markers genes are not easily distinguishable (because my dataset has a healthy and 2 patients), would you recommend going ahead with the labels that get predicted even if the accuracy is 62%?

## scVI with large datasets
**Topic:** 2533 | **Last activity:** 2024-09-24T22:51:51Z
**Posts:** 5 | **Views:** 599 | **Created:** 2024-09-24 | **URL:** https://discourse.scverse.org/t/scvi-with-large-datasets/2533

**Question**: Related to the topic of large datasets, I have been working with some datasets of millions of cells and training scVI models with all human genes and I have been having out of memory errors prior to training initiating, when the scVI constructor is called, i.e. model = scvi.model.SCVI(adata, n_layers=n_layers, n_latent=n_latent, n_hidden=n_hidden, gene_likelihood="nb") runs out of memory (and I have been using machines with as much as 384 gigabytes of RAM). Is there a workaround for this or something I am missing? The anndata object is in backed mode adata = ad.read_h5ad(h5ad_file, backed="r+") Is the constructor loading the entire dataset into memory for some reason? I previously commented this in this thread, but never got a response: SCVI tools with large datasets scvi-tools I have have …

**Reply (@yojetsharma)**: I tried training a dataset from Braun et al 2022 Science using a 32GB RAM but I would have the same memory issue. Downsampling the number of cells helped it but this had some influence on mapping.

**Reply (@cane11)**: Can you explicitly define a size_factor in model.setup_anndata (you can set it to the counts per cell). Currently it loads the full data into memory to infer the library size. We are aware of this issue and it will be soon‘ish fixed.

**Reply (@agdenadel)**: Hi @cane11 , thanks I’ll try this. If I have previously trained models using the default (with a smaller training dataset) and I wish to do apples-to-apples comparisons of all of these models, I would need to retrain those with the new size factor, correct?

**Reply (@cane11)**: The difference is very marginal (activation function of the output layer is softplus when using size factor while it is softmax by default otherwise). I would still recommend to retrain, if you want to make sure they are fully comparable.

## ZeroDivisionError using scvi-tools
**Topic:** 2500 | **Last activity:** 2024-09-23T15:07:33Z
**Posts:** 16 | **Views:** 501 | **Created:** 2024-09-09 | **URL:** https://discourse.scverse.org/t/zerodivisionerror-using-scvi-tools/2500

**Question**: I am running snapatac2 tutorial wherein scvi-tools are used to map reference to query (so I am a new scvi-tools at the moment). Reference is a scRNA dataset and query is an atac seq: query= snap.pp.make_gene_matrix(atac, snap.genome.hg38) query AnnData object with n_obs × n_vars = 58534 × 60606 obs: 'sample', 'leiden' reference=snap.read("GEX.h5ad", backed=None) AnnData object with n_obs × n_vars = 187285 × 2000 obs: 'sample', 'cell_type' var: 'highly_variable' query.obs['cell_type']=pd.NA data = ad.concat( [reference, query], join='inner', label='batch', keys=["reference", "query"], index_unique='_', ) data AnnData object with n_obs × n_vars = 245819 × 1397 obs: 'sample', 'cell_type', 'batch' sc.pp.filter_genes(data, min_cells=5) sc.pp.highly_variable_genes( data, n_top_genes = 3000, flav …

**Reply (@cane11)**: Hi, we have never tested transfering to gene activation scores and it doesn’t sound right to me. However, to fix your issue. You are setting all celltypes to None. The way you are then updating it with celltypes is incorrect and it won’t update your matrix (see pandas warning). You should do: data.obs.loc[ref_idx, "celltype_scanvi"] = data.obs.loc[ref_idx, 'cell_type']

**Reply (@yojetsharma)**: Noted, will try this. Thank you! However, I’m confused regarding usage of SCVI-tools for reference mapping. Since scvi is a part of the SNAPATAC2 tutorial, I didn’t think too much about it, until now. Can you please tell me why it’s not the right approach?

**Reply (@cane11)**: Gene activation scores from ATAC data is not measured gene expression using those values equivalent to gene expression sounds weird to me and we don’t support this. ScVI is meant to integrate datasets with measured gene expression data. If the developers of SNAPATAC2 wants to highlight this use case, it’s best to check with them why this is justified and how they tested performance.

**Reply (@yojetsharma)**: Their nature methods manuscript doesn’t really talk about it. So, I will post it there. Thank you for your suggestions!

**Reply (@yojetsharma)**: Update: I am still getting the zerodivisionerror. Will ask on the snapatac2 forum regarding the same.

**Reply (@EmiDalla)**: Hello, I’m having exactly the same issue following exactly the same tutorial . It is definitely weird that SnapATAC2 authors suggest to follow this method, however the code used in the tutorial was working for me until I subset the reference: at that point, I suppose some cell group became empty and the error prompted. I tried using the code recommended by cane11 but got the same error. @ yojetsharma could you please provide the link to the the snapatac2 forum, so that I can follow the discussion there? EDIT: found it

**Reply (@cane11)**: I’m very certain that both of you are running scANVI without any cell-type labels. It would be helpful to report adata.obs[LABEL_KEY].value_counts() as well as adata.obs[‘_scvi_labels’].value_counts().

**Reply (@yojetsharma)**: adata.obs[‘_scvi_labels’].value_counts(): 0 245819 Name: _scvi_labels, dtype: int64 adata.obs[‘cell_type’].value_counts(): Neuron 63422 Radial glia 60436 Neuroblast 27840 Neuronal IPC 18388 Glioblast 17199 Name: cell_type, dtype: int64

**Reply (@cane11)**: Obviously, your labels are not setup properly. In addition, you send the content of cell_type but use celltype_scANVI to set up the model. celltype_scanvi likely contains only unknown currently. With the suggested line in pandas you should be able to update the content.

**Reply (@yojetsharma)**: Yes, it is solved now. Thank you for this! I feel so stupid right now.

**Reply (@EmiDalla)**: Could I kindly ask you what you did to fix the issue? I just started using python and I certainly missed something very important, but using the modified command provided by @ cane11 didn’t solve the problem for me. Besides, in the SnapATAC2 tutorial I also got this data_pbmc5k.obs['_scvi_labels'].value_counts() _scvi_labels 0 14061 Name: count, dtype: int64 but it didn’t prevent the code to run “properly”. One last thing: does the code expect to have the same barcodes used in both scRNA-seq and scATAC-seq data? This might be my problem… Thank you.

**Reply (@yojetsharma)**: In my case, the error i found out was due to cell_type column in my reference. I didn’t realize the reference i was populating itself had annotation as NaN for some clusters. After correcting this it ran fine. I am still concerned with what cane11 pointed out regarding use of scvi-tool to annotate atac dataset using rna.

**Reply (@yojetsharma)**: Were you able to solve it?

**Reply (@EmiDalla)**: Unfortunately not, as I previously said there is probably a need for the same barcodes being used in both datasets, which is not my case.

**Reply (@yojetsharma)**: I remember asking Kai Zhang on their repository in one of the issues regarding this and he replied that it’s not needed. And I have actually also mapped my ATAC onto the an independent RNA. It worked after realising the issue.

## Embedding number for visualization
**Topic:** 2482 | **Last activity:** 2024-09-23T05:04:21Z
**Posts:** 11 | **Views:** 361 | **Created:** 2024-08-29 | **URL:** https://discourse.scverse.org/t/embedding-number-for-visualization/2482

**Question**: Recently I found some standard deviation (sd) of embedding scores after scvi integration were closed to 0 (about 0.02, the information was store in seurat_object@reductions[[“integrated.scvi”]] @cell.embeddings ), even some of the top embeddings (scvi_1, scvi_4, scvi_9, shown as follow: embedding scores in cells belong to different clusters). I wonder if embedding score with sd close to 0 is helpful for visualization. Why do the results turn out like this and how many embeddings should I choose. The analysis was based on Seurat V5, integratelayers function. 图片1 1303×1208 236 KB

**Reply (@cane11)**: Hi. Unfortunately, I really don’t get what you are doing here. Are those different runs of scVI compared with each other? What’s your expectation and why are you doing it? Sharing some code would additionally be helpful.

**Reply (@vgettaa)**: Hi, thanks for reply. I used scvi tool to integrate 6 scrna samples. After integration, the functions (FindNeighbors, FindClusters, RunUMAP) were used for clustering and visualization. A parameter specifed the number of embeddings should be input when using FindNeighbors and RunUMAP. Like PCA, the top PCs capture most data variances, and PCs have variances in decreasing order (The first pc has highest variance). But the SD of first, fourth, ninth embedding scores output by scvi were closed to 0 in the above figure, indicated that it is unhelpful of these embeddings (sd closed to 0) for clustering. So I am confused about the results and dont know how many embeddings should I choose for visulization.

**Reply (@cane11)**: I see, you should use all latent_dimensions. The order of latent dimensions doesn’t highlight importance or something. While axes with a higher estimated variance (qz_v) contain less information, filtering these out is unconventional for VAEs.

**Reply (@vgettaa)**: Maybe axes with higher estimated variance contain more information? I am not familiar with the VAE and UMAP algorithm, and I should use all latent dimensions for clustering and visulization? (the integration function ‘Integratelayers’ will output 30 latent dimensions). Thanks!

**Reply (@cane11)**: I think in integratelayers you don’t have access to the estimated variances of each cell but only to the estimated mean position in latent space (so you are displaying here the variances across these means). I was speaking about the per cell variance in a VAE. I would highly recommend to not reduce the number of latent parameters post hoc but use all latent dimensions for downstream analysis.

**Reply (@vgettaa)**: Thanks for reply! Actually, I dont know the relation between VAE and latent dimension. I would like to express this more clearly, in my understanding, the output of integratelayers contains a n x 30 matrix, n represents the number of cells, 30 represents the number of latent dimensions. The matrix indicates the position of each cell in a 30 dimension space, and it is difficult to distinguish cells with dimensions of low variance. I think these 30 latent dimensions are similar to principal components. So if the importance of latent dimensions is unrelated to variance, then I think all latent dimensions should be used for downstream analysis.

**Reply (@cane11)**: Yes use all latent dimensions.

**Reply (@vgettaa)**: Hi. I tried to use 21 dims to plot the UMAP, which removed the dims with low SD (in the above figure, integratedscvi_29, integratedscvi_10, integratedscvi_27, integratedscvi_1, integratedscvi_11, integratedscvi_4, integratedscvi_9, integratedscvi_15, integratedscvi_18). Compared to the UMAP plotted with 30 dims (all dims were used), I found the two plots are similar. So, for the UMAP, maybe it should rank the dims by SD and choose the high ones? 资源 4 1006×528 137 KB

**Reply (@cane11)**: The one with low variance might be important for lowly abundant celltypes. I would highly recommend against subsetting the latent dimensions based on some criterion. Standard VAEs are not designed to have a sparse set of latent dimensions that are important.

**Reply (@vgettaa)**: Thanks! I think I should take some time to learn VAE.

## scArches with multiple covariates
**Topic:** 1372 | **Last activity:** 2024-09-22T21:08:33Z
**Posts:** 10 | **Views:** 1086 | **Created:** 2023-05-02 | **URL:** https://discourse.scverse.org/t/scarches-with-multiple-covariates/1372

**Question**: Hi, I want to use scArches to query disease samples to a normal reference. My data comes from a range of studies, using different single cell technologies, each including different patient samples. My reference model looks like this: scvi.model.SCVI.setup_anndata( adata_ref, layer=“counts”, batch_key=“sample”, categorical_covariate_keys=[“study”], ) But when I add the query data I get an error: vae_q = scvi.model.SCVI.load_query_data( adata_query, dir_path, ) scArches currently does not support models with extra categorical covariates. Does this mean I can’t have multiple covariates? Is there any workaround for this? Many thanks, Jess

**Reply (@martinkim0)**: Hi, thank you for your question. Yes, it looks like scArches currently does not support categorical covariates. A possible way around this would be to concatenate your "sample" and "study" columns into a single obs and then use that as the batch key. I’m not sure if there are plans to support extra categorical covariates for scArches in the future.

**Reply (@jesswhitts)**: Thanks for your help I think this feature would definitely be useful, for future versions of scArches

**Reply (@martinkim0)**: Thanks for the feedback! We’ll see if we can update scarches with this feature.

**Reply (@sdettle)**: Any update on this?? Would really love a categorical covariate option for my work.

**Reply (@cane11)**: Hi, we have an open PR. We haven’t fully tested it yet. It might be part of the 1.2 release. However, please be mindful we don’t specifically decouple multiple covariates and I wouldn’t say that we learn the effect of e.g. disease due to this. The approach in MrVI is likely more founded.

**Reply (@sdettle)**: Thanks for the quick response, and I agree MrVI will be better for my work. However, I still need to develop a way to use the trained model to work on data it isn’t trained on. From my understanding MrVI is not compatible with scarches and isn’t planned to be. (For my research question I want to train the model on in vivo data and then benchmark multiple in vitro datasets against the in vivo MrVI model as to what it is most similar to). Before my workflow was scVI → scANVI → scArches (to get label transfer) any ideas about how to proceed while keeping batch specific learned effects (cross species)?

**Reply (@cane11)**: You are right, JAX scArches doesn’t exist currently. It won’t be super hard to implement and it is definitely planned. However, timeline is Q1/2 2025.

**Reply (@sdettle)**: Thanks Cane11! Ive got the github version of scvi-tools install (pypi installation doesn’t have the external.mrvi i found… maybe something else was going on). But, besides that I am loving mrVI (great preprint also!), and super excited to polish up my metadata to use it to it’s full abilities on my data. Thanks team this is an awesome upgrade to the scviverse.

**Reply (@yojetsharma)**: I think what you’re looking for is done in this ms by Truetlin/Theis lab where they’ve mapped multiple iPSC derived brain organoids single cell datasets to developing human brain: neural_organoid_atlas/NOMS_mapping/03_NOMS_to_HNOCA_mapping.ipynb at main · theislab/neural_organoid_atlas · GitHub

## Ambient RNA removal before TotalVI?
**Topic:** 2528 | **Last activity:** 2024-09-22T16:38:49Z
**Posts:** 2 | **Views:** 186 | **Created:** 2024-09-22 | **URL:** https://discourse.scverse.org/t/ambient-rna-removal-before-totalvi/2528

**Question**: I am processing CITE-seq data, in which Cellbender is recommended to remove ambient RNA contamination to reduce the noise of gene and ADT signals. However, at the same time, I noticed that TotalVI also have the ‘denoise’ step. I am not sure whether these two steps will conflict? In addition, in which step should ‘isotype’ be input as control? There is also the question of whether the ‘Hashtag’ demultiplex step should be done before or after backgroud denoising?

**Reply (@cane11)**: It is generally speaking safe to run ambient removal with Cellbender before running VI models. Ambient and background might be two different things though as the distribution of antibody and in cells might be different due to effects like FC receptors. As to setting isotype: I’m not sure as to what code you are referring?

## scVI reproducibility seed issue
**Topic:** 1731 | **Last activity:** 2024-09-19T15:34:22Z
**Posts:** 5 | **Views:** 1160 | **Created:** 2023-08-31 | **URL:** https://discourse.scverse.org/t/scvi-reproducibility-seed-issue/1731

**Question**: I have seen a few similar issues on discourse but not quite exactly the same. Background: I have been using scVI across two Jupyter notebooks within the same conda environment. The first notebook is to run the top 3 models identified using autotune. The second notebook is to run the model of choice. Issue: I have noticed that both scVI models, despite setting seeding and having identical parameters, appear different. The cluster node used for both were identical. I ran this again with the following code across two notebooks and still had different scVI outputs. import os import sys import pandas as pd import numpy as np import matplotlib.pyplot as plt import matplotlib.font_manager import seaborn as sns import anndata import scvi import scanpy as sc scvi.settings.seed = 9627 adata = sc.rea …

**Reply (@Justin_Hong)**: Thanks for flagging this @Nusob888 . Unfortunately I’ve been more out of the loop with recent changes. @martinkim0 do you know what may have caused this? Perhaps it is related to the change for the jax random seed?

**Reply (@martinkim0)**: Hi @Nusob888 , thanks for bringing up this issue. It’s not immediately clear to me why this is occurring as the recent changes have only addressed setting a default seed, so manually setting your seed should be fine. I tried to reproduce your results with a different dataset but with the same parameters, and I’m seeing that the two models have the same validation ELBO and latent representation. import numpy as np import scvi scvi.settings.seed = 9627 adata = scvi.data.heart_cell_atlas_subsampled(save_path="./data") early_stopping_kwargs = { "early_stopping": True, "early_stopping_monitor": "elbo_validation", "early_stopping_patience": 10, "early_stopping_min_delta": 0.001, } plan_kwargs = { "reduce_lr_on_plateau": False, "lr_patience": 10, 'lr': 0.0011 } model_kwargs = { "use_layer_norm": …

**Reply (@inofechm)**: Hi, I ran into a similar issue and found that if the scvi.settings.seed = 9627 line is at the start of a script then I get different outputs but if I set scvi.settings.seed = 9627 right before model = scvi.model.SCVI(adata) then it replicates.

**Reply (@cane11)**: Can you share your full notebook or code? I don’t think this is not a problem with recent versions of scVI-tools. The problem described above was Jax specific and is fixed in our main branch. I guess, what might happen here: You import another package that resets the seed or part of it (like numpy seed).In your case it’s safe to just set the seed before running train.

## SCANVI: Label transfer from in vivo reference to in vitro model?
**Topic:** 412 | **Last activity:** 2024-09-15T12:22:14Z
**Posts:** 5 | **Views:** 818 | **Created:** 2022-04-19 | **URL:** https://discourse.scverse.org/t/scanvi-label-transfer-from-in-vivo-reference-to-in-vitro-model/412

**Question**: I’m wondering if anyone has had success in predicting cell type labels from an in vivo reference dataset to an in vitro model of that system, which in theory should contain a subset of the cell types found in the reference, albeit with some non-trivial transcriptomic profile differences. I’ve tried this a few times, but I have never seen the two datasets integrate, and my query (in vitro) cells always remain labelled as ‘Unknown’. In this example, rep1 and rep2 are two in vitro experiments, while D59_fetal is the reference, and all cells in the reference are labelled going in. All cells in rep1 and rep2 were Unknown going in. CleanShot 2022-04-19 at 14.31.55@2x 1518×476 67.4 KB

**Reply (@adamgayoso)**: can you add your code so that we can see how you ran the model?

**Reply (@Valentine_Svensson)**: It may simply be that your in vitro data is too different from the primary in vivo data for the cells to match up. In vitro models of human organs can be quite distinct from eachother except for a few key pathways. Imagine if you’d try to transfer labels from PBMCs to the (I assume) retinal cells here. The cells would be too different from each other and won’t match up. My recommendation would be to look at expression of classical markers for retinal ganglion cells and photo receptors with the .get_normalized_expression() method on your fitted model. If you find that the expression levels of those few genes line up between the in vitro cells and the in vivo cells, you can learn why the model thinks the cells are different by selecting an expression threshold on e.g. SNCG for RGCs to define …

**Reply (@yojetsharma)**: Your reasoning actually goes against the well-established foundations of in-vitro modeling using stem cells. Many labs have shown concordance even at transcriptome and chromatin level. Additionally, I am just curious about your statement: “Imagine if you’d try to transfer labels from PBMCs to the (I assume) retinal cells here.” Why would anyone be interested in transferring labels from a one germ layer to another?

**Reply (@yojetsharma)**: Since you posted this, have you had any luck with your analyses? I am trying to do the same but end up with same issue. I read someone state that it could be because of the non-matching categorical labels in the query.

## [Usage clarification] Should the .obs in query and reference be exactly the same?
**Topic:** 2515 | **Last activity:** 2024-09-13T20:43:01Z
**Posts:** 3 | **Views:** 125 | **Created:** 2024-09-13 | **URL:** https://discourse.scverse.org/t/usage-clarification-should-the-obs-in-query-and-reference-be-exactly-the-same/2515

**Question**: I have a query (iPSC derived precursors snRNA, merged from 1-healthy and 2-patients) and a reference (human brain scRNA dataset). Query dataset contains ‘sample’ and ‘leiden’ and reference contains ‘sample’ and ‘cell_type’. I rename the Leiden column in the query to cell_type to match the reference. Following gene intersection and concantation, I have run the SCVI tutorial with default parameters. However, my query never overlaps with reference. So, is it because the ‘leiden’ or cell_types labels in my query (which are essentially cluster numbers) and reference are different?

**Reply (@cane11)**: In scVI the content of these columns doesn’t matter (for scANVI it will seperate based on the cell-type column). However, you use two different celltypes iPSC and brain and two different technologies scRNA/snRNA. The second one is already hard to integrate and the first one also sounds like strong differences in gene expression. If you really want to integrate both datasets something like Seurat rPCA/CCA integration might be more effective.

**Reply (@yojetsharma)**: In the manuscript from Truetlin and Theis lab I came across the following in their methods section: We compared the data integration performance across the following latent representations of the data: unintegrated PCA, RSS(default parameters except for using 2 layers, latent space of size 30 and negative binomial likelihood) integration, scANVI(default parameters) integrations using either snapseed level 1, 2 or 3 annotation as cell type label input, scPoli(parameters shown above) integrations using either snapseed level 1, 2 or 3 annotation or all three annotation levels at once as cell type label input, scPoli36 integrations of meta-cells aggregated with the aggrecell algorithm (first employed as “pseudocell” using either snapseed level 1 or 3 annotation as cell type label input to scPo …

## How is the scArches scvi/scanvi pipeline different from the one on SCVI tutorials?
**Topic:** 2516 | **Last activity:** 2024-09-13T19:42:19Z
**Posts:** 1 | **Views:** 235 | **Created:** 2024-09-13 | **URL:** https://discourse.scverse.org/t/how-is-the-scarches-scvi-scanvi-pipeline-different-from-the-one-on-scvi-tutorials/2516

**Question**: Since scArches makes use of SCVI and scanvi in their tutorials for mapping, I was wondering why not just direct us to SCVI tutorial? How are the two different?

## Weird UMAP after running scVI
**Topic:** 2433 | **Last activity:** 2024-09-12T18:37:08Z
**Posts:** 7 | **Views:** 556 | **Created:** 2024-08-07 | **URL:** https://discourse.scverse.org/t/weird-umap-after-running-scvi/2433

**Question**: Hello, there! Thank you for developing such a great tool. I’m analyzing my single cell RNA sequencing dataset (about 2,000K cells) using scanpy and scVI. After running scVI and plotting UMAP, my plot seems so weird. The code I run is as below: adata = ad.concat([adata_dict[key] for key in adata_dict.keys()], merge = "same") # subsampling to reduce computing time sc.pp.subsample(adata, n_obs = 100000, random_state = 42) # preprocessing sc.pp.filter_cells(adata, min_counts = 1000) sc.pp.filter_cells(adata, min_genes = 10) adata.layers["counts"] = adata.X.copy() sc.pp.normalize_total(adata, exclude_highly_expressed = True, target_sum = 1e6) sc.pp.log1p(adata) adata.raw = adata.copy() # selecting HVGs and running scVI sc.pp.highly_variable_genes(adata, n_top_genes = 3000, layer = "counts", fla …

**Reply (@cane11)**: Hi, can you check how many counts the cells contain after highly_variable_gene selection. It might be a problem with UMAP (small outlier cells that are hard to see. Can you add plots for the 20 latent dimensions or a 2D PCA plot of your latent dimensions.

**Reply (@to-be-so-lonely)**: Thank you for your reply. I’m not sure what you mean by the number of counts the cells contain after the “HVG selection”: np.max(adata.obs["n_counts"]) 192466.0 np.min(adata.obs["n_counts"]) 1000.0 Though I didn’t perform QC for this dataset, I removed cells whose total counts were bigger than 99th percentile of the n_counts or n_genes or smaller than 1st percentile when preprocessing the original dataset (this dataset was downsampled to 1000K cells). I’m not sure I got your purpose…

**Reply (@cane11)**: The PCA looks fine, which was my expectation. The model has captured variations in your data. UMAPs can look wildly off if there are disconnected graphs in the neighborhood graph. This is a problem with UMAP. You can increase the number of neighbors for UMAP which usually helps with those wrong UMAP displays.

**Reply (@christophechu)**: set the number of pcs to 20 using n_pcs=20 when you are running sc.pp.neighbors.

**Reply (@cane11)**: I’m confused. You don’t need to set n_pcs when using scVI embeddings but should run it on all latent dimensions (see our tutorials).

**Reply (@christophechu)**: You are right. In this case, n_lanent =20.

## What to do when the query dataset has different genes from the reference?
**Topic:** 2483 | **Last activity:** 2024-09-04T07:39:07Z
**Posts:** 5 | **Views:** 282 | **Created:** 2024-08-29 | **URL:** https://discourse.scverse.org/t/what-to-do-when-the-query-dataset-has-different-genes-from-the-reference/2483

**Question**: Hello everyone! I’m new here (and relatively new to the world of scRNA data analysis). I recently generated a scRNA dataset for my phd project and have been trying my best to use scanpy and scanVI to analyze it. I was wondering if I could get some help with this. Here’s some info which is relevant: My query dataset is generated from a transgenic mouse embryo E11.5 which have been FACSed for mCherry expression. It’s a mix of cell types which I only vaguely know the composition to. Additionally, there are 30 artificial genes which I’ve inserted into the genome (they don’t exist in the WT transcriptome). ~15,000 cells. The reference dataset is from the Ontogeny of Mouse, Graphed ( https://omg.gs.washington.edu/ ). I’ve filtered for cells from E11.25, E11.5 and E11.75 embryos. ~500,000 cells. …

**Reply (@cane11)**: Hi, I have some preference to recommend removing the genes if you don’t need them in a joint model (predict expression of those in the full atlas or similar - which I wouldn’t really recommend) and use it afterward with the annotated cells/latent spaces. If the expression of these genes is low, it likely is fine to pad with zeros. I assume you do highly variable gene selection on both datasets, when first concatenating. This can have drastic effects. Indeed, I would expect otherwise both embeddings to be comparable (mind though UMAP tends to exaggerate differences between two runs). This is a lot of celltypes and scANVI is not tested with this amount of celltypes. I would doubt that label transfer is accurate for all cell-types and expect major manual clean-up to be necessary (could you sp …

**Reply (@joshuak94)**: Hi Can, thanks for the detailed response! You’re correct, I don’t need to predict the expression of those genes or anything, so I’ll remove them from the joint dataset and then add them in after the predictions. Yes to the HVG selection after concatenation. My current “workflow” is as follows: Concatenate datasets, normalize/log transform, HVG selection, train SCVI on unnormalized data (saved in layer “counts”), train SCANVI on SCVI model (I’ve tried varying numbers of n_sampels_per_label here) predict on the “Unknown” cell types. Additionally, I’ve tried removing cells belonging to certain celltypes before step 4. Specifically, I removed all cells and celltypes which have fewer than 100 cells which was probably 1/3 of the total # of cell types. Do you think this is a reasonable filtration …

**Reply (@joshuak94)**: Some updates in the last few days: I’ve tested the resulting model (trained with n_samples_per_label = 1000) on a dataset of mouse embryonic limbs and it seems to perform quite well. However, I’m uncertain as to how to perform some downstream analyses with my artificial genes of interest. Since they were removed prior to training, I can’t use SCANVI’s built in differential_expression function. Is there a way around this? Or should I just revert to scanpy’s rank_genes_groups function on log-normalized counts?

**Reply (@cane11)**: I would do rank_genes_groups or pseudobulk DE (better practice if you have several replicates) for downstream analysis.

## Autotune on custom model class
**Topic:** 2484 | **Last activity:** 2024-08-30T00:00:42Z
**Posts:** 5 | **Views:** 260 | **Created:** 2024-08-29 | **URL:** https://discourse.scverse.org/t/autotune-on-custom-model-class/2484

**Question**: Hi there, I am trying to use the scvi.autotune module on a custom model class based on BaseModelClass . I’ve followed the tutorial and I am able to use the TunableMixin to customize the set of tunable parameters, but not for exposing additional metrics. Can I use the mixin to expose more metrics? I would like to use other metrics reported in the training history for tuning (e.g. elbo_validation ). Thanks in advance!

**Reply (@cane11)**: Hi, can you please use the current main? I inherited it from Martin and this seems more straightforward to me. Is it a metric that is anyhow tracked by your model (I assume so as you mention the model history) or do you want to have a custom callback to track another metric. First one is easy by passing in a list of metrics to run_autotune in scvi-tools/src/scvi/autotune/_tune.py at main · scverse/scvi-tools · GitHub

**Reply (@cane11)**: An example for the second one, you can find at: Comparing main...metrics · scverse/scvi-tools · GitHub (it is pretty involved to set it up), so if you think it’s of general use, we can provide some help to set up a new Callback.

**Reply (@emdann)**: Thank you @cane11 for the quick reply! I switched to the implementation in main and that does exactly what I need, to use another regularly tracked metric). I also agree that this implementation looks more straightforward than the one in the tutorial.

**Reply (@cane11)**: Great and thanks for the feedback. Release will be in the next weeks.

## Doublet removal: solo model train error
**Topic:** 2473 | **Last activity:** 2024-08-29T06:22:50Z
**Posts:** 14 | **Views:** 397 | **Created:** 2024-08-26 | **URL:** https://discourse.scverse.org/t/doublet-removal-solo-model-train-error/2473

**Question**: Hi, I am performing doublet removal using scvi-tools. The following code is working on my other dataset. However, in an alternate concatenated dataset, it fails. How to overcome this problem? I checked there is no NaN values in my input dataset. sc.pp.filter_genes(doublet_adata, min_cells = 10) sc.pp.highly_variable_genes(doublet_adata, n_top_genes = 2000, subset = True, flavor = 'seurat_v3') filtered out 20160 genes that are detected in less than 10 cells extracting highly variable genes → added ‘highly_variable’, boolean vector (adata.var) ‘highly_variable_rank’, float vector (adata.var) ‘means’, float vector (adata.var) ‘variances’, float vector (adata.var) ‘variances_norm’, float vector (adata.var) doublet_adata AnnData object with n_obs × n_vars = 216049 × 2000 obs: ‘sample_id’, ‘diag …

**Reply (@cane11)**: Hi, you might want to check out our FAQ for none errors. It’s pretty unusual in SOLO in my experience. I would check that the AnnData contain count data (not normalized), filter out cells with less than 100 cells after hvg filtering. I would otherwise suggest to reduce the learning rate in SOLO to 1e-4. I would suggest to use a batch_key and restrict SOLO to single batches.

**Reply (@TRakesh0121)**: Thanks @cane11 . I checked FAQs. It’s a public dataset. As suggested I tried all the options but error appearing in concatenated data. Therefore, I tried running on each sample. BY “filter out cells with less than 100 cells after hvg filtering” do you mean => “filter out cells with less than 100 genes”? Because, with that understanding, I started processing one sample at a time, and it’s working. doublet_adata AnnData object with n_obs × n_vars = 61980 × 40316 obs: ‘sample_id’, ‘diagnosis’, ‘tissue_location’, ‘Glioma_grade’ var: ‘gene_ids’ sc.pp.filter_genes(doublet_adata, min_cells = 100) sc.pp.highly_variable_genes(doublet_adata, n_top_genes = 3000, subset = True, flavor = 'seurat_v3') sc.pp.filter_cells(doublet_adata, min_genes=100) filtered out 25638 genes that are detected in less tha …

**Reply (@cane11)**: I would recommend using the restrict_to_batch argument in from_scvi_model and setting up scVI with a batch key (train a single scVI model across all batches and SOLO per batch). This way the selection is more similar across batches. You might be able to reduce the min_counts filtering to keep more cells. For standard 10X data, I usually find a steep drop in quality with counts before gene filtering below 1000 counts.

**Reply (@ddiez)**: Although I do not know about the details, I just saw this in the output of the first step ( sc.pp.filter_genes ). I think this is a very large number of genes removed. How many are left? Might this be the source of the problem? TRakesh0121: filtered out 25638 genes that are detected in less than 100 cells

**Reply (@cane11)**: I assume the reason for both is the same (low reads per cell), which could be either low read depth in 10X or another technology with less efficient capture. Filtering cells will help to make it more stable (likely cells with 30 counts after hvg selection will work).

**Reply (@TRakesh0121)**: Hi @cane11 , I tried the following code, but ‘restrict_to_batch’ is giving error. scvi.model.SCVI.setup_anndata(doublet_adata, batch_key="sample_id") vae = scvi.model.SCVI(doublet_adata) vae.train(batch_size=130) solo = scvi.external.SOLO.from_scvi_model(vae, restrict_to_batch="SCPCL000001" ) solo.train(batch_size=130)

**Reply (@TRakesh0121)**: Hi @ddiez It’s a public dataset, removing NaN from the dataset leaves ~40,000 genes. After filter genes that are detected in less than 100 cells, ~15000 were there. Thanks

**Reply (@cane11)**: Please add the error message.

**Reply (@TRakesh0121)**: TRakesh0121: restrict_to_batch="SCPCL000001" @cane11 Sorry, I forgot to attach the error. Here is the command and error. I am using the ‘batch_key’ & ‘restrict_to_batch’ option for the first time, that’s no idea what exactly this error means. sc.pp.filter_genes(doublet_adata, min_cells = 10) sc.pp.highly_variable_genes(doublet_adata, n_top_genes = 2000, subset = True, flavor = 'seurat_v3') scvi.model.SCVI.setup_anndata(doublet_adata, batch_key="sample_id") vae = scvi.model.SCVI(doublet_adata) vae.train(batch_size=130) solo = scvi.external.SOLO.from_scvi_model(vae,restrict_to_batch="SCPCL000001") solo.train(batch_size=130) Screenshot 2024-08-27 at 1.28.55 PM 1972×1427 447 KB Thanks

**Reply (@cane11)**: TRakesh0121: scvi.model.SCVI.setup_anndata(doublet_adata, batch_key="sample_id") It is registered with a single batch. You should input the full data (without subsetting to a single batch) to scVI. SOLO then simulates doublets for a single batch and provides results for this single batch.

**Reply (@TRakesh0121)**: Hi @cane11 , Thanks. Still it’s not working. adata_file_name_combined_adata = sc.concat([adata_file_name_1, adata_file_name_2], merge='same') adata_file_name_combined_adata AnnData object with n_obs × n_vars = 216049 × 40316 obs: ‘sample_id’, ‘diagnosis’, ‘tissue_location’, ‘Glioma_grade’ var: ‘gene_ids’ doublet_adata = adata_file_name_combined_adata.copy() sc.pp.filter_genes(doublet_adata, min_cells = 10) sc.pp.highly_variable_genes(doublet_adata, n_top_genes = 2000, subset = True, flavor = 'seurat_v3') filtered out 20160 genes that are detected in less than 10 cells extracting highly variable genes → added ‘highly_variable’, boolean vector (adata.var) ‘highly_variable_rank’, float vector (adata.var) ‘means’, float vector (adata.var) ‘variances’, float vector (adata.var) ‘variances_norm’, …

**Reply (@cane11)**: Now combine both (first advice). You still need to filter out cells with only a few counts. You can set min_counts to 100. If you have some knowledge of celltypes you can also check what the minimum counts per cell is that clusters by celltype and not by low counts.

**Reply (@TRakesh0121)**: Thanks, it finally worked!!

## Understanding `differential_expression()` and lvm-DE
**Topic:** 2481 | **Last activity:** 2024-08-28T20:50:40Z
**Posts:** 4 | **Views:** 284 | **Created:** 2024-08-28 | **URL:** https://discourse.scverse.org/t/understanding-differential-expression-and-lvm-de/2481

**Question**: I are interested in looking code behind the differential_expression() function, in particular the lvm-DE method. From an issue in scVI-tools Github , it seems as though the lvm-DE method is now a part of the general differential_expression() function in ‘scVI-tools’ (when using weights=“importance”). Exploring scVI-tools , it seems like the differential_expression() function code is tied to _de_core.py and _differential.py (same folder as _de_core.py; can’t add a third link). However, I can’t find the “weights” flag in either script (or a conditional looking for the word “importance”), which makes me think I’m looking in the wrong spot. Any help to direct me would be most appreciated.

**Reply (@cane11)**: Hi, lvmDE is active when using mode=‘change’ (the default), while the old method requires mode=‘vanilla’. Weights=‘importance’ changes the manner samples are taken in get_normalized_expression .

**Reply (@emucaki)**: Thanks for your reply. I had a hard time understanding what combination of settings constituted the lvm-DE method. The guide really didn’t go over that. de_results = model.differential_expression( groupby="subtype", idx1=group1, idx2=group2, weights="importance", batch_correction=False, delta=None, fdr_target=0.01 ) Can you help me understand where “differential_expression()” and “get_normalized_expression()” interact? Adding “weights=importance” to “differential_expression” clearly makes a big impact on the results, but I can’t seem to figure out how adding the “weights” flag to the former function calls the latter.

**Reply (@cane11)**: scvi-tools/scvi/model/base/_rnamixin.py at d094c9b3c14e8cb3ac3a309b9cf0160aff237393 · scverse/scvi-tools · GitHub defines a partial function of get_normalized_expression.

## Pre-defined validation data
**Topic:** 2478 | **Last activity:** 2024-08-27T00:48:11Z
**Posts:** 2 | **Views:** 90 | **Created:** 2024-08-27 | **URL:** https://discourse.scverse.org/t/pre-defined-validation-data/2478

**Question**: I am training multiple models and have pre-existing h5ad files corresponding to train/test/validation datasets that are fixed across the models. Is there a way to manually set the train and validation anndata objects when training an scvi.model.SCVI model? I see that there is a setter for validation_indices , is the best way to just concatenate the two anndata objects and then manually set validation_indices ? My idea solution would look something like this: model = scvi.model.SCVI(train_adata, val_adata, n_layers=n_layers, n_latent=n_latent, n_hidden=n_hidden, gene_likelihood="nb") but I’m not sure that this would be a broadly applicable change for other users.

**Reply (@cane11)**: Hi, yes concatenating and setting validation indices is the correct way (only works in the current main branch and will be released for 1.2). ScVI-tools requires a single AnnData object. We are working with other group to lift this restrictions.

## How to compare different parameter sets using the validation loss?
**Topic:** 2017 | **Last activity:** 2024-08-26T17:31:46Z
**Posts:** 7 | **Views:** 1257 | **Created:** 2024-01-23 | **URL:** https://discourse.scverse.org/t/how-to-compare-different-parameter-sets-using-the-validation-loss/2017

**Question**: Hi, I am applying scVI to about 250k cells, and I use “sample” as the batch key to integrate the snRNA-seq data. I tried several different parameter sets and plotted validation losses for each model. But I didn’t know how to interpret the results, after reading the posts here and here . model 1 : n_hidden: 128, n_latent: 30, n_layers: 2, dropout_rate: 0.1, dispersion: gene, gene_likelihood: nb The reconstuction error for this was: -433.33 (from model.get_reconstruction_error(indices=model.validation_indices) ) model 2 : n_hidden: 128, n_latent: 30, n_layers: 1, dropout_rate: 0.1, dispersion: gene, gene_likelihood: zinb The reconstuction error for this was: -428.675 model 3 . I found that some samples did not mix well after scVI. So, I tried to add more covariates including percent.mt, perc …

**Reply (@martinkim0)**: Hey there! Yeah, I would train the model for a couple more epochs to see if the ELBO flattens out more. In general, we’re more interested in the ELBO converging over other metrics such as the reconstruction. It does imply that model 2 is overfitting slightly more, but with that small of a difference, I wouldn’t worry about it too much. It’s only a matter of concern when the validation loss is much larger compared to the training one, and/or the validation loss goes up while training decreases. As always, you should supplement inspecting loss curves with other evaluations such as plotting UMAPs or computing integration metrics. I would plot model 3’s curves on the same y-scale as the other models, and I think you’ll find that it looks similar or worse to the other models. Particularly, the …

**Reply (@niuyw)**: Hey Martin, Thank you very much for the explanations! It helps a lot. For model 1, I increased the epoches to 100 and below is the training curve. image 588×580 33 KB So, even at 100 epoch the ELBO didn’t converge, should I increase the epoch further? I mean, the default max epoch is only 33. Also, the reconstruction loss goes up after 50 epoches. The difference between model 3 and model 1/2 is that I added more covariates to correct for, and you mentioned that the training is not stable. I was wondering what I should do to make it better if I want to use this model. Bests, Yiwei

**Reply (@niuyw)**: Hey, I tried early_stoping=True and checked the traing curves. It seems that the ELBO loss became flat after 200 epoches, but reconstruction loss went up after 50 epoches. @martinkim0 I was wondering if I should only focus on the ELBO convergence.

**Reply (@swc)**: Hi Yiwei, I saw the exactly same thing on my dataset, did you find any explanation for this? I saw the other post mentioning: Suggestion on parameters for training scvi model If you find that elbo_validation , validation_loss , and reconstruction_loss_validation are converging at the end of training, then your model is probably fine. Best, swc

**Reply (@niuyw)**: Hi, sorry no. I’m currently using model 2 above with 100 epoches.

**Reply (@cane11)**: I would say it’s the correct choice. It doesn’t matter to much. I wouldn’t take model 3 above as it’s quite spiky. We warm up the kl_loss (it increases over time). In the beginning it’s small and the model puts more effort on the reconstruction loss while the full elbo (kl_weight=1) is optimized latter during training. From VAE literature, the ELBO is the thing you want to optimize. However, for scVI I see very slight differences between slightly different ELBO losses.

## SCVI and SCANVI for label transfer how to assess accuracy?
**Topic:** 2456 | **Last activity:** 2024-08-20T17:25:37Z
**Posts:** 4 | **Views:** 456 | **Created:** 2024-08-18 | **URL:** https://discourse.scverse.org/t/scvi-and-scanvi-for-label-transfer-how-to-assess-accuracy/2456

**Question**: Hello, I followed this tutorial sanbomics_scripts/scvi_label_transfer.ipynb at main · mousepixels/sanbomics_scripts · GitHub where it first concatenated the sample(s) of unknown labels with the reference. Now ref and my samples have different batches then I trained vae=scvi.model.SCVI(adata) without any extra arguments and it ran for 6 epoch only ( data is about 1.4 million) so I wonder if 6 epoch is a good number and how to assess that the model is accurate?? then lvae = scvi.model.SCANVI.from_scvi_model(vae, adata = adata, unlabeled_category = ‘Unknown’, labels_key = ‘cell_ontology_class’) lvae.train(max_epochs=20, n_samples_per_label=100) was done to predict the labels of my samples which have unknown. I want to ask what does the n_samples_per_label mean ? what I understand is that it t …

**Reply (@cane11)**: I tend to train for at least 20 epochs. However, this is more an experience based thing. You should check elbo_validation and elbo_train afterwards. You can increase batch_size to 1024 (increases runtime by a factor of 8). Yes it takes 1000 representative cells for each celltype (or if there are less than 100 cells of a celltype all cells of this type). The classifier doesn’t have balanced weights and this helps with balancing.

**Reply (@Flu09)**: Thank you. strangely I do not have elbo_validation. May be I need to add another argument? vae.history.keys() dict_keys([‘kl_weight’, ‘train_loss_step’, ‘train_loss_epoch’, ‘elbo_train’, ‘reconstruction_loss_train’, ‘kl_local_train’, ‘kl_global_train’]) vae SCVI model with the following parameters: n_hidden: 128, n_latent: 10, n_layers: 1, dropout_rate: 0.1, dispersion: gene, gene_likelihood: zinb, latent_distribution: normal. Training status: Trained Model’s adata is minified?: False lvae.history.keys() dict_keys([‘train_loss_step’, ‘train_loss_epoch’, ‘elbo_train’, ‘reconstruction_loss_train’, ‘kl_local_train’, ‘kl_global_train’, ‘train_classification_loss’, ‘train_accuracy’, ‘train_f1_score’, ‘train_calibration_error’]) lvae ScanVI Model with the following params: unlabeled_category: Un …

**Reply (@cane11)**: Can you add check_val_every_n_epoch=1 to train? This enables tracking validation losses.

## Error when using scVI.model.train
**Topic:** 2423 | **Last activity:** 2024-08-19T12:34:53Z
**Posts:** 3 | **Views:** 254 | **Created:** 2024-07-31 | **URL:** https://discourse.scverse.org/t/error-when-using-scvi-model-train/2423

**Question**: Hi there, I am trying to integrate my data using scVI. I have tuned the model hyperparameters with ray. I am subsetting my object to highly variable genes Here is the code: # set up the adata object scvi.model.SCVI.setup_anndata(adata_scvi, layer = 'counts', batch_key = "patient.seqbatch" ) # set up the scVI model # specify the parameters according to the ray optimisation vae = scvi.model.SCVI(adata_scvi, n_latent = 30, n_hidden = 60, n_layers = 1, dropout_rate = 0.1, dispersion = 'gene-batch', gene_likelihood='zinb') # add the parameter for lr kwargs = {'lr': 0.0023} # calculate the number of epochs needed which varies according to the cell number max_epochs_scvi = np.min([round((20000 / adata_ref.n_obs) * 400), 400]) max_epochs_scvi # run the training (need the GPU queue here) vae.train( …

**Reply (@cane11)**: Hi, you have to cast max_epochs_scVI to integer.

**Reply (@ccohen)**: Many thanks, a quick fix!

## Scvi - denoising single-cell/single-nucleus transcription data
**Topic:** 2365 | **Last activity:** 2024-08-08T04:05:43Z
**Posts:** 4 | **Views:** 451 | **Created:** 2024-07-02 | **URL:** https://discourse.scverse.org/t/scvi-denoising-single-cell-single-nucleus-transcription-data/2365

**Question**: Hello, Thank you for the wonderful tool and efforts in maintaining this community. We have been very interested in working with denoised single-cell/single-nucleus transcription vectors. Specifically, we are very interested in obtaining the batch-corrected “count” vectors after denoising. We have been using the scVI tool and found the following: For our project, we have been using scVI to run the raw counts from a cohort with about 12 separately-sequenced individuals (treated as batches). In addition, we included all the genes (rather than just the highly variable genes) because we want as many genes as possible for downstream analysis. We found that the latent space was very well batch-corrected , but the denoised vectors still showed batch-specific clustering . Is there something we shou …

**Reply (@cane11)**: Hi, what do you hope another tool to do? I can then link to other tools within scVI for this purpose. The normalized expression is by default not batch corrected but only when you provide transform_batch the generated counts will be projected to this batch leading to corrected gene expression

**Reply (@suchzheng2)**: Thank you for your response! I’m using the Splatter simulated dataset with 10 batches with dropout and aiming to remove batch effects to obtain corrected/denoised read counts. While the scVI model shows a good removal of batch effects in the latent space UMAP, which reflects in meaningful clustering potentially indicative of cell types, the results diverge when examining the denoised read counts obtained via get_normalized_expression() . Here’s the situation: Using get_normalized_expression() : I’ve experimented with the parameters library_size , n_samples , and transform_batch . When I set transform_batch , only the integer 0 is accepted without errors. Other inputs, like real batch names or other integers, return errors like: ValueError: “1” not a valid batch category. ValueError: “Batch …

**Reply (@cane11)**: Maybe you first explain why you are doing that. Splatter contains no gene-gene dependencies (except they have a new simulation) but all genes are sampled independently. This is bad for all embedding methods that try to cover gene-gene dependencies and especially for the generative models. UMAP then strongly manipulates these embeddings and you end up with spaghettis or distinct clusters. Just use real data or more advanced simulations e.g. scDesign?

## scVI integration set batch_key and poor Umap result
**Topic:** 2435 | **Last activity:** 2024-08-07T18:25:58Z
**Posts:** 4 | **Views:** 400 | **Created:** 2024-08-07 | **URL:** https://discourse.scverse.org/t/scvi-integration-set-batch-key-and-poor-umap-result/2435

**Question**: I have a large dataset downloaded from GEO with inherent structural complexities. When integrating data using the scVI model for batch effect correction and conducting DEG analysis on Cancer vs. Normal samples, I need guidance on how to properly set up Anndata and configure the batch_key and categorical_covariate_key . Currently, I have set batch_key as ‘sample’ and categorical_covariate_keys as ‘study_origin’ and ‘sequencing_method’. The hierarchy of my data is as follows: 12 samples (including Control and Cancer) < 3 sequencing methods < 4 studies from GEO. Despite these current settings, my UMAP clustering shows poor integration for one cancer sample, with barely any other samples mapping to the same area. Could you help me troubleshoot this issue?

**Reply (@cane11)**: Hi, it is very helpful to provide more information especially including plots and code that you used. To provide some ideas what to look for: Are the other samples/studies well integrated? Is this specific study very different from the other ones (like different sequencing technology or similar drastic differences)? It can help to define a batch_key (here study_id), when identifying highly variable genes in Scanpy and to reduce the number of genes. Have you tried especially harmony and was it giving the correct integration? You can the. use scANVI and provide labels_key that correspond to the good integration.

**Reply (@holjol)**: cane11: me ideas what to look for: Are the other samples/studies well integrated? Is this specific study very different from the other ones (like different sequencing technology or similar drastic differences)? It can help to define a batch_key (here study_id), when identifying highly variable genes in Scanpy and to reduce the number of genes. Have you tried especially harmony and was it giving the correct integration? You can the. use scANVI and provide labels_key that correspond to the good integration Hi, thanks for the reply. Here are more details about my problem: Below is the code I used. This is the head of my adata object: ||sample|doublet|n_genes_by_counts|total_counts|total_counts_mt|pct_counts_mt|total_counts_ribo|pct_counts_ribo|Study|SequencingMethod| |---|---|---|---|---|---| …

**Reply (@cane11)**: It looks good in my oppinion. I would perform clustering and look at DE genes and see whether it lines up with any biological signal like e.g. proliferation of cell stress or assay. I would recommend subsetting to highly variable genes (not included in your code).

## Is the output of `get_normalized_expression` batch-corrected or not?
**Topic:** 2427 | **Last activity:** 2024-08-05T14:42:21Z
**Posts:** 3 | **Views:** 521 | **Created:** 2024-08-01 | **URL:** https://discourse.scverse.org/t/is-the-output-of-get-normalized-expression-batch-corrected-or-not/2427

**Question**: Hello! First things first, thank you for this awesome tool. I know this question is similar to previous questions on this forum, but that’s part of the confusion I’m running into. Some background. I have scRNA-seq data from several independent experiments (which I’ll refer to as batches) that I am hoping to pool together/integrate and use for eQTL mapping. I am hoping to use scvi to integrate these data together and correct for the batch effects that come from pooling multiple independent experiments. I used scvi.model.SCVI.setup_anndata with batch_key="experiment" (that’s the categorical variable that encodes the scRNA-seq experiment), and I’ve trained an scvi model using that anndata object. Now my question is this: is the output of model.get_normalized_expression() expected to be batch- …

**Reply (@cane11)**: The output is not batch corrected. See the other post. I highly suggest against using get_normalized_counts for eQTL mapping. ScVI learns gene-gene dependencies. This will lead to trans-eQTL that are not backed by data. This is such a sensitive field that you should use best practice for sc-eQTL mapping and not apply less well validated approach (like scVI to normalize counts). You can still use the latent space to identify cell-types or similar cells across samples.

**Reply (@dtaylo95)**: Thanks so much for the response, this is very helpful. I’ll stick to using the scVI output for cell-type ID, and relying on the raw data for downstream.

## Benchmarking with scib-metrics: Graph Connectivity as a batch correction metric
**Topic:** 2387 | **Last activity:** 2024-07-25T05:29:18Z
**Posts:** 6 | **Views:** 434 | **Created:** 2024-07-15 | **URL:** https://discourse.scverse.org/t/benchmarking-with-scib-metrics-graph-connectivity-as-a-batch-correction-metric/2387

**Question**: Hello! I was wondering why graph connectivity is grouped as a batch correction metric in scib-metrics? From my understanding of the ( reference ) it seems to be measuring if cells of the same cell type are connected in the kNN graph - which sounds like a bioconservation metric? Any insight would be appreciated! Thanks,

**Reply (@cane11)**: Hello, the scvi-tools tag seems confusing here. It measures how well connected cells of a specific type are. If batch correction fails, then you get seperated graphs for the same cell-type. To get a better intuition, batch correction metrics (like graph connectivity) improve if you would use as embedding of the full dataset a single point.

**Reply (@andrewdchen)**: Ah yes didn’t know what tag to throw it under. I guess to me that still sounds like a bioconservation metric (i.e. how well a given cell type is embedded within neighbors of the same cell type). Perhaps there are separate graphs for a single cell type, but within those separate graphs the ‘batch label’ is fully mixed, then one would say that in terms of ‘batch correction’ alone the method did its job well. Hope that makes sense!

**Reply (@cane11)**: Again this metric would be optimized by setting a single point as the embedding. It doesn’t measure bioconservation therefore (as this is the worst embedding for cell-type conservation). It computes a subgraph per cell-type and therefore has no notion of cell-type distances. See scib.metrics.graph_connectivity — scib 1.1.4 documentation for a good description.

**Reply (@andrewdchen)**: Sorry to belabor the point, but the above documentation says subgraph connectivity is quantified per cell type. Wouldn’t a single point be the best embedding (from a bioconservation point of view) for a given cell type? I.e. all data points belonging to a given cell type are given the same embedding.

**Reply (@cane11)**: Bioconservation checks for between cell-type distances (how well seperated are cell-types). As the graph is only built for a single cell-type it doesn’t measure whether different cell-types are separated. Therefore you can easily maximize this metric while minimizing bioconservation (all cell-types embedded to a single point).

## AdversarialTrainingPlan in _trainingplans.py
**Topic:** 2410 | **Last activity:** 2024-07-23T19:50:42Z
**Posts:** 2 | **Views:** 68 | **Created:** 2024-07-23 | **URL:** https://discourse.scverse.org/t/adversarialtrainingplan-in-trainingplans-py/2410

**Question**: There are two optimizers in the training_step function, are they optimized every batch or every epoch?

**Reply (@cane11)**: training_step is the function called for every batch to compute the training step. So both optimizers are updated for every minibatch.

## Different UMAPs for same dataset with scANVI
**Topic:** 2400 | **Last activity:** 2024-07-22T18:47:41Z
**Posts:** 7 | **Views:** 580 | **Created:** 2024-07-20 | **URL:** https://discourse.scverse.org/t/different-umaps-for-same-dataset-with-scanvi/2400

**Question**: I am using scVI and scANVI to integrate datasets of two species. I am noticing that there is a very big difference in species integration on the UMAP depending on whether scANVI creates a new model or if it imports in an existing scVI model (see code below). I have confirmed that the environment is the same and that the random seed is set to the same number in both scripts. The data is identical and adata_subset is created with the same subset of highly variable genes. Here is the code for if I am generating an scVI model first and then passing it to the scANVI model: scvi.model.SCVI.setup_anndata(adata_subset, batch_key = “10x_batch”, layer = “raw”, labels_key = ‘cell_type’) model = scvi.model.SCVI(adata_subset, dispersion = ‘gene-batch’) model.train() lvae = scvi.model.SCANVI.from_scvi_m …

**Reply (@cane11)**: It is expected that both codes yield different results. We highly recommend training scVI first and then training scANVI. Training a classifier on a bad embedding can have unwanted side effects. If you think training scANVI only provides better embeddings, I would recommend looking into MrVI with a cell-type bias, which has a slightly different strategy and is better tested in these cases.

**Reply (@danamcc)**: Can you explain why they would yield different results? I thought that scANVI was an extension from the scVI model, and that the extra time training scANVI when you start without an scVI model first was just wrapping in the scVI training time. Is there anything necessarily wrong with using scANVI without making the scVI model first? We had favorable results with going directly to scANVI. I will look into MrVI too, thank you for the recommendation.

**Reply (@cane11)**: scANVI was built with the idea of pretraining an scVI model first that doesn’t take celltypes into consideration (see our tutorials on how to correctly use scANVI). Directly using scANVI does not train an scVI model (see e.g. Seed labeling with scANVI — scvi-tools for how to correctly use scANVI). Training it directly with a classifier will increase reliance on correct cell-type labels and might have negative side effects (I have observed this several times). In your case relying on labels might be helpful but I would then recommend the MrVI (or scPoli) manner of enforcing cell-type labels.

**Reply (@danamcc)**: Hmm, I see where I was confused. I was looking at the API here and its example showed going directly to scANVI. Is there a scenario where this usage is appropriate, or is the API outdated? Thank you!

**Reply (@cane11)**: This is not a tutorial but a demonstration of the API. Especially, taking into consideration Metric Mirages in Cell Embeddings , I don’t have a good feeling with increasing the effect cell-type labels have on embeddings.

**Reply (@danamcc)**: This is a lot to think about, thank you very much!

## Differences in library sizes between reference and query
**Topic:** 2399 | **Last activity:** 2024-07-22T15:55:41Z
**Posts:** 4 | **Views:** 239 | **Created:** 2024-07-19 | **URL:** https://discourse.scverse.org/t/differences-in-library-sizes-between-reference-and-query/2399

**Question**: Is anyone aware of benchmarks that have tested how large differences in library size (i.e. mean total counts per cell) affect integration with scVI and query mapping with scArches? I am working with an scVI model trained on a reference with significantly lower counts per cell compared to the query (where reference mean total count ~ 1000, query mean total count ~ 5000). After query mapping, I see a relationship between total counts for a cell and similarity to the reference. I’m curious to see if other people have looked at this, before going into doing downsampling experiments, since in my case a bunch of other biological factors are correlated with total counts per cell. From the user guide I get that the scVI model default is to use sum of counts for library size the recent default for …

**Reply (@cane11)**: Hi, it’s usually not a good idea in my hands. Purely for the latent space, it might be fine but I wouldn’t trust downstream methods like get_normalized_counts or differential expression. In general, I would suggest training from scratch and check whether the same structure shows up. It doesn’t necessarily mean that you are interested in this feature and additionally adding total_counts as continuous covariate key might then help.

**Reply (@emdann)**: Hi @cane11 , thanks for the tips. By training from scratch do you mean training an scVI model on concatenated reference and query, instead of using query mapping?

**Reply (@cane11)**: Hi Emma, yes after concatenation or just use the query data if you are not interested in the reference data.

## Integration with multiple categorical variable
**Topic:** 2406 | **Last activity:** 2024-07-22T15:54:41Z
**Posts:** 2 | **Views:** 97 | **Created:** 2024-07-22 | **URL:** https://discourse.scverse.org/t/integration-with-multiple-categorical-variable/2406

**Question**: Hello, I want to try to use scvi.model.SCVI with multiple categorical_covariate_keys. I just wanted to know if there is a sequence in which SCVI operates with the different keys ? Best regards, Lionel Lenoir

**Reply (@cane11)**: Hi, no in short the order doesn’t matter. All values get one hot encoded and every category value gets concatenated to the latent code.

## Function 'sexp_as_cholmod_sparse' not provided by package 'Matrix'
**Topic:** 2380 | **Last activity:** 2024-07-21T14:10:48Z
**Posts:** 5 | **Views:** 687 | **Created:** 2024-07-15 | **URL:** https://discourse.scverse.org/t/function-sexp-as-cholmod-sparse-not-provided-by-package-matrix/2380

**Question**: Hello, I’m integrating datasets with scVI in R, and followed the tutorial ( Integrating datasets with scVI in R — scvi-tools ) The format conversion and model training have been done, but when I runumap, with combined_seurat ← RunUMAP(combined_seurat, dims = 1:10, reduction = “scvi”, n.components = 2) I get the error Error in irlba::irlba(L, nv = n, nu = 0, maxit = iters): function 'sexp_as_cholmod_sparse' not provided by package 'Matrix' . My Matrix version is [1] ‘1.6.1.1’ . Do you know which version of Matrix provides sexp_as_cholmod_sparse ?

**Reply (@cane11)**: Hi. I assume you can also not compute RunUMAP on other dimensionality embeddings. In this case, please check this with Seurat or Matrix developers? We unfortunately can’t provide support beyond making sure that scVI trains correctly in R.

**Reply (@ddiez)**: I remember this problem happening some time ago when Matrix package was updated and some dependent packages, like irlba , needed to be recompiled, as suggested in this thread. So, can you try running? install.packages("irlba", type="source")

**Reply (@xiaoshanji)**: Thank you so much for replying. I’ve solved this problem.

**Reply (@xiaoshanji)**: Thank you so much! I’ve solved this problem by recompiling package irlba.

## MrVI min cells per sample, cross tissue samples
**Topic:** 2394 | **Last activity:** 2024-07-20T07:06:01Z
**Posts:** 2 | **Views:** 130 | **Created:** 2024-07-18 | **URL:** https://discourse.scverse.org/t/mrvi-min-cells-per-sample-cross-tissue-samples/2394

**Question**: Hi! I have some (rather naive) questions about the new MrVI tool. Given that it predicts counterfactual cell states for each cell across samples, is there a recommended minimum number of cells/sample, for a sample to be included in this analysis? Intuitionally, I would think that if a sample has few cells, the algorithm will have a hard time predicting the effect of that sample on any cell. Similarly, if two samples belong to different tissues (cross organ integration), would the algorithm be essentially trying to predict what a cell from tissue A would look like if it belonged to tissue B, which perhaps might not make a lot of biological sense?

**Reply (@cane11)**: Indeed, the algorithm relies on representative cellular states being present and will otherwise not predict reasonable results. We performed cross-tissue analysis in a limited sense within the manuscript (ileum and colon of inflammatory bowel disease) and we performed extensive cross-tissue analysis within https://www.biorxiv.org/content/10.1101/2024.01.03.573877v2.full . Obviously this only makes sense for cell-types that are present in both tissues. To reduce the risk of this, we provide an option to filter samples for counterfactuals that have no similar cells present using the procedure described in the manuscript.

## Multithreading error
**Topic:** 2388 | **Last activity:** 2024-07-16T16:06:17Z
**Posts:** 2 | **Views:** 388 | **Created:** 2024-07-15 | **URL:** https://discourse.scverse.org/t/multithreading-error/2388

**Question**: Hi, I tried to set: scvi.settings.dl_num_workers = 19 and saw the following warning, accompanied by significant reduction in speed: os.fork() was called. os.fork() is incompatible with multithreaded code, and JAX is multithreaded, so this will likely lead to a deadlock. I didn’t see any bugs related to this on scvi github so I am guessing this isn’t a bug with the tool. Does anyone know how to fix it? Is this a pytorch issue? My pyTorch version: 2.3.1+cu121 p.s. I ran into this while running the new version of MrVI, but I assume this is model agnostic. Thanks! Kunal

**Reply (@martinkim0)**: Hi, we don’t recommend setting scvi.settings.dl_num_workers when using JAX models such as MrVI due to the warning that it emits. Dataloading will be a little slower without multiple workers, but in my experience it’s not too bad.

## Error with DefaultAssay in R when Integrating Data Using scvi-tools
**Topic:** 2333 | **Last activity:** 2024-07-16T05:54:45Z
**Posts:** 5 | **Views:** 264 | **Created:** 2024-06-14 | **URL:** https://discourse.scverse.org/t/error-with-defaultassay-in-r-when-integrating-data-using-scvi-tools/2333

**Question**: Hello, I am encountering an issue while trying to integrate data using scvi-tools in R. Here is the code I am using: R latent <- as.matrix(latent) rownames(latent) = colnames(adata) adata[["scvi"]] <- CreateDimReducObject(embeddings = latent, key = "scvi_", assay = DefaultAssay(adata)) However, this results in the following error: Error in UseMethod(generic = “DefaultAssay”, object = object): no applicable method for ‘DefaultAssay’ applied to an object of class “c(‘anndata._core.anndata.AnnData’, ‘python.builtin.object’)” Traceback: CreateDimReducObject(embeddings = latent, key = “scvi_”, assay = DefaultAssay(adata)) DefaultAssay(adata) t seems that the DefaultAssay function is not recognizing the adata object as expected. I have confirmed that adata is an AnnData object. version： r-seurat …

**Reply (@cane11)**: I’m not really an expert for Seurat. However, from the error latent contains an AnnData object and not a matrix. Can you provide the data type of latent?

**Reply (@xiaoshanji)**: Thank you very much for your reply, and I apologize for the delay in getting back to you. You were correct, I checked the format of latent and adata , and the issue was indeed there. The error has been resolved, thank you so much. However, I have encountered a new problem. When running ifnb <- RunUMAP(ifnb, dims = 1:10, reduction = "scvi", n.components = 2) , I get the error Error in irlba::irlba(L, nv = n, nu = 0, maxit = iters): function 'sexp_as_cholmod_sparse' not provided by package 'Matrix' . My Matrix version is [1] ‘1.6.1.1’ . Do you know which version of Matrix provides sexp_as_cholmod_sparse ? Thank you again for your reply!

**Reply (@cane11)**: This is more a question to the Seurat (or matrix) developers and I wouldn’t expect a response her, unfortunately.

**Reply (@xiaoshanji)**: ok, I’ll try to solve it focusing on Seurat and Matrix, thanks a lot!

## Any suggestions for speeding up model training (vae and solo) on M2 mac
**Topic:** 2371 | **Last activity:** 2024-07-08T17:34:29Z
**Posts:** 2 | **Views:** 459 | **Created:** 2024-07-06 | **URL:** https://discourse.scverse.org/t/any-suggestions-for-speeding-up-model-training-vae-and-solo-on-m2-mac/2371

**Question**: Hello scverse! first time asking a question so let me know what I can improve I’ve been trying to train the vae and solo models but using my MPS gpu throws the same error mentioned in this post ( Error when training model on M3 Max MPS ) so I’ve been going cpu only. It is absolutely slow because of the dataset size (700000 x 35000), but I was wondering if you all had any suggestions for things I could do to make sure this is going at the max possible speed. I’ve been running this code scvi.settings.dl_num_workers = 11 scvi.settings.batch_size = 2048 scvi.settings.num_threads = 10 scvi.model.SCVI.setup_anndata(adata) vae = scvi.model.SCVI(adata) vae.train() if it helps, here is the startup output of the code above GPU available: True (mps), used: False TPU available: False, using: 0 TPU cor …

**Reply (@martinkim0)**: I haven’t tried this recently so not sure if it’s stable, but you can install an MPS-supported version of PyTorch and then run use the MPS backend by passing in: vae.train(accelerator="mps")

## Recommendation for transform_batch / categorical_covariate_keys to obtain "batch corrected" counts
**Topic:** 2346 | **Last activity:** 2024-07-03T22:45:02Z
**Posts:** 2 | **Views:** 340 | **Created:** 2024-06-22 | **URL:** https://discourse.scverse.org/t/recommendation-for-transform-batch-categorical-covariate-keys-to-obtain-batch-corrected-counts/2346

**Question**: Hi, Thanks for making this great package! I’m working with a multi-batch dataset with several donors, generated from multiple studies with their own batch effects (technology and varying sequencing depth). I am interested in generating a “batch-corrected” count matrix for downstream analysis. I see that in scvi.model.SCVI.setup_anndata() there are options for categorical_covariate_keys and continuous_covariate_keys . So then I could use the various batch effects like “technology” and “donor” as categorical covariates, for example. I also see that once I build the model, there is a function model.get_normalized_expression, which can take a transform_batch argument, but how should I combine this with the categorical_covariates_keys above? I saw a similar question here but didn’t see a specif …

**Reply (@cane11)**: Hi, to use transform_batch you have to use batch_key instead of categorical_covariate_key. You can provide a list of batches and the output is the average over these batches (so.e.g. All samples for a specific technology).

## New scvi-tools version using SOLO returns probabilities, how to return logits like in version 1.1.2
**Topic:** 2360 | **Last activity:** 2024-07-02T15:31:32Z
**Posts:** 8 | **Views:** 301 | **Created:** 2024-06-30 | **URL:** https://discourse.scverse.org/t/new-scvi-tools-version-using-solo-returns-probabilities-how-to-return-logits-like-in-version-1-1-2/2360

**Question**: Noticed a new warning while predicting doublets with SOLO that it returns probabilities instead of logits, how does one convert back or return the logit values like in previous versions? I have tried using the expit function and logit function to convert but have been unable to recreate data I analyzed in the past.

**Reply (@ddiez)**: Not sure if this is the way but have you tried following like here and calculating logit = ln(p/(1-p)) where p are the probabilities?

**Reply (@scuser)**: Hi, I did try that, but it did not work as expected. After playing around with it a bit I believe the issue is that the “logits” mentioned in the update are not logits formed from the logit function you link but they are transformed into probabilities using the softmax function. I’m unsure if the softmax function is invertible but there’s some ideas here i might try. Or i’ll just uninstall and downgrade to 1.1.2 again

**Reply (@martinkim0)**: Hi, I’ve released scvi-tools 1.1.4 which allows you to pass in return_logits=True to SOLO.predict to replicate the previous (buggy) behavior.

**Reply (@ddiez)**: Thanks for the quick action. Can you elaborate or point to some reference about why the behavior was buggy?

**Reply (@martinkim0)**: Oh, this is because our documentation for the soft argument says the method should return probabilities, so it was technically a bug on our end.

**Reply (@ddiez)**: Thanks for the clarification. FYI, it seems the version now in pypi is 1.1.5?

**Reply (@martinkim0)**: Yes, I had to make another patch release! Anything >= 1.1.4 will have the new argument.

## N_samples ( refers to Monte Carlo sampling for each cell) setting in totalVI
**Topic:** 2340 | **Last activity:** 2024-06-28T01:22:39Z
**Posts:** 2 | **Views:** 149 | **Created:** 2024-06-19 | **URL:** https://discourse.scverse.org/t/n-samples-refers-to-monte-carlo-sampling-for-each-cell-setting-in-totalvi/2340

**Question**: Hi I have a question about the n_samples ( refers to Monte Carlo sampling for each cell) setting in totalVI. In the tutorial ( CITE-seq analysis with totalVI — scvi-tools ), n_samples is set to 25 in get_normalized_expression function. rna_denoised, protein_denoised = model.get_normalized_expression( n_samples=25, return_mean=True, transform_batch=[“PBMC10k”, “PBMC5k”] ) However, n_samples is not a parameter in the function ‘differential_expression’ de_df = model.differential_expression( groupby=“rna_subset:leiden_totalVI”, delta=0.5, batch_correction=True ) As I understand the differential calculation is based on the denoised data, so I checked the source code from github, and found the n_samples is set as 1 by default def _expression_for_de(): rna, protein = self.get_normalized_expressio …

**Reply (@cane11)**: Hi. We take mc_samples for differential expression from all cells within group1 and group2. Usually we create enough values for these group comparison to get a good estimate, whereas for the normalized expression you want one value per cell and need more samples. Were you experiencing issues?

## Failing to import SCVI-tools modules: has AnnDatasetFromAnnData been replaced?
**Topic:** 2359 | **Last activity:** 2024-06-27T19:10:15Z
**Posts:** 3 | **Views:** 141 | **Created:** 2024-06-27 | **URL:** https://discourse.scverse.org/t/failing-to-import-scvi-tools-modules-has-anndatasetfromanndata-been-replaced/2359

**Question**: Hello! I am attempting to learn how to use totalVI to analyze big CITE seq datasets after reading This paper regarding thymic development. There was an abundance of code provided, and I had hoped to work through it to reanalyze. Unfortunately, I think either I’m failing to import/install scvi-tools properly, or the packages/commands used might have changed. Notably, running the following seems to cause an error: import scvi from scvi.dataset import GeneExpressionDataset, CellMeasurement, AnnDatasetFromAnnData, Dataset10X from scvi.models import VAE, TOTALVI from scvi.inference import TotalPosterior, TotalTrainer, Posterior, UnsupervisedTrainer induces ModuleNotFound errors, where “scvi.models”, “scvi.inference”, and “scvi.dataset” do not exist. I only find these mentioned in older tutorial …

**Reply (@martinkim0)**: Hi, yes it looks like you’re trying to reproduce an older version of scvi-tools. Please refer to the recent totalVI tutorial for our updated API!

**Reply (@Adam)**: Ah, Bummer! Thanks for the quick confirmation, I’ll get working on updating things.

## Error in py_call_impl(callable, call_args$unnamed, call_args$named)
**Topic:** 2349 | **Last activity:** 2024-06-24T01:57:41Z
**Posts:** 1 | **Views:** 367 | **Created:** 2024-06-24 | **URL:** https://discourse.scverse.org/t/error-in-py-call-impl-callable-call-args-unnamed-call-args-named/2349

**Question**: Hi, When I use scvi in R, errors occur when I set the parameters as follows; however, when I cancel these parameter settings and use the default parameters, the errors disappear. How can I resolve this issue? model = scvi$model$SCVI(adata, gene_likelihood = "nb", n_latent = 50, n_layers = 2) Error in py_call_impl(callable, call_args$unnamed, call_args$named) : TypeError: can’t multiply sequence by non-int of type ‘float’ Run reticulate::py_last_error() for details. reticulate::py_last_error() ── Python Exception Message ────────────────────────────────────────────────────────────────────────────── Traceback (most recent call last): File “/home/data/t170403/miniconda3/envs/scvi/lib/python3.9/site-packages/scvi/model/_scvi.py”, line 158, in init self.module = self._module_cls( File “/home/da …

## The output of scANVI
**Topic:** 2324 | **Last activity:** 2024-06-19T04:05:33Z
**Posts:** 3 | **Views:** 283 | **Created:** 2024-06-10 | **URL:** https://discourse.scverse.org/t/the-output-of-scanvi/2324

**Question**: Hi, Thank for the wonderful libraries. I have some questions. After doing integration, should I get model_scanvi.get_latent_represention() or model_scanvi.get_normalized_expression() as a new X matrix to do downstream analysis such as DGE or GSEA? When I plotted the UMAP of get_normalized_expression() method, the result is not really integrated in the right way. image 844×290 63.9 KB The output matrix of get_latent_representation() has negative values. If we should take this matrix as X of annotated data, how can we avoid these negative values (by setting some parameters of scANVI or scVI) Thank you so much for helping me!

**Reply (@cane11)**: Responded on GitHub to the same question. In short latent representation goes into obsm and not X.

**Reply (@ngvananh2508)**: Thank you so much! <3

## Differential expression with scvi - batch correction?
**Topic:** 2331 | **Last activity:** 2024-06-19T03:35:12Z
**Posts:** 2 | **Views:** 414 | **Created:** 2024-06-13 | **URL:** https://discourse.scverse.org/t/differential-expression-with-scvi-batch-correction/2331

**Question**: Hello, Thanks a lot for this great tool. I’m running the following analysis: control = sc.read_h5ad(control_dir) #When you want to load after SOLO you need to use h5ad load instead of h5 control.var_names_make_unique() ove = sc.read_h5ad(ove_dir) ove.var_names_make_unique() healthy = sc.read_h5ad(healthy_dir) healthy.var_names_make_unique() adata = control.concatenate(ove, healthy, batch_key="Sample", batch_categories=["control", "ove", "healthy"]) print(adata.obs['Sample']) # mitochondrial genes adata.var["mt"] = adata.var_names.str.startswith("mt-") # ribosomal genes adata.var["ribo"] = adata.var_names.str.startswith(("rps", "rps")) # hemoglobin genes. adata.var["hb"] = adata.var_names.str.contains(("^hb[^(p)]")) sc.pp.calculate_qc_metrics( adata, qc_vars=["mt", "ribo", "hb"], inplace=Tr …

**Reply (@cane11)**: Hi, in this case no you don’t want to use it as it seems that you want to compare healthy and diseased cells and this is the same key as provided to scVI, so by doing batch correction you will mask the differential expression between both samples. If you have multiple healthy and diseased samples you can provide healthy sample IDs to batchid1 and all diseased sample IDs to batchid2.

## Question about differential expression and the batch_correction usage
**Topic:** 2323 | **Last activity:** 2024-06-07T15:17:06Z
**Posts:** 1 | **Views:** 242 | **Created:** 2024-06-07 | **URL:** https://discourse.scverse.org/t/question-about-differential-expression-and-the-batch-correction-usage/2323

**Question**: Hello, Say I train a model using categorical covariates to correct for donors/biological replicates, but the scRNA experiment was run in one “batch” (that is, on one flow cell/sequencing run) with a treated and untreated groups. The way I setup_anndata is with the following: setup_anndata(adata, layer = “X_Scar_Denoised_Counts”, categorical_covariate_keys=[“Sample”], continuous_covariate_keys=[‘pct_counts_mt’, ‘total_counts’]) then I train the model and run differential expression using model.differential_expression(). My question is in this case, when I call the differential expression function, does it make sense to have the batch_correction in the function when I wish to compare treated vs untreated populations? Another question I have is that many of the calculated differentially expre …

## Best way to rank genes for GSEA analysis
**Topic:** 1043 | **Last activity:** 2024-06-05T22:01:32Z
**Posts:** 4 | **Views:** 1132 | **Created:** 2023-01-09 | **URL:** https://discourse.scverse.org/t/best-way-to-rank-genes-for-gsea-analysis/1043

**Question**: Hi there, Thanks for the tool. I have used scvi differential expression to get DE genes. Now, I want to proceed to do GSEA analysis (with another tool) so I have to rank the genes for that. Generally, I use sign(lfc)*pvalue for ordering genes. But, in scvi de results there is no p-value (I got delta=0.25 for all genes). Also, not sure which should I use lfc_mean or lfc_median? So, do you have any idea that you can help me with regarding this. Many thanks.

**Reply (@adamgayoso)**: munta: Thanks for the tool. I have used scvi differential expression to get DE genes. Now, I want to proceed to do GSEA analysis (with another tool) so I have to rank the genes for that. Generally, I use sign(lfc)*pvalue for ordering genes. But, in scvi de results there is no p-value (I got delta=0.25 for all genes). Also, not sure which should I use lfc_mean or lfc_median? So, do you have any idea that you can help me with regarding this. Many thanks. You can use the Bayes factor, where higher would indicate more likelihood of the hypothesis that there is differential expression (note that this is not interpreted exactly the same as a p-value). I would start with LFC median as it’s more likely to get the sign correct, where mean can be influenced by outliers.

**Reply (@aj95b)**: @munta @PierreBoyeau I don’t think this is correct. With GSEA, you need to be able to asses if a pathway is enriched positively or negatively between treatment and controls. So you do need to rank the genes in a way that makes sense with direction of regulation. @munta For volcano plots the scVI tutorial uses ‘proba_not_de’ as equivalent to p-value to compute a -log10(proba_not_de) score, it has made sense in my analyses to rank with sign(lfc_median)*(-log10(proba_not_de))

**Reply (@munta)**: Thanks @aj95b for that and you are right I did the same by taking (proba_not_de) as I wasn’t convinced to take bayes factor ( @adamgayoso no offence).

## Issues running the updated version of MrVI
**Topic:** 2169 | **Last activity:** 2024-06-03T19:43:29Z
**Posts:** 2 | **Views:** 284 | **Created:** 2024-03-18 | **URL:** https://discourse.scverse.org/t/issues-running-the-updated-version-of-mrvi/2169

**Question**: Hi all, we would like to use the newer version of MrVI (1.0.0b1), but we can not run it - when trying to train the model: model = MrVI(adata) model.train() we get the follwing error: TypeError: scvi.train._trainer.Trainer() got multiple values for keyword argument 'devices' We suspect it’s a dependency issue ( divices and other arguments are given twice, once explicitely as the train function defalut, and once through the **trainer_kwargs ). We would love to get your input on that - any idea how to fix it? We would also be happy to get the dependecies list, to make sure we are using the same versions. Thanks for your help, Shani

**Reply (@Justin_Hong)**: Hi @shani.bmo , Thanks for trying the new version. This was an issue with a jax update that we should have fixed. Could you try again with the implementation in scvi-tools if you haven’t already?

## mrVI hyperparameter tunning
**Topic:** 1833 | **Last activity:** 2024-06-03T19:40:45Z
**Posts:** 4 | **Views:** 443 | **Created:** 2023-10-24 | **URL:** https://discourse.scverse.org/t/mrvi-hyperparameter-tunning/1833

**Question**: Hi all, We get great results from mrVI and we want to further make sure we use it t optimally. We would like to do a quick HPO on mrVI and would love to get your experienced input on which parameters to focus? When running HPO on scVI, we focused on N_latent, N_hidden and learning rate. Are there additional parameters you advise to scan for mrVI? thanks!!

**Reply (@Justin_Hong)**: Hi @shani.bmo ! Thanks for your interest in using MrVI. It’s really exciting that you are seeing good results from it. We have an upcoming reimplementation of MrVI with significant modifications, which I will recommend to use once it comes out. But in the meantime I would recommend focusing on the n_latent, epochs/learning rate, kl annealing (n_epochs_kl_warmup), hvg selection (be careful what metric you use for this), choice of sample / batch covariates.

**Reply (@shani.bmo)**: @Justin_Hong thank you for your fast response and for your work looking forward for the new version.

**Reply (@Justin_Hong)**: Hi @shani.bmo just to update here in case you missed it, we the new manuscript is up on biorxiv along with an updated version in scvi-tools. You can see all the details in the tweetorial: x.com

## SCVI tools with large datasets
**Topic:** 1966 | **Last activity:** 2024-05-31T14:39:19Z
**Posts:** 4 | **Views:** 1184 | **Created:** 2023-12-22 | **URL:** https://discourse.scverse.org/t/scvi-tools-with-large-datasets/1966

**Question**: I have have 2 hardware partitions, one is a large memory partition that I can concatenate many AnnDatas into a single large cell by gene matrix. I also have a GPU partition that has limited memory. How can I load the large AnnData into SCVI tools if it won’t fit into the GPU partition’s memory limit? I see that AnnData 0.10 has been released and has extended on-disk support here . Is there documentation for this or other methods to train an SCVI/SCANVI model with a “larger-than-memory” counts matrix? Thanks in advance for any input.

**Reply (@LinearParadox)**: I believe SCVI batches the cells it loads in, so the whole dataset shouldn’t ever be loaded into the GPU. Specifically this paragraph from their pub: " A second level of stochasticity comes from subsampling from the training set (possible because the cells are identically independently distributed when conditioned on the latent variables). We then have an online optimization procedure that can handle massive datasets, used by both scVI and other methods that exploit neural networks 18 , 19 , 20 , 21 . At each iteration, we focus only on a small subset of the data randomly sampled ( M = 128 data points) and do not need to go through the entire dataset. Therefore, there is no need to store the entire dataset in memory. Because the number of genes is in practice limited to a few tens of thous …

**Reply (@Valentine_Svensson)**: Hi crhodes, I believe everything will run correctly if you have read in the AnnData file with the option backed = 'r+' and run the setup_anndata method for the SCVI model. Did you try this? I would expect it to be extremely slow however, because you will need to move each mini-batch of data from the hard drive through the RAM to the GPU. Hope this helps, /Valentine

**Reply (@agdenadel)**: Related to the topic of large datasets, I have been working with some datasets of millions of cells and training scVI models with all human genes and I have been having out of memory errors prior to training initiating, when the scVI constructor is called, i.e. model = scvi.model.SCVI(adata, n_layers=n_layers, n_latent=n_latent, n_hidden=n_hidden, gene_likelihood="nb") runs out of memory (and I have been using machines with as much as 384 gigabytes of RAM). Is there a workaround for this or something I am missing? The anndata object is in backed mode adata = ad.read_h5ad(h5ad_file, backed="r+")

## Training split conditioned on batch_key
**Topic:** 2283 | **Last activity:** 2024-05-22T14:26:11Z
**Posts:** 4 | **Views:** 290 | **Created:** 2024-05-16 | **URL:** https://discourse.scverse.org/t/training-split-conditioned-on-batch-key/2283

**Question**: Hello SCVI-Team, I am currently working with public scRNAseq Atlas data (HCA, HLCA, etc.). It is crucial to account for not only patient-specific but also technical effects such as study, sample preparation, and assay type. Typically, I utilize the patient_id as the batch_key and address sources of technical noise with the categorical_covariate_keys parameter during model setup. This approach generally works well with some additional preprocessing steps. However, I’ve noticed significant variations in the total number of cells per patient across different studies. This variability poses a risk of underrepresentation or absence of certain patients and/or studies (and their respective covariates) in the training and validation datasets. Would it be advisable to split the data per patient ID …

**Reply (@Florian_Deckert)**: I have reviewed the splitting indices in model.train_indices and model.validation_indices and confirmed that the random shuffling and splitting effectively distribute data without considering the patient ID. Each patient (or study) approximately maintains a 0.9/0.1 ratio for the training/validation datasets, which aligns with our expectations (In hindsight, it was unreasonable to assume otherwise.). However, would you advise to monitor any additional parameters to ensure proper learning when observing strong differences in total cell numbers between covariant? Thank you once again for your support. Best regards, Florian

**Reply (@cane11)**: Hi, we have scVI criticism. The think you could monitor is whether the CV per cell is different for different batches. This could point to this batch being modeled worse. It is hard to tell without much more information whether this is due to technical effects (library sizes, ambient genes etc) or model training though.

**Reply (@Florian_Deckert)**: @cane11 Thank you very much! I just slowly start to really understand some fundamental concepts of VAE and your input is highly appreciated. I will read up the Posterior Predictive checks (PPC) section of scvi-criticism, it looks great

## With `data_module`, how do I get the `adata_manager`?
**Topic:** 2296 | **Last activity:** 2024-05-22T02:50:07Z
**Posts:** 1 | **Views:** 146 | **Created:** 2024-05-22 | **URL:** https://discourse.scverse.org/t/with-data-module-how-do-i-get-the-adata-manager/2296

**Question**: I’m trying to train using data_module s passed to a model’s .train , because I already have a train / valid split that I need to respect, and don’t want SCVI to redo the split internally. For some reason, there isn’t a built-in way to do this as far as I can tell, to just specific two anndatas or to specify indices over a single anndata for training and validation? But now, I need the anndata manager as SCVI.setup_anndata does a lot of work to setup the batch that the model can ingest, and the anndata manager is needed to create the dataset object that is then passed to dataloaders, following the batch format set by setup_anndata, from my understanding. I’m taking inspiration from scvi.dataloaders.DataSplitter, which is what scvi-tools uses internally when one just calls model.train scvi-t …

## Issue importing sysVI
**Topic:** 2282 | **Last activity:** 2024-05-17T08:48:33Z
**Posts:** 3 | **Views:** 352 | **Created:** 2024-05-16 | **URL:** https://discourse.scverse.org/t/issue-importing-sysvi/2282

**Question**: Very interested in the sysVI release - I can’t see that it is currently importable from scvi.external as suggested in the tutorial: from scvi.external import SysVI ImportError: cannot import name ‘SysVI’ from ‘scvi.external’ (/.conda/envs/scarches/lib/python3.9/site-packages/scvi/external/ init .py) Other scvi.external packages import just fine. Could you advise if sysVI is available as yet? Many thanks

**Reply (@martinkim0)**: Hi, we are still working on integrating sysVI into the codebase. Apologies as I don’t have an ETA for when this is released as we’re working through a backlog of contributions and features. If you’d like to try out the work-in-progress, you may install it as follows: pip install "scvi-tools @ git+https://github.com/Hrovatin/scvi-tools@main"

**Reply (@eoinmckinney)**: Many thanks - I realise its an ongoing piece of work and very grateful for the early look. all the best

## Does a scvi model has something like pytorchs state_dict?
**Topic:** 2280 | **Last activity:** 2024-05-17T07:42:06Z
**Posts:** 3 | **Views:** 220 | **Created:** 2024-05-16 | **URL:** https://discourse.scverse.org/t/does-a-scvi-model-has-something-like-pytorchs-state-dict/2280

**Question**: Hey I am using an external package with my scvi model and this package (originally written for pytorch models) tries to access the model.state_dict . i.e this dictionary where all the weights and so on are saved. With my scvi model I get the Error : AttributeError: 'SCVI' object has no attribute 'state_dict' Is there something similar to pytorchs state_dict for scvi models ? Thanks a lot for your help!

**Reply (@martinkim0)**: Hi, the module attribute of SCVI is a regular PyTorch module, so you can access it through model.module.state_dict .

**Reply (@luschaef)**: Ahhh, awesome! Thank you

## Generating gene expression from latent vectors
**Topic:** 2259 | **Last activity:** 2024-05-15T20:26:57Z
**Posts:** 2 | **Views:** 197 | **Created:** 2024-05-08 | **URL:** https://discourse.scverse.org/t/generating-gene-expression-from-latent-vectors/2259

**Question**: Hi, Firstly great set of tools! I have a small question. I am wondering if there’s a way to generate expression data from the latent vectors in scVI. Is it possible to separately access the decoder/generator? If that’s possible, what’s the best way to do it? Really stuck here so highly appreciate any help!

**Reply (@cane11)**: Hi, for several models we have a minified mode. The purpose of this mode is to generate gene expression from latent vectors Minification — scvi-tools .

## Insufficient batch correction for certain cell-types
**Topic:** 2237 | **Last activity:** 2024-05-15T20:25:19Z
**Posts:** 9 | **Views:** 760 | **Created:** 2024-04-24 | **URL:** https://discourse.scverse.org/t/insufficient-batch-correction-for-certain-cell-types/2237

**Question**: Hello, Dataset I have a scRNASeq dataset that was based on the following experimental design: timepoint Nsamples t0 5 t1 3 t2 4 Aim Correct for interindividual variability across timepoints and study gene expression for each cell-type between timepoints. Batch correction In order to remove interindividual variability, first I created two columns: One column named Replicate containing sample IDs. Second column denoting the timepoint t1 , t2 and t3 . then I performed batch correction as following: Select 4000 highly variable genes sc.pp.highly_variable_genes(adata, n_top_genes=4000, subset = True, layer = 'soupX_counts', flavor = "seurat_v3", batch_key="Replicate") soupX_counts were provided by the SoupX package duing the QC steps to remove any possible mRNA contamination. Setup SCVI model s …

**Reply (@martinkim0)**: Hi, I have a couple of clarifying questions: What is the size of your dataset? Depending on that, the number of maximum epochs might be too large. How long does it take for early stopping to kick in? What’s the reason behind setting limit_train_batches=20 ?

**Reply (@dkioroglou)**: The size of the merged dataset (i.e t0+t1+t2) is 86500 cells. The activation of the early stopping depended on the early_stopping_patience value. When the latter was set at 45, early stopping happened within 7 minutes, at 150 within 20 minutes and at 400 close to 50 minutes. Regarding the limit_train_batches , I’m not sure whether my reasoning is correct but the idea was to constrain RAM usage and instead of loading all cells during training, I wanted to load batches of 20 till all dataset was used. However, I’m not sure whether this is correct. Does limit_train_batches gets multiplied by batch_size and provides the total number of cells used in each epoch? If that’s true, then I’m using only 20k cells in each epoch.

**Reply (@martinkim0)**: Could you also specify the number of epochs for which your model is training? I have a feeling that with those values of max_epochs and early_stopping_patience , your model is most likely overfitting on the training set. This can be checked by plotting "elbo_validation" and "elbo_train" in model.history post-training. If the validation ELBO is significantly higher than its training counterpart, then it’s likely that the model overfit. Something in the ballpark of max_epochs=400 and early_stopping_patience=10 might be more appropriate for this dataset size. My understanding of limit_train_batches is that it will run that number of minibatches during each training epoch, so yes the model would be seeing about 20k observations during training. Your main memory usage will mostly be set by your …

**Reply (@cane11)**: Hi, I think overall it looks fine integration wise. Yes, it will likely affect DE genes between replicates (between cell-types I guess it might be fine. If you want to get classical monocytes better integrated, I would check DE gene between those batches. It’s a very typical behaviour that monocytes get activated during the experiment (in humans higher in IL1B but also FOS and JUN). scVI usually does not integrate this (it’s helpful as it would otherwise do overintegration). If you think it’s critical to get better integration, I would reduce the number of genes and n_latent (to maybe 1500 genes). I’m also not sure whether Replicate is a unique sample or whether it has the same value for different samples at different time points. I would in that case recommend to replace Replicate by a st …

**Reply (@dkioroglou)**: Thank you both for your suggestions. I have done a couple of optimizations by combining your recommendations. Previous implementation The intuition of Martin was right and my previous implementation was overfitting. model_elbo_train_and_validation_score 3000×1500 135 KB Optimization 1 I introduced the following changes in the code: Reduced highly variable genes to 3000: Code sc.pp.highly_variable_genes(adata, n_top_genes=3000, subset = True, layer = 'soupX_counts', flavor = "seurat_v3", batch_key="Replicate") Used SCANVI and replaced categorical_covariate_keys with batch_key . Code scvi.model.SCANVI.setup_anndata(adata, layer = "soupX_counts", batch_key="Replicate", labels_key="celltypist_cell_types_high_resolution", unlabeled_category="Unknown", continuous_covariate_keys=['pct_counts_mt', …

**Reply (@cane11)**: Can you also share your line of code for DE (I need to know how batch_key is used there)? In general batch effects exist between sequencing samples/sample processings. I assume the time points of one replicate are independent (different patients or mice). If it’s the same patient sampled multiple times using replicate for integration makes sense (otherwise your design could contain e.g. male and female for the same replicate name and this will lead to low integration). I’m case, it’s a single replicate across time points. I still think your first integration looks fine and your main point was how to get more integration.

**Reply (@dkioroglou)**: Hi Can, Regarding the experimental design, there are 5 patients ( p1,p2,p4,p5,p6 ) each one provided samples at 3 timepoints ( t0, t1, t2 ) as shown in the table below. Replicate Condition Replicate2 p1 t0 p1_t0 p1 t1 p1_t1 p1 t2 p1_t2 p2 t0 p2_t0 p2 t1 p2_t1 p2 t2 p2_t2 p4 t0 p4_t0 p4 t1 p4_t1 p4 t2 p4_t2 p5 t0 p5_t0 p5 t1 p5_t1 p5 t2 p5_t2 p6 t0 p6_t0 p6 t1 p6_t1 p6 t2 p6_t2 The idea is to remove inter-individual differences between patients across timepoints (Condition) and get DEGs between timepoints (Condition). My initial implementation included the column “ Replicate ” as batch_key and my last implementation included “ Replicate2 ” as batch_key . Below is my code for DEGs: pairs = [("t0", "t1"), ("t1", "t2"), ("t0", "t2")] def getDEGs(cellType): global DEGs for pair in pairs: p1, p2 …

**Reply (@cane11)**: I think in your setup it is fine to use replicate as batch_key. The different donors will be the reason for most of the batch effect likely, so there’s little batch effect between time points. It is fine to use Replicate2 in this case though you want to set batch_correction=False in model.differential_expression or better set batch_id1 to all batches of condition1 and for batch_id2 to condition2. This way the model won’t correct gene expression for the covariate of interest and will generate those counts for the correct batch.

## Batch correction in reconstructed gene space
**Topic:** 1256 | **Last activity:** 2024-05-09T09:17:37Z
**Posts:** 6 | **Views:** 1202 | **Created:** 2023-03-23 | **URL:** https://discourse.scverse.org/t/batch-correction-in-reconstructed-gene-space/1256

**Question**: Hi We recently have been applying scVI for batch correction to scRNAseq data from two different batches. We see the batch correction working when visualizing the data, however, when we do the genewise comparison between batches it looks like batch effect has not been removed. I wonder if we expect to see batch effect in the reconstructed gene space? Khagani

**Reply (@Justin_Hong)**: What do you mean by genewise comparison between batches? It sounds like you are comparing the reconstructed gene counts output by get_normalized_expression . If this is the case, by default it uses the original batch terms when inferring the normalized gene levels, which means it will reproduce the batch effects. If you would like a view of the gene counts where they are simulated to come from the same batch, you need to use the transform_batch kwarg, which when set to an integer computes the normalized expression rates as if they came from the same batch.

**Reply (@khagani)**: Hi Justin Thanks for the quick response. I really appreciate it. Can you explain what exactly transform_batch doing? and how should we interpret the values we are getting from transform_batch. Khagani

**Reply (@khagani)**: And also documentation is a bit confusing and out of date. We tried to use the following link but it was broken: https://docs.scvi-tools.org/en/stable/user_guide/notebooks/totalVI.html Would be very helpful if there was a tutorial to get the corrected data with the up to date API. I appreciate your work and wanted to give a feedback. Khagani

**Reply (@adamgayoso)**: Hi the tutorial is here scvi-tools CITE-seq analysis with totalVI With totalVI, we can produce a joint latent representation of cells, denoised data for both protein and RNA, integrate datasets, and compute differential expression of RNA and protein. Here we demo... If you ever have a broken link you can always revert back to https://docs.scvi-tools.org/en/stable/ We have a page here that we will complete describing transform_batch scvi-tools Counterfactual prediction

**Reply (@malonzm1)**: Hi, The link to Counterfactual prediction is broken (and so are all the other links). May I know what values can be assigned to transform_batch ? Btw, in this tutorial Introduction to scvi-tools — scvi-tools , why isn’t transform_batch mentioned? Br,

## SOLO usage - batch, training, predicting
**Topic:** 60 | **Last activity:** 2024-05-08T02:16:24Z
**Posts:** 9 | **Views:** 1623 | **Created:** 2021-03-25 | **URL:** https://discourse.scverse.org/t/solo-usage-batch-training-predicting/60

**Question**: Hello - great set of tools, extremely useful. I was hoping to try using SOLO for doublet detection and can see this is now incorporated into scvi tools. I’m not finding the usage of this particularly clear. Seems that the guidance is that it should be run on a single droplet sequencing lane at a time, and it’s not possible to run after training an scvi model with batch correction. Is that correct? After training then predicting I am getting a numpy array which is a little difficult to interpret - the dimensions are larger than the original anndata object - so perhaps it is the simulated doublets and the native cells together. It’s just a little unclear. Any chance you could clarify how best to use this tool? Thanks,

**Reply (@adamgayoso)**: Thank you for the raising this. Indeed it looks like the predict() method will give predictions of real cells and simulated doublets. bjstewart1: Seems that the guidance is that it should be run on a single droplet sequencing lane at a time, and it’s not possible to run after training an scvi model with batch correction. Is that correct? Indeed this is true; this is how Solo was designed, as doublets are generated within a specific lane. bjstewart1: Any chance you could clarify how best to use this tool? The workflow in the examples of the documentation should be followed, except here is a workaround to process the output of the predict function. def process_predict_output(output, solo_model): import pandas as pd label = solo_model.adata.obs["_solo_doub_sim"].values.ravel() preds = output[ …

**Reply (@bjstewart1)**: Thanks for your quick and helpful response Adam. I’m just conscious that with multiple droplet lanes, this requires recomputing a model for each lane which would be very time consuming for big experiments. I wonder if it would be possible to compute a model overall for the experiment and then run solo off that for subsets corresponding to individual lanes? Or do you think this would break some important assumptions of the tool?

**Reply (@davek44)**: Yes, it’s totally fine to fit one scVI model and then run Solo independently for each lane, seeded from that model. That --seed option in our CLI demonstrates that workflow: solo/solo.py at master · calico/solo · GitHub

**Reply (@adamgayoso)**: davek44: Yes, it’s totally fine to fit one scVI model and then run Solo independently for each lane Hmmm I think we might need to change the scvi-tools Solo API a bit to allow this. I can do this relatively soon.

**Reply (@bjstewart1)**: Thanks for your thoughts on this @davek44 & @adamgayoso I think modifying the API to allow for this approach would be extremely useful

**Reply (@adamgayoso)**: PR is up.

**Reply (@malonzm1)**: Hi, I used scvi.external.SOLO.from_scvi_model . How do I find output and solo_model ? Thanks.

**Reply (@malonzm1)**: This is resolved. Thanks.

## Scvi.data.organize_multiome_anndatas with two big anndata objects
**Topic:** 2247 | **Last activity:** 2024-05-03T20:46:47Z
**Posts:** 2 | **Views:** 250 | **Created:** 2024-05-01 | **URL:** https://discourse.scverse.org/t/scvi-data-organize-multiome-anndatas-with-two-big-anndata-objects/2247

**Question**: Hi, I am trying to use MultiVI with two different anndata objects for paired scRNA and scATAC. In the organize_multiome_anndatas step, I was following the tutorial from the singl-cell best practice adata_paired = ad.concat([rna.copy().T, atac.copy().T]).T adata_paired.obs = adata_paired.obs.join(rna.obs[["cell_type", "batch"]]) adata_paired.obs["modality"] = "paired" adata_paired adata_mvi = scvi.data.organize_multiome_anndatas(adata_paired) But this ad.concat([rna.copy().T, atac.copy().T]).T step requires huge memory and my jobs were always killed by the system. I was wondering if there are some ways to “bypass” this step. Thanks in advance!

**Reply (@cane11)**: Hi, first try would be: adata = ad.concat([rna, atac], axis=1) There is also a function to do the merging on disk ( anndata.experimental.concat_on_disk — anndata 0.1.dev50+gb3763f8 documentation ). It also makes sense to subset to highly variable genes beforehand.

## Scale by total protein counts before running totalVI (to eliminate a batch effect of having different sequencing depths)
**Topic:** 2249 | **Last activity:** 2024-05-03T20:41:09Z
**Posts:** 4 | **Views:** 264 | **Created:** 2024-05-01 | **URL:** https://discourse.scverse.org/t/scale-by-total-protein-counts-before-running-totalvi-to-eliminate-a-batch-effect-of-having-different-sequencing-depths/2249

**Question**: Hello, I am trying to scale by total protein counts before running totalVI to eliminate the batch effect). More specifically, Prior to running TotalVI with data integrated from two independent experiments (two batches), I would like to normalize or scale protein counts for each cells. Is there an equivalent to the scanpy normalization function for genes (scanpy.pp.normalize_total) for protein? Or, what is the best way to scale my protein count values prior to running TotalVI?

**Reply (@martinkim0)**: Hi, we don’t recommend scaling or normalizing protein counts prior to running totalVI since the generative model of totalVI uses a negative binomial distribution to model counts, thus normalized counts will not be suitable for this type of modeling. Hope this clarifies things.

**Reply (@Milcah)**: That makes sense. But, even so, is there a way I can scale the protein count values and round up to the nearest integer prior to TotalVI?

**Reply (@cane11)**: This is not recommended. Downsampling would be fine but it’s throwing away part of your data with potentially negative side effects. Maybe we start a step earlier: why do you want to do it? Do you get low integration without doing these steps and using totalVI?

## Inquiry about Data Input and DE Analysis Details in scVI
**Topic:** 2244 | **Last activity:** 2024-05-03T20:38:40Z
**Posts:** 5 | **Views:** 475 | **Created:** 2024-04-29 | **URL:** https://discourse.scverse.org/t/inquiry-about-data-input-and-de-analysis-details-in-scvi/2244

**Question**: Dear SCVI team, I hope this message finds you well. I am currently utilizing scVI for my research and have some questions regarding the data input and analysis process, particularly concerning differential expression (DE) analysis. Your insights would be greatly helpful in advancing my understanding and application of the tool. Data Input for DE Analysis : When conducting DE analysis using scVI, what specific type of data should be inputted into the model? Is it the raw count data, normalized data within the model, or another form of standardized data? I noticed that in tutorials, there is no explicit specification of the data input type, which has led to some uncertainty about what exactly is being used for DE analysis. Interpretation of DE Results : Regarding the DE results, specifically …

**Reply (@qweasdf1354)**: I want to know whether should I do the normalize step to the raw count adata before i using the SCVI_DE model. In my understanding, the DE model will using the trained model which using the scvi-model.SCVI function initially?

**Reply (@martinkim0)**: I can address a subset of the questions: Most of the models in scvi-tools (including scVI) require raw count data as input since the generative process parametrizes discrete distributions (negative binomial or Poisson). The generative process also learns normalized expression values ( scvi.model.SCVI.get_normalized_expression ) that are used for downstream differential expression. You can learn more about that in our user guide . It’s recommended to set up a batch key using scvi.model.SCVI.setup_anndata when you expect there to be technical effects in your data ( e.g. assay type), and this can help later for differential expression.

**Reply (@qweasdf1354)**: Thank you for your reply!

**Reply (@cane11)**: Positive LFC means higher expression in group1 than group2. I prefer validating and plotting results using raw data. This gives you additional insights about the actual measured differences. Scanpy takes logarithmic values (after library size normalization) as input while scVI uses raw count data. The LFC is an arithmetic mean LFC in scVI and is the LFC of a geometric mean in scanpy. See The impact of package selection and versioning on single-cell RNA-seq analysis - PubMed for more details.

## Computing neighbors from X_scANVI representation
**Topic:** 2052 | **Last activity:** 2024-04-26T13:32:19Z
**Posts:** 6 | **Views:** 565 | **Created:** 2024-02-04 | **URL:** https://discourse.scverse.org/t/computing-neighbors-from-x-scanvi-representation/2052

**Question**: Hi, in this tutorial: Atlas-level integration of lung data — scvi-tools a neighborhood graph is computed from the latent representation (here called X_scVI). When I try to reproduce the steps, I get an error: —> 73 sc.pp.neighbors(self.adata, n_neighbors=10, use_rep=self.rep, method=‘gauss’) #num_pcs=50 74 # The width of the connectivity kernel is implicitly determined by the number of neighbors used to compute the single-cell graph in neighbors() 75 sc.tl.diffmap(self.adata) File ~/.conda/envs/new_sc/lib/python3.11/site-packages/scanpy/neighbors/ init .py:139, in neighbors(adata, n_neighbors, n_pcs, use_rep, knn, random_state, method, metric, metric_kwds, key_added, copy) 137 adata._init_as_actual(adata.copy()) 138 neighbors = Neighbors(adata) → 139 neighbors.compute_neighbors( 140 n_neig …

**Reply (@jolespin)**: Did you ever get any clarity regarding this question? I’m trying to do something similar.

**Reply (@a_ke_nna)**: Hi, at some point it just worked, I’m so sorry, I do not remember what I changed… I remember that I tried to print the shapes, but I did not change anything knowingly…

**Reply (@cane11)**: I have never seen this error. Can you tell me the scvi-tools and scanpy version? Is this also happening if not setting method to ‘gauss’. What’s the shape of self.adata.obsm[self.rep]?

**Reply (@a_ke_nna)**: Hi, sorry but I do not have access to the workstation which I was running the code on anymore, since this was from a uni project from last semester. The envs do not exist anymore and since the issue resolved, I did not go deeper into this. Sorry!

**Reply (@cane11)**: It was more to get some troubleshooting from @jolespin . I assume some cells are created with only a single neighbor (not an expert for “gauss” nearest neighbor method). In scVI, it’s likely a problem with cells with almost no counts and usual qc (filtering to cells with more than 100 counts or much higher should solve it. Otherwise, my recommendation is using another NN method or if you require “gauss” as a method increase the number of nearest neighbors.

## Early stopping debug
**Topic:** 2240 | **Last activity:** 2024-04-26T13:29:33Z
**Posts:** 2 | **Views:** 479 | **Created:** 2024-04-26 | **URL:** https://discourse.scverse.org/t/early-stopping-debug/2240

**Question**: Hi, I have a user running the latest scvi on a scrna dataset. For some reason the model triggers and early stopping that i can’t quite understand ( i was lucky enough to never have an early stopping occur until now!) 2024-04-25 17:20:28,337: INFO - AnnData object with n_obs × n_vars = 32322 × 22512 obs: 'sample_id', 'tissue', 'condition', 'batch', 'subject', 'CMV_status', 'doublet_scores', 'predicted_doublets', 'n_genes_by_counts', 'log1p_n_genes_by_counts', 'total_counts', 'log1p_total_counts', 'total_counts_hb', 'log1p_total_counts_hb', 'pct_counts_hb', 'total_counts_mt', 'log1p_total_counts_mt', 'pct_counts_mt', 'total_counts_rp', 'log1p_total_counts_rp', 'pct_counts_rp', 'MarkersNeutro_score', 'S_score', 'G2M_score', 'phase' var: 'gene_ids', 'feature_types', 'genome', 'hb', 'mt', 'rp', …

**Reply (@cane11)**: I’m not understanding the issue here. Is the model still improving and is stopping early? Or is an optimal model found and then training stops? The second behavior is good behavior and if you don’t want to have it, then disable early_stopping would be recommended. Scvi actually prints the reason for stopping (elbo_validation did not improve).

## Benchmarking CellHint with scib-metrics Benchmarker tool how to use embedding_obsm_keys
**Topic:** 2216 | **Last activity:** 2024-04-25T21:27:48Z
**Posts:** 2 | **Views:** 274 | **Created:** 2024-04-12 | **URL:** https://discourse.scverse.org/t/benchmarking-cellhint-with-scib-metrics-benchmarker-tool-how-to-use-embedding-obsm-keys/2216

**Question**: Hi! I am integrating different single-cell atlases and testing different methods like scVI and scANVI and then benchamrking them using scib-metrics package to assess the quality of the integration. However, I also wanted to integrate the newly developed mthod called CellHint Google Colab . However CellHint calculated the new corrected distances and connectivies that are then used to draw the new batch corrected umap. I was wondering if I can use the CellHint umap embedding in embedding_obsm_keys and compare them to the scVI and scANVI embeddings. Thank you for your help!

**Reply (@cane11)**: This is the general way to perform the comparison. scib-metrics does not work with precomputed neighborhood graphs and requires an embedding.

## Confused about hyperparam tuning in scVI
**Topic:** 2217 | **Last activity:** 2024-04-25T21:26:12Z
**Posts:** 2 | **Views:** 477 | **Created:** 2024-04-13 | **URL:** https://discourse.scverse.org/t/confused-about-hyperparam-tuning-in-scvi/2217

**Question**: I’m not well-versed in ML concepts, so this might be a very naïve question. I have followed the hyperparam tuning example here: Model hyperparameter tuning with scVI — scvi-tools and applied the approach to my model. I used “validation_loss” as the metric: sc.pp.highly_variable_genes( adata, n_top_genes=5000, subset=True, flavor='seurat_v3', batch_key="dataset", ) scvi.model.SCVI.setup_anndata( adata, categorical_covariate_keys=['dataset', 'sample_name'], continuous_covariate_keys=['pct_counts_mt'] ) scvi_tuner = autotune.ModelTuner(scvi.model.SCVI) search_space = { "n_hidden": tune.choice([128, 256, 512]), "n_layers": tune.choice([1, 3, 5]), "n_latent": tune.choice([10, 20, 30]), "batch_size": tune.choice([128, 256, 512]), "lr": tune.loguniform(1e-4, 1e-2), } ray.init(log_to_driver=False) …

**Reply (@cane11)**: We perform kl_warmup during model training (kl_weight increases during training). Validation_loss uses the current kl_weight while elbo_validation uses a kl_weight of 1 (the correct elbo term). The observation therefore is expected and your curves look converged and fine.

## Scvi model training after sub-clustering
**Topic:** 2220 | **Last activity:** 2024-04-25T21:23:16Z
**Posts:** 2 | **Views:** 398 | **Created:** 2024-04-16 | **URL:** https://discourse.scverse.org/t/scvi-model-training-after-sub-clustering/2220

**Question**: Hi. Thank you for these amazing tools. I have a very basic question regarding model training. After generating the model and plotting the map, if I need to sub cluster a population or remove a sample from the dataset, do I need to re-train the model?? If not re-training can I use the dcvi-normalized values for the sub clustered group?

**Reply (@cane11)**: Generally you can just go ahead. I sometimes retrain, if I subset from an atlas object to e.g. T cells and need better resolution for T cell subsets. In general, I rerun the highly variable gene selection before training the second model.

## scvi.model.SCVI input values
**Topic:** 2233 | **Last activity:** 2024-04-23T23:23:37Z
**Posts:** 2 | **Views:** 490 | **Created:** 2024-04-23 | **URL:** https://discourse.scverse.org/t/scvi-model-scvi-input-values/2233

**Question**: Hi, I’m using the AnnData format, but I get a warning when I try to train the model on min-max normalized single-cell inputs: /module/_vae.py:458: UserWarning: The value argument must be within the support of the distribution reconst_loss = -generative_outputs[“px”].log_prob(x).sum(-1) Can the training data (X) be positive floating-point numbers, or do they have to be positive integers? This data doesn’t contain any NANs or negative values. This question is in reference to this post: github.com/scverse/scvi-tools UserWarning: The value argument must be within the support of the distribution reconst_loss = -px.log_prob(x).sum(-1) opened 11:39AM - 30 Jan 24 UTC closed 12:22AM - 14 Feb 24 UTC FZ-hajji bug Hello, I am using the scANVI model for batch correction of pancreas cell data … , as dem …

**Reply (@martinkim0)**: Hi, scVI expects raw count data as input (as do the vast majority of models in scvi-tools), so inputting any form of normalized data will result in undefined behavior. This is because we parametrize discrete distributions in the generative model. You’ll notice that you get a warning, not an error - the model will still attempt to train, but it’s likely you’ll end up with NaNs during training and/or a poorly-fit model. Please consult our user guides and tutorials for more details!

## Environment recipes for scVI autotune and scIB-metrics Benchmarker
**Topic:** 2200 | **Last activity:** 2024-04-07T18:06:28Z
**Posts:** 1 | **Views:** 212 | **Created:** 2024-04-07 | **URL:** https://discourse.scverse.org/t/environment-recipes-for-scvi-autotune-and-scib-metrics-benchmarker/2200

**Question**: I haven’t been able to reproduce the autotune or Benchmarker elements of the scVI-tools tutorials on a variety of CentOS nodes with several Xeon models and several NVIDIA GPUs (incl. A100 and A40), across about a dozen different fresh conda environments created first by following the installation instructions to the letter, and then also by trying a number of variations when that didn’t work. While the errors differed from case to case, they’re always due to dependency conflicts involving Jax, PyTorch, Tensorflow, and/or Ray. Does anyone have working conda / pip recipes to share in which autotune and Benchmarker both run without error?

## scRNA-seq batch correction for DestVI
**Topic:** 2184 | **Last activity:** 2024-04-03T21:08:34Z
**Posts:** 3 | **Views:** 277 | **Created:** 2024-03-26 | **URL:** https://discourse.scverse.org/t/scrna-seq-batch-correction-for-destvi/2184

**Question**: Hello, Thanks for providing DestVI. I’m trying to understand if one can include batch correction in the scRNA-seq data processing for DestVI. The Methods section of the DestVI paper (Lopez et al. 2022) mentions that scVI conditions on the batch identifier, whereas scLVM conditions on the cell type information. The DestVI tutorial , uses 4 lymph node scRNA-samples, which seem have to minimal batch effects between them–i.e. all 4 batches overlap very well with each other in the UMAP(see figure). Screenshot 2024-03-26 at 11.12.56 AM 2224×722 156 KB However, for the analysis that I’m running, I’d like to use scRNA-seq datasets from the same cancer type but from multiple studies, and I know that there are batch effects between studies. I can run scVI to correct the batch effects and get the emb …

**Reply (@cane11)**: It’s not exactly clear how to set the batch_id for the spatial dataset in this setup (it uses the Decoder and requires setting a batch_id), which is why it wasn’t included in the original DestVI. I am looking into it currently and did some other changes to DestVI ( GitHub - scverse/scvi-tools at can_destvi_v2 ). However, it is under development and I currently can neither guarantee a stable version nor guarantee model performance. I’ll try to update here, when we have a release candidate.

**Reply (@jdime)**: Hello Can, Thanks for your response. I look forward for a release candidate when you have a chance. J.

## TCR and BCR genes and HVGs selection
**Topic:** 2139 | **Last activity:** 2024-04-03T01:02:07Z
**Posts:** 6 | **Views:** 388 | **Created:** 2024-03-05 | **URL:** https://discourse.scverse.org/t/tcr-and-bcr-genes-and-hvgs-selection/2139

**Question**: Hello world! I’ve read in many papers that when performing a re-clustering of some populations, like T cells or B cells, prior to the step of integration and so on, they re-calculate the HVGs but excluding the TCR- or BCR-related genes, because they are donor-specific, especially when talking about BCR. Can you help me how to remove the TCR- or BCR-related genes before computing the HVGs selection, but without removing them from the .var of the anndata, since I want to evaluate their expression during the step of cell annotation? The code that I use to calculate the HVGs is the following: sc.pp.highly_variable_genes(adata, n_top_genes = 4000, flavor = “seurat_v3”, layer = “raw”, batch_key = ‘sample_id’, subset = False) Thanks a lot! Paolo

**Reply (@ivirshup)**: I think you could do something like: sub = adata[:, ~tcr_bcr_genes] hvg_df = sc.pp.highly_variable_genes(sub, inplace=False) hvg_df.index = sub.var_names # only necessary in scanpy <1.10 Then grab the info out of the returned dataframe. adata.var["highly_variable"] = hvg_df["highly_variable"].reindex(adata.var_names, fill_value=False)

**Reply (@pmarzano97)**: Thank you so much @ivirshup !!! Do you know if there’s a repository or a document or anything else where the BCR/TCR related genes are listed (like for the ones related to the cell cycle in the guide)? Thank you!!

**Reply (@ivirshup)**: No problem. For gene lists I don’t, but maybe @grst does?

**Reply (@grst)**: The Ensembl gene annotation provides this information in the “Transcript type” column which you can retrieve from Biomart. Other genome annotations should have similar annotations. More speficially, BCR genes are those with IG_[VDJDC]_(gene|pseudogene) and TCR genes those with TR_[VDJDC]_(gene|pseudogene) transcript type.

**Reply (@cane11)**: As I used it yesterday: dataset = pybiomart.Dataset(name='hsapiens_gene_ensembl', host='http://www.ensembl.org') table = dataset.query(attributes=['ensembl_gene_id', 'external_gene_name', 'chromosome_name', 'transcript_biotype'], use_attr_names=True) merged = pd.merge( adata.var, table, left_on='gene_ids', right_on='ensembl_gene_id' ) merged['transcript_biotype'].value_counts() adata.var['gene_name'] = adata.var_names gene_subset = pd.merge( adata.var, table[table['transcript_biotype'].isin(['protein_coding', 'lncRNA', 'IG_C_gene', 'TR_C_gene'])], # replace here with your filter. left_on='gene_ids', right_on='ensembl_gene_id', ) gene_subset.index = gene_subset['gene_name'] gene_subset.index.value_counts()

## Issues setting up anndata for SCVI
**Topic:** 2175 | **Last activity:** 2024-04-02T23:05:48Z
**Posts:** 3 | **Views:** 582 | **Created:** 2024-03-22 | **URL:** https://discourse.scverse.org/t/issues-setting-up-anndata-for-scvi/2175

**Question**: Hello scvi team, I am trying to integrate datasets using scvi in Rstudio. I used SCTransformation instead of log normalization to normalize my Seurat object. So, I extracted the RNA counts, variable features, and metadata to create a new Seurat object and converted to anndata for integration using scvi. This is the original seurat object. seurat An object of class Seurat 64931 features across 33657 samples within 2 assays Active assay: SCT (28330 features, 3000 variable features) 3 layers present: counts, data, scale.data 1 other assay present: RNA This is the new seurat object I created with RNA counts seurat_n ← CreateSeuratObject(counts = LayerData(seurat_RNA, layer = “counts”)) VariableFeatures(seurat_n) ← VariableFeatures(seurat_RNA) seurat_n@meta.data ← seurat_RNA@meta.data seurat_n[ …

**Reply (@cane11)**: The model will train anyhow, so it’s a warning not an error. You need to change the format of sparsity, even easier and okay as your data is small, is to make your count object dense. Reading CSC - column sparse data row-wise (each cell) is an efficient procedure and will slow down your training.

**Reply (@sallyseullee)**: @cane11 , thanks for your guidance! I’m a bit puzzled, though. You mentioned that handling column sparse data row-wise is efficient yet might slow down training. Did you mean it could actually speed up the process? Also, could you advise on converting my data to CSR format prior to training? Creating a Seurat object with a dense matrix leads to an automatic conversion to a sparse dgCMatrix. Any tips on managing this would be greatly appreciated!

## Interpreting model history curves
**Topic:** 2156 | **Last activity:** 2024-03-23T21:32:20Z
**Posts:** 2 | **Views:** 727 | **Created:** 2024-03-13 | **URL:** https://discourse.scverse.org/t/interpreting-model-history-curves/2156

**Question**: Hello all ! I trained a PeakVI model for 50 epochs. What can you interpret using these curves from model history ? Also, can please someone explain me: What is the difference between local and global KL ? Should we look for a minimal KL local value ? (i.e, would you train for more epochs to reduce KL local ?) Why are there some peaks in train loss step ? How can be Loss so high (> 1e7) ? Is it important ? perf 1390×989 93.1 KB Thank you for your help ! Phil

**Reply (@cane11)**: I would check the ELBO curves and reconstruction_loss curves. Train loss step is a noisy estimate (it might be that some minibatches have lower loss and I would avoid interpreting it). Elbo is preferable of Loss as we use kl_warmup during model training (the weight of KL local in the total loss increases over time up to a maximum value of 1 - this is tracked in the kl_weight plot and is the reason why the kl_local loss increases and then decreases again). KL global tracks KL losses of parameters that are not computed per cell (e.g. technical variation in DestVI mdel). It depends on your downstream task whether you prefer low reconstruction loss (a good generative model) or low KL local (likely better integration). We use those curves mainly to see that training converged (Elbo reaches a pl …

## Remove outliers from trained scVI model
**Topic:** 2165 | **Last activity:** 2024-03-23T21:22:41Z
**Posts:** 4 | **Views:** 273 | **Created:** 2024-03-16 | **URL:** https://discourse.scverse.org/t/remove-outliers-from-trained-scvi-model/2165

**Question**: Thanks for the great framework! On occasion when I build a model for a particular cell type, the majority of the cells cluster together while some are severe outliers and clearly not of the same cell type. I can easily remove these cells, however then they are absent from the trained model, so I cannot load the model with that dataset or perform differential expression. Is there a simple way to update the trained model with the outliers excluded, without having to train a new model?

**Reply (@Valentine_Svensson)**: You should be able to use the model in any way regardless if you have removed some cells from the dataset. What kind of error are you seeing?

**Reply (@joseph-siefert)**: I could still use it, but the cells, which are clearly outliers, are still included and will affect analysis performed with the model. For example, if I recompute neighbors from the latent space the projections only get worse. The model still seems to still retain information regarding the outlier cells in the latent space. My concern is this also affects the batch conditioning, normalization, and DEG. Similarly, in order to perform DE I would need to do some fancy indexing to exclude the outlier cells. Would be much easier and cleaner if it was possible to update the model.

**Reply (@cane11)**: You can pass indices to most downstream tasks or an AnnData object. If you pass your filtered objects you will get the results on only those cells. In the DE function there is an ‘importance’ weighting. Enabling this downweights the effect that these outliers will have without removing those. This downweighting is described in: https://www.pnas.org/doi/full/10.1073/pnas.2209124120

## Questions about reference mapping
**Topic:** 2161 | **Last activity:** 2024-03-23T21:20:44Z
**Posts:** 2 | **Views:** 475 | **Created:** 2024-03-14 | **URL:** https://discourse.scverse.org/t/questions-about-reference-mapping/2161

**Question**: Hi, i want to ask several naive questions. I hope someone takes the time to answer. I downloaded a reference from cellxgene in h5ad format and i want to annotate my samples using that reference. First question, should I perform any pre-prossessing on that reference object, (normalize, log, scale etc. or not) ? also the samples? I did the them on the reference: adata AnnData object with n_obs × n_vars = 2480956 × 59357 obs: ‘ROIGroup’, ‘ROIGroupCoarse’, ‘ROIGroupFine’, ‘roi’, ‘organism_ontology_term_id’, ‘disease_ontology_term_id’, ‘self_reported_ethnicity_ontology_term_id’, ‘assay_ontology_term_id’, ‘sex_ontology_term_id’, ‘development_stage_ontology_term_id’, ‘donor_id’, ‘suspension_type’, ‘dissection’, ‘fraction_mitochondrial’, ‘fraction_unspliced’, ‘cell_cycle_score’, ‘total_genes’, ‘to …

**Reply (@cane11)**: Hi, you need to input raw count data to scVI. Those are usually stored either in adata.X or adata.raw.X. You do a lot of normalization here so it’s difficult to follow. Just make sure that the layer that you pass into scVI are integer count values. You need to subset the genes before inputting to scvi-tools models. You can however store a second object with subset genes and afterwards continue working with adata.

## Normalized data found instead of raw counts
**Topic:** 2163 | **Last activity:** 2024-03-18T10:46:24Z
**Posts:** 3 | **Views:** 1140 | **Created:** 2024-03-15 | **URL:** https://discourse.scverse.org/t/normalized-data-found-instead-of-raw-counts/2163

**Question**: I’m running a scRNA-seq scVI workflow and getting warnings saying that non-integers were found in the AnnData: adata.layers['counts'] = adata.X.copy() sc.pp.normalize_total(adata, target_sum=1e4) sc.pp.log1p(adata) adata.raw = adata sc.pp.highly_variable_genes( adata, n_top_genes=3000, subset=True, layer="counts", flavor="seurat_v3", batch_key="dataset", ) The warning here: /opt/conda/envs/scvi-env/lib/python3.9/site-packages/scanpy/preprocessing/_highly_variable_genes.py:64 : UserWarning: flavor='seurat_v3' expects raw count data, but non-integers were found. warnings.warn( Also for scV model setupI: scvi.model.SCVI.setup_anndata( adata, layer='counts', categorical_covariate_keys=['dataset', 'sample_name'], continuous_covariate_keys=['pct_counts_mt'] ) model = scvi.model.SCVI(adata) model …

**Reply (@ivirshup)**: Could you try: np.unique(adata.layers["counts"].data) It’s possible there are some non-integer values in there. Certain aligners will assign partial counts for ambiguous reads, which can trigger the warning.

**Reply (@f6v)**: Thanks, I concatenated multipe datasets and one of them was normalized. But it was in the end, so I didn’t catch it by checking the first rows.

## Extracting Normalized Expression from Trained Model on Variable Subset
**Topic:** 2155 | **Last activity:** 2024-03-14T20:31:18Z
**Posts:** 3 | **Views:** 317 | **Created:** 2024-03-13 | **URL:** https://discourse.scverse.org/t/extracting-normalized-expression-from-trained-model-on-variable-subset/2155

**Question**: Hello, apologies for a somewhat trivial question. I am trying to extract the normalized expression matrix from my trained model, which was done so on a subset of variable genes. I want to plot a heatmap of the expression but not all of my curated markers appear in the variable genes list used to train the model. I was under the impression I could still extract normalized expression for any gene regardless of whether it was used to train the model. Is this correct or do I need to retrain the model including genes of interest to extract their denoised-normalized expression for visualization? Thanks in advance!

**Reply (@cane11)**: Hi, scVI models can only generate gene expression for genes used during training, so yes you would have to retrain your model.

**Reply (@abbass2)**: Okay yes I thought so, just wanted to confirm. Thanks for that!

## Access to each training example's original index in the input Anndata object
**Topic:** 2153 | **Last activity:** 2024-03-12T16:18:01Z
**Posts:** 1 | **Views:** 166 | **Created:** 2024-03-12 | **URL:** https://discourse.scverse.org/t/access-to-each-training-examples-original-index-in-the-input-anndata-object/2153

**Question**: I am training scvi with augmentations. For one of my augmentations, I need access to each cell’s original index in the full input adata object. What is the best way to go about this?

## How to interpret the latent space in scVI
**Topic:** 2005 | **Last activity:** 2024-03-05T16:49:59Z
**Posts:** 7 | **Views:** 2045 | **Created:** 2024-01-15 | **URL:** https://discourse.scverse.org/t/how-to-interpret-the-latent-space-in-scvi/2005

**Question**: Hi scverse community, From what I understood, the latent space of the model is a feature that is defined prior to the training, meaning when creating the model to train. After the training, each cell can be represented in the latent space with a n-dimensional vector. Now, the latent space reproduces the statiscal properties of the original data. For this reason, it sounds a lot like a reduced dimensionality representation like a PCA. So my questions are, Can I assume that the latent dimensions (usually stored in X_scvi ) are ordered by most explained variance to least explained variance? And does it make sense then to run sc.pp.neighbors on the first e.g., 5 latent dimensions out of 10? Or, for example, would it make more sense to just train a model with 5 latent dimensions in total? Thank …

**Reply (@martinkim0)**: Unlike PCA, scVI’s latent variables are not ordered in any meaningful way nor are they interpretable since the model is not a linear method. It can just be thought of as a low-dimensional, compressed representation that the model has learned when trying to optimize its objective, i.e. , the ELBO, which includes the reconstruction loss (how well the model is able to recover the full gene counts from the compressed representation) and a KL prior term (for regularization). Regarding your second and third questions, I think it makes more sense to train the model with 5 latent dimensions instead of subsetting from a larger dimensionality, since the model effectively requires all latent variables to reconstruct gene counts. In other words, we don’t expect a subset of the latent variables to cont …

**Reply (@zvittorio)**: Thanks for the clear and complete answer!

**Reply (@gregjohnso)**: Unlike PCA, scVI’s latent variables are not ordered in any meaningful way nor are they interpretable since the model is not a linear method. I am not sure that is true. The KL divergence is a measure of information and different latent dimensions carry different amounts of information. You can compute dimension-wise KLD with the following # get latents from your data mu, sigma = model.get_latent_representation(adata=adata, return_dist=True) # the KLD function, measured latent-dimension-wise kld_per_dimension = -0.5 * np.sum( 1 + np.log(sigma) - mu**2 - sigma, axis=0, ) # sort by descending KLD kld_importance = np.argsort(kld_per_dimension, ascending=False) Sorting by descending KLD is equivalent to sorting by the information passing through the latent dimensions. A good overview of how KLD …

**Reply (@davemcg)**: Alternatively you could use LDVAE, which is more interpretable Python Linearly decoded VAE This notebook shows how to use the ‘linearly decoded VAE’ model which explicitly links latent variables of cells to genes. The scVI model learns low-dimensional latent representations of cells whic...

**Reply (@martinkim0)**: @gregjohnso Thanks for that information! This is very interesting. @zvittorio Just to clarify, the output of scvi.model.SCVI.get_latent_representation is not ordered in a meaningful way in the sense that, by default, the values in the output array themslves are not ordered, whether that be with KLD or some other measure. You could, of course, compute KLD yourself and then rearrange these latent variables.

**Reply (@zvittorio)**: OK I see. It’s understandable that some vectors in the latent representation are more “meaningful” than others. But good to know that they do not get ordered in any way by default. So, selecting a subset of them as in a PCA does not make sense if not backed up by some kind of KLD (or similar) ordering. Thanks again to all of you for the insightful comments @martinkim0 @gregjohnso @davemcg

## Explicit Access to the Training Set During scVI Training
**Topic:** 2137 | **Last activity:** 2024-03-04T10:50:08Z
**Posts:** 1 | **Views:** 160 | **Created:** 2024-03-04 | **URL:** https://discourse.scverse.org/t/explicit-access-to-the-training-set-during-scvi-training/2137

**Question**: I would like to explicitly access the training DataLoader to compute quantities things like Pearson/Spearman gene correlations, gene entropies, NearestNeighbors etc. It is important that these batches are not computed per batch , but rather on the entire training set . What is the best way to go about this?

## Unexpected Effect of Augmentations on scVI Batch Integration
**Topic:** 2136 | **Last activity:** 2024-03-02T01:08:59Z
**Posts:** 1 | **Views:** 390 | **Created:** 2024-03-02 | **URL:** https://discourse.scverse.org/t/unexpected-effect-of-augmentations-on-scvi-batch-integration/2136

**Question**: I’m experimenting with augmentations in scVI and I get some results I can’t quite explain. When applying augmentations like random gene masking, cell swaps, poisson noise etc (only for training) and on a per training step basis, I get increases in biological conservation scores (eg Leiden ARI and NMI) but decreases in batch correction scores (eg KBET). I’m sure my augmentations are correctly applied and my scores are measured with scIB metrics. The results seem to be consistent across different datasets and random seeds. Any intuition for why this happens?

## Scvi performance on nvidia h100 vs a100
**Topic:** 2120 | **Last activity:** 2024-03-01T20:52:37Z
**Posts:** 5 | **Views:** 387 | **Created:** 2024-02-25 | **URL:** https://discourse.scverse.org/t/scvi-performance-on-nvidia-h100-vs-a100/2120

**Question**: We recently ran a small internal benchmark of scvi-tools speed on 2 gpus, and it showed considerably slower results on H100 compared to A100 on the same task, same code. Have you seen something similar? Do you have any ideas about what might contribute to this or how to investigate? I used scvi-tools==1.0.4 with torch==2.1.1 Thank you

**Reply (@martinkim0)**: Hi, would you be able to send your benchmark code if possible?

**Reply (@mxposed)**: Sure, here it is. I used our internal dataset, but pretty sure it should be reproducible with pbmc 3k. import scvi import scanpy as sc import time import torch adata = sc.read_h5ad('…') sc.pp.highly_variable_genes( adata, flavor="seurat_v3", n_top_genes=1000, subset=True, batch_key="Patient" ) scvi.model.SCVI.setup_anndata( adata, layer="counts", batch_key="Patient", categorical_covariate_keys=["Chemistry"] ) model_adata = scvi.model.SCVI(adata, n_layers=2, dropout_rate=0.2, n_latent=10) train_start = time.time() model_adata.train( max_epochs=100, use_gpu=True, check_val_every_n_epoch=2, early_stopping=False ) print(f'Training on {torch.cuda.get_device_name()} took {time.time() - train_start}s')

**Reply (@martinkim0)**: Thanks. If you don’t mind, could you try using one of the built-in Lightning profilers to see where the bottleneck is? You can directly pass it into the train method. Feel free to report the results here and I can take a look. Also, what is your setup like? Are both GPUs connected to the same motherboard, or are they on different nodes? If they’re on different nodes, do they have different CPUs/data interconnects?

**Reply (@Intron7)**: Against which cuda version did you build torch?

## Incorporating augmentations (per batch) for scVI training
**Topic:** 2070 | **Last activity:** 2024-02-28T10:03:30Z
**Posts:** 12 | **Views:** 585 | **Created:** 2024-02-09 | **URL:** https://discourse.scverse.org/t/incorporating-augmentations-per-batch-for-scvi-training/2070

**Question**: I have a module of augmentations that I would like to try with an scvi.model.SCVI model. In particular, I only want my augmentations to be used during training of this model. What is the easiest method to integrate these augmentations in the training pipeline? I know I can directly modify some of the scvi codebase but I was wondering if there may already be a simpler way?

**Reply (@martinkim0)**: What kind of augmentations do you have? If they are simple enough, you could potentially re-write them as Lightning callbacks and pass them in with the callbacks argument in train() . Otherwise, depending on the complexity of the augmentations, you might have to fiddle with creating custom torch modules.

**Reply (@g12bftd)**: Hey, thanks for getting back to me. I’m considering augmentations that directly target the raw read count matrix such as: Random masking of gene expressions in the read count matrix Poisson noise added to gene expressions in the read count matrix I’m also considering augmentations that can be applied after the log-transformation in scVI. This would be things like: Gaussian noise Monotonous function transformations (e.g. linear functions, power functions etc. all with randomly sampled parameters) Note that a given transformation should occur on a per training step basis. Currently the way I’m implementing it is a separate Augmentations Class which directly modifies a given batch in the training step. I just need to add a couple of extra lines into the “training_step” function (See: scvi-too …

**Reply (@martinkim0)**: For the first set of augmentations targeting the raw read counts, I think it would be straightforward to implement those in a Lightning Callback that overrides the on_train_batch_start method, since it has access to the batch before it is passed into training_step . The only consideration would be to modify the tensors in-place as the hooks aren’t supposed to return anything. Then, you can initialize the callback and pass it into scvi.model.SCVI.train(callbacks=[...]) . For a more flexible approach, you could subclass our TrainingPlan and then override the training_step (I guess you’re doing something similar to this already). class AugmentationsTrainingPlan(scvi.train.TrainingPlan): def training_step(self, batch, batch_idx): # modify batch here return super().training_step(self, batch, ba …

**Reply (@g12bftd)**: Thanks again for the reply. Here is the approach I am now following: class AugmentationsTrainingPlan(scvi.train.TrainingPlan): def __init__(self, augmentation_fn=None, **kwargs): super().__init__(**kwargs) self.augmentation_fn = augmentation_fn def training_step(self, batch, batch_idx): if self.augmentation_fn is None: return super().training_step(batch, batch_idx) # Instantiate the Augmentation class augmentation = Augmentation(batch) # Mapping of augmentation functions augmentation_map = { "random_mask": augmentation.random_mask, "poisson_noise": augmentation.poisson_noise, "random_linear_augmentation": augmentation.random_linear_augmentation } # Apply the selected augmentation if self.augmentation_fn in augmentation_map: batch = augmentation_map[self.augmentation_fn](batch) else: raise …

**Reply (@martinkim0)**: For (2), if you want to apply augmentations after log1p, I think the most straightforward way to do this is to pass in log_variational=False to the model constructor, which will disable automatic log1p transforming, and then follow the same steps as for pre-log1p transformations and add the log1p step yourself in training_step .

**Reply (@martinkim0)**: For (1), could you instead try putting the augmentations in the on_after_batch_transfer hook instead? The API should be similar.

**Reply (@g12bftd)**: Can you please clarify what you mean here? I see there is already a definition of on_after_batch_transfer hook in the scvi.dataloaders.DataSplitter class. If my aim is to be able to define my augmentations at model initialization, I suspect there is quite a bit of work to do (but I’m happy to be proven wrong).

**Reply (@martinkim0)**: Sorry, what I meant was if you could replace training_step with on_after_batch_transfer as the hook for the training plan to see if this might fix the error you were running into.

**Reply (@g12bftd)**: I managed to solve the problem by implementing my augmentations in the on_after_batch_transfer function from the DataSplitter. I can then pass the augmentations I wish to apply onto the model.train() call. I will try to the post-log1p transformation augmentations and let you know how it goes. Thanks again. 1 more question. I would like to apply an augmentation that’s based on the sequencing technology (i.e. 10X, Smart-seq). This information is stored in my anndata object. What would be the easiest way to pass this on to the model so that I can apply, say one augmentation to 10X data and another to smart-seq data?

**Reply (@martinkim0)**: Great! Glad you were able to figure it out. If you don’t already have a batch key that you’re passing into the model, you can register the obs field with the sequencing metadata and pass it into setup_anndata(batch_key=...) . Then, you can access this information in any of the Lightning hooks that have batch as an argument by accessing batch[scvi.REGISTRY_KEYS.BATCH_KEY] , which will give you a tensor with integer-encoded values for the sequencing tech. If you already have a batch key, you can pass in this information with categorical_covariate_keys in setup_anndata , and similarly access it with REGISTRY_KEYS.CAT_COVS_KEY . The only difference is that this tensor will contain integer-encoded values for all other covariates you are passing in categorical_covariate_keys (this argument takes …

**Reply (@g12bftd)**: Hey @martinkim0 . Thanks for all the help. I fixed the post-log1p augmentations by applying them directly in the _regular_inference( ) function from the vae module, instead of applying them in the on_after_batch_transfer data hook. I have one more issue: Using Sequencing Tech (basically 2 categories) To Inform the Augmentation I already have a batch key. I want to my augmentations to be applied depending on the sequencing tech (either 10X or smart-seq). I registered the sequencing tech as a new key, but I do not want the sequencing tech to be passed on to the decoder as a covariate. I just want to use this key to inform the augmentation (e.g. if the sequencing tech = 10X, multiply read counts by 0.8, otherwise multiply read counts by some other float scale factor). I’m not sure how to regi …

## Loading model.pt in R
**Topic:** 2108 | **Last activity:** 2024-02-21T14:55:37Z
**Posts:** 1 | **Views:** 142 | **Created:** 2024-02-21 | **URL:** https://discourse.scverse.org/t/loading-model-pt-in-r/2108

**Question**: Hello, I used scvi tools in R, trained a model to integrate multiple scRNA datasets and saved it as a .pt file. How can I load it back in R to continue the analysis? seu_ann ← anndata::read_h5ad(“seu_ann.h5ad”) scvi$settings$dl_num_workers = 4L scvi$settings$num_threads = 60L scvi$settings$seed = 813L scvi$model$SCVI$setup_anndata(seu_ann) model = scvi$model$SCVI(seu_ann) model$train(model$train(early_stopping = T)) model$save(“model”, save_anndata = T) Thank you!

## Reloading saved model gives different results
**Topic:** 2042 | **Last activity:** 2024-02-20T22:23:58Z
**Posts:** 8 | **Views:** 640 | **Created:** 2024-02-01 | **URL:** https://discourse.scverse.org/t/reloading-saved-model-gives-different-results/2042

**Question**: Hello, I’m working through the c. elegans tutorial for scVI. The first run through the tutorial worked great, and I was able to replicate all the results. However, I saved the trained model and tried to reload it, and I got substantially different results. Specifically, I used the following code to save the model after training OR load the saved model, depending on the TRAIN_MODEL variable: #previous code: Import data, setup adata, following tutorial exactly TRAIN_MODEL = False model_dir = os.path.join(save_dir, "scvi_model") if TRAIN_MODEL: model = scvi.model.SCVI( adata, gene_likelihood = 'nb' ) model.train( check_val_every_n_epoch = 1, max_epochs = 400, early_stopping = True, early_stopping_patience = 20, early_stopping_monitor = 'elbo_validation', use_gpu = False, ) model.save(model_di …

**Reply (@gargerd)**: This happens in my case as well. I train the model and check the latent representation, which shows a good separation of the celltype clusters and mixing of the batch effects. However, when I save the model, re-load it and run get_latent_representation, I also get a “scrambled” representation of my cells, similarly to @pckinnunen_lbl . Update: I tested it a bit and this only happens, if I restart my kernel. If I run training-saving-loading within the same Jupyter notebook session, then the representations always look nice. However, if I restart my Jupyter kernel and then load the model, the scrambling of the cells happens. Even if I set torch.manual_seed(0) in the beginning of my script. Happens both in scvi-tools 1.0.4 and 1.1.0. @martinkim0 , any idea what we are doing wrong?

**Reply (@martinkim0)**: Not sure what might be going wrong right now - could you send a reproducible script with data? I can look into this further.

**Reply (@gargerd)**: Hey @martinkim0 , I figured the issue out… I overlooked a var_names for adata passed in does not match var_names of adata used to train the model. For valid results, the vars need to be the same and in the same order as the adata used to train the model. error. I am working given gene subsets of my reference data, and at the beginning of the script I subsetted the reference based on a list of genes. The problem was the order of the genes: every time I ran the notebook, the order of the genes was changed, and differed from the gene order from the anndata I trained on… I fixed the order of the genes and now it is working fine! @pckinnunen_lbl : Compare the genes and the order of the genes in your Anndata after loading it! If some genes are missing or the gene order in var_names is different …

**Reply (@martinkim0)**: Glad you were able to figure out the issue!

**Reply (@pckinnunen_lbl)**: @gargerd Thank you! I failed to fully examine my outputs, since I was running the notebook on the same data, in the same way, each time. However, the way the tutorial does differential gene expression using scvi.data.poisson_gene_selection(adata) is stochastic, so different genes were selected each time I ran the code. The following code snippet shows what happens (it should work on any computer, it’ll just download the packer2019 c. elegans data). import os import scanpy as sc import scvi # Get the data save_dir = 'c_elegans_tut_files' adata_path = os.path.join(save_dir, "packer2019.h5ad") adata = sc.read( adata_path, backup_url="https://github.com/Munfred/wormcells-site/releases/download/packer2019/packer2019.h5ad", ) #Make 2 identical copies of the data adata1 = adata.copy() adata2 = ad …

**Reply (@martinkim0)**: Hmm I see - could you check whether adding scvi.settings.seed = 0 leads to the same stochastic results? If not, I’ll take a look at what’s causing this.

**Reply (@pckinnunen_lbl)**: Sure! Restarting the kernel and running the same code without a seed yields different percentages of matching indices between adata1 and adata2 each time: run 1: 0.9931757491840569 run 2: 0.9932746513697953 run 3: 0.9934724557412719 If I add scvi.settings.seed = 0 , I get identical results each run. However, the differentially expressed genes between adata1 and adata2 are still different. run 1: 0.9930768469983187 run 2: 0.9930768469983187 run 3: 0.9930768469983187 So, using the seed would solve my problem. Thanks again!

## Clustering with X_scVI after removing doublets
**Topic:** 2102 | **Last activity:** 2024-02-20T02:28:39Z
**Posts:** 1 | **Views:** 220 | **Created:** 2024-02-20 | **URL:** https://discourse.scverse.org/t/clustering-with-x-scvi-after-removing-doublets/2102

**Question**: I am following instructions in SOLO to find doublets when having two batches. When I don’t care about doublets I use X-scVI latent space to cluster cells. Now that I have doublets I was wondering if I just want to cluster singlets, should I use another latent space to cluster? Since X-scVI is based on the info of all cells regardless of doublets or singlets (right?) and it doesn’t make sense to filter out cells (doublets) and still use the old X-scVI for clustering rest of cells (Singlets). What is the best strategy here? Thank you.

## Preserving biological variability in scVI sample integration
**Topic:** 2097 | **Last activity:** 2024-02-16T18:15:58Z
**Posts:** 5 | **Views:** 1290 | **Created:** 2024-02-16 | **URL:** https://discourse.scverse.org/t/preserving-biological-variability-in-scvi-sample-integration/2097

**Question**: Hello scVI community! I am utilizing scVI for the first time to integrate scRNA-seq data from over 50 samples (batches). Each sample in my dataset also corresponds to biological variables of interest, being age. I am concerned that there may be a risk that the integration might over-correct and remove the age-related biological variations. Could you advise on how to configure the scVI to recognize age as a critical biological variable, while correcting for technical batch effects? Also, my scRNA-seq data is formatted for Seurat. I noticed that the scVI tutorials typically demonstrate preprocessing with log normalization. However, considering scVI’s input is raw count data rather than normalized data, I am curious whether the choice of normalization method (log normalization or SCTransform) …

**Reply (@martinkim0)**: Hi, thanks for your questions! If you’d like the model to account for continuous covariates in your data such as age, you may pass in the corresponding AnnData.obs keys with the continuous_covariate_keys argument in scvi.model.SCVI.setup_anndata . This will, by default, concatenate these continuous values to the latent representation and then pass in that combined vector to the decoder. Correct, scVI expects raw counts as input. We typically compute log-normalized counts in tutorials for downstream functions such as PCA-UMAP visualization, but you’ll notice that we feed in the raw counts only to scVI. We don’t recommend passing in log-normalized or otherwise transformed data to scVI as these values will be out-of-distribution for the decoder.

**Reply (@sallyseullee)**: Hi @martinkim0 , thank you so much for the prompt response! Regarding your suggestion for my first question, the age variate consists of discrete integer values ranging from 1 to 50. Given that these are not continuous measurements but rather distinct age categories, should I represent these age values as floating-point numbers (e.g., 1.0 to 50.0) to imply continuity? Or is there an alternative approach within scVI that better accommodates discrete variables like age groups? Thank you again!

**Reply (@martinkim0)**: I think it makes sense to convert these age values to floats since there is a sense of orderedness, and we’d like the model to treat them as such. What do you think @cane11 ?

**Reply (@cane11)**: I would recommend treating your samples (donors) as batch_key in scVI and not feeding in additional covariates. In my hands, feeding in additional covariates can lead to overcorrection. For downstream analysis, we used age groups to study differences in Multimodal profiling reveals tissue-directed signatures of human immune cells altered with age - PubMed . You can see in this publication downstream analysis to distinguish aging features. We used MrVI there but scVI will likely work to identify cell-types etc. For DE analysis, I would use pseudobulk DE. ContrastiveVI within scVI-tools 1.1 could be also an interesting model to study aging but I have no experience there.

## Trouble with scvi environment from reticulate in R to run seurat pipeline
**Topic:** 2068 | **Last activity:** 2024-02-16T17:59:26Z
**Posts:** 2 | **Views:** 699 | **Created:** 2024-02-09 | **URL:** https://discourse.scverse.org/t/trouble-with-scvi-environment-from-reticulate-in-r-to-run-seurat-pipeline/2068

**Question**: Hi, I am on a MacOS Ventura, M2 Max , I have installed conda in the terminal by: brew install --cask mambaforge curl -L -O “httpgithub(dot)com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh” bash Miniforge3-MacOSX-arm64.sh Said yes to everything. conda create -n scvi-env python=3.10 conda activate scvi-env Got a “/Users/mainuser/miniforge3/envs/scvi-env/” conda install -c conda-forge r-base r-essentials r-reticulate Then followed the Integration Seurat5 vignette Integrative analysis in Seurat v5 • Seurat Loaded these packages… library(Seurat) library(SeuratData) library(SeuratWrappers) library(Azimuth) library(ggplot2) library(patchwork) library(reticulate) library(SeuratDisk) library(harmony) library(ggplot2) library(patchwork) options(future.globals.maxSize = 1 …

**Reply (@martinkim0)**: Hi, sorry you’re running into this issue. Could you try upgrading to the newest version of scvi-tools (1.1.0) and seeing if this issue persists?

## How to compute the integration metrics
**Topic:** 2066 | **Last activity:** 2024-02-16T17:58:19Z
**Posts:** 2 | **Views:** 297 | **Created:** 2024-02-08 | **URL:** https://discourse.scverse.org/t/how-to-compute-the-integration-metrics/2066

**Question**: Hi, I want to ask how to compute integration metrics, such as ARI, normalized mutual information, graph connectivity, batch LISI (iLISI), cell-type LISI (cLISI) and so on? Cause I can’t find the related code on GitHub and Zenodo. I want to if the raw data has the label annotated by experts as the ground truth? For example, best to my knowledge, I think the ARI should be computed by the predicted clusters and the raw data true labels(ground truth), if I just cluster the raw data for original labels and compute it with predicted clusters for ARI, I think the metrics is not convincing right?

**Reply (@martinkim0)**: For computing integration metrics, you may refer to scib-metrics or the original implementations in scib .

## Error when training model on M3 Max MPS
**Topic:** 1896 | **Last activity:** 2024-02-16T17:45:46Z
**Posts:** 6 | **Views:** 1273 | **Created:** 2023-11-17 | **URL:** https://discourse.scverse.org/t/error-when-training-model-on-m3-max-mps/1896

**Question**: Hi there, I ran into an error when trying to train a model on M3 Max MBP. Python version is 3.10 with nightly Pytorch build: ValueError: Expected parameter loc (Tensor of shape (128, 10)) of distribution Normal(loc: torch.Size([128, 10]), scale: torch.Size([128, 10])) to satisfy the constraint Real(), but found invalid values: tensor([[nan, nan, nan, …, nan, nan, nan], [nan, nan, nan, …, nan, nan, nan], [nan, nan, nan, …, nan, nan, nan], …, [nan, nan, nan, …, nan, nan, nan], [nan, nan, nan, …, nan, nan, nan], [nan, nan, nan, …, nan, nan, nan]], device=‘mps:0’, grad_fn=) I would like to know if this issue is specifically because I am using a beta version of Pytorch or because I am doing something wrong with the script. I am new to Python sc-seq analysis, so I apologize in advance if this qu …

**Reply (@martinkim0)**: Hi, we’ve had some issues with NaNs in MultiVI and gimVI, are you using either of those models by chance? If so, I’d try downgrading to scvi-tools==0.20.3 and checking if the issue still persists. I’ll also note that our models are not fully compatible with PyTorch MPS builds as the lgamma kernel is not supported with that backend yet, but based on the traceback, that doesn’t seem to be the source of the error here.

**Reply (@sshinBRC)**: Thank you for the response! I am only using scvi.model.SCVI and I have found that I do not get any errors when I use the CPU instead. Also, scvi-tools==0.20.3 gives the same error as before. I suppose this is a compatibility issue Thanks again for your time!

**Reply (@martinkim0)**: Sorry about that! We’re also looking forward for PyTorch to add full compatibility with MPS, so we’ll be testing on our end to see when that is available.

**Reply (@TaniaThimraj)**: I have the same issue.

**Reply (@martinkim0)**: Please refer to the following thread: Macbook M1 M2 mps acceleration with scVI - #4 by martinkim0

## Batch correction using scvI on multiple datasets + hyperparameter tuning of an scvI model
**Topic:** 2076 | **Last activity:** 2024-02-16T17:45:21Z
**Posts:** 2 | **Views:** 371 | **Created:** 2024-02-11 | **URL:** https://discourse.scverse.org/t/batch-correction-using-scvi-on-multiple-datasets-hyperparameter-tuning-of-an-scvi-model/2076

**Question**: I want to perform batch integration on multiple datasets (loaded as separate h5ad files). Is there an exemplar code snippet on how to do this? Once I’ve loaded and pre-processed the data, what is the best way to rigorously perform hyperparameter tuning of the scVI model?

**Reply (@martinkim0)**: For concatenating and integrating multiple datasets, please refer to this tutorial that combines two datasets. For an example on how to perform hyperparameter tuning with scVI, please refer to this tutorial

## Running totalVI by batch
**Topic:** 2087 | **Last activity:** 2024-02-16T17:41:35Z
**Posts:** 2 | **Views:** 262 | **Created:** 2024-02-14 | **URL:** https://discourse.scverse.org/t/running-totalvi-by-batch/2087

**Question**: Hi! Thank you for the great program. I’ve been using totalVI very often on small datasets (~40 samples) with no problem. Recently we’ve acquired a CITE+RNA dataset of more than 100 samples with 10,000 cells each. The data was generated in pools of 4-5 samples each and batches of 4 pools (~20 samples). I believe totalVI has to be run on the full data at once, but the size of the dataset is making it difficult, reaching our computing limit. If running totalVI by batch is not an option, what would you recommend to make it less challenging? Any help would be much appreciated! Thank you again for the amazing program.

**Reply (@martinkim0)**: Hi, thanks for your question. How long does it currently take to train totalVI on the full dataset? Or are you running into memory issues with loading the whole data? If your main concern is the total runtime of the algorithm, you could try the following to potentially speed up training time: Since early_stopping is enabled by default in TOTALVI , you can modify its parameters such as early_stopping_patience , which controls the number of epochs before early stopping kicks in. Lowering this value will most likely decrease the number of training epochs. See more here . This should be adjusted after inspecting the validation loss. Increase the batch_size . The default is set to 256 , which is typically not enough to maximize GPU memory. Increasing this value and monitoring GPU utilization ca …

## Failure to remove a batch_key/ effect of number of LVs
**Topic:** 1973 | **Last activity:** 2024-02-09T16:30:02Z
**Posts:** 7 | **Views:** 708 | **Created:** 2024-01-01 | **URL:** https://discourse.scverse.org/t/failure-to-remove-a-batch-key-effect-of-number-of-lvs/1973

**Question**: Hello. I have a dataset containing cells(700k) from two different conditions: unstimulated and stimulated with a virus. I noticed that when I set the batch_key to “condition”, scVI was unable to remove the batch effect, as the cell types were clustered based on the stimulation condition. This is evident in the UMAP plot, which shows that the cells are clustered by stimulation condition rather than cell type. What can I do to address this issue? does chaning the number of used HVG could affect this ? Does the number of latent variables and layers scale with the number of cells , should I specify more LVs and layers if I have more cells? i saw when i increased the n_epochs the result where a bit diffrent also, ideally shall i go for much higher epochs since i got alot of cells? Thanks

**Reply (@Marwansha)**: here is a umap colored by celltype and conditions that i wanted to remove its effect(normal workflow of pca/knn/umap yield a similary umap) MicrosoftTeams-image (2) 1312×471 58.7 KB

**Reply (@Marwansha)**: increasing the epochs until convergence ( using early stopping) still couldn’t remove the batch effect of the condition.

**Reply (@Valentine_Svensson)**: Hi Marwansha, Are all your 700k cells from just two samples / batches that are confounded with your virus treatment? Integration of samples with scVI tend to work better if you include all samples / batches. For example, if you have 8 untreated samples, and 8 treated samples, for a total of 16 samples but with 2 conditions – then integration typically works better if you give the ‘sample’ as batch_key than if you give ‘condition’ as batch_key . WIth only 700k cells, I think the default of 10 latent variables should be sufficient. When there are many more cells increasing LVs can help, but necessarily for batch integration, which tend to benefit from a small ‘bottleneck’. Hope this helps! /Valentine

**Reply (@Marwansha)**: Thank you alot for your response. My library design was quite complex, with each library containing samples from different individuals at different conditions (one individual from same library was stimulated with a virus, while other was not) followed by demultiplexing the cell identities using genotyping data the visualization shows distinct clustering and separation of each cell type based on the condition with no library batch effect. I was trying to remove this separation using scVI. I tried a variety of model settings For instance, I tried different numbers of latent variables (10, 20, 30, 50, 10), number of layers (1, 2, 4, 10), dispersion settings (gene, gene-batch), and gene likelihood models (Zinb and nb). all models reach convergence ( Early stopping option ) *Do you have any sug …

**Reply (@Valentine_Svensson)**: Hi Marwansha, Since you want to account for (‘remove’) variation due to ‘condition’, the ‘condition’ indicator should be part of your ‘batch’ in the batch correction. Did you try this? For example, if you have one column ‘individual’ and another column ‘condition’ in your adata.obs , you can make a new column adata.obs['individual_condition'] = adata.obs['individual'] + '-' + adata.obs['condition'] , then use 'individual_condition' as batch_key when setting up the model. The choice of how to group cells with the batch_key argument will have a much larger effect than latent dimensionality, number or layers or other technical settings. I would be interested in seeing how your UMAP changes with different choices for what you put in the batch_key ! Hope this helps, /Valentine

**Reply (@Marwansha)**: Hi Valentine, just to let you know i tried excatly what u suggested and i think scvi / scanvi failed to remove this strong condition effectop( which is mainlya biological effect, stimulated and unstimulated cells) i know its a tool effect since after i switched to harmony and it worked normal. i would be happy to try again with any specific suggestion for the model parameters you would offer. Thanks Marwan

## Scvi and subtyping
**Topic:** 1967 | **Last activity:** 2024-02-09T06:11:21Z
**Posts:** 2 | **Views:** 612 | **Created:** 2023-12-22 | **URL:** https://discourse.scverse.org/t/scvi-and-subtyping/1967

**Question**: I had a question regarding subclustering clusters and the scvi model. Specifically, I wanted to subcluster some immune cells in my sample to get some important subtypes we are interested in. However, I’m unsure whether I should retrain a new model on the subset of immune cells, or whether I can use the previously trained model. Also, I wanted to check if I am understanding the differential expression module correctly, the module requires the model to be trained, correct? Or does it perform inference independent of the training.

**Reply (@Valentine_Svensson)**: Hi LinearParadox, I would subcluster using the original embeddings for the cell type you want to subcluster. The ‘resolution’ of the SCVI embedding space is quite high. For visualization, I would fit a new UMAP/TSNE/MDE on the original embeddings for the subset of cells. These will fill out the 2D plot space with the cells you give them, making it more clear which cells are pairwise neighbors in the embedding space. Regarding differential expression: yes, the model needs to be trained to give meaningful results. It uses the inference network (encoder) to obtain uncertainty for cells from the different conditions, and the decoder is used to map the uncertainty to gene expression values. Hope this helps! /Valentine

## How to save intermediate checkpoints?
**Topic:** 1720 | **Last activity:** 2024-02-03T19:46:14Z
**Posts:** 4 | **Views:** 535 | **Created:** 2023-08-29 | **URL:** https://discourse.scverse.org/t/how-to-save-intermediate-checkpoints/1720

**Question**: What is the standard way of saving intermediate states during model training? We came up with a workaround ( here ) using PyTorch lightning callbacks as indicated in the documentation ( here ), but that largely seems unsupported and completely hacky. Is there a way to periodically save checkpoints during training that is natively supported by scvi-tools, and also retains trainer state?

**Reply (@martinkim0)**: Hi @gregjohnso , thank you for your question. We don’t have a super straightforward way of saving intermediate checkpoints as of right now. I’ll see if I can implement a solution for this for our next release - for now, you can track the feature request here: Add changes to make saving intermediate checkpoints easier · Issue #2264 · scverse/scvi-tools · GitHub

**Reply (@martinkim0)**: Hi @gregjohnso , just wanted to update you that we now have an experimental SaveCheckpoint callback that subclasses Lightning’s ModelCheckpoint for compatibility with our model saves. You can enable this automatically by passing in enable_checkpointing=True into most train methods, or passing it in explicitly with the callbacks argument. We are anticipating to release this by the end of the year with our 1.1 release. In the meantime, feel free to install from the main branch - feedback is appreciated!

**Reply (@gregjohnso)**: awesome thank you @martinkim0 !

## Using a model with categorical_covariate_key instead of batch_key
**Topic:** 1993 | **Last activity:** 2024-02-01T15:30:46Z
**Posts:** 3 | **Views:** 720 | **Created:** 2024-01-09 | **URL:** https://discourse.scverse.org/t/using-a-model-with-categorical-covariate-key-instead-of-batch-key/1993

**Question**: Hi Martin, I am currently using scvi-tools reference mapping with scArches to integrate a query data set with a reference data set that has an existing scVI model. I am at the step where I create a new query model instance, but I have encountered the following error: NotImplementedError: scArches currently does not support models with extra categorical covariates. This error arises because I used one ‘categorical_covariate_key’ in my original model instead of a ‘batch_key’. This package seems to only recognize ‘batch_key’. The reason I chose to use ‘categorical_covariate_key’ is because the scvi-tools quick start tutorial first suggests to use ‘categorical_covariate_key’ (and only after suggests that ‘batch_key’ may also be used if there is only one key). I am trying to avoid running a new …

**Reply (@martinkim0)**: Hi @jflusche , it should be possible to transfer a categorical covariate to a batch key when loading in a model for scArches, but it would require delving a bit into the codebase. Let me get back to you with a code snippet to make this work.

**Reply (@jflusche)**: Quick update: I found that the same issue exists in both scvi and scanvi in the load_query_data functions.

## AttributeError: module 'jax' has no attribute 'Device'
**Topic:** 1463 | **Last activity:** 2024-01-31T15:17:24Z
**Posts:** 10 | **Views:** 5721 | **Created:** 2023-05-25 | **URL:** https://discourse.scverse.org/t/attributeerror-module-jax-has-no-attribute-device/1463

**Question**: Hey everyone, When I install scVI as described in your documentation, I get an error following import. I attached a screenshot of the error log. Thanks in advance for any help you can afford! image 1920×949 92.3 KB

**Reply (@martinkim0)**: Hi, could you run pip install --upgrade jax jaxlib chex ?

**Reply (@wbrett87)**: Hi Martin, Thanks for getting back to me! I will try this when I get home tonight!

**Reply (@Florian_Deckert)**: I encountered the same issue after upgrading scvi-tools from 0.16 to 0.20.3. Your suggestion worked nicely. Many thanks!

**Reply (@alexanderchang1)**: Hi, This solution no longer works as it upgrades Jax and Jaxlib to versions that no longer have ShapedArray - resulting in the following error. ImportError: cannot import name ‘ShapedArray’ from ‘jax’

**Reply (@martinkim0)**: Hi, what version of scvi-tools do you have installed?

**Reply (@alexanderchang1)**: Hi, 0.20.3 Best, Alex

**Reply (@martinkim0)**: Could you please update to the latest stable release (1.0.4) and check if the issue persists?

**Reply (@alexanderchang1)**: Hi, That fixed it. It required both an upgrade to the latest version of scvi-tools as well as flax. Best, Alex

**Reply (@sdettle)**: Hi all, I recently upgraded my scvi-tools to the 1.0.4 release as described above as I was experiencing the same errors (The errors only went away when I resorted to making a whole new conda environment with: conda create --name new_scvi_tools scvi-tools==1.0.4 --channel=conda-forge), but now when I run the code: model.differential_expression( groupby=SCVI_CLUSTERS_KEY, group1=group1, group2=group2, weights = ‘importance’ # This is from the 2023 paper describing lvm-DE is better #also this is log2 fold change returned ) It takes forever: as of writing this it has been over 12 hours of compute. Previously this used to take only about a minute (weights=‘uniform’ #the default) as I only have ~7k cells (All genes however). Is this because I recently upgraded my scvi-tools to 1.0.4 and my model …

## GIMVI, label specification for single cell and spatial data
**Topic:** 2034 | **Last activity:** 2024-01-28T01:14:38Z
**Posts:** 1 | **Views:** 338 | **Created:** 2024-01-28 | **URL:** https://discourse.scverse.org/t/gimvi-label-specification-for-single-cell-and-spatial-data/2034

**Question**: Hello, I noticed in the tutorial for GIMVI there is an option for specifying the labels in each dataset: Python Introduction to gimVI Imputing missing genes in spatial data from sequencing data with gimVI: Preparing the data: In this section, we hold out some of the genes in the spatial dataset in order to test the imputation res... I’m wondering whether this is supposed to be the cluster labels, as in each dataset was clustered prior and for some reason that clustering info may be useful in the imputation process. or whether these cluster labels should be putative annotations that roughly match each other, like whether I could identify similar cell types across the datasets and they should be labeled the same name. I didn’t see anything about cluster labels in the paper, so ultimately I’m …

## Preparing data for training of a classifier while preserving biological signal
**Topic:** 2033 | **Last activity:** 2024-01-27T22:15:53Z
**Posts:** 1 | **Views:** 199 | **Created:** 2024-01-27 | **URL:** https://discourse.scverse.org/t/preparing-data-for-training-of-a-classifier-while-preserving-biological-signal/2033

**Question**: Hi, I want to train a classifier (probably something tree based) to determine sex based on expression of certain genes. My training material are multiple datasets. To prepare datasets I would like to remove batch effects while keeping sex-specifc differences. My batches and sex are confounded, as every sample was prepared separately. If I run scvi will it also eliminate the differences I am interested in or can I do something to prevent this? Thanks a lot!

## Label Transfer Discrepancy in scANVI Model Training
**Topic:** 2011 | **Last activity:** 2024-01-22T19:24:53Z
**Posts:** 3 | **Views:** 548 | **Created:** 2024-01-22 | **URL:** https://discourse.scverse.org/t/label-transfer-discrepancy-in-scanvi-model-training/2011

**Question**: Hello All, I am currently working on training a model using scANVI, and I have encountered a puzzling situation regarding label transfer. Here’s a brief overview: Reference data: 200,000 cells with 3 labels. Query datasets: Three sets with varying sizes (500,000 cells, and two with close to 800,000 cells each). The issue arises when I perform label transfer using the same set of parameters for the three different query datasets separately. The reference prediction accuracy varies across these datasets. Here’s an example to illustrate: Query data 1: Class label 1: 0.98 Class label 2: 0.94 Class label 3: 0.99 Query data 2: Class label 1: 0.88 Class label 2: 0.92 Class label 3: 0.91 Query data 3: Class label 1: 0.77 Class label 2: 0.89 Class label 3: 0.88 My question is, why am I observing di …

**Reply (@martinkim0)**: Maybe I’m not understanding your code correctly, but it looks like you’re setting all labels to "Unknown" in the reference data. I am referring to this line: adata.obs[name_of_the_new_col] = "Unknown" Could you clarify what’s going on here? To also clarify my understanding of the issue, are you doing additional training with the query data and then performing prediction on the reference dataset?

**Reply (@AkilaRanjith)**: Hello, I would like to clarify the following code snippet: name_of_the_new_col = "celltype_scanvi" adata.obs[name_of_the_new_col] = "Unknown" In this part of the code, I am creating a new column named “celltype_scanvi” in the AnnData object ( adata ) to store prediction labels. Initially, before training, all labels in this column are set to “Unknown.” After training and obtaining prediction results, this column will be updated with the predicted labels. ref_mask = adata.obs["ds_ID"] == "ref" adata.obs[name_of_the_new_col][ref_mask] = adata.obs.SORT[ref_mask].values Following that, a Boolean mask ( ref_mask ) is created to filter rows where the “ds_ID” is equal to “ref.” Subsequently, the values in the “celltype_scanvi” column for these rows are replaced with the corresponding values from …

## Differential expression and rarely expressed genes
**Topic:** 1998 | **Last activity:** 2024-01-20T16:02:41Z
**Posts:** 2 | **Views:** 360 | **Created:** 2024-01-13 | **URL:** https://discourse.scverse.org/t/differential-expression-and-rarely-expressed-genes/1998

**Question**: Hi all, When I’m doing differential expression on a subset of my cells (specifically cancer cells between various treatment and resistance conditions), a lot of genes come up as differentially expressed. However, when I inspect them, many of these genes are only expressed in <1% of the cells in some condition, and not expressed at all in another condition or also expressed at similarly low levels. I’m currently filtering by proportion of nonzeroes for genes expressed in at least 30% of the cells. I’m worried though that this may indicate something wrong with the model marking these genes as DE, or if I should be feeding some params to make sure this doesn’t happen. I already tried using a pseudocount of 1e-6, as well as automatic delta, importance weighing, and filtering outlier cells. I t …

**Reply (@cane11)**: Hi, indeed we usually run scVI DE after selecting highly variable genes and subset to only those genes. It makes sense to filter the results afterwards to only expressed genes in most cases. 30% is rather high and I usually use max(percent expressing in group 1, percent expressing in group 2) and set the threshold to 5%. A similar result is yielded when filtering all genes with an estimated scale below 1e-4.

## Encountering Error in Label Transfer : Query Dataset Slightly Larger than Reference Dataset
**Topic:** 1988 | **Last activity:** 2024-01-11T02:12:09Z
**Posts:** 4 | **Views:** 367 | **Created:** 2024-01-08 | **URL:** https://discourse.scverse.org/t/encountering-error-in-label-transfer-query-dataset-slightly-larger-than-reference-dataset/1988

**Question**: Hello All, I am working on labeling the transfer dataset using scANVI, where the reference file contains 460,000 cells, and the query file contains 656,000 cells, both from the same brain region. The reference dataset comprises 65 cell types, and I expect the same cell types in the query data. Our goal is to transfer labels from the reference to the query data. However, I am encountering an error message during the prediction process. version scvi-tools: scvi-tools 1.0.0 Code: lvae=scvi.model.SCANVI.from_scvi_model(vae,adata=adata,unlabeled_category = "Unknown", labels_key = name_of_the_new_col,linear_classifier=True) lvae.train(max_epochs=200,n_samples_per_label=1000) ValueError: Expected parameter loc (Tensor of shape (128, 30)) of distribution Normal(loc: torch.Size([128, 30]), scale: t …

**Reply (@martinkim0)**: Hi, sorry you’re experiencing this issue. Is the error occurring in the first epoch of training or sometime after? In addition, could you try out the following potential fixes and let me know if any of them work? Downgrade to scvi-tools 0.20.3 Set scvi.settings.seed = 0 before training Set linear_classifier=False Set n_samples_per_label to something much lower, maybe like 50 Pass in var_activation=torch.nn.functional.softplus when initializing SCVI

**Reply (@AkilaRanjith)**: Thank you for your suggestion. I attempted your advice by maintaining linear_classifier=False and decreasing n_sample_per_label to 100. However, the prediction failed at 52 epochs, and the same error persists. ValueError: Expected parameter loc (Tensor of shape (128, 30)) of distribution Normal(loc: torch.Size([128, 30]), scale: torch.Size([128, 30])) to satisfy the constraint Real(), but found invalid values: tensor([[nan, nan, nan, ..., nan, nan, nan] Is there is any way to figure out? Thanks Akila

**Reply (@martinkim0)**: Were you able to try out the other suggestions too? I would give them a try if possible. In general, it’s hard to unambiguously diagnose NaN errors since they can be due to a combination of the model architecture, the stability during training, and the quality of the data. If the other points I suggested don’t work out for you, I would recommend plotting some quality metrics in your dataset such as number of genes expressed per cell, number of cells expressing a gene, observed library size per cell, etc, and doing additional preprocessing as needed.

## scVI dropout, need for it?
**Topic:** 1991 | **Last activity:** 2024-01-10T17:38:33Z
**Posts:** 3 | **Views:** 412 | **Created:** 2024-01-09 | **URL:** https://discourse.scverse.org/t/scvi-dropout-need-for-it/1991

**Question**: If any of the team working on scVI could help this query that’d be amazing. I am just checking whether I am right in my interpretation of the base code, that the dropout occurs both in the encoder and decoder layers? If that is the case, I just wanted to check if any internal validation works have been done on performance dependent on dropout values? My vague understanding of VAEs (which isn’t particularly good), is that dropout isn’t necessarily a good thing? as it may affect the latent representation. From a small trial of my data, it seems the umap embeddings look “better” when it is set to zero. I know this isn’t a good way of judging a model, but there aren’t really any consensus metrics and I find that autotune embeddings (while optimise for the lowest loss value), often result in ov …

**Reply (@martinkim0)**: I believe we only have dropout by default in the encoder (see the encoder code here and decoder here ). We include dropout in scVI primarily for regularization - in other words, it’s helping the model not overfit on the training dataset. Of course this depends on the data, but generally speaking removing dropout leads to an increase in the validation loss and/or worse embeddings on the validation set, while decreasing training loss. If you see that removing dropout leads to better visualization of the data, then go for it, I don’t see anything wrong with that. I would just be careful that the model is performing adequately on the validation set.

**Reply (@Nusob888)**: Thanks Martin, you were right, the validation loss was worse. Thanks, this was helpful

## Attribute Error while training simplescvi on tutorial lung data. Differences to full scvi?
**Topic:** 1985 | **Last activity:** 2024-01-09T08:00:10Z
**Posts:** 3 | **Views:** 287 | **Created:** 2024-01-08 | **URL:** https://discourse.scverse.org/t/attribute-error-while-training-simplescvi-on-tutorial-lung-data-differences-to-full-scvi/1985

**Question**: Hej! Great package and impressive work! I want to dive into some simple method development based on the scvi integration and found this simple-scvi code to start from: GitHub - scverse/simple-scvi: Example repo of using scvi-tools building blocks externally with simplified scVI implementation Just to get it running and get a feeling for it I wanted to run it on the lung data used in the atlas-level integration tutorial ( Atlas-level integration of lung data — scvi-tools ). But following the tutorial, just not with the normal scvi but this simple scvi model, I get the following Error while running model.train: AttributeError: 'NoneType' object has no attribute 'numel' image 1609×706 52.7 KB Any Idea what the error is about ? And what are the main differences between the full version of scvi …

**Reply (@martinkim0)**: In terms of model architecture, both models are identical I believe. The main difference is that the simpler version does not include additional analysis functions such as differential expression, etc. The code hasn’t been tested/updated in a while, so it’s likely that there’s some bug there. In terms of the user API, both models are identical, so I would recommend going for the normal scVI if your intention is to get a feel for how it works. Nevertheless, I’ll take a look at the repo and fix the bug if possible.

**Reply (@luschaef)**: hej, thanks a lot for your super quick response and help! As I want to build my own model at some point, I thought the simple scvi would be an easier model to start with, but I will also have a look on the source code of the normal scvi then! would be awesome if you would manage to fix the bug. Thank you!!

## Adding cycle consistency loss and VampPrior to scVI
**Topic:** 1987 | **Last activity:** 2024-01-09T07:09:26Z
**Posts:** 3 | **Views:** 225 | **Created:** 2024-01-08 | **URL:** https://discourse.scverse.org/t/adding-cycle-consistency-loss-and-vampprior-to-scvi/1987

**Question**: We were considering adding cycle consistency loss and VampPrior (see Integrating single-cell RNA-seq datasets with substantial batch effects | bioRxiv ) to scvi-tools as a separate model or if possible to scVI directly as an add-on functionality. Would especially the latter be of interest? If yes, could we further discuss implementation choices as the current implementation deviates a lot from the scvi-tools backbone and is also based on an old version of it.

**Reply (@martinkim0)**: Hi, we’re definitely interested - could you actually submit an issue in our GitHub repo instead since this topic is more appropriate there, and then we can discuss further? Thanks!

**Reply (@Hrovatin)**: Added here: Adding cycle consistency loss and VampPrior to scVI · Issue #2383 · scverse/scvi-tools · GitHub

## Denoising/remove ambient RNA with scAR then scvi modeling?
**Topic:** 1971 | **Last activity:** 2024-01-06T23:38:05Z
**Posts:** 4 | **Views:** 887 | **Created:** 2023-12-28 | **URL:** https://discourse.scverse.org/t/denoising-remove-ambient-rna-with-scar-then-scvi-modeling/1971

**Question**: Hello, I am working with multiple 10x prepped samples. I would like to remove ambient RNA using a scAR model. Considering you must provide the raw feature matrix and filtered gene matrix to do this, my plan was to do this scAR ambient removal first for each sample, then concatenate each of these objects into a singular adata object. From here is it feasible to train an scvi model on the denoised counts and cluster, do differential gene expression, and do doublet predcition, etc from here? My question is, is this the appropriate way to do this type of analysis? I know I can use SoupX to achieve the same denoised counts, but I would prefer to stay entirely in python if possible.

**Reply (@ergonyc)**: Hi there. I have not done this, but you’ve outlined the basic workflow I’ve been considering. I’m trying to make an alternative to an R based workflow which uses scrublet, and SoupX on the individual sample data objects. And harmony on the merged data. So I was thinking: SOLO-> scAR → scVI. So far I’ve just been testing scrublet → scVI and it does okay. I found your post when searching for examples of people using a full scvi-tool examples. If I make progress with scAR (and / or SOLO) I’ll check back here. best, Andy

**Reply (@scuser)**: Hi, Glad to hear others are thinking about this. I actually went through with this and have a pipeline working and it seems to work well. I went scAR → doubletdetector (python package), removed the doublets ,and saved the raw and denoised counts to new layers, and overwrote the adata.X with the denoised counts. Then I concatenated these into one large adata object and trained an scvi model on it, and clustered off the latent space. I have the code working if you have any questions let me know and I’m happy to share how I went about it

**Reply (@ergonyc)**: Great to hear its working for you! If you’re able to share a working example, I’m sure everyone would benefit from seeing the proof of concept. I’ll be instantiating something in the next few weeks. Quick question: Can you say why you are using doubletdetector vs. scrublet or SOLO? I’d love to start to get some insight around the strengths and weaknesses of the different methods. I’ll start with anecdotes as a start towards some solid benchmarks. best, Andy

## Interpretation and visualization of MrVI output?
**Topic:** 1856 | **Last activity:** 2024-01-06T17:35:07Z
**Posts:** 2 | **Views:** 398 | **Created:** 2023-11-06 | **URL:** https://discourse.scverse.org/t/interpretation-and-visualization-of-mrvi-output/1856

**Question**: MrVI is very much needed to understand sample heterogeneity. I ran MrVI successfully as shown on the github pages. But I don’t know how to interpret or visualize the outcome. I’ve read that a tutorial for this MrVI version is not planned MrVI input and interpretation and that reimplantation of MrVI will soon come mrVI hyperparameter tunning . However, for a project soon to be published it would be great to have some guidance how to interpret and visualize the z and u representations or the cell sample representations or distances. Or is this major update of MrVI including tutorials a matter of days, if i may ask? @Justin_Hong maybe? Thank you!

**Reply (@mihem)**: This post has been banned for 1 1/2month. Not sure why it took so long to review or why it was hidden, but my question was already answered here MrVI input and interpretation - #12 by Justin_Hong

## Option to plot separate umaps for concatenated datasets
**Topic:** 1955 | **Last activity:** 2023-12-27T17:49:06Z
**Posts:** 5 | **Views:** 1449 | **Created:** 2023-12-13 | **URL:** https://discourse.scverse.org/t/option-to-plot-separate-umaps-for-concatenated-datasets/1955

**Question**: Is there an option/argument that can be passed to sc.pl.umap to plot separate UMAPs based on a categorical variable i.e. batch,sample etc. Something like the “split.by” argument in Seurat. Thank you, Ishwar

**Reply (@Dorobou)**: Hello Ishwar, this is how I plot my umaps of 4 samples: sc.pl.umap(adata, color = [‘leiden’, ‘Sample’], frameon = false, legend_loc = ‘on data’)

**Reply (@ishwarvh)**: Thank you for your reply. I am not sure if this does what I am looking for. AFAIK, this just plots 2 plots which contain cells from all 4 of your samples. Correct me if I am wrong, but does this split your merged object into 4 plots each with its leiden clusters and sample name?

**Reply (@Dorobou)**: Ishwar, you are right, the code I shared doesn’t do your request. I think I stumbled upon a code that does what you want in one of the tutorials by sambomics GitHub - mousepixels/sanbomics_scripts: scripts and notebooks from sanbomics I just can’t find it. Maybe you can check it out?

**Reply (@dub2s)**: Hii I don’t think it can be done directly. Here is what I do: fig,ax = plt.subplots(nrows=1,ncols=4) ## Assuming 4 samples for i,j in zip(adata.obs["sample"].unique().tolist(),ax.ravel()): sc.pl.umap(adata[adata.obs["sample"].isin([i])],color=["CD8A"],size=20,show=False,ax=j) plt.tight_layout() plt.show() You may need to play around a bit with size parameter. You can choose the colormaps or other specifications as you wish.

## Clustering on the scVI latent space generates only gray-colored cells
**Topic:** 1933 | **Last activity:** 2023-12-24T23:27:56Z
**Posts:** 5 | **Views:** 376 | **Created:** 2023-12-04 | **URL:** https://discourse.scverse.org/t/clustering-on-the-scvi-latent-space-generates-only-gray-colored-cells/1933

**Question**: Hi, I’d like to cluster my data on the scVI latent space using the following code: adata = sc.read_h5ad(filename='%s/%s.h5ad'%(infolder,gse)) sc.pp.highly_variable_genes( adata, n_top_genes=1200, subset=True, layer="counts", flavor="seurat_v3", batch_key="gse", ) scvi.model.SCVI.setup_anndata( adata, layer="counts", categorical_covariate_keys=["gse"], continuous_covariate_keys=['pct_counts_mt', 'total_counts'] ) os.chdir(infolder) model = scvi.model.SCVI(adata) model.train() latent = model.get_latent_representation() adata.obsm["X_scVI"] = latent adata.layers["scvi_normalized"] = model.get_normalized_expression(library_size=10e4) sc.pp.neighbors(adata, use_rep="X_scVI") sc.tl.umap(adata, min_dist=0.3) SCVI_CLUSTERS_KEY = "leiden_scVI" sc.tl.leiden(adata, key_added=SCVI_CLUSTERS_KEY, resolu …

**Reply (@martinkim0)**: Hi, I believe this is occurring because there are too many clusters in data such that there’s no way to color them clearly. One way around this would be to Leiden cluster with less granularity so that you have fewer clusters in the end.

**Reply (@cane11)**: I would assume you have very low quality cells with only a few counts after highly variable gene filtering. This creates those dispersed points in UMAP and leads to those many clusters. Please adjust the number of highly variable genes (more genes) and check your filtering for low count cells (something like 500 or 1000 should be fine for 10X v3 - different numbers for other technologies). If you want to keep your current settings, increasing n_neighbors in sc.pp.neighbors might help.

**Reply (@malonzm1)**: Thank you. I tried this.

**Reply (@malonzm1)**: Thank you. I also tried this. The dispersed points in UMAP turned out to be duplicates.

## Kernel dies when training simple SCVI on mac m3
**Topic:** 1961 | **Last activity:** 2023-12-20T14:02:32Z
**Posts:** 2 | **Views:** 364 | **Created:** 2023-12-19 | **URL:** https://discourse.scverse.org/t/kernel-dies-when-training-simple-scvi-on-mac-m3/1961

**Question**: I’m facing dying kernel on mac os (Sanorama 14.1.2 (23B2091)), chip M3 with 36GB memory. I have explored discussions on this matter but none of them work. I have create an environment using mamba to have native python but it didn’t resolved the issue. I’m using other packages in my code. An export of the env is accessible via this link. Any help highly appreciated in advance

**Reply (@mossishahi)**: @adamgayoso Hey Adam! do you have any idea about this issue?

## How to use normalised expression
**Topic:** 1963 | **Last activity:** 2023-12-19T20:32:57Z
**Posts:** 1 | **Views:** 772 | **Created:** 2023-12-19 | **URL:** https://discourse.scverse.org/t/how-to-use-normalised-expression/1963

**Question**: Hello, I would like to get some more information about the normalised expression of genes once the model has been trained. Let’s suppose that anndata is my object over which I train my model. Are the values in anndata.X the same as the original raw counts contained before training the model? How does the function get_normalized_expression work? I have seen that it returns a dataframe containing the normalised expression of genes from the decoder, but how are these values calculated? Are they the same as the ones stored in anndata.X ? Are they log-normalised? I would like to plot the expression for few genes on the umap to see which clusters express my genes of interest. Would it be okay to plot the expressions of the genes obtained from model.get_normalised_expression(gene_list=my_genes) u …

## MultiVI error on only paired data
**Topic:** 1665 | **Last activity:** 2023-12-19T18:43:45Z
**Posts:** 4 | **Views:** 551 | **Created:** 2023-08-04 | **URL:** https://discourse.scverse.org/t/multivi-error-on-only-paired-data/1665

**Question**: Hello, I was following the MultiVI tutorial using the same 10x Multiome dataset in the tutorial. I removed the part where the data is split into paired data, gene expression only data, and peak only data. i.e. there’s only paired data, adata_mvi = scvi.data.organize_multiome_anndatas(adata) . Otherwise, the rest of the tutorial code is unchanged. When I start training the model, I receive the following error before the first training epoch: # First few stack traces omitted File ~/notebooks/../../scvi-tools/scvi/train/_trainingplans.py:574, in AdversarialTrainingPlan.training_step(self, batch, batch_idx) 571 else: 572 opt1, opt2 = opts --> 574 inference_outputs, _, scvi_loss = self.forward( 575 batch, loss_kwargs=self.loss_kwargs 576 ) 577 z = inference_outputs["z"] 578 loss = scvi_loss.los …

**Reply (@Joey)**: I also face this problems. I don’t know whether it’s because there are some much Nan values in the single cell data

**Reply (@niujeffrey)**: What I found is that so long as there is at least one cell with only RNA information and only one cell with ATAC information, it runs. So the workaround I applied was to copy one cell and unpair the modalities and feed them as single modality cells.

**Reply (@bsierieb1)**: I’m facing the same issue and the workaround suggested by @niujeffrey works. Below is my environment: channels: - conda-forge - bioconda - defaults dependencies: - absl-py=2.0.0=pyhd8ed1ab_0 - anndata=0.10.2=pyhd8ed1ab_0 - annotated-types=0.6.0=pyhd8ed1ab_0 - anyio=3.7.1=pyhd8ed1ab_0 - aom=3.6.1=hb765f3a_0 - appnope=0.1.3=pyhd8ed1ab_0 - arpack=3.8.0=nompi_ha3438d0_101 - array-api-compat=1.4=pyhd8ed1ab_0 - arrow=1.3.0=pyhd8ed1ab_0 - asttokens=2.4.0=pyhd8ed1ab_0 - attrs=23.1.0=pyh71513ae_1 - backcall=0.2.0=pyh9f0ad1d_0 - backoff=2.2.1=pyhd8ed1ab_0 - backports=1.0=pyhd8ed1ab_3 - backports.functools_lru_cache=1.6.5=pyhd8ed1ab_0 - beautifulsoup4=4.12.2=pyha770c72_0 - blessed=1.19.1=pyhe4f9e05_2 - blosc=1.21.5=hc338f07_0 - brotli=1.1.0=hb547adb_1 - brotli-bin=1.1.0=hb547adb_1 - brotli-python=1.1 …

## Predicting of unassigned cells using scANVI
**Topic:** 1951 | **Last activity:** 2023-12-10T19:52:26Z
**Posts:** 1 | **Views:** 376 | **Created:** 2023-12-10 | **URL:** https://discourse.scverse.org/t/predicting-of-unassigned-cells-using-scanvi/1951

**Question**: I have two questions related to scanvi and scvi model options: Using scanvi for Predicting Unlabeled Cells: I’ve trained a scvi model on 1 million cells with cell type annotations. Now, I have a proportion of unlabeled cells and would like to predict their cell types using scanvi. After initializing the scanvi model, should I use scanvi_model.predict() to achieve this? Understanding Model Parameters: In the scvi model initialization, I used the following parameters: python model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood=“nb”) I’m curious about the impact of adjusting n_latent and gene_likelihood. Could you explain how varying these parameters affects the output of the learning model? For example, using different values for n_latent and choosing a different gene_like …

## Error running ModelTuner.fit
**Topic:** 1010 | **Last activity:** 2023-12-08T03:25:14Z
**Posts:** 6 | **Views:** 642 | **Created:** 2022-12-19 | **URL:** https://discourse.scverse.org/t/error-running-modeltuner-fit/1010

**Question**: Dear the authors of scvi-tools, Thank you very much for continuing support! I have tried to run automated hyperparameter tuning using ModelTuner class functions following the instructions here : The sample codes are written as following: adata_sampled = scvi.data.synthetic_iid() model_cls = scvi.model.SCVI model_cls.setup_anndata(adata_sampled) tuner = scvi.autotune.ModelTuner(model_cls) results = tuner.fit(adata_sampled, metric=“validation_loss”) However, all the trials came up with an error, stating that: File “./scvi/autotune/_manager.py”, line 133, in _get_search_space _type = tunables[param][“tunable_type”] KeyError: ‘n_hidden’ I have checked the accompanying files of the ModelTuner class but could not figure out what caused the problem. Could you please tell me what I should do to fi …

**Reply (@martinkim0)**: Hi, thank you for your question. I am not able to replicate your issue using the latest version of scvi. Would you be able to provide the scvi-tools version you are using, and could you also run tuner.info() and post what that returns. Thanks!

**Reply (@tu.le)**: Hello Martin, hope this message finds you well. Thank you very much for your feedback! I was running scvi-tools 0.19.0 on python 3.8 and raytune 2.2.0 . I have realized that the installed scvi package did not contain the _scvi.py and _vae.py version that support autotuning. Therefore, I have updated the two (and supporting) files with their development versions retrieved from the following link: Implement a basic working ModelTuner API with Ray Tune by martinkim0 · Pull Request #1785 · scverse/scvi-tools · GitHub . However, necessary changes are still required: to _defaults.py ( BaseLatentModeModuleClass was added to make VAE class eligible for model’s hyperparameter scanning), and to _vae.py to make other hyperparameters of the VAE class tunable (in the original file, only n_hidden is dec …

**Reply (@martinkim0)**: Hi, thank you for your question. Sorry about the discrepancies regarding tunable hyperparameters in the code base – it is still in progress and we are working on adding support for more hyperparameters and model classes. We have a pull request that will be released soon with v0.20.0 that will contain changes that make this process easier. This will also include tutorials on how to use this module. Regarding how train and plan keyword arguments are passed into the function, you can provide all hyperparameters (model, train, and plan) as a single dictionary in the search_space argument of ModelTuner.fit . We parse the arguments on our end so it is not necessary to provide separate dictionaries of keyword args. Hopefully this will be clear in the documentation once it is officially released.

**Reply (@tu.le)**: Hi Martin, Thanks a lot for helping to clarify the unclear points. It’s great to know that the development of autotuning modules is almost completed. It would be of great help for the community regarding the popularity of scvi-tools. I am looking forward to its release in the near future. Wish you and the scvi-tools development team a great year ahead! Kind regards,

**Reply (@JoshL)**: Hi Martin, Apologies for digging up an old thread but I was wondering how exactly one would provide train_kwargs such as batch_size in the search_space argument? Doing the following : search_space = {"batch_size": tune.choice([129, 130]), ## other arguments} is throwing an error : batch_size is invalid for SCVI. Thanks!

## scVI integration with all genes
**Topic:** 1943 | **Last activity:** 2023-12-05T19:07:58Z
**Posts:** 1 | **Views:** 376 | **Created:** 2023-12-05 | **URL:** https://discourse.scverse.org/t/scvi-integration-with-all-genes/1943

**Question**: Hello! I would like to integrate all my samples using all the genes instead of only the top 2000 most variable genes. I would do this in order to better characterise the variability and differences between my batches, and to subsequently run the differential gene expression on my cells using all the genes. However, not all the samples have the same number of genes, so that I would do the following: anndata_dir = 'C:/Users/Martina/Desktop/AnnData' list_files = os.listdir(anndata_dir) anndata_list = [] for filename in list_files: file_path = os.path.join(anndata_dir, filename) anndata_obj = ad.read_h5ad(file_path) anndata_list.append(anndata_obj) concatenated_anndata = ad.concat(anndata_list, axis=0, join='outer') In this way, the cells from batches that do not express certain genes are adde …

## Suggestion on parameters for training scvi model
**Topic:** 1936 | **Last activity:** 2023-12-04T21:41:56Z
**Posts:** 4 | **Views:** 2236 | **Created:** 2023-12-04 | **URL:** https://discourse.scverse.org/t/suggestion-on-parameters-for-training-scvi-model/1936

**Question**: Hello! I want to integrate 67 different samples (batches) from three different datasets using scVI. I have a total of 235k cells, and as suggested in the Atlas integration tutorial I integrated selecting only the top 2000 most variable features in common between all cells, as this method better removes the batch effect. I set up the anndata and used the following settings: scvi.model.SCVI.setup_anndata(anndata, layer="counts", batch_key="batch") model = scvi.model.SCVI(anndata, n_layers=2, n_latent=30, gene_likelihood="zinb") model.train() By default, the training runs 34 epochs (calculated as 20.000/n_cells*400 as defined in the function). By plotting the training metrics stored in model.history() , I get the following trends: train_loss_step : fluctuating trend (slightly decreasing for t …

**Reply (@martinkim0)**: Hey, thanks for your question! I’d suggest passing in check_val_every_n_epoch=1 into train() in order to compute validation losses as well. If you find that elbo_validation , validation_loss , and reconstruction_loss_validation are converging at the end of training, then your model is probably fine. Otherwise, you can tweak the learning rate or number of epochs depending on what’s going on. Hope this helps!

**Reply (@martibonomi)**: Thanks you very much for your fast reply! This helped me a lot. I also have another question: I would like to integrate my samples but instead of using only the top 2000 highly variable genes, I would like to use all the genes. However, the batches do not all have the same number of genes, so when creating the concatenated matrix I would do anndata_dir = 'C:/Users/Martina/Desktop/CAR-T Atlas Data/AnnData' list_files = os.listdir(anndata_dir) anndata_list = [] for filename in list_files: file_path = os.path.join(anndata_dir, filename) anndata_obj = ad.read_h5ad(file_path) anndata_list.append(anndata_obj) concatenated_anndata = ad.concat(anndata_list, axis=0, join='outer') so that I can keep all the genes, and for those cells not having that genes I have 0 counts added from the ad.concat fun …

**Reply (@martibonomi)**: Thank you so much! I actually have another question: I would like to integrate all my samples using all the genes instead of only the top 2000 most variable genes. I would do this in order to better characterise the variability and differences between my batches, and to subsequently run the differential gene expression on my cells using all the genes. However, not all the samples have the same number of genes, so that I would do the following: anndata_dir = 'C:/Users/Martina/Desktop/AnnData' list_files = os.listdir(anndata_dir) anndata_list = [] for filename in list_files: file_path = os.path.join(anndata_dir, filename) anndata_obj = ad.read_h5ad(file_path) anndata_list.append(anndata_obj) concatenated_anndata = ad.concat(anndata_list, axis=0, join='outer') In this way, the cells from batc …

## scPoli implementation in dcvi-tools
**Topic:** 1927 | **Last activity:** 2023-12-01T21:18:39Z
**Posts:** 3 | **Views:** 230 | **Created:** 2023-12-01 | **URL:** https://discourse.scverse.org/t/scpoli-implementation-in-dcvi-tools/1927

**Question**: Dear scVI team, is there any plans to incorporate scPoli into the next version of scVI tools, which I saw might be released imminently? Many thanks

**Reply (@martinkim0)**: No plans for that, sorry, since scPoli is already available through the scarches package!

**Reply (@Nusob888)**: Thanks for letting me know. Apologies, I had assumed the team were trying to wrap external models too as so many have been wrapped to date. Hard to harmonise so many tools in one place so really appreciate what you guys have added already as external wrappers.

## When mutli-gpu support is planned on scanvi?
**Topic:** 1925 | **Last activity:** 2023-12-01T16:58:56Z
**Posts:** 4 | **Views:** 332 | **Created:** 2023-11-30 | **URL:** https://discourse.scverse.org/t/when-mutli-gpu-support-is-planned-on-scanvi/1925

**Question**: If someone has been able to to do , it will be nice if he can share with us

**Reply (@martinkim0)**: We are planning on releasing multi-GPU training for SCVI and SCANVI with our next release (1.1), which will be out sometime within the next 2 weeks!

**Reply (@joshchiou)**: Cool! Are there any plans to extend multi-GPU training to other models (multiVI)?

**Reply (@martinkim0)**: Yes! We plan on eventually supporting that feature for all our models after 1.1

## UserWarning: No data for colormapping provided via 'c'. Parameters 'cmap' will be ignored
**Topic:** 1221 | **Last activity:** 2023-12-01T16:36:21Z
**Posts:** 9 | **Views:** 8122 | **Created:** 2023-03-12 | **URL:** https://discourse.scverse.org/t/userwarning-no-data-for-colormapping-provided-via-c-parameters-cmap-will-be-ignored/1221

**Question**: Hello, I am experiencing an issue with my UMAP plots in Scanpy. When trying to plot my data, the process takes over 20 minutes and does not produce any output. I have updated my Scanpy to the latest version and re-installed it, but the issue persists. Additionally, when running the plotting function, I receive the following warning message: ‘/Users/sei/opt/anaconda3/envs/scvi-env/lib/python3.9/site-packages/scanpy/plotting/_tools/scatterplots.py:392: UserWarning: No data for colormapping provided via ‘c’. Parameters ‘cmap’ will be ignored cax = scatter(.’ Can someone provide some guidance on how to resolve this issue? Thank you. import scanpy print(scanpy. version ) 1.9.3 !python --version Python 3.9.16 Package Version absl-py 1.4.0 altair 4.2.2 anndata 0.8.0 anyio 3.6.2 appnope 0.1.3 argo …

**Reply (@sruthi-hub)**: I have the same error. My sc.pl.umap also just does not give an output for over 30 mins, and also breaks the jupyter kernel eventually. First had this issue with scanpy 1.9.1, after uninstalling and reinstalling 1.9.3, I still have the same problem. Any advice will be helpful!

**Reply (@rboiar)**: Having similar issues. UMAP taking 18 hours on 200,00 cells. My current workaround is calculating UMAP outside of scanpy using the cuml package from RAPIDS (runs on a GPU in about a minute), and then pasting those UMAP results back into my anndata object.

**Reply (@DRSEI)**: @rboiar @sruthi-hub Are you guys using the VScode or jupyter notebook?

**Reply (@grst)**: You aren’t, by any chance, using a svg backend with your notebooks? Could you try to set it to png explicitly? %config InlineBackend.figure_formats = ['png']

**Reply (@brainfo)**: I tried but didn’t work

**Reply (@brainfo)**: Hi, I changed from %matplotlib widget to %matplotlib notebook and now it’s fine See if it helps with your case also

**Reply (@jan-engelmann)**: @ivirshup I do not have the waiting time problem but I do get the same warning: ...lib/python3.8/site-packages/scanpy/plotting/_tools/scatterplots.py:392: UserWarning: No data for colormapping provided via 'c'. Parameters 'cmap' will be ignored cax = scatter( for scanpy=='1.9.1' and matplotlib=='3.6.2' Simply calling: sc.pl.umap(adata, color="cell_label") On a categorical column. Is there a way to get rid of this warning? Thanks a lot!

**Reply (@jlrodriguezp)**: The UserWarning isn’t printed when passing c=[‘cool’] or c=[‘b’].

## Nested batch effects with scvi
**Topic:** 1910 | **Last activity:** 2023-11-29T22:58:16Z
**Posts:** 4 | **Views:** 615 | **Created:** 2023-11-22 | **URL:** https://discourse.scverse.org/t/nested-batch-effects-with-scvi/1910

**Question**: Hi all, I’m not exactly sure how to code the batch effect comparison here. I started with including all the levels, but I’m not sure if this is ideal. Essentially this is a 10x FFPE experiment with 15 samples. The 10X FFPE protocol splits this into 4 pool, and the Pools were sequenced in 2 batches. The set up is something like: Batch 1 has pools 1 and 2 Batch 2 has pools 3 and 4. There is one sample in batch 2 that was also repeated in batch one. I currently have it as: scvi.model.SCVI.setup_anndata( adata, layer="counts", categorical_covariate_keys=["pool", "batch", "samples"], continuous_covariate_keys=["pct_counts_mt", "S_score", "G2M_score"], ) Not sure if this is ideal however, as I realize some of the categorical variables are very well correlated. Thank you for your help!!

**Reply (@cane11)**: Correlated categorical covariates are not a problem in my experience and also not in the code. ScVI corrects for those covariates, it doesn’t try to learn the effect of each covariate separately. However, in my experience adding continuous covariates can make the latent space significantly worse as more information is encoded through those continuous covariates than through the actual latent space.

**Reply (@LinearParadox)**: Thank you for your advice. Do you usually not include any continuous covariates? Is there any way to quantify how much information I’m removing from the latent space between models? Like for example, is there any way to estimate how much I lost if I included cell cycle scores as a continuous covariate, or if I included %mt as another example.

**Reply (@cane11)**: I generally don’t include them. Run scVI and check the output. If there is a strong gradient, I’m adding them and rerunning training. Best advice to check that structure is well preserved is prior knowledge (like celltypes or development trajectory). Quantifying it is possible using scib-metrics, while they are very focussed on cell-types.

## Scvi for developmental data
**Topic:** 1906 | **Last activity:** 2023-11-29T20:27:35Z
**Posts:** 5 | **Views:** 416 | **Created:** 2023-11-20 | **URL:** https://discourse.scverse.org/t/scvi-for-developmental-data/1906

**Question**: Hey there, I want to fit a scvi model for developmental data, meaning the different batches are from different timepoints, and thus are different in many ways. specifically, i intend to use this for the Solo de-dubletting, but my question is also general. Would it be correct to indicate the different timepoints as batchs?

**Reply (@martinkim0)**: Hi, thanks for your question. scVI wasn’t explicitly designed for integration across different timepoints, so your mileage may vary when trying to fit the model to developmental data. I would give it a try and see how well it performs. You can pass in the timepoints with either batch_key or continuous_covariate_keys in SCVI.setup_anndata , depending on whether you want the model to treat it categorically (one-hot) or continuously.

**Reply (@cane11)**: It sounds appropriate for decipher. https://www.biorxiv.org/content/10.1101/2023.11.11.566719v1 It assumes correlated latent factors which is what you want to have for time series data and doesn’t try batch correction but embedding in a very low dimensional space (2D). Generally, I wouldn’t try to correct for the batch in this setup.

**Reply (@yotamcons)**: Thanks @cane11 , looks like an interesting method. I think it doesn’t fit my needs (doublet removal in the embedding), but the idea is intriguing .

**Reply (@cane11)**: For doublet removal, just run solo on each batch seperately and train an scVI model with or without batch information (it doesn’t really matter there). You can then run solo for each batch seperately, like: batches = pd.unique(rna.obs[batch_key]) is_solo_singlet = np.ones((rna.n_obs,), dtype=bool) for batch in batches: logger.add_to_log("Running solo on batch {}...".format(batch)) solo_batch = scvi.external.SOLO.from_scvi_model(scvi_model, restrict_to_batch=batch) solo_batch.train(max_epochs=configs["solo_max_epochs"]) is_solo_singlet[(rna.obs["batch"] == batch).values] = solo_batch.predict(soft=False) == "singlet" rna.obs["is_solo_singlet"] = is_solo_singlet

## Compatibility between scVI and SCENIC
**Topic:** 1795 | **Last activity:** 2023-11-28T18:22:46Z
**Posts:** 11 | **Views:** 998 | **Created:** 2023-10-06 | **URL:** https://discourse.scverse.org/t/compatibility-between-scvi-and-scenic/1795

**Question**: Hi, I have a large scVI integrated dataset and was wondering what the best way to implement scenic is? This GRN tool takes a raw matrix, ideally with all genes used as input. But from what I have read, it seems there is no way to retrieve a corrected (but not normalised) counts matrix of all genes from scVI. Should I use the full raw counts matrix, or the HVG-resitricted scVI normalised matrix? Is it appropriate to run GRN on uncorrected data? Many thanks, jess

**Reply (@martinkim0)**: Hi, thanks for you question. I’m not familiar with SCENIC, but if you’d like access to scVI’s corrected and unnormalized gene counts, you can run the following after training: X = model.get_normalized_expression(library_size="latent") Note that this will only return the genes that scVI was trained on.

**Reply (@zvittorio)**: Just out of curiosity, does that mean that the values are the same as the input scVI received? Also to comment @jesswhitts question: running GRN inference on uncorrected data might be interesting anyways because SCENIC can be robust enough to “correct” for batch effects.

**Reply (@martinkim0)**: No, these values will be different from the input that scVI receives as they are reconstructed/generated counts from the model.

**Reply (@dub2s)**: Hi @martinkim0 Can these corrected counts be used to perform DEGs analysis (in a pseudobulk fashion). While I could correct for batch-effect in UMAP and clustering with scVI, but when I perform pyDESEQ2 on the raw counts, I see very less overlap between the batches. I wonder if the scVI corrected counts might be better for that purpose.

**Reply (@jesswhitts)**: Thanks for your help @martinkim0 ! Is the ‘transform_batch’ parameter required in this instance, or just specifying latent library size? I can’t quite figure out what the transform_batch parameter does from the docs

**Reply (@martinkim0)**: @dub2s I’m not sure actually - I have a feeling that it’s more appropriate to use uncorrected raw counts for DESeq2. Maybe someone else with more experience with DESeq2 can comment. If you want to perform differential expression on scVI-corrected counts, I would recommend using the built-in function for it: scvi.model.SCVI — scvi-tools

**Reply (@martinkim0)**: @jesswhitts Using transform_batch shouldn’t be necessary as it produces counterfactual reconstructions. It just decodes the latent representation with a different batch index than what is the actual data. When you use model.get_normalized_expression(library_size="latent") , this will by default use the empirical library size of your data. In other words, it will scale the normalized expression generated from the model by the total UMI counts in each cell in your data, so you don’t need to explicitly pass in a library size.

**Reply (@dub2s)**: Thanks for your input. I wasn’t aware of the differential expression within scVI. I will be trying it soon!

**Reply (@jesswhitts)**: This makes sense. Thanks for your help!

**Reply (@cane11)**: To conclude it, I would recommend using raw counts for DESEQ2. All autoencoder or factor models learn gene-gene correlation. This might lead to false positives. DESEQ2 expects unnormalized count data as input. You won’t get this type of data out of scVI.

## MultiVI size factor for multiple modalities
**Topic:** 1915 | **Last activity:** 2023-11-24T23:49:48Z
**Posts:** 1 | **Views:** 286 | **Created:** 2023-11-24 | **URL:** https://discourse.scverse.org/t/multivi-size-factor-for-multiple-modalities/1915

**Question**: In the methods from the MultiVI paper, both the expression and accessibility distributions contain ℓc - a term that captures cell-specific biases. In scvi.model.MULTIVI.setup_anndata, I believe setting size_factor_key overrides the estimated library size for expression. Is there an equivalent parameter or a workaround for accessibility? I would like to be able to manually specify the library size for both modalities. Thanks, Josh

## Setting num_workers in DataLoader for improving train performance
**Topic:** 1902 | **Last activity:** 2023-11-21T00:10:07Z
**Posts:** 3 | **Views:** 3603 | **Created:** 2023-11-18 | **URL:** https://discourse.scverse.org/t/setting-num-workers-in-dataloader-for-improving-train-performance/1902

**Question**: Hi! Thanks for the great ecosystem of scVI tools! It has become an essential part of my work. I recently shifted my workload to a server with A100 GPU and when I run model.train(), I get the following message: /env/lib/python3.9/site-packages/lightning/pytorch/trainer/connectors/data_connector.py:441: The 'train_dataloader' does not have many workers which may be a bottleneck. Consider increasing the value of the `num_workers` argument` to `num_workers=9` in the `DataLoader` to improve performance. /env/lib/python3.9/site-packages/lightning/pytorch/trainer/connectors/data_connector.py:441: The 'val_dataloader' does not have many workers which may be a bottleneck. Consider increasing the value of the `num_workers` argument` to `num_workers=9` in the `DataLoader` to improve performance. I tr …

**Reply (@martinkim0)**: Hi, thanks for you question! I haven’t had too much success increasing the number of dataloader workers when training models - in my hands it hasn’t made too much of a difference, which is weird since most of our models are primarily data transfer bottlenecked. Have you had the chance to measure GPU utilization/power consumption when increasing the number of workers? I would be curious to know.

**Reply (@martinkim0)**: Hey, I looked into this and it turns out that we don’t apply settings.dl_num_workers correctly in our dataloader, which is probably why you’re seeing the warning message. I have a fix here which will be released in scvi-tools 1.1 soon.

## Error in Fine-tuning scANVI Hyperparameters from Pretrained scVI Model
**Topic:** 1899 | **Last activity:** 2023-11-20T21:40:44Z
**Posts:** 3 | **Views:** 515 | **Created:** 2023-11-17 | **URL:** https://discourse.scverse.org/t/error-in-fine-tuning-scanvi-hyperparameters-from-pretrained-scvi-model/1899

**Question**: Hello everyone, I am working with a single-cell RNA-seq dataset of approximately 48,000 cells from the Tabula Muris datasets and an in-house dataset. My goal is to integrate these datasets for label transfer from the reference to our query dataset using scANVI. After successfully fine-tuning the scVI hyperparameters with “autotune” (ray 2.7.0), I tried to fine-tune the scANVI hyperparameters. I focused on n_layer , n_latent and gene_likelihood starting from the pretrained scVI model using from_scvi_model method. Does it make sense to fine-tune the hyperparameters of the scANVI model after scVI, or the hyperparameters are inherited from the scVI model without the possibility of changing them? I used the same steps to fine-tune scANVI, however, during the process, I encountered the following …

**Reply (@PaulArthurM)**: Updating ray to 2.8.0 and scvi-tools to 1.0.4 does not resolve this issue. And configure the model with setup_anndata instead of from_scvi_model either. model_cls = scvi.model.SCANVI model_cls.setup_anndata(adata, unlabeled_category="Unknown", labels_key=SCANVI_CELLTYPE_KEY)

**Reply (@martinkim0)**: Hi, thank you for your question. We recently caught this bug and was fixed in this PR, which will be released in scvi-tools 1.1. Not sure how we didn’t catch this before. For now, I would recommend running hyperparameter optimization on just scVI, training scVI on those parameters, and then initializing scANVI from the trained scVI model. This should hopefully bypass the error you’re seeing.

## Vae_q.latent_space_classifer_ not found in totalVI CITE-seq reference mapping tutorial
**Topic:** 1859 | **Last activity:** 2023-11-20T20:59:42Z
**Posts:** 4 | **Views:** 314 | **Created:** 2023-11-07 | **URL:** https://discourse.scverse.org/t/vae-q-latent-space-classifer-not-found-in-totalvi-cite-seq-reference-mapping-tutorial/1859

**Question**: We are following the tutorial located here to create a reference and map cell idents to a query. CITE-seq reference mapping with totalVI — scvi-tools In “Query cell type prediction”, we receive an error that vae_q does not have latent_space_classifier_ , when running: predictions = vae_q.latent_space_classifer_.predict(query.obsm["X_totalvi_scarches"]) Should this be vae instead of vae_q ? Or do we need to rerun the code to generate the classifier in the “Train a classifier on the latent space” Section? Thank you!

**Reply (@martinkim0)**: Hi, thank you for your question. I am unable to reproduce the reported error using the latest version of scvi-tools (1.0.4). Could you let me know what version you are using?

**Reply (@JenniferF)**: Thank you for the reply. We backtracked our steps and found this was due to some incompatibilities in versions, and we were able to resolve it!

**Reply (@martinkim0)**: Great! Glad you were able to resolve it.

## Input to scvi encoder
**Topic:** 233 | **Last activity:** 2023-11-14T19:31:20Z
**Posts:** 5 | **Views:** 600 | **Created:** 2021-12-06 | **URL:** https://discourse.scverse.org/t/input-to-scvi-encoder/233

**Question**: I have a vague memory that in the original version of scvi, the counts were normalized somehow before being passed into the encoder, perhaps as log(1+CPM). My recollection is this was more numerically stable than passing raw counts directly. Is that still the case? I couldn’t find anything in the documentation or in the code itself.

**Reply (@adamgayoso)**: Just a log(1+x) transform. It’s here: github.com YosefLab/scvi-tools/blob/c01cb292cbb4f2974bd4f6403df3665fd9fac800/scvi/module/_vae.py#L256-L266 def inference(self, x, batch_index, cont_covs=None, cat_covs=None, n_samples=1): """ High level inference method. Runs the inference (encoder) model. """ x_ = x if self.use_observed_lib_size: library = torch.log(x.sum(1)).unsqueeze(1) if self.log_variational: x_ = torch.log(1 + x_) And yes, more numerically stable!

**Reply (@willtownes)**: Excellent, thanks a ton Adam!

**Reply (@yxy92)**: Hi Adam, I can see that log(1+X) keep partial info of the raw data while increasing the numerical stability as you mentioned. Is there a specific reason that scVI does not use more common log2(1+CPM) or log2(1+TPM)?

**Reply (@martinkim0)**: Hi, we just use log(1 + x) for simplicity as we generally only care about numerical stability of the model.

## Multi-omics scANVI
**Topic:** 1879 | **Last activity:** 2023-11-14T19:24:41Z
**Posts:** 2 | **Views:** 319 | **Created:** 2023-11-09 | **URL:** https://discourse.scverse.org/t/multi-omics-scanvi/1879

**Question**: Is there an extension of the scANVI model that could also model protein data from CITE-seq like totalVI?

**Reply (@martinkim0)**: Hi, thank you for your question. We don’t have this extension implemented in totalVI yet - we are tracking this feature request here . It should be straightforward to add but we don’t have an estimated timeline for this yet.

## Raw count input for scVI cell clustering
**Topic:** 1865 | **Last activity:** 2023-11-08T19:16:10Z
**Posts:** 3 | **Views:** 564 | **Created:** 2023-11-08 | **URL:** https://discourse.scverse.org/t/raw-count-input-for-scvi-cell-clustering/1865

**Question**: I notice that scVI model recommends raw count for input, is there a argument to pass for using preprocessed (CPM & log1p transformed) count matrix?

**Reply (@martinkim0)**: Hi, thank you for your question. scVI only supports raw counts as input because the generative portion of the model uses either the negative binomial or Poisson distribution, both of which expect discrete values. Since transforming with log1p maps to continuous values, this is unsupported. We also don’t support any sort of normalized input because the scVI model will either learn a latent size factor per cell or use the empirical total UMI counts per cell, both of which are needed in the generative portion to reconstruct counts.

**Reply (@yxy92)**: Appreciate your explanation.

## About the scvi-tools category
**Posts:** 1 | **Views:** 1257

**Question**: For questions about using scvi-tools .
