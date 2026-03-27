# Late Terminal Settle - Step-Magnitude + One-Sided Axial Restore Validation

Date: 2026-03-27
Scope: bounded `neutral_transit_v1` validation only

## Validation path

Validation used:

- `fixture.active_mode = neutral_transit_v1`
- maintained `movement_model = v4a`
- single-fleet candidate-active expected-position path
- no viewer-side semantic change

Focused checks:

```powershell
python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py
```

The headless run exported a terminal window dump and per-tick component summary from:

- `objective_reached_tick - 5 .. objective_reached_tick + 5`

Human review was then performed in the 3D viewer around the same window.

## Comparison set

This note compares four states:

1. prior late-only post-cleanup bounded state
2. whole-frame freeze first cut
3. orientation-freeze / live-centroid split cut
4. current step-magnitude + one-sided axial restore candidate

## Arrival integrity

Current accepted candidate:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.001780`
- `centroid_to_objective_distance min = 0.001780`

Reference:

- late-only bounded state
  - `objective_reached_tick = 425`
  - `distance_final = 0.053`
- whole-frame freeze
  - `objective_reached_tick = 425`
  - `distance_final = 0.428314`
- orientation-freeze / live-centroid split cut
  - `objective_reached_tick = 425`
  - `distance_final = 0.055162`

Read:

- arrival timing is preserved
- final terminal distance is much smaller than the prior split cut
- arrival integrity remains strong while terminal motion is heavily reduced

## Terminal window summary

Current accepted candidate:

- `tick 428`
  - `mean_step_magnitude_gain = 0.219054`
  - `mean_pre_projection_total_norm = 0.219054`
  - `mean_realized_disp_norm = 0.219054`
  - `mean_cohesion_norm = 0.575120`
  - dominant counts = `target 68 / cohesion 32 / separation 0 / projection 0`
  - `backward_count = 2`
  - `front10_backward_count = 2`
- `tick 429`
  - `mean_step_magnitude_gain = 0.113908`
  - `mean_pre_projection_total_norm = 0.113908`
  - `mean_realized_disp_norm = 0.113908`
  - `mean_cohesion_norm = 0.528189`
  - dominant counts = `target 70 / cohesion 30 / separation 0 / projection 0`
  - `backward_count = 0`
- `tick 430`
  - `mean_step_magnitude_gain = 0.056954`
  - `mean_pre_projection_total_norm = 0.056954`
  - `mean_realized_disp_norm = 0.056954`
  - `mean_cohesion_norm = 0.506417`
  - dominant counts = `target 70 / cohesion 30 / separation 0 / projection 0`
  - `backward_count = 0`

Read:

- this candidate no longer leaves the late tail dominated by separation/projection reshaping
- per-unit movement magnitude is now strongly compressed once the fleet is inside the terminal window
- the mass backward settle seen in the weaker candidate is gone by `tick 429`

## Remaining visible artifact

Human 3D review still found one very narrow residual:

- at `tick 428`, the two same long-standing frontmost protruding units are pulled backward once
- from `tick 429` onward they no longer continue changing

Trace confirms that those two units are:

- `A88`
- `A93`

and that at `tick 428` they are exactly the two frontmost outliers in the fleet.

## Locally rejected follow-up

One stricter follow-up was also tested locally:

- terminal `no-net-backward axial clamp`

That branch removed the remaining `tick 428` backward count, but produced a new visible defect:

- the same two frontmost units rotated left from `tick 425 .. 430`
- then snapped back at `tick 431`

That variant was rejected and reverted.

## Honest result

Current honest read:

- this is the best local late-terminal candidate so far
- it materially outperforms whole-frame freeze and split-cut-only
- it is human-confirmed as the correct current direction
- but it is still reported as a bounded candidate, not a generalized closure claim

## Files

- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_step_magnitude_one_sided_restore_component_summary_20260327.csv`
