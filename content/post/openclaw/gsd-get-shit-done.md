---
title: 'gsd-get-shit-done'
categories: ["openclaw"]
date: 2026-03-18T03:00:02+08:00
lastmod: 2026-04-08T23:32:29+08:00
draft: false
---
# GSD (Get Shit Done) - Claude Code 上下文工程系统

**GitHub**: [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)
**Stars**: 31,514+
**作者**: TÂCHES
**官网**: https://github.com/gsd-build/get-shit-done

---

## 项目概述

GSD 是一个针对 Claude Code 的**元提示、上下文工程和规格驱动开发系统**。它解决了 **context rot** 问题：随着 Claude 的上下文窗口被填满，输出质量逐步劣化。

通过智能的上下文管理和多代理编排，GSD 让 Claude Code 的输出质量持续稳定。

**已被 Amazon、Google、Shopify 和 Webflow 的工程师采用。**

---

## 核心工作流程

```
/gsd:new-project     → 提问 + 研究 → 需求 + 路线图
/gsd:discuss-phase   → 收集实现决策（视觉、API、内容系统等）
/gsd:plan-phase      → 研究 + 制定计划（XML格式）+ 验证
/gsd:execute-phase    → 并行执行（wave方式）+ 原子提交
/gsd:verify-work     → 用户验收测试
→ 重复直到完成
```

### 1. 初始化项目

```
/gsd:new-project
```

系统会：
1. **提问**：一直问到彻底理解想法（目标、约束、技术偏好、边界情况）
2. **研究**：并行拉起代理调研领域知识
3. **需求梳理**：提取 v1、v2 范围
4. **路线图**：创建与需求映射的阶段规划

生成：`PROJECT.md`、`REQUIREMENTS.md`、`ROADMAP.md`、`STATE.md`、`.planning/research/`

### 2. 讨论阶段

```
/gsd:discuss-phase 1
```

在规划前收集实现决策：
- **视觉功能**：布局、信息密度、交互、空状态
- **API / CLI**：返回格式、flags、错误处理、详细程度
- **内容系统**：结构、语气、深度、流转方式
- **组织型任务**：分组标准、命名、去重、例外情况

生成：`{phase_num}-CONTEXT.md`

### 3. 规划阶段

```
/gsd:plan-phase 1
```

系统会：
1. **研究**：结合 CONTEXT.md 决策调研实现方式
2. **制定计划**：创建 2-3 份原子化任务计划（XML结构）
3. **验证**：将计划与需求对照检查，直到通过

每份计划足够小，可以在一个全新的上下文窗口里执行。

生成：`{phase_num}-RESEARCH.md`、`{phase_num}-{N}-PLAN.md`

### 4. 执行阶段

```
/gsd:execute-phase 1
```

系统会：
1. **按 wave 执行计划**：能并行的并行，有依赖的顺序执行
2. **每个计划使用新上下文**：20 万 token 纯用于实现，零历史垃圾
3. **每个任务单独提交**：每项任务都有自己的原子提交
4. **对照目标验证**：检查代码库是否真的交付了该阶段承诺的内容

#### Wave 执行方式

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE EXECUTION                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  WAVE 1 (parallel)          WAVE 2 (parallel)          WAVE 3       │
│  ┌─────────┐ ┌─────────┐    ┌─────────┐ ┌─────────┐    ┌─────────┐ │
│  │ Plan 01 │ │ Plan 02 │ →  │ Plan 03 │ │ Plan 04 │ →  │ Plan 05 │ │
│  │         │ │         │    │         │ │         │    │         │ │
│  │ User    │ │ Product │    │ Orders  │ │ Cart    │    │ Checkout│ │
│  │ Model   │ │ Model   │    │ API     │ │ API     │    │ UI      │ │
│  └─────────┘ └─────────┘    └─────────┘ └─────────┘    └─────────┘ │
│       │           │              ↑           ↑              ↑       │
│       └───────────┴──────────────┴───────────┘              │       │
│              Dependencies: Plan 03 needs Plan 01            │       │
│                          Plan 04 needs Plan 02              │       │
│                          Plan 05 needs Plans 03 + 04        │       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

生成：`{phase_num}-{N}-SUMMARY.md`、`{phase_num}-VERIFICATION.md`

