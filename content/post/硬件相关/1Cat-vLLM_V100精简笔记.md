---
title: '1Cat-vLLM_V100精简笔记'
categories: ["硬件相关"]
date: 2026-03-25T02:31:13+08:00
lastmod: 2026-04-08T23:32:29+08:00
draft: false
---
# 1Cat-vLLM V100 部署笔记

**硬件:** Tesla V100-SXM2-32GB | **模型:** Qwen3.5-35B-A3B-AWQ (MoE, AWQ 4bit)

---

## 一、构建镜像

```bash
# 1. 克隆项目
git clone https://github.com/1CatAI/1Cat-vLLM.git E:/AI/1Cat-vLLM

# 2. 关键修复 (docker/Dockerfile.sm70-wheel)
# - wheel URL: v0.0.3 → v0.0.2
# - 添加 python3-dev
# - PyTorch: --index-url https://download.pytorch.org/whl/cu128
# - 添加 sed -i 's/\r$//' 处理 CRLF

# 3. 启用多模态 (docker/entrypoint.sm70.sh)
default_mm_limits='{"image":1,"video":0}'  # 改为 image:1

# 4. 构建
cd E:\AI\1Cat-vLLM
docker build -f docker/Dockerfile.sm70-wheel -t 1cat-vllm-sm70:0.0.2 .
```

---

## 二、启动容器

```bash
docker run --rm --name vllm --gpus all --ipc=host -p 8000:8000 \
  -v E:/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:/models:ro \
  -e VLLM_MODEL=/models/Qwen3.5-35B-A3B-AWQ \
  -e VLLM_SERVED_MODEL_NAME=Qwen3.5-35B-A3B-AWQ \
  -e VLLM_TENSOR_PARALLEL_SIZE=1 \
  -e VLLM_GPU_MEMORY_UTILIZATION=0.90 \
  -e VLLM_MAX_MODEL_LEN=32768 \
  -e VLLM_MAX_NUM_SEQS=2 \
  1cat-vllm-sm70:0.0.2
```

---

## 三、API 调用

### 禁用思考模式
```json
{"chat_template_kwargs": {"enable_thinking": false}}
```

### 图片识别 (Base64)
```json
{
  "type": "image_url",
  "image_url": {"url": "data:image/png;base64,<base64_data>"}
}
```

---

## 四、性能结果

| 测试项 | 速度 |
|--------|------|
| 长文本 (500 tok) | 75 tok/s |
| 代码生成 (800 tok) | 77 tok/s |
| 知识讲解 (400 tok) | 80 tok/s |
| **平均** | **~74 tok/s** |

**多模态:** ✅ 图片识别成功

---

## 五、常见问题

| 问题 | 解决 |
|------|------|
| 思考模式关不掉 | 请求加 `chat_template_kwargs: {"enable_thinking": false}` |
| 图片无法识别 | entrypoint 改 `default_mm_limits='{"image":1,"video":0}'` |
| CRLF 错误 | Dockerfile 加 `sed -i 's/\r$//'` |
| JSON 格式破坏 | 用 entrypoint 默认值，不用环境变量 |
