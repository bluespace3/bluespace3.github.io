# Skills Directory

本目录包含标准的 AI Skills 定义，可供 Claude Code 或其他 AI 助手使用。

## 什么是 Skills？

Skills 是标准化的任务描述文件，定义了项目中常用的自动化操作。AI 助手可以读取这些文件来理解如何执行特定任务。

## 可用 Skills

| Skill | 描述 |
|-------|------|
| [deploy.md](./deploy.md) | 部署博客到 GitHub Pages |
| [preview.md](./preview.md) | 启动本地预览服务器 |
| [encrypt-articles.md](./encrypt-articles.md) | 批量加密文章 |
| [categorize-articles.md](./categorize-articles.md) | 自动分类文章 |
| [sync-notes.md](./sync-notes.md) | 从 GitHub 同步笔记 |

## Skill 格式

每个 skill 文件包含：

1. **标题和描述** - 清晰说明技能的功能
2. **使用方法** - 详细的命令示例
3. **参数说明** - 所有命令行参数及其用途
4. **示例输出** - 预期的执行结果
5. **相关 Skills** - 关联的其他技能

## 如何使用

### 在 Claude Code 中

直接描述你想做的事情，Claude 会自动查找相关的 skill：

```
"帮我部署博客"
"预览博客"
"加密工作目录下的文章"
```

### 手动使用

参考对应的 skill 文件中的命令直接执行。

## 添加新 Skill

创建新的 skill 文件时，请遵循以下格式：

```markdown
# Skill Name

Brief description of what this skill does.

## Description

Detailed description of the skill's purpose and functionality.

## Usage

```bash
command example
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| name | Description | example |

## What It Does

1. ✅ Step 1
2. ✅ Step 2
3. ✅ Step 3

## Example

```bash
# Command example with expected output
```

## Requirements

- Requirement 1
- Requirement 2

## Notes

Additional notes, tips, or warnings.

## Related Skills

- [other-skill.md](./other-skill.md) - Description
```

## 相关文档

- [../README.md](../README.md) - 项目主文档
- [../GUIDES.md](../GUIDES.md) - 详细使用指南
- [../SKILLS.md](../SKILLS.md) - AI 友好的项目指南
