#!/bin/bash
set -e

echo "🔍 验证部署配置..."

# 检查 public/ 目录中的 URL（只检查 href/src 属性，忽略文章内容）
if [ -d "public" ]; then
    LOCALHOST_COUNT=$(grep -E 'href="http://localhost:1313|src="http://localhost:1313' public/index.html 2>/dev/null | wc -l)
    if [ "$LOCALHOST_COUNT" -gt 0 ]; then
        echo "❌ 发现 $LOCALHOST_COUNT 个 localhost URL 在首页配置中"
        echo "请重新生成：hugo --environment production"
        exit 1
    fi
    echo "✅ public/ 目录 URL 验证通过"
fi

# 检查首页文章数量
if [ -f "public/index.html" ]; then
    POST_COUNT=$(grep -c "post-entry" public/index.html || echo "0")
    echo "📊 首页文章数量: $POST_COUNT"
    if [ "$POST_COUNT" -lt 5 ]; then
        echo "⚠️  警告：首页文章数量偏少"
    fi
fi

# 检查配置文件
if grep -q "bluespace.eu.org" hugo.toml; then
    echo "✅ 生产配置 baseURL 正确"
else
    echo "❌ hugo.toml baseURL 配置异常"
    exit 1
fi

echo "✅ 验证通过"
