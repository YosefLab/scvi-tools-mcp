"""Scrape GitHub issues, pull requests, Discussions and Discourse threads for the FAQ knowledge base.

All three snapshots are *accumulative*: each run merges newly fetched content into
the existing markdown files instead of overwriting them. An entry is only removed
once its last activity is older than ``RETENTION_DAYS`` (3 years), because by then
it is likely obsolete. Entries are never dropped because they fell out of a
listing, a ranking, or because a fetch failed.

* Discourse: the scvi-tools category and the ``scvi`` tag are listed (newest activity
  first) and every thread with posts since the newest stored thread is (re-)fetched
  with all its posts. The first run builds a baseline of the whole retention window.
Both are incremental, so after the first (baseline) run the monthly refresh only
fetches what changed since the previous run.

* GitHub (every repo in ``GITHUB_REPOS``): issues and PRs (bots excluded) are fetched
  incrementally, oldest update first, starting from the newest ``Last activity`` already
  stored for that repo. If the API rate limit is hit, progress so far is saved and the
  next run resumes from there. Discussions are fetched via GraphQL (needs a token) for
  repos that have them enabled.

Requires: requests (included in dev extras)
GitHub token recommended: set GITHUB_TOKEN env var for higher rate limits
(e.g. ``GITHUB_TOKEN=$(gh auth token) python scripts/scrape_external.py``).

Usage:
    python scripts/scrape_external.py
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import html
import os
import re
import time
from collections.abc import Callable, Iterable
from pathlib import Path

import requests

KNOWLEDGE_FAQ = Path(__file__).parent.parent / "src/scvi_tools_mcp/knowledge/faq"

# Keep every entry with activity in this window; older entries may be pruned as obsolete.
RETENTION_DAYS = 3 * 365

# Repos whose issues, PRs and (when enabled) Discussions are snapshotted. Smaller repos come
# first so that, if the shared API rate limit runs out, they are not starved by scvi-tools.
GITHUB_REPOS = [
    "YosefLab/scvi-hub-models",
    "scverse/scvi-colab",
    "YosefLab/scviva-tools",
    "YosefLab/scib-metrics",
    "scverse/scvi-tutorials",
    "scverse/scvi-tools",
]
GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = f"{GITHUB_API}/graphql"
# Snapshot files written before multi-repo support; folded into the scvi-tools files.
LEGACY_GITHUB_FILES = {"github_issues.md": ("scverse/scvi-tools", "issues")}
DISCOURSE_BASE = "https://discourse.scverse.org"
DISCOURSE_URLS = [
    f"{DISCOURSE_BASE}/c/help/scvi-tools/7.json",
    f"{DISCOURSE_BASE}/tag/scvi.json",
]
DISCOURSE_MAX_PAGES = 200  # safety cap on listing pagination (30 topics/page)
GITHUB_MAX_PAGES = 200  # safety cap on listing pagination (100 items/page)

MAX_BODY_CHARS = 1500
MAX_COMMENT_CHARS = 800


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _trim(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) > limit:
        return text[:limit].rstrip() + " …"
    return text


def _parse_ts(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _fmt_ts(value: dt.datetime | None) -> str:
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if value else "unknown"


# ---------------------------------------------------------------------------
# Accumulative snapshot files
#
# Each file is "# header" followed by "## title" sections. A section carries a
# metadata line such as
#     **Topic:** 3949 | **Last activity:** 2026-04-23T09:29:07Z
#     **Issue:** #3010 | **Last activity:** ...
#     **PR:** #3011 | **Last activity:** ...
#     **Discussion:** #12 | **Last activity:** ...
# which is used to match it against freshly fetched content and to apply the
# retention window. Sections without it (written by older versions of this
# script) are matched by title and never expire.
#
# Issue/PR/discussion bodies often contain their own "## Summary"-style headings,
# so a "## " line only starts a new section when the next line is a metadata
# line (current format) or the first line of the legacy formats.
# ---------------------------------------------------------------------------

_SECTION_RE = re.compile(
    r"^## (?P<title>.+)\n(?=\*\*(?:Topic|Issue|PR|Discussion|Posts|State):\*\* )",
    re.MULTILINE,
)
_META_RE = re.compile(r"\*\*(?:Topic|Issue|PR|Discussion):\*\* #?(?P<id>\d+) \| \*\*Last activity:\*\* (?P<last>\S+)")


@dataclasses.dataclass
class SnapshotEntry:
    """One ``## title`` section of a snapshot file."""

    title: str
    body: str  # everything after the "## title" line
    item_id: int | None = None  # None for legacy sections written before ids were recorded
    last_activity: dt.datetime | None = None

    @property
    def key(self) -> str:
        return f"id:{self.item_id}" if self.item_id is not None else f"title:{self.title.strip().lower()}"

    def render(self) -> str:
        return f"## {self.title}\n{self.body.strip()}\n"


