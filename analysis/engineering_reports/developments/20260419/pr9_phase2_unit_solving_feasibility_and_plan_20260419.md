# PR9 Phase II Unit Solving Feasibility And Plan 20260419

## Scope

- Type: engineering feasibility analysis and execution plan
- Phase context: PR #9 Phase II opening wave
- Status: planning only, no mechanism implementation in this note

## Input Governance Anchor

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)

## Executive Read

The new Phase II direction is feasible without reopening Phase I Formation work.

The repo is already in a good structural position for this opening wave because:

- Formation coarse-body boundary is now locked
- fleet heading is now runtime-owned again
- low-level locomotion seam already exists
- fire-cone target filtering already exists as a bounded mechanism

The main risk is not missing infrastructure alone. The main risk is ownership relapse:

- letting `resolve_combat()` remain the hidden target owner
- letting `test_run` grow back into a doctrine owner
- letting fleet front, unit facing, and actual movement collapse into one signal again

Therefore the Phase II opening wave should remain document-first and owner/path-first, exactly as governance now requires.

## Current Feasibility By Seam

## 1. Fleet layer vs unit layer

Feasibility: high

Reason:

- current runtime already distinguishes fleet-level carriers such as:
  - `last_target_direction`
  - `coarse_body_heading_current`
  - `movement_command_direction`
- current Formation layer is no longer the immediate blocking problem

Main engineering caution:

- do not silently let unit-level target / combat adaptation logic backflow into these fleet carriers

## 2. Shared spatial service

Feasibility: medium-high

Reason:

- the runtime already has local-neighborhood style machinery in several places
- a shared runtime-owned local-enumeration seam is compatible with the current no-O(n^2)-by-default requirement

Main engineering caution:

- the shared service must stay infrastructure-only
- it must not become a new place where targeting doctrine quietly hides

## 3. Unit target owner reroot

Feasibility: medium

Reason:

- current target choice still materially lives inside `resolve_combat()`
- moving to same-tick minimal `selected_target_id` is conceptually simple
- but owner-flow must be explicit so that `resolve_combat()` becomes a validity / fire / damage stage instead of a doctrine stage

Main engineering caution:

- do not add heavy target memory
- do not add fallback logic where `resolve_combat()` silently re-selects targets and thus stays the real owner

## 4. Combat adaptation seam

Feasibility: medium

Reason:

- the repo already shows that local battle geometry affects fleet behavior
- governance now requires an explicit seam rather than implicit leakage

Main engineering caution:

- this seam should not be implemented first as a large mode/state machine
- it should begin as a minimal owner/contract distinction

## 5. Low-level locomotion continuation

Feasibility: high for note/design work, medium for implementation

Reason:

- heading / speed realization seam already exists
- governance clarifies that locomotion is not just turn-rate limiting
- the current codebase can continue from the established low-level seam rather than inventing a new layer

Main engineering caution:

- do not let Formation-side patches grow again to compensate for locomotion limitations
- do not let retreat policy interrupt the current Phase II opening wave

## 6. 3D reservation

Feasibility: high

Reason:

- this is primarily an architectural constraint on naming, ownership, and semantics
- it does not require immediate 3D implementation

Main engineering caution:

- avoid hard-freezing current 2D width/depth tactical semantics into future unit/combat owners

## Recommended Immediate Work Order

This should follow governance literally and remain document-first.

## Step 1. Governance export

Status: completed in this thread

Path:

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)

## Step 2. Unit structure / contract note

Next recommended note.

Purpose:

- make the unit solving layer explicit without implementation
- define the minimal contract between:
  - fleet layer
  - unit solving layer
  - low-level locomotion
  - combat resolution stage

Must explicitly distinguish:

- fleet-level objective/front/reference
- unit-level target choice / adaptation / desired heading / desired speed
- locomotion realization
- combat execution

## Step 3. Simplified unit targeting note

After unit structure note.

Purpose:

- define the unit target owner
- define the same-tick `selected_target_id` read
- define what the shared spatial service provides and what it must not own

Must explicitly state:

- target choice moves out of `resolve_combat()`
- `resolve_combat()` becomes re-check / fire / damage / engagement status
- no heavy target memory doctrine

## Step 4. Locomotion follow-up note

After targeting note.

Purpose:

- define how desired heading / desired speed pass from unit solving into locomotion
- keep distinct:
  - fleet front
  - unit facing
  - actual velocity

Must explicitly preserve:

- no collapse of those three layers back into one signal
- no retreat-policy activation in this opening wave

## Step 5. Only then a bounded implementation-slice proposal

Only after the three notes above.

Recommended first implementation candidate:

- minimal unit target-owner reroot

Why:

- it is central to Phase II
- it is smaller than introducing combat adaptation mechanism or retreat mechanism
- it creates the contract needed for later locomotion/combat adaptation work

## Not Recommended In This Opening Wave

The following should remain deferred for now:

- retreat-policy activation
- `back_off_keep_front`
- `turn_away_retirement`
- broad combat adaptation implementation
- heavy unit state machine / behavior tree design
- broad viewer-driven changes
- harness-side doctrine expansion

## Likely Active Owner Paths For Future Notes

Primary runtime files:

- `runtime/runtime_v0_1.py`
- `runtime/engine_skeleton.py`

Primary harness/reference files:

- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`

Main current owner tension to watch:

- `resolve_combat()` still carries target-owner burden that governance now wants moved

## Validation Posture For The Next Thread

For the immediate next wave, validation should remain light because the next wave should still be note/contract-first:

- static owner/path audit first
- document export / contract note first
- no broad dynamic experimentation before the first bounded implementation slice is approved

## Bottom Line

Phase II is feasible now.

The repo does not need another broad Formation pass first.
It needs a disciplined transition from:

- Formation coarse-body carrier

to:

- unit solving layer
- simplified target owner
- locomotion as bounded realization layer

The correct next move is not implementation-first.
It is:

1. governance export
2. unit contract note
3. targeting note
4. locomotion note
5. only then bounded implementation proposal
