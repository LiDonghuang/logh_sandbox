# step3_3d_pr6_active_old_named_cohesion_seam_reroot_record_20260410

## Scope

- baseline/runtime
- maintained internal seam reroot
- no math rewrite

## What changed

The active maintained cohesion seam has been rerooted from old `v3` naming to
honest current naming:

- runtime geometry owner
  - `_compute_cohesion_v3_geometry()`
  - -> `_compute_fleet_cohesion_score_geometry()`

- runtime state carrier
  - `BattleState.last_fleet_cohesion`
  - -> `BattleState.last_fleet_cohesion_score`

- maintained reader update
  - `test_run_execution.py` trajectory export now reads
    `state.last_fleet_cohesion_score`

## What did not change

- the maintained cohesion-score math
- the scalar score semantics
- battle / neutral behavior
- internal diagnostic subterms:
  - `c_conn`
  - `rho`
  - `c_scale`
  - `c_v3`

## Why `_compute_cohesion_v3_geometry()` remains

The old function name is retained on a cold path inside
`runtime/engine_skeleton.py` as a historical 2D-era reference seam.

Reason for retaining it:

- it was one of the project's most important 2D-era mechanism results
- the concept may be revisited later
- retaining the named reference locally is preferable to pretending that this
  history never existed

But the maintained mainline no longer uses that old-name seam. Active code now
calls `_compute_fleet_cohesion_score_geometry()` instead.
