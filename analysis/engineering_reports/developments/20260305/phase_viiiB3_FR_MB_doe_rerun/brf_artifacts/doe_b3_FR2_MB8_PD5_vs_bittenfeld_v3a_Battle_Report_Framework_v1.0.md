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
- max_time_steps_effective: `539`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR2_MB8_PD5 vs B=bittenfeld, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 109 |
| First Kill | 118 |
| Formation Cut | 147 |
| Pocket Formation | 172 |
| Pursuit Mode | N/A |
| Inflection | 184 |
| Endgame Onset | 332 |
| End | 539 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR2_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 |
| B | bittenfeld | 5.0 | 4.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 9.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR2 MB8 PD5(A) vs 弗利兹·约瑟夫·毕典菲尔特(B)
B3-FR2-MB8-PD5舰队: 10000艘 (A: 100 units); 毕典菲尔特舰队: 10000艘 (B: 100 units)

双方在标准时01:49 (t=109) 开始交火。 双方在标准时01:58 (t=118) 出现成建制伤亡。 战线在中段拉扯后，于标准时03:04 (t=184) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 B3-FR2-MB8-PD5舰队与毕典菲尔特舰队在标准时04:36 (t=276) 附近出现一次战术拉扯（Alive优势易手）。 标准时05:32 (t=332) 后，战局进入终盘压制。 至标准时08:59 (t=539)，B3-FR2-MB8-PD5舰队全灭，毕典菲尔特舰队残余462艘 (B units=6)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR2 MB8 PD5(A) vs Fritz Josef Bittenfeld(B)
B3-FR2-MB8-PD5 Fleet: 10000 ships (A: 100 units); Bittenfeld Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:49 (t=109). Organized losses appeared at ST 01:58 (t=118). After a mid-line tug of war, an advantage inflection appeared at ST 03:04 (t=184), and Bittenfeld Fleet gradually took initiative. B3-FR2-MB8-PD5 Fleet and Bittenfeld Fleet traded local tactical initiative once near ST 04:36 (t=276) based on alive-unit lead. After ST 05:32 (t=332), the battle entered endgame suppression. By ST 08:59 (t=539), B3-FR2-MB8-PD5 Fleet was eliminated, and Bittenfeld Fleet retained 462 ships (B units=6).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
