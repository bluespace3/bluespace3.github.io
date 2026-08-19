---
title: 'bu-30b-a3b-preview中文乱码修复微调教程'
categories: ["教程"]
date: 2026-08-19T17:50:53+08:00
lastmod: 2026-08-19T17:50:53+08:00
draft: false
---

# BU-30B-A3B-Preview 中文乱码修复微调教程

> 结论先行：
> 1. **能修**。这是典型的「英文为主的 Agent SFT 导致非英文语言灾难性遗忘」，不是玄学 bug。用 LoRA 微调 + 中文多模态数据修补 + 英文任务数据回放，是标准解法，社区同款问题（日语退化、中文实体编造）都指向同一根因。
> 2. **要做的事**：五步——①快速诊断排除部署层问题 → ②准备四类混合数据（工作量占 70%）→ ③ms-swift LoRA 训练 → ④中英双语评估防回退 → ⑤合并权重 + vLLM 重新部署。
>
> 本笔记是方案教程，未动手执行。部署相关见[《BU-30B-A3B-Preview 本地部署笔记》](bu-30b-a3b-preview部署笔记.md)。

## 1. 问题定位：为什么中文会乱码

### 1.1 模型背景

| 属性 | 值 |
|---|---|
| 模型 | browser-use/bu-30b-a3b-preview |
| 基座 | Qwen/Qwen3-VL-30B-A3B-Instruct |
| 架构 | `qwen3_vl_moe`（xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx） |
| 官方标注语言 | **仅 `en`**（HF model card language 字段） |
| 训练目标 | 截图 + DOM 理解 → 浏览器操作，深度重训 |

### 1.2 根因：灾难性遗忘（Catastrophic Forgetting）

browser-use 官方在 Qwen3-VL 基座上用**英文为主的 Agent 轨迹数据**做了深度 SFT，把模型往「英文任务 → 英文格式动作」的窄分布上拉，中文生成能力被大幅冲掉。这不是猜测，证据链：

