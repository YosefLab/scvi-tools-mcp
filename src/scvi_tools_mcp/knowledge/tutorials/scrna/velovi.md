# Variational inference for RNA velocity with VeloVI

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvelo as scv
import seaborn as sns
import torch
from velovi import VELOVI, preprocess_data
```

## Load and preprocess data

```python
adata = scv.datasets.pancreas()
```

```python
scv.pp.filter_and_normalize(adata, min_shared_counts=30, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
```

```python
adata = preprocess_data(adata)
```

## Train and apply model

```python
VELOVI.setup_anndata(adata, spliced_layer="Ms", unspliced_layer="Mu")
vae = VELOVI(adata)
vae.train()
```

```python
fig, ax = plt.subplots()
vae.history["elbo_train"].iloc[20:].plot(ax=ax, label="train")
vae.history["elbo_validation"].iloc[20:].plot(ax=ax, label="validation")
plt.legend()
```

### Get model outputs

```python
def add_velovi_outputs_to_adata(adata, vae):
    latent_time = vae.get_latent_time(n_samples=25)
    velocities = vae.get_velocity(n_samples=25, velo_statistic="mean")

    t = latent_time
    scaling = 20 / t.max(0)

    adata.layers["velocity"] = velocities / scaling
    adata.layers["latent_time_velovi"] = latent_time

    adata.var["fit_alpha"] = vae.get_rates()["alpha"] / scaling
    adata.var["fit_beta"] = vae.get_rates()["beta"] / scaling
    adata.var["fit_gamma"] = vae.get_rates()["gamma"] / scaling
    adata.var["fit_t_"] = (
        torch.nn.functional.softplus(vae.module.switch_time_unconstr).detach().cpu().numpy()
    ) * scaling
    adata.layers["fit_t"] = latent_time.values * scaling[np.newaxis, :]
    adata.var["fit_scaling"] = 1.0


add_velovi_outputs_to_adata(adata, vae)
```

```python
scv.tl.velocity_graph(adata)
```

```python
scv.pl.velocity_embedding_stream(adata, basis="umap")
```

### Intrinsic uncertainty

```python
uncertainty_df, _ = vae.get_directional_uncertainty(n_samples=100)
uncertainty_df.head()
```

```python
for c in uncertainty_df.columns:
    adata.obs[c] = np.log10(uncertainty_df[c].values)
```

```python
sc.pl.umap(
    adata,
    color="directional_cosine_sim_variance",
    cmap="Greys",
    vmin="p1",
    vmax="p99",
)
```

### Extrinsic uncertainty

```python
def compute_extrinisic_uncertainty(adata, vae, n_samples=25) -> pd.DataFrame:
    import io
    from contextlib import redirect_stdout

    from scvi.utils import track
    from velovi._model import _compute_directional_statistics_tensor

    extrapolated_cells_list = []
    for i in track(range(n_samples)):
        with io.StringIO() as buf, redirect_stdout(buf):
            vkey = f"velocities_velovi_{i}"
            v = vae.get_velocity(n_samples=1, velo_statistic="mean")
            adata.layers[vkey] = v
            scv.tl.velocity_graph(adata, vkey=vkey, sqrt_transform=False, approx=True)
            t_mat = scv.utils.get_transition_matrix(
                adata, vkey=vkey, self_transitions=True, use_negative_cosines=True
            )
            extrapolated_cells = np.asarray(t_mat @ adata.layers["Ms"])
            extrapolated_cells_list.append(extrapolated_cells)
    extrapolated_cells = np.stack(extrapolated_cells_list)
    df = _compute_directional_statistics_tensor(extrapolated_cells, n_jobs=-1, n_cells=adata.n_obs)
    return df
```

```python
ext_uncertainty_df = compute_extrinisic_uncertainty(adata, vae)
```

```python
for c in ext_uncertainty_df.columns:
    adata.obs[c + "_extrinisic"] = np.log10(ext_uncertainty_df[c].values)
```

```python
sc.pl.umap(
    adata,
    color="directional_cosine_sim_variance_extrinisic",
    vmin="p1",
    vmax="p99",
)
```

### Permutation score

```python
perm_df, _ = vae.get_permutation_scores(labels_key="clusters")
adata.var["permutation_score"] = perm_df.max(1).values
```

```python
sns.kdeplot(data=adata.var, x="permutation_score")
```
