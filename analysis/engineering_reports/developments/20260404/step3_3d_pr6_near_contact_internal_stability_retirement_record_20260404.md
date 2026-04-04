Scope: test-only / harness-only

Summary
- Retired the `v4a` near-contact internal-stability group from the active public `test_run` surface:
  - `runtime.movement.v4a.battle_near_contact_internal_stability_blend`
  - `runtime.movement.v4a.battle_near_contact_speed_relaxation`
- Removed their execution-path effect from `test_run/test_run_execution.py`.

Why this was recorded
- This is a major item under R-11 because it changes active mechanism availability and narrows the public `test_run` configuration interface.
- The removal follows subtraction-first cleanup after Human read indicated the group likely contributed to degraded formation readability despite some contact-smoothing benefits.

Code and interface touchpoints
- `test_run/test_run_execution.py`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Operational read
- The active `v4a` line keeps the signed hold relation and current near-contact distance semantics.
- It no longer performs the removed near-contact internal-speed unification blend or per-unit speed relaxation path.
