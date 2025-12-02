---
title: 'Hugo静态网站生成器入门指南'
categories: ["技术"]
date: 2025-12-02T15:13:19+00:00
lastmod: 2025-12-02T15:39:38+00:00
encrypted: false
password: "123456"
---
















## 什么是Hugo？

Hugo是一个用Go语言编写的快速、现代的静态网站生成器。它可以将Markdown文件转换为HTML页面，非常适合构建文档网站、博客等。

## Hugo的主要特点

- 极快的构建速度
- 丰富的主题支持
- 简单的Markdown内容管理
- 强大的模板系统
- 内置的短代码功能

## 安装Hugo

在Windows上安装Hugo的步骤：

1. 下载Hugo的Windows版本
2. 解压到指定目录
3. 将Hugo的可执行文件路径添加到系统环境变量

## 创建新站点

使用以下命令创建一个新的Hugo站点：

```bash
hugo new site mydocs
```

## 下载插件

## 添加内容

在content目录下创建Markdown文件来添加内容：

```bash
hugo new blog/my-first-post.md
```

## 运行开发服务器

使用以下命令启动开发服务器：

```bash
hugo server -D --environment development #如果未设置环境变量则不需要指定环境。
```

## 部署网站

使用以下命令生成静态文件：

```bash
hugo
```

1. 然后将public目录下的文件部署到Web服务器即可，注意每次推送前运行hugo更新public文件夹
2. 若有更新域名，请删除public后，再运行hugo重新生成public，否则会出现路由错误的情况。
3. 为了方便新建.sh脚本文件，命名为.command.sh

```bash
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
```

4. 终端运行 .\.command.sh

## 更新维护

后期维护有许多要留意的地方否则容易踩坑。

1. 新增文章，在项目根目录终端运行，hugo new content/post/文章名称 不同主题博客目录不一致，这里需要留意你下载主题的说明。
2. 生成的文章会自带字段，其中draft默认true需要维护成false或者删掉，否则视为草稿。如下：

   ```
   title: "测试平台教程"

   date: 2025-03-20T12:59:32+08:00

   draft: false

   tags: ["测试平台", "静态网站", "教程"]
   ```

3.若只有一台电脑更新博客，可以只把public托管到github，若要多个终端更新。需要满足以下条件。

* 终端的hugo版本和主题保持需要保持一致，建议把主题配置在hugo.toml文件里面。否则本地有多个主题时在运行时要指定主题。

  `hugo -t hugo-theme-reimu`
* 需要把整个项目推到github，并且指定githubPage为存放public的分支。需要建立工作流，脚本如下。

  ```bash
  name: Deploy Hugo site

  on:
    push:
      branches:
        - main  # 或者你的默认分支名

  jobs:
    deploy:
      runs-on: ubuntu-latest
      permissions:
        contents: write  # Ensure GITHUB_TOKEN has write access to contents
      steps:
        - uses: actions/checkout@v3
          with:
            submodules: false  # 确保自动拉取子模块
            fetch-depth: 0    # 获取所有历史记录和标签

        - name: Setup Hugo
          uses: peaceiris/actions-hugo@v2
          with:
            hugo-version: 'latest'
            extended: true

        - name: Build
          run: hugo --minify

        - name: Deploy
          uses: peaceiris/actions-gh-pages@v3
          with:
            github_token: ${{ secrets.GITHUB_TOKEN }}
            publish_dir: ./public
            publish_branch: gh-pages  # 部署到gh-pages分支
  ```

## 总结

Hugo是一个功能强大且易于使用的静态网站生成器，非常适合构建个人博客、文档网站等。

优点是能快速构建，丰富的模板生态，方便的托管到github，后期维护成本低。

缺点：只支持md格式，不支持在线编辑，因为只支持通过代码push到远程仓库更新，所以在切换终端时简直是噩梦，笔者在此处踩坑无数，特别需要注意这里。
