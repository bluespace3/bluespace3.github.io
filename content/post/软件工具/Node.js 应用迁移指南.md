---
title: 'Node.js 应用迁移指南'
categories: ["软件工具"]
date: 2026-04-06T21:21:10+08:00
lastmod: 2026-04-06T21:21:10+08:00
draft: false
---
# Node.js 应用迁移指南

> **创建时间**: 2026-04-06  
> **适用范围**: Ubuntu VPS 环境下的 Node.js 应用迁移  
> **核心目标**: 零依赖丢失、零数据库连接错误

---

## 📋 目录

1. [迁移前准备](#迁移前准备)
2. [Node.js 环境备份](#nodejs 环境备份)
3. [应用代码备份](#应用代码备份)
4. [依赖包备份](#依赖包备份)
5. [数据库迁移](#数据库迁移)
6. [新环境搭建](#新环境搭建)
7. [应用恢复与启动](#应用恢复与启动)
8. [常见问题解决](#常见问题解决)

---

## 🚀 迁移前准备

### 1.1 检查清单
- [ ] 确认 Node.js 版本（使用 `node -v`）
- [ ] 确认 npm/yarn/pnpm 版本
- [ ] 检查数据库连接信息
- [ ] 记录所有环境变量
- [ ] 确认服务端口和运行方式（pm2/systemd）

### 1.2 识别应用组件
在旧 VPS 上执行：

```bash
# 查看 Node.js 版本
node -v
npm -v
# 或
yarn -v
pnpm -v

# 查看当前运行的 Node 进程
ps aux | grep node

# 查看 PM2 进程（如果使用）
pm2 list

# 查找 package.json
find ~/projects -name "package.json" -type f

# 查看环境变量
printenv | grep -E "(NODE_|DB_|APP_)"
```

---

## 📦 Node.js 环境备份

### 2.1 备份 Node.js 版本信息
```bash
# 生成版本报告
cat > node_env_report.txt << EOF
Node.js Version: $(node -v)
NPM Version: $(npm -v)
Yarn Version: $(yarn -v 2>/dev/null || echo "not installed")
PNPM Version: $(pnpm -v 2>/dev/null || echo "not installed")
Platform: $(uname -a)
Architecture: $(uname -m)
EOF

cat node_env_report.txt
```

### 2.2 备份全局安装的 npm 包
```bash
# 列出全局包
npm list -g --depth=0 > global_packages.txt

# 备份全局包列表
npm list -g --depth=0 > ~/global_packages_backup.txt
```

### 2.3 备份 PM2 配置（如果使用）
```bash
# 导出 PM2 配置
pm2 save
pm2 dump

# 备份 PM2 配置目录
cp -r ~/.pm2 ~/pm2_backup/

# 查看应用状态
pm2 list --cols 50
```

---

## 📁 应用代码备份

### 3.1 备份应用目录
```bash
# 找到应用目录
cd /path/to/your/app

# 备份完整目录（排除 node_modules 和 .env）
tar czvf app_backup.tar.gz \
  --exclude=node_modules \
  --exclude=.env \
  --exclude=.git \
  --exclude=logs \
  --exclude=.cache \
  .

# 单独备份 node_modules（可选）
tar czvf node_modules_backup.tar.gz node_modules/

# 备份 .env 文件
cp .env .env_backup.txt
```

### 3.2 备份配置文件
```bash
# 备份所有配置文件
tar czvf configs_backup.tar.gz \
  --exclude=node_modules \
  --exclude=logs \
  .env* \
  config/ \
  settings/

# 备份环境变量模板
cp .env.example .env_example_backup.txt 2>/dev/null || echo "No .env.example"
cp .env.prod .env_prod_backup.txt 2>/dev/null || echo "No .env.prod"
```

### 3.3 记录启动脚本
```bash
# 如果有启动脚本
cp start.sh start_backup.sh
cp server.js server_backup.js
cp app.js app_backup.js

# 查看启动命令
cat package.json | grep -A2 '"scripts"'
```

---

## 📦 依赖包备份

### 4.1 生成依赖清单
```bash
# 生成 dependencies 列表
npm list --prod --depth=0 > dependencies.txt

# 生成 devDependencies 列表
npm list --dev --depth=0 > dev_dependencies.txt

# 生成 package-lock.json
cp package-lock.json package-lock_backup.json

# 生成 yarn.lock（如使用 yarn）
cp yarn.lock yarn.lock_backup
```

### 4.2 备份依赖安装命令
```bash
# 生成安装命令脚本
cat > install_dependencies.sh << 'EOF'
#!/bin/bash
npm install --production
# 或
# npm ci --production
EOF

chmod +x install_dependencies.sh
cat install_dependencies.sh
```

---

## 🗄 数据库迁移

### 5.1 备份数据库连接信息
```bash
# 记录数据库配置
cat > db_config_backup.txt << EOF
DB_HOST: $(grep DB_HOST .env 2>/dev/null || echo "not found")
DB_PORT: $(grep DB_PORT .env 2>/dev/null || echo "not found")
DB_NAME: $(grep DB_NAME .env 2>/dev/null || echo "not found")
DB_USER: $(grep DB_USER .env 2>/dev/null || echo "not found")
DB_PASS: (HIDDEN)
EOF

cat db_config_backup.txt
```

### 5.2 导出数据库数据
```bash
# MySQL 备份
mysqldump -u [user] -p [database] > database_backup.sql

# PostgreSQL 备份
pg_dump [database] > database_backup.sql

# MongoDB 备份
mongodump --db [database] --out ~/mongodb_backup/

# Redis 备份
redis-cli --dumpfile ~/redis_backup.rdb
```

### 5.3 记录数据库结构
```bash
# 导出表结构（MySQL）
mysqldump -u [user] -p --no-data [database] > schema_backup.sql

# 导出数据（仅数据）
mysqldump -u [user] -p --no-create-info [database] > data_backup.sql
```

---

## 🏗️ 新环境搭建

### 6.1 安装 Node.js
```bash
# 使用 NodeSource 安装（推荐，可指定版本）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node -v
npm -v

# 安装 nvm（可选，用于多版本管理）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
nvm use --lts
```

### 6.2 安装依赖工具
```bash
# 安装构建工具
sudo apt install build-essential -y

# 安装 PM2（进程管理器）
sudo npm install -g pm2

# 安装其他系统依赖
sudo apt install git curl wget unzip -y
```

### 6.3 创建应用目录
```bash
# 创建目录结构
mkdir -p ~/projects/yourapp/{logs,backup,config}
cd ~/projects/yourapp

# 设置权限（根据运行用户调整）
sudo chown -R $USER:$USER ~/projects
```

---

## 🔄 应用恢复与启动

### 7.1 传输应用文件
```bash
# 使用 rsync 传输（排除 node_modules）
rsync -avzP --exclude=node_modules \
  --exclude=.env \
  ~/yourapp/ user@new_vps:~/projects/yourapp/

# 传输 node_modules 备份（可选）
rsync -avzP ~/node_modules_backup.tar.gz user@new_vps:~/projects/yourapp/

# 传输 .env 文件
rsync -avzP .env_backup.txt user@new_vps:~/projects/yourapp/
```

### 7.2 安装依赖包
```bash
# 在新机器进入项目目录
cd ~/projects/yourapp

# 复制 .env 文件
cp .env_backup.txt .env

# 设置环境变量权限
chmod 600 .env

# 安装依赖（使用 package-lock.json 锁定版本）
npm ci --production

# 或（如果没有 package-lock.json）
npm install --production
```

### 7.3 恢复数据库
```bash
# 传输数据库备份
rsync -avzP ~/database_backup.sql user@new_vps:~/backup/

# 在新机器恢复数据库
# MySQL
mysql -u root -p < ~/backup/database_backup.sql

# PostgreSQL
psql -U postgres -d [database] < ~/backup/database_backup.sql

# MongoDB
mongorestore --db [database] ~/mongodb_backup/

# Redis
redis-cli < ~/backup/redis_backup.rdb
```

### 7.4 启动应用

#### 方法 A：使用 PM2（推荐）
```bash
# 查看应用启动脚本（package.json 中的 start 脚本）
cat package.json | grep -A3 '"start"'

# 启动应用
pm2 start ecosystem.config.js
# 或
pm2 start npm --name "yourapp" -- start

# 保存 PM2 配置
pm2 save

# 设置开机自启
pm2 startup systemd -u $USER --hp /home/$USER

# 查看状态
pm2 list
pm2 monit
```

#### 方法 B：使用 Systemd
```bash
# 创建服务文件
sudo nano /etc/systemd/system/yourapp.service
```

内容示例：
```ini
[Unit]
Description=Your Node.js App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/projects/yourapp
Environment=NODE_ENV=production
Environment=HOME=/home/$USER
ExecStart=/usr/bin/node server.js
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable yourapp
sudo systemctl start yourapp
sudo systemctl status yourapp
```

#### 方法 C：使用 forever
```bash
# 安装 forever
sudo npm install -g forever

# 启动应用
forever start -l /home/$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.log server.js

# 查看状态
forever list

# 停止
forever stop
```

---

## ✅ 验证步骤

### 应用状态验证
```bash
# 检查进程运行状态
pm2 list
# 或
sudo systemctl status yourapp

# 检查端口监听
sudo netstat -tlnp | grep [PORT]

# 测试应用响应
curl http://localhost:[PORT]/health

# 查看应用日志
tail -f /home/$USER/projects/yourapp/logs/app.log
```

### 数据库连接验证
```bash
# 测试数据库连接（使用 node）
node -e "const db = require('./config/db'); console.log('Connected!')"

# 或在应用内执行
npm run db:check  # 如果有测试脚本
```

### 功能验证
```bash
# 测试 API 端点
curl http://localhost:[PORT]/api/status

# 测试数据库查询
curl http://localhost:[PORT]/api/users

# 检查日志无错误
grep -i "error" /home/$USER/projects/yourapp/logs/*.log
```

---

## ❗ 常见问题解决

### 问题 1：node_modules 安装失败
**原因**: 系统依赖缺失或 Node.js 版本不兼容  
**解决**:
```bash
# 检查 Node.js 版本
node -v

# 安装系统依赖
sudo apt install libcurl4-openssl-dev libssl-dev -y

# 清理并重新安装
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 或尝试 yarn
yarn install
```

### 问题 2：端口被占用
**原因**: 旧应用仍在运行或端口冲突  
**解决**:
```bash
# 检查端口占用
sudo netstat -tlnp | grep [PORT]

# 查找并结束进程
sudo lsof -i :[PORT]
sudo kill -9 [PID]

# 或更改应用端口
nano .env  # 修改 PORT 环境变量
```

### 问题 3：数据库连接失败
**原因**: 数据库未启动或连接配置错误  
**解决**:
```bash
# 检查数据库状态
sudo systemctl status mysql
sudo systemctl status postgresql

# 检查连接配置
cat .env | grep DB_

# 测试数据库连接
mysql -h localhost -u root -p -e "SHOW DATABASES;"
```

### 问题 4：环境变量丢失
**原因**: `.env` 文件未正确迁移  
**解决**:
```bash
# 检查 .env 文件是否存在
ls -la .env

# 重新传输 .env 文件
rsync -avzP .env user@new_vps:~/projects/yourapp/

# 设置权限
chmod 600 .env

# 检查变量是否加载
env | grep NODE_
```

### 问题 5：PM2 启动失败
**原因**: 启动脚本错误或路径问题  
**解决**:
```bash
# 查看详细错误
pm2 logs yourapp --lines 50

# 检查启动命令
cat package.json | grep '"start"'

# 手动测试启动命令
cd /home/$USER/projects/yourapp
node server.js

# 重新保存 PM2 配置
pm2 save
```

---

## 📊 迁移检查清单

- [ ] Node.js 环境版本确认
- [ ] 所有依赖包清单生成
- [ ] 应用代码完整备份
- [ ] .env 文件已安全传输
- [ ] 数据库数据完整导出
- [ ] 新机器 Node.js 安装完成
- [ ] 依赖包成功安装
- [ ] 数据库成功恢复
- [ ] 应用成功启动
- [ ] 所有功能正常响应
- [ ] 日志无错误信息
- [ ] 服务开机自启配置

---

## 💡 最佳实践建议

1. **依赖锁定**: 使用 `package-lock.json` 或 `yarn.lock` 确保版本一致
2. **环境隔离**: 生产环境使用 `NODE_ENV=production`
3. **进程管理**: 使用 PM2 或 systemd 管理进程，避免服务中断
4. **日志管理**: 配置日志轮转，避免日志文件过大
5. **数据库迁移**: 先迁移数据库再迁移应用，确保数据先行
6. **环境变量**: 使用加密或安全的 .env 管理工具
7. **测试先行**: 在新机器先测试单功能，再全面切换

---

## 🔧 高级技巧

### 生成迁移脚本
```bash
cat > migrate_app.sh << 'EOF'
#!/bin/bash
# Node.js 应用迁移脚本
set -e

echo "开始备份应用..."
cd /path/to/app

# 备份
tar czvf app_backup.tar.gz --exclude=node_modules --exclude=.env .

# 传输
rsync -avzP app_backup.tar.gz user@new_server:~/backup/

# 传输 .env
rsync -avzP .env user@new_server:~/backup/

echo "迁移完成！"
EOF

chmod +x migrate_app.sh
```

### 自动化依赖安装
```bash
# 创建安装脚本
cat > install.sh << 'EOF'
#!/bin/bash
npm ci --production
pm2 start npm --name "myapp" -- start
pm2 save
EOF

chmod +x install.sh
```

### 数据库迁移脚本
```bash
cat > migrate_db.sh << 'EOF'
#!/bin/bash
# MySQL 数据库迁移
mysqldump -u [user] -p [db] | ssh user@new_server "mysql -u [user] -p [db]"
EOF
```

---

> **创建时间**: 2026-04-06  
> **最后更新**: 2026-04-06
