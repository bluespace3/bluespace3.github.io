#!/bin/bash

# 博客自动化部署脚本
# 适用于 Linux 和 macOS

set -e  # 遇到错误立即退出

echo "========================================"
echo "       博客自动化部署脚本"
echo "========================================"
echo ""

# 获取脚本所在目录（支持从任何位置执行）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# -1. 后台同步笔记（不阻塞主流程）
echo "🔄 触发后台笔记同步..."
if [ -f "scripts/sync-notes-background.sh" ]; then
    # 使用 nohup 在后台运行，不输出到终端
    nohup bash scripts/sync-notes-background.sh > /dev/null 2>&1 &
    echo "✅ 笔记同步已在后台运行（日志：/tmp/notes-sync-*.log）"
else
    echo "⚠️  未找到笔记同步脚本，跳过"
fi
echo ""

# 0. 检查加密文件
echo "[0/6] 正在检查加密文件..."
if [ ! -f "static/decrypt.js" ]; then
    echo "📁 复制 decrypt.js 到 static 目录..."
    cp tools/hugo_encryptor/decrypt.js static/
    if [ $? -eq 0 ]; then
        echo "✅ decrypt.js 复制成功"
    else
        echo "⚠️  decrypt.js 复制失败，请手动检查"
    fi
else
    echo "✅ decrypt.js 已存在"
fi
echo ""

# 1. 生成网站
echo "[1/6] 正在生成网站..."
hugo --cleanDestinationDir --environment production --minify
echo "✅ 网站生成成功（环境：production）"
echo ""

# 2. 加密文章
echo "[2/6] 正在加密文章..."
if python3 tools/hugo_encryptor/hugo-encryptor.py; then
    echo "✅ 文章加密成功"
else
    echo "⚠️  加密失败或没有需要加密的文章"
fi
echo ""

# 2.5. 验证部署
echo "[2.5/6] 正在验证部署..."
if [ -f "scripts/verify-deploy.sh" ]; then
    if bash scripts/verify-deploy.sh; then
        echo "✅ 部署验证通过"
    else
        echo "❌ 部署验证失败，中止部署"
        exit 1
    fi
else
    echo "⚠️  未找到验证脚本，跳过验证"
fi
echo ""

# 3. 提交到 Git
echo "[3/6] 正在提交到 Git..."
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "⚠️  没有新的更改需要提交"
    echo ""
    echo "========================================"
    echo "       📝 无需部署"
    echo "========================================"
    exit 0
fi

COMMIT_MSG="自动部署: $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"
echo "✅ 提交成功"
echo ""

# 4. 推送到 GitHub
echo "[4/6] 正在推送到 GitHub..."
git push origin main
echo "✅ 推送成功"
echo ""

echo "========================================"
echo "       🎉 部署完成！"
echo "========================================"
echo ""
echo "博客地址: https://bluespace.eu.org/"
echo ""
