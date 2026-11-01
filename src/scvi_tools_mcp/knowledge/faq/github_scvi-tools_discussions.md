# scverse/scvi-tools GitHub Discussions Q&A

6 GitHub Discussions from scverse/scvi-tools with activity in the last 3 years, most recently active first. This snapshot accumulates across refreshes; discussions are only removed once they age out of that window.

## #4029: Implementing a new multimodal model for GET-seq
**Discussion:** #4029 | **Last activity:** 2026-09-21T13:24:05Z
**Category:** Ideas | **Author:** @dawe | **Comments:** 1 | **Answered:** no | **Created:** 2026-09-21 | **URL:** https://github.com/scverse/scvi-tools/discussions/4029

Hello, I'd like to test scVI on some GET-seq data. GET-seq data are basically ATAC-seq on steroids, so I have two sets of counts obtained by two transposases (tn5 and tnH). In principle I can use PEAKVI or POISSONVI on the tn5 layer to go on, but I'd like to implement a new model that takes into account both matrices. I guess this would be analogous to MultiVI or TotalVI but with two layers modeled as in PEAKVI or POISSONVI. Any hint would be appreciated.

**@dawe:** I think I've found the docs about this. Next time RTFM :-/

## #3402: Visualization of the scvi-tools' codebase
**Discussion:** #3402 | **Last activity:** 2025-08-29T22:58:24Z
**Category:** Show and tell | **Author:** @ivanmilevtues | **Comments:** 1 | **Answered:** no | **Created:** 2025-06-28 | **URL:** https://github.com/scverse/scvi-tools/discussions/3402

Hey all I generated diagram for the scvi-tools repo (via static analysis and LLMs): https://github.com/CodeBoarding/GeneratedOnBoardings/blob/main/scvi-tools/on_boarding.md

The diagram is designed to give a high-level overview of the codebase by providing the main components and how they interact with eachother. With this information a new contributor can start their first task by understanding how what they are editing fits in the big picture. I'd love to hear what is your opinion on diagram first documentation.

Full disclosure: we're trying to turn this into a startup, but we're still in a very early stage and figuring out what will actually be useful for people. Also as many people brought that the diagrams will become outdated fast, we've introduced free github action!

**@ivanmilevtues:** Hey, a quick update on our side, we have released our diagram generation engine as an open-source repo: https://github.com/CodeBoarding/CodeBoarding

If you are interested to see how exactly we combined Static Analysis and LLMs you can head and see that there!

## #3485: is MultiVI suitable for integrating ATAC and RNA assays from 10X Multiome?
**Discussion:** #3485 | **Last activity:** 2025-08-26T15:47:41Z
**Category:** Q&A | **Author:** @MolendoLabBio | **Comments:** 1 | **Answered:** yes | **Created:** 2025-08-26 | **URL:** https://github.com/scverse/scvi-tools/discussions/3485

Hi,

I have several Multiome libraries from pooled samples (we have 6 patients per libraries and pooled 4 libraries per modality for sequencing).  Our lab was planning to demultiplex the pools using genotyping data and Demuxafy.  We would then pre-process the ATAC and RNA data separately before using MultiVI to integrate the two modalities.  Is this feasible?

