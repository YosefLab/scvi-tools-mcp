from __future__ import annotations

from datetime import datetime

project = "scvi-tools-mcp"
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
html_title = "scvi-tools MCP"

exclude_patterns = ["superpowers"]
