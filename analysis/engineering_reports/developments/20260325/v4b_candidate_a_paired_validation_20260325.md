# v4b Candidate A - Paired Validation Report (2026-03-25)

Status: Limited Authorization  
Scope: paired validation for the fixture-only `v4b Candidate A` very small implementation step

## 1. Validation Goal

Primary question:

does expected-position restoration reduce long-distance front stretching without letting projection burden rebound toward the old polluted-path level?

## 2. Validation Method

Paired comparison used:

- pre-change current `v4a` post-fix path
- post-change `v4a + v4b Candidate A`

Validation commands:

1. `python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py`
2. `python test_run/test_run_anchor_regression.py`
3. bounded paired fixture runs for:
   - `P0_super_long`
   - `P1_long_diag`

## 3. Paired Cases

### P0

- `arena_size = 400`
- `origin_xy = [50, 50]`
- `objective_point_xy = [350, 350]`

### P1

- `arena_size = 400`
- `origin_xy = [50, 50]`
- `objective_point_xy = [150, 150]`

Note:

`P1` is used here as the bounded long-diagonal comparison case.

## 4. Results

### P0 Super Long

| metric | current `v4a` post-fix | `v4a + Candidate A` | reading |
|---|---:|---:|---|
| arrival_tick | 451 | 426 | faster |
| final_tick | 461 | 436 | shorter total run |
| peak_front_extent_ratio | 8.207 | 2.393 | strong front-stretch mitigation |
| final_front_extent_ratio | 3.747 | 1.993 | much less residual front stretch |
| final_rms_radius_ratio | 1.017 | 0.984 | no obvious inward collapse rebound |
| mean_corrected_unit_ratio | 0.774 | 0.109 | burden fell sharply |
| peak_projection_pairs_count | 119 | 86 | burden fell |
| peak_projection_mean_displacement | 0.354 | 0.361 | roughly flat / slight rise |
| peak_projection_max_displacement | 0.944 | 0.827 | peak local correction improved |
| peak_expected_position_rms_error | n/a | 23.731 | diagnostic only |
| final_expected_position_rms_error | n/a | 2.344 | diagnostic only |

### P1 Long Diagonal

| metric | current `v4a` | `v4a + Candidate A` | reading |
|---|---:|---:|---|
| arrival_tick | 151 | 143 | faster |
| final_tick | 161 | 153 | shorter total run |
| peak_front_extent_ratio | 3.544 | 2.880 | front-stretch mitigation present |
| final_front_extent_ratio | 3.515 | 2.456 | less residual front stretch |
| final_rms_radius_ratio | 0.665 | 0.986 | avoids inward collapse |
| mean_corrected_unit_ratio | 0.844 | 0.331 | burden fell materially |
| peak_projection_pairs_count | 114 | 86 | burden fell |
| peak_projection_mean_displacement | 0.354 | 0.361 | roughly flat / slight rise |
| peak_projection_max_displacement | 0.982 | 0.827 | peak local correction improved |
| peak_expected_position_rms_error | n/a | 23.723 | diagnostic only |
| final_expected_position_rms_error | n/a | 3.268 | diagnostic only |

## 5. Reading Against Success Criteria

### 1. Front stretching

Satisfied.

Both paired cases show clear front-stretch mitigation, especially the primary long-distance case:

- `8.207 -> 2.393` peak
- `3.747 -> 1.993` final

### 2. Corrected-unit burden rebound

Satisfied.

`mean_corrected_unit_ratio` did not rebound.
It fell sharply in both cases.

### 3. Projection pair rebound

Satisfied.

`peak_projection_pairs_count` also fell in both cases.

### 4. Inward collapse

Satisfied.

`final_rms_radius_ratio` did not collapse back toward the old compacted shape.
In both cases it moved to a more open end-state than the current `v4a` comparator.

### 5. Legality / projection independence

Satisfied structurally.

The legality/projection algorithm was left untouched.
Only the upstream restoration object changed.

### 6. Battle-path safety

Satisfied.

`test_run_anchor_regression.py` passed:

- `[off] ok`
- `[hybrid_v2] ok`
- `[intent_unified_spacing_v1] ok`
- `mismatch_count=0`

## 6. Interpretation

The result is stronger than a mere cosmetic improvement.

The implementation did **not** reduce front stretching by reintroducing inward collapse.
Instead, it produced:

- materially lower front-stretch proxies
- materially lower corrected-unit coverage
- lower projection-pair burden
- non-collapsed final radius ratio

The only metric that did not improve cleanly was:

- `peak_projection_mean_displacement`, which stayed roughly flat with a slight increase

That is acceptable in this bounded read because:

- burden breadth dropped sharply
- peak pair burden dropped
- peak max displacement improved

So the remaining correction surface is smaller and more local, not more broadly polluted.

## 7. Bottom Line

This very small implementation step is accepted as successful against the bounded authorization target.

The current reading is:

- expected-position restoration is a better upstream restoration object than centroid pull for the neutral transit fixture
- it materially mitigates long-distance front stretching
- it does so without obvious projection-burden rebound
- it does not require touching legality / projection or battle path
