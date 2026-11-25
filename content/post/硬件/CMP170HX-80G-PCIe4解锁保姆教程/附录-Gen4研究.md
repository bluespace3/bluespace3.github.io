---
title: '附录-Gen4研究'
categories: ["硬件"]
date: 2026-11-24T16:32:18+08:00
lastmod: 2026-11-24T16:32:18+08:00
draft: false
---
# CMP 170HX 8GB -> PCIe Gen4: Research Notes

Research synthesis for the Gen4 attempt, built on the working Gen3 x16 unlock
(see `cmp_gen3.md`). Primary source: Consensus-Protocol/cmp170hx technical wiki
(docs/frontier/pcie-gen3-gen4.md, docs/hardware/pcie-subsystem.md,
docs/hardware/vbios.md), cross-checked against JRex's fuse reference table and
the lixiangwuxian Gen3 guide.

NOTE ON DATING: the Consensus-Protocol wiki is current as of 2026-07-31 and
states "no Gen3 or Gen4 link has ever trained." That is OUTDATED for Gen3 --
this card runs Gen3 x16 (13.6 GB/s) via the Oct-2026 lixiangwuxian post-GSP
sequence + RM staged training, with the fuses burned. The wiki's Gen4
"unsolved" is the same kind of snapshot; its register-level analysis below is
still the best available map.

## Current state

| Item | Value |
|---|---|
| Working link | Gen3 x16, 13.6 GB/s (CmpGen3=1 post-GSP + cmp-gen3.sh) |
| Host | Gen4-capable (Host Max 4), direct x16 slot, cap mod done |
| Card | Device Max 4 (Gen4 fuse bit25 burned); LnkCap speed still Gen3 |
| Gen4 blocker | SUPPORTED_LINK_SPEED vector latched at Gen3; Gen4 DevInit block suppressed |

## E1 RESULT (validated on this card): cap lifts, training is firmware-blocked

The E1 probe (tools/pcie_gen4_probe.py) wrote the A100 Gen4 init state from the
Gen3 x16 base. Results:

- **MAX_LINK_SPEED cap LIFTED to Gen4**: LnkCap 0x88084 went 0x00457103 (nibble 3)
  -> 0x00457104 (nibble 4). The Gen4 DevInit registers ARE the cap lever:
  0x88CE4=0x14, 0x88CE0=(old&~0x3F)|0x06, CYA_0=0x060711B2 (A100). All wrote OK.
- LnkCap2 0x880A4 = 0x0180001E already carries the full Gen1-4 vector (bits[7:1]
  = 0xF) -- the supported-speeds vector was NEVER the blocker; the MAX_LINK_SPEED
  nibble was, and the Gen4 init lifted it.
