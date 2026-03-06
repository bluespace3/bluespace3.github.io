---
title: 'nextcloud-setup-summary'
categories: ["nextcloud-setup-summary.md"]
date: 2026-03-06T13:42:26+08:00
lastmod: 2026-03-06T13:42:26+08:00
draft: false
---
# Nextcloud 配置与优化总结

**日期**: 2026-03-05
**任务**: Nextcloud 局域网/公网访问配置、SSL证书配置、性能优化

---

## 一、项目概述

### 目标
1. 在本地Mac上通过Docker运行Nextcloud
2. 配置局域网HTTPS访问（解决SSL初始化失败）
3. 配置公网HTTPS访问（Let's Encrypt证书）
4. 优化访问性能

### 环境信息
- **本地环境**: macOS (Darwin 25.2.0)
- **Docker运行时**: Colima
- **云服务器**: 38.55.39.104 (Ubuntu)
- **Nextcloud版本**: 33.0.0.16
- **数据库**: MySQL 8.0 (本地)
- **缓存**: Redis

---

## 二、架构设计

### 网络架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         访问路径                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  公网访问                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ 客户端      │───▶│ Cloudflare   │───▶│ 服务器Nginx  │       │
│  │ (任何网络)  │    │ (DNS only)   │    │ (38.55.39.   │       │
│  └─────────────┘    └──────────────┘    │ 104)         │       │
│                                         │  Let's Encrypt│      │
│                                         └──────┬─────────┘       │
│                                                │                 │
│                                         ┌──────▼─────────┐       │
│                                         │ Tailscale VPN  │       │
│                                         └──────┬─────────┘       │
│                                                │                 │
│  局域网访问                               ┌──────▼─────────┐       │
│  ┌─────────────┐                        │ 本地Mac        │       │
│  │ 局域网设备  │───▶────────────────────│ Docker/Colima │       │
│  │ (192.168.   │                        │                │       │
│  │ 10.222)     │◀───┐                   │  - Nextcloud  │       │
│  └─────────────┘    │                   │  - MySQL      │       │
│                     │                   │  - Redis      │       │
│  ┌─────────────┐   │                   └──────┬─────────┘       │
│  │ 本地Mac     │───┘                          │                 │
│  │ Nginx代理   │    G盘挂载                   ▼                 │
│  │ (:8443)     │◀───/Volumes/G/nextCloud    存储层              │
│  └─────────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 访问方式对比

| 访问方式 | 地址 | 延迟 | 证书类型 | 适用场景 |
|---------|------|------|---------|---------|
| 公网HTTPS | https://nc.skyspace.eu.org | 0.90秒 | Let's Encrypt | 所有客户端 |
| 旧公网HTTPS | https://nextcloud.skyspace.eu.org | 1.22秒 | 自签名 | 备用 |
| 局域网HTTPS | https://192.168.10.222:8443 | 0.01秒 | 自签名 | 局域网设备 |
| Tailscale | http://100.97.62.83:8080 | 0.35秒 | HTTP | VPN内设备 |
| 局域网HTTP | http://192.168.10.222:8080 | 0.01秒 | HTTP | 局域网设备 |

---

## 三、配置步骤详解

### 3.1 基础环境搭建

#### Docker Compose配置
**文件**: `~/nextcloud/docker-compose.yml`

