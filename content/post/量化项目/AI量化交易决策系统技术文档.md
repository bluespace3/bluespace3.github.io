---
title: "AI量化交易决策系统技术文档"

date: 2025-07-13T12:59:32+08:00

draft: false

tags: ["AI量化交易", "文档"]

categories: ["技术",  "AI", "量化交易"]
---
## 📝 2025-07-13 近期优化与变更

- API支持ETF与A股评分体系分离，ETF基本面恒为0，ETF评分=技术面50分+AI消息面50分。
- 评分体系与决策等级优化，买入阈值降至50分，持有30分，谨慎持有10分，卖出<10分。
- 日志与邮件内容去重，每只股票仅保留最新信号。
- 集成自动邮件功能，主程序运行后自动发送HTML决策报告。
- 数据兼容性增强，分析引擎支持成交量列名为vol或volume。
- 文档补充与完善，详细说明系统架构、评分体系、部署与接口。
- 用户体验提升，聚合报告美化，策略可读性提升。

## 📋 概述

本文档详细说明了量化交易系统的各个模块、类、方法和接口，为开发者提供完整的API参考。

## 🏗️ 系统架构

### 核心模块

```
src/
├── config.py              # 配置管理
├── data_loader.py         # 数据加载器
├── analysis_engine.py     # 分析引擎
├── strategy_engine.py     # 策略引擎
└── gemini_analyzer.py    # AI分析器
```

## 📊 配置模块 (config.py)

### 类和方法

#### 配置常量

# 股票池配置

STOCK_POOL = {
    "000001.SZ": "平安银行",
    "600519.SH": "贵州茅台",
    # ...
}

# API配置

GEMINI_API_URL = "https://rglnawodplak.ap-southeast-1.clawcloudrun.com/*******t/completions"
GEMINI_API_KEY = "***"

# 数据路径

DATA_PATH = "data"

## 📈 数据加载器 (data_loader.py)

### DataLoader 类

#### 方法

##### `__init__(self)`

初始化数据加载器。

**参数**: 无
**返回**: 无

##### `run_update(self, days_to_fetch: int = 365)`

更新所有股票的最新数据。

**参数**:

- `days_to_fetch` (int): 获取数据的天数，默认365天

**返回**: 无

**异常**:

- `Exception`: 数据更新失败时抛出

##### `update_single_stock(self, stock_code: str, days_to_fetch: int = 365)`

更新单个股票的数据。

**参数**:

- `stock_code` (str): 股票代码
- `days_to_fetch` (int): 获取数据的天数

**返回**: 无

## 🔍 分析引擎 (analysis_engine.py)

### AnalysisEngine 类

#### 技术指标计算方法

##### `calculate_ma(self, data: pd.DataFrame, window: int) -> pd.Series`

计算移动平均线。

**参数**:

- `data` (pd.DataFrame): 包含 'close' 列的DataFrame
- `window` (int): 移动平均窗口大小

**返回**: pd.Series - 移动平均线数据

**异常**:

- `ValueError`: 数据中缺少 'close' 列时抛出

##### `calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series`

计算相对强弱指数。

**参数**:

- `data` (pd.DataFrame): 包含 'close' 列的DataFrame
- `window` (int): RSI计算窗口，默认14

**返回**: pd.Series - RSI数据

##### `calculate_macd(self, data: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9)`

计算MACD指标。

**参数**:

- `data` (pd.DataFrame): 包含 'close' 列的DataFrame
- `short_window` (int): 短期EMA窗口，默认12
- `long_window` (int): 长期EMA窗口，默认26
- `signal_window` (int): 信号线EMA窗口，默认9

**返回**: tuple - (MACD, Signal Line, MACD Histogram)

##### `calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, num_std: float = 2)`

计算布林带指标。

**参数**:

- `data` (pd.DataFrame): 包含 'close' 列的DataFrame
- `window` (int): 移动平均窗口，默认20
- `num_std` (float): 标准差倍数，默认2

**返回**: tuple - (上轨, 中轨, 下轨)

##### `calculate_kdj(self, data: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3)`

计算KDJ指标。

**参数**:

- `data` (pd.DataFrame): 包含 'high', 'low', 'close' 列的DataFrame
- `n` (int): RSV计算周期，默认9
- `m1` (int): K值平滑系数，默认3
- `m2` (int): D值平滑系数，默认3

