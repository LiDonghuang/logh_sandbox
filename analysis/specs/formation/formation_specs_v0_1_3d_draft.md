# Formation Specs v0.1 (3D Draft)

Status: Structural Draft Only  
Authority: Governance-bounded Step 3 second-topic opening review  
Implementation: Runtime implementation is not authorized by this document

## 1. Scope

This document defines the minimum 3D-only draft language for formation reference.

It is written for:

- Step 3 second-topic opening review only
- contract/layering clarification before any 3D formation implementation
- preserving strict separation from objective, mapping, legality, movement, and viewer ownership

It is not:

- a runtime implementation spec
- a 3D slot-mapping implementation spec
- a 3D legality / projection spec
- a 3D movement or combat spec

## 2. Purpose

`Formation Specs v0.1 (3D Draft)` answers one narrow question:

what is the minimum reference geometry language needed to describe how a fleet should be organized in 3D space, without turning that language into movement, legality, or rendering ownership?

The formation contract must remain downstream of objective and upstream of mapping / legality.

## 3. Minimum Contract Surfaces

The minimum 3D draft language should stay split into:

- `FormationFrameSpec3D v0.1`
- `FormationLayoutSpec3D v0.1`
- `FormationSpacingSpec3D v0.1`

These are still reference-only surfaces.

## 4. FormationFrameSpec3D v0.1

### Allowed Draft Fields

| Field | Type | Required | Meaning |
| --- | --- | ---: | --- |
| `anchor_mode` | `enum` | yes | How the reference frame anchor is chosen. |
| `primary_axis_source` | `enum` | yes | Where the forward/reference axis comes from. |
| `up_reference_mode` | `enum` | yes | Minimal non-roll up reference used to derive the frame. |
| `frame_handedness` | `enum` | yes | Stable handedness declaration. |
| `degeneracy_policy` | `enum/struct` | yes | How unstable or near-zero axis cases are handled. |
| `frame_smoothing` | `struct` | no | Optional bounded smoothing for frame stability only. |

### Intended Reading

For the current bounded draft, the intended reading is:

- `anchor_mode`: fleet-centroid anchored
- `primary_axis_source`: objective-derived forward/reference axis
- `up_reference_mode`: fixed global up reference only
- `frame_handedness`: explicit and deterministic
- `degeneracy_policy`: explicit, bounded, deterministic

`up_reference_mode` is intentionally weaker than full attitude language.

It exists only so 3D can derive a stable frame without introducing roll/bank semantics.

## 5. FormationLayoutSpec3D v0.1

### Allowed Draft Fields

| Field | Type | Required | Meaning |
| --- | --- | ---: | --- |
| `layout_family` | `enum` | yes | Declares the reference layout family only. |
| `aspect_ratio_target` | `float/struct` | yes | Declares intended broad aspect tendency only. |
| `depth_layer_policy` | `enum` | yes | Declares whether/how depth layering is represented in the reference layout. |
| `rotation_policy` | `enum` | yes | Declares how the layout aligns to the reference frame. |
| `centering_policy` | `enum` | yes | Declares how the layout is centered around the chosen anchor. |
| `slot_identity_policy` | `enum` | yes | Declares how slot identity is expected to remain stable upstream. |

### Intended Reading

For the current bounded draft:

- `layout_family` should stay a reference family, not a runtime generator
- `aspect_ratio_target` should remain coarse and declarative
- `depth_layer_policy` is allowed only because 3D needs a depth reading, not because extents/volume semantics are now open
- `rotation_policy` aligns the layout to the reference frame
- `slot_identity_policy` should remain deterministic and conservative

## 6. FormationSpacingSpec3D v0.1

### Allowed Draft Fields

| Field | Type | Required | Meaning |
| --- | --- | ---: | --- |
| `expected_axis_spacings_xyz` | `vec3_3d` | yes | Intended spacing along the reference axes only. |
| `spacing_mode` | `enum` | yes | Declares spacing interpretation mode. |
| `slot_fill_order` | `enum` | yes | Declares deterministic traversal order for reference slots. |

### Intended Reading

`FormationSpacingSpec3D v0.1` should still mean:

- spacing belongs to formation reference intent
- spacing does not become legality / collision resolution
- spacing remains deterministic and upstream

## 7. What Counts As Formation Reference Only

These draft fields are allowed only as formation reference language:

- anchor selection for the reference frame
- reference-axis derivation
- coarse layout family / aspect tendency
- deterministic slot-identity expectation
- intended axis-aligned spacing

They do not authorize:

- slot assignment execution
- final feasibility checks
- projection
- collision handling
- runtime steering rules

## 8. Explicit Non-Fields

The following should **not** appear in `Formation Specs v0.1 (3D Draft)`:

- roll
- bank
- attitude quaternion
- full-axis package with independently authored secondary/tertiary axes
- principal extents targets
- anisotropy ratio packages
- legality / feasibility fields
- collision / boundary fields
- target preference semantics
- doctrine / posture semantics
- viewer rendering fields
- camera hints
- glyph / display attributes

## 9. Boundary Note

This 3D draft keeps the same reading discipline established in 2D:

- objective answers where to go
- formation answers reference geometry only
- mapping answers assignment to reference slots
- legality answers feasibility / projection

The 3D version adds only the minimum extra language needed to avoid pretending that 3D is still a 2D perpendicular-frame problem.
