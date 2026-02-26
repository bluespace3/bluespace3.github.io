# 部署到 Ubuntu 服务器指南

## 📋 服务器信息

- **主机名**: openclaw
- **IP 地址**: 38.55.39.104
- **端口**: 22
- **用户**: root
- **SSH 密钥**: ~/.ssh/id_rsa_new

---

## 🚀 快速部署

### Windows 用户（推荐）

```powershell
# 在 PowerShell 中运行
.\deploy-to-server.ps1
```

### Linux/macOS 用户

```bash
# 在终端中运行
./deploy-to-server.sh
```

---

## 📝 部署脚本功能

部署脚本会自动完成以下任务：

1. ✅ **测试 SSH 连接**
2. ✅ **安装系统依赖**
   - Python 3
   - pip
   - Git
   - Hugo
3. ✅ **克隆/更新项目**
   - 从 GitHub 克隆仓库到 `/var/www/bluespace3.github.io`
4. ✅ **上传配置文件**
   - 上传 `.env` 文件（如果本地存在）
5. ✅ **安装 Python 依赖**
   - 创建虚拟环境
   - 安装 requirements.txt 中的依赖
6. ✅ **测试同步脚本**
   - 运行预览模式验证安装

---

## 🔧 手动部署步骤

如果自动部署脚本失败，可以手动执行以下步骤：

### 1. 连接到服务器

```bash
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104
```

### 2. 安装系统依赖

```bash
# 更新包管理器
apt-get update

# 安装 Python 和 Git
apt-get install -y python3 python3-pip python3-venv git

# 安装 Hugo
wget https://github.com/gohugoio/hugo/releases/download/v0.128.0/hugo_extended_0.128.0_linux-amd64.deb -O /tmp/hugo.deb
dpkg -i /tmp/hugo.deb
```

### 3. 克隆项目

```bash
# 创建项目目录
mkdir -p /var/www/bluespace3.github.io
cd /var/www/bluespace3.github.io

# 克隆仓库
git clone https://github.com/bluespace3/bluespace3.github.io.git .
```

### 4. 配置环境

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入 GITHUB_TOKEN
nano .env

# 或者直接命令行写入
echo "GITHUB_TOKEN=your_token_here" > .env
```

### 5. 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r tools/requirements.txt
```

### 6. 测试运行

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 预览模式测试
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 如果预览没问题，执行实际同步
python tools/sync_notes_from_github.py --batch content/post
```

### 7. 构建博客

```bash
# 构建 Hugo 网站
hugo --minify

# 查看生成的文件
ls public/
```

---

## 🔄 后续使用

### 同步笔记

```bash
# 连接到服务器
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104

# 进入项目目录
cd /var/www/bluespace3.github.io

# 激活虚拟环境
source venv/bin/activate

# 同步笔记
python tools/sync_notes_from_github.py --batch content/post

# 构建博客
hugo --minify
```

### 查看日志

```bash
# 查看同步输出
python tools/sync_notes_from_github.py --batch content/post --verbose
```

---

## 🛠️ 常见问题

### Q1: SSH 连接失败

**错误**: `Permission denied (publickey)`

**解决**:
```bash
# 检查密钥权限
chmod 600 ~/.ssh/id_rsa_new

# 测试 SSH 连接
ssh -i ~/.ssh/id_rsa_new root@38.55.39.104
```

### Q2: 权限不足

**错误**: `Permission denied` when writing to `/var/www`

**解决**:
```bash
# 使用 sudo 或更改目录所有者
sudo chown -R $USER:$USER /var/www/bluespace3.github.io
```

### Q3: Python 依赖安装失败

**错误**: `pip install failed`

**解决**:
```bash
# 更新 pip
pip install --upgrade pip

# 清除缓存后重新安装
pip cache purge
pip install -r tools/requirements.txt
```

### Q4: GITHUB_TOKEN 未设置

**错误**: `未设置 GITHUB_TOKEN 环境变量`

**解决**:
```bash
# 检查 .env 文件是否存在
cat /var/www/bluespace3.github.io/.env

# 如果不存在，创建它
cp /var/www/bluespace3.github.io/.env.example /var/www/bluespace3.github.io/.env
nano /var/www/bluespace3.github.io/.env
```

---

## 📊 服务器目录结构

```
/var/www/bluespace3.github.io/
├── .env                    # 环境变量配置
├── .env.example            # 环境变量模板
├── venv/                   # Python 虚拟环境
├── tools/                  # 工具脚本
│   ├── sync_notes_from_github.py
│   ├── github_api.py
│   ├── config.py
│   └── requirements.txt
├── content/                # 博客内容
│   └── post/              # 文章目录
├── public/                 # 生成的静态网站
├── hugo.toml              # Hugo 配置
└── deploy-to-server.sh    # 部署脚本
```

---

## 🔐 安全建议

1. **保护 .env 文件**
   ```bash
   chmod 600 .env
   ```

2. **使用防火墙**
   ```bash
   ufw allow 22/tcp
   ufw enable
   ```

3. **定期更新系统**
   ```bash
   apt-get update && apt-get upgrade -y
   ```

4. **定期备份数据**
   ```bash
   # 备份到本地
   scp -i ~/.ssh/id_rsa_new -r root@38.55.39.104:/var/www/bluespace3.github.io ./backup
   ```

---

## 📞 支持

如果遇到问题，请检查：
1. SSH 连接是否正常
2. Python 和 Hugo 是否正确安装
3. .env 文件是否存在且格式正确
4. 虚拟环境是否激活

需要帮助？查看详细文档：
- `tools/SYNC_NOTES_GUIDE.md` - 同步工具完整指南
- `QUICKSTART.md` - 快速开始指南
- `IMPLEMENTATION_SUMMARY.md` - 实施总结
