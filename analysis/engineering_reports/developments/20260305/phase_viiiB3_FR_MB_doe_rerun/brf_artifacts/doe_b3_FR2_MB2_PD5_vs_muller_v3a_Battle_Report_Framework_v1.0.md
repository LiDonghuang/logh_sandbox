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
- max_time_steps_effective: `393`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR2_MB2_PD5 vs B=muller, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 108 |
| First Kill | 116 |
| Formation Cut | 138 |
| Pocket Formation | 146 |
| Pursuit Mode | N/A |
| Inflection | 172 |
| Endgame Onset | 293 |
| End | 393 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR2_MB2_PD5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 |
| B | muller | 5.0 | 3.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR2 MB2 PD5(A) vs 奈特哈尔·缪拉(B)
B3-FR2-MB2-PD5舰队: 10000艘 (A: 100 units); 缪拉舰队: 10000艘 (B: 100 units)

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 战线在中段拉扯后，于标准时02:52 (t=172) 出现优势拐点，缪拉舰队逐步掌握主动。 B3-FR2-MB2-PD5舰队与缪拉舰队在标准时03:09 (t=189) 附近出现一次战术拉扯（Alive优势易手）。 标准时04:53 (t=293) 后，战局进入终盘压制。 至标准时06:33 (t=393)，B3-FR2-MB2-PD5舰队全灭，缪拉舰队残余2463艘 (B units=26)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR2 MB2 PD5(A) vs Neidhart Müller(B)
B3-FR2-MB2-PD5 Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:56 (t=116). After a mid-line tug of war, an advantage inflection appeared at ST 02:52 (t=172), and Müller Fleet gradually took initiative. B3-FR2-MB2-PD5 Fleet and Müller Fleet traded local tactical initiative once near ST 03:09 (t=189) based on alive-unit lead. After ST 04:53 (t=293), the battle entered endgame suppression. By ST 06:33 (t=393), B3-FR2-MB2-PD5 Fleet was eliminated, and Müller Fleet retained 2463 ships (B units=26).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
