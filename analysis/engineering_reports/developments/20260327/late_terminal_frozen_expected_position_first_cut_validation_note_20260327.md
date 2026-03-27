# Late Terminal Settle - Frozen Expected-Position Reference First Cut Validation

Date: 2026-03-27
Scope: bounded `neutral_transit_v1` validation only

## Commands

```powershell
python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py
```

Validation used the maintained neutral-transit fixture path with layered settings plus:

- `fixture.active_mode = neutral_transit_v1`
- current maintained `movement_model = v4a`
- no viewer-side change or runtime-schema widening

## Latch read

Current bounded run:

- `objective_reached_tick = 425`
- `frozen_terminal_frame_active = True`
- `frozen_terminal_latched_tick = 425`
- `frozen_terminal_centroid_xy = [348.760603, 348.761082]`
- `frozen_terminal_primary_axis_xy = [0.707243, 0.706970]`

This confirms the first cut latched on the first post-step in-window confirmation and stayed bounded to the candidate-active fixture path.

## Terminal metrics

Current bounded run:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.428314`
- `centroid_to_objective_distance min = 0.001637`
- `near_target axial progress sign tail = ++-+-+--++`

Reference from the prior late-only post-cleanup state:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.053`
- `centroid_to_objective_distance min = 0.000`
- `near_target axial progress sign tail = ++-+++-+-+`

Read:

- the latch timing is correct
- centroid-level arrival timing does not regress
- terminal settle is **not closed**
- final tail distance is worse than the prior late-only state, even though minimum distance remains very small

## 428..430 contributor comparison

Current first cut, derived from the exported window dump:

- `tick 428`
  - dominant counts = `target 10 / cohesion 74 / separation 16`
  - `mean_cohesion_norm = 1.790890`
- `tick 429`
  - dominant counts = `target 46 / cohesion 0 / separation 52 / projection 2`
  - `mean_cohesion_norm = 1.169119`
- `tick 430`
  - dominant counts = `target 6 / cohesion 52 / separation 41 / projection 1`
  - `mean_cohesion_norm = 1.762346`

Baseline decomposition reference:

- `tick 428`
  - dominant counts = `target 0 / cohesion 100 / separation 0`
  - `mean_cohesion_norm = 1.000000`
- `tick 429`
  - dominant counts = `target 0 / cohesion 57 / separation 40`
  - `mean_cohesion_norm = 0.781214`
- `tick 430`
  - dominant counts = `target 0 / cohesion 36 / separation 62`
  - `mean_cohesion_norm = 0.608492`

Read:

- the frozen frame does change the contributor mix
- `tick 428` is no longer an immediate `100 / 100` cohesion takeover
- `tick 429` shifts heavily into a `target + separation` mix
- but restore/cohesion magnitude does **not** simply collapse; by `tick 430` it rises again and remains large

## Honest result

This first cut is structurally correct and bounded, but the residual is still open.

Current best read:

- freezing the expected-position reference frame is not enough by itself
- it interrupts the old always-moving restore frame, but does not produce a clean terminal settle
- the residual now reads as a reshaped mix of:
  - remaining target pull
  - still-large restore error against the frozen frame
  - separation / projection reshaping

So the current honest conclusion is:

- **still not closed**

## Human 3D observation addendum

Human review of the Panda3D replay for the same late window reports:

- `tick 425 .. 435` still shows a strong formation-break / fragmentation read
- unit direction still flips violently in the objective area
- the current first cut therefore does **not** cross the human-visible threshold for terminal settle

This human read is consistent with the headless validation:

- the contributor mix changed
- but unit-level residual motion did not collapse into a stable shared settle
- the remaining terminal disorder is still clearly visible in 3D

Therefore the current result remains:

- **still not closed**

## Files

- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_component_summary_20260327.csv`
