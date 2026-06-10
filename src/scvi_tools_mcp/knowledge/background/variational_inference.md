# Variational Inference

## Problem Setup

For models with latent variables $z$ and observed data $x$, the posterior $p(z|x) = p(x|z)p(z)/p(x)$ is intractable because:

$$p(x) = \int p(x|z)p(z)\, dz$$

cannot be computed analytically.

## Variational Inference

Cast posterior inference as an optimization problem: minimize KL divergence between an approximate posterior $q \in Q$ and the true posterior.

$$q^\star = \arg\min_{q \in Q} \; \text{KL}(q(z) \| p(z|x))$$

Using Bayes rule, this is equivalent to maximizing the **Evidence Lower Bound (ELBO)**:

$$q^\star = \arg\max_{q \in Q} \; \mathbb{E}_q[\log p(x|z)] - \text{KL}(q(z) \| p(z))$$

The ELBO lower bounds the log-evidence: $\log p_\theta(x) \geq \text{ELBO}$

## End-to-End Learning

With model parameters $\theta$ and variational parameters $\phi$:

$$\text{ELBO} := \mathbb{E}_{q_\phi}[\log p_\theta(x|z)] - \text{KL}(q_\phi(z) \| p_\theta(z))$$

Maximizing ELBO jointly over $\theta$ and $\phi$ gives:

- Model parameter estimates
- Approximate posterior over latent variables

This is also known as minimizing $\text{KL}(q_\phi(z) \| p_\theta(z|x))$ with a moving true posterior.

## Amortized Variational Inference

In single-cell data with millions of cells, having per-cell variational parameters doesn't scale. **Amortization**: use a neural network (encoder) that takes $x$ as input and outputs $q(z)$ parameters (mean, variance). The network parameters are shared across all cells.

Trade-off: scales well, but introduces an **amortization gap** — the shared encoder may not find the optimal $q$ for every cell individually.

This technique is also called **auto-encoding variational Bayes (AEVB)** and is the basis for variational autoencoders (VAEs). All major scvi-tools models use this approach.

## Application in scvi-tools

In scVI:

- Latent variable $z$: low-dimensional cell state
- Model parameters $\theta$: decoder neural network params + dispersion params
- Variational parameters $\phi$: encoder neural network params
- ELBO = reconstruction of gene counts + KL regularization toward Normal(0,I) prior

## References

- Blei, Kucukelbir, McAuliffe (2017), *Variational inference: A review for statisticians*, JASA.
- Cremer, Li, Duvenaud (2018), *Inference suboptimality in variational autoencoders*, ICML.
- Kingma, Welling (2019), *An introduction to variational autoencoders*, arXiv.
