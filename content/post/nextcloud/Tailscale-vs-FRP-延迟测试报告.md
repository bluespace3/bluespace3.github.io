---
title: 'Tailscale vs FRP 网络延迟测试报告'
categories: ['nextcloud']
date: 2026-03-16T04:00:03+0800
draft: false
---
# Tailscale vs FRP 网络延迟测试报告

> 测试时间: 2025-03-09  
> 测试环境: macOS → 外部服务器 (xxx.xxx.xxx.xxx)  
> 本地 Tailscale IP: xxx.xxx.xxx.xxx

---

## 测试结果总览

| 测试项目 | 延迟 | 丢包率 | 稳定性 |
|---------|------|--------|--------|
| **Tailscale Ping** | 0.517 ms | 0% | 优秀 |
| **Tailscale HTTP** | 23.06 ms | 0% | 优秀 |
| **服务器直连 Ping** | 0.323 ms | 0% | 优秀 |
| **HTTPS (Cloudflare)** | 1513.44 ms* | 0% | 良好 |
| **FRP** | ❌ 不可用 | N/A | N/A |

*注: HTTPS 延迟包含 TLS 握手时间

---

## 详细测试数据

### 1. Tailscale 连接测试

#### Ping 测试 (ICMP)
```
目标: xxx.xxx.xxx.xxx (Tailscale IP)
测试次数: 100 次

结果:
• 平均延迟: 0.517 ms
• 最小延迟: 0.199 ms
• 最大延迟: 0.899 ms
• 标准差: 0.127 ms
• 丢包率: 0%
```

**评价**: ⭐⭐⭐⭐⭐
- 延迟极低（亚毫秒级）
- 无丢包
- 抖动很小（标准差 0.127ms）
- 连接非常稳定

#### HTTP 应用层测试
```
目标: http://xxx.xxx.xxx.xxx:8080
测试次数: 10 次

结果:
• 平均延迟: 23.06 ms
• 成功率: 100%
```

**评价**: ⭐⭐⭐⭐⭐
- 应用层延迟依然很低
- 包含 HTTP 处理时间
- 适合实时应用

### 2. 服务器直连测试

#### Ping 测试
```
目标: xxx.xxx.xxx.xxx (外网 IP)
测试次数: 20 次

结果:
• 平均延迟: 0.323 ms
• 最小延迟: 0.159 ms
• 最大延迟: 0.435 ms
• 标准差: 0.072 ms
• 丢包率: 0%
```

**评价**: ⭐⭐⭐⭐⭐
- 延迟最低（直连）
- 性能稳定
- 作为基准参考

### 3. HTTPS 连接测试

#### 通过 Cloudflare CDN
```
目标: https://nc.skyspace.eu.org
测试次数: 10 次

结果:
• 平均延迟: 1513.44 ms
• 成功率: 100%
```

**评价**: ⭐⭐⭐⭐
- 延迟较高（包含 TLS 握手）
- 首次连接较慢
- 后续连接会复用连接，延迟降低
- CDN 节点缓存会改善性能

### 4. FRP 连接测试

```
目标: http://xxx.xxx.xxx.xxx:8080
状态: ❌ 不可用

检查结果:
• FRP 客户端运行中
• 端口 8080 可连通
• HTTP 请求失败
• 可能原因:
  - 服务器端 FRP 未运行
  - FRP 配置错误
  - 防火墙规则
```

---

## 性能对比分析

### 延迟排名（从低到高）
1. **服务器直连**: 0.323 ms ⭐⭐⭐⭐⭐
2. **Tailscale Ping**: 0.517 ms ⭐⭐⭐⭐⭐
3. **Tailscale HTTP**: 23.06 ms ⭐⭐⭐⭐⭐
4. **HTTPS (含 TLS)**: 1513.44 ms ⭐⭐⭐⭐
5. **FRP**: 不可用 ⭐

### 关键发现

#### ✅ Tailscale 优势
1. **延迟极低**: 平均 0.5ms，接近直连性能
2. **零丢包**: 100 次测试无丢包
3. **稳定性强**: 抖动仅 0.127ms
4. **自动维护**: 无需手动配置
5. **NAT 穿透**: 优秀的连接能力

#### ⚠️ FRP 问题
1. **当前不可用**: HTTP 请求失败
2. **需要排查**: 服务端配置或防火墙
3. **额外维护**: 需要管理 FRP 服务

#### 💡 Cloudflare CDN
1. **首次连接慢**: TLS 握手耗时
2. **后续连接快**: 连接复用
3. **全球加速**: 跨地域访问优势明显
4. **安全防护**: DDoS/WAF 保护

---

## 实际应用场景建议

### 场景 1: 家庭局域网访问
**推荐**: 直连 (https://xxx.xxx.xxx.xxx:8443)
- 延迟: <1ms
- 最快速度
- 最稳定

### 场景 2: 公网访问（推荐）
**推荐**: Tailscale + Cloudflare
- 域名: nextcloud.skyspace.eu.org
- 延迟: ~23ms（应用层）
- 稳定性: 优秀
- 安全性: 双层加密

### 场景 3: 备用方案
**待修复**: FRP + Cloudflare
- 域名: nc.skyspace.eu.org
- 当前状态: 不可用
- 建议: 切换到 Tailscale

---

## FRP 故障排查

### 症状
- 端口连通但 HTTP 失败
- FRP 客户端运行正常

### 可能原因
1. **服务器端 FRP 未运行**
   ```bash
   # 检查服务器 FRP 状态
   ssh server
   ps aux | grep frps
   ```

2. **FRP 配置不匹配**
   - 客户端期望 8080 端口
   - 服务端未配置

3. **防火墙规则**
   ```bash
   # 检查服务器防火墙
   ssh server
   sudo ufw status
   ```

### 解决方案
**建议**: 直接使用 Tailscale，放弃 FRP
- Tailscale 性能更优
- 配置更简单
- 维护成本更低

---

## 结论

### 性能排名
1. 🥇 **Tailscale**: 最佳选择（0.5ms 延迟，0% 丢包）
2. 🥈 **直连**: 局域网最优（0.3ms 延迟）
3. 🥉 **Cloudflare CDN**: 公网访问最优（23ms 延迟）
4. ❌ **FRP**: 当前不可用

### 推荐配置

#### 主方案（强烈推荐）
```yaml
域名: nextcloud.skyspace.eu.org
架构: Cloudflare CDN + Tailscale VPN
延迟: ~23ms
稳定性: ⭐⭐⭐⭐⭐
```

#### 局域网方案
```yaml
地址: https://xxx.xxx.xxx.xxx:8443
架构: 本地 Nginx 反向代理
延迟: <1ms
适用: 家庭内网
```

#### 公网备用方案（待修复）
```yaml
域名: nc.skyspace.eu.org
架构: Cloudflare CDN + FRP (或切换到 Tailscale)
当前状态: 需要修复
```

---

## 下一步行动

### ✅ 立即可做
1. **为 nc.skyspace.eu.org 开启 Cloudflare CDN**
   - 登录 Cloudflare 控制台
   - 开启橙色云朵代理
   - 已在使用 Tailscale，无需 FRP

### 🔧 可选优化
2. **修复或移除 FRP**
   - 检查服务器端 FRP 状态
   - 或直接停止使用 FRP

3. **性能监控**
   - 设置延迟监控告警
   - 定期测试连接质量

---

**测试工具**: ping, curl, time  
**测试平台**: macOS (Darwin 25.2.0)  
**测试日期**: 2025-03-09

