# Step 3 3D PR #6
## Centroid and Alive-Body Observation Gate Note

Status: analysis / review-method note  
Scope: mandatory Human/Engineering observation gate for current PR `#6` lines  
Authority: local engineering note for Human review  
Non-scope: implementation approval, runtime semantics change

---

## Purpose

This note records a now-mandatory review correction:

- **fleet-centroid observation**
- **alive-unit body observation**

must both be treated as hard observation metrics for the current PR `#6` line.

This is not optional polish.
It is a required validation gate.

---

## Why This Note Is Needed

A recent battle-first hold / terminal local candidate looked superficially
plausible if viewed only through:

- target-direction owner transfer
- scalar focus indicators

But Human immediately saw the real failure:

- on first contact, fleets were knocked apart
- unit-level motion became highly unstable
- each side gradually drifted back away instead of holding an honest battle
  geometry

Engineering then checked the centroid trajectories and confirmed:

- the local candidate was wrong
- owner removal had occurred without a replacement battle-owned geometry owner

So the lesson is now explicit:

- if centroid trajectories are not inspected, the line can look locally
  "conceptually correct" while actually failing in an obvious motion read
- if the alive-unit body is not inspected, internal disorder can be missed even
  when outer shell or scalar metrics look cleaner

---

## Hard Observation Metrics

The following two observation surfaces are now mandatory for this line.

### 1. Fleet-centroid observation

Human and Engineering must inspect:

- centroid trajectory of fleet A
- centroid trajectory of fleet B

Questions:

- are fleets still advancing, holding, separating, or drifting?
- does a new seam accidentally remove the current owner without giving geometry
  to a new owner?
- do fleets get knocked apart and then retreat or disperse?
- does the post-contact body still behave like one battle geometry, or does it
  split into disconnected drift?

Minimum read:

- centroid position over time
- centroid speed before and after the event being tested

This is now a required check, not an optional extra.

### 2. Alive-unit body observation

Human and Engineering must inspect the actual body formed by currently alive
units, not only the intended shape state.

Questions:

- does the alive body remain one coherent body?
- are units being squeezed out, dropped out, or shell-only regularized?
- is the interior orderly or chaotic?
- does the visible shape change come from real body transport, or only from a
  late forced shell correction?
- after contact, does the alive body hold a meaningful front / fire plane, or
  does it degrade into rotating clumps?

This must be observed directly in animation / frame-read, not inferred only from
carrier-owned morphology quantities.

---

## Required Use on Current Lines

These hard metrics must now be applied to at least the following active lines:

### A. Battle-first hold / terminal semantics

Before accepting any candidate, check:

- fleet-centroid trajectory
- alive-unit body continuity

If the fleets are being knocked apart, drifting away, or losing one coherent
battle body, the candidate is not accepted, even if a scalar owner-transfer read
looks clean.

### B. Targeting / fire-distribution correction

Before accepting any candidate, check:

- centroid-level battle geometry
- alive-unit body and fire-body distribution

This matters because over-concentrated targeting can still look "active" in
scalar terms while actually collapsing visible fire-plane behavior into one
unstable local knot.

---

## Relationship to Existing Rubric

This note does not replace the existing Human motion-read rubric.

Instead, it strengthens it with two hard requirements:

1. centroid trajectory is mandatory  
2. alive-unit body observation is mandatory

This is particularly important when evaluating:

- battle contact onset
- hold / terminal semantics
- post-contact geometry

because these are exactly the areas where scalar cleanliness can mislead most
easily.

---

## Bottom Line

For the current PR `#6` phase, the following are now hard observation gates:

- fleet-centroid trajectory
- alive-unit body observation

If a candidate fails clearly on either of these, it should not be treated as
plausible, even when local indicators or conceptual ownership language look
clean.
