# Hostile Spacing Floor v2 Mechanism-Form Note

Date: 2026-03-14  
Status: Engineering note  
Scope: Mechanism-form review only. No implementation authorization.

## 1. Purpose

This note defines the proposed mechanism form for `hostile_spacing_floor_v2` after the insufficiency of `hostile_spacing_floor_v1`.

This is not:

- a baseline proposal
- a DOE plan
- an implementation request

It is only a bounded `v2` mechanism-form note.

## 2. Root Difference from v1

`v1` clips movement mainly along one inward hostile-facing axis.

`v2` would instead resolve hostile spacing pressure against **multiple nearby hostile units at once**, so that the mechanism no longer suppresses only one penetration channel while leaving tangential sliding and multi-normal overlap growth mostly untouched.

In short:

```text
v1 = single-axis inward clipping
v2 = local multi-hostile spacing resolution
```

## 3. Overlap Channel v2 Tries to Cover

`v1` partially covers direct inward penetration, but does not adequately cover:

- tangential sliding
- local weaving
- broad-contact multi-normal overlap growth

`v2` is intended to reduce those remaining channels without turning hostile spacing into a hard wall.

## 4. Why v2 Is Still Same-Layer, Not Movement Rewrite

`v2` still belongs to the same-layer hostile spacing floor family because it would:

- use `min_unit_spacing` as the base geometric scale
- operate only on hostile-side local spacing conflict
- modify only the tentative local displacement needed to avoid deeper hostile spacing violation
- avoid target selection, support semantics, breakthrough logic, or doctrine logic

So the mechanism still answers only:

```text
how much of this tentative movement would deepen hostile-side spacing violation?
```

It does not answer:

```text
should this force keep breaking through?
```

## 5. Required Style Constraints

`v2` must remain:

- continuous
- local
- symmetric
- low-semantic
- test-only

It must not introduce:

- support-aware shaping
- front-value logic
- force-ratio logic
- discrete contact modes
- doctrine-like behavior selection

## 6. Minimal Form Preference

The preferred `v2` form is:

- a local hostile-spacing displacement correction over nearby hostile units
- using no more than two parameters

Recommended parameter roles:

- `scale`
- `strength`

No third shaping parameter should be introduced in the first `v2` attempt.

## 7. One-Line Conclusion

```text
hostile_spacing_floor_v2 should move from single-axis inward clipping to local multi-hostile spacing resolution, while remaining same-layer, continuous, local, symmetric, and low-semantic.
```