def parse_snapshot(text: str) -> list[SnapshotEntry]:
    """Split an existing snapshot file into its sections."""
    matches = list(_SECTION_RE.finditer(text))
    entries: list[SnapshotEntry] = []
    for i, m in enumerate(matches):
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end() : body_end]
        meta = _META_RE.search(body)
        entries.append(
            SnapshotEntry(
                title=m.group("title").strip(),
                body=body,
                item_id=int(meta.group("id")) if meta else None,
                last_activity=_parse_ts(meta.group("last")) if meta else None,
            )
        )
    return entries


def merge_entries(
    existing: Iterable[SnapshotEntry],
    fetched: Iterable[SnapshotEntry],
    now: dt.datetime,
    retention_days: int = RETENTION_DAYS,
) -> list[SnapshotEntry]:
    """Merge freshly fetched entries into an existing snapshot.

    * a fetched entry replaces the existing section with the same id (or, for a
      legacy section without an id, the same title);
    * existing entries that were not re-fetched are kept unchanged;
    * the only entries dropped are those whose last activity is known and older
      than the retention window.
    """
    cutoff = now - dt.timedelta(days=retention_days)
    merged: dict[str, SnapshotEntry] = {e.key: e for e in existing}
    for entry in fetched:
        merged.pop(f"title:{entry.title.strip().lower()}", None)  # upgrade a legacy section
        merged[entry.key] = entry

    kept = [e for e in merged.values() if e.last_activity is None or e.last_activity >= cutoff]

    epoch = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    # Most recently active first; legacy sections (unknown date) last, in their original order.
    return sorted(kept, key=lambda e: e.last_activity or epoch, reverse=True)


def render_snapshot(title: str, description: str, entries: list[SnapshotEntry]) -> str:
    header = f"# {title}\n\n{len(entries)} {description}\n\n"
    text = header + "\n".join(e.render() for e in entries)
    # LF endings, no trailing whitespace, single final newline (matches the pre-commit hooks).
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n") + "\n"


def _retention_note(noun: str) -> str:
    return (
        f"with activity in the last {RETENTION_DAYS // 365} years, most recently active first. "
        f"This snapshot accumulates across refreshes; {noun} are only removed once they age out of that window."
    )


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


class RateLimitedError(RuntimeError):
    """Raised when the GitHub API rate limit is exhausted."""


def _get(
    url: str,
    params: dict | list | None = None,
    headers: dict | None = None,
    retries: int = 4,
    is_rate_limited: Callable[[requests.Response], bool] | None = None,
) -> requests.Response:
    """GET with exponential back-off on transient errors (429/5xx, connection errors)."""
    delay = 2.0
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(delay)
            delay *= 2
            continue
        if is_rate_limited is not None and is_rate_limited(resp):
            raise RateLimitedError(f"rate limited on {url}: {resp.status_code} {resp.text[:200]}")
        if (resp.status_code == 429 or resp.status_code >= 500) and attempt < retries:
            try:
                retry_after = float(resp.headers.get("Retry-After", 0))
            except ValueError:
                retry_after = 0.0
            time.sleep(max(delay, retry_after))
            delay *= 2
            continue
        resp.raise_for_status()
        return resp
    raise RuntimeError("unreachable")


# ---------------------------------------------------------------------------
# GitHub issues + pull requests
# ---------------------------------------------------------------------------

