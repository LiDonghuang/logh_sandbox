# Step 3 3D PR #6 Design Note
## Battle-First Hold / Terminal Semantics

Status: design / governance-alignment note only  
Scope: PR `#6` next hold / terminal read before implementation  
Authority: engineering design note for Human + Governance review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note defines the next hold / terminal discussion on PR `#6` after the latest
Human + Governance direction.

The key correction is now explicit:

- do **not** establish separate `neutral` and `battle` hold / terminal semantics
- `battle` remains the authority surface
- `neutral` remains only a validation instrument

So the question is no longer:

- "how should neutral arrival look?"

The correct question is:

- "what does a more honest **battle-first** hold / terminal state mean?"
- "how should `neutral` behave under that same read?"

This note is design-only.
It proposes no code changes.

---

## II. Current Accepted Read

The following are treated as accepted background.

### 1. Old hard terminal regularization was dishonest

The previous harness-side morphology-level terminal/hold latch was rejected by
Human because it read as:

- too hard
- too discrete
- too visibly forced

Disabling it was the correct move.

### 2. Neutral cleanliness is not the authority target

After disabling the hard latch:

- `neutral` no longer showed the same forced terminal snap
- but battle remained chaotic at contact

This does **not** mean:

- neutral has now found the correct semantics

It means:

- neutral only showed that the old hard snap was dishonest
- battle still owns the actual semantics problem

### 3. Current branch context

PR `#6` should still be read as:

- a bounded review / learning line
- not merge-ready
- not a solved formation-transition line

The next hold / terminal step must remain:

- small
- explicit
- honest about which layer actually owns the meaning

---

## III. First Clarification: Several Different Things Were Being Collapsed

The previous terminal discussion repeatedly collapsed several different ideas into
one word.

They must now be separated.

### A. `objective reached`

This is an event.

Meaning:

- a bounded positional condition has been satisfied
- for example: distance to objective has entered a stop-radius criterion

This says nothing yet about:

- whether the formation should freeze
- whether battle geometry is settled
- whether motion should become clean

### B. `stop chasing`

This is a behavioral cut.

Meaning:

- the fleet should stop treating the old far-field objective relation as an
  active pursuit source

This is not the same thing as:

- stopping all motion
- freezing shape
- or becoming visually neat

### C. `contact / engagement hold`

This is a battle-owned state.

Meaning:

- battle geometry is now locally relevant
- the fleet should remain in a battle-owned stance rather than keep pursuing an
  old pre-contact approach relation

This is different from:

- objective reached in neutral
- and different from exact-position settling

### D. `hard regularization`

This is what should currently be rejected.

Meaning:

- exact-looking reshaping
- visibly forced cleanup
- discrete end-state snap

This is not an honest hold / terminal semantics.
It is only a cosmetic regularization artifact.

### E. `post-battle or post-contact settling`

This is a later question.

Meaning:

- what a fleet should gradually do after sustained contact geometry stabilizes or
  after battle no longer meaningfully drives local engagement

This question is real, but it should not be smuggled in under the old
arrival-latch mechanism.

---

## IV. Proposed Battle-First Read

The current best first read is:

- hold / terminal should be a **battle-owned geometry state**
- not an arrival-owned shape-freeze state

More concretely:

### 1. Hold should mean: stop chasing the obsolete driver

If the fleet has entered a battle-relevant state, hold should first mean:

- stop continuing to chase the obsolete far-field objective relation

It should **not** mean:

- freeze exact unit positions
- freeze exact slot realization
- force the shape into a neat final shell

### 2. Hold should preserve a battle-owned body, not a frozen template

The fleet should remain:

- coherent enough to still read as one battle body
- loose enough to permit bounded residual motion

So a more honest hold state should allow:

- residual local motion
- residual spacing correction
- residual engagement-driven adjustment

but should reject:

- discrete snap-to-shape
- exact-position clamp
- exact front-face lock

### 3. Terminal should be read weakly

At this stage, `terminal` should not mean:

- "the fleet has reached a final geometrically correct finished form"

It should mean only:

- the old pursuit relation is no longer the active owner
- battle-owned geometry or bounded residual motion is now the owner

This is a much weaker and more honest read.

