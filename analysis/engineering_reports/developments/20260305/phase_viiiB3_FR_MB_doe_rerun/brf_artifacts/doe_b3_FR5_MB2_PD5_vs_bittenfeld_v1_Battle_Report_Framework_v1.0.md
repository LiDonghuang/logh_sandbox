# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `e:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- test_mode: `1` (observe)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v1`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `575`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB2_PD5 vs B=bittenfeld, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 113 |
| Formation Cut | 351 |
| Pocket Formation | 193 |
| Pursuit Mode | N/A |
| Inflection | 106 |
| Endgame Onset | 338 |
| End | 575 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | bittenfeld | 5.0 | 4.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 9.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB2 PD5(A) vs 弗利兹·约瑟夫·毕典菲尔特(B)
B3-FR5-MB2-PD5舰队: 10000艘 (A: 100 units); 毕典菲尔特舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 战线在首批建制伤亡前，于标准时01:46 (t=106) 出现优势拐点，B3-FR5-MB2-PD5舰队逐步掌握主动。 双方在标准时01:53 (t=113) 出现成建制伤亡。 B3-FR5-MB2-PD5舰队与毕典菲尔特舰队在标准时04:58 (t=298) 附近出现一次战术拉扯（Alive优势易手）。 标准时05:38 (t=338) 后，战局进入终盘压制。 至标准时09:35 (t=575)，B3-FR5-MB2-PD5舰队全灭，毕典菲尔特舰队残余343艘 (B units=4)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB2 PD5(A) vs Fritz Josef Bittenfeld(B)
B3-FR5-MB2-PD5 Fleet: 10000 ships (A: 100 units); Bittenfeld Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Before the first organized losses, an advantage inflection appeared at ST 01:46 (t=106), and B3-FR5-MB2-PD5 Fleet gradually took initiative. Organized losses appeared at ST 01:53 (t=113). B3-FR5-MB2-PD5 Fleet and Bittenfeld Fleet traded local tactical initiative once near ST 04:58 (t=298) based on alive-unit lead. After ST 05:38 (t=338), the battle entered endgame suppression. By ST 09:35 (t=575), B3-FR5-MB2-PD5 Fleet was eliminated, and Bittenfeld Fleet retained 343 ships (B units=4).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
