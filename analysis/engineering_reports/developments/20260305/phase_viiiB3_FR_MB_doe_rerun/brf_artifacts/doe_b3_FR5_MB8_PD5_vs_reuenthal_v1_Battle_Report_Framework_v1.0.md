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
- max_time_steps_effective: `412`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=doe_b3_FR5_MB8_PD5 vs B=reuenthal, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-05

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 111 |
| First Kill | 120 |
| Formation Cut | 138 |
| Pocket Formation | 184 |
| Pursuit Mode | N/A |
| Inflection | 113 |
| Endgame Onset | 306 |
| End | 412 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | doe_b3_FR5_MB8_PD5 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | reuenthal | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 2.0 | 5.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
DOE B3 Test Persona FR5 MB8 PD5(A) vs 奥斯卡·冯·罗严塔尔(B)
B3-FR5-MB8-PD5舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

双方在标准时01:51 (t=111) 开始交火。 战线在首批建制伤亡前，于标准时01:53 (t=113) 出现优势拐点，罗严塔尔舰队逐步掌握主动。 双方在标准时02:00 (t=120) 出现成建制伤亡。 标准时05:06 (t=306) 后，战局进入终盘压制。 至标准时06:52 (t=412)，B3-FR5-MB8-PD5舰队全灭，罗严塔尔舰队残余3261艘 (B units=35)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
DOE B3 Test Persona FR5 MB8 PD5(A) vs Oskar von Reuenthal(B)
B3-FR5-MB8-PD5 Fleet: 10000 ships (A: 100 units); Reuenthal Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:51 (t=111). Before the first organized losses, an advantage inflection appeared at ST 01:53 (t=113), and Reuenthal Fleet gradually took initiative. Organized losses appeared at ST 02:00 (t=120). After ST 05:06 (t=306), the battle entered endgame suppression. By ST 06:52 (t=412), B3-FR5-MB8-PD5 Fleet was eliminated, and Reuenthal Fleet retained 3261 ships (B units=35).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