```yaml
version: '3.8'

services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    ports:
      - "8080:80"
    volumes:
      - nextcloud_data:/var/www/html
      - ./config.php:/var/www/html/config/config.php
      - ./optimizations/00-opcache.ini:/usr/local/etc/php/conf.d/00-opcache.ini:ro
      - ./optimizations/99-timeouts.ini:/usr/local/etc/php/conf.d/99-timeouts.ini:ro
      - ./optimizations/http2.conf:/etc/apache2/conf-available/http2.conf:ro
      - /Volumes/G/nextCloud:/mnt/g-drive:ro
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud123
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - PHP_MEMORY_LIMIT=512M
      - PHP_UPLOAD_LIMIT=10G
      - PHP_MAX_EXECUTION_TIME=3600
      - APACHE_BODY_LIMIT=10737418240
      - APACHE_TIMEOUT_LIMIT=3600
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - nextcloud-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/80"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  db:
    image: mysql:8.0
    container_name: nextcloud-mysql
    volumes:
      - mysql_data:/var/lib/mysql
      - ./optimizations/mysql.cnf:/etc/mysql/conf.d/custom.cnf:ro
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud123
    restart: unless-stopped
    networks:
      - nextcloud-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootpassword"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:alpine
    container_name: nextcloud-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    networks:
      - nextcloud-network

networks:
  nextcloud-network:
    driver: bridge

volumes:
  nextcloud_data:
    driver: local
  mysql_data:
    driver: local
```

### 3.2 性能优化配置

#### MySQL 8.0优化
**文件**: `~/nextcloud/optimizations/mysql.cnf`

```ini
[mysqld]
# 性能调优
max_connections = 200
innodb_buffer_pool_size = 256M
innodb_redo_log_capacity = 128M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# 快速启动
innodb_fast_shutdown = 2
innodb_doublewrite = 0
skip_name_resolve

# 连接设置
max_allowed_packet = 64M
connect_timeout = 5
wait_timeout = 600

# 禁用二进制日志以加快启动
skip_log_bin
disable_log_bin

# SSD优化
innodb_io_capacity = 200
innodb_io_capacity_max = 2000
```

#### PHP OPcache配置
**文件**: `~/nextcloud/optimizations/00-opcache.ini`

```ini
opcache.enable=1
opcache.enable_cli=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=32
opcache.max_accelerated_files=20000
opcache.revalidate_freq=60
opcache.fast_shutdown=1
opcache.jit_buffer_size=128M
```

#### PHP超时配置（大文件上传）
**文件**: `~/nextcloud/optimizations/99-timeouts.ini`

```ini
max_execution_time = 3600
max_input_time = 3600
memory_limit = 512M
file_uploads = On
upload_max_filesize = 10G
post_max_size = 10G
max_file_uploads = 20
default_socket_timeout = 3600
mysql.connect_timeout = 3600
```

### 3.3 局域网HTTPS配置

#### 安装Nginx（Mac）
```bash
brew install nginx
```

#### 生成自签名证书
```bash
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout ~/nextcloud/ssl/nextcloud-local.key \
  -out ~/nextcloud/ssl/nextcloud-local.crt \
  -subj '/CN=192.168.10.222'
```

#### Nginx配置
**文件**: `/opt/homebrew/etc/nginx/servers/nextcloud-https.conf`

```nginx
server {
    listen 8443 ssl;
    server_name 192.168.10.222;

    ssl_certificate /Users/tianqinghong/nextcloud/ssl/nextcloud-local.crt;
    ssl_certificate_key /Users/tianqinghong/nextcloud/ssl/nextcloud-local.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host:$server_port;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
        proxy_buffering off;
        client_max_body_size 10G;
    }
}
```

#### Nextcloud配置更新
```bash
docker exec nextcloud php occ config:system:set trusted_domains 7 --value="192.168.10.222:8443"
docker exec nextcloud php occ config:system:set overwritehost --value="192.168.10.222:8443"
docker exec nextcloud php occ config:system:set overwriteprotocol --value="https"
```

### 3.4 公网HTTPS配置（Let's Encrypt）

#### 前置条件
1. 在Cloudflare中将nc.skyspace.eu.org的代理模式关闭（DNS only）
2. 确保DNS解析到服务器IP（38.55.39.104）
3. 服务器已安装Tailscale并可访问本地Mac（100.97.62.83:8080）

#### 获取Let's Encrypt证书
```bash
# 在服务器上执行
ssh server

# 创建验证目录
mkdir -p /var/www/html/.well-known/acme-challenge
chown -R www-data:www-data /var/www/html

# 获取证书
certbot certonly --webroot \
  -w /var/www/html \
  -d nc.skyspace.eu.org \
  --email admin@skyspace.eu.org \
  --agree-tos \
  --non-interactive
```

