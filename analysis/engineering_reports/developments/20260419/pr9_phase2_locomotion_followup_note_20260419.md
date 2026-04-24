# PR9 Phase II Locomotion Follow-Up Note 20260419

## Scope

- Type: locomotion seam follow-up note
- Phase context: PR #9 Phase II opening wave
- Status: note only, no mechanism implementation in this document
- Purpose: clarify the current locomotion seam and the intended Phase II read for desired heading / desired speed realization

## Input Anchors

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md)

## Why This Note Exists

Phase II governance already locks the read that:

- upper layers should output desired heading and desired speed
- low-level locomotion should realize them under bounded physical-style limits
- Formation should not keep growing compensating heading/speed patches

This note records the current locomotion seam truth and the intended next contract, without opening implementation yet.

## Current Active Path Read

This section describes current code truth, not the desired future contract.

### 1. A maintained locomotion seam already exists in runtime

Current active read in `runtime/engine_skeleton.py`:

- `_prepare_v4a_bridge_state(...)` maintains fleet heading and movement-command carriers before movement integration
- `integrate_movement(...)` performs the main per-unit movement realization pass
- `_apply_v4a_transition_speed_realization(...)` and `_apply_v4a_hold_speed_realization(...)` already adjust per-unit speed-related behavior

So Phase II does not need to invent a locomotion seam from zero.

### 2. Current movement realization already includes bounded turn and speed behavior

Current active read in `integrate_movement(...)`:

- heading realization is limited by `max_turn_deg_per_tick`
- speed change is limited by `max_accel_per_tick`
- speed decrease is limited by `max_decel_per_tick`
- turn-speed coupling is already present via `turn_speed_min_scale`

Therefore the active code already contains a bounded locomotion realization family rather than only instantaneous steering.

### 3. Current desired movement is still assembled from mixed sources

Current active read in `integrate_movement(...)`:

- fleet-level `movement_direction` still feeds the target term
- cohesion / restore terms remain part of the same realized motion
- separation and boundary terms also contribute
- the unit heading finally writes `orientation_vector`
- realized velocity writes `velocity`

So the locomotion stage exists, but upstream intent is still not expressed through a clean Phase II unit-solving contract.

### 4. Current locomotion shaping still reads engagement state directly

Current active read in `_apply_v4a_transition_speed_realization(...)`:

- engaged-state speed shaping still depends on `engaged` and `engaged_target_id`

This means the current locomotion seam is still coupled to current combat-stage engagement outputs.

## Phase II Locomotion Contract

This section records the intended contract for later bounded implementation work.
It is not a claim that current runtime already behaves this way.

### A. Upstream output to locomotion

Upper layers should output:

- desired heading
- desired speed

The intended upstream owner for those values is the unit solving layer.

Fleet layer remains upstream context, not the final owner of per-unit realized heading or speed.

### B. Low-level locomotion ownership

Low-level locomotion owns:

- bounded heading realization
- bounded speed realization
- acceleration / deceleration constraints
- turn-rate constraints
- speed-turn coupling

Low-level locomotion does not own:

- fleet-front doctrine
- target doctrine
- combat adaptation doctrine

### C. Separation that must remain explicit

The following must remain conceptually distinct:

1. fleet front axis
2. unit facing
3. actual velocity / movement direction

Correct read:

- fleet front is a fleet/coarse-body owner
- unit facing is the owner used for fire-cone semantics
- velocity is the realized movement result

They may stay lightly coupled in realization, but they should not collapse into one owner.

### D. Formation-side compensation should continue shrinking

Guiding Phase II read remains:

- Formation becomes dumber
- locomotion becomes truer

Therefore later work should not:

- push more heading/speed compensation meaning back into Formation
- re-grow Formation-side patches because locomotion is still imperfect
- let fixture or harness surfaces become hidden locomotion owners

### E. Relationship to targeting and combat

Locomotion may consume same-tick unit-solving intent that is informed by:

- target choice
- combat adaptation read

But locomotion should not itself become the owner of:

- target selection
- combat permission
- damage execution

Combat execution remains downstream from locomotion realization and same-tick combat checks.

## Deferred Details

This note intentionally does not freeze:

- exact future carrier names for desired heading and desired speed
- whether any intermediate unit-intent structure is added
- retreat-family realization branches
- 3D locomotion representation details

Those should stay local to later bounded implementation discussion.

## Recommended Implementation Read For Later

When implementation is later opened, the safest first locomotion-aligned read is:

- keep existing bounded locomotion mechanisms
- feed them from clearer unit-solving intent rather than from mixed legacy ownership
- reduce reliance on engagement-state coupling where that coupling hides owner confusion

This should happen only after the targeting-owner seam is made explicit.

## Non-Goals In This Note

This note does not authorize:

- retreat-policy activation
- a broad locomotion rewrite
- test harness doctrine growth
- viewer-driven locomotion semantics
- any claim that current 2D semantics are future final architecture

## Bottom Line

Current code truth remains:

- locomotion seam already exists
- bounded turn / accel / decel / speed-turn coupling already exist
- current realized motion still mixes fleet movement direction, cohesion, separation, and boundary terms
- locomotion still reads current engagement-state outputs in places

The intended Phase II contract is:

- unit solving outputs desired heading and desired speed
- low-level locomotion realizes them under bounded limits
- fleet front, unit facing, and velocity remain distinct owners
- Formation-side compensation should continue shrinking rather than regrowing
