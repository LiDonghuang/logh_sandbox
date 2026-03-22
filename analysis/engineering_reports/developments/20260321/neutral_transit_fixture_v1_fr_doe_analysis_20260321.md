# Neutral Transit Fixture v1 FR DOE Analysis (2026-03-21)

## 1. Scope

This is a bounded 10-run DOE on the existing `neutral_transit_v1` fixture.

- Fixture path: shared `test_run` maintained spine
- Movement model: `v3a`
- Archetype anchor: `lobos`
- Only experimental factor inside personality: `formation_rigidity (FR) in [1, 3, 5, 7, 9]`
- Objective-point factor: `[100.0, 100.0]` and `[150.0, 150.0]`
- All other personality dimensions held at `5`
- All other fixture geometry held at current test-only baseline:
  `origin_xy=[50,50]`, `facing_angle_deg=45`, `fleet_size=100`, `aspect_ratio=4.0`, `stop_radius=2.0`

Source run table:
[neutral_transit_fixture_v1_fr_doe_run_table_20260321.csv](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_doe_run_table_20260321.csv)

## 2. Execution Setup

- Runtime length policy: `max_time_steps = -1`
- Fixture stop rule: objective arrival, then shared `post_elimination_extra_ticks = 10`
- Boundary: disabled
- Observer: enabled
- Hostile contact impedance: forced off inside fixture execution

Fixed seeds:

- `random_seed_effective = 20260321`
- `metatype_random_seed_effective = 20260322`
- `background_map_seed_effective = 20260323`

## 3. Run Table

| run_id | FR | objective | arrival_tick | final_tick | min_distance | final_rms_radius_ratio | mean_corrected_unit_ratio | peak_corrected_unit_ratio | peak_projection_pairs_count | peak_projection_mean_displacement | peak_projection_max_displacement |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| neutral_transit_fixture_fr1_obj100_100 | 1 | [100,100] | 72 | 82 | 0.052 | 0.752 | 0.820 | 0.980 | 92 | 0.298 | 0.498 |
| neutral_transit_fixture_fr3_obj100_100 | 3 | [100,100] | 73 | 83 | 0.324 | 0.644 | 0.916 | 1.000 | 114 | 0.294 | 0.590 |
| neutral_transit_fixture_fr5_obj100_100 | 5 | [100,100] | 74 | 84 | 0.121 | 0.606 | 0.950 | 1.000 | 153 | 0.285 | 0.850 |
| neutral_transit_fixture_fr7_obj100_100 | 7 | [100,100] | 74 | 84 | 0.119 | 0.591 | 0.963 | 1.000 | 182 | 0.290 | 1.074 |
| neutral_transit_fixture_fr9_obj100_100 | 9 | [100,100] | 75 | 85 | 0.266 | 0.559 | 0.975 | 1.000 | 219 | 0.347 | 1.359 |
| neutral_transit_fixture_fr1_obj150_150 | 1 | [150,150] | 146 | 156 | 0.257 | 0.692 | 0.815 | 0.980 | 93 | 0.298 | 0.548 |
| neutral_transit_fixture_fr3_obj150_150 | 3 | [150,150] | 147 | 157 | 0.365 | 0.666 | 0.896 | 1.000 | 113 | 0.294 | 0.672 |
| neutral_transit_fixture_fr5_obj150_150 | 5 | [150,150] | 148 | 158 | 0.377 | 0.645 | 0.929 | 1.000 | 146 | 0.285 | 0.850 |
| neutral_transit_fixture_fr7_obj150_150 | 7 | [150,150] | 149 | 159 | 0.340 | 0.633 | 0.959 | 1.000 | 186 | 0.307 | 1.258 |
| neutral_transit_fixture_fr9_obj150_150 | 9 | [150,150] | 151 | 161 | 0.291 | 0.591 | 0.965 | 1.000 | 213 | 0.342 | 1.241 |

## 4. Cell-Level Reading

### 4.1 Objective `[100,100]`

- FR increases arrival time only mildly: `72 -> 75`
- Projection burden rises strongly with FR:
  `peak_projection_pairs_count 92 -> 219`
  `peak_projection_max_displacement 0.498 -> 1.359`
- Formation radius ratio falls as FR rises:
  `0.752 -> 0.559`
- `peak_corrected_unit_ratio` is already `0.98` at `FR=1` and saturates at `1.0` from `FR=3` upward

### 4.2 Objective `[150,150]`

- FR again increases arrival time mildly: `146 -> 151`
- Projection burden again rises strongly with FR:
  `peak_projection_pairs_count 93 -> 213`
  `peak_projection_max_displacement 0.548 -> 1.241`
- Formation radius ratio again falls with FR:
  `0.692 -> 0.591`
