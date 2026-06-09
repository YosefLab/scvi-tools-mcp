# VELOVI — API Reference

**Class:** `scvi.external.velovi._model.VELOVI`

**Signature:** `VELOVI(adata: 'AnnData', n_hidden: 'int' = 256, n_latent: 'int' = 10, n_layers: 'int' = 1, dropout_rate: 'float' = 0.1, gamma_init_data: 'bool' = False, linear_decoder: 'bool' = False, **model_kwargs)`

## Docstring

Velocity Variational Inference :cite:p:`GayosoWeiler23`.

Parameters
----------
adata
    AnnData object that has been registered via :meth:`~scvi.external.VELOVI.setup_anndata`.
n_hidden
    Number of nodes per hidden layer.
n_latent
    Dimensionality of the latent space.
n_layers
    Number of hidden layers used for encoder and decoder NNs.
dropout_rate
    Dropout rate for neural networks.
gamma_init_data
    Initialize gamma using the data-driven technique.
linear_decoder
    Use a linear decoder from latent space to time.
**model_kwargs
    Keyword args for :class:`~scvi.external.velovi.VELOVAE`

## setup_anndata

```python
VELOVI.setup_anndata(adata: 'AnnData', spliced_layer: 'str', unspliced_layer: 'str', **kwargs) -> 'AnnData | None'
```

Sets up the :class:`~anndata.AnnData` object for this model.

A mapping will be created between data fields used by this model to their respective locations in
adata. None of the data in adata are modified. Only adds fields to adata.

Parameters
----------
adata
    AnnData object. Rows represent cells, columns represent features.
spliced_layer
    Layer in adata with spliced normalized expression.
unspliced_layer
    Layer in adata with unspliced normalized expression.

Returns
-------
None. Adds the following fields:

.uns['_scvi']
    `scvi` setup dictionary
.obs['_scvi_labels']
    labels encoded as integers
.obs['_scvi_batch']
    batch encoded as integers

## train

```python
VELOVI.train(self, max_epochs: 'int | None' = 500, lr: 'float' = 0.01, weight_decay: 'float' = 0.01, accelerator: 'str' = 'auto', devices: 'int | list[int] | str' = 'auto', train_size: 'float | None' = None, validation_size: 'float | None' = None, batch_size: 'int' = 256, early_stopping: 'bool' = True, gradient_clip_val: 'float' = 10, plan_kwargs: 'dict | None' = None, external_indexing: 'list[np.ndarray]' = None, **trainer_kwargs)
```

Train the model.

Parameters
----------
max_epochs
    Number of passes through the dataset. If ``None``, defaults to
    `np.min([round((20000 / n_cells) * 400), 400])`
lr
    Learning rate for optimization.
weight_decay
    Weight decay for optimization.
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
    Size of the training set in the range ``[0.0, 1.0]``.
validation_size
    Size of the test set. If ``None``, defaults to ``1 - train_size``. If
    ``train_size + validation_size < 1``, the remaining cells belong to a test set.
batch_size
    Minibatch size to use during training.
early_stopping
    Perform early stopping. Additional arguments can be passed in ``**kwargs``.
    See :class:`~scvi.train.Trainer` for further options.
gradient_clip_val
    Value for gradient clipping.
plan_kwargs
    Keyword args for :class:`~scvi.train.TrainingPlan`. Keyword arguments passed to
    this method will overwrite values present in ``plan_kwargs``, when appropriate.
external_indexing
    A list of data split indices in the order of training, validation, and test sets.
    Validation and test set are not required and can be left empty.
**trainer_kwargs
    Other keyword args for :class:`~scvi.train.Trainer`.
