# PR #6 Human Motion Read Rubric Note

Date: 2026-04-01  
Scope: analysis / review-method note  
Branch: `eng/two-layer-spacing-first-bounded-impl`

## Purpose

Record and formalize the Human motion-read method that has become necessary for PR `#6`.

This note is not an implementation note.

Its purpose is:

- make Human review more reusable across rounds
- reduce repeated ad hoc re-explanation
- keep Engineering from over-trusting local scalar neatness
- clarify which visible failures belong to the current round and which are only secondary exposures

## Why this note is needed

Recent PR `#6` work repeatedly produced local reads that looked cleaner in:

- logic
- parameter ownership
- scalar metrics

but still failed under Human animation review.

The main reasons were:

- rigid plate-like success in matched cases
- shell-like external success with chaotic interior in mismatch cases
- battle-specific apparent improvement that did not carry over honestly to neutral
- late forced regularization masking earlier transition failure

Therefore Human motion read is not just a supplement.

For this line it is the controlling review surface.

## Fixed case set

The default case set for transition review is now:

- `1 -> 4`
- `2 -> 4`
- `2 -> 1`
- `4 -> 1`

And when needed later:

- `1 -> 1`
- `4 -> 4`

Read:

- left side = initial aspect
- right side = target/reference aspect

## Required mode split

For each active mismatch-critical case, compare:

- `neutral`
- `battle`

This split is mandatory because one of the main current diagnostic questions is:

- why battle sometimes shows apparently correct forward compression while neutral does not

## Required phase split

Each case should be read in three phases:

### 1. Pre-contact / marching

Questions:

- does lateral expansion / compression happen?
- does forward compression / expansion happen?
- is the transition coordinated or only partial?

### 2. Contact / post-contact

Questions:

- does contact immediately replace transition with forced regularization?
- does front ownership drift?
- does battle settle into a local rotating junction?

### 3. Terminal / arrival

Questions:

- does arrival trigger abrupt shell-only regularization?
- does the formation become visually orderly only at the last moment?
- do many units reverse direction?
- does terminal hold remain plausible?

## Required axis split

For each phase, read separately:

- lateral / wing-side behavior
- forward / depth-side behavior

This is important because many recent false positives were of the form:

- lateral change happens
- but forward compaction does not

## Required visible reads

For each case, Human should explicitly note:

1. whether lateral reorganization is present
2. whether forward compression / expansion is present
3. whether the transition looks coordinated or broken
4. whether units are being squeezed out / dropped out of the body
5. whether the interior remains orderly or becomes chaotic
6. whether terminal behavior is:
   - honest settling
   - or forced shell regularization
7. whether large numbers of units reverse direction
8. whether any post-contact rotation belongs to the current round's target scope

## Current scope guidance

At the current stage of PR `#6`, not every visible failure belongs to the same implementation round.

### In-scope primary read right now

The current primary question is:

- can mismatch cases achieve honest transition continuity before contact?

More specifically:

- why do neutral mismatch cases still fail to show honest forward compression?
- why does battle sometimes show apparently correct forward compression instead?

This means the current active primary read is:

- pre-contact / marching transition
- especially battle-vs-neutral divergence in mismatch cases

### Secondary but not primary in this round

The following are important, but should not be mistaken for the current round's only target:

- post-contact rotation
- post-contact front ownership drift
- terminal shell regularization
- half-formation reversal at terminal settling

These should be recorded, but not allowed to hide the more basic pre-contact transition problem.

## New warning learned from `2 -> 4`

Human's recent `2 -> 4` observation adds an important caution:

- `1 -> 4` can look more orderly than it deserves
- because its symmetry may accidentally help the current transport seam

Therefore:

- `2 -> 4` must remain a standard sanity case
- `1 -> 4` alone is not enough to validate expansive transition continuity

## How Engineering should use this rubric

Before claiming improvement on PR `#6`, Engineering should be able to answer:

1. which cases improved
2. in which mode (`neutral` / `battle`)
3. in which phase
4. on which axis
5. whether the improvement is:
   - true transition continuity
   - or only late regularization / shell-level success

If those answers cannot be given clearly, Engineering should not treat local metric cleanliness as success.
