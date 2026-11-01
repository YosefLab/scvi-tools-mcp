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
    assert "**Function:**" in md
    assert "**Class:**" not in md
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


def _snapshot_section(title, item_id, last, reply="answer"):
    return (
        f"## {title}\n"
        f"**Topic:** {item_id} | **Last activity:** {last}\n"
        f"**Posts:** 2 | **Views:** 10\n\n"
        f"**Question**: q\n\n**Reply (@someone)**: {reply}\n\n"
    )


def test_snapshot_merge_keeps_entries_not_refetched():
    import datetime as dt

    from scripts.scrape_external import merge_entries, parse_snapshot

    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    existing = parse_snapshot(
        "# header\n\n"
        + _snapshot_section("Correct way to run SOLO", 3949, "2026-04-23T09:29:07Z", "run hvg and run SOLO")
        + _snapshot_section("Other", 4000, "2026-10-01T00:00:00Z")
    )
    fetched = parse_snapshot(_snapshot_section("Other", 4000, "2026-10-20T00:00:00Z", "updated"))

    merged = merge_entries(existing, fetched, now)

    assert [e.item_id for e in merged] == [4000, 3949]
    assert "updated" in merged[0].body
    assert "run hvg and run SOLO" in merged[1].body


def test_snapshot_merge_prunes_only_entries_older_than_retention():
    import datetime as dt

    from scripts.scrape_external import merge_entries, parse_snapshot

    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    existing = parse_snapshot(
        _snapshot_section("Old", 1, "2022-01-01T00:00:00Z")
        + _snapshot_section("Recent", 2, "2024-01-01T00:00:00Z")
        + "## Legacy without metadata\n**Posts:** 1 | **Views:** 5\n\n**Question**: q\n\n"
    )

    merged = merge_entries(existing, [], now)

    assert [e.title for e in merged] == ["Recent", "Legacy without metadata"]


def test_snapshot_merge_upgrades_legacy_section_by_title_and_round_trips():
    import datetime as dt

    from scripts.scrape_external import merge_entries, parse_snapshot, render_snapshot

    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    existing = parse_snapshot("## Same title\n**Posts:** 1 | **Views:** 5\n\n**Question**: old\n\n")
    fetched = parse_snapshot(_snapshot_section("Same title", 7, "2026-05-01T00:00:00Z", "new"))

    merged = merge_entries(existing, fetched, now)

    assert len(merged) == 1 and merged[0].item_id == 7
    reparsed = parse_snapshot(render_snapshot("T", "entries", merged))
    assert [(e.item_id, e.title) for e in reparsed] == [(7, "Same title")]


def test_build_github_entry_marks_merged_pr_and_skips_bot_comments():
    from scripts.scrape_external import build_github_entry, parse_snapshot

    item = {
        "number": 3011,
        "title": "Fix SOLO doublet scores",
        "state": "closed",
        "pull_request": {"merged_at": "2026-05-02T00:00:00Z"},
        "user": {"login": "dev", "type": "User"},
        "labels": [{"name": "bug"}],
        "created_at": "2026-05-01T00:00:00Z",
        "updated_at": "2026-05-03T00:00:00Z",
        "html_url": "https://github.com/scverse/scvi-tools/pull/3011",
        "body": "Fixes the scores.",
    }
    comments = [
        {"user": {"login": "codecov[bot]", "type": "Bot"}, "body": "coverage report"},
        {"user": {"login": "reviewer", "type": "User"}, "body": "LGTM"},
    ]

    entry = build_github_entry(item, comments)
    rendered = entry.render()

    assert entry.title == "#3011: Fix SOLO doublet scores"
    assert "**PR:** #3011" in rendered and "**State:** merged" in rendered
    assert "LGTM" in rendered and "coverage report" not in rendered
    assert parse_snapshot(rendered)[0].item_id == 3011


