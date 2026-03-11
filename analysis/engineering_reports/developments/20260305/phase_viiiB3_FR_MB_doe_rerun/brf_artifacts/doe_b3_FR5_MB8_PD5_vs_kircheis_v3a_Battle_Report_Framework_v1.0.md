# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `e:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v3_test`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v3a`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `425`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB8_PD5 vs B=kircheis, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 104 |
| First Kill | 114 |
| Formation Cut | 123 |
| Pocket Formation | 209 |
| Pursuit Mode | N/A |
| Inflection | 159 |
| Endgame Onset | 300 |
| End | 425 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB8 PD5(A) vs 齐格飞·吉尔菲艾斯(B)
B3-FR5-MB8-PD5舰队: 10000艘 (A: 100 units); 吉尔菲艾斯舰队: 10000艘 (B: 100 units)

双方在标准时01:44 (t=104) 开始交火。 双方在标准时01:54 (t=114) 出现成建制伤亡。 B3-FR5-MB8-PD5舰队与吉尔菲艾斯舰队在标准时02:21 (t=141) 附近出现一次战术拉扯（Alive优势易手）。 战线在中段拉扯后，于标准时02:39 (t=159) 出现优势拐点，吉尔菲艾斯舰队逐步掌握主动。 标准时05:00 (t=300) 后，战局进入终盘压制。 至标准时07:05 (t=425)，B3-FR5-MB8-PD5舰队全灭，吉尔菲艾斯舰队残余1835艘 (B units=20)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB8 PD5(A) vs Siegfried Kircheis(B)
B3-FR5-MB8-PD5 Fleet: 10000 ships (A: 100 units); Kircheis Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:44 (t=104). Organized losses appeared at ST 01:54 (t=114). B3-FR5-MB8-PD5 Fleet and Kircheis Fleet traded local tactical initiative once near ST 02:21 (t=141) based on alive-unit lead. After a mid-line tug of war, an advantage inflection appeared at ST 02:39 (t=159), and Kircheis Fleet gradually took initiative. After ST 05:00 (t=300), the battle entered endgame suppression. By ST 07:05 (t=425), B3-FR5-MB8-PD5 Fleet was eliminated, and Kircheis Fleet retained 1835 ships (B units=20).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
