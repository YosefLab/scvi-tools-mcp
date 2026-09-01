# Constructing a high-level model

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import os
import tempfile
from collections.abc import Sequence

import numpy as np
import scvi
import torch
from anndata import AnnData
from scvi import REGISTRY_KEYS
from scvi.data import AnnDataManager
from scvi.data.fields import (
    CategoricalJointObsField,
    CategoricalObsField,
    LayerField,
    NumericalJointObsField,
    NumericalObsField,
)
from scvi.model.base import BaseModelClass, UnsupervisedTrainingMixin, VAEMixin
from scvi.module import VAE
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```{note}
You can modify `save_dir` below to change where the data files for this tutorial are saved.
```

```python
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

At this point we have covered

1. Data registration via `setup_anndata` and dataloaders via `AnnDataLoader`
1. Building a probabilistic model by subclassing `BaseModuleClass`

In this tutorial, we will cover the highest-level classes in `scvi-tools`: the model classes. The main purpose of these classes (e.g., `scvi.model.SCVI`) is to wrap the actions of module instantiation, training, and subsequent posterior queries of our module into a convenient interface. These model classes are the fundamental objects driving scientific analysis of data with `scvi-tools`. Out of convention, we will refer to these objects as "models" and the lower-level objects presented in the previous tutorial as "modules".

## A simple model class

Here we will walkthrough an example of building the `scvi.model.SCVI` class. We will progressively add functionality to the class.

### Sketch of `BaseModelClass`

Let us start by providing a high level overview of `BaseModelClass` that we will inherit. Note that this is pseudocode to provide intuition. We see that `BaseModelClass` contains some unverisally applicable methods, and some private methods (conventionally starting with `_` in Python) that will become useful after training the model.

```python
class MyModel(UnsupervisedTrainingMixin, BaseModelClass):
    def __init__(self, adata):
        # sets some basic attributes like is_trained_
        # record the setup_dict registered in the adata
        self.adata = adata
        self.scvi_setup_dict_ = adata.uns["_scvi"]
        self.summary_stats = self.scvi_setup_dict_["summary_stats"]

    def _validate_anndata(self, adata):
        # check that anndata is equivalent by comparing
        # to the initial setup_dict
        pass

    def _make_dataloader(self, adata):
        # return a dataloader to iterate over adata
        pass

    def train(self):
        # Universal train method provided by UnsupservisedTrainingMixin
        # BaseModelClass does not come with train
        # In general train methods are straightforward to compose manually
        pass

    def save(self):
        # universal save method
        # saves modules, anndata setup dict, and attributes ending with _
        pass

    def load(self):
        # universal load method
        pass

    @classmethod
    def setup_anndata(cls, adata):
        # anndata registration method
        pass
