---
title: 'vLLM0.32升级试验-TEP2prefill诅咒解除与decode纪录-1029'
categories: ["硬件"]
date: 2026-10-29T01:07:44+08:00
lastmod: 2026-10-29T01:14:17+08:00
draft: false
---
# vLLM 0.32 升级试验：TEP2 prefill 诅咒解除 + decode 本机纪录（PP2 有 decode 回归）

日期：2026-10-28 深夜 ～ 10-29 凌晨 ｜ 状态：✅ 试验完成，0.32 暂不上车，结论留档 ｜ 被测：Qwen3.8-Flash-Next 176B NVFP4 @ 双 CMP 170HX (sm_80)

## 一句话结论

**vLLM 0.32（官方 wheel + 社区补丁 graft）在 TEP2 拓扑下 decode 创本机纪录（200K 档 164.8 t/s，历史区间 62–112），且 0.29 时代 TEP2 的 prefill 短板（5,100 vs PP2 9,700，-47%）彻底消失**；同版本 PP2 则出现 decode 大幅回归（80K 档崩到 17.03 t/s + out=645 早停），疑似 0.32 PP 调度器退化，悬案在案。**如果未来升级到 0.32，生产拓扑应改 TEP2（tp2/EP），弃 PP2。**

## 背景与动机

- 生产栈：0.29（dev499 底 + Qwen-Flash-SM80-170HX graft：GDS loader/PLE mmap/nvfp4-sm80/MTP6/eagle_drop），PP2 拓扑，786K 上下文。当年弃 TEP2 选 PP2 的唯一原因是 TEP2 prefill 太慢（5,100 vs 9,700 tok/s），agent 场景 TTFT 不能忍。
- 社区仓库（README 0.32.3.dev3 GDS 路径）+ Qwen-AgentRaider 出现 0.32 相关补丁，值得验证 0.32 是否解决 PP2 decode 波动、且让 TEP2 prefill 追上。
- 用户要求：复用 torch 等大依赖不重复下载；重启贵，测试并入一次加载窗口。

## 试验方法（graft 法）

1. **隔离底座**：官方 0.32.0 wheel 装入 `/mnt/nvme1/vllm032-venv`（torch 2.13.0+cu130 与生产 0.29 venv 完全同版本，nvidia 全家桶走 `/mnt/nvme1/caches/home-pip` 缓存盘，零大依赖重下载）。
2. **补丁移植**：社区工作树 `/mnt/nvme1/vllm-032-wt`，rsync 进隔离 venv 的 site-packages；两处从未入 git 的生产现场改动先做血统审计——`Q38_SAMPLING_WARMUP` 预热块按生产同源植入（保持未提交态），`draft_int8` 钩子判死不移植（0.29 生产从未启用，差距记录在案）。
3. **跨版本移植纪律**（用户 10-29 点名）：禁逐崩逐修——先全量审计一次补齐再点火。实际踩到一个断言坑：`assert ep_size==2` 拦 tp2/pp2（EP 组切分前提不成立），生产同款 `enable_expert_parallel=False` + `VLLM_DISABLE_EP_INLINE_OFFLOAD=1` 绕开。
4. **启动器**：全部 clone 自生产脚本逐字对齐（mem 0.94 / max_num_batched 6144 / maxlen 786432 / MTP6 / PLE mmap env 全套），仅动必要差异行；`VLLM_USE_REORDERED_MTP_PROBE_WORKSPACE=1` 在 0.32 已删（grep 全库零匹配）。
5. **测速口径**：llm_speedtest c1 × 80K/200K、out 1280、每流不同 seed（防 prefix cache），与 0.29 基线逐字同口径；看门狗豁免 `/run/gpu-no-standby` 全程挂；起跑前 WS 握手验活。

## 数据一：0.32 PP2 三方对照（10-28 深夜）

| 配置 | 80K pre / dec / TTFT | 200K pre / dec / TTFT | 异常 |
|---|---|---|---|
| A（warmup 植入 + eagle drop 默认） | 5674 / 49.73 / 14.1s | 5705 / 99.14 / 35.1s | out=1148 未到 EOS |
| B（graft 的 --eagle_drop=off） | **3931 / 17.03 / 20.4s** | 3629 / 97.26 / 55.1s | out=645 早停 |
| C（官方默认 drop=on，对照） | 5402 / 49.38 / 14.8s | 5688 / 85.85 / 35.4s | out=1280 正常 |
| 0.29 生产（参照） | ~4400 / ~61 / ~30s | ~5300 / 103 / 54s | — |

- PP2 上 0.32 的 prefill 是真提升（+44～58%），TTFT 同步改善（14–15s vs 20s）。
- 但 B 组暴露 decode 崩溃（17.03）+ 早停（645 token 提前停），eagle_drop=off 是崩溃诱因之一；即便 A/C 健康档，decode 也逊于 0.29 同期水平（99 vs 103，波动区间更宽）。
- PP2 的 dec 17 崩溃病因**未结案**（是否 0.32 PP 调度器退化）。

## 数据二：0.32 TEP2 对照（10-29 01:00，本次主菜）

