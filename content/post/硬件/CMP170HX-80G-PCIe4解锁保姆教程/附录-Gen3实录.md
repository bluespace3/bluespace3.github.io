---
title: '附录-Gen3实录'
categories: ["硬件"]
date: 2026-11-24T16:32:18+08:00
lastmod: 2026-11-24T16:32:18+08:00
draft: false
---
# CMP 170HX 8GB -> PCIe Gen3: Unlock Record

Complete record of the PCIe Gen3 link unlock on this card, built on top of the
FF fuse burns (see `cmp_burn.md`). Gen3 validated at ~13.3 GB/s
x16-equivalent (2x Gen2). Read this before touching the PCIe patches or
attempting Gen4.

## Card identity / result

| Field | Value |
|---|---|
| SKU | CMP 170HX 8GB (Hynix HBM) |
| PCI ID | 10de:20c2 |
| BDF | 0000:01:00.0 (upstream bridge 0000:00:01.0) |
| Die | GA100 (PMC_BOOT_0 = 0x170000A1) |
| Host root port | Gen3 x16 (Host Max 3) |
| Link (this record) | **Gen3 trained** (reduced width at measurement; x16 needs direct slot + cap mod) |
| Device Max | 4 (Gen4 capable, fuses burned) |

Measured (256 MiB pinned, `tools/pcie_bandwidth.py`). The link was trained
at **reduced width** (half of the x16 capability) for these runs; the
x16-equivalent columns scale the measured throughput linearly with width:

| Stage | LnkSta | H2D | D2H | H2D (x16-equiv) | D2H (x16-equiv) |
|---|---|---|---|---|---|
| Gen2 (boot default) | 0x1082 | 3.39 GB/s | 3.35 GB/s | 6.78 GB/s | 6.70 GB/s |
| Gen3 (after training) | 0x1083 | 6.67 GB/s | 6.60 GB/s | 13.34 GB/s | 13.20 GB/s |

Full width requires the decoupling-cap mod + a direct x16 slot (Width note
below); the cap mod restores width only, not generation.

~1.97x gain, stable under load, no Xid/AER. Reproduced across a cold boot.

## Why Gen3 needed more than the fuse burns

PCIe on the CMP is **double-locked** (JRex register table):

1. **Option fuses** -> config-space capability (LnkCap / Device Max). Cleared by
   the FF burns (rows 305-307). After burning, Device Max went 2 -> 4.
2. **PHY / devinit** -> actual link training. The IFF/devinit programs the PHY
   for Gen1/2 at boot; the option fuses alone do NOT make the link train Gen3.

So after the burns the card *advertised* Gen3/4 but still *trained* Gen1/2.
Gen2 is reachable by the cmpunlocker register overrides (upstream of the fuse
gate); Gen3 needs the full post-GSP PHY sequence **plus RM-driven training**.

