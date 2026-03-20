---
title: 'FRP配置诊断与修复指南'
categories: ["nextcloud"]
date: 2026-03-10T03:00:01+08:00
lastmod: 2026-03-10T03:00:01+08:00
draft: false
---
# FRP Token 修复指南

## 问题
服务端和客户端 Token 不匹配导致认证失败

## 修复步骤

### 1. 更新客户端 Token（选择其中一个）

#### 选项 A: 修改客户端 Token 匹配服务端
```bash
# 编辑客户端配置
vi /xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.toml

# 修改这一行：
auth.token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 改为：
auth.token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### 选项 B: 修改服务端 Token 匹配客户端
```bash
# 在服务器上
ssh server
sudo vi /etc/frp/frps.toml

# 修改这一行：
auth.token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 改为：
auth.token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 重启服务
sudo systemctl restart frps
```

### 2. 启动 Nextcloud FRP 客户端

```bash
# 方式 A: 手动启动（测试）
/opt/homebrew/opt/frpc/bin/frpc -c /xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.toml

# 方式 B: 后台运行
nohup /opt/homebrew/opt/frpc/bin/frpc -c /xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.toml > /tmp/frpc.log 2>&1 &

# 方式 C: 创建 systemd 服务（推荐）
# 创建 ~/Library/LaunchAgents/com.github.frpc.nextcloud.plist
```

### 3. 验证连接

```bash
# 检查服务端日志
ssh server "journalctl -u frps -f"

# 测试连接
curl -I http://xxx.xxx.xxx.xxx:8080
```

### 4. 更新 Nginx 配置（如果使用 FRP）

如果要让 nc.skyspace.eu.org 使用 FRP 而不是 Tailscale：

```nginx
# 在服务器上
ssh server
sudo vi /etc/nginx/sites-available/nc.skyspace.eu.org.conf

# 修改 upstream：
upstream nextcloud_backend {
    server xxx.xxx.xxx.xxx:8080;  # FRP 监听端口
    keepalive 64;
}

# 重启 Nginx
sudo systemctl reload nginx
```

## 推荐：不修复，直接使用 Tailscale

基于测试结果，**强烈建议继续使用 Tailscale**：

### Tailscale 优势
- ✅ 延迟更低（0.5ms vs FRP 预期的 10-50ms）
- ✅ 更稳定（0% 丢包）
- ✅ 无需维护（自动连接）
- ✅ 已在正常工作

### 操作
1. 保持当前 Tailscale 配置
2. 可选：停止 FRP 相关服务
3. 在 Cloudflare 为 nc.skyspace.eu.org 开启 CDN（已使用 Tailscale）

## 安全提示

日志显示有大量未授权连接尝试（来自 censys.local）：
```
register control error: token in login doesn't match token from configuration
```

建议：
- 更强密码（Web UI）
- 限制访问来源 IP
- 或考虑禁用 FRP Web UI

