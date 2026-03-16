---
title: 'Nextcloud 双域名性能测试报告'
categories: ['nextcloud']
date: 2026-03-17T03:00:04+0800
draft: false
---
# Nextcloud 双域名性能测试报告

> 测试时间: 2025-03-09 15:35  
> 状态: ✅ 两个域名都开启了 Cloudflare CDN  
> 测试环境: macOS → Cloudflare (SIN节点) → 服务器 → 后端隧道 → Mac

---

## 📊 测试结果

### 延迟对比

| 域名 | 路径 | 平均延迟 | 最小延迟 | 最大延迟 | 性能比 |
|------|------|---------|---------|---------|--------|
| **nextcloud.skyspace.eu.org** | CDN + Tailscale | 1.42 秒 | 1.03 秒 | 2.18 秒 | 基准 (100%) |
| **nc.skyspace.eu.org** | CDN + FRP | 1.50 秒 | 1.04 秒 | 2.30 秒 | 106% (慢6%) |

### 关键发现

✅ **两个域名都经过 Cloudflare CDN**
```bash
# 响应头验证
server: cloudflare
cf-ray: 9d987bf87ca581d7-SIN  # 新加坡节点
```

✅ **性能差异极小**
- 差距仅 0.08 秒（6%）
- 属于正常网络波动范围
- 用户体验无明显区别

✅ **CDN 提供了明显的保护**
- DDoS 防护
- Web 应用防火墙
- 隐藏源站 IP
- 全球加速

---

## 🏗️ 当前架构

```
外网用户访问 Nextcloud 有两条等价路径：

┌────────────────────────────────────────────────────────┐
│ 路径1: nextcloud.skyspace.eu.org                        │
│                                                         │
│ 用户 → Cloudflare CDN (新加坡)                          │
│        ↓                                                │
│     服务器 (xxx.xxx.xxx.xxx)                               │
│        ↓                                                │
│   Tailscale VPN (xxx.xxx.xxx.xxx)                         │
│        ↓                                                │
│     你的Mac (Nextcloud:8080)                           │
│                                                         │
│ 延迟: 1.42秒                                            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ 路径2: nc.skyspace.eu.org                               │
│                                                         │
│ 用户 → Cloudflare CDN (新加坡)                          │
│        ↓                                                │
│     服务器 (xxx.xxx.xxx.xxx)                               │
│        ↓                                                │
│     FRP 隧道 (xxx.xxx.xxx.xxx:8080)                          │
│        ↓                                                │
│     你的Mac (Nextcloud:8080)                           │
│                                                         │
│ 延迟: 1.50秒                                            │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 性能分析

### 为什么两者性能接近？

**相同因素**:
1. ✅ 都经过 Cloudflare CDN（相同的新加坡节点）
2. ✅ 都使用 HTTPS 加密
3. ✅ 都有 TLS 握手开销
4. ✅ 都访问同一个 Nextcloud 实例

**差异因素**:
1. ⚖️ 后端隧道不同（Tailscale vs FRP）
   - 差距仅 0.08 秒（6%）
   - 相比 CDN 延迟可忽略

2. ⚖️ 网络波动影响
   - 不同时间的网络状况
   - CDN 节点负载变化

### Cloudflare CDN 的作用

**主要功能**:
- ✅ DDoS 防护
- ✅ Web 应用防火墙 (WAF)
- ✅ 隐藏源站 IP
- ✅ HTTP/3 支持
- ✅ 自动压缩
- ✅ 全球 CDN 节点

**性能影响**:
- 首次连接较慢（TLS 握手）
- 后续连接复用会更快
- 跨地域访问有明显优势

---

## 📈 测试数据详情

### 测试方法
```bash
# 各测试 20 次，取平均值
for i in {1..20}; do
  curl -o /dev/null -s -w "%{time_total}\n" https://域名
done
```

### 统计结果

**nextcloud.skyspace.eu.org** (Tailscale):
- 测试次数: 20
- 平均延迟: 1.42 秒
- 最小延迟: 1.03 秒
- 最大延迟: 2.18 秒
- 标准差: ~0.3 秒

**nc.skyspace.eu.org** (FRP):
- 测试次数: 20
- 平均延迟: 1.50 秒
- 最小延迟: 1.04 秒
- 最大延迟: 2.30 秒
- 标准差: ~0.3 秒

---

## 🎯 使用建议

### 主访问域名
```
https://nextcloud.skyspace.eu.org
```
**理由**:
- ✅ 稍快（1.42 秒）
- ✅ Tailscale 更成熟稳定
- ✅ 适合日常使用

### 备用域名
```
https://nc.skyspace.eu.org
```
**理由**:
- ✅ 性能接近（1.50 秒）
- ✅ FRP 作为技术备份
- ✅ 故障切换选项

### 两个域名都保留的优势

1. **高可用性**: 一个出问题可用另一个
2. **负载分担**: 可以分散访问压力
3. **技术验证**: 对比不同技术方案
4. **容错能力**: 降低单点故障风险

---

## 🛠️ 故障切换流程

### 如果主域名无法访问

```bash
# 1. 测试备用域名
curl -I https://nc.skyspace.eu.org

# 2. 如果备用域名正常，继续使用
# 3. 检查主域名问题
ssh server
nginx -t
systemctl status nginx

# 4. 如果需要，恢复配置
cp /etc/nginx/sites-available/nc.skyspace.eu.org.conf.backup \
   /etc/nginx/sites-available/nc.skyspace.eu.org.conf
systemctl reload nginx
```

---

## 📊 性能优化建议

### 当前状态评估

✅ **已优化**:
- Cloudflare CDN 已启用
- HTTP/2 支持
- SSL/TLS 优化
- 后端隧道稳定

⚠️ **可优化**:
1. **启用 HTTP/3**: Cloudflare 支持，可提升性能
2. **缓存规则**: 静态资源缓存优化
3. **压缩配置**: Brotli/Gzip 压缩
4. **监控告警**: 设置性能监控

### 性能基准

- ✅ 当前延迟: 1.4-1.5 秒（可接受）
- ✅ 稳定性: 良好
- ✅ 可用性: 两个域名互备

---

## 🎉 结论

### 配置成功确认

- [x] nc.skyspace.eu.org 配置为使用 FRP
- [x] 两个域名都启用 Cloudflare CDN
- [x] 性能测试通过
- [x] 两者延迟接近（1.4-1.5 秒）
- [x] 互为备份，提高可用性

### 最终架构

```
Nextcloud 双域名高可用架构

主: https://nextcloud.skyspace.eu.org
     ↓
  Cloudflare + Tailscale
     ↓
  你的 Mac (Nextcloud)

备: https://nc.skyspace.eu.org
     ↓
  Cloudflare + FRP
     ↓
  你的 Mac (Nextcloud)
```

### 总结

✅ **配置成功**: nc.skyspace.eu.org 现在走 FRP  
✅ **CDN 加速**: 两个域名都启用 Cloudflare  
✅ **性能相当**: 差距仅 6%，可忽略  
✅ **高可用**: 两个域名互为备份  

**建议**: 两个域名都保留，根据情况选择使用！

---

**测试完成**: 2025-03-09 15:35  
**配置状态**: ✅ 正常运行  
**性能评估**: ⭐⭐⭐⭐ 良好

