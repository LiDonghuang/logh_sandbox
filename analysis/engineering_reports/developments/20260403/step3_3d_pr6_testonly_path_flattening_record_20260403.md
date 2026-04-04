# LOGH Sandbox

## PR #6 Testonly Path Flattening Record
## Remove Redundant `test_only` Subtree Wrappers

Status: implementation record  
Scope: `test_run` public test-only configuration interface  
Authority: harness / test-only configuration only

---

## What changed

This turn flattens the active test-only config interface by removing redundant
`test_only` wrappers from the dedicated test-only layer file:

- `runtime.movement.v4a.test_only.*` -> `runtime.movement.v4a.*`
- `runtime.movement.v3a.test_only.*` -> `runtime.movement.v3a.*`
- `runtime.physical.contact_model.test_only.hostile_contact_impedance.*`
  -> `runtime.physical.contact_model.hostile_contact_impedance.*`

The file itself already owns the test-only identity:

- `test_run/test_run_v1_0.testonly.settings.json`

So the extra subtree wrappers were interface weight rather than useful meaning.

---

## Why it changed

Human correctly identified that repeating `test_only` inside the test-only file:

- adds reading burden
- lengthens active settings paths
- increases accessor / docs / validation plumbing
- provides little semantic value

This turn implements the previously approved simplification direction explicitly.

---

## Files updated

- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

---

## Boundary

This is a public `test_run` config-interface change.

It does **not**:

- change frozen runtime semantics
- change canonical doctrine
- change baseline/runtime config ownership

It only changes the test-only harness-facing config path surface.

---

## Compatibility read

This turn does **not** keep a dual-path compatibility bridge.

Old wrapped paths are not retained silently.

Reason:

- explicit failure is preferred over hidden fallback
- the simplification should actually reduce interface width

---

## Validation expectation

Because this is a public test-only settings-path change, it should be checked by:

1. layered settings load
2. scenario preparation
3. at least one override smoke check on an active setting

This aligns with the stronger settings-wiring gate now recorded separately in:

- `docs/engineering/Runtime_Settings_Wiring_Gates_v1.0.md`

