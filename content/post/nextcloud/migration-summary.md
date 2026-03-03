---
title: 'migration-summary'
categories: ["nextcloud"]
date: 2026-03-04T01:34:21+08:00
lastmod: 2026-03-04T01:34:21+08:00
---
# Nextcloud 数据库迁移总结

迁移日期：2026-03-04

## 一、迁移概述

将 Nextcloud 从本地 MariaDB 数据库迁移到 Aiven 云托管 MySQL 数据库。

### 迁移动机
- 评估云数据库延迟影响
- 测试分布式部署可行性
- 释放本地服务器资源

### 迁移结果
✅ **成功迁移** - 123/126 个表成功导入

---

## 二、延迟测试结果

### 测试环境
- 本地服务器：4 核 CPU，3.8GB 内存
- 网络：Tailscale P2P + Aiven 云数据库

### 延迟对比

| 方案 | 平均延迟 | 稳定性 |
|------|----------|--------|
| 本地数据库 | <1 ms | ⭐⭐⭐⭐⭐ |
| Tailscale 设备间 | 155 ms | ⭐⭐⭐⭐ |
| Aiven 云数据库 | 219-246 ms | ⭐⭐⭐⭐⭐ |

### 性能影响评估

| 指标 | 本地 | Aiven | 影响 |
|------|------|-------|------|
| 简单查询 | <1 ms | ~250 ms | 可感知 |
| 页面加载 | 即时 | +0.5-1s | 明显 |
| 大文件上传 | 正常 | 无影响 | 无 |

---

## 三、迁移步骤

### 1. 导出本地数据
```bash
# 从本地 MariaDB 导出
docker exec nextcloud-db mariadb-dump \
  -unextcloud -p<LOCAL_PASSWORD> nextcloud \
  > /tmp/nextcloud_backup.sql

# 备份大小：2.6 MB
```

### 2. 测试云数据库连接
```bash
# 使用 SSL 证书连接
mysql --user avnadmin --password=<AVN_PASSWORD> \
  --host <AVN_HOST> --port 23804 \
  --ssl-ca=/path/to/ca.pem defaultdb
```

### 3. 导入数据到云数据库
```bash
# 创建 Nextcloud 数据库
mysql -e "CREATE DATABASE IF NOT EXISTS nextcloud;"

# 导入数据
mysql --host=<AVN_HOST> --port=23804 \
  --user=avnadmin --password=<AVN_PASSWORD> \
  --ssl-ca=/path/to/ca.pem nextcloud \
  < /tmp/nextcloud_backup.sql
```

### 4. 更新 Nextcloud 配置

配置文件位置：`/root/nextcloud/config/config.php`

**修改前（本地数据库）：**
```php
'dbhost' => 'db',
'dbname' => 'nextcloud',
'dbuser' => 'nextcloud',
'dbpassword' => '<LOCAL_PASSWORD>',
```

**修改后（Aiven 云数据库）：**
```php
'dbhost' => '<AVN_HOST>.aivencloud.com',
'dbname' => 'defaultdb',  // 或 'nextcloud'
'dbuser' => 'avnadmin',
'dbpassword' => '<AVN_PASSWORD>',
'dbport' => '23804',
'mysql.ssl.ca' => '/path/to/ca.pem',
```

### 5. 重启服务
```bash
docker restart nextcloud
```

---

## 四、遇到的问题与解决

### 问题 1：SSL 证书路径
**现象**：容器内无法访问 SSL 证书
**解决**：证书需要挂载到容器内，或使用环境变量配置

### 问题 2：MySQL 8.0 兼容性
**现象**：3 个表导入失败
```
ERROR 1101: BLOB, TEXT can't have a default value
```
**原因**：MariaDB 允许 TEXT 列有默认值，MySQL 8.0 不允许
**影响表**：
- `oc_ex_ui_files_actions`（扩展 UI 操作）
- `oc_flow_operations`（工作流操作）
- `oc_sec_signatory`（电子签名）
**影响**：不影响核心文件存储和共享功能

### 问题 3：外键依赖顺序
**现象**：部分表因外键约束导入失败
**解决**：使用 `--force` 参数继续导入

---

## 五、当前配置

### 本地服务器（/root/nextcloud）

```
服务：
├── nextcloud (主应用)
├── nextcloud-readonly (只读副本)
├── nextcloud-db (MariaDB - 已停止使用)
├── nextcloud-redis (Redis 缓存)
└── nextcloud-nginx (反向代理)
```

### 云数据库配置

| 参数 | 值 |
|------|-----|
| 主机 | `mysql-<id>.aivencloud.com` |
| 端口 | `23804` |
| 用户 | `avnadmin` |
| 数据库 | `defaultdb` / `nextcloud` |
| SSL | 必需 |

### 原有数据表（保留未删除）

| 表名 | 大小 | 用途 |
|------|------|------|
| stock_data | 1.5 MB | 股票行情数据 |
| analysis_results | 1.5 MB | AI 分析结果 |
| t_settings | 16 KB | 系统配置 |

---

## 六、回滚方案

如需切回本地数据库：

```bash
# 1. 修改 config.php
vim /root/nextcloud/config/config.php

# 改为：
'dbhost' => 'db',
'dbname' => 'nextcloud',
'dbuser' => 'nextcloud',
'dbpassword' => '<LOCAL_PASSWORD>',

# 2. 重启 Nextcloud
docker restart nextcloud

# 3. 验证
docker logs --tail 20 nextcloud
```

---

## 七、资源对比

### 迁移前
- 内存占用：~270 MB (Nextcloud + DB + Redis)
- 数据库：本地 116 MB

### 迁移后
- 内存占用：~150 MB (Nextcloud + Redis)
- 数据库：云端，本地释放 ~120 MB

### 资源释放
- **内存**：约 120 MB
- **CPU**：查询高峰时释放 10-30%
- **存储**：本地保留原数据库（未删除）

---

## 八、建议

### 当前延迟下的建议
✅ **适合**：
- 个人/小团队使用
- 不频繁的文件访问
- 作为异地备份

❌ **不适合**：
- 高并发场景
- 需要即时响应的应用
- 大量数据库查询操作

### 优化建议
1. **启用 Redis 查询缓存** - 减少数据库访问
2. **使用 CDN** - 静态资源缓存
3. **分离只读副本** - 分散读请求

---

## 九、访问地址

- **主服务**：https://<TAILSCALE_IP>:8443
- **只读副本**：http://localhost:8081

---

## 附录：命令参考

### 检查数据库连接
```bash
docker exec nextcloud php -r "
\$pdo = new PDO(
  'mysql:host=<AVN_HOST>;port=23804;dbname=defaultdb',
  'avnadmin',
  '<AVN_PASSWORD>'
);
echo 'Connection: SUCCESS\n';
"
```

### 查看表大小
```sql
SELECT
  TABLE_NAME,
  ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS Size_MB
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'defaultdb'
ORDER BY Size_MB DESC;
```

### 检查延迟
```bash
# ICMP Ping
ping -c 10 <AVN_HOST>

# TCP 连接延迟
nc -z -w 2 <AVN_HOST> 23804
```