Community context: the CMP wiki lists 8GB Gen3 as **unproven** ("no 8GB
equivalent of the 10GB RIR path"). The proven 10GB Gen3 route uses an RIR burn
to clear `disable_sw_override`, then volatile overrides. This card instead has
the fuses **permanently burned via VFI**, so it skips the RIR prerequisite and
runs the post-GSP Gen3 sequence directly. This 8GB burned-fuse Gen3 result is
novel relative to the public wiki.

## PCIe fuse burns (rows 305-307, chain 2)

From `cmp_burn.md` (pass 3 records):

| Row | Block | Old | New | Encoded | Meaning |
|---|---|---|---|---|---|
| 305 | 39 | 0x0782 | 0x0580 | 0x058009C2 | DISABLE_GEN3_SPEED (bits 1+9 candidates) |
| 306 | 47 | 0x0059 | 0x0051 | 0x00510BC2 | PCIE_MAGIC_BITS_D[25] Gen4 flag |
| 307 | 49 | 0x00E4 | 0x0024 | 0x00240C42 | BOOT_GEN23 + BOOT_GEN3 disable |

Verified post-burn shadows (match an enabled GA100):
- OPT_DISABLE_GEN3_SPEED (0x820250) = 0
- PCIE_MAGIC_BITS_D (0x820520) bit25 = 0
- OPT_PCIE_BOOT_GEN23_DISABLE (0x82057C) = 0
- OPT_PCIE_BOOT_GEN3_DISABLE (0x820580) = 0

## The Gen3 mechanism (two parts)

### Part 1 - post-GSP register sequence (driver)

Runs in `kgspBootstrap_TU102` **after** successful BooterLoad (NOT at probe;
firmware re-clamps earlier writes). Gated on registry key `CmpGen3=1` and
device id 0x20C2/0x2082. Implemented in `driver/patches/pcie-gen3.patch`.

| Register | Offset | Gen3 write |
|---|---|---|
| PRIV_MISC_1 | 0x8841C | set bits 11,13; clear bits 12,14 **and 30,31** |
| PL_CYA_0 | 0x8C2C0 | clear bits **2 and 3** (DIS_G2 + Gen3 disable) |
| LINK_CTRL_2 | 0x880A8 | target speed = 3 (normal encoding) |
| PL_LINK_RATE | 0x8C1C0 | `(v & ~0x000F0000) \| (3 << 16)` (Gen3 rate field) |
| VSEC_HIERARCHY | 0x88610 | **SET bit12** (0x1000) - opposite of Gen2 |
| LINK_CONFIG_0 | 0x8C040 | MAX_RATE = **1** (REVERSED encoding, see below) |
| DLManager | 0x8B8C0 | set bit2, poll LINK_CONFIG_0[4:0]==0, set [3:0]=1, poll, restore |
| XVE_FUSE_OVERRIDE | 0x8872C | **8** (Gen3; Gen2 used 6) |

### CRITICAL: MAX_RATE uses a REVERSED encoding

`LINK_CONFIG_0.MAX_LINK_RATE[19:18]` (NVIDIA internal, per ropuls / cmp.wiki):

| Value | Meaning |
|---|---|
| 0 | Gen4 (16 GT/s) |
| 1 | Gen3 (8 GT/s) |
| 2 | Gen2 (5 GT/s) |
| 3 | Gen1 (2.5 GT/s) |

Config-space `LnkCtl2` Target Link Speed uses the NORMAL encoding (1..4).
**Do not interchange the two.** Setting MAX_RATE=3 thinking it meant Gen3
actually commands Gen1 and crashes the link on a Gen3 retrain (this was the
main debugging trap - see below). Gen2 worked with MAX_RATE=2 only because
2=Gen2 in both encodings.

### Part 2 - RM staged link training (userspace)

`setpci` retrain alone does NOT train Gen3 ("repeating setpci alone is not a
solution" - the guide). Training must go through NVIDIA RM control
`NV2080_CTRL_CMD_BUS_SET_PCIE_SPEED` (0x20801805), staged Gen1 -> Gen2 -> Gen3.

- `tools/set_pcie_speed.c` -> compiled to `/usr/local/sbin/cmp-pcie-speed`.
  Args: `<0|1|2|3> <device-minor> <PCI-bus-hex>` (generation, NOT MB/s).
- `tools/cmp-gen3.sh <BDF>` -> single-pass staged training. Idempotent: if
  already Gen3 it validates and exits; otherwise Gen1->Gen2->Gen3, then checks
  LnkSta on both endpoints. No retry loop.

## Implementation files (cmpunlocker-v0.5-oc-80g)

| File | Change |
|---|---|
| driver/patches/pcie-gen3.patch | post-GSP Gen3 block (pure insertion at the unique `if (status != NV_OK)` / "failed to execute Booter Load" anchor in kernel_gsp_tu102.c) |
| driver/build.sh | pcie-gen3.patch in PATCH_ORDER; compiles set_pcie_speed.c -> /usr/local/sbin/cmp-pcie-speed; **normalizes all patches CRLF->LF before applying** |
| common/constants.yaml | pcie_gen3 unlock entry (register manifest) |
| install.sh | writes /etc/modprobe.d/cmp-gen3.conf (merges existing NVreg_RegistryDwords) |
| tools/set_pcie_speed.c | RM SET_PCIE_SPEED tool |
| tools/cmp-gen3.sh | staged Gen1->Gen2->Gen3 training script (accepts 20c2/2082) |
| tools/pcie_bandwidth.py | libcuda H2D/D2H bandwidth test (no CUDA toolkit needed) |
| tools/pcie_phy_probe.py | read-only PHY register dump |
| tools/pcie_phy_enable.py | runtime PHY experimentation (reversed MAX_RATE aware) |

Registry keys (`/etc/modprobe.d/cmp-gen3.conf`):
```
options nvidia NVreg_RegistryDwords="RmForceEnableGen2=1;RMPcieLinkSpeed=0x5;CmpGen3=1"
```
`CmpGen3=1` enables the post-GSP Gen3 block. `CmpGen3=0` -> Gen2 fallback.
`RMPcieLinkSpeed=0x5` is a bitfield allowing Gen3 (not "generation five").

## Build / install / train

```bash
sed -i 's/\r$//' install.sh verify.sh driver/build.sh tools/*.sh
sudo ./install.sh           # builds driver + Gen3 patch, compiles cmp-pcie-speed, writes conf
sudo shutdown -h now        # cold boot

# after boot (link comes up Gen2):
dmesg | grep "Gen3 post-GSP sequence applied"     # expect (CmpGen3=1)
sudo bash tools/cmp-gen3.sh 0000:01:00.0          # staged Gen1->Gen2->Gen3
setpci -s 01:00.0 CAP_EXP+12.w                    # 0x1083 = Gen3 trained
python3 tools/pcie_bandwidth.py                   # ~6.6 GB/s
```

## Reboot behavior / persistence

The link trains **Gen2 at boot** (the Gen2 probe retrain wins); the post-GSP
Gen3 block prepares the Gen3 config but does not force training. The RM staged
step (`cmp-gen3.sh`) brings it to Gen3. So **Gen3 must be re-trained after each
boot**. A boot service (run cmp-gen3.sh once after NVIDIA init, before compute)
is the pending piece to make it automatic - NOT yet added.

## Debugging traps (what went wrong before it worked)

1. **MAX_RATE encoding** - assumed normal (3=Gen3); it is reversed (3=Gen1).
   Gen3 attempts with MAX_RATE=3 crashed the link (fell off the bus). Fixed by
   MAX_RATE=1. Gen2 masked the bug (2=Gen2 both ways).
2. **Blind CYA_0 clearing** - clearing bits 4,5 (wrong candidates) while
   commanding Gen1 destabilized the PHY and dropped the card. The proven
   sequence clears bits 2,3. Do not blind-clear CYA bits.
3. **setpci-only retrain** - never trains Gen3; RM staged training is required.
4. **Patch line endings** - repo patches are CRLF (Windows checkout); a CRLF
   patch adds CRLF lines to the LF source, breaking later LF patches' context.
   build.sh now strips CR from all patches before applying. The Gen3 patch is
   a pure insertion at a unique anchor (no dependency on the Gen2 block tail).
5. **Missing PL_LINK_RATE / VSEC / XVE** - early runtime attempts omitted the
   Gen3 rate field (3<<16), VSEC bit12 set, and XVE=8; the full sequence needs
   all of them.

## Safety / recovery

- Gen3 transitions can drop the GPU off the bus (Xid 79 / RM 0x0f). **Cold boot
  (power cycle) recovers**; a single failure does not imply hardware damage.
  Stop and keep logs; do NOT retry-loop (the wiki records a card whose PCIe
  controller was damaged by repeated Gen3 transitions).
- `cmp-gen3.sh` is single-pass and exits on any failed RM call.
- Runtime rollback to Gen2: `sudo /usr/local/sbin/cmp-pcie-speed 2 <minor> <bus>`.
- Persistent rollback: set `CmpGen3=0` in cmp-gen3.conf + reboot (Gen2).
- Judge success ONLY by config-space LnkSta (8 GT/s), never LnkCap/LnkCtl2 or
  nvidia-smi "max" (those describe capability/target, not the trained link).

## Width note

The measurements above were taken with the link trained at reduced width
(LnkCap x16, LnkSta downgraded). x16 requires the **PCIe decoupling-cap mod**
(24x 0402 0.22uF) + a direct x16 slot. Gen3 x16 ~ 15.7 GB/s. The cap mod
restores width only, not generation.

## Gen4 (next, not done)

The card is Gen4-ready (Device Max 4, MAGIC_BITS_D[25] burned). To extend:
- post-GSP block: MAX_RATE = **0** (reversed: 0=Gen4); Gen4 PL_LINK_RATE field.
- RM staged training extended to `SET_PCIE_SPEED(4)` (Gen1->2->3->4).
- **Requires a Gen4-capable host** (root port LnkCap 16 GT/s) or a Gen4 PLX
  switch. This host is Gen3 (Host Max 3) - check `lspci -s 00:01.0 -vv | grep
  LnkCap` and BIOS PCIe speed setting. A Gen4 card on a Gen3 host stays Gen3.
- Gen4 needs the cap mod for x16 (without it Gen4 falls back to Gen3 per wiki).
- Gen4 16 GT/s is signal-integrity sensitive: use a direct x16 slot.

## References

- Proven Gen3 guide (10GB): github.com/lixiangwuxian/170hx_tips (Gen3_unlock_en.md)
- Wrapper: github.com/evanrodgers/cmp-170hx-rir-burn-util
- CMP wiki: cmp.wiki/wiki/PCIe_Gen3_on_the_10_GB_card and /wiki/Unlocks
- JRex fuse/register table: gist.github.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- Blog: https://blog.kate.land/posts/using-voltage-glitching-to-unlock-the-a100
- cmpunlocker: github.com/amoghmunikote/cmpunlocker
- Local: cmp_burn.md (fuse burns), cmprir/ga100-fuse-re/ (research)