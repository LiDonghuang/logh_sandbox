# ODW Runtime Mapping Review v1.0

Status: Active review  
Scope: Concept-to-runtime mapping review for `ODW`  
Authority Context: Governance-authorized review phase  
Implementation: Not authorized by this document

## I. Purpose

This document reviews how `ODW` should enter runtime behavior under current canonical constraints.

The purpose is to identify one clean, bounded, interpretable runtime role for `ODW`.

This is not a baseline-replacement document.

It is not a mechanism activation document.

It is a review document used to define the first acceptable implementation direction.

## II. Canonical Constraints

The following constraints are binding.

### 1. ODW remains a personality preference parameter

`ODW` must not be interpreted as:

- combat strength
- tactical skill
- execution quality
- intelligence
- capability modifier

It may only express:

```text
offense / defense preference
```

### 2. ODW must not directly create formations

`ODW` must not be mapped as:

- direct wedge selector
- direct concave selector
- direct line selector
- formation template switch

Formation geometry must remain:

```text
emergent property of the movement vector field
```

### 3. ODW must remain orthogonal to PD and RT

For the first implementation, `ODW` must not directly modify:

- pursuit trigger threshold
- deep-pursuit entry
- retreat trigger threshold
- retreat entry

Those responsibilities belong primarily to:

- `PD` for pursuit willingness
- `RT` for retreat willingness

## III. Current Legacy Status

Engineering audit confirms that the historical ODW path should not be treated as an active baseline mechanism.

Reference:

- `analysis/engineering_reports/developments/20260308/phase_runtime_collapse_signal_source_evaluation/odw_tl_legacy_runtime_path_audit.md`

Summary:

- `ODW` exists in archetype data and personality loading
- combat code contains a unit-level ODW bias formula
- but active initialization does not inject archetype ODW into `UnitState`
- therefore the active runtime path does not currently use archetype ODW as intended

This legacy path should be treated as:

```text
historical trace only
```

It should not be repaired as the basis for the next ODW mechanism.

## IV. Recommended Runtime Role

The recommended runtime role of `ODW` is:

```text
posture bias
```

More precisely:

```text
offense / defense posture bias inside movement behavior
```

This means `ODW` should influence:

- how strongly pressure is maintained versus relaxed
- how much forward pressure is distributed across the active front
- how much structure-preservation competes with attack posture

It should not initially influence:

- pursuit willingness
- retreat willingness
- target semantics
- combat effectiveness

## V. Preferred Insertion Path

The preferred first insertion path is:

```text
movement-layer posture bias
```

Specifically:

`ODW` should bias how forward pressure is distributed laterally across the fleet front.

This is the cleanest first path because:

1. it changes posture rather than thresholds
2. it operates through the movement vector field
3. it allows geometry consequences to emerge rather than be selected directly
4. it avoids turning `ODW` into a second `PD`, `RT`, `MB`, or `FR`

## VI. Minimal Prototype Path

The first prototype should use only one runtime insertion point:

```text
ODW-driven lateral pressure distribution bias in movement
```

The intended behavior is:

- higher offensive ODW:
  - relatively stronger maintained forward pressure
  - narrower or more concentrated pressure distribution
  - more attack-posture persistence while still remaining inside movement dynamics
- higher defensive ODW:
  - relatively flatter or broader pressure distribution
  - greater structure-preservation tendency
  - less aggressive forward posture without directly invoking retreat

Important:

This is still:

```text
vector bias
```

not:

```text
formation command
```

Any wedge-like, flat-front, or concave tendency must remain an emergent result.

## VII. Rejected First-Cut Paths

The following insertion paths are rejected for the first implementation.

### 1. Combat formula insertion

Rejected because it makes `ODW` look like:

```text
hidden combat strength modifier
```

This violates canonical intent.

### 2. Pursuit-threshold insertion

Rejected because it makes `ODW` overlap with:

- `PD`

This risks turning `ODW` into a second pursuit parameter.

### 3. Retreat-threshold insertion

Rejected because it makes `ODW` overlap with:

- `RT`

This risks turning `ODW` into a second retreat parameter.

### 4. Targeting-logic insertion

Rejected for the first cut because:

- `TL` should remain independently meaningful
- combining `ODW` with target semantics too early would blur parameter boundaries

### 5. Direct formation selection

Rejected because it violates the Formation Geometry Doctrine directly.

## VIII. Orthogonality Check

The proposed prototype preserves orthogonality as follows.

### Versus `PD`

`PD` answers:

```text
how willing is the fleet to continue pursuit
```

Proposed `ODW` answers:

```text
what attack/hold posture does the fleet express while moving
```

### Versus `RT`

`RT` answers:

```text
when is retreat acceptable
```

Proposed `ODW` does not decide retreat.

It only biases posture before such thresholds are considered.

### Versus `MB`

`MB` answers:

```text
how movement bias is expressed directionally
```

Proposed `ODW` does not replace mobility bias.

Instead, it biases offensive versus defensive posture inside the movement field.

### Versus `FR`

`FR` answers:

```text
how strongly formation deformation is resisted
```

Proposed `ODW` does not define rigidity.

It biases pressure posture, while `FR` continues to govern deformation resistance.

## IX. Engineering Recommendation

Engineering should proceed in this order:

1. treat the historical ODW combat path as legacy only
2. do not repair the legacy combat-bias path
3. design one bounded prototype in the movement layer
4. test only whether ODW creates interpretable offense/defense posture difference with `PD` and `RT` fixed

The first review target is therefore:

```text
ODW as posture bias through movement-vector pressure distribution
```

That is currently the cleanest path consistent with canonical doctrine.