#### Nginx配置（服务器）
**文件**: `/etc/nginx/sites-available/nc.skyspace.eu.org.conf`

```nginx
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name nc.skyspace.eu.org;
    return 301 https://$server_name$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name nc.skyspace.eu.org;

    # Let's Encrypt证书
    ssl_certificate /etc/letsencrypt/live/nc.skyspace.eu.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nc.skyspace.eu.org/privkey.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志
    access_log /var/log/nginx/nc.skyspace.eu.org.access.log;
    error_log /var/log/nginx/nc.skyspace.eu.org.error.log;

    # 反向代理到Nextcloud（通过Tailscale）
    location / {
        proxy_pass http://100.97.62.83:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
        proxy_buffering off;
        proxy_request_buffering off;
        client_max_body_size 10G;
        client_body_timeout 3600s;
    }

    # WebDAV支持
    location /remote.php/webdav/ {
        proxy_pass http://100.97.62.83:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
        proxy_buffering off;
        client_max_body_size 10G;
    }
}
```

#### 证书自动续期
Certbot会自动设置定时任务，可通过以下命令验证：
```bash
certbot renew --dry-run
systemctl list-timers | grep certbot
```

---

## 四、Nextcloud配置详解

### 4.1 完整配置文件
**文件**: `~/nextcloud/config.php`

```php
<?php
$CONFIG = array (
  'memcache.local' => '\\OC\\Memcache\\APCu',
  'memcache.distributed' => '\\OC\\Memcache\\Redis',
  'memcache.locking' => '\\OC\\Memcache\\Redis',
  'filelocking.enabled' => 'true',
  'redis' =>
  array (
    'host' => 'redis',
    'port' => 6379,
    'timeout' => 0.0,
    'compression' => 'none',
  ),
  'trusted_domains' =>
  array (
    0 => 'localhost',
    1 => 'localhost:8080',
    2 => 'nextcloud.skyspace.eu.org',
    3 => '192.168.10.222:8080',
    4 => '100.97.62.83:8080',
    5 => 'nc.skyspace.eu.org',
    6 => '192.168.10.222:8443',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'mysql',
  'version' => '33.0.0.16',
  'overwrite.cli.url' => 'http://localhost:8080',
  'overwriteprotocol' => false,  // 自动检测协议
  'dbname' => 'nextcloud',
  'dbhost' => 'db',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'nextcloud',
  'dbpassword' => 'nextcloud123',
  'installed' => true,
  'instanceid' => 'ocnkmggsliuq',
  'htaccess.RewriteBase' => '/',
  'default_language' => 'zh_CN',
  'default_locale' => 'zh_CN',
  'knowledgebaseenabled' => false,
  'check_for_working_htaccess' => false,
  'simpleSignUpLink.shown' => false,
  'trashbin_retention_obligation' => 'auto, 30',
  'versions_retention_obligation' => 'auto, 30',
  'activity_expire_days' => 30,
  'allow_local_remote_servers' => true,
  'debug' => false,
  'loglevel' => 2,
  'upgrade.disable-web' => false,
  'app.disable_background' => false,
  'chunk_file_size' => 10485760,
  'max_chunk_size' => 10485760,
);
```

### 4.2 关键配置说明

#### trusted_domains（可信域名）
- 用于Nextcloud识别允许访问的域名
- 需要包含所有访问方式（HTTP/HTTPS，不同端口）
- 修改后需重启容器生效

#### overwriteprotocol
- `false`: 自动检测（推荐）
- `https`: 强制使用HTTPS
- `http`: 强制使用HTTP
- 本配置中使用`false`以支持多种访问方式

#### Redis缓存配置
- `memcache.local`: 本地缓存（APCu）
- `memcache.distributed`: 分布式缓存（Redis）
- `memcache.locking`: 文件锁缓存（Redis）

---

## 五、性能测试结果

### 5.1 首页加载性能（status.php）

