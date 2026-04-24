# PR9 Phase II Bounded Implementation Slice Proposal Unit Intent Bridge 20260419

Status: proposal only
Date: 2026-04-19
Scope: second bounded implementation proposal after the first target-owner reroot slice
Authority: engineering proposal for Human + governance review before any new code implementation

## Purpose

This proposal defines the next smallest honest Phase II slice after:

- the first same-tick target-owner reroot
- the new Phase II primary baseline freeze

It does not implement the next slice.
It does not open retreat policy.
It does not open a mode system.
It does not open a broad locomotion rewrite.

Its job is to make the next real owner/path problem explicit:

- same-tick target ownership is now out of `resolve_combat(...)`
- but movement / bridge shaping still read post-resolution engagement state

So the next bounded question is no longer "who selects the target inside combat?"
It is:

- how unit-solving intent should feed locomotion / bridge without re-collapsing into `engaged_target_id`

## Governance And Note Anchors

This proposal follows:

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_simplified_unit_targeting_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_target_owner_reroot_first_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_target_owner_reroot_first_bounded_implementation_report_20260419.md)

Current primary baseline anchor for future paired comparison:

- [eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Most important governance reads carried into this proposal:

- do not re-collapse selection and engagement writeback
- do not introduce mode in this next slice
- treat current downstream `engaged*` reads as transitional only
- keep combat adaptation as solving-assist semantics, not a behavior tree
- keep one essential owner/path change at a time

## Assumptions

1. The first target-owner reroot slice is accepted as the current starting point.
2. The next slice should remain inside `runtime/engine_skeleton.py`.
3. The next slice should not widen into `test_run/` or schema-heavy state changes unless a narrower option is impossible.
4. The next slice should preserve `engaged_target_id` as post-resolution engagement writeback rather than unit-solving intent.
5. The next slice should be reviewed against the new Phase II primary baselines before any further major code slice is stacked on top.

## Verified Current Active Path Tension

### 1. Current `selected_target_by_unit` exists too late in the tick to inform movement

Current active order in `runtime/engine_skeleton.py::step(...)` is now:

- `evaluate_cohesion()`
- `evaluate_target()`
- `evaluate_utility()`
- movement integration
- contact impedance / fixture clamp
- `_select_targets_same_tick(...)`
- `resolve_combat(...)`

So the first-slice target carrier currently exists only on the combat-execution side of the tick.

### 2. Bridge shaping still reads engagement writeback

Current active read in `runtime/engine_skeleton.py::_evaluate_target_with_v4a_bridge(...)`:

- `engaged_target_id` is still used to build `engaged_attack_vectors`
- those vectors still feed:
  - `effective_fire_axis_raw_hat`
  - `fire_axis_coherence_raw`
  - later front reorientation / hold shaping inside the battle bundle path

This means the bridge still derives maneuver-for-fire shaping from post-resolution engagement state.

### 3. Locomotion shaping still reads engagement writeback

Current active read in `runtime/engine_skeleton.py::_apply_v4a_transition_speed_realization(...)`:

- `engaged` and `engaged_target_id` still gate `attack_speed_scale`
- the target-relative attack direction there is still derived from post-resolution engagement state

This means locomotion still uses engagement writeback as a practical owner for some combat-facing speed shaping.

### 4. `integrate_movement(...)` still lacks an explicit unit-intent seam

Current active read in `runtime/engine_skeleton.py::integrate_movement(...)`:

- `movement_direction` still feeds `target_term_x` / `target_term_y`
- `desired_heading_hat` is derived from the combined movement / cohesion / separation / boundary vector
- `desired_speed` is still derived from turn-alignment and current locomotion limits

So there is still no explicit unit-solving carrier between:

- fleet coarse direction
- unit local target / maneuver-for-fire read
- locomotion realization

## Why The Next Slice Should Not Be An Immediate Direct Rewrite

The tempting but unsafe move would be:

- simply reuse the current `_select_targets_same_tick(...)` output earlier in the tick
- wire it directly into all upstream movement / bridge consumers

That is too under-specified right now because:

- the current helper was introduced as a combat-side first slice
- it currently uses the same bounded local combat neighborhood / in-range read as the old combat selector
- movement / bridge use cases may need a clearer unit-intent read than a mechanically lifted combat helper

So the next slice should be planned as a unit-intent bridge, not as a blind helper relocation.

## Proposed Second Slice

### A. Slice goal

The second bounded implementation slice should do exactly this:

1. introduce a pre-movement unit-intent seam in `runtime/engine_skeleton.py`
2. make bridge / locomotion read that unit intent instead of post-resolution `engaged*`
3. keep `resolve_combat(...)` as a downstream re-check / fire / damage / engagement stage

### B. Preferred carrier read

Preferred next-slice carrier family:

- stage-local
- tick-local
- runtime-local
- non-persistent

Minimum intended content:

- selected target identity for the current unit-solving read
- optional attack-direction / maneuver-for-fire assist values only if strictly necessary

Not allowed in that slice:

- persistent target memory
- long-lived lock-on state
- doctrine-scale mode growth
- broad new runtime schema surfaces

### C. Preferred placement

The smallest honest placement is:

- add a pre-movement unit-intent helper in `runtime/engine_skeleton.py`
- compute that helper output before `integrate_movement(...)`
- allow `_evaluate_target_with_v4a_bridge(...)` and `_apply_v4a_transition_speed_realization(...)` to consume it
- allow the downstream combat stage to continue consuming a same-tick target-selection read

This keeps the second slice in the same active runtime file and avoids early multi-file widening.

## Exact Future Seams To Touch

Primary future implementation file:

- `runtime/engine_skeleton.py`

Primary future implementation seams:

- `step(...)`
- `_evaluate_target_with_v4a_bridge(...)`
- `_apply_v4a_transition_speed_realization(...)`
- possibly a new unit-intent helper local to runtime stage ownership
- `resolve_combat(...)` only if its input path needs to align with the new pre-movement carrier

Not preferred for the second slice:

- `runtime/runtime_v0_1.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`

## Concrete Contract Read For The Next Slice

### 1. Unit intent is not engagement writeback

The next slice must preserve the distinction:

- unit intent = pre-movement / same-tick solving read
- `engaged_target_id` = post-resolution engagement writeback

### 2. Unit intent is not a mode system

If the second slice needs any solving-assist semantics, they must remain:

- minimal
- local
- non-doctrinal

The slice must not introduce:

- a behavior tree
- a persistent combat mode machine
- FR / Formation-side combat adaptation ownership

### 3. Unit intent should be enough for locomotion / bridge to stop reading `engaged*`

The second slice should aim to remove post-resolution `engaged*` as the practical owner in:

- `_evaluate_target_with_v4a_bridge(...)`
- `_apply_v4a_transition_speed_realization(...)`

But the slice should do so through a single new unit-intent seam, not through separate ad hoc replacements in each function.

## Recommended Rejection Rules

The second implementation should be rejected if it does any of the following:

1. keeps bridge / locomotion on `engaged_target_id` and merely adds comments
2. introduces a mode tree or persistent combat state system
3. widens into retreat policy or locomotion formula redesign
4. reintroduces Formation / FR as a combat-adaptation owner
5. creates two parallel same-tick target owners for movement and combat without an explicit contract
6. skips paired baseline review after changing runtime behavior

## Baseline Review Discipline For The Future Implementation Turn

Because the second slice will affect active runtime behavior, future implementation review should compare against the current Phase II primary baselines in this order:

1. `battle_36v36`
2. `battle_100v100`
3. `neutral_36`
4. `neutral_100`

Review expectations:

- do not rely on smoke-only judgment
- do not compare by impression
- explain any clear behavior difference before stacking another slice

## Bottom Line

The first reroot solved the combat-side target owner.

The next real mainline problem is now:

- bridge / locomotion still read post-resolution engagement state

So the narrowest honest next Phase II step is:

- a second bounded implementation slice that introduces a pre-movement unit-intent bridge
- removes practical upstream ownership from `engaged*`
- still avoids mode, retreat, broad locomotion rewrite, and harness widening
