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
- Grid Parameters: A=bittenfeld vs B=grillparzer, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 106 |
| First Kill | 114 |
| Formation Cut | 138 |
| Pocket Formation | 183 |
| Pursuit Mode | N/A |
| Inflection | 123 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | bittenfeld | 2.0 | 5.0 | 9.0 | 8.0 | 7.0 | 3.0 | 7.0 | 4.0 | 5.0 | 6.0 |
| B | grillparzer | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
弗利兹·约瑟夫·毕典菲尔特(A) vs 阿弗雷德·格利鲁帕尔兹(B)
毕典菲尔特舰队: 10000艘 (A: 100 units); 格利鲁帕尔兹舰队: 10000艘 (B: 100 units)

双方在标准时01:46 (t=106) 开始交火。 双方在标准时01:54 (t=114) 出现成建制伤亡。 战线在早段拉扯后，于标准时02:03 (t=123) 出现优势拐点，毕典菲尔特舰队逐步掌握主动。 毕典菲尔特舰队与格利鲁帕尔兹舰队在标准时03:24 (t=204) 附近出现一次战术拉扯（Alive优势易手）。 至标准时05:00 (t=300)，毕典菲尔特舰队全灭，格利鲁帕尔兹舰队残余2980艘 (B units=32)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Fritz Josef Bittenfeld(A) vs Alfred Grillparzer(B)
Bittenfeld Fleet: 10000 ships (A: 100 units); Grillparzer Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:46 (t=106). Organized losses appeared at ST 01:54 (t=114). After early-phase exchanges, an advantage inflection appeared at ST 02:03 (t=123), and Bittenfeld Fleet gradually took initiative. Bittenfeld Fleet and Grillparzer Fleet traded local tactical initiative once near ST 03:24 (t=204) based on alive-unit lead. By ST 05:00 (t=300), Bittenfeld Fleet was eliminated, and Grillparzer Fleet retained 2980 ships (B units=32).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: Yes
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
