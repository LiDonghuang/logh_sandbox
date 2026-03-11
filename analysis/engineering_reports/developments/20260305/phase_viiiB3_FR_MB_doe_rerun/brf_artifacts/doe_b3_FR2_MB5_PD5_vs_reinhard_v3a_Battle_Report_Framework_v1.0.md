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
- max_time_steps_effective: `450`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR2_MB5_PD5 vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 109 |
| First Kill | 117 |
| Formation Cut | 138 |
| Pocket Formation | 175 |
| Pursuit Mode | N/A |
| Inflection | 237 |
| Endgame Onset | 320 |
| End | 450 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR2_MB5_PD5 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 |
| B | reinhard | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 6.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR2 MB5 PD5(A) vs 莱因哈特·冯·罗严克拉姆(B)
B3-FR2-MB5-PD5舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:49 (t=109) 开始交火。 双方在标准时01:57 (t=117) 出现成建制伤亡。 战线在中段拉扯后，于标准时03:57 (t=237) 出现优势拐点，罗严克拉姆舰队逐步掌握主动。 B3-FR2-MB5-PD5舰队与罗严克拉姆舰队在标准时04:04 (t=244) 附近出现一次战术拉扯（Alive优势易手）。 标准时05:20 (t=320) 后，战局进入终盘压制。 至标准时07:30 (t=450)，B3-FR2-MB5-PD5舰队全灭，罗严克拉姆舰队残余1603艘 (B units=17)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR2 MB5 PD5(A) vs Reinhard von Lohengramm(B)
B3-FR2-MB5-PD5 Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:49 (t=109). Organized losses appeared at ST 01:57 (t=117). After a mid-line tug of war, an advantage inflection appeared at ST 03:57 (t=237), and Lohengramm Fleet gradually took initiative. B3-FR2-MB5-PD5 Fleet and Lohengramm Fleet traded local tactical initiative once near ST 04:04 (t=244) based on alive-unit lead. After ST 05:20 (t=320), the battle entered endgame suppression. By ST 07:30 (t=450), B3-FR2-MB5-PD5 Fleet was eliminated, and Lohengramm Fleet retained 1603 ships (B units=17).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
