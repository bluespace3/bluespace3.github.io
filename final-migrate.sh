#!/bin/bash
SSH_KEY="/c/Users/Administrator/.ssh/id_rsa_new"
SERVER_IP="38.55.39.104"
SERVER_USER="root"
SERVER_PORT="22"
REMOTE_DIR="/var/www/bluespace3.github.io"
REPO_URL="https://github.com/bluespace3/bluespace3.github.io.git"

echo "================================================"
echo "🚀 重新迁移项目到服务器"
echo "================================================"
echo ""

# 1. 删除旧目录
echo "🗑️  删除旧的项目目录..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_IP "rm -rf $REMOTE_DIR && echo '✅ 旧目录已删除'"

# 2. 重新克隆
echo ""
echo "📥 重新克隆项目（main 分支）..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www
git clone --branch main --single-branch $REPO_URL $REMOTE_DIR
cd $REMOTE_DIR

echo ""
echo "✅ 项目克隆完成"
echo ""
echo "📁 项目目录内容:"
ls -la | head -30

echo ""
echo "📁 tools 目录:"
ls -la tools/ | head -20

echo ""
echo "📄 关键文件检查:"
for file in .env.example tools/requirements.txt tools/sync_notes_from_github.py tools/github_api.py; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done
EOF

# 3. 创建虚拟环境并安装依赖
echo ""
echo "🐍 创建虚拟环境并安装依赖..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/bluespace3.github.io
python3 -m venv venv
source venv/bin/activate
pip install --quiet -r tools/requirements.txt
echo "✅ Python 依赖安装完成"
EOF

# 4. 创建 .env 文件
echo ""
echo "📝 创建 .env 文件..."
ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/bluespace3.github.io
if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ .env 文件已创建（模板）"
    echo "⚠️  需要手动填入 GITHUB_TOKEN"
else
    echo "⚠️  .env.example 不存在"
fi
EOF

echo ""
echo "================================================"
echo "✅ 迁移完成！"
echo "================================================"
echo ""
echo "📝 下一步："
echo ""
echo "1. SSH 连接到服务器配置 GITHUB_TOKEN:"
echo "   ssh -i $SSH_KEY -p $SERVER_PORT $SERVER_USER@$SERVER_IP"
echo "   cd $REMOTE_DIR"
echo "   nano .env"
echo ""
echo "2. 运行同步脚本测试:"
echo "   source venv/bin/activate"
echo "   python tools/sync_notes_from_github.py --batch content/post --dry-run"
echo ""
