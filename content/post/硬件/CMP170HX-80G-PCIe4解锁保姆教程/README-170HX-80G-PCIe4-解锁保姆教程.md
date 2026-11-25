---
title: 'README-170HX-80G-PCIe4-解锁保姆教程'
categories: ["硬件"]
date: 2026-11-24T16:32:18+08:00
lastmod: 2026-11-24T16:32:18+08:00
draft: false
---
# CMP 170HX 一步到位：80GB 显存 + PCIe Gen4 解锁保姆教程

> 整理日期：2026-11-19 ｜ 素材已全部落盘在本目录（images/ 全量配图 + 4 份附录原文）
> 本教程 = 社区四条血脉（Kate 的 GA100VFI / dalzyu 的 pico-ga100vfi / CMPGlitch 烧写全记录 / EthanZhangCN 端到端手册）的合成实操版，实操判据全部来自真实跑通的记录（2026-11-15/16 实测：81920 MiB / 128 SM / Gen4 x16 24.7–26.3 GB/s）。

---

## ⛔ 开始前的三句话风险声明

1. **FF 熔丝烧写物理不可逆**。烧错记录可能永久禁用单元或卡死 die。每个阶段末尾都有"✅ 达成判据"，**不过关绝不进下一阶段**。
2. **Gen4 不是软件送的**。它 = 熔丝 + 手焊 24 颗电容 + Gen4 主板，三者缺一不可；不想焊电容的人天花板是 Gen2 x4（约 1.7 GB/s）。
3. **只有 8GB 版（PCI ID `10de:20c2`）有 80GB 潜力**。10GB 版（`2082`）解 80G 已被证实是地址折叠（40G 后写入会覆盖 0 地址区直接崩），目标只能是 40G——社区定案，别再撞墙。

---

## 一、最终成果账（做完你得到什么）

| 项目 | 出厂 | 纯软件解（对照组） | 本教程全解 |
|---|---|---|---|
| 显存 | 8 GB | 64 GB | **81920 MiB (80 GB)** |
| SM | 70 | 74 左右 | **126–128**（超过零售 A100 的 108） |
| PCIe | Gen1 x4（~0.85 GB/s） | Gen2 x4（~1.7 GB/s） | **Gen4 x16（实测 H2D 24.74 / D2H 26.34 GB/s）** |
| 持久性 | — | 每次开机驱动补丁 | 熔丝永久 + 软件层每次开机自动 |

最终验收凭证的样子见 `images/tests.png`（跑分成品的实测截图）。

---

## 二、物料清单（先备齐再动手，缺一样都白搭）

### 2.1 硬件（要花钱买的）

| # | 物品 | 规格/型号 | 数量 | 用途 | 参考价 |
|---|---|---|---|---|---|
| 1 | CMP 170HX 显卡 | **必须是 8GB 版**，`lspci -nn` 里显示 `10de:20c2` | 1 | 主角 | 二手 ~¥1800–2500 |
| 2 | 毛刺板 | **Raspberry Pi Pico 2**（RP2350A）或 Pico 2 W / Waveshare RP2350 Plus-W（RP2350B） | 1 | 打电压毛刺开烧写窗 | ~¥30–60 |
| 3 | 漆包线/细跳线 | 镀锡头，够焊 4 个点 | 4 根 | 接 I2C×2 + PEX_RST + GND | 几块钱 |
| 4 | 烙铁 + 助焊剂 + 吸锡带 + 放大镜/显微镜 | 尖头，能焊 0402 | 1 套 | 卡背面焊 4 根线（必做）+ 电容 mod（要 Gen4 才做） | ¥100–300 |
| 5 | 0402 去耦电容 | **0.22µF / 220nF, X7R, ≥6.3V**；实锤料号：三星 **CL05B224KO5NNNC** | **买 30–40 颗用 24 颗** | 补焊 PCIe lane 4–15 的 AC 耦合电容 → 恢复 x16 宽度 | ¥20 左右 |
| 6 | Linux 主机 | 能 sudo；**要 Gen4 就必须：主板/CPU 的直插 x16 槽支持 16GT/s**（先 `lspci -vv` 查根端口 LnkCap） | 1 | 宿主 | 已有则 0 |
| 7 | 电源 | 1× 8-pin CPU/EPS 线（走附赠矿卡转接线），300W 富余；被动散热卡**必须加装风扇** | — | 供电+散热 | — |
| 8 | （可选·阶段 6 转 A100 才要）nvflash 5.692 + **CH341A + SOP8 烧录夹** | — | 1 | 刷 A100 VBIOS 的唯一离线退路；**不备好别碰阶段 6** | ¥20 |