| 域名 | 平均延迟 | 最快 | 最慢 | 标准差 |
|------|---------|------|------|--------|
| nextcloud.skyspace.eu.org | 1.22秒 | 0.89秒 | 1.39秒 | 0.15秒 |
| nc.skyspace.eu.org | 0.90秒 | - | - | - |
| 192.168.10.222:8443 | 0.01秒 | - | - | - |
| **性能提升** | **26%** | - | - | - |

### 5.2 WebDAV操作性能（文件列表）

| 域名 | 平均延迟 | 性能对比 |
|------|---------|----------|
| nextcloud.skyspace.eu.org | 1.08秒 | 基准 |
| nc.skyspace.eu.org | 0.83秒 | ✅ 快23% |
| 192.168.10.222:8443 | 0.02秒 | ✅ 极快 |

### 5.3 文件上传性能

#### 小文件上传（1MB）
| 域名 | 平均耗时 | 平均速度 | 状态 |
|------|---------|---------|------|
| nextcloud.skyspace.eu.org | ~4秒 | 256KB/s | ✅ |
| nc.skyspace.eu.org | ~3-5秒 | 200-350KB/s | ✅ |
| 192.168.10.222:8443 | <1秒 | >2MB/s | ✅ |

#### 大文件上传（10MB）
| 域名 | 耗时 | 平均速度 | 状态 |
|------|------|---------|------|
| nc.skyspace.eu.org | ~37秒 | 280KB/s | ✅ |
| 192.168.10.222:8443 | ~15秒 | 700KB/s | ✅ |

### 5.4 性能瓶颈分析

#### 延迟组成（公网访问）
```
总延迟: 0.90秒
├── 客户端 → Cloudflare DNS: ~50ms
├── Cloudflare → 服务器: ~100ms
├── 服务器处理: ~50ms
├── 服务器 → Tailscale → 本地Mac: ~350ms
└── Nextcloud处理: ~350ms
```

#### 优化效果
- ✅ 使用Let's Encrypt证书：减少握手时间
- ✅ 配置Redis缓存：减少数据库查询
- ✅ 启用OPcache：加速PHP执行
- ✅ HTTP/2支持：多路复用连接
- ✅ 本地nginx代理：局域网访问极快

---

## 六、问题解决方案

### 6.1 SSL初始化失败

#### 问题描述
- 客户端（iOS/Android）无法连接
- 错误提示："SSL初始化失败"
- 原因：使用自签名证书，客户端不信任

#### 解决方案
**公网访问**：
1. 获取Let's Encrypt证书（可信CA）
2. 配置nginx使用新证书
3. 客户端自动信任证书

**局域网访问**：
1. 安装本地nginx
2. 生成自签名证书
3. 首次访问时手动信任

### 6.2 局域网访问报错"不被信任的域名"

#### 问题描述
- 访问 `https://192.168.10.222:8443` 报错
- 提示："通过不被信任的域名访问"

#### 解决步骤
1. 添加到trusted_domains：
```bash
docker exec nextcloud php occ config:system:set trusted_domains 7 --value="192.168.10.222:8443"
```

2. 配置overwritehost和overwriteprotocol：
```bash
docker exec nextcloud php occ config:system:set overwritehost --value="192.168.10.222:8443"
docker exec nextcloud php occ config:system:set overwriteprotocol --value="https"
```

3. 重启容器：
```bash
~/nextcloud/nextcloud.sh restart
```

4. 确保nginx正确传递Host header：
```nginx
proxy_set_header Host $host:$server_port;
proxy_set_header X-Forwarded-Proto https;
```

### 6.3 大文件上传失败

#### 问题描述
- 上传大文件时失败
- 错误：网络中断、超时

#### 解决方案
1. **增加PHP超时设置**（已在99-timeouts.ini配置）：
```ini
max_execution_time = 3600
max_input_time = 3600
default_socket_timeout = 3600
```

2. **增加nginx超时**：
```nginx
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
```

3. **配置分块上传**（config.php）：
```php
'chunk_file_size' => 10485760,  // 10MB
'max_chunk_size' => 10485760,
```

