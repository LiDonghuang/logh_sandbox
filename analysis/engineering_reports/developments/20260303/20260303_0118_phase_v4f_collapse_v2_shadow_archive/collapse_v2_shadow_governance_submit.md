# collapse_v2_shadow Governance Submit (Phase V.4-f, Observer-only)

Engine baseline: v5.0-alpha5 (behavior path unchanged: cohesion_v2 active, v3.1 shadow only)

## Threshold Quantiles Used (fixed, per-side from reference timeline ticks 0..200)
- theta_conn = q20(C_conn_rel)
- theta_coh = q20(C_v3p1)
- theta_force = q30(ForceRatio)
- theta_attr = q70(AttritionMomentum)

Per-side values:
- Side A: theta_conn=0.110000, theta_coh=0.977528, theta_force=0.955556, theta_attr=0.100000
- Side B: theta_conn=0.060000, theta_coh=1.000000, theta_force=1.000000, theta_attr=0.000000

Signal definitions used:
- ForceRatio(t) = Alive_self(t) / Alive_enemy(t)
- AttritionMomentum(t), W=20: [(Alive_self(t-W)-Alive_self(t))/W] - [(Alive_enemy(t-W)-Alive_enemy(t))/W]
- For t < 20, AttritionMomentum is set to 0.0 (window unavailable).

Schema note: this phase uses `C_conn_abs` column from V4-d shadow exports as the effective `C_conn_rel` signal (relative-LCC connectivity).

## Tick-1 Trigger Check
- reference_alpha_AB: side A tick1 shadow=0, old_v2=1; side B tick1 shadow=0, old_v2=1
- FR8_MB8_PD5: side A tick1 shadow=0, old_v2=1; side B tick1 shadow=0, old_v2=1

## Key Deltas vs collapse_event_v2 (baseline)
- Old collapse_event_v2 asserts at tick1 in representative timelines.
- New collapse_v2_shadow requires 2-of-4 pressure plus 10-tick sustain, so it does not fire at tick1 in the two required timelines.
- 3x3x3 matrix output (54 case-side rows, T=300) indicates case+side pressure prevalence and whether shadow collapse ever triggers within observed window.

## Outputs
- analysis/engineering_reports/collapse_v2_shadow_timeline_FR8_MB8_PD5.csv
- analysis/engineering_reports/collapse_v2_shadow_timeline_reference_alpha_AB.csv
- analysis/engineering_reports/collapse_v2_shadow_events_matrix_3x3x3.csv
- analysis/engineering_reports/collapse_v2_shadow_governance_submit.md

Data source note:
- Timeline CSVs are computed from V4-d exported shadow timelines (ticks 0..200).
- 3x3x3 matrix is computed from observer-only runtime replays (ticks 1..300) under Phase-V default execution settings with FR/MB/PD overrides.

Determinism check (FR8_MB8_PD5 observer timeline digest): PASS
- digest_run1=b477dd2879964b04bb726f08689e0006409d850814fa450f1bb93154288a6a72
- digest_run2=b477dd2879964b04bb726f08689e0006409d850814fa450f1bb93154288a6a72

Determinism impact: PASS (observer-only; runtime behavior path unchanged).
