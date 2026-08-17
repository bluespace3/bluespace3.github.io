---
title: 'bu-30b-a3b-preview部署笔记'
categories: ["教程"]
date: 2026-08-17T15:57:31+08:00
lastmod: 2026-08-17T15:57:31+08:00
draft: false
---

# BU-30B-A3B-Preview 本地部署笔记

Browser-use 官方的第一个开源模型，专为浏览器自动化 Agent 场景训练。本文记录模型信息、显存需求评估、各精度部署方案、browser-use 接入方式，以及自量化和加速优化的结论。

## 1. 模型信息

| 属性 | 值 |
|---|---|
| 基座模型 | Qwen/Qwen3-VL-30B-A3B-Instruct |
| 架构 | Qwen3VL MoE（视觉语言模型） |
| 总参数 | 30B（激活仅 3B） |
| 上下文 | 65,536 tokens（官方推荐 32k 内使用） |
| 原版精度 | BF16，13 个 safetensors 分片，约 61GB |
| 许可 | Apache-2.0 |
| 仓库 | [ModelScope](https://www.modelscope.cn/models/browser-use/bu-30b-a3b-preview/files) / [HuggingFace](https://huggingface.co/browser-use/bu-30b-a3b-preview) |

特点：在 Qwen3-VL 底座上针对「截图 + DOM 理解 → 浏览器操作」重训，擅长网页布局解析、弹窗处理、元素定位这类 Agent 任务。定价宣传是 200 tasks / $1（云端），本地部署则只剩电费。

⚠️ 是 Vision-Language 模型，视觉塔不能裁掉，部署方案必须带 mmproj / vision 支持。

## 2. 显存需求评估

以 65GB 显存的卡为例（其他显存可按比例换算）：

| 精度 | 权重占用 | 65G 卡可行性 | 备注 |
|---|---|---|---|
| BF16 原版 | ~61GB | ❌ | 加 KV cache（32k 约 3GB）+ 视觉激活 + 运行时开销，总需求 66~70GB，必爆 |
| FP8 (W8A8) | ~31GB | ✅ 宽裕 | 需卡支持 FP8：L40S / H100 / RTX Pro 6000 等；A100 不支持 |
| AWQ/GPTQ Int8 | ~32GB | ✅ 宽裕 | 几乎无损，兼容性好 |
| AWQ/GPTQ Int4 | ~17~19GB | ✅ 非常宽松 | 还能开满 65k 上下文 + 多并发 |
| GGUF Q4_K_M（llama.cpp） | ~19GB | ✅ | 需较新版本 llama.cpp + mmproj 视觉文件 |

结论：**65G 显存跑 BF16 不行，跑 FP8 / AWQ-4bit 绰绰有余**。24G 消费级卡（3090/4090）跑 Int4 也没问题。

参考实测：Qwen3-30B-A3B-AWQ（同底座）vLLM 加载占用约 17GB。

## 3. 部署方案 A：vLLM + AWQ-4bit（推荐）

NVIDIA 论坛有 DGX Spark 上完整的 runbook，可直接参考：[Runbook: bu-30b-a3b-preview-AWQ-4bit on DGX Spark](https://forums.developer.nvidia.com/t/runbook-bu-30b-a3b-preview-awq-4bit-model-on-dgx-spark-solo-with-vllm-browser-use/359704)

社区现成量化版（不用自己做）：

- `cyankiwi/bu-30b-a3b-preview-AWQ-4bit` / `AWQ-8bit`
- `sintanial/bu-30b-a3b-preview-AWQ-4bit` / `AWQ-8bit`
- `Code4me2/bu-30b-a3b-preview-NVFP4`

启动命令：

```bash
pip install vllm

vllm serve cyankiwi/bu-30b-a3b-preview-AWQ-4bit \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.92 \
  --served-model-name bu-30b-a3b-preview
```

国内网络可用 ModelScope 源：环境变量 `VLLM_USE_MODELSCOPE=True`，或者提前 `modelscope download` 到本地后直接 serve 本地路径。

## 4. 部署方案 B：llama.cpp + GGUF

适合没有 CUDA 生态、或想 CPU offload 的场景：

```bash
# 1. 下载 GGUF 权重 + mmproj（视觉投影文件，必须）
#    bartowski/browser-use_bu-30b-a3b-preview-GGUF
#    qvshuo/bu-30b-a3b-preview-Q4_K_M-GGUF

# 2. 启动 llama-server
llama-server \
  -m bu-30b-a3b-preview-Q4_K_M.gguf \
  --mmproj mmproj.gguf \
  -c 32768 -ngl 99 \
  --port 8080
```

注意 llama.cpp 需要较新版本（Qwen3-VL 支持已进主线）。MLX 生态（Mac）有 `mlx-community/bu-30b-a3b-preview-4bit/8bit`，4bit 约 18.3GB 统一内存。

## 5. 接入 browser-use

vLLM / llama-server 都暴露 OpenAI 兼容 API，browser-use 直接指过去：

```python
from dotenv import load_dotenv
from browser_use import Agent, ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    base_url='http://localhost:8000/v1',   # vLLM 地址
    model='bu-30b-a3b-preview',
    temperature=0.6,
    top_p=0.95,
    dont_force_structured_output=True,  # 官方建议：关掉结构化输出提速
)

agent = Agent(
    task='Find the number of stars of browser-use and stagehand. Tell me which one has more stars :)',
    llm=llm,
)
agent.run_sync()
```

## 6. 自行量化（可选）

社区量化版够用，但要自己做也完全可行，一台 24G 卡就能做离线量化：

**工具**：[llm-compressor](https://github.com/vllm-project/llm-compressor)（vLLM 官方生态）或 GPTQModel，跑一遍校准集即可。Qwen 官方对同底座发过 FP8 / AWQ / GPTQ-Int8 / Int4 全套，校准配方可直接抄 Qwen3-VL-30B-A3B 的官方脚本。

**两个关键注意点**：

1. **MoE 的 router/gate 权重保持高精度**，别量化，否则专家路由崩掉，质量断崖下跌
2. **视觉塔单独处理**：建议 fp8 或干脆不量化。截图理解对量化最敏感，视觉塔掉点会直接伤 Agent 的元素定位能力

GGUF 路线：`convert_hf_to_gguf.py` + `llama-quantize`，Qwen3-VL 架构已支持。

## 7. 加速优化：别碰 MTP，用这些

### MTP 层：不建议 ❌

- MTP（Multi-Token Prediction）头是**训出来的权重**，不是架构上加一层就行。bu-30b 和底座 Qwen3-VL-30B-A3B 都没有发布 MTP checkpoint（只有 Qwen3-Next 线带 MTP）
- 自己训：冻结主干 + 蒸馏 MTP 头，是个小工程；且 vLLM 的 `method=mtp` 通路目前面向 DeepSeek/Qwen3-Next 的 config 格式，Qwen3-VL 没接，还得改 serving 代码，性价比极低

### 实际有效的加速手段 ✅

1. **n-gram 投机解码**（零训练、零额外显存）：

```bash
vllm serve <model> \
  --speculative-config '{"method":"ngram","num_speculative_tokens":5,"prompt_lookup_max":5}'
```

browser-use 的输出是大量重复格式的 JSON action（`{"action": [{"type": "click", ...}]}`），n-gram 命中率不低。Qwen3-30B-A3B 上有社区实测案例。

2. **Prefix caching**（vLLM 默认开启）：Agent 每步都重发 DOM + 历史消息，前缀命中率很高，对端到端延迟的改善往往比投机解码还明显。

3. `dont_force_structured_output=True`：官方示例默认配置，省掉 constrained decoding 的开销。

## 8. 相关链接

- 官方模型卡：https://huggingface.co/browser-use/bu-30b-a3b-preview
- 发布公告（Our First Open-Source LLM）：https://browser-use.com/changelog/16-12-2025
- DGX Spark 部署 runbook：https://forums.developer.nvidia.com/t/runbook-bu-30b-a3b-preview-awq-4bit-model-on-dgx-spark-solo-with-vllm-browser-use/359704
- vLLM 投机解码文档：https://docs.vllm.ai/en/latest/features/speculative_decoding
- 社区量化版索引：HF 搜 `base_model:quantized:browser-use/bu-30b-a3b-preview`

---

*2026-08-17 记录。模型是 preview 版，长上下文会卡顿（官方自己提醒 test before prod），生产环境建议限制在 32k 上下文内使用。*