### 5. 验证工作

```
/gsd:verify-work 1
```

系统会：
1. **提取可测试的交付项**
2. **逐项带你验证**
3. **自动诊断失败**：拉起 debug 代理定位根因
4. **创建验证过的修复计划**

如果出现问题，重新运行 `/gsd:execute-phase` 即可执行自动生成的修复计划。

生成：`{phase_num}-UAT.md`，以及发现问题时的修复计划

---

## 核心技术特点

### 1. 上下文工程

GSD 通过一系列结构化文件管理上下文，每个文件尺寸都控制在质量阈值内：

| 文件 | 作用 |
|------|------|
| `PROJECT.md` | 项目愿景，始终加载 |
| `research/` | 生态知识（技术栈、功能、架构、坑点） |
| `REQUIREMENTS.md` | 带 phase 可追踪性的 v1/v2 范围定义 |
| `ROADMAP.md` | 你要去哪里、哪些已经完成 |
| `STATE.md` | 决策、阻塞、当前位置，跨会话记忆 |
| `PLAN.md` | 带 XML 结构和验证步骤的原子任务 |
| `SUMMARY.md` | 做了什么、改了什么、已写入历史 |
| `todos/` | 留待后续处理的想法和任务 |

### 2. XML 提示格式

每个计划都使用为 Claude 优化过的结构化 XML：

```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    Use jose for JWT (not jsonwebtoken - CommonJS issues).
    Validate credentials against users table.
    Return httpOnly cookie on success.
  </action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials return cookie, invalid return 401</done>
</task>
```

指令足够精确，验证也内建在计划里。

### 3. 多代理编排

每个阶段都遵循同一种模式：一个轻量 orchestrator 拉起专用代理、汇总结果，再路由到下一步。

| 阶段 | Orchestrator 做什么 | Agents 做什么 |
|------|---------------------|---------------|
| 研究 | 协调与展示研究结果 | 4 个并行研究代理分别调查技术栈、功能、架构、坑点 |
| 规划 | 校验并管理迭代 | Planner 生成计划，checker 验证，循环直到通过 |
| 执行 | 按 wave 分组并跟踪进度 | Executors 并行实现，每个都有全新的 20 万上下文 |
| 验证 | 呈现结果并决定下一步 | Verifier 对照目标检查代码库，debuggers 诊断失败 |

**最终效果**：你可以在一个阶段里完成深度研究、生成并验证多个计划、让多个执行代理并行写下成千上万行代码，再自动对照目标验证，而主上下文窗口依然能维持在 30-40% 左右。

### 4. 原子 Git 提交

每个任务完成后都会立刻生成独立提交：

```bash
abc123f docs(08-02): complete user registration plan
def456g feat(08-02): add email confirmation flow
hij789k feat(08-02): implement password hashing
lmn012o feat(08-02): create registration endpoint
```

**好处**：
- `git bisect` 能精准定位是哪项任务引入故障
- 每个任务都可单独回滚
- 未来 Claude 读取历史时也更清晰
- 整个 AI 自动化工作流的可观测性更好

### 5. 模块化设计

- 给当前里程碑追加 phase
- 在 phase 之间插入紧急工作
- 完成当前里程碑后开启新的周期
- 在不推倒重来的前提下调整计划

---

## 常用命令

### 核心工作流

| 命令 | 作用 |
|------|------|
| `/gsd:new-project [--auto]` | 完整初始化：提问 → 研究 → 需求 → 路线图 |
| `/gsd:discuss-phase [N] [--auto]` | 在规划前收集实现决策 |
| `/gsd:plan-phase [N] [--auto]` | 为某个阶段执行研究 + 规划 + 验证 |
| `/gsd:execute-phase <N>` | 以并行 wave 执行全部计划，完成后验证 |
| `/gsd:verify-work [N]` | 人工用户验收测试 |
| `/gsd:audit-milestone` | 验证里程碑是否达到完成定义 |
| `/gsd:complete-milestone` | 归档里程碑并打 release tag |
| `/gsd:new-milestone [name]` | 开始下一个版本：提问 → 研究 → 需求 → 路线图 |

### 导航

