# Step 3 3D PR #6
## Battle-First Hold / Terminal Round 1 Local Implementation Note

Status: local implementation note only  
Scope: bounded harness-side candidate on PR `#6`  
Authority: Engineering local note for Human review  
Non-scope: push report, merge claim, runtime-core rewrite

---

## Purpose

This note records the first bounded implementation candidate after the
`battle-first hold / terminal semantics` design note was approved for a small
local trial.

Human-approved scope for this local candidate was:

- keep the change small
- do not restore any hard terminal regularization
- preserve objective-reached reporting
- implement only the smallest "stop chasing the obsolete far-field driver"
  read

---

## What Changed

File touched:

- `test_run/test_run_execution.py`

No runtime-core file was touched.

### 1. New internal carrier field

The active `v4a` reference bundle now carries one new internal field:

- `far_field_owner_active`

Initial value:

- `True`

This is an internal harness-side ownership flag only.

It does **not** create a new public settings surface.

### 2. Neutral read

For `neutral_transit_v1`:

- once the fleet truly enters `stop_radius`
- the old far-field objective owner is latched off
- subsequent target evaluation returns zero target direction / zero intensity

This means:

- objective reached is still recordable
- but the old objective no longer reclaims ownership after that

### 3. Battle read

For the active `v4a` battle line:

- once a fleet has any alive engaged unit with a valid engaged target
- the old far-field owner is latched off for that fleet
- subsequent Layer-A target evaluation returns zero target direction / zero intensity

Current first read:

- real contact means far-field pursuit is no longer the active owner

This is intentionally simple and probably not the final battle doctrine.

---

## What Did Not Change

This candidate does **not**:

- restore terminal/hold geometry latching
- freeze exact positions
- define post-contact front reorientation
- define bounded local range-entry correction
- alter frozen runtime combat semantics

---

## Current Engineering Read

This round is only a first owner-transfer cut.

It should be read as:

- keep the event
- remove the old far-field owner
- do not yet invent the next owned settle geometry

So the branch still does **not** claim:

- solved hold semantics
- solved terminal semantics
- solved battle settle behavior

It only claims:

- the obsolete far-field owner now has a first bounded exit path

---

## Expected Review Question

Human review should now focus on:

- whether this simpler owner-transfer cut is already more honest than the old
  "keep chasing until a discrete regularized end-state" behavior

before any larger hold / terminal semantics are implemented.
