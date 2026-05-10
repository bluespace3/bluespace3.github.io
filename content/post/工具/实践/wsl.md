---
title: 'wsl'
categories: ["工具"]
date: 2026-01-14T19:53:18+08:00
lastmod: 2026-04-10T01:57:39+08:00
draft: false
---
账号：dministrator

密码：123456

激活py虚拟环境：source vllm_env/bin/activate

vllm运行大模型：vllm serve .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-14B-GPTQ-Int4
--trust-remote-code
--max-model-len 65536
--gpu-memory-utilization 0.95
--tensor-parallel-size 1
--max-num-seqs 1

vllm serve .xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-VL-8B-Instruct
--trust-remote-code
--max-model-len 65536
--gpu-memory-utilization 0.95
--tensor-parallel-size 1
--max-num-seqs 1

