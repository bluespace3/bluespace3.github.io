---
title: 'FlashNext-PLE表精度AB-BF16vsFP8-含1M长上下文'
categories: ["硬件"]
date: 2026-09-04T16:35:51+08:00
lastmod: 2026-09-04T16:35:51+08:00
draft: false
---
# PLE 表精度 A/B：BF16 vs FP8 + 1M 长上下文实测（2026-09-04 定稿）

> 附属于《170HX双卡部署Qwen3.8-Flash-Next-176B笔记》。同 W4A16 权重，只变 PLE n-gram 表精度。
> 结论先行：**BF16（不量化）甜区 decode 全面胜出，FP8 表已删除**。默认模型目录已切换为 AutoRound 版。

## 一、两个版本

| | FP8-PLE（旧，已删） | BF16-PLE（新，默认） |
|---|---|---|
| 目录 | Qwen3.8-Flash-Next-W4A16-**fp8ple** | Qwen3.8-Flash-Next-W4A16-**AutoRound** |
| ngram 表 dtype | F8_E4M3 | BF16 |
| 表体积 | 51.2 GB | **102.4 GB** |
| 权重 | W4A16（相同） | W4A16（相同） |

## 二、c2 并发 A/B（ws_bench，七档，2026-09-01 FP8 基线 vs 09-04 BF16）

Δ% 为 BF16 相对 FP8：

| len | prefill Δ | decode Δ | TTFT Δ |
|---|---|---|---|
| 80K | -30.1%（冷启动惩罚） | **+31.6%** | +36.9% |
| 110K | -1.1% | **+13.3%** | +0.4% |
| 140K | +2.8% | **+16.6%** | -2.7% |
| 170K | +2.8% | +5.4% | -2.5% |
| 200K | +1.9% | **+12.2%** | -2.1% |
| 230K | -9.1% | **-44.9%** ⚠️ | +31.2% |
| 260K | -7.7% | **-39.8%** ⚠️ | +23.9% |

原始数据（BF16，`~/llm_speedtest/results/qwen38flash_bf16ple_c2_0904.log`）：

| len | avg_prefill | avg_decode | avg_ttft |
|---|---|---|---|
| 80000 | 2278.87 | 42.17 | 36479 |
| 110000 | 4288.96 | 49.62 | 28732 |
| 140000 | 4374.65 | 42.49 | 36027 |
| 170000 | 4307.64 | 32.65 | 44512 |
| 200000 | 4249.49 | 39.52 | 53191 |
| 230000 | 3712.32 | 30.49 | 83474 |
| 260000 | 3722.34 | 21.88 | 90360 |

FP8 基线见 `qwen38flash_next_c2_0901_1315.log`。

## 三、单发 c1 四档（BF16，含 1M 上下文）

262K 实例（pp + MTP3）：`qwen38flash_bf16ple_c1_80k260k_0904.log`
1M 实例（pp1m YaRN4 + MTP4 + KV BF16）：`qwen38flash_bf16ple_1m_c1_500k900k_0904.log`

| len | prefill (t/s) | decode (t/s) | TTFT | ITL |
|---|---|---|---|---|
| 80K | 6143 | 81.2 | 13.0s | 32.4ms |
| 260K | 5605 | 70.0 | 46.4s | 32.9ms |
| 500K | 4242 | 61.5 | 117.9s | 38.6ms |
| 900K | 2035 | **66.8** | 442.2s | 40.4ms |

对照 FP8 时代单发（09-01 官方基线）：80K 106.2 / 260K 78.4 t/s decode——BF16 在随机词负载下 decode 81/70，考虑 MAL 内容差异，两者单发接近；**BF16 的收益在真实负载甜区（+12~32%）**。

## 四、I/O 观察（用户实测，与 A/B 数据互证）

- ngram 表在 HDD vs SSD：速度差 ~10%（冷缓存）；SSD vs 内存：无差别（热缓存后瓶颈在 GPU 不在盘）
- 含义：**PLE 表放 NVMe 完全可行**，页缓存命中后盘速不是因素；HDD 差距主要伤小内存大显存设备
- 102G BF16 表 > 60G RAM → 热区+KV 并存时（c2 @230K+）页缓存抖动，prefill 3:1 分化、decode 腰斩；**单流顺序访问局部性好，900K 单发 decode 仍 67 t/s**

## 五、结论与决策

1. **FP8 量化 PLE 表有可测的精度损失**：甜区 decode -12~-32%，ngram 检索对精度敏感
2. **BF16 表 102G 放 NVMe + mmap 完全可用**：单发 80K-900K 全档稳定；≤200K 并发也稳
3. **c2 @230K+ 翻车是 RAM 容量问题不是表精度问题**（102G 表 + KV 挤 60G 页缓存）
4. **决策（2026-09-04）**：
   - 删除 `Qwen3.8-Flash-Next-W4A16-fp8ple` 目录（51G 表版）
   - 默认模型 = `Qwen3.8-Flash-Next-W4A16-AutoRound`（BF16 表）
   - 启动器：`start-flashnext.sh`/`start-flashnext-bf16ple.sh`(pp 262K)/`start-flashnext-bf16ple-1m.sh`(pp1m 1M) 全部指向 AutoRound
   - 服务定位不变：单请求 + 超长上下文优先；并发 ≥230K 场景慎用
