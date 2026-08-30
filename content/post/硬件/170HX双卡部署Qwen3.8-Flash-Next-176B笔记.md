---
title: '170HX双卡部署Qwen3.8-Flash-Next-176B笔记'
categories: ["硬件"]
date: 2026-08-30T20:31:01+08:00
lastmod: 2026-08-30T23:57:46+08:00
draft: false
---
# 双 CMP 170HX 部署 Qwen3.8-Flash-Next 176B：最佳策略与最终结果

> 2026-08-30 定稿。硬件：MSI B850M-P / Ryzen7 9800X3D / 60G 内存 / CMP 170HX 64G ×2。
> 模型：Qwen3.8-Flash-Next 176B（MoE），W4A16 权重 ~15.5G + FP8 PLE n-gram 表 48G。
> 服务：vLLM 0.29（/root/vllm029-venv），端口 8000，兼容别名 Qwen3.8-27B-INT8（客户端零改动）。

## 一、核心矛盾与解法（部署策略的骨架）

**矛盾**：176B 模型 = 权重 31G（PP 后每卡 ~15.5G）+ PLE n-gram 表 48G。SM80 无原生 FP8，量化无路可走；而 1M 上下文的 KV 池必须独占每卡 ~22G 显存——**表进显存与大上下文是数学互斥的**（48G 表进显存，KV 池只剩 6K 上下文）。

**解法分层**（本次部署最重要的一条经验）：

| 数据 | 去处 | 理由 |
|---|---|---|
| 权重 W4A16 | GPU 显存 | PP=2 每卡 15.5G，计算热路径 |
| KV cache（BF16） | GPU 显存 | MEM=0.97 时每卡 22.5G → 池 ~1.078M token |
| PLE n-gram 表 48G | **NVMe 存文件 + 内存页缓存干活** | mmap + 预热 42G 进页缓存，每步 gather 纯内存拷贝 |
| YaRN 位置编码 | hf-overrides | factor 4.0 + orig_max 262144 → 1M 上下文 |

```
模型目录: /mnt/nvme0/llm_models/Qwen3.8-Flash-Next-W4A16-fp8ple/
PLE 表 = model-00016-of-00017.safetensors（48G，NVMe）
启动器: tools/model-launcher/start-flashnext.sh pp1m [chunk] [spec]
```

## 二、最终配置（pp1m 模式）

```bash
sudo start-flashnext.sh pp1m 2048 4
```

关键参数：

- `--pipeline-parallel-size 2`（PP 流水线；TP=2 已全面被 PP 取代）
- `--max-model-len 1048576` + `--max-num-seqs 8` + `--gpu-memory-utilization 0.97`
- YaRN factor 4.0（hf-overrides，rope_type=yarn, original_max_position_embeddings=262144）
- KV 只能 BF16——**fp8 KV 被 QSA 层断言封死**（仅 auto/bf16）
- MTP 投机解码 `num_speculative_tokens=4`（QSA 约束下的可用上限，详见坑 2）
- PLE mmap 五件套：`VLLM_PLE_MMAP=1 WORKERS=32 PREWARM=1 READAHEAD=256 CHUNK=2048`
- `-cc.cudagraph_mode=PIECEWISE`（PP+MTP 组合下 full cudagraph 会重编译停摆）

## 三、最终实测结果

llm_speedtest 前端，1/1 并发，OpenAI 兼容接口（2026-08-30）：

| 提示词长度 | TTFT (ms) | ITL 平均 (ms) | ITL 标准差 | 预填充速度 (t/s) | 输出长度 | 输出速度 (t/s) | 状态 |
|---|---|---|---|---|---|---|---|
| 8100 | 1453.31 | 31.26 | 1.46 | 5576.84 | 1280 | **112.19** | 1/1 并发成功 |
| 8228 | 1485.37 | 32.18 | 3.15 | 5543.36 | 487 | 66.96 | 1/1 并发成功 |
| 8356 | 1751.34 | 32.00 | 2.70 | 4774.49 | 1071 | 65.88 | 1/1 并发成功 |

