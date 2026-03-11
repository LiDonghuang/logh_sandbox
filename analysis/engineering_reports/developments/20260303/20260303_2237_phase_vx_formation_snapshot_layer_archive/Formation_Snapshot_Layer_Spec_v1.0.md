# Formation Snapshot Layer Spec v1.0

## Scope
- Observer-only diagnostic layer.
- Runtime decision path remains unchanged (no PD/movement/combat/collapse dependency).

## Sampling Policy
- Snapshot cadence: `Delta_t_snapshot = 10` ticks.
- Sample ticks: `t = 0, 10, 20, ...`.
- Computed independently per side (A/B).

## Per-Snapshot Features
1. Centroid: `c = mean(positions)` -> `centroid_x`, `centroid_y`.
2. PCA: `AR`, `AreaScale`, `orientation_theta`.
3. Split: deterministic 1D k=2 on PCA-major projection.
   - `split_separation = |mean(u1)-mean(u2)| / (std(u)+eps)`
4. Envelopment: enemy-centric 12-bin angular coverage.
5. Wedge: top/bottom 30% along `u`, compare lateral std ratio.

## Label Rules
- Compact: `AR < 1.5` and `AreaScale` small (implemented as side-local q30).
- Line: `AR > 3`.
- Rectangle: `1.5 <= AR <= 3` and `|wedge_ratio - 1| < 0.2`.
- Split: `split_separation > 1.2`.
- Enveloping: `angle_coverage > 0.5`.

## Event Tracking
- `first_split_tick` per side.
- `first_envelopment_tick` per side.
- `first_line_formation_tick` per side.

## BRF Integration
- Formation events are appended into BRF tactical timeline lines.
- split: "Fleet X formation shows structural separation."
- envelopment: "Fleet X begins surrounding maneuver."
- line: "Fleet X stretches into a linear attack formation."

## Determinism
- Observer computations are deterministic functions of runtime state.
- No random branch, no smoothing, no future-state peeking.
