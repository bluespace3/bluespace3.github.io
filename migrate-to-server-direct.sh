#!/bin/bash
#
# 迁移项目到 Ubuntu 服务器（使用 IP 地址）
#

# 服务器配置
SERVER_IP="38.55.39.104"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="~/.ssh/id_rsa_new"
REMOTE_DIR="/var/www/bluespace3.github.io"
REPO_URL="https://github.com/bluespace3/bluespace3.github.io.git"

echo "================================================"
echo "🚀 迁移项目到服务器: $SERVER_IP"
echo "================================================"
echo ""

# 检查 SSH 密钥
SSH_KEY_FULL=$SSH_KEY
if [[ $SSH_KEY == ~/* ]]; then
    SSH_KEY_FULL="$HOME/${SSH_KEY:2}"
fi

if [ ! -f "$SSH_KEY_FULL" ]; then
    echo "❌ SSH 密钥不存在: $SSH_KEY_FULL"
    echo "请检查密钥路径"
    exit 1
fi

echo "🔑 使用 SSH 密钥: $SSH_KEY_FULL"

# 测试 SSH 连接
echo ""
echo "📡 测试 SSH 连接..."
ssh -i $SSH_KEY_FULL -p $SERVER_PORT -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "echo '✅ SSH 连接成功'" || {
    echo "❌ SSH 连接失败"
    echo "请检查："
    echo "1. 服务器 IP 是否正确: $SERVER_IP"
    echo "2. SSH 密钥是否存在: $SSH_KEY_FULL"
    echo "3. 服务器是否运行且端口 22 开放"
    exit 1
}

# 安装系统依赖
echo ""
echo "📦 安装系统依赖..."
ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'ENDSSH'
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv git
echo "✅ 系统依赖安装完成"
ENDSSH

# 克隆项目到服务器
echo ""
echo "📁 克隆项目到服务器..."
ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP << ENDSSH
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
    scp -i $SSH_KEY_FULL -P $SERVER_PORT .env $SERVER_USER@$SERVER_IP:$REMOTE_DIR/
    echo "✅ .env 文件已上传"
else
    echo ""
    echo "⚠️  未找到 .env 文件"
    echo "将在服务器上创建 .env 文件..."
    ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP << ENDSSH
cd $REMOTE_DIR
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件并填入 GITHUB_TOKEN:"
    echo "  ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP"
    echo "  cd $REMOTE_DIR"
    echo "  nano .env"
fi
ENDSSH
fi

# 安装 Python 依赖
echo ""
echo "🐍 安装 Python 依赖..."
ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP << ENDSSH
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
echo "   ssh -i $SSH_KEY_FULL -p $SERVER_PORT $SERVER_USER@$SERVER_IP"
echo ""
echo "2. 进入项目目录："
echo "   cd $REMOTE_DIR"
echo ""
echo "3. 配置 GITHUB_TOKEN（如果还没有）："
echo "   cp .env.example .env"
echo "   nano .env  # 填入你的 GitHub Token"
echo ""
echo "4. 运行同步脚本："
echo "   source venv/bin/activate"
echo "   python tools/sync_notes_from_github.py --batch content/post"
echo ""
echo "5. 提交并推送到 GitHub："
echo "   git add ."
echo "   git commit -m 'chore: 更新文章时间'"
echo "   git push origin main"
echo ""
echo "6. GitHub Actions 会自动部署到 GitHub Pages"
echo ""
