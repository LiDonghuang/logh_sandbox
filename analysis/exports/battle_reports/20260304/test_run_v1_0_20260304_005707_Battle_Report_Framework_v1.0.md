# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `470`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=bittenfeld vs B=muller, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 100 |
| First Kill | 110 |
| Formation Cut | N/A |
| Pocket Formation | N/A |
| Pursuit Mode | N/A |
| Inflection | 101 |
| Endgame Onset | 317 |
| End | 470 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | bittenfeld | 9.0 | 6.0 | 9.0 | 9.0 | 6.0 | 7.0 | 6.0 | 2.0 | 8.0 | 5.0 |
| B | muller | 6.0 | 1.0 | 1.0 | 2.0 | 2.0 | 6.0 | 9.0 | 4.0 | 2.0 | 2.0 |

### 3.2 ZH Narrative
QXPXMZ 星域会战
弗利兹·约瑟夫·毕典菲尔特(A) vs 奈特哈尔·缪拉(B)
毕典菲尔特舰队: 10000艘 (A: 100 units); 缪拉舰队: 10000艘 (B: 100 units)

双方在标准时01:40 (t=100) 开始交火。 战线在首批建制伤亡前，于标准时01:41 (t=101) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 双方在标准时01:50 (t=110) 出现成建制伤亡。 标准时05:17 (t=317) 后，战局进入终盘压制。 至标准时07:50 (t=470)，缪拉舰队全灭，毕典菲尔特舰队残余1148艘 (A units=12)。

### 3.3 EN Narrative
QXPXMZ Starfield Engagement
Fritz Josef Bittenfeld(A) vs Neidhart Müller(B)
Bittenfeld Fleet: 10000 ships (A: 100 units); Müller Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:40 (t=100). Before the first organized losses, an advantage inflection appeared at ST 01:41 (t=101), and Bittenfeld Fleet gradually took initiative. Organized losses appeared at ST 01:50 (t=110). After ST 05:17 (t=317), the battle entered endgame suppression. By ST 07:50 (t=470), Müller Fleet was eliminated, and Bittenfeld Fleet retained 1148 ships (A units=12).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
