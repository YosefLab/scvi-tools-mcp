from __future__ import annotations

from datetime import datetime

from scverse_doc.config import DEFAULTS
from scverse_doc.registry import intersphinx

project = "scvi-tools MCP"
author = "Ori Kronfeld"
copyright = f"{datetime.now():%Y}, {author}."
source_repository = "https://github.com/YosefLab/scvi-tools-mcp"

# scverse-doc sets up the shared theme, sidebar layout and extension stack
# (MyST-NB, autodoc, autosummary, intersphinx, napoleon, copybutton, sphinx-design, opengraph).
extensions = ["scverse_doc"]

# intersphinx() is scverse-doc's registry of the scverse packages and their common dependencies.
intersphinx_mapping = intersphinx()

exclude_patterns = [*DEFAULTS.exclude_patterns, "superpowers"]

html_extra_path = ["architecture/scvi-tools-mcp-block-diagram.html"]

# scverse-doc turns on nitpicky mode; the tools' result models live in private modules
# and are not part of the documented API.
nitpick_ignore_regex = [("py:class", r"scvi_tools_mcp\.tools\._\w+\.\w+")]

html_logo = "_static/logo.png"
# pydata-sphinx-theme swaps in the dark-mode logo (light text) when the dark colour mode is active.
html_theme_options = {"logo": {"image_light": "_static/logo.png", "image_dark": "_static/logo-dark.png"}}
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
