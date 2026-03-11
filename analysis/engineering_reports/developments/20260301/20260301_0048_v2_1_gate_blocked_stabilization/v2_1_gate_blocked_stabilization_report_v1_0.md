# Engineering Report v1.0 - Phase V.2 Gate-Blocked Stabilization
Engine Version: v5.0-alpha4
Modified Layer: Movement (`integrate_movement`) optimization only
Affected Parameters: mobility_bias (already canonical-active), no new parameters
Cross-Dimension Coupling: none
Mapping Impact: none beyond existing V2.1 mapping
Backward Compatible: yes (`mobility_bias=5` bitwise with alpha3)

## A) Immediate Questions
### A1. Mapping Activation Audit (10 parameters)
| Archetype Parameter | Layer | implemented? | where (file:function:line) | gate dependency | notes |
|---|---|---|---|---|---|
| force_concentration_ratio | Movement | N | - | - | No runtime read path in engine_skeleton. |
| mobility_bias | Movement | Y | runtime/engine_skeleton.py:integrate_movement:239-243, 301-333 | MB=5 bitwise vs alpha3 required | Canonical MB_eff mapping active and clipped to [-0.2,+0.2]. |
| offense_defense_weight | Combat | N | runtime/engine_skeleton.py:resolve_combat:1736-1737 (UnitState field only) | If activated from archetype, ODW=5 regression required | Combat reads UnitState.offense_defense_weight, but test initialization does not map archetype ODW into UnitState. |
| risk_appetite | Movement | N | - | - | No runtime read path. |
| time_preference | Movement | N | - | - | No runtime read path. |
| targeting_logic | Targeting | N | - | - | evaluate_target() is archetype-independent nearest-enemy centroid heading. |
| formation_rigidity | Movement + Cohesion-FSR | Y | runtime/engine_skeleton.py:evaluate_cohesion:71; integrate_movement:238; FSR coupling:436-437 | Determinism + no pipeline reorder | Canonical FR mapping active in cohesion, movement composition, and FSR k_f. |
| perception_radius | Contact | N | - | - | No runtime read path. |
| pursuit_drive | Targeting | N | - | - | No runtime read path. |
| retreat_threshold | Combat | N | - | - | No runtime read path. |

### A2. Metric Ownership Audit
- Prior V2 report ownership was not fully aligned (per-case gate judgment vs single FR5_MB5 reference mixed behavior and gate ownership).
- Ownership is now aligned under an explicit contract:
  - Scenario set: FRxMB 3x3 variant on Fleet-A, Fleet-B neutral, mirrored companion per case.
  - Determinism: two runs per case, digest equality.
  - Mirror: macro mean_abs_antisym_error over 9 paired cases, degrade vs alpha3.
  - Jitter: macro mean over same 9-case set, degrade vs alpha3.
  - Overhead: macro mean per_tick over same 9-case set, degrade vs alpha3.

## B) Allowed Work (Fix Track)
- Applied: MB hot-path cache optimization (per-fleet target-axis normalization, removed per-unit repeated normalization).
- Not applied: no combat/targeting/contact/projection changes; no tunable additions; no mapping-form changes.

## C) 6-Gate + Overhead
- Determinism: PASS
- mobility_bias=5 bitwise vs alpha3: PASS
- Mirror degradation <= +5%: PASS (old=0.292932, new=0.205417, degrade=-29.88%)
- Jitter degradation <= +10%: PASS (old=5775.00, new=6312.78, degrade=9.31%)
- Runtime overhead <= +10%: PASS (old=0.022173s/tick, new=0.021771s/tick, overhead=-1.81%)
- No new attractor proxy: PASS

## D) Retained / Rolled-Back
### Retained
- Canonical MB mapping and clip range retained.
- MB=0 legacy-equivalent path retained for bitwise guarantee.
- Pipeline ordering retained (no projection reorder / no multipass).
### Rolled-Back
- None in this round.

### Debug-only (default OFF)
- `debug_fsr_diag_enabled=False`
- `debug_diag4_enabled=False`
- `debug_diag4_rpg_enabled=False`
- `debug_contact_assert=False`
- Outlier debug constants are diagnostics-only.

Artifacts:
- v2_1_gate_blocked_summary_v1_0.json
- v2_1_gate_blocked_metrics.csv
