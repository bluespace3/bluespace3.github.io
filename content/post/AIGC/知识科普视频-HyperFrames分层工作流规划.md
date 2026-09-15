---
title: '知识科普视频-HyperFrames分层工作流规划'
categories: ["AIGC"]
date: 2026-09-15T16:17:14+08:00
lastmod: 2026-09-15T19:27:45+08:00
draft: false
---
# 知识科普/项目介绍视频 — HyperFrames 分层工作流规划

> 2026-09-15 定稿 · 承接《HyperFrames-HTML渲染视频实测笔记》· 状态：规划（①②档待实测验证）

## 0. 适用边界（先划线）

**适用**：概念驱动内容——知识科普、教程讲解、项目/产品介绍、数据报告、changelog 视频化。
**不适用**：画面驱动内容——山海经/古文/纪录片类（08-12 规：写实纪录风，靠 I2V 实镜，禁止网页感排版）。口播情景剧类也不适用（配音=老驴克隆，走现有 I2V 流水线）。

判断标准：**画面是"讲清楚概念"还是"呈现意境"**。前者进本流水线，后者走 ComfyUI/H3。

## 1. 总流水线（六阶段）

```
选题文本 ──① 脚本──▶ 分镜稿(YAML) ──② 配音──▶ WAV+词级时间戳
                                                    │
   成片 ◀──⑥ 审核门+发布 ◀──⑤ render ◀──④ 合成装配 ◀┘
                                                    
④ 的画面素材按"四层策略"分工生产（见 §3），并行汇入
```

| 阶段 | 工具 | 产物 | 算力 |
|---|---|---|---|
| ① 脚本 | 本地 vLLM（GLM/FlashNext）| 分镜 YAML：每 scene = 旁白文本 + 画面层指定（默认 L1；标 L2/L3 需给"必须动"的理由；**L4 禁默认选取**，仅在 prompt 里明确告知 L4 是审批例外）| CPU |
| ② 配音 | edge-tts(云扬,-10%) 或 IndexTTS v1 克隆（科普女声）| WAV → `whisper.cpp`/transcript.json 词级时间戳 | CPU |
| ③ 素材生产 | 四层策略（§3）| SVG 组件 / Lottie JSON / I2V 片段 / 图表数据 | ①②③档 CPU；④档 GPU（ComfyUI）|
| ④ 合成装配 | agent 写 index.html（HF skills 约束）| composition 项目 | CPU |
| ⑤ 渲染 | `hyperframes check` → `render` | MP4 | 纯 CPU，**与 GPU 的 I2V 可并行不打架** |
| ⑥ 审核门 | 抽帧 → vision 审（沿用 h3_qc 思路）| 通过→发布；否则回④迭代 | CPU |

沿用全局规则：⑦审核门必过、④精确 PID、脚本 `--step` 幂等跳过、日志 `~/桌面/pipeline.log`。

## 2. 时间对齐契约（核心难点，先定死）

**旁白时长驱动一切**（用户 08-08 规：视频长度跟配音走，每段 80-120 字，引入→递进→高潮→总结）：

1. 配音完成后拿词级时间戳（whisper），生成 `beats.json`：每个 scene 的 start/duration、每句字幕的精确入出点
2. index.html 里所有 `data-start`/`data-duration` **从 beats.json 程序化生成**（模板引擎或 agent 按数据填），不手拍数字
3. GSAP timeline 内的动画偏移 = scene 内相对时间，字幕动画对齐词时间戳（误差 ≤1 帧）
4. ⚠️ HF 里禁用 PTS 拉伸思路——时间是刚性的，改配音=重新生成 beats → 重装配 → 重渲（反正 render 秒级，成本可忽略）
5. 字幕样式：仍守 subtitle-burn-standard 的像素 A/B 终审；HF 内字幕是 DOM 元素不是滤镜，lint 会自动查 contrast（WCAG）

## 3. 画面四层策略（本规划的核心）

**配比总则（09-15 定）：静态画面为主，动画只做点睛。** 一个 scene 默认就是 L1 静态排版（含入画/出场这类基础转场动效，不算"动画"）；动画（L2/L3）只花在**概念被"讲透"的那一下**——生长曲线、count-up 高潮、关键机制演示，单片动画占比建议 ≤30% 时长，每 60s 视频 1-3 处足矣。**L4 写实画面是显式可选项，默认关闭**（理由：成本高、会诱导 LLM 分镜滥用 I2V 稀释概念密度、与科普"图解优先"的气质不符——需要它的科普场景很少）。

按"动画复杂度"选层，**所有层收敛进同一个 index.html 的同一个可 seek 时间线**：

