# Data handling in scvi-tools

In this tutorial we will cover how data is handled in scvi-tools.

Sections:

1. Introduction to the `registry` comprised of `data_registry`, `state_registry`, and `summary_stats`.
1. Explanation of `AnnDataField` classes and how they populate the `registry` via the `AnnDataManager`.
1. Data loading with `AnnDataLoader()` outside of scvi-tools models.
1. Writing a `setup_anndata()` function for an scvi-tools model.

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import numpy as np
import scvi
import torch.nn
from scvi.data import AnnDataManager
from scvi.data.fields import CategoricalObsField, LayerField
from scvi.dataloaders import AnnDataLoader
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

## Recording AnnData state with object registration

Scvi-tools knows what subset of AnnData to load into models during training/inference via a data registration process handled by `setup_anndata()`.

This setup process is orchestrated by an `AnnDataManager` object which wraps the `AnnData` object and creates a corresponding `registry`.

In this section we enumerate the fields in the `registry` object. The registry takes the form of a nested dictionary and is stored as an instance variable of an `AnnDataManager` object, `adata_manager.registry`.

The top level of the registry contains the following keys:

- `scvi_version` keeps track of the version of scvi-tools used to setup the AnnData Object.
- `model_name` and `setup_args` keep track of the model and arguments used to run `setup_anndata()`. These fields are optional, since the `AnnDataManager` can also be created outside of a `setup_anndata()` function.
- `field_registries` is dictionary which maps registry keys (e.g. `batch`, `labels`) to additional field-specific information.

Within each field registry, there the following three keys:

- `data_registry` contains the location of data to load. This is what is used by the DataLoaders to iterate over the AnnData.
- `state_registry` contains any state (e.g. categorical mappings for batch) relevant to the field during `register_field()`.
- `summary_stats` contains summary statistics relevant to the field.

Here we construct an `AnnDataManager` and create a `registry` via `register_fields`. In the next section, we will breakdown how the `registry` is populated as a function of the `AnnDataFields`. We can visualize the contents of the `registry` via the function `view_registry()`.

```python
adata = scvi.data.synthetic_iid()

anndata_fields = [
    LayerField(registry_key="x", layer=None, is_count_data=True),
    CategoricalObsField(registry_key="batch", attr_key="batch"),
]
adata_manager = AnnDataManager(fields=anndata_fields)
adata_manager.register_fields(adata)
print(adata_manager.registry.keys())
```

```python
adata_manager.view_registry()
```

The above summary incorporates all three of the components making up each field registry as mentioned before.

### Data Registry

First, lets turn our attention to the `data_registry`.

This is used by the `AnnDataLoader` during training to

- Access the correct "slots" of AnnData
- Minibatch the data, while optionally densifying sparse-formatted data

Each key of the `data_registry` is the name of tensor and is used to retreive the data from the dataloader output.

- All the data registered via `register_fields()` have registry keys associated with them, as defined in the `AnnDataField` class.

The value of each key in the `data_registry` is a dictionary with two keys: `attr_name` and `attr_key`.

- `attr_name` is the attribute of `adata` to load data from eg. `obs`, `obsm`, `layers`.
- `attr_key` is the key of the attribute to access the data.

For example, based off the following data_registry, batch information is loaded from `adata.obs['_scvi_batch']` and will be accessible via `batch`.

While the data registry dictionary is stored within the `registry`, the `AnnDataManager` provides a helper method, `adata_manager.data_registry`, which coalesces the full data registry across each of the fields. This helper method additionally wraps the dictionary in a custom `attrdict` class which allows dictionary access via dot notation (e.g. `data_registry.batch.attr_name`).

```python
data_registry = adata_manager.data_registry
data_registry
```

```python
print(data_registry["batch"])
print(data_registry.batch.attr_key)
```

### State Registries

During the data registration process, we also keep track of additional information from the registration process, necessary for model initialization or downstream functionality. For example, for the batch field, scvi-tools keeps track of the location of the original data as well as the categorical to integer mappings.

The batch state registry holds the following two keys:

- `original_key` is the original key passed in by the user to load the data.
- `categorical_mapping` is the categorical to integer mapping of the data. The index of the category is its corresponding integer representation.

We can access a state registry via the function `AnnDataManager.get_state_registry()` which takes a registry key.

```python
batch_state_registry = adata_manager.get_state_registry("batch")
print(batch_state_registry.keys())

print(f"Categorical mapping: {batch_state_registry.categorical_mapping}")
print(f"Original key: {batch_state_registry.original_key}")
```

### Summary Stats

Lastly, we have the summary stats dictionary which is a dictionary meant to store summary statistics frequently used in models, to avoid redundancy and for summarization in `view_registry()`. Like the other two components, the `AnnDataManager` has a helper method in the form of the property `adata_manager.summary_stats`.

