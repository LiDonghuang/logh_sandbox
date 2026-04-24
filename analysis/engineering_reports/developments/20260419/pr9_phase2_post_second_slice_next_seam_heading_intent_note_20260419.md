# PR9 Phase II Post Second Slice Next Seam Heading Intent Note 20260419

Status: note only
Date: 2026-04-19
Scope: post-second-slice continuation read
Authority: engineering-side next-step note after governance continuation judgment

## Purpose

This note records the smallest honest next seam after:

- the accepted first target-owner reroot slice
- the accepted second unit-intent bridge slice
- the latest governance continuation judgment that allows continuation but does not authorize broad expansion

This note does not open implementation.
This note does not modify governance files.
This note does not claim approval for a third runtime slice.

## Input Anchors

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_locomotion_followup_note_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_bounded_implementation_slice_proposal_unit_intent_bridge_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_bounded_implementation_slice_proposal_unit_intent_bridge_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_intent_bridge_second_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_intent_bridge_second_bounded_implementation_report_20260419.md)
- [analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

Additional human-provided governance read carried into this note:

- the second slice is accepted
- `unit_intent_target_by_unit` is accepted only as a transitional runtime-local carrier
- no broad widening into mode / retreat / broad locomotion rewrite is authorized
- the next move should remain one essential owner/path at a time
- document-first is preferred unless a next slice is already equally narrow and fully specified

## Assumptions

1. The accepted second slice is the current active starting point.
2. The next honest move should stay inside the maintained active runtime path rather than widen into harness or schema work.
3. Because the latest governance continuation judgment has not yet been exported into a new repo-side governance markdown with explicit file-level approval, this note stays on the engineering-analysis side only.

## Current Owner/Path Read

### 1. What the second slice did settle

Current active code truth in [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py):

- `_evaluate_target_with_v4a_bridge(...)` now computes and stores runtime-local `unit_intent_target_by_unit`
- `_apply_v4a_transition_speed_realization(...)` now reads that carrier
- post-movement combat still uses the same minimal selector contract and `resolve_combat(...)` still owns re-check / fire / damage / engagement writeback

So upstream bridge shaping and transition-speed shaping no longer read `engaged_target_id` as the practical owner.

### 2. What the second slice did not settle

Current active read in `integrate_movement(...)` is still:

- `movement_direction` feeds `target_term_x` / `target_term_y`
- `desired_heading_hat` is still derived from the combined restore / target / separation / boundary vector
- unit-intent target identity does not yet directly own a per-unit maneuver heading contribution there

So the current Phase II seam is cleaner than before, but per-unit desired heading generation is still practically assembled from:

- fleet-level `movement_command_direction`
- restore / spacing / boundary terms

rather than from an explicit per-unit maneuver-heading intent.

## Minimal Human-Readable Evidence

Current active path evidence:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1898) computes `unit_intent_target_by_unit`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1572) uses that carrier for attack-facing speed shaping
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2869) still sets `target_term_x` / `target_term_y` from fleet-level `movement_direction`
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:2903) still forms `desired_heading_hat` from the mixed locomotion vector rather than a dedicated unit maneuver-heading carrier

Shortest plain-language read:

- target identity now reaches bridge and speed shaping
- target identity does not yet own the unit's heading-term input inside locomotion realization

## Smallest Honest Next Seam

The smallest honest next seam is now:

- per-unit heading-intent contribution into `integrate_movement(...)`

More concretely:

- not "pick a new doctrine"
- not "add mode"
- not "activate retreat"
- not "rewrite locomotion"

It is only:

- making the unit layer more explicit in the specific place where per-unit desired heading is still practically fleet-owned

## Why This Is The Next Seam

Governance already locks the intended Phase II read:

- unit layer should own desired heading generation
- unit layer should own desired speed generation
- low-level locomotion should realize them under bounded limits

After the second slice:

- desired speed shaping has a narrower unit-intent path
- desired heading generation still does not

So the remaining asymmetry is now visible and local.

## What A Future Third Slice Would Need To Stay Narrow

If a later third slice is proposed, the narrow read should be:

- keep work inside `runtime/engine_skeleton.py`
- do not add persistent state
- do not turn `unit_intent_target_by_unit` into doctrine by itself
- do not add a behavior tree or heavy mode system
- do not alter combat execution ownership
- do not broaden into general locomotion redesign

The likely carrier family would need to remain:

- stage-local
- tick-local
- runtime-local
- bounded

The most likely target seam would be a per-unit maneuver or heading-assist carrier that can influence:

- `target_term_x`
- `target_term_y`

without redefining the rest of the locomotion stack.

## What Did Not Change

This note did not change:

- runtime code
- baseline files
- test harness
- `BattleState` schema
- governance documents

No new baseline review was needed because this note makes no runtime behavior change.

## Bottom Line

The second slice cleaned the upstream target-intent path, but it did not yet make per-unit desired heading generation explicit inside locomotion realization.

So the smallest honest next seam is now:

- a document-first heading-intent seam read

not:

- mode
- retreat
- persistent memory
- broad locomotion rewrite
- doctrine expansion
