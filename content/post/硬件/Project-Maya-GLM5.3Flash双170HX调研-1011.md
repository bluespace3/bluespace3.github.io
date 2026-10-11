---
title: 'Project-Maya-GLM5.3Flash双170HX调研-1011'
categories: ["硬件"]
date: 2026-10-11T15:04:23+08:00
lastmod: 2026-10-11T15:04:23+08:00
draft: false
---
# Project Maya（GLM-5.3-Flash 321B）双 170HX 可行性 + 质量调查 — 2026-10-11

调查对象：https://github.com/mw00/project-maya （Strata 衍生，MIT）
问题：①双 CMP 170HX 64G 能不能跑 ②质量 vs Qwen3.8-Flash-Next（要证据不要猜想）

## 一、Maya 是什么

- 跑 GLM-5.3-Flash（zai-org，MIT）：321B 总参 MoE / ~18B 激活，原生 1M ctx，GLM-5 系列首个原生多模态
- llama.cpp 魔改引擎：热门专家驻 VRAM → 次热 RAM → 其余 NVMe 按路由搬运；自带 OpenAI+Anthropic 兼容 API(:8080/v1)、dashboard、MTP 投机解码、思考档位、图片输入
- 自带量化五档：Maya-S 96.5G / S24 94.7G / **M 116G** / M-Derisked 116G / L 156.3G

## 二、双 170HX 能跑吗：能，有同款硬件实测背书

**仓库 issue #22 = 同款硬件完整报告**（2× CMP 170HX 64G、GA100 sm_80、PCIe Gen2 x4、E5-2690 v4、91G RAM、Maya-M 全专家驻留显存 99.5-99.8% 命中）：

| 指标 | #22 实测 |
|---|---|
| decode | **61.3 tok/s**（3 问均值 57.3-65.0，随 MTP 接受率 62-81% 波动） |
| prefill 8K | **514 tok/s**（窄 PCIe 读专家是瓶颈） |
| 并发 | c1 46.8 / c2 107.6 / c4 194.4 tok/s 聚合（线性） |

本机条件核对：9800X3D ✓（远强于 E5 v4）、PCIe Gen1 x16 ≈ 对方法定配置、nvme1 剩 815G ✓、CUDA 12.8/13.3 + g++13 + AVX2 ✓、sm_80 支持（要求 ≥7.0）。
推荐档位：**Maya-M + 32K ctx**（116G < 128G 双卡；模型占满后显存仅剩 ~1.5G 给 KV，别贪上下文）。Maya-L 需 156G，会溢到 RAM 层，本机 60G RAM 不建议。

两个必加 flag（#22 实测）：`--native`（接受率 53→95%）+ `--kv int8`（长答案 +34%），装完跑 `--calibrate` 10-15 分钟。

## 三、速度对比（vs 本机 Qwen3.8-Flash NVFP4 生产栈实测口径）

| | Maya-M/GLM-5.3-Flash | Qwen3.8-Flash NVFP4（现栈） |
|---|---|---|
| decode | ~61（短 ctx，MTP） | 62-112（MTP6 接受率波动） |
| prefill | ~500-900 | **2400-4800** |
| 长上下文 | 32K 封顶（VRAM 见底） | 实测 260K-900K 仍 61-67 tok/s |
| 并发 | 单请求排队制 | ≤2（自定限） |

decode 打平略低，**prefill 慢 5-9 倍**，长上下文完全不是一个量级。

## 四、质量证据（全部有出处，无推测）

### 4.1 厂商图互相回避，无官方头对头
- Z.ai bench_53.png 对比列：GLM-5.2 / DeepSeek-V4-Vision-Exp / Claude Opus 4.8 / GPT-5.6 Terra / Gemini 3.7 Flash —— **无 Qwen**
- Qwen3.8-Flash-Next 官方表对比列：Qwen3.8-27B / 3.7-Plus / DeepSeek-V4-Flash-0731 / Claude-Opus-4.6 —— **无 GLM**

