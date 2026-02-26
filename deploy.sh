#!/bin/bash

# 博客自动化部署脚本
# 适用于 Linux 和 macOS

set -e  # 遇到错误立即退出

echo "========================================"
echo "       博客自动化部署脚本"
echo "========================================"
echo ""

# 0. 检查加密文件
echo "[0/5] 正在检查加密文件..."
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
echo "[1/5] 正在生成网站..."
hugo --cleanDestinationDir
echo "✅ 网站生成成功"
echo ""

# 2. 加密文章
echo "[2/5] 正在加密文章..."
if python tools/hugo_encryptor/hugo-encryptor.py; then
    echo "✅ 文章加密成功"
else
    echo "⚠️  加密失败或没有需要加密的文章"
fi
echo ""

# 3. 提交到 Git
echo "[3/5] 正在提交到 Git..."
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
echo "[4/5] 正在推送到 GitHub..."
git push origin main
echo "✅ 推送成功"
echo ""

echo "========================================"
echo "       🎉 部署完成！"
echo "========================================"
echo ""
echo "博客地址: https://bluespace3.github.io/"
echo ""
