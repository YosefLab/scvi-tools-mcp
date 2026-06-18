"""Scrape a snapshot of GitHub issues and Discourse threads for the FAQ knowledge base.

Requires: requests (included in dev extras)
GitHub token recommended: set GITHUB_TOKEN env var for higher rate limits.

Usage:
    python scripts/scrape_external.py
"""

from __future__ import annotations

import html
import os
import re
import time
from pathlib import Path

import requests

KNOWLEDGE_FAQ = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/faq"
GITHUB_REPO = "scverse/scvi-tools"
GITHUB_ISSUES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
DISCOURSE_URLS = [
    "https://discourse.scverse.org/c/help/scvi-tools/7.json",
    "https://discourse.scverse.org/tag/scvi.json",
]
MAX_ISSUES = 100
MAX_THREADS = 30
MAX_BODY_CHARS = 1500
MAX_COMMENT_CHARS = 800
MAX_COMMENTS_PER_ISSUE = 5
MAX_POSTS_PER_THREAD = 5


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _trim(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) > limit:
        return text[:limit].rstrip() + " …"
    return text


def fetch_github_issues() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    params = {"state": "open", "per_page": MAX_ISSUES, "sort": "comments", "direction": "desc"}
    resp = requests.get(GITHUB_ISSUES_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    issues = [i for i in resp.json() if "pull_request" not in i]

    lines = [
        "# scvi-tools GitHub Issues Q&A",
        "",
        f"Top {len(issues)} issues by discussion volume (PRs excluded).",
        "",
    ]

    for issue in issues:
        title = issue.get("title", "")
        number = issue.get("number", "")
        n_comments = issue.get("comments", 0)
        state = issue.get("state", "")
        body = _trim(issue.get("body") or "", MAX_BODY_CHARS)
        labels = ", ".join(lb["name"] for lb in issue.get("labels", []))

        lines += [
            f"## #{number}: {title}",
            f"**State:** {state} | **Comments:** {n_comments}" + (f" | **Labels:** {labels}" if labels else ""),
            "",
        ]
        if body:
            lines += [body, ""]

        # Fetch comments for issues with discussion
        if n_comments > 0:
            try:
                time.sleep(0.3)
                comments_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{number}/comments"
                cr = requests.get(
                    comments_url, headers=headers, params={"per_page": MAX_COMMENTS_PER_ISSUE}, timeout=30
                )
                cr.raise_for_status()
                for comment in cr.json():
                    author = comment.get("user", {}).get("login", "unknown")
                    cbody = _trim(comment.get("body") or "", MAX_COMMENT_CHARS)
                    if cbody:
                        lines += [f"**@{author}:** {cbody}", ""]
            except Exception as e:
                print(f"  WARN: Could not fetch comments for #{number}: {e}")

    return "\n".join(lines)


def fetch_discourse_threads() -> str:
    seen: set[int] = set()
    all_topics: list[dict] = []

    for url in DISCOURSE_URLS:
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for topic in data.get("topic_list", {}).get("topics", []):
                tid = topic.get("id")
                if tid not in seen:
                    seen.add(tid)
                    all_topics.append(topic)
        except Exception as e:
            print(f"  WARN: Discourse list fetch failed for {url}: {e}")
        time.sleep(1)

    # Sort by views descending, take top N
    all_topics = sorted(all_topics, key=lambda t: t.get("views", 0), reverse=True)[:MAX_THREADS]

    lines = [
        "# scvi-tools Discourse Forum Q&A",
        "",
        f"Top {len(all_topics)} threads by views (deduplicated across sources).",
        "",
    ]

    for topic in all_topics:
        title = topic.get("title", "")
        posts_count = topic.get("posts_count", 0)
        views = topic.get("views", 0)
        topic_id = topic.get("id")

        lines += [
            f"## {title}",
            f"**Posts:** {posts_count} | **Views:** {views}",
            "",
        ]

        # Fetch the actual thread content
        if topic_id:
            try:
                time.sleep(0.5)
                thread_url = f"https://discourse.scverse.org/t/{topic_id}.json"
                tr = requests.get(thread_url, timeout=30)
                tr.raise_for_status()
                posts = tr.json().get("post_stream", {}).get("posts", [])[:MAX_POSTS_PER_THREAD]
                for i, post in enumerate(posts):
                    cooked = post.get("cooked") or post.get("raw") or ""
                    text = _trim(_strip_html(cooked), MAX_COMMENT_CHARS)
                    author = post.get("username", "unknown")
                    role = "**Question**" if i == 0 else f"**Reply (@{author})**"
                    if text:
                        lines += [f"{role}: {text}", ""]
            except Exception as e:
                print(f"  WARN: Could not fetch thread {topic_id}: {e}")

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
