# 服务器工作流程说明

## 🎯 工作流程概述

```
本地 ──迁移──> 服务器 ──同步──> Git 提交 ──推送──> GitHub ──自动部署──> GitHub Pages
```

### 详细流程

1. **本地** - 开发和测试
2. **迁移到服务器** - 把项目文件复制到 Ubuntu 服务器
3. **服务器同步** - 在服务器上运行 `sync_notes_from_github.py` 获取文章真实时间
4. **Git 提交** - 提交更改到 Git 仓库
5. **推送到 GitHub** - 推送到 `main` 分支
6. **GitHub Actions** - 自动构建 Hugo 网站
7. **GitHub Pages** - 自动部署到 `https://bluespace3.github.io/`

---

## 📋 服务器信息

```
Host: openclaw
IP: 38.55.39.104
Port: 22
User: root
SSH Key: ~/.ssh/id_rsa_new
项目目录: /var/www/bluespace3.github.io
```

---

## 🚀 第一步：迁移到服务器

### 首次迁移（只需一次）

#### Windows PowerShell

```powershell
.\migrate-to-server.ps1
```

#### Linux/macOS/Git Bash

```bash
./migrate-to-server.sh
```

### 手动迁移

```bash
# 1. 连接到服务器
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104

# 2. 安装依赖
apt-get update
apt-get install -y python3 python3-pip python3-venv git

# 3. 克隆项目
mkdir -p /var/www/bluespace3.github.io
cd /var/www/bluespace3.github.io
git clone https://github.com/bluespace3/bluespace3.github.io.git .

# 4. 创建 .env 文件
cp .env.example .env
nano .env  # 填入 GITHUB_TOKEN

# 5. 安装 Python 依赖
python3 -m venv venv
source venv/bin/activate
pip install -r tools/requirements.txt
```

---

## 🔄 第二步：同步并部署（日常使用）

### 方式 A：一键同步部署（推荐）

#### Windows PowerShell

```powershell
.\sync-and-deploy.ps1
```

#### Linux/macOS/Git Bash

```bash
./sync-and-deploy.sh
```

这个脚本会自动：
1. ✅ 连接到服务器
2. ✅ 运行同步脚本更新文章时间
3. ✅ 提交更改到 Git
4. ✅ 推送到 GitHub
5. ✅ GitHub Actions 自动部署

### 方式 B：手动操作

```bash
# 1. 连接到服务器
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104

# 2. 进入项目目录
cd /var/www/bluespace3.github.io

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 同步笔记
python tools/sync_notes_from_github.py --batch content/post

# 5. 提交更改
git add .
git commit -m "chore: 更新文章时间"
git push origin main

# 6. GitHub Actions 自动部署
```

---

## 📊 部署状态查看

### GitHub Actions 部署状态

访问：https://github.com/bluespace3/bluespace3.github.io/actions

### 查看博客

访问：https://bluespace3.github.io/

### 查看归档页面

访问：https://bluespace3.github.io/archives/

检查文章时间分布是否正确（应该有不同的日期，而不是都是 2025-11-20）

---

## 🔧 常见问题

### Q1: .env 文件未找到

**错误**: `⚠️  未设置 GITHUB_TOKEN 环境变量`

**解决**:
```bash
# 在服务器上
cd /var/www/bluespace3.github.io
cp .env.example .env
nano .env  # 填入你的 GitHub Token
```

### Q2: 推送失败

**错误**: `git push failed`

**解决**:
```bash
# 检查 Git 配置
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

# 重新推送
git push origin main
```

### Q3: GitHub Actions 部署失败

**检查**:
1. 访问 Actions 页面查看错误日志
2. 确保 `hugo.yml` 配置正确
3. 确保 Repository Settings → Pages 启用了 GitHub Actions

---

## 📁 服务器目录结构

```
/var/www/bluespace3.github.io/
├── .env                    # GitHub Token 配置
├── .github/
│   └── workflows/
│       └── hugo.yml        # GitHub Actions 配置
├── content/
│   └── post/              # 博客文章（会被同步脚本更新）
├── tools/
│   ├── sync_notes_from_github.py  # 同步脚本
│   ├── github_api.py              # GitHub API 封装
│   ├── config.py                  # 配置管理
│   └── requirements.txt           # Python 依赖
├── venv/                   # Python 虚拟环境
├── hugo.toml              # Hugo 配置
└── .git/                  # Git 仓库
```

---

## 🔄 完整工作流程示例

### 场景：你在 GitHub 知识库中更新了一篇笔记

#### 步骤 1：更新笔记

在 `https://github.com/bluespace3/knowledge_bases` 仓库中更新或添加笔记。

#### 步骤 2：运行同步部署脚本

```powershell
# Windows PowerShell
.\sync-and-deploy.ps1

# 或 Linux/macOS
./sync-and-deploy.sh
```

#### 步骤 3：等待 GitHub Actions

1. 访问 https://github.com/bluespace3/bluespace3.github.io/actions
2. 等待 "deploy" workflow 完成（通常 1-2 分钟）

#### 步骤 4：查看博客

访问 https://bluespace3.github.io/ 查看更新后的博客。

---

## 📝 脚本说明

### migrate-to-server.sh / migrate-to-server.ps1

**用途**: 首次迁移项目到服务器

**功能**:
- 安装系统依赖
- 克隆项目到服务器
- 安装 Python 依赖
- 上传 .env 文件

**使用频率**: 仅首次使用

### sync-and-deploy.sh / sync-and-deploy.ps1

**用途**: 日常同步和部署

**功能**:
- 运行同步脚本更新文章时间
- 提交更改到 Git
- 推送到 GitHub
- 触发 GitHub Actions 自动部署

**使用频率**: 每次更新笔记后使用

---

## 🎯 总结

### 核心理念

- **本地** - 用于开发和测试
- **服务器** - 用于运行同步脚本（获取 GitHub API 数据）
- **GitHub** - 用于版本控制和自动部署
- **GitHub Pages** - 最终的博客网站

### 优势

1. ✅ **自动化** - 一键同步部署
2. ✅ **准确时间** - 使用 GitHub API 获取真实创建时间
3. ✅ **CDN 加速** - GitHub Pages 全球加速
4. ✅ **版本控制** - Git 完整的版本历史
5. ✅ **免费托管** - GitHub Pages 完全免费

---

## 📞 需要帮助？

- **同步工具**: 参考 `tools/SYNC_NOTES_GUIDE.md`
- **快速开始**: 参考 `QUICKSTART.md`
- **实施总结**: 参考 `IMPLEMENTATION_SUMMARY.md`
- **GitHub Actions**: 参考 `.github/workflows/hugo.yml`
