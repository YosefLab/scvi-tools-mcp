# Constructing a probabilistic module

In our previous tutorial, we went over the principle of a dataloader, and how scvi-tools interacts natively with AnnData. In this tutorial, we will go in further details towards the creation of a novel statistical method for single-cell omics data. The gist of a method is essentially summarized in two components:

1. **A generative model**, that aims at efficiently mimicking the underlying data distribution. Ideally, a generative model fits the data well, while making use of informative and interpretable latent variables that summarize certain aspects of the data. For example, scVI aims at summarizing the biological signal of the gene expression $x_{n}$ of a cell $n$ into a latent variable $z_n$ that represents cell-specific transcriptomic states.
1. An **inference method**, that aims at "guessing" the latent variables (and/or the parameters of the model), based on the data.

scvi-tools proposes two different backends for the developement of such probabilistic programs, both being built on top of PyTorch Lightning:

1. A **vanilla PyTorch** interface, on which most of the models are implemented. We expect this interface to be useful when the objective function (likelihood or evidence lower bound) may be easily written in PyTorch, or when ad-hoc stochastic variational inference procedures are needed.
1. A **Pyro** interface, which we expect to be useful when working with large hierarchical Bayesian models or when the inference used relies on a clear algorithmic recipe (ADVI, VAEs).

In this tutorial, we shall present how to create a new Module to reimplement a simple version of scVI from scratch. We will proceed as follow:

1. Brief introduction to the scVI model and its inference recipe
1. Drafting the inner components (neural nets and likelihood functions)
1. Crafting the Module in vanilla PyTorch
1. Crafting the Module in Pyro

## A simpler scVI model and its inference recipe

We work here with a simpler version of scVI to highlight how easy it is to craft new modules inside of scvi-tools.

### The generative model

Let

$$z_n \sim \textrm{Normal}(0, I),$$

be a latent random vector representing the transcriptomic state of cell $n$, tyipically low-dimensional (e.g., dimension 10). Let $l_{n}$ be the number of captured unique molecule identifier in cell $n$, that we assume to be an observed random variable. The gene expression of a gene $g$ in a cell $n$, $x_{ng}$ is obtained as:

$$x_{ng} \sim \textrm{NegativeBinomial}\left(l_n f^g(z_n), \theta_g\right),$$

where $f$ is a function mapping the latent space to the simplex of the gene expression space. $\theta_g$ is a positive parameter to be learned: the dispersion parameter of the negative binomial distribution.

### The inference mechanism

The scvi-tools codebase is expected to work with many different inference mecanisms (e.g., AEVB, VI, EM, MAP, MLE, etc.). In this precise tutorial, we focus on auto-encoding variational Bayes. AEVB is part of the family of variational inference recipes, in which one seeks to maximize a lower-bound of the likelihood (when the likelihood itself is intractable).

In our case, we aim at finding the parameters $\Theta = \{\theta, f\}$ that maximize the log-likelihood of the data $\log p_\Theta(x)$ (we identify the function $f$ to its parameters). As the likelihood is intractable, we optimize instead a lower-bound:

$$ \log p_\Theta(x) \geq \mathbb{E}_{q(z \mid x)}\log p_\Theta(x \mid z) - \textrm{KL}\left(q(z \mid x) \mid p(z)\right), $$

in which the distribution $q(z \mid x)$ is named the variational distribution.

There are two important things to mention. First, we must specify a parameterization for the variational distribution. In AEVB, $q(z \mid x)$ is specified via a pair of neural networks:

$$q(z \mid x) \sim \textrm{Normal}\left(g_\mu(x), \textrm{diag}(g^2_\sigma(x))\right).$$

Second, optimizing the lower bound cannot be done in closed-form. Instead, gradients are approximated by sampling from the variational distribution using the reparameterization trick.

