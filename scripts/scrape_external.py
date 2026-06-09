"""Scrape a snapshot of GitHub issues and Discourse threads for the FAQ knowledge base.

Requires: requests (included in dev extras)
GitHub token recommended: set GITHUB_TOKEN env var for higher rate limits.

Usage:
    python scripts/scrape_external.py
"""
from __future__ import annotations
import os
import time
from pathlib import Path
import requests

KNOWLEDGE_FAQ = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/faq"
GITHUB_ISSUES_URL = "https://api.github.com/repos/scverse/scvi-tools/issues"
DISCOURSE_URL = "https://discourse.scverse.org/c/help/scvi-tools/7.json"
MAX_ISSUES = 50
MAX_THREADS = 30


def fetch_github_issues() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    params = {"state": "open", "per_page": MAX_ISSUES, "sort": "comments", "direction": "desc"}
    resp = requests.get(GITHUB_ISSUES_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    issues = resp.json()
    lines = ["# scvi-tools GitHub Issues Snapshot", "", f"Fetched top {len(issues)} issues by comment count.", ""]
    for issue in issues:
        title = issue.get("title", "")
        number = issue.get("number", "")
        comments = issue.get("comments", 0)
        body = (issue.get("body") or "")[:500].replace("\n", " ")
        lines += [
            f"## #{number}: {title}",
            f"**Comments:** {comments}",
            f"**Body:** {body}",
            "",
        ]
    return "\n".join(lines)


def fetch_discourse_threads() -> str:
    resp = requests.get(DISCOURSE_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    topics = data.get("topic_list", {}).get("topics", [])[:MAX_THREADS]
    lines = ["# scvi-tools Discourse Forum Snapshot", "", f"Fetched top {len(topics)} threads.", ""]
    for topic in topics:
        title = topic.get("title", "")
        posts = topic.get("posts_count", 0)
        views = topic.get("views", 0)
        lines += [
            f"## {title}",
            f"**Posts:** {posts} | **Views:** {views}",
            "",
        ]
    return "\n".join(lines)


def run() -> None:
    KNOWLEDGE_FAQ.mkdir(parents=True, exist_ok=True)
    print("Fetching GitHub issues...")
    try:
        issues_md = fetch_github_issues()
        (KNOWLEDGE_FAQ / "github_issues.md").write_text(issues_md, encoding="utf-8")
        print(f"  wrote github_issues.md ({len(issues_md)} chars)")
    except Exception as e:
        print(f"  WARN: GitHub fetch failed: {e}")
    time.sleep(1)
    print("Fetching Discourse threads...")
    try:
        discourse_md = fetch_discourse_threads()
        (KNOWLEDGE_FAQ / "discourse_threads.md").write_text(discourse_md, encoding="utf-8")
        print(f"  wrote discourse_threads.md ({len(discourse_md)} chars)")
    except Exception as e:
        print(f"  WARN: Discourse fetch failed: {e}")
    print("Done.")


if __name__ == "__main__":
    run()
