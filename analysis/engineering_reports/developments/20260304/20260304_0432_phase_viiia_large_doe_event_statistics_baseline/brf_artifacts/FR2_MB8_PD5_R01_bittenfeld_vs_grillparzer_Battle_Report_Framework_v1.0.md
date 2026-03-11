# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `phase_viiiA_doe_harness_internal`
- display_language: `EN`
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
- Grid Parameters: A=bittenfeld vs B=grillparzer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 116 |
| Formation Cut | 124 |
| Pocket Formation | 181 |
| Pursuit Mode | N/A |
| Inflection | N/A |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | bittenfeld | 2.0 | 8.0 | 9.0 | 8.0 | 7.0 | 3.0 | 7.0 | 4.0 | 5.0 | 6.0 |
| B | grillparzer | 2.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
DXJFOT 星域会战
弗利兹·约瑟夫·毕典菲尔特(A) vs 阿弗雷德·格利鲁帕尔兹(B)
毕典菲尔特舰队: 10000艘 (A: 100 units); 格利鲁帕尔兹舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 双方在标准时01:56 (t=116) 出现成建制伤亡。 至标准时05:00 (t=300)，毕典菲尔特舰队全灭，格利鲁帕尔兹舰队残余2997艘 (B units=34)。

### 3.3 EN Narrative
DXJFOT Starfield Engagement
Fritz Josef Bittenfeld(A) vs Alfred Grillparzer(B)
Bittenfeld Fleet: 10000 ships (A: 100 units); Grillparzer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Organized losses appeared at ST 01:56 (t=116). By ST 05:00 (t=300), Bittenfeld Fleet was eliminated, and Grillparzer Fleet retained 2997 ships (B units=34).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
