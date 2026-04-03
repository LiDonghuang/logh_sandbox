# Step 3 3D Visual Direction Mode Rethink
## Governance Proposal Note

Status: proposal / discussion note only  
Scope: 3D viewer visual direction modes only  
Authority: Engineering proposal for Human + Governance discussion  
Non-scope: runtime mechanism change, movement-core change, combat semantics change, default switch

---

## I. Purpose

This note proposes a rethink of the 3D viewer direction-mode line.

It is intentionally limited to:

- viewer-side direction display semantics
- mode naming
- mode split
- future visual-only direction synthesis

It does **not** propose:

- any runtime ownership change
- any change to combat or movement mechanism semantics
- any claim that visual direction modes should influence simulation behavior

The goal is to improve the honesty of the visual read:

- what does a fleet/unit currently look like it is doing?

That question has become more important during the recent formation-transition work,
because visual motion-read is now repeatedly the highest-control review surface.

---

## II. Current Problem Read

The current 3D viewer inherited or extended several older direction-display ideas:

- `effective`
- `free`
- `attack` / `fire`
- `composite`
- and later `realistic`

These modes are all useful as bounded visual probes.

But they still share a structural limitation:

- they all try to summarize too much state into one arrow/direction read

That becomes increasingly misleading once we remember that a real warship can:

- move in one direction
- continue rotating its body/posture in another direction
- and fire toward yet another direction

So the problem is not only:

- "current realistic is not good enough"

The deeper problem is:

- the current direction-mode line still over-compresses several distinct semantics into one displayed arrow

---

## III. What Current `realistic` Actually Does

The current 3D `realistic` mode lives in:

- `viz3d_panda/replay_source.py`

Its present logic is not a true warship-posture model.

It is better described as:

- a short-window travel-posture read
- or a smoothed movement-direction read

More concretely, current `realistic`:

1. inspects position change across several nearby frames
2. prefers a longer displacement window when available
3. falls back to shorter displacement windows when needed
4. reuses the last valid displayed direction when displacement is too small
5. finally falls back to `effective` or unit orientation

So current `realistic` is fundamentally:

- displacement-history driven

It does **not** honestly own:

- fire direction as a bounded influence
- posture-vs-travel separation
- turn-rate-like display memory
- side-slip / reverse-fire / backing-under-fire reads

This is why the current name now looks too ambitious.

---

## IV. Why the Current Name Is Misleading

Calling the current mode `realistic` now creates two problems:

### 1. It overclaims what the mode is doing

The mode is not yet a credible general read of:

- ship posture
- maneuvering body orientation
- or combat-aware travel posture

It is a useful smoothed movement read, but not a mature realism mode.

### 2. It blocks a better future name

The name `realistic` is actually better reserved for a future viewer-side mode that tries to show:

- how the ship body currently looks like it is maneuvering

That future mode should probably use:

- recent travel history
- turn continuity
- engaged state
- attack direction
- and bounded posture memory

So the name should be freed for that later mode.

---

## V. Proposed Renaming and Mode Split

Current Engineering proposal:

### A. Rename current `realistic` to `movement`

Reason:

- this is what it really is
- a smoothed travel-direction display

Its viewer-side question becomes:

- "where does this unit currently look like it is moving?"

This is honest, useful, and still worth keeping.

### B. Keep at least one additional distinct mode

Human explicitly wants at least two meaningful visual modes in 3D.

Engineering agrees.

The proposal is:

- keep `movement`
- add a new future `realistic`

Optional older modes may still remain for debugging or transitional comparison:

- `effective`
- `fire`
- maybe `composite`

But the long-term main pair would be:

1. `movement`
2. `realistic`

---

## VI. What the New `movement` Mode Should Mean

The renamed `movement` mode should answer only one question:

- "what direction does this unit currently look like it is traveling?"

This is strictly a viewer-side kinematic read.

It should continue to be based mainly on:

- short-window displacement
- multi-frame smoothing
- last valid movement read when the current displacement is too small

It may be improved incrementally,
but it should not pretend to represent:

- fire posture
- combat-facing orientation
- or a complete ship-body semantics

This honesty alone is already an improvement.

