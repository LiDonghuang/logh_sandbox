# Late Terminal Settle - Orientation Freeze / Live-Centroid Split Cut Validation

Date: 2026-03-27
Scope: bounded `neutral_transit_v1` validation only

## Validation path

Validation used the maintained neutral-transit fixture path with:

- `fixture.active_mode = neutral_transit_v1`
- current maintained `movement_model = v4a`
- candidate-active expected-position reference path
- no viewer-side or replay-side change

Focused checks:

```powershell
python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py
```

The headless validation run used the maintained prepared carrier and exported the terminal window CSVs from the resulting fixture telemetry.

## Comparison set

This note compares three states:

1. baseline decomposition state
   - late-only post-cleanup bounded state
2. prior whole-frame frozen first cut
3. current orientation-freeze / live-centroid split cut

## Current split-cut latch read

- `objective_reached_tick = 425`
- `frozen_terminal_frame_active = True`
- `frozen_terminal_latched_tick = 425`
- `frozen_terminal_primary_axis_xy = [0.707243, 0.706970]`

Read:

- the bounded latch still activates at the same first post-step in-window confirmation
- the active split cut keeps only the orientation latch
- the old frozen centroid center is no longer part of the consumed expected-position path

## Arrival integrity

Current split cut:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.055162`
- `centroid_to_objective_distance min = 0.000000`

Reference: baseline late-only decomposition state:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.053`
- `centroid_to_objective_distance min = 0.000`

Reference: prior whole-frame frozen first cut:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.428314`
- `centroid_to_objective_distance min = 0.001637`

Read:

- arrival timing is not degraded relative to either comparison state
- final tail distance is dramatically better than the prior whole-frame freeze
- arrival integrity is now back near the prior late-only state

## 428..430 contributor mix

Baseline decomposition state:

- `tick 428`
  - dominant counts = `target 0 / cohesion 100 / separation 0 / projection 0`
  - `mean_cohesion_norm = 1.000000`
- `tick 429`
  - dominant counts = `target 0 / cohesion 57 / separation 40 / projection 3`
  - `mean_cohesion_norm = 0.781214`
- `tick 430`
  - dominant counts = `target 0 / cohesion 36 / separation 62 / projection 2`
  - `mean_cohesion_norm = 0.608492`

Prior whole-frame frozen first cut:

- `tick 428`
  - dominant counts = `target 10 / cohesion 74 / separation 16 / projection 0`
  - `mean_cohesion_norm = 1.790890`
- `tick 429`
  - dominant counts = `target 46 / cohesion 0 / separation 52 / projection 2`
  - `mean_cohesion_norm = 1.169119`
- `tick 430`
  - dominant counts = `target 6 / cohesion 52 / separation 41 / projection 1`
  - `mean_cohesion_norm = 1.762346`

Current orientation-freeze / live-centroid split cut:

- `tick 428`
  - dominant counts = `target 44 / cohesion 56 / separation 0 / projection 0`
  - `mean_cohesion_norm = 0.908925`
- `tick 429`
  - dominant counts = `target 15 / cohesion 12 / separation 69 / projection 4`
  - `mean_cohesion_norm = 0.548660`
- `tick 430`
  - dominant counts = `target 1 / cohesion 10 / separation 88 / projection 1`
  - `mean_cohesion_norm = 0.784267`

Read:

- the frozen-wrong-center tug-of-war is materially reduced
- cohesion no longer reasserts itself at `tick 430` the way it did under whole-frame freeze
- by `429..430`, the residual becomes primarily `separation`-dominant instead of `frozen centroid mismatch`-dominant

## Honest result

This split cut is a clear improvement over the prior whole-frame freeze:

- arrival integrity is restored to near the prior late-only baseline
- the contributor mix is cleaner
- the whole-frame frozen-center mismatch is no longer the main late-tail conflict

However, closure is still not claimed.

## Later human 3D follow-up

After this headless validation, a direct 3D replay pass was performed around `tick 425 .. 435`.

That human-visible follow-up confirmed the split cut was still not sufficient:

- formation fracture remained strong
- visible shaking started already around the terminal approach
- after centroid arrival, many units still flipped hard on a per-tick basis

So the later human read reinforced, rather than weakened, the headless conclusion:

- **still not closed**

Current honest read:

- the split cut fixes the wrong-center freeze problem
- the remaining late-tail residual now looks more like a `separation / projection reshaping` family than a restore-center mismatch
- later human 3D replay follow-up also confirmed that the residual remained strongly visible

Therefore the current bounded result is:

- **improved, but still not closed**

## Files

- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_window_dump_20260327.csv`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_component_summary_20260327.csv`
