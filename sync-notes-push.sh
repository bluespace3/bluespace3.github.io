#!/bin/bash

# 自动化脚本：将主项目笔记更改推送到独立仓库
# 用法：./sync-notes-push.sh

set -e

echo "🔄 开始将主项目笔记更改推送到独立仓库..."

# 检查是否在正确的目录
if [ ! -f "hugo.toml" ]; then
    echo "❌ 错误：请在 Hugo 项目根目录运行此脚本"
    exit 1
fi

# 定义路径
HUGO_PROJECT_DIR=$(pwd)
NOTES_REPO_DIR="C:/Users/tian4/knowledge_bases"

echo "📍 主项目目录：$HUGO_PROJECT_DIR"
echo "📍 笔记仓库目录：$NOTES_REPO_DIR"

# 检查笔记仓库是否存在
if [ ! -d "$NOTES_REPO_DIR" ]; then
    echo "❌ 错误：笔记仓库目录不存在：$NOTES_REPO_DIR"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  检测到未提交的更改，请先提交再推送"
    git status
    exit 1
fi

# 执行 subtree push
echo "🔄 执行 git subtree push..."
git subtree push --prefix=content/post "$NOTES_REPO_DIR" master

echo "✅ 推送完成！"
echo "📋 更新已成功推送到独立笔记仓库"