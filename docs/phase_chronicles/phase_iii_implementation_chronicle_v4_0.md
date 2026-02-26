# Phase III Implementation Chronicle
(Technical Execution Record)

## 1) Version Evolution Table

| Version ID | Files Modified | Core Technical Change | Determinism Impact | Mirror Symmetry Impact |
|---|---|---|---|---|
| v3.6 | `runtime/engine_skeleton.py`, `runtime/engine_driver_dummy.py` | Minimal deterministic combat added (in-range attack, simultaneous damage, unit removal). | Yes (preserved) | No |
| v3.7 | `runtime/engine_skeleton.py`, `analysis/test_run_v1_0.py` | Intra-fleet separation term added to movement composition (snapshot-based). | Yes (preserved) | Yes |
| v3.8 | `runtime/engine_skeleton.py` | Targeting within range changed to weakest-local focus (lowest HP, then nearest, then deterministic tie-break). | Yes (preserved) | Yes |
| v3.9 | `runtime/engine_skeleton.py` | Hard min-unit-spacing projection added (single-pass post-movement penetration guard). | Yes (preserved) | Yes |
| v3.9a | `runtime/engine_skeleton.py` | Zero-distance projection fallback changed from world-axis fallback to deterministic pair-based mapping. | Yes (preserved) | Yes |
| v3.9b | `runtime/engine_skeleton.py` | Projection writeback changed from immediate pair writeback to accumulated single-pass apply. | Yes (preserved) | Yes |
| v3.9c | `runtime/engine_skeleton.py` | Zero-distance fallback mapping switched to fleet-local rank based mapping (removed fleet-label/global-id dependency in fallback seed). | Yes (preserved) | Yes |
| v3.10 | `runtime/engine_skeleton.py` | Target final tie-break changed to fleet-local stable numeric rank (removed global `unit_id` tie-break). | Yes (preserved) | Yes |
| v3.10-NSAM.1 | `runtime/engine_skeleton.py`, `runtime_numeric_stability_log.md` | Separation threshold branch stabilized via squared-distance + epsilon deadband. | Yes (preserved) | Yes |
| v3.10-NSAM.2 | `runtime/engine_skeleton.py`, `runtime_numeric_stability_log.md` | Combat boundary comparisons stabilized (squared-distance, epsilon-based equal-distance handling). | Yes (preserved) | Yes |
| v3.10-NSAM Stabilized | `runtime_numeric_stability_log.md` | Residual antisymmetry accepted as stabilized baseline. | Yes (preserved) | Yes |
| v3.11 | `runtime_v0_1.py`, `runtime/engine_skeleton.py` | ODW activated in combat exchange with exchange-conserving linear bias and clamp. | Yes (preserved) | No |
| v3.12 | `runtime/engine_skeleton.py` | Bounded geometric fire coupling introduced using engaged-count ratio term. | Yes (preserved) | No |
| v3.12b | `runtime/engine_skeleton.py` | Geometric coupling gain recalibrated (`gamma: 0.3 -> 0.15`). | Yes (preserved) | No |
| v3.13 | `runtime/engine_skeleton.py` | Geometric coupling replaced by participation-ratio coupling (`p_A`, `p_B`) with fixed `gamma=0.3`. | Yes (preserved) | No |
| v4.0 | `runtime/engine_skeleton.py` | Targeting refactor to unified score-based selector; behavior preserved identical to v3.13 outputs. | Yes (preserved) | No change |

## 2) Combat Equation Evolution

- v3.6 deterministic combat base:
  - Attack condition: `dist_sq <= attack_range_sq - combat_cmp_eps`
  - Damage accumulation (per attacker to chosen target):
    `incoming_damage[target] += damage_per_tick`
  - Resolution: simultaneous HP writeback after full assignment.

- v3.11 ODW exchange-conserving linear bias:
  - `bias_i = 0.6 * (ODW_i - 0.5)`
  - `damage_scale(i->j) = 1 + bias_i - bias_j`
  - clamp: if `damage_scale < 0`, set `damage_scale = 0`
  - `incoming_damage[j] += damage_per_tick * damage_scale(i->j)`

- v3.12 bounded geometric coupling (engagement-count form):
  - For engagement pair `(A_i, B_j)`:
    - `n_A = #A attackers currently attacking B_j`
    - `n_B = #B attackers currently attacking A_i`
    - `f = 1 + gamma * (n_A - n_B) / (n_A + n_B)`, `gamma = 0.3`
  - Damage term:
    - `damage(i->j) = damage_per_tick * (1 + bias_i - bias_j) * f`

