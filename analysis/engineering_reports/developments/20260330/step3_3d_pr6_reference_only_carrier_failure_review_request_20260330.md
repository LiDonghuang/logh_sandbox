# Step 3 3D PR #6 Reference-Only Carrier Failure Review Request

Status: Governance review request  
Scope: PR `#6` formation-substrate main line  
Layer read: branch review / carrier reassessment only  
Authority requested: discussion and carrier-redesign review only, not merge approval, not default switch approval

---

## I. Purpose

This note requests Governance review after a new local engineering attempt exposed a more basic failure in the current PR `#6` carrier direction.

The current note is **not** a request to merge PR `#6`.

It is also **not** a request to roll back:

- expected/reference spacing
- physical minimum spacing split
- restore-line legitimacy
- band legitimacy

Instead, it requests Governance review of a narrower but more serious conclusion:

> the current PR `#6` carrier still reads too much like a **reference-only formation generator**, while the actual problem already requires a coupled read across:
> - formation target
> - continuous transport / topology
> - movement realization

In other words:

- the current carrier line is no longer failing only because of `restore_strength`
- and no longer only because of rigid slot persistence
- it is now failing because the method is still too close to
  **"define a clean reference surface, then let runtime follow it"**
  for a problem that is structurally harder than that

---

## II. Human Observations That Trigger This Review

Human reran four neutral-transit checks using the current branch logic, comparing initial aspect vs reference aspect:

### 1. Initial `1.0` -> reference `1.0`

Observed read:

- formation remains stable
- but almost fully rigid / plate-like
- only a few units move slowly while most units look nearly fixed
- after arrival, a few units reverse direction

### 2. Initial `4.0` -> reference `4.0`

Observed read:

- same overall rigid stability
- again only a few units move while most remain nearly fixed
- after arrival, more units than in `1.0 -> 1.0` show reverse direction and offset

### 3. Initial `1.0` -> reference `4.0`

Observed read:

- formation does **not** shorten in the intended forward-axis sense
- instead it breaks laterally
- odd/even or row-like splitting remains visible
- near arrival it collapses into an outer shell roughly resembling `4.0`
- but internal structure is disordered

### 4. Initial `4.0` -> reference `1.0`

Observed read:

- formation does **not** lengthen/reshape in the intended forward-axis sense
- left / center / right compress independently
- wings compress the center
- near arrival it expands/collapses toward an outer shell roughly resembling `1.0`
- but internal structure is again disordered

These four observations should be read as the core evidence of failure.

The main requirement for "formation" is not only:

- holding a target shape when initial and reference already match

The main requirement is:

- **forming the target shape continuously from a different initial shape**

That is exactly where the current carrier is failing.

---

## III. Current Engineering Reassessment

Current engineering reassessment is now:

### 1. The previous `initial -> reference` implementation path was methodologically wrong

The recent branch work tried to improve the carrier by:

- separating initial aspect from reference aspect
- adding hold-await semantics
- softening band actuation

Those steps were reasonable as local corrections.

However, the deeper carrier still remained too close to:

- "compute a better expected/reference surface"
- "let units be restored toward it"

That is insufficient.

### 2. `1.0 -> 4.0` and `4.0 -> 1.0` reveal the real requirement

These cases expose what the project actually means by formation:

- not static template holding
- not only shape preservation
- but **continuous formation change**

The current branch still does not truly own that problem.

### 3. The failure is multi-layer, not single-parameter

The system now clearly spans at least three coupled layers:

#### A. Formation target

What morphology the fleet is trying to become:

- `1.0`
- `4.0`
- later banded and true 3D targets

#### B. Continuous transport / topology

How real units migrate from current structure toward target structure:

- broad topology preservation
- reassignment / transport continuity
- local ordering
- non-chaotic internal reorganization

#### C. Movement realization

How units physically realize that change:

- turning
- slowing / stopping
- approach to hold-await
- final-state stabilization

The current carrier still overweights A and under-owns B and C.

---

## IV. Why This Matters

The latest local iterations produced two false-positive tendencies:

### False positive 1. Metrics and logical cleanliness looked cleaner than the motion really was

Several local iterations improved:

- RMS error
- front extent behavior
- hold semantics
- apparent reference coherence

But Human observation still showed:

- rigid plate behavior
- sparse stray movers
- wrong mismatch evolution
- late-stage collapse into disordered shells

So the branch has now shown a real engineering warning:

> data/logic cleanliness is not enough if the motion and topology read is still wrong.

### False positive 2. AI optimization drifted toward surface coherence rather than real formation behavior

This should be said plainly.

The recent engineering work exposed a limitation in the current AI-assisted workflow:

- the AI repeatedly found locally coherent reference-surface interpretations
- and repeatedly produced superficially cleaner internal logic
- but failed to treat turning, slowing, transport continuity, and target-formation transition as inseparable parts of the same carrier

Human direct observation caught this failure.

Current honest read:

> this system problem is already too coupled to be solved by "reference logic first, motion later" without producing misleadingly clean but behaviorally wrong intermediate carriers.

This is not a reason to stop AI assistance.

But it **is** a reason to narrow the next carrier definition more honestly and rely on Human observation as a hard control surface.

---

## V. What Should Not Be Misread

This failure should **not** be read as:

- expected/reference spacing was a bad concept
- physical minimum spacing split was a bad concept
- bands were a bad concept
- hold-await semantics were a bad concept

Those lines still appear structurally meaningful.

What failed is the current assumption that:

- a sufficiently good reference generator
- plus restore

would already form a credible first carrier for formation transition.

That assumption should now be considered invalid.

---

## VI. Requested Governance Review Question

Engineering requests Governance review of the following sharper question:

> If PR `#6` is to continue honestly, should the next carrier be redefined away from a reference-surface-first method and toward a smaller but more correct coupled carrier that explicitly owns:
> - target morphology
> - transport / topology continuity
> - movement realization seams
> before any merge-read discussion continues?

This is the main review request.

---

## VII. Current Recommended Direction

Current engineering recommendation is:

### 1. Do not continue simple local tuning on the current reference-first carrier

Not recommended as the main next move:

- more restore-strength tuning
- more band-envelope tuning
- more small hold-trigger tuning
- more local reference-surface cleanup without recarriering the problem

### 2. Re-open the carrier definition itself

The next carrier should likely be defined as the smallest coupled formation carrier that owns all three:

#### A. Target morphology

What shape the fleet should become.

#### B. Transport continuity

How units move from current structure to target structure without chaotic reassignment artifacts.

#### C. Movement realization seam

How turning, slowing, and terminal hold are represented so the transition can actually read correctly.

### 3. Keep Human observation as a hard gate

Future evidence must continue to prioritize:

- direct animation / frame reads
- not just scalar cleanliness
- not just apparent logical neatness

---

## VIII. What Is Not Requested Yet

This note does **not** request:

- merge approval for PR `#6`
- default switch to `v4a`
- rollback of band legitimacy
- hostile-contact redesign as the new main line
- turning-cost implementation approval yet
- runtime-core rewrite
- full 3D ownership claim

---

## IX. Bottom Line

Current branch learning should now be read as follows:

- PR `#6` succeeded in proving that spacing split and restore/reference semantics are real and important
- but the current carrier has now also proved a limit:
  - **formation cannot honestly be solved here as a reference-only generator problem**
- the decisive requirement is not only holding a target shape
- it is continuously forming that shape from another one
- that requirement already couples:
  - target
  - transport/topology
  - movement realization

Engineering therefore requests Governance review of a carrier redefinition on PR `#6` under this more honest read.
