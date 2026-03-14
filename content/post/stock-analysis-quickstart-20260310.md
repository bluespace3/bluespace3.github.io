---
title: 'stock-analysis-quickstart-20260310'
categories: ["stock-analysis-quickstart-20260310.md"]
date: 2026-03-10T03:00:01+08:00
lastmod: 2026-03-10T03:00:01+08:00
draft: false
---
# 股票技术面分析 - 快速开始指南

**日期:** 2026-03-10
**目标:** 5 分钟内开始使用 OpenClaw 进行技术面分析

---

## 🚀 三种方式快速开始

### 方式 1: 直接使用 OpenClaw (最简单)

**无需任何安装，直接提问：**

```
"分析 AAPL 的技术面"
"TSLA 的技术指标如何？"
"对比 AAPL 和 MSFT 的走势"
```

OpenClaw 会自动使用 `manus-stock-analysis` 技能获取 Yahoo Finance 数据。

---

### 方式 2: 安装 Python 依赖 (推荐)

**步骤 1: 安装依赖**
```bash
pip3 install yfinance pandas-ta pandas numpy
```

**步骤 2: 运行分析脚本**
```bash
python3 /root/.openclaw/workspace/scripts/stock-analysis.py
```

**步骤 3: 自定义分析**
```python
from stock_analysis import StockTechnicalAnalyzer

# 分析 TSLA，使用 1 年数据
analyzer = StockTechnicalAnalyzer("TSLA", period="1y")
summary = analyzer.get_summary()

# 查看结果
print(f"评级: {summary['rating']}")
print(f"趋势: {summary['trend']['trend']}")
print(f"RSI: {summary['rsi']['signal']}")
```

---

### 方式 3: 集成到 OpenClaw (高级)

创建自定义技能，让 OpenClaw 直接调用 Python 脚本。

详见: `/root/.openclaw/workspace/scripts/README-stock-analysis.md`

---

## 📊 输出示例

### 方式 1 输出 (OpenClaw 技能)

```
AAPL 技术分析报告

当前价格: $185.23

技术指标:
- 短期趋势: 看涨
- 中期趋势: 上涨
- 支撑位: $180
- 阻力位: $190
- RSI(14): 65
- MACD: 看涨
```

### 方式 2 输出 (Python 脚本)

```
股票代码: AAPL
当前价格: $185.23
分析时间: 2026-03-10T01:00:00

趋势分析:
  趋势: 上涨 (中)
  MA20: $182.50
  MA50: $178.30
  MA200: $172.10

RSI 分析:
  RSI(14): 65.00
  信号: 偏强
  建议: 谨慎持有

MACD 分析:
  MACD: 2.35
  Signal: 1.80
  Histogram: 0.55
  交叉: 金叉
  动能: 多头市场

布林带分析:
  位置: 上轨和中轨之间
  信号: 偏强
  波动率: 中

综合评级:
  得分: 75/100
  评级: 买入
```

---

## 🎯 常用查询示例

### OpenClaw 技能查询

```
"分析 AAPL 的技术面"
"TSLA 是一个好的买入机会吗？"
"给我 AAPL 的支撑和阻力位"
"对比 AAPL、MSFT、GOOGL 的技术指标"
"NVDA 的分析师评级如何？"
```

### Python 脚本查询

```python
# 单只股票
analyzer = StockTechnicalAnalyzer("AAPL")
print(analyzer.to_json())

# 批量分析
symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
for symbol in symbols:
    analyzer = StockTechnicalAnalyzer(symbol, period="3mo")
    print(f"{symbol}: {analyzer.get_summary()['rating']}")

# 多时间周期
for period in ['1mo', '3mo', '6mo', '1y']:
    analyzer = StockTechnicalAnalyzer("AAPL", period=period)
    print(f"{period}: {analyzer.get_summary()['trend']['trend']}")
```

---

## 📈 技术指标说明

### 趋势指标
- **MA (移动平均线)**: 平滑价格波动，判断趋势方向
- **EMA (指数移动平均线)**: 给近期价格更高权重
- **趋势判断**: 上涨、下跌、震荡

### 动量指标
- **RSI (相对强弱指数)**:
  - > 70: 超买，可能回调
  - < 30: 超卖，可能反弹
- **MACD (异同移动平均线)**:
  - 金叉: 看涨信号
  - 死叉: 看跌信号

### 波动率指标
- **布林带**:
  - 上轨之上: 强势突破
  - 下轨之下: 超卖
  - 宽度: 波动率高低

---

## 🎓 学习路径

### 初级 (1-2 小时)
1. 使用 OpenClaw 技能查询几只股票
2. 理解 MA、RSI、MACD 基本含义
3. 尝试 Python 脚本基础分析

### 中级 (1-2 天)
1. 安装 Python 依赖
2. 批量分析多只股票
3. 多时间周期对比分析
4. 自定义指标参数

### 高级 (1 周以上)
1. 创建自定义 OpenClaw 技能
2. 添加可视化 (Plotly)
3. 实现策略回测
4. 建立自动化分析流程

---

## ⚠️ 注意事项

### 数据质量
- Yahoo Finance 数据可能有延迟
- 建议交叉验证多个数据源
- 注意实时性和准确性

### 法律合规
- 仅限个人使用和研究
- 不得用于商业用途
- 遵守相关法律法规

### 风险提示
- 技术分析不能保证盈利
- 任何投资决策需谨慎
- 建议结合基本面分析

---

## 📚 相关文档

- **完整研究报告:** `/root/.openclaw/workspace/note-gen-sync/stock-technical-analysis-openclaw-research-20260310.md`
- **Python 脚本:** `/root/.openclaw/workspace/scripts/stock-analysis.py`
- **详细文档:** `/root/.openclaw/workspace/scripts/README-stock-analysis.md`

---

## 🔄 快速参考

### 常用股票代码
- AAPL: Apple
- TSLA: Tesla
- MSFT: Microsoft
- GOOGL: Google
- AMZN: Amazon
- NVDA: NVIDIA
- 0700.HK: 腾讯
- 600519.SS: 贵州茅台

### 时间周期
- 1mo: 1 个月
- 3mo: 3 个月
- 6mo: 6 个月
- 1y: 1 年
- max: 所有历史数据

---

**文档版本:** 1.0
**更新日期:** 2026-03-10
**作者:** 小老弟
