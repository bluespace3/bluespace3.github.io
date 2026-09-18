---
title: 'Qwen3.8-Flash-Next测速月度综述-0830至0916'
categories: ["硬件"]
date: 2026-09-18T23:51:08+08:00
lastmod: 2026-09-18T23:51:08+08:00
draft: false
---
# Qwen3.8-Flash-Next 测速月度综述（2026-08-30 ~ 09-16）

> 综合来源：《170HX双卡部署笔记(08-30/09-04)》《PLE表精度AB-BF16vsFP8-09-04》《AWQ-vs-AutoRound-0904》《CMP170HX-SM超频AB-0913》《NVFP4-vs-AWQ-AB-0914》《NVFP4生产切换与PLE精度实验-0914》《NVFP4生产栈decode掉速排查-0916》
> 硬件：双 CMP 170HX 64G（SM80），MSI B850M-P / 9800X3D / 60G RAM / NVMe

## TL;DR 五条关键结论

1. **量化路线演进**：AutoRound W4A16 → AWQ-INT4（速度持平，09-05 定案常驻）→ **NVFP4 W4A16/TEP2/MTP6（09-14 切换生产）**，每步都有 A/B 数据背书。
2. **NVFP4 栈（B）社区口径 decode ≈ 165-180 t/s，是 AWQ 栈的 ~2.1 倍**；曾出现 320K+ prefill 断崖（500K 档 TTFT 331s vs A 栈 148s E2E），**根因 = KV 缓存池不足，MEM 拓展到 97% 已解决（09-18 定位）**。
3. **decode 速度 = 步率 × MAL，瓶颈在内容不在硬件**：ITL 恒 ~32ms（31-33 步/s），MAL 2.5→5 表观速度翻倍。"100 vs 150"之争 100% 是口径差异，非回退。
4. **PLE 表精度结论随栈形态反转**：AWQ/MTP3 时代 BF16 表甜区 decode +12~32%；NVFP4/MTP6 时代 BF16 表反而 prefill -40~-61%（RAM 装不下 102G 表，page fault），**现役组合 = NVFP4 + FP8 表**。
5. **服务定位未变：单请求 + 超长上下文**。并发是排队不是并行：C2/C3 聚合 prefill ≤ 单发水平，TTFT ×1.6-2.6，decode 单流摊薄至 12-45 t/s。

## 一、栈演进时间线与选型 A/B

| 日期 | 事件 | 关键数据 |
|---|---|---|
| 08-30 | 部署定稿：PP2 + MTP4 + mmap PLE | 单发 prefill 5690-6287 t/s (80K-260K)，decode 110-136 t/s（内容友好时） |
| 09-01/04 | PLE 表 FP8 vs BF16 A/B | BF16 甜区 decode +12~32%；c2@230K+ 翻车是 RAM 问题（102G 表 > 60G RAM） |
| 09-04 | AWQ-INT4 vs AutoRound | **速度零差**（±3% 内）：500K prefill 4256 vs 4242，decode 63.6 vs 61.5 |
| 09-05 | AWQ 定为常驻 | 速度持平下选 g32 理论质量略优；代价 -5G/卡 KV，窗口固 512K |
| 09-13 | SM 超频偏移 A/B | **OC 无可测收益**（热态差 ≤1-4%）；提速方向不在 OC |
| 09-14 | NVFP4 vs AWQ A/B + 生产切换 | decode 96-107 平带 vs AWQ 61-94；竞态崩溃零复现 |
| 09-16 | "掉速"排查 | 100 vs 150 = 口径差，结论：同口径才可比 |

## 二、现役 NVFP4 生产栈 vs 上代 AWQ 栈（核心对比）

**单发、out=1280、512K YaRN（09-14 A/B，c1）：**

| 输入 | A prefill/decode | B prefill/decode | decode Δ |
|---|---|---|---|
| 40K | 2587 / 93.9 | 2513 / 99.5 | +6% |
| 80K | 4411 / 61.1 | 4527 / **106.6** | +74% |
| 160K | 5429 / 69.9 | 5032 / **106.3** | +52% |
| 320K | 6682 / 63.4 | 4982 / 96.7 | +53% |
| 500K | 3894 / 62.9 | **1510** / 106.4 | +69% |

B 特征：decode 96-107 全档平带（无长度衰减）；代价是 320K+ prefill 断崖。

