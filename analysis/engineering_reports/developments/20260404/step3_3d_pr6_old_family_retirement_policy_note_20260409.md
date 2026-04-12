# Step3 3D PR6 - Old Family Retirement Policy Note - 2026-04-09

## Purpose

Establish a practical retirement policy for old mechanism families during the ongoing `v4a` cleanup line, so later cleanup work can proceed with a stable deletion-first standard instead of re-deciding retention rules every round.

This note is an operating guideline for cleanup execution.
It is not a merge approval, default-switch approval, or full retirement plan.

## Current read

- `v4a` is now the active movement line under cleanup.
- The current cleanup goal is not to preserve mixed-era coexistence indefinitely.
- Old `2D / v3a / v3_test / fixture-era` mechanism families should not remain as silent fallback or historical baggage on the active path.
- Human already keeps a full `dev2.0` / PR `#6` core-script backup in local `retired/`; this can remain untouched as a historical anchor.

## Retirement policy

### 1. Default direction: delete, do not preserve by inertia

For old-family cleanup, the default action is:

- delete inactive legacy surfaces
- delete silent compatibility branches
- delete stale selector paths
- delete historical wrappers that no longer own active semantics

Retention requires a positive reason.
Historical existence alone is not a reason to keep code alive.

### 2. Keep only what is still required by the active line

An old-family function, branch, or parameter path may remain temporarily only if it is one of:

- an active bridge that the current `v4a` line still truly depends on
- a short-lived migration seam whose removal would break the current active owner before re-rooting is complete
- a bounded regression-support helper still needed to verify active cleanup work

Anything else should be treated as retirement candidate by default.

### 3. `retired/` is a small historical shelf, not a second active code tree

`retired/` may hold:

- historically valuable full-script anchors
- specific old implementations the Human still expects to inspect directly
- a very small number of high-value reference scripts

`retired/` must not become:

- a shadow runtime
- a fallback source for active imports
- a compatibility layer
- a place to dump large amounts of unresolved active logic

If a script is kept in `retired/`, it is for historical reading, not active execution.

### 4. Remote / frozen branches remain the primary archive

The default long-term preservation mechanism is:

- remote history
- frozen branches
- tagged or otherwise stable historical branch anchors

So for most retired mechanisms:

- prefer deletion from active tree
- rely on remote / frozen history for recovery

Only promote code into local `retired/` when Human specifically wants it preserved as an easy local reading anchor.

### 5. Retirement must happen by mechanism group, not by vague age

Do not retire code because it is merely "old."

Retire one mechanism group at a time:

- identify the active owner
- identify any transitional bridge
- identify stale but still-present historical surfaces
- delete the old-family group only after the active owner is clear

Chronology alone is not retirement justification.

### 6. Do not spread old logic just to achieve consistency

If a legacy mechanism still exists on one branch of behavior:

- do not copy it to another branch for symmetry
- first decide whether that mechanism is still intended

Consistency must be achieved by deleting the wrong owner, not by proliferating it.

### 7. Truth surface must shrink with retirement

When a family is retired, cleanup must also shrink the human-facing truth surface:

- settings comments
- settings reference
- ownership map
- local engineering records where needed

Do not leave:

- stale mode names
- stale parameter descriptions
- stale claims that a mechanism is still active

### 8. Retirement order should follow active-risk priority

Preferred order:

1. stale public surface and stale ownership truth
2. transitional bridges already known to be temporary
3. active mixed-era fallback branches
4. cold helper/support paths
5. large historical script bodies, only after active dependence is truly gone

This keeps high-risk active confusion ahead of cosmetic cleanup.

## Practical execution standard

For each retirement slice:

1. identify the active owner
2. identify any bridge that still keeps the old family alive
3. decide:
   - delete now
   - keep temporarily as bridge
   - preserve in `retired/`
   - rely on remote / frozen branch only
4. make one bounded cleanup cut
5. update truth surface
6. record the retirement in an independent note if it materially changes active mechanism availability

## Immediate implication for the current mainline

The current cleanup line should continue to treat:

- old `v3a / v3_test / 2D / fixture-era` active-path residues

as retirement candidates by default.

Large-scale preservation is not the goal.

The Human-kept `retired/` backup of the old `dev2.0` / PR `#6` core scripts is sufficient historical protection for now, and does not need to be reworked during the current cleanup turns.