---

## VII. What the New `realistic` Mode Should Try to Mean

The future `realistic` mode should answer a different question:

- "what maneuvering posture does this unit currently look like it has?"

This is not identical to pure travel direction.

The current proposal is that this mode should synthesize a viewer-side posture read from several bounded inputs:

1. current and recent movement direction
2. previous displayed posture direction
3. attack direction
4. engaged state
5. bounded turning memory / turn-rate-like display smoothing

This is still visual-only.
It is not a runtime ship-dynamics model.

But it is closer to what a human would perceive as:

- the visible direction of maneuver

especially in situations like:

- moving while turning
- drifting laterally under fire
- backing / sliding while firing off-angle
- attack direction disagreeing with current travel direction

---

## VIII. First Bounded Read for the Future `realistic` Mode

Engineering's current first bounded read is:

### Step 1. Build a `movement_dir_target`

Use:

- current displacement
- short-window displacement
- medium-window displacement

This is similar to current `realistic`,
but should be explicitly re-read as travel direction only.

### Step 2. Build a `posture_dir_target`

Blend between:

- movement direction
- attack direction

using only bounded viewer-side influences such as:

- engaged state
- local attack angle
- recent turning trend

Attack direction should act as:

- a posture bias

not as direct ownership of the displayed arrow.

### Step 3. Apply display-side turn continuity

The final displayed posture should be obtained through a bounded rotate-toward process from:

- previous displayed posture
to
- current posture target

This prevents:

- one-frame flips
- overreaction to tiny displacement noise
- and visually implausible high-frequency pivots

This is the current best bounded concept for a new `realistic` mode.

---

## IX. Why This Matters for Current Formation Work

This proposal is not random viewer polish.

It matters directly to the current formation-transition line because:

- Human motion read is repeatedly the main control surface
- current viewer direction modes can exaggerate or distort perceived motion quality
- some of the "violent swing / jitter / sudden turn" read may be a mixed result of:
  - actual runtime behavior
  - plus an overcompressed visual direction read

This does **not** mean:

- visual cleanup can replace runtime cleanup

It means:

- the viewer should stop making the motion-read problem noisier than necessary

That is a legitimate and useful support line.

---

## X. Boundaries

The following boundaries are explicit:

### 1. Viewer only

No dir-mode change should participate in:

- runtime target choice
- movement force composition
- combat resolution
- formation-transition ownership

### 2. No silent semantics drift

If the name `realistic` is changed or reused,
the change must be explicitly recorded because it changes human interpretation.

### 3. Keep at least two useful modes

The current goal is not to collapse everything into one "best" mode.

The goal is to keep at least two honest modes with different meanings:

- movement
- realistic

### 4. Do not let debug-only modes become the main visual language by accident

Modes like:

- `effective`
- `fire`
- `composite`
- `radial_debug`

may still be valuable,
but their role should be understood explicitly.

---

## XI. What Governance Is Being Asked to Judge

Governance is **not** being asked for implementation approval yet.

Governance is being asked to judge these questions:

1. Is the current rename correct?
   - should old `realistic` become `movement`?

2. Is the new two-mode split honest?
   - `movement` as travel-direction read
   - `realistic` as maneuver-posture read

3. Is the proposed future `realistic` synthesis conceptually sound?
   - movement history
   - posture memory
   - attack-direction bias
   - bounded turn continuity

4. Should `composite` remain as a third debug/transitional mode,
   or should it later be retired once the split is cleaner?

5. What literature or doctrine families might help here?
   - ship maneuver visualization
   - naval tactical diagrams
   - motion/posture display in simulation
   - perception-oriented trajectory visualization

Governance is encouraged to:

- push back
- propose better terminology
- and reject any part that still sounds too hand-wavy

---

## XII. Bottom Line

Current Engineering read:

- current 3D `realistic` is useful, but misnamed
- it should be re-read as `movement`
- a future new `realistic` should be reserved for a more honest maneuver-posture display mode

The long-term pair should likely become:

- `movement`
- `realistic`

with all semantics remaining strictly viewer-side.

This is the proposal now being prepared for Governance review before any implementation decision.
