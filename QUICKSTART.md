# 笔记同步工具 - 快速开始

## 🚀 3 步开始使用

### 步骤 1：设置 GitHub Token

**方式 A：使用交互式脚本（推荐）**

```bash
python tools/setup_token.py
```

脚本会引导你：
1. 打开 GitHub Token 创建页面
2. 配置 Token 权限
3. 自动创建 `.env` 文件

**方式 B：手动设置**

```bash
# 1. 复制模板
cp .env.example .env

# 2. 编辑 .env 文件
# 将 your_token_here 替换为你的 GitHub Token
```

### 步骤 2：安装依赖

```bash
pip install -r tools/requirements.txt
```

### 步骤 3：同步笔记

```bash
# 预览模式（推荐先运行这个）
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 确认无误后执行
python tools/sync_notes_from_github.py --batch content/post
```

---

## 📖 详细文档

- **完整使用指南**：`tools/SYNC_NOTES_GUIDE.md`
- **技能说明**：`SKILLS.md` 中的 "Skill: 同步笔记到博客" 章节
- **实施总结**：`IMPLEMENTATION_SUMMARY.md`

---

## ❓ 常见问题

### Q: 如何获取 GitHub Token？

**A**: 按以下步骤操作：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置：
   - **Note**: Hugo 博客同步工具
   - **Expiration**: 90 days 或 No expiration
   - **权限**: ✅ `repo` (Full control of private repositories)
4. 点击 "Generate token"
5. **立即复制** Token（只会显示一次）

### Q: Token 安全吗？

**A**: 是的，Token 只存储在本地 `.env` 文件中：

- ✅ `.env` 文件已添加到 `.gitignore`，不会提交到 Git
- ✅ 只在你的本地计算机上使用
- ✅ 如果不慎泄露，可在 GitHub 上随时撤销

### Q: 每次都要设置 Token 吗？

**A**: 不需要！设置一次后：

- ✅ `.env` 文件会永久保存 Token
- ✅ 脚本会自动读取 `.env` 文件
- ✅ 无需每次都设置环境变量

### Q: 提示 "未设置 GITHUB_TOKEN"？

**A**: 检查以下几点：

1. `.env` 文件是否存在？
   ```bash
   ls .env
   ```

2. `.env` 文件内容是否正确？
   ```bash
   cat .env
   # 应该看到：GITHUB_TOKEN=ghp_xxxxxxxx
   ```

3. 如果还不行，重新运行设置脚本：
   ```bash
   python tools/setup_token.py
   ```

---

## 🎯 下一步

1. **本地验证**：
   ```bash
   hugo server -D
   # 访问 http://localhost:1313/archives/ 检查文章时间
   ```

2. **发布到博客**：
   ```bash
   # Windows
   deploy.bat

   # Linux/macOS
   ./deploy.sh
   ```

3. **访问博客**：https://bluespace3.github.io/archives/

---

## 🔗 相关链接

- [GitHub Token 设置](https://github.com/settings/tokens)
- [项目仓库](https://github.com/bluespace3/bluespace3.github.io)