GITHUB_KINDS = ("issues", "pulls", "discussions")


def github_snapshot_name(repo: str, kind: str) -> str:
    return f"github_{repo.split('/')[1]}_{kind}.md"


def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _github_rate_limited(resp: requests.Response) -> bool:
    if resp.status_code not in (403, 429):
        return False
    return resp.headers.get("X-RateLimit-Remaining") == "0" or "rate limit" in resp.text.lower()


def _github_get(url: str, params: dict | None = None) -> requests.Response:
    return _get(url, params=params, headers=_github_headers(), is_rate_limited=_github_rate_limited)


def _github_graphql(query: str, variables: dict) -> dict:
    delay = 2.0
    for attempt in range(5):
        resp = requests.post(
            GITHUB_GRAPHQL, json={"query": query, "variables": variables}, headers=_github_headers(), timeout=60
        )
        if _github_rate_limited(resp):
            raise RateLimitedError(f"GraphQL rate limited: {resp.status_code} {resp.text[:200]}")
        if (resp.status_code == 429 or resp.status_code >= 500) and attempt < 4:
            time.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
        payload = resp.json()
        errors = payload.get("errors")
        if errors:
            if any(err.get("type") == "RATE_LIMITED" for err in errors):
                raise RateLimitedError(f"GraphQL rate limited: {errors}")
            raise RuntimeError(f"GraphQL errors: {errors}")
        return payload["data"]
    raise RuntimeError("unreachable")


def _is_bot(user: dict | None) -> bool:
    user = user or {}
    return user.get("type") == "Bot" or str(user.get("login", "")).endswith("[bot]")


def _fetch_github_list(url: str) -> list[dict]:
    """GET every page of a GitHub list endpoint."""
    out: list[dict] = []
    next_url: str | None = url
    params: dict | None = {"per_page": 100}
    while next_url:
        resp = _github_get(next_url, params=params)
        out.extend(resp.json())
        next_url = resp.links.get("next", {}).get("url")
        params = None  # the "next" link already carries the query string
    return out


def _fetch_github_comments(repo: str, number: int) -> list[dict]:
    """Conversation comments of an issue or PR."""
    return _fetch_github_list(f"{GITHUB_API}/repos/{repo}/issues/{number}/comments")


def _fetch_github_reviews(repo: str, number: int) -> tuple[list[dict], list[dict]]:
    """Review summaries and inline (code) review comments of a PR."""
    reviews = _fetch_github_list(f"{GITHUB_API}/repos/{repo}/pulls/{number}/reviews")
    review_comments = _fetch_github_list(f"{GITHUB_API}/repos/{repo}/pulls/{number}/comments")
    return reviews, review_comments


