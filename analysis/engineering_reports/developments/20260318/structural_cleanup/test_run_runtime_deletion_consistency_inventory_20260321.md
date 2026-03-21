# Test Run / Runtime Deletion Consistency Inventory 20260321

Status: cleanup inventory  
Scope: maintained test_run surface vs retired runtime surface  
Purpose: list remaining remap / compatibility residues that should be handled with the same deletion-first rule

## Current Mismatch Inventory

### 1. `movement_model=v1` is retired in runtime, but `test_run_scenario.py` still accepts and remaps it

- File: `test_run/test_run_scenario.py`
- Current behavior:
  - accepts `baseline | v1 | v3a`
  - prints a remap message for `v1`
  - resolves effective model to `v3a`
- Why it is now inconsistent:
  - `runtime/engine_skeleton.py` no longer maintains `MOVEMENT_MODEL == "v1"`
  - runtime now fails fast for non-`v3a`

### 2. settings comments still advertise `v1` as a selectable runtime movement model

- File: `test_run/test_run_v1_0.settings.comments.json`
- Current text still says:
  - `baseline | v3a | v1`
  - `legacy v1 is remapped out of standard test runs`
- Why it is now inconsistent:
  - runtime no longer treats `v1` as a maintained selectable family

### 3. execution still generically forwards `MOVEMENT_MODEL` from prepared runtime config

- File: `test_run/test_run_execution.py`
- Current behavior:
  - still sets `("MOVEMENT_MODEL", str(runtime_cfg["movement_model"]).strip().lower() or "v3a")`
- Why it matters:
  - harmless under current scenario remap
  - but it preserves a wider-than-needed engine input surface

## Not Yet Classified for Deletion

### 4. `diag4` main family

- Still active maintained diagnostic surface
- Not a deletion candidate by default

### 5. `movement_model=baseline`

- Still a maintained selector alias at test_run scenario/settings level
- Not equivalent to retired `v1`

## Recommended Next Deletion-Consistency Order

1. Remove `v1` from `test_run/test_run_scenario.py` accepted selector surface
2. Remove `v1` from `test_run/test_run_v1_0.settings.comments.json`
3. Re-check whether `test_run/test_run_execution.py` can narrow its `MOVEMENT_MODEL` forwarding to maintained `v3a` only
