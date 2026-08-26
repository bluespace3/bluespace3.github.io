---
title: '12-factor-agents笔记'
categories: ["AIGC"]
date: 2026-08-26T14:01:22+08:00
lastmod: 2026-08-26T14:01:22+08:00
draft: false
---
# 12-Factor Agents 阅读笔记

> 仓库地址：<https://github.com/humanlayer/12-factor-agents>

## 一句话概括

由 HumanLayer 创始人 Dex (Dexter Horthy) 发起的开源指南，模仿经典的 [12 Factor Apps](https://12factor.net/)，总结出 **12 条构建"足以交付给生产客户"的 LLM 应用（AI Agent）的工程原则**。

## 核心洞察

作者试遍了主流 Agent 框架（LangChain/Crew、LangGraph、smolagents 等），并与 100+ 位 SaaS 创始人交流后发现：

1. **生产环境中很少有人直接用框架**——典型的路径是：拿框架快速做到 70-80% 的质量，然后发现客户面前 80% 不够好，想再提升就得反向工程框架，最终推倒重写。
2. **好的"AI Agent"产品其实没那么 agentic**——大部分是确定性代码，只在恰当的位置嵌入 LLM 步骤来制造"魔法时刻"，而不是"给个 prompt + 一袋工具然后循环到目标"。
3. 结论：与其 all-in 框架，不如**把 Agent 构建中的小而模块化的概念吸收进现有产品**，普通工程师也能做到。

Agent 的本质循环：

```
1. LLM 决定下一步（输出结构化 JSON / tool call）
2. 确定性代码执行该调用
3. 结果追加进上下文窗口
4. 重复，直到 LLM 判定"完成"
```

## 十二原则

| # | 原则 | 要点 |
|---|------|------|
| 1 | Natural Language → Tool Calls | Agent 的核心能力是让 LLM 把自然语言转成结构化工具调用 |
| 2 | Own Your Prompts | 提示词是核心资产，要自己掌控，不要藏在框架黑盒里 |
| 3 | Own Your Context Window | 主动管理上下文窗口（即"Context Engineering"），决定什么进上下文、如何裁剪/压缩 |
| 4 | Tools Are Just Structured Outputs | 工具本质上是 LLM 的结构化输出，围绕这一点设计工具契约 |
| 5 | Unify Execution State & Business State | 执行状态和业务状态统一存储，避免两套状态不一致 |
| 6 | Launch / Pause / Resume with Simple APIs | 用简单 API 支持启动、暂停、恢复——长时间运行和 human-in-the-loop 的基础 |
| 7 | Contact Humans with Tool Calls | 把"找人类求助/审批"也建模成一个工具调用（HITL 一等公民） |
| 8 | Own Your Control Flow | 控制流自己写代码掌握，不要交给框架的隐式图引擎 |
| 9 | Compact Errors into Context Window | 错误信息要压缩、精炼后放进上下文，而不是堆原始报错 |
| 10 | Small, Focused Agents | 小而专注的 Agent 优于大而全的 Agent |
| 11 | Trigger from Anywhere | 支持从任意事件触发（webhook、cron、消息等），在用户所在的地方交付结果 |
| 12 | Make Your Agent a Stateless Reducer | Agent 做成无状态 reducer：`(state, event) → new state`，易测试、易恢复、易扩展 |

另有 "第 13 条"荣誉提名：Pre-fetch 所有可能需要的上下文。

## 我的点评 / 收获

- **工程视角而非模型视角**：即使模型继续变强，这些软件工程原则（状态管理、控制流、错误处理）依然是可靠性的来源。
- **框架 vs 库**：作者观点接近 "Libraries over Frameworks"——框架能快速起步，但深度控制和后期迭代更重要。
- 最有实操价值的三条：#3（上下文工程）、#7（HITL 工具化）、#12（无状态 reducer 架构）。

## 相关资源

- 原版 12 Factor Apps：<https://12factor.net>
- Anthropic《Building Effective Agents》：<https://www.anthropic.com/engineering/building-effective-agents>
- 作者博客 The Outer Loop：<https://theouterloop.substack.com>
- 用该方法论构建的 Agent 合集：<https://github.com/got-agents/agents>
