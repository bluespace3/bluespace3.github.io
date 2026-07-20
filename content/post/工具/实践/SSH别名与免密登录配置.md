---
title: 'SSH别名与免密登录配置'
categories: ["工具"]
date: 2026-07-20T19:22:31+08:00
lastmod: 2026-07-20T19:22:31+08:00
draft: false
---
# SSH别名与免密登录配置

**场景**：已经能通过 `ssh user@ip` 密码登录目标机器，如何设置别名 + 免密登录，实现一键直连。

## 一、配置别名（本地操作）

编辑本地 SSH 配置文件：

```bash
# Linux / macOS
nano ~/.ssh/config

# Windows (Git Bash)
notepad C:\Users\Administrator\.ssh\config
```

如果文件不存在就新建一个。添加如下配置：

```
Host administrator
  HostName xxx.xxx.xxx.xxx
  User administrator
  Port 22
```

- `Host` 后面的名字就是别名，自定义即可（如 `server`、`home-pc` 等）
- `HostName` 是目标机器的 IP 或域名
- `User` 是目标机器的登录用户名
- `Port` 是 SSH 端口，默认 22，非标准端口需修改

保存后，直接用别名连接：

```bash
ssh administrator
```

## 二、配置免密登录

### 第一步：查看本地公钥

```bash
cat ~/.ssh/id_ed25519.pub
```

输出类似：

```
ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx user@example.com
```

如果没有公钥，先生成一个：

```bash
ssh-keygen -t ed25519
```

### 第二步：在目标机器上部署公钥

**Linux / macOS 目标机器：**

```bash
# 确保 .ssh 目录存在
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 追加公钥到 authorized_keys
echo "ssh-ed25519 AAAA...你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**Windows 目标机器（PowerShell）：**

```powershell
# 确保 .ssh 目录存在
New-Item -ItemType Directory -Force -Path "$HOME\.ssh"

# 追加公钥到 authorized_keys（把引号内的内容替换为你的公钥）
Add-Content -Path "$HOME\.ssh\authorized_keys" -Value 'ssh-ed25519 AAAA...你的公钥内容' -NoNewline
```

### 第三步：更新本地 config 添加密钥认证

```
Host administrator
  HostName xxx.xxx.xxx.xxx
  User administrator
  Port 22
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

新增了两行：
- `IdentityFile` 指定使用的私钥路径
- `IdentitiesOnly yes` 强制只使用指定的密钥，避免尝试其他密钥导致连接慢

### 第四步：验证

```bash
ssh administrator
```

无需输入密码，直接登录成功。

## 三、完整配置示例

```
# 别名 1
Host server
  HostName xxx.xxx.xxx.xxx
  User root
  IdentityFile ~/.ssh/id_ed25519_server_64_83_18_146
  IdentitiesOnly yes

# 别名 2
Host administrator
  HostName xxx.xxx.xxx.xxx
  User administrator
  Port 22
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

# 别名 3（非标准端口）
Host mac
  HostName xxx.xxx.xxx.xxx
  User tianqinghong
  IdentityFile ~/.ssh/id_rsa_new
  IdentitiesOnly yes
```

## 四、常见问题

### 1. 目标机器是 Windows，`mkdir -p ~/.ssh` 报错

Windows 的 PowerShell 不支持 Linux 命令，改用：

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.ssh"
```

### 2. 配置了公钥但仍然要求输入密码

参考 [[ssh连接服务器踩坑点]]，检查目标机器 SSH 服务是否开启了公钥认证：

```bash
grep PubkeyAuthentication /etc/ssh/sshd_config
```

如果是 `no`，改为 `yes` 后重启 SSH 服务。

### 3. 多台机器使用同一个别名

`Host` 后面的名字是唯一的，后定义的会覆盖前面的。如果需要连接不同机器，使用不同的别名。
