# PR9 Phase II - `signed_longitudinal_facing_axis_guard` Bounded Implementation Report

Date: 2026-04-23
Scope: bounded locomotion-capability correction
Status: implemented locally; validation passed

**Line classification:** Locomotion capability line
**Owner classification:** capability-layer correction; fleet authorization unchanged
**Honest claim boundary:** prevent turn-away forward motion from masquerading as
keep-front backpedal

## 1. Static Owner / Path Audit

Active runtime owner remains:

- `runtime/engine_skeleton.py`
- Unit desire producer:
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- locomotion realization consumer:
  - `EngineTickSkeleton.integrate_movement(...)`

Carrier split preserved:

- `desired_heading_xy`
  - facing intent
- `desired_speed_scale`
  - unsigned speed amplitude / cap
- `desired_longitudinal_travel_scale`
  - signed longitudinal forward / backward travel intent

No target or combat owner moved:

- `_compute_unit_intent_target_by_unit(...)` remains the target owner
- `resolve_combat(...)` remains the combat / fire / damage owner

No retreat, turn-away retirement, lateral strafe, behavior-line retuning, module
split, or broad locomotion rewrite was implemented.

## 2. Exact Runtime Touch Surface

Edited file:

- `runtime/engine_skeleton.py`

Primary active realization edit:

- `EngineTickSkeleton.integrate_movement(...)`

The correction is inline in the existing movement realization block:

- when `signed_longitudinal_backpedal_enabled` is false, the old
  `total_direction` facing path remains unchanged
- when the gate is true, `desired_heading_xy` is normalized and used as the
  facing target
- turn-rate limits still apply through `_rotate_direction_toward(...)`
- signed longitudinal speed is still realized along the resulting facing axis
- if `desired_longitudinal_travel_scale >= 0.0` and local translation pressure
  points away from that facing axis, the speed cap is reduced toward hold instead
  of rotating facing away to synthesize backward battle-axis motion

Small producer-side explicitness edit:

- `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- when the signed-longitudinal gate is enabled and the base heading vector is
  zero, the producer writes the current fleet-front vector into
  `desired_heading_xy`

Reason:

- this keeps the required facing carrier explicit
- it avoids a consumer-side silent fallback in no-enemy / neutral objective
  paths
- it does not change the default-off path

No new helper was added.
No debug catalog was added.
No compatibility wrapper was added.

## 3. Compile Check

Passed:

```powershell
python -m py_compile runtime\engine_skeleton.py test_run\settings_accessor.py test_run\test_run_scenario.py test_run\test_run_execution.py test_run\test_run_entry.py viz3d_panda\app.py
```

Passed:

```powershell
git diff --check
```

## 4. Default-Off No-Drift Result

Gate:

- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled = false`

Reference was generated before the facing-axis guard edit in the same workspace
state, with deterministic seeds:

- `run_control.random_seed = 424242`
- `runtime.metatype.random_seed = 424243`
- `battlefield.background_map_seed = 424244`

Default-off `battle_36v36`:

- before hash:
  - `8053142d43ae3dc49b952f9d9ef56e6dbfd15b0f7750622084b9fb3e3a83ab14`
- after hash:
  - `8053142d43ae3dc49b952f9d9ef56e6dbfd15b0f7750622084b9fb3e3a83ab14`
- result:
  - exact match

Default-off `battle_100v100`:

- before hash:
  - `6d8dd102229a06c1203fec7a218bf519224d1b5de31b9a53045b6c5ed70bb764`
- after hash:
  - `6d8dd102229a06c1203fec7a218bf519224d1b5de31b9a53045b6c5ed70bb764`
- result:
  - exact match

Hash payload included:

- final tick
- captured position / orientation / velocity / hit-point frames
- alive trajectory
- fleet-size trajectory
- combat telemetry

## 5. `36v36` Critical-Window Review (`60-80`)

Gate:

- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled = true`

Tick-60 row anchor:

- fleet A and B each partitioned into front / middle / rear rows from the tick
  60 enemy-axis ordering

Fleet A read:

| tick | R1 facing dot | R1 signed speed | R1 enemy-axis speed | R1 fake-turnaway count | R2 facing dot | R3 facing dot | R1-to-R3 depth |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 60 | 1.000 | 0.881 | 0.881 | 0 | 1.000 | 1.000 | 6.288 |
| 66 | 1.000 | 0.872 | 0.872 | 0 | 1.000 | 1.000 | 6.099 |
| 71 | 1.000 | 0.755 | 0.755 | 0 | 1.000 | 1.000 | 5.950 |
| 80 | 1.000 | 0.020 | 0.020 | 0 | 1.000 | 1.000 | 5.714 |

Before this guard, the observed comparable failure read was:

- tick 71 front-row facing dot:
  - `-0.299`
- tick 71 front-row signed speed:
  - `+0.202`
- tick 71 front-row enemy-axis speed:
  - `-0.060`
- tick 80 R1-to-R3 depth:
  - about `3.33`

After this guard:

- first-row facing remains battle-facing through the window
- positive speed along turned-away facing no longer creates backward battle-axis
  movement
- rows two and three remain battle-facing through the window
- row-depth compression at tick 80 is materially reduced

Important residual:

- `desired_longitudinal_travel_scale_min` remains `+1.0` through this critical
  tick 60 to tick 80 window
- therefore this slice mainly blocks fake backpedal and slows / holds pressure
  when the signed carrier is non-negative
- it does not make the behavior line authorize earlier negative backpedal in the
  tick 60 to tick 80 window

## 6. `100v100` Regression Review

Gate:

- `runtime.physical.locomotion.experimental_signed_longitudinal_backpedal_enabled = true`

Full-run aggregate:

- final tick:
  - `480`
- signed focus rows:
  - `960`
- negative ask rows:
  - `355`
- negative realized signed-speed rows:
  - `355`
- minimum `desired_longitudinal_travel_scale_min`:
  - `-0.087207`
- minimum `realized_signed_longitudinal_speed_min`:
  - `-0.038422`
- backward battle-axis unit samples:
  - `20180 / 41756`
- fake forward-turnaway samples:
  - `0`

This keeps literal backward realization available later in the run while blocking
the fake version where positive signed speed moves backward only because facing
turned away.

## 7. Short Human-Readable Replay Read

The guard does what this slice was meant to do.

In the 36v36 tick 60 to tick 80 contact window, the front row no longer rotates
through side/back angles. Rows two and three also remain facing the battle
instead of being pulled into the same rotational breakdown. The old visible
failure, "move backward by turning away and then going forward", is removed.

The visible result is not stronger early backpedal. It is a cleaner keep-front
hold / slow-down during the part of the window where the behavior line is still
asking for non-negative longitudinal travel.

Later in the run, real negative signed-longitudinal travel still occurs through
the explicit carrier. In both 36v36 and 100v100, fake forward-turnaway samples
were `0`.

Neutral smoke:

- `neutral_100`, gate true
- objective reached tick:
  - `484`
- no facing-carrier failure after the producer made zero-base facing explicit

## 8. What Still Remains Unsolved

This slice does not solve:

- behavior-line timing for earlier negative `desired_longitudinal_travel_scale`
- stronger backpedal magnitude
- retreat
- turn-away retirement
- lateral strafe
- arbitrary facing / translation decoupling
- target-owner redesign
- combat-owner redesign
- module split
- full 3D locomotion redesign

The main residual is now clearer:

- if Governance wants literal keep-front backward travel earlier in tick 60 to
  tick 80, that is no longer a locomotion-axis bug
- it is a behavior / authorization question about when the signed carrier should
  become negative

This implementation deliberately does not retune that behavior-line ask.
