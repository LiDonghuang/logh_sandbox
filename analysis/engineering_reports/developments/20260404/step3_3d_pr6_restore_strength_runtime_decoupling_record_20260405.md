# PR6 / dev_v2.1 `restore_strength` Runtime Decoupling Record

Status: major-item record  
Date: 2026-04-05  
Scope: runtime / movement ownership only  
Authority: local implementation record; not merge approval

## Summary

`runtime.movement.v4a.restore_strength` has been re-rooted so that current
`v4a` movement no longer depends on the old runtime cohesion decision line:

- `runtime.selectors.cohesion_decision_source = v2`
- `runtime.selectors.cohesion_decision_source = v3_test`

The active `v4a` movement path now keeps:

- direct scaling of the runtime restore vector by `v4a_restore_strength`

and no longer consumes:

- `last_fleet_cohesion -> enemy_cohesion -> deep_pursuit_mode`
- `forward_gain / cohesion_gain / extension_gain`

as active owners on the `v4a` line.

## Files touched

- `runtime/engine_skeleton.py`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_active_ownership_map_20260404.md`

## Implementation read

Inside `runtime/engine_skeleton.py`, the movement-only deep-pursuit gain family
is now bypassed when `v4a_active`:

- `enemy_cohesion = 1.0`
- `enemy_collapse_signal = 0.0`
- `deep_pursuit_mode = False`
- `pursuit_intensity = 0.0`
- `forward_gain = 1.0`
- `cohesion_gain = 1.0`
- `extension_gain = 1.0`

This is subtraction-first:

- old runtime cohesion decision no longer biases `v4a` movement
- `v4a_restore_strength` still scales the restore vector directly

## Validation

Paired comparison was run under identical `v4a` settings with only
`runtime.selectors.cohesion_decision_source` changed between `v2` and
`v3_test`.

Cases:

- battle, `max_time_steps = 5`
- battle, `max_time_steps = 50`
- neutral_transit_v1, `max_time_steps = 5`
- neutral_transit_v1, `max_time_steps = 50`

Observed result in all four comparisons:

- `max_unit_pos_diff = 0.0`
- `mean_unit_pos_diff = 0.0`
- centroid deltas = `0.0`

So current `v4a` movement is no longer sensitive to the old runtime cohesion
decision selector.

## What is still not retired

This decoupling does **not** retire the old families yet.

Still live:

- `runtime.selectors.cohesion_decision_source` as baseline / legacy selector
- old `v3a` experiment surface
- observer / cohesion-report surfaces that still read the old selector

So the result is:

- `restore_strength` decoupling for active `v4a` movement: completed
- old family retirement: not yet started here
