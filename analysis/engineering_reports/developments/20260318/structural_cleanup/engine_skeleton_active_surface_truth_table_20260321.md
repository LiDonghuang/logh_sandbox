# Engine Skeleton Active Surface Truth Table

Status: Phase 0 Preparation  
Date: 2026-03-21  
Scope: `runtime/engine_skeleton.py` current HEAD truth table only

## Scope Note

This table reflects current `HEAD`, not earlier governance prefaces.

Already removed and therefore **not** current blockers:

- `exp_a_reduced_centroid -> exp_precontact_centroid_probe` alias remap
- `PRECONTACT_CENTROID_PROBE_SCALE` fallback

## 1. `__init__`

### Active runtime surface

- `attack_range`
- `damage_per_tick`
- `separation_radius`
- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`
- `FSR_ENABLED`
- `BOUNDARY_SOFT_ENABLED`
- `BOUNDARY_HARD_ENABLED`
- `boundary_soft_strength`
- `alpha_sep`
- `fsr_strength`
- `fsr_lambda_delta`
- `COHESION_DECISION_SOURCE`
- `MOVEMENT_MODEL`
- `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`
- `ODW_POSTURE_BIAS_ENABLED`
- `ODW_POSTURE_BIAS_K`
- `ODW_POSTURE_BIAS_CLIP_DELTA`

### Active debug/reference surface

- `debug_contact_assert`
- `debug_contact_sample_ticks`
- `debug_fsr_diag_enabled`
- `debug_outlier_eta`
- `debug_outlier_persistence_ticks`
- `debug_diag4_enabled`
- `debug_diag4_topk`
- `debug_diag4_contact_window`
- `debug_diag4_return_sector_deg`
- `debug_diag4_neighbor_k`
- `debug_diag4_rpg_enabled`
- `debug_diag4_rpg_window`
- `debug_cohesion_v1_enabled`
- `debug_cohesion_v3_shadow_enabled`
- `debug_diag_timeseries`

### Retired-but-still-present surface

- none clearly retired in `__init__` after the last flattening pass

### Unknown / decision-needed surface

- whether `debug_contact_assert` family is still maintained enough to stay top-level
- whether the full `diag4` family is still a maintained debug/reference surface
- whether the full `RPG diagnostics` family is still a maintained debug/reference surface

## 2. `integrate_movement(...)`

### Active runtime surface

- movement model selection via `MOVEMENT_MODEL`
- v3a experiment selection via `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`
- `COHESION_DECISION_SOURCE`
- `ODW_POSTURE_BIAS_*`
- `BOUNDARY_SOFT_ENABLED`
- `BOUNDARY_HARD_ENABLED`
- `boundary_soft_strength`
- `alpha_sep`
- `FSR_ENABLED`
- `fsr_strength`
- `fsr_lambda_delta`

### Active debug/reference surface

- `debug_fsr_diag_enabled`
- `debug_diag4_enabled`
- `debug_diag4_rpg_enabled`
- `debug_outlier_eta`
- `debug_outlier_persistence_ticks`
- `debug_last_cohesion_v3` / `debug_last_cohesion_v3_components` indirect support path

### Retired-but-still-present surface

- dead/zero-use locals:
  - `major_hat_x`
  - `major_hat_y`
  - `ar_ratio`
  - `ar_forward_ratio`
  - `precontact_gate`
  - `axial_pull_x`
  - `axial_pull_y`

### Unknown / decision-needed surface

- full `MOVEMENT_MODEL == "v1"` branch
- `COHESION_DECISION_SOURCE == "v1_debug"` path
- how much of diag4 bookkeeping still counts as maintained debug/reference rather than legacy residue

## 3. `resolve_combat(...)`

### Active runtime surface

- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`
- attack-range based contact gate
- damage accumulation and HP writeback
- orientation override on stationary in-contact attacker

### Active debug/reference surface

- `debug_last_combat_stats`
- `debug_diag_last_tick`
- `debug_contact_assert`
- `debug_contact_sample_ticks`
- `debug_diag4_contact_window`
- diag4 contact-history augmentation

### Retired-but-still-present surface

- dead accumulator:
  - `attackers_to_target`

### Unknown / decision-needed surface

- whether full contact-history / diag4 combat augmentation still belongs in maintained debug/reference surface
- whether combat assert family still belongs in maintained path

## 4. Internal-only state currently hosted outside active runtime surface

Hosted in `_debug_state`:

- previous cohesion-v1 cache
- diag4 contact history
- boundary force total
- outlier streak state
- diag4 RPG bookkeeping
- FSR debug snapshot

This is the correct direction and should not be re-expanded into top-level fields.
