# PR #6 Far-Field Target Cleanup Local Note

Date: 2026-04-01  
Scope: test-only / harness-only local note  
Branch: `eng/two-layer-spacing-first-bounded-impl`

## Purpose

Record the first bounded implementation step after the 2026-04-01 design alignment note:

- clean Layer A far-field battle target for the current v4a carrier
- keep `d*`
- remove outdated local enemy semantics from v4a far-field battle target ownership
- do not implement Layer B / post-contact engagement geometry yet

## Local implementation read

Changed files:

- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.settings.comments.json`

Behavioral change:

- when a real v4a battle restore bundle exists for a fleet, far-field battle target no longer uses:
  - `nearest5_centroid`
  - `soft_local_weighted`
  - `soft_local_weighted_tight`
  - `weighted_local`
  - `local_cluster`
- instead, far-field battle target reads:
  - global enemy relation via enemy-fleet centroid
  - plus the already-opened bounded `d*` seam

Legacy/local substrate behavior is intentionally retained for older / non-v4a harness lines in this step.

## Assumptions

1. This step should stay minimal and should not silently widen into Layer B implementation.
2. The existing `d*` and unit-level attack-direction-aware speed envelope remain directionally correct and are not rolled back here.
3. A real v4a battle bundle is the honest local indicator that the current fleet is on the active bounded v4a battle carrier.

## Quick local read

Very small early-phase compare (`steps=120`, `capture_positions=true`) was run for:

- neutral `1 -> 4`
- battle `1 -> 4`
- neutral `2 -> 4`
- battle `2 -> 4`

Simple fleet-A lateral/forward extent ratio read:

- `1 -> 4`
  - tick 1: neutral `1.0381`, battle `1.0153`
  - tick 50: neutral `2.0582`, battle `1.7877`
  - tick 100: neutral `2.0585`, battle `2.3849`
- `2 -> 4`
  - tick 1: neutral `2.3670`, battle `2.3464`
  - tick 50: neutral `2.0000`, battle `2.7484`
  - tick 100: neutral `1.7660`, battle `2.2887`

## Current local conclusion

- The far-field cleanup appears directionally correct:
  - battle and neutral are now very close at tick 1 in both mismatch cases
- But the mismatch-critical divergence is not removed:
  - battle and neutral still separate materially by tick 50/100
  - `2 -> 4` remains especially unstable / non-honest

So the local read is:

- far-field local target contamination was a real issue and this cleanup was needed
- but far-field cleanup alone does not solve the main formation-transition problem
- the main remaining gap still reads as transition continuity / movement realization, not merely target substrate
