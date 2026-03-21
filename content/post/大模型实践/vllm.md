---
title: 'vllm'
categories: ["大模型实践"]
date: 2026-03-21T17:02:14+08:00
lastmod: 2026-03-21T17:37:10+08:00
draft: false
---
source 1cat-vllm/bin/activate

python -m vllm.entrypoints.openai.api_server \  
  --model ~\Qwen3.5-35B-A3B-AWQ \  
  --quantization awq \  
  --dtype float16 \  
  --gpu-memory-utilization 0.9 \  
  --max-model-len 65536 \  
  --tensor-parallel-size 1 \  
  --max-num-seqs 4 \  
  --max-num-batched-tokens 2048 \  
  --attention-backend TRITON_ATTN \  
  --compilation-config '{"cudagraph_mode":"full_and_piecewise","cudagraph_capture_sizes":[1]}' \  
  --host xxx.xxx.xxx.xxx \  
  --port 8000