```

### Baseline version of `SCVI` class

Let's now create the simplest possible version of the `SCVI` class. We inherit the `BaseModelClass`, and write our `__init__` method.

We take care to do the following:

1. Set the `module` attribute to be equal to our `VAE` module, which here is the torch-level version of scVI.
1. Add a `_model_summary_string` attr, which will be used as a representation for the model.
1. Run `self.init_params_ = self._get_init_params(locals())`, which stores the arguments used to initialize the model, facilitating saving/loading of the model later.

To initialize the `VAE`, we can use the information in `self.summary_stats`, which is information that was stored in the anndata object at `setup_anndata()` time. In this example, we have only exposed `n_latent` to users through `SCVI`. In practice, we try to expose only the most relevant parameters, as all other parameters can be accessed by passing `model_kwargs`.

Finally, we write the `setup_anndata` class method, which is used to register the appropriate matrices inside the anndata that we will use to load data into the model. This method uses the `AnnDataManager` class to orchestrate the data registration process. More details about the `AnnDataManager` can be learned in our data handling tutorial.

```python
class SCVI(UnsupervisedTrainingMixin, BaseModelClass):
    """single-cell Variational Inference [Lopez18]_."""

    def __init__(
        self,
        adata: AnnData,
        n_latent: int = 10,
        **model_kwargs,
    ):
        super().__init__(adata)

        self.module = VAE(
            n_input=self.summary_stats["n_vars"],
            n_batch=self.summary_stats["n_batch"],
            n_latent=n_latent,
            **model_kwargs,
        )
        self._model_summary_string = (
            f"SCVI Model with the following params: \nn_latent: {n_latent}"
        )
        self.init_params_ = self._get_init_params(locals())

    @classmethod
    def setup_anndata(
        cls,
        adata: AnnData,
        batch_key: str | None = None,
        layer: str | None = None,
        **kwargs,
    ) -> AnnData | None:
        setup_method_args = cls._get_setup_method_args(**locals())
        anndata_fields = [
            LayerField(REGISTRY_KEYS.X_KEY, layer, is_count_data=True),
            CategoricalObsField(REGISTRY_KEYS.BATCH_KEY, batch_key),
            # Dummy fields required for VAE class.
            CategoricalObsField(REGISTRY_KEYS.LABELS_KEY, None),
            NumericalObsField(REGISTRY_KEYS.SIZE_FACTOR_KEY, None, required=False),
            CategoricalJointObsField(REGISTRY_KEYS.CAT_COVS_KEY, None),
            NumericalJointObsField(REGISTRY_KEYS.CONT_COVS_KEY, None),
        ]
        adata_manager = AnnDataManager(fields=anndata_fields, setup_method_args=setup_method_args)
        adata_manager.register_fields(adata, **kwargs)
        cls.register_manager(adata_manager)