```{note}
A great advantage of the Pyro API is that only the specification of the parameterization of the inference networks is required (this is called the guide), while our vanilla pytorch API requires the implementation of the reparameterization trick, as well as the evidence lower bound.
```

Great, now let's start coding!

```{note}
Running the following cell will install tutorial dependencies on Google Colab only. It will have no effect on environments other than Google Colab.
```

```python
!pip install --quiet scvi-colab
from scvi_colab import install

install()
```

```python
import tempfile
from typing import Literal

import pyro
import pyro.distributions as dist
import scvi
import torch
from scvi import REGISTRY_KEYS
from scvi.module.base import (
    BaseModuleClass,
    LossOutput,
    PyroBaseModuleClass,
    auto_move_data,
)
from torch.distributions import NegativeBinomial, Normal
from torch.distributions import kl_divergence as kl
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

## Drafting the inner components (neural nets)

We aim here at creating all the elementary stochastic computation units needed to describe the generative model, as well as performing inference. We will then craft those units together into a Module (either in vanilla Pytorch or in Pyro).

Our model includes one neural network, that we will refer to as the decoder. Our inference recipe includes two neural networks (the encoders). Because each neural network will have a specific output non-linearity to handle the different cases, we will create a generic class. The class inherits from the torch.nn.Module class so that it's parameters are automatically optimized during inference.

```python
class MyNeuralNet(torch.nn.Module):
    def __init__(
        self,
        n_input: int,
        n_output: int,
        link_var: Literal["exp", "none", "softmax"],
    ):
        """Encodes data of ``n_input`` dimensions into a space of ``n_output`` dimensions.

        Uses a one layer fully-connected neural network with 128 hidden nodes.

        Parameters
        ----------
        n_input
            The dimensionality of the input.
        n_output
            The dimensionality of the output.
        link_var
            The final non-linearity.
        """
        super().__init__()
        self.neural_net = torch.nn.Sequential(
            torch.nn.Linear(n_input, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, n_output),
        )
        self.transformation = None
        if link_var == "softmax":
            self.transformation = torch.nn.Softmax(dim=-1)
        elif link_var == "exp":
            self.transformation = torch.exp

    def forward(self, x: torch.Tensor):
        output = self.neural_net(x)
        if self.transformation:
            output = self.transformation(output)
        return output
