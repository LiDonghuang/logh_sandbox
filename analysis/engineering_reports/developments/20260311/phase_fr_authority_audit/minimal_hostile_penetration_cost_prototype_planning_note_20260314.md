# Minimal Hostile Penetration Cost Prototype Planning Note

Date: 2026-03-14  
Status: Prototype planning note  
Scope: Bounded Phase 1 planning only. No implementation authorization.

## 1. Purpose

This note translates the current hostile penetration governance direction into a minimal prototype plan.

It does not request:

- implementation authorization
- baseline replacement
- large DOE
- personality activation

It only defines the smallest acceptable prototype shape for a future test-only comparison.

## 2. Planning Target

The target mechanism is:

```text
minimal hostile-side penetration cost / non-penetration bias
```

Its job is intentionally narrow:

- detect whether a movement step embeds a unit more deeply into hostile local occupancy
- apply a continuous local cost to that deeper embedding

It must not decide:

- whether a side should break through
- whether a side should hold
- whether local support is sufficient
- whether local force ratio favors penetration

For current planning purposes, this prototype should be interpreted as:

```text
the future RA=5 baseline reference for hostile penetration cost
```

That does not mean `RA` is implemented now.
It only means the shared base layer should correspond to the neutral reference level that a future `RA` modulation would later act on.

## 3. Occupancy Field Definition

The preferred base object is a continuous hostile occupancy field.

For a unit position `x`, define:

```text
H(x) = sum_i K(||x - e_i|| / s)
```

where:

- `e_i` are hostile unit positions
- `K` is a continuous short-range kernel
- `s` is a single scale parameter

Recommended design constraints:

- `K` should be smooth and monotone
- `K` should decay with distance
- `K` should remain local rather than global
- `K` should not use hard membership sets

The most natural scale anchor is:

```text
s = hostile_penetration_cost_scale * min_unit_spacing
```

This keeps the mechanism structurally close to base spacing rather than turning it into a separate tactical layer.

## 4. Penetration Delta Definition

For each unit on a given tick, compare hostile occupancy before and after the tentative move:

- `H(pre)`
- `H(post)`

Then define:

```text
penetration_delta = max(0, H(post) - H(pre))
```

Interpretation:

- if a unit does not move deeper into hostile occupancy, no extra hostile penetration cost is applied
- if a unit increases its hostile occupancy exposure, the increase itself is what gets priced

This is the key low-level distinction that keeps the mechanism neutral:

- static proximity alone is not the target
- deeper embedding is the target

## 5. Cost Injection Into Movement

The prototype should enter movement as a continuous displacement cost, not as a discrete state.

Preferred first form:

- compute the tick displacement vector
- preserve the current tentative movement proposal
- apply a continuous reduction proportional to `penetration_delta`
- only the portion of movement that increases hostile occupancy should be suppressed

This can be represented in one of two equivalent low-level styles:

1. displacement damping  
Reduce the effective displacement magnitude as `penetration_delta` rises.

2. occupancy rollback  
Move the tentative position partway back toward pre-move position as `penetration_delta` rises.

For the first bounded prototype, the cleaner option is:

```text
occupancy rollback
```

because it directly maps to "do not move as far into hostile local occupancy."

## 6. Minimal Parameter Set

The first prototype should contain at most two parameters:

1. `hostile_penetration_cost_scale`
- controls the locality radius of the occupancy field

2. `hostile_penetration_cost_strength`
- controls how strongly `penetration_delta` suppresses deeper embedding

No third shaping parameter should be introduced in the first prototype.

In particular, the prototype should not add:

- support weighting
- force-ratio terms
- side-dependent branching
- angle-gated tactical semantics

## 7. Why This Is More Neutral Than the Retired Family

This plan is more neutral than `support_weighted_v3` because it does not inspect local tactical meaning.

It does not use:

- local support counts
- support contrast
- front support thickness
- local hostile quantity interpretation

It only uses:

- hostile positions
- local continuous occupancy
- whether the proposed movement step goes deeper into that occupancy

That keeps it closer to shared substrate and farther from implicit doctrine.

## 8. Why This Preserves Future RA Compatibility

Current governance direction says future personality compatibility should remain possible, and that this line is conceptually closer to `RA` than to `PD`.

This prototype preserves that option because the base layer only establishes:

```text
penetration has continuous cost
```

It does not establish:

```text
whether a force is willing to keep paying that cost
```

That second question can remain open for future higher-layer modulation.

This is why the mechanism is compatible with later RA-style interpretation:

- the base layer supplies the cost
- a future higher layer could modulate tolerance toward that cost

But that future modulation is not implemented now, and must not be smuggled into the base prototype.

## 9. Validation Preparation

If implementation is later authorized, the first validation should remain small.

Recommended preparation:

- keep `hybrid_v2_r125_d035_p020` as the working Phase 1 reference
- add one new test-only family for the minimal penetration-cost prototype
- compare only:
  - working reference
  - new minimal penetration-cost prototype
  - `off`

Use the existing three-fixture discipline:

- `2:1` close-contact exception
- neutral close-contact
- neutral long-range

Keep:

- `boundary_enabled = false`
- current pre-TL substrate unchanged
- intermix diagnostics as diagnostics only

Do not reopen large DOE before the first bounded comparison.

## 10. Bottom Line

The next hostile penetration prototype should be minimal in both meaning and parameter count.

The cleanest first plan is:

```text
construct a local hostile occupancy field,
measure only deeper embedding into that field,
and apply a continuous rollback cost with one scale and one strength parameter
```

That is the narrowest prototype shape that matches current governance requirements and preserves clean future compatibility.
