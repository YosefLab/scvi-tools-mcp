"""Entry-level search over the community snapshots in ``knowledge/faq/``.

The GitHub (issues, PRs, discussions) and Discourse snapshots are single large
Markdown files made of many independent ``## title`` entries, each with a
metadata line such as ``**Issue:** #123 | **Last activity:** 2026-04-23T09:29:07Z``
(written by ``scripts/scrape_external.py``). Ranking whole files would let the
biggest file win every query, so these files are split into entries that are
ranked individually by keyword relevance weighted by recency: when several
threads answer the same question, the most recent answer should come first.
"""

from __future__ import annotations

import datetime as dt
import functools
import math
import re
from dataclasses import dataclass
from pathlib import Path

# Same section rule as scripts/scrape_external.py: a "## " line only starts an entry when
# the next line is its metadata line (bodies often contain their own "## Summary" headings).
_SECTION_RE = re.compile(
    r"^## (?P<title>.+)\n(?=\*\*(?:Topic|Issue|PR|Discussion|Posts|State):\*\* )",
    re.MULTILINE,
)
_LAST_ACTIVITY_RE = re.compile(r"\*\*Last activity:\*\* (\S+)")
_URL_RE = re.compile(r"\*\*URL:\*\* (\S+)")
_METADATA_PREFIXES = (
    "**Topic:**",
    "**Issue:**",
    "**PR:**",
    "**Discussion:**",
    "**Posts:**",
    "**State:**",
    "**Category:**",
)

# Recency weight halves every RECENCY_HALF_LIFE_DAYS, but never drops below MIN_RECENCY_WEIGHT
# so a much better (older) match can still outrank a weak recent one.
RECENCY_HALF_LIFE_DAYS = 365
MIN_RECENCY_WEIGHT = 0.125

STOPWORDS = frozenset(
    "the and for with how what why when where which who does can could should would are was were "
    "this that these those from into about have has had not but you your use using get any all "
    "there their them then than its it's".split()
)


@dataclass(frozen=True)
class CommunityEntry:
    source: str  # snapshot file stem, e.g. "github_scvi-tools_issues"
    title: str
    body: str
    body_lower: str
    last_activity: dt.datetime | None
    url: str


def keywords_from_query(query: str) -> list[str]:
    """Lower-cased query terms longer than two characters, minus common stopwords (deduplicated)."""
    seen: dict[str, None] = {}
    for word in query.lower().split():
        word = word.strip(".,;:!?\"'()[]{}")
        if len(word) > 2 and word not in STOPWORDS:
            seen.setdefault(word, None)
    return list(seen)


def _parse_ts(value: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def split_entries(text: str, source: str) -> list[CommunityEntry]:
    matches = list(_SECTION_RE.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end() : end]
        meta = _LAST_ACTIVITY_RE.search(body)
        url = _URL_RE.search(body)
        title = m.group("title").strip()
        entries.append(
            CommunityEntry(
                source=source,
                title=title,
                body=body,
                body_lower=f"{title}\n{body}".lower(),
                last_activity=_parse_ts(meta.group(1)) if meta else None,
                url=url.group(1) if url else "",
            )
        )
    return entries


@functools.lru_cache(maxsize=64)
def _load_file(path: str, mtime_ns: int) -> tuple[CommunityEntry, ...]:
    p = Path(path)
    return tuple(split_entries(p.read_text(encoding="utf-8"), p.stem))


def load_entries(faq_dir: Path) -> list[CommunityEntry]:
    """All entries of every snapshot file in ``faq_dir`` (cached per file modification time)."""
    entries: list[CommunityEntry] = []
    if not faq_dir.exists():
        return entries
    for md in sorted(faq_dir.glob("*.md")):
        try:
            entries.extend(_load_file(str(md), md.stat().st_mtime_ns))
        except OSError:
            continue
    return entries


def is_snapshot_file(path: Path) -> bool:
    """True for files made of community entries (ranked per entry instead of per file)."""
    try:
        return bool(_load_file(str(path), path.stat().st_mtime_ns))
    except OSError:
        return False


def recency_weight(last_activity: dt.datetime | None, now: dt.datetime) -> float:
    if last_activity is None:
        return MIN_RECENCY_WEIGHT
    age_days = max((now - last_activity).total_seconds() / 86400, 0.0)
    return max(0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS), MIN_RECENCY_WEIGHT)


def relevance(entry: CommunityEntry, keywords: list[str]) -> float:
    """Distinct query terms matched dominate (squared); total occurrences (log-damped) break ties.

    Squaring coverage means an entry answering the whole question is not overtaken by a
    partially matching one just because it is newer: a full 3-term match from a year ago
    (9 x 0.5) still beats a 2-term match from today (4 x 1.0), while among entries that
    match equally well the more recent one ranks first.
    """
    counts = [entry.body_lower.count(kw) for kw in keywords]
    matched = sum(1 for c in counts if c)
    if not matched:
        return 0.0
    return matched**2 + math.log1p(sum(counts)) / 10


def best_line(entry: CommunityEntry, keywords: list[str], limit: int = 200) -> str:
    """The body line containing the most distinct query terms (metadata lines skipped)."""
    best, best_hits = "", 0
    for line in entry.body.splitlines():
        stripped = line.strip()
        if len(stripped) <= 20 or stripped.startswith(_METADATA_PREFIXES):
            continue
        low = stripped.lower()
        hits = sum(1 for kw in keywords if kw in low)
        if hits > best_hits:
            best, best_hits = stripped, hits
    return best[:limit] + (" …" if len(best) > limit else "")


def rank_entries(
    entries: list[CommunityEntry],
    keywords: list[str],
    now: dt.datetime | None = None,
    limit: int = 5,
) -> list[tuple[float, CommunityEntry]]:
    """Top ``limit`` entries by relevance x recency weight."""
    now = now or dt.datetime.now(dt.timezone.utc)
    scored = []
    for entry in entries:
        rel = relevance(entry, keywords)
        if rel:
            scored.append((rel * recency_weight(entry.last_activity, now), entry))
    epoch = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    scored.sort(key=lambda s: (s[0], s[1].last_activity or epoch), reverse=True)
    return scored[:limit]


def format_entry(entry: CommunityEntry, keywords: list[str]) -> list[str]:
    date = entry.last_activity.date().isoformat() if entry.last_activity else "date unknown"
    lines = [f"- **{entry.title}** ({entry.source}, last activity {date})"]
    if entry.url:
        lines.append(f"  {entry.url}")
    excerpt = best_line(entry, keywords)
    if excerpt:
        lines.append(f"  > {excerpt}")
    return lines
