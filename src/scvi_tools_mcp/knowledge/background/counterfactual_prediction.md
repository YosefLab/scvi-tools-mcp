# Counterfactual Prediction

## Overview

After training a generative model, we can make predictions for unobserved scenarios by perturbing inputs. A **counterfactual query** is a pair $(x, c')$ where $c' \neq c$ is a condition (batch, treatment) not observed for that cell.

> Note: "counterfactual" is used loosely here — this is not rigorous causal counterfactual prediction, but querying statistical models to understand what they've learned.

## Concept

Given a trained model $f_\theta$ that takes data $x$ and condition $c$:

- **Observed prediction**: $\hat{y} = f_\theta(x, c)$
- **Counterfactual query**: $(x, c')$ where $c' \neq c$
- **Counterfactual prediction**: $\hat{y}' = f_\theta(x, c')$

## When to Trust Counterfactual Predictions

Reliable when the counterfactual query $(x, c')$ is similar to training points $(x', c')$ (i.e., $\|x - x'\|$ is small). If $(x, c')$ is very different from any training point with condition $c'$, predictions are unreliable.

Dimensionality reduction / harmonization helps create feature overlap across conditions, enabling more reliable predictions.

## Applications in scvi-tools

### Batch counterfactual (scVI)

```python
# Predict expression for cell as if it were in batch "batch_2"
norm_expr = model.get_normalized_expression(adata=adata, transform_batch="batch_2")
```

### Other applications

- Cell-type-specific sample-level effects (MrVI)
- Predicting chemical perturbation responses (scGen, CPA)
- Cross-species perturbation response prediction
- Understanding batch correction in gene space

## References

- Boyeau et al. (2024), *Deep generative modeling of sample-level heterogeneity in single-cell genomics*, bioRxiv.
- Lotfollahi et al. (2023), *Predicting cellular responses to complex perturbations in high-throughput screens*, Molecular Systems Biology.
