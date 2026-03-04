# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `422`
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
| First Contact | 108 |
| First Kill | 117 |
| Formation Cut | 83 |
| Pocket Formation | 188 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 311 |
| End | 422 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 1.0 | 6.0 | 7.0 | 5.0 | 5.0 |
| B | reuenthal | 6.0 | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | 3.0 | 8.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
GPLKAK 星域会战
齐格飞·吉尔菲艾斯(A) vs 奥斯卡·冯·罗严塔尔(B)
吉尔菲艾斯舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:57 (t=117) 出现成建制伤亡。 标准时05:11 (t=311) 后，战局进入终盘压制。 至标准时07:02 (t=422)，吉尔菲艾斯舰队全灭，罗严塔尔舰队残余2253艘 (B units=24)。

### 3.3 EN Narrative
GPLKAK Starfield Engagement
Siegfried Kircheis(A) vs Oskar von Reuenthal(B)
Kircheis Fleet: 10000 ships (A: 100 units); Reuenthal Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:57 (t=117). After ST 05:11 (t=311), the battle entered endgame suppression. By ST 07:02 (t=422), Kircheis Fleet was eliminated, and Reuenthal Fleet retained 2253 ships (B units=24).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
