---
title: 'AWQ-INT4-vs-AutoRound-W4A16-单发速度AB-0904'
categories: ["硬件"]
date: 2026-09-04T23:02:35+08:00
lastmod: 2026-09-04T23:02:35+08:00
draft: false
---
# Qwen3.8-Flash-Next：AWQ-INT4 vs AutoRound W4A16 单发速度 A/B（2026-09-04）

## 结论（TL;DR）

**速度几乎无差**：500K/900K 两点 prefill 与 decode 均与 AutoRound 基线持平（±3% 内，属 MTP 接受率自然波动）。AWQ-INT4 (g32) 没有速度优势，也没有劣化。选型依据只剩质量与显存驻留成本——速度不构成决策因素。

## 测试口径（与基线严格同参）

- 工具：~/llm_speedtest python 后台（WS）+ ws_bench c1 单发，`qwen38flash_awq_c1_500k900k_0904.log`
- 硬件/部署：双 CMP170HX PP2，PLE mmap（BF16 102G 表），MTP spec=4，YaRN f4.0，FLASH_ATTN，PIECEWISE cudagraph
- 服务参数唯一差异：AWQ 因权重驻留开销大，窗口 1048576→921600、MEM 0.97→0.98（500K/900K 测试点不受影响）
- 量化本质：AWQ=compressed-tensors pack-quantized int4 g32/MSE；AutoRound=int4 g128（PLE/embed/hyper_connection 等 BF16）

## 结果

| 指标 | AWQ-INT4 g32 | AutoRound g128 基线 | 差异 |
|---|---|---|---|
| 500K prefill t/s | **4256** | 4242 | +0.3% |
| 500K decode t/s | **63.6** | 61.5 | +3.4% |
| 500K TTFT s | 117.5 | 117.9 | -0.3% |
| 900K prefill t/s | **2002** | 2035 | -1.7% |
| 900K decode t/s | **67.1** | 66.8 | +0.4% |
| 900K TTFT s | 449.7 | 442.2 | +1.7% |

峰值 decode 339 t/s 出现在并发统计窗口（MTP 多事件聚合），单流稳定值即上表。
MTP 接受率两版相近（AWQ 期间出现 39-62% 区间采样，与基线期一致）。

## 代价与限制

1. **显存驻留**：AWQ compressed-tensors 格式 vLLM 权重驻留更大（每卡 KV 可用 24.9G→19.8G，约 -5G/卡），1M 窗口装不下（需 15G KV > 可用 12G 首次启动失败），只能 921600。
2. **磁盘**：AWQ 全量 188.3G；本次跳过 20 个纯 PLE 分片（96G，与本地 AutoRound model-00016 字节级同源，元数据 131/131 张量一致 + 组装后抽样 5 处 1MB 全一致），实下 92.3G + 本地组装 96G。
3. **质量**：理论 g32 vs g128 差 0.1~0.3 点（09-03 分析），速度持平下需质量评测定夺，未测。

## 复现

```bash
# 启动（AWQ）
sudo -S -p '' bash $HERMES_HOME/tools/model-launcher/start-flashnext-awq-1m.sh
# 测试
cd ~/llm_speedtest/python && .venv/bin/python /tmp/ws_bench_1m.py 1 | tee results/qwen38flash_awq_c1_500k900k_0904.log
# 基线记录: results/qwen38flash_bf16ple_1m_c1_500k900k_0904.log
```

## 后续建议

- 切回 AutoRound 常驻服务（1M 窗口完整、KV 更大）：`start-flashnext-bf16ple-1m.sh`
- 若要定质量，需另做评测（评测集未定）；速度维度本 A/B 已闭环。
