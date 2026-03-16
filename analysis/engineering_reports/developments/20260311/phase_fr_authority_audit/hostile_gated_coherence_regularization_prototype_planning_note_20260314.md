# Hostile-Gated Coherence Regularization Prototype Planning Note

Date: 2026-03-14  
Status: Prototype planning note  
Scope: Bounded test-only planning only. No implementation authorization.

## 1. Purpose

This note defines the first minimal prototype plan for:

```text
hostile-gated coherence regularization
```

The goal is to preserve the accepted same-layer hostile-spacing direction while preventing overlap suppression from being purchased by same-fleet tearing.

## 2. Minimal Prototype Form

The first prototype should stay extremely small:

- start from the existing tentative local displacement
- detect local hostile-side spacing pressure
- build a hostile-driven local correction only when that pressure exists
- use nearby same-fleet geometry only to regularize or smooth that hostile-driven correction

So same-fleet coherence does not become an independent correction field.

## 3. Intended Mechanism Shape

The first prototype should work like this:

1. collect nearby hostile spacing-conflict sources inside a local envelope
2. build one hostile-driven local correction from those sources
3. inspect nearby same-fleet local spacing/coherence geometry
4. attenuate, smooth, or redistribute the hostile-driven correction so it does not tear same-fleet geometry apart
5. apply only the minimum corrected local displacement needed to reduce deeper hostile-side spacing violation

This remains:

- local
- continuous
- symmetric
- low-semantic
- test-only

## 4. Parameter Roles

The first prototype should keep only two parameter roles:

- `scale`
  - shared local envelope scale relative to `min_unit_spacing`
- `strength`
  - shared correction strength for the hostile-driven correction after coherence regularization

No third shaping parameter should be added in the first attempt.

## 5. Why This Differs from Failed Co-Resolution v1

`co_resolution_v1` failed because same-fleet coherence terms became an active correction source of their own.

The new prototype should not do that.

Its intended structure is:

```text
hostile pressure first,
coherence regularization second
```

not:

```text
hostile correction field plus friendly correction field
```

## 6. Minimal Validation Shape

The first validation should remain narrow:

- `off`
- `hybrid_v2_r125_d035_p020`
- failed `hostile_spacing_floor_v2`
- failed `hostile_spacing_co_resolution_v1`
- one new hostile-gated coherence-regularization prototype point

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

No large DOE should be opened until the first prototype point is shown to be mechanically stable.

## 7. One-Line Conclusion

```text
the next bounded prototype should keep hostile-side spacing as the only active trigger and use same-fleet coherence only as a local regularizer on that correction, so overlap is reduced without turning coherence itself into a new source of fleet tearing.
```
