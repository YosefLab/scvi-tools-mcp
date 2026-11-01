<!-- Source: https://github.com/scverse/scvi-tools-site/blob/HEAD/src/pages/get_started.mdx -->

import TeamCard from "@theme/TeamCard";
import useBaseUrl from "@docusaurus/useBaseUrl";

# Get Started

`scvi-tools` (single-cell variational inference tools) is a package for probabilistic modeling of single-cell omics data,
built on top of [PyTorch](https://pytorch.org/) and [AnnData](https://anndata.readthedocs.io/en/latest/). The package
hosts implementations of several models that perform a wide range of single-cell data analysis tasks, as well as the
building blocks to rapidly prototype new probabilistic models.

## Basic installation

`scvi-tools` can be installed with `pip` or `conda`:

```
pip install scvi-tools
```

```
conda install scvi-tools -c conda-forge
```

To leverage a GPU for inference, a version of [PyTorch](https://pytorch.org/get-started/locally/) that supports your
GPU will need to be installed separately.


## Resources

- Tutorials, API reference, and advanced installation guides are available in the [docs](https://docs.scvi-tools.org/en/stable/).
- For discussion of usage, checkout out our [forum](https://discourse.scvi-tools.org/).
- For immediate public chat with the developers, come talk to us on [Zulip](https://scverse.zulipchat.com/#narrow/stream/324229-scvi-tools).
- For a skeleton of implementation of a new model in scvi-tools, refer to our [template repository](https://github.com/YosefLab/scvi-tools-skeleton/)
- To report bugs, make an issue on [GitHub](https://github.com/scverse/scvi-tools/issues).

## Single-cell omics data analysis

Data analysis with `scvi-tools` is driven by model objects. Each model typically corresponds to a computational method
described in a manuscript and each model may perform several important downstream tasks (with the same fit). Importantly,
each model has an easy-to-use interface that conveniently interacts with [Scanpy](https://scanpy.readthedocs.io/en/stable/),
[Seurat](https://satijalab.org/seurat/) and [Bioconductor](https://www.bioconductor.org/).

A full overview of each model and its corresponding analytical tasks is in the
[user guide](https://docs.scvi-tools.org/en/stable/user_guide/index.html). Currently we support workflows for the
following modalities:

- scRNA-seq
- Spatial Transcriptomics
- Multimodal (CITE-seq, Multiome)
- Chromatin Accessibility (scATAC-seq)
- DNA Methylation
- Flow and Mass Cytometry

`scvi-tools` continues to grow: recent releases added models for niche-aware spatial analysis
([scVIVA](https://docs.scvi-tools.org/en/stable/user_guide/models/scviva.html),
[ResolVI](https://docs.scvi-tools.org/en/stable/user_guide/models/resolvi.html)), cytometry
([CytoVI](https://docs.scvi-tools.org/en/stable/user_guide/models/cytovi.html)), DNA methylation
([MethylVI](https://docs.scvi-tools.org/en/stable/user_guide/models/methylvi.html)), and multi-sample
comparison ([MrVI](https://docs.scvi-tools.org/en/stable/user_guide/models/mrvi.html)), among others. See the full,
up-to-date model list in the [user guide](https://docs.scvi-tools.org/en/stable/user_guide/models/index.html) and the
[changelog](https://docs.scvi-tools.org/en/stable/changelog.html).


## Rapid development of novel probabilistic models

`scvi-tools` facilitates rapid development and deployment of single-cell-focused probabilistic models. To achieve this,
we host black-box primitives for loading data from [AnnData](https://anndata.readthedocs.io/en/latest/), black-box
training procedures using [Lightning](https://lightning.ai/), and optionally provides automatic inference recipes based
on [Pyro](https://pyro.ai/). We currently support many optimization-based inference procedures including SVI, AEVB, MAP,
MLE and EM. To learn more about the developer toolkit, please visit our
[tutorials](https://docs.scvi-tools.org/en/stable/tutorials/index.html). We also provide an example
[skeleton](https://github.com/YosefLab/scvi-tools-skeleton/) implementation of a basic scVI in PyTorch and Pyro as an
independent package powered by `scvi-tools`. If you wish to add an implementation of your algorithm in scvi-tools,
please post a [GitHub issue](https://github.com/scverse/scvi-tools/issues) to reach out to us.

## Reference

If you use scvi-tools in your research, please consider citing

```
@article{Gayoso2022,
         author={Gayoso, Adam and Lopez, Romain and Xing, Galen and Boyeau, Pierre and Valiollah Pour Amiri, Valeh and Hong, Justin and Wu, Katherine and Jayasuriya, Michael and   Mehlman, Edouard and Langevin, Maxime and Liu, Yining and Samaran, Jules and Misrachi, Gabriel and Nazaret, Achille and Clivio, Oscar and Xu, Chenling and Ashuach, Tal and Gabitto, Mariano and Lotfollahi, Mohammad and Svensson, Valentine and da Veiga Beltrame, Eduardo and Kleshchevnikov, Vitalii and Talavera-L{\'o}pez, Carlos and Pachter, Lior and Theis, Fabian J. and Streets, Aaron and Jordan, Michael I. and Regier, Jeffrey and Yosef, Nir},
         title={A Python library for probabilistic analysis of single-cell omics data},
         journal={Nature Biotechnology},
         year={2022},
         month={Feb},
         day={07},
         issn={1546-1696},
         doi={10.1038/s41587-021-01206-w},
         url={https://doi.org/10.1038/s41587-021-01206-w}
}
```
along with the publicaton describing the model used.
