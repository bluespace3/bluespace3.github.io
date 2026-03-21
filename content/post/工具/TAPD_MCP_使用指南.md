---
title: 'TAPD_MCP_使用指南'
categories: ["工具"]
date: 2026-03-20T11:50:13+08:00
lastmod: 2026-03-20T11:50:13+08:00
draft: false
---
# TAPD MCP 服务器使用指南

## 概述

`mcp-server-tapd` 是一个 Model Context Protocol (MCP) 服务器，用于与 TAPD（Tencent Agile Product Development）项目管理系统进行集成。

## 前提条件

1. ✅ MCP 服务器已配置在 `C:\Users\Administrator\.claude.json` 中
2. ✅ 访问令牌已配置：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
3. ⚠️ **需要重启 Claude Code** 使配置生效

## 可用工具列表（共 38 个）

### 📋 项目和工作区管理
- `get_user_participant_projects` - 获取用户参与的项目列表
- `get_workspace_info` - 获取工作区信息
- `get_iterations` - 获取迭代列表
- `create_iteration` - 创建迭代
- `update_iteration` - 更新迭代

### 📝 需求和任务管理
- `get_stories_or_tasks` - 获取需求或任务
- `get_story_or_task_count` - 获取需求或任务数量
- `create_story_or_task` - 创建需求或任务
- `update_story_or_task` - 更新需求或任务
- `get_stories_fields_lable` - 获取需求字段标签
- `get_stories_fields_info` - 获取需求字段信息

### 🐛 缺陷管理
- `get_bug` - 获取缺陷
- `get_bug_count` - 获取缺陷数量
- `create_bug` - 创建缺陷
- `update_bug` - 更新缺陷
- `get_related_bugs` - 获取相关缺陷

### 💬 评论管理
- `get_comments` - 获取评论
- `create_comments` - 创建评论
- `update_comments` - 更新评论

### 📎 附件和媒体
- `get_entity_attachments` - 获取实体附件
- `get_image` - 获取图片

### 🔧 字段和配置
- `get_entity_custom_fields` - 获取实体自定义字段
- `get_workitem_types` - 获取工作项类型

### 🔄 工作流管理
- `get_workflows_all_transitions` - 获取工作流所有转换
- `get_workflows_status_map` - 获取工作流状态映射
- `get_workflows_last_steps` - 获取工作流最后步骤

### 🧪 测试用例管理
- `create_or_update_tcases` - 创建或更新测试用例
- `create_tcases_batch` - 批量创建测试用例
- `get_tcases` - 获取测试用例

### 📖 Wiki 管理
- `create_wiki` - 创建 Wiki
- `update_wiki` - 更新 Wiki
- `get_wiki` - 获取 Wiki

### ✅ 待办和工时
- `get_todo` - 获取待办事项
- `add_timesheets` - 添加工时
- `update_timesheets` - 更新工时
- `get_timesheets` - 获取工时

### 🚀 发布和代码
- `get_release_info` - 获取发布信息
- `get_commit_msg` - 获取提交消息

### 🤖 关系和消息
- `entity_relations` - 实体关系
- `send_qiwei_message` - 发送企业微信消息

## 使用方法

### 方法 1：通过 Claude Code 直接使用（推荐）

重启 Claude Code 后，你可以直接在对话中要求使用这些工具：

```
请帮我获取 TAPD 中我参与的项目列表
```

```
请查询 workspace_id 为 12345 的项目中，状态为"进行中"的所有需求
```

```
请在 TAPD 中创建一个新需求，标题是"实现登录功能"
```

### 方法 2：了解工具参数

如果需要了解具体工具的参数，可以询问：

```
请告诉我 get_stories_or_tasks 工具需要哪些参数
```

## 常见使用场景

### 场景 1：获取项目列表
```
请使用 get_user_participant_projects 获取我参与的所有 TAPD 项目
```

### 场景 2：查询需求
```
请查询项目 ID 为 12345 中的所有需求，只查询前 10 条
```

### 场景 3：创建需求
```
请在项目 12345 中创建一个需求：
- 标题：实现用户登录功能
- 描述：包括手机号登录和微信登录
- 优先级：高
```

### 场景 4：更新任务状态
```
请将任务 ID 67890 的状态更新为"已完成"
```

### 场景 5：获取自定义字段
```
请先获取项目 12345 中需求的自定义字段配置
```

## 重要提示

1. **获取 workspace_id**：大多数操作需要先调用 `get_user_participant_projects` 获取项目 ID
2. **自定义字段**：使用自定义字段前，必须先调用 `get_entity_custom_fields` 获取字段配置
3. **分页查询**：获取列表时建议使用 `limit` 参数限制返回数量
4. **状态查询**：支持使用中文状态名称或状态别名

## 工具命名规范

在 Claude Code 中，这些工具会以 `mcp__mcp-server-tapd__` 前缀出现，例如：
- `mcp__mcp-server-tapd__get_user_participant_projects`
- `mcp__mcp-server-tapd__get_stories_or_tasks`
- `mcp__mcp-server-tapd__create_story_or_task`

## 故障排查

如果工具不可用：
1. 确认已重启 Claude Code
2. 检查 `.claude.json` 中的配置是否正确
3. 确认访问令牌是否有效
4. 查看错误消息获取详细信息

## 配置位置

- **配置文件**：`C:\Users\Administrator\.claude.json`
- **服务器名称**：`mcp-server-tapd`
- **类型**：stdio
- **命令**：uvx mcp-server-tapd

## 下一步

1. **重启 Claude Code**
2. **尝试获取项目列表**：
   ```
   请帮我获取 TAPD 中我参与的项目列表
   ```
3. **根据返回的项目 ID 进行进一步操作**

---

*最后更新：2026-03-20*
*TAPD MCP 服务器版本：1.26.0*
