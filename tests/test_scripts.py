from pathlib import Path

from scripts._apidoc_utils import merge_with_user_guide, render_doc, resolve_dotted
from scripts.convert_notebooks import convert_all, convert_notebook

FIXTURES = Path(__file__).parent / "fixtures"


class _Dummy:
    """dummy class for testing"""

    def __init__(self, x: int = 1):
        pass


class _DummyTwo:
    """another dummy class"""

    def __init__(self, y: str = "a"):
        pass


def _dummy_func(a: int, b: str = "x") -> None:
    """dummy function docstring"""


def test_resolve_dotted_imports_object():
    cls = resolve_dotted("pathlib.Path")
    assert cls is Path


def test_resolve_dotted_returns_none_for_missing():
    assert resolve_dotted("nonexistent.module.Thing") is None
    assert resolve_dotted("badformat") is None


def test_render_doc_single_object():
    md = render_doc("DUMMY", [_Dummy])
    assert "# DUMMY — API Reference" in md
    assert "**Class:**" in md
    assert "dummy class for testing" in md
    assert "Signature:" in md


def test_render_doc_combines_multiple_objects():
    md = render_doc("STEREOSCOPE", [_Dummy, _DummyTwo])
    assert "# STEREOSCOPE — API Reference" in md
    assert "_Dummy" in md
    assert "_DummyTwo" in md
    assert "dummy class for testing" in md
    assert "another dummy class" in md


def test_render_doc_includes_extra_methods():
    class WithTrain:
        """has a train method"""

        def __init__(self):
            pass

        def train(self, max_epochs: int = 10):
            """train docstring"""

    md = render_doc("WITHTRAIN", [WithTrain], extra_methods=("train",))
    assert "train" in md
    assert "train docstring" in md


def test_merge_with_user_guide_appends_when_present(tmp_path):
    docs_dir = tmp_path / "docs"
    (docs_dir / "models").mkdir(parents=True)
    (docs_dir / "models" / "resolvi.md").write_text("Narrative guide for ResolVI.", encoding="utf-8")

    merged = merge_with_user_guide("resolvi", "# API content", docs_dir)

    assert "# API content" in merged
    assert "## User Guide" in merged
    assert "Narrative guide for ResolVI." in merged


def test_extract_scviva_api_docs_model_classes_cover_all_eight_models():
    from scripts.extract_scviva_api_docs import MODEL_CLASSES

    assert set(MODEL_CLASSES) == {
        "resolvi",
        "destvi",
        "scviva",
        "gimvi",
        "diagvi",
        "stereoscope",
        "tangram",
        "harreman",
    }
    assert MODEL_CLASSES["stereoscope"] == [
        "scviva.external.stereoscope.RNAStereoscope",
        "scviva.external.stereoscope.SpatialStereoscope",
    ]
    assert MODEL_CLASSES["resolvi"] == ["scviva.model.ResolVI"]
    assert MODEL_CLASSES["harreman"] == ["scviva.tools.harreman.HarremanAnalysis"]


def test_extract_scib_metrics_api_docs_covers_twelve_metrics():
    from scripts.extract_scib_metrics_api_docs import BENCHMARK_CLASSES, METRIC_FUNCTIONS

    assert len(METRIC_FUNCTIONS) == 12
    assert "isolated_labels" in METRIC_FUNCTIONS
    assert "ilisi_knn" in METRIC_FUNCTIONS
    assert "kbet_per_label" in METRIC_FUNCTIONS
    assert set(BENCHMARK_CLASSES) == {"benchmarker", "bioconservation", "batchcorrection"}
    assert BENCHMARK_CLASSES["benchmarker"] == ["scib_metrics.benchmark.Benchmarker"]


def test_render_doc_renders_plain_function():
    md = render_doc("ISOLATED_LABELS", [_dummy_func])
    assert "# ISOLATED_LABELS — API Reference" in md
    assert "dummy function docstring" in md
    assert "Signature:" in md


def test_merge_with_user_guide_passthrough_when_missing(tmp_path):
    assert merge_with_user_guide("resolvi", "# API content", None) == "# API content"

    docs_dir = tmp_path / "docs"
    (docs_dir / "models").mkdir(parents=True)
    assert merge_with_user_guide("resolvi", "# API content", docs_dir) == "# API content"


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
