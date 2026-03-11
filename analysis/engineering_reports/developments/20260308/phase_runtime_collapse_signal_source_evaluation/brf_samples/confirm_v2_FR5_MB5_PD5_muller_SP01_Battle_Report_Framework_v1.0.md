# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `test_run/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v3a`
- movement_v3a_experiment_effective: `exp_precontact_centroid_probe`
- centroid_probe_scale_effective: `0.5`
- random_seed_effective: `1981813971`
- background_map_seed_effective: `897304369`
- metatype_random_seed_effective: `3095987153`
- display_language: `EN`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `427`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- boundary_soft_strength: `0.1`
- boundary_hard_enabled (requested/effective): `False` / `True`
- alpha_sep: `0.6`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=test_FR5_MB5_PD5 vs B=muller, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-09

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 110 |
| First Kill | 118 |
| Formation Cut | 129 |
| Pocket Formation | 135 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 309 |
| End | 427 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | test_FR5_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | muller | 3.0 | 3.0 | 1.0 | 2.0 | 3.0 | 6.0 | 8.0 | 5.0 | 4.0 | 9.0 |

### 3.2 ZH Narrative
IPNOGU 星域会战
test_FR5_MB5_PD5(A) vs 奈特哈尔·缪拉(B)
test_FR5_MB5_PD5舰队: 10000艘 (A: 100 units); 缪拉舰队: 10000艘 (B: 100 units)

双方在标准时01:50 (t=110) 开始交火。 双方在标准时01:58 (t=118) 出现成建制伤亡。 标准时05:09 (t=309) 后，战局进入终盘压制。 至标准时07:07 (t=427)，缪拉舰队全灭，test_FR5_MB5_PD5舰队残余2269艘 (A units=25)。

### 3.3 EN Narrative
IPNOGU Starfield Engagement
test_FR5_MB5_PD5 Fleet(A) vs Neidhart Müller(B)
test_FR5_MB5_PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:50 (t=110). Organized losses appeared at ST 01:58 (t=118). After ST 05:09 (t=309), the battle entered endgame suppression. By ST 07:07 (t=427), Müller Fleet was eliminated, and test_FR5_MB5_PD5 Fleet retained 2269 ships (A units=25).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): Yes
- Collapse shadow preceded or aligned with pursuit mode: N/A
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): No
