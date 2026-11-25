---
title: '附录-Gen4-retrain原理'
categories: ["硬件"]
date: 2026-11-24T16:32:18+08:00
lastmod: 2026-11-24T16:32:18+08:00
draft: false
---
# Gen4 Retrain & Reporting: Why It Works This Way

Research analysis of three observations on the unlocked CMP 170HX 8GB (GA100):
1. Why Gen4 needs a **config-space retrain** instead of the RM `SET_PCIE_SPEED` call.
2. How our **FF/fuse + PHY state compares to the A100/A30** references.
3. Why the system **reports Gen3 while the link runs Gen4**.

All source citations are from `open-gpu-kernel-modules 610.43.03` (the exact driver
in use) unless noted. Companion docs: `cmp_gen3.md`, `cmp_gen4.md`, `cmp_burn.md`.

---

## 0. The measured end state (reference for everything below)

| Item | Value | Source |
|---|---|---|
| `MAGIC_D` (0x820520) | `0x00200000` | burned (block47=0, block46 bit13 cleared) |
| `LINK_CONFIG_0` (0x8C040) | `0x80004C00` | E1 write (SPEED field = 0) |
| `CYA_0` (0x8C2C0) | `0x060711B2` | E1 write |
| `PL_LINK_RATE` (0x8C1C0) | `0x00240036` | gen field[19:16] = 4 |
| `0x88CE4` / `0x88CE0` | `0x14` / `0x02100006` | E1 write |
| internal `LINK_CAP` (0x88084) | `0x00456104` | after E1 |
| config `LnkCap` (CAP_EXP+0C) | `0x6103` -> **`0x7104`** | before -> after retrain |
| config `LnkCap2` (CAP_EXP+2C) | `0x0180001E` | supported speeds vector |
| config `LnkSta` (CAP_EXP+12) | **`0x1104`** | **Gen4 x16 trained** |
| measured bandwidth | H2D 24.74 / D2H 26.34 GB/s | `pcie_bandwidth.py`, 256 MiB pinned |
| `nvidia-smi` Max / Current | **3 / 3** | RM cached view (see §3) |
| `nvidia-smi` Device Max / Host Max | 4 / 4 | fuse capability / root port |

---

## 1. FF / fuse comparison: our card vs A100 vs A30

### 1.1 The four Gen4 `MAGIC_D` bits — now empirically mapped

Stock `MAGIC_D = 0x16680000`; A100 (all SKUs) and A30-class GA100 = `0x00200000`.
The five-bit delta was resolved by one-bit-at-a-time FF derivation:

| MAGIC_D bit | FF location (chain 2) | Burned at row | Evidence |
|---|---|---|---|
| 25 | block 47, bit 3 | 306 | blog FF map (documented) |
| 22, 26, 28 | block 47, bits {0,4,6} | 309 (block47 -> 0x0000) | clearing block47 dropped exactly bits 22,26,28 |
| 19 | block 46, bit 13 | 310 (block46 0xA000 -> 0x8000) | clearing it dropped bit 19, left bit 21 |
| 21 | block 46, bit 15 (inferred) | **not burned — kept** | A100 has bit21 set; it survived both burns |

Derivation trace (measured):
```
stock                 MAGIC_D = 0x16680000   bits 19,21,22,25,26,28
after row306 (b47 bit3) MAGIC_D = 0x14680000   bits 19,21,22,26,28
after row309 (b47 = 0)  MAGIC_D = 0x00280000   bits 19,21
after row310 (b46 bit13) MAGIC_D = 0x00200000  bit 21   == A100 exactly
```
This confirms Amogh's "Gen3 needs one fuse, Gen4 needs four": the four Gen4 bits
are 19, 22, 26, 28 (bit 25 being the separately-documented `GEN4_SPEED_DISABLED`,
NVIDIA bug 2220334). **Our card's `MAGIC_D` is now bit-identical to a retail A100.**

