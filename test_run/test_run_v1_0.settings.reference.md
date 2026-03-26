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

- `test_run_v1_0.testonly.settings.json`
  - Test-only mechanism switches and prototype parameters.
  - Current usage: `runtime.physical.contact_model.test_only.hostile_contact_impedance`.

- `test_run_v1_0.viz.settings.json`
  - Rendering/export/layout controls.
  - Should not change battle semantics.
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
