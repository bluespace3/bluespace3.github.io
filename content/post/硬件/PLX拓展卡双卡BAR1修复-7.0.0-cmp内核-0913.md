---
title: 'PLX拓展卡双卡BAR1修复-7.0.0-cmp内核-0913'
categories: ["硬件"]
date: 2026-09-13T15:44:08+08:00
lastmod: 2026-09-13T15:44:08+08:00
draft: false
---
# PLX 拓展卡双卡 170HX 初始化失败修复全记录（7.0.0-cmp 内核）

日期：2026-09-13 ｜ 状态：✅ 已修复并验证

## 一句话结论

两张 CMP 170HX 同时插在 PLX PEX9765 拓展卡后面时 GSP 初始化失败、nvidia-smi 卡死，根因是**内核 PCI 桥窗口计算不考虑子设备 64GB 对齐**导致双卡 BAR1 都退回 64MB；用 bayley 的两个内核补丁构建 `7.0.0-cmp` 内核后，双卡 BAR1 各 65536MB，P2P 6.7GB/s（Gen2 x16 打满）。

## 故障现象与根因

- 拓扑：`00:01.1`(CPU 根端口) → PLX 上游 `01:00.0` → 下游 `02:04.0`/`02:08.0` → GPU `03:00.0`/`04:00.0`
- 症状：dmesg `CMP BAR1: final size = 64 MB`（应为 65536）、Booter failed 0x31、PLM 全 F、`RmInitAdapter failed! (0x62:0x65:2120)`、GSP 每 60s 重试风暴、nvidia-smi D 状态
- 关键对照（journalctl 按 boot 对比）：
  - PLX + 单卡：BAR1=65536MB 正常（boot -6/-5）
  - PLX + 双卡：BAR1=64MB 失败（boot -4/-1/0）
  - 直连双卡：正常（更早记录）
- 根因：双卡各需 64GB **64GB 对齐**的 BAR1 窗口。内核 `pbus_size_mem()` 用 `max(size,align)` 而非 `ALIGN(size,align)` 估算桥窗口，把 ~256GB 的地址空间需求低估；resize 失败整体回滚，两张卡一起退回出厂 64MB。单卡能成功是因为窗口重分配刚好够用。
- 附带发现：反复失败的 GSP 初始化会拖脏内核 vmalloc 子系统（`vmap_pages_pud_range` WARNING → `Cannot fork`），高负载构建时叠加直接压挂机器。

## 修复方案（bayley kernel-patches）

源码：`~/cmpunlocker-bayley/kernel-patches/`
- `0001` `drivers/pci/setup-bus.c`：桥窗口按子设备对齐累加（`size += ALIGN(r_size, align)`）
- `0002` `drivers/pci/quirks.c`：`quirk_nvidia_cmp170hx_bar1` EARLY quirk，枚举前把 `10de:20c2` 的 BAR1 REBAR 编程到 64GB，让桥窗口一开始就按 64GB 分配

构建（构建树保留在 `/mnt/nvme0/kernel-cmp/linux-7.0`）：
- 基线：kernel.org `linux-7.0` tarball + `/boot/config-7.0.0-31-generic` + `LOCALVERSION="-cmp"`
- 必装依赖：`bison flex libelf-dev cpio libdw-dev gawk`（gawk 是 7.0 新增 modules.builtin.ranges 需要，缺了 vmlinux 无声失败）
- 清 `SYSTEM_TRUSTED_KEYS/SYSTEM_REVOCATION_KEYS`（无 Canonical 证书）
- `make -j12` + `ionice -c2 -n7 nice -n5`（-j16 曾叠加 GPU 重试压挂机器）
- **装模块必须 `sudo make INSTALL_MOD_STRIP=1 modules_install`**：Ubuntu config 自带 DEBUG_INFO_DWARF5，不剥离的话 /lib/modules 膨胀到 8.5G（amdgpu.ko 单个 706MB），剥离后 649M
- nvidia 模块：`sudo /usr/lib/cmpunlocker/rebuild.sh 7.0.0-cmp` 直接成功（610.43.02 + NDIV=70 + P2P 强制开）

## GRUB 与两个大坑

1. **`disable_acs_redir` 多设备列表用分号 `;`，不是逗号**。内核 `pci_dev_str_match` 以 `;` 分隔；逗号会被 `pci_setup` 拆成独立的 `pci=` 子选项（第二个设备起全部报 `Unknown option` 丢弃）。旧参数 `00:01.1,00:02.1` 其实一直只有第一项生效。
2. **GRUB 自己又把未转义的 `;` 当命令分隔符吃掉**。`/etc/default/grub` 里必须写成 `\\;`，grub.cfg 里生成 `\;`，内核才收得到 `;`。本次首次冷启动 `/proc/cmdline` 里 `;` 后全被截断（只关了 00:01.1），修转义后要再重启一次才对 PLX 下游口生效。

当前参数（已验证进入 grub.cfg）：
```
pci=realloc pci=hpmmioprefsize=2T pci=disable_acs_redir=0000:00:01.1\;0000:02:04.0\;0000:02:08.0
```

3. 无显示器机器的启动安全网：`/etc/grub.d/01_cmp_recordfail_fallback`，recordfail=1 时自动回退 `7.0.0-31-generic`（成功启动后 grub-common.service 自动清标志）。

## 验证结果（7.0.0-cmp 冷启动后）

- `dmesg`：两卡 `CMP 170HX: BAR1 REBAR programmed to 64GB before enumeration` + `CMP BAR1: final size = 65536 MB` ×2
- Booter/RmInitAdapter 失败仅集中在启动最初 4 秒的 GSP 预热重试（历史同款，正常），之后 0 新增；`nvidia-smi` 秒回，双卡 65536MiB
- `nvidia-smi topo -m`：GPU0↔GPU1 = **PIX**（同 PLX 交换机，比直连的 PHB 更优）
- `p2p_test`：双向 **6.70 GB/s**，无 aliasing（Gen2 x16 ≈8GB/s 已打满，符合 bayley gen2-retrain 设计）
- FlashNext PP2（pipeline-parallel-size=2 跨双卡）正常运行、推理抽查 OK
- 服务恢复：170tune-bootcheck / 170tune-persist / gpu-idle-watchdog 已 enable+运行；flashnext 保持 enable 但本次不 --now（用户手动起的实例占着 8000，其 ExecStartPre 端口检查会拒启，属预期）

## 遗留 / 下次重启注意

- ACS 分号转义修复后**尚未重启验证**：下次冷启动后检查 `cat /proc/cmdline` 应含完整三设备列表、`lspci -vv` 里 `02:04.0/02:08.0` 变 `ReqRedir-`。当前 6.7GB/s 是 ACS 重定向经根端口的路径，关掉 PLX 下游口重定向后理论同速或略优（Gen2 带宽已是硬顶）。
- 构建树 `/mnt/nvme0/kernel-cmp/`（约 25G）可保留用于后续内核升级；不再需要时可清理。
- 若要在 -cmp 上跑 HBM 超频调参（170tune），bayley 状态文件的 BDF 已随新拓扑更新，GPU0 +250/GPU1 +200 偏移照常。
