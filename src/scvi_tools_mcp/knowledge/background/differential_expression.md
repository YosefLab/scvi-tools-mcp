# Differential Expression

## Problem Statement

Differential expression analyses quantify and detect expression differences between conditions (cell types, treatments, etc.). The canonical effect size is the **log fold-change**:

$$\beta_g := \log h_g^B - \log h_g^A$$

where $h_g^A, h_g^B$ are mean expression levels in populations $A$ and $B$.

For chromatin accessibility (PeakVI): $\beta_f = h_f^B - h_f^A$ (not log).

## Approach in scvi-tools

Deep generative models (scVI, TotalVI, PeakVI) handle batch effects nonlinearly and leverage large datasets via amortization — better suited for large-scale data than linear models.

## Step 1: Approximating Population-Specific Expression Levels

Aggregate variational posteriors over cells in each state:

$$\hat{P}^C(Z) = \frac{1}{\mathcal{N}_C} \sum_{n \in \mathcal{N}_C} p_\theta(z|x_n)$$

`idx1` and `idx2` parameters specify which cells to include. Expression vectors $h_n = f^h_\theta(z_n)$ are sampled from these aggregate posteriors.

## Step 2: Detecting Biologically Relevant Features

**`mode="vanilla"`**: Point null $\mathcal{H}_{0f}: \beta_f = 0$

**`mode="change"` (recommended)**: Composite null $|\beta_f| \leq \delta$ where `delta` is a threshold. With `delta=None`, estimated data-adaptively. Avoids detecting statistically significant but biologically irrelevant differences.

## Step 3: Controlling FDR

For a target significance level $\alpha$ (`fdr_target`), selects maximum $k^*$ detections such that:

$$\mathbb{E}_{post}[FDP_{\mu^k}] = \frac{\sum_f (1-p^f)\mu_f^k}{\sum_f \mu_f^k} \leq \alpha$$

where $p^f$ is the posterior probability of $|\beta_f| \leq \delta$.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `idx1`, `idx2` | Cell masks or queries for populations A and B |
| `mode` | `"vanilla"` (point null) or `"change"` (composite null, recommended) |
| `delta` | LFC threshold for `mode="change"` (None = data-driven) |
| `fdr_target` | Desired FDR significance level |
| `importance_sampling` | Whether to use importance sampling for expression estimation |

## Usage Example

```python
# Differential expression between two cell types
de_df = model.differential_expression(
    groupby="cell_type",
    group1="CD4 T",
    group2="CD8 T",
    mode="change",
    delta=0.25,
    fdr_target=0.05,
)
```

## References

- See scVI, TotalVI, PeakVI documentation for model-specific implementations.
