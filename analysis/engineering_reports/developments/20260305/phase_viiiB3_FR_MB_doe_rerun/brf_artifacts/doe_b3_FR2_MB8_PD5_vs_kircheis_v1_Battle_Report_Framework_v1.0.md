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
- max_time_steps_effective: `448`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR2_MB8_PD5 vs B=kircheis, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 110 |
| First Kill | 119 |
| Formation Cut | 135 |
| Pocket Formation | 183 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | 316 |
| End | 448 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR2_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 |
| B | kircheis | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR2 MB8 PD5(A) vs 齐格飞·吉尔菲艾斯(B)
B3-FR2-MB8-PD5舰队: 10000艘 (A: 100 units); 吉尔菲艾斯舰队: 10000艘 (B: 100 units)

双方在标准时01:50 (t=110) 开始交火。 双方在标准时01:59 (t=119) 出现成建制伤亡。 标准时05:16 (t=316) 后，战局进入终盘压制。 至标准时07:28 (t=448)，吉尔菲艾斯舰队全灭，B3-FR2-MB8-PD5舰队残余1911艘 (A units=20)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR2 MB8 PD5(A) vs Siegfried Kircheis(B)
B3-FR2-MB8-PD5 Fleet: 10000 ships (A: 100 units); Kircheis Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:50 (t=110). Organized losses appeared at ST 01:59 (t=119). After ST 05:16 (t=316), the battle entered endgame suppression. By ST 07:28 (t=448), Kircheis Fleet was eliminated, and B3-FR2-MB8-PD5 Fleet retained 1911 ships (A units=20).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
