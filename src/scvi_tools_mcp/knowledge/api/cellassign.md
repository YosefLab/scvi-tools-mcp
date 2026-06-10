# CELLASSIGN — API Reference

**Class:** `scvi.external.cellassign._model.CellAssign`

**Signature:** `CellAssign(adata: 'AnnData', cell_type_markers: 'pd.DataFrame', **model_kwargs)`

## Docstring

Reimplementation of CellAssign for reference-based annotation :cite:p:`Zhang19`.

Original implementation: https://github.com/irrationone/cellassign.

Parameters
----------
adata
    single-cell AnnData object that has been registered via
    :meth:`~scvi.external.CellAssign.setup_anndata`. The object should be subset to contain the
    same genes as the cell type marker dataframe.
cell_type_markers
    Binary marker gene DataFrame of genes by cell types. Gene names corresponding to
    `adata.var_names` should be in the DataFrame index,
    and cell type labels should be the columns.
**model_kwargs
    Keyword args for :class:`~scvi.external.cellassign.CellAssignModule`

Examples
--------
>>> adata = scvi.data.read_h5ad(path_to_anndata)
>>> library_size = adata.X.sum(1)
>>> adata.obs["size_factor"] = library_size / np.mean(library_size)
>>> marker_gene_mat = pd.read_csv(path_to_marker_gene_csv)
>>> bdata = adata[:, adata.var.index.isin(marker_gene_mat.index)].copy()
>>> CellAssign.setup_anndata(bdata, size_factor_key="size_factor")
>>> model = CellAssign(bdata, marker_gene_mat)
>>> model.train()
>>> predictions = model.predict(bdata)

Notes
-----
Size factors in the R implementation of CellAssign are computed using scran. An approximate
approach computes the sum of UMI counts (library size) over all genes and divides by the mean
library size.

See further usage examples in the following tutorial:

1. :doc:`/tutorials/notebooks/scrna/cellassign_tutorial`

## setup_anndata

```python
CellAssign.setup_anndata(adata: 'AnnData', size_factor_key: 'str', batch_key: 'str | None' = None, categorical_covariate_keys: 'list[str] | None' = None, continuous_covariate_keys: 'list[str] | None' = None, layer: 'str | None' = None, **kwargs)
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
size_factor_key
    key in `adata.obs` with continuous valued size factors.
batch_key
    key in `adata.obs` for batch information. Categories will automatically be converted into
    integer categories and saved to `adata.obs['_scvi_batch']`. If `None`, assigns the same batch
    to all the data.
layer
    if not `None`, uses this as the key in `adata.layers` for raw count data.
categorical_covariate_keys
    keys in `adata.obs` that correspond to categorical data.
    These covariates can be added in addition to the batch covariate and are also treated as
    nuisance factors (i.e., the model tries to minimize their effects on the latent space). Thus,
    these should not be used for biologically-relevant factors that you do _not_ want to correct
    for.
continuous_covariate_keys
    keys in `adata.obs` that correspond to continuous data.
    These covariates can be added in addition to the batch covariate and are also treated as
    nuisance factors (i.e., the model tries to minimize their effects on the latent space). Thus,
    these should not be used for biologically-relevant factors that you do _not_ want to correct
    for.

## train

```python
CellAssign.train(self, max_epochs: 'int' = 400, lr: 'float' = 0.003, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, shuffle_set_split: 'bool' = True, batch_size: 'int' = 1024, datasplitter_kwargs: 'dict | None' = None, plan_kwargs: 'dict | None' = None, early_stopping: 'bool' = True, early_stopping_patience: 'int' = 15, early_stopping_warmup_epochs: 'int' = 0, early_stopping_min_delta: 'float' = 0.0, **kwargs)
```

Trains the model.

Parameters
----------
max_epochs
    Number of epochs to train for
lr
    Learning rate for optimization.
accelerator
    Supports passing different accelerator types `("cpu", "gpu", "tpu", "ipu", "hpu",
    "mps, "auto")` as well as custom accelerator instances.
devices
    The devices to use. Can be set to a non-negative index (`int` or `str`), a sequence
    of device indices (`list` or comma-separated `str`), the value `-1` to indicate all
    available devices, or `"auto"` for automatic selection based on the chosen
    `accelerator`. If set to `"auto"` and `accelerator` is not determined to be `"cpu"`,
    then `devices` will be set to the first available device.
train_size
    Size of the training set in the range [0.0, 1.0].
validation_size
    Size of the test set. If `None`, defaults to 1 - `train_size`. If
    `train_size + validation_size < 1`, the remaining cells belong to a test set.
shuffle_set_split
    Whether to shuffle indices before splitting. If `False`, the val, train, and test set
    are split in the sequential order of the data according to `validation_size` and
    `train_size` percentages.
batch_size
    Minibatch size to use during training.
datasplitter_kwargs
    Additional keyword arguments passed into :class:`~scvi.dataloaders.DataSplitter`.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`.
early_stopping
    Adds callback for early stopping on validation_loss
early_stopping_patience
    Number of times early stopping metric cannot improve over early_stopping_min_delta
early_stopping_warmup_epochs
    Wait for a certain number of warm-up epochs before the early stopping starts monitoring
early_stopping_min_delta
    Threshold for counting an epoch towards patience
    `train()` will overwrite values present in `plan_kwargs`, when appropriate.
**kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
