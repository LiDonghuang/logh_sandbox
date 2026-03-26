# Step 3 3D Objective Viewer Consumption Hookup Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: `viz3d_panda/` viewer-consumption path only
Affected Parameters: viewer-local `--source` selection and viewer overlay readout only
New Variables Introduced: none in runtime; viewer source choices `auto`, `active_battle`, `neutral_transit_fixture`
Cross-Dimension Coupling: viewer now consumes the already-owned neutral-transit first carrier readout through replay metadata
Mapping Impact: none; no new replay protocol or semantic owner introduced
Governance Impact: fulfills the authorized "Very Small Viewer-Consumption Hookup Only" turn
Backward Compatible: yes

Summary
- `viz3d_panda/replay_source.py` now supports loading the bounded neutral-transit fixture path in addition to the active battle path.
- `viz3d_panda/app.py` now accepts a viewer-local `--source` selector.
- Default `--source auto` follows the current layered `fixture.active_mode` only for source selection.
- Viewer overlay now shows a very small read-only fixture contract echo when that readout already exists.
- No runtime schema widening, no new replay protocol, and no viewer-owned objective semantics were added.

## Scope

This turn only connects the existing Panda3D viewer to the already-implemented neutral-transit first carrier.

It does not:

- open 3D movement
- open 3D formation
- open 3D combat
- open 3D legality
- create an objective marker scene package
- create a new replay protocol
- move objective ownership into the viewer

## Code Touchpoints

Only the following files were touched:

- `viz3d_panda/replay_source.py`
- `viz3d_panda/app.py`

No `runtime/` files were modified.
No `test_run/` files were modified in this turn.

## Viewer Behavior

The viewer now supports three source modes:

- `auto`
- `active_battle`
- `neutral_transit_fixture`

`auto` is viewer-local convenience only. It checks the current layered `fixture.active_mode` and chooses:

- `neutral_transit_fixture` when the layered fixture mode is `neutral_transit_v1`
- otherwise `active_battle`

The viewer overlay may display the following already-owned fixture fields when present:

- `source_owner`
- `objective_mode`
- `no_enemy_semantics`
- `anchor_point_xyz`
- `projected_anchor_point_xy`

These are display-only echoes of existing runtime-owned results.

## Validation

Minimal validation completed:

- `python -m py_compile viz3d_panda/app.py viz3d_panda/replay_source.py`
- `load_viewer_replay(source='auto', frame_stride=8)`
- `load_viewer_replay(source='neutral_transit_fixture', frame_stride=8)`
- `load_viewer_replay(source='active_battle', frame_stride=12, max_steps=120)`
- `python -m viz3d_panda.app --help`

Observed results:

- `auto` resolved to `test_run_neutral_transit_fixture`
- explicit `neutral_transit_fixture` resolved to the same bounded fixture path
- fixture readout exposed `source_owner=fixture`, `objective_mode=point_anchor`, `no_enemy_semantics=enemy_term_zero`, `anchor_point_xyz=[350.0, 350.0, 0.0]`
- explicit `active_battle` still resolved to `test_run_active_surface`
