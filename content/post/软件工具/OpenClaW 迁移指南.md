---
title: 'OpenClaW 迁移指南'
categories: ["软件工具"]
date: 2026-04-06T21:21:10+08:00
lastmod: 2026-04-06T21:21:10+08:00
draft: false
---
# OpenClaW 迁移指南

> **创建时间**: 2026-04-06  
> **适用范围**: OpenClaW 管理平台迁移  
> **核心目标**: 零配置丢失、零记忆丢失、零功能中断

---

## 📋 目录

1. [OpenClaW 架构理解](#openclaw 架构理解)
2. [迁移前准备](#迁移前准备)
3. [OpenClaW 组件备份](#openclaw 组件备份)
4. [工作空间迁移](#工作空间迁移)
5. [新环境搭建](#新环境搭建)
6. [配置恢复与验证](#配置恢复与验证)
7. [常见问题解决](#常见问题解决)

---

## 🏗️ OpenClaW 架构理解

### 1.1 核心组件
OpenClaW 由以下关键部分组成：

- **Gateway**: 核心管理服务，处理所有通信
- **Workspace**: 工作空间目录，包含所有记忆、配置和对话历史
- **Skills**: 技能模块，提供扩展功能
- **Plugins**: 插件系统，增强功能
- **Memory**: 记忆文件，存储长期和短期记忆

### 1.2 目录结构
```
~/.openclaw/
├ workspace/              # 核心工作空间（最重要！）
│  ├ AGENTS.md           # 主配置
│  ├ SOUL.md             # 角色设定
│  ├ MEMORY.md           # 长期记忆
│  ├ memory/             # 每日记忆文件
│  ├ TOOLS.md            # 工具配置
│  ├ USER.md             # 用户信息
│  └ ...其他配置文件
├ gateway/                # Gateway 服务配置
├ plugins/                # 插件目录
├ skills/                 # 技能目录
├ config/                 # 全局配置
└ .env                    # 环境变量
```

---

## 🚀 迁移前准备

### 2.1 检查清单
- [ ] 确认旧 VPS 和 新 VPS 的磁盘空间
- [ ] 确认 Node.js 版本（OpenClaW 依赖）
- [ ] 确认 Docker 是否使用（如果使用了）
- [ ] 检查所有 API 密钥和敏感配置
- [ ] 记录当前 Gateway 状态

### 2.2 识别运行状态
在旧 VPS 上执行：

```bash
# 查看 OpenClaW 进程
ps aux | grep openclaw

# 检查 Gateway 状态
openclaw gateway status

# 查看工作空间位置
echo $CLAUDE_PLUGIN_ROOT
echo $OPENCLAW_WORKSPACE

# 查看配置文件
ls -la ~/.openclaw/workspace/
ls -la ~/.openclaw/config/
ls -la ~/.openclaw/gateway/
```

---

## 📦 OpenClaW 组件备份

### 3.1 备份工作空间（核心）
```bash
# 找到工作空间路径
export WORKSPACE_PATH=$(echo $CLAUDE_PLUGIN_ROOT | sed 's|/plugins/.*||')
echo "WorkSpace Path: $WORKSPACE_PATH"

# 备份完整工作空间
tar czvf openclaw_workspace_backup.tar.gz \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=logs \
  $WORKSPACE_PATH

# 或者使用 rsync（支持增量）
rsync -avzP \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=logs \
  $WORKSPACE_PATH/ \
  ~/backup/openclaw_workspace/
```

### 3.2 备份配置文件
```bash
# 备份 Gateway 配置
cp -r ~/.openclaw/gateway ~/backup/openclaw_gateway_config/

# 备份全局配置
cp -r ~/.openclaw/config ~/backup/openclaw_config/

# 备份环境变量
cp ~/.env ~/.env_backup.txt

# 备份插件目录
cp -r ~/.openclaw/plugins ~/backup/openclaw_plugins/

# 备份技能目录
cp -r ~/.openclaw/skills ~/backup/openclaw_skills/
```

### 3.3 备份记忆文件
```bash
# 备份 memory 目录（每日记忆）
tar czvf memory_backup.tar.gz ~/.openclaw/workspace/memory/

# 备份长期记忆
cp ~/.openclaw/workspace/MEMORY.md ~/backup/MEMORY_backup.md

# 备份所有重要配置文件
cp ~/.openclaw/workspace/*.md ~/backup/
```

### 3.4 备份 API 密钥和敏感信息
```bash
# 导出环境变量（脱敏）
env | grep -E "(API_|KEY_|TOKEN_|SECRET_)" > api_keys_backup.txt

# 或使用 openclaw 命令导出
openclaw config list > config_backup.txt

# 备份敏感文件（如果存在）
find ~/.openclaw -name "*.key" -o -name "*.token" -o -name "*secret*" | xargs cp -t ~/backup/
```

### 3.5 备份 Gateway 服务状态
```bash
# 导出 Gateway 配置
openclaw gateway dump > gateway_config.yaml

# 检查活跃连接
openclaw connection list > connections_backup.txt

# 记录服务端口
netstat -tlnp | grep openclaw
```

---

## 🗄 工作空间迁移

### 4.1 传输工作空间文件
```bash
# 方法 A：使用 rsync（推荐，支持断点续传）
rsync -avzP \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=logs \
  $WORKSPACE_PATH/ \
  user@new_vps:~/backup/openclaw_workspace/

# 方法 B：使用 tar 打包传输
tar czvf openclaw_workspace.tar.gz $WORKSPACE_PATH
scp openclaw_workspace.tar.gz user@new_vps:~/backup/

# 方法 C：使用 scp 传输记忆文件
scp -r ~/.openclaw/workspace/memory user@new_vps:~/backup/
scp ~/.openclaw/workspace/MEMORY.md user@new_vps:~/backup/
```

### 4.2 验证传输完整性
```bash
# 在新机器上检查文件
cd ~/backup/openclaw_workspace
ls -la

# 检查记忆文件完整性
find memory/ -name "*.md" | wc -l

# 检查配置文件
ls -la *.md

# 对比文件大小
stat ~/.openclaw/workspace/MEMORY.md
stat ~/backup/MEMORY_backup.md
```

---

## 🏗️ 新环境搭建

### 5.1 安装 Node.js（如果尚未安装）
```bash
# 安装 Node.js 18 LTS（推荐）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证版本
node -v
npm -v

# 安装 PM2（进程管理）
sudo npm install -g pm2
```

### 5.2 安装 OpenClaW CLI
```bash
# 全局安装 OpenClaW（如果需要使用 CLI）
sudo npm install -g openclaw

# 验证安装
openclaw --version

# 查看帮助
openclaw help
```

### 5.3 设置工作空间目录
```bash
# 创建工作空间目录
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/gateway
mkdir -p ~/.openclaw/plugins
mkdir -p ~/.openclaw/skills

# 解压工作空间（如果使用 tar 备份）
cd ~/backup
tar xzf openclaw_workspace.tar.gz -C ~/.openclaw/workspace

# 或使用 rsync 传输的文件
rsync -avzP ~/backup/openclaw_workspace/ ~/.openclaw/workspace/

# 设置权限（关键步骤！）
sudo chown -R $USER:$USER ~/.openclaw
sudo chmod -R 755 ~/.openclaw
sudo chmod 600 ~/.openclaw/workspace/MEMORY.md 2>/dev/null || true
```

### 5.4 恢复配置文件
```bash
# 恢复 Gateway 配置
cp -r ~/backup/openclaw_gateway_config/* ~/.openclaw/gateway/

# 恢复全局配置
cp -r ~/backup/openclaw_config/* ~/.openclaw/config/

# 恢复环境变量
cp ~/.env_backup.txt ~/.env

# 恢复插件
cp -r ~/backup/openclaw_plugins/* ~/.openclaw/plugins/

# 恢复技能
cp -r ~/backup/openclaw_skills/* ~/.openclaw/skills/
```

### 5.5 恢复 API 密钥和敏感信息
```bash
# 重新设置敏感环境变量
export API_KEY=[您的 API 密钥]
export TOKEN=[您的 Token]
# ... 设置其他必要的环境变量

# 写入 .env 文件
cat >> ~/.env << EOF
API_KEY=[您的 API 密钥]
TOKEN=[您的 Token]
# ... 其他配置
EOF

chmod 600 ~/.env
```

---

## 🔄 配置恢复与验证

### 6.1 初始化 Gateway 服务
```bash
# 启动 Gateway
openclaw gateway start

# 检查状态
openclaw gateway status

# 查看详细日志
openclaw gateway logs --lines 50
```

### 6.2 验证工作空间
```bash
# 检查工作空间加载
ls -la ~/.openclaw/workspace/

# 检查记忆文件
ls -la ~/.openclaw/workspace/memory/

# 验证配置文件
cat ~/.openclaw/workspace/AGENTS.md | head -20
cat ~/.openclaw/workspace/MEMORY.md | head -20

# 测试工作空间功能
openclaw workspace list
```

### 6.3 验证技能插件
```bash
# 检查技能加载
openclaw skills list

# 检查插件状态
openclaw plugins list

# 测试技能功能
openclaw skills test
```

### 6.4 验证连接
```bash
# 检查连接状态
openclaw connection list

# 测试连接健康
openclaw connection health

# 查看连接日志
openclaw connection logs
```

### 6.5 测试核心功能
```bash
# 测试记忆读取
openclaw memory read --query "测试记忆是否正常工作"

# 测试技能调用
openclaw skills run --skill search --query "测试搜索技能"

# 测试 Gateway 响应
curl -X POST http://localhost:PORT/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "测试连接"}'
```

---

## ✅ 验证检查清单

### 基础验证
- [ ] Gateway 服务成功启动
- [ ] 工作空间目录完整
- [ ] 所有记忆文件正确恢复
- [ ] 配置文件加载成功
- [ ] 环境变量设置正确
- [ ] API 密钥已配置

### 功能验证
- [ ] 记忆读取功能正常
- [ ] 技能调用成功
- [ ] 插件加载正常
- [ ] 网络连接正常
- [ ] 对话历史可读取
- [ ] 配置修改可保存

### 性能验证
- [ ] 响应速度正常
- [ ] 无内存泄漏
- [ ] 无异常错误日志
- [ ] 服务稳定运行

---

## ❗ 常见问题解决

### 问题 1：Gateway 启动失败
**症状**: `openclaw gateway start` 报错  
**解决**:
```bash
# 查看详细错误
openclaw gateway logs --lines 100

# 检查端口占用
sudo netstat -tlnp | grep openclaw

# 检查配置语法
openclaw gateway validate

# 重置 Gateway 配置
rm -rf ~/.openclaw/gateway/*
openclaw gateway init

# 重新导入配置
cp -r ~/backup/openclaw_gateway_config/* ~/.openclaw/gateway/
```

### 问题 2：工作空间加载失败
**症状**: 无法读取记忆文件  
**解决**:
```bash
# 检查目录权限
ls -la ~/.openclaw/workspace/
ls -la ~/.openclaw/workspace/memory/

# 修复权限
sudo chown -R $USER:$USER ~/.openclaw
sudo chmod -R 755 ~/.openclaw

# 检查文件完整性
find ~/.openclaw/workspace/memory -name "*.md" | wc -l

# 重新解压工作空间
tar xzf ~/backup/openclaw_workspace.tar.gz -C ~/.openclaw/workspace
```

### 问题 3：API 密钥无效
**症状**: API 调用失败  
**解决**:
```bash
# 检查环境变量
env | grep API
env | grep KEY

# 重新设置环境变量
export API_KEY=[正确的 API 密钥]

# 更新 .env 文件
nano ~/.env
# 添加正确的密钥

# 重启 Gateway
openclaw gateway restart
```

### 问题 4：技能加载失败
**症状**: 技能无法调用  
**解决**:
```bash
# 检查技能目录
ls -la ~/.openclaw/skills/

# 检查技能配置
openclaw skills list

# 重新安装技能
openclaw skills install --all

# 检查技能日志
openclaw skills logs --lines 50
```

### 问题 5：端口被占用
**症状**: Gateway 无法启动  
**解决**:
```bash
# 检查端口占用
sudo netstat -tlnp | grep [PORT]

# 查找进程
sudo lsof -i :[PORT]

# 结束进程
sudo kill -9 [PID]

# 或更改端口
nano ~/.openclaw/config/gateway.yaml
# 修改 port 配置

# 重启服务
openclaw gateway restart
```

---

## 📊 迁移监控脚本

### 7.1 创建监控脚本
```bash
cat > ~/openclaw_migration_check.sh << 'EOF'
#!/bin/bash

echo "=== OpenClaW 迁移验证 ==="

# 检查 Gateway 状态
echo "1. Gateway 状态:"
openclaw gateway status

# 检查工作空间
echo -e "\n2. 工作空间文件数:"
find ~/.openclaw/workspace -name "*.md" | wc -l

# 检查记忆文件
echo -e "\n3. 记忆文件列表:"
ls -la ~/.openclaw/workspace/memory/ | wc -l

# 检查技能
echo -e "\n4. 已加载技能:"
openclaw skills list | head -10

# 检查插件
echo -e "\n5. 已加载插件:"
openclaw plugins list | head -10

# 检查连接
echo -e "\n6. 活跃连接:"
openclaw connection list

# 检查日志
echo -e "\n7. 最近错误:"
openclaw gateway logs --lines 20 | grep -i error

echo -e "\n=== 检查完成 ==="
EOF

chmod +x ~/openclaw_migration_check.sh
```

### 7.2 运行监控
```bash
# 手动运行检查
~/openclaw_migration_check.sh

# 设置定时检查（每小时）
(crontab -l 2>/dev/null; echo "0 * * * * ~/openclaw_migration_check.sh >> /var/log/openclaw_check.log") | crontab -
```

---

## 💡 最佳实践建议

1. **双机并行**: 迁移后保留旧机器至少 48 小时，确保一切正常
2. **分阶段验证**: 先验证基础功能，再验证复杂功能
3. **日志监控**: 持续监控日志文件，及时发现异常
4. **配置版本控制**: 使用 Git 管理工作空间配置
5. **定期备份**: 建立定期自动备份机制
6. **环境隔离**: 区分测试环境和生产环境
7. **文档记录**: 记录所有迁移步骤和遇到的问题

---

## 🔧 高级技巧

### 自动化迁移脚本
```bash
cat > auto_migrate_openclaw.sh << 'EOF'
#!/bin/bash
set -e

# 1. 备份
echo "开始备份..."
tar czvf workspace_backup.tar.gz ~/.openclaw/workspace/

# 2. 传输
echo "传输到新机器..."
rsync -avzP workspace_backup.tar.gz user@new_vps:~/backup/

# 3. 在新机器恢复
echo "在新机器恢复..."
ssh user@new_vps "
  cd ~/backup
  tar xzf workspace_backup.tar.gz -C ~/.openclaw/
  openclaw gateway restart
"

echo "迁移完成！"
EOF
```

### 增量备份脚本
```bash
cat > incremental_backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups/openclaw_$TIMESTAMP

mkdir -p $BACKUP_DIR

# 增量备份工作空间
tar czvf $BACKUP_DIR/workspace.tar.gz \
  --exclude=node_modules \
  --exclude=.git \
  --exclude=logs \
  ~/.openclaw/workspace/

# 备份配置
cp -r ~/.openclaw/gateway $BACKUP_DIR/
cp -r ~/.openclaw/config $BACKUP_DIR/
cp -r ~/.openclaw/plugins $BACKUP_DIR/
cp -r ~/.openclaw/skills $BACKUP_DIR/

# 备份记忆
tar czvf $BACKUP_DIR/memory.tar.gz ~/.openclaw/workspace/memory/

echo "备份完成：$BACKUP_DIR"
EOF
```

### 配置同步工具
```bash
cat > sync_config.sh << 'EOF'
#!/bin/bash
# 同步配置到多个服务器

servers=("server1" "server2" "server3")

for server in "${servers[@]}"; do
    echo "同步到 $server..."
    rsync -avzP \
      ~/.openclaw/workspace/ \
      $server:~/.openclaw/workspace/
    
    rsync -avzP \
      ~/.openclaw/config/ \
      $server:~/.openclaw/config/
    
    ssh $server "openclaw gateway restart"
done

echo "同步完成！"
EOF
```

---

## 📝 迁移后检查表

### 即时检查（迁移后 1 小时内）
- [ ] Gateway 正常运行
- [ ] 所有记忆文件可访问
- [ ] 技能插件加载成功
- [ ] 网络连接正常
- [ ] 无异常错误日志

### 短期检查（迁移后 24 小时内）
- [ ] 持续监控日志
- [ ] 验证所有功能
- [ ] 测试 API 调用
- [ ] 确认备份策略

### 长期检查（迁移后 1 周）
- [ ] 性能评估
- [ ] 资源使用情况
- [ ] 功能完整性
- [ ] 用户反馈收集

---

> **创建时间**: 2026-04-06  
> **最后更新**: 2026-04-06

**提示**: 迁移完成后，建议立即更新 `MEMORY.md` 记录本次迁移详情！
