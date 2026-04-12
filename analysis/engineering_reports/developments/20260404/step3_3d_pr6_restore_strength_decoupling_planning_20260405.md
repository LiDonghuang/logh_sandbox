# PR6 Restore Strength Decoupling Planning

Status: engineering planning record  
Date: 2026-04-05  
Scope: `restore_strength` ownership re-rooting / decoupling planning only  
Authority: working plan only; not implementation approval, not retirement approval

## 1. Intent

This record turns the current `restore_strength` read into one implementation-ready planning surface.

It does **not** implement decoupling.

It exists to make the next step explicit on:

- current active ownership
- current transitional bridge
- current runtime carrier
- candidate native `v4a` owner
- minimal implementation scope
- settings/container/comments sync obligations

## 2. Verified current chain

The current active path is:

1. `test_run/test_run_v1_0.testonly.settings.json`
   - `runtime.movement.v4a.restore_strength`

2. `test_run/settings_accessor.py`
   - `v4a_restore_strength -> ("movement", "v4a", "restore_strength")`

3. `test_run/test_run_scenario.py::_build_movement_cfg(...)`
   - reads and validates `v4a_restore_strength`
   - carries:
     - `movement_cfg["v4a_restore_strength"]`
     - `movement_cfg["v4a_restore_strength_effective"]`

4. `test_run/test_run_execution.py`
   - when `movement_model == "v4a"`:
     - writes `movement_surface["v3a_experiment"]`
     - writes `movement_surface["centroid_probe_scale"] = v4a_restore_strength`

5. `runtime/engine_skeleton.py`
   - runtime still evaluates cohesion under:
     - `runtime_cohesion_decision_source = v3_test`
   - movement still consumes:
     - `movement_surface["v3a_experiment"]`
     - `movement_surface["centroid_probe_scale"]`
   - `integrate_movement(...)` scales `cohesion_x` / `cohesion_y` by `centroid_probe_scale`
     only when:
     - `movement_v3a_experiment == exp_precontact_centroid_probe`

## 3. Truthful ownership read

Current truthful read is:

- public owner:
  - `runtime.movement.v4a.restore_strength`
- transport / bridge:
  - `test_run/test_run_execution.py`
- runtime carrier actually doing the work:
  - old `v3a` / `v3_test` centroid-probe path

So the parameter is active, but the ownership is still transitional.

This is **not**:

- native `v4a` runtime ownership
- a dead path
- a pure docs mismatch only

## 4. Verified runtime surface gap

Current runtime `_movement_surface` contains:

- `alpha_sep`
- `model`
- `v3a_experiment`
- `centroid_probe_scale`
- `odw_posture_bias_*`

It does **not** currently contain any dedicated native `v4a` restore host such as:

- `v4a_restore_strength`
- `v4a_restore_scale`
- other explicit `v4a` restore-only runtime scalar

This means decoupling cannot be treated as merely reconnecting an already-existing native runtime field.

A small explicit native runtime surface addition will likely be required.

## 5. Candidate native `v4a` owner

The best current candidate seam is inside:

- `runtime/engine_skeleton.py::integrate_movement(...)`

Specifically:

- the maintained `v4a_active` movement path
- near the existing cohesion contribution
  - `cohesion_x`
  - `cohesion_y`

Why this seam is the best current candidate:

- `restore_strength` currently acts as a bounded restore/cohesion-strength modifier
- the old carrier already scales the cohesion term only
- keeping the effect near the cohesion contribution is the narrowest behavioral re-root
- it avoids inventing a second harness-side owner
- it avoids disguising decoupling as pure parameter transport

Current planning read:

- decoupling should establish one native `v4a` runtime read that acts where
  the maintained `v4a` cohesion contribution is already composed
- after that native read exists, the `v3a_experiment` /
  `centroid_probe_scale` reuse becomes unnecessary for `v4a.restore_strength`

## 6. Minimal implementation scope

The first implementation round should stay inside:

- `runtime/engine_skeleton.py`
  - add one explicit native runtime host
  - consume it in the maintained `v4a` path

- `test_run/test_run_execution.py`
  - stop translating `v4a.restore_strength` into old `v3a` bridge writes for active `v4a`
  - keep old writes only where the old `v3a` family is still actually the owner

- `test_run/test_run_scenario.py`
  - keep validation and effective-summary truth aligned with the new carrier

- `test_run/settings_accessor.py`
  - update only if the active settings ownership path changes

- `test_run/test_run_v1_0.testonly.settings.json`
  - keep or move the parameter only if the ownership change formally justifies it

- `test_run/test_run_v1_0.settings.comments.json`
  - must be updated together with the real new owner wording

- `test_run/test_run_v1_0.settings.reference.md`
  - must be updated together with the real new owner wording

## 7. Human container / sync constraints

Human clarified the following and this planning turn accepts them as active engineering constraints:

- `test_run/test_run_v1_0.runtime.settings.json`
  - current-value container for runtime-owned parameters

- `test_run/test_run_v1_0.testonly.settings.json`
  - current-value container for test-only / not-yet-promoted parameters

- `test_run/test_run_v1_0.settings.comments.json`
  - authoritative parameter comments surface

Therefore future implementation must ensure:

1. if an old mechanism or parameter is deleted, it must be deleted from the relevant settings container(s) too
2. settings values must truthfully link to the active runtime mechanism
3. when a mechanism is formally accepted and ownership changes, the parameter may move from `testonly.settings` to `runtime.settings`
4. `settings.comments.json` must be updated in the same turn

Planning consequence:

- the decoupling implementation should not change parameter container location casually
- if `restore_strength` remains experimental after native re-rooting, it can stay in `testonly.settings`
- if Human later treats it as formal runtime-owned surface, that move should happen explicitly and with synchronized comments/reference updates

## 8. Non-goals for the first decoupling round

The first round should **not**:

- retire the whole `v3a` family
- retire `v3_test`
- redesign battle doctrine
- widen targeting logic
- perform broad settings taxonomy cleanup
- move unrelated parameters between `testonly` and `runtime`

## 9. Validation shape for the future implementation round

When implementation begins, the round should validate against the recovered anchor using:

- `python -m py_compile`
- one paired comparison against the current recovered anchor for the active battle / neutral read
- no broad DOE reopening

The core question is:

- does the new native `v4a` owner preserve the recovered read while removing the old bridge dependency?

## 10. Immediate next action after this planning record

The next concrete engineering move should be:

1. package the current targeting subset as its own mechanism carrier when requested
2. then open one bounded decoupling implementation turn using this plan

## Bottom Line

The next decoupling turn should be read as:

- not “delete old carrier”
- not “move parameter names around”
- but:
  - introduce one small native `v4a` restore host
  - connect the active `restore_strength` surface to it
  - remove the old `v3a` / `v3_test` bridge dependence for active `v4a`
  - keep settings containers and comments truthful in the same turn