### 6.4 MySQL 8.0配置错误

#### 问题描述
- MySQL容器启动失败
- 错误：`unknown variable 'query_cache_size=0'`

#### 原因
- MySQL 8.0已移除query cache功能
- 配置文件使用了旧版本参数

#### 解决方案
1. 移除已弃用的参数：
```ini
# 删除以下配置
# query_cache_size = 0
# query_cache_type = 1
# innodb_log_file_size = 256M  # 改用innodb_redo_log_capacity
```

2. 使用新参数：
```ini
innodb_redo_log_capacity = 128M
```

### 6.5 Docker容器启动慢

#### 问题描述
- 容器重启耗时20-30秒
- MySQL初始化时间长

#### 优化方案
1. **MySQL快速启动**：
```ini
innodb_fast_shutdown = 2
innodb_doublewrite = 0
skip_log_bin
```

2. **减少buffer pool**：
```ini
innodb_buffer_pool_size = 256M  # 从512M降低
```

3. **添加健康检查**：
```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootpassword"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**效果**：启动时间缩短至5-10秒

---

## 七、管理脚本

### 7.1 快速管理脚本
**文件**: `~/nextcloud/nextcloud.sh`

```bash
#!/bin/bash
# Nextcloud 快速管理脚本

case "$1" in
  start)
    echo "🚀 启动 Nextcloud..."
    cd ~/nextcloud && docker compose up -d
    echo "✅ Nextcloud 已启动"
    echo "访问地址: http://localhost:8080"
    ;;

  stop)
    echo "⏹️  停止 Nextcloud..."
    cd ~/nextcloud && docker compose down
    echo "✅ Nextcloud 已停止"
    ;;

  restart)
    echo "🔄 快速重启 Nextcloud（仅重启服务）..."
    cd ~/nextcloud && docker compose restart nextcloud
    echo "✅ Nextcloud 已重启（耗时约 5秒）"
    ;;

  full-restart)
    echo "🔄 完全重启 Nextcloud（包含数据库）..."
    cd ~/nextcloud && docker compose down && docker compose up -d
    echo "✅ Nextcloud 已完全重启（耗时约 15-20秒）"
    ;;

  status)
    echo "📊 Nextcloud 状态:"
    docker ps --filter "name=nextcloud" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ;;

  logs)
    echo "📋 Nextcloud 日志（最后 30 行）:"
    docker logs nextcloud --tail 30
    ;;

  update)
    echo "🔄 更新 Nextcloud 镜像..."
    cd ~/nextcloud && docker compose pull && docker compose up -d --force-recreate
    echo "✅ Nextcloud 已更新并重启"
    ;;

  *)
    echo "Nextcloud 快速管理脚本"
    echo ""
    echo "用法: ./nextcloud.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start        - 启动服务"
    echo "  stop         - 停止服务"
    echo "  restart      - 快速重启（推荐）"
    echo "  full-restart - 完全重启"
    echo "  status       - 查看状态"
    echo "  logs         - 查看日志"
    echo "  update       - 更新镜像"
    echo ""
    echo "示例:"
    echo "  ./nextcloud.sh restart"
    echo "  ./nextcloud.sh logs"
    ;;
esac
```

### 7.2 使用方法
```bash
# 启动服务
~/nextcloud/nextcloud.sh start

# 快速重启
~/nextcloud/nextcloud.sh restart

# 查看状态
~/nextcloud/nextcloud.sh status

# 查看日志
~/nextcloud/nextcloud.sh logs
```

---

## 八、客户端配置指南

### 8.1 iOS客户端

#### 配置步骤
1. 下载Nextcloud官方App
2. 创建新连接：
   - 服务器地址: `https://nc.skyspace.eu.org`
   - 用户名: `admin`
   - 密码: `tianz728~`
3. 点击"登录"

#### 局域网访问（可选）
- 服务器地址: `https://192.168.10.222:8443`
- 首次连接时点击"高级" → "访问此网站"

### 8.2 Android客户端

