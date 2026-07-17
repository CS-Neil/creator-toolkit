#!/usr/bin/env python3
"""Extract a deterministic 24-hour window from a FreshRSS per-user SQLite DB."""

from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


class TextExtractor(HTMLParser):
    BREAK_TAGS = {"br", "p", "div", "section", "li", "h1", "h2", "h3", "h4", "tr"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BREAK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.BREAK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    parser = TextExtractor()
    parser.feed(value)
    text = html.unescape("".join(parser.parts)).replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def parse_end(value: str | None, timezone: ZoneInfo) -> datetime:
    if not value:
        return datetime.now(timezone).replace(microsecond=0)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone).replace(microsecond=0)


def detect_platform(link: str, feed_url: str) -> str | None:
    host = urlparse(link).netloc.lower()
    feed_lower = feed_url.lower()
    if host == "mp.weixin.qq.com" or "mp.weixin.qq.com" in feed_lower:
        return "公众号"
    if host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        return "X"
    if "/twitter/" in feed_lower or "/x/" in feed_lower:
        return "X"
    return None


def external_id(platform: str, link: str, guid: str, entry_id: int) -> str:
    pattern = r"/s/([^/?#]+)" if platform == "公众号" else r"/status/(\d+)"
    match = re.search(pattern, link)
    if match:
        return match.group(1)
    return guid.strip() or str(entry_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--end", help="ISO-8601 end timestamp; defaults to now")
    parser.add_argument("--hours", type=float, default=24.0)
    parser.add_argument("--timezone", default="Asia/Shanghai")
    args = parser.parse_args()

    if args.hours <= 0:
        raise SystemExit("--hours must be positive")
    if not args.db.is_file():
        raise SystemExit(f"FreshRSS DB not found: {args.db}")

    timezone = ZoneInfo(args.timezone)
    end = parse_end(args.end, timezone)
    start = end - timedelta(hours=args.hours)
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    query = """
        SELECT e.id, e.guid, e.title, e.author, e.content, e.link,
               e.date, e.lastSeen, f.name, f.url, c.name
        FROM entry AS e
        LEFT JOIN feed AS f ON f.id = e.id_feed
        LEFT JOIN category AS c ON c.id = f.category
        WHERE COALESCE(NULLIF(e.date, 0), e.lastSeen) >= ?
          AND COALESCE(NULLIF(e.date, 0), e.lastSeen) < ?
        ORDER BY COALESCE(NULLIF(e.date, 0), e.lastSeen) DESC, e.id DESC
    """
    connection = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    rows = connection.execute(query, (start_epoch, end_epoch)).fetchall()
    connection.close()

    seen: set[tuple[str, str]] = set()
    entries: list[dict[str, object]] = []
    skipped_other = 0
    for row in rows:
        (entry_id, guid, title, author, content, link, published, last_seen,
         feed_name, feed_url, category_name) = row
        platform = detect_platform(link or "", feed_url or "")
        if platform is None:
            skipped_other += 1
            continue
        source_id = external_id(platform, link or "", guid or "", entry_id)
        duplicate_key = (platform, source_id)
        is_duplicate = duplicate_key in seen
        seen.add(duplicate_key)
        timestamp = int(published or last_seen or 0)
        published_at = datetime.fromtimestamp(timestamp, timezone).isoformat()
        raw_content = clean_html(content)
        entries.append({
            "platform": platform,
            "published_at": published_at,
            "published_at_ms": timestamp * 1000,
            "importance": None,
            "raw_content": raw_content,
            "content_nature": None,
            "title": (title or "").strip(),
            "confidence": None,
            "feed": (feed_name or category_name or "").strip(),
            "feed_url": feed_url or "",
            "is_duplicate": is_duplicate,
            "link": link or "",
            "needs_follow_up": False,
            "needs_fulltext": platform == "公众号" and len(raw_content) < 200,
            "themes": [],
            "summary": "",
            "source": (author or feed_name or "").strip(),
            "fetched_at": end.isoformat(),
            "external_id": source_id,
            "guid": guid or "",
            "entry_id": entry_id,
        })

    counts = Counter(str(item["platform"]) for item in entries)
    payload = {
        "meta": {
            "timezone": args.timezone,
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
            "window_start_ms": start_epoch * 1000,
            "window_end_ms": end_epoch * 1000,
            "report_date": end.date().isoformat(),
            "generated_at": datetime.now(timezone).replace(microsecond=0).isoformat(),
            "counts": {"total": len(entries), "公众号": counts["公众号"], "X": counts["X"]},
            "skipped_other_platforms": skipped_other,
        },
        "entries": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