```

Now we explore what we can and cannot do with this model. Let's get some data and initialize a `SCVI` instance. Of note, for testing purposes we like to use `scvi.data.synthetic_iid()` which returns a simple, small anndata object that was already run through `setup_anndata()`.

```python
adata = scvi.data.synthetic_iid()
adata
```

Above we saw in the `setup_anndata()` implementation that we ended the function with `cls.register_manager(adata_manager)`. This function stores the newly created `AnnDataManager` instance in a class-specific dictionary called `_setup_adata_manager_store`. Specifically, this maps from UUIDs (specific to each `AnnData` object; stored on `adata.uns["_scvi_uuid"]`) to `AnnDataManager` instances instantiated by that class's `setup_anndata()` function.

On model initialization, the model instance retrieves the `AnnDataManager` object specific to the passed in `adata`.

```python
SCVI.setup_anndata(adata, batch_key="batch")
print(f"adata UUID (assigned by setup_anndata): {adata.uns['_scvi_uuid']}")
print(f"AnnDataManager: {SCVI._setup_adata_manager_store[adata.uns['_scvi_uuid']]}")
model = SCVI(adata)
model
```

### More `AnnDataManager` Details

The `AnnDataManager` class stores state on data registered with scvi-tools. Since each manager is specific to a single `AnnData`, each model instance has an `AnnDataManager` instance for every `AnnData` object it has interfaced with. In addition to `setup_anndata()`, new `AnnDataManager` objects are created via the `_validate_anndata()` method when called on new `AnnData` objects (not the `AnnData` the model instance was initialized with). `_validate_anndata()` should be called in any method that references data on the `AnnData` object, via the scvi-tools data handling strategy (e.g. `get_latent_representation()`). Any instance-specific `AnnDataManager` objects are stored in a separate class-specific manager store called `_per_instance_manager_store`, which maps model instance UUIDs (assigned on initialization) and `AnnData` UUIDs to `AnnDataManager` instances. This avoids the issue of incorrect `AnnDataManager` retrieval when working with two model instances working over the same `AnnData` object.

```python
print(f"model instance UUID: {model.id}")
print(f"adata UUID: {adata.uns['_scvi_uuid']}")
print(
    "AnnDataManager for adata: "
    f"{SCVI._per_instance_manager_store[model.id][adata.uns['_scvi_uuid']]}"
)  # { model instance UUID: { adata UUID: AnnDataManager } }
```

```python
adata2 = scvi.data.synthetic_iid()
model._validate_anndata(adata2)
```

```python
print(f"adata2 UUID: {adata.uns['_scvi_uuid']}")
print(
    f"Model instance specific manager store: {SCVI._per_instance_manager_store[model.id]}"
)  # { model instance UUID: { adata UUID: AnnDataManager } }
```

Additionally, the data registration process can modify or add data on the `AnnData` object directly. As a result, if calls between two models are interleaved, it is possible that we refer to fields created by another model instance's data registration incorrectly. In order to avoid this, `_validate_anndata()` additionally checks the `AnnData` object for an `AnnDataManager`-specific UUID stored in `adata.uns['_scvi_manager_uuid']`. If this UUID is inconsistent with the `AnnDataManager` fetched from the manager store, this means the data registration must be replayed on the `AnnData` object before referencing any data on the `AnnData`. This is automatically done in `_validate_anndata()`.

As a result, we can interleave method calls on two model instances without worrying about this clobbering issue.

```python
SCVI.setup_anndata(adata, batch_key=None)  # No batch correction.
model2 = SCVI(adata)
print(f"Manager UUID: {model2.adata_manager.id}")
print(f"Last setup with manager UUID: {adata.uns['_scvi_manager_uuid']}")
print(f"Encoded batch obs field: {adata.obs['_scvi_batch']}")
```

```python
model._validate_anndata(adata)  # Replays registration on adata
print(f"Manager UUID: {model.adata_manager.id}")
print(f"Last setup with manager UUID: {adata.uns['_scvi_manager_uuid']}")
print(f"Encoded batch obs field: {adata.obs['_scvi_batch']}")
```

### The `train` method

A model can be trained simply by calling the `train` method.

```python
model.train(max_epochs=20)
```

We were able to train this model, as this method is inherited in the class. Let us now take a look at psedocode of the `train` method of `UnsupervisedTrainingMixin`. The function of each of these objects is described in the API reference.

```python
def train(
    self,
    max_epochs: Optional[int] = 100,
    train_size: float = 0.9,
    **kwargs,
):
    """Train the model."""
    # object to make train/test/val dataloaders
    data_splitter = DataSplitter(
        self.adata,
        train_size=train_size,
        validation_size=validation_size,
        batch_size=batch_size,
    )
    # defines optimizers, training step, val step, logged metrics
    training_plan = TrainingPlan(
        self.module,
        len(data_splitter.train_idx),
    )
    # creates Trainer, pre and post training procedures (Trainer.fit())
    runner = TrainRunner(
        self,
        training_plan=training_plan,
        data_splitter=data_splitter,
        max_epochs=max_epochs,
        **kwargs,
    )
    return runner()
