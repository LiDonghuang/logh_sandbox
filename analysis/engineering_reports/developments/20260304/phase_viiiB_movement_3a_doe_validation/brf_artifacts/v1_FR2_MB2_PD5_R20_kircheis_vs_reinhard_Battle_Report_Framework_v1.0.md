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
- Grid Parameters: A=kircheis vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 105 |
| First Kill | 114 |
| Formation Cut | N/A |
| Pocket Formation | 169 |
| Pursuit Mode | N/A |
| Inflection | 110 |
| Endgame Onset | 295 |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | kircheis | 2.0 | 2.0 | 5.0 | 5.0 | 5.0 | 1.0 | 7.0 | 7.0 | 5.0 | 5.0 |
| B | reinhard | 2.0 | 2.0 | 8.0 | 7.0 | 8.0 | 9.0 | 6.0 | 7.0 | 5.0 | 7.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
齐格飞·吉尔菲艾斯(A) vs 莱因哈特·冯·罗严克拉姆(B)
吉尔菲艾斯舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:45 (t=105) 开始交火。 战线在首批建制伤亡前，于标准时01:50 (t=110) 出现优势拐点，罗严克拉姆舰队逐步掌握主动。 双方在标准时01:54 (t=114) 出现成建制伤亡。 吉尔菲艾斯舰队与罗严克拉姆舰队在标准时03:16 (t=196) 附近出现一次战术拉扯（Alive优势易手）。 标准时04:55 (t=295) 后，战局进入终盘压制。 至标准时05:00 (t=300)，罗严克拉姆舰队全灭，吉尔菲艾斯舰队残余2605艘 (A units=28)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Siegfried Kircheis(A) vs Reinhard von Lohengramm(B)
Kircheis Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:45 (t=105). Before the first organized losses, an advantage inflection appeared at ST 01:50 (t=110), and Lohengramm Fleet gradually took initiative. Organized losses appeared at ST 01:54 (t=114). Kircheis Fleet and Lohengramm Fleet traded local tactical initiative once near ST 03:16 (t=196) based on alive-unit lead. After ST 04:55 (t=295), the battle entered endgame suppression. By ST 05:00 (t=300), Lohengramm Fleet was eliminated, and Kircheis Fleet retained 2605 ships (A units=28).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
