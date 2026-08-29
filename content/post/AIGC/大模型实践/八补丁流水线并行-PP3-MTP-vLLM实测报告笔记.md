---
title: '八补丁流水线并行-PP3-MTP-vLLM实测报告笔记'
categories: ["AIGC"]
date: 2026-08-30T01:48:50+08:00
lastmod: 2026-08-30T01:48:50+08:00
draft: false
---
# Eight Patches to Pipeline Parallel — 实测笔记

> 来源：Claude Artifact · FIELD REPORT · 2026-08-27
> 原文链接：https://claude.ai/code/artifact/2aea33f6-93dc-40aa-8c8e-215ed068a486

## 一句话总结

在 3× CMP 170HX（PCIe Gen2 x4、无 NVLink、无可用 P2P）上，让 vLLM 以 **PP3 + MTP + PLE offload** 跑 Qwen3.8-Flash-Next 修了 8 个真实缺陷；结果推翻了此前的结论：**慢速互联正是 PP 获胜的原因**——prefill 比 expert-parallel 快 **5.2×**（32k prompt）。

## 硬件与环境

- 3× NVIDIA CMP 170HX · sm_80
- PCIe Gen2 x4 · 无 NVLink · 无可用 P2P
- vLLM · PP3 + MTP（多 token 预测）+ PLE offload
- 模型：512 个专家、每 token 激活 10 个、48 层（MoE）
- 200k context、8 并发，测量方法：唯一 prompt 前缀（防 prefix cache）、三次取中位数、两轮完整运行

## 性能对比（PP vs DEP）

| 指标 | DEP | PP | 倍数 |
|---|---|---|---|
| Prefill 32k (tok/s) | 1,950 | 10,156 | 5.2× |
| Prefill 8k (tok/s) | 1,898 | 8,014 | 4.2× |
| Decode 8 并发 (tok/s) | 290.2 | 441.9 | 1.5× |
| Decode 单流 (tok/s) | 44.1 | 76.0 | 1.7× |
| KV cache 池 (tokens @ 200k) | ~232,000 | 904,109 | 4.52× |

另：262k ctx 下 KV tokens 935,216，为 DEP 池的 4×。

## 为什么 PP 在慢互联上反而赢

之前把因果搞反了。结构性原因：

- **DEP（专家并行）**：专家分散在三张卡上，每层每 token 都要 all-to-all dispatch + combine —— 每个 forward pass **48 次跨卡往返**，全走 PCIe Gen2 x4。
- **PP（流水线并行）**：每个 stage 拥有其所辖层的全部专家，**专家路由永不离开 GPU**；只有 hidden states 跨 stage 边界，每个 forward pass 仅 **2 次**。
- KV cache：DEP 每个 rank 都要复制一份；PP 按层分片 → 池容量近乎免费翻 4 倍。

**通用教训**：互联成本应该驱动并行策略的选择，而不只是决定可行性。链路窄时，**最小化集合通信次数**的拓扑胜过计算负载最均衡的拓扑——即使后者纸面更漂亮。

## 8 个上游缺陷清单

| # | 文件 | 缺陷 |
|---|---|---|
| 1 | gpu_worker.py | PLE offload 直接拒绝 PP，无任何技术理由 |
| 2 | model.py | 非 last rank 上 `hyper_connection_mixer = None`；None 不是 nn.Module，loader 无法放置权重 |
| 3 | model_state.py | 一刀切 "PLE requires PP=1" 守卫 |
| 4 | gpu_model_runner.py | 同一守卫在另一个 runner 里又出现一次 |
| 5 | ple_offload/worker.py | offload worker 不是 pipeline rank，却解析了 PP 分区 —— `len(partitions)=3` vs `pp_size=1` |
| 6 | gpu/model_runner.py | Connector 要求每个 rank 都有 PleOffloadLayer；实际只有 rank 0 有 |
| 7 | — config — | GDN state dtype 各 stage 不一致：rank 0 bfloat16 / rank 2 float32 |
| 8 | pp_utils.py | Draft token 从未转发给非 last rank —— 各 rank 对集合通信次数的预期不一致 |

