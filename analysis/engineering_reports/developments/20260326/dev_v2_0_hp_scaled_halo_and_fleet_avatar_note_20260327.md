# dev_v2.0 HP-Scaled Fleet Halo + Screen-Space Fleet Avatar

Date: 2026-03-27  
Scope: `viz3d_panda/` viewer-local presentation only

## Identity

This viewer-local turn now includes three bounded presentation results:

1. fleet halo radius is HP-scaled
2. fleet avatar is a fixed-size screen-space overlay
3. dual-layer unit rendering now includes a minimal transparency-order correction so the inner cluster is less often swallowed by the transparent outer shell

It does not change:

- runtime schema
- replay protocol
- position frame structure
- simulation ownership
- 3D world-object semantics

## HP-Scaled Fleet Halo

Current halo radius rule is:

- compute a first-frame baseline per fleet:
  - `initial_halo_radius`
  - `initial_alive_total_hp`
- each frame:
  - `halo_radius = initial_halo_radius * sqrt(current_alive_total_hp / initial_alive_total_hp)`

Halo center still uses the current-frame fleet geometric centroid.

## Fleet Avatar Overlay

Fleet avatar is rendered as a fixed-size screen-space overlay, not as a world-space 3D object.

Current behavior:

- avatar source comes from existing scenario/prepared-side avatar ids
- viewer metadata carries only a small `fleet_avatars` mapping
- the app resolves avatar files from `visual/avatars`
- avatar keeps a fixed on-screen `4:5` portrait ratio
- avatar position is anchored above the fleet by projecting fleet position into screen space and using a bounded vertical offset
- avatar size does not grow or shrink with 3D zoom
- avatar visibility now has a viewer-local keyboard toggle:
  - default: on
  - key: `P`
- avatar card now includes:
  - faction-colored border
  - dark matte backing
  - light faction-colored highlight layer

This means the avatar:

- follows fleet movement
- does not flip with 3D orbit
- does not scale with 3D zoom like a world-space object
- can be hidden without changing simulation or replay data

## Dual-Layer Cluster Visibility Correction

The inner fleet cluster previously could be swallowed by the transparent outer wedge from some camera angles.

Current minimal correction:

- outer token depth-write disabled
- inner cluster depth-write disabled
- existing transparent-bin ordering retained

This is a viewer-local transparency-order fix only. It does not change semantics, replay data, or unit geometry ownership.

## Files Touched

- `viz3d_panda/replay_source.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/app.py`

## Structured Summary

- Engine Version: `dev_v2.0`
- Modified Layer: viewer-local presentation only
- Affected Parameters: none user-facing beyond local overlay toggles
- New Variables Introduced: viewer-local replay metadata field `fleet_avatars`
- Cross-Dimension Coupling: none beyond existing replay consumption and scenario-side avatar id reuse
- Mapping Impact: none
- Governance Impact: extends the authorized halo/avatar presentation work while staying consumer-only
- Backward Compatible: yes

Summary
- Halo area now scales approximately with alive total HP.
- Halo center remains tied to current-frame fleet centroid.
- Fleet avatar is fixed-size screen-space `4:5`, not world-space.
- Avatar supports a viewer-local `P` toggle and uses faction-colored card framing.
- A minimal transparency-order correction reduces inner-cluster occlusion by the outer shell.
- No runtime or position-frame widening was introduced.
