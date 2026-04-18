# step3_3d_pr6_halo_summary_interpolation_and_engagement_owner_reroot_20260410

## Scope

- baseline/runtime: viewer integration + runtime-settings structure cleanup
- test-only or harness-only: cross-layer
- protocol or policy only: no

## Summary

This round completed two cleanup items:

1. fleet halo interpolation no longer recomputes fleet centroid from live node
   positions; it now stays on the maintained `fleet_body_summary` export by
   blending current-frame and next-frame summary rows
2. engaged/attack-direction movement allowances were rerooted out of
   `runtime.movement.v4a.*` test-only space into maintained runtime settings
   under `runtime.movement.engagement.*`

## Result

### Viewer

- interpolation no longer creates a second fleet-body owner inside
  `viz3d_panda/unit_renderer.py`
- `fleet_body_summary` is now used for normal placement and interpolation

### Settings ownership

Moved from:

- `runtime.movement.v4a.engaged_speed_scale`
- `runtime.movement.v4a.attack_speed_lateral_scale`
- `runtime.movement.v4a.attack_speed_backward_scale`

To:

- `runtime.movement.engagement.engaged_speed_scale`
- `runtime.movement.engagement.attack_speed_lateral_scale`
- `runtime.movement.engagement.attack_speed_backward_scale`

### Kept in place

- `runtime.movement.v4a.reference_surface_mode`

Reason:

- it remains a candidate-internal seam for the current v4a line
- future movement candidates may coexist temporarily, so it should not yet be
  promoted to a generic maintained movement owner

