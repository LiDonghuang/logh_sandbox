# Hostile Spacing Floor v2 Failure Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Bounded prototype readout only. No implementation authorization.

## 1. Purpose

This note records the first-failure result of `hostile_spacing_floor_v2`.

It is not:

- a baseline proposal
- a governance directive
- a request to reopen DOE

## 2. Main Finding

`hostile_spacing_floor_v2` reduced broad hostile overlap coverage, but did so by over-fragmenting fleet geometry while still failing to preserve `min_unit_spacing`.

In short:

```text
coverage improved, but the fleets were torn apart and spacing still collapsed
```

## 3. Current Evidence

Using the current active point:

- `hostile_spacing_floor_v2.scale = 1.0`
- `hostile_spacing_floor_v2.strength = 1.0`

and the current active fixture family, the key comparison was:

- mean `IntermixCoverage 20..50`
  - `off = 0.712`
  - `hybrid_v2 = 0.627`
  - `spacing_floor_v1 = 0.543`
  - `spacing_floor_v2 = 0.269`

So `v2` clearly suppresses broad overlap more strongly.

However, the same runs show strong fragmentation:

- mean connected components per fleet over `t20..50`
  - A:
    - `off = 2.81`
    - `hybrid_v2 = 2.45`
    - `spacing_floor_v1 = 2.29`
    - `spacing_floor_v2 = 3.77`
  - B:
    - `off = 1.94`
    - `hybrid_v2 = 1.35`
    - `spacing_floor_v1 = 2.29`
    - `spacing_floor_v2 = 3.16`

This is not just harmless reshaping. It is a real shattering tendency.

`min_unit_spacing` also remains badly violated:

- `min_unit_spacing = 2.0`
- mean same-fleet minimum distance over `t20..50`
  - A:
    - `spacing_floor_v2 = 0.390`
  - B:
    - `spacing_floor_v2 = 0.328`
- minimum observed same-fleet distance over `t20..50`
  - A:
    - `spacing_floor_v2 = 0.018`
  - B:
    - `spacing_floor_v2 = 0.018`

So the current v2 point does not create a credible spacing floor.

## 4. Mechanism Interpretation

The likely mechanism failure is:

- `v2` resolves multiple hostile spacing conflicts locally
- but does not co-resolve same-fleet spacing/coherence at the same layer
- so the fleet can be pulled apart by several local hostile conflict sources at once

That means `v2` suppresses overlap partly by tearing geometry apart, not by establishing a stable hostile-side spacing lower bound.

## 5. Current Engineering Judgment

The correct reading is:

- `hostile_spacing_floor_v2` is a meaningful mechanism-form experiment
- but its first prototype point is not acceptable
- this is not a case for small parameter patching

The safer conclusion is:

```text
multi-hostile local spacing resolution cannot be accepted in this form
unless same-fleet spacing/coherence is preserved at the same effective layer
```

## 6. One-Line Conclusion

```text
hostile_spacing_floor_v2 reduced overlap coverage, but failed by fragmenting fleets and still violating min_unit_spacing; the current v2 prototype point should be treated as a failed first attempt, not as a tunable near-solution.
```
