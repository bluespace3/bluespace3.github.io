---
title: 'wsl'
categories: ["实践"]
date: 2026-01-15T23:25:17+08:00
lastmod: 2026-01-15T23:25:17+08:00
encrypted: false
---
title: 'wsl'
categories: ["实践"]
date: 2026-01-15T23:25:17+08:00
lastmod: 2026-01-15T23:25:17+08:00
encrypted: false
title: 'wsl'
categories: ["实践"]
date: 2026-01-15T23:25:17+08:00
lastmod: 2026-01-15T23:25:17+08:00
encrypted: false
title: 'wsl'
categories: ["实践"]
date: 2026-01-15T23:25:17+08:00
lastmod: 2026-01-15T23:25:17+08:00
encrypted: false
title: 'wsl'
categories: ["实践"]
date: 2026-01-15T23:25:17+08:00
lastmod: 2026-01-15T23:25:17+08:00
encrypted: false
账号：dministrator

密码：123456

激活py虚拟环境：source vllm_env/bin/activate

vllm运行大模型：vllm serve .cache/modelscope/hub/models/JunHowie/Qwen3-14B-GPTQ-Int4
--trust-remote-code
--max-model-len 65536
--gpu-memory-utilization 0.95
--tensor-parallel-size 1
--max-num-seqs 1

vllm serve .cache/modelscope/hub/models/Qwen/Qwen3-VL-8B-Instruct
--trust-remote-code
--max-model-len 65536
--gpu-memory-utilization 0.95
--tensor-parallel-size 1
--max-num-seqs 1

