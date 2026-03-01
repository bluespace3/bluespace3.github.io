---
title: 'linux常用命令'
categories: ["编程语言"]
date: 2025-09-07T00:20:44+08:00
lastmod: 2025-09-07T00:20:44+08:00
encrypted: false
---
---
title: 'linux常用命令'
categories: ["编程语言"]
date: 2025-09-07T00:20:44+08:00
lastmod: 2025-09-07T00:20:44+08:00
encrypted: false
title: 'linux常用命令'
categories: ["编程语言"]
date: 2025-09-07T00:20:44+08:00
lastmod: 2025-09-07T00:20:44+08:00
encrypted: false
title: 'linux常用命令'
categories: ["编程语言"]
date: 2025-09-07T00:20:44+08:00
lastmod: 2025-09-07T00:20:44+08:00
encrypted: false

**查看历史使用命令**

```Shell
history
1
```

过滤与 `es`相关命令

```Shell
history | grep es
1
```

**查看占用资源**

```Shell
ps -au                占用的资源是从进程启动开始，计算的平均占用资源，比如cpu等
top                        实时占用的资源；
12
```

**查看当前目录所占存储**

```Shell
du -lh                        查看当前文件下各文件夹占用存储空间
du -sh                        查看当前文件夹所占存储空间
du --max-depth=<目录层数>         超过指定层数的目录后，予以忽略。
du --max-depth=1                         只查看当前目录下文件占用的存储空间
1234
```

**管道命令：**
根据项目查看进程，更加PID查看项目，以及项目路径

```Shell
ps -ef                                                 查看所有的进程
ps -ef | grep mysql                        查看mysql相关的进程
12
```

通过进程PID查看所占用的端口号

```Shell
netstat -nap |grep 进程ID(PID)
1
```

**查看Linux下系统存储使用率**

```Shell
df -h                        查看系统硬盘使用情况
1
```

**杀死进程(根据PID)**

```Shell
kill -9 2630                进程pid
1
```

**关闭防火墙**

```Shell
service iptables stop      临时关闭防火墙
chkconfig iptables off     防火墙开启不启动
service iptables status    查看防火墙状态
123
```

**开机启动选项**

```Shell
msconfig                                        查看开机启动选项
chkconfig                                        查看开机启动服务列表
12
```

**查看MySQL服务的程序的状态**

```Shell
service mysql start        开启MySQL
service mysql status       查看MySQL的状态
service mysql stop         关闭MySQL
123
```

### 2、curl语法

**GET请求**

```Shell
curl "http://www.wangchujiang.com"
1
```

**POST请求**

```Shell
#  普通文本
curl -d'login=emma＆password=123' -X POST https://wangchujiang.com/login
#  Json格式
curl -l -H "Content-type: application/json" -X POST -d '{"phone":"13521389587","password":"test"}' http://wangchujiang.com/apis/users.json

12345
```