### L1 · 排版/字幕/静态画面 — HTML+CSS（+GSAP 基础入画动效）【主力层，默认】
- 用途：大字号概念、kinetic captions、章节卡、对比分栏、highlight 划重点——**静态呈现是常态**，入场/强调动效是标配但按 seek-safe 写
- 生产方式：agent 直接写，`/hyperframes-animation` + `/hyperframes-keyframes` skills 兜模式
- 成本：零素材，最快路径。**分镜默认落点：没有明确"必须动"的理由就留在 L1**

### L2 · 图解级动画 — 手写 SVG + GSAP【点睛，节制使用】
- 用途：流程箭头流动、轮子旋转、描线生长（`stroke-dashoffset`）、path morph、几何示意、简笔画图标动效
- 生产方式：**LLM 代码生成**（几何/流程/简笔类是 LLM 强项）+ 人工微调；SVG 组件入库 `assets/svg/` 复用
- 规范：每个可动部件独立 `<g id>`；动画只动 transform/opacity/stroke 属性（seek-safe）；禁 `<animate>` SMIL 与 JS 时钟混用；`viewBox` 固定禁百分号宽高
- 实测状态：待验证（鹈鹕骑自行车测试件已立项，见 §7）

### L3 · 角色/物理事件级 — Lottie
- 用途：拟人角色循环（走路/骑车/点头）、复杂 bound puppet、加载类吉祥物
- 铁律：**不手写角色关键帧，不用 I2V 抽风做小图标动效**；LLM 画不好这类 SVG（经典 pelican-bicycle 全灭）
- 生产方式：优先 lottiefiles 市场现成素材（导出 JSON 冻结进仓库）；无货再 AE/Rive 自制导出
- HF 接入：Lottie 适配器，`goToAndStop(frame)` 帧索引驱动，**比 GSAP 更贴确定性模型**（零墙钟风险）
- 素材治理：只收离线 JSON，禁运行时 fetch（确定性契约）；命名 `lottie_<动作>_<帧数>.json`

### L4 · 写实/有机画面 — ComfyUI/H3 生成后挂入【可选项，默认关闭】
- **默认不用**。仅当选题整篇确实依赖真实画面感（如"显微镜下的细胞分裂"这类图解无法承载的题材）才开启，且需分镜阶段显式标注 `l4: true` 走审批口径，不允许装配阶段临时加
- 用途：实景示意、科学现象实拍模拟等 L1-L3 承载不了的概念
- 生产方式：现有 I2V 流水线照常跑（GPU），产物当 `<video class="clip" muted>` 挂进 HF；音频走独立 `<audio>`
- 注意：视频片段必须先过 h3_qc 三层审核再入 HF 装配；HF 会自动 proxy 媒体（`media.autoProxy`）

**选型决策树**：
```
scene 需要动吗？（判据：不动能否讲清概念——默认答案是不能才继续往下）
   │否（默认，多数 scene）
   ▼
L1 静态排版 + 标配入画动效 ◀────────────── 80% 以上的 scene 应落在这里
   │是
概念示意/流程/几何？ ──是──▶ L2 手写SVG（动画点睛，≤30%时长）
   │否
角色/机械/循环动作？ ──是──▶ L3 Lottie(市场优先)
   │否
分镜阶段已显式标 l4:true？ ──是──▶ L4 I2V素材(默认关，需审批)
   │否
回到 L1：用排版动效硬讲（静态排版+精准字幕本身就是表现力）
```

## 4. 项目目录与复用规范

```
kf-video/<选题名>/                 # 每个科普选题一目录（~/comfy 同级）
├── index.html                     # 根 composition（装配阶段程序化生成）
├── beats.json                     # 词级时间戳+scene 预算（②产物，勿手改）
├── narration/                     # WAV + 冻结的 BGM（media-use ledger）
├── assets/
│   ├── svg/                       # L2 组件库（跨选题复用，入 git）
│   ├── lottie/                    # L3 冻结 JSON（禁运行时下载）
│   └── video/                     # L4 已过审 I2V 片段
├── compositions/                  # 子合成（长片拆分章节）
└── renders/
```

- **共享组件库**：`kf-video/_lib/` 沉淀章节卡模板、字幕轨组件、常用 L2 图解（曲线生长/漏斗/时间轴/对比卡），新项目 `hyperframes add` 或软链复用——目标是第 3 个视频起只做内容不做基建
- 字体：全局 `@font-face src:local()` 清单固化进模板（Noto Sans CJK + 一个数字等宽），过 lint 不再踩
- GSAP 本地化：`assets/gsap.min.js` 冻结版本入库，禁 CDN（确定性+断网可渲）

## 5. Agent 分工（HF skills × 自有 skills）

