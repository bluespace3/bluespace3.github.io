# Hugo博客双仓库部署方案

## 项目说明

本项目采用双仓库部署方案：

- **私有仓库 (hugo-source-private)**: 存储博客源码
- **公开仓库 (bluespace3.github.io)**: 存储生成的静态文件，用于GitHub Pages展示

## 部署流程

1. 源码保存在私有仓库 `bluespace3/hugo-source-private`
2. GitHub Actions自动构建Hugo站点
3. 构建结果自动推送到公开仓库 `bluespace3/bluespace3.github.io` 的 `gh-pages` 分支

## 配置说明

### 部署密钥设置

需要在私有仓库中设置以下密钥：

1. `DEPLOY_KEY`: 用于向公开仓库推送内容的SSH部署密钥
   - 生成SSH密钥对: `ssh-keygen -t rsa -b 4096 -C "$(git config user.email)" -f gh-pages-deploy`
   - 私钥添加到私有仓库的Secrets中
   - 公钥添加到公开仓库的Deploy Keys中（需要勾选写入权限）

2. `CNAME`（可选）: 如果使用自定义域名，在此处设置

### GitHub Actions工作流

工作流配置文件位于 `.github/workflows/hugo.yml`，主要完成以下工作：

1. 检出私有仓库代码
2. 设置Hugo环境
3. 构建站点
4. 将生成的静态文件推送到公开仓库

## 本地开发

1. 克隆私有仓库：
   ```bash
   git clone https://github.com/bluespace3/hugo-source-private.git
   ```

2. 本地预览：
   ```bash
   hugo server -D
   ```

3. 提交更改到私有仓库：
   ```bash
   git add .
   git commit -m "更新内容"
   git push origin main
   ```

4. GitHub Actions会自动构建并部署到公开仓库

## 注意事项

- 所有内容修改应在私有仓库中进行
- 不要直接修改公开仓库的内容，它们会被自动部署覆盖
- 确保部署密钥配置正确，否则自动部署将失败

## 一键部署脚本

为了方便本地开发和手动部署，项目提供了一键部署脚本：

### 使用方法

1. **PowerShell (Windows)**:
   ```powershell
   # 在公开仓库目录中运行
   .\deploy-blog.ps1 "提交信息"
   ```

2. **Bash (Linux/macOS/Git Bash)**:
   ```bash
   # 赋予执行权限
   chmod +x deploy-blog.sh

   # 在公开仓库目录中运行
   ./deploy-blog.sh "提交信息"
   ```

### 脚本功能

- 自动将博客源码提交到私有仓库 `bluespace3/hugo-source-private`
- 自动构建 Hugo 站点
- 自动将生成的静态文件提交到公开仓库 `bluespace3/bluespace3.github.io`

### 注意事项

- 确保已安装 Hugo
- 确保有私有仓库的访问权限
- 脚本假设私有仓库 URL 为 `https://github.com/bluespace3/hugo-source-private.git`
- 如果私有仓库 URL 不同，请修改脚本中的 `PRIVATE_REPO_URL` 变量
