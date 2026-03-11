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
- max_time_steps_effective: `532`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB5_PD5 vs B=mittermeyer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 106 |
| First Kill | 115 |
| Formation Cut | 125 |
| Pocket Formation | 202 |
| Pursuit Mode | N/A |
| Inflection | 168 |
| Endgame Onset | 321 |
| End | 532 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | mittermeyer | 5.0 | 9.0 | 5.0 | 5.0 | 5.0 | 5.0 | 4.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB5 PD5(A) vs 沃尔夫冈·米达麦亚(B)
B3-FR5-MB5-PD5舰队: 10000艘 (A: 100 units); 米达麦亚舰队: 10000艘 (B: 100 units)

双方在标准时01:46 (t=106) 开始交火。 双方在标准时01:55 (t=115) 出现成建制伤亡。 战线在中段拉扯后，于标准时02:48 (t=168) 出现优势拐点，米达麦亚舰队逐步掌握主动。 B3-FR5-MB5-PD5舰队与米达麦亚舰队在标准时03:02 (t=182) 到 06:03 (t=363) 间出现4次战术拉扯（Alive优势多次易手）。 标准时05:21 (t=321) 后，战局进入终盘压制。 至标准时08:52 (t=532)，米达麦亚舰队全灭，B3-FR5-MB5-PD5舰队残余498艘 (A units=6)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB5 PD5(A) vs Wolfgang Mittermeyer(B)
B3-FR5-MB5-PD5 Fleet: 10000 ships (A: 100 units); Mittermeyer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:46 (t=106). Organized losses appeared at ST 01:55 (t=115). After a mid-line tug of war, an advantage inflection appeared at ST 02:48 (t=168), and Mittermeyer Fleet gradually took initiative. B3-FR5-MB5-PD5 Fleet and Mittermeyer Fleet traded local tactical initiative 4 times between ST 03:02 (t=182) and ST 06:03 (t=363) based on alive-unit lead. After ST 05:21 (t=321), the battle entered endgame suppression. By ST 08:52 (t=532), Mittermeyer Fleet was eliminated, and B3-FR5-MB5-PD5 Fleet retained 498 ships (A units=6).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