```

We notice two new things:

1. A training plan (`training_plan`)
1. A train runner (`runner`)

The `TrainRunner` is a lightweight wrapper of the PyTorch lightning's [`Trainer`](https://pytorch-lightning.readthedocs.io/en/stable/trainer.html#trainer-class-api), which is a completely black-box method once a `TrainingPlan` is defined. So what does the `TrainingPlan` do?

1. Configures optimizers (e.g., Adam), learning rate schedulers.
1. Defines the training step, which runs a minibatch of data through the model and records the loss.
1. Defines the validation step, same as training step, but for validation data.
1. Records relevant metrics, such as the ELBO.

In `scvi-tools` we have `scvi.lightning.TrainingPlan`, which should cover many use cases, from VAEs and VI, to MLE and MAP estimation. Developers may find that they need a custom `TrainingPlan` for e.g,. multiple optimizers and complex training scheme. These can be written and used by the model class.

Developers may also overwrite this train method to add custom functionality like Early Stopping (see TOTALVI's train method). In most cases the higher-level train method can call `super().train()`, which would be the `BaseModelClass` train method.

### Using External Indices

In the previous example, we saw that by selecting the train size proportion in our data, as well as maybe the validation size of it, we automatically got the train / valid/ test splits that will be used during our model training and inference.

However, this is not always the case and we might want to pre-specified our splitting indices. This can be the case for reproducibility reasons or if we want to increase the abundance of rare cell types so we will converge quicker. So it actually matters to have custom indices on a limited compute budget.

There are 2 options to use external indices during model train:
1. By creating a DataSplitter pre model train
2. Directly as input to model train using the model datasplitter_kwargs
Both methods are practically the same

The input of it is a list of 3 np.arrays (train/valid/test) of integer indices of the data.
The train split is always mandatory but the validation and test splits are not (and can be left empty or None), and in any case there must not be duplicates and it should cover the whole data.

If external indices are used it will bypass any tain or valid size or proportion.

Example:

train_ind=np.array([1,2,3])
valid_ind=np.array([4,5,6])
test_ind=np.array(None)
```python
# object to make train/test/val dataloaders with external indices
data_splitter = DataSplitter(
    external_indexing=[train_ind, valid_ind, test_ind]
)
model.train(datamodule=datamodule)

#Or insert indices directly in train with datasplitter_kwargs
model.train(
    datasplitter_kwargs={
        "external_indexing": [train_ind, valid_ind, test_ind]
    },
)
```

### Save and load

We can also save and load this model object, as it follows the expected structure.

```python
model_dir = os.path.join(save_dir.name, "saved_model")

model.save(model_dir, save_anndata=True)
model = SCVI.load(model_dir)
```

## Writing methods to query the model

So we have a model that wraps a module that has been trained. How can we get information out of the module and present in cleanly to our users? Let's implement a simple example: getting the latent representation out of the VAE.

This method has the following structure:

1. Validate the user-supplied data
1. Create a data loader
1. Iterate over the data loader and feed into the VAE, getting the tensor of interest out of the VAE.

```python
@torch.inference_mode()
def get_latent_representation(
    self,
    adata: AnnData | None = None,
    indices: Sequence[int] | None = None,
    batch_size: int | None = None,
) -> np.ndarray:
    r"""Return the latent representation for each cell.

    Parameters
    ----------
    adata
        AnnData object with equivalent structure to initial AnnData. If `None`, defaults to the
        AnnData object used to initialize the model.
    indices
        Indices of cells in adata to use. If `None`, all cells are used.
    batch_size
        Minibatch size for data loading into model. Defaults to `scvi.settings.batch_size`.

    Returns
    -------
    latent_representation : np.ndarray
        Low-dimensional representation for each cell
    """
    if self.is_trained_ is False:
        raise RuntimeError("Please train the model first.")

    adata = self._validate_anndata(adata)
    dataloader = self._make_dataloader(adata=adata, indices=indices, batch_size=batch_size)
    latent = []
    for tensors in dataloader:
        inference_inputs = self.module._get_inference_input(tensors)
        outputs = self.module.inference(**inference_inputs)
        qz_m = outputs["qz_m"]

        latent += [qz_m.cpu()]
    return torch.cat(latent).numpy()
```

```{note}
Validating the anndata is critical to the user experience. If `None` is passed it just returns the anndata used to initialize the model, but if a different object is passed, it checks that this new object is equivalent in structure to the anndata passed to the model. We took great care in engineering this function so as to allow passing anndata objects with potentially missing categories (e.g., model was trained on batches `["A", "B", "C"]`, but the passed anndata only has `["B", "C"]`). These sorts of checks will ensure that your module will see data that it expects, and the user will get the results they expect without advanced data manipulations.
```

As a convention, we like to keep the module code as bare as possible and leave all posterior manipulation of module tensors to the model class methods. However, it would have been possible to write a `get_z` method in the module, and just have the model class that method.

## Mixing in pre-coded features

We have a number of Mixin classes that can add functionality to your model through inheritance. Here we demonstrate the [`VAEMixin`](https://www.scvi-tools.org/en/stable/api/reference/scvi.model.base.VAEMixin.html#scvi.model.base.VAEMixin) class.

Let's try to get the latent representation from the object we already created.

```python
try:
    model.get_latent_representation()
