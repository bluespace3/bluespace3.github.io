---
title: 'bu-30b-pp2-vs-single-gpu实测笔记'
categories: ["教程"]
date: 2026-09-01T19:01:43+08:00
lastmod: 2026-09-01T19:01:43+08:00
draft: false
---

# BU-30B PP2 对比单卡：prefill/decode A/B 实测与 PP 启动崩溃修复

BU-30B-A3B（Qwen3-VL MoE 底座，30B 总参/3B 激活，AWQ 8bit 量化 32GB）在双 CMP 170HX 上的单卡 vs PP2 双卡 A/B 对比。核心问题：**这个 32GB 的模型单卡放得下，PP2 到底值不值？** 答案分场景——长 prompt prefill 和 decode 稳定性 PP2 赢，短 prompt 极速首 token 单卡赢。

## 1. 实测数据（9 reps 中位数，同生成器同内容）

| prompt 长度 | 单卡 prefill t/s | PP2 prefill t/s | 单卡 decode t/s | PP2 decode t/s |
|---|---|---|---|---|
| 1.4k tok | **7970** | 6089 | 103.8 | **114.1** |
| 5.6k tok | **8755** | 7057 | 79.9 | **110.5** |
| 22.2k tok | 6148 | **6986** | 86.1 | **98.8** |
| 视觉跨卡（base64 图）| ✓ | ✓ | | |

要点：

- **长 prompt（>16k tok）PP2 prefill 反超 +14%**——纯计算受限场景下双卡流水线各算一半，通信开销被摊薄
- **decode PP2 全面更快（+15~38%）**——PP2 每卡 KV cache 空间翻倍，batch 从容，speed-of-light 波动小
- **短 prompt 单卡完胜**——PP 固有的流水线填充延迟（1.4k tok 时 238ms vs 182ms）短任务摊不掉
- 单卡版还带 ngram 投机解码；但中文自由文本 ngram 命中率近 0（MAL 1.0），实测无增益，browser-use 重复 JSON 场景才有收益

## 2. PP 启动崩溃根因与修复（本次最大收获）

PP2 首次启动必崩，单卡却正常。根因链：

1. vLLM 0.24 的 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.__init__` 用 `vllm_config.with_hf_config(config.text_config)` 构造语言塔
2. `with_hf_config()` 发现 `hf_config.architectures is None` 时，查 transformers 的 `MODEL_FOR_CAUSAL_LM_MAPPING_NAMES`
3. bu-30b 的 `text_config.model_type` 是自定义类型 `qwen3_vl_moe_text`，映射表不认识 → 不填 architectures
4. PP 模式下 Worker 进程重建 VllmConfig（dataclass replace）触发 pydantic 校验 → `No model architectures are specified` 崩溃
5. 单卡路径不触发重校验，所以潜伏不炸

**修复**：给模型 config.json 的 text_config 补标准字段：

```json
"text_config": {
  "architectures": ["Qwen3MoeForCausalLM"]
}
```

原文件备份为 `config.json.bak-pp-fix`。此修复对单卡无害（architectures 非 None 时 `with_hf_config` 直接采用，不再查映射表）。

## 3. 两套并存脚本（互斥切换，同端口 8001）

| 模式 | 脚本（tools/model-launcher/） | 特点 |
|---|---|---|
| 单卡极速 | `start-bu30b-fast-vllm.sh` | GPU1，ngram 投机解码，短 prompt TTFT 最优 |
| PP2 双卡 | `start-bu30b-pp2-vllm.sh` | 双卡流水线，无投机解码（0.24 spec+PP 不通），长 DOM prefill + decode 稳定性最优 |

两脚本均带防御：模型分片完整性（7 个）、GPU 占用（>20GB 拒启）、端口冲突检查。venv 必须用 `/root/cmp170hx-bench/venv`（0.24.0）——Marlin MoE 补丁在位（L104），8bit+group32 量化走 Triton。

## 4. 基准方法坑（skill 三坑的 BU-30B 变体）

- **裸 `/v1/completions` + 重复散文 prompt → 100% 立即 EOS**：这个 preview 模型对裸 prompt 极敏感，必须走 chat 端点
- **chat 流式解析要用 `delta.content`**，不是 completions 的 `text` 字段——否则 n_ev=0 误判"全部异常"
- prefill_tps = prompt_tokens ÷ 首字延迟；decode_tps = (completion_tokens-1) ÷ (末字-首字)；9 reps 取中位数
- prefix cache 会虚高：本基准每发随机 seed 换 Reference id，前缀不重复

## 5. 与其他部署的关系

- **flashnext 176B**（systemd `flashnext.service`，端口 8000）：与本模型双卡互斥，切换需 `systemctl stop flashnext` → 起动 bu30b；反向切换 `systemctl start flashnext`（有 8000 端口守卫）
- ComfyUI 固定 GPU0；单卡版钉 GPU1 与其错开；PP2 版占满双卡时 ComfyUI 不能同跑大模型

## 6. 结论建议

- **browser-use 生产（长 DOM、多步 agent）**：选 PP2——真实场景 prompt 几千到几万 token，prefill 和 decode 双收益
- **短交互/单轮问答**：单卡版 TTFT 更优，还留一张卡给 ComfyUI
- ngram 投机解码只对重复 JSON 有增益；中文自由文本零命中零损失，可常开

---

*2026-09-01 实测。机器：双 CMP 170HX 64GB（sm_80，x1 链路）；vLLM 0.24.0（bench-venv）；基准脚本改编自 skill bench_decode.py（usage 计数/delta.content/防 prefix cache 虚高）。*
