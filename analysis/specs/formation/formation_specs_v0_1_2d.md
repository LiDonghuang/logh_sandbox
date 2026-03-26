# Formation Specs v0.1 (2D Only)

Status: Draft Spec Constraint  
Authority: Governance-bounded engineering spec solidification  
Implementation: Runtime implementation not authorized by this document

## 1. Scope

This document freezes the allowed 2D-only runtime-facing language for:

- `FormationFrameSpec v0.1`
- `FormationLayoutSpec v0.1`
- `FormationSpacingSpec v0.1`

The scope is bounded to `v4b Candidate A` preparation for single-fleet neutral transit.

## 2. Why This Spec Exists

After `v4a`, the main surviving issue is not old shaping-family tuning.
It is the restoration object.

So the first rebuild question is:

what minimal formation-aware reference description can exist upstream of movement without opening a broad formation engine?

## 3. FormationFrameSpec v0.1

### Allowed Fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `anchor_mode` | `enum` | yes | How the fleet frame anchor is chosen in 2D. |
| `primary_axis_source` | `enum` | yes | Where the forward axis comes from. |
| `secondary_axis_rule` | `enum` | yes | How the lateral axis is derived in 2D. |
| `frame_handedness` | `enum` | yes | Stable 2D handedness declaration. |
| `degeneracy_policy` | `enum/struct` | yes | How near-zero or unstable axis cases are handled. |
| `frame_smoothing` | `struct` | optional | Optional bounded smoothing for frame stability. |

### Candidate A Reading

For the current bounded review, the intended reading is:

- `anchor_mode`: fleet-centroid anchored
- `primary_axis_source`: objective `forward_hint_xy`
- `secondary_axis_rule`: 2D perpendicular-to-primary
- `frame_handedness`: fixed 2D handedness
- `degeneracy_policy`: explicit, bounded, and deterministic

`frame_smoothing` may exist as an optional field, but it is not required for the first narrow implementation request.

## 4. FormationLayoutSpec v0.1

### Allowed Fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `layout_family` | `enum` | yes | Must be `rect_lattice_2d`. |
| `aspect_ratio_target` | `float` | yes | 2D compatibility field for width-depth tendency. |
| `rotation_policy` | `enum` | yes | How the layout aligns to the frame. |
| `centering_policy` | `enum` | yes | How the layout is centered around the chosen anchor. |
| `dim_policy` | `enum` | yes | How row/column counts are resolved in 2D. |
| `slot_identity_policy` | `enum` | yes | How unit identity stays tied to layout slots. |

### Candidate A Reading

For the current bounded review, the intended reading is:

- `layout_family = rect_lattice_2d`
- `aspect_ratio_target` stays a 2D compatibility field only
- `rotation_policy` aligns the layout to the primary axis
- `centering_policy` keeps the layout centered on the frame anchor
- `dim_policy` stays deterministic
- `slot_identity_policy = fixed_initial_order`

This is enough for a bounded expected-position anchor without opening slot reassignment or a generalized formation system.

## 5. FormationSpacingSpec v0.1

### Allowed Fields

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `expected_axis_spacings_xy` | `vec2_2d` | yes | Intended spacing along frame primary/secondary axes. |
| `spacing_mode` | `enum` | yes | Declares spacing interpretation mode. |
| `slot_fill_order` | `enum` | yes | Declares deterministic slot traversal order. |

### Candidate A Reading

For the current bounded review, this spec exists to declare expected spacing, not to perform final collision handling.

That means:

- spacing belongs to formation reference intent
- spacing does not replace separation/projection
- spacing must stay deterministic and 2D-only

## 6. Explicit Non-Fields

The following do **not** belong in these `v0.1` runtime-facing tables:

- `z`
- `vec3`
- `vertical_axis_source`
- `world_up`
- `expected_vertical_spacing`
- runtime-facing `principal_extents_target`
- runtime-facing `anisotropy_ratios`
- roll / bank / volume-lattice selectors

## 7. Canonical Discipline Note

These specs define upstream reference language only.

They do **not** mean:

- FR becomes a formation generator
- movement becomes a formation engine
- legality becomes reference mapping

FR remains resistance to deformation.
The formation geometry is still expected to emerge through the vector field once the restoration object is no longer centroid-only.
