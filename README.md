# creator-toolkit

提升自媒体创作效率的 Claude Code Skills 集合。

## 安装

将 `skills/` 目录下的 Skill 文件夹复制到 `~/.claude/skills/` 即可：

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

## 已有 Skills

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
    └── douyin-viral-analyzer/
        └── SKILL.md
```

## 依赖

- [Claude Code](https://claude.ai/code)
- `lark-cli`（飞书多维表格写入）