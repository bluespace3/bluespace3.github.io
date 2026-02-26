# Hugo 博客管理

Hugo 博客项目的日常管理和维护工作。

## 项目结构

```
bluespace3.github.io/
├── content/          # 博客文章源文件
│   ├── post/        # 公开文章
│   └── archives/    # 加密文章
├── themes/          # Hugo 主题
├── static/          # 静态资源
├── layouts/         # 自定义布局
├── tools/           # 工具脚本
├── public/          # 生成的静态网站（用于本地预览）
├── hugo.toml        # Hugo 配置文件
└── .github/workflows/ # GitHub Actions 自动部署配置
```

## 部署方式

- **本地开发**：修改内容 → 生成到 `public/` → 本地预览
- **自动部署**：推送到 `main` 分支 → GitHub Actions 自动构建 → 发布到 `gh-pages` 分支

## 日常使用流程

### 1. 创建新文章

```bash
# 创建文章
hugo new post/我的文章.md

# 编辑文章
# 使用编辑器编辑 content/post/我的文章.md
```

### 2. 本地预览

```bash
# Windows
preview.bat

# Linux/macOS
./preview.sh

# 或直接运行
hugo server -D
```

访问 http://localhost:1313

### 3. 发布文章

```bash
# Windows - 一键发布
deploy.bat

# Linux/macOS - 一键发布
./deploy.sh
```

## 文章加密

### 使用 hugo-encryptor 加密文章

1. **在文章中添加加密标记**：

```markdown
---
title: "文章标题"
---

这是公开内容。

<!--more-->  <!-- 必须有 -->

{{% hugo-encryptor "你的密码" %}}

这里是加密内容...

{{% /hugo-encryptor %}}
```

2. **生成并加密**：

```bash
hugo --cleanDestinationDir
python tools/hugo_encryptor/hugo-encryptor.py
```

### 批量加密文章

```bash
# Windows - 加密整个目录
tools\batch-encrypt.bat content\archives 密码

# Linux/macOS
./tools/batch-encrypt.sh content/archives 密码
```

## 自动分类

根据文章所在目录自动添加分类：

```bash
# 预览会添加什么分类
tools\add-categories.bat content/post --dry-run

# 执行分类添加
tools\add-categories.bat content/post
```

## 主题配置

- **主题**：PaperMod
- **配置文件**：`hugo.toml`
- **自定义样式**：`static/css/`、`static/js/`

## 工具脚本

所有工具位于 `tools/` 目录：

- `batch-encrypt.*` - 批量加密文章
- `add_categories.*` - 自动添加分类
- `encrypt_file.py` - 单文件加密

## GitHub Actions 自动部署

推送代码到 `main` 分支后，自动：

1. 构建 Hugo 网站
2. 部署到 `gh-pages` 分支
3. GitHub Pages 自动更新

## 注意事项

1. **加密脚本**：每次生成网站后需要运行 `python tools/hugo_encryptor/hugo-encryptor.py`
2. **public 目录**：用于本地预览，正式发布由 GitHub Actions 处理
3. **主题更新**：PaperMod 主题是子模块，更新使用 `git submodule update --remote --merge`
4. **Python 版本**：需要 Python 3.x 运行加密脚本

## 相关文档

- [快速开始](./快速开始.md)
- [博客搭建指南](./博客搭建指南.md)
- [工具箱](./工具箱.md)
