# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `412`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=reuenthal vs B=mittermeyer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 109 |
| First Kill | 118 |
| Formation Cut | N/A |
| Pocket Formation | N/A |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 303 |
| End | 412 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | reuenthal | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 5.0 | 6.0 | 7.0 | 3.0 | 3.0 |
| B | mittermeyer | 4.0 | 9.0 | 7.0 | 4.0 | 9.0 | 4.0 | 2.0 | 5.0 | 6.0 | 5.0 |

### 3.2 ZH Narrative
WFXSZW 星域会战
奥斯卡·冯·罗严塔尔(A) vs 沃尔夫冈·米达麦亚(B)
罗严塔尔舰队: 10000艘 (A: 100 units); 米达麦亚舰队: 10000艘 (B: 100 units)

双方在标准时01:49 (t=109) 开始交火。 双方在标准时01:58 (t=118) 出现成建制伤亡。 标准时05:03 (t=303) 后，战局进入终盘压制。 至标准时06:52 (t=412)，罗严塔尔舰队全灭，米达麦亚舰队残余3291艘 (B units=35)。

### 3.3 EN Narrative
WFXSZW Starfield Engagement
Oskar von Reuenthal(A) vs Wolfgang Mittermeyer(B)
Reuenthal Fleet: 10000 ships (A: 100 units); Mittermeyer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:49 (t=109). Organized losses appeared at ST 01:58 (t=118). After ST 05:03 (t=303), the battle entered endgame suppression. By ST 06:52 (t=412), Reuenthal Fleet was eliminated, and Mittermeyer Fleet retained 3291 ships (B units=35).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