```python
adata_manager.summary_stats
```

## AnnDataManager and AnnDataFields

Now that we have gone over the registered state of an `AnnDataManager`, we can go over how the underlying logic is organized.

While the `AnnDataManager` provides the main interface to the data registration components, the logic specific to each field is encapsulated in `AnnDataField` classes (any child class of `BaseAnnDataField`).

An `AnnDataField` class contains four main functions to be implemented:

1. `register_field` sets up the relevant field on the AnnData object and returns the state registry for this field.
1. `validate_field` is a function called before `register_field`. E.g. checks if the data field is present on the AnnData object.
1. `transfer_field` is a function similar to `register_field`, but additionally takes a source `state_registry` which can modify the behavior of registration. E.g. for categorical fields we may want to maintain the source categories and append any additional categories on the target AnnData object for downstream transfer learning.
1. `get_summary_stats` is a function that takes a `state_registry` and outputs the summary stat dictionary. Note, this means the summary statistics must be a function of what is stored in `state_registry`.

Together, the set of `AnnDataField`s produces the `registry` detailed in part 1.

```python
print(adata_manager.fields)
```

```python
adata2 = scvi.data.synthetic_iid()
batch_field = adata_manager.fields[1]
print("Before register_field:")
print(adata2)
print()

batch_state_registry = batch_field.register_field(adata2)
print("After register_field:")
print(adata2)
print()
print(f"State registry: {batch_state_registry}")
```

Notice how in this case the batch field's `register_field()` function adds an additional `.obs` field that stores an encoded version of the `adata.obs['batch']` column. The categorical mapping array order corresponds to the integer encoding of the category.

```{important}
Adding data inplace to an AnnData object should be done with care. Most fields do not add any data; however, for categorical data it is faster to encode the categories inplace instead of on-the-fly during data loading.
```

`adata_manager.transfer_fields()` can be used to produce a new `AnnDataManager` for a target `AnnData` object that follows the same structure as the original `AnnData`. This can be useful in models that are trained with an `AnnData` object, then used to make predictions on new query data. Under the hood, this calls the `transfer_field()` function of each field in the `AnnDataManager`.

In the example below, we try to transfer the batch field onto a new `AnnData` object with an extra batch category. In this case, the `CategoricalObsField.transfer_field()` function is parameterized with a `extend_categories` kwarg which, when `True`, will extend the batch category set as necessary. If marked `extend_categories=False`, `transfer_field()` will raise an error, which may be desired behavior in cases where we want to ensure that query data does not contain any batch categories missing from the train data.

```python
adata3 = scvi.data.synthetic_iid(n_batches=3)
try:
    adata_manager.transfer_fields(adata_target=adata3)
except ValueError as e:
    print(e)  # Errors due to additional batch_2 category absent from adata_manager.adata
```

```python
adata3_manager = adata_manager.transfer_fields(adata_target=adata3, extend_categories=True)
adata3_manager.view_registry()  # batch_2 appended to the batch category mapping
```

## DataLoaders

`AnnDataLoader` is the base dataloader for scvi-tools. In this section we show how the data registered is loaded by `AnnDataLoader`.

Parameters of `AnnDataLoader`:

- `adata_manager`: `AnnDataManager` object to load data from.
- `shuffle`: if True will shuffle the data beforehand.
- `indices`: can provide a subset of indices to load from (Useful when doing train/test splits).
- `data_and_attributes`: a dictionary where the key corresponds to its key in the `data_registry` and the value is the numpy data type. By default, all data is passed to the model as `np.float32`.
- `data_loader_kwargs`: additional arguments from `torch.utils.data.DataLoader`.

First, we construct an `AnnDataLoader` and get the first batch. Then we will enumerate all the values in the batch. The variable **data_batch** contains the first batch of data. It is a dictionary whose values are the tensors registered in the previous section via `register_fields()`.

```python
# initialize an AnnDataLoader which will iterate over our anndata
adl = AnnDataLoader(adata_manager, shuffle=False, batch_size=10)

# get the first batch of data
data_batch = next(iter(adl))
```

Notice that the keys in **data_batch** are the same as the keys in the `data_registry`.

```python
print("data_batch_keys:")
print(data_batch.keys())
```

```python
adata_manager.data_registry.keys()
```

If we look at the labels for the first batch from the data loader, it corresponds to the labels of the first 10 cells of our AnnData.

```python
adata.obs["batch"][:10]
```

```python
# CategoricalObsField.register_field() automatically encoded the categorical labels as integers
data_batch["batch"]
```

```python
print(data_batch["x"].shape)  # shape is batch_size x n_genes
print(data_batch["batch"].shape)  # shape is batch_size x 1
```

