# LOGH Sandbox

## PR #6 Fire Plane vs Formation Design Note
## Battle Engagement Geometry Clarification

Status: design note only  
Scope: PR `#6` battle-geometry clarification before implementation  
Authority: engineering design note for Human + Governance review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note narrows the next battle problem on PR `#6`.

After the recent battle-first hold work, the current read is no longer:

- "the main problem is still `d*` hold tuning"

The sharper read is:

- `d*` and reversible hold are now directionally correct and broadly usable
- but the branch is still missing an honest relation between:
  - **effective fire plane**
  - and **formation front ownership**

This note exists to define that problem cleanly before any implementation is attempted.

---

## II. Current Accepted Read

### 1. The reversible battle hold seam is now "good enough" as a bounded line

Recent Human review indicates:

- the old first-contact discontinuity improved materially
- battle no longer exhibits the same obviously dishonest hard break on contact
- hold-weight tuning now feels hard mostly because larger battle geometry problems dominate the read

So the current hold seam should be read as:

- bounded
- directionally correct
- not the current main blocker

### 2. The next main blocker is not "contact" as a one-time event

The earlier wording "post-contact problem" can be misleading.

The better read is:

- `first-contact` or `initial-contact` is an event
- but battle geometry after that is a **continuing state**
- formation/front ownership must evolve continuously within that state

So the problem is not:

- "what happens after a one-time contact event"

It is:

- "how battle geometry is owned once sustained engagement begins and then changes"

### 3. Current visible failure mode

Human repeatedly observed variants of:

- localized wing-only contact
- two arc-shaped bodies rotating back-to-back
- later collapse into rotating clusters

This should now be read as:

- **fire-plane vs formation-front misownership**

not mainly as:

- bad `d*` tuning
- or a simple targeting bug

---

## III. Problem Statement

Current battle behavior suggests the following:

1. An **effective fire plane** emerges naturally once engagement begins.
2. The formation still behaves as if its primary front remains the old pre-contact front.
3. The system therefore keeps preserving the wrong front too faithfully.
4. Because no honest front redefinition occurs, contact localizes around one junction.
5. The battle then degrades into long-lived rotation around that junction.

So the missing mechanism is not just "move less" or "hold more."

The missing mechanism is:

- a battle-owned way for formation front responsibility to shift toward the
  currently effective fire plane

---

## IV. Layered Read

This note continues the earlier Layer A / B / C organization.

### Layer A. Far-field pre-engagement movement

Owns:

- global enemy relation
- `d*`
- approach / hold before engagement geometry matters

Does not own:

- local front redefinition
- battle fire-plane ownership

### Layer B. Engagement geometry layer

This is the layer that must now be clarified.

It should own:

- locally relevant enemy geometry
- effective fire plane
- front reorientation signal
- later, bounded local range-entry reference

This layer is not simply "who attacks whom."

It is the battle-geometry layer that tells the fleet:

- what battle-facing direction currently matters
- how the fleet front should gradually respond

### Layer C. Movement realization

Owns:

- turning
- slowing
- pressure / hold realization
- consumption of Layer B signals

Does not own:

- independent local enemy invention
- unrestricted nearest-enemy pursuit

---

## V. Fire Plane vs Formation Read

### A. What "effective fire plane" means here

For current discussion, "effective fire plane" does **not** need a final mathematical definition yet.

It only needs an honest semantic meaning:

- the currently active engagement-facing geometry that best explains where the fleet's real fire exchange is happening

This is not identical to:

- enemy centroid relation
- pre-contact front
- any one unit's local target direction

It is an aggregate battle geometry read.

### B. What is failing now

The current branch still lets the formation preserve a front that is too loyal to:

- pre-contact morphology
- or pre-engagement approach geometry

while the effective fire exchange has already shifted.

That mismatch produces:

- partial-wing contact
- skewed local coupling
- rotating engagement bodies

### C. Better read

The formation front should gradually become responsible for:

- `formation × effective fire plane`

not only:

- `formation × pre-contact approach front`

This is the central doctrine correction.

---

## VI. Front Reorientation as Doctrine

This line should be read as a long-term battle doctrine, not as a local patch.

### A. What it should be

Front reorientation should be:

- fleet-level
- continuous
- low-jump
- bounded
- persistence-aware

### B. What it should not be

It should not be:

- a high-frequency every-tick pivot
- a direct nearest-enemy chase
- a hidden local swarm release
- a new exact-template front lock

### C. Why it matters

Without front reorientation, battle geometry has no honest way to absorb:

- drift of the active fire plane
- asymmetry of actual contact
- changing engagement center

So the fleet either:

- preserves the wrong front
or
- falls apart into unstructured local correction

Neither is acceptable.

---

## VII. Minimum Candidate for Layer B

The smallest next conceptual candidate should not yet try to solve everything.

It only needs to introduce enough Layer B meaning to support later implementation.

### Suggested minimum signals

1. `effective_fire_axis`
- a fleet-level aggregate read of current engagement-facing direction

2. `front_reorientation_weight`
- a bounded scalar telling how much formation front responsibility should shift
  away from the old pre-contact front and toward the effective fire axis

3. `engagement_geometry_active`
- a bounded activation read saying battle geometry is now the owning surface,
  rather than pure far-field approach geometry

This is enough to define the next implementation question without already
inventing a full local correction doctrine.

---

## VIII. What Should Wait

The following should remain later than the first fire-plane/front clarification:

### 1. Bounded local range-entry correction

This is still valid as a future direction, but it should come **after** front
reorientation is defined.

Otherwise movement will again absorb local geometry in an unstructured way.

### 2. Targeting / fire-distribution correction

This is also real and important, especially at `attack_range = 10`.

But it should remain a separate line:

- `hp_term + crowd_term + angle_term`

or similar

because it addresses:

- who gets targeted
- and how fire is distributed

not the more basic question of:

- what battle-facing front the formation currently owns

### 3. Richer battle behaviors

Ideas such as:

- temporary withdrawal
- regrouping
- renewed pressure

may matter later, but they are not needed to define the current problem.

---

## IX. Validation Read

Any future candidate on this line should be judged first by the now-fixed
runtime dynamics gates:

- fleet-centroid trajectory
- alive-unit body observation

And then by Human motion read of:

- `1 -> 4`
- `2 -> 4`
- `4 -> 1`

especially battle cases where the front/fire-plane mismatch is visible.

The key question is not:

- "did the fleet look busier?"

It is:

- "did the fleet keep a more honest battle body relative to the active fire plane?"

---

## X. Touchpoint Judgment

This note's main job is conceptual clarification.

Current judgment:

- the first clarification and maybe even the first bounded probe may still be
  expressible inside `test_run/`
- but true ownership of engagement geometry may eventually strain the
  `test_run-only` boundary

Reason:

- Layer B engagement geometry starts to overlap with live combat ownership,
  not only harness-side target shaping

So this line should remain explicitly watched for deeper touchpoint pressure.

---

## XI. Bottom Line

Current hold tuning is no longer the main battle problem.

The sharper current read is:

- the branch still lacks an honest relation between effective fire plane and
  formation front ownership

Therefore the next major battle-geometry line should be read as:

- **fire plane vs formation**

with the first doctrine-level task being:

- define bounded, fleet-level front reorientation toward the effective fire
  plane

before introducing:

- bounded local range-entry correction
- or targeting/fire-distribution correction

