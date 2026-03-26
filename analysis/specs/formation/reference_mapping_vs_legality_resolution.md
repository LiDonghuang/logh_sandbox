# Formation Reference Mapping vs Legality Resolution

Status: Draft Separation Note  
Authority: Governance-bounded engineering spec solidification  
Implementation: Runtime implementation not authorized by this document

## 1. Purpose

This note freezes one boundary that `v4b Candidate A` must not blur:

Formation Reference Mapping Policy != Final Feasibility / Legality Resolution

The first is upstream reference preparation.
The second is downstream movement legality handling.

## 2. FormationReferenceMappingPolicy v0.1

### Allowed Fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `mapping_mode` | `enum` | yes | How units map to reference slots. |
| `allow_reflow` | `bool` | yes | Whether remapping/reflow is allowed. |
| `debug_emit_expected_positions` | `bool` | optional | Whether expected positions are emitted for debug/inspection. |

### Candidate A Reading

For the current bounded review:

- `mapping_mode` should stay deterministic and fixture-bounded
- `allow_reflow` should remain `false`
- `debug_emit_expected_positions` may be used for fixture diagnostics only

## 3. Responsibilities of Reference Mapping

Reference mapping may do the following:

- consume `ObjectiveLocationSpec v0.1`
- consume `FormationFrame/Layout/Spacing` specs
- preserve stable unit order
- generate `expected_position_map`
- optionally emit debug expected positions

Reference mapping may **not** do the following:

- final min-spacing enforcement
- collision resolution
- boundary clipping
- projection overrides
- slot reassignment / role system / reflow

## 4. Responsibilities of Legality / Projection

Legality / projection may do the following:

- enforce feasibility
- enforce spacing constraints
- resolve overlap / collision conflicts
- respect boundary semantics

Legality / projection may **not** do the following:

- redefine expected slot identity
- reinterpret mapping ownership
- silently replace reference mapping
- reintroduce hidden doctrine through fallback geometry

## 5. Why The Separation Matters

If reference mapping and legality are blended together, three failures happen quickly:

1. expected-position logic becomes unreadable
2. projection burden can no longer be interpreted cleanly
3. Candidate A silently turns into a broad rewrite instead of a bounded upstream move

That is exactly what this round must avoid.

## 6. Candidate A Minimal Sequence

The bounded intended sequence is:

1. resolve objective location
2. derive fleet frame
3. prepare formation layout / spacing intent
4. map stable unit identity to expected positions
5. feed expected-position-directed restoration input upstream of movement
6. leave legality / projection unchanged

## 7. Explicit Non-Authorizations

This separation note does **not** authorize:

- generalized slot reassignment
- battle-path reference mapping
- new legality heuristics
- projection redesign
- 3D mapping language

## 8. Bottom Line

For `v4b Candidate A`, the first bounded move is upstream reference preparation only.

The legality layer stays exactly where it is:

- later in the pipeline
- behaviorally separate
- unchanged by this document
