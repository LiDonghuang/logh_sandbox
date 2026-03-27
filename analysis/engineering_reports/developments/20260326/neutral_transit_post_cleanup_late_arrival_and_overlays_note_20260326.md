# Neutral Transit Post-Cleanup Late Arrival Fix + Minimal Viewer Overlays

Date: 2026-03-26  
Scope: bounded `neutral_transit_v1` only  
Layer: late-side mechanism correction plus viewer-local consumption overlays only

## Identity

This turn is a bounded post-cleanup follow-up.

It does only three things:

1. keeps the existing early-side state unchanged
2. adds one late-side result clamp inside the existing `stop_radius` window
3. adds two minimal viewer overlays that consume already-owned runtime/fixture results

It does not:

- reopen early-side mechanism work
- add settings
- add replay protocol
- add viewer semantic ownership
- grow a new marker or halo framework

## Mechanism Change

File:

- `test_run/test_run_execution.py`

Current late-side correction is now:

- keep existing `A1` arrival gain in `_evaluate_target_with_fixture_objective(...)`
- add a post-move terminal non-overshoot clamp in `TestModeEngineTickSkeleton.step(...)`

The clamp is bounded as follows:

- applies only when fixture mode is `neutral_transit_v1`
- applies only to the fixture fleet
- uses only the existing `objective_contract_3d` anchor and existing `stop_radius`
- activates only when pre-step centroid distance to anchor is already within `stop_radius`
- measures realized centroid advance along the current objective axis
- if that realized forward advance would overshoot the remaining anchor distance, it removes only the overshoot amount by a uniform reverse translation applied to alive units of the fixture fleet
- lateral residual is left untouched

What it does not add:

- no new user parameters
- no new settings surface
- no second radius
- no latch
- no speed/step heuristic quantity family
- no fallback family

## Viewer Overlays

File:

- `viz3d_panda/unit_renderer.py`

Two viewer-local overlays were added.

### V1. Single-Fleet Objective Marker

For bounded neutral-transit point-anchor replay only:

- a small red center marker is drawn at `anchor_point_xyz`
- a ring is drawn using the existing `stop_radius`
- if `stop_radius <= 0`, only the center marker is shown
- if no valid point-anchor fixture readout exists, nothing is shown

This overlay reads only from `ReplayBundle.metadata["fixture_readout"]`.

### V2. Fleet Halo

For every frame and every fleet:

- compute current-frame live-unit geometric centroid
- compute current-frame max radial extent
- render one low-alpha halo ring from that single scan

This remains viewer-local consumption only.

## Boundary Check

- `runtime/runtime_v0_1.py` untouched
- `runtime/engine_skeleton.py` untouched in this turn
- no early-side mechanism added
- no replay ownership widened
- no viewer-owned objective meaning introduced

## Files Touched

- `test_run/test_run_execution.py`
- `viz3d_panda/unit_renderer.py`

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: bounded neutral-transit late-side mechanism and viewer-local overlay layer
- Affected Parameters: none user-facing
- New Variables Introduced: none in public settings; only local overshoot handling and overlay nodes
- Cross-Dimension Coupling: viewer reads existing fixture-owned point-anchor and stop radius only
- Mapping Impact: none
- Governance Impact: implements the post-cleanup late-only bounded turn without reopening early-side work
- Backward Compatible: yes

Summary
- `A1` remains the intent-side late gain.
- A result-side non-overshoot clamp now prevents positive centroid overshoot inside `stop_radius`.
- Objective marker uses existing fixture anchor and stop radius only.
- Fleet halo uses current-frame centroid plus max radial extent only.
- No new settings, no new replay protocol, no new framework surface.
