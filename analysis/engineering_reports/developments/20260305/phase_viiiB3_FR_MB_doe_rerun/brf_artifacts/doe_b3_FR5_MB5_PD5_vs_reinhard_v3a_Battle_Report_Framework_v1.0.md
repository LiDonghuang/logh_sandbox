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
- max_time_steps_effective: `495`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB5_PD5 vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 114 |
| Formation Cut | 124 |
| Pocket Formation | 258 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 319 |
| End | 495 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | reinhard | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 6.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB5 PD5(A) vs 莱因哈特·冯·罗严克拉姆(B)
B3-FR5-MB5-PD5舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 双方在标准时01:54 (t=114) 出现成建制伤亡。 标准时05:19 (t=319) 后，战局进入终盘压制。 至标准时08:15 (t=495)，B3-FR5-MB5-PD5舰队全灭，罗严克拉姆舰队残余968艘 (B units=10)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB5 PD5(A) vs Reinhard von Lohengramm(B)
B3-FR5-MB5-PD5 Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Organized losses appeared at ST 01:54 (t=114). After ST 05:19 (t=319), the battle entered endgame suppression. By ST 08:15 (t=495), B3-FR5-MB5-PD5 Fleet was eliminated, and Lohengramm Fleet retained 968 ships (B units=10).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
