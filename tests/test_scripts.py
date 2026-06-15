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


def test_normalize_huggingface_model_parses_scvi_tags():
    from scripts.scrape_huggingface_hub import normalize_model

    raw = {
        "id": "scvi-tools/heart-cell-atlas-scvi",
        "createdAt": "2024-12-06T09:14:33.000Z",
        "lastModified": "2026-03-01T10:58:11.000Z",
        "downloads": 4,
        "likes": 1,
        "tags": [
            "scvi-tools",
            "model_cls_name:SCVI",
            "scvi_version:1.4.2",
            "anndata_version:0.12.7",
            "modality:rna",
            "tissue:heart",
            "annotated:True",
            "license:cc-by-4.0",
        ],
        "siblings": [
            {"rfilename": "README.md"},
            {"rfilename": "_scvi_required_metadata.json"},
            {"rfilename": "adata.h5ad"},
            {"rfilename": "model.pt"},
        ],
    }

    model = normalize_model(raw)

    assert model["model_id"] == "scvi-tools/heart-cell-atlas-scvi"
    assert model["url"] == "https://huggingface.co/scvi-tools/heart-cell-atlas-scvi"
    assert model["model_class"] == "SCVI"
    assert model["modalities"] == ["rna"]
    assert model["tissues"] == ["heart"]
    assert model["annotated"] is True
    assert model["scvi_version"] == "1.4.2"
    assert model["anndata_version"] == "0.12.7"
    assert model["license"] == "cc-by-4.0"
    assert model["files"] == ["README.md", "_scvi_required_metadata.json", "adata.h5ad", "model.pt"]


def test_build_huggingface_summary_counts_models():
    from scripts.scrape_huggingface_hub import build_snapshot, build_summary

    raw_models = [
        {
            "id": "scvi-tools/heart-cell-atlas-scvi",
            "lastModified": "2026-03-01T10:58:11.000Z",
            "tags": ["model_cls_name:SCVI", "modality:rna", "tissue:heart", "annotated:True"],
            "siblings": [{"rfilename": "README.md"}],
        },
        {
            "id": "scvi-tools/haniffa_covid_pbmc_totalvi",
            "lastModified": "2026-03-01T10:45:40.000Z",
            "tags": [
                "model_cls_name:TOTALVI",
                "modality:rna",
                "modality:protein",
                "tissue:thymus",
                "annotated:True",
            ],
            "siblings": [{"rfilename": "README.md"}],
        },
    ]

    snapshot = build_snapshot(raw_models, fetched_at="2026-06-15T00:00:00Z")
    summary = build_summary(snapshot)

    assert "Fetched 2 public model repos" in summary
    assert "- SCVI: 1" in summary
    assert "- TOTALVI: 1" in summary
    assert "- rna: 2" in summary
    assert "- protein: 1" in summary
