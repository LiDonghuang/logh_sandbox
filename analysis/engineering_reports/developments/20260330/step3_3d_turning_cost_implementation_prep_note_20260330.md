# Step 3 3D Turning-Cost / Heading-Inertia Implementation-Prep Note (2026-03-30)

Status: implementation-prep discussion only  
Authority: structural prep only, not implementation authorization  
Scope: future movement-substrate modernization seam  
Non-scope: this round's primary carrier, hostile-contact repair, personality re-entry, full acceleration rewrite

## Summary Read

Current runtime still reads too close to near-instant heading response.

That read matters because:

- it keeps formation response visually and mechanically too crisp
- it increases the risk that any future formation-reference carrier becomes snapping or over-clean
- it affects both neutral transit and battle readability

But it should not displace the current main line.  
The current main line is still formation substrate.

## Why Turning-Cost Is Same-Theme but Not First Carrier

Turning-cost belongs to the same modernization theme because it affects:

- how alive a fleet looks
- how quickly formation adjustments are realized
- whether restore and movement feel glued together or mechanically separated

But it is not the first carrier of this round because:

- PR #6 still needed a cleaner answer to "what is the formation reference surface?"
- changing heading realization too early would blur the source of improvement
- turning-cost could easily mask or amplify formation-reference issues before the reference layer is clean

So the correct order remains:

1. formation-reference carrier first
2. turning-cost prep second
3. turning-cost implementation only later if the formation carrier is more settled

## Current Runtime Read

The current movement stack still behaves too close to:

- desired direction -> realized direction almost immediately

That does not mean there is literally zero lag everywhere.  
It means the current maintained read is still much closer to:

- direct heading realization

than to:

- bounded turning cost
- heading inertia
- max turn-rate governance

## Smallest Clean Future Seam

The best clean future seam is between:

- desired movement direction
- realized heading/orientation used by the unit

That seam should stay:

- bounded
- deterministic
- low-parameter
- source-of-truth clean

It should not start as:

- full linear-acceleration physics
- coupled translational inertia stack
- large personality-owned movement palette

## Candidate Ranking

Current ranking for the first future turning-cost carrier:

1. **Heading relaxation**
   - simplest bounded first seam
   - easy to reason about
   - likely lowest implementation burden
   - can be phrased as continuous approach to desired heading

2. **Max turn-rate**
   - also clean
   - more interpretable in some tactical reads
   - can be visually readable
   - slightly more explicit as a hard cap

3. **Simple heading inertia**
   - plausible, but slightly more stateful and less transparent as a first cut

Current preference:

- heading relaxation first
- max turn-rate as the strongest nearby alternative

## Why Not Full Acceleration-First Modeling

Acceleration-first modeling is not the preferred next read because it would mix together:

- heading realization
- translational speed realization
- potentially braking and overshoot

That is too much for the first modernization seam.

If the immediate human complaint is:

- fleets and groups turn too instantly

then the smallest clean answer should stay:

- heading-cost first

not:

- full inertial physics stack first

## Risks to Watch Later

Any future turning-cost carrier will create risks for:

- neutral-transit validation
  - soft morphology could become too sluggish or lagging
- battle readability
  - close-range contact may become blurrier before contact substrate is ready
- formation restore behavior
  - restore may look weaker simply because heading realization is delayed

So any later implementation will need clean paired comparison against:

- current PR #6 carrier
- not just old pre-split baselines

## Same-Theme Conclusion

Turning-cost should remain an active same-theme modernization line because it is highly likely to matter for:

- future living formation read
- future 3D readability
- future motion honesty

But it should remain:

- implementation-prep only
- behind formation-substrate clarification

## Bottom Line

Current runtime still reads too close to near-instant heading response.

The best future first seam is still:

- heading relaxation

with:

- max turn-rate

as the strongest nearby alternative.

This line should stay open as implementation-prep, but not displace the current formation-first carrier line.
