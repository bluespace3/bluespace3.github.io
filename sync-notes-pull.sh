#!/bin/bash

# 自动化脚本：从独立笔记仓库同步到主项目
# 用法：./sync-notes-pull.sh

set -e

echo "🔄 开始从独立笔记仓库同步到主项目..."

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

# 执行 subtree pull
echo "🔄 执行 git subtree pull..."
git subtree pull --prefix=content/post "$NOTES_REPO_DIR" master

echo "✅ 同步完成！"
echo "📋 如果有冲突，请手动解决后再次运行脚本"