# test_run_v1_0 Settings Reference

## 1) Layered Files

1. `test_run/test_run_v1_0.settings.json`
2. `test_run/test_run_v1_0.runtime.settings.json`
3. `test_run/test_run_v1_0.testonly.settings.json`
4. `test_run/test_run_v1_0.viz.settings.json`
5. `test_run/test_run_v1_0.settings.comments.json`

## 2) What each file is for

- `test_run_v1_0.settings.json`
  - Thin entry file.
  - Declares layer paths and keeps lightweight run-display toggles (`visualization`).
  - `visualization.vector_display_mode` is the single source of truth for unit-direction display mode.

- `test_run_v1_0.runtime.settings.json`
  - Runtime values consumed by simulation.
  - Includes `run_control`, `battlefield`, `fleet`, `unit`, and `runtime` (without test-only mechanism branches).
  - `run_control.post_resolution_hold_steps` is the authoritative hold-window setting for both battle winner hold and neutral-transit objective-arrival hold.

- `test_run_v1_0.testonly.settings.json`
  - Test-only mechanism switches and prototype parameters.
  - Current usage:
    - `runtime.physical.contact_model.test_only.hostile_contact_impedance`
    - `runtime.movement.v4a.test_only.expected_reference_spacing`
    - `runtime.movement.v4a.test_only.reference_layout_mode`
    - `runtime.movement.v4a.test_only.reference_surface_mode`
    - `runtime.movement.v4a.test_only.soft_morphology_relaxation`
    - `runtime.movement.v4a.test_only.shape_vs_advance_strength`
    - `runtime.movement.v4a.test_only.heading_relaxation`
    - `runtime.movement.v4a.test_only.restore_strength`
  - For the current v4a candidate:
    - `runtime.physical.movement_low_level.min_unit_spacing` remains the physical-layer minimum spacing
    - `runtime.movement.v4a.test_only.expected_reference_spacing` carries the expected/reference formation spacing
    - `runtime.movement.v4a.test_only.reference_layout_mode` now selects an explicit reference target aspect (`rect_centered_1.0` or `rect_centered_4.0`) distinct from the fleet's initial spawned aspect ratio
    - `runtime.movement.v4a.test_only.reference_surface_mode` selects between the legacy rigid slot-map reference read and the bounded soft-morphology carrier
    - `runtime.movement.v4a.test_only.soft_morphology_relaxation` controls fleet-level morphology relaxation for the bounded soft-morphology carrier
    - `runtime.movement.v4a.test_only.shape_vs_advance_strength` controls how strongly large morphology error suppresses pure objective advance in favor of ongoing shape transition
    - `runtime.movement.v4a.test_only.heading_relaxation` controls the minimal fleet-level heading realization seam used by the transition carrier
    - `runtime.movement.v4a.test_only.restore_strength` weakens the current bounded restore response without changing public runtime semantics

- `test_run_v1_0.viz.settings.json`
  - Rendering/export/layout controls.
  - Should not change battle semantics.
  - Does not own post-resolution hold duration; that setting remains in layered `run_control`.
  - Does not own unit-direction mode; that setting remains in layered `visualization`.

- `test_run_v1_0.settings.comments.json`
  - Field-level comments migrated from legacy `_comments`.
  - This is the authoritative comments payload for settings keys.

## 3) Merge rule

- Base file: `test_run_v1_0.settings.json`
- Deep-merge order:
  1. runtime layer
  2. test-only layer
- Later layer wins on key conflict.

## 4) Better maintenance approach (low drift)

- Keep comments in one machine-readable file (`settings.comments.json`), not in runtime value files.
- Keep this markdown as architecture/readme only.
- If needed later, add a lightweight key-coverage check script:
  - verify all active settings keys have comment entries
  - fail fast when new keys are added without docs

This keeps value files clean while reducing docs/config drift risk.
