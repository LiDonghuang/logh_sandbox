# step3_3d_pr6_fleet_body_summary_phase1_residue_audit_planning_20260410

## Scope

- baseline/runtime: planning carrier only
- test-only or harness-only: cross-layer planning (`test_run` + `viz3d_panda`)
- protocol or policy only: no

## Current state

Phase 1 of the maintained `fleet_body_summary` contract is already active:

- producer:
  - `test_run/test_run_execution.py`
- frame carrier:
  - `viz3d_panda/replay_source.py`
- active consumers:
  - `viz3d_panda/camera_controller.py`
  - `viz3d_panda/unit_renderer.py`
  - `viz3d_panda/app.py`

Viewer-facing fleet body geometry now uses the shared export instead of
consumer-local maintained recomputation.

## Residual categories

### A. Allowed presentation-only exception

- `viz3d_panda/unit_renderer.py`
  - `_sync_fleet_halos(..., use_node_positions=True)`
  - still recomputes a temporary centroid from current node positions during
    interpolation/smoothing

This remains acceptable only as a presentation-only exception. It must not grow
into a second maintained owner for fleet-body geometry.

### B. Viewer-side residue audit still worth doing

Re-check for any remaining consumer-local maintained geometry in:

- `viz3d_panda/app.py`
- `viz3d_panda/camera_controller.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/replay_source.py`

Current read:

- camera: already rerooted to `frame.fleet_body_summary`
- halo baseline and normal placement: already rerooted
- HUD fleet centroid/speed readout: already rerooted

### C. Harness/runtime internal duplicates that are out of Phase 1 scope

The following are still repeated, but they are not yet all the same semantic
owner and should not be mixed into the viewer contract turn:

- `test_run/test_run_execution.py`
  - `_compute_position_centroid()`
  - `_compute_centroid_and_rms_radius()`
  - fixture metrics
  - battle observer metrics
- `runtime/engine_skeleton.py`
  - mechanism-local centroid/radius uses

These require a later Phase 2 decision separating:

- maintained exported fleet-body summary
- mechanism-local geometry
- presentation-only geometry

## Recommended next order

1. finish `test_mode` retirement
2. keep this Phase 1 contract stable for at least one more cleanup slice
3. then run a small residue audit on viewer-side exceptions only
4. only later consider Phase 2 harness/runtime internal unification

