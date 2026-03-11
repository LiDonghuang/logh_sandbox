# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `e:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- test_mode: `1` (observe)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v1`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `585`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR8_MB2_PD5 vs B=mittermeyer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 116 |
| Formation Cut | 126 |
| Pocket Formation | 181 |
| Pursuit Mode | N/A |
| Inflection | 313 |
| Endgame Onset | 325 |
| End | 585 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR8_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | mittermeyer | 5.0 | 9.0 | 5.0 | 5.0 | 5.0 | 5.0 | 4.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR8 MB2 PD5(A) vs 沃尔夫冈·米达麦亚(B)
B3-FR8-MB2-PD5舰队: 10000艘 (A: 100 units); 米达麦亚舰队: 10000艘 (B: 100 units)

双方在标准时01:47 (t=107) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 B3-FR8-MB2-PD5舰队与米达麦亚舰队在标准时05:03 (t=303) 到 05:32 (t=332) 间出现2次战术拉扯（Alive优势多次易手）。 战线在中段拉扯后，于标准时05:13 (t=313) 出现优势拐点，B3-FR8-MB2-PD5舰队逐步掌握主动。 标准时05:25 (t=325) 后，战局进入终盘压制。 至标准时09:45 (t=585)，B3-FR8-MB2-PD5舰队全灭，米达麦亚舰队残余241艘 (B units=3)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR8 MB2 PD5(A) vs Wolfgang Mittermeyer(B)
B3-FR8-MB2-PD5 Fleet: 10000 ships (A: 100 units); Mittermeyer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Organized losses appeared at ST 01:56 (t=116). B3-FR8-MB2-PD5 Fleet and Mittermeyer Fleet traded local tactical initiative 2 times between ST 05:03 (t=303) and ST 05:32 (t=332) based on alive-unit lead. After a mid-line tug of war, an advantage inflection appeared at ST 05:13 (t=313), and B3-FR8-MB2-PD5 Fleet gradually took initiative. After ST 05:25 (t=325), the battle entered endgame suppression. By ST 09:45 (t=585), B3-FR8-MB2-PD5 Fleet was eliminated, and Mittermeyer Fleet retained 241 ships (B units=3).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
