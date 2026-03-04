# Battle Report Framework v1.0

## Output Naming Rule
- Runtime output filename must be theme-scoped:
  - `<topic>_Battle_Report_Framework_v1.0.md`
- Do not use generic output filename `Battle_Report_Framework_v1.0.md` for report packs.

## Output Storage Rule
- Report-pack BRF files under `analysis/engineering_reports` must be archived at:
  - `analysis/engineering_reports/developments/YYYYMMDD/<pack>/`
- Test-run BRF exports must be written to:
  - `analysis/exports/battle_reports/YYYYMMDD/`

## A/B Fallback Rule
- If archetype/commander naming info is unavailable, use pure side labels `A` and `B` in both CN and EN narrative sections.
- Commander line fallback: `A vs B`
- Initial force line fallback should use side-labeled fleets (for example `A舰队` / `B舰队`).

## Narrative Style Rule
- If named factions are available, EN narrative should use `<Name> Fleet` (for example `Hawke Fleet`) instead of `<Name> side`.
- If named factions are available, avoid using bare `A/B` as EN narrative subject; keep `A/B` only for explicit technical parenthetical counters when needed.
- Language code contract: Simplified Chinese is `ZH` (not `CH`).
- `CH` may appear only as Contact Hysteresis abbreviation in runtime parameter fields (for example `ch_enabled`).
- ZH canonical event wording:
  - First contact: `????`
  - First kill / first organized loss: `???????`
- Fixed-lead integration rule:
  - Legacy fixed-lead lines are no longer a standalone section.
  - They must be embedded at the beginning of both `3.2 ZH Narrative` and `3.3 EN Narrative`.

## 0. Run Configuration Snapshot
- Source settings path: {{settings_path}}
- attack_range: {{attack_range}}
- min_unit_spacing: {{min_unit_spacing}}
- arena_size: {{arena_size}}
- max_time_steps_effective: {{max_time_steps_effective}}
- unit_speed: {{unit_speed}}
- damage_per_tick: {{damage_per_tick}}
- ch_enabled / contact_hysteresis_h: {{ch_enabled}} / {{contact_hysteresis_h}}
- fsr_enabled / fsr_strength: {{fsr_enabled}} / {{fsr_strength}}
- boundary_enabled: {{boundary_enabled}}
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
- Collapse occurred before contact: {{collapse_before_contact}}
- Collapse preceded or aligned with pursuit mode: {{collapse_before_pursuit}}
- Collapse aligned with formation cut (|delta_tick|<=1): {{collapse_aligned_with_cut}}
