# Governance Submit - Phase VIII-C Movement 3A Decision Gate
Engine Version: v5.0-alpha5
Scope: Decision gate only (no runtime changes)

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: upstream FR/FCR mapping error in supporting DOE interpretation.
> This decision-gate conclusion is invalid pending corrected FR mapping rerun (`FR = formation_rigidity`).

## Decision Request
Approve the following policy:
1. Keep canonical default `movement_model=v1` for `test_mode` 0/1.
2. Keep `movement_model=v3a` as experimental branch under `test_mode=2` only.
3. Authorize Task 3 (high-FR stray-unit correction) as next implementation priority.

## Evidence Snapshot
1. Source DOE package: `analysis/engineering_reports/developments/20260304/phase_viiiB_movement_3a_doe_validation/`.
2. Determinism: PASS per movement model (from Phase VIII-B determinism check).
3. Duration censoring: 100% runs at `end_tick=300`; duration metrics low sensitivity.
4. Event-quality deltas:
   - v3a cut_exists_rate lower than v1 (85.556% vs 92.222%).
   - v3a pocket_no_cut_rate higher than v1 (14.444% vs 7.778%).
   - v3a precontact_geom_cut_any_rate higher than v1 (96.667% vs 76.667%).

## Artifacts
1. `phase_viiic_decision_matrix.csv`
2. `phase_viiic_decision_summary.json`
3. `phase_viiic_decision_brief.md`
4. `phase_viiic_movement_3a_governance_submit.md`

## Guardrail Compliance
1. No runtime code change: PASS.
2. No BRF schema change: PASS.
3. No PD/collapse/movement formula edit in this phase: PASS.
