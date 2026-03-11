# Governance Submission - Collapse Tick=1 Root-Cause Data Capture
Engine Version: v5.0-alpha5 + V5.4-b
Modified Layer: Diagnostic instrumentation only (no behavior change)
Affected Parameters: None
Cross-Dimension Coupling: None added
Mapping Impact: None
Backward Compatible: Yes

Determinism (FR8_MB8_PD5 double-run): PASS
tick=1 dominant component (frequency max): elong (54/54)
tick=1 collapse margin mean/min/max: 0.7003/-0.0385/0.9607
tick=1 margin interpretation: deeply positive (scale mismatch-like)
Plot generation: SKIPPED

Interpretation (<=10 lines):
1) Tick=1 dominant contributor (by case-side frequency): elong (54/54).
2) Tick=1 margin stats: mean=0.7003, min=-0.0385, max=0.9607 -> deeply positive (scale mismatch-like).
3) collapse_event_v2(t=1) positives: 51/54.
4) enemy_cohesion_v2 at tick 1 is consistently low enough to cross theta in switched path.
5) v1 reference generally stays high at early ticks, indicating switch sensitivity source is v2 signal scale.
6) No semantic change applied in this capture; data reflects active V5.4-b behavior only.

Artifacts:
- collapse_tick1_early_tick_diagnostic.csv
- collapse_tick1_summary_table.csv
- collapse_tick1_FR8_MB8_PD5_ticks0_200.csv
- collapse_tick1_capture_summary.json
- plots_skipped_reason: No module named 'matplotlib'
