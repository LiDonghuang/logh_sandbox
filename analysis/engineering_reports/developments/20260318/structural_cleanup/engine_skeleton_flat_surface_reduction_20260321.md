# Engine Skeleton Flat-Surface Reduction Report

Status: Round 2 delivery  
Scope: `runtime/engine_skeleton.py` only  
Date: 2026-03-21

## Visible Reduction

Compared with `HEAD` before Round 2:

- `EngineTickSkeleton.__init__`: `62 -> 46` lines
- `EngineTickSkeleton.integrate_movement(...)`: `772 -> 748` lines
- `EngineTickSkeleton.resolve_combat(...)`: `462 -> 441` lines
- `runtime/engine_skeleton.py` total: `2720 -> 2679` lines

This round therefore produced real file-level subtraction, not only hot-path redistribution.

## Flat Reads Reduced

Round 2 replaced a large set of hot-path `getattr(...)` pulls with direct active-surface reads from initialized attributes, especially in:

- `integrate_movement(...)`
- `resolve_combat(...)`
- movement diagnostic helpers

Examples of active runtime/debug fields now read directly:

- `alpha_sep`
- `debug_fsr_diag_enabled`
- `debug_diag4_enabled`
- `debug_diag4_rpg_enabled`
- `boundary_soft_strength`
- `BOUNDARY_SOFT_ENABLED`
- `BOUNDARY_HARD_ENABLED`
- `MOVEMENT_MODEL`
- `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`
- `COHESION_DECISION_SOURCE`
- `ODW_POSTURE_BIAS_*`
- `FSR_ENABLED`
- `fsr_strength`
- `fsr_lambda_delta`
- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`

## Surface Tightening

The main flat-surface reduction was:

- top-level internal debug caches moved into `_debug_state`
- active runtime knobs left visible as direct attributes
- maintained debug outputs kept top-level only where maintained caller usage still exists

This creates a clearer three-way split:

- active runtime controls
- active maintained debug outputs
- internal debug-only state

## Remaining Burden Centers

Round 2 did not finish flat-surface cleanup. Remaining burden centers include:

- large local geometry blocks inside `integrate_movement(...)`
- broad per-attacker contact evaluation in `resolve_combat(...)`
- remaining debug-setting reads inside diag-only helper sections
- retained legacy/reference branches:
  - `MOVEMENT_MODEL == "v1"`
  - `COHESION_DECISION_SOURCE == "v1_debug"`

These remain candidates for later rounds, but were not silently removed here.
