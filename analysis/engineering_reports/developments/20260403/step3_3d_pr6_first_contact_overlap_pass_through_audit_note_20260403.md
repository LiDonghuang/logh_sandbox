# LOGH Sandbox

## PR #6 v4a First-Contact Overlap / Pass-Through Audit Note

Status: design note only  
Scope: first-contact overlap / pass-through loop diagnosis on the active `v4a` line  
Authority: engineering analysis note for Human review  
Non-scope: implementation approval, merge approval, default switch approval, targeting redesign, flow-structure redesign

---

## I. Purpose

This note narrows the current `v4a` battle diagnosis to one specific symptom:

- after the earlier hard first-contact "collision feel" was reduced,
- the fleets now often **overlap / pass through each other**,
- then re-separate,
- then re-approach,
- and repeat this loop.

This note does **not** propose another immediate patch.

Its purpose is to classify that loop more precisely before further repair work.

---

## II. Current Human-Observed Symptom

Current Human read for `1 -> 4 battle` is:

- the earlier hard collision feel at first-contact is materially reduced
- but the fleets do not settle into a believable battle standoff
- instead they overlap, pass through, separate, then re-approach and overlap again

So the sharper current read is:

- the line has reduced one visible discontinuity
- but it still does **not** own a stable range-preserving battle interaction

This is not simply "hold too weak" or "hold too strong."

It is more likely a systems problem involving:

- owner/state semantics
- suppression / approach recovery
- hostile-contact response timing
- movement realization under shared battle-body pressure

---

## III. Current Classification Read

Using the accepted `v4a` discontinuity classes, this symptom is best read as:

### Primary

- **Class A. Owner / state discontinuity**
- **Class C. Force / speed-envelope discontinuity**

### Secondary

- **Class B. Reference / axis discontinuity**

### Not primary for this specific symptom

- **Class D. Targeting / combat discontinuity**
- **Class E. Terminal / settle discontinuity**

Reason:

- the fleets are not failing because target selection is suddenly wrong
- and they are not failing because arrival/settle logic is firing
- they are failing because near-contact battle motion still lacks a stable reversible distance-owned interaction

---

## IV. Sharper Problem Statement

The current issue should not be framed as:

- "why do they still bounce a little?"

The sharper question is:

- **why does the battle body still lack a stable near-contact relation around the intended engagement distance?**

At present, the observed loop is:

1. fleets approach toward battle relation
2. first-contact occurs
3. direct hard collision feel is reduced
4. fleets nonetheless continue into overlap / pass-through
5. local pressure then separates them
6. once separated far enough, approach recovers
7. the same cycle restarts

That is a stronger sign of:

- missing range-preserving interaction ownership

than of a single bad scalar.

---

## V. Mechanisms Most Likely Involved

The following current active mechanisms are the most likely contributors.

### 1. `battle_hold_weight`

Current read:

- suppresses far-field approach as fleets enter the `d*` neighborhood
- reversible by distance

Current limitation:

- it is a suppression term, not a true near-contact equilibrium owner
- by itself, it does not define a stable "stay here and exchange fire" body relation

Class:

- A + C

### 2. `approach_drive`

Current read:

- provides forward approach authority based on distance gap
- now smoothed as a current state

Current limitation:

- after separation, it can recover and re-drive fleets into each other
- so the system may alternate between suppressed approach and renewed charge

Class:

- A + C

### 3. hostile-contact / separation pressure

Current read:

- local short-range body-pressure / spacing response

Current limitation:

- it appears to act mainly once fleets are already too deep into overlap / shared space
- so it can become a "late push-apart" mechanism rather than a stable range-preserving relation

Class:

- C

### 4. engaged speed envelope

Current read:

- reduces movement freedom while engaged
- directional semantics already exist

Current limitation:

- it does not yet appear to create enough shared battle-body braking / discipline to stop pass-through
- especially when fleet-level approach has already carried the body too deep

Class:

- C

### 5. engagement/front geometry signals

Current read:

- `effective_fire_axis`
- `engagement_geometry_active`
- `front_reorientation_weight`

Current limitation for this symptom:

- these matter for front ownership and later battle geometry
- but they do not currently appear to be the primary cause of the overlap/pass-through loop

Class:

- B secondary

---

## VI. Current Best Causal Read

The best current causal read is:

- the system now reduces the earlier abrupt first-contact jump,
- but it still lacks a proper **near-contact battle relation**
- so suppression and local pressure are doing too much of the work

That means:

- `hold` is preventing some abrupt surge
- but not actually owning a believable "maintain battle relation" state
- hostile-contact / separation then responds too late
- approach recovers again once distance opens
- and the fleets re-enter the same cycle

So the overlap/pass-through loop is best read as:

- **reduced collision discontinuity without a completed battle-body equilibrium**

---

## VII. Methodological Implication

This symptom reinforces the current methodological rule:

- do not ask only which scalar is wrong
- ask which signals still have the wrong owner and the wrong timescale

For this specific line, each relevant mechanism must explicitly answer:

1. what is the `raw_*` signal?
2. what is the `*_current` state?
3. what is the `*_weight` actually used by behavior?
4. what is the intended `*_timescale`?
5. what battle-body observation validates it?

For this symptom, the hard validation gates remain:

- fleet-centroid trajectory
- alive-unit body observation

Those are the primary truth surfaces for deciding whether pass-through is actually being reduced.

---

## VIII. Repair Read Suggested by This Audit

This note does not authorize the next implementation.

But it does sharpen the next repair target.

The next repair should **not** be framed as:

- "tune hold harder"
- "tune hold softer"
- "increase one more repulsion term"

The sharper next target should be:

- define a more honest **near-contact battle relation** for the active line

And then ask:

- how should `hold`
- `approach`
- hostile-contact / spacing response
- engaged speed envelope

cooperate to preserve that relation **without**:

- hard collision feel
- overlap/pass-through
- bounce-out and recharge cycling

---

## IX. Recommended Next Application Order

The next practical order suggested by this audit is:

1. inspect `hold` + `approach_drive` + hostile-contact response together
2. decide whether the current active line still lacks a true near-contact relation owner
3. only then choose the smallest mathematical correction candidate

This should remain:

- battle-first
- local to current active `v4a` line
- focused on Class A + C

It should **not** yet branch into:

- targeting correction
- fire-model implementation
- broader flow restructuring

---

## X. Bottom Line

The current first-contact problem is no longer best described as a pure "collision feel" bug.

The sharper read is:

- `v4a` has reduced one kind of first-contact discontinuity
- but it still lacks a stable near-contact battle relation
- so the battle body now tends to cycle through:
  - overlap / pass-through
  - separation
  - renewed approach

This should be treated as a joint:

- owner/state
- force/speed-envelope

problem, with battle centroid and alive-body observation remaining the primary review gates before the next repair turn.
