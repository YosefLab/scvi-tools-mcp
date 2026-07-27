from __future__ import annotations

from datetime import datetime

project = "scVI-Tools MCP"
author = "Ori Kronfeld"
copyright = f"{datetime.now():%Y}, {author}."

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
html_title = "scVI-Tools MCP"

exclude_patterns = ["superpowers"]

html_extra_path = ["architecture/scvi-tools-mcp-block-diagram.html"]
