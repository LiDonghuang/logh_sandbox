# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v1`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `300`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `False`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=T_FR8_MB2_PD5 vs B=mittermeyer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 116 |
| Formation Cut | 126 |
| Pocket Formation | 171 |
| Pursuit Mode | N/A |
| Inflection | 114 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | T_FR8_MB2_PD5 | 8.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | mittermeyer | 4.0 | 9.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
Test Persona FR8 MB2 PD5(A) vs 沃尔夫冈·米达麦亚(B)
T_FR8_MB2_PD5舰队: 10000艘 (A: 100 units); 米达麦亚舰队: 10000艘 (B: 100 units)

双方在标准时01:47 (t=107) 开始交火。 战线在首批建制伤亡前，于标准时01:54 (t=114) 出现优势拐点，T_FR8_MB2_PD5舰队逐步掌握主动。 双方在标准时01:56 (t=116) 出现成建制伤亡。 T_FR8_MB2_PD5舰队与米达麦亚舰队在标准时04:53 (t=293) 附近出现一次战术拉扯（Alive优势易手）。 至标准时05:00 (t=300)，T_FR8_MB2_PD5舰队全灭，米达麦亚舰队残余2524艘 (B units=29)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Test Persona FR8 MB2 PD5(A) vs Wolfgang Mittermeyer(B)
T_FR8_MB2_PD5 Fleet: 10000 ships (A: 100 units); Mittermeyer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Before the first organized losses, an advantage inflection appeared at ST 01:54 (t=114), and T_FR8_MB2_PD5 Fleet gradually took initiative. Organized losses appeared at ST 01:56 (t=116). T_FR8_MB2_PD5 Fleet and Mittermeyer Fleet traded local tactical initiative once near ST 04:53 (t=293) based on alive-unit lead. By ST 05:00 (t=300), T_FR8_MB2_PD5 Fleet was eliminated, and Mittermeyer Fleet retained 2524 ships (B units=29).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
