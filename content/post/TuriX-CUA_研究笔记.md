---
title: 'TuriX-CUA 研究笔记'
categories: ['技术']
date: 2026-03-17T03:00:03+0800
draft: false
---
# TuriX-CUA 研究笔记

## 基本信息

**项目名称：** TuriX-CUA (Computer Use Agent)
**开发者：** TurixAI
**GitHub：** https://github.com/TurixAI/TuriX-CUA
**官网：** https://turix.ai/
**开源协议：** 100% 开源，个人和研究使用免费

## 核心概念

TuriX-CUA 是一个 AI 驱动的**桌面自动化数字助手**，让 AI 能够像人一样"看"屏幕、"动"鼠标、"敲"键盘，直接在桌面上执行操作。

### Slogan
"Talk to your computer, watch it work."
（和你的电脑对话，看着它工作）

## 核心特性

### 1. 无需应用特定 API
- 不依赖各应用的 API 接口
- 如果人类能点击，TuriX 也能操作
- 支持 WhatsApp、Excel、Outlook、内部工具等任何应用
- 甚至能绕过验证码（CAPTCHA）

### 2. 多模型架构
- 支持热插换的"大脑"模型
- 通过 config.json 即可更换，无需修改代码
- 支持多种 VLM（视觉语言模型）

### 3. MCP-Ready
- 完全支持 Model Context Protocol（模型上下文协议）
- 可集成 Claude for Desktop 或任何 Agent
- 官方 MCP 工具：https://mcp-container.com/mcp/ef487377-b9ef-4908-9e58-fe0f4771aa8e

### 4. Skills（技能系统）
- 基于 Markdown 的可重用工作流指南
- Planner 选择相关技能（名称 + 描述）
- Brain 使用完整指令规划每个步骤
- 类似"剧本"或"操作手册"机制

### 5. 可恢复记忆
- 支持任务中断后恢复
- 使用稳定 agent_id + resume 模式
- 先进的记忆压缩机制

## 技术架构

### 多角色分工
```
Brain（大脑）→ 理解任务，规划步骤
Actor（执行者）→ 执行具体操作
Memory（记忆）→ 管理上下文和状态
Planner（规划者）→ 制定分步计划（可选）
```

### 支持的模型

#### 1. Turix 官方模型（推荐）
- `turix-brain`（大脑）
- `turix-actor`（执行者）
- 100% 开源，个人/研究免费
- 性能优异

#### 2. Ollama 本地模型
- `llama3.2-vision`
- 完全本地运行，无需 API 费用

#### 3. 第三方模型
- Qwen3-VL（通义千问视觉语言模型）
- Gemini-3-pro（测试中最智能）
- Gemini-3-flash（快速且智能）
- GPT-4.1-mini
- 其他兼容的 VLM

## 性能表现

### 基准测试
- 在内部 OSWorld 风格测试集上通过率 >68%
- 集成 Qwen3-VL 后，复杂 UI 交互任务成功率提升 15%
- 在 macOS 上优于 UI-TARS 等开源 Agent

### 应用场景示例
1. 预订机票、酒店、Uber
2. 搜索 iPhone 价格、创建 Pages 文档并发送给联系人
3. 在 Numbers 中生成图表，插入到 PPT 指定位置，回复老板
4. 搜索 YouTube 视频、点赞
5. 通过 MCP 集成：Claude 搜索 AI 新闻，调用 TuriX 操作电脑，将研究结果写入 Pages 并发送

## 平台支持

### 当前支持
- **macOS 15.6+**（仅 Apple Silicon，不支持 Intel）
- **Windows 10+**

### 即将支持
- **Linux**（Ubuntu 等）- 计划 2026 Q2
- **Chrome-like 浏览器自动化** - 计划 2026 Q2

## 安装方式

### 方式一：下载 App（推荐，简单）
1. 访问官网 https://turix.ai/
2. 下载 TuriX.dmg (macOS) 或 .exe (Windows)
3. 拖拽到应用程序文件夹
4. 打开并授予必要权限

### 方式二：源码安装（高级用户）

#### 环境准备
```bash
# 克隆仓库
git clone https://github.com/TurixAI/TuriX-CUA.git

# Windows 用户切换分支
git checkout multi-agent-windows

# 创建 Python 3.12 环境
conda create -n turix_env python=3.12
conda activate turix_env
pip install -r requirements.txt
```

#### macOS 权限设置
1. **辅助功能（Accessibility）**
   - 系统设置 → 隐私与安全性 → 辅助功能
   - 添加：Terminal、VS Code（或你使用的 IDE）
   - 如果还失败，添加 `/usr/bin/python3`

2. **Safari 自动化**
   - Safari → 设置 → 高级 → 启用"在菜单栏中显示开发菜单"
   - 开发菜单 → 允许远程自动化
   - 开发菜单 → 允许 Apple Events 的 JavaScript

3. **触发授权（终端执行）**
```bash
osascript -e 'tell application "Safari" to do JavaScript "alert(\"Triggering accessibility request\")" in document 1'
```

#### 配置与运行
编辑 `examples/config.json`，设置任务：
```json
{
  "agent": {
    "task": "open system settings, switch to Dark Mode"
  }
}
```

运行：
```bash
python examples/main.py
```

## 配置详解

### API 配置（TuriX 官方）
```json
{
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://turixapi.io/v1"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "turix-brain",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://turixapi.io/v1"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "turix-brain",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://turixapi.io/v1"
  }
}
```

### Ollama 本地配置
```json
{
  "brain_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "actor_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "memory_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "planner_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  }
}
```

