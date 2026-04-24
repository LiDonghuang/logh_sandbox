# PR9 Phase II Unit Desire Bridge Proposal Governance Acceptance Sync Note 20260419

Status: sync note only
Date: 2026-04-19
Scope: repo-side engineering sync for latest governance judgment
Authority: engineering-side record only; no runtime implementation is authorized by this note

## Repo-Relative Accepted Baseline

Current approved document baseline for the next seam:

- `analysis/engineering_reports/developments/20260419/pr9_phase2_unit_desire_bridge_bounded_implementation_slice_proposal_20260419.md`

Governance judgment on that proposal:

- `ACCEPT-WITH-NOTE`
- accepted as the correct next document-first step
- not broad authorization to open a third runtime slice automatically

## Current Owner/Path Read

Current accepted next-seam read remains:

- same-tick per-unit desire generation
- pre-movement
- runtime-local
- tick-local
- non-persistent

Current accepted minimal carrier read remains:

- `desired_heading_xy`
- `desired_speed_scale`

Current active owner/path tension this proposal addresses:

- locomotion input ownership inside `runtime/engine_skeleton.py`
- specifically the gap between accepted upstream unit intent and current mixed locomotion input assembly

Minimal active-path evidence:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1898) computes upstream same-tick unit target intent
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2869) still feeds `target_term_x / target_term_y` from `movement_direction`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2903) still derives `desired_heading_hat` from the mixed realization vector

## What Did Not Change

This sync note does not change:

- runtime code
- baseline files
- `BattleState` schema
- test harness ownership
- governance documents

No paired baseline review was needed because this note makes no runtime behavior change.

## Acceptance Notes To Carry Forward

The following remain explicitly carried constraints:

- do not widen the next slice into a full locomotion-family rewrite
- do not collapse pre-movement desire and post-movement combat target ownership into one undocumented owner
- do not let the desire seam silently grow into a mode system or combat-adaptation doctrine

Still not authorized:

- mode introduction
- retreat activation
- persistent target memory
- broad locomotion redesign
- schema-heavy expansion by default
- harness-owned doctrine growth

## Required Next Gate Before Any Third Slice

If engineering later wants to open a third bounded implementation slice, it should first return with a very short implementation-ready confirmation that states:

1. the exact owner/path being changed
2. what still does not change
3. that the slice remains strictly smaller than a combat-adaptation or locomotion-rewrite wave

## Bottom Line

The unit desire bridge proposal is now the current approved document baseline for the next seam.

Engineering should treat it as:

- accepted proposal
- narrow continuation anchor
- not automatic authorization for implementation