By default, all the data loaded in scvi-tools is `np.float32`. If you wish to load as a different datatype, you can pass in a dictionary where the key corresponds to a key in the data registry and the value is the datatype.

In the following snippet, we load some continuous data as `np.float64` and integer data as `np.long32`.

```python
adl = AnnDataLoader(adata_manager, shuffle=False, batch_size=10)
data_batch = next(iter(adl))

# by default data has the dtype np.float32
print(data_batch["x"].dtype)
print(data_batch["batch"].dtype)
```

```python
data_batch.keys()
```

To specify the datatype of each key, we can use the `data_and_attributes` parameter of AnnDataLoader. Here we make make `X` an `np.long` and our `cat_covs` an `np.float64`, but keep everything else as `np.float32`.

```python
# the keys of data_and_attributes should correspond to keys in the data registry
data_registry_keys = adata_manager.data_registry.keys()
print("Data Registry keys:", data_registry_keys)
```

```python
data_and_attributes = {}
for key in data_registry_keys:
    if key == "x":
        data_and_attributes[key] = np.int64
    else:
        data_and_attributes[key] = np.float32
print(data_and_attributes)
```

```python
adl = AnnDataLoader(
    adata_manager, shuffle=False, batch_size=10, data_and_attributes=data_and_attributes
)
data_batch = next(tensors for tensors in adl)

# by default data has the dtype np.float32
print(data_batch["x"].dtype)
print(data_batch["batch"].dtype)
```

Finally, if the `data_and_attributes` parameter is used, it will only load the keys of the passed in dictionary. For example, if the only key in the dictionary passed in to `data_and_attributes` is X, the data loader will only load X.

```python
data_and_attributes = {"x": float}
adl = AnnDataLoader(
    adata_manager, shuffle=False, batch_size=10, data_and_attributes=data_and_attributes
)
data_batch = next(iter(adl))

print(data_batch.keys())
```

### Using the DataLoader

Below we demonstrate a toy use case where we can take advantage of the `AnnDataLoader` to minibatch data from our `AnnData` object into a model. In this example, we train a simple linear regression model.

```{important}
The DataLoader will not move data to a device (e.g., GPU). This is the responsibility of the user. Alternatively, frameworks like [PyTorch Lightning](https://pytorch-lightning.readthedocs.io/en/latest/) will do this autmoatically for users.
```

```python
# Initialize synthetic_iid data and register with an AnnDataManager
n_genes, n_labels = 10, 3
adata = scvi.data.synthetic_iid(n_genes=n_genes, n_labels=n_labels)
anndata_fields = [
    LayerField(registry_key="x", layer=None, is_count_data=True),
    CategoricalObsField(registry_key="labels", attr_key="labels"),
]
adata_manager = AnnDataManager(fields=anndata_fields)
adata_manager.register_fields(adata)

# Regression model
linear_reg_model = torch.nn.Linear(n_genes, 1)

# Define loss and optimize
loss_fn = torch.nn.MSELoss(reduction="sum")
optim = torch.optim.Adam(linear_reg_model.parameters(), lr=0.05)


def train(x, labels):
    labels = labels.float()
    # run the model forward on the data
    label_pred = linear_reg_model(x).squeeze(-1)
    # calculate the mse loss
    loss = loss_fn(label_pred, labels.squeeze())
    # initialize gradients to zero
    optim.zero_grad()
    # backpropagate
    loss.backward()
    # take a gradient step
    optim.step()
    return loss


# Create AnnDataLoader
# drop a minibatch if it has 3 or fewer observations
data_loader = AnnDataLoader(
    adata_manager,
    batch_size=128,
    shuffle=True,
)

for i in range(5):
    for data in data_loader:
        loss = train(data["x"], data["labels"])
    print(f"[iteration {i + 1}] loss: {loss.item()}")
```

## `scvi-tools` Data Registration

Scvi-tools models produce an `AnnDataManager` instance in the `setup_anndata()` function for the purpose of data registration.

`setup_anndata()` is used to setup data fields specific to each model.

Here we will go over the parameters of one instance of a `setup_anndata()` method, `scvi.model.SCVI.setup_anndata()`:

- `adata` is the input `AnnData` object.
- `layer` is the key in `adata.layers` to use for the input data matrix. By default, this is None and the input data matrix will be pulled from `adata.X`.
- `batch_key` is the key in `adata.obs` for batch information. If this is None, will assume that all the data is the same batch.
- `labels_key` is the key in `adata.obs` for label information. If this is None, will assume that all the data has the same label.
- `size_factor_key` is the key in `adata.obs` that optionally stores size factors for computing the likelihood. If this is None, the library size is used to compute the size factor.
- `categorical_covariate_keys` is a list of keys in `adata.obs` for categorical covariates.
- `continuous_covariate_key` is a list of keys in `adata.obs` for continuous covariates.

Under the hood:

