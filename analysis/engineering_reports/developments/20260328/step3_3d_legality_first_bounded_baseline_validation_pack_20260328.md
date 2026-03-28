# Step 3 3D Legality First-Bounded Baseline Validation Pack (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line bounded baseline validation only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: validates the merged legality intake / middle-stage / handoff seam on the current bounded neutral-transit fixture path without changing algorithm shape
Mapping Impact: none; validation reuses the existing mapping-produced reference-position surface as already merged
Governance Impact: establishes the first bounded legality implementation as a working merged baseline with bounded evidence and human-trackable readout
Backward Compatible: yes

Summary
- This pack validates the merged legality first-bounded baseline as a real working baseline.
- The validation uses the merged `dev_v2.0` baseline after PR #5 acceptance and merge.
- The chosen human-trackable artifact is a light tick-level CSV rather than a heavier long-form per-unit dump.
- The baseline continues to show explicit legality intake, legality-owned middle-stage activity, and feasible-position handoff on the bounded fixture path.
- No legality algorithm rewrite or seam redesign is introduced in this turn.

## 1. Merged Baseline Identity

- merged baseline commit: `4e6a9163125e13cf62b9ca706c15d72114d3ec5a`
- accepted implementation carrier source commit: `dea30f7be664d6818ced5a915c460c88bb62e9df`
- supporting human-trackable reference commit kept in repo: `86df7f2`

## 2. Exact Validation Path Used

Validation used the current bounded neutral-transit fixture path through:

- `test_run/test_run_scenario.py`
  - `prepare_neutral_transit_fixture(...)`
- `test_run/test_run_entry.py`
  - `run_active_surface(...)`

Validation shape:

- headless run
- `capture_positions=True`
- `frame_stride=999999`
- `plot_diagnostics_enabled=True`
- `animate=False`
- `export_battle_report=False`

This keeps the run on the merged baseline while preserving the existing legality counts/flags and expected-position / projection metrics.

## 3. Key Bounded Metrics

Observed bounded outputs from the merged baseline run:

- `ticks = 425`
- `objective_reached_tick = 425`
- `legality_reference_surface_count_peak = 100`
- `legality_feasible_surface_count_peak = 100`
- `legality_middle_stage_any = True`
- `legality_handoff_any = True`
- `expected_position_rms_error_last = 1.0999073359004958`
- `expected_position_rms_error_peak = 1.1025581303349725`
- `projection_pairs_peak = 80`
- `projection_mean_displacement_peak = 0.36117894748889684`
- `projection_max_displacement_peak = 0.6487541778854071`
- `corrected_unit_ratio_peak = 0.94`

## 4. Human-Trackable Artifact Choice

The lightest useful artifact for this validation pack is:

- `analysis/engineering_reports/developments/20260328/step3_3d_legality_first_bounded_baseline_tick_metrics_20260328.csv`

That CSV is a tick-level long table with:

- legality reference surface count
- legality feasible surface count
- legality middle-stage active flag
- legality handoff-ready flag
- expected-position RMS error
- projection activity metrics
- corrected-unit ratio

The earlier per-unit long-form sample remains in repo as supporting reference:

- `analysis/engineering_reports/developments/20260328/step3_3d_legality_expected_positions_first50_ticks_longform_20260328.csv`

## 5. What The Baseline Now Proves

The merged bounded baseline now proves the following at runtime/harness level:

- the legality intake seam is not only documented but active on the bounded fixture path
- the legality-owned middle stage remains traceable throughout the run
- the feasible-position handoff surface remains identity-preserving and populated
- the seam does not break the existing expected-position or projection metric path
- the baseline is stable enough to serve as a real working baseline rather than a purely local experiment

## 6. What Remains Unresolved

The merged bounded baseline does not yet resolve:

- final legality hook location
- final legality surface/storage type
- downstream consumer integration shape
- execution order details inside the legality-owned stage
- projection / collision / boundary algorithm finalization

These remain outside this validation turn.

## 7. Recommendation

Current engineering recommendation:

- continue with baseline hardening

Reason:

- evidence is good enough to keep this seam as the bounded baseline
- no validation signal here suggests that the seam choice should be reopened yet
- the next useful work should tighten validation/hardening before any algorithm redesign discussion
