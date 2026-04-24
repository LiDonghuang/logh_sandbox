# PR9 Phase II Unit Desire Bridge Bounded Implementation Slice Proposal 20260419

Status: proposal only
Date: 2026-04-19
Scope: next bounded implementation proposal after the accepted second slice
Authority: engineering proposal for Human + governance review before any third runtime slice

## Purpose

This proposal defines the next smallest honest seam after:

- the first bounded slice rerooted same-tick target selection out of `resolve_combat(...)`
- the second bounded slice rerooted upstream bridge / transition-speed shaping away from post-resolution `engaged*`

The next real owner/path tension is now:

- how same-tick unit-solving intent should produce `desired_heading`
- how same-tick unit-solving intent should produce `desired_speed`
- how low-level locomotion should consume those without reopening doctrine growth

This proposal does not implement the next slice.
This proposal does not authorize a third slice by itself.

## Input Anchors

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_post_second_slice_next_seam_heading_intent_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_post_second_slice_next_seam_heading_intent_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_intent_bridge_second_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_intent_bridge_second_bounded_implementation_report_20260419.md)
- [analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Additional human-provided governance suggestion carried into this proposal:

- do not open the third bounded implementation slice immediately
- first produce one new repo-side markdown proposal
- preferred topic is unit desire bridge / locomotion input seam
- no widening into persistent memory, heavy mode, retreat, broad locomotion rewrite, FR flow-back, harness doctrine growth, or broad refactor

## Assumptions

1. The accepted second slice is the current active starting point.
2. The next honest slice should remain inside `runtime/engine_skeleton.py` unless a narrower runtime-local option proves impossible.
3. The next slice should remain schema-light and should not expand `BattleState` by default.
4. The next slice should preserve the already accepted separation that `engaged_target_id` remains post-resolution engagement writeback.
5. Any future runtime implementation from this proposal must be reviewed against the current Phase II primary baselines.

## Verified Current Active Tension

### 1. Same-tick target intent is now available upstream

Current active read in [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py):

- `_evaluate_target_with_v4a_bridge(...)` computes runtime-local `unit_intent_target_by_unit`
- `_apply_v4a_transition_speed_realization(...)` consumes it

So same-tick target identity already reaches bridge and transition-speed shaping.

### 2. Fleet/coarse direction context is also available pre-movement

Current active read in `_prepare_v4a_bridge_state(...)`:

- fleet/coarse heading state is updated
- `movement_command_direction` is updated
- transition-speed shaping is applied before locomotion realization

So the pre-movement pipeline already has:

- fleet/coarse direction context
- same-tick target intent
- per-unit speed envelope shaping

### 3. Locomotion still assembles the actual desire input from a mixed vector

Current active read in `integrate_movement(...)`:

- `movement_direction` still directly feeds `target_term_x` / `target_term_y`
- `desired_heading_hat` is still derived from the mixed restore / target / separation / boundary vector
- `desired_speed` is still derived locally from turn alignment and `unit.max_speed`

Minimal evidence:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2869) sets `target_term_x` / `target_term_y` from `movement_direction`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2903) forms `desired_heading_hat`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2916) forms `desired_speed_scale`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2921) derives `desired_speed`

So the remaining seam is no longer target identity.
It is locomotion input ownership.

## Proposal Goal

The next bounded slice should do exactly this:

1. introduce the smallest honest same-tick unit desire carrier
2. compute it pre-movement after fleet/coarse context and same-tick target intent are both available
3. let locomotion consume it as `desired_heading` and `desired_speed`
4. keep the rest of the accepted separations intact

This proposal explicitly does not open:

- combat-adaptation doctrine growth
- a heavy mode system
- retreat-policy activation
- a broad locomotion redesign

## Recommended Carrier Shape

### A. Preferred read: one unified carrier

Preferred next-slice carrier:

- one unified runtime-local mapping keyed by `unit_id`

Preferred minimal shape:

```text
unit_desire_by_unit[unit_id] = {
    "desired_heading_xy": (hx, hy),
    "desired_speed_scale": s,
}
```

Where:

- `desired_heading_xy` is normalized or zero-like if no explicit desire is available
- `desired_speed_scale` is a bounded scalar in `[0.0, 1.0]`

### B. Why one unified carrier is preferred over two parallel carriers

One unified carrier is smaller because:

- heading and speed desire are produced from the same same-tick unit-solving read
- locomotion consumes them together in the same function
- it avoids split-owner drift between parallel `heading_intent_by_unit` and `speed_intent_by_unit`
- it avoids a new synchronization problem inside one bounded slice

