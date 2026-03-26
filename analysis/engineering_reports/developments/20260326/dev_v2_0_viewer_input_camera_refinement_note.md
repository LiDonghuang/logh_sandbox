# dev_v2.0 Viewer Input / Camera Refinement Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: `viz3d_panda/` viewer-local input and camera-control layer only
Affected Parameters: viewer-local key bindings, step-repeat behavior, viewer-local fleet camera tracking behavior
New Variables Introduced: viewer-local hold-step timing constants and viewer-local tracked-fleet state
Cross-Dimension Coupling: none; replay data is consumed only to derive fleet centroid/heading for camera initialization and tracking
Mapping Impact: none
Governance Impact: records bounded human-observation refinements inside the additive viewer container
Backward Compatible: yes

Summary
- `N/B` now support hold-to-repeat stepping in addition to single-step.
- Reset is now bound only to the backquote/tilde physical key.
- Reset now uses a near-top-down "2D" view as the default camera reset state.
- `1/2` now initialize a fleet-facing camera for fleet `A/B` and then keep centroid tracking active.
- While tracking is active, backquote/tilde cancels tracking instead of resetting the camera.
- While tracking is inactive, backquote/tilde performs the normal reset.
- Tracking updates focus only after initialization, so manual yaw/pitch/zoom adjustments remain under human control.

## Scope

This turn is viewer-local usability only.

It does not:

- change replay ownership
- change simulation ownership
- change objective semantics
- change movement / formation / combat / legality

## Changes

### Step Repeat

`N/B` now behave as:

- press once -> one frame step
- hold -> repeated frame stepping after a short delay

This is a viewer-local playback convenience only.

### Reset Key

Reset is now bound only to:

- backquote / tilde

The older `C` reset binding is retired.

### Reset Camera Shape

The default reset view is now a near-top-down "2D" reading:

- `yaw = 0`
- `pitch = -89`

This makes the reset surface align more closely with the existing 2D reading habit.

### Fleet Camera Tracking

`1` and `2` now:

- initialize a fleet-facing camera for fleet `A` / `B`
- start viewer-local centroid tracking for that fleet

The initialization uses:

- fleet centroid
- aggregate fleet heading
- fixed viewer-local oblique pitch

After initialization, tracking updates:

- centroid / focus only

and deliberately does **not** keep forcing:

- yaw
- pitch
- zoom distance

This preserves human control after tracking begins.

### Conditional Reset Behavior

The reset key now behaves by state:

- tracking active -> cancel tracking
- tracking inactive -> perform normal reset

## Validation

Minimal validation completed:

- `python -m py_compile viz3d_panda/app.py viz3d_panda/camera_controller.py`
- source inspection of active bindings / tracking methods

Validated surfaces include:

- hold-step binding for `N/B`
- backquote / tilde reset binding only
- fleet tracking entry on `1/2`
- tracked-frame sync that updates focus without re-forcing yaw/pitch
