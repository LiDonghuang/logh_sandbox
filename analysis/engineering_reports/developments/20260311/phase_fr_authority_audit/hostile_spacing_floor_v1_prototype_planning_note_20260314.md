# Hostile Spacing Floor v1 Prototype Planning Note

Date: 2026-03-14  
Status: Prototype planning note  
Scope: Bounded Phase 1 planning only. No implementation authorization.

## 1. Purpose

This note defines the next hostile-penetration prototype direction after the current limits of:

- `hybrid_v2_r125_d035_p020` as working Phase 1 reference only
- `penetration_cost_v1` as a geometry-safer but under-suppressing challenger
- `hostile_envelope_cost_v1` as a family that improved some broad-overlap readouts but still remained too weak relative to `min_unit_spacing`, or else created front-crushing side effects in earlier forms

The goal is to move to a mechanism that is:

- still continuous
- still local
- still non-personality
- still future-compatible with `RA`

but now clearly works at the **same layer as `min_unit_spacing`**, rather than as a softer movement-bias surrogate.

## 2. Current Diagnosis

The most important new engineering conclusion is:

```text
hostile penetration cost should not be weaker than min_unit_spacing by one mechanism layer
```

Current evidence supports that conclusion:

- `IntermixCoverage` has become a useful diagnostic for broad hostile overlap
- current hostile-envelope suppression can reduce or redistribute overlap
- but it still does not create a convincing hostile-side spacing lower bound
- when tuned too softly, fleets still interpenetrate broadly
- when handled too late, suppression and reprojection fight each other and front geometry gets crushed

So the current problem is no longer best described as:

```text
find a better soft rollback parameter
```

It is better described as:

```text
create a hostile-side spacing constraint that operates at the same layer as min_unit_spacing
without turning into a hard wall
```

## 3. Planning Target

The next bounded prototype should be:

```text
hostile_spacing_floor_v1
```

Its job is narrower and more same-layer than the prior families:

- identify the portion of tentative movement that would carry a unit deeper into hostile spacing-envelope violation
- continuously suppress only that inward portion
- leave outward and mostly lateral motion less affected

It should not decide:

- who should break through
- who should hold
- who has better support
- who is locally stronger

This remains a shared hostile-penetration substrate layer only.

For planning purposes, it should still be interpreted as:

```text
the future RA=5 baseline reference for hostile-side penetration cost
```

That means:

- the layer exists for all sides regardless of personality
- the current task is to set its neutral baseline strength
- future `RA` may later modulate tolerance toward continuing into that cost
- but `RA` is not implemented now and must not be smuggled in

## 4. Core Difference From Hostile Envelope Cost v1

`hostile_envelope_cost_v1` still behaved too much like:

- a pre-move speed bias
- or, in earlier forms, a post-hoc rollback

That was not enough.

The new prototype should instead operate on:

```text
the inward component of tentative displacement relative to hostile spacing envelope
```

So the mechanism is no longer:

```text
reduce generic movement intensity when hostile entry pressure is high
```

It becomes:

```text
continuously remove or cap the part of the tentative displacement
that would carry the unit deeper into hostile spacing-envelope penetration
```

This is the key shift.

## 5. Geometric Definition

Let:

- `r_h = hostile_spacing_floor_scale * min_unit_spacing`

with the initial prototype expected to keep `r_h` close to `1.0 * min_unit_spacing`.

For a given unit and tentative post-move position:

1. Collect hostile units within `r_h`
2. Build a local hostile inward normal from those hostile neighbors
3. Measure envelope penetration depth before and after tentative motion

One acceptable continuous definition is:

```text
depth_i(x) = max(0, (r_h - d_i(x)) / r_h)
```

where `d_i(x)` is distance from position `x` to hostile unit `i`.

Then combine local penetration continuously, for example with bounded soft aggregation rather than hard min/max.

The key planning requirement is:

- the reference scale is `min_unit_spacing`
- hostile envelope depth is measured directly in that neighborhood
- the prototype should not fall back to a weaker generic occupancy surrogate

## 6. Movement Injection

The first prototype should inject its cost **before** final movement write-back and before later geometric cleanup.

Preferred shape:

1. compute tentative displacement `delta`
2. decompose `delta` into:
   - inward component toward hostile spacing-envelope penetration
   - residual component
3. compute positive penetration increase from pre to tentative post
4. continuously suppress only the inward component
5. recompose the displacement

In compact form:

```text
delta = delta_residual + delta_inward
delta_inward_effective = (1 - c) * delta_inward
delta_effective = delta_residual + delta_inward_effective
```

where:

- `c` is a continuous cost factor
- `c` rises with positive penetration increase
- `c` stays in `[0, 1]`

This is not a hard wall:

- inward motion is suppressed, not absolutely forbidden
- outward motion is not punished
- lateral motion is only affected insofar as it contributes to deeper penetration

## 7. Parameter Discipline

The prototype should keep a strict two-parameter budget:

1. `hostile_spacing_floor_scale`
- hostile envelope radius as a multiplier of `min_unit_spacing`

2. `hostile_spacing_floor_strength`
- continuous suppression strength on positive inward penetration increase

No third shaping parameter in v1.

Do not add:

- support weighting
- force-ratio terms
- contrast terms
- angle class switches
- doctrine or posture semantics

## 8. Why This Is More Aligned With Current Diagnosis

This plan is more aligned with the current diagnosis for three reasons.

### A. Same-layer reference

It treats hostile penetration relative to `min_unit_spacing` itself, not as a softer generic field effect.

### B. Earlier action

It acts during tentative displacement formation, so it does not rely on post-hoc fighting between suppression and reprojection.

### C. Narrower meaning

It only says:

```text
deeper hostile-side spacing penetration should cost you movement
```

It does not say:

```text
who is justified in penetrating
```

That preserves future compatibility.

## 9. Observer / Validation Preparation

If implementation is later authorized, the first bounded comparison should remain small.

Comparison set:

- `off`
- `hybrid_v2_r125_d035_p020`
- `hostile_spacing_floor_v1`

Fixtures:

- `exception_2to1_close`
- `neutral_close`
- `neutral_long`

Keep:

- `boundary_enabled = false`
- current pre-TL substrate unchanged
- all-5 neutral personalities

Primary diagnostics:

- `IntermixCoverage`
- human animation review

Secondary diagnostics:

- `IntermixSeverity`
- `hostile_deep_intermix_ratio`
- `FrontCurv`
- `C_W_PShare`
- `first_contact_tick`

This preserves the current rule:

```text
intermix diagnostics are diagnostics, not acceptance proxies
```

## 10. Bottom Line

The next hostile-penetration prototype should stop acting like a generic soft movement bias and start acting like a continuous hostile-side spacing floor at the same layer as `min_unit_spacing`.

The cleanest bounded v1 plan is:

```text
measure hostile spacing-envelope penetration relative to min_unit_spacing,
identify the inward part of tentative displacement that would deepen that penetration,
and continuously suppress that inward component with one scale and one strength parameter
```

That is the narrowest next prototype shape that matches:

- the new geometry diagnosis
- current governance boundaries
- future `RA` compatibility
- and the current demand that hostile penetration cost must not sit one mechanism layer below `min_unit_spacing`
