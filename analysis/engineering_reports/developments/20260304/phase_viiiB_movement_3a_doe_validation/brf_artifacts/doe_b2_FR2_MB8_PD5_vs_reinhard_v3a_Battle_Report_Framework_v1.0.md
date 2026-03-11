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
- Grid Parameters: A=T_FR2_MB8_PD5 vs B=reinhard, units_per_side=100
- Determinism Status: Not checked in this single-run export
- Date: 2026-03-04

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | 107 |
| First Kill | 116 |
| Formation Cut | 157 |
| Pocket Formation | 194 |
| Pursuit Mode | N/A |
| Inflection | 112 |
| Endgame Onset | N/A |
| End | 300 |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
| Side | Archetype | force_concentration_ratio | mobility_bias | offense_defense_weight | risk_appetite | time_preference | targeting_logic | formation_rigidity | perception_radius | pursuit_drive | retreat_threshold |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | T_FR2_MB8_PD5 | 2.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| B | reinhard | 9.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 7.0 | 5.0 |

### 3.2 ZH Narrative
MYNBIQ 星域会战
Test Persona FR2 MB8 PD5(A) vs 莱因哈特·冯·罗严克拉姆(B)
T_FR2_MB8_PD5舰队: 10000艘 (A: 100 units); 罗严克拉姆舰队: 10000艘 (B: 100 units)

双方在标准时01:47 (t=107) 开始交火。 战线在首批建制伤亡前，于标准时01:52 (t=112) 出现优势拐点，罗严克拉姆舰队逐步掌握主动。 双方在标准时01:56 (t=116) 出现成建制伤亡。 T_FR2_MB8_PD5舰队与罗严克拉姆舰队在标准时03:53 (t=233) 附近出现一次战术拉扯（Alive优势易手）。 至标准时05:00 (t=300)，T_FR2_MB8_PD5舰队全灭，罗严克拉姆舰队残余2836艘 (B units=30)。

### 3.3 EN Narrative
MYNBIQ Starfield Engagement
Test Persona FR2 MB8 PD5(A) vs Reinhard von Lohengramm(B)
T_FR2_MB8_PD5 Fleet: 10000 ships (A: 100 units); Lohengramm Fleet: 10000 ships (B: 100 units)

The fleets started exchanging fire at ST 01:47 (t=107). Before the first organized losses, an advantage inflection appeared at ST 01:52 (t=112), and Lohengramm Fleet gradually took initiative. Organized losses appeared at ST 01:56 (t=116). T_FR2_MB8_PD5 Fleet and Lohengramm Fleet traded local tactical initiative once near ST 03:53 (t=233) based on alive-unit lead. By ST 05:00 (t=300), T_FR2_MB8_PD5 Fleet was eliminated, and Lohengramm Fleet retained 2836 ships (B units=30).

## 4. Structural Metrics Summary
- Mirror delta: N/A
- Jitter delta: N/A
- Runtime delta: N/A
- Cohesion behavior summary: Runtime path unchanged; this export is observer/report-layer only.

## 5. Collapse Analysis
- Collapse occurred before contact: No
- Collapse preceded or aligned with pursuit mode: N/A
- Collapse aligned with formation cut (|delta_tick|<=1): No
