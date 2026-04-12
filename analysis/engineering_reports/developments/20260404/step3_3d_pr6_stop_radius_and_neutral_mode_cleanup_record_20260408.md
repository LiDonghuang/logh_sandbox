Scope: test-only / harness + runtime bridge cleanup only

# Summary

This round performs a bounded cleanup on the active neutral fixture carrier:

1. `fixture.active_mode` is renamed from `neutral_transit_v1` to `neutral`
2. `hold_radius` is removed from the shared movement truth surface and restored to a neutral-only termination semantic as `stop_radius`
3. runtime expected-position entry no longer depends on `active_mode == neutral_transit_v1`

Battle and neutral continue to share the same active `v4a` movement mechanism family.
The only intended semantic difference remains objective source.

# Active Owner Read

After this round:

- `stop_radius`
  - is neutral-only objective termination semantics
  - is not the battle hold mechanism
  - is not carried by battle restore bundles
  - is not carried by the battle temp fixture carrier

- runtime expected-position bridge
  - now enters from direct bridge truth:
    - `expected_position_candidate_active`
    - `fleet_id`
    - local slot offsets
  - no longer requires `active_mode == neutral_transit_v1`

- runtime terminal step gate
  - now keys off bridge truth plus objective/termination presence
  - specifically:
    - `expected_position_candidate_active`
    - `fleet_id`
    - `objective_contract_3d`
    - `stop_radius`

# Files

- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_entry.py`
- `test_run/test_run_v1_0_viz.py`
- `viz3d_panda/replay_source.py`
- `viz3d_panda/app.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

# Validation

Minimal validation completed:

- `python -m py_compile runtime/engine_skeleton.py test_run/test_run_execution.py test_run/test_run_scenario.py test_run/test_run_entry.py test_run/test_run_v1_0_viz.py viz3d_panda/replay_source.py viz3d_panda/app.py`
- 5-tick smoke runs:
  - `neutral 1->4`
  - `neutral 4->1`
  - active battle default
  - active battle with `rect_centered_1.0`

All compiled and ran.

# Current Residual Read

This cleanup removes old neutral-only mode/radius ownership, but it does not fully eliminate the observed neutral residual:

- `neutral 4->1` still compresses less in forward depth than battle
- `neutral 1->4` still does not yet match battle read

So the current remaining issue is no longer the old `neutral_transit_v1` mode gate or the shared `hold_radius` naming mistake.
It remains in a deeper shared carrier / objective-seam layer.
