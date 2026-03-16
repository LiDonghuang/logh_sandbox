# Support-Weighted Contact Impedance Family Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Phase 1 hostile contact impedance family redesign. Test-only substrate work only.

## 1. Why a New Family Is Needed

The current leading Phase 1 prototype, `hybrid_v2_r125_d035_p020`, passed the numeric DOE gate but did not pass human visual acceptance cleanly.

The key problem is not that the prototype is inactive. It is active. The problem is that its mechanism shape is still too local and too symmetric in the wrong way.

Current `hybrid_v2` behavior:

- damp positive forward displacement under hostile proximity
- add bounded local repulsion
- remain blind to friendly support depth and front integrity

This means it can reduce some deep penetration while still allowing visually obvious weaving, lateral slip-through, and local infiltration in cases where a thicker, intact front should feel harder to penetrate.

## 2. Problem Restatement

The unresolved failure case is:

- close-contact
- intact front
- strong local friendly support
- especially asymmetric `2:1` pressure

In that situation, the current model still does not express:

```text
penetration resistance should rise when hostile forward motion faces a locally supported front
```

That is the missing mechanism.

## 3. Family Identity

The next family should be understood as:

```text
support-weighted / front-support-aware contact impedance
```

This is still low-level substrate work.

It is **not**:

- TL activation
- doctrine scripting
- personality expression
- line-holding by hard state switch

## 4. Core Mechanism Idea

For each unit, impedance should depend not only on hostile proximity, but also on the local support structure behind and around the hostile-facing front.

In practical terms:

1. compute hostile proximity continuously
2. compute local friendly support continuously
3. estimate whether the unit is pressing into a supported hostile-facing structure
4. increase forward damping and/or penetration resistance accordingly

The important distinction is:

- `hybrid_v2` asks: "am I close to enemies?"
- the new family asks: "am I trying to push into enemies who are locally supported as a front?"

## 5. Candidate Continuous Inputs

All inputs should remain continuous and physically local.

### 5.1 Hostile proximity

Keep the current proximity term as one factor:

- local
- continuous
- symmetric

### 5.2 Friendly support density

Add a local friendly support measure, for example:

- nearby same-fleet unit mass within a support radius
- distance-weighted friendly support
- optionally biased toward the local hostile-facing half-plane

This should express whether a unit belongs to a locally thick, supported structure rather than an isolated spear tip.

### 5.3 Front-support asymmetry

The most important new signal is not raw support alone, but support contrast:

```text
front_resistance ~ hostile_proximity * hostile_support / (self_support + eps)
```

or a bounded monotone variant of that shape.

Interpretation:

- pushing into a thicker supported hostile front should be harder
- pushing through a thin, weakly supported hostile fringe should be easier

This gives the model a way to distinguish:

- intact front resistance
- weak exposed fringe

without introducing doctrine semantics.

## 6. Why This Is Better Than "More Repulsion"

Increasing raw hostile repulsion tends to create the wrong visual style:

- fronts bounce apart
- contact geometry gets noisy
- neutral close-contact safety degrades

Support-weighted impedance is preferable because it can act mainly on:

- forward penetration intent

rather than trying to solve the problem by stronger geometric shoving.

That should better preserve:

- local sliding
- contact continuity
- non-doctrinal flow

while still making intact fronts harder to penetrate.

## 7. Recommended First Mechanism Shape

The first bounded candidate should stay simple.

Recommended structure:

1. keep current hostile proximity
2. add a local friendly support score
3. compute a bounded hostile-front-support score
4. use that score to scale forward damping
5. keep repulsion small and secondary

That implies a shape closer to:

```text
new_forward_damping
= base_hostile_proximity
  * support_weight_term
```

with:

- continuous weighting
- monotone response
- no contact-state switch

Repulsion should remain capped and auxiliary, not primary.

## 8. First Test Intent

The first test goal should not be "make fronts rigid."

It should be:

- reduce visually implausible penetration in the `2:1` close-contact exception fixture
- avoid materially worsening neutral close-contact observer safety

That is, the next family should be judged by:

1. whether B still slips too easily into a supported A front
2. whether neutral mirrored fixtures remain acceptably clean

## 9. What This Family Must Not Encode

The redesign must not silently encode:

- target value
- weak-point semantics
- TL-style preference
- personality-specific courage or discipline
- doctrine-specific line behavior

This remains a substrate-level penetration-resistance family, not a tactical brain.

## 10. Bottom Line

The current `hybrid_v2` family is useful, but insufficient.

The next defensible Phase 1 direction is not:

- stronger raw repulsion

but:

- support-weighted / front-support-aware penetration resistance

The intended gain is:

```text
make supported hostile fronts harder to penetrate,
without turning contact geometry into a hard wall or doctrine script.
```
