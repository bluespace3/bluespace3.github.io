---
title: '1Cat-vLLM_V100部署与使用笔记'
categories: ["硬件相关"]
date: 2026-03-25T02:31:13+08:00
lastmod: 2026-03-25T02:31:13+08:00
draft: false
---
# 1Cat-vLLM 在 V100 上的部署与使用笔记

**日期:** 2026-03-25
**硬件:** Tesla V100-SXM2-32GB
**模型:** Qwen3.5-35B-A3B-AWQ (MoE, AWQ 4-bit)
**项目:** https://github.com/1CatAI/1Cat-vLLM

---

## 一、项目简介

1Cat-vLLM 是 vLLM 的 fork 版本，专门优化用于 **SM70 架构 (Tesla V100)**，支持：
- AWQ 4-bit 量化推理
- Qwen3.5 Dense 和 MoE 模型
- 长上下文支持
- 多模态（图片识别）

---

## 二、环境准备

### 2.1 硬件要求
- GPU: Tesla V100 (16GB/32GB)
- 显存: 建议 32GB 单卡或双卡 16GB
- 驱动: CUDA 12.8

### 2.2 软件要求
- Windows 11 + WSL2 或 Docker Desktop for Windows
- Python 3.12
- Git

---

## 三、构建 Docker 镜像

### 3.1 克隆项目

```bash
git clone https://github.com/1CatAI/1Cat-vLLM.git E:/AI/1Cat-vLLM
cd E:/AI/1Cat-vLLM
```

### 3.2 修复 Dockerfile

**文件:** `docker/Dockerfile.sm70-wheel`

**关键修改：**
1. 修复 wheel URL 版本号 (v0.0.3 → v0.0.2)
2. 添加 Python 开发包 (`python3-dev`)
3. 添加 CRLF 转换（Windows 行尾符问题）
4. 指定 CUDA 版本的 PyTorch (`--index-url https://download.pytorch.org/whl/cu128`)

**修改后的关键部分：**
```dockerfile
FROM python:3.12-slim-trixie

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    VLLM_NO_USAGE_STATS=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash ca-certificates curl gcc g++ git \
        libgl1 libglib2.0-0 libgomp1 python3-dev tini \
    && rm -rf /var/lib/apt/lists/*

ARG TORCH_VERSION=2.9.1
ARG VLLM_WHEEL_URL="https://github.com/1CatAI/1Cat-vLLM/releases/download/v0.0.2/vllm-0.0.2.dev0+g55573923a.d20260321.cu128-cp312-cp312-linux_x86_64.whl"

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --index-url https://download.pytorch.org/whl/cu128 \
        torch==${TORCH_VERSION} \
        torchvision==0.24.1 \
        torchaudio==2.9.1 \
    && python -m pip install "${VLLM_WHEEL_URL}"

COPY docker/entrypoint.sm70.sh /usr/local/bin/entrypoint.sm70.sh
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sm70.sh && chmod +x /usr/local/bin/entrypoint.sm70.sh

WORKDIR /workspace
EXPOSE 8000
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sm70.sh"]
```

### 3.3 启用多模态（修改 entrypoint.sm70.sh）

**文件:** `docker/entrypoint.sm70.sh`

修改默认值为启用图片支持：
```bash
default_compilation='{"cudagraph_mode":"full_and_piecewise","cudagraph_capture_sizes":[1]}'
default_mm_limits='{"image":1,"video":0}'  # 改为 image:1
```

### 3.4 构建镜像

```bash
cd E:\AI\1Cat-vLLM
docker build -f docker/Dockerfile.sm70-wheel -t 1cat-vllm-sm70:0.0.2 .
```

**构建时间:** 约 10-15 分钟（首次下载 PyTorch 和 CUDA 库）

---

## 四、启动容器

### 4.1 基础启动命令

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

### 4.2 参数说明

| 参数 | 说明 |
|------|------|
| `--gpus all` | 使用所有 GPU |
| `--ipc=host` | 共享主机内存，提高性能 |
| `-p 8000:8000` | 端口映射 |
| `-v ...:/models:ro` | 挂载模型目录（只读）|
| `VLLM_GPU_MEMORY_UTILIZATION` | GPU 内存使用率 (0.90 = 90%) |
| `VLLM_MAX_MODEL_LEN` | 最大上下文长度 |
| `VLLM_MAX_NUM_SEQS` | 最大并发请求数 |

### 4.3 双卡配置

