---
title: '【教程】Openclaw部署、使用、skill与三大实用玩法-Xuan酱-0305'
categories: ['openclaw']
date: 2026-03-09T00:38:42+0800
draft: false
---
# 【教程】Openclaw部署、使用、skill与三大实用玩法-Xuan酱-0305

本文档为Xuan酱 2026.3.5《OpenClaw 3大超实用玩法》视频配套教程文档
全平台@Xuan酱，关注我，和我一起探索AI的更多玩法

(注：此处省略部分非核心图片/辅助内容，完整内容见飞书文档)

## 写在前面
养龙虾的经验总结：
1. 模型能力很关键，简单任务用笨模型，复杂任务用聪明模型。
2. 上下文记忆碎片化，建议多养几只龙虾各司其职。
3. 逐步安装 Skill，不要一口气装太多。

## 部署教程
- 云服务器部署：火山引擎、腾讯云、阿里云、百度智能云均有教程。
- 本地部署：推荐 Mac。

## 环境准备
- 安装 Homebrew, Node.js v22, npm。

## 安装 Openclaw
- `curl -fsSL https://openclaw.ai/install.sh | bash`
- 初始化向导 `openclaw onboard`。

## 配置
- 飞书机器人对接：创建企业自建应用，添加机器人能力，配置凭据，开启长连接接收事件。

## 常用指令
- `openclaw gateway start` (启动服务)
- `openclaw dashboard` (Web UI)
- `openclaw tui` (终端界面)
- `openclaw gateway restart` (重启)
- `openclaw update` (更新)

## Skill 安装建议
- 优先级推荐：
  1. Skill Vetter (安全审计)
  2. Tavily / SerpAPI (联网)
  3. Browser / Playwright (自动化)
  4. Code Interpreter (生产力引擎)

## 其他
- 实用玩法：收藏管理、资讯收集、日程管理。
