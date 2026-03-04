# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `400`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=bittenfeld vs B=reuenthal, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 110 |
| First Kill | 119 |
| Formation Cut | 137 |
| Pocket Formation | 141 |
| Pursuit Mode | N/A |
| Inflection | 112 |
| Endgame Onset | 296 |
| End | 400 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | bittenfeld | 8.0 | 6.0 | 9.0 | 8.0 | 7.0 | 3.0 | 5.0 | 4.0 | 9.0 | 6.0 |
| B | reuenthal | 6.0 | 5.0 | 5.0 | 4.0 | 4.0 | 5.0 | 2.0 | 8.0 | 4.0 | 5.0 |

### 3.2 ZH Narrative
NEVWRI 星域会战
弗利兹·约瑟夫·毕典菲尔特(A) vs 奥斯卡·冯·罗严塔尔(B)
毕典菲尔特舰队: 10000艘 (A: 100 units); 罗严塔尔舰队: 10000艘 (B: 100 units)

双方在标准时01:50 (t=110) 开始交火。 战线在首批建制伤亡前，于标准时01:52 (t=112) 出现优势拐点，罗严塔尔舰队逐步掌握主动。 双方在标准时01:59 (t=119) 出现成建制伤亡。 标准时04:56 (t=296) 后，战局进入终盘压制。 至标准时06:40 (t=400)，毕典菲尔特舰队全灭，罗严塔尔舰队残余3050艘 (B units=33)。

### 3.3 EN Narrative
NEVWRI Starfield Engagement
Fritz Josef Bittenfeld(A) vs Oskar von Reuenthal(B)
Bittenfeld Fleet: 10000 ships (A: 100 units); Reuenthal Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:50 (t=110). Before the first organized losses, an advantage inflection appeared at ST 01:52 (t=112), and Reuenthal Fleet gradually took initiative. Organized losses appeared at ST 01:59 (t=119). After ST 04:56 (t=296), the battle entered endgame suppression. By ST 06:40 (t=400), Bittenfeld Fleet was eliminated, and Reuenthal Fleet retained 3050 ships (B units=33).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
