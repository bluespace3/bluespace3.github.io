# OpenClaw 场景配置指南

本文档介绍如何配置和使用 OpenClaw 的高价值场景，包括 AI 新闻日报、技术新闻聚合、播客自动化等内容生成。

---

## 🎯 场景列表

### 1. AI 新闻日报（已运行） ✅

- **功能**：每天早上 8:00 发送 AI 领域重要新闻
- **状态**：已运行
- **覆盖**：深度 AI 新闻分析（产品发布、融资、研究突破等）
- **频率**：每天 1 次

---

### 2. Multi-Source Tech News Digest（新增） ✅

- **功能**：每天晚上 7:30 发送多源技术新闻汇总
- **状态**：待安装
- **覆盖**：全科技领域（Web3、SaaS、硬件、创业、监管）
- **数据源**：109+ 个来源（RSS、Twitter/X、GitHub、Web 搜索）
- **频率**：每天 1 次

---

### 3. Podcast Production Pipeline（待安装）

- **功能**：自动化播客全流程制作
- **状态**：待安装
- **覆盖**：
  - 嘉宾调研
  - 选题研究
  - 内容大纲生成
  - 节目笔记
  - 封面设计（AI 生成）
  - 社交媒体推广素材生成
- **频率**：按需触发

---

### 4. GitHub Trending Monitor（待安装）

- **功能**：监控 GitHub Trending，发现有价值的开源项目
- **状态**：待安装
- **覆盖**：
  - 实时监控 GitHub Trending
  - 自动 star、watch、fork
  - 按语言、类别筛选
  - 生成项目推荐
- **频率**：按需触发

---

### 5. Goal-Driven Autonomous Tasks（待安装）

- **功能**：目标驱动的自动化任务管理
- **状态**：待安装
- **覆盖**：
  - 目标设定
  - AI 自动规划
  - 每日任务拆解
  - 自动执行
  - 惊喜功能
- **频率**：每天触发

---

## 🚀 配置步骤

### 配置 AI 新闻日报（已运行）

**注意**：此场景已经配置并运行，无需额外配置。

**查看当前配置**：
- 场景名称：`AI新闻日报`
- 调度时间：每天 08:00（Asia/Shanghai）
- 状态：已运行

---

### 配置 Multi-Source Tech News Digest（每天晚上 7:30）

**使用 cron 工具**：

```json
{
  "action": "add",
  "job": {
    "name": "Multi-Source Tech News Digest",
    "schedule": {
      "kind": "cron",
      "expr": "30 19 * * *",
      "tz": "Asia/Shanghai"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "deleteAfterRun": false,
    "payload": {
      "kind": "agentTurn",
      "message": "你是一个专业的技术新闻编辑。请汇总今天的科技新闻，涵盖以下领域：\n\n1. AI/大模型（产品发布、融资、研究突破）\n2. Web3/区块链（DeFi、NFT、基础设施）\n3. SaaS/云服务（产品更新、融资、并购）\n4. 创业（融资、趋势、政策）\n5. 硬件/设备（芯片、手机、可穿戴）\n6. 开发工具（框架、库、IDE）\n\n要求：\n- 覆盖全领域，不要遗漏重要新闻\n- 突出最热门的事件（标注 ⭐⭐⭐⭐⭐）\n- 标注热度等级（⭐⭐⭐⭐、⭐⭐⭐、⭐⭐）\n- 每条新闻包含标题、简要描述、来源链接\n- 总条数控制在 20-25 条\n- 格式清晰，易读，使用 emoji 适当点缀\n- 语言：中文\n- 标题：🔥 技术新闻速递（2026-MM-DD）\n\n不要回复 HEARTBEAT_OK，不要解释你是谁，直接输出新闻摘要。",
      "deliver": true,
      "channel": "qqbot",
      "to": "0482CAA8F5806F99754A5A4EC2832B6F"
    }
  }
}
```

**说明**：
- `expr`: `"30 19 * * *"` 表示每天 19:30（晚上 7:30）
- `tz`: `"Asia/Shanghai"` 时区设置
- `deleteAfterRun`: `false` 表示每天都运行

