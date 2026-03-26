# Step 3 3D Objective Fixture Readout Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: fixture telemetry / launcher readout only
Affected Parameters: `observer_telemetry['fixture']` and concise fixture summary text
New Variables Introduced: fixture readout fields `anchor_point_xyz`, `projected_anchor_point_xy`, `source_owner`, `objective_mode`, `no_enemy_semantics`
Cross-Dimension Coupling: readout only; no semantic ownership moved to viewer
Mapping Impact: none beyond explicit contract echo/readout
Governance Impact: records the minimum readout surface used by the first implementation
Backward Compatible: yes

Summary
- The fixture telemetry now echoes the minimum 3D objective contract fields explicitly.
- Launcher summary now prints one concise contract line in addition to the existing fixture line.
- The readout remains harness-side only.
- No viewer or replay ownership was added.

## Telemetry Fields Added

The fixture telemetry now includes:

- `anchor_point_xyz`
- `projected_anchor_point_xy`
- `source_owner`
- `objective_mode`
- `no_enemy_semantics`

Existing fixture metrics such as:

- `objective_point_xy`
- `objective_reached_tick`
- `centroid_to_objective_distance`

remain in place.

## Launcher Summary Addition

`_run_neutral_transit_fixture(...)` now emits one extra concise summary line:

- contract anchor xyz
- projected anchor xy
- source owner
- objective mode
- no-enemy semantics
- fixture fleet id

This is the minimum human-readable proof surface requested by the validation note.