except AttributeError:
    print("This function does not exist")
```

This method becomes avaialble once the `VAEMixin` is inherited. Here's an overview of the mixin methods, which are coded generally enough that they should be broadly useful to those building VAEs.

```python
class VAEMixin:
    @torch.inference_mode()
    def get_elbo(
        self,
        adata: Optional[AnnData] = None,
        indices: Optional[Sequence[int]] = None,
        batch_size: Optional[int] = None,
    ) -> float:
        pass

    @torch.inference_mode()
    def get_marginal_ll(
        self,
        adata: Optional[AnnData] = None,
        indices: Optional[Sequence[int]] = None,
        n_mc_samples: int = 1000,
        batch_size: Optional[int] = None,
    ) -> float:
        pass

    @torch.inference_mode()
    def get_reconstruction_error(
        self,
        adata: Optional[AnnData] = None,
        indices: Optional[Sequence[int]] = None,
        batch_size: Optional[int] = None,
    ) -> Union[float, Dict[str, float]]:
        pass

    @torch.inference_mode()
    def get_latent_representation(
        self,
        adata: Optional[AnnData] = None,
        indices: Optional[Sequence[int]] = None,
        give_mean: bool = True,
        mc_samples: int = 5000,
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        pass
```

Let's now inherit the mixin into our SCVI class.

```python
class SCVI(VAEMixin, UnsupervisedTrainingMixin, BaseModelClass):
    """single-cell Variational Inference [Lopez18]_."""

    def __init__(
        self,
        adata: AnnData,
        n_latent: int = 10,
        **model_kwargs,
    ):
        super().__init__(adata)

        self.module = VAE(
            n_input=self.summary_stats["n_vars"],
            n_batch=self.summary_stats["n_batch"],
            n_latent=n_latent,
            **model_kwargs,
        )
        self._model_summary_string = (
            f"SCVI Model with the following params: \nn_latent: {n_latent}"
        )
        self.init_params_ = self._get_init_params(locals())

    @classmethod
    def setup_anndata(
        cls,
        adata: AnnData,
        batch_key: str | None = None,
        layer: str | None = None,
        **kwargs,
    ) -> AnnData | None:
        setup_method_args = cls._get_setup_method_args(**locals())
        anndata_fields = [
            LayerField(REGISTRY_KEYS.X_KEY, layer, is_count_data=True),
            CategoricalObsField(REGISTRY_KEYS.BATCH_KEY, batch_key),
            # Dummy fields required for VAE class.
            CategoricalObsField(REGISTRY_KEYS.LABELS_KEY, None),
            NumericalObsField(REGISTRY_KEYS.SIZE_FACTOR_KEY, None, required=False),
            CategoricalJointObsField(REGISTRY_KEYS.CAT_COVS_KEY, None),
            NumericalJointObsField(REGISTRY_KEYS.CONT_COVS_KEY, None),
        ]
        adata_manager = AnnDataManager(fields=anndata_fields, setup_method_args=setup_method_args)
        adata_manager.register_fields(adata, **kwargs)
        cls.register_manager(adata_manager)
```

```python
SCVI.setup_anndata(adata, batch_key="batch")
model = SCVI(adata)
model.train(10)
model.get_latent_representation()
```

## Summary

We learned the structure of the high-level model classes in scvi-tools, and learned how a simple version of `SCVI` is implemented.

Questions? Comments? Keep the discussion going on our [forum](https://discourse.scvi-tools.org/)
