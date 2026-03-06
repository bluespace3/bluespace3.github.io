#!/bin/bash
set -e

echo "🔍 验证部署配置..."

# 检查 public/ 目录结构性 URL（排除教程内容中的示例）
if [ -d "public" ]; then
    # 排除 post.backup/ 目录（教程内容包含 localhost 示例）
    LOCALHOST_COUNT=$(find public/ -name "*.html" -not -path "*/post.backup/*" -exec grep -l "localhost:1313" {} \; 2>/dev/null | wc -l)
    if [ "$LOCALHOST_COUNT" -gt 0 ]; then
        echo "❌ 发现 $LOCALHOST_COUNT 个结构性 localhost URL"
        echo "请重新生成：hugo --environment production"
        find public/ -name "*.html" -not -path "*/post.backup/*" -exec grep -l "localhost:1313" {} \; 2>/dev/null
        exit 1
    fi
    echo "✅ public/ 目录结构性 URL 验证通过"
fi

# 检查配置文件
if [ -f "config/production/config.toml" ]; then
    if grep -q "bluespace.eu.org" config/production/config.toml; then
        echo "✅ 生产配置正确"
    else
        echo "❌ 生产配置异常"
        exit 1
    fi
fi

echo "✅ 验证通过"
