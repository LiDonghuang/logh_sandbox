# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `399`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- contact_hysteresis_enabled (legacy key: ch_enabled) / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=bittenfeld vs B=reuenthal, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 104 |
| First Kill | 114 |
| Formation Cut | N/A |
| Pocket Formation | N/A |
| Pursuit Mode | N/A |
| Inflection | 105 |
| Endgame Onset | 293 |
| End | 399 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 CN Fixed Lead
RNWNPB 星域会战

弗利兹·约瑟夫·毕典菲尔特(A) vs 奥斯卡·冯·罗严塔尔(B)

毕典菲尔特舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

### 3.2 CN Narrative
双方在标准时01:44 (t=104) 开始交火，并在标准时01:54 (t=114) 出现成建制伤亡。 战线在首批建制伤亡前，于标准时01:45 (t=105) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 标准时04:53 (t=293) 后，战局进入终盘压制。 至标准时06:39 (t=399)，罗严塔尔舰队全灭，毕典菲尔特舰队残余2425艘 (A units=27)。

### 3.3 EN Narrative
The fleets started exchanging fire at ST 01:44 (t=104), and organized losses appeared at ST 01:54 (t=114). Before the first organized losses, an advantage inflection appeared at ST 01:45 (t=105), and Bittenfeld Fleet gradually took initiative. After ST 04:53 (t=293), the battle entered endgame suppression. By ST 06:39 (t=399), Reuenthal Fleet was eliminated, and Bittenfeld Fleet retained 2425 ships (A units=27).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