---

### 配置 Podcast Production Pipeline

**使用 cron 工具**：

```json
{
  "action": "add",
  "job": {
    "name": "Podcast Production Pipeline",
    "schedule": {
      "kind": "at",
      "atMs": 1772437800000 + 86400000"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "deleteAfterRun": true,
    "payload": {
      "kind": "agentTurn",
      "message": "你是一个专业的播客制作人。请帮我完成以下播客制作任务：\n\n任务 1：调研嘉宾\n- 调研 [嘉宾姓名/领域] 的背景、经历、代表作品\n- 生成 10 个有价值的访谈问题\n\n任务 2：选题研究\n- 分析 [主题] 的最新趋势\n- 提供 5 个有深度的选题方向\n\n任务 3：内容大纲\n- 基于 [选题] 生成详细的节目标题\n- 每个节目标题包含：开场白、3-5 个核心讨论点、过渡语、结束语\n\n任务 4：脚本写作\n- 为 [节目标题] 撰写详细的对话脚本\n- 包含：主持人提问、嘉宾回答、互动环节\n- 控制总时长在 30-45 分钟\n\n任务 5：封面设计\n- 设计播客封面图的概念和视觉风格\n- 提供详细的 AI 提示词，用于 Midjourney/DALL-E 等工具生成封面\n\n任务 6：节目笔记\n- 生成详细的节目笔记\n- 包含：时间戳、关键点、资源链接\n\n任务 7：推广素材\n- 生成社交媒体推广文案\n- 包括：Twitter 推文（3 条）、Facebook 帖文（1 条）、Instagram 快拍文案（1 条）\n\n要求：\n- 每个任务都要详细、专业、可直接使用\n- 使用 emoji 适当点缀\n- 标题要吸引人\n- 考虑播客风格和受众偏好\n\n不要回复 HEARTBEAT_OK，不要解释你是谁，直接输出完整的制作计划。",
      "deliver": true,
      "channel": "qqbot",
      "to": "0482CAA8F5806F99754A5A4EC2832B6F"
    }
  }
}
```

**说明**：
- `atMs`: 需要计算具体的毫秒时间戳
- `deleteAfterRun`: `true` 表示只运行一次

---

### 配置 GitHub Trending Monitor

**使用 cron 工具**：

