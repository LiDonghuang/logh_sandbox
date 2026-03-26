# v4b Candidate A Expected-Position Validation Plan (2026-03-24)

Status: Draft Test Plan  
Scope: very small paired validation plan for a future fixture-only `v4b Candidate A` implementation

## 1. Purpose

This plan exists to validate one bounded question only:

does fixture-only expected-position restoration reduce the remaining long-distance deformation problem more cleanly than `v4a`, without reopening broad rewrite?

## 2. Fixed Scope

Validation remains fixed to:

- `neutral_transit_v1`
- single fleet
- no enemy
- no battle-path activation
- paired against current `v4a`
- long-distance geometry only

Current long-distance anchor:

- `arena_size = 400`
- `origin_xy = [50, 50]`
- `objective_point_xy = [350, 350]`

## 3. Primary Validation Targets

### Primary Target A - Long-Distance Front Stretching

This is now a primary target, not a side note.

Use the same bounded proxy family already established during the no-enemy fix review:

- `front_extent_peak_ratio`
- `front_extent_final_ratio`

Question:

- does Candidate A reduce excessive front stretching relative to `v4a`?

### Primary Target B - Interpretation Quality

Question:

- do geometry changes become more readable as reference-restoration effects rather than as projection side-effects?

This is judged from paired metric direction plus one bounded animation read, not from large DOE.

## 4. Secondary Targets

- `mean_corrected_unit_ratio`
- `peak_projection_pairs_count`
- `peak_projection_mean_displacement`
- `peak_projection_max_displacement`
- `formation_rms_radius_ratio`
- `arrival_tick`
- final centroid-to-objective distance

These remain important, but they are secondary to front stretching in this plan.

## 5. Minimal Paired Cases

### Pair 1 - Primary Anchor Case

- `movement_model = v4a`
- `movement_model = Candidate A experimental path`
- identical seeds
- identical long-distance fixture geometry
- identical archetype/personality input

This is the only required pair for first authorization.

### Pair 2 - Optional Confirmatory Pair

Only if Governance asks for one extra check:

- same geometry
- same paired movement comparison
- one alternate stable personality anchor

No DOE matrix is authorized here.

## 6. Minimal Validation Commands If Implementation Is Later Approved

1. `python -m py_compile ...`
2. `python test_run/test_run_anchor_regression.py`
3. one paired neutral-transit run on the long-distance case
4. optional one animation export/read for qualitative front-shape inspection

## 7. Directional Reading Rules

Preferred reading after Candidate A:

- front stretching should improve materially
- projection burden should stay flat or improve
- RMS radius should remain interpretable and not collapse into old broad compaction
- arrival should not regress sharply

This plan does **not** require an immediate perfect score on every metric.
It asks whether the remaining deformation problem becomes cleaner and more explainable.

## 8. Explicit Non-Authorizations

This plan does **not** authorize:

- large DOE
- old-factor interaction DOE
- battle-path validation expansion
- baseline replacement protocol
- generalized reference-formation testing

## 9. Bottom Line

The smallest meaningful future validation is:

- one paired long-distance neutral-transit comparison
- `v4a` vs fixture-only Candidate A
- with front stretching promoted to a primary outcome, not just projection burden