启动：tp2 / pp1 / `enable_expert_parallel=True`（断言坑绕开后 EP 正常激活，worker 日志 `Worker_TP{0,1}_EP{0,1}` 为证）。就绪约 4 分钟，engine init 78.29s，graph capture 仅 3s/0.31GiB（PP2 为 30s/1.15GiB），KV 1,027,706 tokens（786K 档并发 1.31x；PP2 同机 816,973/1.04x——两拓扑 KV 都足以容纳单发 80K/200K，容量不构成对比干扰）。

| 档位 | prefill | decode | TTFT |
|---|---|---|---|
| 80K | 3155（vs PP2 -20%） | 99.55 | 25.4s |
| 200K | **4860（vs PP2 +34%）** | **164.82（vs PP2 +69%）** | **41.2s（-25%）** |

对照 0.29 时代 TEP2 档案（0914 NVFP4 512K 窗口）：80K/160K/320K decode 106/106/97。

三条推论：

1. **TEP2 prefill 诅咒解除**。0.29 死因（-47% vs PP2）变成 0.32 上的 ±20% 级噪声，长档甚至反超。当年挡在 TEP2 面前的唯一障碍没了。
2. **decode 优势扩大到 +48%～+69%**（相对 0.29 档案），且无长度衰减、无 PP2 的 80K 崩溃病。
3. **164.82 t/s 在数学上只能是 MTP6 高接受率跑满**：164.8 ÷ 步率 ~31/s ≈ MAL 5.3（区间上限），本机历史 MTP 单流 62↔112 区间之外。引擎侧 SpecDecoding 行（MAL 2.1–3.6 采样）佐证投机在工作，但 bench 精确窗口内无新采样行（疑 0.32 指标打印间隔变化），此点存瑕。

## 决策与遗留

- **0.32 不上生产**（本轮定位是摸底试验；PP2 decode 回归未定罪 + 786K 长档未测 + 双卡实验期不宜长跑）。
- **若升级 0.32：生产拓扑改 TEP2（tp2/EP）**，decode + 长档 TTFT 双收益；80K 档 TTFT 比 PP2 慢 5s 是主要代价。
- 悬案：① 0.32 PP2 80K dec 17 崩溃 + out=645 早停归因；② 0.32 TEP2 在 786K 档的 TTFT（MTP prefill 成本在 786K 比 512K 贵得多，当年实测 386s vs 212s）；③ 0.32 SpecDecoding 指标打印间隔变化。
- 产物：基准日志 `~/llm_speedtest/python/results/q38_v032_tep2_c1_80_200k_1029.log`、`q38_B_hook_80_200k_1027.log`；引擎日志 `/mnt/nvme1/vllm-032-wt/vllm032{,-tep2}.log`；启动器 `start-nvfp4{-pp2,}-v032.sh`（同目录）。
- 相关笔记：[NVFP4 vs AWQ A/B-0914](NVFP4-W4A16-vs-AWQ-AB实测-TEP2-MTP6-0914.md)（TEP2 前科档案）、[生产切换-0914](NVFP4生产切换与PLE精度实验-0914.md)（eagle-drop=off 换稳定性决策）。

## 经验固化（已回写 skill）

- 跨版本移植「先全量血统审计一次补齐再点火」纪律生效：本次仅一个断言坑，无逐崩逐修循环。
- 0.32 移除的 knob 清单：`--disable-log-requests`（改 `--logging-*`）、`VLLM_USE_REORDERED_MTP_PROBE_WORKSPACE`。
- TEP2 点火前必查 EP 激活证据（worker 行 `Worker_TP*_EP*`），否则可能假 EP。

## 后记：基准收尾 8 分钟后 TEP2 实崩（10-29 01:11）

基准跑完（01:03 ALL_DONE）后服务保留在线，01:09-01:11 被局域网客户端 xxx.xxx.xxx.xxx 连发三个 chat 请求，第三个大 prefill 进行中（窗口吞吐 ~26K tok/s）双卡**同时** Xid 31（MMU Fault: FAULT_PDE VIRT_READ @ GPC4 GPCCLIENT_T1_0，两卡故障地址同尾缀 `_1b200000`）→ Worker_TP0_EP0 `CUDA illegal memory access`（浮出点 prepare_inputs 的 `is_padding.fill_`，异步报错真凶内核在上一步）→ executor 级联优雅关停。

**判读**：双卡同刻、同 GPC、同偏移模式的 MMU fault = 两 rank 执行了同一段确定性越界读代码 → **0.32 TEP2 路径的软件 bug**（大 prefill/外部请求形态触发，本基准 c1 两档未触达），非硬件（对照 7.2.12-cmp 内核 Xid 140 随机单卡掉卡）、非 OOM/温度。Xid 31 双卡同形是软件 OOB 的经典指纹。

**对结论的修正**：TEP2 的速度优势成立，但 0.32 TEP2 **稳定性不成立**——「升级则改 TEP2」追加前提：先定位该越界读（候选：0.32 新调度器 × chunked prefill × EP/MTP 路径）。0.32 不上车的决策被本次实崩进一步加固。
