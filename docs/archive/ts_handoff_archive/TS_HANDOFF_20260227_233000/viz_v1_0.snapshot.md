# Visualization Chronicle v1.0

Status: Frozen (Visualization Track Local Governance)  
Scope: `analysis/test_run_v1_0_viz.py`, `analysis/test_run_v1_0.viz.settings.json`  
Reference Contract: `docs/animation_contract_v1.md`

## 1. Purpose

This document archives the current visualization baseline so the simulation runtime and presentation layer stay decoupled.

## 2. Layer Boundary

Visualization is read-only over simulation outputs.

Visualization must not modify:

- `runtime/*`
- simulation state transitions
- movement/combat/targeting/projection semantics
- canonical mapping and governance files

## 3. Current Render Structure

- Main layout: 2-column composite figure.
- Left: 2D battlefield animation.
- Right-top: cohesion trajectory.
- Right-bottom: alive units trajectory.
- Battlefield uses directional quiver markers (orientation-aware).
- Alive/fleet-size text panel is shown at top-left of battlefield.
- Fleet legend is shown at top-right and uses display names.

## 4. Camera and Zoom Baseline

- Discrete zoom levels only: `1x`, `2x`, `4x`.
- Camera check interval is config-driven.
- Transition rule:
1. If zoom trigger condition is met: smooth zoom transition.
2. Else if offscreen trigger condition is met: smooth pan-only transition.
3. Else: no camera transform update.
- Replay start resets camera to full view (`1x`).
- Transition uses smooth interpolation over configured duration.

## 5. Background Baseline

- Background haze band (fixed structural layer in scene).
- One major star.
- Independent asteroids.
- Belt-like asteroid clusters.
- All style/geometry values are externalized in viz settings.

## 6. Data Overlays

- Top-left status:
  - `A - [Alive: n | Fleet Size: current / initial (%)]`
  - `B - [Alive: n | Fleet Size: current / initial (%)]`
- Right-top legend:
  - `A [disp_name]`
  - `B [disp_name]`
- Death-linger ring overlay is supported and settings-driven.

## 7. Configuration Governance

Primary config file:

- `analysis/test_run_v1_0.viz.settings.json`

Rules:

- Visualization-only parameters may be tuned locally.
- Any glyph semantic change must follow governance Class C gate.
- Debug visualization must be switchable and default-off.

## 8. Validation Gate (Operational)

Minimum checks before accepting visualization edits:

1. Units render from first valid frame.
2. No NaN/Inf in rendered positions/orientation vectors.
3. Rendered alive counts match frame data.
4. Camera behavior follows contract.
5. Runtime outputs remain unchanged by visualization toggles.

## 9. Rollback Rule

If rendering regression appears:

1. Revert visualization changes only.
2. Keep runtime untouched.
3. Reproduce with fixed seeds and minimal settings.
4. Re-apply incrementally under the contract gate.

## 10. Version Anchor

This document captures the active v1.0 visualization baseline and is intended as the reference point before `viz_v2` thread work starts.

