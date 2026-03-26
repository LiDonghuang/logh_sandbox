# R2 - Arrival Oscillation Residual Note (2026-03-25)

Status: Residual Readout / Explanation Note  
Scope: bounded explanation of the target-near arrival oscillation after `v4b Candidate A` acceptance

## 1. Question

This note answers one narrow question only:

is the target-near oscillation a new `Candidate A` defect, or a pre-existing residual inherited from the earlier path?

## 2. Did It Already Exist In `v4a`

Yes.

Bounded comparison against a readout run with `Candidate A` disabled shows that the same target-near oscillation pattern already existed in the current `v4a` post-fix path.

Observed comparison:

- `v4a` without `Candidate A`: arrival tick `451`
- current accepted `Candidate A`: arrival tick `426`

In both paths:

- centroid-to-objective distance declines steadily during approach
- once the run enters the target-near window, the axial velocity component begins alternating sign
- the signed distance proxy stays small, indicating the fleet is hovering near the target instead of diverging away from it

So the accepted reading is:

- `Candidate A` inherited this residual
- `Candidate A` did not create it

## 3. What Stage The Residual Belongs To

This residual is best classified as:

`reached-but-not-frozen / near-stop behavior`

It is not primarily an approach-phase problem.

Why:

- the approach trend itself is clean and monotone up to the target-near window
- the alternating behavior appears only after the centroid is already inside or near the stop-radius region
- the run is still advancing through extra post-arrival ticks rather than freezing immediately at first arrival

## 4. What It Most Likely Is

Current evidence most strongly supports:

- `objective arrival handling issue`
- with overlap into `stop radius semantics` and `terminal damping behavior`

It is less consistent with:

- formation mapping defect
- fixture reporting artifact

Reason:

- the oscillation appears in the movement trace itself, not only in the final printed summary
- it is present both before and after `Candidate A`
- the new restoration object clearly improved front profile and burden metrics, yet this near-target oscillation remained

So the simplest current reading is:

the residual belongs to the arrival/terminal behavior family, not the `Candidate A` formation-reference family.

## 5. Are Current Diagnostics Enough

For this bounded explanation, yes.

Existing captured positions plus offline derived traces were enough to show:

- the oscillation predates `Candidate A`
- it appears in the near-stop phase
- it is visible as alternating axial velocity near the target
- it should not currently be blamed on expected-position mapping

No runtime readout expansion was required for this note.

## 6. If Future Readout Is Needed, What Is The Smallest Useful One

If Governance later wants a tighter residual explanation without opening implementation, the smallest useful test-only readout would be:

- target-near signed centroid-to-objective distance trace
- target-near velocity projection onto the objective axis

That would be enough to distinguish:

- approach
- inside-stop-radius drift
- post-arrival bounce

without changing stop semantics or movement gains.

## 7. What Is Not Recommended Now

Current evidence does **not** support doing any of the following in this turn:

- changing stop semantics
- changing the objective contract
- adding arrival hysteresis
- retuning movement gain
- folding this residual into formation-spec work

Those are all behavior changes, and this authorization is readout/explanation only.

## 8. Bottom Line

`R2` is best classified as a `pre-existing target-near arrival oscillation`.

Current evidence supports the following bounded reading:

- it already existed in `v4a`
- it happens in the reached-but-not-frozen / near-stop phase
- it is more likely an arrival/terminal semantics residual than a `Candidate A` mapping defect
- it should remain split from the accepted `Candidate A` success judgment

No runtime behavior change was needed to reach this reading.
