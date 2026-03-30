# Step 3 3D PR #6 Morph-Axis / Hold / Soft-Band Local Note (2026-03-30)

Status: local engineering note  
Scope: `test_run/` bounded candidate follow-up only  
Layer read: test-only / local validation only  
Frozen-layer impact: none

## Purpose

This local note records the first implementation follow-up after Governance accepted the next carrier read for PR `#6`:

- independent morphology-axis ownership
- formation hold / latch semantics
- softer band actuation while preserving band equality

This note is local-only for now and is not yet a Governance push report.

## Files Touched

- `test_run/test_run_execution.py`

No settings-surface expansion was introduced in this iteration.

## Implemented Carrier Changes

### 1. Independent morphology axis

The reference surface no longer directly reuses the raw current target direction as its immediate reference axis.

Instead, the carrier now keeps:

- `morphology_axis_current_xy`

and updates it through a weak bounded relaxation toward the desired direction.

Current default seam:

- `V4A_MORPHOLOGY_AXIS_RELAXATION_DEFAULT = 0.12`

This remains internal to the carrier in this iteration.

### 2. Formation hold / latch

The carrier now supports morphology-level hold/latch state in the bundle:

- `formation_hold_active`
- `formation_hold_axis_xy`
- `formation_hold_forward_extent`
- `formation_hold_lateral_extent`
- held band-anchor / half-span / ordering state

Current trigger in this local first cut:

- neutral-transit fixture path only
- objective-distance bounded by:
  - `stop_radius`
  - or a small morphology-envelope-aware trigger distance

The latch is morphology-level, not exact-position freeze.

### 3. Softer band actuation

The current `front/mid/rear + left/center/right` band read was kept.

What changed is the actuation style:

- shared morphology lattice remains
- band equality remains
- per-band hard recenter/rescale dominance was reduced
- within-band placement now uses softer residual shaping
- hold state also latches broad within-band ordering, rather than letting hold-phase band order drift every tick

## Current Local Read

### What improved clearly

For `neutral_transit_v1`, `aspect_ratio = 1.0`:

- early lateral disturbance dropped sharply
- post-arrival three-cluster collapse effectively disappeared
- final shape metrics stayed close to target

Observed local numbers:

- early lateral motion:
  - left `~0.00058`
  - center `~0.00116`
  - right `~0.00298`
- post-arrival lateral motion:
  - all three lateral bands `~6e-07`
- final metrics:
  - `expected_position_rms_error ~0.100`
  - `front_extent_ratio ~1.001`
  - `formation_rms_radius_ratio ~1.001`

Compared with the previously accepted problematic read, this is a major improvement for the `1.0` neutral case.

### What remains incomplete

For `neutral_transit_v1`, `aspect_ratio = 4.0`:

- early lateral disturbance also dropped strongly
- but post-arrival collapse is not yet cleanly solved

Observed local numbers:

- early lateral motion:
  - left `~0.00025`
  - center `~0.00037`
  - right `~0.00078`
- post-arrival lateral motion still high:
  - roughly `~0.43 - 0.52`
- final metrics remain materially off:
  - `expected_position_rms_error ~1.416`
  - `front_extent_ratio ~1.499`
  - `formation_rms_radius_ratio ~0.678`

So the hold/latch seam clearly helped, but the wide rectangular neutral case still retains a late-phase failure mode.

### Battle-side local read

Battle remained on the same PR `#6` line and still sees the carrier.

On the local matched runs used here:

- battle early lateral motion stayed around `~0.0024 - 0.0032`
- which is now higher than neutral's early lateral motion in both `1.0` and `4.0`

This means the current follow-up no longer reproduces the original specific complaint that neutral early-phase disturbance exceeds battle under matched aspect ratio.

However, this also means the current carrier may now be edging toward over-stabilizing neutral in the `1.0` case.

## Honest Engineering Read After This Iteration

This first follow-up appears directionally correct, but still incomplete.

More specifically:

1. independent morphology-axis ownership looks useful
2. hold/latch semantics are real and necessary
3. softer band actuation helped
4. but the first hold/latch cut is not yet robust across both:
   - square neutral
   - wide rectangular neutral

So the line should currently be read as:

- promising bounded correction
- not yet a settled carrier completion

## Recommended Next Local Focus

If the line continues, the most likely next bounded focus should be:

- improving hold/latch behavior for the wide rectangular neutral case

without:

- reopening restore-strength tuning as the main line
- rolling back band equality
- turning hostile-contact repair into the branch main objective

## Bottom Line

This iteration materially improved the accepted PR `#6` failure read for:

- independent morphology axis
- neutral hold/latch semantics
- softer band actuation

But it did not finish the job.

The `aspect_ratio = 1.0` neutral case now looks much healthier.
The `aspect_ratio = 4.0` neutral late-phase hold behavior still needs another bounded correction pass.