---

## V. How `neutral` Should Behave Under That Same Read

Because `neutral` is only a validation surface now, it should inherit the same
logic in a weaker, battle-absent form.

That means:

### A. `neutral` should still allow `objective reached`

`neutral` may still record the event:

- objective reached

### B. `neutral` should also stop chasing

Once the stop condition is met, `neutral` should stop continuing to chase the
old approach relation.

### C. `neutral` should not become a separate "clean terminal doctrine"

It should not be optimized for:

- beautiful frozen arrival
- perfectly neat final shell
- independent neutral-specific settling semantics

Instead, it should simply show:

- what the same "stop chasing + bounded residual motion" read looks like when
  battle geometry is absent

### D. What Human should expect from `neutral`

Under this read, `neutral` may legitimately show:

- some lingering motion
- some uneven residual spacing
- less theatrical cleanliness

That is acceptable if the motion still reads as:

- honest
- bounded
- non-chaotic
- non-discrete

So `neutral` should not be judged by:

- prettiness

but by:

- whether it remains an honest non-battle validation of the same broader hold
  idea

---

## VI. First Bounded Candidate Semantics

If Human later approves implementation, the smallest honest first candidate
should probably be:

### Candidate read

1. keep `objective reached` as a reportable event  
2. on reach, disable continued chasing of the previous far-field objective  
3. do **not** force terminal geometry latch  
4. do **not** force exact-position-like hold  
5. allow bounded residual motion to continue under the existing formation /
   battle carrier

This is intentionally weak.

It does not yet answer:

- full post-contact settle doctrine
- front reorientation
- battle-phase relaxation
- post-battle cleanup

But it may already be enough to remove the visibly dishonest part:

- exact terminal regularization masquerading as semantics

---

## VII. What This Note Explicitly Does Not Recommend

### 1. No separate neutral doctrine

This note does **not** recommend:

- one arrival rule for `neutral`
- another contact rule for `battle`

### 2. No exact-position freeze

This note does **not** recommend:

- exact unit freeze
- exact slot freeze
- exact terminal shell ownership

### 3. No battle cosmetics disguised as semantics

This note does **not** recommend:

- making battle terminal look cleaner by forced shape correction

### 4. No viewer-side semantic laundering

This note does **not** recommend solving terminal semantics by:

- viewer smoothing
- direction-read cosmetics
- display-side masking

Viewer support can help Human read, but it must not silently become the owner of
runtime semantics.

---

## VIII. Honest Touchpoint Assessment

### A. Can the first candidate still stay in `test_run/`?

Probably yes.

Reason:

- the currently rejected hard terminal/hold path was harness-owned
- the immediate next correction is still mostly:
  - what to stop forcing
  - what event to keep
  - what not to latch

That is still honestly expressible as a bounded harness-side candidate read.

### B. What may later exceed `test_run/`

If hold / terminal later needs to own:

- battle-contact geometry
- redefined front
- post-contact engagement-owned settle

then the line will likely move closer to deeper runtime / engagement touchpoints.

So the current honest assessment is:

- first candidate: still likely `test_run/`-expressible
- later battle-owned settle doctrine: may not remain honestly `test_run-only`

This should be stated now rather than hidden later.

---

## IX. Recommended Next Execution Order

### Round 1

Keep this note as the alignment asset.

### Round 2

Human reviews this battle-first read.

### Round 3

If Human approves implementation, do one bounded candidate only:

- preserve objective-reached reporting
- disable old chase continuation
- keep hard terminal regularization off
- do not add a new neutral-specific settle rule

### Round 4

Re-observe:

- battle contact onset
- battle near-hold behavior
- neutral arrival under the same read

Only after that should the next terminal/hold discussion continue.

---

## X. Bottom Line

The most honest next read is:

- hold / terminal should be battle-first
- battle-first here means:
  - stop chasing the obsolete driver
  - but do not freeze into a clean final template
- `neutral` should only validate that same broad read in the absence of battle
  geometry

So the next candidate should not ask:

- "how do we make neutral arrival look cleaner?"

It should ask:

- "how do we stop the old pursuit relation honestly, without replacing it with a
  fake geometrically neat end-state?"
