# Runtime Numeric Stability Log

## Version Tag
- `v3.10-NSAM.1`

## Invariant Target
- Threshold branch symmetry stabilization in movement separation (`distance < r_sep`) under mirrored configurations.

## Numeric-Layer Modifications
- File: `runtime/engine_skeleton.py`
- Layer: `integrate_movement` separation branch only.
- Change:
  - Replaced direct threshold branch from:
    - `if 0.0 < distance < r_sep`
  - To squared-distance + symmetric epsilon deadband:
    - `distance_sq = dx*dx + dy*dy`
    - `if 0.0 < distance_sq < (r_sep*r_sep - sep_branch_eps)`
  - `sep_branch_eps = 1e-14`
- Unchanged:
  - Force composition equations
  - Cohesion/projection/target/combat semantics
  - Parameters and canonical structures
  - Deterministic execution model

## Before Metrics (v3.10 baseline)
- `mean_abs_antisym_error = 5.0889`
- `diagonal_mean = 2.7`
- `A wins / B wins / Draws = 55 / 42 / 3`
- `avg_survivor_diff (A-B) = 0.0`

## After Metrics (v3.10-NSAM.1)
- `mean_abs_antisym_error = 4.4667`
- `diagonal_mean = -1.2`
- `A wins / B wins / Draws = 50 / 47 / 3`
- `avg_survivor_diff (A-B) = 0.35`

## Determinism Verification
- Identical initial state double-run:
  - tick trajectory: identical
  - termination result: identical
  - survivor counts: identical
- Result: `Deterministic = Yes`

## Macro Behavioral Comparison
- FR macro outcomes remain in the same regime (no collapse or runaway behavior).
- Mirror error improved (`5.0889 -> 4.4667`) but not eliminated.
- New large systemic bias was not introduced; side win counts moved closer to parity (`55/42 -> 50/47`).
- Combat rule behavior unchanged.

## Escalation Notes
- Antisymmetry remains materially above numeric tolerance target.
- Root cause is only partially addressed by separation threshold stabilization.
- Recommended next NSAM target:
  - combat in-range/nearest boundary comparisons (`distance <= attack_range`, nearest tie boundary) with symmetric tolerance policy.

---

## Version Tag
- `v3.10-NSAM.2`

## Invariant Target
- Combat threshold symmetry stabilization:
  - in-range boundary (`distance <= attack_range`)
  - nearest/equal-distance comparison stability

## Numeric-Layer Modifications
- File: `runtime/engine_skeleton.py`
- Layer: `resolve_combat` numeric comparisons only.
- Changes:
  - Replaced sqrt in-range check with squared-distance threshold:
    - `dist_sq <= attack_range_sq - combat_cmp_eps`
  - Added symmetric epsilon comparator in target ranking:
    - HP compare with epsilon
    - distance-squared compare with epsilon
    - final tie by fleet-local numeric index (unchanged priority order)
- Unchanged:
  - Attack range value
  - Damage per tick
  - Target priority semantics (`HP -> nearest -> fleet-local index`)
  - Simultaneous damage resolution structure

## Before Metrics (v3.10-NSAM.1 baseline)
- `mean_abs_antisym_error = 4.4667`
- `diagonal_mean = -1.2`
- `A wins / B wins / Draws = 50 / 47 / 3`
- `avg_survivor_diff (A-B) = 0.35`

## After Metrics (v3.10-NSAM.2)
- `mean_abs_antisym_error = 4.4667`
- `diagonal_mean = -1.2`
- `A wins / B wins / Draws = 50 / 47 / 3`
- `avg_survivor_diff (A-B) = 0.35`

## Determinism Verification
- Identical initial state double-run:
  - tick trajectory: identical
  - termination result: identical
  - survivor counts: identical
- Result: `Deterministic = Yes`

## Macro Behavioral Comparison
- No FR macro regime shift detected.
- No new bias introduced relative to NSAM.1 baseline.
- Combat rule semantics preserved.

## Escalation Notes
- Relative antisymmetry reduction vs NSAM.1 baseline: `0%`.
- Per NSAM rule (`<10%` improvement), paused before further modifications.

---

## Stabilized Baseline Tag
- `v3.10-NSAM Stabilized`
- Decision: residual antisymmetry accepted as baseline; no further mirror-symmetry pursuit at this stage.
- Baseline residual:
  - `mean_abs_antisym_error = 4.4667`
  - `diagonal_mean = -1.2`

---

## Version Tag
- `v3.11`

## Invariant Target
- OffenseDefenseWeight (ODW) activation in combat exchange layer with exchange-conserving linear bias.

## Numeric/Behavioral Modifications
- Files:
  - `runtime_v0_1.py`
  - `runtime/engine_skeleton.py`
- Changes:
  - Added `offense_defense_weight: float = 0.5` to `UnitState`.
  - Combat damage uses linear bias:
    - `bias = 0.6 * (ODW - 0.5)`
    - `damage_scale = 1 + bias_attacker - bias_target`
    - clamp: if negative, set `damage_scale = 0`
- Unchanged:
  - Movement/Cohesion/Separation/Projection
  - Targeting priority
  - Attack range / dt / synchronous resolution structure

## Baseline Equivalence Check (ODW = 0.5 both sides)
- `mean_abs_antisym_error = 4.4667` (matches stabilized baseline)
- `diagonal_mean = -1.2` (matches stabilized baseline)
- `A/B/Draw = 50/47/3` (matches stabilized baseline)
- `avg_survivor_diff (A-B) = 0.35` (matches stabilized baseline)
- Determinism: `Yes`

## Phase 1 Results
- FR fixed at normalized `0.4` (raw `4.6`) for both sides.
- ODW_A in `{0.2, 0.5, 0.8}`, ODW_B fixed at `0.5`.
- Results:
  - `ODW=0.2`: winner `B`, ticks `287`, survivors `A=0, B=50`
  - `ODW=0.5`: winner `A`, ticks `300`, survivors `A=25, B=23`
  - `ODW=0.8`: winner `A`, ticks `292`, survivors `A=48, B=0`
- Damage clamp triggered: `No`
