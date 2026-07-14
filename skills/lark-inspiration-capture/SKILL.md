---
name: lark-inspiration-capture
version: 1.0.0
description: "灵感入库：将用户提供的内容（本地 Markdown 文件、飞书文档链接、或直接粘贴的文字）总结提炼后，上传到飞书「个人成长灵感库」Base。当用户需要保存灵感、摘录笔记、入库内容、记录想法到个人成长库时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  skills:
    - lark-base
    - lark-doc
    - lark-shared
---

# 灵感入库

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 确认认证状态。

将用户提供的内容智能总结后，写入飞书「个人成长灵感库」的「灵感笔记」表。

## 目标 Base

| 属性 | 值 |
|------|-----|
| Base Token | `RNOGbzWXIa75ATs05VccDOeNnLg` |
| Base URL | `https://jcnw6e2ixp8h.feishu.cn/base/RNOGbzWXIa75ATs05VccDOeNnLg` |
| 目标表 | `灵感笔记` (table_id: `tblmBquW2s7JV2Bb`) |

## 工作流

### 第一步：获取内容

根据用户输入类型获取原始内容：

| 输入类型 | 获取方式 |
|---------|---------|
| 本地 `.md` 文件 | 直接 `Read` 读取文件内容 |
| 飞书文档链接 (`/docx/` 或 `/wiki/`) | 切到 `lark-doc` skill，用 `docs +fetch` 读取文档内容 |
| 飞书视频链接 | 切到 `lark-doc` skill 读取视频文稿 |
| 直接粘贴文字 | 直接使用用户提供的文字 |

### 第二步：提炼总结

基于原始内容，完成以下提炼（**所有字段必填，不可遗漏**）：

1. **标题**：提炼 15-30 字的简洁标题，概括核心主题
2. **原始内容**：保留原始内容的完整文字，不做删减
3. **我的解读**：用结构化方式总结核心要点，保持原文关键论述和案例，让未读原文的人也能理解精髓
4. **行动启发**：基于内容提炼 3-5 条具体可执行的行动建议，每条以「在...时，可以...」或动词开头的句式
5. **触动程度**：评估内容深度，1-5 分（1=泛泛之谈，5=醍醐灌顶）
6. **来源类型**：识别来源，从以下选项中选一：`书籍` / `文章` / `视频` / `播客` / `对话` / `电影` / `自悟`
7. **标签**：匹配 1-3 个最相关的标签，从以下选项中选：`心理学` / `认知偏差` / `亲密关系` / `金钱观` / `成长思维` / `情绪管理` / `习惯养成` / `审美力` / `养生` / `社交智慧`
8. **分类**：从以下选项中选一：`情感认知` / `经典语录` / `思维方式` / `人生感悟` / `审美品味` / `效率习惯`

### 第三步：写入 Base

先读取 [`../lark-base/references/lark-base-cell-value.md`](../lark-base/references/lark-base-cell-value.md) 和 [`../lark-base/references/lark-base-record-upsert.md`](../lark-base/references/lark-base-record-upsert.md)，确认 CellValue 格式后，构造 JSON 写入。

```bash
# 将 JSON 写入临时文件（避免 shell 转义问题），然后执行：
lark-cli base +record-upsert \
  --base-token RNOGbzWXIa75ATs05VccDOeNnLg \
  --table-id tblmBquW2s7JV2Bb \
  --as user \
  --json @temp_inspiration.json
```

JSON 结构：

```json
{
    "标题": "<提炼的标题>",
    "原始内容": "<完整原始内容>",
    "记录日期": "<YYYY-MM-DD>",
    "触动程度": <1-5>,
    "我的解读": "<结构化总结>",
    "来源类型": "<来源>",
    "来源链接": "<原始链接，没有则为空字符串>",
    "行动启发": "<3-5条行动建议>",
    "状态": "待消化",
    "标签": ["<标签1>"],
    "分类": "<分类>"
}
```

### 第四步：验证与清理

1. 检查返回结果 `"created": true`，确认写入成功
2. 特别检查 `行动启发` 字段是否已写入，如遗漏则用 `--record-id` 补更新
3. 删除临时 JSON 文件
4. 向用户报告写入结果，附上 Base 链接

## 字段速查

| 显示名 | 字段 ID | 类型 | 说明 |
|--------|---------|------|------|
| 标题 | `fld82PpuHv` | text | 简洁标题 |
| 原始内容 | `fldV6OhQxW` | text | 原始内容完整保留 |
| 记录日期 | `fld42jGuKJ` | datetime | `YYYY-MM-DD` 格式 |
| 触动程度 | `fldng8Rnh3` | number | 1-5 评分 |
| 我的解读 | `fldg8r05fI` | text | 结构化总结 |
| 来源类型 | `fldXqfbvsc` | select | 单选 |
| 来源链接 | `fldAoLymhm` | text(url) | 原始链接 |
| 行动启发 | `fldTAnWIQJ` | text | 可执行行动建议 |
| 状态 | `fldwZN3q0c` | select | 默认「待消化」 |
| 标签 | `fldzZjFG0t` | multiselect | 多选，1-3 个 |
| 分类 | `fld7F0nazA` | select | 单选 |
| 关联兴趣 | `fldfZKqNiv` | link | 可选，关联到「兴趣探索」表 |

## 注意事项

- **所有 11 个字段必须填写**，尤其注意「行动启发」不可遗漏
- 写入成功后务必检查 `行动启发` 是否在返回中，若缺失立即补更新
- 来源链接为空时传空字符串 `""`
- 标签字段为数组，即使只选一个标签也要用数组格式 `["标签名"]`
- 内容中的特殊字符（换行、引号等）需在 JSON 中正确转义
- 临时文件用完即删