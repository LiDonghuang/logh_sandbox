# Contactability Direction Concept Comparison

Date: 2026-03-13
Status: Engineering concept comparison
Scope: Compare bounded pre-TL direction-substrate concept families
Implementation: Not requested

## 1. Purpose

This note compares three bounded concept families for fleet-level direction reference under the current pre-TL substrate line:

- hard local set
- soft local set
- fully continuous local field

The purpose is not to select a permanent answer.
The purpose is to clarify trade-offs under the current governance framing:

- preserve future `TL` ownership of targeting semantics
- favor continuous / monotone / path-local shaping
- avoid discrete hidden doctrine
- improve degeneracy safety under mirrored geometry

## 2. Comparison criteria

The comparison is organized against five criteria:

1. `symmetry safety`
2. `smoothness`
3. `locality / contact relevance`
4. `extensibility for future TL`
5. `degeneracy safety`

## 3. Family A: Hard Local Set

Representative form:

- `nearest5_centroid`

Mechanism shape:

- rank enemies by local distance
- take the nearest `k`
- compute a direction from the centroid of that hard-selected set

### Strengths

- strong locality
- easy to explain
- preserves local encounter flavor
- easy to debug

### Weaknesses

- hard membership boundary
- sensitive to thin margin reordering near the `k` cutoff
- ties and near-ties can still fall back to iteration-order effects
- less graceful under mirrored degeneracy

### Engineering reading

This is a useful bounded default when locality must remain explicit.
But it is not the cleanest long-term answer if degeneracy safety becomes a first-class requirement.

## 4. Family B: Soft Local Set

Representative form:

- start from nearest `m`
- weight those `m` enemies smoothly by distance / local contactability
- compute a weighted local centroid

Mechanism shape:

```text
choose a local envelope first
then smooth inside that envelope
```

### Strengths

- keeps strong locality
- reduces the brittleness of hard nearest-`k`
- better degeneracy safety than a hard set
- still easy to reason about as a local contact structure

### Weaknesses

- still depends on the choice of local envelope
- can still inherit some edge sensitivity at the envelope boundary
- if over-smoothed, may drift toward quasi-global behavior

### Engineering reading

This is the most plausible intermediate family if the project wants:

- more stability than hard `nearest-k`
- without jumping all the way to a fully continuous field

It is a strong candidate region for future bounded comparison.

## 5. Family C: Fully Continuous Local Field

Representative form:

- every nearby enemy contributes
- contribution decays smoothly with local contactability

Mechanism shape:

```text
w_i = K(local_contactability_i)
dir = normalize(sum_i w_i * (x_i - c_self))
```

### Strengths

- strongest smoothness
- strongest degeneracy safety
- no hard “5th in / 6th out” jump
- cleanest substrate for future `TL` to bias later
- most consistent with current governance preference for continuous structures

### Weaknesses

- easiest family to let drift too global
- requires the most care to prevent silent semantic inflation
- harder to explain if the local kernel becomes too abstract

### Engineering reading

This is the strongest concept family if the main objective is:

- substrate purity
- graceful behavior under symmetry
- future extensibility for `TL`

But it requires the tightest discipline to ensure it remains:

- physically grounded
- semantically light
- locally contactable rather than doctrinally target-valued

## 6. Direct comparison

### Symmetry safety

- `hard local set`: weakest
- `soft local set`: better
- `fully continuous local field`: strongest

### Smoothness

- `hard local set`: weakest
- `soft local set`: moderate
- `fully continuous local field`: strongest

### Locality / contact relevance

- `hard local set`: strongest
- `soft local set`: strong
- `fully continuous local field`: variable, depends on kernel discipline

### Extensibility for future TL

- `hard local set`: acceptable but somewhat rigid
- `soft local set`: good
- `fully continuous local field`: strongest

### Degeneracy safety

- `hard local set`: weakest
- `soft local set`: better
- `fully continuous local field`: strongest

## 7. Current engineering preference

Current engineering preference is not:

- "pick the smartest discrete selector"

It is:

- move one step away from hard selection
- toward smoother local weighting
- while preserving a clean boundary against future `TL`

So the current concept ordering is:

```text
fully continuous local field
> soft local set
> hard local set
```

But this ordering is only about substrate quality under the current line.
It is **not** a doctrinal statement about future target preference.

## 8. Practical bounded takeaway

If the project wants the smallest change from where it is now:

- `soft local set` is the safest transitional direction

If the project wants the cleanest long-term substrate:

- `fully continuous local field` is the strongest conceptual direction

If the project wants to retain a simple explicit local default right now:

- `hard local set` can still be tolerated
- but only with the understanding that it is the weakest family on degeneracy safety

## 9. Boundary conclusion

This comparison does **not** authorize:

- implementation
- future `TL` semantics
- doctrinal target preference

It only clarifies the bounded substrate trade-off:

```text
Hard local sets preserve locality best but are weakest on degeneracy safety.
Fully continuous local fields are strongest on substrate quality but require the most boundary discipline.
Soft local sets are the most plausible bridge family between the two.
```
