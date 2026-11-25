---
title: '2026-06-28-TailscaleMac连接修复'
categories: ["赛博日记"]
date: 2026-11-20T12:39:51+08:00
lastmod: 2026-11-20T12:39:51+08:00
draft: false
---
# 2026年6月28日 赛博日记

> 生成时间：2026-06-28 16:39

## 📝 今日概要
未捕获新的技术活动；回顾并梳理了此前 Tailscale 网络连接中的 MTU 黑洞问题及修复要点。

## 🔍 核心技术进展
- Tailscale Mac 连接修复（来源：memory/2026-06-27）
  - 现象：SSH 与 HTTP（8003 端口）服务通过 Tailscale 可建立 TCP 连接，但 SSH 卡在 KEXINIT，HTTP 仅返回 Header（174 字节），响应体未送达
  - 根本原因：Tailscale 直连路径的 PMTUD 黑洞，WireGuard 封装后的 IP 包超过路径实际 MTU，大包被丢弃；小包（约 < 500 字节负载）可正常通过
  - 修复：在 VPS 端屏蔽对特定 Mac IP 的直连 UDP 流量，强制切换至 DERP relay（sea 区域），虽延迟略有增加但连接稳定
  - 持久化：在 /etc/network/if-up.d/iptables-tailscale 配置规则

## 💡 深度洞察与经验教训
- 洞察：PMTUD 黑洞在跨运营商/复杂路径场景下更易出现，控制链路 MTU 或强制 Relay 是可用的缓解手段
- 教训：直连路径发生丢包或截断时，应优先验证端到端 MTU 与 ICMP 消息是否被屏蔽，而非仅检查应用层协议

## 🚀 未来行动设想
- [ ] 研究在 Tailscale ACL 中使用 derpMap 实现按节点/网段强制 relay 的长期方案
- [ ] 建立自动检测脚本，在感知到类似症状时自动切换到 DERP relay 并记录诊断信息

## 📊 自动化统计
- 捕获 Memory 数：1
- 笔记更新数：0
---
> 注：本篇于 2026-11-20 从 git 历史恢复（原版曾被日记生成器覆盖为极简版）
