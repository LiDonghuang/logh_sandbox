# Step3 3D PR6 - Cleanup Methodology Notes - 2026-04-08

## Purpose

Record the practical cleanup lessons learned during the `v4a` incident-recovery and post-recovery cleanup turns, so later mainline cleanup and future mechanism work can reuse the method instead of relearning it through failure.

## Stable lessons

### 1. Static owner audit comes before dynamic testing

For mechanism cleanup and regression isolation:

- first identify the active owner
- then identify any transitional bridge / carrier
- then identify any stale comments or historical surfaces
- only then run dynamic tests to validate narrowed hypotheses

Dynamic testing is a validator, not a substitute for code truth.

### 2. Human-confirmed good/bad windows outrank chronology guesses

Commit timing, local notes, and intuition are not proof of causality.

Highest-trust anchors are:

- Human-confirmed good/bad window
- current active code path
- paired comparison after single-group isolation

### 3. Subtraction-first means deleting the wrong owner, not weakening the right one

When battle looked richer and neutral looked thinner, the correct direction was:

- neutral should adopt battle's movement family
- not battle being cut down to neutral's old path

This was a key correction.

### 4. Shared mechanism family must be explicit

For `v4a` movement:

- battle and neutral must share the same mechanism family
- the only allowed semantic difference is objective source

If a branch keeps its own movement relation semantics, cleanup is not done yet.

### 5. Semantic splits across multiple carriers are high-risk

Examples from this line:

- `restore_strength` plus hidden old personality multipliers
- `stop_radius` plus `hold_stop_radius`

If one semantic is split across multiple carriers, cleanup should first reunify the semantic before tuning behavior.

### 6. Do not spread a dirty mechanism just to get consistency

If battle carries a mechanism and neutral lacks it, first decide whether that battle mechanism is the intended family.

Only after that decision should consistency be achieved.

This prevents “consistency by copying the wrong owner everywhere.”

### 7. Public surface honesty matters

Settings comments, reference docs, and ownership notes must say what is active now.

Do not describe a carrier as:

- dead
- retired
- native
- no longer depended on

unless active code proves it.

### 8. Cleanup should shrink active meaning, not just rewrite prose

A cleanup turn is only real cleanup if one of these becomes smaller:

- active owner count
- public semantic surface
- fallback count
- bridge count
- silent compatibility behavior

Otherwise it is only redescription.

## Current practical rule-of-thumb

When a new mechanism regression appears:

1. identify the Human-confirmed window
2. identify the active owner and any bridge
3. isolate one mechanism group
4. delete or bypass one group at a time
5. only after truth is stable, consider broader structural cleanup