**社区完全等口径（长输出 1.8万-3.1万 token，B 栈）**：8K→177 t/s，32K→165，64K→166；引擎打点中位 180.5 / 峰值 234。复现社区公布区间偏上。同口径下 **prefill B +34~150%，decode B ×2.1，TTFT B 好 25-60%**。

**E2E 口径（TTFT + out/decode）看交叉点**（out=1280）：
- ≤160K：B 赢（80K 档 E2E 29.7s vs 39.1s）
- 320K+：**A 反超**（500K 档 E2E 149s vs 343s——decode 优势救不回 prefill 断崖）
- 长输出场景：decode 占 E2E 的 78-90%，B 优势完全兑现

**结论：NVFP4 适合长输出生成/agent；超长 prompt+短输出（>320K）场景曾因 prefill 断崖被 AWQ 反超（E2E 343s vs 149s）——断崖根因是 KV 缓存池不足，MEM 97% 修复后此劣势应消除（修复后 E2E 交叉点未复测）。**

## 三、decode 的普适规律：步率 × MAL

- ITL 恒定 ~31.5ms（31-33 步/s）= 这台机器物理极限，跨栈不变
- **表观速度 = 步率 × MAL（MTP 每步接受长度）**，MAL 由内容决定：

| 内容类型 | MAL | 表观速度 |
|---|---|---|
| 随机 token | ~1.0 | 33 t/s |
| 普通长文 | 2.5-3.1 | 96-107 t/s |
| 代码+thinking 长跑稳态 | 4.0-5.1 | 165-180 t/s |

MTP 深度：AWQ 栈 spec=4 是硬上限（QSA 容量断言，spec5-8 全灭）；NVFP4 栈 MTP6。**跨口径比速度没有意义，Benchmark 差异主要是投机解码友好度。**

## 四、被证伪/排除的提速方向（省钱清单）

| 方向 | 结论 | 证据 |
|---|---|---|
| SM 超频偏移 +200/+250 | 无收益 | 热态与 stock 差 ≤1-4%，在三轮方差内（09-13） |
| AWQ vs AutoRound 量化格式 | 速度零差 | ±3% 内（09-04） |
| PLE gather chunk 调优 | 非 prefill 旋钮 | 512/2048 全平段 ±1%；唯一禁忌 8192（塌到 ~2000 t/s） |
| NVFP4 栈换 BF16 表 | 有害 | prefill -40~-61%（RAM page fault），decode 持平（09-14） |
| 社区 env 层优化（Q38_TP_PLE 等） | 架构不适用 | HC_GEMV 需 M≤8 扩展，成本>收益 |

有效方向：量化路线本身（AWQ→NVFP4）、MTP 深度（4→6）、**KV 缓存池扩容（MEM→97%，直接消除 500K prefill 断崖）**、长文 PLE readahead（gather p99 1.5s 待调）。

## 五、测量方法论（血泪固化）

1. **判数只认引擎打点**：客户端流式计时系统性偏低（urllib 缓冲可算出 264-516 t/s 假值；SSE 事件数≠token 数，MTP 下低估 3-4 倍）。权威 = `Avg generation throughput` 打点 + usage.completion_tokens
2. **同口径才可比**：prompt 长度、内容类型、thinking 开关、输出上限、采样参数、稳态窗口，一项都不能少；复核基线用 c1 out1280=96-107 锚点
3. **弃冷启动轮**：首请求慢近一倍是 CUDA graph/页缓存未热，A/B 必须热过一轮
4. **网络环境噪音**：httpx 必须 `trust_env=False`（socks 代理劫持）、no_proxy 别写 CIDR

## 六、遗留清单

- [x] 500K prefill 断崖 → 根因 KV 缓存池不足，gpu-memory-utilization 拓展到 97% 解决（09-18；原疑 TP2×YaRN 不成立）
- [ ] 修复后复测：500K 档 prefill/TTFT，及 E2E 口径下与 AWQ 的交叉点是否消失
- [ ] BF16PLE 混合目录 97G 去留；MemoryMax 32G→48G
- [ ] `--max-num-batched-tokens 4096+` 的 prefill 收益未实测（AWQ 时代坑 3 指出）
- [ ] AWQ g32 vs g128 质量评测未做（速度已证平，如需再定夺）
- [ ] 长文 PLE readahead（256 被超，gather p99 ≈1.5s）
