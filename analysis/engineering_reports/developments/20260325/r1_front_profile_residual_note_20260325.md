# R1 - Front-Profile Residual Note (2026-03-25)

Status: Residual Readout / Explanation Note  
Scope: bounded explanation of the stable front-profile residual bias after `v4b Candidate A` acceptance

## 1. Question

This note answers one narrow question only:

what is the remaining front-profile residual in the accepted `neutral_transit_v1` `Candidate A` path, and what does the current evidence support without opening a new implementation turn?

## 2. Current Geometric Reading

In the accepted `Candidate A` long-distance run, the residual front shape is not a broad front-stretch failure anymore.

What remains is a smaller, stable leading-profile bias:

- a few front-center units remain slightly ahead
- both wings also remain slightly ahead
- the profile appears early and then persists through approach and arrival
- the shape is visually steady rather than jittery

Bounded readout from existing `position_frames` and fixture captures shows:

- repeated run under fixed seeds reproduced the same readout exactly
- arrival tick was `426` in both repeated reads
- front-center mean forward deviation was `2.217`
- front-center deviation std was `0.137`
- wing mean forward deviation was `2.547`
- wing deviation std was `0.139`
- the readout window showed zero sign flips for these deviation summaries

So the current residual is:

- deterministic
- low-amplitude relative to the pre-`Candidate A` stretching problem
- persistent
- non-oscillatory in the observed window

## 3. What It Most Likely Is

Current evidence supports the following reading order.

### Most likely

`front-edge reference geometry artifact` combined with a `fixed-initial-order slot mapping artifact`

Reason:

- the residual is localized to the front profile, not the full body
- it is stable across the run instead of drifting or flipping
- `Candidate A` already removed the broad centroid-pull stretch, so the remaining shape looks more like a reference-profile mismatch than a global restore-object failure
- the wing deviation being slightly larger than the center deviation points to how the current rect-lattice front edge is being represented in the expected anchor, not to broad inward collapse

### Plausible but secondary

`objective-facing frame artifact`

Reason:

- the expected anchor is reconstructed in an objective-facing frame, so any small bias in front-edge expression will be carried consistently along that frame
- however, the current evidence does not show frame instability or axis flipping

### Less likely as the primary explanation

`restore-to-reference weighting artifact`

Reason:

- if weighting were still the main issue, we would expect a broader residual deformation pattern or a clearer burden rebound
- current paired validation showed the opposite: front stretching fell sharply and broad projection burden also fell

## 4. Are Current Diagnostics Enough

For the current governance question, yes.

Existing diagnostics plus offline readout from captured positions are sufficient to support these bounded conclusions:

- the residual is real
- it is stable
- it is deterministic
- it is not a projection-instability problem
- it is more consistent with front-profile/reference expression than with renewed broad stretch

What current diagnostics do **not** fully answer yet is the finer split between:

- front-center slot reference mismatch
- wing-front slot reference mismatch
- rect-lattice front-edge expression details

That narrower split would need additional readout, but it is not required to support the present residual classification.

## 5. If Future Readout Is Needed, What Is The Smallest Useful One

No readout expansion was required for this note.

If Governance later wants a tighter explanation without authorizing a behavior change, the smallest useful test-only readout would be:

- front-center vs wing-front slot deviation summary along the current forward axis
- optional paired lateral deviation summary for the same front-row units

This would remain:

- test-only
- fixture-only
- readout-only

and would not require changing mapping, layout, or runtime behavior.

## 6. What Is Not Recommended Now

Current evidence does **not** justify any of the following in this turn:

- changing the layout family
- changing the fixed-order slot mapping rule
- changing `FR` semantics
- changing expected-position reconstruction behavior
- promoting the issue into battle path or generalized formation work

That would collapse a small residual explanation problem back into a rebuild turn, which is explicitly outside this authorization.

## 7. Bottom Line

`R1` is best classified as a `stable front-profile residual bias`.

It is currently best read as:

- a deterministic front-edge/reference-expression artifact
- likely shaped by the interaction of rect-lattice front geometry and fixed-order expected-slot mapping
- not a renewed broad stretching failure
- not a projection-instability problem
- not a reason to reopen centroid pull or old shaping family

No runtime behavior change was needed to reach this reading.
