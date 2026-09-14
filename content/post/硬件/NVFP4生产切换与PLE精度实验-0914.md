---
title: 'NVFP4生产切换与PLE精度实验-0914'
categories: ["硬件"]
date: 2026-09-15T00:05:08+08:00
lastmod: 2026-09-15T00:05:08+08:00
draft: false
---
# NVFP4 生产切换 + PLE 精度实验（2026-09-14 深夜定稿）

> 承接《NVFP4-W4A16-vs-AWQ-AB实测-TEP2-MTP6-0914.md》。本篇：① A 侧热态补测 ② BF16 原版 PLE 表实验 ③ 生产栈正式切换 NVFP4 + 踩坑。

## 一、A 侧（AWQ）社区口径热态补测

同口径（原生 262144 无 YaRN、thinking 开、社区采样、out≤50000）：

| 档位 | 态 | cli_prefill | decode(客户端) | eng_gen | TTFT | MAL |
|---:|---|---:|---:|---:|---:|---:|
| 32K | 冷 | 596.1 | 91.8 | 77.7 | 54.2s | 3.06 |
| 64K | 冷 | 887.2 | 93.2 | 78.8 | 73.4s | 3.11 |
| 64K | 热 | 520.3 | 100.0 | 75.1 | 125.1s | 3.00 |

热态 prefill 反而更差（TTFT 125s）⇒ 早前猜测的"冷编译污染"不成立，A 侧社区口径 prefill 就是 500-900 t/s 波动区间。decode 三态稳定 92-100。
对照 B（NVFP4 同口径）：32K prefill 798 / 64K 2213；decode 引擎中位 180.5。
**终版差距：prefill B +34%~+150%（同口径中档），decode B ×2.1，TTFT B 好 25-60%。**

## 二、PLE 换 BF16 原版表实验 —— 否决，保持 FP8

混合目录组装（NVFP4 权重硬链接 + AWQ 的 128 个 BF16 shard 流式抽取成 10 个分片 + index 改写删 weight_scale），抽样 sha256 与源逐字节一致。脚本 `/mnt/nvme0/qwen-flash-data/build_bf16ple_hybrid.py`（注意 safetensors 必须两遍法写 header，第一版单遍回填覆盖数据头，核验抓出）。

| 档位 | 指标 | FP8 表(51G, 现用) | BF16 表(95.4G) | Δ |
|---|---|---:|---:|---|
| 32K | decode 引擎中位 | 180.5 | 180.0 | 持平 |
| 32K | prefill(TTFT口径) | 798 | 479 | **−40%** |
| 32K | TTFT | 40.5s | 67.5s | 差27s |
| 64K | prefill | 2213 | 868 | **−61%** |
| 64K | TTFT | 29.4s | 75.0s | 差46s |
| 64K | MAL | 4.25 | 4.01 | −6% |

机理：102G 表 > 60G RAM，prefill 期 PLE gather 大量 page fault；decode 不受影响（MTP 接受率与 PLE 精度无关，精度→草稿质量假设证伪）。与 09-04 AWQ/MTP3 时代"BF16 甜区+13~32%"结论相反——栈形态(MTP6 gather 频率×7)不同不可迁移。**结论：NVFP4 栈配 FP8 表是最优组合。**
实验目录 `Qwen3.8-Flash-Next-NVFP4-BF16PLE`（实占 97G）待处置。

## 三、生产切换：flashnext.service → NVFP4

- **启动器** `/mnt/nvme0/qwen-flash-data/start-nvfp4-prod.sh [chunk] [spec] [maxlen]`：TEP2+EP、Marlin、MTP6 localargmax、mmap FP8 PLE、开机闸门、8000 端口 + 27B 别名（客户端零改动）
- **systemd**：drop-in `60-nvfp4-prod.conf`（字母序覆盖 50-ple-fix 的 ExecStart），保留 RAM 闸门/MemoryMax=32G/Restart=always/170tune 时序；`enabled` 开机自启
- **默认 524288+YaRN2.0**（保 512K 能力）；原生 262144 更快但砍长窗口
- **回滚一行**：`sudo rm /etc/systemd/system/flashnext.service.d/60-nvfp4-prod.conf && sudo systemctl daemon-reload && sudo systemctl restart flashnext`
- 验证：active、models 三别名、max_len 524288、`Using 'MARLIN' NvFp4 MoE backend`、冒烟正常、MemoryCurrent 26G/32G

### 踩坑：--hf-overrides 对 quantization_config 是整块替换
想把模型目录还原社区原版、W4A16 声明走命令行注入：
```
ValidationError: Quantization method in model config (None) does not match (modelopt_fp4)
```
hf-overrides 的 `quantization_config` 不做深合并，注入块覆盖后丢了 `quant_method: modelopt` 和 `ignore`(13条) ⇒ vLLM 认不出量化方法。
**正解（现状）**：config.json 用 W4A16 声明版（quant_method + quant_algo=W4A16_NVFP4 + input_activations:null + ignore 齐全）；原版备份 `.orig-metadata-w4a4/`（config e765305d… 与社区钉值一致）。hf_quant_config.json 保持原版——vLLM 在 config.json 已有 quantization_config 时根本不读它。

## 四、遗留
- [ ] BF16PLE 混合目录 97G 去留（等用户）
- [ ] MemoryMax 32G→48G（FP8 表 51G 驻留更充分，等用户）
- [ ] 500K prefill 断崖（B 栈 1510 t/s vs 中档 ~5000）未查
- [ ] 社区 env 层优化 Q38_TP_PLE/Q38_HC_GEMV 移植：架构不适用（见迁移卡 0914 节），HC_GEMV 需 M≤8 扩展+拆融合算子，成本>收益
