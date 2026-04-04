# LOGH Sandbox

## PR #6 Testonly Path Simplification Design Note
## Remove Redundant `test_only` Wrappers from `test_run_v1_0.testonly.settings.json`

Status: design note only  
Scope: `test_run` configuration interface design  
Authority: local engineering design note, not yet implemented

---

## 1. Purpose

This note records a simplification direction that should be handled as an
explicit config-interface change, not as a silent cleanup.

Current Human read is correct:

- `test_run_v1_0.testonly.settings.json` is already the test-only layer
- therefore repeating `test_only` inside multiple subtrees is redundant
- the extra wrapper adds reading burden without adding real semantic value

However, this cannot be removed casually because it is part of the active
public `test_run` config interface.

---

## 2. Current Redundant Paths

The current redundant wrappers are:

- `runtime.movement.v4a.test_only.*`
- `runtime.movement.v3a.test_only.*`
- `runtime.physical.contact_model.test_only.*`

These wrappers repeat a distinction that the file itself already owns.

The file identity is:

- `test_run_v1_0.testonly.settings.json`

So the extra `test_only` layer is interface weight, not necessary information.

---

## 3. Why This Should Change

Reasons for simplification:

1. The current paths are longer than needed.
2. They increase reader friction when comparing runtime vs test-only ownership.
3. They encourage accidental split thinking:
   - the file says "test-only"
   - the subtree says "test_only" again
4. They increase settings-plumbing burden in:
   - comments
   - reference docs
   - accessors
   - scenario validation
   - execution wiring

This is exactly the kind of interface narrowing that should be preferred once
the change is performed intentionally and recorded clearly.

---

## 4. Why This Must Not Be Done Silently

Even though the simplification direction is good, implementation would change
the active config interface.

Therefore it is a major item because it affects:

- public `test_run` configuration paths
- runtime / harness interpretation boundary

So it must not be done by:

- quiet path swapping
- silent compatibility fallbacks
- "both paths work for now" drift

Any implementation must:

1. record the change independently
2. update comments/reference/accessors/scenario/execution together
3. use explicit failure rather than silent fallback for stale paths

---

## 5. Proposed Simplified Shape

Proposed future shape:

- `runtime.movement.v4a.*`
- `runtime.movement.v3a.*`
- `runtime.physical.contact_model.*`

inside the `test_run_v1_0.testonly.settings.json` file.

This keeps the file as the owner of "test-only" identity, instead of repeating
that identity again inside each branch.

---

## 6. Recommended Migration Discipline

When this is implemented, do it as one bounded interface turn:

1. rewrite the config paths in the test-only file
2. update `settings_accessor.py`
3. update scenario validation and effective-value publication
4. update execution consumption
5. update comments/reference docs
6. update major-change record
7. run explicit override smoke checks on representative active settings

Do **not** keep a long-lived compatibility bridge unless Human explicitly asks
for one.

Current preferred behavior after implementation:

- old paths fail fast
- new paths are the only active interface

That keeps the interface honest and avoids hidden dual ownership.

---

## 7. Relationship to Wiring Gates

This simplification should be implemented together with the stronger
settings-wiring rule:

- path existence is not enough
- override smoke checks must prove the active path actually owns behavior

In other words:

- path simplification
- and settings-wiring integrity

should be treated as one engineering-quality package, even if they are
implemented in separate turns.

---

## 8. Recommended Next Step

This note recommends:

1. accept the simplification direction
2. keep it separate from unrelated mechanism work
3. implement it in one explicit bounded config-interface turn later

It should not be mixed casually into battle-hold, targeting, or viewer work.

