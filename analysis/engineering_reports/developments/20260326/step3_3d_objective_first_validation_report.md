# Step 3 3D Objective First Validation Report (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: harness-side validation report only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: validates the new 3D contract carrier through the bounded neutral-transit fixture only
Mapping Impact: validation only
Governance Impact: confirms the first very small implementation meets the approved harness-side validation path
Backward Compatible: yes

Summary
- Validation used one bounded `neutral_transit_v1` run only.
- Validation stayed harness-side only and did not require viewer or replay-protocol changes.
- Required readout fields were present in `observer_telemetry['fixture']`.
- The fleet still trended toward the anchor and reached the stop condition.
- No evidence appeared of formation / legality / combat growth inside the carrier.

## Validation Shape

Validation path:

- one `neutral_transit_v1` run
- single fleet
- no enemy
- no viewer
- no replay protocol requirement

Validation surface:

- `test_run_entry.run_active_surface(...)`
- `observer_telemetry['fixture']`
- concise launcher summary from `_run_neutral_transit_fixture(...)`

## Readout Observed

Observed telemetry readout:

- `anchor_point_xyz = [350.0, 350.0, 0.0]`
- `projected_anchor_point_xy = [350.0, 350.0]`
- `source_owner = fixture`
- `objective_mode = point_anchor`
- `no_enemy_semantics = enemy_term_zero`
- `fleet_id = A`
- `objective_reached_tick = 426`
- `initial_centroid_to_objective_distance = 424.264`
- `final centroid_to_objective_distance = 0.763`
- `minimum centroid_to_objective_distance = 0.185`

Observed launcher summary surface:

- `[fixture] mode=neutral_transit_v1 movement=v4a arrival_tick=426 final_tick=436 objective=(350.00,350.00) stop_radius=2.00`
- `[fixture] objective_contract_3d anchor_xyz=(350.00,350.00,0.00) projected_xy=(350.00,350.00) owner=fixture mode=point_anchor no_enemy=enemy_term_zero fleet_id=A`

## Success Check

This validation is accepted as successful because:

1. the first carrier is explicitly present on the bounded fixture path
2. the required contract fields are read back explicitly
3. the fleet still trends toward the target and reaches the stop condition
4. viewer involvement was not required
5. no new settings surface was introduced
6. no new formation / legality / combat semantics appeared in the carrier

## Scope-Creep Check

No red-flag behavior was observed for:

- `transit_axis_hint_xyz`
- frame / spacing / extents growth
- legality / feasibility fields
- combat intent or doctrine growth
- viewer-owned fallback semantics
- runtime schema widening

## Repro Surface

Minimal reproduction used:

- `scenario.prepare_neutral_transit_fixture(...)`
- `test_run_entry.run_active_surface(...)`

with harness-side overrides that kept:

- `capture_positions = False`
- `include_target_lines = False`
- `print_tick_summary = False`
- `plot_diagnostics_enabled = False`
- `animate = False`
