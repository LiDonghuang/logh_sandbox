# test_run_v1_0 Settings Reference

## 1) Layered Files

1. `test_run/test_run_v1_0.settings.json`
2. `test_run/test_run_v1_0.runtime.settings.json`
3. `test_run/test_run_v1_0.testonly.settings.json`
4. `test_run/test_run_v1_0.settings.comments.json`

## 2) What each file is for

- `test_run_v1_0.settings.json`
  - Thin entry file.
  - Declares layer paths.
  - Keeps the small maintained visualization-side surface:
    - `visualization.display_language`
    - `visualization.print_tick_summary`

- `test_run_v1_0.runtime.settings.json`
  - Runtime values consumed by simulation.
  - Includes `run_control`, `battlefield`, `fleet`, `unit`, and `runtime` (without test-only mechanism branches).
  - `run_control.post_resolution_hold_steps` is the authoritative hold-window setting for both battle winner hold and neutral-transit objective-arrival hold.
  - `run_control.observer_enabled` is the maintained run-level switch for enabling observer telemetry and diagnostic exports in `test_run`.
  - `run_control.symmetric_movement_sync_enabled` is the maintained harness-side execution control for symmetric cross-fleet movement merge.
  - `runtime.observer.tick_timing_enabled` is the single observer-side switch for recording per-tick wall-clock elapsed time into telemetry; default is enabled and it does not change battle semantics.
  - `runtime.metatype.settings_path` and `runtime.metatype.random_seed` drive scenario-level Yang/metatype sampling only.
  - These metatype-derived values remain on the prepared high-level interface and do not enter maintained runtime/tick mechanisms.
  - The current targeting candidate consumes:
    - `runtime.physical.fire_control.fire_quality_alpha`
    - `runtime.physical.fire_control.fire_optimal_range_ratio`
  - `attack_range` remains max range; `fire_optimal_range_ratio` defines the full-quality inner band and `fire_quality_alpha` defines the directional fire-quality modifier.
  - Current read:
    - `angle_quality = max(0, 1 + fire_quality_alpha * cos(theta))`
    - `range_quality = 1.0` inside the inner optimal band, then linearly decays to `0.0` at `attack_range`

