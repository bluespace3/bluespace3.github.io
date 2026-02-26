# Blog Deploy Skill

Deploy blog to GitHub Pages with automatic build and encryption.

## Description

Automatically builds the Hugo site, encrypts protected articles, commits changes to Git, and pushes to GitHub for deployment.

## Usage

```bash
# Linux/macOS
./deploy.sh

# Windows
deploy.bat
```

## What It Does

1. ✅ Checks and copies `decrypt.js` to static directory
2. ✅ Generates the website with Hugo (`hugo --cleanDestinationDir`)
3. ✅ Encrypts articles using `hugo-encryptor.py`
4. ✅ Commits all changes to Git with timestamp
5. ✅ Pushes to GitHub main branch
6. ✅ GitHub Actions automatically deploys to gh-pages branch

## Requirements

- Hugo (Extended) installed
- Python 3 with `pycryptodome`, `beautifulsoup4`, `lxml` packages
- Git configured with GitHub access

## Example

```bash
# Make changes to your blog
# Edit content/post/my-article.md

# Deploy with one command
./deploy.sh

# Output:
# ========================================
#        博客自动化部署脚本
# ========================================
# [0/5] 正在检查加密文件...
# ✅ decrypt.js 已存在
# [1/5] 正在生成网站...
# ✅ 网站生成成功
# [2/5] 正在加密文章...
# ✅ 文章加密成功
# [3/5] 正在提交到 Git...
# ✅ 提交成功
# [4/5] 正在推送到 GitHub...
# ✅ 推送成功
# ========================================
#        🎉 部署完成！
# ========================================
# 博客地址: https://bluespace3.github.io/
```

## Notes

- If no changes detected, deployment will be skipped
- Commit message format: `自动部署: YYYY-MM-DD HH:MM:SS`
- Blog URL: https://bluespace3.github.io/

## Related Skills

- `preview.md` - Local preview before deployment
- `encrypt-articles.md` - Encrypt articles manually
