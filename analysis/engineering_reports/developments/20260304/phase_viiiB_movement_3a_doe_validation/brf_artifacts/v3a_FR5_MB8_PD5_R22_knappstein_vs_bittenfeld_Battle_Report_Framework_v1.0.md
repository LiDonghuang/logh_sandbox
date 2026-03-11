# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `analysis/test_run_v1_0.settings.json`
- test_mode: `2` (test)
- runtime_decision_source_effective: `v2`
- collapse_decision_source_effective: `legacy_v2`
- movement_model_effective: `v3a`
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
- Grid Parameters: A=knappstein vs B=bittenfeld, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 114 |
| Formation Cut | N/A |
| Pocket Formation | 198 |
| Pursuit Mode | N/A |
| Inflection | 138 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | knappstein | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | bittenfeld | 5.0 | 8.0 | 9.0 | 8.0 | 7.0 | 3.0 | 7.0 | 4.0 | 5.0 | 6.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
布鲁诺·冯·克纳普斯坦(A) vs 弗利兹·约瑟夫·毕典菲尔特(B)
克纳普斯坦舰队: 10000艘 (A: 100 units); 毕典菲尔特舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 双方在标准时01:54 (t=114) 出现成建制伤亡。 战线在中段拉扯后，于标准时02:18 (t=138) 出现优势拐点，克纳普斯坦舰队逐步掌握主动。 至标准时05:00 (t=300)，克纳普斯坦舰队全灭，毕典菲尔特舰队残余2406艘 (B units=26)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Bruno von Knappstein(A) vs Fritz Josef Bittenfeld(B)
Knappstein Fleet: 10000 ships (A: 100 units); Bittenfeld Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Organized losses appeared at ST 01:54 (t=114). After a mid-line tug of war, an advantage inflection appeared at ST 02:18 (t=138), and Knappstein Fleet gradually took initiative. By ST 05:00 (t=300), Knappstein Fleet was eliminated, and Bittenfeld Fleet retained 2406 ships (B units=26).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
