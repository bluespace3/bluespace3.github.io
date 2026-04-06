---
title: 'Nginx SSL 证书迁移指南'
categories: ["软件工具"]
date: 2026-04-06T21:21:10+08:00
lastmod: 2026-04-06T21:21:10+08:00
draft: false
---
# Nginx + SSL 证书迁移指南

> **创建时间**: 2026-04-06  
> **适用范围**: Ubuntu VPS 环境下的 Nginx 反向代理迁移  
> **核心目标**: 零 SSL 证书丢失、零域名配置错误

---

## 📋 目录

1. [迁移前准备](#迁移前准备)
2. [Nginx 配置备份](#nginx 配置备份)
3. [SSL 证书备份](#ssl 证书备份)
4. [新环境搭建](#新环境搭建)
5. [配置恢复与验证](#配置恢复与验证)
6. [常见问题解决](#常见问题解决)

---

## 🚀 迁移前准备

### 1.1 检查清单
- [ ] 确认新旧 VPS 的 IP 地址
- [ ] 确认域名 DNS 解析状态
- [ ] 确认 SSL 证书有效期
- [ ] 检查 Nginx 版本兼容性

### 1.2 识别 Nginx 组件
在旧 VPS 上执行以下命令：

```bash
# 查看 Nginx 配置位置
nginx -V 2>&1 | grep "configure arguments"

# 列出所有站点配置
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/

# 查看当前运行配置
nginx -T | grep -A5 "server_name"

# 检查 SSL 证书状态
ls -la /etc/letsencrypt/live/
```

---

## ⚙️ Nginx 配置备份

### 2.1 备份 Nginx 配置文件
```bash
# 备份完整 Nginx 目录
tar czvf nginx_backup.tar.gz /etc/nginx/

# 备份单个站点配置
cp /etc/nginx/sites-available/default ~/nginx_site_backup.conf

# 备份 http 配置
cp /etc/nginx/nginx.conf ~/nginx_main_backup.conf

# 备份 conf.d 目录（如有）
tar czvf nginx_conf.d.tar.gz /etc/nginx/conf.d/

# 备份 uwsgi/fastcgi 配置（如有）
tar czvf nginx_uwsgi.tar.gz /etc/nginx/fastcgi_params
```

### 2.2 记录关键配置信息
```bash
# 导出所有 server 块配置
grep -A100 "server {" /etc/nginx/sites-enabled/* > nginx_servers.txt

# 记录环境变量
cat /etc/nginx/env.conf

# 检查自定义模块
nginx -V 2>&1 | grep "\-\-" > nginx_modules.txt
```

---

## 🔒 SSL 证书备份（核心步骤）

### 3.1 备份 Let's Encrypt 证书
```bash
# 备份整个 letsencrypt 目录（最重要！）
tar czvf letsencrypt_backup.tar.gz /etc/letsencrypt/

# 查看当前证书信息
certbot certificates

# 备份特定域名的证书
tar czvf domain_backup.tar.gz /etc/letsencrypt/live/yourdomain.com/
```

### 3.2 证书文件结构说明
```
/etc/letsencrypt/
├ live/
│  └ yourdomain.com/
│     ├ cert.pem          # 证书
│     ├ privkey.pem       # 私钥（绝对不能丢！）
│     ├ chain.pem         # 中间证书
│     └ fullchain.pem     # 完整证书链
├ archived/              # 历史证书
├ renewal/               # 自动续期配置
│  └ yourdomain.com.conf
└ renewal-hooks/         # 续期钩子脚本
```

### 3.3 备份其他 SSL 证书源
```bash
# 如果使用的是自定义证书
tar czvf custom_ssl_backup.tar.gz /etc/nginx/ssl/

# 备份 Apache SSL（如果双运行）
tar czvf apache_ssl.tar.gz /etc/ssl/
```

---

## 🏗️ 新环境搭建

### 4.1 安装 Nginx
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Nginx
sudo apt install nginx -y

# 检查版本
nginx -v

# 确保配置目录结构
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
sudo mkdir -p /etc/nginx/conf.d
```

### 4.2 安装 Certbot（如需 Let's Encrypt）
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 验证安装
certbot --version
```

---

## 🔄 配置恢复与验证

### 5.1 恢复 Nginx 配置
```bash
# 传输备份文件
rsync -avzP nginx_backup.tar.gz user@new_vps:~/backup/

# 在新机器解压
cd /tmp
tar xzf ~/nginx_backup.tar.gz

# 备份旧配置（防止覆盖）
sudo mv /etc/nginx /etc/nginx.old

# 恢复新配置
sudo mv /tmp/etc/nginx /etc/nginx

# 检查权限
sudo chown -R root:root /etc/nginx
sudo chmod -R 755 /etc/nginx
```

### 5.2 恢复 SSL 证书
```bash
# 传输证书备份
rsync -avzP letsencrypt_backup.tar.gz user@new_vps:~/backup/

# 在新机器解压到正确位置
cd /tmp
tar xzf ~/letsencrypt_backup.tar.gz
sudo mv /tmp/etc/letsencrypt /etc/letsencrypt

# 检查证书权限
sudo chmod 644 /etc/letsencrypt/live/*/cert.pem
sudo chmod 600 /etc/letsencrypt/live/*/privkey.pem
sudo chmod 644 /etc/letsencrypt/live/*/chain.pem
```

### 5.3 更新配置文件中的 IP 地址
```bash
# 检查配置中是否有硬编码的 IP
grep -r "old.ip.address" /etc/nginx/

# 批量替换（谨慎使用）
sudo sed -i 's/old.ip.address/new.ip.address/g' /etc/nginx/sites-available/*

# 或手动编辑配置文件
sudo nano /etc/nginx/sites-available/yourdomain
```

### 5.4 测试配置
```bash
# 测试 Nginx 配置语法
sudo nginx -t

# 如果配置失败，查看详细错误
sudo nginx -T 2>&1 | grep "error"

# 如果证书路径有问题
sudo certbot certificates
```

### 5.5 启动服务
```bash
# 启动 Nginx
sudo systemctl start nginx

# 设置开机自启
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx

# 查看日志
sudo tail -f /var/log/nginx/error.log
```

---

## ✅ 验证步骤

### 配置验证
```bash
# 检查域名配置
grep "server_name" /etc/nginx/sites-available/*

# 检查 SSL 证书
grep "ssl_certificate" /etc/nginx/sites-available/*

# 检查证书是否可用
openssl s_client -connect localhost:443 -servername yourdomain.com
```

### 功能验证
```bash
# 测试 HTTP（应重定向到 HTTPS）
curl -I http://yourdomain.com

# 测试 HTTPS
curl -I https://yourdomain.com

# 测试应用反向代理
curl http://localhost/api/endpoint

# 检查 SSL 有效期
curl -I https://yourdomain.com | grep -i "x-ssl-expiry"
```

---

## ❗ 常见问题解决

### 问题 1：证书失效或过期
**原因**: 证书文件损坏或路径错误  
**解决**:
```bash
# 重新生成证书
sudo certbot certonly --standalone -d yourdomain.com

# 检查证书状态
sudo certbot certificates

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 问题 2：Nginx 启动失败 - 端口被占用
**原因**: 旧 Nginx 服务仍在运行  
**解决**:
```bash
# 停止旧 Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 查找并结束进程
sudo lsof -i :80
sudo kill -9 [PID]
```

### 问题 3：SSL 重定向失败
**原因**: HTTP 到 HTTPS 配置错误  
**解决**:
```bash
# 确保有正确的重定向配置
cat /etc/nginx/sites-available/yourdomain | grep -A5 "return 301"

# 添加重定向（如果缺失）
sudo nano /etc/nginx/sites-available/default

# 配置示例：
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

### 问题 4：证书路径不匹配
**原因**: 配置中的证书路径与实际位置不符  
**解决**:
```bash
# 检查配置中的证书路径
grep ssl_certificate /etc/nginx/sites-available/*

# 更新为正确的路径
sudo nano /etc/nginx/sites-available/yourdomain

# 常用路径：
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

---

## 📊 迁移检查清单

- [ ] Nginx 配置文件完整备份
- [ ] SSL 证书（含私钥）完整备份
- [ ] Nginx 在新机器安装完成
- [ ] 所有配置正确恢复
- [ ] 证书路径更新为新机器 IP
- [ ] Nginx 配置测试通过（nginx -t）
- [ ] Nginx 服务成功启动
- [ ] HTTP 自动重定向到 HTTPS
- [ ] SSL 证书验证通过
- [ ] 应用反向代理正常工作
- [ ] 错误日志无异常

---

## 💡 最佳实践建议

1. **证书私钥保护**: `privkey.pem` 是核心，丢失即无法恢复 HTTPS
2. **配置版本控制**: 使用 Git 跟踪 Nginx 配置文件变更
3. **自动续期**: 确保 `certbot` 定时任务正常工作
   ```bash
   sudo certbot renew --dry-run
   ```
4. **测试域名**: 在修改 DNS 前，使用本地 `hosts` 文件测试
5. **保留旧机器**: 至少保留 48 小时确保一切正常

---

## 🔧 高级技巧

### 批量更新配置中的 IP
```bash
# 使用 sed 批量替换（备份后操作）
sudo cp -r /etc/nginx /etc/nginx.backup
sudo sed -i 's/123\.45\.67\.89/98\.76\.54\.32/g' /etc/nginx/sites-available/*
```

### 检查证书续期状态
```bash
# 查看续期配置
cat /xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.com.conf

# 手动测试续期
sudo certbot renew --force-renewal
```

### 导出 Nginx 完整配置
```bash
# 合并所有配置
sudo nginx -T > /tmp/nginx_full_config.conf
```

---

> **创建时间**: 2026-04-06  
> **最后更新**: 2026-04-06