**返回**: tuple - (K, D, J值)

##### `calculate_volume_indicators(self, data: pd.DataFrame)`

计算成交量相关指标。

**参数**:

- `data` (pd.DataFrame): 包含 'volume' 或 'vol' 列的DataFrame

**返回**: tuple - (成交量MA5, 成交量MA10, 量价关系)

##### `calculate_atr(self, data: pd.DataFrame, window: int = 14)`

计算平均真实波幅。

**参数**:

- `data` (pd.DataFrame): 包含 'high', 'low', 'close' 列的DataFrame
- `window` (int): ATR计算窗口，默认14

**返回**: pd.Series - ATR值

##### `calculate_williams_r(self, data: pd.DataFrame, window: int = 14)`

计算威廉指标。

**参数**:

- `data` (pd.DataFrame): 包含 'high', 'low', 'close' 列的DataFrame
- `window` (int): 计算窗口，默认14

**返回**: pd.Series - Williams %R值

##### `run_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame`

为给定的数据计算所有预设的技术指标。

**参数**:

- `data` (pd.DataFrame): 原始日线数据

**返回**: pd.DataFrame - 附加了所有技术指标列的DataFrame

## 🎯 策略引擎 (strategy_engine.py)

### StrategyEngine 类

#### 决策等级常量

```python
DECISION_LEVELS = {
    'STRONG_BUY': 2,      # 重仓买入: 总分 >= 80
    'BUY': 1,             # 买入: 总分 >= 60
    'HOLD': 0,            # 持有: 总分 >= 20
    'CAUTIOUS_HOLD': -1,  # 谨慎持有: 总分 >= -10
    'SELL': -2            # 卖出: 总分 < -10
}
```

#### 评分方法

##### `get_pe_score(self, pe_ratio_str: str) -> tuple[int, str]`

根据PE估值打分。

**参数**:

- `pe_ratio_str` (str): PE比率字符串

**返回**: tuple - (得分, 原因说明)

##### `get_pb_score(self, pb_ratio_str: str) -> tuple[int, str]`

根据PB估值打分。

**参数**:

- `pb_ratio_str` (str): PB比率字符串

**返回**: tuple - (得分, 原因说明)

##### `get_dividend_yield_score(self, dividend_yield_str: str) -> tuple[int, str]`

根据股息率打分。

**参数**:

- `dividend_yield_str` (str): 股息率字符串

**返回**: tuple - (得分, 原因说明)

##### `get_sentiment_score(self, gemini_analysis: dict) -> tuple[int, str]`

根据Gemini返回的量化情绪分进行打分。

**参数**:

- `gemini_analysis` (dict): Gemini分析结果

**返回**: tuple - (得分, 原因说明)

##### `get_technical_score(self, data: pd.DataFrame) -> tuple[int, str, dict]`

根据多指标组合进行技术面综合打分。

**参数**:

- `data` (pd.DataFrame): 包含技术指标的DataFrame

**返回**: tuple - (总分, 原因字符串, 分数明细字典)

##### `get_decision_level(self, total_score: int) -> tuple[int, str]`

根据总分确定决策等级。

**参数**:

- `total_score` (int): 总分

**返回**: tuple - (决策等级代码, 决策描述)

##### `generate_signals(self, data: pd.DataFrame, gemini_analysis: dict) -> tuple[pd.DataFrame, dict]`

根据技术面和Gemini的全面分析生成最终信号。

**参数**:

- `data` (pd.DataFrame): 包含技术指标的DataFrame
- `gemini_analysis` (dict): Gemini分析结果

**返回**: tuple - (添加了信号的DataFrame, 决策报告字典)

## 🤖 AI分析器 (gemini_analyzer.py)

### GeminiAnalyzer 类

#### 方法

##### `__init__(self)`

初始化Gemini分析器。

**参数**: 无
**返回**: 无

##### `get_holistic_analysis(self, stock_name: str, stock_code: str) -> dict`

获取股票的全面分析。

**参数**:

- `stock_name` (str): 股票名称
- `stock_code` (str): 股票代码

**返回**: dict - 包含分析结果的字典

**返回格式**:

