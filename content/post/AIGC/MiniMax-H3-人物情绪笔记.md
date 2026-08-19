---
title: 'MiniMax-H3-人物情绪笔记'
categories: ["AIGC"]
date: 2026-08-19T13:46:18+08:00
lastmod: 2026-08-19T13:46:18+08:00
draft: false
---
# MiniMax H3 人物情绪笔记

> 来源：飞书文档《纯本地 MiniMax H3 神了！1080P 10 种情绪控制实测｜同一首帧同一句台词》
> 日期：2026-08-19
> 链接：[飞书 Wiki](https://c1bxgy7h3sw.feishu.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
> 提取范围：原文档第六点「逐条生成详情与提示词」（01–06 六种情绪）

---

## 一、实验设置速览

- **核心思路**：同一首帧（`z-image-turbo_00033.png`，汉服女子庭院图）+ 同一句台词（"我恨你，你走吧。"），只改变情绪，验证 H3 的情绪控制能力。
- **生成方式**：本地 ComfyUI + MiniMax H3 I2V（首帧图生视频），工作流 `video_minimax_h3_i2v`。
- **统一参数**：1920×1088，采样 20 步（res_multistep / simple），请求 6 秒 → 实际 6.583 秒（158 帧 @ 24fps，H3 帧数须满足 17k+5）。
- **音频策略**：无背景音乐（`non_diegetic_music: N/A`），只保留台词、呼吸、动作声、自然环境声。
- **单条耗时**：RTX 5070 Ti 本地约 59 分钟/条，6 条全部成功。

| 编号 | 情绪 | 种子 | 耗时 |
|------|------|------|------|
| 01 | 嗔怒娇嗔 | 2650002 | 59:57 |
| 02 | 隐忍怒意 | 2650003 | 59:05 |
| 03 | 雷霆暴怒 | 2650004 | 58:42 |
| 04 | 憋屈闷气 | 2650005 | 59:07 |
| 05 | 委屈巴巴 | 2650006 | 58:46 |
| 06 | 无声落泪 | 2650007 | 59:02 |

---

## 二、情绪提示词通用骨架（七段式）

从 6 条中文提示词提炼出的固定结构，换情绪时只需改【故事与角色】【声线与台词】【正文】三段：

```text
【故事与角色】  参考图锁定身份（五官/发型/服装/背景/构图）+ 情绪动机一句话
【机位与构图】  6秒，16:9，单场景单镜头，中近景，固定机位，延续原图光线与浅景深
【镜头描述】    镜头不推拉摇移，焦点锁定双眼和嘴部，口型清晰
【声线与台词】  声线质感 + 台词逐句的语气/停顿/音量/尾音处理
【正文】        0—1秒 / 1—3秒 / 3—5秒 / 5—6秒 逐段写表演动作，台词插在时间点里
【声音设计】    环境底噪 + 关键动作声，明确"全程不用背景音乐"
【禁止项】      负面清单：表情过头、身份漂移、手指畸形、口型错位、运镜切镜、字幕水印等
```

### H3 实际提交格式（结构化英文）

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and composition from <Picture 1>: ...
（先锁身份，再按 At 0.00–1.00 / 1.00–3.00 / 3.00–5.00 / 5.00–6.00 时间码写表演，
台词用 <d>中文台词</d> 包裹，结尾统一声明单镜头 + 保持身份 + 禁止项）

overall_soundscape: （环境声 + 动作声 + 同步台词）
non_diegetic_music: N/A
```

**关键写法**：
- 台词用 `<d>...</d>` 标记，H3 会做中文口型同步
- 情绪主要靠三处差异化：**眼睛/眉毛的微动作、手部动作、声音质感**
- 每条都锁死"身份、五官、发型、服装、背景不变"，防止漂移

---

## 三、六种情绪逐条笔记

### 01 嗔怒娇嗔（Playful pout）

**情绪本质**：假装生气赶人，实际期待对方留下。表演性愤怒，不是真怒。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的五官、黑色古典发髻、浅色发饰、米白与青绿色刺绣汉服、庭院背景和人物居中位置完全一致。她面对镜头假装生气，嘴上赶人，实际仍期待对方留下。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位。保持原图景别、视角、柔和自然光和浅景深。
>
> 【镜头描述】镜头不移动，焦点始终锁定双眼和嘴部，口型清晰，动作轻巧自然。
>
> 【声线与台词】年轻女性声线，俏皮娇嗔、略带鼻音，清晰说："我恨你，你走吧。""我恨你"假装凶一点，逗号处短停，"你走吧"放轻，尾音微微上扬；中文口型精准同步。
>
> 【正文】0—1秒，她先轻轻瞪向镜头，眉头故意皱起，双唇抿住笑意，肩膀仍然放松。1—3秒，她略微前倾，用俏皮的重音说"我恨你"，下巴轻顿一下，单侧嘴角却短暂扬起。3—5秒，她把头转向一侧，抬手做一次很小的赶人动作，同时从眼角偷看镜头，放轻声音说"你走吧"。5—6秒，她的手停在半空又慢慢收回，身体没有离开，嘴角浮出压不住的浅笑，最后定格在仍偷看镜头的姿态。
>
> 【声音设计】安静庭院底噪、轻微衣料摩擦和一声很轻的鼻腔哼气；全程不使用任何背景音乐，只保留台词、呼吸、动作声与自然环境声。
>
> 【禁止项】真正仇恨、怒吼、哭泣、夸张嘟嘴、连续挥手、身份与五官漂移、发型服装发饰变化、手指畸形、背景变化、口型错位、多余人物、运镜、切镜、字幕、文字、水印、Logo、UI、黑屏、转场、平台尾页。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, she gives the camera a light pretend glare, knitting her brows while suppressing a smile and keeping relaxed shoulders. At 1.00–3.00, she leans forward slightly and says in a young playful, faintly nasal voice: <d>我恨你</d>; she makes a tiny chin dip and one corner of her mouth briefly lifts. At 3.00–5.00, she turns her head slightly aside, makes one very small shooing gesture, steals a glance back at the camera, and softly says <d>你走吧</d> with a gently rising ending. At 5.00–6.00, her raised hand pauses then slowly returns as an irrepressible small smile appears. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Quiet courtyard room tone, a tiny nasal huff, soft fabric rustle, natural breathing, and precise synchronized dialogue.

non_diegetic_music: N/A
```

**要点提炼**：
- 破绽设计是灵魂：抿笑意、单侧嘴角扬起、偷看镜头、手停在半空收回——每个"假生气"动作都留一个"真想留人"的破绽
- 禁止项针对性排除"真正仇恨、怒吼、哭泣"，防止表演性情绪被理解成真情绪

---

### 02 隐忍怒意（Restrained anger）

**情绪本质**：真怒但死死压住。能量全部藏在僵直的身体和收紧的手指里，外放动作极少。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的五官、古典发髻与发饰、刺绣汉服、庭院背景和构图一致。她努力压住愤怒，决定让镜头前的人离开，情绪集中在目光、下颌和克制呼吸中。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位，严格延续原图柔和光线和浅景深。
>
> 【镜头描述】镜头稳定，焦点锁定眼睛和嘴部，不推拉、不摇移。
>
> 【声线与台词】声音低、慢、发紧，压着怒意说："我恨你，你走吧。"每个字清楚有力度；逗号处吞咽并停顿半拍，"你走吧"音量更低。中文口型精准同步。
>
> 【正文】0—1秒，她一动不动地盯住镜头，眉头向内压低，双唇逐渐抿紧，肩膀和颈部保持僵直。1—3秒，她松开唇线，用低而发紧的声音说"我恨你"，下颌越绷越硬，垂在身侧的手指缓慢收紧。3—5秒，她艰难吞咽一次，视线仍不躲闪，以更低的声音说"你走吧"，呼气短而受控。5—6秒，她说完后保持静止，手指仍紧握，目光牢牢钉在镜头上，最后定格在压住爆发的冷硬姿态。
>
> 【声音设计】庭院轻微风声、一次清楚吞咽和短促鼻息；全程不使用任何背景音乐，只保留台词、呼吸、动作声与自然环境声。
>
> 【禁止项】大喊、拍打、前冲、流泪、微笑、夸张怒目、身份与五官漂移、服装发型发饰变化、手指畸形、肢体穿模、背景跳变、口型错位、多余人物、运镜、切镜、字幕、水印、Logo、UI、黑屏、转场、平台尾页。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, she stares into the camera without moving, brows drawn inward, lips progressively pressed tight, neck and shoulders rigid. At 1.00–3.00, she releases her lips and says <d>我恨你</d> slowly in a low tense controlled voice; her jaw hardens and the fingers at her side gradually clench. At 3.00–5.00, she swallows once without breaking eye contact, then says <d>你走吧</d> at lower volume with a short controlled exhale. At 5.00–6.00, she remains still, hand clenched and gaze coldly fixed on the viewer. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Faint courtyard breeze, one clear swallow, brief nasal breathing, subtle fabric movement, and synchronized Chinese dialogue.

non_diegetic_music: N/A
```

**要点提炼**：
- 与 01 的关键区别：动作做减法（"一动不动""僵直""保持静止"），情绪全部内化到眉头、下颌、手指三个"压力表"
- 结尾定格："压住爆发的冷硬姿态"——压抑型情绪收尾不给释放

---

### 03 雷霆暴怒（Thunderous rage）

**情绪本质**：压抑被冲破的爆发。全场唯一一条"喊"的视频，动作幅度最大但要克制次数。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的身份、五官、发髻、发饰、刺绣汉服、庭院和构图稳定。她先咬牙压住怒火，随后被情绪冲破防线，用一句话把镜头前的人赶走。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位。人物始终位于原图中央，不离开画面。
>
> 【镜头描述】镜头保持稳定，以眼睛和嘴部为焦点；快速前倾产生轻微自然运动模糊，但画面不晃动。
>
> 【声线与台词】声音由压抑迅速升级为愤怒，清楚喊出："我恨你！你走吧！""我恨你"重而短促，中间急吸一口气，"你走吧"更响但仍可辨识；中文口型精准同步。
>
> 【正文】0—1秒，她咬紧牙关盯住镜头，眉头压低，肩膀逐渐绷高，胸口吸入一口压抑的气。1—3秒，她的头和上半身突然向前压近，张口怒声说"我恨你"，一只手在身侧猛地攥紧，衣袖随动作轻晃。3—5秒，她急促补气，下巴向前顿一下，用更强的力度喊"你走吧"，抬手明确指向镜头外侧，只完成一次大动作。5—6秒，她的手停住后缓慢落下，身体仍前倾，胸腔粗重起伏，目光没有移开，最后定格在怒意未消的姿态。
>
> 【声音设计】庭院风声、一次急促吸气、衣袖快速摩擦声；全程不使用任何背景音乐，只保留台词、呼吸、动作声与自然环境声，确保台词清晰突出。
>
> 【禁止项】连续乱挥、反复前冲、破坏物件、滑稽表情、五官过度扭曲、身份漂移、服装发饰变化、手指畸形、背景变化、口型错位、多余人物、镜头晃动、切镜、字幕、水印、Logo、UI、黑屏、转场、平台尾页。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, she grits her teeth at the camera, brows low and shoulders rising as she takes one restrained breath. At 1.00–3.00, her head and upper body suddenly thrust a little forward and she sharply says <d>我恨你</d>; one hand clenches hard at her side and the sleeve sways once. At 3.00–5.00, after one quick inhalation, she gives a single firm pointing gesture off to one side and forcefully says <d>你走吧</d>. At 5.00–6.00, the hand slowly lowers while she remains slightly forward, breathing heavily and maintaining an angry gaze. Her face stays recognizable and natural, never grotesque. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Courtyard wind, a quick inhalation, one sharp sleeve rustle, heavy controlled breathing, and clear synchronized Chinese dialogue.

non_diegetic_music: N/A
```

**要点提炼**：
- 爆发型情绪要**限次**："只完成一次大动作""猛地攥紧一次"，防止模型生成连续乱挥的失控画面
- 英文 prompt 多了一句独有保险："Her face stays recognizable and natural, never grotesque"（防暴怒导致五官扭曲）
- 动作升级链：咬牙 → 前倾怒喝 → 指向镜头外侧 → 怒意未消定格，能量单调递增

---

### 04 憋屈闷气（Stifled hurt）

**情绪本质**：受伤害却无法争辩，愤怒向内收缩。视线反复躲闪 + 手抓衣袖是标志性动作。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的五官、古典发髻、浅色发饰、刺绣汉服、庭院背景和原构图一致。她受到伤害却无法争辩，愤怒向内收缩，带着憋屈把镜头前的人推开。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位，延续原图光线与浅景深。
>
> 【镜头描述】焦点锁定眼睛和嘴部；镜头不移动，让低头、吞咽和手部收紧成为表演重点。
>
> 【声线与台词】音量低、声音发紧，带一点压住的鼻音，说："我恨你，你走吧。"开口前短吸气；"我恨你"像勉强挤出，"你走吧"更轻、更委屈，句尾被呼气截断；中文口型精准同步。
>
> 【正文】0—1秒，她的视线先从镜头压向斜下方，双唇向内抿紧，肩膀慢慢内收，手指抓紧衣袖边缘。1—3秒，她极快地抬眼看回镜头，用低而发紧的声音说"我恨你"，眼眶逐渐泛红，手指把衣料揉出褶皱。3—5秒，她再次垂下视线，吞咽后轻声说"你走吧"，下巴出现很小的颤动，呼吸停在喉间半拍。5—6秒，她没有抬头，抓住衣袖的手指仍未松开，眼泪蓄在眼睑边缘但没有落下，最后定格在内缩沉默的姿态。
>
> 【声音设计】安静庭院底噪、衣料被握紧的轻微摩擦声、一次吞咽和短促鼻息；全程不使用任何背景音乐，只保留台词、呼吸、动作声与自然环境声。
>
> 【禁止项】嚎啕大哭、怒吼、挥手赶人、夸张嘟嘴、泪水喷涌、身份与五官漂移、发型服装发饰变化、手指畸形、背景跳变、口型错位、多余人物、运镜、切镜、字幕、水印、Logo、UI、黑屏、转场、平台尾页。
>
> 【提示】与 05 的区别：04 是"说不出话"（内缩沉默），05 是"说反话"（嘴硬想挽留）。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, her gaze drops diagonally downward, lips tuck inward, shoulders slowly close in, and fingers grip the edge of her sleeve. At 1.00–3.00, she quickly looks back up and says <d>我恨你</d> in a low strained voice as her eyes redden slightly and the fabric creases under her tightening fingers. At 3.00–5.00, she lowers her gaze again, swallows, and quietly says <d>你走吧</d>; her chin gives a tiny tremor and breath catches in her throat. At 5.00–6.00, she remains withdrawn, still gripping her sleeve, with tears gathered at the lower eyelid but not falling. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Very quiet courtyard ambience, a sleeve-grip rustle, one swallow, short nasal breath, and restrained synchronized Chinese dialogue.

non_diegetic_music: N/A
```

**要点提炼**：
- 泪水分级第一档："眼泪蓄在眼睑边缘但没有落下"——精确控制泪的量与时机
- 身体语言全部向内：视线下垂、肩膀内收、手指抓衣袖揉出褶皱
- 声音细节："句尾被呼气截断"写出哽咽感

---

### 05 委屈巴巴（Wounded longing）

**情绪本质**：希望被挽留却嘴硬说反话。核心矛盾是"身体想留，嘴巴赶人"。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的五官、古典发髻与发饰、米白青绿刺绣汉服、庭院背景和人物位置一致。她明明希望被挽留，却因受伤而嘴硬地让镜头前的人离开。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位，保持原图自然光与浅景深。
>
> 【镜头描述】焦点始终在双眼与嘴部，镜头稳定，不推拉。表演克制、符合成年女性状态。
>
> 【声线与台词】声音偏低、发软，带轻微鼻音和快要哭出的颤意，说："我恨你，你走吧。"逗号处停顿半拍；"你走吧"像想挽留却说反话，尾音轻轻落下；中文口型精准同步。
>
> 【正文】0—1秒，她从下方抬眼看向镜头，眼眶浮起水光，下巴微微内收，双肩靠近身体。1—3秒，她轻吸一口气，用带鼻音的声音说"我恨你"，下唇轻颤，手指在身前紧紧绞住衣袖。3—5秒，她的视线刚与镜头相碰便滑向一旁，轻声说"你走吧"，身体微微侧转，重心却没有真正撤开。5—6秒，她想再看回镜头，目光却停在半途；嘴唇重新抿住，泪水仍蓄着不落，最后定格在想挽留又不敢开口的姿态。
>
> 【声音设计】庭院微风、轻微衣料摩擦、一次短吸气；全程不使用任何背景音乐，只保留台词、呼吸、动作声与自然环境声。
>
> 【禁止项】幼态卖萌、夸张撅嘴、嚎啕大哭、尖叫、真正离开画面、身份与五官漂移、发型服装发饰变化、手指畸形、背景变化、口型错位、多余人物、运镜、切镜、字幕、水印、Logo、UI、黑屏、转场、平台尾页。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, she looks up from below toward the camera, moisture gathering in her eyes, chin slightly tucked and shoulders close to her body. At 1.00–3.00, with a small inhale and a soft nasal trembling voice, she says <d>我恨你</d> while her lower lip quivers and fingers twist the sleeve in front of her. At 3.00–5.00, her gaze briefly meets the camera then slides away as she softly says <d>你走吧</d>, turning her body a little aside without truly leaving. At 5.00–6.00, she begins to look back but stops halfway; lips press together and tears remain pooled but do not fall. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Soft courtyard breeze, one brief inhale, delicate sleeve friction, quiet breathing, and lip-synchronized Chinese dialogue.

non_diegetic_music: N/A
```

**要点提炼**：
- 矛盾感动作对："身体微微侧转，重心却没有真正撤开""想再看回镜头，目光却停在半途"——每个动作写到一半留一半
- 声线关键词："发软""带鼻音""快要哭出的颤意""尾音轻轻落下"
- 禁止项独有两条："幼态卖萌"和"真正离开画面"（防止 AI 把委屈演成卖萌或人物出走）

---

### 06 无声落泪（Silent tear）

**情绪本质**：平静诀别。眨眼是泪水的"开关"，全场只落一滴泪，克制到极致。

**中文提示词全文**：

> 【故事与角色】以 z-image-turbo_00033.png 为唯一参考图。保持图中女性的五官、黑色古典发髻、发饰、刺绣汉服、庭院空间与构图完全一致。她努力平静地说完诀别的话，眨眼成为泪水滑落的开关。
>
> 【机位与构图】6秒，16:9，单场景单镜头，中近景，固定机位。保持原图柔和自然光、人物居中和浅景深。
>
> 【镜头描述】镜头不动，焦点锁在眼睛和嘴部；泪水沿面颊自然缓慢滑落，不遮挡五官。
>
> 【声线与台词】声音低、轻、克制，带极淡哭腔，说："我恨你，你走吧。"语速偏慢；逗号处呼吸卡住半拍，"你走吧"接近气声，尾音无力；中文口型精准同步。
>
> 【正文】0—1秒，她安静看着镜头，眼神逐渐失焦，下眼睑蓄起一层水光，嘴角无力下坠，肩膀轻轻内收。1—3秒，她重新聚焦一瞬，用低而克制的声音说"我恨你"，嘴唇边缘轻颤，泪水仍停在眼睑边缘。3—5秒，她眨眼时一滴泪沿面颊滑下，同时轻声说"你走吧"，视线慢慢移向斜下方，身体微微下沉。5—6秒，她没有擦泪，嘴唇重新闭合，泪痕继续留在脸上，最后定格在低头安静落泪的姿态。
>
> 【声音设计】安静庭院底噪、一次受控吸气和极轻鼻息；无哭喊，全程不使用任何背景音乐，只保留台词、呼吸与自然环境声。
>
> 【禁止项】泪水瞬间喷涌、多条夸张泪流、嚎啕大哭、擦泪重复动作、怒吼、微笑、身份与五官漂移、发型服装发饰变化、手指畸形、背景跳变、口型错位、多余人物、运镜、切镜、字幕、水印、Logo、UI、黑屏、转场、平台尾页。

**H3 结构化提示词（实际提交）**：

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Preserve the exact identity and centered medium-close 16:9 composition from <Picture 1>: one young East Asian woman facing the camera in a quiet traditional courtyard, with the same oval face, dark classical updo and pale hair ornaments, translucent ivory outer hanfu, pale celadon embroidered dress, peach ribbons, soft natural daylight, blurred grey architecture, shallow depth of field, and stable background. The camera is completely locked off; keep focus on her eyes and mouth. At 0.00–1.00, she looks quietly into the camera, her focus gradually softening as moisture forms under her eyes; the corners of her mouth fall and shoulders draw slightly inward. At 1.00–3.00, she refocuses briefly and says <d>我恨你</d> in a low controlled voice, lips delicately trembling while the tears remain at the eyelid. At 3.00–5.00, she blinks once; exactly one natural tear slowly travels down one cheek as she quietly says <d>你走吧</d> and her gaze lowers diagonally. At 5.00–6.00, she does not wipe the tear, closes her lips, and remains bowed with the tear track visible. Use exactly one continuous shot. Preserve identity, face, hairstyle, ornaments, costume, hands, background, lighting, framing, and accurate Chinese lip synchronization. No camera motion, cuts, subtitles, readable text, watermarks, logos, UI, extra people, background changes, black frames, or transitions.

overall_soundscape: Still courtyard ambience, a controlled inhale, very light nasal breathing, and soft lip-synchronized Chinese dialogue; no sobbing.

non_diegetic_music: N/A
```

**要点提炼**：
- 泪水分级最后一档：`exactly one natural tear slowly travels down one cheek`——数量（一滴）、速度（慢）、路径（单侧面颊）、触发（眨眼）全部指定
- 收尾留痕："泪痕继续留在脸上""不擦泪"，画面有余韵
- 声音几乎静音化："接近气声，尾音无力"，soundscape 明确 "no sobbing"

---

## 四、情绪控制技巧总结

### 1. 怒系三档的区分手段

| 维度 | 01 嗔怒娇嗔 | 02 隐忍怒意 | 03 雷霆暴怒 |
|------|------------|------------|------------|
| 眉眼 | 故意皱眉+偷看 | 眉头向内压低+死盯 | 咬牙+眉头压低 |
| 嘴 | 抿住笑意 | 逐渐抿紧 | 张口怒喝 |
| 手 | 小赶人动作后收回 | 手指缓慢收紧不抬手 | 猛攥+指向镜头外侧一次 |
| 音量 | 俏皮重音→放轻 | 低而发紧→更低 | 重而短促→更响 |
| 结尾 | 浅笑偷看 | 静止冷硬 | 前倾喘息 |
| 破防点 | 装凶露笑 | 不释放 | 释放一次即收 |

### 2. 悲系三档的区分手段

| 维度 | 04 憋屈闷气 | 05 委屈巴巴 | 06 无声落泪 |
|------|------------|------------|------------|
| 视线 | 压向斜下方+快速抬眼 | 抬眼对视即滑开 | 失焦→眨眼后下垂 |
| 手 | 抓衣袖揉出褶皱 | 身前绞衣袖 | 无手部动作 |
| 泪水 | 蓄在眼睑不落 | 水光+蓄泪不落 | 一滴滑落留痕 |
| 声音 | 发紧挤出、句尾被呼气截断 | 发软带颤、尾音轻落 | 接近气声、尾音无力 |
| 心理 | 说不出话 | 说反话想挽留 | 平静诀别 |

### 3. 通用心得

- **情绪 = 时间轴表演，不是形容词堆砌**：每条正文按 4 段时间码（0-1/1-3/3-5/5-6 秒）写具体肌肉和肢体动作，AI 才能演出层次
- **一句话台词三处发力**：拆成"我恨你 / 停顿 / 你走吧"三段，分别指定音量、音色、尾音处理
- **大动作必须限次**：爆发情绪写"只做一次大动作"，防止失控乱挥
- **负面清单针对性定制**：每条禁止项都排除"邻近情绪的过度版本"（如写嗔怒就禁"真怒和哭"，写憋屈就禁"嚎啕大哭"）
- **保持身份是底线**：所有 prompt 开头锁身份（五官/发髻/发饰/服装/背景/构图），结尾再统一声明一次 + 手指畸形、口型错位常驻禁止

---

## 五、复现要点

- 首帧图：`z-image-turbo_00033.png`（z-image-turbo 生成）
- 工作流：ComfyUI `video_minimax_h3_i2v`（MiniMaxH3ImageToVideo 节点）
- 参数：1920×1088 / 20 步 / res_multistep+simple / 158 帧（实际 6.583s）
- 模型：`minimax_h3_fl2va_pruned_int8_convrot` (unet) + `qwen3vl_32b_minimax_h3_nvfp4_awq` (clip) + H3 video/audio VAE
- 种子：2650002–2650007（逐条 +1）
- 输出路径模式：`output/0X_情绪名/0X_00001_.mp4`，记录在同目录 `generation-record.json` / `prompt.txt`
- 硬件参考：i7 U265KF + RTX 5070 Ti + 32GB，单条 6 秒约 59 分钟
