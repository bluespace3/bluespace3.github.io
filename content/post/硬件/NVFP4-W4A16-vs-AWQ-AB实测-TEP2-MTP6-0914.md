---
title: 'NVFP4-W4A16-vs-AWQ-AB实测-TEP2-MTP6-0914'
categories: ["硬件"]
date: 2026-09-14T21:38:17+08:00
lastmod: 2026-09-14T22:19:45+08:00
draft: false
---
# NVFP4(W4A16/TEP2/MTP6) vs AWQ-INT4(PP2/spec3) A/B 实测

日期：2026-09-14 晚 ｜ 状态：✅ B栈可用，竞态探针通过 ｜ 前置：[迁移计划](Qwen3.8-Flash-Next-NVFP4社区栈迁移与对比计划-0914.md)

## 一句话结论

**dev499 直接加载社区 NVFP4 检查点成功**（W4A16 元数据改写 + TEP2 + MTP6，无社区镜像/无 GDS）：单发 decode 80K-500K 全档 **96-107 t/s，比 AWQ 生产栈快 52-74%**；**c2×103K 竞态探针 2/2 通过、零 Xid**——AWQ 栈同口径 19-26 秒必崩的 spec 每请求记账竞态在 NVFP4 栈上未复现。代价：320K+ prefill 衰减、500K TTFT 331s。

## A/B 数据（c1 / out 1280 / 512K YaRN 窗口 / 同 seed 策略 / 双方各自最优 spec）

| 档位 | A prefill | A decode | B prefill | B decode | decode Δ |
|---|---|---|---|---|---|
| 40K | 2587 | 93.9 | 2513 | 99.5 | +6% |
| 80K | 4411 | 61.1 | 4527 | **106.6** | **+74%** |
| 160K | 5429 | 69.9 | 5032 | **106.3** | **+52%** |
| 320K | 6682 | 63.4 | 4982 | **96.7** | **+53%** |
| 500K | 3894 | 62.9 | 1510 | **106.4** | **+69%** |

- A = AWQ-INT4 PP2 spec3+localargmax cgNONE（生产配置）；B = NVFP4 TP2+EP MTP6 async-sched cg F&P
- B 的 decode 几乎无长度衰减（96-107 平带）；A 在 61-94 波动（MTP 接受率随内容波动）
- **MTP6 指标**：MAL=2.48（1488 draft 接受 2207 token），分位置 967/527/341/190/118/64（首 token 65%）
- **c2×103680 并发**：2/2 自然结束（单流 96.3 + 被踩踏流 30.8，排队效应与 AWQ 栈同类），零新增 Xid；AWQ 同口径历史 10+ 次 Xid 43 必崩
- B 首轮（冷缓存）80K decode 7.2 / 160K TTFT 171s —— **PLE FP8 表冷读是首轮失真主因**，热缓存轮全部恢复正常，正式数据以 r2 为准

## B 栈配置（可复现）

- 元数据：`prepare_nvfp4_w4a16.sh` 改写 `quant_algo→W4A16_NVFP4`+`input_activations→null`（原件 `.orig-metadata-w4a4/`）
- 启动：`/mnt/nvme0/qwen-flash-data/start_nvfp4_tep2.sh 6`（TEP2、lazy safetensors、8192 batched、async-scheduling、block 1632、YaRN 512K、PLE mmap env 同 AWQ）
- 内核自动选择：量化主干 MARLIN（nvfp4.py oracle），**未量化 MTP MoE 走 triton**——社区 fork 的 `--moe-backend marlin` 不可照抄（dev499 报 `moe_backend='marlin' is not supported for unquantized MoE`，因其 INT8 草稿机制我们没有）
- 冒烟正确性：质数问答语义正确无乱码

## 遗留与建议

1. **500K prefill 断崖**（1510 t/s, TTFT 331s）：疑 TP2 通信×YaRN 外推叠加，agent 场景净收益仍正；如需可试 pp1m 对照
2. **RAM**：FP8 PLE 51G 热页驻留后余量健康（avail 51G+），比 AWQ 的 BF16 102G 表省一半
3. **切换决策留给用户**：NVFP4 实例当前仍在 8000 服务中；AWQ 生产栈已恢复 enable（未启动）。日常用哪个=速度 vs 情感 familiar 度的取舍
4. c2 只跑了 1 轮——如需更强结论可加轮次/更长（80 万 token 级）

---

## 追加：社区完全等口径复测（09-14 深夜，判定「差距=口径」成立）

**改动**：新增 `start_nvfp4_community.sh` —— 补上社区两个缺失参数 + 恢复原生窗口：
- `--default-chat-template-kwargs {"enable_thinking":true,"preserve_thinking":true}`
- `--override-generation-config {"temperature":1.0,"top_p":0.95,"top_k":20,"min_p":0.0,"presence_penalty":1.5}`（服务端硬覆盖）
- `--max-model-len 262144`（去掉 YaRN）

**测试口径**：prompt=「写个网站网页」（长 filler 撑到目标长度）、输出上限 **50000 token**（社区原版）、thinking 默认开。

| 输入 | 输出 | TTFT | **引擎侧生成** | MAL | thinking 字符 |
|---|---|---|---|---|---|
| 8K | 1844 | 2.5s | **177.3 t/s** | 5.07 | 474 |
| 32K | 31307 | 40.5s | **165.3 t/s** | 4.04 | 13181 |
| 64K | 16844 | 29.4s | **166.3 t/s** | 4.25 | 6456 |

引擎 10s 打点分布（30 样本）：**中位 180.5 / 均值 160.5 / P90 230 / 峰值 234 t/s**，零新增 Xid。

**判定**：社区公布 151.05～168.29 t/s（单请求 8K-128K 长输出）——本机复现落在 **165-177（均值 160.5、中位 180.5）**，**同区间偏上**。⇒ 此前 96-107 t/s 的"低数据"**100% 是测试口径差异**（普通长文 vs 代码生成、out 1280 vs 5 万、thinking 关 vs 开、采样参数不同），不是栈慢。

**MAL 口径链**：普通长文 2.73 → 代码任务+thinking 3.0-3.55（8192 out）→ 长跑稳态 **4.04-5.07**。decode ≈ 步率(≈39-42 步/s) × MAL，MAL 是主变量。

**残留真差异（非口径）**：
1. `splitting_ops` 里 `qwen3_8_flash_next_ple_short_conv` / `_qsa_with_output` 在 dev499 静默失效（命名空间是 `qwen4_exp`），其余 11 条通用算子名生效——若补上对应 qwen4_exp 算子名可能再抠一点
2. 社区有「全词表 INT8 草稿打分 + 每卡 top-32 BF16 复核」自研实现，我们用标准 MTP6+localargmax；但其 MAL 4-5 已高于社区反推值(~4)，**此项已不构成缺口**
3. `--moe-backend marlin` 无法照抄（未量化 MTP MoE 拒收），社区 fork 有配套机制

**测量方法教训**：任何客户端流式计时都不可信——urllib 读取缓冲导致"首 token 迟到 57s + 8192 token 16s 倾泻"，算出 264-516 t/s 的假值。**权威口径 = 引擎自报 `Avg generation throughput` 打点 + `/metrics` 计数增量**。
