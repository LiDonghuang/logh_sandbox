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
- max_time_steps_effective: `478`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR8_MB5_PD5 vs B=reuenthal, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 116 |
| Formation Cut | 140 |
| Pocket Formation | 143 |
| Pursuit Mode | N/A |
| Inflection | 236 |
| Endgame Onset | 313 |
| End | 478 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR8_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | reuenthal | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR8 MB5 PD5(A) vs 奥斯卡·冯·罗严塔尔(B)
B3-FR8-MB5-PD5舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

双方在标准时01:47 (t=107) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 战线在中段拉扯后，于标准时03:56 (t=236) 出现优势拐点，B3-FR8-MB5-PD5舰队逐步掌握主动。 B3-FR8-MB5-PD5舰队与罗严塔尔舰队在标准时04:00 (t=240) 附近出现一次战术拉扯（Alive优势易手）。 标准时05:13 (t=313) 后，战局进入终盘压制。 至标准时07:58 (t=478)，罗严塔尔舰队全灭，B3-FR8-MB5-PD5舰队残余895艘 (A units=10)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR8 MB5 PD5(A) vs Oskar von Reuenthal(B)
B3-FR8-MB5-PD5 Fleet: 10000 ships (A: 100 units); Reuenthal Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Organized losses appeared at ST 01:56 (t=116). After a mid-line tug of war, an advantage inflection appeared at ST 03:56 (t=236), and B3-FR8-MB5-PD5 Fleet gradually took initiative. B3-FR8-MB5-PD5 Fleet and Reuenthal Fleet traded local tactical initiative once near ST 04:00 (t=240) based on alive-unit lead. After ST 05:13 (t=313), the battle entered endgame suppression. By ST 07:58 (t=478), Reuenthal Fleet was eliminated, and B3-FR8-MB5-PD5 Fleet retained 895 ships (A units=10).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
