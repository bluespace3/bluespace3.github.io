---
title: 'xiaomi-speaker-openclaw-integration'
categories: ["xiaomi-speaker-openclaw-integration.md"]
date: 2026-03-04T02:48:21+08:00
lastmod: 2026-03-04T02:48:21+08:00
---
# OpenClaw 接入小米音响研究方案

## 研究结论

OpenClaw 目前**没有原生**的小米音响集成，但可以通过以下几种方式实现接入：

---

## 方案对比

### 方案1：使用 miio 库（⭐ 推荐）

**优点：**
- 直接控制小米设备，响应快
- 轻量级，无需额外系统
- 完全开源，MIT 许可证
- 支持大多数小米生态设备

**缺点：**
- 需要自己编写集成代码
- 需要获取设备 Token
- 维护成本

**实现方式：**

1. **安装 miio 库**
```bash
npm install miio
```

2. **获取小米音响信息**
```javascript
const miio = require('miio');

// 发现设备
miio.devices().then(devices => {
  devices.on('available', device => {
    console.log('Found:', device.model);
  });
});

// 连接设备
const speaker = await miio.device({
  address: '192.168.x.x',  // 小米音响 IP
  token: 'token_as_hex'      // 设备 Token
});
```

3. **创建 OpenClaw 技能/插件**
   - 在 `~/.openclaw/workspace/skills/` 创建新技能
   - 封装小米音响控制逻辑
   - 提供简洁的命令接口

---

### 方案2：Home Assistant 中间件

**优点：**
- Home Assistant 生态成熟，设备支持完善
- 可视化界面配置
- 社区活跃，问题易解决
- 支持自动化和场景

**缺点：**
- 需要额外部署 Home Assistant
- 架构更复杂
- 资源占用较大

**实现方式：**

```
┌─────────────┐      HTTP API      ┌─────────────────┐
│  OpenClaw   │ ────────────────> │ Home Assistant  │
│  (Assistant) │                   │   (Hub)         │
└─────────────┘                   └─────────────────┘
                                         │
                                         │ miio/Zigbee
                                         ▼
                                  ┌─────────────┐
                                  │ 小米音响    │
                                  └─────────────┘
```

**步骤：**
1. 部署 Home Assistant（推荐 Docker）
2. 添加小米网关/音响集成
3. 启用 Home Assistant REST API
4. 在 OpenClaw 中创建 HTTP 请求工具

---

### 方案3：Matter/Thread 生态（未来方案）

小米正在逐步支持 Matter 协议，未来可能：
- 通过 Matter 控制小米音响
- OpenClaw 添加 Matter 支持
- 与其他智能家居平台互通

**当前状态：** 部分小米设备已支持 Matter，但音响类设备支持有限

---

## 推荐实施路径

### 阶段1：验证可行性（1-2天）
1. 安装 miio 库测试连接
2. 获取小米音响 Token
3. 测试基本控制（播放/暂停/音量）
4. 评估延迟和稳定性

### 阶段2：开发集成（3-5天）
1. 创建 OpenClaw 技能封装
2. 定义命令接口（如：`/speaker play`, `/speaker stop`）
3. 实现错误处理和状态查询
4. 测试语音指令集成

### 阶段3：功能完善（持续优化）
1. 支持播放列表控制
2. 集成音乐服务（网易云音乐、QQ音乐等）
3. 场景化控制（早晨模式、睡眠模式）
4. 多设备支持

---

## 技术细节

### 获取小米音响 Token

**方法1：使用 miio CLI**
```bash
npm install -g miio
miio discover
miio tokens  # 查看已存储的 Token
```

**方法2：抓包分析**
1. 使用 tcpdump 或 Wireshark 抓取局域网流量
2. 连接音响时查看握手包
3. 提取 Token（32位十六进制字符串）

**方法3：小米设备调试**
- 部分设备可通过调试接口获取
- 需要 Root 权限和开发者模式

### 小米音响常用控制命令

```javascript
// 播放/暂停
await speaker.call('play', ['']);  // 播放
await speaker.call('pause', []);   // 暂停

// 音量控制
await speaker.setVolume(50);       // 设置音量 0-100

// 播放指定内容
await speaker.call('player_play', [
  'http://example.com/music.mp3'
]);

// 状态查询
const status = await speaker.status();
console.log(status);  // { power: true, volume: 50, ... }
```

---

## OpenClaw 技能示例

### 创建技能目录结构

```
~/.openclaw/workspace/skills/xiaomi-speaker/
├── SKILL.md
├── package.json
├── index.js
└── README.md
```

### SKILL.md

```markdown
# 小米音响控制技能

## 功能
控制小米小爱音响的播放、音量、播放列表等

## 命令
- `play` - 播放音乐
- `pause` - 暂停
- `volume [0-100]` - 设置音量
- `next` - 下一首
- `previous` - 上一首

## 依赖
- miio 库
- 小米音响设备 Token
```

### index.js（简化示例）

```javascript
const miio = require('miio');
let speaker = null;

async function init() {
  if (!speaker) {
    speaker = await miio.device({
      address: process.env.SPEAKER_IP || '192.168.x.x',
      token: process.env.SPEAKER_TOKEN || 'token'
    });
  }
  return speaker;
}

async function play() {
  const device = await init();
  await device.call('play', ['']);
  return '开始播放';
}

async function pause() {
  const device = await init();
  await device.call('pause', []);
  return '已暂停';
}

async function setVolume(level) {
  const device = await init();
  await device.setVolume(level);
  return `音量设置为 ${level}`;
}

module.exports = { play, pause, setVolume };
```

---

## 配置 OpenClaw

在 `~/.openclaw/openclaw.json` 中添加技能配置：

```json
{
  "skills": {
    "xiaomi-speaker": {
      "enabled": true,
      "config": {
        "speakerIp": "192.168.x.x",
        "speakerToken": "your_token_here"
      }
    }
  }
}
```

---

## 注意事项

### 安全性
- Token 是敏感信息，不要泄露
- 仅在局域网内使用，避免暴露到公网
- 建议使用防火墙限制访问

### 稳定性
- 小米音响固件更新可能改变协议
- 建议测试不同型号的兼容性
- 实现错误重试机制

### 合规性
- 仅控制自己拥有的设备
- 遵守小米服务条款
- 用于个人学习目的

---

## 扩展方向

1. **语音指令集成**：通过 OpenClaw 的语音控制功能
2. **音乐服务**：对接网易云音乐、QQ音乐 API
3. **场景自动化**：结合 OpenClaw 的 cron 功能
4. **多设备管理**：支持多个小米音响
5. **状态同步**：与智能家居系统联动

---

## 参考资料

- [miio GitHub](https://github.com/aholstenson/miio)
- [小米 IoT 文档](https://iot.mi.com)
- [OpenClaw 技能开发](https://docs.openclaw.ai/tools/creating-skills)
- [Home Assistant 小米集成](https://www.home-assistant.io/integrations/xiaomi)

---

**最后更新：** 2025-06-20  
**状态：** 研究完成，待实施验证
