---
title: 'ACP-Claude-Code快捷指令'
categories: ["实践"]
date: 2026-02-28T01:35:43+08:00
lastmod: 2026-03-25T13:02:09+08:00
draft: false
---
# ACP Claude Code 使用指南

> 最后更新：2026-03-05
> ACP (Agent Client Protocol) 是 OpenClaw 接入 Claude Code 等外部编码工具的标准方式

---

## 什么是 ACP？

**ACP (Agent Client Protocol)** 是一种协议，让 OpenClaw 能够调用外部编码工具（Claude Code、Codex、Pi、OpenCode、Gemini CLI 等）。

### ACP vs 传统方式

| 方式 | 特点 | 适用场景 |
|------|------|----------|
| **ACP 运行时** | 集成到 OpenClaw 会话系统，支持线程绑定、持久化会话 | 在聊天中持续使用编码工具 |
| **直接调用 acpx** | 通过 CLI 驱动外部会话，更底层 | 需要精细控制或调试 |

---

## 在 OpenClaw 中使用 Claude Code

### 方法 1：通过 `sessions_spawn` 工具（推荐）

这是最常用的方式，直接在聊天中启动 Claude Code ACP 会话。

#### 基础用法

```python
sessions_spawn(
    task="帮我分析这个代码库的结构",
    runtime="acp",
    agentId="claude",
    thread=True,
    mode="session"
)
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `task` | 必填 | 初始发送给 Claude Code 的任务描述 |
| `runtime` | 必填 | 固定为 `"acp"` |
| `agentId` | 可选 | 目标工具 ID：`"claude"`（Claude Code）、`"codex"`、`"pi"` 等 |
| `thread` | 可选 | 是否绑定到线程（默认 `false`） |
| `mode` | 可选 | `"session"`（持久化）或 `"run"`（一次性） |
| `cwd` | 可选 | 工作目录路径 |
| `label` | 可选 | 会话标签，便于识别 |

#### 示例场景

**场景 1：在 Discord 线程中启动持久化会话**

```python
sessions_spawn(
    task="打开这个项目并帮我添加一个用户认证功能",
    runtime="acp",
    agentId="claude",
    thread=True,
    mode="session",
    label="用户认证开发"
)
```

**场景 2：一次性分析任务**

```python
sessions_spawn(
    task="审查这个文件的安全漏洞：src/auth.py",
    runtime="acp",
    agentId="claude"
)
```

**场景 3：指定工作目录**

```python
sessions_spawn(
    task="重构这个模块，提高性能",
    runtime="acp",
    agentId="claude",
    cwd="/var/www/bluespace3.github.io"
)
```

---

### 方法 2：通过 `/acp` 命令（聊天中直接使用）

在支持的聊天平台（如 Discord）中，可以直接使用斜杠命令。

#### 启动会话

```text
/acp spawn claude --mode persistent --thread auto
```

#### 命令参数

| 参数 | 说明 |
|------|------|
| `--mode persistent` | 持久化模式（保持会话活跃） |
| `--mode oneshot` | 一次性模式（执行完立即关闭） |
| `--thread auto` | 自动绑定线程（如果有线程则绑定，没有则创建） |
| `--thread here` | 绑定到当前线程 |
| `--thread off` | 不绑定线程 |
| `--cwd <路径>` | 指定工作目录 |
| `--label <名称>` | 设置会话标签 |

#### 其他常用命令

```text
# 查看状态
/acp status

# 取消当前正在执行的任务
/acp cancel

# 向运行中的会话发送新指令
/acp steer 优化测试覆盖率

# 设置工作目录
/acp cwd /path/to/project

# 设置使用的模型
/acp model anthropic/claude-opus-4-5

# 设置超时时间（秒）
/acp timeout 300

# 查看所有 ACP 会话
/acp sessions

