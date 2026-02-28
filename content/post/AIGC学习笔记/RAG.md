---
title: 'RAG'
categories: ["AIGC学习笔记"]
date: 2025-12-04T19:41:12+08:00
lastmod: 2025-12-04T19:41:12+08:00
encrypted: false
---
title: 'RAG'
categories: ["AIGC学习笔记"]
date: 2025-12-04T19:41:12+08:00
lastmod: 2025-12-04T19:41:12+08:00
encrypted: false
title: 'RAG'
categories: ["AIGC学习笔记"]
date: 2025-12-04T19:41:12+08:00
lastmod: 2025-12-04T19:41:12+08:00
encrypted: false
title: 'RAG'
categories: ["AIGC学习笔记"]
date: 2025-12-04T19:41:12+08:00
lastmod: 2025-12-04T19:41:12+08:00
encrypted: false
**RAG定义**：模型的外挂知识库，解决专业领域的知识检索；可以将用户的问题与知识库检索内容结合成提示词，发给大模型给出结果。

![image.png](/assets/674a7cce-9e56-471c-ab09-185017d061ba.png)

PDF/PPT：使用Layout Parsing提取文本、表格、图片
图片理解：调用MiniCPM-V2模型生成图表描述（如"2018-2023年电信业务收入趋势图"）

**RAG的步骤**：

1. 文档分块
2. 文档向量化-》（由嵌入模型转成稠密向量-适合语义搜索）文本块向量
3. 存储
4. 检索
5. 增强生成

**检索**

1.使用关键字检索，打分，归一化

2.使用向量相似度检索，打分，归一化

3.总分=权重1x关键字检索分+权重2x向量检索分；取前n条数据