如果有双 V100 16GB：
```bash
docker run --rm --name vllm --gpus all --ipc=host -p 8000:8000 \
  -v E:/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:/models:ro \
  -e VLLM_MODEL=/models/Qwen3.5-35B-A3B-AWQ \
  -e VLLM_TENSOR_PARALLEL_SIZE=2 \
  -e VLLM_GPU_MEMORY_UTILIZATION=0.90 \
  -e VLLM_MAX_MODEL_LEN=262144 \
  -e VLLM_MAX_NUM_SEQS=2 \
  1cat-vllm-sm70:0.0.2
```

---

## 五、API 调用

### 5.1 健康检查

```bash
curl http://localhost:8000/health
```

### 5.2 文本对话（禁用思考模式）

**请求示例：**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-35B-A3B-AWQ",
    "messages": [{"role": "user", "content": "你好，请简短回答"}],
    "max_tokens": 100,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
```

**关键参数：**
- `chat_template_kwargs: {"enable_thinking": false}` - 禁用思考模式

### 5.3 图片识别（多模态）

**方法：使用 Base64 编码**

```powershell
# PowerShell 脚本
$imgPath = "C:\path\to\image.png"
$base64 = [Convert]::ToBase64String([System.IO.File]::ReadAllBytes($imgPath))

$body = @{
    model = "Qwen3.5-35B-A3B-AWQ"
    messages = @(
        @{
            role = "user"
            content = @(
                @{ type = "text"; text = "请描述这张图片" }
                @{ type = "image_url"; image_url = @{ url = "data:image/png;base64,$base64" } }
            )
        }
    )
    max_tokens = 400
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:8000/v1/chat/completions" `
  -Method Post -Body $body -ContentType "application/json"
```

**JSON 格式：**
```json
{
  "model": "Qwen3.5-35B-A3B-AWQ",
  "messages": [{
    "role": "user",
    "content": [
      { "type": "text", "text": "请描述这张图片" },
      { "type": "image_url", "image_url": { "url": "data:image/png;base64,<base64_data>" } }
    ]
  }],
  "max_tokens": 400
}
```

---

## 六、性能测试结果

### 6.1 测试环境
- GPU: Tesla V100-SXM2-32GB
- 模型: Qwen3.5-35B-A3B-AWQ (AWQ 4-bit)
- 思考模式: 已禁用

### 6.2 性能数据（3次测试平均）

| 测试项 | Tokens | 耗时 | 速度 | 首字延迟 |
|--------|--------|------|------|----------|
| 长文本生成 (500 tok) | 500 | 6.7秒 | **75.00 tok/s** | 27 ms |
| 代码生成 (800 tok) | 800 | 10.3秒 | **77.42 tok/s** | 26 ms |
| 技术分析 (500 tok) | 500 | 6.3秒 | **78.95 tok/s** | 25 ms |
| 日常对话 (100 tok) | 100 | 1.7秒 | **60.00 tok/s** | 33 ms |
| 知识讲解 (400 tok) | 400 | 5.0秒 | **80.00 tok/s** | 25 ms |

**综合平均速度:** ~74 tok/s

### 6.3 图片识别测试

✅ **成功识别** Windows CMD 界面中的 nvidia-smi 输出
- 准确识别了命令行界面
- 理解了 `nvidia-smi` 命令的用途
- 解读了显卡状态信息的含义

---

## 七、常见问题

### 7.1 思考模式无法禁用

**解决方案：** 在请求中添加 `chat_template_kwargs: {"enable_thinking": false}`

### 7.2 图片无法识别

**错误：** `At most 0 image(s) may be provided`

**原因：** entrypoint 默认禁用了多模态

**解决方案：** 修改 entrypoint.sm70.sh 中的 `default_mm_limits='{"image":1,"video":0}'`

### 7.3 Windows 行尾符问题

**错误：** `/usr/bin/env: 'bash\r': No such file or directory`

**解决方案：** 在 Dockerfile 中添加 `sed -i 's/\r$//'` 处理

### 7.4 JSON 格式被破坏

**问题：** PowerShell 环境变量会破坏 JSON 双引号

**解决方案：** 将参数放在 entrypoint 脚本默认值中，而不是通过环境变量传递

---

## 八、参考链接

- 项目地址: https://github.com/1CatAI/1Cat-vLLM
- vLLM 文档: https://docs.vllm.ai/
- Qwen3.5 模型: https://huggingface.co/Qwen

---

**记录人:** Claude AI
**最后更新:** 2026-03-25
