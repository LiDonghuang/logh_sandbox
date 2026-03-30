# Step 3 3D PR #6 Hold-Await + Transport + Softening Local Note

Status: local engineering note only  
Scope: `test_run/` bounded candidate line only  
Layer read: harness/test-only carrier evolution for PR `#6`  
Runtime core impact: none

## Purpose

Record the next bounded local correction after the Governance-approved read that:

- band ownership had become too explicit / too active
- neutral arrival lacked true hold-await semantics
- the carrier still needed softer formation-reference ownership

This note records one local implementation step that:

1. removes extent-coupled early hold triggering
2. makes neutral hold-await truly objective-non-chasing
3. replaces `unit_id`-driven initial-to-reference transport with band/local-position-driven soft transport
4. weakens within-band exact residual authority

## Files changed locally

- `test_run/test_run_execution.py`

## Main local changes

### A. Hold-await trigger narrowing

Removed the late-phase hold trigger that scaled with morphology extent.

Current local read:

- hold now latches only on the explicit objective stop-radius path
- morphology hold no longer activates early just because the reference envelope is wide

### B. Initial-to-reference transport correction

Replaced the old `unit_id` / row-major reference transport read with:

- stable band identity from actual initial offsets
- anonymous reference lattice for target morphology bands
- soft within-band placement driven by initial local phase, not exact target-slot ownership

### C. Within-band residual softening

The carrier now uses per-unit initial band phase (`[-1, 1]`) rather than exact per-unit target residual.

Current local read:

- units aim for soft band-relative placement
- not exact point reoccupation under a renamed mechanism

## Focused local validation

Neutral-transit matched/mismatched aspect-reference checks were rerun locally for:

- initial `1.0` -> reference `1.0`
- initial `4.0` -> reference `4.0`
- initial `1.0` -> reference `4.0`
- initial `4.0` -> reference `1.0`

Observed local summary:

- `1.0 -> 1.0`
  - objective arrival restored
  - no premature stop
  - `final RMS ~= 0.061`
- `4.0 -> 4.0`
  - objective arrival restored
  - no premature stop
  - `final RMS ~= 0.029`
- `1.0 -> 4.0`
  - no premature stop
  - clear mismatch evolution remains visible
  - `final front extent ~= 1.50`
- `4.0 -> 1.0`
  - no premature stop
  - mismatch evolution remains visible
  - `final front extent ~= 0.88`

## Honest local read

This step appears to fix two structural bugs from the prior local carrier:

1. wide-reference cases no longer stop early outside the stop-radius
2. initial/reference mismatch is no longer primarily expressed as a rigid `unit_id`-mapped transport artifact

But this does **not** mean the carrier is finished.

Remaining likely issues:

- matched cases still read very tight / very clean
- mismatch evolution is now less artificial, but may still need softer shared morphology behavior
- more human visual review is still required before reporting this as the next settled read

## Boundary

This note is local only.

It is **not**:

- a Governance report
- a merge recommendation
- a baseline replacement claim
- a runtime-core change record
