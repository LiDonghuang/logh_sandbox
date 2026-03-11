# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v3a`
- movement_v3a_experiment_effective: `exp_precontact_centroid_probe`
- centroid_probe_scale_effective: `0.5`
- random_seed_effective: `104729`
- background_map_seed_effective: `130363`
- metatype_random_seed_effective: `181081`
- display_language: `EN`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `501`
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
- Grid Parameters: A=test_FR5_MB5_PD8 vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-08

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 111 |
| First Kill | 119 |
| Formation Cut | 167 |
| Pocket Formation | 136 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 354 |
| End | 501 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | test_FR5_MB5_PD8 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 |
| B | reinhard | 9.0 | 5.0 | 8.0 | 7.0 | 8.0 | 9.0 | 6.0 | 7.0 | 7.0 | 7.0 |

### 3.2 ZH Narrative
GTPJJO 星域会战
test_FR5_MB5_PD8(A) vs 莱因哈特·冯·罗严克拉姆(B)
test_FR5_MB5_PD8舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:51 (t=111) 开始交火。 双方在标准时01:59 (t=119) 出现成建制伤亡。 标准时05:54 (t=354) 后，战局进入终盘压制。 至标准时08:21 (t=501)，罗严克拉姆舰队全灭，test_FR5_MB5_PD8舰队残余1166艘 (A units=12)。

### 3.3 EN Narrative
GTPJJO Starfield Engagement
test_FR5_MB5_PD8 Fleet(A) vs Reinhard von Lohengramm(B)
test_FR5_MB5_PD8 Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:51 (t=111). Organized losses appeared at ST 01:59 (t=119). After ST 05:54 (t=354), the battle entered endgame suppression. By ST 08:21 (t=501), Lohengramm Fleet was eliminated, and test_FR5_MB5_PD8 Fleet retained 1166 ships (A units=12).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): Yes
- Collapse shadow preceded or aligned with pursuit mode: N/A
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): No