def build_github_entry(
    item: dict,
    comments: list[dict],
    reviews: list[dict] | None = None,
    review_comments: list[dict] | None = None,
) -> SnapshotEntry:
    """Render one GitHub issue or PR (as returned by the issues API) into a snapshot section.

    Conversation comments, review summaries and inline review comments are merged
    into a single chronological discussion; bot authors are skipped.
    """
    number = item["number"]
    is_pr = "pull_request" in item
    state = item.get("state", "")
    if is_pr and (item.get("pull_request") or {}).get("merged_at"):
        state = "merged"
    labels = ", ".join(lb["name"] for lb in item.get("labels", []))
    author = (item.get("user") or {}).get("login", "unknown")
    last_activity = _parse_ts(item.get("updated_at")) or _parse_ts(item.get("created_at"))

    timeline: list[tuple[str, str]] = []  # (timestamp, rendered line)
    for comment in comments:
        if _is_bot(comment.get("user")):
            continue
        cbody = _trim(comment.get("body") or "", MAX_COMMENT_CHARS)
        if cbody:
            login = (comment.get("user") or {}).get("login", "unknown")
            timeline.append((comment.get("created_at") or "", f"**@{login}:** {cbody}"))
    for review in reviews or []:
        if _is_bot(review.get("user")):
            continue
        rbody = _trim(review.get("body") or "", MAX_COMMENT_CHARS)
        if rbody:  # approvals without text carry no knowledge
            login = (review.get("user") or {}).get("login", "unknown")
            verdict = str(review.get("state") or "").replace("_", " ").lower()
            timeline.append((review.get("submitted_at") or "", f"**@{login} (review, {verdict}):** {rbody}"))
    for rc in review_comments or []:
        if _is_bot(rc.get("user")):
            continue
        rcbody = _trim(rc.get("body") or "", MAX_COMMENT_CHARS)
        if rcbody:
            login = (rc.get("user") or {}).get("login", "unknown")
            where = f" on `{rc['path']}`" if rc.get("path") else ""
            timeline.append((rc.get("created_at") or "", f"**@{login}{where}:** {rcbody}"))
    timeline.sort(key=lambda t: t[0])

    lines = [
        f"**{'PR' if is_pr else 'Issue'}:** #{number} | **Last activity:** {_fmt_ts(last_activity)}",
        f"**State:** {state} | **Author:** @{author} | **Comments:** {len(timeline)}"
        f" | **Created:** {(item.get('created_at') or '')[:10]}"
        + (f" | **Labels:** {labels}" if labels else "")
        + f" | **URL:** {item.get('html_url', '')}",
        "",
    ]
    body = _trim(item.get("body") or "", MAX_BODY_CHARS)
    if body:
        lines += [body, ""]
    for _, line in timeline:
        lines += [line, ""]

    return SnapshotEntry(
        title=f"#{number}: {(item.get('title') or '').strip()}",
        body="\n" + "\n".join(lines),
        item_id=number,
        last_activity=last_activity,
    )


def _since(existing: Iterable[SnapshotEntry], now: dt.datetime) -> dt.datetime:
    known = [e.last_activity for e in existing if e.item_id is not None and e.last_activity is not None]
    return max(known) if known else now - dt.timedelta(days=RETENTION_DAYS)


def fetch_github_issues_and_pulls(
    repo: str, existing: list[SnapshotEntry], now: dt.datetime, since: dt.datetime | None = None
) -> tuple[list[SnapshotEntry], list[SnapshotEntry]]:
    """Fetch a repo's issues and PRs updated since the newest entry already stored.

    Items are processed oldest update first, so if a run stops early everything up
    to that point can be saved and the next run resumes from the newest stored
    ``Last activity``. Errors propagate as :class:`PartialFetchError` carrying the
    progress made so far. ``since`` overrides the stored cursor (used for backfills).
    """
    since = since or _since(existing, now)
    print(f"  {repo}: issues/PRs updated since {_fmt_ts(since)}")
    issues: list[SnapshotEntry] = []
    pulls: list[SnapshotEntry] = []
    params = {"state": "all", "sort": "updated", "direction": "asc", "since": _fmt_ts(since), "per_page": 100}
    try:
        for page in range(1, GITHUB_MAX_PAGES + 1):
            resp = _github_get(f"{GITHUB_API}/repos/{repo}/issues", params={**params, "page": page})
            for item in resp.json():
                if _is_bot(item.get("user")):
                    continue
                number = item["number"]
                comments = _fetch_github_comments(repo, number) if item.get("comments", 0) > 0 else []
                if "pull_request" in item:
                    reviews, review_comments = _fetch_github_reviews(repo, number)
                    pulls.append(build_github_entry(item, comments, reviews, review_comments))
                else:
                    issues.append(build_github_entry(item, comments))
                time.sleep(0.2)
            if not resp.links.get("next"):
                break
    except Exception as e:
        done = [x.last_activity for x in issues + pulls if x.last_activity is not None]
        if done:
            last = _fmt_ts(max(done))
            print(f"  {repo}: processed up to {last} (resume a backfill with --since {last})")
        raise PartialFetchError(e, issues, pulls) from e
    return issues, pulls


class PartialFetchError(RuntimeError):
    """A fetch stopped early; ``partial`` holds what was fetched before the error."""

    def __init__(self, cause: Exception, *partial: list[SnapshotEntry]):
        super().__init__(str(cause))
        self.cause = cause
        self.partial = partial


