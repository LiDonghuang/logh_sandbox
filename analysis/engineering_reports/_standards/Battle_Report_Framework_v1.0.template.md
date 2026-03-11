# Battle Report Framework v1.0

## Normative References
- Authoritative policy and export rules are defined in:
  - `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md`
- This file defines BRF section schema and placeholders only.

## 0. Run Configuration Snapshot
- source_settings_path: {{settings_path}}
- attack_range: {{attack_range}}
- min_unit_spacing: {{min_unit_spacing}}
- arena_size: {{arena_size}}
- max_time_steps_effective: {{max_time_steps_effective}}
- unit_speed: {{unit_speed}}
- damage_per_tick: {{damage_per_tick}}
- ch_enabled: {{ch_enabled}}
- contact_hysteresis_h: {{contact_hysteresis_h}}
- fsr_enabled: {{fsr_enabled}}
- fsr_strength: {{fsr_strength}}
- boundary_enabled: {{boundary_enabled}}
- test_mode: {{test_mode}}
- runtime_decision_source_effective: {{runtime_decision_source_effective}}
- collapse_decision_source_effective: {{collapse_decision_source_effective}}
- movement_model_effective: {{movement_model_effective}}
- random_seed_effective: {{random_seed_effective}}
- background_map_seed_effective: {{background_map_seed_effective}}
- metatype_random_seed_effective: {{metatype_random_seed_effective}}
- overrides_applied: {{overrides_applied}}

## 1. Header
- Engine Version: {{engine_version}}
- Grid Parameters: {{grid_parameters}}
- Determinism Status: {{determinism_status}}
- Date: {{report_date}}

## 2. Operational Timeline
| Event | Tick |
| --- | --- |
| First Contact | {{first_contact_tick}} |
| First Kill | {{first_kill_tick}} |
| Formation Cut | {{formation_cut_tick}} |
| Pocket Formation | {{pocket_start_tick}} |
| Pursuit Mode | {{pursuit_mode_onset_tick}} |
| Inflection | {{inflection_tick}} |
| Endgame Onset | {{endgame_onset_tick}} |
| End | {{end_tick}} |

## 3. Tactical Narrative (Auto-generated)
### 3.1 Archetypes
{{archetypes_snapshot_en}}

### 3.2 ZH Narrative
{{tactical_narrative_zh}}

### 3.3 EN Narrative
{{tactical_narrative_en}}

## 4. Structural Metrics Summary
- Mirror delta: {{mirror_delta}}
- Jitter delta: {{jitter_delta}}
- Runtime delta: {{runtime_delta}}
- Cohesion behavior summary: {{cohesion_summary}}

## 5. Collapse Analysis
- Collapse shadow occurred before contact (observer-only, any side): {{collapse_before_contact}}
- Collapse shadow preceded or aligned with pursuit mode: {{collapse_before_pursuit}}
- Collapse shadow aligned with formation cut (|delta_tick|<=1, earliest side): {{collapse_aligned_with_cut}}
