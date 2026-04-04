# Step 3 3D Visual Direction Mode Round 1
## Local Implementation Note

Status: local implementation note only  
Scope: 3D viewer direction-display semantics only  
Authority: local Engineering note for Human review  
Non-scope: runtime mechanism change, combat semantics change, default switch

---

## Purpose

This note records the first bounded implementation step after the Governance
discussion on 3D viewer direction modes.

The goal of this round is narrow:

- rename the old 3D `realistic` mode to `movement`
- introduce a first bounded `posture` mode
- keep `composite` available as a comparison/debug mode

Everything in this round remains strictly viewer-side.

---

## What Changed

### 1. Old `realistic` was removed

The old name is no longer kept as a compatibility alias.

Reason:

- it overclaimed what the mode was doing
- it is better to force an honest rename than to preserve a misleading label

### 2. Old `realistic` became `movement`

`movement` is now the explicit name for the previous short-window,
multi-frame displacement-based direction read.

Its intended question is:

- "where does this unit currently look like it is traveling?"

### 3. New `posture` was added

`posture` is the first bounded viewer-only maneuver-posture mode.

It is intentionally not a runtime ship-dynamics model.

It currently combines:

- movement history
- previous displayed posture
- engaged / attack-direction presence
- bounded broadside bias under engagement
- bounded turn continuity

---

## Current Read of `posture`

The first bounded `posture` read is:

1. build a movement target from the same smoothed travel-direction logic
2. preserve some posture memory from the previously displayed posture
3. when engaged, bias toward the broadside-compatible orientation that best
   matches current movement/posture preference
4. apply a bounded per-frame turn limit to the displayed posture

This keeps attack direction as a bounded influence only.

Attack direction does **not** own the arrow.

---

## Why `posture` Is Not `composite`

`composite` is still the simple angle-bisector style debug read between
effective movement and fire direction.

`posture` differs because it:

- uses display memory
- uses bounded turn continuity
- biases toward broadside-compatible maneuver posture rather than directly
  averaging movement and attack direction
- is intended to answer a different question:
  - not "what is the average of movement and fire?"
  - but "what visible ship-body maneuver posture seems plausible here?"

---

## Boundaries

This round does **not** claim:

- that `posture` is already finished
- that it is already the default review mode
- that it should replace `movement`
- that it should influence runtime behavior

Current intended usage remains:

- `movement` as the main motion-read mode
- `posture` as a bounded experimental viewer mode
- `composite` retained for comparison