#### 配置步骤
1. 下载Nextcloud官方App
2. 创建新连接：
   - 服务器地址: `https://nc.skyspace.eu.org`
   - 用户名: `admin`
   - 密码: `tianz728~`
3. 点击"登录"

#### 局域网访问（可选）
- 服务器地址: `https://192.168.10.222:8443`
- 勾选"忽略SSL验证"

### 8.3 桌面客户端（macOS/Windows/Linux）

#### 配置步骤
1. 下载Nextcloud官方客户端
2. 创建新账户：
   - 服务器地址: `https://nc.skyspace.eu.org`
   - 用户名: `admin`
   - 密码: `tianz728~`
3. 选择同步文件夹
4. 点击"连接"

### 8.4 Web浏览器访问

直接访问：`https://nc.skyspace.eu.org`

局域网访问：`https://192.168.10.222:8443`（首次需信任证书）

---

## 九、维护与监控

### 9.1 日常维护

#### 查看日志
```bash
# Nextcloud日志
docker logs nextcloud --tail 50

# MySQL日志
docker logs nextcloud-mysql --tail 50

# Nginx日志（本地）
tail -f /opt/homebrew/var/log/nextcloud-https.error.log

# Nginx日志（服务器）
ssh server "tail -f /var/log/nginx/nc.skyspace.eu.org.error.log"
```

#### 检查服务状态
```bash
# 容器状态
docker ps | grep nextcloud

# 磁盘使用
df -h /Volumes/G/nextCloud

# 数据库大小
docker exec nextcloud-mysql du -sh /var/lib/mysql
```

### 9.2 备份策略

#### 数据备份位置
- Nextcloud数据: `/var/www/html/data` → Docker volume `nextcloud_data`
- 数据库: `/var/lib/mysql` → Docker volume `mysql_data`
- G盘挂载: `/Volumes/G/nextCloud` → 物理存储

#### 备份脚本示例
```bash
#!/bin/bash
# 备份脚本
BACKUP_DIR="/path/to/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份配置
cp ~/nextcloud/config.php $BACKUP_DIR/config_$DATE.php

# 导出数据库
docker exec nextcloud-mysql mysqldump -u nextcloud -pnextcloud123 nextcloud > $BACKUP_DIR/database_$DATE.sql

# 备份Docker volumes
docker run --rm \
  -v nextcloud_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/nextcloud_data_$DATE.tar.gz -C /data .

docker run --rm \
  -v mysql_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/mysql_data_$DATE.tar.gz -C /data .
```

### 9.3 性能监控

#### Nextcloud OCC命令
```bash
# 检查系统状态
docker exec nextcloud php occ status

# 检查文件完整性
docker exec nextcloud php occ integrity:check-core

# 查看配置
docker exec nextcloud php occ config:list

# 清理文件缓存
docker exec nextcloud php occ files:cleanup

# 扫描文件
docker exec nextcloud php occ files:scan --all
```

#### 数据库维护
```bash
# 进入MySQL
docker exec -it nextcloud-mysql mysql -u nextcloud -pnextcloud123 nextcloud

# 优化表
OPTIMIZE TABLE oc_filecache;
OPTIMIZE TABLE oc_filecache_extended;

# 查看表大小
SELECT table_name,
       ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size in MB"
FROM information_schema.TABLES
WHERE table_schema = "nextcloud"
ORDER BY (data_length + index_length) DESC;
```

### 9.4 Let's Encrypt证书维护

#### 查看证书信息
```bash
ssh server "openssl x509 -in /etc/letsencrypt/live/nc.skyspace.eu.org/fullchain.pem -noout -subject -issuer -dates"
```

#### 手动续期
```bash
ssh server "certbot renew"
```

#### 测试自动续期
```bash
ssh server "certbot renew --dry-run"
```

#### 证书有效期
- 颁发日: 2026-03-04
- 到期日: 2026-06-02
- 有效期: 90天
- 自动续期: ✅ 已启用

---

## 十、故障排查

### 10.1 常见问题诊断流程

