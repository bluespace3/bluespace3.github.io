---
title: '笔记管理自动化工具'
categories: ["技术"]
date: 2025-09-05T14:47:32+00:00
lastmod: 2025-09-05T14:47:32+00:00
---

# 笔记管理自动化工具

本目录包含多个自动化脚本，用于简化笔记仓库的管理和同步。

## 📋 脚本列表

### 1. sync-notes-pull.sh
**功能**：从独立笔记仓库同步到主项目
**用法**：
```bash
./sync-notes-pull.sh
```

**说明**：
- 必须在 Hugo 项目根目录运行
- 自动执行 `git subtree pull` 操作
- 将笔记仓库的最新更改拉取到主项目的 `content/post` 目录

### 2. sync-notes-push.sh
**功能**：将主项目笔记更改推送到独立仓库
**用法**：
```bash
./sync-notes-push.sh
```

**说明**：
- 必须在 Hugo 项目根目录运行
- 自动执行 `git subtree push` 操作
- 将主项目中 `content/post` 的更改推送到独立笔记仓库
- 运行前会检查是否有未提交的更改

### 3. add-hugo-frontmatter.sh
**功能**：为 Markdown 文件自动添加 Hugo Front Matter
**用法**：
```bash
# 处理单个文件
./add-hugo-frontmatter.sh path/to/file.md

# 处理整个目录
./add-hugo-frontmatter.sh path/to/directory

# 处理当前目录下所有 .md 文件
./add-hugo-frontmatter.sh
```

**说明**：
- 自动检测文件是否已有 Hugo 头
- 提取文件第一行作为标题（去除 # 符号）
- 如果第一行为空，使用文件名作为标题
- 自动设置当前时间为 `date` 和 `lastmod`
- 默认分类为 `["技术"]`

### 4. push-to-github.sh
**功能**：将笔记仓库推送到 GitHub
**用法**：
```bash
./push-to-github.sh <repository-url>
```

**示例**：
```bash
./push-to-github.sh git@github.com:yourname/knowledge-bases.git
```

**说明**：
- 自动添加远程源 `origin`
- 自动提交未提交的更改
- 推送到 GitHub 并设置上游分支

## 🚀 完整工作流程

### 1. 首次设置
```bash
# 创建 GitHub 仓库后
./push-to-github.sh git@github.com:yourname/knowledge-bases.git
```

### 2. 日常使用
**在笔记仓库中编辑：**
```bash
cd C:/Users/tian4/knowledge_bases
# 编辑文件
git add .
git commit -m "更新笔记"
```

**同步到主项目：**
```bash
cd E:/code/golang/hugo/bluespace3.github.io
./sync-notes-pull.sh
```

**从主项目推送更改：**
```bash
./sync-notes-push.sh
```

### 3. 为新文件添加 Hugo 头
```bash
# 在笔记仓库中
cd C:/Users/tian4/knowledge_bases
./add-hugo-frontmatter.sh  # 处理所有文件
./add-hugo-frontmatter.sh 新文件.md  # 处理单个文件
```

## ⚠️ 注意事项

1. **运行环境**：所有脚本都需要在 Git Bash 或支持 bash 的环境中运行
2. **权限问题**：确保脚本有执行权限（`chmod +x script.sh`）
3. **路径问题**：Windows 路径使用正斜杠 `/` 而非反斜杠 `\`
4. **Git 配置**：确保已配置 Git 用户名和邮箱

## 🐛 故障排除

### 错误：请在 Hugo 项目根目录运行此脚本
确保在包含 `hugo.toml` 文件的目录中运行脚本。

### 错误：笔记仓库目录不存在
检查路径是否正确：`C:/Users/tian4/knowledge_bases`

### 错误：检测到未提交的更改
在运行 `sync-notes-push.sh` 前，先提交所有更改：
```bash
git add .
git commit -m "提交更改"
```

### 错误：权限被拒绝
确保脚本有执行权限：
```bash
chmod +x script.sh
```

## 🎯 最佳实践

1. **定期同步**：建议定期运行 `./sync-notes-pull.sh` 保持主项目更新
2. **Hugo 头规范**：新添加的笔记文件记得运行 `./add-hugo-frontmatter.sh`
3. **GitHub 备份**：定期运行 `git push origin master` 备份到 GitHub
4. **分支管理**：对于重大更改，建议创建功能分支而非直接在 master 上操作