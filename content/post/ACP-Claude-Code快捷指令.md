---
title: 'ACP-Claude-Code快捷指令'
categories: ["ACP"]
date: 2026-02-28T01:35:43+08:00
lastmod: 2026-02-28T01:35:43+08:00
encrypted: false
---

# Claude Code 快捷指令与使用技巧

> 最后更新：2026-02-28

## 什么是 ACP？

ACP (Agent Client Protocol) 让 OpenClaw 能调用外部编码工具（Claude Code、Codex 等）。

**在 OpenClaw 中使用 Claude Code：**
\`\`\`bash
# 启动 Claude Code 会话
/acp spawn claude --mode persistent

# 配置默认使用 Claude Code
openclaw config set acp.defaultAgent claude
\`\`\`

更多信息：查看 OpenClaw 文档中的 ACP 部分

---

## Claude Code 核心指令

### 文件操作

| 指令 | 功能 | 示例 |
|------|------|------|
| \`read <file>\` | 读取文件内容 | \`read src/main.py\` |
| \`write <file>\` | 写入文件 | \`write output.txt\` |
| \`edit <file>\` | 编辑文件 | \`edit config.yaml\` |
| \`list <dir>\` | 列出目录内容 | \`list src/\` |
| \`search <pattern>\` | 搜索文件 | \`search "TODO"\` |

### 代码分析

| 指令 | 功能 | 示例 |
|------|------|------|
| \`analyze <file>\` | 分析代码 | \`analyze app.js\` |
| \`explain <code>\` | 解释代码 | \`explain for i in range(10):\` |
| \`debug <file>\` | 调试代码 | \`debug server.py\` |
| \`refactor <file>\` | 重构代码 | \`refactor legacy.js\` |

### Git 操作

| 指令 | 功能 | 示例 |
|------|------|------|
| \`git status\` | 查看 Git 状态 | \`git status\` |
| \`git diff\` | 查看改动 | \`git diff\` |
| \`git commit\` | 提交更改 | \`git commit "fix bug"\` |
| \`git log\` | 查看提交历史 | \`git log\` |

### 测试相关

| 指令 | 功能 | 示例 |
|------|------|------|
| \`test\` | 运行测试 | \`test\` |
| \`test <file>\` | 运行特定测试 | \`test test_main.py\` |
| \`coverage\` | 查看测试覆盖率 | \`coverage\` |

---

## Claude Code 使用技巧

### 1. 上下文管理

**最佳实践：**
- 先用 \`read\` 读取相关文件，再提出具体问题
- 使用 \`@file\` 语法引用文件（如果支持）
- 保持对话连贯，避免频繁切换无关话题

### 2. 代码修改技巧

**渐进式修改：**
- 先让 Claude 理解现有代码
- 然后提出具体修改需求
- 检查修改结果，必要时迭代

### 3. 调试技巧

**系统化调试：**
1. 描述问题和预期行为
2. 提供错误信息和日志
3. 让 Claude 分析可能的原因
4. 根据建议逐步排查

### 4. 代码审查

**高效审查：**
- 让 Claude 检查代码质量、安全性、性能
- 请求改进建议
- 要求解释具体问题

### 5. 重构策略

**安全重构：**
1. 先让 Claude 理解代码意图
2. 讨论重构方案
3. 执行重构并验证
4. 确保测试通过

---

## 高级用法

### 1. 多文件操作

**批量操作：**
\`\`\`
# 批量操作
你：列出所有 Python 文件
你：为每个文件添加类型注解
\`\`\`

### 2. 自动化脚本

**生成脚本：**
\`\`\`
# 生成自动化部署脚本
你：生成一个自动化部署脚本
你：要求：备份、构建、测试、部署
\`\`\`

### 3. 文档生成

**自动生成文档：**
\`\`\`
# 生成 README
你：为这个模块生成 README
你：包含：安装、使用、API 说明
\`\`\`

---

## 常见任务速查

### 修复 Bug
\`\`\`
1. read <出错文件>
2. 分析错误信息
3. 询问 Claude 可能的原因
4. 应用修复方案
5. 验证修复
\`\`\`

### 添加新功能
\`\`\`
1. read 相关文件
2. 解释需求和设计
3. 让 Claude 实现功能
4. 审查和测试代码
\`\`\`

### 重构代码
\`\`\`
1. read 要重构的代码
2. 讨论重构目标
3. 执行重构
4. 运行测试确保不破坏功能
\`\`\`

### 编写测试
\`\`\`
1. read 要测试的代码
2. 让 Claude 编写测试用例
3. 运行测试
4. 根据结果调整
\`\`\`

### 性能优化
\`\`\`
1. read 性能瓶颈代码
2. 让 Claude分析优化点
3. 应用优化方案
4. 验证性能提升
\`\`\`
