#!/bin/bash

# 启动本地预览服务器
# 适用于 Linux 和 macOS

echo "========================================"
echo "       启动本地预览服务器"
echo "========================================"
echo ""
echo "正在启动 Hugo 预览服务器..."
echo ""
echo "┌─────────────────────────────────────┐"
echo "│  博客预览地址:                       │"
echo "│  http://localhost:1313               │"
echo "│                                     │"
echo "│  按 Ctrl+C 停止服务器                │"
echo "└─────────────────────────────────────┘"
echo ""

hugo server -D --buildDrafts
