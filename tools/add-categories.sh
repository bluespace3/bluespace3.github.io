#!/bin/bash

# 自动添加分类工具 - Linux/macOS Shell 脚本
# 根据文件所在的目录自动添加到 categories

if [ $# -eq 0 ]; then
    echo "使用方法: $0 <文件或目录路径> [选项]"
    echo ""
    echo "示例:"
    echo "  $0 content/archives"
    echo "  $0 content --dry-run"
    echo "  $0 content --verbose"
    echo ""
    echo "选项:"
    echo "  --dry-run     预览模式，不实际修改文件"
    echo "  --verbose     显示详细信息"
    exit 1
fi

echo "========================================"
echo "     自动添加分类工具"
echo "========================================"
echo ""

python tools/add_categories.py "$@"
