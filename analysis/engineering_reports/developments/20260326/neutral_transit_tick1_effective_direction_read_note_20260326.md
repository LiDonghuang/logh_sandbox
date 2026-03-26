# Neutral Transit Tick-1 Effective Direction Read Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: analysis / readout note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: uses 3D viewer step observation to classify an existing 2D neutral-transit heading/display phenomenon
Mapping Impact: none
Governance Impact: records a newly visible readout about the existing neutral-transit path without opening a new implementation turn
Backward Compatible: yes

Summary
- Human step inspection in the 3D viewer exposed a tick-1 heading pattern that was not easy to notice in the 2D animation path.
- This does not read as a new 3D bug.
- In the bounded `neutral_transit_v1` path, `composite` currently degenerates to `effective` because there are no enemies and therefore no attack vectors.
- At tick `1`, the viewer-side `effective` read is not yet frame-to-frame displacement; it falls back to the captured runtime `orientation_vector`.
- That tick-1 orientation field is already strongly geometric, deterministic, and left-right symmetric.
- The later apparent "flattening toward the objective point" is consistent with the existing fixture target path and does not require a new 3D explanation.
- The slight post-flatten shape bias remains best classified as the existing `R1` front-profile residual debt.

## Question

What does the newly visible tick-1 `effective` direction posture suggest about the bounded `neutral_transit_v1` path?

## Key Reading

For the bounded neutral-transit fixture:

- layered `vector_display_mode` is currently `composite`
- there are no enemies
- replay frames contain no attack targets

So in practice:

- `composite -> effective`

for this path.

## Why Tick 1 Is Special

The viewer-side `effective` direction logic uses:

- frame-to-frame displacement when a previous position exists
- otherwise the captured heading/orientation payload already present in the frame

At tick `1`, there is no previous frame inside the viewer replay bundle.
So the visible tick-1 `effective` direction is actually the runtime-owned `orientation_vector` captured from the first simulated tick.

That means tick-1 is not a noisy "what happened between frame 0 and frame 1" estimate.
It is a direct readout of the runtime-facing initial movement/orientation field after the first step.

## Observed Pattern

Bounded readout from the current fixture replay shows:

- `tick = 1`
- `dir_mode = composite`
- `nonempty_targets = 0`

and the unit headings at tick `1` are already highly structured.

When read in the fleet-local frame defined by:

- centroid -> objective as the primary axis
- its perpendicular as the lateral axis

the tick-1 headings show:

- strong positive parallel component toward the objective
- mirrored positive / negative lateral components on opposite sides
- deterministic left-right symmetry rather than random angular noise

Example samples from the current readout:

- several flank/near-flank units read approximately `hpar=0.857`, `hlat=+/-0.514`
- several more central lanes read approximately `hpar=1.000`, `hlat=0.000`

This is best read as:

- a structured symmetric initial heading field
- not a viewer artifact
- not a newly introduced 3D-only mechanism

## Current Interpretation

The most useful bounded interpretation is:

1. The tick-1 pose makes a previously under-observed fact visible:
   the neutral-transit path begins from a deterministic, geometry-shaped heading field rather than from a visually uniform "all arrows already perfectly objective-facing" state.
2. That first-field geometry is consistent with the current fixture path:
   a common fleet objective direction plus structured local correction / restoration effects.
3. The later visual impression that headings become "flattened" toward the objective point is also expected:
   as the transit converges, the lateral part of the initial heading field becomes less visually dominant and the common objective-facing component wins out.
4. The final slight shape bias should still be read through the existing `R1` classification, not as a new 3D issue.

## Relationship to Existing Residual Classification

This note does not replace the existing residual reading.

The current stable shape bias after convergence is still best anchored by:

- `analysis/engineering_reports/developments/20260325/r1_front_profile_residual_note_20260325.md`

That record already classifies the remaining issue as:

- stable
- deterministic
- low-amplitude
- non-oscillatory in the observed window

The new point here is narrower:

- 3D step inspection reveals that the very early heading field is itself structured and symmetric
- this early readout helps explain why humans now notice an initial "restless" or "alive" posture before later visual flattening

## Bottom Line

The new tick-1 observation is worth recording because it sharpens the reading of the existing neutral-transit path:

- early heading presentation is not arbitrary jitter
- it is a deterministic symmetric initial heading field
- later objective-facing flattening is consistent with the current fixture target/restore path
- residual shape bias after convergence remains the old `R1` debt, not a new 3D regression
