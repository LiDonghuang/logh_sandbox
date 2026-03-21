# ODW Prototype Insertion Note v1.0

Status: Engineering review note  
Scope: First-cut ODW prototype insertion path  
Authority Context: Post-review prototype preparation  
Implementation: Not authorized by this note

## I. Purpose

This note converts the `ODW` runtime mapping review into one concrete prototype direction.

It answers a narrower question than the review document:

```text
Where should the first ODW prototype enter the movement runtime path?
```

The goal is not to maximize effect size.

The goal is to choose the cleanest insertion point that preserves:

- canonical semantics
- orthogonality with `PD`, `RT`, `MB`, and `FR`
- formation emergence through vector dynamics

## II. Review Anchor

Reference:

- `docs/archive/governance_specs/ODW_Runtime_Mapping_Review_v1.0.md`

That review established:

- the historical ODW combat path should be discarded as a prototype basis
- `ODW` should be treated as posture bias
- the first implementation should stay inside the movement layer

## III. Current Movement Structure

In the active runtime, movement currently separates into:

```text
centroid restoration
+ target-direction forward pressure
+ enemy attraction
+ separation
+ boundary response
+ MB-dependent tangent / parallel redistribution
+ deep-pursuit extension effects
```

This means there are several plausible insertion points for a new posture-bias parameter.

But most of them are poor first choices.

## IV. Rejected Insertion Points

### 1. Centroid restoration gain

Rejected because this makes `ODW` look too similar to:

- defensive rigidity
- formation-preservation control

This risks overlap with `FR`.

### 2. Deep-pursuit gain or pursuit confirmation

Rejected because this turns `ODW` into:

- second `PD`

This violates the intended boundary between posture and pursuit willingness.

### 3. Retreat gating or retreat thresholds

Rejected because this turns `ODW` into:

- second `RT`

### 4. Targeting path

Rejected for first cut because:

- `TL` should remain available as its own future mechanism
- blending `ODW` into targeting too early would blur parameter roles

### 5. Combat damage scale

Rejected because it makes `ODW` behave like:

- hidden combat effectiveness

This is explicitly outside canonical intent.

## V. Preferred Prototype Insertion

The preferred first insertion point is:

```text
movement-layer lateral pressure distribution
```

More precisely:

`ODW` should bias how much forward pressure is concentrated toward the attack axis versus spread laterally across the active front.

This is the cleanest first insertion because:

1. it changes posture, not trigger rules
2. it does not directly alter pursuit or retreat semantics
3. it influences geometry through movement redistribution
4. it can generate visible offense/defense differences without becoming a template selector

## VI. Recommended Mathematical Role

The first prototype should treat `ODW` as a small posture-bias coefficient:

```text
odw_posture_bias = normalized(ODW) - 0.5
```

Interpretation:

- offensive side of ODW:
  - more concentrated forward pressure
  - less lateral spreading
- defensive side of ODW:
  - broader forward pressure distribution
  - more lateral spreading / holding posture

Important:

This coefficient should not directly change:

- pursuit threshold
- retreat threshold
- damage output
- target choice

It should only bias the relative distribution of already-existing movement components.

## VII. Best First-Cut Injection Site

The most promising first-cut site is after the movement system constructs its forward-axis and lateral-axis decomposition, but before final total movement is committed.

That is the part of the runtime where:

- target-axis parallel motion
- tangent / lateral motion
- MB redistribution

are already explicitly separated.

Engineering implication:

`ODW` should likely multiply or rebalance:

```text
parallel pressure component
vs
lateral spread component
```

inside the movement-layer decomposition.

This is preferable to modifying raw centroid or enemy-attraction terms directly, because the decomposition layer is already where posture-like directional structure is expressed.

## VIII. Expected Behavioral Signature

If this insertion path is correct, then with `PD`, `RT`, `MB`, and `FR` held fixed:

- higher offensive ODW should produce:
  - stronger attack-axis concentration
  - more persistent forward pressure posture
  - geometry that may trend toward narrower, more penetrative fronts through emergence

- higher defensive ODW should produce:
  - broader pressure spread
  - more holding / preserving posture
  - geometry that may trend toward flatter or more containing fronts through emergence

These effects should appear:

```text
through vector redistribution
```

not through direct formation commands.

## IX. Prototype Boundary

The first prototype should remain deliberately small.

Recommended boundary:

- one new ODW-derived coefficient
- one insertion point
- movement layer only

Do not combine it with:

- combat changes
- pursuit changes
- retreat changes
- targeting changes

## X. Engineering Recommendation

The next implementation step should be:

```text
one bounded movement-layer prototype
that biases parallel-vs-lateral pressure distribution using ODW
```

This is currently the most defensible first ODW insertion path because it is:

- small
- bounded
- interpretable
- orthogonal
- compatible with the formation-emergence doctrine
