# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v3_test`
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
- max_time_steps_effective: `412`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `False`
- boundary_soft_strength: `1.0`
- boundary_hard_enabled (requested/effective): `False` / `False`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=test_FR8_MB8_PD5 vs B=muller, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-08

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 113 |
| Formation Cut | 124 |
| Pocket Formation | 142 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 300 |
| End | 412 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | test_FR8_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | muller | 3.0 | 3.0 | 1.0 | 2.0 | 3.0 | 6.0 | 8.0 | 5.0 | 4.0 | 9.0 |

### 3.2 ZH Narrative
IPNOGU 星域会战
test_FR8_MB8_PD5(A) vs 奈特哈尔·缪拉(B)
test_FR8_MB8_PD5舰队: 10000艘 (A: 100 units); 缪拉舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 双方在标准时01:53 (t=113) 出现成建制伤亡。 标准时05:00 (t=300) 后，战局进入终盘压制。 至标准时06:52 (t=412)，test_FR8_MB8_PD5舰队全灭，缪拉舰队残余2192艘 (B units=23)。

### 3.3 EN Narrative
IPNOGU Starfield Engagement
test_FR8_MB8_PD5 Fleet(A) vs Neidhart Müller(B)
test_FR8_MB8_PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Organized losses appeared at ST 01:53 (t=113). After ST 05:00 (t=300), the battle entered endgame suppression. By ST 06:52 (t=412), test_FR8_MB8_PD5 Fleet was eliminated, and Müller Fleet retained 2192 ships (B units=23).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): No
- Collapse shadow preceded or aligned with pursuit mode: N/A
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): No
