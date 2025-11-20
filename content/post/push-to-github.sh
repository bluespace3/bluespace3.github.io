#!/bin/bash

# 自动化脚本：将笔记仓库推送到 GitHub
# 用法：./push-to-github.sh <repository-url>

set -e

echo "🔄 准备将笔记仓库推送到 GitHub..."

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 错误：请提供 GitHub 仓库 URL"
    echo "用法：./push-to-github.sh <repository-url>"
    echo "示例：./push-to-github.sh git@github.com:yourname/knowledge-bases.git"
    exit 1
fi

REPO_URL="$1"
NOTES_REPO_DIR="C:/Users/tian4/knowledge_bases"

# 检查笔记仓库目录
if [ ! -d "$NOTES_REPO_DIR" ]; then
    echo "❌ 错误：笔记仓库目录不存在：$NOTES_REPO_DIR"
    exit 1
fi

# 切换到笔记仓库目录
cd "$NOTES_REPO_DIR"

echo "📍 笔记仓库目录：$(pwd)"
echo "🔗 目标仓库：$REPO_URL"

# 检查是否已有远程源
if git remote | grep -q "origin"; then
    echo "⚠️  检测到已存在的远程源 'origin'，将更新其 URL"
    git remote set-url origin "$REPO_URL"
else
    echo "🔗 添加远程源 'origin'"
    git remote add origin "$REPO_URL"
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，自动提交..."
    git add .
    git commit -m "更新笔记内容 - 自动提交

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi

# 推送到 GitHub
echo "🚀 推送到 GitHub..."
git push -u origin master

echo "✅ 推送完成！"
echo "📋 你的笔记现在已存储在 GitHub 上：$REPO_URL"
echo ""
echo "🔧 后续使用："
echo "   从 GitHub 拉取更新：git pull origin master"
echo "   推送到 GitHub：git push origin master"