### 1.2 Pre-burn chain-2 blocks (from `tools/ff.json`) vs post-burn

| block | pre-burn | bits | post-burn | role |
|---|---|---|---|---|
| 37 | 0x4184 | 2,7,8,14 | unchanged | DEVIDA |
| 38 | 0x4184 | 2,7,8,14 | unchanged | DEVIDB |
| 39 | 0x0782 | 1,7,8,9,10 | 0x0580 (row305) | Gen3 speed gate (bits 1+9) |
| 46 | 0xA000 | 13,15 | 0x8000 (row310) | MAGIC_D bit19 (13), bit21 (15) |
| 47 | 0x0059 | 0,3,4,6 | 0x0000 (rows306,309) | MAGIC_D bits 22,25,26,28 |
| 49 | 0x00E4 | 2,5,6,7 | 0x0024 (row307) | BOOT_GEN23 (6), BOOT_GEN3 (7) |

### 1.3 PHY register state vs the A100 reference — now matching

A100 reference values from the Consensus-Protocol wiki (`pcie-subsystem.md`,
`pcie-gen3-gen4.md`, measured on a reference A100 80GB) and JRex's fuse table:

| Register | CMP stock | **ours now** | A100 ref | match |
|---|---|---|---|---|
| `MAGIC_D` 0x820520 | 0x16680000 | **0x00200000** | 0x00200000 | **exact** |
| `LINK_CONFIG_0` 0x8C040 | 0x800C4C00 | **0x80004C00** | 0x80004C00 | **exact** |
| `CYA_0` 0x8C2C0 | 0x068731B7 | **0x060711B2** | 0x060711B2 | **exact** |
| `PL_LINK_RATE` 0x8C1C0 | 0x00140036 | **0x00240036** | 0x00040036 | gen field = 4 both; bit21 differs |
| `0x88CE4` | 0x3F | **0x14** | 0x14 | **exact** |
| `0x88CE0` low 6 bits | 0x02 | **0x06** | 0x06 | **exact** |
| `LnkCap2` 0x880A4 | 0x00000002 | **0x0180001E** | 0x0180001E | **exact** |
| `LnkCap` 0x88084 | 0x00456101 | 0x00456104 | 0x00457104 | speed nibble 4 both; bit12 differs |
| `LnkCtl2` 0x880A8 | 0x00000001 | 0x00000004 | 0x001F0004 | target 4 both; upper bits differ |

Two residual deltas worth noting (neither blocks Gen4):
- **`LnkCap` bit12** (`0x00456104` vs A100 `0x00457104`): a capability flag outside
  the speed nibble; the link trains Gen4 x16 regardless.
- **`PL_LINK_RATE` bit21** (`0x00240036` vs `0x00040036`): bit21 read back set even
  when we wrote it clear — it is hardware-driven, not a writable config bit. The
  gen field[19:16] = 4 (Gen4) is what matters and it matches.

### 1.4 The `LINK_CONFIG_0` SPEED encoding (why 0 = Gen4)

`LINK_CONFIG_0[19:18]` uses a **reversed** encoding (wiki, corroborated by the
stock/measured values):

| field value | meaning |
|---|---|
| 0 | Gen4 (16 GT/s) — "max" |
| 1 | Gen3 (8 GT/s) |
| 2 | Gen2 (5 GT/s) |
| 3 | Gen1 (2.5 GT/s) |

Cross-check: CMP stock `0x800C4C00` -> field = 3 = Gen1 (matches stock Gen1 link);
A100 `0x80004C00` -> field = 0 = Gen4. Our Gen3 build wrote 1, E1 writes 0.
**Do not confuse this with config-space `LnkCtl2` Target Link Speed, which uses
the normal encoding (1=Gen1 ... 4=Gen4).** That asymmetry is why the Gen3 patch
writes `MAX_RATE=1` but `setpci CAP_EXP+30.w=0x3`.

