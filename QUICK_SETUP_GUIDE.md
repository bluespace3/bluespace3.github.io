# 快速设置指南 - 笔记转换成博客

## 🎯 目标

将笔记仓库（knowledge_bases）的笔记转换成博客文章，使用 GitHub API 获取真实时间。

**注意**：已存在的 Front Matter 会被跳过（--no-overwrite）

---

## 📝 步骤 1：设置 GitHub Token

### 方式 A：交互式设置（推荐）

```bash
python tools/setup_token.py
```

按提示粘贴你的 GitHub Token。

### 方式 B：手动设置（如果交互式失败）

```bash
# 1. 创建 .env 文件
cat > .env << 'EOF'
# GitHub Token 配置
GITHUB_TOKEN=你的Token

# 注意：将 "你的Token" 替换为实际的 GitHub Token
EOF

# 2. 编辑 .env 文件
notepad .env  # Windows
# 或
nano .env    # Linux/Mac
```

### 获取 GitHub Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置：
   - **Note**: Hugo 博客同步工具
   - **Expiration**: 90 days 或 No expiration
   - **权限**: ✅ `repo` (Full control of private repositories)
4. 点击 "Generate token"
5. **立即复制** Token（格式：`ghp_xxxxxxxxxxxxxxxxxxxx`）

---

## 🚀 步骤 2：安装 Python 依赖

```bash
pip install -r tools/requirements.txt
```

需要的依赖：
- `requests` - HTTP 请求
- `pyyaml` - YAML 配置解析

---

## 🔄 步骤 3：运行转换脚本

### 预览模式（推荐先运行）

```bash
python tools/sync_notes_from_github.py --batch content/post --dry-run --no-overwrite
```

### 执行转换

```bash
python tools/sync_notes_from_github.py --batch content/post --no-overwrite
```

**参数说明**：
- `--batch content/post` - 批量处理 content/post 目录
- `--no-overwrite` - 跳过已有 Front Matter 的文件
- `--dry-run` - 预览模式，不实际修改文件
- `--verbose` - 显示详细日志

---

## ✅ 步骤 4：验证结果

### 本地预览

```bash
hugo server -D
```

访问：http://localhost:1313/archives/

### 检查要点

- [ ] 文章时间是否正确（应该是不同的日期）
- [ ] 时区是否为东八区 (+08:00)
- [ ] 分类是否正确（来自父目录）
- [ ] 标题是否正确（来自文件名）

---

## 📤 步骤 5：提交到 GitHub

```bash
# 提交更改
git add .
git commit -m "chore: 使用 GitHub API 更新文章时间

- 使用 sync_notes_from_github.py 同步笔记
- 通过 GitHub API 获取文件真实创建和更新时间
- 自动生成 Hugo Front Matter
- 时间转换为东八区 (+08:00)
- 跳过已有 Front Matter 的文件"

# 推送到 GitHub
git push origin main
```

---

## 🌐 步骤 6：GitHub Actions 自动部署

推送到 GitHub 后，GitHub Actions 会自动：
1. 构建 Hugo 网站
2. 部署到 GitHub Pages

等待 1-2 分钟后访问：https://bluespace3.github.io/

---

## 📊 预期结果

### 转换前

```yaml
---
title: 'mcp-intro'
categories: ["技术"]
date: 2025-11-20T15:58:14+00:00  # UTC 时间
lastmod: 2025-12-02T16:07:56+00:00
---
```

### 转换后

```yaml
---
title: 'mcp-intro'
categories: ["AIGC学习笔记"]
date: 2025-03-15T18:30:00+08:00  # 东八区时间，真实创建日期
lastmod: 2025-12-26T19:30:00+08:00
---
```

### 改进

- ✅ 时区：UTC (+00:00) → 东八区 (+08:00)
- ✅ 时间来源：本地 git log → GitHub API
- ✅ 准确性：同步日期 → 真实创建日期
- ✅ 分类：手动指定 → 自动提取（来自父目录）

---

## 🔧 常见问题

### Q1: 提示 "未设置 GITHUB_TOKEN"

**解决**：创建 .env 文件并填入 Token

```bash
# Windows
echo "GITHUB_TOKEN=ghp_xxxxx" > .env

# Linux/Mac
echo "GITHUB_TOKEN=ghp_xxxxx" > .env
```

### Q2: 所有文件都被跳过

**原因**：所有文件都已有 Front Matter

**解决**：如果想强制更新，去掉 `--no-overwrite` 参数

```bash
python tools/sync_notes_from_github.py --batch content/post
```

### Q3: 某些文件处理失败

**检查**：
1. 文件是否在 GitHub 仓库中存在
2. Token 权限是否正确（需要 `repo` 权限）
3. 网络连接是否正常

**查看详细日志**：
```bash
python tools/sync_notes_from_github.py --batch content/post --verbose
```

---

## 📚 相关文档

- **完整指南**: `tools/SYNC_NOTES_GUIDE.md`
- **快速开始**: `QUICKSTART.md`
- **时间验证**: `TIME_CONFIG_VERIFICATION.md`
- **服务器工作流程**: `SERVER_WORKFLOW.md`

---

## 🎉 一键执行（配置完成后）

```bash
# 1. 设置 Token（首次）
python tools/setup_token.py

# 2. 安装依赖（首次）
pip install -r tools/requirements.txt

# 3. 运行转换
python tools/sync_notes_from_github.py --batch content/post --no-overwrite

# 4. 本地预览
hugo server -D

# 5. 提交推送
git add .
git commit -m "chore: 更新文章时间"
git push origin main
```

---

**完成！** 🎉
