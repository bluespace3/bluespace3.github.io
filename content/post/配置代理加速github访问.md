---
title: '配置代理加速github访问'
categories: ["配置代理加速github访问.md"]
date: 2026-02-28T03:25:00+08:00
lastmod: 2026-02-28T03:25:00+08:00
encrypted: false
---

## 第一部分：服务端配置（海外服务器）

### 1.1 安装 Shadowsocks 服务端

```bash
# SSH 连接到服务器
ssh root@your-server-ip

# 更新包管理器
apt update

# 安装 shadowsocks-libev
apt install shadowsocks-libev -y
```

### 1.2 创建配置文件

```bash
cat > /etc/shadowsocks-libev/config.json << EOF
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "password": "YourStrongPassword123!",
    "timeout": 300,
    "method": "aes-256-gcm"
}
EOF
```

**配置说明**：

- `server`: 监听所有网络接口
- `server_port`: 服务器端口（可自定义）
- `password`: 连接密码（请修改为强密码）
- `method`: 加密方式（aes-256-gcm 推荐）

### 1.3 配置防火墙

```bash
# 如果使用 ufw
ufw allow 8388/tcp
ufw allow 8388/udp
ufw reload

# 如果使用 iptables
iptables -A INPUT -p tcp --dport 8388 -j ACCEPT
iptables -A INPUT -p udp --dport 8388 -j ACCEPT
iptables-save > /etc/iptables/rules.v4
```

### 1.4 创建系统服务

```bash
cat > /etc/systemd/system/shadowsocks-libev.service << EOF
[Unit]
Description=Shadowsocks-libev Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/ss-server -c /etc/shadowsocks-libev/config.json
Restart=on-failure
RestartSec=5s
User=nobody

[Install]
WantedBy=multi-user.target
EOF
```

### 1.5 启动服务

```bash
# 重载 systemd 配置
systemctl daemon-reload

# 启动服务
systemctl start shadowsocks-libev

# 设置开机自启
systemctl enable shadowsocks-libev

# 检查服务状态
systemctl status shadowsocks-libev

# 查看日志
journalctl -u shadowsocks-libev -f
```

### 1.6 验证服务运行

```bash
# 检查端口是否监听
netstat -tuln | grep 8388

# 或使用 ss 命令
ss -tuln | grep 8388

# 应该看到类似输出
# udp   UNCONN  0  0  0.0.0.0:8388  0.0.0.0:**
```

---

## 第二部分：本地客户端配置（Windows）

### 2.1 安装 Node.js

```bash
# 检查是否已安装 Node.js
node --version
npm --version

# 如果未安装，访问 https://nodejs.org/ 下载安装
# 或使用公司允许的安装方式
```

### 2.2 安装 Shadowsocks Node.js 客户端

```bash
# 方式一：安装 shadowsocks 包
npm install -g shadowsocks

# 方式二：如果上面失败，使用这个
npm install -g shadowsocks-node-client

# 方式三：使用更现代的 fork 版本
npm install -g @lenov/smgr
```

**如果安装失败，使用本地安装**：

```bash
# 创建项目目录
mkdir C:\shadowsocks-client
cd C:\shadowsocks-client

# 初始化项目
npm init -y

# 安装到本地
npm install shadowsocks

# 或安装其他兼容版本
npm install shadowsocks-node-client
```

### 2.3 创建配置文件

**创建配置文件** `C:\Users\YourName\.shadowsocks\config.json`：

```json
{
    "server": "your-server-ip",
    "server_port": 8388,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "YourStrongPassword123!",
    "timeout": 300,
    "method": "aes-256-gcm"
}
```

**配置说明**：

- `server`: 你的海外服务器 IP 地址
- `server_port`: 服务器端口（与服务端配置一致）
- `local_address`: 本地监听地址
- `local_port`: 本地 SOCKS5 代理端口
- `password`: 连接密码（与服务端配置一致）
- `method`: 加密方式（与服务端配置一致）

### 2.4 启动客户端

**方式一：全局安装启动**

```bash
# 使用配置文件启动
sslocal -c C:\Users\YourName\.shadowsocks\config.json
```

**方式二：本地安装启动**

```bash
cd C:\shadowsocks-client

# 使用 npx 运行
npx sslocal -c config.json

# 或直接运行
node node_modules/shadowsocks/bin/sslocal -c config.json
```

