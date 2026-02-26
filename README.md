# 蓝色空间号 - Hugo 博客

基于 Hugo + PaperMod 主题的个人博客，支持文章加密、自动分类和笔记同步。

## ✨ 特性

- 📝 **简洁优雅**：PaperMod 主题，极简设计
- 🔐 **文章加密**：AES-256 加密保护私密文章
- 🎨 **响应式设计**：完美适配手机和电脑
- 🌓 **深色模式**：自动切换主题
- 🚀 **一键部署**：自动构建并部署到 GitHub Pages
- 📂 **智能分类**：根据目录自动添加分类
- 🔄 **笔记同步**：从 GitHub 仓库同步笔记并获取真实时间

---

## 🚀 快速开始

### 环境要求

- **Git** - 版本控制
- **Hugo Extended** (v0.140.0+) - 静态网站生成器
- **Python 3** - 运行加密和同步脚本

### 安装依赖

```bash
# 安装 Python 依赖
pip install pycryptodome beautifulsoup4 lxml
```

### 本地预览

```bash
# 克隆项目
git clone https://github.com/bluespace3/bluespace3.github.io.git
cd bluespace3.github.io

# 启动预览
./preview.sh  # Linux/macOS
preview.bat   # Windows
```

访问 http://localhost:1313

### 发布部署

```bash
./deploy.sh  # Linux/macOS
deploy.bat   # Windows
```

---

## 📖 完整使用指南

### 1. 博客搭建

从零开始搭建，请按以下步骤操作：

#### 1.1 安装 Hugo Extended

**Windows:**
```bash
choco install hugo-extended -y
```

**macOS:**
```bash
brew install hugo
```

**Linux:**
```bash
wget https://github.com/gohugoio/hugo/releases/download/v0.140.2/hugo_extended_0.140.2_linux-amd64.tar.gz
tar -xzf hugo_extended_0.140.2_linux-amd64.tar.gz
sudo mv hugo /usr/local/bin/
```

#### 1.2 克隆主题（如需要）

```bash
git clone --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

#### 1.3 验证安装

```bash
git --version
hugo version
python --version
```

### 2. 创建和发布文章

#### 创建新文章

```bash
# 使用 Hugo 命令创建
hugo new post/我的文章.md

# 或直接创建文件
vim content/post/我的文章.md
```

#### 文章格式

```markdown
---
title: "文章标题"
date: 2026-02-26T14:30:00+08:00
lastmod: 2026-02-26T14:30:00+08:00
categories: ["技术"]
tags: ["hugo", "博客"]
---

文章摘要...

<!--more-->

文章正文...
```

#### 日常发布流程

```bash
# 1. 编辑文章
vim content/post/我的文章.md

# 2. 本地预览
./preview.sh

# 3. 一键部署
./deploy.sh
```

### 3. 文章加密

#### 手动添加加密

```markdown
---
title: "加密文章"
date: 2026-02-26
---

公开内容...

<!--more-->

{{% hugo-encryptor "密码123" %}}

加密内容，需要密码才能查看。

{{% /hugo-encryptor %}}
```

#### 批量加密

```bash
# 加密整个目录
bash tools/batch-encrypt.sh content/post/工作 密码123

# 加密单个文件
python tools/encrypt_file.py "content/post/secret.md" "密码123"
```

### 4. 笔记同步

从 GitHub 仓库同步笔记并获取真实时间戳。

#### 核心特性

- ✅ 使用 GitHub API 获取文件真实时间（非本地 Git 时间）
- ✅ 自动从文件名提取 title
- ✅ 自动从父目录提取 categories
- ✅ 时间自动转换为东八区（+08:00）
- ✅ 批量处理，支持速率限制保护

#### 安装依赖

```bash
cd tools
pip install -r requirements.txt
```

#### 设置 GitHub Token

**方式一：使用 .env 文件（推荐）**

```bash
# 1. 复制模板文件
cp .env.example .env

# 2. 编辑 .env 文件
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 3. 完成！脚本会自动读取 .env 文件
```

**方式二：使用交互式脚本**

```bash
python tools/setup-token-simple.py
```

**方式三：环境变量**

```bash
# 临时设置
export GITHUB_TOKEN='your_token_here'

