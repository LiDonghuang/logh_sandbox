# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `test_run/test_run_v1_0.settings.json`
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
- max_time_steps_effective: `471`
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
| First Contact | 107 |
| First Kill | 115 |
| Formation Cut | 126 |
| Pocket Formation | 206 |
| Pursuit Mode | N/A |
| Inflection | 146 |
| Endgame Onset | 311 |
| End | 471 |

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

双方在标准时01:47 (t=107) 开始交火。 双方在标准时01:55 (t=115) 出现成建制伤亡。 战线在中段拉扯后，于标准时02:26 (t=146) 出现优势拐点，缪拉舰队逐步掌握主动。 test_FR5_MB5_PD5舰队与缪拉舰队在标准时03:00 (t=180) 附近出现一次战术拉扯（Alive优势易手）。 标准时05:11 (t=311) 后，战局进入终盘压制。 至标准时07:51 (t=471)，test_FR5_MB5_PD5舰队全灭，缪拉舰队残余1411艘 (B units=15)。

### 3.3 EN Narrative
IPNOGU Starfield Engagement
test_FR5_MB5_PD5 Fleet(A) vs Neidhart Müller(B)
test_FR5_MB5_PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Organized losses appeared at ST 01:55 (t=115). After a mid-line tug of war, an advantage inflection appeared at ST 02:26 (t=146), and Müller Fleet gradually took initiative. test_FR5_MB5_PD5 Fleet and Müller Fleet traded local tactical initiative once near ST 03:00 (t=180) based on alive-unit lead. After ST 05:11 (t=311), the battle entered endgame suppression. By ST 07:51 (t=471), test_FR5_MB5_PD5 Fleet was eliminated, and Müller Fleet retained 1411 ships (B units=15).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): No
- Collapse shadow preceded or aligned with pursuit mode: N/A
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): No