**方式三：后台运行（Windows）**

创建启动脚本 `start-shadowsocks.bat`：

```batch
@echo off
echo Starting Shadowsocks client...
cd /d C:\shadowsocks-client
start /B node node_modules/shadowsocks/bin/sslocal -c config.json
echo Shadowsocks started on port 1080
```

**方式四：使用 PM2 管理进程（推荐）**

```bash
# 安装 pm2
npm install -g pm2

# 启动并监控
pm2 start C:\shadowsocks-client\node_modules\shadowsocks\bin\sslocal --name shadowsocks -- -c C:\Users\YourName\.shadowsocks\config.json

# 设置开机自启
pm2 startup
pm2 save

# 查看状态
pm2 status

# 查看日志
pm2 logs shadowsocks

# 停止
pm2 stop shadowsocks

# 重启
pm2 restart shadowsocks
```

### 2.5 验证连接

```bash
# 新开终端窗口，测试代理
curl --proxy socks5://127.0.0.1:1080 https://www.google.com

# 或测试 GitHub API
curl --proxy socks5://127.0.0.1:1080 https://api.github.com

# 查看当前 IP（应该显示服务器 IP）
curl --proxy socks5://127.0.0.1:1080 https://api.ipify.org
```

**成功输出示例**：

```html
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="https://www.google.com/">here</A>.
</BODY></HTML>
```

---

## 第三部分：配置应用程序使用代理

### 3.1 浏览器配置

#### Chrome / Edge

**方法 1：系统代理设置（推荐）**

1. 按 `Win + I` 打开设置
2. 搜索"代理"
3. 点击"代理服务器设置"
4. 手动设置代理：
  - 地址：`127.0.0.1`
  - 端口：`1080`
  - 勾选" SOCKS 代理"

**方法 2：启动参数（仅当前浏览器）**

```bash
# Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --proxy-server="socks5://127.0.0.1:1080"

# Edge
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --proxy-server="socks5://127.0.0.1:1080"
```

**方法 3：SwitchyOmega 扩展（灵活切换）**

