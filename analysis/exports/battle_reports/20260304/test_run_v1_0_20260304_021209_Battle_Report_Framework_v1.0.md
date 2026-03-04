# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `410`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=kircheis vs B=reuenthal, units_per_side=100
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
| Inflection | N/A |
| Endgame Onset | 290 |
| End | 410 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 1.0 | 6.0 | 7.0 | 5.0 | 5.0 |
| B | reuenthal | 6.0 | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | 7.0 | 8.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
UOJELM 星域会战
齐格飞·吉尔菲艾斯(A) vs 奥斯卡·冯·罗严塔尔(B)
吉尔菲艾斯舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

双方在标准时01:44 (t=104) 开始交火。 双方在标准时01:54 (t=114) 出现成建制伤亡。 标准时04:50 (t=290) 后，战局进入终盘压制。 至标准时06:50 (t=410)，罗严塔尔舰队全灭，吉尔菲艾斯舰队残余2043艘 (A units=22)。

### 3.3 EN Narrative
UOJELM Starfield Engagement
Siegfried Kircheis(A) vs Oskar von Reuenthal(B)
Kircheis Fleet: 10000 ships (A: 100 units); Reuenthal Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:44 (t=104). Organized losses appeared at ST 01:54 (t=114). After ST 04:50 (t=290), the battle entered endgame suppression. By ST 06:50 (t=410), Reuenthal Fleet was eliminated, and Kircheis Fleet retained 2043 ships (A units=22).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