| 环节 | 负责方 |
|---|---|
| 脚本分镜 | 本地 vLLM + 台词规范（80-120字/段）|
| 配音+时间戳 | 自有 pipeline 脚本（edge-tts/IndexTTS → whisper）|
| L1/L2 composition | coding agent + `/hyperframes` 路由 → `/faceless-explainer`（科普）或 `/product-launch-video`（项目介绍）；改动后必跑 `hyperframes check` |
| L3 选型 | agent 搜 lottiefiles 冻结素材；缺口登记"待 AE 自制"清单 |
| L4 | 现有 ComfyUI 流水线 + h3_qc 审 |
| 装配 | beats.json → index.html 模板生成（脚本），agent 只做 diff 修正 |
| 审核 | 抽帧 vision 审 + 字幕像素 A/B；成片走局域网链接交付 |

## 6. 环境（实测已踩平的坑，直接抄）

```bash
# 一次性
sudo apt install ffmpeg                      # 真 ffprobe（/usr/bin），绕开机那台假 symlink
npm i hyperframes@X.Y.Z --ignore-scripts \
    --registry=https://registry.npmmirror.com # 3秒；禁走 npx 直装(代理下 onnxruntime/Chrome 龟速)
# chrome-headless-shell 从 npmmirror 手动下（版本对齐 puppeteer）

# 每次渲染会话
export HYPERFRAMES_BROWSER_PATH=~/hf-test/chrome-headless-shell-linux64/chrome-headless-shell
export HYPERFRAMES_FFPROBE_PATH=/usr/bin/ffprobe
```
- lint 三门必过：`@font-face` 全覆盖 / 禁 `Math.random`·`Date.now`·fetch / clip+timeline 注册规范
- 渲染参数：默认 30fps/looks(CRF16) 足够；交付档 `--quality delivery`；实测 8s@1080p 渲染 2.4s，10 分钟长片外推 ≈2-4 分钟
- 全程 CPU（SwiftShader+x264 软编），GPU 空闲——**I2V 在渲关键帧的同时可以并行 render 装配片**

## 7. 落地路线（验证顺序，逐级解锁）

1. **[✅ 09-15 超预期完成] 端到端样片**：`~/kf-video/hyperframes-intro/`——HyperFrames 自我介绍 3分08秒成片一次跑通：脚本→IndexTTS女声(GPU RTF0.17)→句级时间戳→L1+L2 装配(4个SVG流程图)→render 1m33s→QC→飞书交付。L2 验证顺带覆盖（流程图/金字塔/泳道全部 SVG+GSAP）；L3 Lottie 未触发（本项目无角色动画需求）
2. **[✅ 同步沉淀] skill 固化**：`media-production/hyperframes-kf-pipeline`（SKILL.md+step2/step4 脚本+script.json 模板），下个项目直接套用
3. **[待做] 模板泛化**：第 2 个选题（候选：mcp-intro.md / RAG.md）用时若 <30 分钟人工介入则视为流水线成熟；届时抽 `kf-video/_template/` 并接 `--step` 幂等脚本体系
4. **[待做] 首个正式发布选题**：数据密度高的科普题材打样发布，复盘后定 L2 的 LLM 生成边界是否需要单独 skill

**风险登记**：
- L2 的 LLM 生成质量上限存疑 → 路线 1 先行定级，不行就降级为"仅流程/几何图，角色一律 L3"
- whisper 词时间戳对中文语速的精度 → 样片实测，必要时句级对齐+手调
- BGM/音效来源：HF media-use 走国外模型，本地优先用现成曲库冻结（同"3套VAE不混用"式的登记管理）
- L4 片段进 HF 后整体重渲成本：片段长则先 proxy 低码预览，终审后换高码重渲

## 8. 系列量产实战（09-15 晚，17集全量完成）

**《小白AI通识课》E01-E17**：`~/kf-video/ai-course/`，总时长 ~63 分钟，全部 IndexTTS 女声+一句一屏字幕+7种模板图解。

**关键升级——通用装配器 `step4_gen.py`**（已入 skill scripts/）：
- script.json 声明式驱动：每场景 `{"id","type","p":{...},"narration"}`，7 种模板 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- 每集制作=只写 script.json（10分钟创作），TTS→装配→check→render→QC→飞书全自动（`run_all.sh` 幂等批量）
- 泛化指标达成：E02 起 0 人工干预，17/17 FAIL=0

**新增坑**：
- 装配器根容器五件套 `data-composition-id/width/height/duration/fps` 缺一 check 报 4 错
- `__timelines` 必须按 composition-id 注册（`["main"]=tl`），不能 push 数组
- compare rows 支持三种形态：双元素/字符串/单元素数组（通栏注释行）
- 生成式写 JSON 用 write_file 直写项目路径会被 lint 拒 → 先写 /tmp 验证再 cp
- `hyperframes render` 音频混流失败=无声片（audio src 断链时 hard fail，草稿验证须 sed 掉 audio 标签）
