# Neutral Transit Second Bounded Corrections Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: bounded `neutral_transit_v1` mechanism only
Affected Parameters: none exposed; internal use of existing `stop_radius`, `separation_radius`, `unit.max_speed`, and `dt`
New Variables Introduced: internal-only `gain_no_overshoot`, `target_gate`
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: implements the authorized second bounded neutral-transit correction turn only
Backward Compatible: yes, outside `neutral_transit_v1`

Summary
- This turn stays inside the bounded `neutral_transit_v1` carrier only.
- No new user parameters or settings surfaces were added.
- Governance correction froze the late side at the already active A1 behavior.
- This turn therefore implements only early-side E2 on top of the existing B1 deadband.
- No latch, no fallback, no generalized framework growth was introduced.
- Validation shows that E2, by itself, regresses formation geometry and arrival timing materially.
- The honest reading is still below the human-visible threshold.

## Scope

After the immediate Governance correction, this turn implements only:

1. late side frozen at current A1
2. early-side E2 on the fixture expected-position / common forward path

Nothing else was expanded.

## Late Side

Late-side behavior remains at the already active A1-only state:

- `target_direction = normalized_direction_to_objective * gain_arrival`
- `gain_arrival = clamp(d / stop_radius, 0, 1)` when `stop_radius > 0`

No second gate, no speed-derived quantity, and no helper family were kept.

## Early E2

Touchpoint:

- `runtime/engine_skeleton.py`
- `integrate_movement(...)`

Implementation:

- Keep existing B1:
  - `restore_deadband = 0.28 * separation_radius`
- Add slot-error-aware attenuation:
  - `slot_error_excess = max(0, cohesion_norm - restore_deadband)`
  - `target_gate = clamp(1 - slot_error_excess / separation_radius, 0, 1)`
- Apply `target_gate` only to the common forward / target term

This turn does not:

- scale separation
- scale boundary
- add a second deadband
- add a smooth family
- add a slot-priority registry

## Readout Surface

This turn does not add new late-side telemetry surfaces.

Validation continues to use the existing bounded fixture metrics:

- `objective_reached_tick`
- `centroid_to_objective_distance`
- `formation_rms_radius_ratio`
- `front_extent_ratio`
