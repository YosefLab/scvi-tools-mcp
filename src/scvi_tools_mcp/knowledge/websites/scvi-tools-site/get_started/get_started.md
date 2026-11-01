<!-- Source: https://github.com/scverse/scvi-tools-site/blob/HEAD/get_started/get_started.md -->

---
id: get_started
title: Get started
slug: /
---


`scvi-tools` (single-cell variational inference tools) is a package for probabilistic modeling of single-cell omics data, built on top of PyTorch and AnnData. The package hosts implementations of models that perform a wide range of single-cell data analysis tasks, as well as the building blocks to rapidly prototype new probabilistic models.

## Installation

`scvi-tools` can be installed with `pip` or `conda`:

```
pip install scvi-tools
```

```
conda install scvi-tools -c conda-forge
```

To leverage a GPU for inference, a version of [PyTorch](https://pytorch.org/get-started/locally/) that supports your GPU will need to be installed separately.

<!-- ## Analysis of single-cell data

### scRNA-seq

- LDVAE
- scVI
- scANVI

### CITE-seq

- totalVI

### Spatial transcriptomics

- Steroscope
- gimVI

## Rapid prototyping of probabilistic models

- MLE
- MAP
- VI -->


## Resources

- Tutorials, API reference, and advanced installation guides are available in the [docs](https://docs.scvi-tools.org/en/stable/).
-  For discussion of usage, checkout out our [forum](https://discourse.scvi-tools.org/).
-  To report bugs, make an issue on [GitHub](https://github.com/YosefLab/scvi-tools/issues).