# 永久设置（添加到 ~/.bashrc）
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**获取 Token 步骤**：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置 Token：
   - **Note**: Hugo 博客同步工具
   - **Expiration**: 90 days 或 No expiration
   - **权限**: ✅ `repo` (Full control of private repositories)
4. 生成并复制 Token（只会显示一次）

#### 使用同步工具

```bash
# 预览模式（推荐）
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 批量同步
python tools/sync_notes_from_github.py --batch content/post

# 同步单个文件
python tools/sync_notes_from_github.py --file "content/post/my-article.md"

# 不覆盖已有 frontmatter
python tools/sync_notes_from_github.py --batch content/post --no-overwrite
```

#### Front Matter 格式

同步后的文章会自动添加以下格式的 Front Matter：

```yaml
---
title: "Python 基础"  # 来自文件名
categories: ["技术"]  # 来自父目录
date: 2025-03-15T18:30:00+08:00  # GitHub 创建时间
lastmod: 2025-12-26T19:30:00+08:00  # GitHub 更新时间
---
```

#### 注意事项

- **GitHub API 速率限制**：有认证 5000 次/小时
- **首次使用**：建议先用 `--dry-run` 预览
- **验证结果**：运行 `hugo server -D` 访问归档页检查时间

### 5. 自动分类

根据文章目录自动添加分类。

```bash
# 预览分类结果
bash tools/add-categories.sh content/post --dry-run

# 应用分类
bash tools/add-categories.sh content/post
```

---

## 🛠️ 工具箱

### 核心工具（根目录）

| 工具 | 功能 | 命令 |
|------|------|------|
| **deploy** | 一键部署到 GitHub | `./deploy.sh` |
| **preview** | 本地预览服务器 | `./preview.sh` |

### 辅助工具（tools/ 目录）

| 工具 | 功能 | 命令 |
|------|------|------|
| **batch-encrypt** | 批量加密文章 | `bash tools/batch-encrypt.sh <目录> <密码>` |
| **add-categories** | 自动添加分类 | `bash tools/add-categories.sh <目录>` |
| **sync-notes** | 同步 GitHub 笔记 | `python tools/sync_notes_from_github.py --batch <目录>` |
| **setup-token** | 快速设置 Token | `python tools/setup-token-simple.py` |
| **run-full-sync** | 交互式全量同步 | `bash tools/run-full-sync.sh` |
| **sync-and-deploy** | 服务器同步并部署 | `bash tools/sync-and-deploy.sh` |
| **deploy-to-server** | 部署到 Ubuntu 服务器 | `bash tools/deploy-to-server.sh` |

### 常见使用场景

**场景 1：写完新文章并发布**
```bash
# 1. 添加分类
bash tools/add-categories.sh content/post

# 2. 预览效果
./preview.sh

# 3. 发布
./deploy.sh
```

**场景 2：批量加密文章**
```bash
# 1. 批量加密
bash tools/batch-encrypt.sh content/post/工作 密码123

# 2. 发布
./deploy.sh
```

**场景 3：同步 GitHub 笔记**
```bash
# 1. 首次使用 - 设置 Token
python tools/setup-token-simple.py

# 2. 预览同步
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 3. 执行同步
python tools/sync_notes_from_github.py --batch content/post

# 4. 发布
./deploy.sh
```

**场景 4：交互式全量同步**
```bash
# 交互式选择预览或执行模式
bash tools/run-full-sync.sh
```

**场景 5：服务器同步并部署**
```bash
# 在服务器上同步笔记并推送到 GitHub
bash tools/sync-and-deploy.sh
```

---

## 📁 项目结构

```
.
├── content/              # 博客文章
│   └── post/            # 文章目录
├── themes/              # Hugo 主题（PaperMod）
├── static/              # 静态资源
├── layouts/             # 自定义布局
├── tools/               # 工具脚本
│   ├── batch-encrypt.*  # 批量加密
│   ├── add-categories.* # 自动分类
│   └── sync_notes_from_github.py  # 笔记同步
├── skills/              # AI Skills 定义
├── config/              # 配置文件
├── public/              # 生成的静态网站
├── hugo.toml           # Hugo 配置
├── deploy.sh           # 部署脚本
├── preview.sh          # 预览脚本
└── .github/workflows/  # GitHub Actions
```

