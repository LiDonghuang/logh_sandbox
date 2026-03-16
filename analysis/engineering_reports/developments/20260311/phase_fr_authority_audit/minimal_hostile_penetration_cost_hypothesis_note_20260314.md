# Minimal Hostile Penetration Cost Hypothesis Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Phase 1 hostile contact impedance follow-up mechanism hypothesis only. No implementation authorization.

## 1. Purpose

This note proposes the next bounded mechanism hypothesis for Phase 1 hostile contact impedance work, following the stop decision on `support_weighted_v3` and the governance requirement that any continuation must begin from a genuinely different mechanism idea.

This is not:

- a baseline replacement proposal
- a TL proposal
- a personality mechanism proposal
- an implementation request

It is only a new bounded mechanism hypothesis for review.

## 2. Current Position

The current line has already produced two conclusions:

1. The original diagnosis remains valid:

```text
the system still lacks a sufficiently convincing hostile-side contact impedance layer
```

2. The current family has reached a local limit:

- `repulsion_v1` is not sufficient
- `damping_v2` is not sufficient
- `hybrid_v2_r125_d035_p020` remains the current working Phase 1 reference only
- `support_weighted_v3` did not justify continuation

So the next step cannot be "more parameters on the same family." It must start from a simpler and more different mechanism definition.

This also fixes the intended interpretation of the shared penetration-cost layer:

```text
the current penetration-cost prototype should be treated as the future RA=5 baseline reference
```

Meaning:

- hostile penetration cost exists as shared substrate regardless of personality
- the present engineering task is to calibrate that neutral baseline
- a future higher-layer parameter may later modulate willingness to continue paying that cost
- but the base layer itself must remain non-personality and future-compatible

## 3. Mechanism Hypothesis

### Proposed direction

```text
minimal hostile-side penetration cost / non-penetration bias
```

### Core idea

The low-level substrate should impose a continuous cost on **entering more deeply into a hostile local occupancy zone**.

The key change in emphasis is:

- not "how much support does each side have"
- not "which side should hold the line"
- not "who should break through"

but only:

```text
does this tick's movement embed the unit further into local hostile-occupied space?
```

If yes, that extra embedding should carry a continuous local cost.

## 4. Why This Is Genuinely Different

This hypothesis differs from `support_weighted_v3` in a fundamental way.

`support_weighted_v3` tried to improve contact impedance by adding local semantic shaping:

- self-support
- hostile-support
- support contrast
- conditional damping scaling

That direction moved too close to local quantity interpretation and still failed to produce a stable advantage.

The present hypothesis removes that layer entirely.

It does **not** ask:

- who has more local support
- who deserves to penetrate
- which front is stronger
- whether a side is locally outnumbered

It only asks:

- whether the current displacement increases hostile-side penetration depth

That is a simpler substrate question and stays closer to "enemy line is not air."

## 5. Proposed Low-Level Form

The most defensible shape is a continuous hostile occupancy field.

For each hostile unit, define a local soft occupancy kernel around its position.

For a unit position `x`, define:

```text
H(x) = sum_i K(||x - e_i||)
```

where:

- `e_i` are hostile unit positions
- `K` is a continuous short-range kernel
- `K` decays smoothly with distance
- `K` is strongest inside or near the hostile spacing envelope

Then evaluate:

- `H(pre_move_position)`
- `H(post_move_position)`

and define:

```text
penetration_delta = max(0, H(post) - H(pre))
```

Interpretation:

- if the movement does not enter more deeply into hostile occupancy, no extra cost is applied
- if the movement increases hostile occupancy exposure, apply a continuous damping or rollback proportional to that increase

This is the key difference from current `hybrid_v2`:

- `hybrid_v2` mostly prices hostile proximity at the destination
- this hypothesis prices the **incremental act of moving deeper into hostile occupancy**

That is closer to a true non-penetration bias.

## 6. Desired Mechanical Properties

This hypothesis should preserve the current Phase 1 design principles:

- continuous
- local
- symmetric
- non-doctrinal
- non-personality
- test-only

It should also avoid:

- hard contact-state switching
- local support counting
- hostile quantity functions as primary logic
- tactical mode trees
- doctrine-like behavior selectors

## 7. Why This May Be Better Than the Retired Family

The previous failed branch tried to infer more about the local tactical situation.

This hypothesis tries to infer less.

That restraint may be exactly what is missing.

Expected advantages:

1. Simpler substrate meaning  
It is easier to interpret "deeper hostile occupancy costs more" than "support contrast changes damping."

2. Better layer discipline  
It does not pull local force-balance semantics into the base impedance layer.

3. Better alignment with governance guidance  
It is closer to minimal hostile-side penetration cost and farther from support-aware conditional shaping.

4. Better chance of visual relevance  
If units are paying for entering deeper into hostile local occupancy, the mechanism may target the exact animation failure more directly than support-aware scaling.

## 8. Bounded Prototype Guidance

If implementation is later authorized, the first prototype should remain very small.

Recommended bounded shape:

- keep `hybrid_v2_r125_d035_p020` as working reference
- add one new test-only family for comparison
- use only a small number of parameters

Preferred parameter discipline:

- one range/scale parameter
- one cost strength parameter
- avoid adding a third semantic shaper unless the first two clearly fail

This is important because the current line has already shown that parameter growth is not the right direction.

## 9. Evaluation Discipline

If this hypothesis is later prototyped, evaluation should keep the current Phase 1 discipline:

- exception fixture for penetration suppression
- neutral close-contact fixture for geometry safety
- neutral long-range fixture as guard rail
- `IntermixSeverity` and related signals as diagnostics only
- human visual review remains necessary

Low `IntermixSeverity` must still not be treated as a sufficient acceptance proxy.

## 10. Bottom Line

The next acceptable Phase 1 hypothesis should not be a more decorated version of `support_weighted_v3`.

The cleaner direction is:

```text
a minimal hostile-side penetration cost,
implemented as a continuous cost on moving deeper into hostile local occupancy
```

This is simpler than support-aware shaping, closer to basic non-penetration bias, and better aligned with current governance guidance.
