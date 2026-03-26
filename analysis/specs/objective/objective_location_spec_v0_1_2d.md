# Objective Location Spec v0.1 (2D Only)

Status: Draft Spec Constraint  
Authority: Governance-bounded engineering spec solidification  
Implementation: Runtime implementation not authorized by this document

## 1. Scope

This document freezes the allowed 2D-only runtime-facing language for `ObjectiveLocationSpec v0.1`.

It is written for:

- `neutral_transit_v1`
- future bounded `v4b Candidate A` work
- possible future TL handoff into the same objective surface

It is **not** a 3D spec, battle-doctrine spec, or baseline-replacement document.

## 2. Purpose

`ObjectiveLocationSpec v0.1` answers one narrow question:

where should the fleet trend go, and what shared forward hint should upstream layers consume?

It must stay separate from:

- formation reference generation
- restoration-object choice
- low-level movement integration
- final legality / projection

## 3. Allowed Runtime-Facing Fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `anchor_point_xy` | `vec2_2d` | yes | Target location in world 2D coordinates. |
| `forward_hint_xy` | `vec2_2d` | yes | Shared forward-direction hint in world 2D coordinates. |
| `source_owner` | `enum` | yes | Declares who owns the objective source, e.g. `fixture` or `tl`. |
| `no_enemy_semantics` | `enum` | yes | Declares no-enemy handling; current required meaning is `enemy_term_zero`. |

## 4. Field Semantics

### `anchor_point_xy`

- Must represent the objective point itself.
- In `neutral_transit_v1`, this is the fixture objective point.
- It is a location field, not a tactic field.

### `forward_hint_xy`

- Must represent the fleet-level shared forward trend.
- In `neutral_transit_v1`, this should be derived from current fleet anchor toward `anchor_point_xy`.
- It is not a unit-level slot vector.
- It is not a hidden enemy-derived fallback channel.

### `source_owner`

Allowed `v0.1` readings:

- `fixture`
- `tl`

The point is ownership clarity, not a broad source registry.

### `no_enemy_semantics`

Current required reading:

- `enemy_term_zero`

Meaning:

- no-enemy state must not recreate an inward self-centering term through enemy-derived fallback
- the no-enemy fallback fix remains frozen

## 5. Consumption Contract

`ObjectiveLocationSpec v0.1` may be consumed by:

- formation-frame preparation
- fleet-level objective trend generation
- bounded fixture-only expected-position preparation

It must not be consumed as:

- implicit slot assignment
- implicit posture doctrine
- hidden centroid-restoration justification

## 6. Neutral Transit Binding

For `neutral_transit_v1`, the intended binding is:

- `anchor_point_xy` = fixture objective point
- `forward_hint_xy` = normalized 2D vector toward the objective
- `source_owner` = `fixture`
- `no_enemy_semantics` = `enemy_term_zero`

This keeps objective ownership explicit and preserves the current no-enemy fix.

## 7. Explicit Non-Fields

The following do **not** belong in `ObjectiveLocationSpec v0.1`:

- `z`
- `vec3`
- `vertical_axis_source`
- `world_up`
- unit-level slot targets
- legality / collision-resolution parameters
- any fallback that converts no-enemy state into own-centroid pull

## 8. 3D Note

Future 3D work may require richer orientation and reference language, but that belongs in future extension notes only.

It must not backflow into this `v0.1` 2D runtime-facing field table.
