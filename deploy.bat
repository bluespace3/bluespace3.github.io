@echo off
chcp 65001 >nul
echo ========================================
echo       博客自动化部署脚本
echo ========================================
echo.

echo [0/5] 正在检查加密文件...
if not exist "static\decrypt.js" (
    echo 📁 复制 decrypt.js 到 static 目录...
    copy "tools\hugo_encryptor\decrypt.js" "static\" >nul
    if %errorlevel% equ 0 (
        echo ✅ decrypt.js 复制成功
    ) else (
        echo ⚠️  decrypt.js 复制失败，请手动检查
    )
) else (
    echo ✅ decrypt.js 已存在
)
echo.

echo [1/5] 正在生成网站...
hugo --cleanDestinationDir
if %errorlevel% neq 0 (
    echo ❌ 网站生成失败！
    pause
    exit /b 1
)
echo ✅ 网站生成成功
echo.

echo [2/5] 正在加密文章...
python tools/hugo_encryptor/hugo-encryptor.py
if %errorlevel% neq 0 (
    echo ⚠️  加密失败或没有需要加密的文章
) else (
    echo ✅ 文章加密成功
)
echo.

echo [3/5] 正在提交到 Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ Git add 失败！
    pause
    exit /b 1
)
echo ✅ 文件已添加到暂存区
echo.

echo [4/5] 正在推送到 GitHub...
set commit_msg=自动部署: %date% %time%
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo ⚠️  没有新的更改需要提交
) else (
    echo ✅ 提交成功
    git push origin main
    if %errorlevel% neq 0 (
        echo ❌ 推送失败！请检查网络连接或 GitHub 权限
        pause
        exit /b 1
    )
    echo ✅ 推送成功
)
echo.

echo ========================================
echo       🎉 部署完成！
echo ========================================
echo.
echo 博客地址: https://bluespace.eu.org/
echo.

pause