# 关闭会话并解绑线程
/acp close
```

---

## ACP 会话管理

### 线程绑定（Thread Binding）

**线程绑定**允许将 ACP 会话绑定到聊天线程，后续在该线程中的消息会自动路由到该会话。

#### 支持的平台

- ✅ Discord（内置支持）
- 🔄 其他平台（需插件支持）

#### 配置要求

```json5
{
  acp: {
    enabled: true,
    dispatch: { enabled: true }
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true
      }
    }
  }
}
```

#### 线程模式

| `--thread` 值 | 行为 |
|--------------|------|
| `auto` | 在线程中绑定，不在线程中创建并绑定 |
| `here` | 必须在现有线程中执行，否则失败 |
| `off` | 不绑定，会话独立运行 |

---

### 会话控制

#### 手动聚焦（Focus）

将当前线程绑定到已有会话：

```text
/focus agent:claude:acp:abc123-def456
```

或使用标签：

```text
/focus 用户认证开发
```

#### 解绑（Unfocus）

```text
/unfocus
```

#### 查看活跃会话

```text
/agents
```

#### 设置会话 TTL（自动解绑时间）

```text
/session ttl 12h
/session ttl off
```

---

## Claude Code 快捷键与指令

### 快捷键（在 Claude Code 独立运行时）

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Esc` | 停止生成 |
| `Ctrl+C` | 一次清除输入，两次退出 |
| `↑/↓` | 浏览历史消息 |
| `Ctrl+L` | 清屏 |

### 常用指令

**文件操作**

```text
read <file>         # 读取文件
write <file>        # 写入文件
edit <file>         # 编辑文件
list <dir>          # 列出目录
search <pattern>    # 搜索文件
```

**代码分析**

```text
analyze <file>      # 分析代码
explain <code>      # 解释代码
debug <file>        # 调试代码
refactor <file>     # 重构代码
```

**Git 操作**

```text
git status          # 查看状态
git diff            # 查看改动
git commit "msg"    # 提交更改
git log             # 查看历史
```

---

## 典型工作流程

### 1. 在 OpenClaw 中启动 ACP Claude Code

**目标：为现有项目添加新功能**

```python
# Step 1: 启动持久化会话并绑定线程
sessions_spawn(
    task="帮我理解这个项目的结构，准备添加新功能",
    runtime="acp",
    agentId="claude",
    thread=True,
    mode="session",
    cwd="/var/www/bluespace3.github.io"
)
```

**后续步骤（在绑定线程中）：**

1. 让 Claude Code 分析代码库
2. 提出新功能的需求
3. 让 Claude Code 实现功能
4. 审查代码质量
5. 运行测试验证

---

### 2. 一次性代码审查

```python
sessions_spawn(
    task="审查以下代码的安全性、性能和可维护性：src/auth/user.py",
    runtime="acp",
    agentId="claude"
)
```

---

### 3. 持续开发会话

**启动：**
```text
/acp spawn claude --mode persistent --thread auto --label "重构登录模块"
```

**在绑定线程中：**

```
你：分析当前的登录流程
你：重构为使用 JWT
你：添加单元测试
你：更新文档
```

---

## 技能（Skills）集成

Claude Code 支持 OpenClaw 的技能系统。

### 已安装技能示例

**git-commit-message 技能**

位置：`~/.openclaw/workspace/skills/.claude/skills/git-commit-message`

当你在 ACP Claude Code 会话中使用 `git commit` 时，该技能会自动：

1. 分析暂存区的变更
2. 生成符合规范的 commit message
3. 遵循 Conventional Commits 规范

### 为其他项目安装技能

```bash
cd /path/to/project
mkdir -p .claude/skills
ln -s ~/.openclaw/workspace/skills/.agents/skills/git-commit-message .claude/skills/git-commit-message
```

---

## 配置与安装

### 1. 确保 ACP 插件已安装

```bash
# 检查插件状态
openclaw plugins list

# 如果未安装
openclaw plugins install @openclaw/acpx
openclaw config set plugins.entries.acpx.enabled true
```

### 2. 验证 ACP 后端

```text
/acp doctor
```

### 3. 检查配置

