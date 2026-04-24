# Step3 / PR6 Fleet-Body Summary Export Unification Management Note

Status: management / methodology note  
Scope: future cleanup and structure work for unified fleet-body summary export  
Authority: local engineering note, not yet canonical policy

## 1. Why this note exists

Current code still recomputes fleet body summary quantities in multiple places:

- runtime
- harness / `test_run`
- 3D consumers

The duplicated quantities include, at minimum:

- centroid
- radius-like summaries
- objective-distance style body summaries

This is a long-term management problem because repeated local recomputation causes:

- inconsistent semantics across subsystems
- consumer-local drift
- harder cleanup of old mechanism families
- confusion about what is an indicator and what is an actuator owner

## 2. Concrete duplication observed in this stage

Examples of repeated centroid/radius computation currently exist in:

### Runtime

- `runtime/engine_skeleton.py`
  - `_compute_cohesion_v3_geometry()`
  - `evaluate_target()`
  - passive fleet-radius diagnostics in `integrate_movement()`

### Harness / test_run

- `test_run/test_run_execution.py`
  - `_compute_position_centroid()`
  - `_compute_centroid_and_rms_radius()`
  - fixture/objective observer calculations

### 3D consumers

- `viz3d_panda/camera_controller.py`
- `viz3d_panda/unit_renderer.py`

In particular, the fleet halo and camera summary currently derive radius/centroid locally instead of consuming a maintained exported summary.

## 3. Recommended future direction

Create one maintained fleet-body summary export for each tick, owned upstream and reused downstream.

The future shared export should likely include:

- `centroid_x`
- `centroid_y`
- `rms_radius`
- `max_radius`
- `heading_x`
- `heading_y`

Possible extensions later, if truly needed:

- objective distance summary
- body forward/lateral extent
- front/back strip summary

## 4. Design rule implied by this note

The preferred future structure is:

- one upstream owner computes fleet-body summary
- viewers and reports consume it
- consumers do not silently redefine body geometry locally unless there is a clearly local-only presentation need

This should be treated as a management / cleanup principle first, not as an excuse to immediately build a large export framework.

## 5. Immediate recommendation

Do **not** mix this unification into the current FSR/contact cleanup round.

Instead:

1. finish the current subtraction-first cleanup slice  
2. record this duplication explicitly  
3. later open a dedicated cleanup/structure line for fleet-body summary export unification  

## 6. Candidate future methodology status

This note is important enough that it may later deserve promotion into a reusable cleanup methodology rule.

However, it should only move into AGENTS if the project first proves a stable general method for:

- choosing the single owner
- defining the maintained export contract
- preventing consumer-side silent recomputation drift

Until then, this note should be treated as:

- a strong engineering recommendation
- a future cleanup planning anchor
- a reference for ownership-truth reviews
