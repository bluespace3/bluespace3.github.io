#!/bin/bash

# 一键部署Hugo博客到双仓库
# 此脚本将博客源码提交到私有仓库，并将构建的静态文件提交到公开仓库

# 配置
PRIVATE_REPO_URL="https://github.com/bluespace3/hugo-source-private.git"
PUBLIC_REPO_URL="https://github.com/bluespace3/bluespace3.github.io.git"

# 获取提交信息
COMMIT_MESSAGE="${1:-Update blog content}"

echo "开始部署博客..."

# 步骤1: 提交源码到私有仓库
echo ""
echo "步骤1: 提交源码到私有仓库..."

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "创建临时目录: $TEMP_DIR"

# 克隆私有仓库
if git clone "$PRIVATE_REPO_URL" "$TEMP_DIR"; then
    echo "克隆私有仓库成功"

    # 复制源码文件（排除构建输出）
    SOURCE_FILES=(
        ".gitignore"
        ".gitmodules"
        "README.md"
        "DEPLOY_KEY_SETUP.md"
        "hugo.toml"
        "manage-notes.py"
        "notes.md"
        "archetypes"
        "config"
        "content"
        "data"
        "layouts"
        "resources"
        "static"
        "themes"
    )

    echo "复制源码文件到私有仓库..."
    for file in "${SOURCE_FILES[@]}"; do
        if [ -e "$file" ]; then
            cp -r "$file" "$TEMP_DIR/"
            echo "  复制: $file"
        fi
    done

    # 提交到私有仓库
    cd "$TEMP_DIR"
    git add .

    if ! git diff --cached --quiet; then
        git commit -m "$COMMIT_MESSAGE"
        if git push origin main; then
            echo "✓ 源码已成功提交到私有仓库"
        else
            echo "✗ 推送到私有仓库失败"
            exit 1
        fi
    else
        echo "⚠ 没有新的更改需要提交到私有仓库"
    fi

    cd - > /dev/null

else
    echo "警告: 无法克隆私有仓库"
    echo "检查当前目录是否为私有仓库..."

    # 检查当前目录是否是私有仓库
    if git remote get-url origin | grep -q "hugo-source-private"; then
        echo "当前目录是私有仓库，直接提交"
        git add .
        if ! git diff --cached --quiet; then
            git commit -m "$COMMIT_MESSAGE"
            git push origin main
            echo "✓ 源码已成功提交到私有仓库"
        else
            echo "⚠ 没有新的更改需要提交到私有仓库"
        fi
    else
        echo "错误: 无法确定私有仓库位置"
        exit 1
    fi
fi

# 清理临时目录
rm -rf "$TEMP_DIR"

# 步骤2: 构建Hugo站点
echo ""
echo "步骤2: 构建Hugo站点..."

if command -v hugo &> /dev/null; then
    hugo --minify --environment production
    if [ $? -eq 0 ]; then
        echo "✓ Hugo站点构建成功"
    else
        echo "✗ Hugo站点构建失败"
        exit 1
    fi
else
    echo "错误: 未找到Hugo命令。请确保已安装Hugo。"
    exit 1
fi

# 步骤3: 提交构建的静态文件到公开仓库
echo ""
echo "步骤3: 提交构建的静态文件到公开仓库..."

# 检查当前目录是否是公开仓库
if git remote get-url origin | grep -q "bluespace3.github.io"; then
    echo "当前目录是公开仓库，直接提交构建结果"

    git add public/

    if ! git diff --cached --quiet; then
        git commit -m "build: 更新博客"
        if git push origin main; then
            echo "✓ 静态文件已成功提交到公开仓库"
        else
            echo "✗ 推送到公开仓库失败"
            exit 1
        fi
    else
        echo "⚠ 没有新的构建结果需要提交"
    fi
else
    echo "错误: 当前目录不是公开仓库。请在公开仓库目录中运行此脚本。"
    exit 1
fi

echo ""
echo "✅ 博客部署完成！"