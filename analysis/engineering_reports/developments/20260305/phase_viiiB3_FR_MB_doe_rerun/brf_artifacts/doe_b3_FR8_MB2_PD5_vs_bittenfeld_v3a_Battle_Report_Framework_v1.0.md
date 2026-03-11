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
- max_time_steps_effective: `429`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR8_MB2_PD5 vs B=bittenfeld, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 103 |
| First Kill | 112 |
| Formation Cut | 122 |
| Pocket Formation | 191 |
| Pursuit Mode | N/A |
| Inflection | 105 |
| Endgame Onset | 300 |
| End | 429 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR8_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | bittenfeld | 5.0 | 4.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 9.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR8 MB2 PD5(A) vs 弗利兹·约瑟夫·毕典菲尔特(B)
B3-FR8-MB2-PD5舰队: 10000艘 (A: 100 units); 毕典菲尔特舰队: 10000艘 (B: 100 units)

双方在标准时01:43 (t=103) 开始交火。 战线在首批建制伤亡前，于标准时01:45 (t=105) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 双方在标准时01:52 (t=112) 出现成建制伤亡。 标准时05:00 (t=300) 后，战局进入终盘压制。 至标准时07:09 (t=429)，B3-FR8-MB2-PD5舰队全灭，毕典菲尔特舰队残余1703艘 (B units=18)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR8 MB2 PD5(A) vs Fritz Josef Bittenfeld(B)
B3-FR8-MB2-PD5 Fleet: 10000 ships (A: 100 units); Bittenfeld Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:43 (t=103). Before the first organized losses, an advantage inflection appeared at ST 01:45 (t=105), and Bittenfeld Fleet gradually took initiative. Organized losses appeared at ST 01:52 (t=112). After ST 05:00 (t=300), the battle entered endgame suppression. By ST 07:09 (t=429), B3-FR8-MB2-PD5 Fleet was eliminated, and Bittenfeld Fleet retained 1703 ships (B units=18).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