_DISCUSSIONS_QUERY = """
query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    hasDiscussionsEnabled
    discussions(first: 25, after: $after, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id number title url body createdAt updatedAt
        author { login }
        category { name }
        answer { id }
        comments(first: 100) {
          pageInfo { hasNextPage endCursor }
          nodes {
            id body author { login }
            replies(first: 100) { pageInfo { hasNextPage endCursor } nodes { body author { login } } }
          }
        }
      }
    }
  }
}
"""

# Follow-up queries for discussions with more comments / replies than fit in the first page.
_DISCUSSION_COMMENTS_QUERY = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on Discussion {
      comments(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id body author { login }
          replies(first: 100) { pageInfo { hasNextPage endCursor } nodes { body author { login } } }
        }
      }
    }
  }
}
"""

_COMMENT_REPLIES_QUERY = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on DiscussionComment {
      replies(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes { body author { login } }
      }
    }
  }
}
"""


def _paginate_connection(conn: dict, fetch_next: Callable[[str], dict]) -> list[dict]:
    """All nodes of a GraphQL connection, following ``pageInfo`` with ``fetch_next(cursor) -> connection``."""
    nodes = list(conn.get("nodes") or [])
    page_info = conn.get("pageInfo") or {}
    while page_info.get("hasNextPage"):
        time.sleep(0.3)
        conn = fetch_next(page_info["endCursor"])
        nodes.extend(conn.get("nodes") or [])
        page_info = conn.get("pageInfo") or {}
    return nodes


def complete_discussion(node: dict) -> dict:
    """Fill in every comment and reply of a discussion node (nested connections are paginated).

    Without this a long discussion would be truncated and, since a fetched entry replaces
    the stored one, the missing answers would be dropped permanently.
    """

    def more_comments(cursor: str) -> dict:
        data = _github_graphql(_DISCUSSION_COMMENTS_QUERY, {"id": node["id"], "after": cursor})
        return data["node"]["comments"]

    comments = _paginate_connection(node.get("comments") or {}, more_comments)
    for comment in comments:

        def more_replies(cursor: str, comment_id: str = comment["id"]) -> dict:
            data = _github_graphql(_COMMENT_REPLIES_QUERY, {"id": comment_id, "after": cursor})
            return data["node"]["replies"]

        replies = _paginate_connection(comment.get("replies") or {}, more_replies)
        comment["replies"] = {"nodes": replies}
    node["comments"] = {"nodes": comments}
    return node


def build_discussion_entry(node: dict) -> SnapshotEntry:
    """Render one GitHub Discussion (GraphQL node) into a snapshot section."""
    number = node["number"]
    last_activity = _parse_ts(node.get("updatedAt")) or _parse_ts(node.get("createdAt"))
    answer_id = (node.get("answer") or {}).get("id")
    author = (node.get("author") or {}).get("login", "unknown")
    comments = (node.get("comments") or {}).get("nodes", [])
    lines = [
        f"**Discussion:** #{number} | **Last activity:** {_fmt_ts(last_activity)}",
        f"**Category:** {(node.get('category') or {}).get('name', '')} | **Author:** @{author}"
        f" | **Comments:** {len(comments)} | **Answered:** {'yes' if answer_id else 'no'}"
        f" | **Created:** {(node.get('createdAt') or '')[:10]} | **URL:** {node.get('url', '')}",
        "",
    ]
    body = _trim(node.get("body") or "", MAX_BODY_CHARS)
    if body:
        lines += [body, ""]
    for comment in comments:
        cauthor = (comment.get("author") or {}).get("login", "unknown")
        marker = " (accepted answer)" if answer_id and comment.get("id") == answer_id else ""
        cbody = _trim(comment.get("body") or "", MAX_COMMENT_CHARS)
        if cbody:
            lines += [f"**@{cauthor}{marker}:** {cbody}", ""]
        for reply in (comment.get("replies") or {}).get("nodes", []):
            rauthor = (reply.get("author") or {}).get("login", "unknown")
            rbody = _trim(reply.get("body") or "", MAX_COMMENT_CHARS)
            if rbody:
                lines += [f"> **@{rauthor}:** {rbody}", ""]
    return SnapshotEntry(
        title=f"#{number}: {(node.get('title') or '').strip()}",
        body="\n" + "\n".join(lines),
        item_id=number,
        last_activity=last_activity,
    )


