# Categorize Articles Skill

Automatically add Hugo categories to articles based on their directory structure.

## Description

Scans markdown files and adds/updates the `categories` field in front matter based on the parent directory name.

## Usage

```bash
# Linux/macOS
bash tools/add-categories.sh <directory> [options]

# Windows
tools\add-categories.bat <directory> [options]
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| directory | Directory to scan for markdown files | `content/post` |
| --dry-run | Preview changes without modifying files | (optional) |
| --verbose | Show detailed output | (optional) |

## What It Does

1. ✅ Recursively finds all `.md` files in directory
2. ✅ Extracts category from parent directory name
3. ✅ Adds or updates `categories` field in front matter
4. ✅ Preserves existing front matter fields
5. ✅ Creates backup before modification

## Example

```bash
# Preview what will be changed (recommended first step)
bash tools/add-categories.sh content/post --dry-run --verbose

# Output:
# 扫描目录: content/post
# [预览模式] 不会修改任何文件
# [DRY RUN] content/post/AIGC学习笔记/mcp-intro.md
#   分类: ["AIGC学习笔记"]
# [DRY RUN] content/post/工作/事项推进.md
#   分类: ["工作"]

# Apply changes
bash tools/add-categories.sh content/post

# Output:
# [1/15] content/post/AIGC学习笔记/mcp-intro.md
#   ✅ 添加分类: ["AIGC学习笔记"]
# [2/15] content/post/工作/事项推进.md
#   ✅ 添加分类: ["工作"]
# ...
```

## Front Matter Example

**Before:**
```yaml
---
title: "我的文章"
date: 2026-01-21
---
```

**After:**
```yaml
---
title: "我的文章"
date: 2026-01-21
categories: ["工作"]
---
```

## Requirements

- Python 3
- No additional packages required

## Notes

- Use `--dry-run` first to preview changes
- Backup files created with `.bak` extension
- Existing categories are preserved
- Multiple categories: Use directory name as primary category

## Related Skills

- `deploy.md` - Deploy after categorizing
- `sync-notes.md` - Sync notes from GitHub with categories
