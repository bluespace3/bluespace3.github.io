# SSH部署密钥设置指南

本文档详细说明如何为Hugo博客双仓库部署方案设置SSH部署密钥。

## 为什么需要部署密钥？

在双仓库部署方案中，我们需要让GitHub Actions从私有仓库（源码）构建Hugo站点后，能够将生成的静态文件推送到公开仓库（GitHub Pages）。这需要设置适当的权限，而SSH部署密钥是最安全的方式。

## 步骤1：生成SSH密钥对

1. 打开终端（Windows上使用Git Bash或PowerShell）
2. 执行以下命令生成SSH密钥对：

```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f gh-pages-deploy
```

> 注意：将 "your-email@example.com" 替换为您的GitHub邮箱地址

3. 系统会提示您输入密码，建议留空（直接按Enter）
4. 命令执行完成后，会在当前目录生成两个文件：
   - `gh-pages-deploy`（私钥）
   - `gh-pages-deploy.pub`（公钥）

## 步骤2：在公开仓库添加部署密钥

1. 复制公钥文件内容：

   ```bash
   cat gh-pages-deploy.pub
   ```

   或使用文本编辑器打开并复制内容
2. 访问公开仓库（bluespace3.github.io）的GitHub页面
3. 点击 "Settings" > "Deploy keys" > "Add deploy key"
4. 填写以下信息：

   - Title: `HUGO_DEPLOY_KEY`
   - Key: 粘贴公钥内容
   - **勾选** "Allow write access"（这很重要，否则无法推送内容）
5. 点击 "Add key" 保存

## 步骤3：在私有仓库添加密钥

1. 复制私钥文件内容：

   ```bash
   cat gh-pages-deploy
   ```

   或使用文本编辑器打开并复制内容
2. 访问私有仓库（hugo-source-private）的GitHub页面
3. 点击 "Settings" > "Secrets and variables" > "Actions"
4. 点击 "New repository secret"
5. 添加以下密钥：

   - Name: `DEPLOY_KEY`
   - Secret: 粘贴私钥内容
6. 点击 "Add secret" 保存

## 步骤4：添加CNAME密钥（可选）

如果您使用自定义域名，需要添加CNAME密钥：

1. 在私有仓库的 "Settings" > "Secrets and variables" > "Actions" 中
2. 点击 "New repository secret"
3. 添加以下密钥：
   - Name: `CNAME`
   - Secret: 您的自定义域名（例如：`example.com`）
4. 点击 "Add secret" 保存

## 验证配置

完成以上步骤后，当您向私有仓库推送更改时，GitHub Actions将自动构建Hugo站点并将结果推送到公开仓库的gh-pages分支。

您可以通过以下方式验证配置是否成功：

1. 向私有仓库推送一个小更改
2. 在私有仓库的 "Actions" 标签页中查看工作流运行情况
3. 检查公开仓库的gh-pages分支是否已更新
4. 访问您的GitHub Pages网站（通常是 `https://bluespace3.github.io`）查看更改是否生效

## 故障排除

如果部署失败，请检查以下几点：

1. 确保部署密钥已正确添加到两个仓库中
2. 确保公开仓库的部署密钥已勾选 "Allow write access"
3. 检查GitHub Actions工作流日志中的错误信息
4. 确保工作流配置文件（`.github/workflows/hugo.yml`）中的仓库名称正确