### 1.5 Why the fuses alone were not enough (two independent gates)

The A100 comparison shows **two** separate Gen4 gates, and we had to defeat both:

1. **Fuse gate** — `MAGIC_D` bits {19,22,26,28} + bit25. Cleared permanently by FF
   burns. This is what the A100/A30 have clear and stock CMP has set.
2. **DevInit PHY-init gate** — the A100 DevInit runs a Gen4 programming block that
   writes `0x88CE4 = table[+0xC9]` (A100 `0x14`, CMP `0x3F`), `0x88CE0` low6
   (A100 `0x06`, CMP `0x02`), LTSSM timeouts `0x8D1A0/0x8D1A4`, and
   `0x88610 = 0x1001`. On CMP a **suppress flag at table+0x0F = 0x01** branches
   around that whole block (A100 = 0x00). Those bytes live inside the
   `csecret(2)` MAC range, so the VBIOS cannot be edited.

**E1 is a runtime replay of the suppressed DevInit Gen4 block.** That is exactly
why the register values we write (`0x14`, low6 `0x06`, `0x1001`) are the A100
values — we are executing the block the CMP VBIOS skips. Fuses alone leave the
PHY un-initialised for Gen4; E1 alone leaves the capability fuse-gated. Both are
required, which matches the wiki's "PCIe double-locked: fuse + devinit" note.

