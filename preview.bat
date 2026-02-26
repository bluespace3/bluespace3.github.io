@echo off
chcp 65001 >nul
echo ========================================
echo       启动本地预览服务器
echo ========================================
echo.
echo 正在启动 Hugo 预览服务器...
echo.
echo ┌─────────────────────────────────────┐
echo │  博客预览地址:                       │
echo │  http://localhost:1313               │
echo │                                     │
echo │  按 Ctrl+C 停止服务器                │
echo └─────────────────────────────────────┘
echo.

hugo server -D --buildDrafts

pause