- For all categorical data (batch, labels, categorical covariates), scvi will automatically compute a mapping from values to integers. Eg. `['a','b','c','a']` will become `[0,1,2,0]`.
- For data fields registered with `scvi.model.SCVI.setup_anndata()`, scvi will copy the data to a seperate field in the anndata.
  - `batch_key` is copied to `scvi.obs['_scvi_batch']` with its integer encoding
  - `labels_key` is copied to `scvi.obs['_scvi_labels']` with its integer encoding
  - keys in `categorical_covariate_keys` are concatenated and saved as a pandas DataFrame and stored in `adata.obsm['_scvi_extra_categorical_covs']` with its integer encoding.
  - keys in `continuous_covariate_keys` are concatenated and saved as a pandas DataFrame and stored in `adata.obsm['_scvi_extra_continuous_covs']`

In the following code, we first format an example AnnData Object to setup for scvi-tools, then call `scvi.model.SCVI.setup_anndata()` to register all the tensors we want to load to the model during training.
For our example AnnData Object, we build off the `synthetic_iid()` dataset, copy X to a layer, and add continuous and categorical covariates to the AnnData.

```python
adata = scvi.data.synthetic_iid()
adata.layers["raw_counts"] = adata.X.copy()
adata.obs["my_categorical_covariate"] = ["A"] * 200 + ["B"] * 200
adata.obs["my_continuous_covariate"] = np.random.randint(0, 100, 400)
print(adata)
```

```python
scvi.model.SCVI.setup_anndata(
    adata,
    batch_key="batch",
    labels_key="labels",
    layer="raw_counts",
    categorical_covariate_keys=["my_categorical_covariate"],
    continuous_covariate_keys=["my_continuous_covariate"],
)
```

Under the hood, this method creates an `AnnDataManager` instance and stores it in a model-specific manager store until a model is initialized with the same `AnnData` object. We can visualize the resulting `registry` via `view_anndata_setup()`. This calls `view_registry()` under the hood.

```python
model = scvi.model.SCVI(adata)
model.view_anndata_setup()
```

Each model defines a set of appropriate `AnnDataField`s and orchestrates calls to these functions and stores the resulting `registry` as an instance variable. As mentioned before, the `AnnDataManager` is constructed during `setup_anndata()` and retrieved during model initialization.

Here we have an abbreviated version of a `setup_anndata()` implementation for a model that only takes a `layer` kwarg and a `batch_key`:

```python
@classmethod
def setup_anndata(
    cls,
    adata: AnnData,
    layer: Optional[str] = None,
    batch_key: Optional[str] = None,
    **kwargs,  # Used when loading a model with a new AnnData object.
):
    setup_method_args = cls._get_setup_method_args(
        **locals()
    )  # Used for saving/loading purposes.
    anndata_fields = [
        LayerField(REGISTRY_KEYS.X_KEY, layer, is_count_data=True),
        CategoricalObsField(REGISTRY_KEYS.BATCH_KEY, batch_key),
    ]
    adata_manager = AnnDataManager(
        fields=anndata_fields, setup_method_args=setup_method_args
    )
    adata_manager.register_fields(adata, **kwargs)
    cls.register_manager(
        adata_manager
    )  # Stores the AnnDataManager in a class-specific manager store.
```

The `setup_anndata()` function itself is quite simple since any complexity in preprocessing is contained within the `AnnDataField` functions. By factorizing the preprocessing steps into each subclass, model developers can easily extend and reuse logic across models and fields.

## Custom DataLoaders

In SCVI, custom dataloaders allow you to create a tailored data pipeline that can handle unique formats or complex datasets not covered by the default loaders. A custom dataloader can be useful when you have a specific structure for your data or need to preprocess it in a particular way before feeding it into the model, in order to gain some advantage.
See more [here](https://docs.scvi-tools.org/en/stable/user_guide/use_case/custom_dataloaders.html)

In SCVI-tools a custom dataloader class is a LightningDataModule inherited class which should create batches of data from an external source and feed them into a scvi pytorch model during training and inference.

Beucase it is tailored made for a specific data source, custom dataloders differ from each other. 
Nevertheless, there are some common bulding blocks that are required in order to create it:
- a 'linkage' to the data source that the custom data loder need to query from.
- `batch_key` is the key for batch information. 
- `labels_key` is the key for label information. 
- `unlabeled_category` is the key for the unlabeled groyp information. 
- `train_dataloader` a function to create a training set pytorch Dataloder
- `val_dataloader` a function to create a validation set pytorch Dataloder
- `registry` its the manual implementaion of the scvi tools registry as a dict filled with information taken from the datamodule itself.
  Note that each datamodule will have its own registry implementation and also it should be extended to work with other models (currently only SCVI and SCANVI are supported, but it should be generic enough to work with any model)

