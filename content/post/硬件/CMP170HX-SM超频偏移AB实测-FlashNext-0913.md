---
title: 'CMP170HX-SM超频偏移AB实测-FlashNext-0913'
categories: ["硬件"]
date: 2026-09-13T22:49:54+08:00
lastmod: 2026-09-13T22:49:54+08:00
draft: false
---
# CMP 170HX SM VF 偏移 A/B 实测（FlashNext 服务口径）— 2026-09-13

## 背景与目的

170tune 按序列给双卡定的偏移：GPU0=+200 / GPU1=+250（gate receipt:
`/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxoff250_clk1400.json`，08-31 认证，
4 sweeps，峰值 HBM 60°C）。该 receipt 的 "+10% 读带宽" 说的是 HBM NDIV70
的部分；**SM VF 偏移对 LLM 推理本身到底有没有收益，此前没有服务口径数据**。
本次用 flashnext（AWQ-INT4 g32, PP2, 50-ple-fix/nospec 常驻服务）单流实测补齐。

## 方法

- 工具：llm_speedtest 单流（c1），prompt 长度 80k / 140k / 200k 各 1 轮
- 偏移切换：`sudo nvml_oc -i <gpu> <sm_off> <mem_off>`（mem offset 恒为 0，
  本次只动 SM VF 偏移，不涉及 NDIV/mclk）
- 四组（21:26–21:38）：
  1. `oc_ab_oc`：+200/+250 刚生效后直接跑（冷态）
  2. `oc_ab_stock`：归零 `nvml_oc -i X 0 0` 后跑（基线）
  3. `oc_ab_oc_hot`：重新打 +200/+250、服务先热过一轮再跑
  4. `oc_ab_140k_oc`：140k 重复 3 轮看方差
- 原始数据：`~/llm_speedtest/results/oc_ab_*_0913.log`

## 数据

| 组 | prompt | prefill tok/s | TTFT ms | decode tok/s |
|---|---|---|---|---|
| oc(冷) | 80k | 5004 | 15988 | 58.6 |
| oc(冷) | 140k | 7753 | 18061 | 77.6 |
| oc(冷) | 200k | 9000 | 22225 | 58.9 |
| stock | 80k | 9220 | 8678 | 55.4 |
| stock | 140k | 9557 | 14651 | 57.1 |
| stock | 200k | 9547 | 20952 | 58.0 |
| oc(hot) | 80k | 9573 | 8358 | 57.5 |
| oc(hot) | 140k | 9600 | 14585 | 82.5 |
| oc(hot) | 200k | 9195 | 21753 | 57.4 |
| oc(hot) 140k×3轮 | 140k | 9611 / 9614 / 9587 | ~14580 | 59.7/58.0/54.9 |

## 结论

1. **热态下 SM VF 偏移 +200/+250 无可测收益**：oc_hot 与 stock 的
   prefill/TTFT 差 ≤1~4%（在 140k 三轮方差内），TTFT 80k 8.36s vs 8.68s、
   140k 14.59s vs 14.65s。单流推理不是 SM 频率瓶颈。
2. **oc(冷) 首请求慢近一倍是冷启动效应**（CUDA graph/PLE page cache 未热），
   不能归因于偏移本身——同偏移热态即恢复。A/B 必须弃掉打偏移后的第一轮。
3. **decode 54→82 tok/s 的大幅波动与偏移无关**，主要受 PLE mmap gather
   （`ple_mmap.py` 行收集）和输出长度影响。
4. 170tune serving 档"验证过的 +10% 读带宽"属于 HBM NDIV70 收益，
   与本 SM 偏移收益是两回事，不可混用做卖点。
5. **运维事实**：暖重启（22:20 那次）后 NVML 偏移仍保留 +200/+250；
   `170tune-persist.service` 未启用，冷启动/断电会回 stock。当前偏移
   属于"没人重新打但也还在"的状态。

## 取舍与下一步

- 保留 +200/+250 无害（gate 过的点，HBM 温度有 receipt 背书），但**对
  FlashNext 单流速度没有理由期待提升**；提速方向应看 PLE readahead /
  并发口径（spec-off 50-ple-fix），不是 OC。
- 22:30 长上下文请求暴露 `VLLM_PLE_MMAP_READAHEAD=256` 被超
  （38474 coalesced runs，gather p99 ≈1.5s）——长文场景 PLE 读盘参数
  是下一个可调点，与 OC 无关。

## 环境快照

服务：flashnext.service（start-flashnext-awq-nospec.sh，即 50-ple-fix
候选 v1-nospec，17:35 envmatrix2 命中后持久化）。当日配套实验：
spec 并发崩溃矩阵（envmatrix / mtp_matrix v1–v3）全部复现 c2+spec 崩、
nospec 2/2 过——与 09-13 早先结论一致。MTP localargmax 候选 19:04
未就绪（verify_mtp_localargmax 未通过），维持 nospec 不变。
