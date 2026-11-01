"""Sync the scvi-tools and scviva-tools project websites (blog posts and pages) into the knowledge base.

The sites are Docusaurus projects; their text content lives in Markdown/MDX files
(``blog/``, ``src/pages/``, ``get_started/``). Each run sparse-clones the site repos
and copies those files to ``knowledge/websites/<repo>/`` (``.mdx`` is saved as ``.md``
so it is picked up by ``search_knowledge``).

The snapshot is *accumulative*: new files are added and changed files are updated,
but files that disappear upstream are never deleted locally.

Requires: git

Usage:
    python scripts/sync_websites.py [--dst DIR]
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

KNOWLEDGE_WEBSITES = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/websites"

# repo -> directories (relative to the repo root) holding the site's text content
SITES: dict[str, list[str]] = {
    "scverse/scvi-tools-site": ["blog", "src/pages", "get_started"],
    "YosefLab/scviva-tools-website": ["blog", "src/pages"],
}
CONTENT_SUFFIXES = (".md", ".mdx")


def clone_site(repo: str, dirs: list[str], dest: Path) -> str:
    """Sparse, blob-less shallow clone of ``dirs`` of ``repo`` (default branch). Returns the short HEAD sha."""
    subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", f"https://github.com/{repo}.git", str(dest)],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", *dirs], check=True, capture_output=True)
    return subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "--short", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def normalize_whitespace(text: str) -> str:
    """LF line endings, no trailing whitespace, exactly one final newline (matches the pre-commit hooks)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n") + "\n"


def _render(repo: str, rel: Path, text: str) -> str:
    source = f"https://github.com/{repo}/blob/HEAD/{rel.as_posix()}"
    header = f"<!-- Source: {source} -->\n\n"
    return header + normalize_whitespace(text.removeprefix("﻿"))


def sync_site(repo: str, src_root: Path, dirs: list[str], dst_root: Path) -> dict[str, list[str]]:
    """Copy content files of one site checkout into ``dst_root``; never deletes. Returns added/updated paths."""
    changes: dict[str, list[str]] = {"added": [], "updated": []}
    for d in dirs:
        base = src_root / d
        if not base.is_dir():
            continue
        for src in sorted(base.rglob("*")):
            if not src.is_file() or src.suffix not in CONTENT_SUFFIXES:
                continue
            rel = src.relative_to(src_root)
            dst = (dst_root / rel).with_suffix(".md")
            content = _render(repo, rel, src.read_text(encoding="utf-8"))
            if dst.exists():
                if dst.read_text(encoding="utf-8") == content:
                    continue
                changes["updated"].append(str(dst.relative_to(dst_root)))
            else:
                changes["added"].append(str(dst.relative_to(dst_root)))
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(content, encoding="utf-8")
    return changes


def run(dst: Path = KNOWLEDGE_WEBSITES) -> None:
    for repo, dirs in SITES.items():
        site_dst = dst / repo.split("/")[1]
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp) / "site"
            try:
                sha = clone_site(repo, dirs, checkout)
            except subprocess.CalledProcessError as e:
                print(f"WARN: could not clone {repo}: {e.stderr!r}")
                continue
            changes = sync_site(repo, checkout, dirs, site_dst)
        print(f"{repo}@{sha}: {len(changes['added'])} added, {len(changes['updated'])} updated")
        for kind, paths in changes.items():
            for path in paths:
                print(f"  {kind}: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dst", type=Path, default=KNOWLEDGE_WEBSITES)
    run(parser.parse_args().dst)
