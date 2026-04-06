---
title: 'Docker 全栈迁移指南'
categories: ["软件工具"]
date: 2026-04-06T21:21:10+08:00
lastmod: 2026-04-06T21:21:10+08:00
draft: false
---
# Docker 全栈迁移指南

> **创建时间**: 2026-04-06  
> **适用范围**: Ubuntu VPS 环境下的 Docker 应用迁移  
> **核心目标**: 零数据丢失、零配置错误

---

## 📋 目录

1. [迁移前准备](#迁移前准备)
2. [Docker 数据备份](#docker 数据备份)
3. [Docker 配置备份](#docker 配置备份)
4. [新环境搭建](#新环境搭建)
5. [数据恢复与验证](#数据恢复与验证)
6. [常见问题解决](#常见问题解决)

---

## 🚀 迁移前准备

### 1.1 检查清单
- [ ] 确认旧 VPS 和新 VPS 的网络连通性
- [ ] 确保两台机器有足够磁盘空间（至少是原数据量的 1.5 倍）
- [ ] 确认 Docker 版本兼容性（建议新版 ≥ 旧版）

### 1.2 识别 Docker 组件
在旧 VPS 上执行以下命令，记录所有正在运行的容器和使用的 Volume：

```bash
# 列出所有容器（包括已停止的）
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 列出所有 Volume
docker volume ls --format "table {{.Name}}\t{{.Driver}}"

# 列出所有 docker-compose 项目
docker-compose ls
```

---

## 📦 Docker 数据备份

### 2.1 备份 Volume 数据（推荐方法）

#### 方法 A：使用临时容器备份（最安全）
```bash
# 备份单个 Volume
docker run --rm \
  -v my_database_data:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/mysql_volume_backup.tar.gz /data

# 备份多个 Volume（一次性打包）
docker run --rm \
  -v mysql_volume:/data1 \
  -v redis_volume:/data2 \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/all_volumes_backup.tar.gz /data1 /data2
```

#### 方法 B：直接打包 Volume 目录（快速）
```bash
# 找到 Volume 实际存储位置
docker volume inspect mysql_volume --format '{{.Mountpoint}}'

# 进入 Docker 卷目录（通常在/var/lib/docker/volumes/）
cd /var/lib/docker/volumes/mysql_volume/_data
tar czf ~/mysql_backup.tar.gz .
```

### 2.2 备份容器配置

#### 导出容器运行参数
```bash
# 获取容器详细配置
docker inspect my_container_name > container_config.json

# 查看环境变量
docker inspect --format='{{range .Config.Env}}{{.}}
{{end}}' my_container_name > env_list.txt
```

#### 备份 docker-compose 文件
```bash
# 查找所有 docker-compose 项目
find / -name "docker-compose.yml" 2>/dev/null

# 备份所有 docker-compose 文件
tar czvf docker-compose_configs.tar.gz /path/to/projects/
```

---

## ⚙️ Docker 配置备份

### 3.1 备份自定义配置文件
```bash
# 备份 Docker 守护进程配置
cp /etc/docker/daemon.json ~/daemon_backup.json

# 备份 Docker 环境变量（如有）
cat /etc/environment >> ~/docker_env_backup.txt
cat ~/.bashrc >> ~/bashrc_backup.txt
```

### 3.2 导出网络配置
```bash
# 列出所有 Docker 网络
docker network ls --format "table {{.Name}}\t{{.Driver}}"

# 导出网络配置
docker network inspect my_network > network_config.json
```

---

## 🏗️ 新环境搭建

### 4.1 安装 Docker
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker（推荐官方源）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose -y

# 验证安装
docker --version
docker-compose --version

# 将当前用户加入 docker 组（避免每次 sudo）
sudo usermod -aG docker $USER
```

### 4.2 创建目录结构
```bash
# 创建项目目录
mkdir -p ~/projects/myapp/{data,config,logs}
cd ~/projects/myapp

# 设置权限（关键！）
chmod -R 755 .
```

---

## 🔄 数据恢复与验证

### 5.1 传输备份文件
```bash
# 使用 rsync（推荐，支持断点续传）
rsync -avzP ~/mysql_backup.tar.gz user@new_vps:~/backup/

# 或使用 scp
scp ~/mysql_backup.tar.gz user@new_vps:~/backup/

# 传输整个项目目录
rsync -avzP ~/projects/ user@new_vps:~/projects/
```

### 5.2 恢复 Volume 数据

#### 方法 A：导入压缩备份
```bash
# 在新机器上解压
cd ~/projects/myapp/data
tar xzf ~/backup/mysql_volume_backup.tar.gz

# 检查文件权限
ls -la
# 确保权限正确（根据应用需求调整）
sudo chown -R 1000:1000 .
```

#### 方法 B：挂载新 Volume 并导入
```bash
# 在新机器创建新 Volume
docker volume create mysql_data_new

# 启动临时容器导入数据
docker run --rm \
  -v mysql_data_new:/data \
  -v /home/user/backup:/backup \
  alpine \
  bash -c "cp /backup/mysql_volume_backup.tar.gz /data/ && \
          tar xzf /data/mysql_volume_backup.tar.gz"
```

### 5.3 恢复 docker-compose 配置
```bash
# 传输配置文件
rsync -avzP ~/projects/myapp/docker-compose.yml user@new_vps:~/projects/myapp/

# 启动服务（自动创建 Volume）
cd ~/projects/myapp
docker-compose up -d

# 停止服务
docker-compose down

# 替换数据目录
docker run --rm \
  -v myapp_db_data:/data \
  -v /home/user/backup:/backup \
  alpine \
  cp -r /backup/* /data/

# 重新启动
docker-compose up -d
```

### 5.4 验证服务
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试应用连接
curl http://localhost:3000

# 检查数据库连接
docker exec -it myapp_db_1 mysql -u root -p -e "SHOW DATABASES;"
```

---

## ❗ 常见问题解决

### 问题 1：容器启动失败 - 权限错误
**原因**: 文件权限在新机器上不正确  
**解决**:
```bash
# 恢复权限（根据应用调整用户 ID）
sudo chown -R 1000:1000 /var/www/html
sudo chmod -R 755 /var/www/html
```

### 问题 2：数据库连接被拒绝
**原因**: 数据库未启动或配置文件未迁移  
**解决**:
```bash
# 检查容器状态
docker ps | grep db

# 查看详细日志
docker logs db_container

# 验证数据库文件
docker run --rm -v db_data:/data alpine ls -la /data
```

### 问题 3：环境变量丢失
**原因**: `.env` 文件未迁移  
**解决**:
```bash
# 创建 .env 文件
cat > .env << EOF
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
NODE_ENV=production
EOF
```

### 问题 4：Volume 数据损坏
**原因**: 备份或传输过程中数据损坏  
**解决**:
```bash
# 验证备份完整性
tar tzf mysql_volume_backup.tar.gz > /dev/null && echo "备份完整"

# 如有损坏，使用源数据重新备份
docker run --rm -v mysql_volume:/data -v $(pwd):/backup alpine tar czf /backup/mysql_volume_backup.tar.gz /data
```

---

## 📊 迁移检查清单

- [ ] Docker 和 Compose 安装完成
- [ ] 所有 Volume 数据备份完成
- [ ] docker-compose 文件备份完成
- [ ] 配置文件和 .env 文件已迁移
- [ ] 数据在新机器解压/导入
- [ ] 容器成功启动
- [ ] 应用可通过浏览器访问
- [ ] 数据库连接正常
- [ ] 日志查看无错误
- [ ] 备份文件已归档

---

## 💡 最佳实践建议

1. **备份前先测试**: 在旧机器上模拟一次完整的数据恢复流程
2. **分阶段迁移**: 先迁移数据和配置，测试无误后再切换到新 IP
3. **保留旧机器**: 迁移后至少保留旧机器 48 小时，确保一切正常后再删除
4. **文档化**: 记录所有操作步骤，方便日后复用

---

> **创建时间**: 2026-04-06  
> **最后更新**: 2026-04-06
