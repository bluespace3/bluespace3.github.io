---
title: 'Supermemory 统一记忆系统 - 完整文档'
categories: ['技术']
date: 2026-03-20T03:00:02+0800
draft: false
---
# Supermemory 统一记忆系统 - 完整文档

> 创建时间：2026-03-08
> 最后更新：2026-03-08
> 状态：✅ 生产环境可用

## 📋 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [配置步骤](#配置步骤)
- [使用指南](#使用指南)
- [所有路径](#所有路径)
- [故障排除](#故障排除)
- [技术细节](#技术细节)

---

## 系统概述

Supermemory 统一记忆系统是一个跨平台的 AI 记忆管理解决方案，支持在 Claude Code、OpenClaw（本地）和 OpenClaw（服务器）之间同步记忆。

### 核心特性

- ✅ **多平台支持**: Claude Code + OpenClaw (本地) + OpenClaw (服务器)
- ✅ **自动同步**: 记住信息后自动推送到服务器
- ✅ **双向同步**: 支持本地和服务器的双向数据同步
- ✅ **Markdown 存储**: 便于阅读和版本管理
- ✅ **关键词搜索**: 快速检索已记忆的内容
- ✅ **SSH 安全**: 使用 SSH 别名，避免硬编码 IP

### 使用场景

1. **记住配置信息**: 服务器地址、数据库连接、API 密钥
2. **记住用户偏好**: 编辑器选择、主题设置、工作习惯
3. **记住项目信息**: 技术栈、分支名称、部署流程
4. **临时笔记**: 会议记录、待办事项、灵感想法

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                            │
├──────────────┬──────────────┬──────────────────────────┤
│  Claude Code │ OpenClaw     │    OpenClaw (服务器)     │
│   (Mac 本地)  │  (Mac 本地)   │                          │
└──────┬───────┴──────┬───────┴──────────┬───────────────┘
       │              │                  │
       │ remember.sh  │ supermemory-    │ supermemory.sh
       │              │ remember.sh     │
       └──────────────┴──────────────────┘
                      │
       ┌──────────────┴──────────────┐
       │    记忆存储层                │
       ├──────────────┬──────────────┤
       │ ~/.supermem- │ /root/.super- │
       │ ory/memories│ memory/mem-   │
       │   (本地)     │ ories (服务器)│
       └──────┬───────┴──────────────┘
              │
       ┌──────┴──────────────────────┐
       │    同步层 (SCP over SSH)     │
       │  supermemory-sync.sh         │
       └──────────────────────────────┘
```

### 同步机制

**协议**: SCP (Secure Copy Protocol) over SSH

**方向**:
- **推送**: 本地 → 服务器（每次记住后自动触发）
- **拉取**: 服务器 → 本地（手动或定时执行）
- **双向**: 先拉取后推送（避免冲突）

**安全性**:
- 使用 SSH 密钥认证（`~/.ssh/id_ed25519`）
- SSH 别名配置（`~/.ssh/config` 中的 `server`）
- 不暴露真实 IP 地址

---

## 配置步骤

### 1. SSH 配置（已完成）

确保 `~/.ssh/config` 中有服务器别名：

```bash
Host server
    HostName xxx.xxx.xxx.xxx
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
```

测试连接：
```bash
ssh server "ls -la /root/.supermemory/memories/"
```

### 2. 本地 Mac 配置

#### Claude Code Skill

**路径**: `~/.claude/skills/remember.sh`

**功能**:
- `remember "内容" "标题" "标签"` - 记住信息
- `search "关键词"` - 搜索记忆
- `list [数量]` - 列出最近记忆
- `stats` - 统计信息
- `sync` - 手动同步

**使用示例**:
```bash
# 记住信息
~/.claude/skills/remember.sh remember "用户喜欢 Vim" "用户偏好" "编辑器"

# 搜索记忆
~/.claude/skills/remember.sh search "编辑器"

# 查看统计
~/.claude/skills/remember.sh stats
```

#### OpenClaw Skill（本地）

**路径**: `~/.openclaw/skills/supermemory-remember/`

**文件结构**:
```
supermemory-remember/
├── SKILL.md                    # 技能说明文档
├── supermemory-remember.sh     # 可执行脚本
└── references/                 # 参考文档目录
```

**使用方式**:
```bash
# 在 OpenClaw 中直接说
"记住：今天学习了 AI 配置"
"搜索：配置信息"
"列出最近5条记忆"
```

#### 同步脚本

**路径**: `~/.claude/skills/supermemory-sync.sh`

**功能**:
- `sync` - 双向同步（先拉取后推送）
- `push` - 只推送到服务器
- `pull` - 只从服务器拉取
- `status` - 查看同步状态

**使用示例**:
```bash
# 双向同步
~/.claude/skills/supermemory-sync.sh sync

# 查看状态
~/.claude/skills/supermemory-sync.sh status

# 只推送
~/.claude/skills/supermemory-sync.sh push
```

### 3. 服务器配置

#### Supermemory Skill

**路径**: `/root/.openclaw/skills/supermemory.sh`

**功能**:
- `add "内容" "标题" "标签"` - 添加记忆
- `search "关键词"` - 搜索记忆
- `list` - 列出所有记忆
- `sync` - 同步到服务器（本地）

#### Remember Skill

**路径**: `/root/.openclaw/skills/remember.sh`

**功能**: 同本地版本

**测试**:
```bash
ssh server "/root/.openclaw/skills/remember.sh stats"
```

---

## 使用指南

### 在 Claude Code 中（推荐）

**直接对话**:
```
你：记住：服务器地址是 server，用户名 root
你：记住：数据库 localhost:5432，用户 postgres
你：记住：项目使用 TypeScript，主要分支 main

你：搜索：服务器配置
你：列出最近5条记忆
你：记忆统计
```

**命令行**:
```bash
# 记住信息
~/.claude/skills/remember.sh remember "内容" "标题" "标签"

# 搜索记忆
~/.claude/skills/remember.sh search "关键词"

# 列出记忆
~/.claude/skills/remember.sh list 10

# 查看统计
~/.claude/skills/remember.sh stats

# 手动同步
~/.claude/skills/remember.sh sync
```

### 在 OpenClaw 中（本地）

**语音命令**:
```
"记住：用户喜欢暗色主题"
"搜索：主题配置"
"列出最近记忆"
```

**命令行**:
```bash
~/.openclaw/skills/supermemory-remember/supermemory-remember.sh remember "内容"
~/.openclaw/skills/supermemory-remember/supermemory-remember.sh search "关键词"
```

### 在 OpenClaw 中（服务器）

**SSH 执行**:
```bash
ssh server "/root/.openclaw/skills/remember.sh remember '内容'"
ssh server "/root/.openclaw/skills/remember.sh search '关键词'"
```

### 自动同步

- ✅ **自动触发**: 每次使用 `remember.sh` 记住信息后自动推送
- ✅ **后台执行**: 不阻塞当前操作
- ✅ **手动同步**: 需要时执行 `supermemory-sync.sh sync`

---

## 所有路径

### 本地 Mac

#### Claude Code
```bash
# 记忆存储
~/.supermemory/memories/

# Skills
~/.claude/skills/remember.sh              # AI 记忆（主要）
~/.claude/skills/supermemory.sh           # 完整版
~/.claude/skills/supermemory-sync.sh      # 同步脚本

# 文档
~/.claude/skills/README-REMEMBER.md       # Remember 使用指南
~/.supermemory/README.md                  # 系统说明
~/.supermemory/COMPLETE-SETUP.md          # 完整配置文档
```

#### OpenClaw
```bash
# 记忆存储
~/.supermemory/memories/

# Skill
~/.openclaw/skills/supermemory-remember/
├── SKILL.md                              # 技能文档
├── supermemory-remember.sh               # 执行脚本
└── references/

# 配置
~/.openclaw/openclaw.json                 # OpenClaw 主配置
~/.claude.json                            # Claude MCP 配置
```

### 服务器

```bash
# 记忆存储
/root/.supermemory/memories/

# Skills
/root/.openclaw/skills/supermemory.sh     # Supermemory 完整版
/root/.openclaw/skills/remember.sh        # AI 记忆

# 配置
/root/.openclaw/openclaw.json             # OpenClaw 主配置
/root/.claude.json                        # Claude MCP 配置
```

### SSH 配置（本地 Mac）

```bash
# SSH 配置文件
~/.ssh/config

# 密钥
~/.ssh/id_ed25519                         # 私钥
~/.ssh/id_ed25519.pub                     # 公钥
```

---

## 故障排除

### 问题1: SSH 连接失败

**症状**:
```
ssh: Could not resolve hostname server: nodename nor servname provided
```

**解决方案**:
1. 检查 SSH 配置：`cat ~/.ssh/config | grep -A 5 "Host server"`
2. 测试连接：`ssh server "ls -la /root/.supermemory/"`
3. 检查密钥权限：`chmod 600 ~/.ssh/id_ed25519`

### 问题2: 同步失败

**症状**:
```
scp: /root/.supermemory/memories/: No such file or directory
```

**解决方案**:
```bash
# 在服务器上创建目录
ssh server "mkdir -p /root/.supermemory/memories/"

# 手动同步
~/.claude/skills/supermemory-sync.sh push
```

### 问题3: 权限问题

**症状**:
```
bash: /root/.openclaw/skills/remember.sh: Permission denied
```

**解决方案**:
```bash
# 本地添加执行权限
chmod +x ~/.claude/skills/*.sh
chmod +x ~/.openclaw/skills/supermemory-remember/*.sh

# 服务器添加执行权限
ssh server "chmod +x /root/.openclaw/skills/*.sh"
```

### 问题4: 记忆未保存

**症状**: 使用 `记住` 命令后，文件未创建

**解决方案**:
```bash
# 检查目录权限
ls -la ~/.supermemory/

# 手动创建目录
mkdir -p ~/.supermemory/memories/

# 测试写入
echo "test" > ~/.supermemory/memories/test.md
```

### 问题5: 搜索无结果

**症状**: `search` 命令找不到记忆

**解决方案**:
```bash
# 检查记忆文件
ls -la ~/.supermemory/memories/

# 查看文件内容
cat ~/.supermemory/memories/*.md

# 确认搜索关键词
grep -r "关键词" ~/.supermemory/memories/
```

---

## 技术细节

### 文件格式

**记忆文件模板**:
```markdown
# 标题

**时间**: 2026-03-08 21:30:00
**标签**: AI,OpenClaw,配置

## 内容

记住的内容

---
```

**文件命名规则**:
- 格式：`YYYYMMDD_HHMMSS.md`
- 示例：`20260308_213000.md`
- 优势：时间排序、避免冲突

### 同步原理

**SCP 协议**:
```bash
# 推送（本机 → 服务器）
scp -q ~/.supermemory/memories/*.md server:/root/.supermemory/memories/

# 拉取（服务器 → 本机）
scp -q server:/root/.supermemory/memories/*.md ~/.supermemory/memories/
```

**同步策略**:
1. **双向同步**: 先拉取后推送
2. **避免冲突**: 时间戳命名不会覆盖
3. **增量同步**: 只传输有变化的文件

### 安全考虑

**SSH 别名优势**:
```bash
# ✅ 安全 - 使用别名
ssh server "ls -la"
scp file.txt server:/path/

# ❌ 不安全 - 硬编码 IP
ssh user@example.com -p 2222 "ls -la"
scp file.txt user@example.com:/path/
```

**密钥管理**:
- 私钥：`~/.ssh/id_ed25519`（权限 600）
- 公钥：已添加到服务器 `~/.ssh/authorized_keys`
- 无密码：SSH 密钥认证，无需输入密码

### 性能优化

**当前方案**: SCP
- 优势：简单、可靠、无需额外服务
- 劣势：全量传输、非实时

**可选方案**:

1. **rsync**（推荐）
   ```bash
   # 增量同步，只传输变化的文件
   rsync -avz ~/.supermemory/memories/ server:~/.supermemory/memories/
   ```

2. **Syncthing**（实时）
   - 双向实时同步
   - 冲突自动解决
   - 需要 GUI 配置

3. **NFS/WebDAV**（网络文件系统）
   - 挂载为本地目录
   - 实时访问
   - 配置复杂

---

## 总结

Supermemory 统一记忆系统已经完全配置并测试通过，支持：

- ✅ **Claude Code**: `~/.claude/skills/remember.sh`
- ✅ **OpenClaw (本地)**: `~/.openclaw/skills/supermemory-remember/`
- ✅ **OpenClaw (服务器)**: `/root/.openclaw/skills/remember.sh`
- ✅ **自动同步**: 记住后自动推送
- ✅ **手动同步**: `supermemory-sync.sh sync`
- ✅ **双向同步**: 本地 ↔ 服务器

**当前状态**:
- 本地记忆：6 条
- 服务器记忆：6 条
- 同步状态：✅ 完全同步

**下一步**:
1. 设置定时同步（cron）
2. 配置 rsync 增量同步
3. 集成 Supermemory 云端 API

---

## 附录

### A. 快速命令参考

```bash
# 记住信息
~/.claude/skills/remember.sh remember "内容" "标题" "标签"

# 搜索记忆
~/.claude/skills/remember.sh search "关键词"

# 列出记忆
~/.claude/skills/remember.sh list

# 查看统计
~/.claude/skills/remember.sh stats

# 同步记忆
~/.claude/skills/remember.sh sync
~/.claude/skills/supermemory-sync.sh sync
```

### B. 相关文档

- [Supermemory 使用指南](~/.supermemory/README.md)
- [Remember Skill 文档](~/.claude/skills/README-REMEMBER.md)
- [完整配置文档](~/.supermemory/COMPLETE-SETUP.md)
- [OpenClaw Skill 文档](~/.openclaw/skills/supermemory-remember/SKILL.md)

### C. 联系与支持

如有问题，请查看：
1. 本文档的"故障排除"部分
2. 各个 skill 的帮助命令：`xxx.sh help`
3. 服务器日志：`ssh server "journalctl -u openclaw -f"`

---

**文档版本**: v1.0
**最后更新**: 2026-03-08
**维护者**: AI Assistant
