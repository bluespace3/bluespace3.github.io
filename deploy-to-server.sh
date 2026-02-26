#!/bin/bash
#
# 部署到 Ubuntu 服务器
# 用法: ./deploy-to-server.sh [服务器名称]
#

# 服务器配置
SERVER_HOST="${1:-openclaw}"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="~/.ssh/id_rsa_new"
REMOTE_DIR="/var/www/bluespace3.github.io"
REPO_URL="https://github.com/bluespace3/bluespace3.github.io.git"

echo "================================================"
echo "🚀 部署到服务器: $SERVER_HOST"
echo "================================================"
echo ""

# 检查 SSH 连接
echo "📡 测试 SSH 连接..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "echo '✅ SSH 连接成功'" || {
    echo "❌ SSH 连接失败"
    echo "请检查："
    echo "1. 服务器地址是否正确: $SERVER_HOST"
    echo "2. SSH 密钥是否存在: $SSH_KEY"
    echo "3. 网络连接是否正常"
    exit 1
}

# 安装系统依赖
echo ""
echo "📦 安装系统依赖..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
# 更新包管理器
apt-get update -qq

# 安装必要的软件
echo "安装 Python 3 和 pip..."
apt-get install -y python3 python3-pip python3-venv git

# 安装 Hugo（如果未安装）
if ! command -v hugo &> /dev/null; then
    echo "安装 Hugo..."
    wget -q https://github.com/gohugoio/hugo/releases/download/v0.128.0/hugo_extended_0.128.0_linux-amd64.deb -O /tmp/hugo.deb
    dpkg -i /tmp/hugo.deb
    rm /tmp/hugo.deb
fi

echo "✅ 系统依赖安装完成"
ENDSSH

# 创建项目目录
echo ""
echo "📁 创建项目目录..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
mkdir -p $REMOTE_DIR
cd $REMOTE_DIR

# 如果不是 git 仓库，则克隆
if [ ! -d ".git" ]; then
    echo "📥 克隆项目仓库..."
    git clone $REPO_URL .
else
    echo "📥 拉取最新代码..."
    git fetch --all
    git reset --hard origin/main
fi
ENDSSH

# 上传 .env 文件（如果本地有）
if [ -f ".env" ]; then
    echo ""
    echo "📤 上传 .env 文件..."
    scp -i $SSH_KEY -P $SERVER_PORT .env $SERVER_USER@$SERVER_HOST:$REMOTE_DIR/
    echo "✅ .env 文件已上传"
else
    echo ""
    echo "⚠️  未找到 .env 文件"
    echo "请在服务器上手动创建："
    echo "  ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST"
    echo "  cd $REMOTE_DIR"
    echo "  cp .env.example .env"
    echo "  nano .env  # 填入你的 GITHUB_TOKEN"
fi

# 安装 Python 依赖
echo ""
echo "🐍 安装 Python 依赖..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $REMOTE_DIR

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
ENDSSH

# 测试运行同步脚本
echo ""
echo "🧪 测试同步脚本..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $REMOTE_DIR
source venv/bin/activate

# 预览模式测试
python tools/sync_notes_from_github.py --batch content/post --dry-run --verbose
ENDSSH

echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo ""
echo "📝 后续步骤："
echo "1. 连接到服务器："
echo "   ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST"
echo ""
echo "2. 进入项目目录："
echo "   cd $REMOTE_DIR"
echo ""
echo "3. 运行同步脚本："
echo "   source venv/bin/activate"
echo "   python tools/sync_notes_from_github.py --batch content/post"
echo ""
echo "4. 构建和部署博客："
echo "   hugo --minify"
echo ""
