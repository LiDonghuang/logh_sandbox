# step3_3d_pr6_v4a_candidate_parameter_surface_structuring_record_20260410

## Scope

- test-only / configuration-interface cleanup
- no runtime movement formula change
- no targeting change

## Why this round happened

The prior local line prematurely promoted:

- `runtime.movement.engagement.engaged_speed_scale`
- `runtime.movement.engagement.attack_speed_lateral_scale`
- `runtime.movement.engagement.attack_speed_backward_scale`

into the maintained runtime surface.

That move was directionally trying to separate engagement motion from
formation/reference semantics, but it was structurally too early:

- the active owner is still the current `v4a` candidate line
- future 3D formation / movement work may stay on `v4a`, split to `v4b`,
  or reroot more broadly
- promoting these seams into a generic runtime owner now would repeat the
  project's earlier mixed-era coupling problem

## What changed

The current `v4a` candidate surface is now grouped under a structured test-only
subtree:

- `runtime.movement.v4a.restore.*`
- `runtime.movement.v4a.reference.*`
- `runtime.movement.v4a.transition.*`
- `runtime.movement.v4a.battle.*`
- `runtime.movement.v4a.engagement.*`

Concrete path changes:

- `runtime.movement.v4a.restore_strength`
  -> `runtime.movement.v4a.restore.strength`
- `runtime.movement.v4a.expected_reference_spacing`
  -> `runtime.movement.v4a.reference.expected_reference_spacing`
- `runtime.movement.v4a.reference_layout_mode`
  -> `runtime.movement.v4a.reference.layout_mode`
- `runtime.movement.v4a.reference_surface_mode`
  -> `runtime.movement.v4a.reference.surface_mode`
- `runtime.movement.v4a.soft_morphology_relaxation`
  -> `runtime.movement.v4a.reference.soft_morphology_relaxation`
- `runtime.movement.v4a.shape_vs_advance_strength`
  -> `runtime.movement.v4a.transition.shape_vs_advance_strength`
- `runtime.movement.v4a.heading_relaxation`
  -> `runtime.movement.v4a.transition.heading_relaxation`
- `runtime.movement.v4a.battle_*`
  -> `runtime.movement.v4a.battle.*`
- `runtime.movement.engagement.*`
  -> `runtime.movement.v4a.engagement.*`

## What did not change

- active `v4a` movement semantics
- `movement_cfg` effective values consumed by `run_simulation()`
- `integrate_movement()` formulae
- maintained runtime generic owners outside this candidate subtree

## Current truthful read

These parameters are still candidate-owned seams, not yet maintained
runtime-generic owners.

This round is therefore:

- a surface-structure cleanup
- an ownership-truth correction

not:

- a runtime taxonomy finalization
- a cross-candidate generalization
- a new movement mechanism
