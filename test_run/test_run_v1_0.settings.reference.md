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
  - `runtime.observer.tick_timing_enabled` is the single observer-side switch for recording per-tick wall-clock elapsed time into telemetry; default is enabled and it does not change battle semantics.
  - `runtime.physical.fire_control.fire_optimal_range_ratio` is the bounded range-quality carrier for the current targeting candidate; `attack_range` remains max range, while the ratio defines the full-quality inner band.

- `test_run_v1_0.testonly.settings.json`
  - Test-only mechanism switches and prototype parameters.
  - Current usage:
    - `runtime.physical.contact_model.hostile_contact_impedance`
    - `runtime.movement.v4a.restore_strength`
    - `runtime.movement.v4a.expected_reference_spacing`
    - `runtime.movement.v4a.reference_layout_mode`
    - `runtime.movement.v4a.reference_surface_mode`
    - `runtime.movement.v4a.soft_morphology_relaxation`
    - `runtime.movement.v4a.shape_vs_advance_strength`
    - `runtime.movement.v4a.heading_relaxation`
    - `runtime.movement.v4a.battle_standoff_hold_band_ratio`
    - `runtime.movement.v4a.battle_target_front_strip_gap_bias`
    - `runtime.movement.v4a.battle_relation_lead_ticks`
    - `runtime.movement.v4a.engaged_speed_scale`
    - `runtime.movement.v4a.attack_speed_lateral_scale`
    - `runtime.movement.v4a.attack_speed_backward_scale`
  - For the current v4a candidate:
    - `runtime.physical.movement_low_level.min_unit_spacing` remains the physical-layer minimum spacing
    - `runtime.movement.v4a.restore_strength` is the active v4a reuse of the runtime `v3_test` centroid-probe carrier; values below `1.0` enable the bounded bridge attenuation and values at `1.0` fall back to the base read
    - `runtime.movement.v4a.expected_reference_spacing` carries the expected/reference formation spacing
    - `runtime.movement.v4a.reference_layout_mode` now selects an explicit reference target aspect (`rect_centered_1.0` or `rect_centered_4.0`) distinct from the fleet's initial spawned aspect ratio
    - `runtime.movement.v4a.reference_surface_mode` selects between the legacy rigid slot-map reference read and the bounded soft-morphology carrier
    - `runtime.movement.v4a.soft_morphology_relaxation` controls fleet-level morphology relaxation for the bounded soft-morphology carrier
    - `runtime.movement.v4a.shape_vs_advance_strength` controls how strongly large morphology error suppresses pure objective advance in favor of ongoing shape transition
    - `runtime.movement.v4a.heading_relaxation` controls the minimal fleet-level heading realization seam used by the transition carrier
    - `runtime.movement.v4a.battle_standoff_hold_band_ratio` defines the near-`d*` no-chase band used by the bounded battle standoff carrier
    - `runtime.movement.v4a.battle_target_front_strip_gap_bias` is the single active correction bias on the base front-strip target gap; it replaces the older two-weight extent buffer interface on the current local line
    - `runtime.movement.v4a.battle_hold_weight_strength` defines how strongly the bounded near-`d*` hold state suppresses approach authority; the read is reversible, so if fleets are separated again, pre-contact-like approach can resume
    - `runtime.movement.v4a.battle_relation_lead_ticks` defines the near-contact lead window in ticks for signed battle-relation slowdown
    - `runtime.movement.v4a.battle_hold_relaxation` defines the restored raw-to-current smoothing weight for the signed near-contact relation family (`battle_relation_gap`, `close_drive`, `brake_drive`, `hold_weight`)
    - `runtime.movement.v4a.battle_approach_drive_relaxation` defines the restored raw-to-current smoothing weight for forward approach authority as a separate seam from hold/brake state
    - `runtime.movement.v4a.battle_near_contact_internal_stability_blend` defines the restored near-contact internal-speed unification blend that pulls unit-local speed factors back toward fleet-level behavior while hold is active
    - `runtime.movement.v4a.battle_near_contact_speed_relaxation` defines the restored per-unit max-speed smoothing seam used after near-contact internal stabilization adjusts unit-local speed targets
    - `runtime.movement.v4a.engaged_speed_scale` defines the overall movement-speed reduction for engaged units
    - `runtime.movement.v4a.attack_speed_lateral_scale` and `runtime.movement.v4a.attack_speed_backward_scale` define the first bounded attack-direction-aware movement allowance for engaged units, aligned conceptually with the existing combat-angle cosine read

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
