# Hostile Spacing Floor v1 Failure and v2 Framing Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Phase 1 hostile penetration follow-up only. No implementation authorization.

## 1. Purpose

This note records why `hostile_spacing_floor_v1` is not yet a sufficient answer, even though it improved one important failure mode, and why any `v2` continuation should be reviewed before implementation.

This is not:

- a baseline-replacement request
- a governance directive
- a request to reopen large DOE
- an implementation request

It is only a short engineering framing note for the next bounded decision.

## 2. Current Finding

`hostile_spacing_floor_v1` improved early front-crushing relative to the earlier envelope-style family, but it still does not create a sufficiently strong hostile-side spacing lower bound.

The user-facing summary is:

```text
front crushing improved, but broad hostile overlap remained too severe
```

That judgment is supported by the current paired checks.

## 3. What v1 Did Improve

Relative to `off`, and often relative to `hybrid_v2`, `hostile_spacing_floor_v1` reduced early `IntermixCoverage`.

Examples:

- `exception_2to1_close`
  - `cov20_30`
    - `off = 0.498`
    - `hybrid_v2 = 0.435`
    - `spacing_floor_v1 = 0.409`
- `neutral_close`
  - `cov20_30`
    - `off = 0.435`
    - `hybrid_v2 = 0.353`
    - `spacing_floor_v1 = 0.323`

So `v1` is not a null direction. It did suppress some rapid broad overlap.

## 4. Why v1 Still Fails

The same runs also show that overlap remains too high once contact broadens.

Example:

- `neutral_close`
  - `cov21_50`
    - `off = 0.599`
    - `hybrid_v2 = 0.643`
    - `spacing_floor_v1 = 0.607`

That is still visually far too high for a mechanism intended to behave at the same layer as `min_unit_spacing`.

`v1` also does not beat `hybrid_v2` on penetration-depth style diagnostics:

- `exception_2to1_close`
  - `sev21_120`
    - `hybrid_v2 = 0.0442`
    - `spacing_floor_v1 = 0.0533`
  - `deep21_120`
    - `hybrid_v2 = 0.0169`
    - `spacing_floor_v1 = 0.0326`

So the current engineering judgment is:

```text
hostile_spacing_floor_v1 is closer to the right problem than prior soft rollback families,
but its current mechanism form is still too weak to serve as a credible hostile-side spacing floor
```

## 5. Likely Mechanism Reason

`v1` clips tentative movement only along a single inward hostile-facing axis derived from local hostile geometry.

That helps with direct inward penetration, but it leaves too much:

- tangential sliding
- local weaving
- multi-normal overlap growth during broad contact

So the mechanism reduces one penetration channel while still allowing too much hostile-side overlap to accumulate through the remaining displacement components.

This is why the geometry can look less crushed while still looking too interpenetrated.

## 6. Why v2 Needs Review First

Any plausible `v2` is unlikely to be "the same formula with one better parameter."

The next step will likely need to move toward one of these forms:

- a joint hostile-spacing displacement constraint over multiple nearby hostile units
- a projection-aware local hostile-spacing solve
- a constrained tentative-displacement resolution rather than single-axis clipping

That is still compatible with the current phase if kept:

- continuous
- local
- symmetric
- low-semantic
- test-only

But it is closer to movement / local displacement resolution than the current `v1` family. That is why it should be reviewed before implementation.

## 7. Current Working Position

The safest current position is:

- keep `hybrid_v2_r125_d035_p020` as the working Phase 1 reference
- keep `IntermixCoverage` as an important diagnostic
- treat `hostile_spacing_floor_v1` as a useful but insufficient first same-layer attempt
- do not reopen large DOE on `v1`
- review a `v2` mechanism framing before writing code

## 8. One-Line Conclusion

```text
hostile_spacing_floor_v1 improved the earlier front-crushing failure,
but it still does not create a sufficiently credible hostile-side spacing lower bound;
any v2 continuation should be reviewed as a new mechanism form, not as another parameter tweak
```
