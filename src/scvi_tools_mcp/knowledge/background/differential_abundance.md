# Differential Abundance

## Problem Statement

Differential abundance analyses detect cell states that are disproportionately abundant in a given group of samples.

For two disjoint sets of samples $A$ and $B$, the relative overabundance of cells from $A$ vs. $B$ at any cell state $u$ is:

$$r_{AB}(u) := \log \frac{q_A(u)}{q_B(u)}$$

## Approach in scvi-tools

### Step 1: Quantify density per sample

For each cell $n$ in sample $s$, use the model's variational posterior $q(z|x_n)$. Aggregate over all cells in sample $s$:

$$q_s(z) := \frac{1}{n_s} \sum_{n: s_n = s} q(z|x_n)$$

Evaluating $q_s(z_n)$ gives the density of sample $s$ at cell $n$'s location in latent space. Returns a **log densities matrix** (cells × samples).

### Step 2: Aggregate posteriors across groups

For a group of samples $A$: $q_A(z) := \frac{1}{|A|} \sum_{s \in A} q_s(z)$

Evaluate at cell $n$ to quantify how likely cell $n$ belongs to group $A$.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `sample_key` | Key for sample covariate in `adata.obs` |
| `num_cells_posterior` | Max cells per sample for posterior computation (memory control) |
| `dof` | Degrees of freedom for Student's t-distribution components. `None` = Normal. Higher `dof` stability for samples with few cells |

## Usage Example

```python
# With MrVI or CytoVI
da_df = model.differential_abundance(
    adata, sample_key="donor", groupby="condition", group1="disease", group2="control"
)
```

## Supported Models

- `scvi.model.MRVI` — designed for multi-sample analyses
- `scvi.external.CYTOVI` — supports label-free differential abundance

## References

- See MrVI and CytoVI documentation for model-specific details.
- Boyeau et al. (2024), *Deep generative modeling of sample-level heterogeneity in single-cell genomics*, bioRxiv.