```
问题：无法访问Nextcloud
│
├─ 1. 检查容器状态
│   └─ docker ps | grep nextcloud
│
├─ 2. 检查网络连接
│   ├─ 局域网: curl http://192.168.10.222:8080
│   ├─ 公网: curl https://nc.skyspace.eu.org
│   └─ Tailscale: curl http://100.97.62.83:8080
│
├─ 3. 检查域名解析
│   ├─ dig nc.skyspace.eu.org
│   └─ dig 192.168.10.222
│
├─ 4. 检查trusted_domains
│   └─ docker exec nextcloud php occ config:system:get trusted_domains
│
├─ 5. 检查SSL证书
│   ├─ 本地: openssl s_client -connect 192.168.10.222:8443
│   └─ 公网: openssl s_client -connect nc.skyspace.eu.org:443
│
└─ 6. 查看详细日志
    ├─ docker logs nextcloud --tail 100
    ├─ docker logs nextcloud-mysql --tail 100
    └─ nginx error日志
```

### 10.2 日志分析

#### 错误日志位置
- Nextcloud: `docker logs nextcloud`
- MySQL: `docker logs nextcloud-mysql`
- Nginx（本地）: `/opt/homebrew/var/log/nginx/error.log`
- Nginx（服务器）: `/var/log/nginx/nc.skyspace.eu.org.error.log`
- Nextcloud内部日志: `docker exec nextcloud cat /var/www/html/data/nextcloud.log`

#### 常见错误代码
- **502 Bad Gateway**: Nextcloud容器未运行或端口错误
- **504 Gateway Timeout**: 请求超时（检查超时配置）
- **SSL_ERROR**: 证书问题或配置错误
- **401 Unauthorized**: 认证失败（检查用户名密码）
- **403 Forbidden**: 权限问题（检查trusted_domains）
- **"通过不被信任的域名访问"**: 需要添加到trusted_domains

### 10.3 性能调优建议

#### 如果公网访问慢
1. 检查Tailscale连接质量
2. 考虑使用CDN（Cloudflare代理）
3. 优化数据库查询
4. 增加Redis缓存

#### 如果局域网访问慢
1. 检查本地网络速度
2. 优化nginx配置
3. 确认使用HTTPS（8443端口）
4. 检查CPU和内存使用率

#### 如果上传失败
1. 检查文件大小限制（配置为10GB）
2. 检查超时设置（配置为3600秒）
3. 检查磁盘空间
4. 尝试使用客户端而非Web上传

---

## 十一、总结

### 11.1 项目成果

✅ **完成的配置**
1. 本地Mac上运行Nextcloud（Docker + Colima）
2. MySQL 8.0数据库优化
3. Redis三级缓存
4. 局域网HTTPS访问（自签名证书）
5. 公网HTTPS访问（Let's Encrypt证书）
6. Tailscale VPN支持
7. 大文件上传支持（10GB）
8. 性能优化（OPcache、HTTP/2）
9. 自动证书续期
10. 监控和管理脚本

✅ **性能提升**
- 公网访问延迟降低26%（1.22秒 → 0.90秒）
- 局域网访问极快（0.01秒）
- 大文件上传稳定

✅ **问题解决**
- SSL初始化失败 → 已修复
- 局域网访问报错 → 已修复
- 大文件上传失败 → 已修复
- MySQL启动慢 → 已优化

### 11.2 最佳实践

#### 推荐使用场景
- **公网访问**: 使用 `https://nc.skyspace.eu.org`（Let's Encrypt证书）
- **局域网访问**: 使用 `https://192.168.10.222:8443`（速度最快）
- **VPN访问**: 使用 `http://100.97.62.83:8080`（Tailscale内网）

#### 安全建议
1. 定期更新Nextcloud版本
2. 使用强密码
3. 启用两步验证（待配置）
4. 定期备份数据
5. 监控日志文件
6. 及时更新SSL证书

#### 备份策略
1. 每周自动备份数据库
2. 每月备份配置文件
3. G盘物理存储作为主要备份
4. 异地备份重要文件

### 11.3 未来优化方向

