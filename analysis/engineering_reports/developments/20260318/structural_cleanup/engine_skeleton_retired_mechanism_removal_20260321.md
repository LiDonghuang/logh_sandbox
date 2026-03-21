# Engine Skeleton Retired Mechanism Removal Report

Status: Round 2 delivery  
Scope: `runtime/engine_skeleton.py` only  
Date: 2026-03-21

## Removed

The following retired compatibility paths were deleted from `integrate_movement(...)`:

- movement experiment alias remap:
  - `exp_a_reduced_centroid -> exp_precontact_centroid_probe`
- legacy probe fallback:
  - `PRECONTACT_CENTROID_PROBE_SCALE`

These were retained only to extend historical naming/parameter debt. Maintained runtime now reads only:

- `MOVEMENT_V3A_EXPERIMENT`
- `CENTROID_PROBE_SCALE`

## Removed Local Duplication

The following duplicated local utility burden was removed:

- duplicated per-fleet numeric-rank parsing in movement projection
- duplicated `fleet_local_numeric_index(...)` local function in combat

They now use one same-file helper:

- `EngineTickSkeleton._fleet_local_numeric_index(...)`

This is a single-source-of-truth consolidation, not helper proliferation.

## Kept Intentionally

The following were not removed in Round 2:

- `MOVEMENT_MODEL == "v1"` path
- `COHESION_DECISION_SOURCE == "v1_debug"` path

Reason:

- current repo comments/settings still treat these as reference/debug-valid surfaces rather than formally retired compatibility residue
- deleting them in this round would risk silent semantic drift beyond the approved gate

## Not Removed Because Status Is Still Live or Canonically Relevant

The following top-level outputs remain because maintained diagnostics still read them:

- `debug_last_combat_stats`
- `debug_diag_last_tick`
- `debug_last_cohesion_v3`
- `debug_last_cohesion_v3_components`

These were not treated as retired.

## Round 2 Removal Boundary

Round 2 removed:

- retired alias compatibility
- retired fallback compatibility
- dead local utility duplication
- top-level internal debug-state sprawl

Round 2 did not remove:

- active runtime knobs
- maintained diagnostics outputs
- debug/reference paths whose canonical retirement status is not explicit
