# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v1`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `300`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `False`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=T_FR5_MB8_PD5 vs B=bittenfeld, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 108 |
| First Kill | 117 |
| Formation Cut | 127 |
| Pocket Formation | 180 |
| Pursuit Mode | N/A |
| Inflection | 208 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | T_FR5_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | bittenfeld | 8.0 | 4.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 9.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
Test Persona FR5 MB8 PD5(A) vs 弗利兹·约瑟夫·毕典菲尔特(B)
T_FR5_MB8_PD5舰队: 10000艘 (A: 100 units); 毕典菲尔特舰队: 10000艘 (B: 100 units)

双方在标准时01:48 (t=108) 开始交火。 双方在标准时01:57 (t=117) 出现成建制伤亡。 战线在中段拉扯后，于标准时03:28 (t=208) 出现优势拐点，T_FR5_MB8_PD5舰队逐步掌握主动。 T_FR5_MB8_PD5舰队与毕典菲尔特舰队在标准时03:30 (t=210) 附近出现一次战术拉扯（Alive优势易手）。 至标准时05:00 (t=300)，毕典菲尔特舰队全灭，T_FR5_MB8_PD5舰队残余2600艘 (A units=28)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Test Persona FR5 MB8 PD5(A) vs Fritz Josef Bittenfeld(B)
T_FR5_MB8_PD5 Fleet: 10000 ships (A: 100 units); Bittenfeld Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:48 (t=108). Organized losses appeared at ST 01:57 (t=117). After a mid-line tug of war, an advantage inflection appeared at ST 03:28 (t=208), and T_FR5_MB8_PD5 Fleet gradually took initiative. T_FR5_MB8_PD5 Fleet and Bittenfeld Fleet traded local tactical initiative once near ST 03:30 (t=210) based on alive-unit lead. By ST 05:00 (t=300), Bittenfeld Fleet was eliminated, and T_FR5_MB8_PD5 Fleet retained 2600 ships (A units=28).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
