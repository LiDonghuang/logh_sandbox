# TL Boundary Remark

Date: 2026-03-13
Status: Engineering boundary note
Scope: Clarify why the current fleet-level direction-surrogate issue touches `TL` responsibility, while still remaining outside current `TL` activation work.

## 1. Why this note is needed

The ongoing mirrored close-contact symmetry audit has now reached a point where a low-level runtime question overlaps with a future parameter-responsibility question.

The immediate engineering problem is:

- the current fleet-level direction surrogate in `evaluate_target()`
- especially raw `nearest-enemy`

appears too sharp and too symmetry-sensitive for mirrored close-contact diagnostics.

However, the deeper semantic issue is:

- "what kind of enemy reference should a fleet orient toward?"

This is not purely a movement-detail question.
At the personality-mechanism level, this is much closer to the future responsibility of `TL` (`targeting_logic`).

So the project needs a boundary clarification:

- what belongs to the current low-level symmetry cleanup
- and what should be left for a later `TL` mechanism

## 2. Engineering judgment

Current engineering judgment is:

1. The responsibility for selecting *which enemy or enemy-group* should define a fleet-level direction surrogate is semantically closer to `TL` than to movement geometry itself.
2. The current audit is **not** an argument for activating `TL` now.
3. The current audit **is** an argument that the runtime needs a cleaner, more neutral, more replaceable direction-surrogate substrate before future `TL` work arrives.

In short:

- future `TL` should decide the preference logic
- current low-level work should only make sure the default surrogate is not already distorting symmetry

## 3. Why this is not a small issue

This is not a minor local implementation detail for three reasons.

### 3.1 It touches authority allocation

If movement internally hardcodes a strong fleet-level target-direction preference, then part of future `TL` authority has already been silently pre-claimed by a low-level runtime rule.

That would repeat the same pattern already seen elsewhere in the project:

- early mechanism enters
- later mechanism arrives on pre-shaped substrate
- later mechanism becomes hard to read cleanly

### 3.2 It affects mirrored diagnostics immediately

The current audit already shows that the default surrogate can amplify asymmetry in mirrored close-contact openings.

So this is not only a future design issue.
It is also a present diagnostic-quality issue.

### 3.3 It can silently bias future mechanism work

If the default surrogate remains too sharp or too semantically opinionated, then future work on:

- `TL`
- `PD`
- contact-entry behavior
- post-contact continuation

will all inherit a biased direction substrate.

That would make later mechanism interpretation harder, not easier.

## 4. Boundary proposal

Engineering recommends the following boundary distinction.

### 4.1 What belongs to the current low-level audit

Current low-level audit may legitimately ask:

- is the default fleet-level direction surrogate numerically stable enough for mirrored diagnostics?
- is it symmetry-safe enough for same-force mirrored close-contact openings?
- is it too sharp, too discontinuous, or too amplification-prone?
- is there a more neutral surrogate family for diagnostic use?

This remains low-level substrate work.

### 4.2 What should remain outside the current audit

Current audit should **not** decide:

- what the canonical future `TL` policy should be
- whether fleets should prefer nearest enemy, local enemy cluster, high-value target, centroid, weak target, or any other semantic targeting style
- how `TL` should differentiate personalities later

Those are later `TL` design questions.

## 5. Working engineering framing

The cleanest current framing is:

> We are not designing `TL`.
> We are identifying whether the current default direction surrogate is too sharp and too authority-heavy to serve as a neutral pre-TL substrate.

That is why:

- testing `nearest-enemy`
- comparing it with `nearest-5 centroid`
- comparing it with `enemy centroid`

does **not** mean that `TL` has been opened.

It means:

- the substrate under future `TL` is being audited for neutrality and replaceability.

## 6. Current engineering recommendation

Engineering recommendation at this stage:

1. Treat this topic as a boundary issue, not a local patch question.
2. Do not silently convert the current audit into `TL` implementation work.
3. Raise this explicitly to governance and human architect discussion.
4. Continue low-level tracing only under the narrow question:

> Is the current default fleet-level direction surrogate too sharp and too symmetry-sensitive to remain the neutral pre-TL diagnostic default?

## 7. Bottom line

This topic belongs near `TL`, but current work is still properly below `TL`.

The correct current goal is not:

- "implement targeting logic now"

but:

- "make sure the default direction-surrogate substrate does not silently occupy future `TL` authority or distort mirrored diagnostics before `TL` is even active."