> 电容 mod 说明：170HX 的 PCB 就是 A100 40G 公版，lane 4–15 的耦合电容被出厂挖掉（走线还在，只有焊盘空着），所以只认 x4。**这一步只改变宽度，不改变代数**；不焊电容任何代数都到不了 x16。手工约 20 分钟/卡，0402 新手先在废料上练。

### 2.2 软件资产（提前全部下载到目标机能摸到的地方）

| # | 仓库/文件 | 地址 | 用途 |
|---|---|---|---|
| 1 | ⭐ 主仓库 `cmp170hx-final-crack` | github.com/EthanZhangCN/cmp170hx-final-crack | 端到端手册 + 一体烧写工具 `utils/ga100_ff.py` + 一键流程 + 全部配图 |
| 2 | `pico-ga100vfi`（submodule） | github.com/dalzyu/pico-ga100vfi | RP2350 毛刺固件 + 主机 CLI（campaign 自动找金窗） |
| 3 | `ga100vfi`（submodule） | github.com/kate-land/ga100vfi | Kate 的 STM32 血脉：寄存器地图、gpu0-capture |
| 4 | `cmp170hx-ffcalc`（submodule） | github.com/sayhellotojungle/cmp170hx-ffcalc | 逐卡算 FF 计划（交叉验证用） |
| 5 | `cmp-170hx-rir-burn-util`（submodule） | github.com/evanrodgers/cmp-170hx-rir-burn-util | 写机制参考 |
| 6 | `open-gpu-kernel-modules-615.71.09.tar.gz`（25MB） | NVIDIA 官网 GitHub Releases | **不入库，需手动放到仓库根目录和 `cmpunlocker/driver/.build/` 两处** |
| 7 | nvidia-open **615.71.09** 用户态（libs+firmware） | 目标机包管理器装 | cmpunlocker 的前提。**⚠️ 千万别用 615.78.08——cmpunlocker 里 VERSION 第一行默认就是它，是坏的** |
| 8 | （备用路线）`cmp.wiki` / Consensus-Protocol/cmp170hx wiki | 社区原理库 | 寄存器/熔丝地图 |

主仓库克隆（国内走 gh-proxy，8118 代理也行）：
```bash
git -c http.proxy=http://xxx.xxx.xxx.xxx:8118 clone https://github.com/EthanZhangCN/cmp170hx-final-crack.git
cd cmp170hx-final-crack
git submodule update --init
# 然后把 open-gpu-kernel-modules-615.71.09.tar.gz 放到：仓库根目录 和 cmpunlocker/driver/.build/
```

### 2.3 目标机系统依赖
```bash
sudo apt install python3 python3-pip gcc make linux-headers-$(uname-r) build-essential cmake ninja-build
# pico-sdk 不用手动装：utils/ff_env_setup.py 会自动拉
```

---

## 三、开工前身份确认（两分钟，决定你有没有资格往下做）

```bash
lspci -nn | grep -i nvidia          # 必须看到 10de:20c2（8GB 版）
nvidia-smi --query-gpu=memory.total --format=csv   # 出厂 8192 MiB
```
- `20c2` ✅ 继续；`2082` ⛔ 你手里是 10G 版，本教程的 80G 目标对它不成立（折叠死案），止步 64G/40G 软件解即可。
- 要 Gen4 的再加一步：`sudo lspci -vv -s <根端口BDF> | grep LnkCap` → 有 `Speed 16GT/s` 才有 Gen4 资格；只有 8GT/s 的主板做到头是 Gen3。

---

## 四、阶段 0：焊线 + 打毛刺进"金窗"（Goldilocks）

