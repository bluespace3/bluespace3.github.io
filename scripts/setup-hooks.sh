#!/bin/bash
# 安装 Git hooks 防止提交错误的 URL 配置

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "📦 安装 Git hooks..."

# 复制 pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# 防止提交包含 localhost URL 的 public/ 文件（结构性 URL）
# 注意：排除 post.backup/ 目录中的教程内容示例

if git diff --cached --name-only | grep -q "^public/"; then
    # 检查是否存在结构性 localhost URL（排除 post.backup）
    if git diff --cached -- public/ | grep --invert-match="post.backup" | grep -q "localhost:1313"; then
        echo "❌ 错误：public/ 目录包含结构性 localhost URL！"
        echo "请使用以下命令重新生成："
        echo "  hugo --cleanDestinationDir --environment production"
        exit 1
    fi
fi
EOF

chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ Git hooks 安装完成"
echo ""
echo "已安装的 hooks:"
echo "  - pre-commit: 防止提交包含 localhost URL 的 public/ 文件"
