#!/bin/bash

# 自动化脚本：将笔记仓库推送到 GitHub
# 用法：./push-to-github.sh <repository-url> [directory]

set -euo pipefail

# 日志函数
log_info() {
    echo "ℹ️  $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "❌ $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# 显示帮助信息
show_help() {
    echo "使用方法: $0 <repository-url> [directory]"
    echo "参数:"
    echo "  repository-url  GitHub 仓库 URL"
    echo "  directory       本地仓库目录 (可选，默认为当前目录)"
    echo ""
    echo "示例:"
    echo "  $0 git@github.com:username/repo.git"
    echo "  $0 https://github.com/username/repo.git"
    echo "  $0 git@github.com:username/repo.git /path/to/repo"
    echo ""
    echo "说明:"
    echo "  该脚本会自动检测未提交的更改并提交，然后推送到 GitHub。"
    echo "  如果远程源 'origin' 已存在，将更新其 URL；否则将添加新的远程源。"
    echo "  脚本会自动检测远程仓库的默认分支并推送。"
}

# 检查帮助参数
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

# 检查参数
if [ -z "${1:-}" ]; then
    log_error "请提供 GitHub 仓库 URL"
    show_help
    exit 1
fi

REPO_URL="$1"
NOTES_REPO_DIR="${2:-$(pwd)}"

# 检查笔记仓库目录
if [ ! -d "$NOTES_REPO_DIR" ]; then
    log_error "笔记仓库目录不存在：$NOTES_REPO_DIR"
    exit 1
fi

# 切换到笔记仓库目录
cd "$NOTES_REPO_DIR" || {
    log_error "无法切换到目录：$NOTES_REPO_DIR"
    exit 1
}

log_info "笔记仓库目录：$(pwd)"
log_info "目标仓库：$REPO_URL"

# 检查是否是git仓库
if [ ! -d ".git" ]; then
    log_error "当前目录不是git仓库"
    exit 1
fi

# 检查是否已有远程源
if git remote | grep -q "origin"; then
    log_info "检测到已存在的远程源 'origin'，将更新其 URL"
    git remote set-url origin "$REPO_URL" || {
        log_error "更新远程URL失败"
        exit 1
    }
else
    log_info "添加远程源 'origin'"
    git remote add origin "$REPO_URL" || {
        log_error "添加远程源失败"
        exit 1
    }
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    log_info "检测到未提交的更改，自动提交..."
    git add . || {
        log_error "git add 失败"
        exit 1
    }

    git commit -m "更新笔记内容 - 自动提交

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>" || {
        log_error "git commit 失败"
        exit 1
    }
fi

# 获取默认分支
DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5 2>/dev/null || echo "main")

# 推送到 GitHub
log_info "推送到 GitHub (分支: $DEFAULT_BRANCH)..."
git push -u origin "$DEFAULT_BRANCH" || {
    log_error "git push 失败"
    exit 1
}

log_info "推送完成！"
log_info "你的笔记现在已存储在 GitHub 上：$REPO_URL"
echo ""
log_info "使用示例："
log_info "  1. 基本用法（当前目录）：./push-to-github.sh git@github.com:username/repo.git"
log_info "  2. 指定目录：./push-to-github.sh https://github.com/username/repo.git /path/to/repo"
log_info "  3. 查看帮助：./push-to-github.sh --help"
echo ""
log_info "后续操作："
log_info "  拉取更新：git pull origin $DEFAULT_BRANCH"
log_info "  推送更改：git push origin $DEFAULT_BRANCH"