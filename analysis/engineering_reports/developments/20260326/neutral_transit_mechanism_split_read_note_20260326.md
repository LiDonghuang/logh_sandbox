# Neutral Transit Mechanism Split Read Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: analysis / mechanism read note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: uses viewer-exposed replay readout to separate two existing mechanism residual families
Mapping Impact: none
Governance Impact: recommends that the observed early and late neutral-transit issues be discussed as separate mechanism questions rather than viewer-only polish
Backward Compatible: yes

Summary
- The new viewer-side `realistic` readout did not create a new mechanism issue; it made two existing mechanism families easier to separate.
- The early-phase issue is best read as a formation-reference / restore-target compatibility problem, not just a display problem.
- The late-phase issue is best read as an objective-arrival / terminal smoothing problem, not the same issue as the early formation deformation.
- Viewer-local direction smoothing alone should not be treated as a sufficient resolution.
- Governance discussion should split these into two mechanism questions rather than one undifferentiated "jitter" problem.

## 1. Question

What do the newly visible 3D readouts suggest about the current bounded `neutral_transit_v1` mechanism?

The narrow question here is not:

- how should the viewer look nicer?

It is:

- what existing mechanism issues become easier to see once the replay is read through a trajectory-oriented heading cue?

## 2. Core Judgment

Current evidence supports a split reading:

1. the early-phase "outward struggle" / shape-growth behavior belongs primarily to the formation-reference / restore-target family
2. the late-phase large heading reversals belong primarily to the objective-arrival / terminal behavior family

These should not be treated as one issue.

## 3. Evidence From The Current Bounded Replay

The current bounded replay was read from the existing `neutral_transit_fixture` path with no runtime changes.

### A. Early / mid-phase shape change is real

Centroid-relative readout from current `position_frames` shows:

| Tick | RMS radius | front extent | rear extent | right extent | left extent |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 11.955 | 4.104 | -4.064 | 19.524 | -19.524 |
| 6 | 12.009 | 4.775 | -4.601 | 19.641 | -19.498 |
| 21 | 11.997 | 6.108 | -5.254 | 19.584 | -19.173 |
| 81 | 12.083 | 7.251 | -5.821 | 19.174 | -19.011 |
| 201 | 12.079 | 7.260 | -5.812 | 19.000 | -19.000 |
| 426 | 12.079 | 7.260 | -5.812 | 19.000 | -19.000 |

This means:

- RMS radius does increase from the initial state and then stabilizes at a slightly larger value
- the footprint does not remain locked to the initial 4:1 geometry
- the most visible growth is along the objective-facing axis rather than a broad random inflation

So the early visual "units are trying to move outward" impression is consistent with the path itself.

### B. Late objective-near oscillation is also real

Centroid-to-objective readout near arrival shows:

| Tick | centroid-to-objective distance | axial velocity projection |
| ---: | ---: | ---: |
| 425 | 2.257 | 1.000 |
| 426 | 1.257 | 1.000 |
| 427 | 0.257 | 1.000 |
| 428 | 0.743 | -1.000 |
| 429 | 0.232 | -0.975 |
| 430 | 0.751 | -0.983 |
| 431 | 0.210 | -0.961 |
| 432 | 0.749 | -0.960 |
| 433 | 0.202 | -0.951 |
| 434 | 0.756 | -0.958 |
| 435 | 0.185 | -0.940 |
| 436 | 0.763 | -0.948 |

This means:

- the fleet reaches the objective-near window cleanly
- then begins alternating across the near-target region
- the target-near behavior is an actual path effect, not only a heading-render artifact

## 4. Early-Phase Interpretation

The early issue is best read as:

- the initial 4:1 rectangle is not a stable fixed point under the current restore/reference path
- the current formation-reference expression or its current runtime-facing reading likely conflicts slightly with the literal initial arrangement

This is consistent with prior 2D observations that:

- early RMS can increase before the path settles
- front-profile residuals remain small but real

The most useful bounded interpretation is:

- the mechanism likely needs some combination of allowable error, tolerance band, or smoothing around the restore/reference target
- not because the viewer is wrong, but because the current formation result appears to be pulling toward a nearby but not identical stable reference shape

This does **not** yet prove which implementation lever is correct.
It only supports the mechanism classification:

- this belongs to the formation-reference / restore-target side of the system

## 5. Late-Phase Interpretation

The late issue is best read as:

- an objective radius / arrival smoothing / terminal behavior residual

This is consistent with the already recorded `R2` reading:

- the approach phase remains clean
- the oscillation appears only after entering the target-near window
- the sign of axial progress begins alternating near the objective

So the realistic viewer mode did not invent a late problem.
It simply made the existing near-stop bounce more visible by reading local realized tangent.

The current bounded interpretation is:

- this belongs to the objective-arrival / stop-radius / terminal damping family
- not to the same formation-reference family that explains the early shape-growth issue

## 6. Why These Should Stay Split

If these two issues are collapsed into one generic "jitter" problem, then:

- a formation-reference issue may be misdiagnosed as an arrival issue
- an arrival/terminal issue may be misdiagnosed as a formation issue
- viewer-local smoothing may be mistaken for a real resolution

That would be a bad mechanism read.

The early issue is:

- reference compatibility / allowable-error / smoothing around the formation target

The late issue is:

- centroid-to-objective radius / near-stop handling / terminal smoothing

Those are different mechanism families and should be discussed separately.

## 7. Governance-Facing Recommendation

Current evidence supports taking this to Governance as:

1. an early-phase formation-reference compatibility question
2. a late-phase objective-arrival smoothing question

It does **not** support treating the matter as:

- a pure 3D viewer problem
- a single undifferentiated movement bug
- a reason to reopen broad formation/runtime work without bounded scope

## 8. Bottom Line

The current 3D readout exposes a useful mechanism split:

- early "outward" posture and RMS growth are best treated as a formation-reference / restore-target compatibility issue
- late large direction reversal is best treated as an objective-arrival / terminal smoothing issue

These are real mechanism-reading questions, not just visual-polish questions.

No runtime behavior change was needed to reach this reading.
