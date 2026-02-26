#!/bin/bash
#
# 全量转换脚本 - 使用 GitHub API 更新所有文章时间
#

set -e  # 遇到错误立即退出

echo "================================================"
echo "🔄 全量转换 - 使用 GitHub API 更新文章时间"
echo "================================================"
echo ""

# 检查 GITHUB_TOKEN
if [ ! -f ".env" ]; then
    echo "❌ 未找到 .env 文件"
    echo ""
    echo "请先设置 GitHub Token："
    echo "1. 复制模板: cp .env.example .env"
    echo "2. 编辑文件: nano .env"
    echo "3. 填入 Token: GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx"
    echo ""
    exit 1
fi

# 加载环境变量
export $(grep -v '^#' .env | xargs)

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ .env 文件中未设置 GITHUB_TOKEN"
    exit 1
fi

echo "✅ GITHUB_TOKEN 已配置"
echo ""

# 检查 Python 依赖
echo "📦 检查 Python 依赖..."
if ! python3 -c "import requests, yaml" 2>/dev/null; then
    echo "❌ Python 依赖未安装"
    echo "正在安装..."
    pip install -r tools/requirements.txt
fi
echo "✅ Python 依赖已安装"
echo ""

# 询问是否预览
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 执行模式"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 预览模式（推荐） - 不实际修改文件，只显示将要进行的操作"
echo "2. 执行模式 - 实际修改所有文章文件"
echo ""
read -p "请选择模式 (1/2): " mode

echo ""

if [ "$mode" = "1" ]; then
    echo "================================================"
    echo "👀 预览模式"
    echo "================================================"
    echo ""
    python tools/sync_notes_from_github.py --batch content/post --dry-run --verbose

elif [ "$mode" = "2" ]; then
    echo "================================================"
    echo "🚀 执行模式"
    echo "================================================"
    echo ""
    echo "⚠️  警告：这将修改所有文章的 Front Matter！"
    echo ""
    read -p "确认执行？(yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        echo ""
        echo "🔄 开始同步所有文章..."
        echo ""
        python tools/sync_notes_from_github.py --batch content/post --verbose

        echo ""
        echo "================================================"
        echo "✅ 同步完成！"
        echo "================================================"
        echo ""
        echo "📊 后续步骤："
        echo ""
        echo "1. 本地预览验证："
        echo "   hugo server -D"
        echo ""
        echo "2. 查看文章归档："
        echo "   http://localhost:1313/archives/"
        echo ""
        echo "3. 确认无误后提交："
        echo "   git add ."
        echo "   git commit -m 'chore: 使用 GitHub API 更新文章时间'"
        echo "   git push origin main"
        echo ""
    else
        echo "❌ 取消执行"
        exit 0
    fi
else
    echo "❌ 无效选择"
    exit 1
fi
