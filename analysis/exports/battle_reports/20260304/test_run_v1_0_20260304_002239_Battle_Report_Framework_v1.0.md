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
ZBEQMG 星域会战

弗利兹·约瑟夫·毕典菲尔特(A) vs 奥斯卡·冯·罗严塔尔(B)

毕典菲尔特舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

### 3.2 CN Narrative
??????01:44 (t=104) ????? ???????????????01:45 (t=105) ???????毕典菲尔特????????? ??????01:54 (t=114) ???????? ???04:53 (t=293) ??????????? 至标准时06:39 (t=399)，罗严塔尔舰队全灭，毕典菲尔特舰队残余2425艘 (A units=27)。

### 3.3 EN Narrative
The fleets started exchanging fire at ST 01:44 (t=104). Before the first organized losses, an advantage inflection appeared at ST 01:45 (t=105), and Bittenfeld Fleet gradually took initiative. Organized losses appeared at ST 01:54 (t=114). After ST 04:53 (t=293), the battle entered endgame suppression. By ST 06:39 (t=399), Reuenthal Fleet was eliminated, and Bittenfeld Fleet retained 2425 ships (A units=27).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
