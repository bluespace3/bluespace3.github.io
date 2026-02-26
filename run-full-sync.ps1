# 全量转换脚本 - Windows PowerShell 版本
# 使用 GitHub API 更新所有文章时间

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Error-Host {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

# 开始
Write-Header "🔄 全量转换 - 使用 GitHub API 更新文章时间"

# 检查 .env 文件
Write-Step "📋 检查配置文件..."

if (-not (Test-Path ".env")) {
    Write-Error-Host "❌ 未找到 .env 文件"
    Write-Host ""
    Write-Host "请先设置 GitHub Token：" -ForegroundColor Yellow
    Write-Host "1. 复制模板: cp .env.example .env" -ForegroundColor White
    Write-Host "2. 编辑文件: notepad .env" -ForegroundColor White
    Write-Host "3. 填入 Token: GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx" -ForegroundColor White
    Write-Host ""
    exit 1
}

# 读取并检查 GITHUB_TOKEN
$envContent = Get-Content ".env"
$githubToken = $envContent | Where-Object { $_ -match "^GITHUB_TOKEN=" } | ForEach-Object { $_.Split("=")[1] }

if ([string]::IsNullOrEmpty($githubToken) -or $githubToken -eq "your_token_here") {
    Write-Error-Host "❌ .env 文件中未设置 GITHUB_TOKEN"
    Write-Host ""
    Write-Host "请编辑 .env 文件并填入你的 GitHub Token" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ GITHUB_TOKEN 已配置" -ForegroundColor Green
Write-Host ""

# 检查 Python 依赖
Write-Step "📦 检查 Python 依赖..."

try {
    $null = python -c "import requests, yaml" 2>$null
    Write-Host "✅ Python 依赖已安装" -ForegroundColor Green
} catch {
    Write-Warning "⚠️  Python 依赖未安装，正在安装..."
    pip install -r tools/requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 依赖安装成功" -ForegroundColor Green
    } else {
        Write-Error-Host "❌ Python 依赖安装失败"
        exit 1
    }
}

Write-Host ""

# 选择执行模式
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📝 执行模式" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 预览模式（推荐）- 不实际修改文件，只显示将要进行的操作" -ForegroundColor White
Write-Host "2. 执行模式 - 实际修改所有文章文件" -ForegroundColor White
Write-Host ""

$mode = Read-Host "请选择模式 (1/2)"

Write-Host ""

if ($mode -eq "1") {
    # 预览模式
    Write-Header "👀 预览模式"
    Write-Host ""

    python tools/sync_notes_from_github.py --batch content/post --dry-run --verbose

} elseif ($mode -eq "2") {
    # 执行模式
    Write-Header "🚀 执行模式"
    Write-Host ""
    Write-Warning "⚠️  警告：这将修改所有文章的 Front Matter！"
    Write-Host ""

    $confirm = Read-Host "确认执行？(yes/no)"

    if ($confirm -eq "yes") {
        Write-Host ""
        Write-Step "🔄 开始同步所有文章..."
        Write-Host ""

        python tools/sync_notes_from_github.py --batch content/post --verbose

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Header "✅ 同步完成！"
            Write-Host ""
            Write-Host "📊 后续步骤：" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "1. 本地预览验证：" -ForegroundColor White
            Write-Host "   hugo server -D" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "2. 查看文章归档：" -ForegroundColor White
            Write-Host "   http://localhost:1313/archives/" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "3. 确认无误后提交：" -ForegroundColor White
            Write-Host "   git add ." -ForegroundColor Yellow
            Write-Host "   git commit -m 'chore: 使用 GitHub API 更新文章时间'" -ForegroundColor Yellow
            Write-Host "   git push origin main" -ForegroundColor Yellow
            Write-Host ""
        } else {
            Write-Host ""
            Write-Error-Host "❌ 同步过程中出现错误"
            exit 1
        }
    } else {
        Write-Host "❌ 取消执行" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Error-Host "❌ 无效选择"
    exit 1
}