详细可以看我写的另一篇：[curl语法整理](https://blog.csdn.net/lydms/article/details/127655845)

```Plaintext
https://blog.csdn.net/lydms/article/details/127655845
1
```

## 十二、Linux内核优化

打开配置文件

```Shell
vim /etc/sysctl.conf
1
```

加载新的配置(需开启防火墙iptables，否则会报错)

```Shell
sysctl -p
1
```

[收藏的详情地址](https://www.cnblogs.com/lldsn/p/10489593.html)

```Java
https://www.cnblogs.com/lldsn/p/10489593.html
1
```

## 十三、用户权限操作

### 1、用户操作

添加用户 `sum`:

```Shell
useradd –d /usr/sum -m sum
1
```

关于useradd的某些参数：

**-u：** 指定 UID，这个 UID 必须是大于等于500，并没有其他用户占用的 UID

**-g：** 指定默认组，可以是 GID 或者 GROUPNAME，同样也必须真实存在

**-G：** 指定额外组

**-c：** 指定用户的注释信息

**-d：** 指定用户的家目录

已创建的用户 `sum`设置密码

```Shell
passwd sum
1
```

用户添加 `root`权限

```Shell
visudo
1
```

找到 `root`用户权限位置
添加与 `root`用户相同权限

```Shell
## Allow root to run any commands anywhere
root    ALL=(ALL)       ALL
eses    ALL=(ALL)       ALL
123
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NzllYmQyYTNiMDNmNzBkZjljYTQ0MmFjODIzMTY0MjFfcVBpNjBCMm9QMkoxZk1YME9zRmNuMlViT3luSlo1MnJfVG9rZW46V2g1bmJMejg2b2hBdWN4ZTlsbWMzandobnVoXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

新建的用户在面显示

```Shell
cat /etc/passwd
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NDgwNTM1MzllNTA1N2ZhNmY5MjcxMGYzZTQ4ZDZkNjBfQ3NRNHpSV1h4SHJ2OUNHczA0V2kyNkdzRkRLTUxFdktfVG9rZW46WFFEOGJzdk83b1V0eTV4b0VKVWNrVXNWbmhmXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

切换下刚才添加的用户

```Shell
su sum
1
```

sum: x:1000:1000:: /usr/sum :/bin/bash
sum: x:0:1000:: /usr/sum :/bin/bash

回到root用户

```Shell
exit
1
```

**修改已有用户信息****`usermod`**

```Shell
usermod 选项 用户名
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=N2FmNDAzMzAwN2NmZjdjMGMzOTBjY2ViZGM3YTUzMjdfZVBRRFZHZGJ2VGlpWXU4TzRBMUlIREExMW90YVJ2dHdfVG9rZW46VVVzRGJ0c1RMb3A2WXJ4UnduQmNOVkZCbnplXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

删除用户文件夹

```Shell
rm -rf /usr/sum
1
```

删除用户 `sum`

```Shell
userdel sum
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTg5ZWU1Y2NiZjM5Nzk2YzgzZGZlNDViOTdjZTEwYTZfeFgxMWxHUTZHbngxdUV2b3RyS3hzZDc2UmRPM2NoUFlfVG9rZW46Q0k1N2J3TDNhbzVYOEF4cE1NMGNXRmRBbm9jXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

### 2、添加组

**添加用户组**

```Shell
groupadd groupname
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YTdhNjZmOGE1MTgxNDc2ZDI5OWQzMDFlZWViYmZmYWJfczMwQmdjcUU2dm1peEV6SW5wTm5Ja0VzaEwzbGtTdjZfVG9rZW46UkdGeGJKRUhhb1RFdDJ4SlRBbmNVOVc1bm9lXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**修改用户组**
使用者权限：管理员用户

```Shell
groupmod 选项 用户组
groupmod  -n new-usergroup  usergroup
12
```

常用的选项有：

* -g GID 为用户组指定新的组标识号。
* -o 与-g选项同时使用，用户组的新GID可以与系统已有用户组的GID相同。
* -n新用户组 将用户组的名字改为新名字

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZWQzZWIwM2RlNjQ3M2E2N2ZkOTJiNjY4ZTU3NTY0NmFfM3M0Nm9VTnZIY0tnZ1NKYnZtSFIzUzhIM1NDaVVxTFlfVG9rZW46SG02UWI2WVBtb2FSUmd4RFFwaWM5ZGNMbmpnXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**删除用户组**

```Shell
groupdel groupname
1
```

可以看到自己的分组和分组id

```Shell
cat /etc/group
1
```

### 3、sudo用户权限操作

> 比如我们使用普通用户操作用户或者操作用户组、以及修改网卡配置文件的时候，需要切换到root用户才操作，此时我们可以使用sudo命令提高普通用户的操作权限，以达到操作目的

`sudo`：控制用户对系统命令的使用权限,root允许的操作。
通过sudo可以提高普通用户的操作权限。
 **使用者权限** ：普通用户

使用root用户权限执行命令，操作

```Shell
sudo -s
1
```

```Shell
sudo   vi /etc/sysconfig/network-scripts/ifcfg-ens33
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MmFiYzIxMzA3MTdiYTIzMzlhZDJhZjgwMmM3N2ExOTVfcGdYS0dlQTFhSTJhMlVQRFVTT1ZBR3ZKUFkyN2Q0T1lfVG9rZW46S21LVmJhTWlrb2dwT1Z4UG9BTmNndlBYbm1IXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

### 4、更换文件所有者

格式：

```Shell
chown [-R] 所有者                 文件或目录
chown [-R] 所有者:所属组         文件或目录
12
```

将 `kibana-8.3.3-linux-x86_64.tar.gz`所有者改为用户 `sum`

```Shell
chown -R sum /usr/sum/kibana-8.3.3-linux-x86_64.tar.gz
1
```

将 `kibana-8.3.3-linux-x86_64.tar.gz`所有者改为用户 `sum`、所有组改为 `sum`

```Shell
chown -R sum:sum /usr/sum/kibana-8.3.3-linux-x86_64.tar.gz
1
```

## 十四、TOP

实时占用的资源:

```Shell
top
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YWUwM2U0ZTQyZTcwZWY5NTlmYmRhNzcyMmJhZGE3NmZfb2VIQ2VkTEpkR2tmV0YyMno5UzRuYU1Va01wYlRkN2xfVG9rZW46RFY5Y2JJSDJ4b2VYUDN4ZG1KT2NLdHNmbnBmXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

top命令执行结果分为两个区域：**统计信息区**和**进程信息区**

### 1、统计信息区

**TOP：任务队列信息，与uptime命令执行结果相同.**

* 15:33:39：系统时间
* up 5:40：主机已运行时间
* 2 users：用户连接数（不是用户数，who命令）
* load average: 1.09, 1.04, 0.98：系统平均负载，统计最近1，5，15分钟的系统平均负载

**Tasks：进程信息**

* 123 total：进程总数
* 3 running：正在运行的进程数
* 120 sleeping：睡眠的进程数
* 0 stopped：停止的进程数
* 0 zombie：僵尸进程数

**%CPU(s)：CPU信息（当有多个CPU时，这些内容可能会超过两行）**

* 42.1 us：用户空间所占CPU百分比
* 2.0 sy：内核空间占用CPU百分比
* 0.0 ni：用户进程空间内改变过优先级的进程占用CPU百分比
* 49.2 id：空闲CPU百分比
* 0.0 wa：等待输入输出的CPU时间百分比
* 6.0 hi：硬件CPU终端占用百分比
* 0.7 si：软中断占用百分比
* 0.0 st：虚拟机占用百分比

**KiB Mem：内存信息（与第五行的信息类似与free命令类似）**

* 3780.9 total：物理内存总量
* 727.4 free：已使用的内存总量
* 668.8 used：空闲的内存总量（free + userd = total）
* 2384.7 buff/cache：用作内核缓存的内存量

**KiB：swap信息**

* 2048.0 total：交换分区总量
* 2046.0 free：已使用的交换分区总量
* 2.0 used：空闲交换分区总量
* 859.6 avail：缓冲的交换区总量，内存中的内容被换出到交换区，然后又被换入到内存，但是使用过的交换区没有被覆盖，交换区的这些内容已存在于内存中的交换区的大小，相应的内存再次被换出时可不必再对交换区写入。

### 2、进程信息区

* PID:进程id
* USER:进程所有者的用户名
* PR:优先级
* NI:nice值。负值表示高优先级，正值表示低优先级
* RES:进程使用的、未被换出的物理内存的大小
* %CPU:上次更新到现在的CPU时间占用百分比
* %MEM:进程使用的物理内存百分比
* TIME+：进程所使用的CPU时间总计，单位1/100秒
* COMMAND:命令名/行
* PPID:父进程id
* RUSER:Real user name（看了好多，都是这样写，也不知道和user有什么区别，欢迎补充此处）
* UID:进程所有者的id
* VIRT:进程使用的虚拟内存总量，单位kb。VIRT=SWAP+RES
* GROUP:进程所有者的组名
* TTY:启动进程的终端名。不是从终端启动的进程则显示为?
* NI:nice值。负值表示高优先级，正值表示低优先级
* P:最后使用的CPU，仅在多CPU环境下有意义
* TIME:进程使用的CPU时间总计，单位秒
* SWAP:进程使用的虚拟内存中被被换出的大小
* CODE:可执行代码占用的物理内存大小
* DATA:可执行代码以外的部分（数据段+栈）占用的物理内存大小
* SHR:共享内存大小
* nFLT:页面错误次数
* nDRT:最后一次写入到现在，被修改过的页面数
* S:进程状态（D=不可中断的睡眠状态，R=运行，S=睡眠，T=跟踪/停止，Z=僵尸进程）
* WCHAN:若该进程在睡眠，则显示睡眠中的系统函数名
* Flags:任务标志

## 十五、文件安装

### 1、文件下载(lrzsz)

下载文件

```Shell
yum install -y lrzsz
1
```

上传文件

```Shell
rz
1
```

保存文件

```Shell
sz
1
```

## 十六、文章PDF版本

[1、2022-02-08](https://download.csdn.net/download/weixin_44624117/79721103)

```Plaintext
https://download.csdn.net/download/weixin_44624117/79721103
1
```
