#!/usr/bin/env python3
"""Validate curated digest data and build lark-cli Base batch-create payloads."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TOPICS = {"地缘政治", "AI与科技", "金融市场", "产业公司", "政策监管", "社会文化", "消费品牌", "气候灾害"}
NATURES = {"事实", "观点", "预测", "转推", "推广", "待核实"}
CONFIDENCE = {"高", "中", "低", "待核实"}
RISKS = {"低", "中", "高", "紧急"}
VERIFICATION = {"未核验", "部分核验", "已核验"}
PLATFORMS = {"公众号", "X"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def local_datetime(value: str, timezone: str) -> str:
    parsed = datetime.fromisoformat(value)
    zone = ZoneInfo(timezone)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone).strftime("%Y-%m-%d %H:%M:%S")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--document-url", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--daily-record-id")
    parser.add_argument("--daily-only", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    report = args.report.read_text(encoding="utf-8")
    meta = data.get("meta", {})
    daily = data.get("daily", {})
    entries = data.get("entries", [])
    timezone = meta.get("timezone", "Asia/Shanghai")

    for key in ("window_start", "window_end", "report_date", "generated_at"):
        require(bool(meta.get(key)), f"meta.{key} is required")
    require(entries, "entries must not be empty")
    require(args.document_url.startswith("https://"), "--document-url must be an https URL")
    require(set(daily.get("themes", [])) <= TOPICS, "daily.themes contains an invalid topic")
    require(daily.get("risk") in RISKS, "daily.risk is invalid")
    require(daily.get("verification") in VERIFICATION, "daily.verification is invalid")

    external_ids: set[tuple[str, str]] = set()
    for index, item in enumerate(entries, 1):
        prefix = f"entries[{index}]"
        require(item.get("platform") in PLATFORMS, f"{prefix}.platform is invalid")
        require(item.get("content_nature") in NATURES, f"{prefix}.content_nature is invalid")
        require(item.get("confidence") in CONFIDENCE, f"{prefix}.confidence is invalid")
        require(set(item.get("themes", [])) <= TOPICS, f"{prefix}.themes contains an invalid topic")
        require(isinstance(item.get("importance"), int) and 1 <= item["importance"] <= 5, f"{prefix}.importance must be 1..5")
        for key in ("published_at", "title", "link", "summary", "external_id"):
            require(bool(item.get(key)), f"{prefix}.{key} is required")
        require(item["link"].startswith("https://"), f"{prefix}.link must be https")
        duplicate_key = (item["platform"], str(item["external_id"]))
        require(duplicate_key not in external_ids or bool(item.get("is_duplicate")), f"duplicate external ID not marked: {duplicate_key}")
        external_ids.add(duplicate_key)

    counts = Counter(item["platform"] for item in entries)
    highlights = daily.get("highlights", [])
    follow_up = daily.get("follow_up", [])
    require(3 <= len(highlights) <= 7, "daily.highlights must contain 3..7 items")

    daily_fields = [
        "日报标题", "生成时间", "发布状态", "总消息数", "核心主题", "风险等级",
        "发布渠道", "汇总日期", "飞书文档链接", "数据窗口结束", "数据窗口开始",
        "公众号数", "日报正文", "核验状态", "今日重点", "X消息数", "后续跟踪",
    ]
    daily_row = [
        f"{meta['report_date']} 每日资讯汇总",
        local_datetime(meta["generated_at"], timezone),
        "已发布",
        len(entries),
        daily.get("themes", []),
        daily["risk"],
        ["飞书文档"],
        f"{meta['report_date']} 00:00:00",
        args.document_url,
        local_datetime(meta["window_end"], timezone),
        local_datetime(meta["window_start"], timezone),
        counts["公众号"],
        report,
        daily["verification"],
        "\n".join(f"{i}. {text}" for i, text in enumerate(highlights, 1)),
        counts["X"],
        "\n".join(f"{i}. {text}" for i, text in enumerate(follow_up, 1)),
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "daily.json", {"fields": daily_fields, "rows": [daily_row]})

    if args.daily_only:
        print(json.dumps({"daily_rows": 1, "detail_rows": 0, "counts": counts}, ensure_ascii=False, default=dict))
        return
    require(bool(args.daily_record_id), "--daily-record-id is required unless --daily-only is used")
    require(args.daily_record_id.startswith("rec"), "--daily-record-id must start with rec")

    detail_fields = [
        "发布时间", "重要度", "原始内容", "所属日报", "内容性质", "资讯标题", "可信度",
        "Feed或列表", "是否重复", "平台", "原文链接", "需跟踪", "主题", "内容概况",
        "来源账号", "抓取时间", "外部ID",
    ]
    rows = []
    for item in entries:
        rows.append([
            local_datetime(item["published_at"], timezone),
            item["importance"],
            item.get("raw_content", ""),
            [{"id": args.daily_record_id}],
            item["content_nature"],
            item["title"],
            item["confidence"],
            item.get("feed", ""),
            bool(item.get("is_duplicate")),
            item["platform"],
            item["link"],
            bool(item.get("needs_follow_up")),
            item.get("themes", []),
            item["summary"],
            item.get("source", ""),
            local_datetime(item.get("fetched_at", meta["window_end"]), timezone),
            str(item["external_id"]),
        ])

    for batch_index, offset in enumerate(range(0, len(rows), 200), 1):
        write_json(
            args.output_dir / f"details-{batch_index:03d}.json",
            {"fields": detail_fields, "rows": rows[offset:offset + 200]},
        )
    print(json.dumps({"daily_rows": 1, "detail_rows": len(rows), "batches": (len(rows) + 199) // 200, "counts": dict(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