```python
{
    'pe': '25.5',
    'pb': '2.8',
    'dividend_yield': '3.2',
    'sentiment_score': '5',
    'sentiment_reason': '市场情绪良好',
    'key_factors': ['政策利好', '业绩增长'],
    'data_date': '2024-01-15'
}
```

## 📧 邮件模块 (send_email.py)

### 函数

##### `send_email(subject: str, body: str, attachments: dict = None)`

发送邮件。

**参数**:

- `subject` (str): 邮件主题
- `body` (str): 邮件内容
- `attachments` (dict): 附件字典，可选

**返回**: 无

**异常**:

- `Exception`: 邮件发送失败时抛出

##### `read_file_content(filepath: str) -> str`

读取文件内容。

**参数**:

- `filepath` (str): 文件路径

**返回**: str - 文件内容，失败时返回None

##### `get_latest_log_content() -> str`

获取最新的日志内容。

**参数**: 无
**返回**: str - 最新日志内容，无日志时返回None

##### `format_decision_report() -> str`

格式化决策报告。

**参数**: 无
**返回**: str - HTML格式的决策报告

## 🧪 测试模块 (test_new_system.py)

### 函数

##### `create_test_data() -> pd.DataFrame`

创建测试数据。

**参数**: 无
**返回**: pd.DataFrame - 模拟的股票数据

##### `test_analysis_engine()`

测试分析引擎。

**参数**: 无
**返回**: pd.DataFrame - 分析后的数据

##### `test_strategy_engine()`

测试策略引擎。

**参数**: 无
**返回**: 无

##### `test_decision_levels()`

测试决策等级。

**参数**: 无
**返回**: 无

##### `main()`

主测试函数。

**参数**: 无
**返回**: 无

## 📊 主程序 (main.py)

### 函数

##### `setup_logging()`

创建日志目录。

**参数**: 无
**返回**: 无

##### `log_signal(signal_to_log: str)`

将信号记录到当天的日志文件中。

**参数**:

- `signal_to_log` (str): 要记录的信号

**返回**: 无

##### `get_signal_color_and_text(signal: int, decision_desc: str) -> tuple[str, str]`

根据信号获取颜色和文本。

**参数**:

- `signal` (int): 信号代码
- `decision_desc` (str): 决策描述

**返回**: tuple - (带颜色的文本, 纯文本)

##### `run_main_flow()`

执行主流程。

**参数**: 无
**返回**: 无

## 🔧 配置说明

### 环境变量

```bash
# 可选的环境变量
GEMINI_API_URL=your-api-url
GEMINI_API_KEY=your-api-key
SMTP_SERVER=smtp.126.com
EMAIL_ADDRESS=your-email@126.com
EMAIL_PASSWORD=your-password
```

### 配置文件

- `src/config.py`: 主要配置文件
- `send_email.py`: 邮件配置
- `requirements.txt`: 依赖包列表

## 📝 日志格式

### 交易信号日志格式

```
Signal for 股票名称 (股票代码) on 日期: 【决策】
  - Tech: 技术面得分 (技术面原因) (技术面明细)
  - Fundamentals: 基本面得分 (基本面原因) (基本面明细)
  - AI Sentiment: 情绪面得分 (情绪面原因) (数据日期) 关键因素
  - TOTAL SCORE: 总分
```

### 系统日志格式

```
时间戳 - 日志内容
```

## ⚠️ 错误处理

### 常见异常

- `ValueError`: 数据格式错误
- `FileNotFoundError`: 文件未找到
- `Exception`: 网络错误、API错误等

### 错误处理建议

1. 检查数据完整性
2. 验证API配置
3. 确认网络连接
4. 查看详细错误日志

## 🔄 版本历史

### v2.0 (当前版本)

- 新增技术指标：布林带、KDJ、成交量、ATR、威廉指标
- 改进评分系统：技术面40分、基本面35分、情绪面25分
- 5级决策系统：重仓买入、买入、持有、谨慎持有、卖出
- 优化邮件报告：HTML格式，更好的可读性
- 完善项目文档

### v1.0

- 基础技术指标：MA、RSI、MACD
- 基础评分系统
- 3级决策系统：买入、持有、卖出
- 基础邮件功能

---

**API版本**: v2.0
**最后更新**: 2025-01-13
**维护者**: 量化交易系统团队
