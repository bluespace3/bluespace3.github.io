---
title: 'nc域名FRP配置成功报告'
categories: ["nextcloud"]
date: 2026-03-10T03:00:01+08:00
lastmod: 2026-03-10T03:00:01+08:00
draft: false
---
# nc.skyspace.eu.org FRP 配置成功报告

> 配置时间: 2025-03-09 15:12  
> 状态: ✅ 配置成功并正常运行

---

## 📊 配置变更

### 修改前
```
nc.skyspace.eu.org → 服务器 → Tailscale (xxx.xxx.xxx.xxx:8080) → Mac
```

### 修改后
```
nc.skyspace.eu.org → 服务器 → FRP (xxx.xxx.xxx.xxx:8080) → Mac
```

---

## 🔧 配置步骤

### 1. 备份配置
```bash
cp /etc/nginx/sites-available/nc.skyspace.eu.org.conf \
   /etc/nginx/sites-available/nc.skyspace.eu.org.conf.backup
```

### 2. 修改配置
修改前：
```nginx
proxy_pass http://xxx.xxx.xxx.xxx:8080;  # Tailscale
```

修改后：
```nginx
proxy_pass http://xxx.xxx.xxx.xxx:8080;  # FRP
```

### 3. 应用配置
```bash
nginx -t                    # 测试配置语法
systemctl reload nginx      # 重载配置
```

---

## ✅ 验证结果

### 访问测试
```bash
curl -I https://nc.skyspace.eu.org
# HTTP/2 302 ✅ 正常
```

### 性能测试

| 域名 | 路径 | 平均延迟 | 状态 |
|------|------|---------|------|
| **nextcloud.skyspace.eu.org** | Tailscale + Cloudflare | 1.40 秒 | ✅ |
| **nc.skyspace.eu.org** | FRP | 1.39 秒 | ✅ |

**结论**: FRP 和 Tailscale + Cloudflare 性能接近！

---

## 🎯 当前架构

```
外网用户访问 Nextcloud 有两条路径：

路径1: nextcloud.skyspace.eu.org (推荐)
  ↓
Cloudflare CDN
  ↓
服务器 (xxx.xxx.xxx.xxx)
  ↓
Tailscale VPN
  ↓
你的Mac (Nextcloud)

路径2: nc.skyspace.eu.org (备用)
  ↓
服务器 (xxx.xxx.xxx.xxx)
  ↓
FRP 隧道
  ↓
你的Mac (Nextcloud)
```

---

## 📊 性能分析

### 为什么两者延迟接近？

**Tailscale + Cloudflare (1.40秒)**:
- Cloudflare CDN: 全球节点，可能跳转多次
- TLS 握手: 多次加密/解密
- Tailscale: WireGuard 加密
- 总开销: CDN + TLS + VPN

**FRP (1.39秒)**:
- 直连服务器
- FRP 隧道转发
- TLS 握手
- 总开销: 隧道 + TLS

**结论**: 
- ✅ FRP 没有比 Tailscale 慢很多
- ✅ 两者性能相当
- ✅ Cloudflare CDN 在这个场景下优势不明显

---

## 🔍 实际测试验证

### FRP 客户端日志
```
2026-03-09 13:52:12 - proxy added: [nextcloud-http]
2026-03-09 13:52:12 - start proxy success
```

### 服务器 FRP 日志
```
2026-03-09 13:52:12 - new proxy [nextcloud-http] success
2026-03-09 13:52:19 - get a user connection
```

### Nginx 访问日志
```
正常的 HTTPS 请求和响应
```

---

## 💡 使用建议

### 主访问（推荐）
```
https://nextcloud.skyspace.eu.org
```
- 有 Cloudflare CDN 保护
- 全球加速
- DDoS 防护

### 备用访问
```
https://nc.skyspace.eu.org
```
- 直连服务器
- 走 FRP 隧道
- 可靠的备用方案

---

## 🛠️ 故障切换

如果某个域名无法访问：

### 方案1: 切换到另一个域名
```
nextcloud.skyspace.eu.org ❌
↓
nc.skyspace.eu.org ✅
```

### 方案2: 恢复原有配置
```bash
ssh server
cp /etc/nginx/sites-available/nc.skyspace.eu.org.conf.backup \
   /etc/nginx/sites-available/nc.skyspace.eu.org.conf
systemctl reload nginx
```

---

## 📝 配置文件位置

**服务器端**:
- 配置文件: `/etc/nginx/sites-available/nc.skyspace.eu.org.conf`
- 备份文件: `/etc/nginx/sites-available/nc.skyspace.eu.org.conf.backup`
- 访问日志: `/var/log/nginx/nc.skyspace.eu.org.access.log`
- 错误日志: `/var/log/nginx/nc.skyspace.eu.org.error.log`

**客户端**:
- FRP 配置: `~/.config/frp/frpc.toml`
- FRP 日志: `/tmp/frpc-nextcloud.log`

---

## ✅ 配置成功确认

- [x] 备份原配置
- [x] 修改为使用 FRP
- [x] Nginx 配置语法正确
- [x] Nginx 重载成功
- [x] nc.skyspace.eu.org 可访问
- [x] FRP 日志显示连接正常
- [x] 性能测试通过

---

**配置完成**: 2025-03-09 15:12  
**测试通过**: 2025-03-09 15:14  
**状态**: ✅ 正常运行

