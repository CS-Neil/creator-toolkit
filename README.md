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

### douyin-viral-analyzer — 爆款文案拆解器

输入一份 markdown 文案，自动按 7 大维度 33 个字段深度拆解，同步至飞书多维表格。

- **输入**：markdown 文案文件（路径或粘贴内容）
- **输出**：结构化分析 + 飞书多维表格记录
- **触发**：`/douyin-viral-analyzer` 或说「分析这份文案」

## 目录结构

```
creator-toolkit/
├── README.md
└── skills/
    ├── photo-copywriter/
    │   └── SKILL.md
    └── douyin-viral-analyzer/
        └── SKILL.md
```

## 依赖

- [Claude Code](https://claude.ai/code)
- `lark-cli`（飞书多维表格写入）