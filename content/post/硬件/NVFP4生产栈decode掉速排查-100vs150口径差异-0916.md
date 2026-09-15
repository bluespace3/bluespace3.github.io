---
title: 'NVFP4生产栈decode掉速排查-100vs150口径差异-0916'
categories: ["硬件"]
date: 2026-09-16T00:20:02+08:00
lastmod: 2026-09-16T00:20:02+08:00
draft: false
---
# NVFP4 生产栈 decode「掉速」排查：100 vs 150 是口径差，不是升级回退

日期：2026-09-16 00:30 ｜ 状态：✅ 已定位，无需修复
前置：[NVFP4 vs AWQ A/B 实测](NVFP4-W4A16-vs-AWQ-AB实测-TEP2-MTP6-0914.md)、[社区栈迁移计划](Qwen3.8-Flash-Next-NVFP4社区栈迁移与对比计划-0914.md)

## 现象

社区仓库 Qwen-Flash-SM80-170HX 于 09-15 23:24 `git pull` 升到 v0.1.7（`78c9a59→d73d882`，多轮 PLE handoff 加固 + QSA 预加载扩容）。同时段观察到 vLLM decode 只有 **~100 t/s**，而"昨天"能测出 **150+**，怀疑升级导致回退。

## 一句话结论

**与仓库升级零关联，是测试口径差异。** 150+ 出自社区等口径探针（代码任务 + thinking 开 + 长输出稳态，MAL 4.0-5.1）；100 出自普通短输出（out≤3000、普通内容，MAL 2.6-3.1）。decode ≈ 步率(≈39-42 步/s) × MAL，**内容决定 MAL，是主变量**——这条 09-14 深夜就写进过 A/B 笔记结论（"别拿普通文跟社区数字比"），这次是它的一次现场重演。

## 排除升级嫌疑的实证链

| 检查项 | 结果 |
|---|---|
| 生产栈是否引用仓库代码 | **否**。`start-nvfp4-prod.sh` 无 PYTHONPATH/仓库路径；`grep -rl Qwen-Flash-SM80 /root/vllm029-venv/.../vllm/` 零命中 |
| vLLM 本体是否被动过 | 否。venv site-packages 最后修改 **09-08**（dev499 build 未重建）；v0.1.7 的修复主体（GDS/TP_PLE/QSA preload）此前已证伪不移植 |
| 今天两次启动是否同配置 | 是。20:08 与 23:27 两次启动 cmdline 完全一致；量化后端选择逐行一致（`nvfp4.py` **MARLIN** MoE + `unquantized.py` **TRITON**，MTP draft 层）|
| GPU OC 是否掉了 | 否。`nvml_oc` 偏移 GPU0=+200 / GPU1=+250 在位，负载采样 `clocks.current.sm=1395`（锁 1400 档正常生效）。170tune-persist 是 oneshot，21:04 执行完退出属正常 |

## 数字对照（同机同栈）

| 口径 | decode | MAL | 出处 |
|---|---|---|---|
| 社区等口径：32K/64K 长 prompt、代码生成、thinking 开、out→5 万稳态 | **166-168**，引擎 10s 打点中位 **180.5** / 峰值 234 | 4.04-5.07 | 09-14 深夜 parity 探针（=「昨天的 150+」） |
| 普通对话/长文（并发会话在跑代码任务时打点） | 140-146 | 2.8-3.1 | 09-16 00:00 pipeline.log 打点 |
| c1 out1280 普通长文（A/B 的 B 栈五档） | **96-107** | 2.48 | 09-14 A/B `qwen38flash_nvfp4_tep2_mtp6_c1_ab0914` |
| 今晚复测：短 prompt + out 3000 + thinking 开 | **94-120**（客户端 94.1；同窗口引擎打点 95.5-120.2） | 2.62-3.14 | 本次排查实测 |

## 今晚实测怎么做的

- 服务：:8000 NVFP4（23:27 由 model-launcher 手动拉起；此前 flashnext.service 21:04 退出，`Restart=no` 是 09-15 定案设计，不是故障）
- 探针：Flask 网站 prompt + `max_tokens=3000` + `enable_thinking/preserve_thinking` + 社区采样（temp1.0/top_p0.95），`stream_options.include_usage` 取 token 数
- 坑复现两枚：① 客户端流式墙钟计时仍偏低（94.1 vs 引擎 100+），**判数只认引擎打点**；② venv 缺 socksio + `all_proxy` 劫持 → httpx 必须 `trust_env=False`（或装 `httpx[socks]`），与同日「no_proxy 的 CIDR 坑」是同一族环境噪音。

## 验收方法（下次判断是否真回退）

1. **同口径才可比**：要复核 150+，重建 parity 探针（口径要素一项不能少：长 prompt 32K+、代码任务、thinking 开、输出跑过 8K 进入稳态、采样参数社区值）；探针模板在 skill `qwen-flash-sm80-170hx-migration`「探针对照」节，/tmp 重启即失需重建
2. **看 MAL**：`SpecDecoding metrics` 打点里 Mean acceptance length ≥4 ⇒ 内容口径对上了；2.5-3 ⇒ 本来就是普通文，100 出头是正常值
3. **基线锚点**：c1 out1280 = 96-107 平带（无长度衰减是 NVFP4 栈特征，AWQ 同档只有 61-94）；若这个锚点本身掉到 <90 再怀疑栈
4. 引擎打点判据：`grep "Avg generation throughput" ~/桌面/pipeline.log`，10s 窗口粒度够看

## 同日插曲（与掉速无关，一并留档）

- 09-15 晚 CLI 会话连本地 vLLM 持续 502：根因 = `no_proxy` 写成 CIDR `xxx.xxx.xxx.xxx/8`（httpx 不认，curl 认），GNOME gsettings ignore-hosts 经 proxy-switch.sh「全局模式」→ gnome-terminal-server 快照 → 终端进程继承。三层修复（gsettings 改裸 IP / 脚本防再武装 / provider base_url 一律 `localhost`）。详见 skill `global-model-switch` 502 坑条目
- config 顶部 model 块残留已删旧 slug `custom:127-0-0-1-8000` → `Unknown provider`，`switch-global-model.sh` 一条命令治愈