- HF model card 语言标签只有 `en`；
- HF Discussion [#4](https://huggingface.co/browser-use/bu-30b-a3b-preview/discussions/4)（2025-12）：**日语输出质量相比基座明显退化**；
- HF Discussion [#7](https://huggingface.co/browser-use/bu-30b-a3b-preview/discussions/7)（2026-04）：**中文实体全是编造的**（"all Chinese entities in the task are made up"），官方暂无修复；
- 你本地实测：同一 vLLM 环境，基座识别正常、bu 乱码 → 排除部署层编码问题，问题在权重本身。

「乱码」是遗忘的严重表现：中文 token 分布被破坏后，模型会吐出罕见字、错位字形、中英夹杂甚至字节级碎片。基座和 bu 的 tokenizer（tokenizer.json / vocab.json / merges.txt / chat template）同源一致，所以不是词表错位。

### 1.3 动手前的 5 分钟诊断清单

虽然基本可以断定是模型问题，微调前先花几分钟确认，避免白训：

1. **裸测**：绕过 browser-use，直接 curl vLLM 的 `/v1/chat/completions`，发一张中文网页截图 + 「用中文识别图中所有文字」，看原始输出。乱码仍在 → 模型问题实锤。
2. **同环境对照**：同一 vLLM 版本、同一请求，换基座 Qwen3-VL-30B-A3B 再发一次。基座正常 → 排除 serving 层。
3. **关掉结构化输出**：browser-use 接入时加 `dont_force_structured_output=True`（官方 quickstart 同款建议）。guided decoding 在弱中文分布上可能放大重复/乱码。
4. **采样参数**：官方推荐 `temperature=0.6, top_p=0.95`；greedy（temperature=0）在这类模型上反而容易重复崩坏。
5. **确认加载的是完整仓库文件**：`chat_template.jinja`、`added_tokens.json`、`special_tokens_map.json` 都在（自量化/手工转换权重时容易丢）。

## 2. 微调能不能解决？两条路线怎么选

| 路线 | 做法 | 成本 | 判断 |
|---|---|---|---|
| **A. 修补 bu（推荐）** | 在 bu-30b-a3b-preview 上 LoRA 微调：中文数据修语言 + 英文数据回放防退化 | 2×80G 卡、几小时训练、数据为主要工作量 | ✅ 保留 Agent 能力，只补语言，性价比最高 |
| B. 从基座重训 | 在 Qwen3-VL-30B-A3B 上用含中文的 browser-use 轨迹整体重做 Agent SFT | 需要重建官方量级的轨迹数据，全参 8×80G | ❌ 除非要完全自主可控，否则不值 |
| C. 不微调的工程绕法 | 见第 6 节 | 几乎为零 | 可先用来顶住，但治标 |

LoRA 修补的预期：中文乱码/编造**大概率明显改善**；能否完全回到基座水平取决于遗忘深度和数据质量，修不彻底就升 rank 或上全参（第 5 节）。

## 3. 第一步：数据准备（工作量的 70%）

### 3.1 四类数据与配比

| 数据类型 | 作用 | 来源 | 建议量级（起步） |
|---|---|---|---|
| ① 中文网页截图识别 | 修乱码主力 | 自采中文站截图（资讯/电商/表格/弹窗/登录页等），**用基座 Qwen3-VL 当 teacher 蒸馏生成中文标注**（你已验证基座识别正常，免费 teacher） | 3k~10k 条 |
| ② 中文 browser-use 轨迹 | 让中文能力长在 Agent 任务分布上 | 强模型（Claude/GPT/Qwen-Max 或基座）驱动 browser-use 在中文网站跑中文任务，录轨迹 | 1k~5k 条轨迹 |
| ③ 英文任务回放 | **防止英文 Agent 能力回退（必加）** | 自采英文轨迹 + 公开数据（Mind2Web 类） | 与②相当 |
| ④ 通用中文 VQA/OCR 回放 | 防通用能力崩 | 开源中文多模态数据集抽样子集 | 2k~5k 条 |

起步配比：①+② 共 ~50%，③ ~30%，④ ~20%。总规模 1~2 万条足够 LoRA 验证一轮，效果好再扩。

### 3.2 轨迹采集的关键：格式必须对齐 browser-use 的真实推理分布

微调数据如果格式和 browser-use 实际发给模型的 prompt 结构不一致，训出来贴合度差。最稳的采集方式：

```python
agent = Agent(
    task="在京东搜索'机械键盘'并按价格排序",   # 中文任务
    llm=teacher_llm,                          # 强模型当 teacher
    save_conversation_path="conv_zh.jsonl",    # 关键：记录发给 LLM 的完整对话
)
```

`save_conversation_path` 会把每一步真实发送的 messages（system prompt、截图、DOM 摘要、历史）和 teacher 的优质回复原样落盘。后处理时把截图从 base64 落成文件、按 `<image>` 占位符顺序对应，直接得到分布完全一致的训练样本。**这比事后手拼 prompt 靠谱得多。**

另一路省钱的采法：bu 模型自己先跑，teacher 只负责审核/重写 assistant 回复（rejection sampling 思路），teacher 调用量减半以上。

### 3.3 数据格式（ms-swift messages 格式）

识别类样本（修乱码）：

```json
{"messages": [
  {"role": "user", "content": "<image>识别这张网页截图中的所有可见文字，按版面顺序输出中文原文。"},
  {"role": "assistant", "content": "顶部导航：首页 / 商品分类 / 购物车……（基座 teacher 生成的中文标注）"}
], "images": ["/data/shots/page_0001.png"]}
```

Agent 轨迹类样本（多轮，含 browser-use 的 system prompt，assistant 输出保持其动作 JSON 风格——schema 字段是英文，自然语言部分输出中文）：

```json
{"messages": [
  {"role": "system", "content": "（browser-use 实际使用的 system prompt 原文）"},
  {"role": "user", "content": "<image>（任务描述 + 页面状态/DOM 摘要 + 历史步骤）"},
  {"role": "assistant", "content": "{\"thought\": \"页面是中文商品列表，需要点击价格排序……\", \"action\": [...]}"}
], "images": ["/data/shots/step_0001.png", "/data/shots/step_0002.png"]}
```

注意点：

- 截图分辨率别缩水：Qwen3-VL 按 patch 切图，1920×1080 截图约 1~2k image token，训练时用 `IMAGE_MAX_TOKEN_NUM` 上限控制（2048 左右），和推理时一致；
- 多轮轨迹里每步一张截图，`max_length` 要给够（16384 起步）；
- 清洗 teacher 输出：乱码样本、编造实体样本必须剔除，**垃圾进垃圾出，脏中文数据会把乱码固化**。

## 4. 第二步：训练（ms-swift LoRA 方案）

### 4.1 框架与资源

- **首选 ms-swift**（ModelScope 官方训练框架，`qwen3_vl_moe` 支持完整，多模态数据格式现成）；
- 备选 LLaMA-Factory（同样支持 Qwen3-VL，template 用 `qwen3_vl` 系），配置思路一致；
- 显存估算（30B MoE）：

| 方案 | 权重 | 资源 | 备注 |
|---|---|---|---|
| LoRA BF16 | ~61GB | **2×80G（ZeRO-2）** | 参考 ms-swift 官方 Qwen3-30B-A3B LoRA 实测需 2×80G；单 80G 极限贴边不建议 |
| QLoRA 4bit | ~20GB | 1×48G 舒适；1×24G 短序列勉强 | 截图 token 多时 24G 会 OOM |
| 全参数 | — | 8×80G（Megatron-SWIFT） | 官方同规模 benchmark；语言修补用不上，修不彻底再考虑 |

### 4.2 环境安装

```bash
pip install "ms-swift>=3.9.1" "transformers>=4.57" "qwen_vl_utils>=0.0.14"
pip install flash-attn --no-build-isolation   # 可选，显著提速；装不上回退 sdpa
```

### 4.3 LoRA 训练脚本（改自 ms-swift 官方 Qwen3-VL 最佳实践）

```bash
PYTORCH_CUDA_ALLOC_CONF='expandable_segments:True' \
NPROC_PER_NODE=2 \
CUDA_VISIBLE_DEVICES=0,1 \
IMAGE_MAX_TOKEN_NUM=2048 \
swift sft \
    --model browser-use/bu-30b-a3b-preview \
    --dataset data/train.jsonl \
    --val_dataset data/val.jsonl \
    --train_type lora \
    --torch_dtype bfloat16 \
    --num_train_epochs 2 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 8 \
    --attn_impl flash_attn \
    --learning_rate 1e-4 \
    --lora_rank 32 \
    --lora_alpha 64 \
    --lora_dropout 0.05 \
    --target_modules all-linear \
    --freeze_vit true \
    --freeze_aligner true \
    --gradient_checkpointing true \
    --max_length 16384 \
    --deepspeed zero2 \
    --warmup_ratio 0.05 \
    --save_steps 200 \
    --eval_steps 200 \
    --logging_steps 5 \
    --output_dir output_bu30b_zh
```

关键参数与坑：

- `freeze_vit true` + `freeze_aligner true`：视觉塔和投影层没坏（基座视觉正常），冻住省显存、防干扰，只训 LLM 部分（MoE 的 expert/gate 线性层会挂 LoRA）；
- **`deepspeed zero2`，不要用 ZeRO-3**：社区实测该 MoE 架构 ZeRO-3 与 LoRA 适配器保存/加载不兼容（Qwen3-VL-30B-A3B LoRA 的已知坑）；
- `lora_rank 32` 起步，乱码改善不足 → 升 64/128（rank 翻倍alpha翻倍）；
- `learning_rate 1e-4` 为 LoRA 常规值；若出现英文能力回退迹象，降 lr 或减 epoch；
- 显存不够 → QLoRA：加 `--quant_method bnb --quant_bits 4`；
- 训练时长参考：1~2 万样本 × 2 epoch，2×80G 约数小时到半天。

### 4.4 训练中快速验证

```bash
swift infer \
    --model browser-use/bu-30b-a3b-preview \
    --adapters output_bu30b_zh/vx-xxx/checkpoint-xxx \
    --stream true \
    --max_new_tokens 2048 \
    --load_data_args true   # 直接跑 val.jsonl 对比标签
```

肉眼盯两点：中文输出是否还乱码、动作 JSON 结构是否还规整。

## 5. 第三步：评估（防回退和修中文同等重要）

| 评估项 | 方法 | 通过标准 |
|---|---|---|
| 中文识别质量 | 自建 100~300 张中文截图评测集（人工标注 GT），算 **CER 字符错误率**，基座 vs 微调前后三方对比 | 显著下降，向基座靠拢 |
| 中文实体真实性 | 抽查提取实体与页面真实内容比对（针对 discussion #7 的「实体编造」） | 编造率肉眼可见下降 |
| 中文任务成功率 | browser-use 跑中文站任务集（搜索/表单/导航各若干） | 显著上升 |
| **英文任务不回退** | browser-use 跑英文标准任务集 | ≥ 微调前的 95% |

英文回退是最大风险，回放数据（③）就是为它准备的。如果英文掉了：加大③占比、降 lr、减 epoch 重训。

## 6. 第四步：合并导出 + vLLM 重新部署

```bash
swift export \
    --model browser-use/bu-30b-a3b-preview \
    --adapters output_bu30b_zh/vx-xxx/checkpoint-xxx \
    --merge_lora true \
    --torch_dtype bfloat16 \
    --output_dir bu-30b-a3b-preview-zh
```

部署清单（沿用[部署笔记](bu-30b-a3b-preview部署笔记.md)的 vLLM 方案）：

1. 合并目录里补齐/保留原仓库的外围文件：`chat_template.jinja`、`added_tokens.json`、`special_tokens_map.json`、`preprocessor_config.json`、`video_preprocessor_config.json`；
2. **补一个 `generation_config.json`**（bu 原仓库没有此文件，从基座拷，写入官方推荐采样 `temperature 0.6 / top_p 0.95`）；
3. 验证可用后可再走 AWQ-4bit 量化（同部署笔记方案 A，~17GB，社区量化脚本通用）；
4. 启动命令不变：`vllm serve bu-30b-a3b-preview-zh --max-model-len 65536 ...`；
5. browser-use 侧接入保持 `temperature=0.6, top_p=0.95, dont_force_structured_output=True`。

## 7. 风险与预期管理

- **LoRA 不保证 100% 修回基座水平**：遗忘严重时需升 rank、扩数据，极端情况全参重训（8×80G）；
- **数据质量 > 数据数量**：teacher 蒸馏的中文标注必须人工抽检，脏数据会把乱码训进权重；
- **官方版本演进**：这是 preview 版，HF 上已有多语言支持请求（discussion #7），官方后续版本可能原生解决，届时自训版可退役——动手前值得再瞄一眼官方动态；
- **许可**：基座 Apache-2.0，bu 仓库带 LICENSE 文件，微调自用/商用前核对一下条款。

## 8. 不想微调的替代方案（先用哪个顶住）

1. **双模型分工**：browser-use 的 planner/extractor 用强模型或基座（中文识别正常的那个），bu 只出 action——browser-use 支持多 LLM 角色（planner + executor）配置；
2. **DOM 文本优先**：`use_vision=False` 走 DOM 文本提取，中文文本直接来自 DOM 而非视觉 OCR，绕开乱码——代价是废掉 bu 的截图理解卖点，纯结构化页面可考虑；
3. **英文中转**：prompt 强制英文输出 + 外部翻译（不可靠，只救急）；
4. **等官方**：关注 HF discussions 的多语言支持进展。

## 参考资料

- 模型主页：[ModelScope](https://www.modelscope.cn/models/browser-use/bu-30b-a3b-preview) / [HuggingFace](https://huggingface.co/browser-use/bu-30b-a3b-preview)
- 中文实体编造反馈：[HF Discussion #7](https://huggingface.co/browser-use/bu-30b-a3b-preview/discussions/7)
- 日语退化反馈（同根因）：[HF Discussion #4](https://huggingface.co/browser-use/bu-30b-a3b-preview/discussions/4)
- ms-swift Qwen3-VL 官方最佳实践（数据格式/训练/导出命令来源）：[swift.readthedocs.io](https://swift.readthedocs.io/zh-cn/v3.10/BestPractices/Qwen3-VL-Best-Practice.html)
- Qwen3-VL-30B-A3B MoE LoRA 实测（ZeRO-2 结论）：[Medium: Fine-Tuning Qwen3-VL-30B-A3B MoE with LoRA](https://medium.com/@ishaafsalman/fine-tuning-qwen-qwen3-vl-30b-a3b-moe-architecture-with-lora-2365359e870f)
- LLaMA-Factory（备选框架）：[github.com/hiyouga/LlamaFactory](https://github.com/hiyouga/LlamaFactory)
- 官方 vLLM + browser-use 接入示例：模型主页 Quickstart 章节
