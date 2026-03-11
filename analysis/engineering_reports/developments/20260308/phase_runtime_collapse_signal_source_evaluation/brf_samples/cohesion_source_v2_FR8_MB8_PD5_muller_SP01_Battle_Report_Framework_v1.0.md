# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
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
- max_time_steps_effective: `435`
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
| First Contact | 108 |
| First Kill | 116 |
| Formation Cut | 127 |
| Pocket Formation | 187 |
| Pursuit Mode | N/A |
| Inflection | 150 |
| Endgame Onset | 310 |
| End | 435 |

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

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 战线在中段拉扯后，于标准时02:30 (t=150) 出现优势拐点，test_FR8_MB8_PD5舰队逐步掌握主动。 标准时05:10 (t=310) 后，战局进入终盘压制。 至标准时07:15 (t=435)，缪拉舰队全灭，test_FR8_MB8_PD5舰队残余1549艘 (A units=16)。

### 3.3 EN Narrative
IPNOGU Starfield Engagement
test_FR8_MB8_PD5 Fleet(A) vs Neidhart Müller(B)
test_FR8_MB8_PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:56 (t=116). After a mid-line tug of war, an advantage inflection appeared at ST 02:30 (t=150), and test_FR8_MB8_PD5 Fleet gradually took initiative. After ST 05:10 (t=310), the battle entered endgame suppression. By ST 07:15 (t=435), Müller Fleet was eliminated, and test_FR8_MB8_PD5 Fleet retained 1549 ships (A units=16).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): Yes
- Collapse shadow preceded or aligned with pursuit mode: N/A
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): No
