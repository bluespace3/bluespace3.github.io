---
title: 'Qwen3.8-Flash-Next-NVFP4社区栈迁移与对比计划-0914'
categories: ["硬件"]
date: 2026-09-14T19:58:54+08:00
lastmod: 2026-09-14T21:17:19+08:00
draft: false
---
# Qwen3.8-Flash-Next-NVFP4 社区栈迁移与对比计划

日期：2026-09-14 ｜ 状态：🟡 进行中（A7 下载收尾）｜ 入口技能：`qwen-flash-sm80-170hx-migration`

## 一句话目标

把社区仓库 **Qwen-Flash-SM80-170HX**（双 CMP 170HX / sm80 上的 GDS+NVFP4+TEP2+MTP6 全栈）与**现役生产栈**（AWQ-INT4 + BF16 PLE mmap，dev499 build）做 A/B 对比，核心动机是**绕开现役栈 MTP spec 每请求记账路径的越界竞态**（c2 并发 + 长上下文必崩，配置级排查四候选全败，生产被迫切 nospec，损失 2–2.7x decode）。

## 两个方案对象

| | 现役生产栈 | 社区栈 |
|---|---|---|
| 权重 | AWQ-INT4（176 G，含 102 G BF16 PLE） | **NVFP4**（135.25 G = 68 G NVFP4 + 51.2 G FP8 PLE + 16 G BF16） |
| PLE | BF16 102 G mmap | FP8 E4M3 51.2 G（省一半内存，白赚） |
| 并行 | PP2 | TEP2（TP2 + EP，双卡直通） |
| 投机 | MTP spec3（有竞态）/ nospec（生产现态） | MTP6 + 全词表 INT8 草稿 + BF16 复核 |
| decode | 单发 52–112 t/s | 作者双卡实测**单请求** 151.05–168.29 t/s（发布版五档 8K–128K） |

作者成绩口径（README + docs/使用说明.md 原文核对）：**单请求长输出、8K～128K 输入、输出上限 5 万 token、全部自然结束**；打包前单次 170.826、思考短时约 199。**无并发数据**，且作者自述"非受控原版 vLLM 对照"。

## 关键结论（本日核查后）

