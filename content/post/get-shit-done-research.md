---
title: 'get-shit-done-research'
categories: ["get-shit-done-research.md"]
date: 2026-03-27T04:00:15+08:00
lastmod: 2026-04-08T23:32:29+08:00
draft: false
---
# 关于 get-shit-done (GSD) 系统的研究笔记

## 简介
`get-shit-done` (GSD) 是一个为 Claude Code、Gemini CLI、Copilot 等 AI 编码工具设计的**元提示 (meta-prompting)、上下文工程 (context engineering) 和规范驱动开发 (spec-driven development)** 系统。

它并不是 Claude Code 的一个内置插件，而是一个独立安装的、用于构建 AI 开发工作流的系统框架。其核心目的是解决 AI 在长任务中常见的“上下文漂移 (context rot)”问题，提供结构化的自动化开发流程。

## 核心功能
GSD 通过一系列系统文件（`.planning/` 目录）和命令行接口，将零散的 AI 对话转化为可管理、可验证的开发任务：

1. **结构化上下文管理**：利用 `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` 等文件，在不同会话间保持一致的开发上下文。
2. **阶段化工作流 (Phase-based Workflow)**：将任务拆解为阶段，执行 `discuss` -> `plan` -> `execute` -> `verify` 的严谨循环。
3. **原子化提交**：通过原子化任务规划和提交，使得每个 Git commit 都具有明确的逻辑关联，极大简化了错误追踪和回退。
4. **多代理编排**：利用 sub-agents 并行处理不同任务，提升大规模项目执行效率。
5. **规范驱动**：不仅生成代码，还会在执行前进行任务规划和执行后进行自动化验证。

## 核心工作流命令
- `/gsd:new-project`: 初始化项目，定义愿景、需求和阶段路线图。
- `/gsd:discuss-phase <N>`: 在每个阶段开始前讨论实现细节，生成 `CONTEXT.md`。
- `/gsd:plan-phase <N>`: 根据上下文生成原子化执行计划（XML 结构）。
- `/gsd:execute-phase <N>`: 并行执行计划，自动处理依赖，并进行原子化提交。
- `/gsd:verify-work <N>`: 进行人工确认和用户验收测试 (UAT)。
- `/gsd:quick`: 用于无需完整规划的轻量级任务。

## 为什么它重要？
- **解决“vibecoding”导致的质量不可控**：通过强制的规划和验证层，让 AI 输出的代码更规范、更易于扩展。
- **上下文复用**：避免每次开会话都要重申项目背景，通过 `.planning/` 存储决策，使 Claude 始终“记得”项目状态。
- **可操作的 Git 历史**：保证了项目历史的清晰，不仅是对人，更是为了未来 AI 能更好地回溯历史代码。

## 安装与使用
可以通过 `npx` 直接安装和更新：
```bash
npx get-shit-done-cc@latest
```
安装后，在 Claude Code 中通过 `/gsd:help` 即可查看所有命令。

---
*注：GSD 是一个不断演进的工具，旨在消除传统的繁琐流程，让 solo 开发者也能利用企业级的 AI 自动化工作流。*
