## PR9 Phase II - Local Desire Experimental Family Testonly Rehome Record

Date: 2026-04-21  
Scope: settings-surface reclassification only  
Status: completed locally

### 1. One-sentence conclusion

The whole current experimental `local_desire` family has been deliberately
rehomed from the maintained runtime settings file into the test-only layer,
while keeping the freeze switch explicit and returning the maintained default to
the safe frozen path.

### 2. Exact scope

This record covers only the settings-surface reclassification for the current
experimental family:

- `runtime.physical.local_desire.experimental_signal_read_realignment_enabled`
- `runtime.physical.local_desire.turn_need_onset`
- `runtime.physical.local_desire.heading_bias_cap`
- `runtime.physical.local_desire.speed_brake_strength`

It does **not** change:

- runtime owner/path
- carrier shape
- target-selection ownership
- `resolve_combat(...)` ownership
- locomotion-family ownership
- any battle formula inside `runtime/engine_skeleton.py`

### 3. Files changed

- [test_run/test_run_v1_0.runtime.settings.json](E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:1)
- [test_run/test_run_v1_0.testonly.settings.json](E:/logh_sandbox/test_run/test_run_v1_0.testonly.settings.json:1)
- [test_run/test_run_scenario.py](E:/logh_sandbox/test_run/test_run_scenario.py:835)
- [test_run/test_run_v1_0.settings.comments.json](E:/logh_sandbox/test_run/test_run_v1_0.settings.comments.json:93)
- [test_run/test_run_v1_0.settings.reference.md](E:/logh_sandbox/test_run/test_run_v1_0.settings.reference.md:1)

### 4. What changed

Surface reclassification:

- removed the whole `local_desire` experimental family from the maintained
  runtime value file
- added the whole family to the test-only value file
- kept the switch explicit and visible
- changed the default switch posture to:
  - `false`

Current maintained read after rehome:

- safe maintained default:
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = false`
- experimental behavior remains available only by explicit test-only enablement
- this is a surface-honesty move for experimentation discipline
- it is **not** a promotion of the experimental family

### 5. What did not change

- nested key names remain:
  - `runtime.physical.local_desire.*`
- code names remain:
  - `local_desire`
- runtime consumption path remains:
  - [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1662)
    `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
- this turn does not rename the code family physically

### 6. Explicit ownership read

Current truthful read is now:

- mechanism shape is still runtime-local
- but configuration ownership for the current experimental family is test-only
- scenario/harness error text now reflects that test-only ownership explicitly

### 7. Validation

Compile check:

```text
python -m py_compile test_run/settings_accessor.py test_run/test_run_scenario.py test_run/test_run_execution.py
```

Result:

- pass

Minimal configuration-path validation:

- default layered load:
  - `local_desire_experimental_signal_read_realignment_enabled = false`
- explicit test-only override:
  - `local_desire_experimental_signal_read_realignment_enabled = true`
- both postures complete a 1-step active-scenario run successfully

### 8. Current judgment

This rehome should be read as:

- a deliberate whole-family surface reclassification
- explicit freeze preserved
- maintained default made safe again

This rehome should **not** be read as:

- maintained acceptance of the experimental battle behavior
- a runtime owner/path redesign
- a code-family rename
