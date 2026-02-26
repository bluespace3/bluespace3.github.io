# 快速参考卡片

## 🎯 工作流程

```
更新笔记 → 同步部署 → GitHub Actions → GitHub Pages
```

---

## 🚀 快速命令

### 首次迁移（仅需一次）

```powershell
# Windows PowerShell
.\migrate-to-server.ps1

# Linux/macOS
./migrate-to-server.sh
```

### 日常同步部署（每次更新笔记后）

```powershell
# Windows PowerShell
.\sync-and-deploy.ps1

# Linux/macOS
./sync-and-deploy.sh
```

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

## 🔗 重要链接

| 链接 | 说明 |
|------|------|
| https://bluespace3.github.io/ | 博客首页 |
| https://bluespace3.github.io/archives/ | 文章归档（检查时间） |
| https://github.com/bluespace3/knowledge_bases | 笔记仓库 |
| https://github.com/bluespace3/bluespace3.github.io | 博客仓库 |
| https://github.com/bluespace3/bluespace3.github.io/actions | 部署状态 |
| https://github.com/settings/tokens | GitHub Token |

---

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `.env` | GitHub Token 配置（需要手动创建） |
| `tools/sync_notes_from_github.py` | 同步脚本 |
| `tools/github_api.py` | GitHub API 封装 |
| `tools/config.py` | 配置管理 |
| `tools/requirements.txt` | Python 依赖 |
| `.github/workflows/hugo.yml` | GitHub Actions 配置 |

---

## 🛠️ 手动操作步骤

如果脚本失败，可以手动执行：

```bash
# 1. 连接到服务器
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104

# 2. 进入项目目录
cd /var/www/bluespace3.github.io

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 同步笔记
python tools/sync_notes_from_github.py --batch content/post

# 5. 提交并推送
git add .
git commit -m "chore: 更新文章时间"
git push origin main

# 6. GitHub Actions 自动部署
```

---

## ❓ 常见问题快速解决

### 问题：未设置 GITHUB_TOKEN

```bash
# 在服务器上
cd /var/www/bluespace3.github.io
cp .env.example .env
nano .env  # 填入 token
```

### 问题：SSH 连接失败

```bash
# 检查密钥权限
chmod 600 ~/.ssh/id_rsa_new

# 测试连接
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104
```

### 问题：部署失败

```bash
# 1. 检查 GitHub Actions 状态
# 访问: https://github.com/bluespace3/bluespace3.github.io/actions

# 2. 检查分支是否为 main
git branch

# 3. 检查 hugo.yml 配置
cat .github/workflows/hugo.yml
```

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| `SERVER_WORKFLOW.md` | 完整工作流程说明 |
| `DEPLOY_TO_SERVER.md` | 服务器部署指南 |
| `tools/SYNC_NOTES_GUIDE.md` | 同步工具完整指南 |
| `QUICKSTART.md` | 快速开始指南 |
| `IMPLEMENTATION_SUMMARY.md` | 实施总结 |
| `SKILLS.md` | 技能说明 |

---

## ✅ 验证清单

部署完成后，检查：

- [ ] 访问 https://bluespace3.github.io/ 能看到博客
- [ ] 访问 /archives/ 文章时间分布合理（不是都是 2025-11-20）
- [ ] GitHub Actions 部署成功（绿色勾）
- [ ] 文章内容正确显示
- [ ] 文章分类正确（来自父目录）

---

## 🎉 快速上手

1. **首次设置**
   ```powershell
   .\migrate-to-server.ps1
   ```

2. **更新笔记后**
   ```powershell
   .\sync-and-deploy.ps1
   ```

3. **等待 2 分钟**

4. **访问博客**
   ```
   https://bluespace3.github.io/
   ```

就这么简单！🚀