### Skills 配置
```json
{
  "agent": {
    "use_plan": true,
    "use_skills": true,
    "skills_dir": "skills",
    "skills_max_chars": 4000
  }
}
```

### 技能文件示例（skills/github-web-actions.md）
```markdown
---
name: github-web-actions
description: Use when navigating GitHub in a browser (searching repos, starring, etc.).
---

# GitHub Web Actions
- Open GitHub, use the site search, and navigate to the repo page.
- If login is required, ask the user before proceeding.
- Confirm the Star button state before moving on.
```

### 恢复任务配置
```json
{
  "agent": {
    "resume": true,
    "agent_id": "my-task-001"
  }
}
```

## OpenClaw 集成

### ClawHub 技能
- 技能地址：https://clawhub.ai/Tongyu-Yan/turix-cua
- 允许 OpenClaw 调用 TuriX 作为桌面 Agent
- 2026-01-30 发布

### 本地技能包
- macOS：仓库内 `OpenCLaw_TuriX_skill/`
- Windows：`multi-agent-windows` 分支的 `OpenCLaw_TuriX_skill/`
- Windows 版本支持直接调度（turix/turix-win 别名）

### 本地技能安装步骤（macOS）
1. 复制 `OpenCLaw_TuriX_skill/` 到 OpenClaw 本地技能文件夹（如 `clawd/skills/local/turix-mac/`）
2. 遵循 `OpenCLaw_TuriX_skill/README.md` 设置权限

### 本地技能安装步骤（Windows）
1. 切换到 `multi-agent-windows` 分支
2. 参考 `OpenCLaw_TuriX_skill/README.md` 安装配置
3. 使用 `turix-win` 命令直接调度
4. 支持 `--dry-run` 模式测试

## 路线图

### 已完成（2025 Q3 - 2026 Q1）
- ✅ 终止和恢复任务
- ✅ Windows 支持
- ✅ 增强的 MCP 集成
- ✅ 下一代 AI 模型
- ✅ Windows 优化模型
- ✅ Gemini-3-pro 模型支持
- ✅ Planner（规划者）
- ✅ 多 Agent 架构
- ✅ DuckDuckGo 集成
- ✅ Ollama 支持
- ✅ 可恢复记忆压缩
- ✅ Skills 系统
- ✅ OpenClaw Skill（ClawHub）
- ✅ OpenClaw Windows 本地技能更新

### 计划中（2026 Q2）
- 🔄 Linux 支持（Ubuntu 等）
- 🔄 浏览器自动化（Chrome-like）
- 🔄 持久化记忆
- 🔄 示例学习（Learning by Demonstration）

## 社区与支持

- **Discord：** https://discord.gg/yaYrNAckb5
- **Email：** user@example.com
- **技术报告：** https://turix.ai/technical-report/
- **API 平台：** https://turixapi.io
- **开发者注册：** https://turix.ai/api-platform/（$20 信用额度）

## 优势与特点

### 相比传统自动化工具
1. **零代码**：无需编写脚本或设计流程
2. **零标注**：无需对 UI 元素进行标记
3. **自适应**：能适应 UI 变化，不像传统工具那样脆弱
4. **学习能力**：从每次任务中学习，变得更智能、更快速
5. **自然语言交互**：用几句话描述需求，即可生成工作流

### 相比其他 AI Agent
1. **开源免费**：100% 开源，个人/研究使用免费
2. **高性能**：OSWorld 测试通过率 >68%，优于 UI-TARS
3. **无数据收集**：隐私保护，不收集用户数据
4. **灵活配置**：支持多种模型，可热插换
5. **MCP 就绪**：易于与其他 Agent 集成

## 潜在应用场景

### 个人用户
- 自动化重复性办公任务
- 批量处理文件（重命名、格式转换等）
- 自动填写表单
- 社交媒体操作（发帖、点赞、回复）
- 财务报表自动化

### 开发者
- 测试自动化
- CI/CD 流程增强
- 文档自动生成
- 代码审查辅助

### 研究人员
- 计算机视觉研究
- 多模态 AI 研究
- Agent 行为研究
- 人机交互研究

## 局限性

1. **平台限制**
   - macOS 仅支持 Apple Silicon（不支持 Intel）
   - Linux 支持仍在开发中

2. **性能依赖**
   - 需要较强的计算能力（尤其是本地 Ollama）
   - 任务成功率受模型能力影响

3. **学习曲线**
   - 初次设置需要配置权限和依赖
   - 编写有效的 Skills 需要一定的 Markdown 技巧

4. **潜在风险**
   - 自动化操作可能产生意外后果
   - 需要用户监督和验证关键操作

## 总结

TuriX-CUA 是一个强大、开源、易于使用的 AI 桌面自动化工具。它的核心优势在于：

1. **真正的"看见"和"操作"**：通过视觉理解界面，直接模拟人类操作
2. **完全开源**：代码透明，可定制，无供应商锁定
3. **灵活集成**：支持 MCP，可与 Claude for Desktop 等 Agent 无缝协作
4. **多模型支持**：可切换不同"大脑"，平衡速度和智能
5. **持续进化**：活跃的开发社区，快速迭代更新

对于想要将 AI 生产力提升到"真正自动化"级别的用户来说，TuriX-CUA 是一个值得探索的优质项目。

---

**研究日期：** 2026-03-07
**研究来源：**
- GitHub 仓库：https://github.com/TurixAI/TuriX-CUA
- 官网：https://turix.ai/
- MCP 工具页面：https://mcp-container.com/mcp/ef487377-b9ef-4908-9e58-fe0f4771aa8e
- 知乎文章：https://zhuanlan.zhihu.com/p/1991453705317398043
