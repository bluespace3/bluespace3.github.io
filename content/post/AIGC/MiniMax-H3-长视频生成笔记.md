---
title: 'MiniMax-H3-长视频生成笔记'
categories: ["AIGC"]
date: 2026-08-12T16:23:34+08:00
lastmod: 2026-08-12T16:23:34+08:00
draft: false
---
# MiniMax H3 长视频生成笔记

> 来源：Reddit r/StableDiffusion 帖子及社区讨论整理
> 日期：2026-08-12
> 原帖：[Long-form videos (1 min+) are very possible with MiniMax H3](https://www.reddit.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/)

---

## 一、MiniMax H3 模型概述

MiniMax H3（又名 Hailuo 3.0 / Hailuo 03）是 MiniMax 于 2026年7月31日发布的**通用多模态生成模型**。

### 核心特性

| 特性 | 规格 |
|------|------|
| **单次生成时长** | 4~15 秒（默认 8 秒） |
| **分辨率** | 最高 2K（原生 768px 短边，上限 768×1344，32 的倍数） |
| **帧率** | 24 fps |
| **音频** | 原生立体声（语音+音效+音乐，单次前向传播同步生成） |
| **参考输入** | 最多 9 张参考图 + 3 段参考视频 + 3 段参考音频 |
| **帧网格** | 17k+5 帧/块（duration 按 17 帧粒度对齐） |
| **开源许可** | MiniMax Community License（年收入 < $20M 组织可商用，需署名） |
| **排行榜** | Artificial Analysis：视频编辑 #1、T2V #2、I2V #3 |

### 技术架构

- **Contextual Omni Representation**：统一理解文本、图像、视频、音频
- **H3-VAE**：视频变分自编码器
- **H3-Omni Transformer**：全模态 Transformer 主干
- **In-Context Regeneration**：上下文内再生成

### 三种生成模式

1. **T2V (Text-to-Video / FL2VA)** — 纯文本生成视频
2. **I2V (Image-to-Video / FL2VA)** — 首帧/尾帧条件生成
3. **R2V (Reference-to-Video / Ref2VA)** — 多参考（图+视频+音频）生成

> ⚠️ R2V 使用 `ref2va` 权重，与 T2V/I2V 的 `fl2va` 权重不同。

---

## 二、为什么能做长视频？

H3 **单次上限只有 15 秒**，API 没有 extend 参数。长视频的核心思路是**链式拼接（Chaining）**：将上一段的末尾帧/潜在表示传给下一段作为起始条件。

### 关键发现

- H3 在单次 15 秒生成中**支持多镜头（multi-shot）**，用时间码分割镜头
- 社区已实现 **1 分钟以上**的连贯视频
- 进阶方案甚至可以做到** 2 小时长片**

---

## 三、长视频生成方案（由简到难）

### 方案 1：手动链式拼接（FFmpeg + I2V）

**原理**：提取上一段最后一帧 → 作为下一段的首帧 → 循环

```bash
# 提取最后一带（近似末尾帧）
ffmpeg -sseof -0.08 -i generation-1.mp4 -frames:v 1 -q:v 2 handoff-frame-01.jpg
```

**流程**：
1. 用 T2V 或 I2V 生成第一段（15s）
2. FFmpeg 提取末尾帧
3. 用 I2V 模式，将该帧作为 `first_frame` 生成下一段
4. 需要换镜头角度时，切换到 R2V 模式
5. 用硬切（hard cut）拼接所有片段

**优点**：简单直接，无需额外插件
**缺点**：接缝处可能有跳变、色彩偏移

### 方案 2：ComfyUI 多镜头工作流（Storyboard / 首尾帧连接）

**原理**：在 ComfyUI 中用 Storyboard 工作流，将多组首尾帧串联

**关键组件**：
- `MiniMaxH3ImageToVideo` 节点连接 `first_frame` 和 `last_frame`
- 每段独立生成后自动合并为一个完整视频
- 可设置每段 5~15 秒不等

**社区资源**：
- [joeygambino/MiniMax-H3-Multishot-Workflow](https://huggingface.co/joeygambino/MiniMax-H3-Multishot-Workflow) — 无缝链接工作流（v2.0），渲染多镜头场景为一个连续镜头
- ComfyUI 0.30.0+ 内置 Storyboard 模板

### 方案 3：H3 Motion Context 插件（推荐方案）

**这是目前社区公认最好的长视频方案。**

#### H3 Motion Context v0.2.0

- **原理**：利用 H3 可以在时间坐标上"钉住"帧并在每个采样步重新注入的能力
- **突破**：解除了 ComfyUI 原本只允许首帧/尾帧的限制，支持任意位置钉帧
- **音频延续**：携带上一段的音频上下文，下一段继续相同的音频而非重新合成
- **Latent 直通模式**：`context_latent` 直接从上一段的 latent 中切片，跳过解码→缩放→VAE 编码，无色彩偏移
- **上下文窗口**：支持 5、22、39、56 帧的上下文长度
- **兼容 R2V**：Ref2VA 图可以保留自己的图/视频/音频参考，同时启用链式延续

**推荐设置**：
```
context_length: 22
encode_mode: video
anchor_mode: head
audio_context_length: 22
Loop Trim: match_tail=true
Spectrum: off
```

#### ComfyUI-MiniMaxH3-Contex-Loop（ethanfel）

更进一步的自动化循环方案：

```
Plan → Loop Start → Current Shot → H3 条件化
    ↓
Contex Loop Context → 采样 → 解码 → Loop Trim
    ↓
Segment + Checkpoint → Review Gate → Loop End ──↺
    ↓
Loop End manifest → Assemble
```

- **Scene Plan**：用 JSON 可视化编辑器编排场景
- **Review Gate**：每段生成后可审查、重试
- **自动拼接**：`ffmpeg` 合并所有片段
- **PNG 序列导出**：无损导出完整帧序列
- **元数据保留**：每段保留 prompt、seed、checkpoint

**Scene Plan 示例**：
```json
{
  "prompt_prefix": "保持相同的表演者、服装和视觉风格。",
  "defaults": {
    "duration_seconds": 15,
    "steps": 20
  },
  "shots": [
    { "id": "intro", "prompt": "在电梯里的器乐开场。" },
    { "id": "street", "prompt": "继续走到外面的雨中。" }
  ]
}
```

### 方案 4：R2V 参考视频续拍（低 VRAM 友好）

**原理**：用上一段视频的最后几帧作为 R2V 的视频参考

- 仅使用前一段的**最后 5 帧**作为视频参考
- 大幅降低显存占用（8GB GPU 可用）
- 配合 `Frame Load Cap` 和 `Skip First Frames` 控制

---

## 四、Prompt 编写指南

### 结构化 Prompt（官方推荐）

```
SHOT 1 (0-5s): 全景锁定，蒸汽升腾，厨师将汤勺浸入黑色碗中，雨水从雨棚边缘滴落。
SHOT 2 (5-10s): 切至特写，汤勺突破汤面，金色油脂旋转，葱花缓慢飘落。
SHOT 3 (10-15s): 切至中景，厨师直视镜头，用日语疲惫微笑说：「一杯，请慢用」。
```

### 要点

1. **先描述整体场景**（地点、角色、事件），再用时间码分镜头
2. **镜头+摄像机+音频**写在同一个 prompt 块中
3. **对话**用 `<d>[语言+声音描述] 文本</d>` 格式
4. **音效**显式写出（SFX: 雨声、脚步声...）
5. **音乐**显式标注（music: 轻柔钢琴...）或写 `no music`
6. **R2V 模式**必须显式分配参考标签（如 `<Subject 1>`, `<Audio 1>`）

### 实用技巧

- **先用 LLM 扩写**：把简单想法喂给 GPT/Claude，让 LLM 按 H3 官方指南格式扩写为详细分镜 prompt
- **先低分辨率预览**：0.6 MP 5秒约 3.5~4 分钟；确认效果后再高分辨率正式生成
- **时间码格式**：`At 00:03.500, the camera cuts to...`

---

## 五、硬件需求与性能参考

### 显存占用

| 配置 | 说明 |
|------|------|
| **8 GB VRAM** | R2V 续拍方案可运行（仅用最后5帧参考） |
| **16 GB VRAM** | 混合工作流（T2V + I2V + R2V）可行 |
| **24 GB VRAM (3090/4090)** | 1 MP 生成，舒适运行 |
| **5090** | 最佳体验 |

### 生成速度参考（RTX 3090）

| 分辨率 | 时长 | 耗时 |
|--------|------|------|
| 0.6 MP | 5 秒 | ~3.5-4 分钟 |
| 0.6 MP | 10 秒 | ~7.5 分钟 |
| 1 MP | 14 秒 | ~40 分钟 |

### 加速方案

- **Sage Attention**：注意力加速
- **Spectrum Node**：H3 专用优化节点
- **EasyCache**：缓存加速
- **nvfp4 / GGUF 量化**：降低显存占用
- **fp16 原生**（V100 等）：比默认快约 11 倍，修复黑帧问题
- **8 步 Turbo 模式**：0.4 MP 约 3-4 分钟/段（5060Ti 16GB 实测）

### 上采样

- **RTX Super Resolution**：NVIDIA 硬件上采样
- **SeedVR2.5**：AI 视频上采样
- **Topaz Video**：专业视频增强
- **LTX Upscale**：LTX 模型上采样工作流
- **策略建议**：先低分辨率生成所有片段 → 最后统一上采样（节省大量时间）

---

## 六、长视频最佳实践

### 1. 先规划后生成
- 编写完整的 Scene Plan（场景表）
- 每段 prompt 用前缀共享视觉语言（角色、服装、风格）
- 用 `prompt_prefix` 统一描述，每段只写变化部分

### 2. 分辨率策略
- **草稿阶段**：全部用低分辨率（0.6 MP）生成
- **审查**：用 `preview_first_shot` 先看第一段效果
- **终稿**：确认后再高分辨率重出，或统一上采样

### 3. 接缝处理
- 优先使用 `context_latent`（Latent 直通）模式消除可见接缝
- `match_tail=true` 自动去除重复的开头上下文
- 必要时在视频编辑器中做转场过渡

### 4. 音频连续性
- H3 生成音画合一，链式拼接时音频也需要延续
- `audio_context_length` 设为与 `context_length` 相同
- 长链拼接可能丢失高频细节，音乐视频建议用 `source_track`

### 5. 一致性维护
- R2V 模式 + 参考图片锁定角色外观
- `ref_image_size=max` 保持 2048px 短边以增强身份保真度
- 跨段使用相同的 seed + prompt_prefix

---

## 七、社区资源索引

| 资源 | 链接 |
|------|------|
| **官方博客** | [minimax.io/blog/minimax-h3](https://www.minimax.io/blog/minimax-h3) |
| **HuggingFace 详解** | [huggingface.co/blog/ResterChed/minimax-h3-hailuo-3-0](https://huggingface.co/blog/ResterChed/minimax-h3-hailuo-3-0) |
| **ComfyUI 官方教程** | [docs.comfy.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-h3](https://docs.comfy.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-h3) |
| **H3 Motion Context** | [comfyui-wiki.com/en/news/2026-08-09-h3-motion-context-v0-2-0](https://comfyui-wiki.com/en/news/2026-08-09-h3-motion-context-v0-2-0) |
| **Contex Loop 插件** | [github.com/ethanfel/ComfyUI-MiniMaxH3-Contex-Loop](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Contex-Loop) |
| **Multishot Workflow** | [huggingface.co/joeygambino/MiniMax-H3-Multishot-Workflow](https://huggingface.co/joeygambino/MiniMax-H3-Multishot-Workflow) |
| **Prompt Guide (LLM)** | [github.com/ethanfel/ComfyUI-MiniMax-H3-Guide](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide) |
| **视频长度深度分析** | [atlascloud.ai/blog/tips/minimax-h3-video-length](https://www.atlascloud.ai/blog/tips/minimax-h3-video-length) |
| **Prompt 实战指南** | [xhinker.medium.com - MiniMax H3 Practical Prompt Guide](https://xhinker.medium.com/minimax-h3-become-the-director-of-any-video-a-practical-prompt-guide-94200a1905a8) |

### 视频教程
- [MiniMax H3 Infinite Video: Make 2-Hour Movies in ComfyUI (SECourses)](https://www.youtube.com/watch?v=1580ZDX-60Q)
- [How To Use MiniMax H3 in ComfyUI (MDMZ)](https://www.youtube.com/watch?v=d_wEd-fZcdg)
- [MiniMax H3 StoryBoard Workflow](https://www.youtube.com/watch?v=hoo8qCKDLbU)
- [ComfyUI MiniMax H3 Workflow Examples (Ep29)](https://www.youtube.com/watch?v=267y00jaOUc)
- [MiniMax H3 V2V + I2V on 8GB VRAM](https://www.youtube.com/watch?v=UJTBiqzZYRk)

---

## 八、总结

MiniMax H3 虽然单次生成上限为 15 秒，但通过社区开发的多种链式拼接技术，完全可以实现 **1 分钟甚至数小时**的连贯长视频。核心要点：

1. **H3 Motion Context / Contex Loop 是当前最佳方案**（Latent 直通 + 音频延续）
2. **Prompt 结构化编写**是质量基础（分镜头 + 时间码 + 音效描述）
3. **低分辨率预览 → 高分辨率出片 / 统一上采样**是效率关键
4. **R2V 参考模式**是保持跨段一致性的重要工具
5. 开源权重 + ComfyUI 本地运行，**零成本**（硬件除外）
