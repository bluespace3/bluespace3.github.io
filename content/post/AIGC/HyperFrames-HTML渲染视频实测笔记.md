---
title: 'HyperFrames-HTML渲染视频实测笔记'
categories: ["AIGC"]
date: 2026-09-15T16:03:01+08:00
lastmod: 2026-09-15T16:03:01+08:00
draft: false
---
# HyperFrames 研究与实测笔记

> 2026-09-15 · github.com/heygen-com/hyperframes · 50k+ star · Apache-2.0 · TypeScript · HeyGen 开源

## 一句话定位

**「Write HTML. Render video. Built for agents」** —— HTML→MP4 确定性渲染框架。视频=一个 HTML 文件：`data-start`/`data-duration` 属性定义时间轴，GSAP/CSS/Lottie/Three.js/WAAPI 写**可 seek** 动画，headless Chrome 逐帧 seek + FFmpeg 编码。同输入必得同输出 → CI/回归测试友好。**无需构建步骤**，index.html 浏览器直接预览。

## 核心 API（极简）

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="10"
     data-width="1920" data-height="1080">
  <h1 class="clip" data-start="1" data-duration="4">标题</h1>
  <video class="clip" data-start="0" data-duration="6" src="a.mp4" muted playsinline></video>
  <audio data-start="0" data-duration="6" data-volume="0.5" src="bgm.wav"></audio>
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.from("#t", { opacity: 0, y: 40, duration: 0.8 }, 1);
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;   // 每个 composition 注册一个 paused 根 timeline
</script>
```

关键契约（AGENTS.md 摘要）：
1. 每个计时元素要有 `data-start` + duration，视觉元素加 `class="clip"`
2. `window.__timelines["<composition-id>"]` 注册 paused 根 timeline；子 timeline 不能再 paused
3. 视频 `muted` + 独立 `<audio>` 出声
4. 子合成 `data-composition-src="compositions/x.html"`
5. **只允许确定性逻辑**：禁 `Date.now()`/`Math.random()`/网络 fetch
6. 变量注入：`--variables '{"title":"x"}'` → `window.__hyperframes.getVariables()`；`--batch rows.json` 批量出片

## 实测记录（本机 9800X3D，纯 CPU，GPU 零占用）

### 安装（坑最多的一步）

- ❌ `npx hyperframes init` 直走代理：onnxruntime-node 二进制(113MB, GitHub release) + Chrome(从 Google storage) 下载龟速，15+ 分钟无进展
- ✅ 正确姿势：
```bash
# 1) CLI 跳过二进制下载
npm i hyperframes@0.8.40 --ignore-scripts --registry=https://registry.npmmirror.com   # 3秒装完
# 2) Chrome headless-shell 从 npmmirror 手动下
curl -o chhs.zip https://cdn.npmmirror.com/binaries/chrome-for-testing/141.0.7390.122/linux64/chrome-headless-shell-linux64.zip && unzip chhs.zip
```
- 浏览器覆盖变量：`HYPERFRAMES_BROWSER_PATH=/path/to/chrome-headless-shell`（`PUPPETEER_EXECUTABLE_PATH` 无效）
- 相关 env：`HYPERFRAMES_FFMPEG_PATH` / `HYPERFRAMES_FFPROBE_PATH`（默认 `FFMPEG_PATH`/`FFPROBE_PATH` 不认）

### ⚠️ 环境坑：本机 ffprobe 是假的

`/usr/local/bin/ffprobe` → symlink 到 imageio_ffmpeg 的 **ffmpeg** 二进制 → 报 `Unrecognized option 'print_format'` 渲染最后一步崩。**解决**：`sudo apt install ffmpeg`（6.1.1 真 ffprobe 在 `/usr/bin/ffprobe`）+ `HYPERFRAMES_FFPROBE_PATH=/usr/bin/ffprobe`。此坑影响所有依赖 ffprobe 的工具，值得全局排查。

### 渲染闭环 ✅

- `hyperframes check`（xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 五门）：第一次报 `font_family_without_font_face`——**连系统字体都要显式 `@font-face { src: local('...') }`**（渲染确定性的偏执程度可见一斑）。加声明后全过。
- 写 8s 中文 demo（两幕：kinetic 标题「写网页，出成片」+ 琥珀色 count-up 到 50,089）
- **`hyperframes render` 实测：8s@30fps 1080p 用 2.4 秒渲染完**（capture 1.2s + encode 0.6s，software gpu/SwiftShader），产物 678KB h264。`hyperframes doctor` 可查环境（whisper-cpp/Kokoro TTS/MusicGen 均为可选本地项）
- 抽帧确认画面正常、中文无豆腐块（Noto Sans CJK）

成片：`~/hf-test/hf/demo/out.mp4`（已发飞书）

## 与 MoneyPrinterTurbo 对比（123k star, Python/MIT, 主题→全自动成片）

| | HyperFrames | MoneyPrinterTurbo |
|---|---|---|
| 定位 | HTML→视频**渲染引擎**（合成器/包装层） | 主题→成片**全自动流水线**（内容工厂） |
| 输入 | 人/agent 写 HTML+GSAP 时间线 | 一个关键词，LLM 全包 |
| 画面来源 | 网页渲染：排版/图表/动效/嵌入素材 | Pexels/Pixabay 库存 + 多家 T2V API(Seedance/H3/Wan) |
| 动画 | 帧级精确可 seek，shader 转场、count-up 随便做 | 库存拼接+简单缩放，无设计层 |
| 确定性 | 核心卖点，CI 回归 | 无（素材搜索随机） |
| TTS/字幕/BGM | skill 内置(可选本地 Kokoro/MusicGen/whisper) | EdgeTTS+10余家、whisper 字幕，全有 |
| 形态 | CLI/Studio/Lambda/云渲染 | Streamlit WebUI+FastAPI+一键包+自动发布 TikTok/YT |
| Agent 接口 | 20 个 skills（`npx skills add`），MCP 生态 | SKILL.md 单文档 |
| 许可证 | Apache-2.0（干净） | MIT（但 README 一半是 API 中转商赞助位） |

**结论：不同层，互补不互斥。**
- MPT=傻瓜出片，画面天花板低；HF=agent 的 AE，画面内容要另行供给
- 对我方流水线的价值：**HF 做包装层**——片头、kinetic 字幕、数据动画、talking-head 设计化 overlay（官方 `/embedded-captions`、`/talking-head-recut` 工作流即此用途），可替换 PIL 烧字幕；素材仍走 ComfyUI/H3。HF 渲染不吃 GPU，能和 I2V 流水线并行不打架
- MPT 值得抄的是任务/批量/API 工厂形态

## 快速命令备忘

```bash
cd ~/hf-test/hf
export HYPERFRAMES_BROWSER_PATH=~/hf-test/chrome-headless-shell-linux64/chrome-headless-shell
export HYPERFRAMES_FFPROBE_PATH=/usr/bin/ffprobe
./node_modules/.bin/hyperframes init demo --non-interactive
cd demo && ../node_modules/.bin/hyperframes check
../node_modules/.bin/hyperframes render --output out.mp4   # 默认30fps/looks(CRF16)；--fps 60 --quality delivery
```

- demo 项目：`~/hf-test/hf/demo/`（index.html 含中文 kinetic 标题+count-up 完整参考）
- docs：hyperframes.heygen.com，机读索引 `llms.txt`；`hyperframes docs <topic>` 离线查
- 对比 Remotion：HF 押纯 HTML（无 React/无 bundler/Apache-2.0），Remotion 押 React；有 `/remotion-to-hyperframes` 迁移 skill
