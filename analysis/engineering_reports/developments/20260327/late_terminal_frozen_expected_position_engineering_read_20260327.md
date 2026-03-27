# Late Terminal Frozen-Frame First Cut - Engineering Read

Date: 2026-03-27
Status: engineering diagnosis only
Scope: bounded `neutral_transit_v1` late-terminal first-cut follow-up

## Current engineering read

The current first cut appears to have solved the wrong part only partially.

It does stop one specific behavior:

- expected positions are no longer rebuilt forever from a moving centroid and moving target axis

But it likely introduces a new persistent mismatch:

- target pull still keeps trying to drive the fleet centroid toward the objective anchor
- while expected-position restore is now centered on a frozen terminal centroid that was latched before the fleet fully settled at the anchor

In the current bounded run, the frozen frame is latched at:

- `frozen_terminal_centroid_xy = [348.760603, 348.761082]`

while the objective anchor remains:

- `[350.0, 350.0]`

So after the latch, the solver appears to be running with:

- a restore frame still centered around the pre-anchor centroid
- a target term still pulling toward the actual anchor

That creates a continuing unit-level tug-of-war instead of a clean settle.

## Why the observed 3D result still looks broken

This source-level reading matches the current human-visible outcome:

- formation still looks broken around `tick 425 .. 435`
- unit heading still flips hard

The current first cut changed the contributor mix, but did not produce a common terminal rest state.

The likely chain is:

1. target pull remains alive inside the terminal window
2. frozen-frame restore now pulls units toward slots centered on the latched centroid, not the anchor
3. separation and post-movement projection reshape the resulting conflict

That is a narrower, more concrete read than "viewer issue" or "projection-only issue".

## Current strongest hypothesis

The strongest current hypothesis is:

- the key remaining late-terminal conflict is no longer "moving frame forever"
- it is now "frozen frame centered at the wrong place while target pull still aims at the anchor"

In other words:

- the first cut may have removed the old moving-frame residual
- but replaced it with a frozen-frame / target-center mismatch

## Engineering recommendation

Before another fix turn, Engineering should ask Governance to let the next debug/fix question separate:

1. frame orientation freeze
2. frame centroid freeze

Those two are currently coupled, and that coupling now looks suspicious.

If a next bounded root-cause turn is opened, the narrowest thing worth checking is likely:

- whether the terminal reference should stop rotating while still allowing its center to converge toward the anchor

rather than:

- freezing both axis and centroid at the same first-entry moment

This is only a recommendation, not a silent implementation change.
