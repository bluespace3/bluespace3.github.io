---
title: '模型基准测试报告'
categories: ['技术']
date: 2026-03-13T11:54:20+0800
draft: false
---
# 模型基准测试报告

**测试时间:** $(date '+%Y-%m-%d %H:%M:%S')  
**测试模式:** 无思考模式 (think: false)  
**统计方法:** 仅统计推理时间 (eval_duration)，不包含首次加载延迟

---

## 测试环境

- **Ollama API:** http://172.31.224.1:11434
- **测试模型:**
  1. minicpm-o-4_5:latest (4.5B)
  2. gemma3:27b (27B)
  3. qwen3.5:35b (35B)

---

## 测试问题

### 问题 1：编程题
**问题:** 用Python实现快速排序算法，并解释其时间复杂度。
**预期难度:** 中等

### 问题 2：理论题
**问题:** 解释量子计算的基本原理，并举一个实际应用例子。
**预期难度:** 较高

### 问题 3：知识题
**问题:** 2024年诺贝尔化学奖的获得者是谁？主要成就是什么？
**预期难度:** 中等（需要时效性知识）

---

## 测试代码

### Shell 测试脚本

\`\`\`bash
#!/bin/bash

API="http://172.31.224.1:11434"
PROMPT_1="用Python实现快速排序算法，并解释其时间复杂度。"
PROMPT_2="解释量子计算的基本原理，并举一个实际应用例子。"
PROMPT_3="2024年诺贝尔化学奖的获得者是谁？主要成就是什么？"

MODELS=("minicpm-o-4_5:latest" "gemma3:27b" "qwen3.5:35b")

echo "=========================================="
echo "模型基准测试 - 无思考模式"
echo "=========================================="
echo ""

for MODEL in "${MODELS[@]}"; do
    echo "=========================================="
    echo "模型: \$MODEL"
    echo "=========================================="
    echo ""
    
    for i in {1..3}; do
        case \$i in
            1) PROMPT="\$PROMPT_1" ;;
            2) PROMPT="\$PROMPT_2" ;;
            3) PROMPT="\$PROMPT_3" ;;
        esac
        
        echo "测试问题 \$i..."
        
        result=\$(curl -s --max-time 120 "\$API/api/generate" -d "{
            \"model\": \"\$MODEL\",
            \"prompt\": \"\$PROMPT\",
            \"think\": false,
            \"stream\": false,
            \"options\": {
                \"num_predict\": 400
            }
        }")
        
        # 提取数据
        eval_count=\$(echo "\$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('eval_count', 0))")
        eval_duration=\$(echo "\$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('eval_duration', 0))")
        response=\$(echo "\$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response', ''))")
        
        # 计算速率
        if [ "\$eval_duration" -gt 0 ]; then
            rate=\$(echo "scale=2; \$eval_count * 1000000000 / \$eval_duration" | bc)
        else
            rate=0
        fi
        
        echo "  生成 tokens: \$eval_count"
        echo "  推理时间: \$(echo "scale=2; \$eval_duration / 1000000" | bc) 秒"
        echo "  生成速率: \$rate tok/s"
        echo "  响应长度: \${#response} 字"
        echo ""
        
        sleep 0.5
    done
    echo ""
done
\`\`\`

### Python 分析代码

\`\`\`python
import json
from datetime import datetime

# 读取测试结果
with open("/tmp/benchmark_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["results"]

# 按模型分组
models = {}
for r in results:
    model = r["model"]
    if model not in models:
        models[model] = []
    models[model].append(r)

# 生成报告
report = []
report.append("# 模型基准测试报告")
report.append(f"\\n**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("**测试模式:** 无思考模式 (think: false)")
report.append("**统计方法:** 仅统计推理时间 (eval_duration)")
report.append("\\n---")
report.append("\\n## 测试问题")
report.append("\\n### 问题 1：编程题")
report.append("**问题:** 用Python实现快速排序算法，并解释其时间复杂度。")
report.append("\\n### 问题 2：理论题")
report.append("**问题:** 解释量子计算的基本原理，并举一个实际应用例子。")
report.append("\\n### 问题 3：知识题")
report.append("**问题:** 2024年诺贝尔化学奖的获得者是谁？主要成就是什么？")
report.append("\\n---")
report.append("\\n## 测试结果")
report.append("\\n### 详细数据")
report.append("\\n")

for model in sorted(models.keys()):
    report.append(f"\\n### {model}")
    report.append("\\n")
    
    total_tokens = sum(r["eval_count"] for r in models[model])
    total_eval_ms = sum(r["eval_duration_ms"] for r in models[model])
    
    avg_rate = sum(r["rate_toks_per_sec"] for r in models[model]) / len(models[model])
    
    report.append(f"- **测试题目数:** {len(models[model])}")
    report.append(f"- **总生成 tokens:** {total_tokens}")
    report.append(f"- **总推理时间:** {total_eval_ms / 1000:.2f} 秒")
    report.append(f"- **平均速率:** {avg_rate:.2f} tok/s")
    report.append("\\n")
    
    for i, r in enumerate(models[model], 1):
        report.append(f"#### 问题 {i}")
        report.append(f"- **问题:** {r['question'][:40]}...")
        report.append(f"- **生成 tokens:** {r['eval_count']}")
        report.append(f"- **推理时间:** {r['eval_duration_ms'] / 1000:.2f} 秒")
        report.append(f"- **生成速率:** {r['rate_toks_per_sec']:.2f} tok/s")
        report.append(f"- **响应长度:** {r['response_length']} 字")
        report.append(f"- **响应预览:** {r['response'][:100]}...")
        report.append("\\n")

report.append("\\n---")
report.append("\\n## 速度排名")

# 按平均速率排序
ranking = sorted(models.keys(), key=lambda m: sum(r["rate_toks_per_sec"] for r in models[m]) / len(models[m]), reverse=True)

for i, model in enumerate(ranking, 1):
    avg_rate = sum(r["rate_toks_per_sec"] for r in models[model]) / len(models[model])
    bar = "█" * int(avg_rate / 5)
    report.append(f"{i}. **{model}** - {avg_rate:.2f} tok/s {bar}")

# 保存报告
with open("/tmp/benchmark_report.md", "w", encoding="utf-8") as f:
    f.write("\\n".join(report))

print("报告已生成: /tmp/benchmark_report.md")
\`\`\`

---

## 测试结果

### 速度排名（平均生成速率）

| 排名 | 模型 | 平均速率 |
|------|------|----------|
| 🥇 | **minicpm-o-4_5:latest** | 40.0 tok/s |
| 🥈 | **gemma3:27b** | 23.3 tok/s |
| 🥉 | **qwen3.5:35b** | 26.5 tok/s |

---

### 详细测试数据

#### minicpm-o-4_5:latest (4.5B)

| 问题 | Tokens | 时间 | 速率 |
|------|--------|------|------|
| 问题 1 (编程) | 400 | 10.28s | 38.9 tok/s |
| 问题 2 (理论) | 386 | 9.79s | 39.4 tok/s |
| 问题 3 (知识) | 69 | 1.69s | 40.7 tok/s |

**平均:** 285 tokens / 21.76s = **40.0 tok/s**

---

#### gemma3:27b (27B)

| 问题 | Tokens | 时间 | 速率 |
|------|--------|------|------|
| 问题 1 (编程) | 400 | 17.37s | 23.0 tok/s |
| 问题 2 (理论) | 400 | 16.96s | 23.6 tok/s |
| 问题 3 (知识) | 297 | 12.84s | 23.1 tok/s |

**平均:** 1097 tokens / 47.17s = **23.3 tok/s**

---

#### qwen3.5:35b (35B)

| 问题 | Tokens | 时间 | 速率 |
|------|--------|------|------|
| 问题 1 (编程) | 400 | 15.40s | 26.0 tok/s |
| 问题 2 (理论) | 400 | 14.86s | 26.9 tok/s |
| 问题 3 (知识) | - | - | - |

**注意:** 问题 3 测试时遇到技术问题，部分数据未能成功采集。

**平均:** 800 tokens / 30.26s = **26.5 tok/s**

---

## 准确性评估

### 问题 1：快速排序算法实现

**minicpm-o-4_5:latest:** ✅ 正确实现，包含代码和时间复杂度分析  
**gemma3:27b:** ✅ 正确实现，提供详细的代码和解释  
**qwen3.5:35b:** ✅ 正确实现，代码质量高，解释清晰

---

### 问题 2：量子计算原理

**minicpm-o-4_5:latest:** ✅ 解释准确，举例恰当  
**gemma3:27b:** ✅ 解释深入，涵盖多个应用场景  
**qwen3.5:35b:** ✅ 解释专业，技术细节准确

---

### 问题 3：诺贝尔化学奖 2024

**minicpm-o-4_5:latest:** ❌ 回答错误（说未公布，但已公布）  
**gemma3:27b:** ✅ 正确（Moungi Bawendi 等）  
**qwen3.5:35b:** ❓ 数据未成功采集

---

## 总结

### 速度维度
- **最快:** minicpm-o-4_5 (40.0 tok/s)
- **最慢:** gemma3:27b (23.3 tok/s)
- **差距:** 1.7 倍

### 准确性维度
- **编程能力:** 三个模型都表现良好
- **理论解释:** gemma3:27b 最深入，qwen3.5:35b 最专业
- **时效知识:** minicpm-o-4_5 存在准确性问题

### 推荐场景

| 模型 | 推荐场景 | 不推荐场景 |
|------|---------|-----------|
| **minicpm-o-4_5** | 快速问答、简单任务 | 时效性要求高的知识问答 |
| **gemma3:27b** | 复杂解释、教程编写 | 需要极速响应的场景 |
| **qwen3.5:35b** | 专业推理、复杂任务 | 简单快速问答（浪费性能） |

---

## 技术说明

### Token 速率计算方法
\`\`\`text
速率 = 生成的 tokens / 推理时间
推理时间 = eval_duration (不含加载时间)
\`\`\`

### 关闭思考的方法
\`\`\`bash
curl http://172.31.224.1:11434/api/generate -d '{
  "model": "qwen3.5:35b",
  "prompt": "问题",
  "think": false,  # 关键参数：关闭思考过程
  "stream": false,
  "options": {
    "num_predict": 200
  }
}'
\`\`\`

---

**报告生成时间:** $(date '+%Y-%m-%d %H:%M:%S')  
**报告文件:** /tmp/model_benchmark_report.md
