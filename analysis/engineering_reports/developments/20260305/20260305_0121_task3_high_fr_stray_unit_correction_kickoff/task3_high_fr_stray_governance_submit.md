# Governance Submit - Task3 T3-1 Baseline Characterization
Engine Version: v5.0-alpha5
Scope: Observer-heavy baseline characterization only (no runtime patch)

> [VOID NOTICE - 2026-03-05]
> Status: VOID (do not use for governance/runtime decisions).
> Reason: FR/FCR mapping error in DOE injection (`FR` wrongly bound to `force_concentration_ratio`).
> FR must map to `formation_rigidity`; all FR-related conclusions below are invalid.

## Execution Summary
1. Baseline runs completed: `108` (expected 108: 9 cells x 6 opponents x 2 movement models).
2. Paired deltas generated: `54` (expected 54 cell-opponent pairs).
3. Determinism spot-check records: `4` (v1 x2, v3a x2).

## Determinism Status
1. Spot-check case: `FR8_MB8_PD5_DET` vs fixed opponent `reinhard`.
2. `v1`: PASS (2/2 identical digest).
3. `v3a`: PASS (2/2 identical digest).

## Key Findings (T3-1 Baseline)
1. FR main effect is not observable in this controlled matrix (`FR=7/8/9` rows duplicate at summary level).
2. MB remains the dominant axis: as MB rises (2 -> 5 -> 8), A win rate and mean survivors decrease, and cut timing shifts earlier.
3. Outlier diagnostics (observer-heavy):
   - `v3a` vs `v1` overall mean `max_outlier_persistence_global`: `-14.556`
   - `v3a` vs `v1` overall mean `%ticks(outlier_total>0)`: `-24.936`
   - `v3a` vs `v1` overall mean `outlier_total/tick`: `-0.029`
4. Interpretation for Task3 entry: `v3a` already suppresses long-lived stray persistence in aggregate, but MB=8 cells still show high persistence and remain the likely correction target.

## Artifacts
1. `task3_high_fr_stray_run_table.csv`
2. `task3_high_fr_stray_delta_table.csv`
3. `task3_high_fr_stray_summary.md` (generated separately via doe_postprocess + task3 addendum)
4. `task3_high_fr_stray_determinism_check.md`
5. `task3_high_fr_stray_governance_submit.md`

## Guardrail Compliance
1. No runtime code changes in this execution step.
2. No BRF schema changes.
3. Combat/targeting/PD/collapse semantics unchanged.
4. Execution remained in analysis/report layer only (observer metrics + DOE tables).

## Explicit Assumptions
1. Matrix `replicates=6` under `opponent_roster=first6` is interpreted as one run per first-six opponent.
2. `*_DET` rows are interpreted as repeated identical runs against fixed opponent `first6[0]=reinhard`.
