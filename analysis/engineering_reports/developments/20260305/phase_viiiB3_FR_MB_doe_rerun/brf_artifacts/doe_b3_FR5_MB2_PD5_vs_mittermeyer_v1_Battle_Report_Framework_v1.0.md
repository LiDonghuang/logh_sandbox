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
- max_time_steps_effective: `530`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB2_PD5 vs B=mittermeyer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 108 |
| First Kill | 116 |
| Formation Cut | 127 |
| Pocket Formation | 196 |
| Pursuit Mode | N/A |
| Inflection | 119 |
| Endgame Onset | 328 |
| End | 530 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | mittermeyer | 5.0 | 9.0 | 5.0 | 5.0 | 5.0 | 5.0 | 4.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB2 PD5(A) vs 沃尔夫冈·米达麦亚(B)
B3-FR5-MB2-PD5舰队: 10000艘 (A: 100 units); 米达麦亚舰队: 10000艘 (B: 100 units)

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 战线在早段拉扯后，于标准时01:59 (t=119) 出现优势拐点，B3-FR5-MB2-PD5舰队逐步掌握主动。 标准时05:28 (t=328) 后，战局进入终盘压制。 至标准时08:50 (t=530)，米达麦亚舰队全灭，B3-FR5-MB2-PD5舰队残余555艘 (A units=6)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB2 PD5(A) vs Wolfgang Mittermeyer(B)
B3-FR5-MB2-PD5 Fleet: 10000 ships (A: 100 units); Mittermeyer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:56 (t=116). After early-phase exchanges, an advantage inflection appeared at ST 01:59 (t=119), and B3-FR5-MB2-PD5 Fleet gradually took initiative. After ST 05:28 (t=328), the battle entered endgame suppression. By ST 08:50 (t=530), Mittermeyer Fleet was eliminated, and B3-FR5-MB2-PD5 Fleet retained 555 ships (A units=6).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