> 目的：用电压毛刺**临时**让熔丝控制器这次开机把控制行读成全 0（DSOV=0），拿到"读熔丝 + 烧熔丝"的权限。
> ⚠️ 这个状态**一断电就没了**，它本身不产生任何永久改变；所有烧写必须在同一个上电窗口内完成。

### 4.1 卡背面焊 4 根线（全程可逆，唯一定位靠图）

| 信号 | 卡上焊点 | Pico 引脚 |
|---|---|---|
| I2CC SDA | **Q808 上方的 pad** | GP0（物理 4 脚） |
| I2CC SCL | **Q808 左下的 pad** | GP1（物理 5 脚） |
| PEX_RST | **U809/U810 中间的 pad** | GP22（物理 30 脚） |
| GND | 任意 GND 过孔 | GND（物理 3 脚） |

**实物接线总览**（Pico 平放卡面，USB-C 朝下）：

![实物接线总览](images/board-wiring-overview.jpg)

**焊点特写**（Q808 找 SDA/SCL，U809/U810 中间找 PEX_RST）：

![焊点特写1](images/tap-points-closeup.jpg)

![焊点特写2](images/position.jpg)

**接线示意（信号流向）**：

![接线示意](images/wiring-diagram.jpg)

**接线与时序框图**：

![Pico 接线与时序](images/pico_flow.png)

**更多实拍参考**（pico-ga100vfi 上游社区实拍）：

![社区实拍](images/better_pic.png)

**红线（违反可能烧卡）：**
- PEX_RST 是 **1.8V 网络，直连、禁串电阻**；固件只会拉低/释放，**绝不允许输出 3.3V 高电平**（任何改代码都不许破坏这个不变量）。
- 每个焊点停留 ≤2 秒；显卡和 Pico 之间**直接接一根 GND 线**共地。
- 不需要焊 NVVDD（正常编译用不到采样脚）。

### 4.2 主机先把驱动踢干净（否则读不到卡）

```bash
sudo systemctl stop lightdm lactd; sudo pkill -x Xorg
sudo modprobe -r nvidia_uvm nvidia_drm nvidia_modeset nvidia
sudo mv /etc/modprobe.d/cmp-preflight.conf{,.disabled} 2>/dev/null   # 若有
sudo tee /etc/modprobe.d/aa-blacklist-nvidia-campaign.conf <<'EOF'
blacklist nvidia
blacklist nvidia_drm
blacklist nvidia_modeset
blacklist nvidia_uvm
install nvidia /bin/false
EOF
```

### 4.3 一键准备 Pico 环境 + 打金窗

```bash
# 环境（apt 工具链→pico-sdk→编固件→BOOTSEL 烧 uf2→装 CLI，幂等可重跑）
python3 utils/ff_env_setup.py check                      # 只体检
sudo python3 utils/ff_env_setup.py all --board pico2_w   # 板型必填：pico2_w / pico2
# ⚠️ 用普通 Pico 2（RP2350A）手动编固件时要加 -DBOARD_RP2350A=ON，仓库默认按 RP2350B 编

# 打金窗（自动闭环：三脉冲→判定→自动调压重打，实测中位 5–16 发、几秒中）
sudo env PYTHONPATH=$PWD/pico-ga100vfi/host python3 -m ga100vfi campaign \
  --bdf 0000:2f:00.0 --adaptive --budget 500 --restore-wait 0.4   # BDF 换成你的卡
```

**软件自动判定的流程**（不用示波器、不用肉眼盯波形）：

![毛刺判定流程](images/judge_flow.png)

**实测三脉冲波形**（命令→电压滞后约 46µs，固件已自动补偿）：

![NVVDD三脉冲波形](images/nvvdd-waveform.png)

**遥测界面长这样**：

![campaign遥测](images/campaign-telemetry.png)

### ✅ 阶段 0 达成判据（缺一不可，全满足才往下）
```
"passed": true
DSOV_STATUS  0x00820084 == 0        ← 金窗核心
CRC_STATUS   0x00820070 == 0x55
PRIV_MASK    == 0xffffffff          ← PLM 全开
```
到这一步断电即回原样，卡无任何永久改变。**这个阶段多打几次很安全，放心练手。**

