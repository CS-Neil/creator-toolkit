# Content and curation framework

## Required report structure

1. `24 小时总览`: Three to six cross-source storylines and the overall signal.
2. `重点结论与观察清单`: Prioritized conclusions with why each matters.
3. `主题聚类`: Theme, representative signals, and judgment in a compact table.
4. `公众号文章逐条概况`: Every WeChat article, in publication order or clearly documented order.
5. `X 消息逐条概况`: Every X entry, normally reverse chronological.
6. `跨平台综合判断`: Connections, contradictions, and leading/lagging signals across platforms.
7. `接下来 24—72 小时建议跟踪`: Specific events, metrics, documents, or confirmations to watch.
8. `数据质量说明`: Counts, missing bodies, duplicates, link-only posts, paywalls, and verification limits.

The title must be `FreshRSS 最近 24 小时内容概况`. State the exact start/end timestamps, timezone, FreshRSS user, source methods, total count, and platform counts below it.

## Per-item analysis

### WeChat article

Summarize from the retrieved full body:

- Nature: reporting, policy notice, company case, market opinion, promotion, commentary, science/health, or another accurate label.
- Core: the article's main claim or event.
- Evidence: important data, examples, actors, dates, and causal logic.
- Relevance: why it matters to the daily themes.
- Caveat: promotional sourcing, unsupported causality, medical/investment risk, missing primary documents, or another limitation.

Use several bullets for substantive long-form articles. Keep official notices concise.

### X post

Use one compact line containing:

- Time, source account, and nature.
- What happened or what the author claims.
- Why it matters or what key detail is missing.
- Original link.

Do not summarize an article behind a link unless its text was retrieved. A link-only/live post must say `信息不足`.

## Curated JSON schema

Use UTF-8 JSON with this structure after analysis:

```json
{
  "meta": {
    "timezone": "Asia/Shanghai",
    "window_start": "2026-07-16T15:52:00+08:00",
    "window_end": "2026-07-17T15:52:00+08:00",
    "report_date": "2026-07-17",
    "generated_at": "2026-07-17T16:30:00+08:00"
  },
  "daily": {
    "themes": ["地缘政治", "AI与科技"],
    "highlights": ["结论一", "结论二"],
    "follow_up": ["跟踪项一", "跟踪项二"],
    "risk": "高",
    "verification": "部分核验"
  },
  "entries": [
    {
      "platform": "X",
      "published_at": "2026-07-17T15:40:00+08:00",
      "importance": 4,
      "raw_content": "Retrieved source text",
      "content_nature": "事实",
      "title": "Concise title",
      "confidence": "高",
      "feed": "X list name",
      "is_duplicate": false,
      "link": "https://x.com/example/status/123",
      "needs_follow_up": true,
      "themes": ["地缘政治"],
      "summary": "一至三句话说明发生了什么、为什么重要。",
      "source": "Reuters",
      "fetched_at": "2026-07-17T15:52:00+08:00",
      "external_id": "123"
    }
  ]
}
```

Keep every extracted entry. Preserve duplicate rows but mark `is_duplicate: true`. For unavailable content, use `content_nature: 待核实`, `confidence: 待核实`, explain the gap in `summary`, and lower importance unless the missing item itself is operationally important.

## Rating and verification rules

- Importance 5: major event with broad or immediate strategic impact.
- Importance 4: material development in a core theme or actionable watch item.
- Importance 3: relevant supporting information.
- Importance 2: narrow, promotional, repetitive, or low-context item.
- Importance 1: noise retained only for completeness.

Confidence:

- `高`: primary official material or well-supported factual reporting.
- `中`: reputable secondary reporting, sourced claims, or incomplete but plausible facts.
- `低`: weak sourcing, strong inference, promotional claims, or material context missing.
- `待核实`: explicit unverified claim, link-only post, or insufficient retrieved content.

Use `需跟踪` for material items whose confirmation, next event, market reaction, filing, court decision, or policy detail should be checked within 24–72 hours.
