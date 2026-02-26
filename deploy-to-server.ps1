# 部署到 Ubuntu 服务器 - Windows PowerShell 版本
# 用法: .\deploy-to-server.ps1 [服务器名称]

param(
    [string]$ServerHost = "openclaw",
    [string]$ServerUser = "root",
    [string]$ServerPort = "22",
    [string]$SSHKey = "~\.ssh\id_rsa_new",
    [string]$RemoteDir = "/var/www/bluespace3.github.io",
    [string]$RepoUrl = "https://github.com/bluespace3/bluespace3.github.io.git"
)

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

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

# 开始部署
Write-Header "🚀 部署到服务器: $ServerHost"

# 检查 SSH 客户端
Write-Step "📡 检查 SSH 客户端..."
try {
    $sshTest = ssh -V 2>&1
    Write-Host "✅ SSH 客户端已安装: $sshTest" -ForegroundColor Green
} catch {
    Write-Error "❌ 未找到 SSH 客户端"
    Write-Host "请安装 OpenSSH 客户端：" -ForegroundColor Yellow
    Write-Host "1. Windows 10/11: 设置 → 应用 → 可选功能 → 添加 OpenSSH 客户端" -ForegroundColor Yellow
    Write-Host "2. 或使用 Git Bash" -ForegroundColor Yellow
    exit 1
}

# 检查 SSH 密钥
$SSHKeyPath = $SSHKey -replace '~', $env:USERPROFILE
if (-not (Test-Path $SSHKeyPath)) {
    Write-Error "❌ SSH 密钥不存在: $SSHKeyPath"
    exit 1
}

# 测试 SSH 连接
Write-Step "📡 测试 SSH 连接..."
try {
    $result = ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost "echo '连接成功'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH 连接成功" -ForegroundColor Green
    } else {
        throw "SSH 连接失败"
    }
} catch {
    Write-Error "❌ SSH 连接失败"
    Write-Host "请检查：" -ForegroundColor Yellow
    Write-Host "1. 服务器地址是否正确: $ServerHost" -ForegroundColor Yellow
    Write-Host "2. SSH 密钥是否存在: $SSHKeyPath" -ForegroundColor Yellow
    Write-Host "3. 网络连接是否正常" -ForegroundColor Yellow
    exit 1
}

# 安装系统依赖
Write-Step "📦 安装系统依赖..."
$installCommands = @"
# 更新包管理器
apt-get update -qq

# 安装必要的软件
echo "安装 Python 3 和 pip..."
apt-get install -y python3 python3-pip python3-venv git > /dev/null 2>&1

# 安装 Hugo（如果未安装）
if ! command -v hugo &> /dev/null; then
    echo "安装 Hugo..."
    wget -q https://github.com/gohugoio/hugo/releases/download/v0.128.0/hugo_extended_0.128.0_linux-amd64.deb -O /tmp/hugo.deb
    dpkg -i /tmp/hugo.deb 2>/dev/null
    rm /tmp/hugo.deb
fi

echo "✅ 系统依赖安装完成"
"@

ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost $installCommands
if ($LASTEXITCODE -ne 0) {
    Write-Warning "⚠️  系统依赖安装可能有问题，但继续部署..."
}

# 创建项目目录
Write-Step "📁 创建项目目录..."
$setupCommands = @"
mkdir -p $RemoteDir
cd $RemoteDir

# 如果不是 git 仓库，则克隆
if [ ! -d ".git" ]; then
    echo "📥 克隆项目仓库..."
    git clone $RepoUrl .
else
    echo "📥 拉取最新代码..."
    git fetch --all
    git reset --hard origin/main
fi
"@

ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost $setupCommands
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ 项目设置失败"
    exit 1
}

# 上传 .env 文件（如果本地有）
if (Test-Path ".env") {
    Write-Step "📤 上传 .env 文件..."
    scp -i $SSHKeyPath -P $ServerPort .env "${ServerUser}@${ServerHost}:${RemoteDir}/"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ .env 文件已上传" -ForegroundColor Green
    }
} else {
    Write-Warning "⚠️  未找到 .env 文件"
    Write-Host "请在服务器上手动创建：" -ForegroundColor Yellow
    Write-Host "  ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost" -ForegroundColor Yellow
    Write-Host "  cd $RemoteDir" -ForegroundColor Yellow
    Write-Host "  cp .env.example .env" -ForegroundColor Yellow
    Write-Host "  nano .env  # 填入你的 GITHUB_TOKEN" -ForegroundColor Yellow
}

# 安装 Python 依赖
Write-Step "🐍 安装 Python 依赖..."
$pythonCommands = @"
cd $RemoteDir

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "安装 Python 包..."
source venv/bin/activate
pip install --quiet -r tools/requirements.txt
echo "✅ Python 依赖安装完成"
"@

ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost $pythonCommands
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Python 依赖安装失败"
    exit 1
}

# 测试运行同步脚本
Write-Step "🧪 测试同步脚本（预览模式）..."
$testCommand = @"
cd $RemoteDir
source venv/bin/activate
python tools/sync_notes_from_github.py --batch content/post --dry-run --verbose 2>&1 | head -20
"@

ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost $testCommand
Write-Host ""

# 完成
Write-Header "✅ 部署完成！"

Write-Host ""
Write-Host "📝 后续步骤：" -ForegroundColor Cyan
Write-Host "1. 连接到服务器：" -ForegroundColor White
Write-Host "   ssh -i $SSHKeyPath -p $ServerPort $ServerUser@$ServerHost" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. 进入项目目录：" -ForegroundColor White
Write-Host "   cd $RemoteDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. 运行同步脚本：" -ForegroundColor White
Write-Host "   source venv/bin/activate" -ForegroundColor Yellow
Write-Host "   python tools/sync_notes_from_github.py --batch content/post" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. 构建博客：" -ForegroundColor White
Write-Host "   hugo --minify" -ForegroundColor Yellow
Write-Host ""
