# Animation Contract v1.0

Status: Approved (Phase V Visualization Governance Decision)  
Owner: Human + Engineering (Codex)  
Applies To: `test_run/test_run_v1_0_viz.py`, `test_run/test_run_v1_0.viz.settings.json`  
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
- Live count panel includes per-side color markers and two-row side-aligned text; marker/text alignment is part of regression baseline.
- Layer priority on battlefield is fixed: background/grid/decorations < boundary and transient markers < unit arrows < HUD overlays.
- HUD overlays (top-left live count panel, battlefield corner identity blocks) must remain above unit arrows at all times.
- Boundary visual state is canonical:
  - soft boundary enabled => black solid frame;
  - soft boundary disabled => dark-gray dotted frame.
- Grid clipping state is canonical:
  - hard boundary enabled => grid clipped to battlefield square;
  - hard boundary disabled => grid not clipped by battlefield square.

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

## 11. Plot Profile Governance (9 Slots)

The 9-slot plotting layout is position-frozen. Slot geometry is stable; only metric assignment may change.

`run_control.test_mode` is the execution permission switch for slot content, but `runtime.selectors.cohesion_decision_source` controls whether v3-test cohesion plots are allowed.

- `0` (`default`): baseline runtime only; plots are forced to baseline.
- `1` (`observe`): baseline runtime + observer/event diagnostics; plots remain baseline unless `cohesion_decision_source=v3_test`, in which case v3-test diagnostic plots are shown while runtime stays baseline.
- `2` (`test`): experimental runtime selectors permitted; plots remain baseline unless `cohesion_decision_source=v3_test`, in which case both runtime selection and v3-test diagnostic plots may activate.

Plot-profile resolution rule:

- `plot_profile=auto`:
  - baseline if requested cohesion source is `baseline` or `v2`;
  - extended only if requested cohesion source is `v3_test` and `test_mode>=1`.
- `plot_profile=extended` is invalid unless requested cohesion source is `v3_test` and `test_mode>=1`; invalid requests must be remapped to baseline.
- `plot_profile=baseline` is always permitted.

Rules:

- no ad-hoc slot relocation when adding/removing diagnostics;
- metric promotion path is explicit: when a test metric is officially adopted, slot mapping and labels must be updated in both code and this contract;
- deprecated test metrics must be removed from active profile (hidden or reserved), not silently mixed into official slots.

Current active slot mapping:

- `slot_01 + slot_02`: Alive Units
- `slot_03`: Cohesion (`C_v2` baseline or `C_v3` when explicitly in v3-test plot mode)
- `slot_04`: `AR_forward`
- `slot_05`: `WedgeRatio`
- `slot_06`: `SplitSeparation`
- `slot_07`: `LossRate`
- `slot_08`: `CollapseSignal`
- `slot_09`: `C Margin` / `Shadow C Margin`

`observer_enabled` is treated as legacy compatibility input and must not override `test_mode` semantics.

This keeps validation switching predictable while preserving visual continuity.

## 12. Debug Panel Line-Length Governance

Debug panel text must use fixed-width formatting and a fixed maximum row length with clipping.

Required:

- archetype parameter rows use fixed column width (table-like alignment);
- every debug row is clipped to the same max character cap before rendering;
- adding new debug rows must not require panel-boundary retuning.

Goal: avoid right-edge overflow regressions while keeping debug content readable.

## 13. Change Log

v1.0 (Approved):

- Initial contract created.
- Encodes camera priority, semantic invariants, debug discipline, and approval classes.
- Updated to Phase V governance decision:
  - Class A/B local governance approved.
  - Class C governance gate criteria expanded and explicit.
  - Mandatory constraints on runtime isolation, toggleability, and canonical authority recorded.

v1.1 (Local update):
- Plot profile switch updated from legacy `observer_enabled` wording to `test_mode` (`0/1/2`) semantics.

v1.2 (Local update):
- Battlefield corner identity blocks standardized:
  - A avatar anchors near lower-left with slight inset; B avatar anchors near upper-right with slight inset.
  - Avatar border is thicker and aligned parallel with battlefield border.
  - A full-name label sits directly above A avatar border.
  - B full-name label sits directly below B avatar border.
  - Name marker uses larger square style consistent with label block height.
  - Full-name rendering follows `display_language` (`ZH` / `EN`).
  - Avatar/name artists are initialized once per render session and must not be per-tick rebuilt.

