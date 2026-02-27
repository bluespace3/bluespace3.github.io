---
title: 'OpenClaw快捷键'
categories: ["OpenClaw快捷键.md"]
date: 2026-02-28T03:17:58+08:00
lastmod: 2026-02-28T03:17:58+08:00
encrypted: false

## 常用命令别名
---

| 原命令 | 别名 |
|--------|------|
| `/think` | `/thinking`, `/t` |
| `/verbose` | `/v` |
| `/reasoning` | `/reason` |
| `/elevated` | `/elev` |
| `/whoami` | `/id` |
| `/export` | `/export-session` |
| `/dock_telegram` | `/dock-telegram` |
| `/dock_discord` | `/dock-discord` |
| `/dock_slack` | `/dock-slack` |

---

## 命令使用技巧

### 1. 快捷键组合技巧
- **快速清理并退出**：`Ctrl+C` 两次
- **快速查看状态**：输入 `/status` 后按 `Enter`
- **切换思考模式**：`Ctrl+T` 或使用 `/think` 命令

### 2. 斜杠命令技巧
- **命令参数分隔**：可在命令和参数间使用 `:`（如 `/think: high`）
- **内联快捷方式**：授权发送者可在消息中内联使用 `/help`, `/commands`, `/status`, `/whoami`
- **仅命令消息**：仅包含命令的消息会立即处理，跳过队列和模型

### 3. 模型选择技巧
- 使用 `/model` 或 `/models` 打开模型选择器
- 可使用模型别名直接选择：`/model 3`（选择编号 3 的模型）
- Discord 支持交互式选择器

### 4. 会话管理技巧
- 会话键格式：`agent:<agentId>:<sessionKey>`
- 使用 `/session main` 快速切换到主会话
- 使用 `/session agent:other:main` 显式切换到其他智能体的会话

### 5. 权限控制技巧
- 使用 `/elevated on` 提升权限级别
- 使用 `/exec` 查看当前执行设置
- 使用 `/approve` 处理执行批准请求

---

## 注意事项

### 权限要求
- `/config` 命令需要 `commands.config: true` 配置
- `/debug` 命令需要 `commands.debug: true` 配置
- `/bash` 命令需要 `commands.bash: true` 配置和 `tools.elevated` 允许列表
- 内联快捷方式仅对授权发送者有效

### 群组使用
- `/reasoning` 和 `/verbose` 在群组中有风险，可能暴露内部推理
- 建议在群组中保持这些功能关闭
- `/activation mention` 设置仅在群组中提及 AI 时响应

### 安全建议
- Dashboard 是管理员界面，不要公开暴露
- 使用 localhost、Tailscale Serve 或 SSH 隧道访问
- 令牌存储在 `localStorage`，注意保护

---

## 快速参考

### 日常高频命令
```bash
/status          # 查看状态
/model           # 选择模型
/think high      # 开启深度思考
/deliver on      # 开启消息投递
/new             # 新建会话
```

### 调试命令
```bash
/verbose on      # 显示详细输出
/context detail  # 查看详细上下文
/debug show      # 查看运行时配置
/export          # 导出会话
```

### 权限管理
```bash
/elevated on     # 提升权限
/allowlist list  # 查看允许列表
/config show     # 查看配置
```
