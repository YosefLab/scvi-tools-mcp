# tests/conftest.py
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_knowledge(tmp_path):
    """Copy fixture knowledge files into a temp dir and patch get_knowledge_dir.

    # IMPORTANT: All tool modules must call get_knowledge_dir() via the module,
    # not via a local import (e.g. use `from scvi_tools_mcp.tools import utils; utils.get_knowledge_dir()`
    # or import it at call time). Direct local-name imports bypass this patch.
    """
    k = tmp_path / "knowledge"
    shutil.copytree(FIXTURES / "knowledge", k)
    # Add minimal model files needed by tools
    models_dir = k / "models"
    models_dir.mkdir(exist_ok=True)
    (models_dir / "scvi.md").write_text(
        "# SCVI — API Reference\n\nscVI is a variational autoencoder for scRNA-seq batch integration.\n\n"
        "**Key parameters:** n_latent (int), gene_likelihood (str)\n\n"
        "## setup_anndata\n\n```python\nSCVI.setup_anndata(adata, batch_key='batch')\n```\n",
        encoding="utf-8",
    )
    for name in ["scanvi", "totalvi", "multivi", "peakvi"]:
        (models_dir / f"{name}.md").write_text(f"# {name.upper()}\n\nDoc for {name}.\n", encoding="utf-8")
    api_dir = k / "api"
    api_dir.mkdir(exist_ok=True)
    (api_dir / "scvi.md").write_text("# SCVI API\n\nSCVI.setup_anndata(adata, batch_key=None)\n", encoding="utf-8")
    tutorials_dir = k / "tutorials"
    tutorials_dir.mkdir(exist_ok=True)
    (tutorials_dir / "scrna").mkdir(exist_ok=True)
    (tutorials_dir / "scrna" / "harmonization.md").write_text(
        "# Harmonization Tutorial\n\nThis tutorial shows batch integration with scVI.\n\n```python\nimport scvi\n```\n",
        encoding="utf-8",
    )
    user_guide_dir = k / "user_guide"
    user_guide_dir.mkdir(exist_ok=True)
    (user_guide_dir / "saving_and_loading_models.md").write_text(
        "# Saving Models\n\nUse model.save().\n", encoding="utf-8"
    )
    faq_dir = k / "faq"
    faq_dir.mkdir(exist_ok=True)
    (faq_dir / "github_issues.md").write_text(
        "# FAQ\n\n## Training\nQ: Loss not decreasing?\nA: Check learning rate.\n", encoding="utf-8"
    )
    (faq_dir / "discourse_threads.md").write_text("# Discourse\n\n## How to use SCANVI?\nPosts: 10\n", encoding="utf-8")

    with patch("scvi_tools_mcp.tools.utils.get_knowledge_dir", return_value=k):
        yield k