v1.3 (Local update):
- Boundary visualization/state contract added:
  - soft boundary OFF uses dark-gray dotted frame;
  - hard boundary OFF disables battlefield-square grid clipping.
- Live-count panel row markers formalized as side-color markers with row alignment as regression baseline.
- Corner identity label format fixed to `<full_name>(A/B)` while preserving `display_language` localization for `full_name`.
- Background celestial generation contract added:
  - primary-star-driven orbital layout,
  - optional visual-only secondary stars,
  - orbit-band-based planet sizing,
  - low-curvature mid/far asteroid-belt arcs.

v1.4 (Local update):
- Secondary-star placement tightened:
  - far-distance constraint from primary star;
  - non-overlap clearance against other major celestial visuals.
- Orbit governance tightened:
  - one orbit shell hosts at most one planet (`1 orbit -> 1 planet`);
  - belt objects must not share orbit shells with planets (exclusion gap).
- Celestial layer order frozen (top -> bottom):
  - asteroid belts;
  - planets/satellites (satellite front/back host randomization allowed);
  - primary star;
  - secondary stars;
  - galaxy haze/background.

v1.5 (Local update):
- Plot-source semantics tightened:
  - baseline/v2 requests must render baseline cohesion plots even in `test_mode=1/2`;
  - v3-test plots are allowed only when `cohesion_decision_source=v3_test` and `test_mode>=1`;
  - `test_mode=1` may show v3-test plots without changing runtime cohesion source;
  - `test_mode=2` may both run and display v3-test when explicitly requested.

v1.6 (Local update):
- Side-plot slot mapping refreshed:
  - removed `rho` from active slot profile;
  - moved Cohesion / `AR_forward` / `WedgeRatio` / `SplitSeparation` to slots `03..06`;
  - added `CollapseSignal` at `slot_07`;
  - moved `C Margin` / `Shadow C Margin` to `slot_08`;
  - `slot_09` is reserved and hidden.

v1.7 (Local update):
- Side-plot slot mapping refreshed again:
  - moved `LossRate` to `slot_07`;
  - moved `CollapseSignal` to `slot_08`;
  - moved `C Margin` / `Shadow C Margin` to `slot_09`.

## 14. Battlefield Identity Block Layout Contract

This section freezes the avatar + full-name visual arrangement on the battlefield canvas.

Position/alignment rules:

- Avatars are inset slightly from battlefield border (not glued to border).
- Avatar borders are thicker than default helper lines and must not protrude with extra pad.
- A-side name block:
  - marker + label share one baseline row above A avatar;
  - label background lower edge visually touches A avatar top border.
- B-side name block:
  - marker + label share one top-aligned row below B avatar;
  - label background upper edge visually touches B avatar bottom border.
- Marker block is larger than legacy marker and visually matched to label block height.
- Name content format is fixed as `<full_name>(A)` for A side and `<full_name>(B)` for B side.
- `full_name` localization still follows `display_language` (`ZH` / `EN`).

Performance/rendering rules:

- Avatar image loading and artist creation occur during setup only.
- Per-tick update path may update dynamic entities (units, lines, counters, debug text), but must not recreate avatar/name artists.

## 15. Background Celestial Generation Contract

Background celestial generation is primary-star driven for coherence and readability.

Rules:

- One primary star is generated first and acts as the reference body for planet/belt orbit-space calculations.
- Optional secondary stars (`0..2`) are visual-only companions (binary/trinary style), sized as scaled variants of primary-star range, and must not become the reference body for planet/belt generation.
- Secondary stars must stay at far distance from the primary star and keep non-overlap clearance against other major celestial visuals.
- Planet-like bodies follow orbit-ratio bands around the primary star:
  - near orbit band: small bodies only;
  - mid/far orbit bands: medium/large bodies allowed.
- Medium/large bodies may host satellites, with moon radius ratio constrained to a small fraction of host size (default `0.1..0.2`).
- Asteroid belts are generated as mid/far orbital arc segments around the primary star, with only mild random curvature (no heavy bend as default style).
- Planet rule: one planet per orbit shell (`1 orbit -> 1 planet`), moons excluded from this constraint.
- Belt rule: belt objects must not share orbit shells with planets (orbit exclusion gap required).

Celestial layer order (top to bottom):

- asteroid belts
- planets / satellites (satellite layer may render in front of or behind host planet)
- primary star
- secondary stars
- galaxy haze/background
