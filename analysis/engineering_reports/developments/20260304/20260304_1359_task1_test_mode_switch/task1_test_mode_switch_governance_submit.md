# Governance Submit - Task 1 Test Runtime Mode Switch (Animation / Harness Parity)
Engine Version: v5.0-alpha5 (runtime semantics unchanged)
Modified Layer: test harness mode switch + observer/report gating only
Affected Parameters: `run_control.test_mode` (new)
Cross-Dimension Coupling: No
Runtime Behavior Change: No (combat/PD/collapse/movement unchanged)
Backward Compatible: Yes (supports `0/1/2` and `default/observe/test` parsing)

## Scope Confirmation
This task implemented a single execution switch to align animation entry and batch-observer/report pipeline behavior without touching runtime battle semantics.

Changed files:
1. `analysis/test_run_v1_0.py`
2. `analysis/test_run_v1_0.settings.json`

## `test_mode` Definition (Authoritative)
- `test_mode=0` (`default`):
  - Runtime path: baseline default runtime path
  - Observer/Event/BRF: disabled (minimal output)
- `test_mode=1` (`observe`):
  - Runtime path: baseline default runtime path (same semantics as mode 0)
  - Observer/Event/BRF: enabled
- `test_mode=2` (`test`):
  - Runtime path: Task 1 keeps same runtime semantics as mode 1
  - Observer/Event/BRF: enabled

## Pipeline Mapping (Task 1)
1. Runtime simulation loop (`EngineTickSkeleton.step`): unchanged for all modes.
2. Observer/event chain: enabled iff `test_mode >= 1`.
3. BRF export chain: enabled iff `test_mode >= 1`.
4. BRF Run Configuration Snapshot now includes:
   - `test_mode`
   - `test_mode_label`

## Determinism Verification (Required Case)
Case: `FR8_MB8_PD5`
- Setup used for check:
  - `force_concentration_ratio=8`, `mobility_bias=8`, `offense_defense_weight=5`
  - `attack_range=5`, `min_unit_spacing=2`, `arena_size=200`
  - `fire_quality_alpha=0.1`, `CH=on(0.1)`, `FSR=on(0.1)`, `boundary=off`

Runs:
1. Run A (`test_mode=0`):
   - digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
   - observer_non_nan_points: `0`
2. Run B (`test_mode=1`):
   - digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
   - observer_non_nan_points: `3664`
3. Run C (`test_mode=2`):
   - digest: `db28cc1969a3c50239b42b1e551c5b74a2cc092f62db656a6ffbc5933c1129da`
   - observer_non_nan_points: `3664`

Result:
1. A vs B digest equality: PASS
2. B vs C digest equality: PASS

Interpretation:
- `test_mode=1` successfully enables observer/event chain without runtime behavior drift.
- In Task 1 implementation, `test_mode=2` is parity-equivalent to mode 1 at runtime semantics level.

## Explicit Non-Changes
1. No combat rule changes.
2. No targeting semantic changes.
3. No PD/collapse runtime decision changes.
4. No movement numeric model changes.

## Assumptions
1. FR8_MB8_PD5 verification uses fixed parameterized fleets for deterministic parity proof.
2. Task 1 intentionally keeps mode 2 runtime-equivalent to mode 1; “test runtime path” differentiation is deferred unless separately approved.