def test_build_discussion_entry_marks_accepted_answer_and_replies():
    from scripts.scrape_external import build_discussion_entry, parse_snapshot

    node = {
        "number": 12,
        "title": "How to pick n_latent?",
        "url": "https://github.com/scverse/scvi-tools/discussions/12",
        "body": "Question body",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-02-01T00:00:00Z",
        "author": {"login": "asker"},
        "category": {"name": "Q&A"},
        "answer": {"id": "C1"},
        "comments": {
            "nodes": [
                {
                    "id": "C1",
                    "body": "Use 10-30.",
                    "author": {"login": "maintainer"},
                    "replies": {"nodes": [{"body": "Thanks!", "author": {"login": "asker"}}]},
                }
            ]
        },
    }

    rendered = build_discussion_entry(node).render()

    assert "**Discussion:** #12" in rendered and "**Answered:** yes" in rendered
    assert "**@maintainer (accepted answer):** Use 10-30." in rendered
    assert "> **@asker:** Thanks!" in rendered
    assert parse_snapshot(rendered)[0].item_id == 12


def test_refresh_github_repo_keeps_existing_and_partial_progress_on_rate_limit(monkeypatch):
    import datetime as dt

    import scripts.scrape_external as se

    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    old_issue = (
        "## #1: Old but recent enough\n**Issue:** #1 | **Last activity:** 2025-01-01T00:00:00Z\n\nbody about SOLO\n"
    )
    new_issue = se.parse_snapshot("## #2: New\n**Issue:** #2 | **Last activity:** 2026-10-01T00:00:00Z\n\nnew\n")

    def fake_issues_and_pulls(repo, existing, now, since=None):
        raise se.PartialFetchError(se.RateLimitedError("limit"), new_issue, [])

    def fail_discussions(*args, **kwargs):  # must not be called once rate limited
        raise AssertionError("discussions fetched after rate limit")

    monkeypatch.setattr(se, "fetch_github_issues_and_pulls", fake_issues_and_pulls)
    monkeypatch.setattr(se, "fetch_github_discussions", fail_discussions)

    out, rate_limited = se.refresh_github_repo("scverse/scvi-tools", {"issues": old_issue}, now)

    assert rate_limited
    assert set(out) == {"issues"}  # no empty pulls/discussions files are created
    assert [e.item_id for e in se.parse_snapshot(out["issues"])] == [2, 1]


def test_refresh_discourse_is_incremental_and_keeps_existing(monkeypatch):
    import datetime as dt

    import scripts.scrape_external as se

    now = dt.datetime(2026, 11, 1, tzinfo=dt.timezone.utc)
    existing = (
        "## Correct way to run SOLO\n**Topic:** 3949 | **Last activity:** 2026-10-01T00:00:00Z\n\n"
        "**Reply (@cane11)**: run hvg and run SOLO\n"
    )
    page0 = {
        "topic_list": {
            "more_topics_url": "/next",
            "topics": [
                {"id": 1, "pinned": True, "last_posted_at": "2020-01-01T00:00:00Z"},
                {"id": 5000, "last_posted_at": "2026-10-20T00:00:00Z"},
                {"id": 4000, "last_posted_at": "2026-09-15T00:00:00Z"},
            ],
        }
    }
    page1 = {
        "topic_list": {
            "more_topics_url": "/next",
            "topics": [{"id": 3000, "last_posted_at": "2026-05-01T00:00:00Z"}],
        }
    }
    requested_pages: list = []
    fetched_ids: list = []

    def fake_json(url, params=None):
        requested_pages.append((url, params))
        return page0 if params["page"] == 0 else page1

    def fake_thread(tid):
        fetched_ids.append(tid)
        return se.parse_snapshot(f"## New {tid}\n**Topic:** {tid} | **Last activity:** 2026-10-20T00:00:00Z\n\nnew\n")[
            0
        ]

    monkeypatch.setattr(se, "_discourse_json", fake_json)
    monkeypatch.setattr(se, "fetch_discourse_thread", fake_thread)
    monkeypatch.setattr(se.time, "sleep", lambda s: None)

    out = se.refresh_discourse(existing, now)

    assert fetched_ids == [5000]  # only the thread with activity since the newest stored one
    # page 1 only holds older topics, so paging stops there for each listing
    assert len(requested_pages) == 2 * len(se.DISCOURSE_URLS)
    assert [e.item_id for e in se.parse_snapshot(out)] == [5000, 3949]
    assert "run hvg and run SOLO" in out


