# Step3 / PR6 Fleet-Body Summary Export Phase 1

Status: implemented local record  
Scope: maintained fleet-body summary export contract, `test_run` producer, and 3D consumer cutover  
Authority: local engineering record, not canonical governance authority

## 1. Why this round exists

Before this round, fleet body geometry was being recomputed independently in:

- `test_run`
- `viz3d_panda/camera_controller.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/app.py`
- parts of `viz3d_panda/replay_source.py`

That duplication created a management problem:

- different consumers could silently drift in centroid/radius semantics
- viewer-side presentation code was acting like an owner of fleet-body geometry
- cleanup of old mechanism families was made harder because the same indicators had multiple informal owners

This round establishes a maintained export contract and cuts the active viewer consumers over to it.

## 2. Maintained contract

Each captured `position_frame` now carries:

- `fleet_body_summary`

Per fleet, the maintained row contains:

- `centroid_x`
- `centroid_y`
- `rms_radius`
- `max_radius`
- `heading_x`
- `heading_y`
- `alive_unit_count`
- `alive_total_hp`

Producer formula:

- `centroid = alive-unit position mean`
- `rms_radius = sqrt(mean(||pos - centroid||^2))`
- `max_radius = max(||pos - centroid||)`
- `heading = normalize(sum(unit.orientation_vector))`

## 3. Active owner

The maintained producer now lives in:

- `test_run/test_run_execution.py`

Specifically:

- `_build_fleet_body_summary_for_state(current_state)`
- `frame["fleet_body_summary"] = ...` inside `_capture_position_frame()`

This makes `test_run` the maintained export owner for replay-facing fleet-body geometry.

## 4. Replay / viewer cutover

### A. Replay carrier

`viz3d_panda/replay_source.py` now:

- treats `fleet_body_summary` as a formal frame control key
- parses it into `ViewerFrame.fleet_body_summary`
- validates the required fields explicitly

### B. Camera

`viz3d_panda/camera_controller.py` no longer recomputes fleet centroid/radius/heading from unit lists for normal operation.

It now reads:

- `centroid_x`
- `centroid_y`
- `heading_x`
- `heading_y`
- `max_radius`

from `ViewerFrame.fleet_body_summary`

### C. Halo

`viz3d_panda/unit_renderer.py` no longer owns maintained baseline fleet-body geometry.

It now reads from exported summary for:

- fleet halo baseline radius
- centroid
- alive total HP

Allowed exception retained:

- during smoothing / interpolation, halo centroid may use local node positions as a presentation-only geometry update
- this is not treated as a maintained owner of fleet-body semantics

### D. HUD / overlay

`viz3d_panda/app.py` now reads fleet centroid and centroid-motion speed from exported `fleet_body_summary` instead of recomputing them from `frame.units`.

### E. Replay internal radial-debug path

`viz3d_panda/replay_source.py` no longer recomputes fleet centroids through a standalone helper for radial-debug direction display.

It now reads centroid from `frame.fleet_body_summary`.

## 5. What this round intentionally does not do

This round does **not**:

- unify all runtime-internal centroid/radius calculations
- move FSR-specific diagnostics into the base fleet-body summary
- add objective-distance or front-strip geometry to the base contract
- require the whole runtime to call one shared centroid helper yet

That larger structure line remains future work.

## 6. Immediate post-change rule

For maintained viewer-facing fleet-body geometry:

- the producer is `test_run/test_run_execution.py`
- consumers should read the export
- consumers should not silently redefine the same centroid/radius contract locally

Presentation-only interpolation is the narrow allowed exception.

## 7. Validation

Minimal checks used for this round:

- `python -m py_compile test_run/test_run_execution.py viz3d_panda/replay_source.py viz3d_panda/camera_controller.py viz3d_panda/unit_renderer.py viz3d_panda/app.py`
- `git diff --check`

Dynamic smoke:

- active battle replay builds and `ViewerFrame.fleet_body_summary` is present
- neutral replay builds with neutral fixture override and `ViewerFrame.fleet_body_summary` is present

## 8. Management significance

This round is important because it creates:

- one maintained export owner
- one replay-facing contract
- a cleaner separation between
  - mechanism geometry
  - exported fleet-body summary
  - consumer-local presentation geometry

It is the first concrete step toward the broader long-term fleet-body summary unification line.
