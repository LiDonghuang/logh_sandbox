# Major Change Record

Date: 2026-03-12
Status: Active independent record
Purpose: Record major mechanism/protocol/interface changes without rewriting historical `analysis`.

## Recording principle

This document records major items that materially changed:

- active mechanism availability
- default experiment protocol or geometry baseline
- runtime/observer interpretation boundary
- public `test_run` configuration interface
- formal retirement / freeze / deprecation status of a mechanism or parameter path

Historical `analysis` remains unchanged and should be read in its original mechanism context.

## Item 1 - Dormant ODW combat residual removed

Date: 2026-03-11
Scope: Baseline runtime
Status: Implemented

Summary:
- The old dormant `ODW` combat bias residual was removed from `runtime/engine_skeleton.py`.
- This was cleanup of a legacy path, not activation of a new mechanism.

Effect boundary:
- Runtime combat path only
- Not a new `ODW` redesign

## Item 2 - FR bounded-correction thread closed without promotable candidate

Date: 2026-03-12
Scope: Engineering conclusion / experimental line
Status: Concluded

Summary:
- The bounded `FR` correction search produced no promotable continuous candidate in the independent single-seed round-1 screen.
- This does not invalidate the `FR authority audit`.
- It invalidates the tested correction family.

Effect boundary:
- No baseline runtime change
- No canonical semantics change

## Item 3 - Discrete FR correction probes retired

Date: 2026-03-12
Scope: `test_run` harness only
Status: Implemented

Summary:
- The discrete personality-conditioned `FR` correction probes were removed from `test_run`.
- They remain diagnostic history, not active candidate mechanisms.

Effect boundary:
- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0.settings.json`
- No frozen runtime edit

## Item 4 - Current experimental policy: ODW and MB held at neutral 5 in the main experimental axis

Date: 2026-03-12
Scope: Experimental policy
Status: Active policy

Summary:
- For the current main experiment line, `ODW` and `MB` are treated as held-at-neutral (`5`) rather than active primary DOE axes.
- This is intended to reduce direct movement-layer crowding while `FR`/symmetry issues are still being resolved.

Effect boundary:
- Experimental policy only
- Not a runtime deletion
- Not a canonical redefinition

## Item 5 - Initial formation interface migrated to side-specific A/B fields

Date: 2026-03-12
Scope: `test_run` public configuration interface
Status: Implemented

Summary:
- Initial formation setup now uses side-specific fields for:
  - unit count
  - aspect ratio
  - origin
  - facing angle

Active keys:
- `initial_fleet_a_size`
- `initial_fleet_b_size`
- `initial_fleet_a_aspect_ratio`
- `initial_fleet_b_aspect_ratio`
- `initial_fleet_a_origin_xy`
- `initial_fleet_b_origin_xy`
- `initial_fleet_a_facing_angle_deg`
- `initial_fleet_b_facing_angle_deg`

Effect boundary:
- `test_run` only

## Item 6 - Legacy shared formation keys removed from `test_run`

Date: 2026-03-12
Scope: `test_run` interface cleanup
Status: Implemented

Removed from active `test_run` interface:
- `initial_fleet_size`
- `initial_fleet_aspect_ratio`

Summary:
- These shared keys were removed from `test_run` because side-specific geometry is now the only supported active interface there.
- Old `analysis` scripts and archived settings were intentionally not rewritten.

Effect boundary:
- `test_run/test_run_v1_0.py`
- `test_run/test_run_v1_0.settings.json`
- Historical `analysis` remains unchanged by design

## Item 7 - Initial formation center-anchor semantics corrected

Date: 2026-03-12
Scope: `test_run` initialization geometry
Status: Implemented

Summary:
- `origin_xy` now means the center anchor of the full initial formation, not the rear-row center.
- Each row is centered by its actual row size, including the final partial row.
- Formation depth is also centered, so changing `aspect_ratio` no longer translates the whole formation along the facing axis.

Effect boundary:
- `test_run` only

## Item 8 - Default `test_run` geometry baseline reaffirmed

Date: 2026-03-12
Scope: Default test protocol
Status: Active default

Summary:
- Default geometry baseline remains:
  - square arena
  - mirrored diagonal deployment
  - opposing diagonal approach

This remains the preferred default baseline for future DOE unless a run explicitly needs a different opening geometry.

Effect boundary:
- Default `test_run` settings/protocol
- Not a frozen runtime rule

## Item 9 - Observer symmetry corrections for mirrored opposing fleets

Date: 2026-03-12
Scope: `test_run` observer layer
Status: Implemented

Summary:
- Observer geometry metrics were corrected to use fleet-local enemy-facing axes instead of a single global A->B axis.
- This materially changed the interpretation boundary for:
  - `FrontCurv`
  - `C_W_SPhere`
  - `posture_persistence_time`

Effect boundary:
- `test_run` observer only
- Not a runtime movement change

## Item 10 - Harness-side symmetric movement sync added

Date: 2026-03-12
Scope: `test_run` harness diagnostic path
Status: Implemented

Summary:
- A test-only harness-side `symmetric_movement_sync_enabled` path was added to reduce cross-fleet sequential-update bias without editing the frozen engine skeleton.

Effect boundary:
- `test_run` harness only
- Diagnostic / mitigation only
- Not a baseline runtime replacement

## Item 11 - Neutral mirrored close-contact asymmetry is now a low-level diagnostic gate

Date: 2026-03-12
Scope: Engineering diagnostic protocol
Status: Active diagnostic principle

Summary:
- A mirrored, close-contact, all-5-vs-all-5 setup is now treated as a low-level symmetry diagnostic window.
- If strong asymmetry appears there, it should be treated as a low-level blocker first, not as personality-mechanism evidence.

Effect boundary:
- Engineering diagnostic protocol only
- Not a canonical semantics change

