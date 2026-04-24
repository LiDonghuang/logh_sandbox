# PR9 Phase II - `signed_longitudinal_backpedal` Bounded Implementation Report

Date: 2026-04-23
Scope: first bounded locomotion-capability implementation slice
Status: implemented locally; validation passed

**Line classification:** Locomotion capability line
**Owner classification:** capability-layer implementation; fleet authorization unchanged
**Honest claim boundary:** first bounded reverse/backpedal realization only

## 1. Static Owner / Path Audit

Active owner preserved:

- runtime owner: `runtime/engine_skeleton.py`
- Unit desire producer: `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- locomotion realization consumer: `EngineTickSkeleton.integrate_movement(...)`

Harness / viewer roles preserved:

- `test_run/settings_accessor.py`
  - path access only
- `test_run/test_run_scenario.py`
  - fail-fast settings preparation only
- `test_run/test_run_execution.py`
  - passes explicit settings into runtime and exports minimal debug
- `viz3d_panda/app.py`
  - consumes focus indicators only

No target or combat owner moved:

- `_compute_unit_intent_target_by_unit(...)` remains the same-tick target owner
- `resolve_combat(...)` still consumes selected target identity for re-check /
  fire / damage

## 2. Exact Carrier Added And Range Validation

New explicit Unit desire carrier:

- `desired_longitudinal_travel_scale`

Semantic meaning:

- signed longitudinal travel ask along realized facing
- `+1.0` means forward longitudinal travel within the speed cap
- `0.0` means no longitudinal travel ask
- negative values mean bounded backward travel along realized facing

Declared range:

- `[-1.0, 1.0]`

Fail-fast behavior:

- when `signed_longitudinal_backpedal` is enabled, runtime requires the carrier
- missing carrier raises an error
- non-finite carrier raises an error
- out-of-range carrier raises an error

Existing carrier meanings preserved:

- `desired_heading_xy`
  - remains heading / facing intent
- `desired_speed_scale`
  - remains unsigned speed amplitude / cap
  - no negative meaning was overloaded onto it

Experimental settings surface:

- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled`
  - default `false`
- `runtime.physical.locomotion.signed_longitudinal_backpedal_reverse_authority_scale`
  - first review value `0.45`
  - valid range `(0.0, 1.0]`

The boolean is only an experimental gate. It is not the primary locomotion
design.

## 3. Compile Check

Passed:

```powershell
python -m py_compile runtime\engine_skeleton.py test_run\settings_accessor.py test_run\test_run_scenario.py test_run\test_run_execution.py test_run\test_run_entry.py viz3d_panda\app.py
```

Passed:

```powershell
@'
import json
from pathlib import Path
for rel in [
    'test_run/test_run_v1_0.runtime.settings.json',
    'test_run/test_run_v1_0.testonly.settings.json',
    'test_run/test_run_v1_0.settings.comments.json',
]:
    json.loads(Path(rel).read_text(encoding='utf-8-sig'))
print('json ok')
'@ | python -
```

Result:

- `json ok`

Passed:

```powershell
git diff --check
```

## 4. Default-Off No-Drift Result

Posture:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`
- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled = false`

Compared against the accepted default-switch-false structural reference anchors:

- `battle_36v36`
- `battle_100v100`
- `neutral_36`
- `neutral_100`

Comparison normalized:

- position frames with `runtime_debug` removed
- combat telemetry
- observer telemetry excluding `tick_elapsed_ms`

Result:

| Scenario | Frames no-debug | Combat telemetry | Observer telemetry |
|---|---|---|---|
| `battle_36v36` | pass | pass | pass |
| `battle_100v100` | pass | pass | pass |
| `neutral_36` | pass | pass | pass |
| `neutral_100` | pass | pass | pass |

Conclusion:

- default-off behavior did not drift
- the new gate preserves the current unsigned forward-only locomotion path when
  disabled

## 5. Experimental-On Battle Validation

Posture:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`
- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled = true`
- reverse authority limiter: `0.45`

Battle validation:

| Scenario | Ticks | Negative ask ticks | Negative realized speed ticks | Backward unit samples | Total unit samples | Min ask | Min realized signed speed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `battle_36v36` | 500 | 171 | 171 | 3398 | 28037 | -0.084546 | -0.037274 |
| `battle_100v100` | 500 | 88 | 87 | 3412 | 81894 | -0.072566 | -0.029957 |

Neutral shared-path checks:

| Scenario | Ticks | Negative ask ticks | Negative realized speed ticks | Backward unit samples | Total unit samples | Min ask | Min realized signed speed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `neutral_36` | 447 | 0 | 0 | 0 | 16092 | 1.0 | 0.0 |
| `neutral_100` | 448 | 0 | 0 | 0 | 44800 | 1.0 | 0.0 |

Read:

- battle cases produced explicit negative signed-longitudinal asks
- battle cases realized negative signed longitudinal speed
- neutral cases stayed forward-only under the same enabled gate because no
  behavior-line back-off ask was present

## 6. Short Human-Readable Replay Read

The behavior-line reference with the new gate off had:

- `battle_36v36`: `0` negative ask ticks and `0` backward samples
- `battle_100v100`: `0` negative ask ticks and `0` backward samples

With the new gate on:

- `battle_36v36`
  - `171` ticks had negative signed-longitudinal asks and realized negative
    signed speed
  - `3398` unit samples moved backward along their own facing axis
  - `2757` samples were keep-front backward samples: facing still pointed
    substantially toward the enemy while velocity moved away
- `battle_100v100`
  - `88` ticks had negative signed-longitudinal asks
  - `87` ticks realized negative signed speed
  - `3412` unit samples moved backward along their own facing axis
  - `2728` samples were keep-front backward samples

Plain read:

1. Rotational pullback is reduced in permitted give-ground windows because some
   give-ground is now realized as signed longitudinal travel instead of only by
   turning the movement heading away.
2. The battle now shows literal backward travel while keeping facing in bounded
   windows.
3. This remains below retreat / turn-away semantics: reverse authority is weak,
   the ask is local and bounded, and orientation remains battle-facing.
4. Target and combat ownership stayed unchanged.
5. New residuals remain: reverse motion is mild, deep overlap recovery can still
   fragment, lateral firing opportunity is not solved, and this is not a full
   facing/translation decoupling system.

## 7. Minimal Debug / VIZ Surface

Added one compact ask read:

- `desired_longitudinal_travel_scale_min`
- VIZ label: `lng`

Added one compact realized-speed read:

- `realized_signed_longitudinal_speed_min`
- VIZ label: `vspd`

These are emitted only when signed-longitudinal diagnostics exist. Default-off
runs do not grow NaN placeholder fields in the focus payload.

No broad indicator catalog was added.

## 8. What This Slice Still Does Not Solve

This slice does not implement:

- retreat
- turn-away retirement
- lateral strafe
- arbitrary facing / translation decoupling
- target-owner redesign
- combat-owner redesign
- behavior-line retuning
- module split
- broad locomotion rewrite
- full 3D locomotion redesign

It only opens the first explicit, default-off, bounded locomotion capability for
signed longitudinal travel along realized facing.