- `peak_corrected_unit_ratio` follows the same saturation pattern:
  `0.98` at `FR=1`, `1.0` from `FR=3` upward

## 5. Factor Main-Effect Check

### 5.1 FR Main Effect

| FR | mean_arrival_tick | mean_final_rms_ratio | mean_peak_corrected_unit_ratio | mean_peak_projection_pairs | mean_peak_projection_mean_disp | mean_peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 109.0 | 0.722 | 0.980 | 92.5 | 0.298 | 0.523 |
| 3 | 110.0 | 0.655 | 1.000 | 113.5 | 0.294 | 0.631 |
| 5 | 111.0 | 0.626 | 1.000 | 149.5 | 0.285 | 0.850 |
| 7 | 111.5 | 0.612 | 1.000 | 184.0 | 0.299 | 1.166 |
| 9 | 113.0 | 0.575 | 1.000 | 216.0 | 0.345 | 1.300 |

Reading:

- FR has only a weak timing effect on arrival.
- FR has a strong and monotonic effect on projection load breadth/intensity proxies.
- FR has a strong and monotonic effect on formation compaction:
  higher FR finishes with lower `formation_rms_radius_ratio`.
- `corrected_unit_ratio` is the clearest breadth indicator:
  the fixture is not showing rare projection intervention;
  it is showing near-whole-formation projection involvement for most of the run.

### 5.2 Objective-Point Main Effect

| objective | mean_arrival_tick | mean_final_rms_ratio | mean_peak_corrected_unit_ratio | mean_peak_projection_pairs | mean_peak_projection_mean_disp | mean_peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|
| [100,100] | 73.6 | 0.630 | 0.996 | 152.0 | 0.303 | 0.874 |
| [150,150] | 148.2 | 0.645 | 0.996 | 150.2 | 0.305 | 0.914 |

Reading:

- Objective length primarily stretches duration.
- Projection burden peaks are remarkably similar across the short and long diagonal.
- This suggests the observed projection pressure is not just a path-length artifact;
  it is strongly tied to the shared movement/projection behavior under this geometry.

### 5.3 MB / PD Main-Effect Check

- `MB`: not testable in this DOE; held at `5`
- `PD`: not testable in this DOE; held at `5`

## 6. Opponent Hardness

Not applicable.

This is a single-fleet / no-enemy fixture DOE, so there is no opponent axis and no win/loss interpretation surface.

## 7. Censoring / Cap Sensitivity

- No run hit an explicit time cap.
- All 10 runs reached the objective.
- `final_tick = objective_reached_tick + 10` in every run, matching the shared post-arrival grace behavior.

Important reading note:

- `final_distance` is not the best arrival-quality metric here because the fixture intentionally continues for 10 ticks after arrival.
- `objective_reached_tick` and `min_distance` are the more trustworthy objective-completion readouts.

## 8. Key Findings

1. The fixture is stable across all 10 cells: every run reaches the objective.
2. FR is not acting as a major transit-speed control in this geometry; arrival shift is only `+3` ticks on the short diagonal and `+5` ticks on the long diagonal from `FR=1` to `FR=9`.
3. FR is acting as a strong projection-load amplifier: pair count and max displacement both rise sharply with FR.
4. `corrected_unit_ratio` confirms projection involvement is broad rather than sparse. By `FR>=3`, at least one tick in every run reaches full-unit correction coverage (`1.0`), and mean corrected coverage stays very high (`~0.896` to `~0.975` depending on cell).
5. Higher FR does not preserve the initial formation radius here; it ends in a more compact state, with pooled final RMS ratio dropping from `0.722` at `FR=1` to `0.575` at `FR=9`.
6. Doubling the diagonal travel distance does not materially change the peak projection burden pattern, which strengthens the case that the fixture is exposing a structural shared-path behavior rather than a one-off short-path artifact.

## 9. Standards Compliance

- DOE size discipline: compliant. Total runs = `10`, so one foreground batch is allowed.
- Seed discipline: compliant. All three effective seeds were fixed and recorded.
- Boundary default rule: compliant. Boundary remained disabled and was not a DOE factor.
- Runtime length policy: compliant. `max_time_steps = -1`; runs ended via fixture arrival plus shared extra ticks.
- Mandatory factor checks: partially adapted. FR is tested directly; MB and PD are explicitly marked not testable because they were held constant.
- Opponent-hardness section: not applicable because this is not a battle DOE.
- Battle-only run-table fields such as winner, first-contact, and first-kill are not applicable in this no-enemy fixture.

## 10. Bottom-Line Reading

This small DOE supports the intended use of `neutral_transit_v1` as a diagnostic fixture.

It does not suggest a new movement baseline.
It does show that, under a clean single-fleet diagonal transit geometry, increasing FR mostly raises projection burden and whole-formation correction coverage, while only modestly delaying arrival.
