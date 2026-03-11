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
- Grid Parameters: A=knappstein vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 114 |
| Formation Cut | N/A |
| Pocket Formation | 179 |
| Pursuit Mode | N/A |
| Inflection | 108 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | knappstein | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 8.0 | 5.0 | 5.0 | 5.0 |
| B | reinhard | 8.0 | 5.0 | 8.0 | 7.0 | 8.0 | 9.0 | 6.0 | 7.0 | 5.0 | 7.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
布鲁诺·冯·克纳普斯坦(A) vs 莱因哈特·冯·罗严克拉姆(B)
克纳普斯坦舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 战线在首批建制伤亡前，于标准时01:48 (t=108) 出现优势拐点，罗严克拉姆舰队逐步掌握主动。 双方在标准时01:54 (t=114) 出现成建制伤亡。 至标准时05:00 (t=300)，罗严克拉姆舰队全灭，克纳普斯坦舰队残余2490艘 (A units=28)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Bruno von Knappstein(A) vs Reinhard von Lohengramm(B)
Knappstein Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Before the first organized losses, an advantage inflection appeared at ST 01:48 (t=108), and Lohengramm Fleet gradually took initiative. Organized losses appeared at ST 01:54 (t=114). By ST 05:00 (t=300), Lohengramm Fleet was eliminated, and Knappstein Fleet retained 2490 ships (A units=28).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
