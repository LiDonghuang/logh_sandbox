# step3_3d_pr6_fleet_body_summary_phase1_residue_audit_record_20260410

## Scope

- baseline/runtime: viewer-side cleanup audit
- test-only or harness-only: cross-layer (`test_run` export + `viz3d_panda` consumer)
- protocol or policy only: no

## Audit target

Phase 1 of the maintained `fleet_body_summary` contract was already landed.

This round audited viewer-side residue to answer:

- whether any viewer consumer still recomputes maintained fleet-body geometry
- whether any remaining exception should be treated as a second owner

## Files audited

- `viz3d_panda/replay_source.py`
- `viz3d_panda/camera_controller.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/app.py`

## Result

### Maintained consumer cutover is complete

The following viewer-facing maintained reads are already routed through
`ViewerFrame.fleet_body_summary`:

- camera focus / fleet view
- HUD fleet centroid readout
- HUD fleet centroid speed readout
- replay radial-debug centroid source
- fleet halo baseline
- fleet halo normal placement

### Interpolation now also stays on the maintained export

`viz3d_panda/unit_renderer.py`

- `_sync_fleet_halos(...)`

Halo interpolation no longer recomputes centroid from live node positions.
It now blends current-frame and next-frame `fleet_body_summary` rows directly.

This removes the last viewer-side geometry exception from Phase 1.

### Summary-derived presentation surface remains acceptable

`App._sync_fleet_avatar_overlays()` still consumes `fleet_halo_state`, but that
state is derived from the maintained export and used only for presentation
placement. It is not a second maintained geometry owner.

## Not done in this round

- no harness/runtime internal centroid/radius unification
- no runtime mechanism-local geometry reroot
- no expansion of the contract fields

Those remain Phase 2 topics.

## Conclusion

Phase 1 is stable and fully cut over on the viewer side.

No further viewer-side maintained geometry cutover is required right now.