The A30 dump (GA100 24GB, Gen3/4 + NVLink + ECC enabled) independently corroborates
the target: `MAGIC_D = 0x00200000`, `BOOT_GEN23 = BOOT_GEN3 = 0`,
`DISABLE_GEN3_SPEED = 0`, `PCIE_LANE_DISABLE = 0`. Our card now matches all of
those. (A30's `ECC_EN = 1` / `FEATURE_OVERRIDE_ECC = 0x1111` is the fuse-based ECC
path; we use cmpunlocker's software ECC instead.)

---

## 2. Why the RM call fails but a config-space retrain works

### 2.1 `SET_PCIE_SPEED` is routed to GSP-RM (closed firmware)

`NV2080_CTRL_CMD_BUS_SET_PCIE_SPEED` = `0x20801805`. In the generated export table
(`src/nvidia/generated/g_subdevice_nvoc.c:10606-10620`):

```c
{   /* [441] */
    /*pFunc=*/    &subdeviceCtrlCmdBusSetPcieSpeed__EXPORT,
    /*flags=*/    0x44u,
    /*methodId=*/ 0x20801805u,
    /*paramSize=*/sizeof(NV2080_CTRL_BUS_SET_PCIE_SPEED_PARAMS),
}
```

Decoding `0x44` against `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.h`:
- `0x40` = `RMCTRL_FLAGS_ROUTE_TO_PHYSICAL`
- `0x04` = `RMCTRL_FLAGS_PRIVILEGED`

So the call is **routed to the physical RM — i.e. GSP-RM on this GSP-based
driver**. `subdeviceCtrlCmdBusSetPcieSpeed_IMPL` has **no body in the open tree**
(only the declaration in `g_subdevice_nvoc.h:515` and the export wrapper). The
implementation lives in the closed RM/GSP firmware. The `0x56`
(`NV_ERR_NOT_SUPPORTED`, `nvstatuscodes.h:115`) is returned by that closed code.

The API itself is *not* the limitation — `ctrl2080bus.h:708-713` explicitly defines
```c
NV2080_CTRL_BUS_SET_PCIE_SPEED_2500MBPS  (0x1)
NV2080_CTRL_BUS_SET_PCIE_SPEED_5000MBPS  (0x2)
NV2080_CTRL_BUS_SET_PCIE_SPEED_8000MBPS  (0x3)
NV2080_CTRL_BUS_SET_PCIE_SPEED_16000MBPS (0x4)   <- Gen4 is a valid parameter
NV2080_CTRL_BUS_SET_PCIE_SPEED_32000MBPS (0x5)
NV2080_CTRL_BUS_SET_PCIE_SPEED_64000MBPS (0x6)
```
Gen4 is a legal argument; the *implementation* refuses it. This is why passing 4
was never a parameter-encoding mistake.

### 2.2 What the closed handler validates against — the boot-time cache

The most probable gate (strongly supported by the open code) is the **cached link
capability**, see §3. GSP-RM validates a requested speed against
`pKernelBif->pcieConfigReg.linkCap`, which was captured **at boot when the link
was Gen3**. Gen1/2/3 pass that check; Gen4 exceeds the cached max and is rejected
`NOT_SUPPORTED`. Consistent with:
- The rejection persisted with `RMPcieLinkSpeed=0x15` (correct Gen4 allow-mask).
- The rejection persisted after the fuses were permanently cleared.
- The rejection persisted after E1 raised the *live* internal cap to Gen4 —
  because the **cache** was never refreshed.

The wiki's independent GSP disassembly finding agrees: GSP has "speed reads with
Gen1/2/3 branching where Gen4 falls into the default path", and GSP never writes
`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.

### 2.3 Why the config-space retrain bypasses all of it

```bash
setpci -s <bridge> CAP_EXP+30.w=0x4   # root port Target Link Speed = Gen4
setpci -s <gpu>    CAP_EXP+30.w=0x4   # endpoint Target Link Speed = Gen4
setpci -s <bridge> CAP_EXP+10.w=0x20  # LnkCtl bit5 = Retrain Link
```

This writes **PCI config space directly** and sets the standard PCIe **Retrain
Link** bit. The retrain is then executed by the **LTSSM — the PCIe link hardware
state machine** — negotiating with the root port via TS1/TS2 ordered sets. Path:

```
host setpci -> config space -> LTSSM (hardware) -> PHY
```

It never enters RM/GSP, so it consults **none** of:
- the cached `linkCap` (stale Gen3),
- the `RMPcieLinkSpeed` policy mask,
- the closed `SET_PCIE_SPEED` validation.

The only things it needs are the **hardware** prerequisites, which we supplied:
- Gen4 capability fuses cleared (so the endpoint's PHY will advertise/accept Gen4),
- the Gen4 PHY init applied (E1: `0x88CE0/CE4`, `CYA_0`, `MAX_RATE=0`, VSEC),
- a Gen4-capable root port and a channel that passes Gen4 equalisation (direct
  slot + the 24-capacitor mod).

**Evidence that the hardware path fully succeeded:** config-space `LnkCap`
*regenerated* from `0x6103` (Gen3) to `0x7104` (Gen4) after the retrain, `LnkSta`
became `0x1104`, and bandwidth measured 24.74/26.34 GB/s. The `LnkCap`
regeneration is the PHY re-advertising its capability — the same "PHY reflection"
behaviour the wiki documented for the Gen2 unlock.

### 2.4 Summary of the asymmetry

| | RM `SET_PCIE_SPEED(4)` | config-space retrain |
|---|---|---|
| Executes in | GSP-RM firmware (closed) | PCIe LTSSM hardware |
| Checks cached `linkCap` (Gen3) | yes -> rejects | no |
| Checks `RMPcieLinkSpeed` policy | yes | no |
| Needs Gen4 fuses cleared | yes | yes |
| Needs E1 PHY init | yes | yes |
| Result on this card | `0x56 NOT_SUPPORTED` | **Gen4 x16 trained** |

The RM path is a *policy/firmware* gate; the config-space path is the *hardware*
mechanism. We satisfied the hardware prerequisites and used the hardware path.

---

## 3. Why the system reports Gen3 while running Gen4

### 3.1 The smoking gun: RM caches link capabilities at boot

`src/nvidia/src/kernel/gpu/bif/kernel_bif.c:1253-1277`:

```c
kbifGetGpuLinkCapabilities_IMPL(OBJGPU *pGpu, KernelBif *pKernelBif)
{
    ...
    if (NV_OK != GPU_BUS_CFG_RD32(pGpu, addrLinkCap, &data)) { ... }

    // Cache link capabilities here to be used by GSP-RM
    pKernelBif->pcieConfigReg.linkCap = data;

    return data;
}
```

And it is called from **state load (boot)** — `kernel_bif.c:93-94`:

```c
    // Cache GPU link capabilities
    kbifGetGpuLinkCapabilities(pGpu, pKernelBif);
```

So at driver init RM reads `LnkCap` **once** and stores it in
`pKernelBif->pcieConfigReg.linkCap`, explicitly "to be used by GSP-RM". At that
moment the link was **Gen3** (`0x6103`) — DevInit had latched Gen3 and E1 had not
run yet. Every later NVML/RM capability query is served from that stale cache.

The reporting chain (`kernel_bif.c:1444-1560`) then maps the cached fields into
`NV2080_CTRL_BUS_INFO_PCIE_LINK_CAP_*` (`_CURR_LEVEL_GEN3/GEN4`,
`_MAX_SPEED_*`), which is what NVML surfaces as `nvidia-smi` "PCIe Generation".

### 3.2 Two different views of the same link

| View | Source | Value | Live? |
|---|---|---|---|
| `nvidia-smi` Max / Current | RM cache `pcieConfigReg.linkCap`, captured at boot | **3 / 3** | **no — stale** |
| `nvidia-smi` Device Max | fuse-derived capability (`MAGIC_D` etc.) | 4 | reflects burned fuses |
| `nvidia-smi` Host Max | root port capability | 4 | host side |
| `setpci CAP_EXP+12.w` (`LnkSta`) | **live PCIe config space** | **0x1104 = Gen4 x16** | **yes** |
| `setpci CAP_EXP+0C.w` (`LnkCap`) | live config space (PHY reflection) | 0x7104 = Gen4 | yes |
| measured bandwidth | actual DMA throughput | 24.74 / 26.34 GB/s | yes |

Because our retrain went through **hardware**, RM never observed a speed change
and never refreshed its cache. RM's own link-management path (which would update
its state) is exactly the path that returns `NOT_SUPPORTED` for Gen4. Hence the
split: **hardware Gen4, RM-reported Gen3.**

This is the same class of reporting artefact the wiki catalogued:
- "On a Gen2-trained 170HX, `/sys/.../max_link_speed` still reads 2.5 GT/s while
  `current_link_speed` reads 5.0 GT/s."
- "`nvidia-smi` has reported `PCIe Generation Max: 2` on a stock card since 2023
  while `Device Current` and `Device Max` both read 1."
- The field data's Gen2 boot-window catch: "NVML reads through the RM, which never
  saw the early-boot retrain" — **identical mechanism**, one generation up.

### 3.3 It is cosmetic, not a functional limit

The link is genuinely Gen4 x16: `LnkSta = 0x1104` and 24.74/26.34 GB/s (Gen3 x16
would be ~13 GB/s; Gen4 x16 theoretical is ~31.5 GB/s, and ~26 GB/s measured is
the expected real-world figure). Nothing is throttled by the reporting.

**Authoritative checks (use these, not `nvidia-smi`):**
```bash
setpci -s 01:00.0 CAP_EXP+12.w                    # LnkSta: 0x1104 = Gen4 x16
sudo lspci -s 01:00.0 -vv | grep -E 'LnkCap:|LnkSta:'
cat /sys/bus/pci/devices/0000:01:00.0/current_link_speed   # expect 16.0 GT/s
cat /sys/bus/pci/devices/0000:01:00.0/current_link_width   # expect 16
python3 tools/pcie_bandwidth.py                   # ~25-30 GB/s
```
`current_link_speed` is read by the kernel from live config space, so it should
agree with `setpci` even though NVML does not.

### 3.4 Can the reporting be corrected?

Only by making RM re-read the capability **while the link is Gen4** — i.e.
refresh `pcieConfigReg.linkCap` after the retrain. Options, in order of risk:
1. **Leave it.** Cosmetic; verify with `setpci`/sysfs/bandwidth. Recommended.
2. **Re-probe the device after retrain** (remove/rescan or module reload) so
   `kbifStateLoad` re-caches. **Risky:** a reload re-runs DevInit/GSP boot, which
   re-latches Gen3 and re-clamps the PHY — likely dropping the link back and
   requiring E1 + retrain again. Not worth it for a cosmetic field.
3. Patch the driver to refresh the cache post-retrain (a small
   `kbifGetGpuLinkCapabilities()` call after the retrain). Feasible but touches
   cmpunlocker; only worth it if a workload actually reads NVML link speed.

---

## 4. Implications for persistence

The winning sequence is **fuse (permanent) + E1 (volatile) + hardware retrain**:
- The **fuses are permanent** — `MAGIC_D = 0x00200000` survives power cycles.
- **E1 is volatile** — the DevInit Gen4 block is suppressed on every boot, so
  `0x88CE0/CE4`, `CYA_0`, `MAX_RATE`, VSEC must be re-applied each boot.
- The **retrain must be the config-space path**, not `cmp-pcie-speed 4`.

So a boot service would have to: (a) apply E1 register writes, (b) `setpci`
target 4 on both ends + Retrain Link on the bridge, (c) verify
`LnkSta == 0x1104`. It must **not** use the RM call (`0x56`) and must not
retry-loop (a failed Gen3/Gen4 transition can drop the GPU off the bus; cold
boot recovers). Such a service was drafted but NEVER tested -- only the
manual retrain sequence was validated -- and is not part of this release.
Persistence across reboots is unproven; re-apply the sequence manually each
boot.

Note the existing `cmp-gen4.sh` uses the RM path and therefore **cannot** train
Gen4 on this card; a `setpci`-based script is required.

---

## 5. Open items / honest limits

- The exact closed-GSP validation that returns `0x56` is inferred (cached
  `linkCap` + Gen1/2/3 branching), not directly observed — the implementation is
  not in the open tree. The inference is consistent with every measurement.
- `LnkCap` bit12 and `PL_LINK_RATE` bit21 deltas vs A100 are unexplained but
  demonstrably do not block Gen4 x16.
- `MAGIC_D` bit21 -> block46 bit15 is inferred by elimination (bit13 was proven to
  be bit19, and bit21 survived), not directly burned/verified.
- Gen4 stability needs a sustained load run (AER/Xid watch) and a cold-boot
  repeatability check before being trusted for production work.

## Sources

- `open-gpu-kernel-modules 610.43.03`:
  - `src/nvidia/generated/g_subdevice_nvoc.c:10606-10620` (SET_PCIE_SPEED flags 0x44)
  - `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.h:199,230` (PRIVILEGED, ROUTE_TO_PHYSICAL)
  - `src/nvidia/src/kernel/gpu/bif/kernel_bif.c:93-94, 1253-1277, 1444-1560`
    (boot-time linkCap cache + reporting map)
  - `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.h:700-713` (speed params)
  - `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.h:115` (0x56 = NOT_SUPPORTED)
- Consensus-Protocol/cmp170hx wiki: `docs/hardware/pcie-subsystem.md`,
  `docs/frontier/pcie-gen3-gen4.md`, `docs/hardware/vbios.md` (A100 reference
  register values, DevInit Gen4 block + suppress flag, reporting artefacts).
- JRex286 GA100 fuse/register reference table (A100/A30-class `MAGIC_D`).
- Local: `tools/ff.json` (pre-burn chain 2), `cmp_burn.md`, `cmp_gen3.md`,
  `cmp_gen4.md`, measured logs in this project's session.