1. **链路速率不是本机偏差**：GPU 侧 `5GT/s x16 (overdriven)` 是 **170HX 全卡固有特性，作者机器同款同速**，其栈就在此速度跑通 ⇒ 不可用作"GDS 悲观"的论据。bayley 补丁（0001/0002）只修 PLX 双卡 **BAR1 映射**，与速率无关。
2. **与参考机的真实差异仅两点**：①GPU 在 PLX switch 后（作者机无 switch）②数据盘 = 走芯片组的 Realtek 无 DRAM 盘（作者机 CPU 直连；本机直连位是 NTFS Windows 盘不可用）。
3. **检查点实际是 W4A4**（config.json：weights 与 input_activations 均 FP4 group16）——与早前"weight-only"记录不符。sm80 无 FP4 张量核心，直接加载会撞 sm100 cutlass ⇒ **必须改元数据走 W4A16 路线**：`prepare_nvfp4_w4a16.sh` 把 `quant_algo→W4A16_NVFP4` + `input_activations→null`，落到 modelopt.py L128 的 **FP4 Marlin GEMM**（`get_min_capability=75`，源码注释明写 A100/SM80 端到端验证过）。
4. **GDS 严格模式缓做**：`gdscheck.py -p` 实测 `use_pci_p2pdma=false` + 全栈 compat；跨根端口穿 PLX 的 P2PDMA 无成功先例 ⇒ 只在重启窗口内用 `gdsio -V` 一次性裁决，失败即永久退回 mmap PLE 路径（仓库保留 `src/vllm_ple_mmap.py`）。**下载等待期不投入 B 段（IOMMU/multipath/GRUB 改造）。**
5. **镜像/Docker 路线已判死**（09-13 穷尽：10 家镜像源全拒或 ~30 KB/s，Hub 经代理 618 B/s，代理单节点不可切；"拿 src/ 本地构建"也证伪——覆盖层需 SHA 匹配的私有基础 vLLM）。**翻盘路线 = 下载完直接在现有 dev499 上试加载 NVFP4**（注册名双向核对通过：dev499 registry.py L594 有 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` ↔ 检查点 `architectures` 同名；PLE FP8 布局与 `ple_mmap.py` 正则/dtype 表精确匹配）。

## 元数据级预验证（09-14 20:0x，下载未完成即可做，已通过 ✅）

用 `.index.json`（完整下载的权威清单）+ 已落盘分片的 safetensors header 头解析，**只读**核对了"翻盘假设"的关键前提：

- **PLE 布局逐项吻合**：`model.language_model.layers.1.ple.ple_embedding.ngram_embedding.shard_0..127.weight`（128 个，dtype **F8_E4M3**，shape `[2500012, 160]`）+ **恰好 1 个全局** `ngram_embedding.weight_scale`（在 `model-plefp8-00009.safetensors`，排在下载队尾）⇒ 与我方 `ple_mmap.py` 的名字正则 `shard_(\d+)\.weight` 与 dtype 表 `F8_E4M3: requires_scale=True` **完全一致**。
- **索引总量核对**：`indexed_bytes = 135195303851`，与方案书期望值逐字一致；索引张量总数 296475。
- **主权重序列化**：标准 modelopt NVFP4（每 Linear `weight_scale_2` + `input_scale` F32 标量；exclude 名单内模块保持 BF16）⇒ 正是 W4A16 Marlin 路径所需格式。

⇒ 结论：**"135G 下完可直接在 dev499 上试加载"的元数据前提已成立**，剩余不确定性收敛到运行期（Marlin FP4 内核可用性、PLE mmap 读取路径、cudagraph/spec 组合）。

## A 段进度（不动主机）

| 步 | 内容 | 状态 |
|---|---|---|
| A0 | 仓库 HEAD `78c9a59` 干净 | ✅ |
| A1 | `check-gds-host.py` 只读盘点 | ✅（acceptance NOT_TESTED） |
| A2 | 工作目录 + hf venv（`hf 1.29.0`） | ✅ |
| A3 | C++ 扩展 `src/ple_gds/*.so` 编译 + import 校验 | ✅ |
| A4 | `requirements-kernels.txt`：tilelang 0.1.14 + apache-tvm-ffi 0.1.12（SHA256 与固定哈希一致） | ✅ |
| A5 | 上游一致性只读校验（7 MISMATCH + 4 MISSING，overlay 路线封死） | ✅ 已知结论 |
| A6 | 磁盘决策（AutoRound 169 G 已删，现余 214 G ≥ 190 G） | ✅ |
| A7 | **模型下载 135.25 G + `check-model.py`** | 🟡 110 G/135 G，剩 3 分片 |
| A8 | PLE 映射/转换/登记（仅 GDS 路线需要） | ⏸ 依赖 B 段裁决 |
| A9 | 静态审查（`check-model.py --help` 已可运行，依赖 `ple_gds.manifest`） | ✅ |

## 下载任务（含两个已踩的坑）

- 通道：**ModelScope**（实测 ~3 MB/s，`--max-workers 4`）；HF 侧 xet 会 401、hf-mirror 单连接 52 KB/s、aria2 64 并发反降到 1.6 MB/s（上游硬限速），**大文件走 MS + 元数据从 HF 补**。
- 脚本：`resume_download_ms.sh`（断点续传，日志 `/mnt/nvme0/qwen-flash-data/download_ms.log`）；承载用 **systemd 瞬时单元** `systemd-run --user --unit=nvfp4-download --collect --no-block --property=Type=oneshot`（Linger=yes 不随会话退出）。
- **坑 1（Permission denied）**：早期 sudo 下载残留的 `.incomplete` 属主为 `root:root 644`，liyi 身份续传写不进 → 报 `Max retries exceeded ... PermissionError(13)` 后进程死于深夜。**修法**：`sudo chown liyi:liyi <model>/*.incomplete` 后重跑。
- **坑 2（监视器误报）**：`systemctl --user is-active` 波动、`systemctl wait` 本机不支持 → 多次假"完成"通知。**修法**：改用进程级判据（`kill -0 <modelscope_pid>`）+ 连续 3 次探测防抖。
- **微信通知**：哨兵 `$HERMES_HOME/scripts/nvfp4_done_watch.sh`（未完成=空输出→cron 静默；退出后判 `rc=0` 发一条，flag 去重）+ `hermes cron create "every 5m" --script nvfp4_done_watch.sh --no-agent --deliver "weixin:<chat_id>"`。⚠️ **`--script` 必须带扩展名**（不带会报 `Script not found` 且静默失败）；`5m` 是一次性，循环必须写 `every 5m`。

## 下载完成后的执行序（本次已备好脚本）

1. `PYTHONPATH=src /root/vllm-gds-venv/bin/python scripts/check-model.py --model <dir>` 只读校验（期望 `indexed_files=206 / indexed_bytes≈135195303851 / ple_rows=320001536 / mtp_tensors=31`；**先校验再改元数据**，因为校验对 config 有 SHA256 固定比对）
2. `bash /mnt/nvme0/qwen-flash-data/prepare_nvfp4_w4a16.sh`（备份原件至 `.orig-metadata-w4a4/`，改写 W4A16）
3. **切会话模型**：部署要停 flashnext（8000 端口），跑在它上面的会话会死 → 先把会话切到云端 GLM-5.3（微信端发 `/model glm-5.3`；桌面端用状态栏模型选择器）。`hermes-config-ops` 记录：gateway 平台会话用 config 顶部 `model:` 块（**现已指向 zai-coding-cn/glm-5.3**），config 改动需 `hermes gateway restart` 生效。
4. 停服务 → 精确 PID 核查（`pgrep -f "vllm serve"` + `/proc/<pid>/cmdline`）→ 起新栈试加载（TEP2 / 端口 18420 / `block-size 1632` / `--async-scheduling`）；就绪判据三合一（`systemctl is-active` + `ss -ltnp` 监听 PID + 该 PID cmdline 含候选特征串），防假阳性
5. A/B 口径：按作者原口径 **c1 × 8K/32K/64K/128K 五档单请求长输出**，同题同输出上限；并发另测且明确标注（现役栈 c2 有竞态）

## 回滚与风险

- 旧栈回滚 = `systemctl start flashnext`（生产启动器 + drop-in 全部在位；nospec 切换靠 `50-ple-fix.conf`）
- 主机级变更前必须 `scripts/backup-plx-p2p-host.sh`（黄金基线在 `/mnt/nvme1/host-backup-20260913/`）；GRUB 改后必须 `cat /proc/cmdline` + `nvidia-smi topo -p2p r/w` 实测（`disable_acs_redir` 的 `\;` 是正确写法，别"修"）
- 双卡互斥：起新栈前 `systemctl stop flashnext`；170tune 档位恢复 = 改 `/var/lib/170tune/persist/<serial>.conf` 的 `OFFSET`（mclk 是 driver-baked，`persist save` 拒写）
- RAM：新栈 FP8 PLE 51 G mmap（旧栈 BF16 热页 ~29 G 停止后释放），60 G 总量下为"停旧起新"口径，切换期间 flashnext 有 5–10 分钟不可用窗口

## 关键路径

- 仓库 `/home/liyi/Qwen-Flash-SM80-170HX`（HEAD `78c9a59`）｜方案全文 `/home/liyi/qwen-flash-sm80-170hx-迁移方案.md`
- 模型 `/mnt/nvme0/qwen-flash-data/models/Qwen3.8-Flash-Next-NVFP4`｜日志 `download_ms.log`｜元数据改写 `prepare_nvfp4_w4a16.sh`
- dev499 venv `/root/vllm029-venv`（含 `marlin_utils_fp4.py` / `nvfp4_emulation_utils.py`）｜gds venv `/root/vllm-gds-venv`

## A/B 实测结果（09-14 晚，c1 / out 1280 / 同 seed 策略）

| 档位 | A prefill | B prefill | A decode | B decode | B TTFT |
|---|---|---|---|---|---|
| 40K | 2587 | 2460 (-5%) | 93.9 | **100.6 (+7%)** | 16.3s |
| 80K | 4411 | 4518 (+2%) | 61.1 | **101.6 (+66%)** | 17.7s |
| 160K | 5429 | 4767 (-12%) | 69.9 | 33.5 ⚠️ | 33.6s |
| 320K | 6682 | 2649 (-60%) | 63.4 | 3.3 ⚠️ | 120.8s |

- A = AWQ-INT4 / PP2 / spec3+localargmax / cgNONE / gpu_util 0.97 / KV 专属配置（生产配置）
- B = NVFP4(W4A16改写) / TEP2(TP2+EP) / **MTP6+localargmax** / Marlin / cg FULL_AND_PIECEWISE / **gpu_util 0.85（社区原值）** / 原生窗口 262144（500K 档不可测）
- 日志文件：`results/qwen38flash_awq_c1_ab0914_40k500k.log` / `results/qwen38flash_nvfp4_tep2_mtp6_c1_ab0914.log`

### 结论

1. **路线成立**：NVFP4+W4A16 Marlin 在 sm80 正确落核（日志 `Using 'MARLIN' NvFp4 MoE backend`），冒烟语义/算术全对，全程 **0 Xid、0 崩溃**——MTP6 大 spec 在 TP2 拓扑下没有复现 PP2 的 spec 记账竞态。
2. **短上下文完胜**：40K/80K decode 100+ t/s（+7%/+66%），引擎日志实测 **MAL 3.33**（分位置 0.667/0.333/…）——社区投机解码路线在本机真实复现。
3. **长上下文崩是配置问题不是路线问题**：160K/320K decode 跌至 33.5/3.3，主因 B 沿用社区 `gpu_memory_utilization 0.85` → 320K 单请求 KV 占用 80%+（日志 67.9%→80% 触发压力），A 是 0.97+专属 KV。次因 PLE FP8 51G 冷读（首遍全表扫描，320K TTFT 120s 里叠加）。
4. **待做**：B 加 `--gpu-memory-utilization 0.97` + YaRN overrides 复测 160K/320K/500K，即"社区路线满血版"数字。
5. **副产物**：spec6 未触发 QSA ring 1616 整除断言（与 dev499 PP2 认知不同）；`VLLM_USE_BREAKABLE_CUDAGRAPH` 自动开启。

### 复现要点

- B 启动器：`/mnt/nvme0/qwen-flash-data/start_nvfp4_tep2.sh [spec|nospec]`（社区参数蓝本 + PLE mmap env 适配）
- 元数据改写原件备份：`models/Qwen3.8-Flash-Next-NVFP4/.orig-metadata-w4a4/`
- 教训：① 非流式 bench 在 MTP6 高接受率下档间会"串档"（Running:2），档间结果要看单档明细 ② 停 vLLM 留 defunct worker 占 55G+ 显存须按 PID 收尸（老坑重现）③ backend `.backend_port` 文件在进程死后残留，起测前须验 WS 真连通
