---
title: 'ssh连接服务器踩坑点'
categories: ["实践"]
date: 2026-02-25T21:36:52+08:00
lastmod: 2026-02-25T21:36:52+08:00
encrypted: false
---
# 通过密钥连接服务器踩坑——配置正确但是连接失败

1. 初始状态

- 已成功生成SSH密钥对（ed25519）

- 已将公钥添加到服务器的 ~/.ssh/authorized_keys                                            - 权限设置正确（.ssh 目录700，authorized_keys 文件600）

2. 问题表现
   ssh -o BatchMode=yes -o PasswordAuthentication=no root@38.55.39.104

## 结果：Permission denied (password)

即使公钥已在服务器上，公钥认证仍然失败。

3. 根本原因
   检查服务器SSH配置：
   grep PubkeyAuthentication /etc/ssh/sshd_config

## 输出：PubkeyAuthentication no

核心问题：服务器的SSH配置中禁用了公钥认证（PubkeyAuthentication no）

修复步骤

步骤1：修改SSH配置文件
sed -i 's/^PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config
将 PubkeyAuthentication no 改为 PubkeyAuthentication yes

步骤2：重启SSH服务
systemctl restart sshd
使配置生效

步骤3：验证修复
ssh -o PasswordAuthentication=no root@38.55.39.104

## 结果：✓ 公钥认证成功！无需输入密码！

关键知识点

Ubuntu 24.04默认行为：

- 新安装的Ubuntu 24.04系统可能在 /etc/ssh/sshd_config 中明确设置 PubkeyAuthentication no
- 这是一个安全默认设置，需要管理员手动启用

公钥认证的三要素：

1. ✓ 客户端有私钥（~/.ssh/id_ed25519）
2. ✓ 服务器有公钥（~/.ssh/authorized_keys）
3. ✓ 服务器允许公钥认证（PubkeyAuthentication yes） ← 这次缺失的

为什么会被禁用：

- 云服务商（如Vultr、DigitalOcean）的某些镜像默认禁用公钥认证
- 安全策略要求使用其他认证方式
- 系统管理员的配置选择