---

## 五、阶段 1：只读采集 + 算这张卡自己的 FF 计划

> 目的：读出**这张卡自己**的熔丝现状和缺陷掩码，算"该烧哪几行、烧什么值"。目标公式只有一句话：**`该禁用X := 真实缺陷X`（只保留真坏的，其余全放开）**。
> ⚠️ **每张卡的计划都不一样，绝对不许抄别人的 plan.json。**

```bash
export PYTHONPATH=$PWD/pico-ga100vfi/host
sudo python3 utils/ga100_ff.py plan --bdf 0000:2f:00.0 -o plan.json    # 纯只读
```
参考量级（一张零坏核 8G 卡的预期）：`FBP_DISABLE 0x852→0x840`、`FBPA/FBIO 0xC0330C→0xC03000`、`GPC 0x13→0`。

### ✅ 阶段 1 达成判据
- `plan.json` 生成且 `records` 非空；每条 `row` **从已用行之后追加（不是 222）**；打印的 `old->new` 只放开非缺陷位。
- 若工具报 `ff_rows 为空` 拒出计划——这是防呆（ffcalc issue#1 案底：从 222 起排会覆盖已有记录），检查读卡，**别绕**。
- 可选双保险：用 `cmp170hx-ffcalc` 独立再算一遍对结果。

---

## 六、阶段 2：烧前预演（强制 dry-run，不许跳过）

```bash
sudo python3 utils/ga100_ff.py burn --plan plan.json     # 默认 dry-run，一个字都不写
```
逐行打印 `row <- record  当前 0x00000000`。

### ✅ 阶段 2 达成判据
- 没有任何一行标 `★非空!`（有空行被占说明计划错，**停**，回阶段 1 重算）；`DSOV=0 / CRC=0x55` 仍然在线。

---

## 七、阶段 3：烧 FF（⛔ 从这里开始永久生效）

> 先做烧前备份（只读），再真烧。金窗易失——**同一个上电窗口内一口气烧完**。

```bash
# 1) 备份整卡熔丝现状（回家的路，永久保留）
sudo python3 CMPGlitch/tools/ff_dump.py --bdf 0000:2f:00.0 -o ff_backup.json

# 2) 先单行试烧（首卡强烈建议）：烧一条 → 物理断电冷启 → CRC 仍 0x55 → 回来重打金窗烧全量
sudo python3 utils/ga100_ff.py burn --plan plan.json --commit

# 或：一键编排（prep→glitch→plan→precheck→burn，断点续跑，两段确认 Y + BURN）
sudo python3 utils/ff_burn_flow.py run --bdf 0000:2f:00.0 --single
```

