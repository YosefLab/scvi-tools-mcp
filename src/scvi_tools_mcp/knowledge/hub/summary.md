# scvi-tools Hugging Face Hub Snapshot

Fetched 121 public model repos from https://huggingface.co/scvi-tools.

**Fetched at:** 2026-06-15T12:59:31Z

The snapshot is bundled for offline MCP use. Runtime tools do not call Hugging Face.

## Model Classes

- SCVI: 32
- SCANVI: 30
- CondSCVI: 28
- RNAStereoscope: 28
- TOTALVI: 3

## Modalities

- rna: 121
- protein: 3

## Annotation Status

- annotated: 118
- not annotated: 3

## Top Tissues

- various: 112
- thymus: 2
- bone marrow: 1
- heart: 1
- lung: 1
- lung parenchyma: 1
- nose: 1
- respiratory airway: 1

## Recently Modified

- scvi-tools/test-scvi-minified (SCVI; rna; unspecified tissue)
- scvi-tools/test-scvi-no-anndata (SCVI; rna; unspecified tissue)
- scvi-tools/test-scvi (SCVI; rna; unspecified tissue)
- scvi-tools/heart-cell-atlas-scvi (SCVI; rna; heart)
- scvi-tools/haniffa_covid_pbmc_totalvi (TOTALVI; rna, protein; thymus)
- scvi-tools/mouse_thymus_cite_totalvi (TOTALVI; rna, protein; thymus)
- scvi-tools/human-lung-cell-atlas-scanvi (SCANVI; rna; nose, respiratory airway, lung parenchyma)
- scvi-tools/tabula-sapiens-vasculature-stereoscope (RNAStereoscope; rna; various)
- scvi-tools/tabula-sapiens-vasculature-condscvi (CondSCVI; rna; various)
- scvi-tools/tabula-sapiens-vasculature-scanvi (SCANVI; rna; various)

## Usage Notes

- Use the dedicated hub tools to filter by model class, modality, tissue, and annotation status.
- Check the linked Hugging Face repo and scvi-tools model class before loading a pretrained model.
- In scvi-tools, use the appropriate model class with `load_from_hub()` when the repo matches the analysis.
