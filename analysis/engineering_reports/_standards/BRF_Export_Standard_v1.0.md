# BRF Export Standard v1.0

## 1. Scope
This standard governs BRF export behavior in engineering report packs.
It is reporting-layer only and does not authorize runtime semantics changes.

## 2. Template Protection
BRF output must preserve the approved BRF template contract.

1. Keep section structure unchanged.
2. Keep timeline schema unchanged.
3. Do not insert ad-hoc schema fields into BRF timeline rows.
4. Observer metrics may be used only through event outputs.
5. Reuse `Battle_Report_Framework_v1.0.template.md`; do not create ad-hoc BRF layouts when the template already covers the request.

## 3. Tick Semantics

1. `t=0` is initial snapshot only.
2. Event detection and timeline event ticks must use `t>=1`.
3. Any event at `t=0` must be treated as a semantic error.

## 4. Naming and Placement

1. Theme-scoped BRF filename pattern:
   `<topic>_Battle_Report_Framework_v1.0.md`
2. DOE report-pack BRF artifacts:
   `analysis/engineering_reports/developments/<YYYYMMDD>/<topic>/brf_artifacts/`
3. Test-run BRF exports:
   `analysis/exports/battle_reports/<YYYYMMDD>/`

## 5. Narrative Conventions

1. BRF Section 3 uses the governance-approved layout:
   `3.1 Archetypes`, `3.2 ZH Narrative`, `3.3 EN Narrative`.
2. `3.1 Archetypes` is an English-only A/B archetype snapshot with ten-parameter numeric values.
3. Legacy fixed-lead lines remain embedded at the beginning of both narrative bodies:
   battle title, commander line, and initial-force line.
4. When named factions are available in EN, use `<Name> Fleet` and avoid `<Name> side`.
5. When named factions are available, avoid bare `A/B` as EN narrative subject text except for explicit technical counters.
6. If naming info is unavailable, both ZH and EN narratives must fall back to pure side labels `A` and `B`.
7. ZH milestone wording must follow the current governance-approved canonical phrasing; do not invent alternate milestone labels in BRF generation.

## 6. Snapshot Requirements
Run Configuration Snapshot in BRF should include effective run-control and runtime-source fields.
At minimum:

1. `max_time_steps_effective`
2. `test_mode`
3. `runtime_decision_source_effective`
4. `movement_model_effective` (when movement model switch exists)
5. `random_seed_effective`
6. `background_map_seed_effective`
7. `metatype_random_seed_effective` (when metatype generation is active)

## 7. Collapse Analysis Semantics

1. BRF Section 5 refers to `collapse_v2_shadow`, not runtime collapse decisions.
2. `Collapse shadow occurred before contact` means:
   earliest side-level `first_tick_collapse_v2_shadow < first_contact_tick`.
3. This field is observer-only diagnostic wording and must not be interpreted as:
   runtime collapse trigger, pursuit-mode switch, or behavior-path change.

## 8. Metatype Semantics

1. `yang` in runtime/test-run usage is an exploration commander / sampler.
2. `yang` is not a canonical fixed archetype definition.
3. `yang` parameters are generated from `archetypes/metatype_settings.json`
   using configured source archetypes, jitter, clamp, and `metatype_random_seed_effective`.
4. Generated `yang` values must never overwrite canonical archetype definitions.

## 9. Compliance Note
DOE summary should include a standards compliance block that cites:

1. Standard version(s) used.
2. Postprocess script version used.
3. Deviations (or "No deviations").
