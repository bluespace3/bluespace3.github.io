#!/usr/bin/env pwsh

<#
.SYNOPSIS
    一键部署Hugo博客到双仓库
.DESCRIPTION
    此脚本将博客源码提交到私有仓库，并将构建的静态文件提交到公开仓库
#>

# 配置仓库URL
$PRIVATE_REPO_URL = "https://github.com/bluespace3/hugo-source-private.git"
$PUBLIC_REPO_URL = "https://github.com/bluespace3/bluespace3.github.io.git"

# 获取提交信息
if ($args.Count -gt 0) {
    $COMMIT_MESSAGE = $args[0]
} else {
    $COMMIT_MESSAGE = "Update blog content"
}

Write-Host "开始部署博客..." -ForegroundColor Green

# 步骤1: 提交源码到私有仓库
Write-Host "`n步骤1: 提交源码到私有仓库..." -ForegroundColor Yellow

# 创建临时目录用于私有仓库
$TEMP_DIR = Join-Path $env:TEMP "hugo-source-private-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

try {
    # 克隆私有仓库到临时目录
    Write-Host "克隆私有仓库到临时目录..."
    git clone $PRIVATE_REPO_URL $TEMP_DIR

    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告: 无法克隆私有仓库。可能需要先手动克隆私有仓库。" -ForegroundColor Red
        Write-Host "请确保你有访问私有仓库的权限。" -ForegroundColor Red

        # 如果克隆失败，尝试检查当前目录是否已经是私有仓库
        $current_remote = git config --get remote.origin.url
        if ($current_remote -like "*hugo-source-private*") {
            Write-Host "当前目录似乎是私有仓库，直接使用当前目录进行提交。" -ForegroundColor Yellow
            $USE_CURRENT_DIR = $true
        } else {
            Write-Host "错误: 无法确定私有仓库位置。" -ForegroundColor Red
            exit 1
        }
    } else {
        $USE_CURRENT_DIR = $false
        # 复制源码文件到私有仓库临时目录
        Write-Host "复制源码文件到私有仓库..."

        # 定义需要复制的源码文件和目录（排除构建输出目录）
        $source_files = @(
            ".gitignore",
            ".gitmodules",
            "README.md",
            "DEPLOY_KEY_SETUP.md",
            "hugo.toml",
            "manage-notes.py",
            "notes.md",
            "archetypes",
            "config",
            "content",
            "data",
            "layouts",
            "resources",
            "static",
            "themes"
        )

        foreach ($file in $source_files) {
            $source_path = Join-Path $PSScriptRoot $file
            $dest_path = Join-Path $TEMP_DIR $file

            if (Test-Path $source_path) {
                if (Test-Path $source_path -PathType Container) {
                    Copy-Item -Path $source_path -Destination $dest_path -Recurse -Force
                } else {
                    Copy-Item -Path $source_path -Destination $dest_path -Force
                }
                Write-Host "  复制: $file"
            }
        }
    }

    # 提交到私有仓库
    if ($USE_CURRENT_DIR) {
        $repo_dir = $PSScriptRoot
    } else {
        $repo_dir = $TEMP_DIR
    }

    Set-Location $repo_dir

    # 添加所有更改
    git add .

    # 检查是否有更改需要提交
    $status = git status --porcelain
    if ($status) {
        git commit -m "$COMMIT_MESSAGE"
        if ($LASTEXITCODE -eq 0) {
            git push origin main
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ 源码已成功提交到私有仓库" -ForegroundColor Green
            } else {
                Write-Host "✗ 推送到私有仓库失败" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "⚠ 没有新的更改需要提交到私有仓库" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ 没有新的更改需要提交到私有仓库" -ForegroundColor Yellow
    }

} finally {
    # 清理临时目录
    if (-not $USE_CURRENT_DIR -and (Test-Path $TEMP_DIR)) {
        Remove-Item -Path $TEMP_DIR -Recurse -Force
    }
}

# 步骤2: 构建Hugo站点
Write-Host "`n步骤2: 构建Hugo站点..." -ForegroundColor Yellow
Set-Location $PSScriptRoot

if (Get-Command hugo -ErrorAction SilentlyContinue) {
    hugo --minify --environment production
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Hugo站点构建成功" -ForegroundColor Green
    } else {
        Write-Host "✗ Hugo站点构建失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "错误: 未找到Hugo命令。请确保已安装Hugo。" -ForegroundColor Red
    exit 1
}

# 步骤3: 提交构建的静态文件到公开仓库
Write-Host "`n步骤3: 提交构建的静态文件到公开仓库..." -ForegroundColor Yellow

# 检查当前目录是否是公开仓库
$current_remote = git config --get remote.origin.url
if ($current_remote -like "*bluespace3.github.io*") {
    Write-Host "当前目录是公开仓库，直接提交构建结果。"

    # 添加构建的文件
    git add public/

    # 检查是否有更改需要提交
    $status = git status --porcelain
    if ($status) {
        git commit -m "build: 更新博客"
        if ($LASTEXITCODE -eq 0) {
            git push origin main
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ 静态文件已成功提交到公开仓库" -ForegroundColor Green
            } else {
                Write-Host "✗ 推送到公开仓库失败" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "⚠ 没有新的构建结果需要提交" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ 没有新的构建结果需要提交" -ForegroundColor Yellow
    }
} else {
    Write-Host "错误: 当前目录不是公开仓库。请在公开仓库目录中运行此脚本。" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ 博客部署完成！" -ForegroundColor Green