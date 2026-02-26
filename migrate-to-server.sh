#!/bin/bash
#
# 迁移项目到 Ubuntu 服务器
# 用法: ./migrate-to-server.sh
#

# 服务器配置
SERVER_HOST="openclaw"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="~/.ssh/id_rsa_new"
REMOTE_DIR="/var/www/bluespace3.github.io"
REPO_URL="https://github.com/bluespace3/bluespace3.github.io.git"

echo "================================================"
echo "🚀 迁移项目到服务器: $SERVER_HOST"
echo "================================================"
echo ""

# 检查 SSH 连接
echo "📡 测试 SSH 连接..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST "echo '✅ SSH 连接成功'" || {
    echo "❌ SSH 连接失败"
    exit 1
}

# 安装系统依赖
echo ""
echo "📦 安装系统依赖..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'ENDSSH'
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv git
echo "✅ 系统依赖安装完成"
ENDSSH

# 克隆项目到服务器
echo ""
echo "📁 克隆项目到服务器..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
# 创建目录
mkdir -p $REMOTE_DIR

# 克隆项目（如果还不存在）
if [ ! -d "$REMOTE_DIR/.git" ]; then
    echo "📥 克隆项目仓库..."
    git clone $REPO_URL $REMOTE_DIR
else
    echo "📥 项目已存在，拉取最新代码..."
    cd $REMOTE_DIR
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
    echo "  nano .env"
fi

# 安装 Python 依赖
echo ""
echo "🐍 安装 Python 依赖..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << ENDSSH
cd $REMOTE_DIR

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --quiet -r tools/requirements.txt
echo "✅ Python 依赖安装完成"
ENDSSH

echo ""
echo "================================================"
echo "✅ 项目迁移完成！"
echo "================================================"
echo ""
echo "📝 后续步骤："
echo ""
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
echo "4. 提交并推送到 GitHub："
echo "   git add ."
echo "   git commit -m 'chore: 更新文章时间'"
echo "   git push origin main"
echo ""
echo "5. GitHub Actions 会自动部署到 GitHub Pages"
echo ""
