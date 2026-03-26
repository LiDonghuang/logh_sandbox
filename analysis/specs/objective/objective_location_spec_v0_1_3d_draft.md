# Objective Location Spec v0.1 (3D Draft)

Status: Structural Draft Only  
Authority: Governance-bounded Step 3 opening review  
Implementation: Runtime implementation is not authorized by this document

## 1. Scope

This document defines the minimum 3D-only draft language for `ObjectiveLocationSpec v0.1`.

It is written for:

- Step 3 opening review only
- a bounded 3D neutral-transit first carrier
- ownership/layering clarification before any 3D mechanism turn

It is not:

- a runtime implementation spec
- a 3D movement spec
- a 3D formation spec
- a 3D combat or legality spec

## 2. Purpose

`ObjectiveLocationSpec v0.1 (3D Draft)` answers one narrow question:

where should the fleet trend go in 3D space?

At most, it may also carry one weak transit-direction hint.

It must stay separate from:

- formation frame construction
- legality / projection
- combat or doctrine semantics
- viewer rendering

## 3. Allowed Draft Fields

| Field | Type | Required | Meaning |
| --- | --- | ---: | --- |
| `anchor_point_xyz` | `vec3_3d` | yes | 3D target point in world coordinates. |
| `source_owner` | `enum` | yes | Declares who owns the objective source. |
| `objective_mode` | `enum` | yes | Declares the current minimal objective shape. |
| `no_enemy_semantics` | `enum` | yes | Declares no-enemy handling. |
| `transit_axis_hint_xyz` | `vec3_3d` | no | Optional weak transit-axis hint only. |

## 4. Field Semantics

### `anchor_point_xyz`

- Must represent a single 3D objective anchor point.
- Must answer where the fleet should trend.
- Must not encode legality, combat intent, or formation layout.
- Must not expand into waypoint chains in `v0.1`.

### `source_owner`

Allowed `v0.1` readings:

- `fixture`
- `tl`

This stays intentionally small. The point is ownership clarity, not a large owner registry.

### `objective_mode`

Allowed `v0.1` reading:

- `point_anchor`

This means the first 3D objective language is explicitly limited to “trend toward one point.”

### `no_enemy_semantics`

Required `v0.1` reading:

- `enemy_term_zero`

Meaning:

- no-enemy state must not silently recreate inward fallback
- missing enemy context must not become hidden self-centering semantics

### `transit_axis_hint_xyz` (optional)

- May provide one weak transit-direction hint.
- Must not become a full frame definition.
- Must not encode roll, bank, second-axis construction, or formation orientation.
- If it complicates the first carrier, it may remain unused in `v0.1`.

## 5. Consumption Contract

This draft may be consumed by:

- bounded neutral-transit objective handoff
- future runtime-owned trend preparation
- replay transfer of already-owned objective results

It must not be consumed as:

- formation frame authority
- legality / feasibility authority
- doctrine or posture authority
- viewer rendering authority

## 6. First-Carrier Binding

For the bounded 3D neutral-transit first carrier, the intended binding is:

- `anchor_point_xyz` = fixture objective point
- `source_owner` = `fixture`
- `objective_mode` = `point_anchor`
- `no_enemy_semantics` = `enemy_term_zero`
- `transit_axis_hint_xyz` = optional only, and may be omitted

This keeps the first 3D carrier narrow and prevents the objective contract from quietly becoming a broader frame language.

## 7. Explicit Non-Fields

The following do not belong in `ObjectiveLocationSpec v0.1 (3D Draft)`:

- formation frame
- roll / bank
- secondary-axis construction
- principal extents
- anisotropy ratios
- spacing policy
- legality / feasibility data
- target preference semantics
- posture / doctrine semantics
- viewer rendering fields
- camera hints
- HP / glyph / display attributes

## 8. Boundary Note

This draft defines a minimum 3D objective contract only.

It does not authorize:

- 3D movement implementation
- 3D formation implementation
- 3D combat or targeting implementation
- 3D legality / projection implementation
