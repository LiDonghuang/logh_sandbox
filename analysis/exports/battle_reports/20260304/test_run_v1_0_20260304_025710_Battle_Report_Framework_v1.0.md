# Battle Report Framework v1.0

## 0. Run Configuration Snapshot
- Source settings path: `E:/logh_sandbox/analysis/test_run_v1_0.settings.json`
- display_language: `ZH`
- attack_range: `5.0`
- min_unit_spacing: `2.0`
- arena_size: `200.0`
- max_time_steps_effective: `446`
- unit_speed: `1.0`
- damage_per_tick: `1.0`
- ch_enabled / contact_hysteresis_h: `True` / `0.1`
- fsr_enabled / fsr_strength: `True` / `0.1`
- boundary_enabled: `True`
- overrides_applied: none

## 1. Header
- Engine Version: v5.0-alpha5
- Grid Parameters: A=bittenfeld vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 106 |
| First Kill | 115 |
| Formation Cut | 329 |
| Pocket Formation | 189 |
| Pursuit Mode | N/A |
| Inflection | 120 |
| Endgame Onset | 302 |
| End | 446 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | bittenfeld | 8.0 | 6.0 | 9.0 | 8.0 | 7.0 | 3.0 | 7.0 | 4.0 | 9.0 | 6.0 |
| B | reinhard | 9.0 | 5.0 | 8.0 | 7.0 | 8.0 | 9.0 | 6.0 | 7.0 | 7.0 | 7.0 |

### 3.2 ZH Narrative
FLDSSW 星域会战
弗利兹·约瑟夫·毕典菲尔特(A) vs 莱因哈特·冯·罗严克拉姆(B)
毕典菲尔特舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:46 (t=106) 开始交火。 双方在标准时01:55 (t=115) 出现成建制伤亡。 战线在早段拉扯后，于标准时02:00 (t=120) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 标准时05:02 (t=302) 后，战局进入终盘压制。 至标准时07:26 (t=446)，毕典菲尔特舰队全灭，罗严克拉姆舰队残余1636艘 (B units=19)。

### 3.3 EN Narrative
FLDSSW Starfield Engagement
Fritz Josef Bittenfeld(A) vs Reinhard von Lohengramm(B)
Bittenfeld Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:46 (t=106). Organized losses appeared at ST 01:55 (t=115). After early-phase exchanges, an advantage inflection appeared at ST 02:00 (t=120), and Bittenfeld Fleet gradually took initiative. After ST 05:02 (t=302), the battle entered endgame suppression. By ST 07:26 (t=446), Bittenfeld Fleet was eliminated, and Lohengramm Fleet retained 1636 ships (B units=19).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: N/A
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): N/A
