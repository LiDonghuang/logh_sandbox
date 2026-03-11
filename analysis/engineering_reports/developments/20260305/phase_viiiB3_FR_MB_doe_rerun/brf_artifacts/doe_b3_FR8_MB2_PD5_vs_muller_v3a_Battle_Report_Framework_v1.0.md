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
- max_time_steps_effective: `637`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR8_MB2_PD5 vs B=muller, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 103 |
| First Kill | 113 |
| Formation Cut | 122 |
| Pocket Formation | 179 |
| Pursuit Mode | N/A |
| Inflection | 106 |
| Endgame Onset | 322 |
| End | 637 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR8_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | muller | 5.0 | 3.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR8 MB2 PD5(A) vs 奈特哈尔·缪拉(B)
B3-FR8-MB2-PD5舰队: 10000艘 (A: 100 units); 缪拉舰队: 10000艘 (B: 100 units)

双方在标准时01:43 (t=103) 开始交火。 战线在首批建制伤亡前，于标准时01:46 (t=106) 出现优势拐点，B3-FR8-MB2-PD5舰队逐步掌握主动。 双方在标准时01:53 (t=113) 出现成建制伤亡。 标准时05:22 (t=322) 后，战局进入终盘压制。 B3-FR8-MB2-PD5舰队与缪拉舰队在标准时09:37 (t=577) 附近出现一次战术拉扯（Alive优势易手）。 至标准时10:37 (t=637)，B3-FR8-MB2-PD5舰队全灭，缪拉舰队残余104艘 (B units=2)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR8 MB2 PD5(A) vs Neidhart Müller(B)
B3-FR8-MB2-PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:43 (t=103). Before the first organized losses, an advantage inflection appeared at ST 01:46 (t=106), and B3-FR8-MB2-PD5 Fleet gradually took initiative. Organized losses appeared at ST 01:53 (t=113). After ST 05:22 (t=322), the battle entered endgame suppression. B3-FR8-MB2-PD5 Fleet and Müller Fleet traded local tactical initiative once near ST 09:37 (t=577) based on alive-unit lead. By ST 10:37 (t=637), B3-FR8-MB2-PD5 Fleet was eliminated, and Müller Fleet retained 104 ships (B units=2).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
