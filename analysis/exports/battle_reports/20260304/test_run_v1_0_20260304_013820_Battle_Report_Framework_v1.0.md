# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `392`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=reinhard vs B=kircheis, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 102 |
| First Kill | 112 |
| Formation Cut | N/A |
| Pocket Formation | N/A |
| Pursuit Mode | N/A |
| Inflection | 103 |
| Endgame Onset | 288 |
| End | 392 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | reinhard | 9.0 | 4.0 | 7.0 | 6.0 | 7.0 | 9.0 | 6.0 | 8.0 | 5.0 | 7.0 |
| B | kircheis | 5.0 | 8.0 | 5.0 | 4.0 | 6.0 | 1.0 | 7.0 | 5.0 | 3.0 | 5.0 |

### 3.2 ZH Narrative
JONLOJ 星域会战
莱因哈特·冯·罗严克拉姆(A) vs 齐格飞·吉尔菲艾斯(B)
罗严克拉姆舰队: 10000艘 (A: 100 units); 吉尔菲艾斯舰队: 10000艘 (B: 100 units)

双方在标准时01:42 (t=102) 开始交火。 战线在首批建制伤亡前，于标准时01:43 (t=103) 出现优势拐点，罗严克拉姆舰队逐步掌握主动。 双方在标准时01:52 (t=112) 出现成建制伤亡。 标准时04:48 (t=288) 后，战局进入终盘压制。 至标准时06:32 (t=392)，吉尔菲艾斯舰队全灭，罗严克拉姆舰队残余2426艘 (A units=26)。

### 3.3 EN Narrative
JONLOJ Starfield Engagement
Reinhard von Lohengramm(A) vs Siegfried Kircheis(B)
Lohengramm Fleet: 10000 ships (A: 100 units); Kircheis Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:42 (t=102). Before the first organized losses, an advantage inflection appeared at ST 01:43 (t=103), and Lohengramm Fleet gradually took initiative. Organized losses appeared at ST 01:52 (t=112). After ST 04:48 (t=288), the battle entered endgame suppression. By ST 06:32 (t=392), Kircheis Fleet was eliminated, and Lohengramm Fleet retained 2426 ships (A units=26).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