单发大长度扫描（官方基线，llm_speedtest 前端 1/1 并发，输出上限 1280；原始 CSV：`~/下载/history_..._1788067928517.csv`）：

| 提示词长度 | TTFT (ms) | ITL 平均 (ms) | 预填充速度 (t/s) | 输出长度 | 输出速度 (t/s) |
|---|---|---|---|---|---|
| 80000 | 12725 | 31.46 | 6287.14 | 1280 | 106.22 |
| 110000 | 17790 | 32.24 | 6183.64 | 627 | 66.60 |
| 140000 | 22945 | 32.22 | 6101.90 | 891 | 67.77 |
| 170000 | 28299 | 32.59 | 6007.62 | 584 | 64.68 |
| 200000 | 33889 | 32.29 | 5901.79 | 912 | 63.61 |
| 230000 | 39870 | 32.51 | 5768.96 | 409 | 65.86 |
| 260000 | 45691 | 32.64 | 5690.57 | 956 | 78.43 |

（另：超长档 prefill 峰值 6016 t/s @64K 口径，128K 5673、256K 5292；decode 稳定 110-136 t/s。）

### 并发补充：2 / 3 并发 @ 大长度（与上表同测试点，llm_speedtest Python 后端，输出上限 1280，2026-08-30）

| 长度 | TTFT：C1→C2均值→C3均值 (ms) | C3 最慢流 TTFT (ms) | 聚合 prefill C1→C2→C3 (t/s) | 单流 decode C1→C2→C3 (t/s) |
|---|---|---|---|---|
| 80K | 12725 → 21758 → 29197 | 43587 | 6287 → 5552 → 5500 | 106 → 59.6 → 27.1 |
| 110K | 17790 → 27998 → 40398 | 60673 | 6184 → 5888 → 5433 | 67 → 46.3 → 21.9 |
| 140K | 22945 → 36108 → 51276 | 76957 | 6102 → 5809 → 5446 | 68 → 57.2 → 25.6 |
| 170K | 28299 → 45062 → 60894 | 92456 | 6008 → 5634 → 5510 | 65 → 22.1 → 27.3 |
| 200K | 33889 → 53360 → 71849 | 108665 | 5902 → 5595 → 5522 | 64 → 40.4 → 11.7 |
| 230K | 39870 → 62550 → 95063 | 160534 | 5769 → 5479 → 4291 | 66 → 21.0 → 12.3 |
| 260K | 45691 → 71242 → 98999 | 153429 | 5691 → 5436 → 5073 | 78 → 39.9 → 44.8 |

成功率：C2 全档 2/2、C3 全档 3/3，无超时（动态超时按 65K=30min 比例伸缩，260K 档余量 ~2h）。

**结论**：

1. **prefill 单流即已打满**：2/3 并发聚合 prefill 恒在 ~5400-5900 t/s，不超过单发同档水平（5690-6290）——并发不产生额外 prefill 吞吐，只是排队。
2. **排队直接砸在 TTFT 上**：C2 平均 TTFT ≈ 单发 ×1.6-1.7，C3 ≈ ×2.2-2.6；260K+C3 最慢流要等 **160 秒**才见首 token。长上下文下并发对交互体验是灾难。
3. **decode 并发扩展性差且随长度恶化**：单流被摊薄到 C2 21-60 / C3 12-45 t/s（200K 以上档均值跌到 12-45）；波动仍受内容 MAL 支配（见第四节），但"长上下文+并发"叠加时明显低于单发同档。PP2 下 batch decode 不划算。
4. 230K+C3 聚合 prefill 掉到 4291 属测量噪声（该档双流 decode 窗口几乎不重叠，聚合口径失真）；其余档聚合口径正常。
5. 印证服务定位：**并发吞吐没有免费午餐，单请求 + 超长上下文才是这台机器的正确用法**。
6. 测速方法：Python 后端 `llm_speedtest/python/venv/bin/python llm_test_backend.py 18000`（前端页 `http://localhost:18000/`），绕过浏览器 6 并发限制；请求走 `ws://localhost:18000/ws/test`，test_lengths=[80000,110000,...,260000]，output_length=1280。每个并发流 seed 不同防 prefix cache（vLLM 日志命中 ~36% 来自跨轮 warmup 复用）。工具路径：`/home/liyi/llm_speedtest`，复跑脚本已固化：`llm_speedtest/python/ws_bench.py 2|3`（后端未起时先 `venv/bin/python llm_test_backend.py 18000`）。