---

## 🔄 自动部署流程

部署脚本自动完成以下操作：

1. ✅ 检查并复制 `decrypt.js`
2. ✅ 生成网站 (`hugo --cleanDestinationDir`)
3. ✅ 加密文章
4. ✅ 提交到 Git
5. ✅ 推送到 GitHub

GitHub Actions 自动构建并部署到 `gh-pages` 分支：

1. 检测到 `main` 分支的推送
2. 构建 Hugo 网站
3. 部署到 `gh-pages` 分支
4. GitHub Pages 自动更新

查看部署状态：https://github.com/bluespace3/bluespace3.github.io/actions

---

## 🔧 常用命令

```bash
# 创建新文章
hugo new post/我的文章.md

# 启动预览（包含草稿）
hugo server -D

# 生成网站
hugo --cleanDestinationDir

# 手动加密文章
python tools/hugo_encryptor/hugo-encryptor.py

# 查看 Git 状态
git status

# 查看最近提交
git log --oneline -10

# 清理生成文件
rm -rf public/ resources/
```

---

## ⚠️ 常见问题

### Q: Hugo 版本不兼容

**解决**: 升级 Hugo 到 v0.140.0+
```bash
choco upgrade hugo-extended -y  # Windows
brew upgrade hugo                # macOS
```

### Q: Python 依赖安装失败

**解决**: 使用 `pycryptodome` 替代 `pycrypto`
```bash
pip install pycryptodome beautifulsoup4 lxml
```

### Q: 加密内容不生效

**检查**:
1. 是否包含 `<!--more-->` 标签
2. 是否运行了加密脚本
3. shortcode 语法是否正确
4. `static/decrypt.js` 是否存在

### Q: Git 推送失败

**解决**:
```bash
# 使用 SSH 密钥
git remote set-url origin git@github.com:bluespace3/bluespace3.github.io.git

# 或使用 Personal Access Token
git remote set-url origin https://token@github.com/...
```

### Q: GitHub Token 无效

**解决**:
```bash
# 检查 Token 是否设置
echo $GITHUB_TOKEN

# 或检查 .env 文件
cat .env

# 重新设置 Token
python tools/setup-token-simple.py
```

---

## 📝 注意事项

### 部署相关

1. **加密脚本**：每次生成网站后需要运行加密脚本
2. **public 目录**：用于本地预览，正式发布由 GitHub Actions 处理
3. **提交信息**：使用自动生成的提交信息，便于追踪

### 主题配置

- **主题**：PaperMod
- **配置文件**：`hugo.toml`
- **自定义样式**：`static/css/`、`static/js/`
- **主题更新**：`git submodule update --remote --merge`（如使用子模块）

### Python 版本要求

- 需要 Python 3.x 运行加密脚本
- 推荐使用 Python 3.8 或更高版本

### 文件管理

- **加密文件**：`decrypt.js` 必须存在于 `static/` 目录
- **环境变量**：`.env` 文件已添加到 `.gitignore`，不会被提交
- **备份**：重要修改前建议创建 Git 分支或备份

---

## 📚 更多文档

- **[DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)** - 服务器部署指南
- **[skills/](./skills/)** - AI Skills 定义目录（供 AI 助手使用）

---

## 💡 技术栈

- **Hugo** v0.140.0+ Extended - 静态网站生成器
- **PaperMod** - Hugo 主题
- **hugo-encryptor** - 内容加密
- **GitHub Actions** - 自动部署
- **Python** - 自动化脚本

---

## 🔗 相关链接

- **博客地址**: https://bluespace3.github.io/
- **GitHub 仓库**: https://github.com/bluespace3/bluespace3.github.io
- **Hugo 文档**: https://gohugo.io/documentation/
- **PaperMod 主题**: https://github.com/adityatelange/hugo-PaperMod

---

## 📄 许可证

© 2025 蓝色空间号
