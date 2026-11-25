---
title: '2026-05-20-CouponAPI解析器大改造'
categories: ["赛博日记"]
date: 2026-11-20T12:39:51+08:00
lastmod: 2026-11-20T12:39:51+08:00
draft: false
---
# 2026年05月20日 赛博日记

> 生成时间：2026-05-20 23:55:02

## 📝 今日概要

**高产突破日。** LLM-api-test-tool 项目从「能跑」进化到「能用」—— Coupon API 改造落地，认证体系从硬编码走向可配置，测试报告从无到有。今天解决的不是单个 Bug，而是一整条链路的打通。

## 🔍 核心技术进展

### 1. Coupon API 大改造 🏗️（来源：claude 会话 · 18:24 起）

今天最重的工作。88 个 POST 接口、7 个 Tag、253 个 Schema —— 不是小打小闹。

**核心模块落地：**
- **swagger_parser.py** — 循环 `$ref` 防护 + 深度上限（max_depth=8），这是踩了坑才加的，原始解析器对自引用 Schema 会直接栈溢出
- **openapi_filter.py** — 按 Tag 筛选 endpoints，配合 **Tag MVP 策略**先打通 1-2 个 tag 验证链路
- **schema_body_builder.py** — 基于 OpenAPI Schema 自动生成请求体（positive/negative/boundary 三种策略）
- **coupon_auth.py** — 鉴权注入：appId/authCode/token 全链路

**策略决策：** 采用 LLM 分批生成 + Rule 模式双轨制。LLM 失败自动降级到 Rule，避免任务直接挂掉。这个降级机制后来证明非常关键——实测中 LLM JSON 输出不稳定，降级救了不少任务。

### 2. 认证体系从硬编码到可配置 🔐（来源：claude 会话 · 多个时段）

设计了三种可切换的认证方案：

| 方案 | 适用场景 | Token 来源 |
|------|---------|-----------|
| ysb-user-sms | 用户域 | 短信登录接口，从 body/Cookie 提取 |
| coupon-static | Coupon 域 | 环境变量静态注入 |
| bearer-password | 通用 | 账号密码获取 Bearer |

**硬核问题：** 实测发现接口返回的 token 在 `Set-Cookie` 里而非 response body，而原来 `auth_token` fixture 只从 JSON 取 token。修复后支持从 body、header、cookie 三路提取，用 JSON 路径 + 正则表达式做 token 定位。

### 3. FastAPI 204 陷阱修复 🐛（来源：cursor 会话 · 18:00）

`AssertionError: Status code 204 must not have a response body` — 表面简单，实际踩了两轮：

- ❌ 第一次：去掉 `-> None`，还留着 `response_class=Response` + `return Response(status_code=204)` → 还是报错
- ✅ 最终：装饰器只保留 `status_code=204`，函数不写返回类型注释，不 return 任何东西

**根因：** FastAPI 0.115 对 204 路由的 body 推断非常严格，`-> None` 也会被当作"声明了一个 response body"。

### 4. 工程化补课 🔧（来源：claude/cursor 会话 · 多个时段）

- **pytest-html 报告**：装了插件还不够，`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 下必须显式写 `-p pytest_metadata.plugin`（不是 `-p metadata`，这个坑卡了一阵）
- **后端热重载**：`--reload --reload-dir app`，只监视 `app/` 目录，否则 `outputs/` 写文件会疯狂触发重启
- **Electron 镜像**：国内环境下 `ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/` 一行解决

### 5. Rules 模式逆向理解 📖（来源：claude 会话 · 16:48）

完整梳理了 Rule 模式的 8 条规则匹配逻辑。结论：**不依赖 LLM**，纯规则驱动，对 OpenAPI 文档做模式匹配。这是一个可控、可预测的基线方案，LLM 是锦上添花，Rule 是兜底保障。

## 💡 深度洞察与经验教训

- **洞察：降级设计是 AI 工程化的核心。** LLM 生成的不确定性不是 Bug 而是 Feature——前提是你有 Rule 模式兜底。今天的 LLM→Rule 自动降级，本质上是把「AI 幻觉」这个风险收敛到了一个可控范围内。这个模式可以推广：任何 AI 驱动的流程都应该有一个确定性的 fallback 路径。

- **教训：204 No Content 在 FastAPI 里是个地雷。** 不光是不能 return body，连 `-> None` 类型注释都算"暗示有 body"。这种隐式约束不看文档根本猜不到，唯一的办法是遇到就记住。今天记了，以后不会再踩。

- **教训：Swagger/OpenAPI 文档质量决定生成质量。** 今天遇到接口文档写的是业务错误码 `40001`，但实际返回 Spring 风格的 `{status: 400, error: "Bad Request"}`——断言对着一个不存在的 `code` 字段去 assert，必然全红。**生成的测试好不好，七分看文档，三分看生成策略。**

- **教训：数据持久化不能后补。** 任务列表放在内存里，重启即丢。认证配置倒是在第一时间落盘了（`data/auth_profiles.json`），但任务元数据没有。这属于架构层面的短视，应该在第一天就定好哪些数据需要持久化。

## 🚀 未来行动设想

- [ ] **任务元数据持久化**：将 `tasks` 列表序列化到 `data/tasks.json`，后端启动时自动加载，避免每次重启都从零开始
- [ ] **断言归一化策略增强**：针对 Spring 风格错误体（无 `code` 字段）做自适应断言生成，不再一刀切地假设所有接口都有业务码信封
- [ ] **Coupon API Tag 全量覆盖**：当前 MVP 只通了 1-2 个 tag，剩余 tag 需逐个验证鉴权和路径参数是否适配

## 📊 自动化统计
- 捕获 Memory 数：2
- 笔记更新数：2

---
> 注：本篇于 2026-11-20 从 git 历史恢复（原版曾被日记生成器覆盖为极简版）
