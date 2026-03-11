# Task 3 Kickoff - High-FR Stray Unit Correction (Execution Spec v1.0)
Engine Version: v5.0-alpha5
Scope: Movement-layer correction workflow definition
Status: Kickoff (no runtime code changes in this package)

## 1. Problem Statement
From Phase VIII-B and Phase VIII-C:
1. `movement_model=v3a` improves some early-cut timing but shows weaker tactical consistency under MB=5/8.
2. `PocketNoCut` and pre-contact geometry-cut prevalence are elevated in v3a.
3. Current duration metrics are fully censored at `end_tick=300`, so event-time + geometry diagnostics must be primary.

Task 3 objective:
- Reduce high-FR stray-unit persistence and pre-contact geometric over-trigger in v3a branch.
- Keep combat/targeting/PD/collapse semantics unchanged.

## 2. Frozen Boundaries
1. No combat formula change.
2. No targeting semantics change.
3. No PD/collapse decision formula change.
4. No BRF schema change.
5. Canonical default remains `movement_model=v1` until post-Task3 validation passes.

## 3. Execution Phases
### T3-1 Baseline Characterization (Observer-heavy, no runtime patch)
Goal:
- Quantify stray/outlier behavior under high FR with existing v1/v3a.

Required per-run metrics (in addition to existing run table fields):
1. `max_outlier_persistence_global`
2. `mean_outlier_total_per_tick`
3. `%ticks_outlier_total_gt0`
4. `first_tick_persistent_outlier`
5. Existing: `FirstContact`, `FirstKill`, `TacticalCutTick(T)`, `TacticalPocketTick(T)`, `PocketNoCut`.

### T3-2 Candidate Patch (v3a branch only)
Goal:
- Introduce minimal movement-only correction for high-FR stray persistence.

Constraints:
1. Patch must be isolated to v3a movement branch.
2. `test_mode=0/1` canonical behavior unchanged.
3. Determinism must hold within each model/branch.

### T3-3 Focused Validation DOE
Goal:
- Compare `v1` vs `v3a_prepatch` vs `v3a_task3` on Task3 matrix.
- Decide whether v3a branch is stable enough for next governance gate.

## 4. Acceptance Criteria for Task3
1. `PocketNoCut` rate does not worsen versus v3a_prepatch in MB=5/8 high-FR cells.
2. pre-contact geometry-cut rate reduced or held with improved tactical consistency.
3. Determinism PASS for all compared models.
4. No regression in first-contact / first-kill plausibility windows.

## 5. Deliverables (Task3 Execution Package)
1. `task3_high_fr_stray_run_table.csv`
2. `task3_high_fr_stray_delta_table.csv`
3. `task3_high_fr_stray_summary.md`
4. `task3_high_fr_stray_determinism_check.md`
5. `task3_high_fr_stray_governance_submit.md`

## 6. Standards Compliance
- DOE summary sections must follow `DOE_Report_Standard_v1.0`.
- BRF output rules must follow `BRF_Export_Standard_v1.0`.
- Runtime length policy: `max_time_steps=-1` with elimination+grace termination.