```

We can instantiate and immediately test out this elementary unit, that may be used for any of the three neural networks needed for our implementation.

```python
my_neural_net = MyNeuralNet(100, 10, "softmax")
my_neural_net
```

```python
# observe that the output sums to 1 and are positive!
x = torch.randn((2, 100))
my_neural_net(x)
```

## Crafting the Module in vanilla PyTorch

All of our vanilla Pytorch modules inherit from the `BaseModuleClass`, and must implement the following methods:

1. `_get_generative_input()`: selecting the registered tensors from the AnnData, as well as the latent variables (from inference) used in the model
1. `generative()`: mapping the generative inputs to the parameters of the data likelihood function
1. `_get_inference_input()`: selecting the registered tensors from the AnnData used in the inference
1. `inference()`: mapping the inference inputs to the parameters of the variational distribution
1. `loss()`: the log-likelihood or its lower bound
1. `sample()` \[Optional\]: this signature may be used to sample new datapoints (prior predictive or posterior predictive), outside of this tutorial's topic

The `BaseModuleClass` has already implemented a `.forward()` method that will be used by the `Trainer`. The schematic of the method is as follows:

1. Get the tensors for inference, and feed them through the `inference` method to recover the latent variables
1. Get the tensors used for describing the generative model, and feed the through the `generative` method to recover the parameters of the data likelihood
1. Evaluate the data fit in the `loss` method.

The `Trainer` then calculates the gradients of the loss with respect to the model and the inference parameters to update them.

You'll notice that the return type of the `loss` method is [`LossOutput`](https://docs.scvi-tools.org/en/stable/api/reference/scvi.module.base.LossOutput.html#scvi.module.base.LossOutput), which is a dataclass that contains the loss and the tensors that are used to calculate
the loss. While we define keys that are generally used for AEVB (the reconstruction loss and KL
divergence), additional loss terms can be added with the `extra_metrics` key.

```python
class MyModule(BaseModuleClass):
    """Skeleton Variational auto-encoder model.

    Here we implement a basic version of scVI's underlying VAE [Lopez18]_.
    This implementation is for instructional purposes only.

    Parameters
    ----------
    n_input
        Number of input genes.
    n_latent
        Dimensionality of the latent space.
    """

    def __init__(
        self,
        n_input: int,
        n_latent: int = 10,
    ):
        super().__init__()
        # in the init, we create the parameters of our elementary stochastic computation unit.

        # First, we setup the parameters of the generative model
        self.decoder = MyNeuralNet(n_latent, n_input, "softmax")
        self.log_theta = torch.nn.Parameter(torch.randn(n_input))

        # Second, we setup the parameters of the variational distribution
        self.mean_encoder = MyNeuralNet(n_input, n_latent, "none")
        self.var_encoder = MyNeuralNet(n_input, n_latent, "exp")

    def _get_inference_input(self, tensors: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """Parse the dictionary to get appropriate args"""
        # let us fetch the raw counts, and add them to the dictionary
        return {"x": tensors[REGISTRY_KEYS.X_KEY]}

    @auto_move_data
    def inference(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        High level inference method.

        Runs the inference (encoder) model.
        """
        # log the input to the variational distribution for numerical stability
        x_ = torch.log1p(x)
        # get variational parameters via the encoder networks
        qz_m = self.mean_encoder(x_)
        qz_v = self.var_encoder(x_)
        # get one sample to feed to the generative model
        # under the hood here is the Reparametrization trick (Rsample)
        z = Normal(qz_m, torch.sqrt(qz_v)).rsample()

        return {"qz_m": qz_m, "qz_v": qz_v, "z": z}

    def _get_generative_input(
        self, tensors: dict[str, torch.Tensor], inference_outputs: dict[str, torch.Tensor]
    ) -> dict[str, torch.Tensor]:
        return {
            "z": inference_outputs["z"],
            "library": torch.sum(tensors[REGISTRY_KEYS.X_KEY], dim=1, keepdim=True),
        }

    @auto_move_data
    def generative(self, z: torch.Tensor, library: torch.Tensor) -> dict[str, torch.Tensor]:
        """Runs the generative model."""
        # get the "normalized" mean of the negative binomial
        px_scale = self.decoder(z)
        # get the mean of the negative binomial
        px_rate = library * px_scale
        # get the dispersion parameter
        theta = torch.exp(self.log_theta)

        return {
            "px_scale": px_scale,
            "theta": theta,
            "px_rate": px_rate,
        }

    def loss(
        self,
        tensors: dict[str, torch.Tensor],
        inference_outputs: dict[str, torch.Tensor],
        generative_outputs: dict[str, torch.Tensor],
    ) -> LossOutput:
        # here, we would like to form the ELBO. There are two terms:
        #   1. one that pertains to the likelihood of the data
        #   2. one that pertains to the variational distribution
        # so we extract all the required information
        x = tensors[REGISTRY_KEYS.X_KEY]
        px_rate = generative_outputs["px_rate"]
        theta = generative_outputs["theta"]
        qz_m = inference_outputs["qz_m"]
        qz_v = inference_outputs["qz_v"]

        # term 1
        # the pytorch NB distribution uses a different parameterization
        # so we must apply a quick transformation (included in scvi-tools, but here we use the
        # pytorch code)
        nb_logits = (px_rate + 1e-4).log() - (theta + 1e-4).log()
        log_lik = NegativeBinomial(total_count=theta, logits=nb_logits).log_prob(x).sum(dim=-1)

        # term 2
        prior_dist = Normal(torch.zeros_like(qz_m), torch.ones_like(qz_v))
        var_post_dist = Normal(qz_m, torch.sqrt(qz_v))
        kl_divergence = kl(var_post_dist, prior_dist).sum(dim=1)

        elbo = log_lik - kl_divergence
        loss = torch.mean(-elbo)
        return LossOutput(
            loss=loss,
            reconstruction_loss=-log_lik,
            kl_local=kl_divergence,
            kl_global=0.0,
        )
```

```python
# try creating a module and see the description:
MyModule(100, 10)
```

## Crafting the Module in Pyro

The Pyro Module has less code, as it is not needed to write the evidence lower bound. Still, one must implement the following to inherit from our `PyroModuleClass`:

1. A static method `_get_fn_args_from_batch()`: a function that extracts the necessary tensors to be sent to the generative model and the inference (called a guide in Pyro). In the Pyro case, both functions must have the same signature.
1. A `model()` method: that simulates the data generating process using the Pyro syntax.
1. A `guide()` method: that explicitly tells Pyro how to perform inference. Pyro has some automatic guides in the context of ADVI, but for AEVB we will write our own guide with neural networks.

```python
class MyPyroModule(PyroBaseModuleClass):
    def __init__(self, n_input, n_latent):
        super().__init__()
        self.n_latent = n_latent
        self.n_input = n_input
        # in the init, we create the parameters of our elementary stochastic computation unit.

        # First, we setup the parameters of the generative model
        self.decoder = MyNeuralNet(n_latent, n_input, "softmax")
        self.log_theta = torch.nn.Parameter(torch.randn(n_input))

        # Second, we setup the parameters of the variational distribution
        self.mean_encoder = MyNeuralNet(n_input, n_latent, "none")
        self.var_encoder = MyNeuralNet(n_input, n_latent, "exp")

    @staticmethod
    def _get_fn_args_from_batch(tensor_dict):
        x = tensor_dict[REGISTRY_KEYS.X_KEY]
        library = torch.sum(x, dim=1, keepdim=True)
        return (x, library), {}

    def model(self, x, library):
        # register PyTorch module `decoder` with Pyro
        pyro.module("scvi", self)
        with pyro.plate("data", x.shape[0]):
            # setup hyperparameters for prior p(z)
            z_loc = x.new_zeros(torch.Size((x.shape[0], self.n_latent)))
            z_scale = x.new_ones(torch.Size((x.shape[0], self.n_latent)))
            # sample from prior (value will be sampled by guide when computing the ELBO)
            z = pyro.sample("latent", dist.Normal(z_loc, z_scale).to_event(1))
            # get the "normalized" mean of the negative binomial
            px_scale = self.decoder(z)
            # get the mean of the negative binomial
            px_rate = library * px_scale
            # get the dispersion parameter
            theta = torch.exp(self.log_theta)
            # build count distribution
            nb_logits = (px_rate + 1e-4).log() - (theta + 1e-4).log()
            x_dist = dist.NegativeBinomial(total_count=theta, logits=nb_logits)
            # score against actual counts
            pyro.sample("obs", x_dist.to_event(1), obs=x)

    def guide(self, x, log_library):
        # define the guide (i.e. variational distribution) q(z|x)
        pyro.module("scvi", self)
        with pyro.plate("data", x.shape[0]):
            # use the encoder to get the parameters used to define q(z|x)
            x_ = torch.log(1 + x)
            qz_m = self.mean_encoder(x_)
            qz_v = self.var_encoder(x_)
            # sample the latent code z
            pyro.sample("latent", dist.Normal(qz_m, torch.sqrt(qz_v)).to_event(1))
```

```python
# try creating an object
MyPyroModule(10, 100)
```

Let's sum up what we learned:

1. How does the Module work in scvi-tools
1. How is Pyro integrated into scvi-tools

In the next tutorial, you will learn how to train these modules, by wrapping them into a Model!