## 守卫是"过宽"，不是"错"

四处代码在启用 n-gram PLE embedding 时直接拒绝 PP。runner 自己的报错信息道出了真实约束：**PLE 需要原始 input_ids，而只有第一个 rank 收到它们**。

这个约束是可以满足的：n-gram 表是单个 50 GiB 层，任何内存均衡的分区都会把它放在 stage 0 —— 恰好是 input_ids 到达、offload worker 已经 spawn 的地方。补丁把"一刀切拒绝"换成"校验分区包含关系"：

```python
return all(0 <= int(i) - 1 < first_end for i in ple)
```

其中 off-by-one 是关键：模型在 `(layer_idx + 1) in ple_layer_ids` 处挂 PLE，所以 config 里的 `[2]` 指层索引 1 —— checkpoint 的 `layers.1.ple.*` 证实了这一点。此条件先离线单测 6 种情况，再花容器周期验证。

## 缺陷 7：伪装成 block-size 问题的 dtype 不匹配

KV cache setup 因各 stage 页几何不一致而拒绝配置。对 validator 插桩（而非瞎猜）立刻得到答案：

```
layers 19–31  block=832   main_kv page=1,703,936
layers 35–47  block=1600  main_kv page=3,276,800
```

先强制 `--block-size 1600` 统一了 page、清掉了报错 —— 然后 worker 被 signal 杀死，因为 3.27 MB 的 block 是病态的。这是治标。

第二个诊断显示 specs 只差一个字段：rank 0 `dtypes=(bfloat16, bfloat16)` vs rank 2 `(bfloat16, float32)`。float32 恰好是 bfloat16 的两倍 —— 832 vs 1600 的差距全部由此而来。模型自身 config 声明 `mamba_ssm_dtype: "float32"`，所以 `--mamba-ssm-cache-dtype float32` 让所有 stage 与模型声明一致，超大的 block 也就不再需要。

## 缺陷 8：唯一需要真正写代码的

其余都修好后，decode warmup 期间仍有一个 worker 被 signal 杀死。Host 内存全程稳定在 64 GB 空闲 —— 是 segfault 不是 OOM；且换 eager 模式、各种 block size、两种 draft depth、乃至某 fork 解决同类问题的环境配方都躲不过。

答案是一个开放的上游 PR：**vLLM #46994 "[Spec][V2] Support MTP speculative decoding under pipeline parallelism"** —— 12 个文件，+401/−18。干净地 apply 上（当前镜像恰好处于其改动前状态）。

它增加了第三次 broadcast：last rank 把提议的 draft tokens 转发给其他 rank，注释指出该计数必须来自 config "so that every rank agrees on the per-step broadcast count"。没有它，各 rank 预期的 collective 数量不同 → desync → 一个 rank 死掉 —— 产生任何配置改动都救不了的 `Connection closed by peer` 特征。

## 值得记录的三个弯路（Corrections）

1. **改错了文件好几个循环**。vLLM 同时有 `v1/worker/gpu_model_runner.py` 和 `v1/worker/gpu/model_runner.py`，两者都定义 `_setup_ple_offload`。活跃路径是后者，我的修复进了前者。traceback 写着正确的文件名，我读漏了。
2. **把 `--block-size 1600` 当成了修复**。它清掉了瞄准的那个报错，显得正确；实际是在掩盖上面的 dtype 不匹配，其产生的 3.27 MB block 还把 worker 弄 segfault 了。
3. **最重要的框架性错误**：此前的报告把专家并行当作可行选择、把流水线并行描述为"这台硬件勉强能容忍的拓扑"——实测把这个结论整个翻转了。

---
*注：原文末尾在此处被截断（"...presented expert parallelism as the worka—"），如需完整结尾可补原 artifact。*
