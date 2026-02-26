#!/bin/bash
#
# 在服务器上同步笔记并部署到 GitHub Pages
# 用法: ./sync-and-deploy.sh
#

# 服务器配置
SERVER_HOST="openclaw"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="~/.ssh/id_rsa_new"
REMOTE_DIR="/var/www/bluespace3.github.io"

echo "================================================"
echo "🔄 服务器同步并部署到 GitHub Pages"
echo "================================================"
echo ""

# 在服务器上执行命令
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
cd /var/www/bluespace3.github.io

echo "📅 激活 Python 虚拟环境..."
source venv/bin/activate

echo "🔄 同步笔记（使用 GitHub API 获取真实时间）..."
python tools/sync_notes_from_github.py --batch content/post

echo ""
echo "📊 检查 Git 状态..."
git status

echo ""
echo "📝 提交更改..."
git add .
git commit -m "chore: 使用 GitHub API 更新文章时间

- 使用 sync_notes_from_github.py 同步笔记
- 通过 GitHub API 获取文件真实创建和更新时间
- 自动生成 Hugo Front Matter
- 时间转换为东八区 (+08:00)

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "📤 推送到 GitHub..."
git push origin main

echo ""
echo "✅ 推送成功！"
echo "🌐 GitHub Actions 将自动构建并部署到 GitHub Pages"
echo "🔗 访问 https://bluespace3.github.io/ 查看更新"
ENDSSH

echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "📊 查看 GitHub Actions 部署状态："
echo "🔗 https://github.com/bluespace3/bluespace3.github.io/actions"
echo ""
echo "🌐 访问博客："
echo "🔗 https://bluespace3.github.io/"
echo ""
