---
title: 'vllm'
categories: ["硬件相关"]
date: 2026-03-25T00:48:38+08:00
lastmod: 2026-03-25T00:48:38+08:00
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

 

docker run --rm --gpus all --ipc=host -p 8000:8000 -v E:/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:/models:ro -e

  VLLM_MODEL=/models/Qwen3.5-35B-A3B-AWQ -e VLLM_SERVED_MODEL_NAME=Qwen3.5-35B-A3B-AWQ -e VLLM_TENSOR_PARALLEL_SIZE=1 -e

   VLLM_GPU_MEMORY_UTILIZATION=0.90 -e VLLM_MAX_MODEL_LEN=32768 -e VLLM_MAX_NUM_SEQS=2 1cat-vllm-sm70:0.0.2