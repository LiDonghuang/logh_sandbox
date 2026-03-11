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
- Grid Parameters: A=doe_b3_FR2_MB8_PD5 vs B=kircheis, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 108 |
| First Kill | 116 |
| Formation Cut | 142 |
| Pocket Formation | 141 |
| Pursuit Mode | N/A |
| Inflection | 201 |
| Endgame Onset | 295 |
| End | 425 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR2_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 |
| B | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR2 MB8 PD5(A) vs 齐格飞·吉尔菲艾斯(B)
B3-FR2-MB8-PD5舰队: 10000艘 (A: 100 units); 吉尔菲艾斯舰队: 10000艘 (B: 100 units)

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 战线在中段拉扯后，于标准时03:21 (t=201) 出现优势拐点，吉尔菲艾斯舰队逐步掌握主动。 B3-FR2-MB8-PD5舰队与吉尔菲艾斯舰队在标准时03:22 (t=202) 附近出现一次战术拉扯（Alive优势易手）。 标准时04:55 (t=295) 后，战局进入终盘压制。 至标准时07:05 (t=425)，B3-FR2-MB8-PD5舰队全灭，吉尔菲艾斯舰队残余1496艘 (B units=16)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR2 MB8 PD5(A) vs Siegfried Kircheis(B)
B3-FR2-MB8-PD5 Fleet: 10000 ships (A: 100 units); Kircheis Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:56 (t=116). After a mid-line tug of war, an advantage inflection appeared at ST 03:21 (t=201), and Kircheis Fleet gradually took initiative. B3-FR2-MB8-PD5 Fleet and Kircheis Fleet traded local tactical initiative once near ST 03:22 (t=202) based on alive-unit lead. After ST 04:55 (t=295), the battle entered endgame suppression. By ST 07:05 (t=425), B3-FR2-MB8-PD5 Fleet was eliminated, and Kircheis Fleet retained 1496 ships (B units=16).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
