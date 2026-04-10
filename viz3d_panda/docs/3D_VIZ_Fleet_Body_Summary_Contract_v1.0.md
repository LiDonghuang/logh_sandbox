# 3D VIZ Fleet-Body Summary Contract v1.0

Status: maintained viewer-side contract note  
Scope: viewer consumption of exported fleet-body summary  
Authority: viewer integration reference, not runtime doctrine

## Purpose

This note records the maintained fleet-body summary contract that the 3D viewer should consume instead of recomputing the same fleet geometry locally.

## Maintained source

The maintained producer is upstream in:

- `test_run/test_run_execution.py`

The replay carrier is:

- `viz3d_panda/replay_source.py`

The per-frame contract is:

- `ViewerFrame.fleet_body_summary`

## Required row fields

Per fleet:

- `centroid_x`
- `centroid_y`
- `rms_radius`
- `max_radius`
- `heading_x`
- `heading_y`
- `alive_unit_count`
- `alive_total_hp`

## Viewer rule

For maintained fleet-body geometry, viewer consumers should read the exported summary instead of recomputing:

- camera focus / camera fleet view
- fleet halo baseline and normal placement
- HUD fleet centroid summaries
- other generic viewer-facing fleet body readouts

For interpolation, viewers should still stay on the maintained export by
blending current-frame and next-frame summary rows instead of recomputing fleet
geometry from live node positions.

## Out of scope for this contract

This base contract does not include:

- FSR-specific diagnostics such as `r_eq` or `s_f`
- objective-distance semantics
- combat front-strip geometry
- mechanism-local runtime geometry needed only inside specific runtime subsystems

Those belong to separate diagnostics or mechanism surfaces.
