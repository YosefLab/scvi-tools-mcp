from pathlib import Path
import pytest
from scvi_tools_mcp.tools.utils import load_knowledge, truncate, paginate, KnowledgeNotFoundError

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_knowledge_returns_content(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Hello\nworld")
    content = load_knowledge(f)
    assert content == "# Hello\nworld"


def test_load_knowledge_raises_on_missing(tmp_path):
    with pytest.raises(KnowledgeNotFoundError):
        load_knowledge(tmp_path / "missing.md")


def test_truncate_short_content_unchanged():
    result = truncate("hello", max_chars=100)
    assert result.content == "hello"
    assert result.truncated is False


def test_truncate_long_content_cut():
    long = "x" * 5000
    result = truncate(long, max_chars=100)
    assert len(result.content) <= 100
    assert result.truncated is True


def test_paginate_single_page():
    lines = ["line"] * 10
    result = paginate(lines, page=1, page_size=20)
    assert result.total_pages == 1
    assert len(result.lines) == 10


def test_paginate_multiple_pages():
    lines = [f"line{i}" for i in range(50)]
    result = paginate(lines, page=2, page_size=20)
    assert result.total_pages == 3
    assert result.lines[0] == "line20"


def test_paginate_out_of_range():
    lines = ["line"] * 10
    result = paginate(lines, page=99, page_size=20)
    assert result.lines == []
    assert result.total_pages == 1
