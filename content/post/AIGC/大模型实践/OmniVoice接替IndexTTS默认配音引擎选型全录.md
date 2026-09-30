---
title: 'OmniVoice接替IndexTTS默认配音引擎选型全录'
categories: ["AIGC"]
date: 2026-09-30T16:03:03+08:00
lastmod: 2026-09-30T16:03:03+08:00
draft: false
---
# OmniVoice 接替 IndexTTS 成为默认配音引擎（选型全录 · 2026-09-30）

## 结论先行

**定案：本机配音默认引擎由 IndexTTS v1 切换为 OmniVoice（k2-fsa/OmniVoice，VoiceStudio 项目默认引擎）。** 触发点是用户试听克隆样片后直接拍板"提升明显"。IndexTTS 归档为可回退的历史方案，:8766 端口由新引擎以完全兼容契约接管，各流水线 script.json 零改动。

## 选型背景

- 起因：评估 GitHub 项目 debpalash/VoiceStudio（48.9k star，本地化 ElevenLabs 替代，AGPL-3.0）。初判"用不上"（配音链路已锁 IndexTTS），用户仍要求拉下来实测——**证据审判优先于既有定案**，包括我自己一周前写的否定结论。
- 定性结论修正记录：初判"音色设计可满足情绪控制"不成立——OmniVoice 的 instruct 是约 40 项闭集标签词表（性别/年龄/方言/音调档/耳语），自由描述词被拒。情绪表现力这条收益宣称作废，登记欠账（若日后需要，仍走参考音频本身或另测 IndexTTS 2.5）。

## 实验设置（对照口径）

- 独立环境：/mnt/nvme1/voicestudio-test（clone 仓库 + 独立 venv + torch CPU 版），生产双卡 flashnext 全程未动
- 权重：modelscope 直连 k2-fsa/OmniVoice，2.45GB，11MB/s，5.5 分钟
- 参考音频：① 可爱女声 12s 切片（科普音色）② clone_ref_a 电影解说男声 9.5s（山海经/纪录片音色）
- 验收方法：合成 → faster-whisper ASR 回听比对文本 → 用户耳朵终审

## 实测数字（标注：CPU / OMP 12 线程 / fp32，GPU 数字未测——双卡被生产占满，按规则不抢卡）

| 项目 | 数值 |
|---|---|
| 权重加载 | 0.7s |
| 克隆合成（21 字 → 6.2s 音频） | 40.8s（CPU RTF≈6.6） |
| 音色设计合成（同文本量） | 15.7s |
| 服务稳态短句合成 | ~32s/21字 |
| 新参考首见（含自动转写） | +~136s，之后按 sha1 走缓存 |
| 输出 | 24kHz mono PCM16，RMS 0.13/peak 0.84，与旧管线同规格 |
| ASR 回听 | 文本 100% 还原；已知瑕疵：句首偶带一个气口（"嘿"），剪辑时裁头 |

音质判定=用户耳朵（试听克隆样后当场定案）；相似度主观感受接近参考原声，跨语种克隆能力为增量收益（出海配音备用）。

## 落地形态（通道工程）

- systemd user unit `omnivoice-tts.service`：Restart=always、Linger=yes、MemoryMax=12G、HF_HUB_OFFLINE=1
- 监听 xxx.xxx.xxx.xxx:8766（旧 IndexTTS 端口），`POST /tts {text, ref_b64}` 返回 RIFF wav —— 与 step2_tts_http.py 契约逐字节兼容
- 增量能力：`voice:"注册音色名"`（免传参考）、`instruct:"闭集标签"`（音色设计）、GET /voices
- 设备策略：默认 cpu（不抢生产卡）；GPU 腾窗后改 `OMNIVOICE_TTS_DEVICE=cuda` 一键切换（欠账：GPU 速度基线未测）
- 音色纪律平移：老驴音色仅限老驴探案、严肃内容用电影解说男声——换引擎不换音色授权

## 踩坑录（裸用 VoiceStudio 引擎层，服务内已封装修复）

1. torchaudio 2.14 `save` 依赖 torchcodec（默认没装）→ 改 soundfile 写盘
2. `generate()` 有时返回 `list[Tensor]` 而非 Tensor → unwrap 一层
3. faster-whisper 喂 wav 路径触发 av 新版 `metadata_errors` TypeError → 喂 numpy 数组绕开
4. 克隆请求缺 ref_text 时引擎强制现场 ASR 否则直接 raise（"Automatic reference transcription needs..."）→ 服务内置 whisper-small 自动转写+按参考内容 sha1 缓存（旧契约只传 text+ref_b64，此层是兼容关键）
5. instruct 词表外自由形容词被拒并回打合法词表 → 写进 skill 防再犯

## 未闭环欠账

- [ ] GPU（cuda fp16）速度基线：待双卡腾窗，预计 <1GB 显存即够
- [ ] 与 IndexTTS v1 严格同文本 A/B（数字对比归档）：:8766 已被新引擎接管，旧服务未运行，需手动拉旧 venv 复测才有数字；用户耳朵已定案，此项仅补审计追踪
- [ ] 长文本（3 分钟级旁白）批跑实测：CPU 口径外推 ~1h/集，是否触发"必须等 GPU 窗口"的产能红线，等第一集实战校准

## 相关文件

- 服务：/mnt/nvme1/voicestudio-test/tts_server.py · omnivoice-tts.service
- 音色注册：/mnt/nvme1/voicestudio-test/voices.json
- 听样：/mnt/nvme1/voicestudio-test/{omnivoice_clone_test,omnivoice_design_male,smoke_男声}.wav
- 卡片：skill `omnivoice-tts-default`（硬约束/契约/运维全录）
