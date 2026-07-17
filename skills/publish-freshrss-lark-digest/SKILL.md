---
name: publish-freshrss-lark-digest
description: Fetch the latest 24 hours of FreshRSS entries, supplement full WeChat article text through WeWe RSS, summarize WeChat articles and X posts, publish one daily Feishu/Lark document, and write linked daily/detail records into the configured Feishu Base. Use when asked to generate, refresh, upload, publish, or verify the FreshRSS daily intelligence digest or the FreshRSS-to-Feishu workflow.
---

# Publish FreshRSS Lark Digest

Produce one verified daily digest from the configured FreshRSS server and publish it to Feishu without duplicating records or persisting secrets.

## Required companion skills

Use `lark-doc` to create and verify the daily document, `lark-base` to inspect and write Base records, and `lark-shared` if Feishu authorization is missing. Read their current instructions before issuing writes; do not rely on stale CLI syntax from this skill.

## Read first

- Read [references/target-config.md](references/target-config.md) for server paths, Base IDs, field mappings, and secret-handling rules.
- Read [references/content-framework.md](references/content-framework.md) before summarizing or assigning labels.

## Workflow

### 1. Set a deterministic window

Use `Asia/Shanghai`. Record one window end timestamp at the start, then derive the start as exactly 24 hours earlier. Reuse these values for extraction, the report, Base fields, and verification. Do not substitute calendar-day boundaries unless the user asks.

### 2. Preflight Feishu and duplicate state

Check Feishu authorization and list the two target tables' fields. Query the daily table for `YYYY-MM-DD 每日资讯汇总` and the detail table for existing `外部ID` values in the window.

- If the daily record already exists, do not create another one. Report it and ask before replacing or materially updating published content.
- Never delete existing records to make a rerun convenient.
- Never guess linked-record IDs or select-option values.

### 3. Copy and extract FreshRSS data

Connect with SSH using a runtime credential or existing key. Never place the password in a command, file, log, Skill, or final response.

Copy the configured FreshRSS SQLite database to a narrowly named remote temporary file, transfer it locally, then run:

```bash
python3 scripts/extract_freshrss.py \
  --db /path/to/freshrss.sqlite \
  --end 2026-07-17T15:52:00+08:00 \
  --hours 24 \
  --output /tmp/freshrss-24h.json
```

Inspect the emitted counts and sample records. The extractor includes only `公众号` and `X`; it flags duplicate external IDs and WeChat entries that need full text.

### 4. Supplement WeChat full text

Copy `scripts/fetch_wechat_fulltext.js` and the extracted JSON into the `wewe-rss` container. Run the JavaScript inside that container so its existing `got` and `cheerio` packages are used. Copy the result out and merge it locally:

```bash
python3 scripts/merge_wechat_fulltext.py \
  --input /tmp/freshrss-24h.json \
  --fulltext /tmp/wechat-fulltext.json \
  --output /tmp/freshrss-24h-full.json
```

Require a non-empty body for every WeChat article. Retry transient failures conservatively. If a body remains unavailable, keep the item, mark it `待核实`, and state the limitation; do not invent a summary from the title.

### 5. Summarize and curate

Apply [references/content-framework.md](references/content-framework.md). Produce:

1. A Markdown report with all eight required sections.
2. A curated JSON file matching the schema in that reference.

Base summaries only on retrieved text. Distinguish facts, source claims, opinions, forecasts, promotions, reposts, and insufficient-information items. Treat original publication time as `发布时间`; preserve the extraction time separately as `抓取时间`.

### 6. Create and verify the Feishu document

Use the current `lark-doc` create workflow to publish the Markdown report as one document titled `YYYY-MM-DD 每日资讯汇总`. Fetch the created document outline and verify the title, all eight major sections, the expected WeChat count, and the expected X count. Save the final document URL.

Do not proceed to Base writes if document creation or verification failed.

### 7. Build and write Base payloads

First generate the daily payload:

```bash
python3 scripts/build_base_payload.py \
  --input /tmp/curated.json \
  --report /tmp/report.md \
  --document-url 'https://example.feishu.cn/docx/...' \
  --output-dir /tmp/lark-payload \
  --daily-only
```

Write `/tmp/lark-payload/daily.json` with `base +record-batch-create` and capture the returned daily record ID. Then generate linked detail batches:

```bash
python3 scripts/build_base_payload.py \
  --input /tmp/curated.json \
  --report /tmp/report.md \
  --document-url 'https://example.feishu.cn/docx/...' \
  --daily-record-id recxxxxxxxx \
  --output-dir /tmp/lark-payload
```

Write every `details-*.json` batch with `base +record-batch-create`. The script caps batches at 200 rows and validates all configured select options.

### 8. Verify the published result

Use read-only Base queries to prove all of the following:

- Exactly one daily record exists for the report date.
- Its `总消息数`, `公众号数`, and `X消息数` equal the extracted counts.
- The detail count equals the report count and pagination reports `has_more: false` after reading all pages.
- Every detail row has `所属日报` linked to the created daily record.
- Platform counts match, and every row has a non-empty `外部ID`, `原文链接`, and `内容概况`.

Report any discrepancy instead of claiming success.

### 9. Clean up and hand off

Remove only the exact temporary files created by this run, locally, remotely, and inside the WeWe RSS container. Check that `freshrss`, `wewe-rss`, and relevant RSSHub services remain healthy. Never remove broad directories or use unresolved globs.

Return the Base link, document link, total count, platform counts, link-verification count, and any data-quality limitations. Do not repeat credentials or authentication tokens.
