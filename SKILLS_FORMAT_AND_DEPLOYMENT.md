# Skills 格式和服务器部署说明

## ✅ 标准的 Skills 格式

### 1. Skills 文件结构

现在项目已经包含标准的 Claude Code Skills 格式：

```
.claude/
├── settings.local.json    # Claude Code 项目设置
└── skills/                # 技能定义目录（标准格式）
    └── sync-notes.md      # 同步笔记技能
```

### 2. 技能定义格式

**文件**: `.claude/skills/sync-notes.md`

这个文件定义了一个标准的技能，包含：
- ✅ **技能描述** - 清晰说明技能的功能
- ✅ **核心功能** - 列出主要特性
- ✅ **使用方法** - 详细的命令示例
- ✅ **配置说明** - 如何配置技能
- ✅ **参数说明** - 所有命令行参数
- ✅ **验证方法** - 如何验证技能是否正常工作

### 3. 如何使用技能

在 Claude Code 中，您可以直接说：

```
"请使用 sync-notes 技能同步 content/post 目录下的所有文章"
```

Claude Code 会自动读取 `.claude/skills/sync-notes.md` 文件，理解技能的功能和用法。

### 4. 与文档的区别

| 文件 | 用途 | 格式 |
|------|------|------|
| **SKILLS.md** | 项目级技能文档（供人类阅读） | Markdown 说明文档 |
| **.claude/skills/*.md** | Claude Code 技能定义（供 AI 理解） | 标准技能格式 |

两个文件互相补充：
- `SKILLS.md` - 提供详细的用户指南
- `.claude/skills/sync-notes.md` - 提供结构化的技能定义

---

## 🚀 部署到服务器

### 服务器信息

```
Host: openclaw
HostName: 38.55.39.104
Port: 22
User: root
IdentityFile: ~/.ssh/id_rsa_new
```

### 自动部署（推荐）

#### Windows PowerShell

```powershell
# 在项目根目录运行
.\deploy-to-server.ps1
```

#### Linux/macOS/Git Bash

```bash
# 在项目根目录运行
./deploy-to-server.sh
```

### 部署脚本功能

自动完成以下任务：

1. ✅ 测试 SSH 连接到服务器
2. ✅ 安装系统依赖（Python 3, pip, Git, Hugo）
3. ✅ 克隆/更新项目到 `/var/www/bluespace3.github.io`
4. ✅ 上传 `.env` 配置文件（如果本地存在）
5. ✅ 创建 Python 虚拟环境
6. ✅ 安装 Python 依赖
7. ✅ 测试同步脚本（预览模式）

---

## 📋 手动部署步骤

如果自动脚本失败，按以下步骤手动部署：

### 1. 连接到服务器

```bash
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104
```

### 2. 安装依赖

```bash
# 更新系统
apt-get update

# 安装 Python 和 Git
apt-get install -y python3 python3-pip python3-venv git

# 安装 Hugo
wget https://github.com/gohugoio/hugo/releases/download/v0.128.0/hugo_extended_0.128.0_linux-amd64.deb -O /tmp/hugo.deb
dpkg -i /tmp/hugo.deb
```

### 3. 克隆项目

```bash
mkdir -p /var/www/bluespace3.github.io
cd /var/www/bluespace3.github.io
git clone https://github.com/bluespace3/bluespace3.github.io.git .
```

### 4. 配置环境

```bash
# 创建 .env 文件
cp .env.example .env
nano .env  # 填入 GITHUB_TOKEN
```

### 5. 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r tools/requirements.txt
```

### 6. 测试运行

```bash
# 预览模式
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 执行同步
python tools/sync_notes_from_github.py --batch content/post

# 构建博客
hugo --minify
```

---

## 🔄 日常使用

### 同步笔记

```bash
# 连接到服务器
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104

# 进入项目目录
cd /var/www/bluespace3.github.io

# 激活虚拟环境
source venv/bin/activate

# 同步笔记
python tools/sync_notes_from_github.py --batch content/post

# 构建博客
hugo --minify
```

### 定时同步（可选）

创建 cron 定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加每小时同步一次
0 * * * * cd /var/www/bluespace3.github.io && source venv/bin/activate && python tools/sync_notes_from_github.py --batch content/post && hugo --minify
```

---

## 📁 新增文件清单

### Skills 相关
1. **`.claude/skills/sync-notes.md`** - 标准技能定义文件

### 部署相关
2. **`deploy-to-server.sh`** - Linux/macOS 部署脚本
3. **`deploy-to-server.ps1`** - Windows PowerShell 部署脚本
4. **`DEPLOY_TO_SERVER.md`** - 部署完整指南

### 之前创建的文件
5. **`tools/github_api.py`** - GitHub API 封装
6. **`tools/config.py`** - 配置管理
7. **`tools/sync_notes_from_github.py`** - 主同步脚本
8. **`tools/setup_token.py`** - Token 设置脚本
9. **`.env.example`** - 环境变量模板
10. **`tools/requirements.txt`** - Python 依赖
11. **`tests/test_github_api.py`** - 单元测试
12. **`QUICKSTART.md`** - 快速开始指南
13. **`SKILLS.md`** - 技能文档（已更新）
14. **`tools/SYNC_NOTES_GUIDE.md`** - 完整使用指南

---

## ✅ 验证清单

### Skills 格式验证

- [x] `.claude/skills/` 目录存在
- [x] 技能文件包含标准格式
- [x] 技能描述清晰完整
- [x] 使用说明详细
- [x] 配置说明准确

### 服务器部署验证

- [x] 部署脚本创建完成
- [x] 支持 Windows PowerShell
- [x] 支持 Linux/macOS Bash
- [x] 包含完整的错误处理
- [x] 包含手动部署步骤

### 文档完整性

- [x] 快速开始指南
- [x] 完整部署指南
- [x] 常见问题解答
- [x] 服务器目录结构说明

---

## 🎯 下一步

### 立即行动

1. **本地测试**：
   ```bash
   python tools/setup_token.py
   python tools/sync_notes_from_github.py --batch content/post --dry-run
   ```

2. **部署到服务器**：
   ```powershell
   # Windows
   .\deploy-to-server.ps1

   # 或 Linux/macOS
   ./deploy-to-server.sh
   ```

3. **验证安装**：
   ```bash
   ssh -i ~/.ssh/id_rsa_new root@38.55.39.104
   cd /var/www/bluespace3.github.io
   source venv/bin/activate
   python tools/sync_notes_from_github.py --batch content/post
   hugo --minify
   ```

---

## 📞 需要帮助？

- **技能使用**: 参考 `SKILLS.md` 或 `.claude/skills/sync-notes.md`
- **部署问题**: 参考 `DEPLOY_TO_SERVER.md`
- **快速入门**: 参考 `QUICKSTART.md`
- **完整指南**: 参考 `tools/SYNC_NOTES_GUIDE.md`

所有文档都已完善，您可以随时查阅！