**这一层实际烧了什么（概念账，看懂再按回车）**：
- chain 1（floorsweep）：GPC/TPC/FBP/FBPA/FBIO/**PES/ROP_L2** 的禁用位缩到只剩真缺陷 → SM 和 HBM 堆全放开；
- chain 2（PCIe）：Gen3 速度闸（block39）、`MAGIC_D` 的 Gen4 四位 {19,22,26,28}+bit25（block46/47 → 与 A100 逐位一致）、boot 策略位（block49）→ 卡从此**宣告** Gen3/Gen4 能力；
- 记录格式 32 位：`(data<<16)|(block<<6)|chain`，写口 **`FUSEWDATA 0x0082000C`**。

**烧写窗前提（工具每次写前自查，心里有个数）**：FUSECTRL=IDLE、CRC=0x55、DSOV=0、SBFE=0、EFP=1、FUSEWDATA_PLM/FUSECTRL_PLM=全开、DEBUGCTRL.RWL=0、目标行全空。

**实测红线（全是别人踩出来的血坑，逐条背）**：
1. 写口是 `0x0082000C`，**不是**读口 `0x00820008`——写错口会"静默成功、回读全 0、记录丢失"。
2. **绝不直接写 PLM 寄存器 `0x8200F4/F8/FC`**（写死熔丝控制器）；正确姿势是清 `WDATA_WR_SECURE(0x82048C)=0`，PLM 自动全开。PLM 是"结果"不是"写入对象"。
3. 主阵列烧写保持 **DEBUGCTRL.RWL=0**；RWL=1 会把写路由去 RIR macro，可能卡死 die。
4. **GPC/TPC/FB* 必须与 PES/ROP_L2 同批烧齐**。漏烧 PES/ROP_L2 的直接后果是 GSP 起不来（`failed to wait for GFW boot complete: 0x55`）——CMPGlitch Pass1 的真实案底。
5. **PCIe 相关记录放最后**，一次烧齐一次验证（写错可能掉总线）。
6. 这台机器类毛病：`reboot` 可能挂死 → 一切重启都用**物理断电冷启**。
7. FF 是"后写赢"：烧错可以在新空白行追加恢复记录改回，但**物理行烧掉就没了**——不可逆的是行，不是值。

### ✅ 阶段 3 达成判据
每条记录 `readback == 写入值`；全程 `CRC=0x55 DSOV=0 EFP=1`；无报错烧完计划。

---

## 八、阶段 4：物理断电冷启 + 功能验收

拔电 ≥30 秒再上电（软 reboot 不清 GSP 残留——社区定案）。

```bash
sudo lspci -vv -s <bdf> | grep -E "LnkCap:|LnkCap2:|LnkSta:"
nvidia-smi --query-gpu=memory.total --format=csv
sudo python3 utils/ga100_ff.py verify --bdf <bdf>
```

### ✅ 阶段 4 达成判据
```
FBP_DISABLE=0x840  FBPA/FBIO=0xC03000  GPC=0
LnkCap2 出现 2.5-16GT/s          ← Gen4 能力已释放
SM 数明显上升；GSP 正常启动（dmesg 干净无 Xid）
```
显存此刻可能还没满 80G——正常，几何归驱动层管，看下一阶段。**显存必须做全量写读验证**（分配 ~76GiB，`a[i]=i^常量` 全写全读，mismatches=0）——只看 `nvidia-smi` 报的容量会被 L2 别名幻觉骗。

---

## 九、阶段 5A：软件层点亮满血 80GB

熔丝只解开"禁用层"，**显存几何每次开机由驱动重写**（永久解的是资格，显现靠补丁）：

```bash
# 1) 装 nvidia-open 615.71.09 用户态（libs+firmware，包管理器）
# 2) 跑仓库自带 cmpunlocker —— ⚠️ 必须显式指定驱动版本！
cd cmpunlocker
sudo CMPUNLOCKER_DRIVER_VERSION=615.71.09 bash install.sh
sudo shutdown -h now     # 冷启
nvidia-smi               # 期望 81920 MiB
```
> `driver/VERSION` 第一行是 615.78.08（**坏的，别用**）；不显式传版本号就会中招。源码 tar 包提前放进 `driver/.build/` 可离线构建。
> 只想求稳的保底档：不烧熔丝直接用社区 cmpunlocker（amoghmunikote 或 bayley 系）= 64GB + Gen2，风险只到驱动层。

---

## 十、阶段 5B：PCIe 实链提速（Gen3 → Gen4）

熔丝只让你"**有资格**"，实链被固件钉死，还要过三关：**电容 mod（宽度）+ 运行时 PHY 写入（解锁被抑制的 Gen3/4 初始化）+ 硬件 retrain（绕开拒绝 Gen4 的固件）**。

### 第 1 关：手焊 24 颗 0402 电容（决定 x16 宽度）
- 位置：PCIe 金手指旁 `C1100–C1350` 区域的空差分对焊盘（**别只按位号焊**，按空焊盘目视 + 原理图交叉确认；板子有 revision）。
- 步骤：刮净原厂无铅焊料→上有助焊剂→拖少量新锡→0402 摆正→最短时间点焊→放大镜查连锡/立碑→酒精清洗→万用表查邻脚短路→上车 `lspci` 看 Width。
- 陶瓷电容**不分极性**。详细作业指导见 `附录-PCIe-x16电容改装.md`（satspace 版全套）。

### 第 2 关：Gen3 打底（已验证稳定跑通的路）
```bash
# /etc/modprobe.d/cmp-gen3.conf 三个参数（CMPGlitch 改版 cmpunlocker 带，驱动 610.43.03 血脉）
options nvidia NVreg_RegistryDwords="RmForceEnableGen2=1;RMPcieLinkSpeed=0x5;CmpGen3=1"

sudo ./install.sh && sudo shutdown -h now
sudo bash tools/cmp-gen3.sh <bdf>          # 分阶训练 Gen1→Gen2→Gen3
setpci -s <bdf> CAP_EXP+12.w               # 读到 0x1083 = Gen3 已训练
python3 tools/pcie_bandwidth.py            # Gen3 x16 ≈ 13.6–15.7 GB/s
```
⚠️ 编码陷阱：`LINK_CONFIG_0[19:18]` 是**反转编码**（0=Gen4、1=Gen3、3=Gen1），和 config 空间 LnkCtl2（4=Gen4）**正好相反**，写反直接坠链。判据永远只认 `LnkSta`（setpci 读），**别信 nvidia-smi 的 gen**（那是 boot 时缓存，不刷新）。Gen3 每次开机要重新训练。

### 第 3 关：Gen4 临门一脚（LTSSM 硬件 retrain，绕开固件拒绝）
背景：`RM SET_PCIE_SPEED(4)` 被闭源固件一口回绝（`NV_ERR_NOT_SUPPORTED 0x56`），Booter 写 `0x881C0` 会当场 wedge GSP 启动（H-WRITE，路线已死勿试）——所以走 config 空间硬 retrain：
```bash
# post-GSP 状态下先把 PHY 写成 A100 的 Gen4 初始态（tools/pcie_gen4_probe.py 一键）：
#   0x88CE4=0x14, 0x88CE0=(old&~0x3F)|0x06, CYA_0=0x060711B2, PL_LINK_RATE gen 字段=4, LINK_CONFIG_0 SPEED=0
setpci -s <桥BDF>  CAP_EXP+30.w=0x4    # 桥侧 Target=Gen4
setpci -s <卡BDF>  CAP_EXP+30.w=0x4    # 卡侧 Target=Gen4
setpci -s <桥BDF>  CAP_EXP+10.w=0x20   # 触发 Retrain Link
setpci -s <卡BDF>  CAP_EXP+12.w        # 读 0x1104 = Gen4 x16 训练成功
```
成功画像（实卡终态）：`LnkSta 0x1104`、带宽 **H2D 24.74 / D2H 26.34 GB/s**、`nvidia-smi` 显示 Max/Current=3/3（无视它）。原理全解见 `附录-Gen4-retrain原理.md`。

### ✅ 阶段 5 达成判据
- `nvidia-smi` 显存 81920 MiB + 全量写读 0 错误；
- `setpci` 读 LnkSta：Gen4 平台=`16GT/s x16`（0x1104），Gen3 平台=`8GT/s x16`；
- 要 NVLink 的另说：清熔丝只是其一，还得**补焊 U11** 参考时钟 IC + 绕 ROM check，无 U11 只做"解锁层验证"别硬上。

---

## 十一、阶段 6（可选，高危）：转成真 A100 80GB PCIe 身份

把熔丝 devid 从 `0x20C2` 烧成 A100 的 `0x20B5`（chain2 block37 记录 `0x416A0942`、block38 `0x416A0982`），再刷**原版签名的 A100 80G VBIOS**（ID 对上后 MAC 校验天然通过，ROM 一字不改）→ 获得原生 81920 MiB + BAR1 128 GiB。实测跑通于 B450M + R5 3600。

**前置缺一不可**：BIOS 开 Above 4G + CSM 关 + MMIO High ≥128G（不开直接卡 VGA 灯）；nvflash 5.692；自己的 CMP ROM 备份（`nvflash --save` + sha256 永久保留）；**CH341A + SOP8 夹（POST 挂死时唯一退路）**。3 个必做 + 2 个检查点必须**同一个金窗周期干完**——每次冷启都是一次未知 POST。完整流程见主仓库 README 阶段 6 + `CMPGlitch/cmp_a100_conversion.md`。
回退账：只烧了熔丝→反烧 block37/38 回 `0x4184` 免刷写器；刷了 ROM 起不来→CH341A 写回备份 ROM。

---

## 十二、翻车速查表（高频十连）

| 现象 | 原因 | 处理 |
|---|---|---|
| 烧写"成功"但回读 0 | 写到读口 0x820008 | 改写口 **0x82000C** |
| 控制器全 0、CRC=0 | 手贱写了 PLM 0xF4/F8 | 重打 campaign；PLM 只许间接开 |
| 冷启后 GSP 起不来 `0x55` | 漏烧 PES/ROP_L2 | 与 GPC/TPC 同批补烧 |
| 金窗打完 DSOV 又变 1 | 中途 PEX_RST/驱动加载 | 卸干净再打，一个窗口烧完 |
| 显示 80GiB 一碰就崩 | 只改几何没验证/L2 别名幻觉 | 全量 fill/verify；8G 卡用真烧熔丝路线 |
| 烧完还 5GT/s | 驱动 boot 后回锁 | Gen3 走 post-GSP+分阶训练；Gen4 走 setpci 硬 retrain |
| Gen4 训不上 | 固件拒 RM API / 主板只到 Gen3 / 没焊电容 | 用 setpci retrain；查根端口 LnkCap；先补电容 |
| 转 A100 后卡 VGA 灯 | 平台 BAR 窗口不够 128G | Above4G+MMIO≥128G；不行就 CH341A 回写 |
| MMU 风暴/no devices | Xid 45/154 残留 | 软 reboot 一次无效→**拔电 ≥30s** 再上电，等 3–5 分钟别狂重启 |
| reboot 机器不回 | 部分主板 reboot 病 | 一律物理断电冷启 |

**持久性一页账**：毛刺=断电即丢｜烧 FF=**永久**（以后插电即解锁）｜显存几何+PCIe 实链=每次开机驱动补丁/训练脚本。

**已知未解（别许愿）**：ECC 全程未烧未验证（别信 nvidia-smi 的 Enabled 显示）；NVLink 需 U11 硬改；10G 版 80G 折叠无解；FP32 满速/128 SM 的"最后一寸"在某些血脉仍需 `cmpunlocker-a100-minimal` 常驻覆盖。

---

## 十三、附录与素材索引（本目录内）

| 文件 | 内容 |
|---|---|
| `附录-烧写全记录.md` | CMPGlitch 逐行烧写记录（rows 293–310 全表 + 烧写窗前提 + 恢复机制） |
| `附录-Gen3实录.md` | Gen3 x16 跑通全程（reg 序列、持久化、调试陷阱） |
| `附录-Gen4研究.md` | Gen4 全部死路与活路（E1–E4 实验档案） |
| `附录-Gen4-retrain原理.md` | 为什么必须硬件 retrain + MAGIC_D 四位逐位归因 + A100 寄存器对照 |
| `附录-PCIe-x16电容改装.md` | 24 电容作业指导（料号、焊盘位置、检查清单） |
| `images/`（10 张） | 接线总览/焊点特写×2/接线示意/时序图/判定流程/波形图/社区实拍/遥测截图/跑分凭证 tests.png |

**上游权威源**：EthanZhangCN/cmp170hx-final-crack（主手册）· dalzyu/pico-ga100vfi · kate-land/ga100vfi（blog.kate.land 原理博文）· sayhellotojungle/esp32-ga100vfi（ESP32-S3 替代毛刺板，同样实卡验证）· Consensus-Protocol/cmp170hx wiki（55 页技术库）· douyamv/douyamv-170hx-80g（80G 方案编号库+硬件操作规程）· blog.kkk.rs 68/71（10G 版折叠死案中文原始调查）

**本机立场备忘**（生产卡提醒）：这套操作会吃掉生产 vLLM 的双卡窗口；FF 不可逆，建议先拿一张卡当"试验田"烧通全流程、跑一夜 memtest 再动生产卡；烧完的卡若进生产，先跑本项目既有 ECC/Xid 监控观察至少一周。