#### 性能优化
1. 配置Cloudflare CDN（可选）
2. 启用HTTP/3（QUIC）
3. 优化数据库索引
4. 配置负载均衡

#### 功能增强
1. 配置OnlyOffice/Collabora在线编辑
2. 启用两步验证
3. 配置邮件通知
4. 添加应用白名单
5. 配置外部存储（S3、FTP等）

#### 安全加固
1. 配置fail2ban防暴力破解
2. 启用审计日志
3. 定期安全扫描
4. 配置WAF（Web应用防火墙）

---

## 十二、参考文档

### 官方文档
- Nextcloud官方文档: https://docs.nextcloud.com/
- Docker官方文档: https://docs.docker.com/
- Let's Encrypt文档: https://letsencrypt.org/docs/
- Tailscale文档: https://tailscale.com/kb/

### 配置文件位置总结

| 文件类型 | 本地路径 | 容器内路径 | 服务器路径 |
|---------|---------|-----------|-----------|
| Docker Compose | ~/nextcloud/docker-compose.yml | - | - |
| Nextcloud配置 | ~/nextcloud/config.php | /var/www/html/config/config.php | - |
| MySQL配置 | ~/nextcloud/optimizations/mysql.cnf | /etc/mysql/conf.d/custom.cnf | - |
| PHP OPcache | ~/nextcloud/optimizations/00-opcache.ini | /usr/local/etc/php/conf.d/00-opcache.ini | - |
| PHP超时 | ~/nextcloud/optimizations/99-timeouts.ini | /usr/local/etc/php/conf.d/99-timeouts.ini | - |
| Nginx配置（本地） | /opt/homebrew/etc/nginx/servers/nextcloud-https.conf | - | - |
| SSL证书（本地） | ~/nextcloud/ssl/ | - | - |
| Nginx配置（服务器） | - | - | /etc/nginx/sites-available/nc.skyspace.eu.org.conf |
| Let's Encrypt证书 | - | - | /etc/letsencrypt/live/nc.skyspace.eu.org/ |

### 快速命令参考

```bash
# 启动服务
~/nextcloud/nextcloud.sh start

# 重启服务
~/nextcloud/nextcloud.sh restart

# 查看状态
~/nextcloud/nextcloud.sh status

# 查看日志
~/nextcloud/nextcloud.sh logs

# 添加trusted domain
docker exec nextcloud php occ config:system:set trusted_domains 8 --value="new.domain.com"

# 检查更新
docker exec nextcloud php occ update:check

# 扫描文件
docker exec nextcloud php occ files:scan --all

# 清理缓存
docker exec nextcloud php occ maintenance:repair

# 查看系统状态
docker exec nextcloud php occ status

# 证书续期
ssh server "certbot renew"

# 查看证书信息
ssh server "openssl x509 -in /etc/letsencrypt/live/nc.skyspace.eu.org/fullchain.pem -noout -subject -issuer -dates"
```

---

**文档版本**: 1.0
**最后更新**: 2026-03-05
**维护者**: admin@skyspace.eu.org

---

## 附录：完整域名列表

当前配置的trusted_domains：

| 序号 | 域名 | 协议 | 用途 |
|-----|------|------|------|
| 0 | localhost | HTTP | 本地测试 |
| 1 | localhost:8080 | HTTP | 本地测试 |
| 2 | nextcloud.skyspace.eu.org | HTTPS | 公网访问（旧） |
| 3 | 192.168.10.222:8080 | HTTP | 局域网访问 |
| 4 | 100.97.62.83:8080 | HTTP | Tailscale VPN |
| 5 | nc.skyspace.eu.org | HTTPS | 公网访问（新，推荐） |
| 6 | 192.168.10.222:8443 | HTTPS | 局域网HTTPS（推荐） |

**推荐使用**:
- 🌐 公网: `https://nc.skyspace.eu.org`
- 🏠 局域网: `https://192.168.10.222:8443`
- 🔐 VPN: `http://100.97.62.83:8080`

---

**END OF DOCUMENT**
