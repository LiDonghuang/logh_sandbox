# Engine Skeleton Active Surface Report

Status: Round 2 delivery  
Scope: `runtime/engine_skeleton.py` only  
Date: 2026-03-21

## Active Runtime Surface

The following remain active runtime knobs on `EngineTickSkeleton` and are still read directly in maintained runtime flow:

- `attack_range`
- `damage_per_tick`
- `separation_radius`
- `CH_ENABLED`
- `contact_hysteresis_h`
- `fire_quality_alpha`
- `FSR_ENABLED`
- `BOUNDARY_SOFT_ENABLED`
- `BOUNDARY_HARD_ENABLED`
- `boundary_soft_strength`
- `alpha_sep`
- `fsr_strength`
- `fsr_lambda_delta`
- `COHESION_DECISION_SOURCE`
- `MOVEMENT_MODEL`
- `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`
- `ODW_POSTURE_BIAS_ENABLED`
- `ODW_POSTURE_BIAS_K`
- `ODW_POSTURE_BIAS_CLIP_DELTA`

These remain top-level attributes because they are true maintained runtime controls, not legacy compatibility padding.

## Active Debug Surface

The following remain active debug/diagnostic knobs:

- `debug_contact_assert`
- `debug_contact_sample_ticks`
- `debug_fsr_diag_enabled`
- `debug_outlier_eta`
- `debug_outlier_persistence_ticks`
- `debug_diag4_enabled`
- `debug_diag4_topk`
- `debug_diag4_contact_window`
- `debug_diag4_return_sector_deg`
- `debug_diag4_neighbor_k`
- `debug_diag4_rpg_enabled`
- `debug_diag4_rpg_window`
- `debug_cohesion_v1_enabled`
- `debug_cohesion_v3_shadow_enabled`

The following remain active top-level debug outputs because maintained `test_run` diagnostics still consume them:

- `debug_last_combat_stats`
- `debug_diag_last_tick`
- `debug_last_cohesion_v3`
- `debug_last_cohesion_v3_components`
- `debug_diag_timeseries`

## Internal Debug State

Round 2 moved internal, non-maintained debug caches into a single internal host:

- `self._debug_state`

This now holds internal-only state such as:

- previous cohesion-v1 cache
- diag4 contact history
- boundary-force accumulation
- outlier streak state
- v1/v2 cohesion debug caches
- FSR debug snapshot

This reduces top-level flat surface without hiding maintained runtime knobs behind a mega-config object.

## Retired / Deleted From Top-Level Surface

The following are no longer initialized or maintained as top-level members:

- `_debug_outlier_streaks`
- `_debug_diag4_contact_history`
- `_debug_diag4_prev_unit_state`
- `_debug_diag4_prev_unit_radius`
- `_debug_diag4_transition_counts`
- `_debug_diag4_first_outlier_tick`
- `_debug_diag4_return_attempt_count`
- `_debug_diag4_outlier_return_count`
- `_debug_diag4_outlier_duration`
- `_debug_diag4_max_outlier_duration`
- `_debug_diag4_disp_history`
- `_debug_diag4_persistent_records`
- `_debug_diag4_outlier_streaks`
- `_debug_diag4_rpg_outlier_entry`
- `_debug_diag4_rpg_return_stats`
- `_debug_boundary_force_events_total`
- `_debug_prev_cohesion_v1`
- `debug_last_cohesion_v1`
- `debug_last_cohesion_v2`
- `debug_last_cohesion_v2_components`
- `debug_last_fsr_stats`

These were not active maintained runtime knobs. They were internal diagnostics or historical debug state and are now treated as internal-only state.
