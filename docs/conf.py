project = "scvi-tools-mcp"
author = "YosefLab"
copyright = "2024, YosefLab"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "furo"
html_title = "scvi-tools MCP"

exclude_patterns = ["superpowers"]