def fetch_github_discussions(repo: str, existing: list[SnapshotEntry], now: dt.datetime) -> list[SnapshotEntry]:
    """Fetch Discussions updated since the newest stored one (newest first; all-or-nothing)."""
    if not os.environ.get("GITHUB_TOKEN"):
        print(f"  {repo}: skipping Discussions (GraphQL needs GITHUB_TOKEN)")
        return []
    since = _since(existing, now)
    owner, name = repo.split("/")
    fetched: list[SnapshotEntry] = []
    after = None
    while True:
        repo_data = _github_graphql(_DISCUSSIONS_QUERY, {"owner": owner, "name": name, "after": after})["repository"]
        if not repo_data.get("hasDiscussionsEnabled"):
            return []
        conn = repo_data["discussions"]
        for node in conn["nodes"]:
            updated = _parse_ts(node.get("updatedAt"))
            if updated is not None and updated < since:
                return fetched
            fetched.append(build_discussion_entry(complete_discussion(node)))
        if not conn["pageInfo"]["hasNextPage"]:
            return fetched
        after = conn["pageInfo"]["endCursor"]
        time.sleep(0.5)


def _github_header(repo: str, kind: str) -> tuple[str, str]:
    noun = {"issues": "issues", "pulls": "PRs", "discussions": "discussions"}[kind]
    what = {
        "issues": "issues (open and closed, bots excluded)",
        "pulls": "pull requests (open, closed and merged, bots excluded)",
        "discussions": "GitHub Discussions",
    }[kind]
    title = {"issues": "Issues Q&A", "pulls": "Pull Requests", "discussions": "Discussions Q&A"}[kind]
    return f"{repo} GitHub {title}", f"{what} from {repo} " + _retention_note(noun)