| 命令 | 作用 |
|------|------|
| `/gsd:progress` | 我现在在哪？下一步是什么？ |
| `/gsd:help` | 显示全部命令和使用指南 |
| `/gsd:update` | 更新 GSD，并预览变更日志 |
| `/gsd:join-discord` | 加入 GSD Discord 社区 |

### Brownfield（已有项目）

| 命令 | 作用 |
|------|------|
| `/gsd:map-codebase` | 在 `new-project` 前分析现有代码库 |

### 快速模式

```
/gsd:quick
```

适用于不需要完整规划的临时任务（修 bug、小功能、配置改动）：
- 保留核心保障（原子提交、状态跟踪）
- 跳过可选步骤（research、plan checker、verifier）
- 数据存放在 `.planning/quick/`

---

## 配置

### 安装

```bash
npx get-shit-done-cc@latest
```

安装器会提示选择：
1. **运行时**：Claude Code、OpenCode、Gemini、Codex，或全部
2. **安装位置**：全局（所有项目）或本地（仅当前项目）

### 非交互式安装

```bash
# Claude Code 全局安装
npx get-shit-done-cc --claude --global

# 所有运行时
npx get-shit-done-cc --all --global
```

### 推荐配置

建议使用 `--dangerously-skip-permissions` 运行 Claude Code，减少权限确认摩擦。

### 模型 Profile

| Profile | Planning | Execution | Verification |
|---------|----------|-----------|--------------|
| `quality` | Opus | Opus | Sonnet |
| `balanced`（默认） | Opus | Sonnet | Sonnet |
| `budget` | Sonnet | Sonnet | Haiku |

切换方式：`/gsd:set-profile budget`

### 核心设置

| Setting | Options | Default | 作用 |
|---------|---------|---------|---------|
| `mode` | `yolo`, `interactive` | `interactive` | 自动批准，还是每一步确认 |
| `granularity` | `coarse`, `standard`, `fine` | `standard` | phase 粒度 |
| `workflow.research` | `true`/`false` | `true` | 每个 phase 规划前先调研领域知识 |
| `workflow.plan_check` | `true`/`false` | `true` | 执行前验证计划 |
| `workflow.verifier` | `true`/`false` | `true` | 执行后确认交付项 |
| `workflow.auto_advance` | `true`/`false` | `false` | 自动串联 discuss → plan → execute |

### Git 分支策略

| Setting | Options | Default | 作用 |
|---------|---------|---------|---------|
| `git.branching_strategy` | `none`, `phase`, `milestone` | `none` | 分支创建策略 |

---

## 适用场景

### ✅ 适合

- 独立开发者想快速构建项目
- 需要高质量、可维护的代码
- 项目规模较大（防止 context rot）
- 需要规范文档和 git 历史
- 全新项目开发
- 大规模功能开发

### ❌ 不适合

- 简单脚本、配置修改
- 对现有项目的 small bug 修复
- 已经有熟悉且有效的开发流程
- 一次性小任务

---

## 安全

### 保护敏感文件

包含机密信息的文件应当加入 Claude Code 的 deny list：

```json
{
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(**/secrets/*)",
      "Read(**/*credential*)",
      "Read(**/*.pem)",
      "Read(**/*.key)"
    ]
  }
}
```

---

## 更新

```bash
npx get-shit-done-cc@latest
```

---

## 卸载

```bash
# 全局安装卸载
npx get-shit-done-cc --claude --global --uninstall
npx get-shit-done-cc --opencode --global --uninstall
npx get-shit-done-cc --codex --global --uninstall

# 本地安装卸载
npx get-shit-done-cc --claude --local --uninstall
```

---

## 社区

- **Discord**: https://discord.gg/gsd
- **X (Twitter)**: https://x.com/gsd_foundation
- **Token**: $GSD on Solana (Dexscreener)

---

## 总结

> **"Claude Code 很强，GSD 让它变得可靠。"**

GSD 不是在假装你在运营一个 50 人工程组织，而是通过智能的上下文工程和多代理编排，让 Claude Code 真正能够持续、高质量地完成开发工作。

复杂性在系统内部，不在你的工作流里。你看到的是几个真能工作的命令。

---

**文档更新时间**: 2026-03-17
**来源**: B站视频《2万星神器！让Claude Code效率翻倍的GSD深度解析》+ GitHub README
