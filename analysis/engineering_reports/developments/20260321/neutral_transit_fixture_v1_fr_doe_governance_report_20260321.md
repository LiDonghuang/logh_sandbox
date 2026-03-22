# Neutral Transit Fixture v1 FR DOE Governance Report (2026-03-21)

Status: engineering evidence update  
Scope: bounded single-fleet diagnostic DOE on the existing `neutral_transit_v1` fixture

Engine Version:
current local maintained `test_run` path over shared frozen runtime `v3a`

Modified Layer:
none in this DOE turn; execution and reporting only

Affected Parameters:
`formation_rigidity (FR)` swept over `[1, 3, 5, 7, 9]`  
`fixture.neutral_transit_v1.objective_point_xy` swept over `[[100,100], [150,150]]`  
all other personality dimensions held at `5`

New Variables Introduced:
none in this DOE turn

Cross-Dimension Coupling:
runtime behavior unchanged; evidence indicates FR couples strongly to projection burden and final formation compaction under this fixture geometry

Mapping Impact:
none; this DOE does not request a mapping change

Governance Impact:
evidence only; suitable for bounded interpretation of the current shared movement/projection path

Backward Compatible:
yes; no mechanism code changed during this DOE/report round

## Summary

1. This DOE used the existing `neutral_transit_v1` fixture with fixed seeds and no runtime behavior edits.
2. All 10 runs reached the objective; no run hit a time cap.
3. The longer diagonal mainly increased duration, not projection severity.
4. FR had only a mild arrival-time effect.
5. FR had a strong monotonic effect on projection burden:
   pair count and peak correction displacement both rose materially with FR.
6. `corrected_unit_ratio` showed broad projection involvement rather than rare correction.
7. At `FR>=3`, every cell hit at least one tick with full-unit correction coverage (`1.0`).
8. Higher FR ended with lower `formation_rms_radius_ratio`, i.e. stronger net compaction rather than better radius preservation.
9. The fixture is therefore doing its intended job:
   it exposes shared-path movement/projection behavior cleanly without invoking battle semantics.
10. This evidence does not justify baseline replacement.
11. It does justify using the fixture for further bounded paired-comparison or parameter-isolation work.

## 1. DOE Envelope

- Archetype anchor: `lobos`
- Geometry anchor: current test-only diagonal baseline
  `origin_xy=[50,50]`, `facing_angle_deg=45`, `fleet_size=100`, `aspect_ratio=4.0`
- Objective points:
  `[100,100]`, `[150,150]`
- Seeds fixed:
  `random=20260321`, `metatype=20260322`, `background=20260323`
- Boundary disabled
- Shared `integrate_movement` reused unchanged

Run table:
[neutral_transit_fixture_v1_fr_doe_run_table_20260321.csv](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_doe_run_table_20260321.csv)

Detailed engineering analysis:
[neutral_transit_fixture_v1_fr_doe_analysis_20260321.md](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_doe_analysis_20260321.md)

## 2. Governance Reading

### 2.1 What this DOE does support

- `neutral_transit_v1` is functioning as a clean diagnostic surface.
- FR can now be read against projection breadth and projection burden in a no-enemy geometry.
- The new `corrected_unit_ratio` indicator is useful:
  it closes the gap between pair-count reading and actual unit-level correction coverage.

### 2.2 What this DOE does not support

- It does not support treating fixture transit behavior as a new baseline.
- It does not support reinterpreting FR as a clean transit-speed knob.
- It does not support opening a broad movement rewrite from this evidence alone.

## 3. Main Governance-Relevant Findings

1. Arrival-time sensitivity to FR is weak.
   Short diagonal: `72 -> 75`
   Long diagonal: `146 -> 151`

2. Projection burden sensitivity to FR is strong.
   Pooled `peak_projection_pairs_count`: `92.5 -> 216.0`
   Pooled `peak_projection_max_displacement`: `0.523 -> 1.300`

3. Projection coverage is broad, not sparse.
   `peak_corrected_unit_ratio` is `0.98` even at `FR=1` and `1.0` from `FR=3` upward.

4. Higher FR ends more compact in this fixture.
   Pooled `final_rms_radius_ratio`: `0.722 -> 0.575`

5. Objective length mostly changes run length, not the projection burden pattern.
   This strengthens the reading that the burden is structural to the shared path under this geometry.

## 4. Recommended Governance Posture

- Keep `neutral_transit_v1` in test-only status.
- Treat current output as bounded diagnostic evidence, not doctrine.
- Permit further small paired-comparison work on this fixture if the goal is to compare shared-path burden rather than to propose a replacement baseline.
- Do not infer from this DOE that higher FR is “better” or “worse” globally; the current evidence is fixture-specific and projection-specific.

## 5. Explicit Non-Changes

- battle default path remains unchanged
- fixture settings path remains `fixture.neutral_transit_v1`
- objective injection hook remains in the bounded test-only execution path
- `integrate_movement` was not modified in this DOE turn
- no new settings surface was introduced
- no new runtime selector was introduced

## 6. Current Not-Done Items

- no paired model comparison against another movement model
- no multi-waypoint transit
- no enemy-present transit probe
- no baseline-replacement request
- no governance request for broad runtime semantics rewrite