def test_sync_site_adds_updates_and_never_deletes(tmp_path):
    from scripts.sync_websites import sync_site

    src = tmp_path / "site"
    dst = tmp_path / "knowledge"
    (src / "blog").mkdir(parents=True)
    (src / "src/pages").mkdir(parents=True)
    (src / "blog/2026-1-1-post.md").write_text("# Post\r\ntext  \n", encoding="utf-8")
    (src / "src/pages/team.mdx").write_text("# Team\n", encoding="utf-8")
    (src / "blog/image.png").write_bytes(b"\x89PNG")

    first = sync_site("org/site", src, ["blog", "src/pages"], dst)
    assert sorted(first["added"]) == ["blog/2026-1-1-post.md", "src/pages/team.md"]
    post = (dst / "blog/2026-1-1-post.md").read_text(encoding="utf-8")
    assert post.startswith("<!-- Source: https://github.com/org/site/blob/HEAD/blog/2026-1-1-post.md -->")
    assert post.endswith("# Post\ntext\n")  # normalized like the pre-commit hooks
    assert not (dst / "blog/image.png").exists()

    # A post removed upstream is kept; a changed page is updated; an unchanged sync is a no-op.
    (src / "blog/2026-1-1-post.md").unlink()
    (src / "src/pages/team.mdx").write_text("# Team\nnew member\n", encoding="utf-8")
    second = sync_site("org/site", src, ["blog", "src/pages"], dst)
    assert second == {"added": [], "updated": ["src/pages/team.md"]}
    assert (dst / "blog/2026-1-1-post.md").exists()
    assert sync_site("org/site", src, ["blog", "src/pages"], dst) == {"added": [], "updated": []}


def test_parse_snapshot_ignores_markdown_headings_inside_bodies():
    from scripts.scrape_external import build_github_entry, parse_snapshot, render_snapshot

    item = {
        "number": 3500,
        "title": "Add feature",
        "state": "open",
        "pull_request": {},
        "user": {"login": "dev", "type": "User"},
        "updated_at": "2026-10-01T00:00:00Z",
        "body": "## Summary\nAdds X.\n\n## Test plan\n- run tests",
    }
    text = render_snapshot("T", "PRs", [build_github_entry(item, [])])

    entries = parse_snapshot(text)

    assert [e.item_id for e in entries] == [3500]
    assert "## Test plan" in entries[0].body
    assert parse_snapshot(render_snapshot("T", "PRs", entries)) == entries


def test_build_github_entry_includes_pr_reviews_and_inline_comments_in_time_order():
    from scripts.scrape_external import build_github_entry

    item = {
        "number": 9,
        "title": "PR",
        "state": "open",
        "pull_request": {},
        "user": {"login": "dev", "type": "User"},
        "updated_at": "2026-05-05T00:00:00Z",
        "body": "",
    }
    comments = [{"user": {"login": "a", "type": "User"}, "body": "third", "created_at": "2026-05-03T00:00:00Z"}]
    reviews = [
        {
            "user": {"login": "r", "type": "User"},
            "body": "first",
            "state": "CHANGES_REQUESTED",
            "submitted_at": "2026-05-01T00:00:00Z",
        },
        {
            "user": {"login": "r", "type": "User"},
            "body": "",
            "state": "APPROVED",
            "submitted_at": "2026-05-04T00:00:00Z",
        },
    ]
    review_comments = [
        {
            "user": {"login": "r", "type": "User"},
            "body": "second",
            "path": "src/x.py",
            "created_at": "2026-05-02T00:00:00Z",
        },
        {
            "user": {"login": "bot[bot]", "type": "Bot"},
            "body": "noise",
            "path": "src/x.py",
            "created_at": "2026-05-02T00:00:00Z",
        },
    ]

    rendered = build_github_entry(item, comments, reviews, review_comments).render()

    assert "**Comments:** 3" in rendered
    first = rendered.index("**@r (review, changes requested):** first")
    second = rendered.index("**@r on `src/x.py`:** second")
    third = rendered.index("**@a:** third")
    assert first < second < third
    assert "noise" not in rendered
