# Hugo 博客管理

Hugo 博客项目的日常管理和维护工作。

## 项目结构

```
bluespace3.github.io/
├── content/          # 博客文章源文件
│   ├── post/        # 公开文章
│   └── archives/    # 加密文章
├── themes/          # Hugo 主题
├── static/          # 静态资源
├── layouts/         # 自定义布局
├── tools/           # 工具脚本
├── public/          # 生成的静态网站（用于本地预览）
├── hugo.toml        # Hugo 配置文件
└── .github/workflows/ # GitHub Actions 自动部署配置
```

## 部署方式

- **本地开发**：修改内容 → 生成到 `public/` → 本地预览
- **自动部署**：推送到 `main` 分支 → GitHub Actions 自动构建 → 发布到 `gh-pages` 分支

## 日常使用流程

### 1. 创建新文章

```bash
# 创建文章
hugo new post/我的文章.md

# 编辑文章
# 使用编辑器编辑 content/post/我的文章.md
```

### 2. 本地预览

```bash
# Windows
preview.bat

# Linux/macOS
./preview.sh

# 或直接运行
hugo server -D
```

访问 http://localhost:1313

### 3. 发布文章

```bash
# Windows - 一键发布
deploy.bat

# Linux/macOS - 一键发布
./deploy.sh
```

## 文章加密

### 使用 hugo-encryptor 加密文章

1. **在文章中添加加密标记**：

```markdown
---
title: "文章标题"
---

这是公开内容。

<!--more-->  <!-- 必须有 -->

{{% hugo-encryptor "你的密码" %}}

这里是加密内容...

{{% /hugo-encryptor %}}
```

2. **生成并加密**：

```bash
hugo --cleanDestinationDir
python tools/hugo_encryptor/hugo-encryptor.py
```

### 批量加密文章

```bash
# Windows - 加密整个目录
tools\batch-encrypt.bat content\archives 密码

# Linux/macOS
./tools/batch-encrypt.sh content/archives 密码
```

## 自动分类

根据文章所在目录自动添加分类：

```bash
# 预览会添加什么分类
tools\add-categories.bat content/post --dry-run

# 执行分类添加
tools\add-categories.bat content/post
```

## 主题配置

- **主题**：PaperMod
- **配置文件**：`hugo.toml`
- **自定义样式**：`static/css/`、`static/js/`

## 工具脚本

所有工具位于 `tools/` 目录：

- `batch-encrypt.*` - 批量加密文章
- `add_categories.*` - 自动添加分类
- `encrypt_file.py` - 单文件加密
- `sync_notes_from_github.py` - 从 GitHub 笔记仓库同步笔记到博客

## Skill: 同步笔记到博客 (sync-notes)

### 功能
从 GitHub 笔记仓库同步笔记到 Hugo 博客，使用 GitHub API 获取文件真实时间并自动生成符合 Hugo 格式的 Front Matter。

### 核心特性
- ✅ 使用 GitHub API 获取文件真实时间（非本地 Git 时间）
- ✅ 自动从文件名提取 title
- ✅ 自动从父目录提取 categories
- ✅ 支持覆盖模式（强制更新已有 frontmatter）
- ✅ 时间自动转换为东八区（+08:00）
- ✅ 批量处理，支持速率限制保护

### 配置要求

#### 1. 获取 GitHub Token（只需一次）

**步骤**：

1. **访问 GitHub Token 创建页面**：
   - 直接访问：https://github.com/settings/tokens
   - 或：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **生成新的 Token**：
   - 点击 "Generate new token" → "Generate new token (classic)"

3. **配置 Token**：
   - **Note**: 输入描述，如 "Hugo 博客同步工具"
   - **Expiration**: 选择过期时间（建议 90 days 或 No expiration）
   - **勾选权限**: ✅ `repo` (Full control of private repositories)

4. **生成并保存**：
   - 点击 "Generate token"
   - **重要**: 立即复制 Token（只会显示一次！）
   - Token 格式：`ghp_xxxxxxxxxxxxxxxxxxxx`

#### 2. 配置 Token（三种方式任选其一）

