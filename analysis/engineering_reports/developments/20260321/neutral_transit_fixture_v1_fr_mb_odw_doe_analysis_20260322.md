# Neutral Transit Fixture v1 FR x MB x ODW DOE Analysis (2026-03-22)

## 1. Scope

This report summarizes a bounded 125-run DOE on the existing `neutral_transit_v1` fixture.

- Geometry factor frozen:
  long diagonal `[50,50] -> [150,150]`
- Active factors:
  `formation_rigidity (FR) in [1,3,5,7,9]`
  `mobility_bias (MB) in [1,3,5,7,9]`
  `offense_defense_weight (ODW) in [1,3,5,7,9]`
- Archetype anchor:
  `lobos`
- Non-DOE personality dimensions held at `5`
- Movement path:
  shared maintained `v3a`
- Objective:
  keep the fixture diagnostic and identify which axis most strongly drives transit delay, projection burden, and geometry drift

Merged run table:
[neutral_transit_fixture_v1_fr_mb_odw_doe_run_table_20260322.csv](e:/logh_sandbox/analysis/engineering_reports/developments/20260321/neutral_transit_fixture_v1_fr_mb_odw_doe_run_table_20260322.csv)

## 2. Execution Envelope

- Total runs: `125`
- Seeds fixed:
  `random=20260321`
  `metatype=20260322`
  `background=20260323`
- Boundary: disabled
- Observer: enabled
- Objective completion: `125 / 125` reached objective
- Termination behavior:
  `final_tick = objective_reached_tick + 10` for all `125` runs
- Cap censoring:
  none observed

## 3. Factor Main Effects

### 3.1 FR Main Effect

| FR | mean arrival_tick | mean final_rms_radius_ratio | mean mean_corrected_unit_ratio | mean peak_corrected_unit_ratio | mean peak_projection_pairs | mean peak_projection_mean_disp | mean peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 146.76 | 0.727 | 0.778 | 0.991 | 93.40 | 0.319 | 0.543 |
| 3 | 149.40 | 0.665 | 0.897 | 0.990 | 117.68 | 0.312 | 0.691 |
| 5 | 150.80 | 0.628 | 0.939 | 0.999 | 156.92 | 0.302 | 0.951 |
| 7 | 152.80 | 0.599 | 0.962 | 1.000 | 192.72 | 0.323 | 1.237 |
| 9 | 156.52 | 0.571 | 0.976 | 1.000 | 232.00 | 0.371 | 1.579 |

Reading:

- FR has a clear monotonic slowing effect on arrival.
- FR is the strongest positive driver of projection pair burden.
- FR also strongly increases unit-level correction coverage.
- Higher FR ends with a smaller final RMS radius ratio, i.e. stronger net compaction / drift from the initial radius.

### 3.2 MB Main Effect

| MB | mean arrival_tick | mean final_rms_radius_ratio | mean mean_corrected_unit_ratio | mean peak_corrected_unit_ratio | mean peak_projection_pairs | mean peak_projection_mean_disp | mean peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 145.68 | 0.649 | 0.927 | 0.996 | 160.76 | 0.243 | 0.801 |
| 3 | 147.56 | 0.643 | 0.919 | 0.997 | 158.68 | 0.280 | 0.878 |
| 5 | 150.32 | 0.636 | 0.911 | 0.998 | 157.08 | 0.324 | 0.988 |
| 7 | 154.00 | 0.630 | 0.902 | 0.996 | 157.44 | 0.367 | 1.112 |
| 9 | 158.72 | 0.631 | 0.892 | 0.993 | 158.76 | 0.415 | 1.221 |

Reading:

- MB also slows arrival monotonically, and its arrival swing is larger than FR in this fixture.
- MB has little effect on projection pair count.
- MB does materially raise projection displacement intensity.
- MB only weakly affects final RMS radius ratio compared with FR.

### 3.3 ODW Main Effect

| ODW | mean arrival_tick | mean final_rms_radius_ratio | mean mean_corrected_unit_ratio | mean peak_corrected_unit_ratio | mean peak_projection_pairs | mean peak_projection_mean_disp | mean peak_projection_max_disp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 161.76 | 0.609 | 0.903 | 0.996 | 178.72 | 0.450 | 1.451 |
| 3 | 154.68 | 0.626 | 0.903 | 0.996 | 164.40 | 0.382 | 1.168 |
| 5 | 148.92 | 0.644 | 0.910 | 0.996 | 152.24 | 0.305 | 0.921 |
| 7 | 146.00 | 0.653 | 0.917 | 0.996 | 148.92 | 0.257 | 0.753 |
| 9 | 144.92 | 0.658 | 0.919 | 0.997 | 148.44 | 0.235 | 0.707 |

