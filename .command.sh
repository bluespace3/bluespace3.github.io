#加载静态文件
hugo --minify 

# 判断是否已初始化Git仓库
if [ ! -d ".git" ]; then
    echo "未检测到Git仓库，正在初始化..."
    git init
else
    echo "Git仓库已初始化"
fi

# 创建.gitignore文件，排除不需要版本控制的文件
cat > .gitignore << EOF
resources/
.DS_Store
node_modules/
.hugo_build.lock
EOF

# 添加所有文件
git add .

# 提交更改
git commit -m "更新博客" 

# 检查是否已关联远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    echo "未检测到远程仓库，正在添加..."
    git remote add origin https://github.com/bluespace3/bluespace3.github.io
else
    echo "已关联远程仓库：$REMOTE_URL"
fi

# 推送到GitHub
git push -u origin main --force