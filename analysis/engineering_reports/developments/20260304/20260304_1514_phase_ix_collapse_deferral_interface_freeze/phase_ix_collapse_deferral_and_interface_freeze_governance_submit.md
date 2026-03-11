# Governance Submit - Phase IX Collapse Runtime Deferral + Shadow Interface Freeze
Engine Version: v5.0-alpha5
Scope: Observer/runtime boundary enforcement + interface freeze + Movement 3A feature-boundary kickoff
Result: Implemented

## 1. Directive Compliance Summary
1. Collapse runtime deferral: enforced.
2. Collapse shadow interface freeze: documented and archived.
3. BRF audit fields retained/added as required.
4. Movement 3A clean feature boundary: initiated via `runtime.movement_model` (`v1|v3a`) with no equation change yet.

## 2. Implemented Controls
### 2.1 Runtime Deferral (Collapse)
1. `collapse_v2_shadow` is computed in observer post-processing only.
2. No runtime branch in movement/targeting/combat/PD/collapse consumes `collapse_v2_shadow`.
3. `collapse_decision_source_effective` is fixed to `legacy_v2` in BRF snapshot for all modes.

### 2.2 Frozen Interface Fields
Implemented per-tick fields:
1. `tick`
2. `pressure_v2_shadow`
3. `collapse_v2_shadow`
4. `pressure_sustain_counter`
5. `C_conn_signal`
6. `C_coh_signal`
7. `ForceRatio`
8. `AttritionMomentum`

Implemented per-run summary fields:
1. `first_tick_pressure_v2_shadow`
2. `first_tick_collapse_v2_shadow`
3. `%ticks_pressure_true`
4. `%ticks_collapse_true`
5. `notes`

### 2.3 BRF Snapshot Audit Fields
Run Configuration Snapshot now includes:
1. `test_mode`
2. `runtime_decision_source_effective`
3. `collapse_decision_source_effective`
4. `movement_model_effective`

## 3. Determinism Spot-check (FR8_MB8_PD5)
Digest contract after this change:
1. mode0 digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
2. mode1 digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
3. mode2 run1 digest: `7087f78322fa2864c08bdc0f16a3dc123fd0776bfdb2ff80c7f77c71fa7643e0`
4. mode2 run2 digest: `7087f78322fa2864c08bdc0f16a3dc123fd0776bfdb2ff80c7f77c71fa7643e0`

Checks:
1. mode0 == mode1: PASS
2. mode2_run1 == mode2_run2: PASS
3. mode1 != mode2: PASS (allowed)

## 4. Movement 3A Kickoff Boundary
To begin Phase 3A under controlled boundary, runtime config now carries:
1. `movement_model = v1|v3a`

Current status:
1. `v1` remains canonical and default.
2. `v3a` switch boundary is established for upcoming implementation.
3. No movement equation changes were introduced in this package.

## 5. Files Changed (Scope)
1. `analysis/test_run_v1_0.py`
2. `analysis/test_run_v1_0.settings.json`
3. `analysis/engineering_reports/developments/20260304/20260304_1514_phase_ix_collapse_deferral_interface_freeze/collapse_v2_shadow_interface_freeze_v1.0.md`
4. `analysis/engineering_reports/developments/20260304/20260304_1514_phase_ix_collapse_deferral_interface_freeze/phase_ix_collapse_deferral_and_interface_freeze_governance_submit.md`

## 6. Non-Changes (Explicit)
1. No combat formula changes.
2. No targeting semantic changes.
3. No PD formula changes.
4. No collapse runtime decision formula changes.
5. No movement equation changes in this package.
