# Hugo 笔记管理工具

这是一个用于管理和自动化 Hugo 博客笔记的 Python 脚本工具。它能够从远程知识库同步笔记、自动格式化 Front Matter、统一标题，并支持一键部署。

## 📋 脚本列表

### 1. manage-notes.py (推荐)

**功能**：一体化笔记管理工具，集成了笔记同步、格式化、标题统一、推送和网站部署的全流程功能。

**Front Matter 格式**：
脚本自动生成的标准 Front Matter 格式如下：
```yaml
---
title: '文章标题'
categories: ["分类名称"]
date: 2025-11-23T10:30:00+00:00
lastmod: 2025-11-23T10:30:00+00:00
encrypted: false
password: "123456"
---
```

**分类规则**：
- 分类名称来自 `C:\Users\tian4\knowledge_bases` 目录中的第一级文件夹名
- 例如：`C:\Users\tian4\knowledge_bases\AIGC学习笔记\langchain.md` → 分类为 `"AIGC学习笔记"`
- 如果找不到匹配的文件，默认使用 `"技术"` 作为分类

**用法**：

```bash
# 执行完整的自动化流程（推荐）
# 流程：提交知识库 -> 同步笔记 -> 格式化笔记 -> 推送笔记 -> 部署网站
python manage-notes.py

# --- 功能组合示例 ---

# 只同步笔记，不进行任何格式化
python manage-notes.py --sync-only

# 只进行格式化（包括添加 Hugo 头和统一标题）
python manage-notes.py --format-only

# 只将所有笔记的标题统一为文件名
python manage-notes.py --title-only

# 格式化后，将笔记的更改推送到远程笔记仓库
python manage-notes.py --format-only --push-notes

# 一键完成所有操作：同步 -> 格式化 -> 推送笔记 -> 部署网站
python manage-notes.py --push-notes --deploy

# 只部署网站（适用于手动修改后）
python manage-notes.py --deploy

# 强制同步模式（自动提交本地更改并强制覆盖）
python manage-notes.py --force
```

**说明**：

- 一体化管理工具，集成所有功能
- 不带参数运行时，默认执行完整自动化流程：提交知识库 → 同步 → 格式化 → 推送笔记 → 部署网站
- **新增**：每次执行前自动提交并推送本地知识库 (`C:\Users\tian4\knowledge_bases`) 到 GitHub
- 自动从笔记仓库同步到主项目（使用 git subtree）
- **新增**：智能 Front Matter 生成，自动从知识库目录结构提取分类
- **新增**：自动生成加密相关字段 (`encrypted: false`, `password: "123456"`)
- **新增**：自动将所有文章的标题统一为文件名（去除.md后缀）
- **新增**：支持将笔记子仓库的更改推送回远程
- **新增**：支持一键构建和部署整个 Hugo 网站
- 递归处理多层目录结构
- 支持强制模式，覆盖现有更改
- **增强**：智能检测文件是否已有完整 Hugo Front Matter，避免重复修改
- 提取文件第一行内容作为初始标题
- 自动设置当前时间为 `date` 和 `lastmod`
- 完全支持中文文件名和路径
- 提供详细的处理进度和统计信息

## ⚠️ 注意事项

1. **运行环境**：脚本需要 Python 3.x 环境。
2. **Git 配置**：确保已配置 Git 用户名和邮箱。
3. **知识库路径**：默认知识库路径为 `C:\Users\tian4\knowledge_bases`，如需修改请编辑脚本中的 `knowledge_base_dir` 变量。
4. **Hugo 配置**：确保在包含 `hugo.toml` 文件的 Hugo 项目根目录中运行脚本。
5. **加密笔记使用方法**：
   - 在你的 Markdown 文章中使用以下 shortcode 来包裹需要加密的内容：
     ```markdown
     {{</* encrypted password="你的密码" */>}}
     这里是需要加密的内容...
     支持 Markdown 语法、代码块、表格等。
     {{</* /encrypted */>}}
     ```
   - **重要：为了防止加密内容在列表页泄露，请务必在加密内容之前，使用 `<!--more-->` 分隔符来手动指定文章摘要的结束位置。**
     ```markdown
     ---
     title: "我的加密文章"
     ---
     这是公开的摘要内容，会显示在列表页。

     <!--more-->

     {{</* encrypted password="你的密码" */>}}
     这是不会在列表页出现的加密内容。
     {{</* /encrypted */>}}
     ```

## 🔧 配置说明

脚本中的关键配置可以在 `NotesManager` 类的 `__init__` 方法中修改：

```python
def __init__(self):
    self.hugo_project_dir = os.getcwd()
    self.notes_repo_url = "https://github.com/bluespace3/knowledge_bases.git"
    self.content_post_dir = os.path.join(self.hugo_project_dir, "content/post")
    self.knowledge_base_dir = r"C:\Users\tian4\knowledge_bases"  # 可修改此路径
```

### 可配置项
- `notes_repo_url`: 远程笔记仓库 URL
- `knowledge_base_dir`: 本地知识库目录路径
- 加密密码：在 `add_hugo_frontmatter` 方法中可修改默认密码 `"123456"`

## 🐛 故障排除

### 错误：请在 Hugo 项目根目录运行此脚本

确保在包含 `hugo.toml` 文件的目录中运行脚本。

### 错误：检测到未提交的更改

在运行同步前，先提交所有更改，或使用 `--force` 参数来自动提交：

```bash
git add .
git commit -m "提交更改"
```

### 错误：权限被拒绝

如果是在 Linux/macOS 环境下，请确保脚本有执行权限：

```bash
chmod +x your_script_name.sh
```

### 知识库推送失败

如果本地知识库推送失败（通常是因为远程有更新），脚本会继续执行后续步骤。建议手动拉取远程更新后再运行脚本。

## 🎯 最佳实践

1. **定期同步**：建议定期运行 `python manage-notes.py` 保持主项目更新。
2. **完整工作流**：直接运行 `python manage-notes.py` 即可执行完整自动化流程（提交知识库 → 同步 → 格式化 → 推送笔记 → 部署网站）。
3. **分支管理**：对于重大更改，建议创建功能分支而非直接在 `master` 或 `main` 分支上操作。
4. **模板覆盖**：为了修复主题的加密内容泄露问题，我们在 `layouts/partials/post.html` 创建了一个模板覆盖文件。请不要轻易删除它。
5. **分类管理**：在知识库中合理组织文件夹结构，以便自动生成准确的分类。