```bash
openclaw config get acp
```

期望输出：
```json5
{
  acp: {
    enabled: true,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "claude",
    allowedAgents: ["pi", "claude", "codex", "opencode", "gemini"]
  }
}
```

---

## 故障排查

### 常见问题

**Q: 启动 ACP 会话时报 "ACP runtime backend is not configured"**

A: 安装并启用 acpx 插件
```bash
openclaw plugins install @openclaw/acpx
openclaw config set plugins.entries.acpx.enabled true
openclaw gateway restart
```

---

**Q: `--thread here` 报错 "requires running /acp spawn inside an active thread"**

A: 你不在线程中，使用 `--thread auto` 或先进入线程

---

**Q: 无法启动，报 "ACP agent 'xxx' is not allowed by policy"**

A: 该 agent 不在允许列表中，检查配置：
```bash
openclaw config get acp.allowedAgents
```

---

**Q: 会话绑定丢失**

A: 可能原因：
- 会话 TTL 过期
- 线程被关闭/存档
- Gateway 重启

重新绑定：
```text
/focus <session-key>
```

---

**Q: Claude Code 无法识别技能**

A: 检查符号链接是否正确：
```bash
ls -la .claude/skills/git-commit-message
# 应该是符号链接指向技能目录
```

---

## 高级用法

### 1. 多会话并行

启动多个独立的 Claude Code 会话处理不同任务：

```python
# 会话 1：后端开发
sessions_spawn(
    task="实现用户 API",
    runtime="acp",
    agentId="claude",
    thread=True,
    label="后端 API"
)

# 会话 2：前端开发
sessions_spawn(
    task="实现登录页面 UI",
    runtime="acp",
    agentId="claude",
    thread=True,
    label="前端 UI"
)
```

---

### 2. 切换工作目录

```text
/acp cwd /var/www/bluespace3.github.io
```

或在启动时指定：
```python
sessions_spawn(
    task="任务",
    runtime="acp",
    agentId="claude",
    cwd="/var/www/bluespace3.github.io"
)
```

---

### 3. 模型切换

```text
/acp model anthropic/claude-opus-4-5
```

---

### 4. 设置超时

```text
/acp timeout 600  # 10 分钟后自动停止
```

---

## 最佳实践

### 对话技巧

**1. 先上下文，后任务**
```text
你：read package.json
你：read src/index.js
你：分析这个项目的依赖和入口文件
```

**2. 渐进式修改**
```text
你：理解这个函数
你：添加错误处理
你：添加日志
```

**3. 明确需求**
- ❌ "优化代码"
- ✅ "优化这个循环的时间复杂度"

---

### 工作流建议

**新功能开发：**
1. 启动持久化 ACP 会话
2. 分析现有代码
3. 讨论设计
4. 实现功能
5. 编写测试
6. 验证和优化

**Bug 修复：**
1. 复现问题
2. 分析相关代码
3. 定位根因
4. 实施修复
5. 验证修复
6. 添加测试

**代码审查：**
1. 一会话审查逻辑层
2. 二会话审查安全层
3. 三会话审查性能层

---

## 提示词模板

### 功能实现
```text
实现以下功能：
1. [需求 1]
2. [需求 2]

约束条件：
- 不破坏现有功能
- 符合项目编码规范
- 添加必要的测试
```

### 代码重构
```text
重构目标：
- [目标 1]
- [目标 2]

要求：
- 保持功能不变
- 提高可读性
- 添加注释
```

### 调试帮助
```text
遇到的问题：
[描述问题]

错误信息：
[粘贴错误]

相关代码：
[read 相关文件]

帮助我：
1. 找出问题原因
2. 提供修复方案
3. 解释为什么会发生
```

---

## 相关资源

- **ACP 协议**: https://agentclientprotocol.com/
- **OpenClaw 文档**: https://docs.openclaw.ai/
- **Claude 官方文档**: https://docs.anthropic.com/
- **Conventional Commits**: https://www.conventionalcommits.org/
