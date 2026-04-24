# PR9 Phase II - Reader-Facing Stale-Surface Cleanup Record

Date: 2026-04-23  
Scope: VIZ reader-facing stale indicator cleanup only  
Status: completed

## 1. Exact Stale Reader-Facing Surfaces Replaced

Touched files:

- `viz3d_panda/app.py`
- `viz3d_panda/docs/3D_VIZ_Debug_Block_Reference_v1.0.md`

Replaced stale surface:

- old VIZ HUD/source read:
  - `relation_violation_severity`
  - displayed as `viol=...`
- new VIZ HUD/source read:
  - `late_reopen_persistence`
  - displayed as `reopen=...`

Replaced stale documentation:

- the Debug Block Reference no longer describes `viol` /
  `relation_violation_severity` as the current maneuver-envelope focus
  indicator
- it now describes `reopen` / `late_reopen_persistence` as the current late
  reopen-space persistence indicator
- the summary table now lists `late_reopen_persistence` as the shown
  maneuver-envelope indicator instead of `relation_violation_severity`

Historical engineering reports were not back-edited. They remain records of
their own earlier stage.

## 2. Current Reader-Facing Indicator Set

The current VIZ `focus <fleet_id>+` row now shows:

- `raw_gap`
  - source: `relation_gap_raw`
- `embg`
  - source: `early_embargo_permission`
- `reopen`
  - source: `late_reopen_persistence`
- `brk`
  - source: `brake_drive`

The local maneuver debug pair shown to Human is now:

- `early_embargo_permission`
- `late_reopen_persistence`

No new indicator was added. This was a stale-field replacement only.

## 3. Runtime / Behavior Confirmation

No runtime files were modified in this cleanup.

No behavior-bearing logic changed:

- no target ownership change
- no local maneuver / back-off formula change
- no locomotion change
- no retreat behavior
- no settings-surface migration
- no new debug catalog

Validation:

```powershell
python -m py_compile viz3d_panda\app.py
rg -n "relation_violation_severity|viol=" viz3d_panda -S
```

The stale VIZ references are gone from `viz3d_panda`.

## 4. Human-Read Reduction

This cleanup reduces misreading in the current behavior line because Human no
longer sees `viol` as if it were the active current local maneuver indicator.

The displayed battle read now matches the current runtime/test_run export:

- `embg` answers whether early local peel-out is still constrained
- `reopen` answers whether the late reopen-space persistence band is active

This keeps the viewer aligned with the accepted post-cleanup structural anchor
without reopening runtime-side subtraction.