So this proposal recommends:

- one unified carrier host
- two minimal fields inside that host

not:

- two top-level parallel carriers

### C. Why the carrier should use speed scale rather than absolute speed by default

The narrowest read is:

- unit solving expresses desired speed as a bounded share
- locomotion still converts that into actual speed under:
  - `unit.max_speed`
  - turn-speed coupling
  - accel / decel limits
  - fixture gate

That keeps low-level locomotion as the realization owner rather than moving full speed realization upstream.

## Preferred Computation Placement

The smallest honest computation point is:

- pre-movement
- after `_prepare_v4a_bridge_state(...)`
- after same-tick `unit_intent_target_by_unit` already exists
- before the per-unit realization loop in `integrate_movement(...)`

Preferred host file:

- `runtime/engine_skeleton.py`

Preferred helper form:

- a new runtime-local helper such as `_compute_unit_desire_by_unit(...)`

Preferred input read:

- `state.movement_command_direction`
- `state.last_target_direction`
- `state.coarse_body_heading_current`
- runtime-local `unit_intent_target_by_unit`
- already prepared bundle / bridge context when available

## What Locomotion Should Consume

### A. Desired heading

`integrate_movement(...)` should consume:

- per-unit `desired_heading_xy`

instead of relying only on:

- fleet-level `movement_direction` as the unit target term owner

This does not mean removing cohesion / separation / boundary.
It means the unit-layer maneuver contribution should become explicit before those terms are combined.

### B. Desired speed

`integrate_movement(...)` should consume:

- per-unit `desired_speed_scale`

and then continue realizing actual speed through the existing low-level machinery.

This keeps the slice smaller than a full locomotion rewrite because it does not replace:

- accel / decel limiting
- turn-rate limiting
- turn-speed coupling
- projection / boundary / legality handling

### C. Intentional non-goal

The next slice should not attempt to fully redesign the mixed locomotion vector family in one step.

The intended narrow read is:

- clarify who supplies locomotion desire
- not redesign every term of locomotion realization

## Exact Future Seams To Touch

Primary future implementation file:

- `runtime/engine_skeleton.py`

Primary future seams:

- `_prepare_v4a_bridge_state(...)` only if needed to expose already-computed fleet/coarse context
- a new runtime-local helper for same-tick unit desire generation
- `integrate_movement(...)` at the point where locomotion input is assembled

Not preferred for the next slice:

- `runtime/runtime_v0_1.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- viewer / replay files

## Required Separation Reads To Preserve

The next slice must preserve:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- combat adaptation seam remains solving-assist only

The next slice must not quietly collapse:

- same-tick desire generation into post-resolution engagement writeback
- locomotion input clarification into mode design
- per-unit maneuver input into fleet-front redefinition

## How To Keep The Slice Smaller Than Full Combat Adaptation

The next slice should be rejected if it starts expressing:

- behavior families
- doctrine states
- retreat families
- long-lived combat memory

Instead, the narrow read should stay at:

- one same-tick desire carrier
- one pre-movement computation point
- one locomotion consumption seam

That is enough to clarify locomotion input ownership without claiming a full combat-adaptation implementation.

## Rejection Rules

Reject the next implementation proposal if it silently widens from:

- locomotion input seam clarification

to any of:

- mode system introduction
- retreat-policy pre-activation
- broad locomotion redesign
- persistent target memory
- broad file refactor without proof that a runtime-local option is impossible

## What Would Not Change In The Future Slice

The future slice derived from this proposal should keep unchanged unless a narrower option fails:

- `BattleState` schema
- combat execution ownership in `resolve_combat(...)`
- test harness ownership
- baseline files
- accepted fleet-front / unit-facing / velocity separation

## Baseline Review Discipline For Any Future Implementation

If a future implementation from this proposal changes runtime behavior, it must be reviewed against the current Phase II primary baselines in this order:

1. `battle_36v36`
2. `battle_100v100`
3. `neutral_36`
4. `neutral_100`

Review should include:

- explicit paired comparison
- short human-readable evidence
- explanation before any further slice is stacked if a visible difference appears

## Bottom Line

Target-owner reroot is now sufficiently advanced that the next honest seam is no longer combat execution or upstream target identity.

The next best document-first step is:

- a bounded unit desire bridge proposal

And the narrowest intended next slice after that would be:

- compute one minimal same-tick per-unit desire carrier
- pre-movement
- runtime-local
- tick-local
- non-persistent
- feed `desired_heading` and `desired_speed` into locomotion

without opening:

- mode
- retreat
- persistent memory
- broad locomotion rewrite
- doctrine expansion