（附：早前还跑过一轮 8100/8228/8356 短题并发，结论方向一致——C2 聚合 prefill 5113-5830、TTFT 1.5s→2.5s→3.2s，本轮大长度原始日志已存 `~/llm_speedtest/results/st_big_c2.log`、`st_big_c3.log`。）

## 四、decode 的真相：一步三响（本次调优最大的认知收获）

**ITL 恒定 ~31.5ms → 服务节拍恒为 31-33 步/s，这台机器的物理极限。输出速度 = 步率 × MTP 每步接受长度（MAL），瓶颈不在硬件在内容**：

| 输出内容可预测性 | MAL | 表观速度 |
|---|---|---|
| 乱码/随机 token 续写 | ~1.0 | 33 t/s |
| 普通真实负载（散文/问答） | 2.1-3.5 | 66-110 t/s |
| 高模式化内容（跑分题/代码补全） | ~4.0 | 110-136 t/s |

上表三行"速度差一倍"实为同一服务同一节拍下 MAL 2.1 vs 3.5 的差别——**Benchmark 数字差异主要来自题目对投机解码的友好度，不要拿它当硬件差距**。

## 五、踩过的硬坑（按血泪排序）

1. **spec=5 起不来**：QSA 环形缓存容量 = 4×⌈(4+spec)/4⌉，必须整除注意力块 1616(=16×101)。spec=5→容量12 不整除，直接断言崩溃；**spec 5-8 全灭**。spec=9+（容量16）虽合法但第 9 位接受率≈0.7⁹≈4% 纯亏。**spec=4 是硬上限**（容量仍 8）：混合内容 +1%，可预测内容天花板 148 vs 136。
2. **PLE gather chunk（VLLM_PLE_MMAP_CHUNK）不是 prefill 旋钮**：512/2048 在 ≤256K 全平段（±1%），drop_caches 冷缓存也零劣化——每步 gather 只有 MB 级 I/O，32 线程+readahead 全藏住了。**唯一要记的是别用 8192**（PLE 供给跟不上 + 重编译停摆，200K prefill 从 ~5300 塌到 ~2000 t/s）。
3. **调度器级 chunk 是另一个东西**：投机解码会把 max_num_scheduled_tokens 钳到 2048（启动 WARNING），想再抬 prefill 应调 `--max-num-batched-tokens 4096+`，与 PLE chunk 无关。
4. **PP2 气泡**：GPU1 槽位 PCIe x1 降级（06:00.0）放大 stage 间传输延迟，软件无解，换槽或查线。
5. **测量本身会骗人**：流式 bench 数 SSE 事件数≠token 数（MTP 每事件可带 2-4 token，低估 3-4 倍）；乱码 prompt 会让模型 1 token 就 EOS。计数必须用 usage.completion_tokens。
6. 27B 客户端零改动切换：端口 8000 + `--served-model-name` 多别名 + `--reasoning-parser qwen3 --tool-call-parser qwen3_coder --enable-auto-tool-choice`。

## 六、遗留与下一步

- 512K/1M 两档 prefill 未测（外推 ~112s / ~286s）。
- `--max-num-batched-tokens` 提到 4096/8192 的 prefill 收益未实测（坑 3 提示的方向）。
- 服务定位：**单请求 + 超长上下文第一优先**，prefill 速度可让位；并发吞吐不做。