**方式一：使用 .env 文件（推荐，最简单）**

```bash
# 1. 复制模板文件
cp .env.example .env

# 2. 编辑 .env 文件，将 your_token_here 替换为你的 token
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 3. 完成！脚本会自动读取 .env 文件
```

**方式二：临时环境变量（重启终端后失效）**

```bash
# Linux/macOS
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxx'

# Windows PowerShell
$env:GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxx'

# Windows CMD
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**方式三：永久环境变量（推荐给高级用户）**

```bash
# Linux/macOS - 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc

# Windows - 设置系统环境变量
# 控制面板 → 系统 → 高级系统设置 → 环境变量 → 新建
# 变量名：GITHUB_TOKEN
# 变量值：ghp_xxxxxxxxxxxxxxxxxxxx
```

#### 3. 安装依赖

```bash
pip install -r tools/requirements.txt
```

需要的依赖：
- `requests` - HTTP 请求库
- `pyyaml` - YAML 配置文件解析

#### 4. 配置文件（可选）

编辑 `tools/sync_notes_config.yaml`（通常使用默认配置即可）：

```yaml
github:
  token: '${GITHUB_TOKEN}'  # 从 .env 或环境变量读取
  owner: 'bluespace3'       # 仓库所有者
  repo: 'knowledge_bases'   # 笔记仓库名
  branch: 'main'            # 分支名

hugo:
  content_dir: 'content/post'
  timezone: 'Asia/Shanghai'

frontmatter:
  overwrite: true           # 是否覆盖已有 frontmatter
  default_category: '技术'
```

### 使用方法

```bash
# 预览模式（不实际修改）
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 处理单个文件
python tools/sync_notes_from_github.py --file "content/post/技术/python.md"

# 批量处理目录
python tools/sync_notes_from_github.py --batch content/post

# 不覆盖已有 frontmatter
python tools/sync_notes_from_github.py --batch content/post --no-overwrite
```

### Hugo Front Matter 格式

```yaml
---
title: "Python 基础"  # 来自文件名
categories: ["技术"]  # 来自父目录
date: 2025-03-15T18:30:00+08:00  # GitHub 创建时间
lastmod: 2025-12-26T19:30:00+08:00  # GitHub 更新时间
encrypted: false
password: "123456"
---
```

### 与 manage-notes.py 的区别

| 特性 | manage-notes.py | sync_notes_from_github.py |
|------|-----------------|--------------------------|
| 时间来源 | 本地 git log | GitHub API |
| 时间准确性 | ❌ 所有文章时间相同（同步日期） | ✅ 真实创建时间 |
| 需求 | 需要本地知识库 | 只需 GitHub 访问 |
| 速率限制 | 无 | 有（GitHub API 限制） |

### 注意事项

1. **GitHub API 速率限制**：
   - 无认证：60 次/小时
   - 有认证：5000 次/小时
   - 批量处理时自动添加延迟避免超限

2. **首次使用建议**：
   ```bash
   # 先用 --dry-run 预览
   python tools/sync_notes_from_github.py --batch content/post --dry-run

   # 确认无误后再执行
   python tools/sync_notes_from_github.py --batch content/post
   ```

3. **验证结果**：
   ```bash
   # 本地预览
   hugo server -D

   # 访问归档页检查时间分布
   # http://localhost:1313/archives/
   ```

## GitHub Actions 自动部署

推送代码到 `main` 分支后，自动：

1. 构建 Hugo 网站
2. 部署到 `gh-pages` 分支
3. GitHub Pages 自动更新

## 注意事项

1. **加密脚本**：每次生成网站后需要运行 `python tools/hugo_encryptor/hugo-encryptor.py`
2. **public 目录**：用于本地预览，正式发布由 GitHub Actions 处理
3. **主题更新**：PaperMod 主题是子模块，更新使用 `git submodule update --remote --merge`
4. **Python 版本**：需要 Python 3.x 运行加密脚本

## 相关文档

- [快速开始](./快速开始.md)
- [博客搭建指南](./博客搭建指南.md)
- [工具箱](./工具箱.md)
