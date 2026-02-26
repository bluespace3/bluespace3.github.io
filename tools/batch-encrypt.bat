@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 批量加密文章脚本 - Windows 版本
REM 使用方法: batch-encrypt.bat <目录路径> <密码>
REM 示例: batch-encrypt.bat content\archives tian123456

if "%~1"=="" (
    echo 使用方法: %~nx0 <目录路径> <密码>
    echo 示例: %~nx0 content\archives tian123456
    exit /b 1
)

if "%~2"=="" (
    echo 使用方法: %~nx0 <目录路径> <密码>
    echo 示例: %~nx0 content\archives tian123456
    exit /b 1
)

set "TARGET_DIR=%~1"
set "PASSWORD=%~2"

echo ========================================
echo        批量加密文章脚本
echo ========================================
echo.
echo 目标目录: %TARGET_DIR%
echo 加密密码: %PASSWORD%
echo.

REM 检查目录是否存在
if not exist "%TARGET_DIR%" (
    echo ❌ 错误：目录不存在: %TARGET_DIR%
    exit /b 1
)

REM 计数器
set total=0
set success=0
set failed=0

REM 遍历所有 markdown 文件
for %%f in ("%TARGET_DIR%\*.md") do (
    set /a total+=1
    set "filename=%%~nxf"
    echo [!total!] 处理: !filename!

    REM 调用 Python 脚本处理单个文件
    python -c "import sys; sys.path.insert(0, '.'); exec(open('tools/encrypt_file.py').read())" "%%f" "%PASSWORD%"

    if !errorlevel! equ 0 (
        set /a success+=1
        echo    ✅ 加密成功
    ) else (
        set /a failed+=1
        echo    ❌ 加密失败
    )
)

echo.
echo ========================================
echo        处理完成
echo ========================================
echo 总数: %total%
echo 成功: %success%
echo 失败: %failed%
echo.

pause
