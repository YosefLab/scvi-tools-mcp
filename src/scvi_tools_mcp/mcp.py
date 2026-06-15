from fastmcp import FastMCP

mcp = FastMCP(
    name="scvi-tools-mcp",
    instructions=(
        "You are an expert on scvi-tools, a Python package for deep probabilistic "
        "analysis of single-cell omics data. Use these tools to help users choose "
        "models, prepare data, find tutorials, understand the API, find pretrained "
        "Hugging Face Hub models, and troubleshoot. "
        "Always start with recommend_model or search_knowledge if the user's need is unclear."
    ),
)

# Tool modules register their tools with @mcp.tool() decorator on import
from scvi_tools_mcp.tools import (  # noqa: E402, F401
    _api_reference,
    _data_prep,
    _hub,
    _model_guidance,
    _troubleshooting,
    _tutorials,
    _workflows,
)
