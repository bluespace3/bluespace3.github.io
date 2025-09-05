# 笔记管理自动化工具

本目录包含自动化脚本，用于简化笔记仓库的管理和同步。

## 📋 脚本列表

### 1. manage-notes.py (推荐)
**功能**：一体化笔记管理工具，集成同步和格式化功能
**用法**：
```bash
# 执行完整的同步和格式化流程（推荐）
python manage-notes.py

# 只同步笔记（从独立仓库到主项目）
python manage-notes.py --sync

# 只格式化 Hugo 头
python manage-notes.py --format

# 强制模式（覆盖现有更改和 Hugo 头）
python manage-notes.py --all --force

# 处理指定目录
python manage-notes.py --format --target content/post/编程语言

# 试运行模式
python manage-notes.py --dry-run
```

**说明**：
- 一体化管理工具，集成所有功能
- 自动从笔记仓库同步到主项目（使用 git subtree）
- 自动为 Markdown 文件添加 Hugo Front Matter
- 递归处理多层目录结构
- 支持强制模式，覆盖现有更改
- 智能检测文件是否已有 Hugo 头
- 提取文件第一行作为标题
- 自动设置当前时间为 `date` 和 `lastmod`
- 默认分类为 `["技术"]`
- 完全支持中文文件名和路径
- 提供详细的处理进度和统计信息

### 2. sync-notes-pull.sh
**功能**：从独立笔记仓库同步到主项目
**用法**：
```bash
./sync-notes-pull.sh
```

**说明**：
- 必须在 Hugo 项目根目录运行
- 自动执行 `git subtree pull` 操作
- 将笔记仓库的最新更改拉取到主项目的 `content/post` 目录

### 3. sync-notes-push.sh
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

### 2. 日常使用（推荐方式）
**在笔记仓库中编辑：**
```bash
cd C:/Users/tian4/knowledge_bases
# 编辑文件
git add .
git commit -m "更新笔记"
```

**同步并格式化：**
```bash
cd E:/code/golang/hugo/bluespace3.github.io
python manage-notes.py --all --force
```

### 3. 传统方式
**同步到主项目：**
```bash
./sync-notes-pull.sh
```

**从主项目推送更改：**
```bash
./sync-notes-push.sh
```

## ⚠️ 注意事项

1. **运行环境**：Python 脚本需要 Python 3.x 环境
2. **权限问题**：确保脚本有执行权限（`chmod +x script.sh`）
3. **路径问题**：Windows 路径使用正斜杠 `/` 而非反斜杠 `\`
4. **Git 配置**：确保已配置 Git 用户名和邮箱

## 🐛 故障排除

### 错误：请在 Hugo 项目根目录运行此脚本
确保在包含 `hugo.toml` 文件的目录中运行脚本。

### 错误：笔记仓库目录不存在
检查路径是否正确：`C:/Users/tian4/knowledge_bases`

### 错误：检测到未提交的更改
在运行同步前，先提交所有更改：
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

1. **定期同步**：建议定期运行 `python manage-notes.py` 保持主项目更新
2. **GitHub 备份**：定期运行 `git push origin master` 备份到 GitHub
3. **分支管理**：对于重大更改，建议创建功能分支而非直接在 master 上操作
4. **推荐使用**：优先使用 `manage-notes.py` 一体化工具，功能更完整