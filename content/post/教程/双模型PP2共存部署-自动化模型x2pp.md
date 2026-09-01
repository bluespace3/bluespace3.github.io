---
title: '双模型PP2共存部署-自动化模型x2pp'
categories: ["教程"]
date: 2026-09-02T00:14:01+08:00
lastmod: 2026-09-02T00:14:01+08:00
draft: false
---

# 双模型 PP2 共存部署：BU-30B + AutoGLM 各自跨双卡（自动化模型x2pp）

在双 CMP 170HX（各 64GB）上让 BU-30B-A3B（browser-use 模型）与 AutoGLM-Phone-9B（手机 agent 模型）**同时常驻，且都跑 PP2 流水线并行**——两个 vLLM 实例各自把模型切层跨双卡。最终形态打包为 systemd 服务 `automodels-x2pp`，纳入启动器交互与开机自启管理。

## 1. 显存账（共存的核心）

vLLM 的 `--gpu-memory-utilization` 是"本实例在整卡上的预算上限"，且**启动时要求空闲显存 ≥ 预算值，KV cache 会把预算吃满**（不是只占权重大小）。因此共存的关键是**预算之和 ≤ 1.0**，按各家真实需求分配：

| 实例 | util | 每卡占用 | 构成 |
|---|---|---|---|
| BU-30B PP2 | 0.60 | 38GB | 权重 16GB + KV ~20GB |
| AutoGLM PP2 | 0.25 | 15.8GB | 权重 5.5GB + KV ~5GB |
| 合计 | 0.85 | ~50GB/64GB | 留 15% 余量 |

试错记录：初版 0.62+0.80 直接超卡被 `Free memory (49.48GiB) < desired utilization (50.71GiB)` 拒启；且 vLLM 会把 KV 撑满预算（AutoGLM 0.62 时 KV 被撑到 28GB/卡），必须按预算和算，不能按权重大小估。

**启动顺序必须先小后大**：先 AutoGLM 落卡，再启 BU-30B；反序则第二家撞"空闲<预算"被拒。

## 2. 单发速度实测：共存零损失

同基准脚本（9 reps 中位数）对比 PP2 独占（util 0.95）：

| prompt 长度 | 独占 prefill / decode | 共存 prefill / decode |
|---|---|---|
| 1.4k tok | 6089 / 114.1 | 6226 / 114.3 |
| 5.6k tok | 7057 / 110.5 | 7056 / 110.7 |
| 22.2k tok | 6986 / 98.8 | 7228 / 99.0 |

**结论：单发 prefill/decode 与 util 无关，完全持平**（计算量不变，KV 缩小只影响并发容量：22k 上下文并发数约减半）。两模型同时高负载才会互相抢 SM，单路场景零冲突。

## 3. PP 兼容性差异（两模型对比）

- **BU-30B（Qwen3-VL MoE）**：text_config 缺 `architectures` 且 model_type `qwen3_vl_moe_text` 不在 transformers 映射表 → PP 必崩，需给 config.json 补 `"architectures": ["Qwen3MoeForCausalLM"]`（备份 .bak-pp-fix）
- **AutoGLM（Glm4v）**：vLLM 0.24 的 `glm4_1v.py` 内部已对 `glm4v` model_type 显式指定 `architectures=["Glm4ForCausalLM"]` → **PP 开箱即用，无需改 config**

## 4. systemd 打包（automodels-x2pp.service）

wrapper 脚本 `start-automodels-x2pp.sh` 编排两实例，主进程=BU-30B：

```
等双卡清空(防旧实例退出竞态, ≤120s)
→ 后台拉 AutoGLM PP2
→ 等 :8003 /v1/models 就绪(硬信号, ≤300s; 拿不到 exit 1)
→ exec BU-30B PP2 为主进程
```

- **09-02 竞态修复**：初版用"GPU0>15GB"启发式判断 AutoGLM 落卡，切换场景下旧实例退出慢，AutoGLM 撞残留显存静默死亡（`No available memory for the cache blocks`）而主进程无感。改为等端口就绪为准 + 开头等 GPU 清空
- 停止：systemd 杀整个 cgroup 两模型同退；8002 瘦身代理幂等，下次启动自拉
- 端口守卫：ExecStartPre 检查 :8001/:8003 空闲，防双实例

## 5. 启动器集成（model-launcher.sh）

- `m) 自动化模型x2pp`：停互斥托管服务（bu30b/flashnext）+ 手动实例兜底清理 → `systemctl start automodels-x2pp --no-block`
- `f) 服务管理`：ALL_UNITS 列表加入 `automodels-x2pp`，与 flashnext/bu30b 同权管理（启停/自启/互斥切换，`e)` 一键切自启归属支持 `[x]2pp`）
- 状态页自动识别：`:8001` 与 `:8003` 均标注 `[systemd: automodels-x2pp]`
- `x) 一键退出`：cgroup 识别路由 systemctl stop，与单模型一致

## 6. 验收清单（09-02 全过）

- 双模型文本冒烟：BU-30B "ok" ✓ / AutoGLM 正常回复 ✓
- 视觉跨卡（绿底白字图）：两模型均正确识别 ✓
- 8002 瘦身代理转发 ✓
- `m)` 切换 → systemd 托管 → 双就绪 ~200s ✓
- 自启互斥：automodels-x2pp=enabled，bu30b/flashnext=disabled ✓

## 7. 运维速查

```bash
systemctl status automodels-x2pp        # 双模型总状态
journalctl -u automodels-x2pp -f        # wrapper+BU30B 日志
sudo systemctl stop automodels-x2pp     # 两模型一起停
# 切回单模型: 启动器 x) 全停 → f) 启 bu30b (或反向)
```

端口：8001=BU-30B，8003=AutoGLM 直连，8002=AutoGLM 瘦身代理（手机 agent 用）。

---

*2026-09-02。机器：双 CMP 170HX 64GB；vLLM 0.24.0（/root/cmp170hx-bench/venv，Marlin 补丁 L104 在位）。上篇：《BU-30B PP2 对比单卡实测》——本篇的独占基线数据来自该文。*