def refresh_github_repo(
    repo: str, texts: dict[str, str], now: dt.datetime | None = None, since: dt.datetime | None = None
) -> tuple[dict[str, str], bool]:
    """Refresh one repo's snapshots.

    ``texts`` maps kind ("issues", "pulls", "discussions") to the existing file text.
    Returns ``(new_texts, rate_limited)``; ``new_texts`` only contains kinds that
    have at least one entry, so no empty files are created.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    existing = {kind: parse_snapshot(texts.get(kind, "")) for kind in GITHUB_KINDS}
    fetched: dict[str, list[SnapshotEntry]] = {kind: [] for kind in GITHUB_KINDS}
    rate_limited = False

    try:
        fetched["issues"], fetched["pulls"] = fetch_github_issues_and_pulls(
            repo, existing["issues"] + existing["pulls"], now, since
        )
    except PartialFetchError as e:
        fetched["issues"], fetched["pulls"] = e.partial
        rate_limited = isinstance(e.cause, RateLimitedError)
        print(f"  WARN: {repo} issues/PRs stopped early ({e.cause}); saving progress, next run resumes from here")

    if not rate_limited:
        try:
            fetched["discussions"] = fetch_github_discussions(repo, existing["discussions"], now)
        except Exception as e:
            # Discussions are fetched newest first, so a partial result would leave a gap: discard it.
            rate_limited = isinstance(e, RateLimitedError)
            print(f"  WARN: {repo} Discussions fetch failed ({e}); keeping existing snapshot")

    print(
        f"  {repo}: fetched {len(fetched['issues'])} issues, {len(fetched['pulls'])} PRs,"
        f" {len(fetched['discussions'])} discussions"
    )
    out: dict[str, str] = {}
    for kind in GITHUB_KINDS:
        merged = merge_entries(existing[kind], fetched[kind], now)
        if merged:
            out[kind] = render_snapshot(*_github_header(repo, kind), merged)
    return out, rate_limited


def refresh_github(
    faq_dir: Path,
    now: dt.datetime | None = None,
    since: dt.datetime | None = None,
    repos: list[str] | None = None,
) -> None:
    """Refresh the snapshot files of every repo in ``GITHUB_REPOS`` inside ``faq_dir``.

    ``since`` re-fetches everything updated after that time instead of resuming from
    the stored cursor (e.g. to backfill new fields into existing entries).
    """
    legacy: dict[tuple[str, str], str] = {}
    for fname, target in LEGACY_GITHUB_FILES.items():
        legacy[target] = _read(faq_dir / fname)

    for repo in repos or GITHUB_REPOS:
        texts = {}
        for kind in GITHUB_KINDS:
            text = _read(faq_dir / github_snapshot_name(repo, kind))
            extra = legacy.get((repo, kind), "")
            texts[kind] = text + ("\n" + extra if extra else "")
        try:
            out, rate_limited = refresh_github_repo(repo, texts, now, since)
        except Exception as e:
            print(f"  WARN: {repo} refresh failed: {e}")
            continue
        for kind, md in out.items():
            path = faq_dir / github_snapshot_name(repo, kind)
            path.write_text(md, encoding="utf-8")
            print(f"  wrote {path.name} ({len(md)} chars)")
        if rate_limited:
            print("  GitHub rate limit reached; remaining repos will be refreshed on the next run")
            break
        time.sleep(1)

    # Legacy files have been folded into the per-repo files above.
    for fname, target in LEGACY_GITHUB_FILES.items():
        legacy_path = faq_dir / fname
        if legacy_path.exists() and (faq_dir / github_snapshot_name(*target)).exists():
            legacy_path.unlink()
            print(f"  removed legacy {fname} (merged into {github_snapshot_name(*target)})")


# ---------------------------------------------------------------------------
# Discourse
# ---------------------------------------------------------------------------

DISCOURSE_TITLE = "scvi-tools Discourse Forum Q&A"


def _discourse_json(url: str, params: dict | list | None = None) -> dict:
    return _get(url, params=params).json()


def _topic_activity(topic: dict) -> dt.datetime | None:
    for field in ("last_posted_at", "bumped_at", "created_at"):
        value = _parse_ts(topic.get(field))
        if value is not None:
            return value
    return None


def list_discourse_topics(since: dt.datetime, max_pages: int = DISCOURSE_MAX_PAGES) -> dict[int, dict]:
    """Collect topic stubs active since ``since`` from every Discourse listing, deduplicated by id.

    Listings are ordered by latest activity (pinned topics first), so paging stops at
    the first page whose non-pinned topics are all older than ``since``.
    """
    topics: dict[int, dict] = {}
    for url in DISCOURSE_URLS:
        for page in range(max_pages):
            try:
                data = _discourse_json(url, params={"page": page})
            except Exception as e:
                print(f"  WARN: Discourse list fetch failed for {url} page {page}: {e}")
                break
            topic_list = data.get("topic_list", {})
            page_topics = topic_list.get("topics", [])
            for topic in page_topics:
                tid = topic.get("id")
                activity = _topic_activity(topic)
                if tid is not None and (activity is None or activity >= since):
                    topics.setdefault(tid, topic)
            unpinned = [t for t in page_topics if not t.get("pinned")]
            reached_older = bool(unpinned) and all((_topic_activity(t) or since) < since for t in unpinned)
            if not page_topics or reached_older or not topic_list.get("more_topics_url"):
                break
            time.sleep(0.5)
    return topics


def _fetch_all_posts(topic_id: int, thread: dict) -> list[dict]:
    """Return every post of a thread (Discourse only inlines the first ~20)."""
    post_stream = thread.get("post_stream", {})
    posts = list(post_stream.get("posts", []))
    have = {p.get("id") for p in posts}
    missing = [pid for pid in post_stream.get("stream", []) if pid not in have]
    for i in range(0, len(missing), 20):
        time.sleep(0.5)
        chunk = missing[i : i + 20]
        data = _discourse_json(
            f"{DISCOURSE_BASE}/t/{topic_id}/posts.json", params=[("post_ids[]", pid) for pid in chunk]
        )
        posts.extend(data.get("post_stream", {}).get("posts", []))
    return sorted(posts, key=lambda p: p.get("post_number", 0))


def fetch_discourse_thread(topic_id: int) -> SnapshotEntry:
    """Fetch and render a single thread with all of its posts."""
    thread = _discourse_json(f"{DISCOURSE_BASE}/t/{topic_id}.json")
    posts = _fetch_all_posts(topic_id, thread)
    last_activity = _parse_ts(thread.get("last_posted_at")) or _parse_ts(thread.get("created_at"))
    slug = thread.get("slug") or "topic"

    lines = [
        f"**Topic:** {topic_id} | **Last activity:** {_fmt_ts(last_activity)}",
        f"**Posts:** {thread.get('posts_count', len(posts))} | **Views:** {thread.get('views', 0)}"
        f" | **Created:** {(thread.get('created_at') or '')[:10]} | **URL:** {DISCOURSE_BASE}/t/{slug}/{topic_id}",
        "",
    ]
    for post in posts:
        cooked = post.get("cooked") or post.get("raw") or ""
        text = _trim(_strip_html(cooked), MAX_COMMENT_CHARS)
        author = post.get("username", "unknown")
        role = "**Question**" if post.get("post_number") == 1 else f"**Reply (@{author})**"
        if text:
            lines += [f"{role}: {text}", ""]

    return SnapshotEntry(
        title=(thread.get("title") or "").strip(),
        body="\n" + "\n".join(lines),
        item_id=topic_id,
        last_activity=last_activity,
    )


def refresh_discourse(existing_text: str = "", now: dt.datetime | None = None) -> str:
    """Merge Discourse threads active since the newest stored thread into the snapshot.

    The first run (no thread with a ``Last activity`` stored yet) builds a baseline of
    every thread active in the retention window; later runs only fetch threads with
    new posts since the previous run, so monthly refreshes stay light.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    existing = parse_snapshot(existing_text)
    # Small overlap so posts landing while the previous run was in progress are not missed.
    since = _since(existing, now) - dt.timedelta(days=1)
    print(f"  threads active since {_fmt_ts(since)}")

    stubs = list_discourse_topics(since)
    to_fetch = sorted(stubs, reverse=True)
    print(f"  fetching {len(to_fetch)} threads")

    fetched: list[SnapshotEntry] = []
    for tid in to_fetch:
        try:
            time.sleep(0.5)
            fetched.append(fetch_discourse_thread(tid))
        except Exception as e:
            print(f"  WARN: Could not fetch thread {tid}: {e} (keeping existing copy, if any)")

    merged = merge_entries(existing, fetched, now)
    return render_snapshot(
        DISCOURSE_TITLE,
        "threads from the scvi-tools category and `scvi` tag " + _retention_note("threads"),
        merged,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run(
    faq_dir: Path = KNOWLEDGE_FAQ,
    only: str | None = None,
    since: dt.datetime | None = None,
    repos: list[str] | None = None,
) -> None:
    faq_dir.mkdir(parents=True, exist_ok=True)

    if only in (None, "github"):
        print("Fetching GitHub issues, pull requests and discussions...")
        try:
            refresh_github(faq_dir, since=since, repos=repos)
        except Exception as e:
            print(f"  WARN: GitHub refresh failed: {e}")
        time.sleep(1)

    if only in (None, "discourse"):
        print("Fetching Discourse threads...")
        discourse_path = faq_dir / "discourse_threads.md"
        try:
            discourse_md = refresh_discourse(_read(discourse_path))
            discourse_path.write_text(discourse_md, encoding="utf-8")
            print(f"  wrote {discourse_path.name} ({len(discourse_md)} chars)")
        except Exception as e:
            print(f"  WARN: Discourse refresh failed: {e}")

    print("Done.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Refresh the accumulative GitHub/Discourse FAQ snapshots.")
    parser.add_argument("faq_dir", nargs="?", type=Path, default=KNOWLEDGE_FAQ)
    parser.add_argument("--only", choices=["github", "discourse"], help="refresh only one source")
    parser.add_argument(
        "--since",
        type=_parse_ts,
        help="GitHub: re-fetch everything updated after this ISO time instead of resuming from the stored cursor",
    )
    parser.add_argument("--repo", action="append", dest="repos", help="GitHub: limit to this repo (repeatable)")
    args = parser.parse_args()
    run(args.faq_dir, only=args.only, since=args.since, repos=args.repos)
