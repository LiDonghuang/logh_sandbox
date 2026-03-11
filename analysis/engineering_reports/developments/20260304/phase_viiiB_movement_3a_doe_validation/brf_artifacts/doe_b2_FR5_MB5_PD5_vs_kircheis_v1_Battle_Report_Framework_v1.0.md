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
- Grid Parameters: A=T_FR5_MB5_PD5 vs B=kircheis, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 116 |
| Formation Cut | 126 |
| Pocket Formation | 177 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 294 |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | T_FR5_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
Test Persona FR5 MB5 PD5(A) vs 齐格飞·吉尔菲艾斯(B)
T_FR5_MB5_PD5舰队: 10000艘 (A: 100 units); 吉尔菲艾斯舰队: 10000艘 (B: 100 units)

双方在标准时01:47 (t=107) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 标准时04:54 (t=294) 后，战局进入终盘压制。 至标准时05:00 (t=300)，吉尔菲艾斯舰队全灭，T_FR5_MB5_PD5舰队残余3272艘 (A units=35)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Test Persona FR5 MB5 PD5(A) vs Siegfried Kircheis(B)
T_FR5_MB5_PD5 Fleet: 10000 ships (A: 100 units); Kircheis Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Organized losses appeared at ST 01:56 (t=116). After ST 04:54 (t=294), the battle entered endgame suppression. By ST 05:00 (t=300), Kircheis Fleet was eliminated, and T_FR5_MB5_PD5 Fleet retained 3272 ships (A units=35).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
