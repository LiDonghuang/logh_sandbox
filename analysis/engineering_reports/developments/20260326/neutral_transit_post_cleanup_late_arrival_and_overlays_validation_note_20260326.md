# Neutral Transit Post-Cleanup Late Arrival Fix + Minimal Viewer Overlays Validation

Date: 2026-03-26  
Scope: bounded `neutral_transit_v1` validation only

## Commands

```powershell
python -m py_compile test_run/test_run_execution.py viz3d_panda/unit_renderer.py
python -m py_compile viz3d_panda/app.py viz3d_panda/scene_builder.py runtime/engine_skeleton.py test_run/test_run_scenario.py test_run/test_run_entry.py
```

Harness-side validation used the maintained neutral-transit fixture path through `test_run_entry.run_active_surface(...)` with:

- `capture_positions=True`
- `capture_hit_points=True`
- `frame_stride=1`
- `include_target_lines=False`
- `plot_diagnostics_enabled=False`

Viewer-side smoke used:

- `viz3d_panda.replay_source.load_viewer_replay(source='neutral_transit_fixture', ...)`
- `viz3d_panda.replay_source.load_viewer_replay(source='active_battle', ...)`
- `viz3d_panda.unit_renderer.UnitRenderer(...)`

## Late-Side Metrics

Current bounded run:

- `objective_reached_tick = 425`
- `centroid_to_objective_distance final = 0.053`
- `centroid_to_objective_distance min = 0.000`
- `near_target axial progress sign tail = ++-+++-+-+`

Read:

- the late-side result is materially better than the earlier `A1-only` read on final/min distance
- the clamp succeeds at removing positive centroid overshoot past the anchor along the objective axis
- terminal bounce family is reduced but not fully gone; sign alternation still remains near arrival

## Early / Shape Metrics

Current bounded run:

- `front_extent_ratio final = 2.6200`
- `front_extent_ratio peak = 4.8021`
- `formation_rms_radius_ratio peak = 1.0209`

Read:

- this turn did not attempt a new early-side fix
- early-side residual remains an open mechanism topic and should not be misread as closed by this late-only turn

## Viewer Overlay Smoke

Neutral-transit replay smoke:

- `objective_marker_children = 2`
- `fleet_halo_children = 1`

Active-battle replay smoke:

- `active_objective_marker_children = 0`
- `active_fleet_halo_children = 2`

Read:

- single-fleet objective marker attaches only on the bounded neutral-transit path
- fleet halo attaches on both neutral-transit and active-battle replay paths
- no objective-marker leakage was observed on active battle

## Human-Visible Read

Current honest read:

- the late-side mechanism now shows a real numerical improvement
- the overlay layer is present and scoped correctly
- full human-visible closure on terminal bounce is not yet claimed
- direct human 3D observation is still required before describing this as clearly above threshold

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: bounded neutral-transit late-side validation plus viewer overlay smoke
- Affected Parameters: none user-facing
- New Variables Introduced: none
- Cross-Dimension Coupling: objective marker consumes existing fixture-owned carrier data only
- Mapping Impact: none
- Governance Impact: validates the post-cleanup late-only bounded turn without reopening early-side work
- Backward Compatible: yes

Summary
- Late-side terminal overshoot is reduced in realized centroid behavior.
- Final/min anchor distance is improved.
- Sign alternation still exists, so full closure is not claimed.
- Objective marker and fleet halo are both present.
- Objective marker does not leak into active battle replay.
