# creator-toolkit

提升自媒体创作效率的 Claude Code Skills 集合。

## 安装

将 `skills/` 目录下的 Skill 文件夹复制到 `~/.claude/skills/` 即可：

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

## 已有 Skills

### photo-copywriter — 摄影双平台文案生成器

一组照片 + 基本信息 → 小红书 4 种风格 + 抖音 3 种风格文案。

| 小红书 | 抖音 |
|--------|------|
| 情绪型（氛围感、留白） | 情绪氛围型（画面感、节奏感） |
| 审美型（配色/构图拆解） | 互动共鸣型（共鸣问题、互动钩子） |
| 故事型（娓娓道来、有温度） | 极简金句型（有态度、留白） |
| 电影感/金句型（台词感、逼格高） | |

- **输入**：一组照片 + 拍摄地点/设备/时间/人物/情绪
- **输出**：7 条可直接发布的文案（标题 + 正文 + 标签 + 封面文字）
- **触发**：`/photo-copywriter` 或说「给照片配文案」

### lark-inspiration-capture — 灵感入库

将用户提供的内容（本地 Markdown 文件、飞书文档链接、或直接粘贴的文字）智能总结提炼后，自动上传至飞书「个人成长灵感库」Base。

- **输入**：本地 `.md` 文件、飞书文档/视频链接、或直接粘贴的文字
- **输出**：标题、原始内容、结构化解读、行动启发、标签分类等 11 个字段，写入飞书多维表格
- **触发**：`/lark-inspiration-capture` 或说「把这个内容入库」「保存到灵感库」

### douyin-viral-analyzer — 爆款文案拆解器

输入一份 markdown 文案，自动按 7 大维度 33 个字段深度拆解，同步至飞书多维表格。

- **输入**：markdown 文案文件（路径或粘贴内容）
- **输出**：结构化分析 + 飞书多维表格记录
- **触发**：`/douyin-viral-analyzer` 或说「分析这份文案」

### deep-read — AI 时代深度阅读

将传统 6-10 小时的线性阅读压缩为约 60 分钟的四阶段结构化审问。核心理念：问题驱动 + 分层提取 + 对话内化 + 费曼输出。

- **阶段一 · 骨架拆解**：AI 输出「知识地图」—— 一句话论点 + 每章核心观点 + 必读章节标注 + 阅读优先级
- **阶段二 · 分层阅读**：核心层读原文（60%）/ 支撑层看总结（25%）/ 装饰层跳过（15%）
- **阶段三 · 对话内化**：苏格拉底式追问 → 反对者挑战 → 场景应用题，三轮检验是否真懂
- **阶段四 · 费曼输出**：讲给 12 岁小孩听，AI 指出哪里不清楚、漏了什么、哪里理解错了

- **输入**：书名 + 作者，或书籍 PDF/epub/文本
- **输出**：知识地图 + 分层阅读引导 + 内化检验 + 费曼输出评估
- **触发**：`/deep-read` 或说「读书」「阅读」「深度阅读」「想读《XXX》」
- **适用**：非虚构类（商业、社科、心理、科普等）

### publish-freshrss-lark-digest — FreshRSS 飞书日报

抓取 FreshRSS 最近 24 小时消息，为公众号文章补取全文，逐条概况公众号与 X 内容，并发布为一篇飞书日报和相互关联的多维表格记录。

- **输入**：FreshRSS SQLite、WeWe RSS 服务和飞书 Base 运行时配置
- **输出**：飞书日报文档、日报主记录、逐条资讯明细及上传校验结果
- **能力**：精确 24 小时窗口、公众号全文补抓、分类概况、外部 ID 去重、批量写入、数量与关联校验
- **触发**：`/publish-freshrss-lark-digest` 或说「把 FreshRSS 最近24小时消息生成飞书日报」
- **安全**：不在 Skill 中保存服务器密码、X Token、Cookie 或飞书凭据

## 目录结构

```
creator-toolkit/
├── README.md
└── skills/
    ├── photo-copywriter/
    │   └── SKILL.md
    ├── lark-inspiration-capture/
    │   └── SKILL.md
    ├── douyin-viral-analyzer/
    │   └── SKILL.md
    ├── deep-read/
    │   └── SKILL.md
    └── publish-freshrss-lark-digest/
        ├── SKILL.md
        ├── agents/
        ├── references/
        └── scripts/
```

## 依赖

- [Claude Code](https://claude.ai/code)
- `lark-cli`（飞书文档和多维表格写入）
- FreshRSS SQLite 数据库
- WeWe RSS（公众号全文补抓）
