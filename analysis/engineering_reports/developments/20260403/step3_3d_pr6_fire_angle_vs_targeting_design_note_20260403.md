# LOGH Sandbox

## PR #6 Fire Angle vs Targeting Design Note
## Battle Fire-Distribution Clarification

Status: design note only  
Scope: PR `#6` battle targeting clarification before implementation  
Authority: engineering design note for Human + Governance review  
Non-scope: implementation approval, merge approval, default switch approval, runtime-core rewrite

---

## I. Purpose

This note narrows the second major battle problem now that the hold line is
directionally acceptable and the next geometry line has been identified as:

- `fire plane vs formation`

The purpose of this note is different.

It asks:

- how should **fire angle** and **target selection** relate to each other in the
  active battle hot path?

This note does not propose a broad tactical redesign.
It only clarifies the smallest bounded correction family worth serious review.

---

## II. Current Accepted Read

### 1. `attack_range = 10` exposed the problem more honestly

Human recent testing with:

- `attack_range = 10`

made the battle read clearer.

The problem now visible is:

- too many units concentrate on the same target in the same tick

This is not merely a cosmetic effect.
It suggests the current target-selection chain is too concentrated and that the
current fire-angle participation enters too late.

### 2. This is now a mid/long-term stabilization line

Governance already clarified that this line should not become a fast patch loop.

The correct posture is:

- define one bounded correction concept
- review with Human + Governance
- if accepted, implement once
- then prefer stabilization over repeated redesign

So this note is intentionally narrow.

---

## III. Current Hot-Path Reality

The active owner is frozen runtime:

- `runtime/engine_skeleton.py::resolve_combat()`

Current practical read:

1. a unit scans enemies within attack range
2. target selection is driven mostly by:
   - low HP preference
3. distance is only a very weak tie-break
4. current fire-angle logic does **not** choose the target
5. instead, fire-angle enters only after selection as a damage-quality modifier

So the current hot path is not:

- angle-aware target selection

It is closer to:

- low-HP target picking
- plus post-selection directional damage adjustment

---

## IV. Why This Is No Longer Enough

### A. Fire angle currently enters too late

If a unit can only bring weak or awkward fire onto a target, that should
already influence:

- whether that target is a good target to choose

not only:

- how much damage lands after selection

Otherwise the runtime still allows:

- many units to choose the same target
- even when some of them have poor engagement geometry against it

### B. Fire distribution is too concentrated

Human read now indicates:

- too many attackers pile onto one target in one tick

That means the current chain is missing a bounded notion of:

- "this target is already sufficiently crowded this tick"

This is not the same as local geometry doctrine.
It is a simpler allocation issue.

### C. This line is different from fire-plane/front ownership

The earlier note on:

- `fire plane vs formation`

is about:

- which battle-facing front the fleet currently owns

This note is about:

- once units are already engaging,
- how should they distribute fire more honestly
- and how should angle quality participate in that choice

These two lines are related, but they are not the same mechanism.

---

## V. Bounded Correction Family

The smaller and cleaner primary candidate is now:

- `target_merit = hp_term + expected_damage_term`

where:

- `expected_damage = base_damage * angle_quality * range_quality`

This note now treats that as the preferred first bounded read.

### 1. `hp_term`

Keep a bounded low-HP preference.

Reason:

- finishing vulnerable targets is not inherently wrong

But it should no longer dominate the entire targeting chain by itself.

### 2. `expected_damage_term`

The primary battle correction should be:

- a target should look better not only because it is weak
- but because the attacker expects to deal better damage to it

So the new primary merit should explicitly combine:

- fire angle
- and distance

in one expected-damage read.

### 3. `angle_quality`

Let current attack-angle quality participate in selection, not only in damage.

Reason:

- fire-angle should influence whether a target is attractive
- not only how rewarding it is after already being chosen

### 4. `range_quality`

Distance should now begin to enter the same damage-quality read.

The current first candidate is intentionally simple:

- linear falloff from a better/nearer engagement band toward the far edge of
  allowed attack distance

This is still a bounded proposal, not a final doctrine.

It should be read as:

- expected damage should fall when the attacker is forced into poorer range
  geometry

not as:

- nearest-target pursuit

### 5. `crowd_term` should move out of the first merit layer

This note no longer treats `crowd_term` as part of the first primary score.

Reason:

- the first honest "apple to apple" merit comparison should be:
  - target vulnerability
  - expected damage

If future review still finds unrealistic over-concentration after that, a
bounded fire-allocation / diversification line can be discussed separately.

---

## VI. How This Should Relate to Existing Fire-Quality Logic

Current repo already has an angle-based combat-quality line:

- attacker orientation vs attacker-to-target direction

This should remain conceptually aligned.

The cleaner read is:

- one directional semantics
- two effects

Effect A:

- target attractiveness through expected damage

Effect B:

- realized damage quality

So the note does **not** recommend inventing a second unrelated angle meaning.

Instead it recommends:

- keep one directional read
- let it participate both in:
  - selection quality
  - and fire quality

with different bounded weights

---

## VII. What This Line Should Not Become

This correction should not turn into:

- unrestricted nearest-enemy pursuit
- a large new tactical AI layer
- a hidden replacement for engagement geometry
- repeated short-cycle rewrites after acceptance

It should stay:

- bounded
- legible
- stabilizable

That is why this note prefers a simple score family rather than a broad local
combat doctrine.

---

## VIII. Validation Read

If this line is later implemented, it should be judged by:

1. Human battle motion read
2. fire-distribution plausibility
3. the existing hard runtime-dynamics gates:
   - fleet-centroid trajectory
   - alive-unit body observation

Key questions:

- do attackers still over-concentrate on one victim?
- does angle quality now influence who gets selected?
- does the correction improve battle readability without destabilizing the
  larger battle body?

This line should not be judged only by:

- raw kill speed
- or scalar neatness

---

## IX. Touchpoint Judgment

This is not a `test_run-only` line.

Reason:

- the real hot path lives in frozen runtime
- `test_run` can discuss and prepare the read
- but it cannot honestly own the final correction semantics

So this note is explicitly a design clarification for later Human +
Governance review, not a hidden implementation precursor.

---

## X. Bottom Line

At `attack_range = 10`, the current battle hot path now reads as too
concentrated and too weakly angle-aware at the selection stage.

The sharper current read is:

- fire angle enters too late
- distance quality is absent from the same primary merit read

The preferred first bounded correction family is now:

- `hp_term + expected_damage_term`

with:

- `expected_damage = base_damage * angle_quality * range_quality`

and with `crowd_term` deferred out of the first primary merit layer

This should be treated as:

- a bounded mid/long-term stabilization candidate

not:

- a fast patch loop
