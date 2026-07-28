# API reference

This reference documents the Python entry point and the tools exposed by the
scVI-Tools MCP server. MCP clients discover these tools automatically.

## Server

```{eval-rst}
.. automodule:: scvi_tools_mcp.main
   :members: run_app
```

## Model guidance

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._model_guidance
   :members: recommend_model, get_model_overview, get_model_parameters
```

## Data preparation

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._data_prep
   :members: get_setup_anndata_guide, validate_data_requirements
```

## Tutorials

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._tutorials
   :members: list_tutorials, get_tutorial, search_tutorials
```

## scvi-tools API lookup

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._api_reference
   :members: get_api_reference, search_api
```

## Hugging Face Hub

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._hub
   :members: list_hub_models, get_hub_model, suggest_hub_models
```

## scviva-tools

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._scviva
   :members: list_scviva_models, get_scviva_model, list_scviva_tutorials, get_scviva_tutorial
```

## scib-metrics

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._scib_metrics
   :members: list_scib_metrics, get_scib_metric, list_scib_metrics_tutorials, get_scib_metrics_tutorial
```

## Workflows

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._workflows
   :members: get_workflow_template, get_downstream_guide
```

## Troubleshooting

```{eval-rst}
.. automodule:: scvi_tools_mcp.tools._troubleshooting
   :members: get_faq, search_knowledge
```
