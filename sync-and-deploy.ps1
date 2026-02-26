# 在服务器上同步笔记并部署到 GitHub Pages - Windows PowerShell 版本
# 用法: .\sync-and-deploy.ps1

param(
    [string]$ServerHost = "openclaw",
    [string]$ServerUser = "root",
    [string]$ServerPort = "22",
    [string]$SSHKey = "~\.ssh\id_rsa_new",
    [string]$RemoteDir = "/var/www/bluespace3.github.io"
)

$ErrorActionPreference = "Stop"

$SSHKeyPath = $SSHKey -replace '~', $env:USERPROFILE

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🔄 服务器同步并部署到 GitHub Pages" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 在服务器上执行命令
$remoteCommand = @"
cd $RemoteDir

echo "📅 激活 Python 虚拟环境..."
source venv/bin/activate

echo "🔄 同步笔记（使用 GitHub API 获取真实时间）..."
python tools/sync_notes_from_github.py --batch content/post

echo ""
echo "📊 检查 Git 状态..."
git status

echo ""
echo "📝 提交更改..."
git add .
git commit -m "chore: 使用 GitHub API 更新文章时间

- 使用 sync_notes_from_github.py 同步笔记
- 通过 GitHub API 获取文件真实创建和更新时间
- 自动生成 Hugo Front Matter
- 时间转换为东八区 (+08:00)

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "📤 推送到 GitHub..."
git push origin main

echo ""
echo "✅ 推送成功！"
echo "🌐 GitHub Actions 将自动构建并部署到 GitHub Pages"
echo "🔗 访问 https://bluespace3.github.io/ 查看更新"
"@

Write-Host "📡 连接到服务器并执行同步..." -ForegroundColor Green
ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost $remoteCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "✅ 部署完成！" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 查看 GitHub Actions 部署状态：" -ForegroundColor White
    Write-Host "🔗 https://github.com/bluespace3/bluespace3.github.io/actions" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🌐 访问博客：" -ForegroundColor White
    Write-Host "🔗 https://bluespace3.github.io/" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ 部署失败" -ForegroundColor Red
    Write-Host "请检查错误信息" -ForegroundColor Yellow
    exit 1
}
