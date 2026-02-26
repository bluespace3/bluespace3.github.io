# Encrypt Articles Skill

Batch encrypt articles with password protection using hugo-encryptor.

## Description

Encrypt multiple markdown articles in a directory using AES-256 encryption. Each article will require a password to view the protected content.

## Usage

```bash
# Linux/macOS
bash tools/batch-encrypt.sh <directory> <password>

# Windows
tools\batch-encrypt.bat <directory> <password>
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| directory | Directory containing markdown files | `content/post/工作` |
| password | Password for encryption | `mySecretPassword123` |

## What It Does

1. ✅ Finds all `.md` files in the specified directory (recursive)
2. ✅ Wraps content in `{{% hugo-encryptor "password" %}}` shortcode
3. ✅ Adds `<!--more-->` tag if not present
4. ✅ Preserves front matter
5. ✅ Skips already encrypted files

## Example

```bash
# Encrypt all articles in the 工作 directory
bash tools/batch-encrypt.sh content/post/工作 tian45996

# Output:
# ========================================
#        批量加密文章脚本
# ========================================
# 目标目录: content/post/工作
# 加密密码: tian45996
# [1] 处理: 0909工作.md
#   ✅ 加密成功
# [2] 处理: 1017.md
#   ✅ 加密成功
# ...
# ========================================
#        处理完成
# ========================================
# 总数: 9
# 成功: 9
# 失败: 0
```

## Encrypt Single File

```bash
python tools/encrypt_file.py "content/post/secret-article.md" "password123"
```

## Article Format After Encryption

```markdown
---
title: 'Article Title'
categories: ["工作"]
date: 2026-01-21T11:25:24+08:00
lastmod: 2026-01-21T11:25:24+08:00
---

本文《Article Title》包含加密内容，请输入密码查看。

<!--more-->

{{% hugo-encryptor "password123" %}}

# 原始内容
这里的内容需要密码才能查看。

{{% /hugo-encryptor %}}
```

## Requirements

- Python 3
- No additional packages required

## Notes

- Always test with a small subset first
- Use strong passwords
- Remember the password - it cannot be recovered
- Decrypt.js must be present in static/ directory
- Encryption only works during deployment, not preview

## Related Skills

- `deploy.md` - Deploy encrypted articles
- `preview.md` - Preview before encryption (content visible)
