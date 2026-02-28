# Animation Contract v1.0

Status: Approved (Phase V Visualization Governance Decision)  
Owner: Human + Engineering (Codex)  
Applies To: `analysis/test_run_v1_0_viz.py`, `analysis/test_run_v1_0.viz.settings.json`  
Out Of Scope: `runtime/*`, combat/movement/targeting/projection logic

## 1. Purpose

Define a stable collaboration contract for visualization work so that:

- visual iteration remains fast;
- rendering changes do not accidentally alter simulation semantics;
- debugging and rollback become predictable.

## 2. Hard Boundaries

Visualization changes must not modify:

- `runtime/*` code and behavior;
- simulation state or state-transition semantics;
- movement logic;
- combat logic;
- parameter semantics.

Visualization code may only consume simulation outputs and render them.

Visualization has no Canonical Authority. It must not reinterpret canonical mapping or governance intent.

## 3. Visual Semantics Invariants

The following are considered canonical visualization semantics:

- 2D battlefield uses unit orientation markers (quiver-based directional glyphs), not implicit point-only fallback in release mode.
- Fleet colors map to archetype `color_code` (or documented fallback).
- Camera zoom states are discrete: `1x`, `2x`, `4x`.
- Camera transition is progressive (smooth interpolation), not hard jump.
- Auto-zoom check cadence follows configured tick interval.
- Live count panel must reflect rendered alive units per fleet.
- Layer priority on battlefield is fixed: background/grid/decorations < boundary and transient markers < unit arrows < HUD overlays.
- HUD overlays (top-left live count panel, top-right legend) must remain above unit arrows at all times.

If any item changes, it must be recorded in Change Log section before merge.

For visualization-only changes:

- feature must be fully switchable OFF;
- default must remain minimal interpretive form;
- base glyph semantics must remain unchanged unless Class C approval is granted.

## 4. Camera Behavior Contract

Decision priority per camera check:

1. If zoom trigger condition is met: execute smooth zoom transition to target center/scale.
2. Else if off-screen ratio threshold is exceeded: execute smooth pan-only transition.
3. Else: no camera transform update.

Additional constraints:

- If target zoom level equals current level, skip zoom update.
- At animation replay start, reset camera to `1x` full view.
- Do not move camera on non-check frames except active transition interpolation.

## 5. Settings Governance (Visualization Layer)

Any new visualization setting must include:

- purpose (one sentence);
- observable effect (what user should see);
- default value;
- safe range;
- ownership class: `visual-only` or `cross-layer-risk`.

`cross-layer-risk` settings are not allowed without explicit review.

## 6. Debug Instrumentation Rules

Allowed:

- debug assertions for render data integrity;
- frame-level diagnostics for NaN/Inf/out-of-range data;
- temporary overlays for camera diagnostics.

Required:

- all debug features must be behind explicit flags;
- default must be OFF;
- debug code path must not change release rendering semantics.

## 7. Validation Gate (Before Accepting Visual Changes)

Minimum checks:

1. Render Presence: units visible from first valid frame.
2. Frame Integrity: no NaN/Inf in rendered positions/orientation vectors.
3. Count Consistency: rendered alive counts match simulation frame data.
4. Camera Contract: zoom/pan follows section 4 logic.
5. Determinism Safety: identical runtime inputs yield identical simulation outputs with/without visualization enabled.
6. Regression Check: no accidental symbol-type downgrade (e.g., directional glyph -> plain dots) unless explicitly approved.

## 8. Change Classes and Approval Path

Class A (No Governance Needed):

- colors, line widths, background styling, typography, legend layout.

Class B (Engineering Review Needed):

- camera policies, interpolation timing, marker geometry, frame sampling.
- rendering path replacement;
- visualization parameter externalization;
- debug-only visualization tooling.

Class C (Governance Gate Needed):

- glyph semantic change (for example: arrow to point, directional shape meaning change, major length-ratio meaning change);
- scale interpretation change (for example: nonlinear magnification that changes quantitative reading);
- introducing smoothing/interpolation/filtering on simulation-derived series or positions;
- any change that alters behavioral interpretability or cross-layer semantic cognition;
- any change requiring modification to `runtime/*` or simulation data definitions.

## 9. Rollback Protocol

If a visualization regression is detected:

1. Revert to last known-good visualization commit.
2. Keep simulation code untouched.
3. Reproduce issue with a minimal settings profile.
4. Re-apply changes incrementally under Class A/B/C workflow.

## 10. Local Operating Rule

Engineering executes within this contract by default.  
Governance is consulted only for Class C or scope ambiguity.

## 11. Change Log

v1.0 (Approved):

- Initial contract created.
- Encodes camera priority, semantic invariants, debug discipline, and approval classes.
- Updated to Phase V governance decision:
  - Class A/B local governance approved.
  - Class C governance gate criteria expanded and explicit.
  - Mandatory constraints on runtime isolation, toggleability, and canonical authority recorded.
