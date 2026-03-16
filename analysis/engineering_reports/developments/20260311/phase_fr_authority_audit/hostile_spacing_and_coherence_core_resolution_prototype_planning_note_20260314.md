# Hostile Spacing and Coherence Co-Resolution Prototype Planning Note

Date: 2026-03-14  
Status: Prototype planning note  
Scope: Bounded test-only planning only. No implementation authorization.

## 1. Purpose

This note defines the first minimal prototype plan for:

```text
local spacing-and-coherence co-resolution
```

It follows the accepted framing that the next viable direction is not stronger hostile-side spacing alone, but same-layer co-resolution of:

- hostile-side spacing conflict
- same-fleet spacing/coherence conflict

## 2. Minimal Prototype Form

The preferred first prototype should remain extremely small:

- start from the existing tentative local displacement
- collect nearby hostile spacing-conflict sources
- collect nearby same-fleet spacing/coherence conflict sources
- produce one combined local correction on the tentative displacement

The prototype should not:

- infer support semantics
- infer front value
- infer breakthrough worthiness
- rewrite fleet-level movement logic

## 3. Intended Mechanism Shape

The first prototype should work like this:

1. compute hostile local spacing conflict from nearby hostile units inside a spacing envelope
2. compute same-fleet local spacing/coherence conflict from nearby friendly units inside a matching local envelope
3. combine those two local conflict fields into a single continuous displacement correction
4. apply only the minimum local correction needed to reduce deeper hostile-side spacing violation without tearing same-fleet geometry apart

This remains:

- local
- continuous
- symmetric
- low-semantic
- test-only

## 4. Parameter Roles

The prototype should keep only two parameter roles:

- `scale`
  - shared local envelope scale relative to `min_unit_spacing`
- `strength`
  - shared correction strength for the combined local co-resolution

No third shaping parameter should be added in the first attempt.

## 5. Why This Is Different from Failed v2

`hostile_spacing_floor_v2` failed because it resolved multiple hostile spacing conflicts without co-resolving same-fleet spacing/coherence at the same effective layer.

The new prototype differs by design:

- hostile conflict alone no longer owns the local correction
- same-fleet geometry preservation enters the same local solve

So the goal is no longer:

```text
reduce overlap by local hostile-only resolution
```

It is:

```text
reduce overlap without paying for it by fleet shattering
```

## 6. Minimal Validation Shape

The first validation should remain narrow:

- `off`
- `hybrid_v2_r125_d035_p020`
- failed `hostile_spacing_floor_v2` point as reference
- one new co-resolution prototype point

Fixtures should remain:

- `exception_2to1_close`
- `neutral_close`
- `neutral_long`

Primary diagnostics:

- `IntermixCoverage`
- same-fleet fragmentation / connected-component count
- same-fleet minimum distance relative to `min_unit_spacing`

Secondary diagnostics:

- `IntermixSeverity`
- `FrontCurv`
- `first_contact_tick`

No large DOE should be opened until the first co-resolution prototype form is shown to be mechanically stable.

## 7. One-Line Conclusion

```text
the next bounded prototype should co-resolve hostile-side spacing conflict and same-fleet spacing/coherence in one local continuous correction, using only scale and strength, so overlap is not reduced by shattering fleet geometry.
```
