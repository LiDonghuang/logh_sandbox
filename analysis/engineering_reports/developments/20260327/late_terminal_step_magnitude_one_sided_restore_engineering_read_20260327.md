# Late Terminal Settle - Step-Magnitude + One-Sided Axial Restore Engineering Read

Date: 2026-03-27
Status: engineering read after local prototype cycle

## Main read

The current local late-terminal result supports a narrower source-level diagnosis than the earlier freeze-based turns.

The key late problem was not only:

- which expected-position frame to freeze

It was also:

- that once the fleet entered the terminal window, the unit solver was still effectively resolving near full step magnitude
- while front outliers could still receive strong backward axial restore

That combination created:

- tail motion that was too large
- front-edge compression
- then visible unit flips

## Why the current candidate works better

The current accepted local candidate combines three ideas:

1. freeze orientation, keep center live
2. reduce actual per-unit step magnitude near the anchor
3. soften only backward axial restore

This works better because the two added cuts attack the actual observed terminal mechanics directly:

- step-magnitude gate reduces the size of residual unit motion
- one-sided axial restore gate prevents backward restore from dominating the front edge as easily

The resulting tail is much smaller and much less destructive than either:

- whole-frame freeze
- split-cut-only

## Why the stricter third clamp was rejected

The locally rejected `no-net-backward axial clamp` looked attractive because it removed the last two backward units at `tick 428`.

But source-level and human-visible reads both showed the same problem:

- it over-constrained the frontmost outliers
- the backward settle disappeared
- but the units then rotated left across several ticks and snapped back later

That means the third clamp was no longer a quiet bounded correction.
It started changing the visible posture path in a worse way.

So the current engineering judgment is:

- do not keep that third clamp
- stop at the previous candidate

## Current remaining residual

The current accepted candidate still leaves one narrow artifact:

- at `tick 428`, the same two long-standing frontmost protruding units settle backward once

But that is qualitatively different from the earlier broken tail:

- it is not a mass fleet fracture
- it does not continue through `429..430`
- it does not reopen the broad terminal disorder

## Early restoration implication

This late-terminal result likely has a broader implication for the earlier restoration problem.

The key implication is:

- restore should not always be treated as a single scalar-strength family
- sign and component matter

In the current late-terminal case, a purely scalar answer was not enough:

- deadband alone was not enough
- freeze-variant changes alone were not enough
- the useful cut turned out to be component-wise and one-sided

That suggests an early-side question worth Governance thought later:

- whether early restoration compatibility may also benefit from separating axial vs lateral restore
- or from treating backward restore differently from forward restore

This note does not propose an early implementation turn.
It records the engineering implication only:

- the late fix hints that early restoration trouble may also be a directional compatibility problem, not just a tolerance/deadband problem

## Current recommendation

Current recommendation to Governance:

- treat this accepted candidate as the best bounded late-terminal line so far
- record the rejected third clamp as an important local non-solution
- keep the early-restoration implication in view for a later deliberate turn
