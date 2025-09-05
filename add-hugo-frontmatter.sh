#!/bin/bash

# 自动化脚本：为没有 Hugo 头的 Markdown 文件添加 Front Matter
# 用法：./add-hugo-frontmatter.sh [文件路径或目录]
# 如果不提供参数，默认处理当前目录下的所有 .md 文件

set -e

# 获取当前时间，格式为 RFC3339
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")

# 函数：为单个文件添加 Hugo 头
add_hugo_frontmatter() {
    local file="$1"
    
    # 检查文件是否存在
    if [ ! -f "$file" ]; then
        echo "⚠️  文件不存在：$file"
        return 1
    fi
    
    # 检查是否已经是 Markdown 文件
    if [[ "$file" != *.md ]]; then
        echo "⚠️  跳过非 Markdown 文件：$file"
        return 0
    fi
    
    # 检查是否已经有 Hugo 头
    if head -n 10 "$file" | grep -q "^---$"; then
        echo "✅ 文件已有 Hugo 头，跳过：$file"
        return 0
    fi
    
    echo "🔄 为文件添加 Hugo 头：$file"
    
    # 获取第一行作为标题（去除 # 符号）
    local first_line=$(head -n 1 "$file" | sed 's/^#* \?//')
    
    # 如果第一行为空，使用文件名作为标题
    if [ -z "$first_line" ]; then
        local filename=$(basename "$file" .md)
        first_line="$filename"
    fi
    
    # 创建临时文件
    local temp_file=$(mktemp)
    
    # 写入 Hugo 头
    cat > "$temp_file" << EOF
---
title: '${first_line}'
categories: ["技术"]
date: ${CURRENT_TIME}
lastmod: ${CURRENT_TIME}
---

EOF
    
    # 追加原文件内容
    cat "$file" >> "$temp_file"
    
    # 替换原文件
    mv "$temp_file" "$file"
    
    echo "✅ 成功添加 Hugo 头：$file"
}

# 主程序
main() {
    local target="$1"
    
    if [ -z "$target" ]; then
        target="."
        echo "🔄 处理当前目录下的所有 Markdown 文件..."
    elif [ -d "$target" ]; then
        echo "🔄 处理目录 $target 下的所有 Markdown 文件..."
    elif [ -f "$target" ]; then
        echo "🔄 处理单个文件：$target"
        add_hugo_frontmatter "$target"
        echo "✅ 处理完成！"
        exit 0
    else
        echo "❌ 错误：目标文件或目录不存在：$target"
        exit 1
    fi
    
    # 查找并处理所有 Markdown 文件
    find "$target" -name "*.md" -type f | while read -r file; do
        add_hugo_frontmatter "$file"
    done
    
    echo "✅ 所有文件处理完成！"
    echo "📋 请检查文件内容，确认 Hugo 头添加正确"
}

# 运行主程序
main "$@"