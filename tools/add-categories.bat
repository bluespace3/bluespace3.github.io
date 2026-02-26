@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 自动添加分类工具 - Windows 批处理脚本
REM 根据文件所在的目录自动添加到 categories

if "%~1"=="" (
    echo 使用方法: %~nx0 <文件或目录路径> [选项]
    echo.
    echo 示例:
    echo   %~nx0 content\archives
    echo   %~nx0 content --dry-run
    echo   %~nx0 content --verbose
    echo.
    echo 选项:
    echo   --dry-run     预览模式，不实际修改文件
    echo   --verbose     显示详细信息
    pause
    exit /b 1
)

echo ========================================
echo     自动添加分类工具
echo ========================================
echo.

python tools\add_categories.py %*

pause
