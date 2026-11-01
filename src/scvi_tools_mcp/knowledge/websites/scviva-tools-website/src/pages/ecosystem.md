<!-- Source: https://github.com/YosefLab/scviva-tools-website/blob/HEAD/src/pages/ecosystem.md -->

---
description: The eight spatial transcriptomics models and tools bundled in scVIVA-Tools.
---

# Ecosystem

`scVIVA-Tools` consolidates eight spatial transcriptomics models and tools into one package. It is
itself part of the [scvi-tools ecosystem](https://scvi-tools.org/ecosystem).

## [scVIVA](https://scviva-tools.readthedocs.io/page/user_guide/models/scviva.html)

Niche-aware representation learning that jointly models a cell's own expression and its
microenvironment, disentangling cell-intrinsic from environment-driven variation.

## [ResolVI](https://scviva-tools.readthedocs.io/page/user_guide/models/resolvi.html)

Corrects segmentation errors, background contamination, and cell-size bias in cellular-resolution
spatial data (Xenium, MERFISH, CosMx).

## [DestVI](https://scviva-tools.readthedocs.io/page/user_guide/models/destvi.html)

Multi-resolution deconvolution of spot-based data (e.g., Visium) into continuous cell-type
compositions.

## [DiagVI](https://scviva-tools.readthedocs.io/page/user_guide/models/diagvi.html)

Diagonal integration of unpaired multi-modal single-cell data using prior cross-modal feature
correspondences.

## [Harreman](https://scviva-tools.readthedocs.io/page/user_guide/models/harreman.html)

Infers spatially-resolved metabolic gene programs and cell-cell metabolic/ligand-receptor
communication, optionally integrating DestVI, ResolVI, and scVIVA outputs.

## [gimVI](https://scviva-tools.readthedocs.io/page/user_guide/models/gimvi.html)

Joint imputation of missing genes between paired scRNA-seq and spatial datasets.

## [Stereoscope](https://scviva-tools.readthedocs.io/page/user_guide/models/stereoscope.html)

A two-stage generative model for spot-based cell-type deconvolution.

## [Tangram](https://scviva-tools.readthedocs.io/page/user_guide/models/tangram.html)

Maps single cells onto spatial coordinates via optimal-transport-style alignment.
