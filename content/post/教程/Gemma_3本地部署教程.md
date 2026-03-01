---
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
---
---
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
title: 'Gemma_3本地部署教程'
categories: ["教程"]
date: 2025-09-07T00:20:45+08:00
lastmod: 2025-09-07T00:20:45+08:00
encrypted: false
Gemma 3 被谷歌称为目前最强的开源视觉模型之一。 该模型支持超过35种语言，能够分析文本、图像和短视频。值得注意的是，Gemma 3 的视觉编码器经过升级，支持高分辨率和非方形图像，并引入了 ShieldGemma 2 图像安全分类器，用于过滤被分类为性暗示、危险或暴力的内容。这些特性使得 Gemma 3 成为当前最强大的开源视觉模型之一。

#### 最新的 Gemma 3 多模态开源模型新功能


使用世界上最好的单加速器模型进行构建： Gemma 3 以其尺寸提供最先进的性能，在 LMArena 排行榜的初步人类偏好评估中胜过 Llama3-405B、DeepSeek-V3 和 o3-mini。这可以帮助您创建可安装在单个 GPU 或 TPU 主机上的引人入胜的用户体验。
以 140 种语言走向全球：构建使用客户语言的应用程序。Gemma 3 提供对超过 35 种语言的开箱即用支持和对超过 140 种语言的预训练支持。
打造具备高级文本和视觉推理能力的AI：轻松构建分析图片、文本、短视频等应用，开启交互智能化新可能1。
使用扩展的上下文窗口处理复杂任务： Gemma 3 提供 128k 令牌上下文窗口，让您的应用程序处理和理解大量信息。
使用函数调用创建 AI 驱动的工作流程： Gemma 3 支持函数调用和结构化输出，以帮助您自动执行任务并构建代理体验。
通过量化模型更快地实现高性能： Gemma 3 引入了官方量化版本，减少了模型大小和计算要求，同时保持了高精度。

本地安装，单显卡可以选择1b，4b，12b，27b，推荐选择27b，因为Gemma 3 27B 处于帕累托最佳点.

#### **本地部署Gemma 3开源大模型：**


1、下载官方 Ollama 【 **[点击前往](https://ollama.com/)** 】 ，并通过下方的安装命令执行下载：

普通用户建议选择4b和12b，显卡好的可以上27b

```
ollama run gemma3:1b
ollama run gemma3:4b
ollama run gemma3:12b
ollama run gemma3:27b
```

2、通过Cherry Studio,添加本地大模型后使用
![Gemma3本地部署教程_1743944257267](/images/Gemma3本地部署教程_1743944257267.png)