I read on here that MultiVI is designed for integrating multiome with either ATAC or single-cell RNA data but not really for integrating ATAC and RNA from the same multiome experiment.  However, this page from sc best practices shows that the two assays can be concatenated before using MultiVI (https://www.sc-best-practices.org/multimodal_integration/paired_integration.html#multiome-data).

Does anyone have experience integrating the modalities using scvi tools?

We are aware of Signac but would like to try with MultiVI if possible.

**@canergen (accepted answer):** Hi, joint alignment and demultiplexing into patients is better (higher number of reads and SNPs per cell). Please check with demuxafy for code. You can then run multiVI on these cells with both RNA and ATAC assayed. We prefer usage questions on discourse.

## #3370: model.get_normalized_expression  issue of MultiVI
**Discussion:** #3370 | **Last activity:** 2025-06-05T18:26:55Z
**Category:** Q&A | **Author:** @ZennFangZhou | **Comments:** 1 | **Answered:** no | **Created:** 2025-06-04 | **URL:** https://github.com/scverse/scvi-tools/discussions/3370

Hello, developer! I'm conducting MultiVI analysis on my CITE-seq data with 30,000 cells and 6,000 genes. When I ran the model.get_normalized_expression function on the trained model, system memory usage quickly surged from 10GB to over 100GB, causing a software crash. This didn't happen when I ran the tutorial data. How can I resolve this?

**@ZennFangZhou:** all right, when i set the para to rna_denoised, protein_denoised =model.get_normalized_expression(mdata,n_samples=25, return_mean=True,gene_list=rna.var_names.to_list()),i deal with the problem

## #3344: Can I train scVI from scratch on my own cancer dataset, or do I need a reference?
**Discussion:** #3344 | **Last activity:** 2025-05-21T15:04:10Z
**Category:** Q&A | **Author:** @AlbertoTh98 | **Comments:** 1 | **Answered:** yes | **Created:** 2025-05-21 | **URL:** https://github.com/scverse/scvi-tools/discussions/3344

Hi everyone,

I'm Alberto Atencia, a bioinformatics PhD student.

I'm transitioning away from classical pipelines like Seurat and exploring scVI, which I find extremely interesting. However, there's one key aspect I don’t fully understand and would appreciate clarification on:

Can I train scVI directly from scratch on my own dataset (e.g., ovarian cancer scRNA-seq), or is it preferable—or even necessary—to train on or include a reference dataset?

If training from scratch is acceptable, what guarantees or considerations should I keep in mind regarding performance, especially for tasks like clustering or batch correction?
On the other hand, if pretraining on another dataset is beneficial, what type of dataset would be most appropriate (same tissue, same platform, etc.)? and is it viable to rely on another's annotated dataset?

Thanks a lot for your time and for building such a great tool.
And I’m sorry if this is a very basic question—I just want to ensure I’m using scVI correctly from the start.

Best regards,
Alberto Atencia

**@ori-kron-wis (accepted answer):** Hello Alberto, and thank you for using the tool.

You can train a scvi model from both scratch and reference.

We usually use UMAPs to assess the quality of the batch correction, and scvi-metrics to also assess it quantitatively, perhaps comparing to other methods or embeddings (like PCA at the very basic).
Another basic thing to consider is to check your loss metrics during training, see that you converge the ELBO loss to a minimum without performing overfitting on a validation test.

If you plan to use the reference model it is recommended to use the most relevant kind of data of course. If it was ovarian, then ovarian, with the same platform use. As far as the reference data is from your query data, then the less likely the transfer learning will work well (we use scArches method …

> **@AlbertoTh98:** Thanks a lot for your time and effort! It is much clearer now!

## #865: Welcome to scvi-tools Discussions!
**Discussion:** #865 | **Last activity:** 2024-12-31T12:29:38Z
**Category:** General | **Author:** @adamgayoso | **Comments:** 0 | **Answered:** no | **Created:** 2020-12-08 | **URL:** https://github.com/scverse/scvi-tools/discussions/865

<!--
    ✏️ Optional: Customize the content below to let your community know what you intend to use Discussions for.
-->
## 👋 Welcome!
We have setup discussions at our [discourse](https://discourse.scvi-tools.org/) site. Please use that site to discuss scvi-tools.
<!--
  For the maintainers, here are some tips 💡 for getting started with Discussions. We'll leave these in Markdown comments for now, but feel free to take out the comments for all maintainers to see.

  📢 **Announce to your community** that Discussions is available! Go ahead and send that tweet, post, or link it from the website to drive traffic here.

  🔗 If you use issue templates, **link any relevant issue templates** such as questions and community conversations to Discussions. Declutter your issues by driving community content to where they belong in Discussions. If you need help, here's a [link to the documentation](https://docs.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository#configuring-the-template-chooser).

  ➡️ You can **convert issues to discussions** either individually or bulk by labels. Looking at you, issues labeled “question” or “discussion”.
-->
