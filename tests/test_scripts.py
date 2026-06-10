from pathlib import Path

from scripts.convert_notebooks import convert_all, convert_notebook

FIXTURES = Path(__file__).parent / "fixtures"


def test_convert_notebook_produces_md(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    assert out.exists()
    content = out.read_text()
    assert "# scVI Tutorial" in content
    assert "import scvi" in content


def test_convert_notebook_strips_outputs(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    content = out.read_text()
    assert "Training..." not in content


def test_convert_notebook_has_code_fences(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out = tmp_path / "sample_notebook.md"
    convert_notebook(nb, out)
    content = out.read_text()
    assert "```python" in content


def test_convert_notebook_skips_checkpoints(tmp_path):
    nb = FIXTURES / "sample_notebook.ipynb"
    out_dir = tmp_path / "tutorials"
    out_dir.mkdir()
    checkpoint_dir = tmp_path / ".ipynb_checkpoints"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "sample-checkpoint.ipynb").write_text(nb.read_text())
    convert_all(tmp_path, out_dir)
    assert not (out_dir / "sample-checkpoint.md").exists()