- PL_LINK_RATE gen field[19:16] changed 3->4 (Gen4); bit 20 is hardware-RO (the
  probe's GATED flag was a false alarm on the full-value compare).
- **BUT Gen4 training FAILS**: RM SET_PCIE_SPEED(4) returns **0x56 =
  NV_ERR_NOT_SUPPORTED** ("Call not supported", nvstatuscodes.h:115). Directed
  setpci retrain to Gen4 also stays Gen3. Gen1/2/3 train fine.

CONCLUSION: the Gen4 capability cap can be lifted via the Gen4 DevInit init
registers (0x88CE0/0x88CE4 + A100 CYA_0), but the GSP-RM firmware's speed-change
handler does not support training to Gen4 on this card (NV_ERR_NOT_SUPPORTED).
The RM API defines Gen4 values, but the firmware handler refuses Gen4. This is
the "Gen4 needs a GSP-RM patch" wall, confirmed empirically. Gen4 training is
firmware-blocked, not register-blocked. The only remaining routes are a GSP-RM
firmware patch (encrypted, frontier) or a retimer/PLX that trains Gen4
independently (the wiki's "Gen4 behind a PLX switch" 10GB report).

PRACTICAL CEILING: Gen3 x16 (13.6 GB/s) without a GSP firmware patch.

## E2 RESULT: SYSTEM_MAX_SPEED Booter write WEDGES BOOT (do not retry as-is)

Built a Gen4 patch with a SEC2 Booter write to 0x881C0 (SYSTEM_MAX_SPEED =
0x00040036) in the kernel_gsp.c postbl path + the E1 init in tu102, gated
CmpGen4=1. Result on cold boot:

- dmesg: "Gen4 SYS_MAX_SPEED booter 0x881C0=0x00040036 attempt=0/1 rd=0xbadf5040"
  (poison readback -- HS-read-only, write cannot be verified).
- **FECS_PRI_TIMEOUT** (NV_PPRIV_SYS_PRI_ERROR_CODE_FECS_PRI_TIMEOUT), poison
  reads 0xbadf1020 at 0x40/0x44/0x48/0x4c/0x110094.
- kgspPopulateWprMeta_HAL failed NV_ERR_INSUFFICIENT_RESOURCES (0x1A) @
  kernel_gsp.c:4857; RmInitAdapter failed (0x62:0x1a:2119); GSP RM cannot init.

This is the wiki's documented Gen4-shadow failure mode (H-WRITE: a specific
write disturbs the PCIe block over the link the Booter uses to DMA its
signature; and/or H-COUNT: extra Booter runs exhaust the priv sequencer).
Writing 0x881C0 via the Booter DURING the postbl timing path wedges GSP boot.

RECOVERY: set CmpGen4=0 (disables the write), cold boot -> Gen3 x16 returns.
The card is NOT bricked (runtime PRI error, no fuse burned).

DO NOT retry the 0x881C0 Booter write in the postbl path. Possible (untested,
risky) variants: apply once per module lifetime (CMP_PCIE_ONCE-style), or move
the write after GSP boot completes (but the Booter primitive is postbl-only).
The SYSTEM_MAX_SPEED lever is real but the write timing/path is the blocker.

## E3 RESULT: once-gating still wedges -> H-WRITE confirmed (route CLOSED)

Retried with a static once-flag + single Booter attempt (CMP_PCIE_ONCE-style,
H-COUNT mitigation). Result: ONE write at 5.458s ("SYS_MAX_SPEED booter ONCE
0x881C0=0x00040036 rd=0xbadf5040") still triggered FECS_PRI_TIMEOUT at 5.959s
and RmInitAdapter failed (0x62:0x1a:2119); nvidia-smi: No devices found.

CONCLUSION: H-WRITE confirmed -- the 0x881C0 write ITSELF wedges the PRI bus,
independent of Booter-run count. Once-gating does not help. The SYSTEM_MAX_SPEED
Booter-write route is DEFINITIVELY CLOSED. Do not retry any 0x881C0 Booter write
in the boot path.

## Gen4 final status (register-level avenues exhausted)

- Cap lifts via E1 (0x88CE0/CE4 + A100 CYA_0 -> LnkCap Gen4). VALIDATED.
- RM SET_PCIE_SPEED(4) = NV_ERR_NOT_SUPPORTED (0x56), closed GSP firmware.
  RMPcieLinkSpeed=0x15 (correct Gen4 allow-mask) does not change this.
- SYSTEM_MAX_SPEED (0x881C0) Booter write wedges GSP boot (H-WRITE). CLOSED.
- Config-space Gen4 retrain stays Gen3 (internal clamp not lifted).

Remaining Gen4 routes (both major projects, NOT register tweaks):
1. GSP-RM firmware patch: decrypt GSP (csecret(6), shared GA100 key, known-
   plaintext oracle exists), add the Gen4 training branch + safe SYSTEM_MAX_SPEED
   handling. The fuse-read sites are located (wiki). High effort/risk.
2. Gen4 retimer / PLX switch interposer: terminates the link and trains Gen4
   independently (the wiki's "Gen4 behind a PLX" 10GB report). Hardware project.

DELIVERED RESULT: Gen3 x16, 13.6 GB/s (stable, validated, beyond public wiki).

## Can Gen2/3/4 be done WITHOUT cmpunlocker (more FF writes only)?

Short answer: NO, not by FF writes alone. The PCIe restriction lives in THREE
separate layers, and FF appends only reach one of them:

| Layer | What it controls | Region | FF-appendable? |
|---|---|---|---|
| Option fuses (GEN23_DIS, GEN3_DIS, MAGIC_D) | advertisement / capability (LnkCap) | FF (rows 222-487) | YES (burned: rows 305-307) |
| PHY training config (CYA_0 Gen3 disable, etc.) | actual link training | IFF (rows 487-512) | NO -- different region |
| Gen4 DevInit init block (0x88CE0/CE4, suppress flag) | Gen4 PHY init at boot | VBIOS (MAC-protected) | NO -- signed flash |

- FF appends change the FF-backed OPTION fuses -> the card ADVERTISES Gen3/4
  (done). They do NOT change the IFF-sourced PHY training config or the VBIOS
  Gen4 block, so the link still will not TRAIN Gen3/4 from FF writes alone.
- The CYA_0 "second Gen3 disable" is IFF-sourced (external-fuse-intel-verbatim-
  sep23.md): IFF executes pre-firmware and sets NV_XP_PL_CYA_0. IFF is modified
  via IFF_RECORD pointer skip (0x820050 START) or SW IFF (volatile, needs
  EN_SW_OVERRIDE) -- NOT permanent FF append.
- The Gen2 unlock itself proves the point: it works via runtime CYA_0 /
  LINK_CONFIG_0 / XP3G / PRIV_MISC_1 overrides WITHOUT clearing the fuse shadow
  (OPT_GEN23 write fails). The training config is not fuse-levered.
- The blog's "FF bits cleared -> Gen3/4 train" is (a) actually "cmpunlocker Gen2
  base + FF bits", not FF alone, and (b) UNREPRODUCED (wiki: nobody else has
  reproduced Kate's VFI PCIe result). Our card needed the extra post-GSP
  sequence + RM training even with the FF burns.

The one permanent fuse that might change DevInit behavior is 0x820148 (the
DevInit gate bit that would make DevInit write the A100 MAGIC_D value). It is an
OTP SPARE bit (regular fuse, reads 0, "can never be set from software") -- NOT
FF-backed, so FF append cannot touch it; only RIR (dangerous) might. Untested.

CONCLUSION: native Gen3/4 (stock driver, no cmpunlocker) is not achievable by
more FF writes. It would need IFF modification (volatile/glitch) + the VBIOS
Gen4 block (closed). The glitch session can test MAGIC_D (FF) + IFF skip
(volatile) to probe native Gen4, but a permanent FF-only solution is not
supported by the evidence.

## The three lock layers (from the wiki)

1. **OTP fuses** (the option shadows):
   - FUSE_PCIE_GEN23_DIS 0x82057C, FUSE_PCIE_GEN3_DIS 0x820580 (burned to 0).
   - FUSE_PCIE_MAGIC_D 0x820520 bit25 = GEN4_SPEED_DISABLED (NVIDIA bug 2220334),
     burned to 0. Stock MAGIC_D=0x16680000; A100=0x00200000.
   - These are fuse-sense reflections; the Gen2/Gen3 unlock works by PHY
     overrides, NOT by writing the fuse shadows (they have no write port).
2. **DevInit config table** (signed SPI flash, MAC-protected, NOT flashable):
   - PCIe table at flash 0x420ED; **suppress flag at table+0x0F**: CMP=0x01
     (skips the Gen4 block), A100=0x00 (runs it).
   - Five PCIe bytes differ; all inside the csecret(2) MAC range -> reflash closed.
3. **Latched PHY capability** (the hard one):
   - SUPPORTED_LINK_SPEED 0x8808C [7:1] and MAX_LINK_SPEED 0x88084 [3:0] are
     **PHY reflections with NO write port** (R-EVF / R-XVF). FWSEC-DevInit
     latches them BEFORE the SEC2 Booter runs, so they are fixed before any
     exploit window. Writing 0x88084 does NOT change the speed nibble (confirmed
     on this card: write stuck bit12 only, speed stayed Gen3).
   - The Gen2/Gen3 unlock works by making these reflections REGENERATE higher
     via the PHY override sequence, then training before re-clamp.

## KEY FINDING: the Gen4 DevInit block registers (never touched by our Gen4 attempt)

When the DevInit suppress flag is 0 (A100), the Gen4 programming block writes
these registers (disassembly 0x31B3F-0x31B92). Our Gen4 patch only did the
Gen3-style sequence with MAX_RATE=0 -- it NEVER wrote these Gen4-specific regs:

| Register | A100 value | CMP stock | Role |
|---|---|---|---|
| 0x88CE4 | 0x00000014 | 0x0000003F | Gen4 init config (write-only, one-shot) |
| 0x88CE0 | low6 = 0x06 | low6 = 0x02 | Gen4 init config (write-only, one-shot) |
| 0x8D1A0 | 0x1B1F2327 | 0x1B1F2327 | LTSSM timeout (already identical) |
| 0x8D1A4 | 0x0B0F1317 | 0x0B0F1317 | LTSSM timeout (already identical) |
| 0x88610 | 0x00001001 | 0x00001001 | VSEC_HIERARCHY (already set by Gen3 seq) |

0x88CE0/0x88CE4 sit in the XVE shadow of the "Physical Layer 16.0 GT/s Extended
Capability" (PCIe cap ID 0x0026, shadow base 0x88C1C). These are the actual
Gen4 PHY init values. **Writing 0x88CE4=0x14 and 0x88CE0=(old&~0x3F)|0x06 is the
most promising untried Gen4 lever.**

## A100 reference register values (the Gen4 target state)

From the wiki's forced-generation sweep on a reference A100 80GB + measured diffs:

| Register | A100 (Gen4) | CMP stock | Notes |
|---|---|---|---|
| LINK_CONFIG_0 0x8C040 | 0x80004C00 | 0x800C4C00 | SPEED[19:18]: 0=Gen4, 1=Gen3, 2=Gen2, 3=Gen1 (REVERSED) |
| CYA_0 0x8C2C0 | 0x060711B2 | 0x068731B7 | diff bits: 0,2,13,23 (CMP has 13,23 set; A100 clear) |
| PL_LINK_RATE 0x8C1C0 | 0x00040036 | 0x00140036 | gen field[19:16]: 4=Gen4, 3=Gen3 (0x00340036) |
| LnkCap 0x88084 | 0x00457104 | 0x00456101 | PHY reflection, no write port |
| LnkCap2 0x880A4 | 0x0180001E | 0x00000002 | supported-speeds vector, no write port |
| LnkCtl2 0x880A8 | 0x001F0004 | 0x00000001 | target, clamped by SUPPORTED |
| 0x88CE4 | 0x00000014 | 0x0000003F | Gen4 init (see above) |
| 0x88CE0 | low6=0x06 | low6=0x02 | Gen4 init (see above) |

CYA_0 NOTE: our Gen4 patch cleared bits 2,3,4 -- WRONG candidates. The A100 diff
is bits 0,2,13,23. The Gen4-relevant CYA bits are likely **13 and 23** (CMP set,
A100 clear), not bit 4. Bit 2 = DIS_G2 (Gen2). To match A100: CYA_0 -> 0x060711B2.

Speed-vector encodings: Gen1=0x1, Gen1_2=0x3, Gen1_2_3=0x7, Gen1_2_3_4=0xF.
LnkCap2 stock=0x2 (Gen1 only), Gen2 unlock=0x6 (Gen1_2), Gen3 needs 0xE, Gen4 0xF.

## The MAGIC_D four-bit hypothesis

Our MAGIC_D=0x14680000 (bits 19,21,22,26,28) vs A100 0x00200000 (bit21 only).
Four extra bits {19,22,26,28} -- matches Amogh's "Gen4 needs four fuses." Bit25
(the documented GEN4_SPEED_DISABLED) is already burned. The other four bits are
undecoded in the public sources; clearing them (MAGIC_D -> 0x00200000) is the
A100 target. MAGIC_D is writable only under SW override (glitch window DSOV=0);
on normal boot DSOV=1 gates the write (confirmed: write ignored at DSOV=1).

## Ranked Gen4 experiments (cheapest first)

### E1. Write the Gen4 DevInit config registers at runtime (NEW, highest value)
From the working Gen3 x16 state, post-GSP (PLMs open), write the A100 Gen4 init:
```
0x88CE4 = 0x00000014
0x88CE0 = (old & ~0x3F) | 0x06
0x8C2C0 = 0x060711B2          # CYA_0 -> A100 (clear bits 0,2,13,23)
0x8C1C0 = 0x00040036          # PL_LINK_RATE Gen4
0x8C040 = (old & ~0xC0000)    # MAX_RATE=0 (Gen4)
0x88610 = 0x00001001          # VSEC
```
Then RM staged training to Gen4 (cmp-pcie-speed 4). Check LnkCap2 (0x880A4) --
does the supported-speeds vector regenerate to 0xF? Does LnkSta reach 16GT/s?
This is the untried lever the wiki points at. Volatile, cold-boot recoverable.

### E2. MAGIC_D -> 0x00200000 in the glitch window
Glitch to DSOV=0, sw_override, write MAGIC_D=0x00200000, check LnkCap. Confirms
whether the four MAGIC_D bits are the Gen4 capability fuses. Volatile.

### E3. Read the strap layer from HS context
0x85080 (supported-speed source [23:20]), 0x85084 (allowed-Gen mask), 0x881C0
(PPCI.UNK1C0: [17:16] LNK_CAP_SPEED, [21:20] SYSTEM_MAX_SPEED) read poison
(0xBADF1100/0xbadf5040) from host. Read from SEC2 HS context (the post-GSP
patch can reach 0x8e1b0/0x823800, so these may be reachable). Locates the strap
that sources the supported-speeds vector.

### E4. LnkSta2 equalization probe during forced Gen4
Dump LnkSta2 EQ fields during a Gen4 attempt. If EqualizationPhase1 never
enters, the PHY is refusing Gen4 at the analog layer (fuse-bound). If it enters
and fails, it's signal integrity / config.

## Hard blockers (closed routes, do not retry)

- Reflashing DevInit/VBIOS: csecret(2) MAC, 2^128 forge; RSA signature check.
- Writing 0x88084/0x8808C/0x85080/0x85084 from host: no write port (PHY
  reflections / poison). Confirmed on this card.
- Writing fuse shadows 0x82057C/0x820580 from host/HS/Booter: no write port.
- 0x820148 (DevInit MAGIC_D gate): OTP spare bit, reads 0, never settable.
- A100 VBIOS cross-flash: tested, fails (Gen4 bit does not carry over).
- Board straps / redriver: straps inert; redriver only re-amplifies (endpoint
  still sources fuse-capped TX rate). Only a retimer could forge TS1/TS2 rate.
- Gen4-shadow patch (0007-pcie-gen4-shadow.patch): boot-looped (7-11 Booter
  runs exhaust the priv sequencer / disturb PCIe over the Booter DMA link).
  If retrying, use CMP_PCIE_ONCE=1 + bisection (LTSSM, vector, UNK1C0, PHY).

## Safety

- Gen4 16GT/s transitions can drop the GPU off the bus (Xid 79 / RM 0x0f).
  Cold boot recovers; do NOT retry-loop (wiki records a damaged PCIe controller).
- Judge by LnkSta (16GT/s), never LnkCap/LnkCap2/nvidia-smi Max.
- All runtime writes volatile; cold boot restores the Gen3 baseline.

## References

- Consensus-Protocol/cmp170hx: docs/frontier/pcie-gen3-gen4.md (the Gen4 map),
  docs/hardware/pcie-subsystem.md (register block), docs/hardware/vbios.md (DevInit).
- JRex fuse reference: gist.github.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- lixiangwuxian/170hx_tips Gen3_unlock_en.md (the working Gen3 sequence).
- cmp.wiki/wiki/PCIe_Gen3_on_the_10_GB_card (Gen3 proven on 10GB, Gen4 behind PLX).
- Local: cmp_gen3.md (working Gen3), cmp_burn.md (fuse burns).