- `test_run_v1_0.testonly.settings.json`
  - Test-only mechanism switches and prototype parameters.
  - `fixture.neutral.stop_radius` is the neutral-only objective termination radius used by the current neutral fixture line; it is not the battle hold mechanism.
  - Current usage:
    - `runtime.physical.contact.hostile_contact_impedance`
    - `runtime.movement.v4a.restore.strength`
    - `runtime.movement.v4a.reference.expected_reference_spacing`
    - `runtime.movement.v4a.reference.layout_mode`
    - `runtime.movement.v4a.reference.surface_mode`
    - `runtime.movement.v4a.reference.soft_morphology_relaxation`
    - `runtime.movement.v4a.transition.shape_vs_advance_strength`
    - `runtime.movement.v4a.transition.heading_relaxation`
    - `runtime.movement.v4a.battle.standoff_hold_band_ratio`
    - `runtime.movement.v4a.battle.target_front_strip_gap_bias`
    - `runtime.movement.v4a.battle.hold_weight_strength`
    - `runtime.movement.v4a.battle.relation_lead_ticks`
    - `runtime.movement.v4a.battle.hold_relaxation`
    - `runtime.movement.v4a.battle.approach_drive_relaxation`
    - `runtime.movement.v4a.battle.near_contact_internal_stability_blend`
    - `runtime.movement.v4a.battle.near_contact_speed_relaxation`
    - `runtime.movement.v4a.engagement.engaged_speed_scale`
    - `runtime.movement.v4a.engagement.attack_speed_lateral_scale`
    - `runtime.movement.v4a.engagement.attack_speed_backward_scale`
  - The maintained hostile-contact selector is now:
    - `off | hybrid_v2`
  - `intent_unified_spacing_v1` has been retired from the maintained mainline.
  - For the current v4a candidate:
    - `runtime.physical.movement_low_level.min_unit_spacing` remains the physical-layer minimum spacing
    - `runtime.movement.v4a.restore.strength` is the active v4a restore-strength seam
    - current direct read is:
      - `restore_term = restore_strength * normalize(restore_vector)`
    - the current v4a line does not apply `formation_rigidity`, `pursuit_drive`, `mobility_bias`, or any hidden native scale on top of this seam
    - maintained `test_run` now uses a single runtime cohesion geometry on the active mainline; `cohesion_decision_source` and `collapse_signal.v3_*` are no longer part of the maintained public settings surface
    - `runtime.movement.v4a.reference.expected_reference_spacing` carries the expected/reference formation spacing
    - `runtime.movement.v4a.reference.layout_mode` now selects an explicit reference target aspect (`rect_centered_1.0` or `rect_centered_4.0`) distinct from the fleet's initial spawned aspect ratio
    - `runtime.movement.v4a.reference.surface_mode` remains the current v4a-internal reference-surface seam; it is still candidate-specific rather than a general movement owner
    - `runtime.movement.v4a.reference.soft_morphology_relaxation` controls fleet-level morphology relaxation for the bounded soft-morphology carrier
    - `runtime.movement.v4a.transition.shape_vs_advance_strength` controls how strongly large morphology error suppresses pure objective advance in favor of ongoing shape transition
    - `runtime.movement.v4a.transition.heading_relaxation` controls the minimal fleet-level heading realization seam used by the transition carrier
    - `runtime.movement.v4a.battle.standoff_hold_band_ratio` defines the near-`d*` no-chase band used by the bounded battle standoff carrier
    - `runtime.movement.v4a.battle.target_front_strip_gap_bias` is the single active correction bias on the base front-strip target gap; current base read is `max(0, fire_optimal_range - expected_reference_spacing)`, where `fire_optimal_range = attack_range * fire_optimal_range_ratio`; it replaces the older two-weight extent buffer interface on the current local line
    - `runtime.movement.v4a.battle.hold_weight_strength` defines how strongly the bounded near-`d*` hold state suppresses approach authority; the read is reversible, so if fleets are separated again, pre-contact-like approach can resume
    - `runtime.movement.v4a.battle.relation_lead_ticks` defines the near-contact lead window in ticks for signed battle-relation slowdown
    - `runtime.movement.v4a.battle.hold_relaxation` defines the restored raw-to-current smoothing weight for the signed near-contact relation family (`battle_relation_gap`, `close_drive`, `brake_drive`, `hold_weight`)
    - `runtime.movement.v4a.battle.approach_drive_relaxation` defines the restored raw-to-current smoothing weight for forward approach authority as a separate seam from hold/brake state
    - `runtime.movement.v4a.battle.near_contact_internal_stability_blend` defines the restored near-contact internal-speed unification blend that pulls unit-local speed factors back toward fleet-level behavior while hold is active
    - `runtime.movement.v4a.battle.near_contact_speed_relaxation` defines the restored per-unit max-speed smoothing seam used after near-contact internal stabilization adjusts unit-local speed targets
    - `runtime.movement.v4a.engagement.engaged_speed_scale` defines the overall movement-speed reduction for engaged units
    - `runtime.movement.v4a.engagement.attack_speed_lateral_scale` and `runtime.movement.v4a.engagement.attack_speed_backward_scale` define the bounded attack-direction-aware movement allowance for engaged units
    - active default `test_run` settings no longer carry the legacy `runtime.movement.v3a.experiment`, `centroid_probe_scale`, or `odw_posture_bias.*` surface
    - the maintained `test_run` mainline no longer supports `v3a` movement execution, and the public `baseline` alias has been retired; the maintained selector is now `v4a` only
    - `run_control.symmetric_movement_sync_enabled` is now the maintained owner for the harness-side symmetric movement merge switch

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
