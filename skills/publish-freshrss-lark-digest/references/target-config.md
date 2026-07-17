# Target configuration

## Server and services

Resolve deployment-specific values at runtime. Prefer task-specific environment variables or a local configuration file excluded from version control.

| Setting | Suggested variable | Example |
|---|---|---|
| SSH host | `FRESHRSS_SSH_HOST` | `rss.example.com` |
| SSH user | `FRESHRSS_SSH_USER` | `rss-operator` |
| Timezone | `FRESHRSS_TIMEZONE` | `Asia/Shanghai` |
| FreshRSS container | `FRESHRSS_CONTAINER` | `freshrss` |
| FreshRSS user | `FRESHRSS_USER` | `reader` |
| FreshRSS SQLite path | `FRESHRSS_DB_PATH` | `/var/www/FreshRSS/data/users/reader/db.sqlite` |
| WeWe RSS container | `WEWE_RSS_CONTAINER` | `wewe-rss` |
| WeWe RSS endpoint | `WEWE_RSS_ENDPOINT` | `http://127.0.0.1:4000` |
| FreshRSS endpoint | `FRESHRSS_ENDPOINT` | `http://127.0.0.1:8081` |

Treat the SSH password, X `auth_token`, Feishu credentials, and session cookies as runtime secrets. Never store them in this Skill, payload files, shell history, reports, or messages. Prefer SSH keys and existing authenticated `lark-cli` state.

## Feishu Base

Resolve these deployment-specific values at runtime:

- Base URL: `LARK_BASE_URL`
- Base token: `LARK_BASE_TOKEN`
- Daily table ID: `LARK_DAILY_TABLE_ID`
- Detail table ID: `LARK_DETAIL_TABLE_ID`

Always run `base +field-list` before writes because users may change field names or options.

## Daily table writable fields

| Field | Value shape |
|---|---|
| 日报标题 | `YYYY-MM-DD 每日资讯汇总` |
| 生成时间 | Local datetime |
| 发布状态 | `待抓取` / `生成中` / `待审核` / `已发布` / `失败` |
| 总消息数 | Integer |
| 核心主题 | Multi-select from the topic list below |
| 关联资讯明细 | Reverse link; normally populated through detail rows |
| 风险等级 | `低` / `中` / `高` / `紧急` |
| 发布渠道 | Multi-select: normally `飞书文档` |
| 汇总日期 | Local date |
| 飞书文档链接 | Verified document URL |
| 数据窗口结束 | Local datetime |
| 数据窗口开始 | Local datetime |
| 公众号数 | Integer |
| 日报正文 | Full Markdown report |
| 核验状态 | `未核验` / `部分核验` / `已核验` |
| 今日重点 | Three to seven conclusions |
| X消息数 | Integer |
| 后续跟踪 | Next 24–72 hour watch list |

Do not write system fields `创建时间` or `更新时间`.

## Detail table writable fields

| Field | Value shape |
|---|---|
| 发布时间 | Original publication datetime |
| 重要度 | Integer rating 1–5 |
| 原始内容 | RSS text or cleaned WeChat body |
| 所属日报 | `[{'id':'rec...'}]` using valid JSON double quotes |
| 内容性质 | `事实` / `观点` / `预测` / `转推` / `推广` / `待核实` |
| 资讯标题 | Text |
| 可信度 | `高` / `中` / `低` / `待核实` |
| Feed或列表 | FreshRSS feed name |
| 是否重复 | Boolean |
| 平台 | `公众号` / `X` |
| 原文链接 | Original URL |
| 需跟踪 | Boolean |
| 主题 | Multi-select from the topic list below |
| 内容概况 | One to three concise sentences |
| 来源账号 | Publisher or X account |
| 抓取时间 | Window extraction datetime |
| 外部ID | X status ID or WeChat article ID |

Do not write system field `创建时间`.

## Topic options

- `地缘政治`
- `AI与科技`
- `金融市场`
- `产业公司`
- `政策监管`
- `社会文化`
- `消费品牌`
- `气候灾害`

Assign topics semantically. Do not use naive substring rules such as matching `ai` inside unrelated English words.

## Safe write order

1. Verify fields and duplicate state.
2. Create and verify the Feishu document.
3. Create one daily record and capture its record ID.
4. Create detail rows linked to that ID in batches of at most 200.
5. Read back counts and links.
6. Clean exact temporary files.
