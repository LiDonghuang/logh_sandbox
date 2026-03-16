# Degeneracy-Safe Contactability Direction Note

Date: 2026-03-13
Status: Engineering concept note
Scope: Bounded low-level direction-substrate refinement
Implementation: Not requested

## 1. Why this note exists

Current pre-TL substrate work has exposed a specific low-level risk:

- under mirrored or near-mirrored geometry
- multiple enemy candidates may be equally good, or nearly equally good
- current surrogate families can then fall back to stable iteration order

This means the problem is not only:

- sharpness
- locality
- smoothness

It is also:

- **degeneracy safety**

That is:

```text
When the geometry does not strongly distinguish among nearby enemies,
the substrate should not silently hand control to arbitrary list order.
```

## 2. The wrong question

The wrong question is:

```text
If several enemies are equally best, which one should be chosen?
```

That framing naturally leads back toward:

- hard discrete tie-breaks
- branch logic
- accidental hidden doctrine

It also risks pre-occupying future `TL` authority.

## 3. The better question

The better substrate question is:

```text
If several nearby enemies are similarly contactable,
how much should each contribute to the current fleet-level direction field?
```

This reframes the problem from:

- discrete selection

to:

- continuous weighting

## 4. Preferred solution direction

Engineering currently prefers the following bounded direction:

### Continuous local contactability weighting

Instead of:

- selecting one enemy
- or selecting a hard nearest-k set and averaging only that set

the substrate should build a local continuous field:

```text
w_i = K(local_contactability_i)
dir = normalize(sum_i w_i * (x_i - c_self))
```

where:

- `c_self` is the current fleet centroid
- `x_i` is enemy position
- `K` is a smooth monotone local weighting kernel

The kernel may depend only on semantically light physical quantities such as:

- distance
- short-horizon approach geometry
- light local contactability / spacing feasibility
- very light range-related contactability

It must not encode future `TL` semantics such as:

- high value
- weak point
- doctrinal main body
- strategic preference

## 5. Why this is better than discrete tie-breaks

This direction is preferred because it:

- removes hard boundary jumps such as “5th enemy in, 6th enemy out”
- reduces sensitivity to exact tie or near-tie ordering
- stays continuous under small geometric perturbations
- preserves future `TL` ownership of targeting preference semantics
- fits the current governance preference for continuous / monotone / path-local mechanisms

## 6. Practical bounded variants

Current bounded concept space can be understood in three levels:

### A. Hard local set

Example:

- `nearest5_centroid`

Strength:

- preserves local contact flavor

Weakness:

- still has a hard membership boundary
- still exposes tie / near-tie order sensitivity

### B. Soft local set

Example:

- take nearest `m` local enemies
- weight all of them smoothly by distance/contactability
- compute a weighted local centroid

Strength:

- keeps locality
- reduces hard set-boundary artifacts

Weakness:

- still partially depends on the initial local candidate envelope

### C. Fully continuous local field

Example:

- all nearby enemies contribute through a decaying local kernel

Strength:

- strongest degeneracy safety
- most continuous
- cleanest substrate for future `TL`

Weakness:

- must be watched so it does not become too global

## 7. Current engineering recommendation

Current engineering recommendation is:

```text
Do not solve degeneracy by inventing a smarter discrete tie-break.
Solve it by moving the substrate one step further toward continuous local weighting.
```

In practical terms:

- do not prefer unit-id order
- do not prefer dict order
- do not add semantically loaded second-stage filters

Prefer instead:

- smooth local weighting
- soft local candidate envelopes
- contactability-weighted direction fields

## 8. Boundary statement

This note does **not** authorize:

- implementation
- future `TL` activation
- doctrinal target preference selection

It only states a bounded engineering direction:

```text
Degeneracy should be handled by continuous local weighting,
not by sharper discrete target choice.
```
