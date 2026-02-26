# Sync Notes Skill

Synchronize notes from GitHub repository to blog with real timestamps.

## Description

Fetches notes from a GitHub repository, retrieves real creation/update times via GitHub API, and syncs them to the blog with proper Hugo front matter.

## Usage

```bash
# Preview mode (recommended first)
python tools/sync_notes_from_github.py --batch content/post --dry-run

# Batch sync all articles
python tools/sync_notes_from_github.py --batch content/post

# Sync single file
python tools/sync_notes_from_github.py --file "content/post/my-article.md"
```

## Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| --batch | Process directory of articles | Yes* |
| --file | Process single file | Yes* |
| --dry-run | Preview changes without modifying | No |
| --verbose | Show detailed output | No |
| --config | Custom config file path | No |

*Either `--batch` or `--file` must be specified

## Setup

### 1. Quick Setup (Recommended)

Use the interactive setup script:

```bash
python tools/setup-token-simple.py
```

This script will:
- Guide you through creating a GitHub Token
- Automatically create `.env` file
- Verify the token format

### 2. Install Dependencies

```bash
cd tools
pip install -r requirements.txt
```

### 3. Manual Token Setup (Alternative)

```bash
# Temporary (current session)
export GITHUB_TOKEN='your_token_here'

# Permanent (add to ~/.bashrc)
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**Get Token:** https://github.com/settings/tokens
- Scope: `repo` (Full control of private repositories)

### 3. Configure (Optional)

Edit `tools/sync_notes_config.yaml`:

```yaml
github:
  token: '${GITHUB_TOKEN}'
  owner: 'bluespace3'
  repo: 'note-gen-sync'
  branch: 'main'

hugo:
  content_dir: 'content/post'
  timezone: 'Asia/Shanghai'

frontmatter:
  overwrite: true
  default_category: '技术'
```

## What It Does

1. ✅ Fetches file metadata from GitHub API
2. ✅ Gets real `created_at` and `updated_at` timestamps
3. ✅ Adds/updates Hugo front matter with correct dates
4. ✅ Extracts title from filename or content
5. ✅ Derives category from file path

## Example

```bash
# Preview changes
python tools/sync_notes_from_github.py --batch content/post --dry-run

# Output:
# =========================================
#        笔记同步工具 (预览模式)
# =========================================
# 配置:
#   仓库: bluespace3/note-gen-sync
#   目标目录: content/post
#   时区: Asia/Shanghai
# =========================================
# [1/50] content/post/AIGC学习笔记/mcp-intro.md
#   标题: mcp-intro
#   分类: ["AIGC学习笔记"]
#   创建时间: 2025-01-15 10:30:00
#   更新时间: 2025-02-20 15:45:00
#   ✅ 将添加 Front Matter
# ...

# Apply changes
python tools/sync_notes_from_github.py --batch content/post

# Output:
# [1/50] content/post/AIGC学习笔记/mcp-intro.md
#   ✅ Front Matter 已更新
# ...
# =========================================
# 同步完成
# 总数: 50 | 成功: 48 | 跳过: 2 | 失败: 0
```

## Front Matter Example

```yaml
---
title: 'MCP Intro'
categories: ["AIGC学习笔记"]
date: 2025-01-15T10:30:00+08:00
lastmod: 2025-02-20T15:45:00+08:00
---
```

## Requirements

- Python 3.7+
- Packages: `requests` (see `tools/requirements.txt`)
- GitHub Personal Access Token with `repo` scope
- Internet connection for GitHub API

## Notes

- Use `--dry-run` first to preview changes
- Real timestamps from GitHub, not local git log
- Rate limit: 5000 requests/hour with token
- Backup files created before modification

## Related Skills

- `categorize-articles.md` - Add categories based on directory
- `deploy.md` - Deploy after syncing notes
