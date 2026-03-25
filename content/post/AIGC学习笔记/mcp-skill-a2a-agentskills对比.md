---
title: 'mcp-skill-a2a-agentskills对比'
categories: ["AIGC学习笔记"]
date: 2026-03-06T01:24:07+08:00
lastmod: 2026-03-25T13:02:09+08:00
draft: false
---
## MCP

特点：一种协议、可供ai复用的工具（与functioncalling非包含关系，但是可以利用大模型的 Function Calling 能力来触发工具调用）服务，可以视为一种大模型使用的sdk。

本质：供大模型使用的工具集服务。

1. 类比

![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/ff88ae4c-8773-4557-ae09-3b4395b0fdd5.png)

2. 有无用mcp的对比

![image.png](https://nextcloud.skyspace.eu.org/index.php/s/68iPdkSFrktBmjw/preview)

3. 工作流程

![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/f9ec0be1-5efb-42e1-b63d-f5a8805cf23c.png)

3. 通信协议

   ![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/6600b3e8-9a70-4af0-a18b-41e42a40be01.png)

## A2A

本质：agent与agent之间的通信标准（目前尚不成熟）


## skills

本质：文件夹，给模型用的包含提示词+工具脚本

1. 要解决的问题：

- 上下文爆炸。
- 经验断层
- 平台锁定

2. 结构标准：

![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/ee64e113-bea9-45f0-800b-194e13850248.png)

3. 与mcp对比：![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/6a2eb590-09e0-4dee-9a7a-0b2e06e1bab9.png)

3. 防止注入

![image.png](https://cdn.jsdelivr.net/gh/bluespace3/note-gen-image-sync@main/1549690d-ed0e-4e3d-b9ec-be2083d27094.png)
