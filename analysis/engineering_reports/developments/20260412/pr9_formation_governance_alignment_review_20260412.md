# PR9 Formation Governance Alignment Review 20260412

Status: current review report
Date: 2026-04-12
Scope: review of the `PR #9` Formation governance instruction against current engineering evidence and the formation discussion history
Authority: engineering review report only; not canonical semantics authority

## Purpose

This report answers two narrow questions:

1. whether the current `PR #9` governance instruction matches the actual direction implied by the repo's formation history
2. whether that instruction needs correction or only refinement

This report does not change governance.
It does not change code.
It does not reopen the already-completed bounded notes unless a contradiction is found.

## Sources reviewed

Primary governance source:

- `PR #9` top-level governance instruction comment:
  - `Governance instruction - Formation-only direction on PR #9`

Current local carrier guidance:

- `docs/archive/ts_handoff_archive/TS_HANDOFF_20260412_144204/NEW_THREAD_INSTRUCTION_20260412.md`

Current formation-thread engineering records:

- `analysis/engineering_reports/developments/20260412/Formation_Owner_Path_Audit_20260412.md`
- `analysis/engineering_reports/developments/20260412/pr9_formation_cold_shell_subtraction_shortlist_note_20260412.md`
- `analysis/engineering_reports/developments/20260412/pr9_formation_coarse_body_boundary_lock_note_20260412.md`

Historical discussion anchors reviewed for context:

- `analysis/engineering_reports/developments/20260322/neutral_transit_decoupling_decision_20260322.md`
- `analysis/engineering_reports/developments/20260322/movement_v4b_review_minimal_formation_aware_rebuild_20260322.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_formation_mapping_legality_split_note.md`
- `analysis/engineering_reports/developments/20260326/step3_3d_formation_fast_visible_path_note.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_formation_layout_structural_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_frozen_expected_position_first_cut_note_20260327.md`
- `analysis/engineering_reports/developments/20260327/late_terminal_orientation_freeze_live_centroid_note_20260327.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_first_honest_formation_ownership_opening_note_20260330.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_round0_formation_transition_carrier_redefinition_note_20260330.md`
- `analysis/engineering_reports/developments/20260402/step3_3d_pr6_battle_first_hold_terminal_design_note_20260402.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_battle_precontact_formation_realization_gap_note_20260404.md`
- `analysis/engineering_reports/developments/20260408/step3_3d_pr6_hold_radius_and_neutral_relation_cleanup_record_20260408.md`
- `analysis/engineering_reports/developments/20260408/step3_3d_pr6_fleet_body_summary_export_phase1_record_20260410.md`

## Main judgment

The current `PR #9` governance instruction is directionally correct and matches the strongest read from the engineering history.

Current recommendation:

- keep the governance instruction in force
- do not issue a substantive correction that changes its direction
- treat any update as a refinement / precision-improvement pass only

## Why the instruction matches the real direction

### 1. It correctly reframes the problem

The instruction says the main issue is not that Formation is too weak.
It says Formation currently owns too many things that should not remain Formation-owned.

That matches the strongest historical read.

The older formation line did not fail because it lacked enough slot logic or notional rigor.
It gradually accumulated:

- reference-slot semantics
- unit-level shaping carriers
- transition budgeting
- terminal / hold residue
- movement compensation

The 2026-04-12 owner/path audit confirms that the current maintained carrier is mixed in exactly this way.

### 2. It is consistent with the older anti-collapse layer doctrine

The older 2026-03-26 and 2026-03-28 formation notes repeatedly insisted that Formation must not silently absorb:

- mapping
- legality
- viewer semantics
- assignment execution

The current governance instruction extends that same discipline forward into the runtime-owned active path.

This is not a reversal of earlier doctrine.
It is the same anti-collapse principle applied to the newer mixed runtime carrier.

### 3. It correctly pushes Formation toward coarse-body ownership

The governance instruction favors:

- body center
- front axis
- forward extent
- lateral extent

That matches both:

- the cleaner fleet-body language emerging by 2026-04-10
- the current code-path reality where these are the most defensible long-term Formation-owned quantities

This is the sharpest correction to the overgrown carrier.

### 4. It correctly treats locomotion as the next lower owner

The instruction explicitly says that Formation should stop compensating for unrealistic locomotion by growing more relaxations and speed patches.

That matches the historical evolution of the carrier:

- by 2026-03-30, the formation-transition read had honestly started carrying movement realization together with morphology
- by 2026-04-04, battle formation artifacts were already being read as an owner gap in realization rather than a scalar-tuning defect
- by 2026-04-12, the active bridge clearly contains heading policy, advance budgeting, and unit-speed modulation

So the governance instruction is not speculative here.
It is naming the real next separation problem.

### 5. Its computational-efficiency constraint is historically and structurally right

The instruction rejects default `O(n^2)` formation logic, global remap thinking, and all-pairs control as the natural language of the next solution.

That is aligned with both:

- the repo's long-running concern that formation logic can silently turn into assignment-heavy machinery
- the realism goal for large fleet bodies

This constraint is not merely optimization taste.
It is a guardrail against returning to slot-first escalation under a more formal name.

### 6. Its immediate order was the right one

The instruction required:

1. cold-shell truth audit
2. coarse-body boundary lock
3. only then locomotion separation framing

That ordering proved correct in practice.

It prevented:

- premature deletion of hold / terminal families
- accidental treatment of active baggage as core doctrine
- a jump from boundary confusion straight into implementation

## What changed in current understanding after the review

The main change is not a new doctrine.
It is a clearer understanding of why the current governance instruction feels correct.

Earlier in the project, formation work grew out of a legitimate problem:

- centroid restoration was too weak and too coarse
- expected-position / reference geometry gave a more honest restore object

That earlier move was reasonable.
But later, the carrier expanded further and started owning:

- body geometry
- per-unit shaping
- transition policy
- speed compensation
- shell-state residues

The current governance instruction is strong because it recognizes that this later expansion, not the original expected-position opening, is now the real problem.

## Where the instruction is already strong enough

No substantive directional correction is needed on the following points:

- Formation should simplify rather than expand
- coarse-body ownership is the correct target
- locomotion should become the lower owner of realization policy
- `O(n^2)` / global-remap thinking should stay rejected by default
- PR `#9` should remain bounded and owner/path-first

These points should stay as-is.

## Where the instruction could be improved

The instruction does not need a directional rewrite, but it could be improved in precision.

### 1. Separate transitional-active from long-term-approved more explicitly

Current instruction already says what should not remain long-term Formation-owned.
What it says less explicitly is:

- some boundary-external fields are still active today
- active today does not imply approved long-term ownership
- therefore those fields should be treated as transitional carriers, not as immediate contradiction

This refinement would reduce future confusion when engineering encounters still-live fields such as:

- `expected_slot_offsets_local`
- `current_material_*_phase_by_unit`
- transition-budget carriers

### 2. Distinguish the shell families more explicitly inside governance language

Current engineering review now has a sharper separation:

- `formation_hold_*` = runtime formation-state shell
- `frozen_terminal_*` = fixture expected-position frame-freeze shell

The governance instruction does not contradict this.
But it does not say it explicitly either.

Adding that distinction would help prevent later threads from:

- deleting the wrong shell for the wrong reason
- treating battle hold and neutral fixture freeze as one family

### 3. State that the first code slice should remain subtraction-only even after the proposal step

The current instruction correctly sequences review notes before implementation.
It could be slightly stronger by saying the first implementation slice after those notes should still be:

- subtraction-only
- same-family
- not a simultaneous locomotion reroot

That would make the already-intended discipline even harder to misread.

### 4. Clarify acceptance language for “stable coarse body”

The instruction already says:

- less neat is acceptable
- high-frequency jitter is not acceptable
- inward terminal collapse is not acceptable

That is directionally strong.
It could still be improved by adding a sharper engineering read such as:

- stable body center / axis / extents matter more than exact slot prettiness

This would connect the acceptance bias more directly to the coarse-body owner target.

## Final recommendation

Current recommendation to Human / Governance:

- do not revise the direction of the `PR #9` governance instruction
- treat it as correct and still fit for purpose
- if a later refinement is desired, make it a precision-improvement addendum rather than a corrective replacement

Recommended refinement themes if such an addendum is ever written:

- explicitly name transitional-active versus long-term-approved ownership
- explicitly separate `formation_hold_*` from `frozen_terminal_*`
- explicitly preserve subtraction-only discipline for the first implementation slice
- explicitly tie acceptance language to coarse-body stability rather than slot neatness

## Bottom line

The `PR #9` governance instruction is aligned with the real formation problem.

It correctly identifies that the active carrier became over-coupled.
It correctly points toward:

- smaller coarse-body Formation
- lower-level locomotion ownership
- strong complexity discipline

So the right move is not to correct its direction.
The right move is to keep it, and if desired later, refine its wording so future engineering threads misread it less easily.
