# Engine Skeleton Flat Surface Inventory

Status: Phase 0 Preparation  
Date: 2026-03-21  
Scope: `__init__`, `integrate_movement(...)`, `resolve_combat(...)`

## 1. `__init__`

### Active runtime fields

- core combat/contact: `attack_range`, `damage_per_tick`, `separation_radius`, `CH_ENABLED`, `contact_hysteresis_h`, `fire_quality_alpha`
- movement/boundary/FSR: `FSR_ENABLED`, `BOUNDARY_SOFT_ENABLED`, `BOUNDARY_HARD_ENABLED`, `boundary_soft_strength`, `alpha_sep`, `fsr_strength`, `fsr_lambda_delta`
- selection/branch knobs: `COHESION_DECISION_SOURCE`, `MOVEMENT_MODEL`, `MOVEMENT_V3A_EXPERIMENT`, `CENTROID_PROBE_SCALE`, `ODW_POSTURE_BIAS_*`

### Debug-only fields

- contact assert pair
- fsr/outlier knobs
- diag4/RPG knobs
- cohesion shadow/debug knobs
- `debug_diag_timeseries`

### Compatibility baggage

- no direct alias/fallback baggage remains in `__init__`

### Should exit hot path or be decision-reviewed later

- large top-level debug family should be assessed by family, not by individual field
- `__init__` still reads like one flat bag of knobs rather than a clearly staged active/debug/reference surface

## 2. `integrate_movement(...)`

### Active fields/reads that are genuinely needed

- `alpha_sep`
- `BOUNDARY_SOFT_ENABLED`
- `boundary_soft_strength`
- `MOVEMENT_MODEL`
- `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`
- `COHESION_DECISION_SOURCE`
- `ODW_POSTURE_BIAS_*`
- `FSR_ENABLED`
- `fsr_strength`
- `fsr_lambda_delta`

### Debug-only burden

- `debug_fsr_diag_enabled`
- `debug_diag4_enabled`
- `debug_diag4_rpg_enabled`
- outlier/diag4 payload assembly
- `_debug_diag_pending`

### Compatibility / reference burden

- `MOVEMENT_MODEL == "v1"` branch
- `COHESION_DECISION_SOURCE == "v1_debug"` path

### Things that should exit hot path

- dead locals:
  - `major_hat_x`
  - `major_hat_y`
  - `ar_ratio`
  - `ar_forward_ratio`
  - `precontact_gate`
  - `axial_pull_x`
  - `axial_pull_y`
- legacy/reference branches once retirement is approved
- any diag4/RPG family that is later judged non-maintained

## 3. `resolve_combat(...)`

### Active fields/reads that are genuinely needed

- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`
- attack-range geometry
- engaged-state writeback
- damage accumulation
- orientation override

### Debug-only burden

- `debug_last_combat_stats`
- `debug_diag_last_tick`
- combat assert path
- diag4 contact-history augmentation

### Compatibility / reference burden

- no explicit alias/fallback remains here
- the main burden is debug/reference entanglement, not name compatibility

### Things that should exit hot path

- dead accumulator:
  - `attackers_to_target`
- combat assert family if declared non-maintained
- diag4 contact-history augmentation if declared non-maintained

## Summary

The current flat-surface problem is no longer “old alias/fallback everywhere.”

It is now mostly:

- too many top-level knobs in `__init__`
- large debug/reference families still adjacent to maintained hot path
- dead locals and placeholder variables still left inside movement/combat
- legacy/reference branches not yet given a clear retirement decision
