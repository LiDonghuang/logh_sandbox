# Governance Submission - Phase V.4-b Cohesion v2 Decision Integration
Engine Version: v5.0-alpha5+v4b-switch
Modified Layer: Decision path input (EnemyCollapseSignal source switched from cohesion_v1 to cohesion_v2)
Affected Parameters: None (FR/MB/PD mappings unchanged)
New Variables: None (v1 retained debug-only)
Cross-Dimension Coupling: Unchanged (FR/MB -> geometry/cohesion -> PD trigger)
Mapping Impact: None
Backward Compatible: Yes (debug baseline path via COHESION_DECISION_SOURCE=v1_debug for validation)

Determinism: PASS
Mirror delta vs alpha5 baseline: -34.2768%
Jitter delta vs alpha5 baseline: -17.1161%
Runtime overhead delta vs alpha5 baseline: -0.8658%
Attractor proxy scan: PASS
Stable geometric locking proxy: PASS
Mirror gate (<= +5%): PASS
Jitter gate (<= +10%): PASS
Overhead watch-tier (> +25%): NOT_TRIGGERED
Pocket lifetime comparison (macro over 27 cases): mean lifetime 32.14 -> 16.87, persistent>=20 count 15.04 -> 10.04
Observation (non-blocking): `collapse_tick_v2` is tick=1 for all 27 cases; `collapse_tick_v1` is mostly no-cross / late-cross. The switch is stable by gates but materially advances collapse sensing and should be reviewed in next governance round.

Artifacts:
- v4b_decision_switch_summary.json
- v4b_case_metrics.csv
- v4b_collapse_tick_comparison.csv
- v4b_pocket_lifetime_comparison.csv
- v4b_timeline_overlay_FR8_MB8_PD2.csv
- v4b_timeline_overlay_FR8_MB8_PD5.csv
- v4b_timeline_overlay_FR8_MB8_PD8.csv