### 4.2 中立第三方 Artificial Analysis（同体系 v4.3.2 十项子评测，两家均收录）★核心证据

| 指标 | GLM-5.3-Flash | Qwen3.8-Flash-Next | 胜者 |
|---|---|---|---|
| **智能总分（117 模型）** | **41.8（#4）** | 39.8（#6） | GLM +2.0 |
| Terminal-Bench 4.0 | **32.8%** | 25.3% | GLM 明显 |
| Terminal-Bench 2.1 | 84.3% | **86.1%** | Qwen |
| AutomationBench | **60.4%** | 55.9% | GLM |
| HLE | **39.9%** | 38.0% | GLM 微 |
| GPQA Diamond | 91.2% | **92.3%** | Qwen 微 |
| CritPt（物理） | **15.4%** | 11.1% | GLM |
| SciCode | 51.6% | 50.6% | 持平 |
| GDPval Elo | 1644 | 1629 | 持平 |
| AA-Briefcase（办公） | 1454 | **1581** | Qwen |
| **Omniscience 幻觉率** | **27.6%** | **45.3%** | **GLM 大幅**（全表最大差距） |
| AA-LCR 长上下文推理 | 80.0% | 79.7% | 持平 |

判读：同梯队、差 2 分，不是代差。GLM 强在 agentic/工程 + 低幻觉；Qwen 赢在 TB2.1 / GPQA / 办公任务。

### 4.3 重叠基准官方数交叉验证（方向一致，GLM +2~5）
- DeepSWE 1.1：GLM 63.4 vs Qwen 58.7
- Agents' Last Exam Pass@1：GLM 26.3 vs Qwen 24.3
- Z.ai 宣传语自留余地："approaching Claude Opus 4.8"（逼近非达到）

### 4.4 落到本机：量化再吃一层
- Maya-M = IQ2_S 专家（2bit 级，比现栈 4bit 更激进），官方自测保留 FP8 的 97.9% 零样本准确率——但测的是 ARC/HellaSwag/WinoGrande/PIQA 老易题，token 一致率 86.2%、KL 0.33；对难题/长程 agent 的真实损耗大概率更高
- 净效应预估：基座 ~2 分差距被更重量化收窄，本地实际差距 ≤1 分档，任务相关（代码 agent 偏 GLM，问答/办公偏 Qwen）

## 五、结论

1. **能跑**，同硬件 61.3 tok/s decode 实测背书，本机只会更快；档位 Maya-M + 32K + `--native` + `--kv int8`
2. **质量有依据的结论**：GLM-5.3-Flash 基座高半档（AA 41.8 vs 39.8），幻觉率优势最显著；非代差
3. **速度**：decode 相当、prefill 慢 5-9 倍、长上下文完败 → 适合"第二意见模型"临时切换，不适合接替生产位
4. 切换成本：吃满双卡+钉内存（留 6G），须停 vLLM/ComfyUI；冷启动 20-40 分钟 + 模型加载 ~5 分钟；模型下载 116G（HF 走代理或 hf-mirror，逐文件 sha256 校验）
5. 测质量对齐 thinking 档位：GLM API 默认 max，Maya dashboard 默认 High，不对齐不公平

## 附：Maya 五档速览

| 档 | 大小 | 保留 FP8 准确率 | token 一致率 |
|---|---|---|---|
| S | 96.5G | 97.9% | 83% |
| S24 | 94.7G | 97.7% | 83% |
| **M** | 116G | 97.9% | 86.2%（KL 0.329） |
| L | 156.3G | 99.2% | 90%（KL 0.188） |

来源：repo README / bench/results/MAYA-M.md / issue #22 / huggingface.co zai-org/GLM-5.3-Flash / artificialanalysis.ai 两模型页 / Qwen3.8-Flash-Next ModelScope README。本机速度数字：~/llm_speedtest/results/（NVFP4 A/B 0914、BF16-PLE 1M 0904）。