Reading:

- ODW has the strongest monotonic arrival effect of the three factors in this grid.
- Low ODW is associated with the heaviest projection burden and the slowest arrival.
- Higher ODW reduces both projection intensity and pair burden.
- Higher ODW also preserves a larger final RMS radius ratio.

## 4. Comparative Reading

### 4.1 Which factor dominates what

- Arrival delay:
  ODW > MB > FR
- Projection pair burden:
  FR >> ODW > MB
- Projection displacement intensity:
  ODW > FR > MB for `peak_projection_max_displacement`
- Final geometry compaction:
  FR is the clearest dominant factor

### 4.2 Corrected-unit coverage reading

`mean_corrected_unit_ratio` stays high across the entire grid.

- Lowest pooled level in this DOE:
  `FR=1 -> 0.778`
- Highest pooled level in this DOE:
  `FR=9 -> 0.976`

This remains a strong signal that projection is not a rare legality cleanup layer in this fixture.
It is a broad, often near-whole-formation intervention surface.

## 5. Notable Cells

| case | run_id | FR | MB | ODW | arrival_tick | peak_projection_pairs | peak_projection_max_disp | final_rms_radius_ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fastest arrival | `neutral_transit_fixture_fr1_mb1_odw7_obj150_150` | 1 | 1 | 7 | 142 | 91 | 0.328 | 0.752 |
| slowest arrival | `neutral_transit_fixture_fr9_mb9_odw1_obj150_150` | 9 | 9 | 1 | 193 | 317 | 2.937 | 0.467 |
| max pair burden | `neutral_transit_fixture_fr9_mb9_odw1_obj150_150` | 9 | 9 | 1 | 193 | 317 | 2.937 | 0.467 |
| max correction displacement | `neutral_transit_fixture_fr9_mb9_odw1_obj150_150` | 9 | 9 | 1 | 193 | 317 | 2.937 | 0.467 |
| strongest compaction | `neutral_transit_fixture_fr9_mb9_odw1_obj150_150` | 9 | 9 | 1 | 193 | 317 | 2.937 | 0.467 |

The adverse corner is therefore very clear:

`high FR + high MB + low ODW`

Under this fixture, that corner is simultaneously the slowest, the most projection-heavy, and the most compacted.

## 6. Interpretation

1. The decision to freeze travel distance at the long diagonal was justified.
   This 125-run grid gives a wide enough observation window to separate timing, projection burden, and geometry drift cleanly.

2. FR should currently be read primarily as a geometry/projection-load amplifier in this fixture, not as the main speed lever.

3. MB behaves more like a displacement-intensity / delay amplifier than a pair-count amplifier.

4. ODW strongly shapes the overall transit burden surface.
   In this grid, low ODW is systematically associated with slower arrival and heavier projection load.

5. The shared movement path remains stable in the narrow sense that every cell still reaches the objective.
   But stability here does not mean light projection involvement.

## 7. Standards Compliance

- Batch discipline: compliant.
  `125` runs were split into `7` background batches with max batch size `20`.
- Seed discipline: compliant.
  All effective seeds were fixed and recorded.
- Boundary rule: compliant.
  Boundary remained disabled.
- Runtime length policy: compliant.
  No hard cap was used as the policy stop; runs ended through fixture arrival plus shared extra ticks.
- Factor main-effect check: adapted and compliant for this fixture DOE.
  The active axes are `FR / MB / ODW`, not battle-standard `FR / MB / PD`.
- Opponent-hardness section: not applicable.
  This is a no-enemy single-fleet fixture DOE.
- Battle-only fields such as winner / first-contact / first-kill are not applicable here.

## 8. Bottom-Line Reading

This DOE strengthens the case for using the long-diagonal neutral-transit fixture as a bounded projection/geometry audit surface.

The most important current engineering reading is not “which cell wins,” but:

- FR chiefly raises projection breadth/burden and compaction
- MB chiefly raises delay and correction intensity
- low ODW is the clearest adverse lever for both delay and projection burden
