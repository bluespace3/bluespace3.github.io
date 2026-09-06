---
title: '开机连环冻结事故-systemd-enable链接残留'
categories: ["工具"]
date: 2026-09-06T22:51:59+08:00
lastmod: 2026-09-06T22:51:59+08:00
draft: false
---
# 开机连环冻结事故复盘：改写 unit 文件 ≠ 取消自启

> 日期：2026-09-06 ｜ 级别：重大事故 ｜ 现象：46 分钟连续死机重启 9 次
> 教训关键词：`systemctl enable` 残留链接、page reclaim 活锁冻结、earlyoom 兜底

## 一、事故现象

9月6日 21:47–22:23，机器 46 分钟内连续冻结重启 9 次：

- 每次开机只活 1~9 分钟，登录开 ComfyUI 干活约 2 分钟后整机僵死
- 死前特征：journald 刷 `Under memory pressure, flushing caches`、鼠标 `SYN_DROPPED`、日志戛然而止
- **没有任何内核报错、没有 OOM kill 记录**——不是进程被杀，是整机活锁冻结，只能断电
- 22:26 手动 `systemctl disable flashnext` 后（boot 0）立刻稳定，至今无复发

## 二、根因链（证据闭环）

| 时间 | 事件 | 证据 |
|------|------|------|
| 08-31 00:42 | `systemctl enable flashnext` | sudo journal 留痕 |
| 09-05 13:57 | 重写 flashnext.service（换 AWQ 模型），自以为改成"手动启动" | unit 文件 mtime |
| 09-06 21:47 起 | **每个 boot 开机 12–15 秒 systemd[1] 照样拉起 vLLM** | 各死亡 boot 的 `Starting flashnext.service` |
| 拉起后 | vLLM 加载：PLE mmap 预热灌入 42.28G page cache + 权重驻留 39.7G | pipeline.log |
| 登录开 ComfyUI | 双实例默认 RAM 缓存模型，内存雪上加霜 | journal |
| ~2 分钟后 | 60G RAM 耗尽 → 冻结 | `Under memory pressure` 刷屏 |

### 核心机制 1：enable 链接残留

`systemctl enable` 的产物是 `multi-user.target.wants/` 目录里的**符号链接**，不是 unit 文件内容。
所以：

- 重写/替换 unit 文件 → 旧符号链接**依然存在、依然生效**
- unit 文件缺 `[Install]` 段 → 只影响"以后再 enable"，不影响"已存在的链接"
- `systemctl cat` 看不到链接；`grep flashnext /etc/systemd/system/` 也搜不到（链接文件名才含 unit 名）

**只有 `systemctl disable` 才删链接。** 这就是"明明已经改成手动了，开机还是自启"的全部真相。

### 核心机制 2：为什么是"冻结"而不是"报错"

之前为防止 systemd-oomd 误杀用户单元，把它 mask 掉了 → 系统失去用户态 OOM 杀手。
RAM 耗尽时，内核看到还有 47G swap 未用 → 选择"慢慢换页回收"而不是杀进程 → **page reclaim 活锁**：所有进程卡在 IO/缺页上，鼠标丢事件，桌面假死，日志停摆。这种死法不产生任何 OOM 日志，排查时极易误判为内核/驱动问题（本次内核恰好 09-05 刚升到 7.0.0-31，一度是头号嫌疑，最终靠 boot 0 同内核稳定运行排除）。

## 三、诊断三板斧（下次直接用）

```bash
# 1. 判断"开机连环死"是否自启服务作祟：死亡 boot 里找开机十几秒的大服务
journalctl -b -1 | grep -E 'systemd\[1\]: (Starting|Started)' | grep -iE 'vllm|flash|model|comfy'

# 2. 查 enable 残留链接（不是看 unit 内容！）
systemctl is-enabled <unit>          # 返回 enabled 就有链接
find /etc/systemd/system -name '*.wants' -exec ls -la {} \; | grep <unit>

# 3. 冻结 vs OOM-kill 的区分
journalctl -b -1 | grep -ciE 'under memory pressure'   # 冻结：刷屏+戛然而止
journalctl -b -1 | grep -i 'killed process'            # OOM-kill：有此行且系统存活
```

## 四、永久修复（已全部落地）

1. **断根**：`sudo systemctl disable --now` 清掉 flashnext / vllm-server / automodels-x2pp / bu30b，验证 wants 目录零残留
2. **earlyoom 兜底（新增第 0 层防御）**：内存可用 ≤10% 时优先 SIGTERM python/vllm 大进程，保护 gnome-shell/Xorg——**宁可死进程，不死整机**
   ```bash
   # /etc/systemd/system/earlyoom.service.d/override.conf
   ExecStart=/usr/bin/earlyoom -m 10 -s 100 -r 60 \
     --prefer 'python|vllm|pt_main' --avoid 'systemd|gnome-shell|Xorg|init|pipewire'
   # 坑：Ubuntu 包路径是 /usr/bin/earlyoom，写成 /usr/sbin 会 Start request repeated too quickly
   ```
3. **清理隐患**：删掉 crontab 遗留的 `@reboot swapon`（与 fstab nofail 重复且有挂载竞态）；清掉 user@.service.d 下每次开机刷 Invalid syntax 的废弃 drop-in
4. **沉淀**：死法 5（enable 链接残留）写入 skill `comfyui-ram-freeze-prevention`，earlyoom 第 0 层写入 skill `comfyui-oom-fix`

## 五、军规（防第四次）

- **改 unit 文件 ≠ 取消自启。** 想断自启必须 `disable --now`，并以下次开机 `journalctl -b | grep -c 'Starting <unit>'` = 0 收口验证
- **mask 了 systemd-oomd 的机器必须装 earlyoom**，否则内存爆 = 整机冻结而不是可控杀进程
- **CF/vLLM 互斥**照旧：跑 ComfyUI 管线前 `nvidia-smi --query-compute-apps` 确认无模型服务占卡，同时它们也是 RAM 的两大户
- 需要 FlashNext 时手动 `sudo systemctl start flashnext`，用完 stop
