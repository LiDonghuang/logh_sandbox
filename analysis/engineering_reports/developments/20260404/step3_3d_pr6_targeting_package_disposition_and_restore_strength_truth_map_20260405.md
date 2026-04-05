# PR6 Targeting Package Disposition and Restore Strength Truth Map

Status: working engineering disposition / planning record  
Date: 2026-04-05  
Scope: current local targeting dirty-group disposition plus next-step `restore_strength` ownership planning  
Authority: engineering working record only; not merge approval, not decoupling implementation approval

## 1. Intent

This record fixes two immediate thread-scope needs without reopening broader design work:

1. decide how the current local targeting dirty group should be handled
2. establish one truthful ownership map for the next cleanup step:
   - `restore_strength` ownership re-rooting / decoupling planning

This record does **not**:

- reopen targeting doctrine
- approve decoupling implementation
- approve old-family retirement
- change runtime behavior

## 2. Current targeting dirty-group disposition

The currently reviewed local dirty group was:

- `runtime/engine_skeleton.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `README.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_targeting_logic_expected_damage_candidate_record_20260404.md`

Current read:

- the core targeting candidate is coherent enough to package as its own mechanism carrier
- an earlier local review found one Human quick-test override mixed into the same file
- Human has now explicitly asked to revert that quick-test override
- after that reversion, the targeting package can be treated as one clean mechanism subset again

### Carrier-in subset

The following changes belong to the targeting mechanism carrier:

- `runtime/engine_skeleton.py`
  - widen `fire_quality_alpha` runtime clamp from `[0.0, 0.2]` to `[0.0, 1.0]`
  - remove fleet `targeting_logic` blend from active target scoring
  - use fixed score:
    - `normalized_hp / expected_damage_ratio`
  - keep expected damage bounded by:
    - `angle_quality = max(0, 1 + fire_quality_alpha * cos(theta))`
    - `range_quality = 1.0` inside the optimal band and then linear decay to `0.0` at `attack_range`

- `test_run/test_run_scenario.py`
  - expose `fire_quality_alpha_effective` in battle and neutral prepared summaries

- `test_run/test_run_v1_0.runtime.settings.json`
  - `runtime.physical.fire_control.fire_quality_alpha = 0.33`
  - `runtime.physical.fire_control.fire_optimal_range_ratio = 0.5`
  - `runtime.physical.fire_control.alpha_safe_max = 1.0`

- `README.md`
  - update documented fire-quality defaults to match the current bounded runtime read

- `step3_3d_pr6_targeting_logic_expected_damage_candidate_record_20260404.md`
  - update the record so it truthfully describes the fixed expected-damage-guided score and current defaults

### Resolved local override

One earlier local quick-test override was:

- `test_run/test_run_v1_0.runtime.settings.json`
  - `run_control.max_time_steps: -1 -> 500`

Current read:

- this was a Human quick-test change, not targeting behavior
- Human has now explicitly requested reversion to `-1`
- this override is therefore no longer part of the current targeting package decision

### Disposition result

Disposition result is:

- `package` the targeting carrier-in subset
- the earlier `max_time_steps = 500` quick-test override is no longer part of the active local package after Human-requested reversion
- do **not** reopen targeting stabilization as a new design phase
- do **not** discard the whole dirty group

## 3. Current truthful `restore_strength` ownership map

### Active public surface

Current Human-facing active surface is:

- `runtime.movement.v4a.restore_strength`

Current validation / ownership gate lives in:

- `test_run/test_run_scenario.py::_build_movement_cfg(...)`

Current read there:

- `v4a_restore_strength` is validated in `[0.0, 1.0]`
- it is carried as `movement_cfg["v4a_restore_strength"]`
- it is exposed as `movement_cfg["v4a_restore_strength_effective"]` for active `v4a`

### Active harness bridge

Current bridge is in:

- `test_run/test_run_execution.py`

Current active behavior:

- when `movement_model == "v4a"`:
  - `movement_surface["v3a_experiment"] = exp_precontact_centroid_probe` if `restore_strength < 1.0`
  - `movement_surface["v3a_experiment"] = base` if `restore_strength == 1.0`
  - `movement_surface["centroid_probe_scale"] = restore_strength`

Truth read:

- `v4a.restore_strength` is not yet native runtime ownership
- it is a harness-side bridge onto older `v3a` / `v3_test` carrier fields

### Active runtime carrier

Current runtime dependency chain is:

- `runtime_cohesion_decision_source = v3_test`
- movement experiment surface:
  - `movement_surface["v3a_experiment"]`
- movement scalar surface:
  - `movement_surface["centroid_probe_scale"]`
- runtime read site:
  - `runtime/engine_skeleton.py`
  - inside `integrate_movement(...)`
  - `cohesion_x` / `cohesion_y` are multiplied by `centroid_probe_scale`
  - only when `movement_v3a_experiment == exp_precontact_centroid_probe`

This means the currently active role is:

- `v4a.restore_strength`
  - reusing a `v3a` experiment switch
  - reusing a centroid-probe scalar carrier
  - under the still-live `v3_test` runtime decision family

This is transitional support, not native `v4a` ownership.

Additional truth point:

- `runtime/engine_skeleton.py::_movement_surface` currently has no dedicated native key such as:
  - `v4a_restore_strength`
  - `v4a_restore_scale`
  - other explicit `v4a` restore-only scalar host

So the decoupling step should not be read as merely reconnecting an already-existing native runtime surface.

## 4. Candidate native `v4a` owner for decoupling planning

The candidate native runtime owner should be read as:

- still inside `runtime/engine_skeleton.py`
- still inside the maintained `v4a` movement hot path
- specifically at the existing `v4a` cohesion contribution seam, not as another harness-only relay

Current best candidate seam is:

- the `v4a_active` branch in `integrate_movement(...)`
- around the existing fleet/unit-local movement composition where:
  - `cohesion_x`
  - `cohesion_y`
  - `maneuver_x`
  - `maneuver_y`
  are already composed for active `v4a`

Current planning read:

- decoupling should establish one explicit `v4a`-native restore/cohesion-strength read in the maintained `v4a` path
- decoupling should then make the `v3a_experiment` / `centroid_probe_scale` bridge non-necessary for `v4a.restore_strength`
- this should not be misframed as only moving a setting name or deleting an old branch
- because no native restore host exists yet, the implementation will likely require one small explicit runtime-surface addition rather than a pure harness-side rewiring

## 5. Exact next-step planning scope

The next planning turn should stay within:

- `test_run/test_run_scenario.py`
  - current validation and active-surface truth
- `test_run/test_run_execution.py`
  - current harness bridge
- `runtime/engine_skeleton.py`
  - current runtime carrier and candidate native seam
- optional truth-surface docs only if needed for mismatch correction after the plan is agreed

The next planning turn should **not** yet:

- implement the native `v4a` owner
- retire `v3a` / `v3_test` families
- narrow taxonomy broadly
- reopen targeting design

## 6. Planning questions to answer before implementation

The next decoupling-planning pass should answer:

1. what exact runtime scalar or seam will become the native `v4a` restore owner?
2. does that native owner act only on the cohesion contribution, or on a broader restoration composite?
3. how will paired comparison be run against the recovered anchor before old carrier retirement?
4. after the native owner exists, which old bridge writes become removable first?

## Bottom Line

The current thread read is now:

- targeting stabilization as a concept phase is already done
- the local targeting dirty group should be packaged, not redesigned
- packaging must exclude the Human local `max_time_steps = 500` quick-test override
- the next true main task is `restore_strength` ownership re-rooting / decoupling planning
- that planning must treat the current path as:
  - `v4a` public surface
  - harness bridge
  - old `v3a` / `v3_test` runtime carrier
  - not yet native `v4a` runtime ownership
