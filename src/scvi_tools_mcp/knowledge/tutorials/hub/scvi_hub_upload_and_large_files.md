# Using scvi-hub to upload pretrained scvi-tools models

In this tutorial, we will see how to use scvi-tools to upload pretrained models onto Hugging Face. We will also see how to handle large training datasets.

If you have not already, make sure to refer to our scvi_hub_into_and_download tutorial, which is a pre-requisite to this one. It introduces Hugging Face (HF) and the scvi-hub, and describes how to use them for downloading pre-trained models from the HF Model Hub.

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

import anndata
import scanpy as sc
import scvi
import seaborn as sns
import torch
from scvi.hub import HubMetadata, HubModel, HubModelCardHelper
```

```python
scvi.settings.seed = 0
print("Last run with scvi-tools version:", scvi.__version__)
```

```{note}
You can modify `save_dir` below to change where the data files for this tutorial are saved.
```

```python
sc.set_figure_params(figsize=(6, 6), frameon=False)
sns.set_theme()
torch.set_float32_matmul_precision("high")
save_dir = tempfile.TemporaryDirectory()

%config InlineBackend.print_figure_kwargs={"facecolor": "w"}
%config InlineBackend.figure_format="retina"
```

## Imports

Let's start by adding the Python imports we need.

## Pretrain a demo model

Let's pretrain a model on some synthetic data which we'll use to upload to the scvi-hub later.

```python
model_path = os.path.join(save_dir.name, "scvi_hub_upload")

adata = scvi.data.synthetic_iid()
scvi.model.SCVI.setup_anndata(adata)
model = scvi.model.SCVI(adata)
model.train(1)
model.save(model_path, save_anndata=True, overwrite=True)
```

## Model Card and Metadata

To upload pretrained models, you'll need to create an instance of the `HubModel` class and then simply call its `push_to_huggingface_hub` method.

As you can see from the API reference, the `HubModel` init function requires metadata and a Model Card. There are a few ways you can provide these:

- The metadata can be either an instance of the `HubMetadata` class that contains the required metadata for this model, or a path to a JSON file on disk where this metadata can be read from.
- The Model Card can be  an instance of the `HubModelCardHelper` class created for this model, or an instance of the HF [Model Card](https://huggingface.co/docs/huggingface_hub/package_reference/cards#huggingface_hub.ModelCard) object, or a path to a Markdown file on disk where the model card can be read from.
  - You can also use the `HubModelCardHelper` class to create a Model Card from the scvi-tools template, then save it on disk and change it as you wish before passing its path into the `HubModel` class.

Here we'll see how to create the HubMetadata and a Model Card from the data on disk.

```python
hm = HubMetadata.from_dir(model_path, anndata_version=anndata.__version__)

hmch = HubModelCardHelper.from_dir(
    model_path,
    license_info="cc-by-4.0",
    anndata_version=anndata.__version__,
    data_modalities=["rna", "protein"],
    data_is_annotated=False,
    description="This is a demo model used during upload demo.",
    references="None.",
)
```

```python
print(hmch.model_card.content)
```

Note: Suppose I wanted to change the content a little bit. To do that, I'd save the card to disk, change it manually as I wish, and then pass its path to `HubModel`.

```python
hmch.model_card.save(
    "local/my_model_card.md"
)  # then change the markdown file on disk...
```

## Create a `HubModel` and upload it

Now we can create the HubModel and push it to the HF Model Hub:

```python
hmo = HubModel(model_path, metadata=hm, model_card=hmch)
hmo
```

To upload, you need to call:

```python
hmo.push_to_huggingface_hub(
    repo_name=repo_name, repo_token=repo_token, repo_create=True
)
```

We won't do it here but will explain the parameters you need to pass:

- `repo_name`: The name/id of your repo.
- `repo_token`: The token you need to authenticate yourself to the HF Model Hub. *It must have "write" permissions.* You can get this from your HF account page. Read [this](https://huggingface.co/docs/hub/security-tokens) article to find out how.
  - The token can either be passed in as plain text or as the full path to a file on disk where the token is stored.
- `repo_create`: Whether you want scvi-tools to create the repo for you. If you want to create the repo yourself on the HF Model Hub or if it already exists, you can set this to False.

## Large training data

So far, all models we've seen have contained the dataset in the HF Hub Model object. However, in some cases, this is not possible — or desirable — if the training data is too large.
For all files large than 5GB, you are prompted to store your training data on a separate storage and provide its URL to the HubModel. This will alert scvi-tools as to where to pull the data from when loading it (or the model) into memory.

There are four possible scenarios. Here we're assuming that the minified data is \<5GB which is very likely to not be the case.

1. Your training data is **\<5GB** and it is **not minified**.\
   👉 In this case, both your model and data will be uploaded to the same HF Model.
1. Your training data is **\<5GB** and it is **minified**.\
   👉 In this case, both your model and minified data will be uploaded to the same HF Model. Optionally, you can provide a link to your full (i.e., non-minified) training data.
1. Your training data is **>=5GB** and it is **not minified**.\
   👉 In this case, only your model will be uploaded to the HF Model. If you want to use your training data, then it is required to provide a link to it (this must be in the required metadata file, and can be present in the model card as well). When needed, scvi-tools will automatically download your training data from the link you registered.
1. Your training data is **>=5GB** and it is **minified**.\
   👉 In this case, both your model and minified data will be uploaded to the same HF Model. Optionally, you can provide a link to your full (i.e., non-minified) training data.

It is highly recommended to try to minify your data if possible. Please refer to our Minification tutorial for how to do that.

```{note}
It is always possible to use another dataset than your training data. You can set `model.adata` prior to saving. However, the convention with scvi-hub is to provide access to the training data (full or minified form), so that users can reproduce the results of the model and perform their own analyses on the same data.
```

## Model evaluation

We recommend that you include some evaluation results in your Model Card. One way to do this is by using our scvi-criticism Python package. It provides a simple API to evaluate the goodness of fit of your model and generate various visualizations. Read more about it in the [scvi-criticism documentation](https://scvi-criticism.readthedocs.io/).
