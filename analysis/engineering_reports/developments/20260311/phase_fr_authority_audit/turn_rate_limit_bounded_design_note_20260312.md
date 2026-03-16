# Turn-Rate Limit Bounded Design Note

Date: 2026-03-12
Status: Discussion draft
Thread: `analysis/engineering_reports/developments/20260311/phase_fr_authority_audit`

Engine Version: current local test harness over frozen runtime baseline
Modified Layer: none in this note
Affected Parameters: candidate future role for `MB`
Governance Impact: none in this note; this is design discussion only
Backward Compatible: N/A

## 1. Purpose

This note records a bounded engineering proposal for a future mechanism:

```text
turn-rate limit / turn-delay
```

The immediate reason to discuss it is structural, not cosmetic:

- current movement has strong instantaneous reorientation behavior
- this likely suppresses some maneuver asymmetries that should matter
- if `MB` retains any legitimate movement-near authority in a future architecture, it is more natural for that authority to live in turning / reorientation than in direct front-geometry shaping

This note does not authorize implementation.

## 2. Current Problem Framing

At present, unit facing is effectively replaced every tick by the newly composed movement direction.

Operationally, that means:

- units can pivot too quickly
- flanking or rear-entry openings may collapse into immediate head-on reorientation
- geometry is expressed too much through direct vector composition and not enough through heading inertia

This matters because the project is already moving toward:

- less direct personality authority in movement shaping
- cleaner separation between geometry emergence and other tactical biases

If so, then any future `MB` role should likely move away from:

- direct parallel / tangent geometry shaping

and toward:

- reorientation responsiveness
- commitment to a chosen heading
- cost or lag of turning under pressure

## 3. Bounded Design Objective

The bounded design objective is:

```text
introduce finite turning responsiveness
without introducing discrete tactical modes
and without turning MB into a new geometry gate
```

The mechanism should:

- remain continuous
- act locally at the unit heading layer
- preserve current movement vector construction as the desired direction source
- only limit how quickly the current facing can align to that desired direction

## 4. Proposed Mechanism Shape

### 4.1 State Variables

For each unit:

- current heading angle `theta_t`
- desired movement angle `theta_desired`

At each tick:

- compute `theta_desired` from the current composite movement vector
- update heading only partway toward that desired angle

### 4.2 Core Update Form

Recommended bounded form:

```text
delta = wrap_to_pi(theta_desired - theta_t)
delta_clamped = clamp(delta, -omega_max * dt, +omega_max * dt)
theta_{t+1} = theta_t + delta_clamped
```

where:

- `wrap_to_pi` gives the shortest signed angular difference
- `omega_max` is the maximum turn rate
- `dt` is simulation timestep

Velocity direction can then follow:

```text
v_hat_{t+1} = [cos(theta_{t+1}), sin(theta_{t+1})]
```

and position integrates from that heading-limited direction.

### 4.3 Continuous MB Coupling Candidate

If `MB` is later allowed to couple here, the cleanest role is:

```text
omega_max = omega_base * f_mb(MB)
```

with `f_mb` continuous and monotonic.

Interpretation candidate:

- lower `MB` -> slower reorientation, more conservative heading commitment
- higher `MB` -> faster reorientation, more aggressive maneuver responsiveness

This is only a directional candidate, not yet a semantic decision.

## 5. Why This Is More Plausible Than Direct MB Geometry Shaping

This mechanism is attractive because it gives `MB` a legitimate movement-near role without making it a geometry selector.

It would influence:

- how fast a unit can exploit an opening
- how quickly a flank can be answered
- how much inertia a committed push has

It would not directly decide:

- wedge vs flat front
- front curvature sign
- posture family

That is a much better authority fit than the current MB parallel/tangent shaping path.

## 6. Expected Tactical Effects

If implemented well, turn-rate limit should make these openings more meaningful:

- side-entry attacks
- rear-entry attacks
- misaligned starts
- staggered formation response

Expected qualitative changes:

- flanking advantages persist longer before being neutralized
- contact geometry depends more on approach history
- local maneuver mistakes are costlier
- rapid full-front reorientation becomes less automatic

## 7. Main Risks

### 7.1 Over-inertia

If turn-rate limit is too strong:

- units may feel sluggish or broken
- battles may become dominated by spawn geometry
- even legitimate front realignment may become impossible

### 7.2 MB Becoming a New Hidden Gate

If `MB` over-controls `omega_max`:

- `MB` could become a new posture-selection proxy
- this would recreate the same kind of authority overreach now under audit for `FR`

So any future `MB` coupling here must remain:

- continuous
- bounded
- secondary to the base turn-rate mechanism itself

### 7.3 Double Counting with Existing Movement Composition

Current movement already blends:

- target-forward drive
- centroid restoration
- attraction
- separation
- boundary
- pursuit effects

Adding turn-delay on top means:

- some behaviors that currently look stable may change sharply
- several tuned constants may need reinterpretation

Therefore this should not be dropped into the current bounded-correction thread casually.

## 8. Engineering Recommendation

My recommendation is:

1. do not implement this inside the current `FR audit / bounded correction` thread
2. carry it forward as a candidate mechanism for the next architecture-design phase
3. if later prototyped, do it first in `test_run` harness only
4. introduce the base turn-rate limit first
5. only after that, test whether `MB` should modulate it at all

This ordering matters.

The project should first answer:

```text
Is finite turning itself beneficial?
```

before answering:

```text
Should MB modulate finite turning?
```

## 9. Bounded Prototype Plan

If this mechanism is approved for future test-only prototyping, the clean bounded sequence would be:

1. base turn-rate limit with no personality coupling
2. paired comparison on:
   - diagonal approach
   - left/right symmetric approach
   - side-entry / rear-entry openings
3. only then test a continuous `MB -> omega_max` coupling

Required readouts:

- alive trajectory
- first major divergence tick
- flank/rear conversion quality
- front-profile stability after contact
- whether geometry selection remains attributable to posture/movement history rather than MB gate behavior

## 10. Conclusion

Turn-rate limit is a credible and worthwhile future mechanism.

Engineering judgment:

- it is a better long-term home for any legitimate `MB` movement-near authority than direct geometry shaping
- it is architecturally compatible with the current move toward authority purification
- but it belongs to a future architecture/prototype phase, not to the active bounded FR correction line

In short:

```text
turn-delay looks promising,
MB may fit there better than it fits current geometry shaping,
but the mechanism should be prototyped as a new bounded design track later,
not merged into the present FR audit thread.
```