1. 安装 [SwitchyOmega](https://github.com/FelisCatus/SwitchyOmega/releases)
2. 配置情景模式：
  - 新建情景模式：`Shadowsocks`
  - 代理协议：`SOCKS5`
  - 代理服务器：`127.0.0.1`
  - 端口：`1080`
  - 勾选" SOCKS v5 代理进行 DNS 查询"
3. 点击"应用选项"
4. 浏览器图标切换到 `Shadowsocks` 情景模式

#### Firefox

1. 打开设置
2. 搜索"代理"
3. 点击"网络设置"
4. 选择"手动配置代理"
5. 填写：
  - SOCKS v5 代理：`127.0.0.1`
  - 端口：`1080`
  - ✓ SOCKS v5
  - ✓ 使用 SOCKS v5 代理进行 DNS 查询
6. 点击"确定"

### 3.2 配置 Git 访问 GitHub

#### HTTPS 代理

```bash
# 设置代理
git config --global http.proxy socks5://127.0.0.1:1080
git config --global https.proxy socks5://127.0.0.1:1080

# 查看配置
git config --global --get http.proxy

# 测试
git clone https://github.com/username/repo.git
```

#### SSH 代理

```bash
# 编辑 SSH 配置
notepad ~/.ssh/config
```

添加以下内容：

```
Host github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:1080 %h %p
    Hostname ssh.github.com
    Port 443

Host gist.github.com
    ProxyCommand nc -X 5 -x 127.0.0.1:1080 %h %p
    Hostname ssh.github.com
    Port 443
```

**测试 SSH 连接**：

```bash
ssh -T git@github.com
# 成功会显示：Hi username! You've successfully authenticated...
```

#### 取消代理

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 3.3 命令行工具配置

#### PowerShell

```powershell
# 临时设置（当前会话）
$env:http_proxy="http://127.0.0.1:1080"
$env:https_proxy="http://127.0.0.1:1080"
$env:all_proxy="socks5://127.0.0.1:1080"

# 测试
curl https://www.google.com

# 永久设置（添加到 PowerShell 配置文件）
notepad $PROFILE
# 添加上述内容
```

#### Bash / Git Bash

```bash
# 临时设置
export http_proxy=http://127.0.0.1:1080
export https_proxy=http://127.0.0.1:1080
export all_proxy=socks5://127.0.0.1:1080

# 永久设置（添加到 ~/.bashrc）
cat >> ~/.bashrc << EOF
# Shadowsocks 代理
export http_proxy=http://127.0.0.1:1080
export https_proxy=http://127.0.0.1:1080
export all_proxy=socks5://127.0.0.1:1080
export no_proxy=localhost,127.0.0.1,::1
EOF

# 应用
source ~/.bashrc
```

#### curl

```bash
# 使用代理
curl --proxy socks5://127.0.0.1:1080 https://www.google.com

# 或使用环境变量
curl https://www.google.com
```

#### wget

```bash
# 使用代理
wget -e "use_proxy=yes" -e "http_proxy=127.0.0.1:1080" https://example.com
```

### 3.4 包管理器配置

#### npm

```bash
# 设置代理
npm config set proxy http://127.0.0.1:1080
npm config set https-proxy http://127.0.0.1:1080

# 查看配置
npm config list

# 测试
npm install express

# 取消代理
npm config delete proxy
npm config delete https-proxy
```

#### pip

```bash
# 设置代理
pip config set global.proxy http://127.0.0.1:1080

# 测试
pip install requests

# 临时使用
pip install --proxy http://127.0.0.1:1080 package-name

# 取消代理
pip config unset global.proxy
```

#### yarn

```bash
# 设置代理
yarn config set proxy http://127.0.0.1:1080
yarn config set https-proxy http://127.0.0.1:1080

# 测试
yarn add express
```

### 3.5 开发工具配置

#### VS Code

**设置 → 搜索 "proxy"**：

```json
{
  "http.proxy": "http://127.0.0.1:1080",
  "http.proxyStrictSSL": false
}
```

或设置环境变量：

```bash
# VS Code 读取系统环境变量
set HTTP_PROXY=http://127.0.0.1:1080
set HTTPS_PROXY=http://127.0.0.1:1080
code .
```

#### Docker

```bash
# 创建 Docker 配置
mkdir C:\Users\YourName\.docker
notepad C:\Users\YourName\.docker\config.json
```

```json
{
  "proxies": {
    "default": {
      "httpProxy": "http://127.0.0.1:1080",
      "httpsProxy": "http://127.0.0.1:1080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### 3.6 Python 配置

#### requests 库

```python
import requests

proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

# 需要安装 pysocks
# pip install requests[socks]

response = requests.get('https://api.github.com', proxies=proxies)
print(response.json())
```

#### urllib

```python
import urllib.request

proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

proxy_handler = urllib.request.ProxyHandler(proxies)
opener = urllib.request.build_opener(proxy_handler)
response = opener.open('https://api.github.com')
print(response.read())
```

### 3.7 验证代理是否生效

#### 浏览器测试

访问：[https://api.ipify.org](https://api.ipify.org) 或 [https://ip.sb](https://ip.sb)

**应该显示你的服务器 IP 地址**

#### 命令行测试

```bash
# 测试代理连接
curl --proxy socks5://127.0.0.1:1080 https://api.ipify.org

# 测试 GitHub API
curl --proxy socks5://127.0.0.1:1080 https://api.github.com

# 测试 Google
curl --proxy socks5://127.0.0.1:1080 https://www.google.com -I
```

#### Git 测试

```bash
# 测试 HTTPS
git ls-remote https://github.com/torvalds/linux.git

# 测试 SSH
ssh -T git@github.com
```

### 3.8 一键开关脚本

#### 启动代理脚本 `proxy-on.bat`

```batch
@echo off
echo ========================================
echo    启动 Shadowsocks 代理客户端
echo ========================================

echo.
echo [1/3] 启动 Shadowsocks 客户端...
cd /d C:\shadowsocks-client
start /B node node_modules\shadowsocks\bin\sslocal -c C:\Users\YourName\.shadowsocks\config.json
timeout /t 2 >nul

echo [2/3] 设置 Git 代理...
git config --global http.proxy socks5://127.0.0.1:1080
git config --global https.proxy socks5://127.0.0.1:1080

echo [3/3] 设置环境变量...
set http_proxy=http://127.0.0.1:1080
set https_proxy=http://127.0.0.1:1080
set all_proxy=socks5://127.0.0.1:1080

echo.
echo ========================================
echo    代理已启动！端口：1080
echo ========================================
echo.
echo 测试命令：
echo curl --proxy socks5://127.0.0.1:1080 https://api.ipify.org
echo.
pause
```

#### 关闭代理脚本 `proxy-off.bat`

```batch
@echo off
echo ========================================
echo    关闭 Shadowsocks 代理客户端
echo ========================================

echo.
echo [1/2] 关闭 Shadowsocks 客户端...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq sslocal*" 2>nul

echo [2/2] 取消 Git 代理...
git config --global --unset http.proxy
git config --global --unset https.proxy

echo.
echo ========================================
echo    代理已关闭！
echo ========================================
echo.
pause
```

#### 快速切换脚本 `proxy-toggle.bat`

```batch
@echo off
tasklist /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq sslocal*" 2>nul | find /I "node.exe" >nul

if %ERRORLEVEL% equ 0 (
    echo 检测到代理运行中，正在关闭...
    taskkill /F /IM node.exe /FI "WINDOWTITLE eq sslocal*" 2>nul
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    echo 代理已关闭
) else (
    echo 检测到代理未运行，正在启动...
    cd /d C:\shadowsocks-client
    start /B node node_modules\shadowsocks\bin\sslocal -c C:\Users\YourName\.shadowsocks\config.json
    git config --global http.proxy socks5://127.0.0.1:1080
    git config --global https.proxy socks5://127.0.0.1:1080
    echo 代理已启动
)

pause
```

---

## 第四部分：开机自启动配置

### 4.1 使用 PM2（推荐）

```bash
# 保存当前 PM2 进程列表
pm2 save

# 安装 PM2 Windows 启动服务
pm2-startup install

# 或者创建开机启动脚本
cat > start_shadowsocks.bat << EOF
@echo off
pm2 resurrect
EOF

# 将快捷方式放入启动文件夹
# C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

### 4.2 使用 Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：当用户登录时
4. 操作：启动程序
  - 程序：`node.exe`
  - 参数：`C:\shadowsocks-client\node_modules\shadowsocks\bin\sslocal -c C:\Users\YourName\.shadowsocks\config.json`
  - 起始于：`C:\shadowsocks-client`

### 4.3 使用启动文件夹快捷方式

```bash
# 创建启动脚本
cat > C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start-shadowsocks.bat << EOF
@echo off
cd /d C:\shadowsocks-client
start /min node node_modules\shadowsocks\bin\sslocal -c C:\Users\YourName\.shadowsocks\config.json
EOF
```

---

## 第五部分：故障排查

### 5.1 连接失败

**检查服务端**：

```bash
# SSH 到服务器
ssh root@your-server-ip

# 检查服务状态
systemctl status shadowsocks-libev

# 查看日志
journalctl -u shadowsocks-libev -n 50

# 检查端口监听
netstat -tuln | grep 8388

# 测试本地连接
telnet 127.0.0.1 8388
```

**检查客户端**：

```bash
# 查看日志输出
# 检查配置文件路径是否正确
cat C:\Users\YourName\.shadowsocks\config.json

# 测试服务器连通性
ping your-server-ip
telnet your-server-ip 8388
```

### 5.2 速度慢

**优化措施**：

1. 更换加密方法（服务端和客户端同步修改）：

```json
"method": "chacha20-ietf-poly1305"
```

2. 检查服务器带宽：

```bash
# 在服务器上测试
wget -O /dev/null http://speedtest.tele2.net/100MB.zip
```

3. 启用 TCP Fast Open（服务端）：

```json
{
    "fast_open": true
}
```

### 5.3 频繁断线

**解决方案**：

1. 增加超时时间：

```json
"timeout": 600
```

2. 配置心跳检测：

```bash
# 在服务端配置 keep-alive
sysctl -w net.ipv4.tcp_keepalive_time=600
```

### 5.4 密码错误

```bash
# 确保服务端和客户端密码完全一致
# 密码中的特殊字符需要正确转义

# 重新设置服务端密码
cat > /etc/shadowsocks-libev/config.json << EOF
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "password": "SimplePassword123",
    "timeout": 300,
    "method": "aes-256-gcm"
}
EOF

# 重启服务
systemctl restart shadowsocks-libev
```

---

## 第六部分：安全建议

### 6.1 使用强密码

```bash
# 生成随机密码
openssl rand -base64 32

# 或使用
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32
```

### 6.2 修改默认端口

```json
{
    "server_port": 23456
}
```

### 6.3 限制访问 IP（可选）

```bash
# 使用 iptables 限制只有特定 IP 可以连接
iptables -A INPUT -s your-client-ip -p tcp --dport 8388 -j ACCEPT
iptables -A INPUT -s your-client-ip -p udp --dport 8388 -j ACCEPT
iptables -A INPUT -p tcp --dport 8388 -j DROP
iptables -A INPUT -p udp --dport 8388 -j DROP
```

### 6.4 定期更新

```bash
# 服务端定期更新
apt update && apt upgrade shadowsocks-libev -y

# 客户端定期更新
npm update -g shadowsocks
```

---

## 第七部分：高级配置

### 7.1 多端口配置

**服务端配置**：

```json
{
    "server": "0.0.0.0",
    "port_password": {
        "8388": "password1",
        "8389": "password2",
        "8390": "password3"
    },
    "timeout": 300,
    "method": "aes-256-gcm"
}
```

### 7.2 配置插件支持

```json
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "password": "password",
    "timeout": 300,
    "method": "aes-256-gcm",
    "plugin": "v2ray-plugin",
    "plugin_opts": "server;tls;host=your-domain.com"
}
```

### 7.3 流量统计（服务端）

```bash
# 安装流量监控工具
apt install iftop nethogs -y

# 监控 8388 端口流量
iftop -i eth0 -f "port 8388"

# 或使用 nethogs
nethogs
```

---

## 附录 A：快速命令参考

### 服务端

```bash
# 启动
systemctl start shadowsocks-libev

# 停止
systemctl stop shadowsocks-libev

# 重启
systemctl restart shadowsocks-libev

# 状态
systemctl status shadowsocks-libev

# 日志
journalctl -u shadowsocks-libev -f
```

### 客户端

```bash
# 启动
sslocal -c config.json

# PM2 管理
pm2 start shadowsocks
pm2 stop shadowsocks
pm2 restart shadowsocks
pm2 logs shadowsocks
pm2 status
```

### Git 代理

```bash
# 设置
git config --global http.proxy socks5://127.0.0.1:1080

# 查看
git config --global http.proxy

# 取消
git config --global --unset http.proxy
```

---

## 附录 B：配置文件模板

### 服务端模板

```json
{
    "server": "0.0.0.0",
    "server_port": 8388,
    "password": "CHANGE_ME_STRONG_PASSWORD",
    "timeout": 300,
    "method": "aes-256-gcm",
    "fast_open": false,
    "workers": 1
}
```

### 客户端模板

```json
{
    "server": "YOUR_SERVER_IP",
    "server_port": 8388,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "CHANGE_ME_STRONG_PASSWORD",
    "timeout": 300,
    "method": "aes-256-gcm"
}
```

---

## 附录 C：常见问题 FAQ

**Q: 连接后无法访问某些网站？**
A: 可能是 DNS 污染，尝试在浏览器配置中使用 SOCKS v5 代理进行 DNS 查询。

**Q: 速度很慢？**
A:

1. 检查服务器带宽
2. 更换加密方法为 chacha20-ietf-poly1305
3. 检查本地网络到服务器的延迟

**Q: 如何确认代理生效？**
A: 访问 [https://api.ipify.org](https://api.ipify.org) 或 [https://ip.sb，应该显示服务器](https://ip.sb，应该显示服务器) IP。

**Q: Node.js 客户端报错？**
A: 尝试使用不同版本的包：

```bash
npm install shadowsocks@latest
# 或
npm install shadowsocks-node-client
```

---

## 总结

本方案使用 Node.js 实现 Shadowsocks 客户端，具有以下优势：

✅ **无需安装额外软件** - 只需 Node.js
✅ **跨平台** - Windows/macOS/Linux 通用
✅ **灵活配置** - JSON 配置文件
✅ **易于管理** - PM2 进程管理
✅ **开机自启** - 系统服务或任务计划

配置完成后，你的所有应用都可以通过 127.0.0.1:1080 的 SOCKS5 代理访问 GitHub 等海外网站。