- v3.12b recalibration:
  - Same structure as v3.12, `gamma = 0.15`.

- v3.13 participation-ratio coupling (final Phase III combat form):
  - `N_F = alive units in fleet F (snapshot)`
  - `n_F = attackers in fleet F with assigned in-range target (snapshot)`
  - `p_F = n_F / N_F` if `N_F > 0`, else `0`
  - Coupling for attack `i->j`:
    - `f(i,j) = 1 + 0.3 * (p_fleet(i) - p_fleet(j))`
  - Final damage:
    - `damage(i->j) = damage_per_tick * max(0, 1 + bias_i - bias_j) * f(i,j)`

## 3) Mirror Symmetry Repair Log

- Zero-distance fallback issue:
  - Initial projection fallback used world-axis constant when `distance == 0`.
  - Replaced with deterministic pair-based fallback vector generation.
  - Then switched to fleet-local rank-based pair mapping.

- Fleet-label/global-id tie-break issue:
  - Target tie-break removed global `unit_id` dependency.
  - Replaced by fleet-local stable numeric rank tie-break.

- Accumulated projection writeback fix:
  - Immediate pair writeback removed.
  - Snapshot-based pairwise symmetric delta accumulation applied once after sweep.

- Antisymmetry metric tracking (recorded):
  - v3.10 baseline: `mean_abs_antisym_error = 5.0889`, `diagonal_mean = 2.7`
  - v3.10-NSAM.1: `mean_abs_antisym_error = 4.4667`, `diagonal_mean = -1.2`
  - v3.10-NSAM.2: `mean_abs_antisym_error = 4.4667`, `diagonal_mean = -1.2`
  - v3.10-NSAM Stabilized baseline: `mean_abs_antisym_error = 4.4667`
  - v4.0 equivalence run set (before/after refactor): `mean_abs_antisym_error = 4.82`, `diagonal_mean = 1.1` (unchanged across refactor)

## 4) NSAM (Numeric Stability Autonomous Mode) Record

- Threshold epsilon introduction:
  - Separation branch uses epsilon deadband (`sep_branch_eps`) in squared-distance comparison.
  - Combat range branch uses epsilon deadband (`combat_cmp_eps`) in squared-distance comparison.

- Squared-distance comparisons:
  - `distance` threshold checks replaced/normalized to `dist_sq` checks where applicable.

- Deadband logic:
  - Equal-HP and equal-distance comparisons use epsilon-tolerant branch conditions.
  - Boundary checks use `attack_range_sq - eps` / `r_sep_sq - eps` forms.

- Snapshot-only enforcement:
  - Targeting/combat distance, HP, alive-status, and participation statistics computed from same tick snapshot before damage writeback.

- Single-pass projection rule:
  - Post-movement projection performs one pair sweep (snapshot distances), one accumulated delta apply, no second pass.

## 5) Determinism Guarantees

- Snapshot order:
  - Tick-level targeting and combat calculations use pre-writeback snapshot maps (`positions`, `hp`, `alive`).

- Pairwise accumulation rules:
  - Same-fleet unordered pair iteration with deterministic ordering.
  - Symmetric pair contributions (`+v`, `-v`) for separation/projection accumulators.

- No random shuffle:
  - No random execution order in core engine targeting, movement, projection, or combat.

- Simultaneous damage resolution:
  - All combat hits first accumulate into `incoming_damage`.
  - HP updates/removals occur after full accumulation sweep.

## 6) Known Technical Constraints (Hard)

- No recursive participation counting inside same tick damage writeback.
- No dynamic mutation of snapshot sets during snapshot-based targeting/combat selection.
- No multi-pass projection / no relaxation loops.
- No fleet-label dependency in zero-distance projection fallback mapping.
- No world-axis fixed fallback direction for zero-distance projection.
- No order-dependent immediate projection writeback.
- No random tie-breaks or stochastic branch selection.
- No change to attack-range semantics during target assignment resolution.
- No asynchronous HP application during combat accumulation.

## 7) Baseline Freeze Summary

- Engine Version: v3.13
- Targeting: v4.0 structural refactor (behavior identical)
- Combat Class: Isotropic Linear Exchange + ODW + Participation Ratio
- Deterministic: Yes
- Mirror Symmetry Level: Level 1 (macro antisymmetry)
- Runaway: None structural
