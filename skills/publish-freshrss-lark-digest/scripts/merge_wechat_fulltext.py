#!/usr/bin/env python3
"""Merge WeChat full-text results into a FreshRSS extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fulltext", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    results = json.loads(args.fulltext.read_text(encoding="utf-8"))
    by_id = {str(item.get("id", "")): item for item in results}
    success = 0
    failed: list[str] = []
    for entry in payload.get("entries", []):
        if entry.get("platform") != "公众号":
            continue
        source_id = str(entry.get("external_id", ""))
        result = by_id.get(source_id)
        if not result or result.get("error") or not result.get("text"):
            entry["needs_fulltext"] = True
            failed.append(source_id)
            continue
        entry["raw_content"] = result["text"].strip()
        entry["needs_fulltext"] = False
        if result.get("title"):
            entry["title"] = result["title"].strip()
        if result.get("source"):
            entry["source"] = result["source"].strip()
        success += 1

    payload.setdefault("meta", {})["wechat_fulltext"] = {
        "success": success,
        "failed": len(failed),
        "failed_external_ids": failed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["meta"]["wechat_fulltext"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
