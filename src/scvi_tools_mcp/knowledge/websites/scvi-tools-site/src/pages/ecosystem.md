<!-- Source: https://github.com/scverse/scvi-tools-site/blob/HEAD/src/pages/ecosystem.md -->

# Ecosystem

Here we highlight projects that make use of scvi-tools.

## [scIB-metrics](https://scib-metrics.readthedocs.io/en/latest/)
scIB-metrics provides accelerated, Python-only implementations of the metrics from the scIB single-cell integration benchmarking suite, using JAX for jit-compiled, hardware-accelerated computation. It is commonly used alongside scvi-tools to benchmark and compare batch-correction and integration methods such as scVI and scANVI against alternatives like Harmony and LIGER.

## [scVIVA-Tools](https://scviva-tools.readthedocs.io/en/latest/)
scVIVA-Tools is a spatial transcriptomics toolkit built on scvi-tools that packages scVIVA, a niche-aware model that learns cellular representations conditioned on the surrounding microenvironment, alongside DestVI, ResolVI, GIMVI, Stereoscope, and Tangram as first-class models, plus the Harreman module for cell-cell communication and metabolic exchange analysis. It provides a unified API for deconvolution, noise correction, gene imputation, and niche-aware differential expression across spatial datasets.

## [scvi-hub](https://huggingface.co/scvi-tools)
scvi-hub is a Hugging Face-hosted collection of pretrained scvi-tools models and reference atlases, including scVI, scANVI, totalVI, and spatial deconvolution models. Models can be browsed, downloaded, and queried directly through the `scvi.hub` module in scvi-tools, letting users skip training and map new query data onto existing reference models.

## [scVI-Tools MCP](https://scvi-tools-mcp.readthedocs.io/en/latest/index.html)
scVI-Tools MCP is a Model Context Protocol (MCP) server that gives AI assistants such as Claude structured access to scvi-tools knowledge: model documentation, tutorials, API references, workflow templates, and pretrained Hugging Face Hub models. It runs as a pure knowledge layer with no runtime model execution, and works with Claude Code, Claude Desktop, Cursor, and any other MCP-compatible client. Install via `pip install scvi-tools-mcp` or [PyPI](https://pypi.org/project/scvi-tools-mcp/).

## [cell2location](https://cell2location.readthedocs.io/en/latest/)
cell2location is a hierarchical Bayesian model for resolving cell types in spatial transcriptomic data (e.g., Visium) with high sensitivity.

## [scArches](https://scarches.readthedocs.io/en/latest/)
scArches allows for the integration of new query data into reference atlases produced with conditional deep generative models such as trVAE, scVI, scANVI, totalVI and PeakVI.

## [scGen](https://github.com/theislab/scgen/)
scGen is a generative model to predict single-cell perturbation response across cell types, studies and species. scGen is implemented using the scvi-tools framework.

## [3DVI: Normalization and De-noising of Single-cell Hi-C Data](https://github.com/yezhengSTAT/3DVI)
3DVI is a deep generative model for scHi-C data, that takes into account 3D genomic structural properties such as the band bias, sequencing depth effect, zero inflation, sparsity impact, and batch effects. 3DVI is implemented using the SCVI model from scvi-tools.

## [Platform for Analysis of single cell Eye in a Disk (scEiaD)](https://plae.nei.nih.gov/)
scEiaD is a meta-atlas that compiles 1.2 million single-cell back of the eye transcriptomes across 28 studies, 18 publications, and 3 species. Deep metadata mining, rigorous quality control analysis, differential gene expression testing, and deep learning based batch effect correction in a unified bioinformatic framework allow the universe of retina single cell expression information to be analyzed in one location. The approach for deep learning based batch effect correction is scVI, as well as scVI + scArches from scvi-tools.

## [scdefg: scvi-tools differential expression Flask GUI](https://github.com/WormBase/scdefg)
This is a a single page Flask GUI that allows users to quickly select cell groups based on annotations of the data and perform differential expression on single cell RNA sequencing data using scvi-tools. Deploying this app only requires a trained scVI model saved with the corresponding anndata. The selection of groups can be done using any of the features annotated at `anndata.obs`. A live deploy with C. Elegans data is available at [https://scdefg.textpressolab.com/](https://scdefg.textpressolab.com/).
