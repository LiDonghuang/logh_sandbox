# LOGH Sandbox

## PR #6 v4a Discontinuity Audit Note
## Battle / Formation Non-Smoothness Classification

Status: design note only  
Scope: PR `#6` v4a discontinuity analysis and methodology clarification  
Authority: engineering analysis note for Human review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note does **not** propose another immediate patch.

Its purpose is to stop local repair from outrunning diagnosis.

The recent Human correction is accepted:

- v4a still contains multiple kinds of "too hard / too discontinuous" behavior
- these likely come from more than one mechanism
- so the next step must be:
  - classification first
  - consistent smoothing methodology second
  - implementation only after that

The most severe current visible symptom remains:

- the strong "collision feel" around `first-contact`, where the two fleets appear
  to slam, separate, re-approach, and slam again

This note treats that as a systems problem, not a one-off bug.

---

## II. Current Accepted Read

### 1. The problem is broader than one parameter

Current Human read indicates that the following are all live:

- hard first-contact collision feel
- raw/step-like engagement activation
- target / axis / fire-plane jumps
- hold suppression jumps
- arrival / settle discreteness

So the problem should no longer be framed as:

- "which single parameter still needs tuning"

The sharper read is:

- multiple mechanisms are still being driven too directly from raw current-tick
  signals

### 2. This is not only a battle problem, but battle exposes it most clearly

The same family of non-smoothness has already appeared in:

- neutral arrival
- formation transition
- battle first-contact
- battle late rotation / clustering

However:

- battle remains the authority surface

So this audit uses battle as the main diagnostic lens.

---

## III. Main Discontinuity Classes

The current v4a problems are best classified into at least five classes.

### Class A. Owner / state discontinuity

Examples:

- far-field owner vs engagement owner
- hold strength vs approach strength
- engagement active vs inactive

Failure pattern:

- an event or threshold is treated too much like an on/off switch

Typical visible result:

- abrupt behavioral phase change
- sudden loss or return of approach authority

### Class B. Reference / axis discontinuity

Examples:

- target direction
- morphology axis
- effective fire axis
- formation front responsibility

Failure pattern:

- a fleet-level reference is driven directly by noisy current-tick geometry

Typical visible result:

- posture jumps
- fire-axis swings
- indicators that jump much faster than the battle body visibly changes

### Class C. Force / speed-envelope discontinuity

Examples:

- hold suppression
- approach suppression
- engaged speed envelope
- hostile contact / repulsion-like responses

Failure pattern:

- movement authority changes too sharply when crossing a local condition

Typical visible result:

- the battle body looks like it is repeatedly "bouncing"
- fleets appear to be pushed apart, then pulled back in

### Class D. Targeting / combat discontinuity

Examples:

- many units switch target in the same tick
- angle quality only enters after selection
- concentrated fire suddenly collapses a local contact picture

Failure pattern:

- target choice and damage realization are not smooth enough relative to one
  another

Typical visible result:

- abrupt concentration
- unstable local fire exchange
- battle geometry being kicked by combat spikes

### Class E. Terminal / settle discontinuity

Examples:

- old hard arrival regularization
- snap-to-terminal-like behavior
- too-discrete "finished transition" reads

Failure pattern:

- terminal semantics are treated as a shape lock rather than a soft state

Typical visible result:

- visibly forced final regularization
- half the body flipping or snapping into a cleaner shell

---

## IV. Current Priority Read

Not all discontinuity classes are equally urgent.

Current priority should be:

1. **Class C: force / speed-envelope discontinuity**
   - because the first-contact "collision feel" is currently the most severe and
     most unrealistic visible problem

2. **Class B: reference / axis discontinuity**
   - because battle geometry ownership is still too jumpy and noisy

3. **Class D: targeting / combat discontinuity**
   - because `attack_range = 10` is now exposing concentration problems more
     clearly

4. **Class E: terminal / settle discontinuity**
   - still real, but no longer the most urgent battle read

5. **Class A: owner / state discontinuity**
   - this remains foundational, but it is best handled together with the above
     rather than as an isolated abstract line

This ordering may still change with Human review.
It is only the current best read.

---

## V. The Current First-Contact "Collision Feel"

The strongest current visible problem should be read carefully.

It should **not** be reduced to:

- one bad repulsion constant
- one bad hold parameter
- one bad contact event flag

The current sharper read is:

- the collision feel likely emerges from several step-like mechanisms stacking:
  - battle hold suppression
  - engaged activation
  - target/reference switching
  - speed-envelope changes
  - hostile-contact / separation pressure

So the right next question is not:

- "which one value is wrong?"

It is:

- "which raw signals are being turned into hard behavior too directly?"

---

## VI. Consistent Methodology Proposal

This note recommends a common treatment pattern for future v4a battle /
formation signals.

Each mechanism should explicitly distinguish:

1. `raw_*`
   - current-tick direct measurement or geometric read

2. `*_current`
   - the smoothed state actually used by runtime/harness behavior

3. `*_active`
   - whether the owning layer is materially active

4. `*_weight`
   - how strongly that owner currently biases behavior

The key rule is:

- **do not let raw current-tick signals directly own fleet behavior unless the
  semantics explicitly require it**

Instead, signals should be forced to answer:

1. is this an event or a state?
2. if it is a state, should it have:
   - relaxation
   - hysteresis
   - persistence
   - reversible weighting
3. what battle/body observation should verify it?

This should become the default review template for v4a battle and formation
signals.

---

## VII. Recommended Interpretation Patterns

The following default interpretations are recommended unless strong reason says
otherwise.

### A. Engagement-related ownership

Preferred read:

- continuous state
- reversible
- persistence-aware

Not:

- first-contact event latch

### B. Fleet-level axes and fronts

Preferred read:

- smoothed state
- low-jump
- fleet-level

Not:

- raw current-tick aggregate directly owning orientation

### C. Speed / pressure / suppression terms

Preferred read:

- bounded weight
- continuously varying with distance / geometry / activation

Not:

- step-like on/off toggles

### D. Arrival / settle

Preferred read:

- soft state with residual motion still allowed

Not:

- exact-position-like regularization

---

## VIII. Validation Rule

The already accepted hard gates should now be read as part of this methodology,
not as optional review aids:

- fleet-centroid trajectory
- alive-unit body observation

Reason:

- these are the lightest and most basic descriptions of runtime dynamics
- they already exist in tracking
- they are low-cost
- they are more trustworthy than local scalar neatness when discontinuity is the
  problem under inspection

So any future candidate that claims to reduce non-smoothness must be checked
against both.

---

## IX. Suggested Next Application of This Audit

This note does not yet pick the next patch.

But it does suggest the next design/application order:

1. first-contact collision / bounce analysis
2. battle front / fire-plane signal smoothing
3. fire-angle / targeting fire-model structuring
4. terminal/settle semantics cleanup

That order is recommended because it follows the current visible severity of the
problem on the battle authority surface.

---

## X. Bottom Line

The v4a branch should no longer be debugged as if each new non-smooth behavior
is an isolated bug.

The sharper current read is:

- v4a still contains several classes of discontinuity
- these classes are interacting
- battle first-contact exposes them most brutally

Therefore the next implementation work should follow a common methodology:

- classify the owner
- separate raw signal from current state
- prefer relaxation / hysteresis / persistence / reversible weight
- validate first by centroid trajectory and alive-unit body

This is the current recommended engineering frame before the next repair turn.