```json
{
  "action": "add",
  "job": {
    "name": "GitHub Trending Monitor",
    "schedule": {
      "kind": "at",
      "atMs": 1772437800000 + 86400000"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "deleteAfterRun": true,
    "payload": {
      "kind": "agentTurn",
      "message": "你是一个开源项目专家。请帮我完成以下 GitHub Trending 监控任务：\n\n任务 1：监控 Trending\n- 访问 GitHub Trending 页面\n- 按语言筛选：Python、JavaScript、TypeScript、Go、Rust\n- 找出过去 24 小时 Trending 的项目\n- 分析项目的技术栈、功能、用途\n\n任务 2：分析项目价值\n- 评估项目的代码质量、社区活跃度（stars、issues、PRs）\n- 识别是否有商业潜力或学习价值\n\n任务 3：生成推荐报告\n- 按类别整理：Web 开发、DevOps、AI/ML、工具\n- 每个项目包含：名称、简介、技术栈、star 数、推荐理由\n\n任务 4：自动行动\n- 生成可以直接使用的 CLI 命令\n  如：`git clone https://github.com/xxx/xxx`\n  `cd xxx && npm install`\n\n任务 5：持续监控设置\n- 提供如何设置持续监控的方案\n  - 使用 GitHub API\n  - 使用 Webhook\n  - 使用第三方服务\n\n要求：\n- 覆盖热门语言和领域\n- 提供可执行的建议\n- 报告格式清晰，易读\n- 使用 emoji 适当点缀\n- 不要回复 HEARTBEAT_OK，不要解释你是谁，直接输出完整的监控报告。",
      "deliver": true,
      "channel": "qqbot",
      "to": "0482CAA8F5806F99754A5A4EC2832B6F"
    }
  }
}
```

---

### 配置 Goal-Driven Autonomous Tasks

**使用 cron 工具**：

```json
{
  "action": "add",
  "job": {
    "name": "Goal-Driven Autonomous Tasks",
    "schedule": {
      "kind": "cron",
      "expr": "0 8 * * *",
      "tz": "Asia/Shanghai"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "deleteAfterRun": false,
    "payload": {
      "kind": "agentTurn",
      "message": "你是一个目标驱动的任务管理助手。请帮我完成以下任务管理：\n\n任务 1：目标设定\n- 分析用户当前的项目和任务\n- 识别优先级（紧急、重要、中等、低）\n- 生成今天的目标列表（3-5 个目标）\n- 每个目标包含：描述、预期成果、时间预算\n\n任务 2：任务拆解\n- 将每个目标拆解为可执行的子任务\n- 子任务应该是具体的、可衡量的\n- 设置时间估算和依赖关系\n\n任务 3：执行追踪\n- 生成每日任务清单\n- 包含：任务名称、优先级、预计时间、负责人\n- 提供进度追踪方法\n\n任务 4：问题识别\n- 识别可能阻碍任务完成的因素\n- 提供解决方案和预防措施\n\n任务 5：惊喜功能\n- 生成一个小的惊喜任务或奖励机制\n  - 激励用户完成任务\n  - 增加任务的趣味性\n\n要求：\n- 目标要具体、可达成\n- 任务拆解要详细\n- 使用项目管理最佳实践\n- 考虑用户的工作节奏和偏好\n- 提供清晰的时间线\n- 使用 emoji 适当点缀\n- 标题：🎯 目标驱动任务管理（2026-MM-DD）\n\n不要回复 HEARTBEAT_OK，不要解释你是谁，直接输出完整的任务管理计划。",
      "deliver": true,
      "channel": "qqbot",
      "to": "0482CAA8F5806F99754A5A4EC2832B6F"
    }
  }
}
```

**说明**：
- `expr`: `"0 8 * * *"` 表示每天 08:00（早上 8 点）
- `deleteAfterRun`: `false` 表示每天都运行

---

## 🛠️ Cron 工具使用方法

### 基本命令

在 OpenClaw 中使用 cron 工具：

```
/cron <action>
```

**支持的 action**：
- `add`: 添加新任务
- `list`: 列出所有任务
- `remove`: 删除任务
- `toggle`: 暂停/恢复任务

### Payload 格式

所有场景的 payload 都必须包含以下字段：

```json
{
  "kind": "agentTurn",
  "message": "你的任务描述...",
  "deliver": true,
  "channel": "qqbot",
  "to": "0482CAA8F5806F99754A5A4EC2832B6F"
}
```

**关键字段说明**：
- `kind`: 必须是 `"agentTurn"`（不要用 `"systemEvent"`，不会发消息）
- `message`: 任务的具体描述
- `deliver`: 必须是 `true`（是否投递到渠道）
- `channel`: 投递渠道（`"qqbot"`、`"wechat"` 等）
- `to`: 接收者 ID

---

## 📋 场景使用建议

### 组合使用场景

#### 场景1：技术内容创作者

**配置**：
- ✅ AI 新闻日报（每天早上 8:00）- 深度分析
- ✅ Multi-Source Tech News Digest（每天晚上 7:30）- 广度覆盖
- ✅ GitHub Trending Monitor（每周运行）- 发现新工具

**效果**：
- 早上：了解 AI 领域深度动态
- 晚上：掌握全科技领域广度动态
- 每周：发现新工具和项目

---

#### 场景2：内容自动化生产

**配置**：
- ✅ Goal-Driven Autonomous Tasks（每天早上 8:00）- 任务规划
- ✅ Podcast Production Pipeline（按需）- 内容生产
- ✅ AI 新闻日报（每天早上 8:00）- 行业资讯

**效果**：
- 自动规划每天的工作
- 按需生产播客内容
- 同步了解行业动态

---

#### 场景3：开源项目关注者

**配置**：
- ✅ Multi-Source Tech News Digest（每天晚上 7:30）- 技术趋势
- ✅ GitHub Trending Monitor（每周运行）- 项目发现
- ✅ AI 新闻日报（每天早上 8:00）- 开发动态

**效果**：
- 实时掌握技术趋势
- 发现高质量开源项目
- 了解开发工具更新

---

### 调度建议

**每日时间线**：

| 时间 | 场景 | 说明 |
|------|------|------|
| 08:00 | AI 新闻日报 + Goal-Driven Tasks | 深度分析 + 任务规划 |
| 08:30 | GitHub Trending Monitor（可选） | 项目发现 |
| 19:30 | Multi-Source Tech News Digest | 技术新闻汇总 |
| 按需 | Podcast Production Pipeline | 播客制作 |

**避免冲突**：
- 同一时间不要运行太多任务
- 保留时间间隔（至少 30 分钟）

---

## 🎯 快速开始

### 1. 配置 Multi-Source Tech News Digest（每天晚上 7:30）

在 OpenClaw 中输入：

```
/cron add
```

然后粘贴上面的配置（包含时间、payload 等信息）

### 2. 配置 Podcast Production Pipeline（按需）

当需要制作播客时，在 OpenClaw 中输入：

```
/cron add
```

然后粘贴上面的 Podcast 配置（需要替换嘉宾、主题等信息）

### 3. 配置 GitHub Trending Monitor（每周运行）

每周一早上 9:00 运行：

```
/cron add
```

然后粘贴上面的 GitHub Trending 配置

### 4. 配置 Goal-Driven Autonomous Tasks（每天早上 8:00）

在 OpenClaw 中输入：

```
/cron add
```

然后粘贴上面的 Goal-Driven 配置

---

## 📊 当前配置总结

| 场景 | 状态 | 发送时间 |
|------|------|----------|
| AI 新闻日报 | ✅ 已运行 | 每天 08:00 |
| Multi-Source Tech News Digest | ⏳ 待配置 | 每天 19:30 |
| Podcast Production Pipeline | ⏳ 待配置 | 按需 |
| GitHub Trending Monitor | ⏳ 待配置 | 按需 |
| Goal-Driven Autonomous Tasks | ⏳ 待配置 | 每天 08:00 |

---

## 💡 最佳实践

### 1. 任务提示词优化

- 明确任务目标和范围
- 提供清晰的输出格式要求
- 指定质量标准和限制

### 2. 时间管理

- 合理安排任务执行时间
- 避免任务冲突
- 预留足够的缓冲时间

### 3. 结果验证

- 检查输出是否完整
- 验证可执行性
- 评估任务完成质量

### 4. 持续优化

- 根据实际效果调整提示词
- 优化任务调度
- 移除不常用的场景

---

## 🆘 问题排查

### Cron 任务没有执行

**检查清单**：
- [ ] 确认任务已成功添加：`/cron list`
- [ ] 检查时间戳是否正确
- [ ] 检查时区设置是否为 "Asia/Shanghai"
- [ ] 检查 payload 格式是否正确
- [ ] 确认 channel 和 to 是否正确

### 消息没有收到

**检查清单**：
- [ ] 确认 OpenClaw 服务正常运行
- [ ] 检查微信/QQ 网关连接状态
- [ ] 验证消息渠道配置
- [ ] 查看是否有错误日志

---

## 📚 相关资源

- **OpenClaw 文档**: https://docs.openclaw.ai/
- **Cron 工具文档**: `/root/.openclaw/extensions/qqbot/skills/qqbot-cron/SKILL.md`
- **场景集合**: https://github.com/hesamsheikh/awesome-openclaw-usecases

---

## 🎯 总结

本文档介绍了 5 个高价值场景的配置和使用方法：

1. ✅ AI 新闻日报（已运行）
2. 🆕 Multi-Source Tech News Digest（每天晚上 7:30）
3. 🆕 Podcast Production Pipeline（按需）
4. 🆕 GitHub Trending Monitor（按需）
5. 🆕 Goal-Driven Autonomous Tasks（每天早上 8:00）

通过合理配置和组合使用这些场景，可以显著提升个人效率和信息获取能力。

---

**文档版本**: 1.0
**最后更新**: 2026-03-02
**维护者**: OpenClaw 社区
