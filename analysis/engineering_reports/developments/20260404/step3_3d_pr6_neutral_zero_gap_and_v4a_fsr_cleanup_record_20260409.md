# step3_3d_pr6_neutral_zero_gap_and_v4a_fsr_cleanup_record_20260409

## Scope

- active `v4a` movement cleanup
- `test_run` / harness / runtime-facing truth surface only
- no Targeting change
- no old-family retirement beyond the specific `v4a` FSR entry removal

## Changes

### 1. neutral objective relation semantics no longer inherit battle standoff gap

In `test_run/test_run_execution.py`, the `neutral` point-anchor objective path inside
`_evaluate_target_with_pre_tl_substrate()` now reads distance control directly from
`reference_distance`, with target distance `0.0`.

This removes the previous incorrect inheritance of:

- `target_front_strip_gap = attack_range - spacing + bias`

for `neutral` objective arrival.

### 2. battle early enemy-front-strip influence is now proximity-gated

In the same evaluator, battle still computes real `enemy_front_strip_depth`, but that
depth no longer enters the relation gap at full strength from far field.

An internal proximity gate based on the existing relation scale now ramps enemy-front-strip
influence in only when battle is nearer to the relation-active zone.

No new parameter was added.

### 3. active `v4a` no longer consumes FSR

In `test_run/test_run_execution.py`, `fsr_surface["enabled"]` is now disabled for
`movement_model == "v4a"` globally, not only for neutral fixture runs.

`test_run/test_run_scenario.py` truth surface was updated accordingly so the prepared
scenario no longer reports FSR as active for `v4a`.

## Ownership read after this change

- `neutral` still shares the same transition / relation controller family as `battle`
- the allowed semantic difference remains objective source
- `neutral` objective arrival is now point-anchor zero-distance semantics
- `battle` keeps battle standoff semantics, but with reduced far-field over-shaping
- FSR is no longer an active residual owner in the current `v4a` path

## Notes

- This change does **not** solve terminal / hold design broadly
- This change does **not** retire old `v3a` / legacy FSR families
- This change is intended as bounded cleanup and residual-owner removal only
