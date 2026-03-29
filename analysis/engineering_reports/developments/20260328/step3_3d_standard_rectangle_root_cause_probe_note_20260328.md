# Step 3 3D Standard Rectangle Root-Cause Probe Note

Date: 2026-03-28  
Scope: local-only diagnostic note  
Target cases: `neutral_transit_v1`, `100 units`, `aspect_ratio = 1.0` and `4.0` only

## Purpose

This note records one final bounded root-cause probe for the observed early-phase
stretching of standard rectangular formations.

The probe explicitly excludes:

- `wide_front_120`
- `aspect_ratio = 8.0`
- viewer-only explanations
- implementation proposals
- mechanism edits

## Starting Point

Human observation already established:

- `aspect_ratio = 1.0` starts visually close to square, then becomes slightly elongated along
  the advance axis during the early run.
- `aspect_ratio = 4.0` shows the same qualitative tendency, starting from a wide rectangle and
  then deepening along the advance axis during the early run.

The first question for this probe was:

**is this a viewer artifact, a reference-layout-generation problem, or a runtime mechanism effect?**

## Reference Layout Check

The initial reference layout generation for the two standard cases is clean:

- `aspect_ratio = 1.0` -> row counts `[10,10,10,10,10,10,10,10,10,10]`
- `aspect_ratio = 4.0` -> row counts `[20,20,20,20,20]`

So the standard rectangle cases do **not** start from malformed row-count generation.

The initial local-shape readings are also clean:

- `1.0`: lateral span `18.0`, forward span `18.0`, width/depth `1.0`
- `4.0`: lateral span `38.0`, forward span `8.0`, width/depth `4.75`

This rules out "reference layout is already wrong at tick 0" as the primary explanation.

## Runtime Findings

## 1. The distortion is real in headless runtime, not only in 3D view

Headless local-shape readings match the visual trend.

For `aspect_ratio = 1.0`:

- tick `1`: width/depth `1.0196`
- tick `21`: width/depth `0.9831`
- tick `51`: width/depth `0.8781`
- tick `101`: width/depth `0.7936`

For `aspect_ratio = 4.0`:

- tick `1`: width/depth `4.7807`
- tick `21`: width/depth `3.4233`
- tick `51`: width/depth `3.0559`
- tick `101`: width/depth `3.0089`

So the effect is not a viewer-only illusion.

## 2. The first visible drift appears before projection

The movement pipeline was split into three shape reads:

- `pre`: start-of-tick shape
- `move`: post-movement, pre-projection shape
- `post`: post-projection shape

Example:

- `aspect_ratio = 1.0`, tick `1`
  - pre ratio `1.0000`
  - move ratio `0.9921`
  - post ratio `1.0196`

- `aspect_ratio = 4.0`, tick `21`
  - pre ratio `3.4952`
  - move ratio `3.4212`
  - post ratio `3.4233`

Interpretation:

- shape drift begins in the movement step
- projection modifies the result, but is not the first cause
- projection is more lateral/local in effect than longitudinal/global

## 3. Projection is not the primary forward-axis driver

Per-unit trace decomposition shows:

- `projection_forward` mean stays near `0`
- `projection_lateral` is more visible during early ticks

This matches the earlier legality reading:

- projection is mostly resolving spacing overlap
- projection is not the main mechanism pushing the rectangle deeper along the forward axis

## 4. Early target drive dominates cohesion restore

Per-unit contribution reads were compared for:

- `target_contrib`
- `cohesion_contrib`
- `separation_contrib`

Early ticks show a strong asymmetry:

- tick `1`: `cohesion` is effectively `0` for both standard cases
- tick `1` / `2`: `target_contrib` is already strongly positive along the forward axis
- `separation` contributes mostly local relief, including lateral relief

Later ticks show that cohesion does start acting, but not strongly enough to stop elongation:

For `aspect_ratio = 1.0`, tick `21`:

- rear10: `coh_f ~= +0.1206`, `tgt_f ~= +1.2971`, `sep_f ~= -0.4633`
- front10: `coh_f ~= -0.3063`, `tgt_f ~= +1.2571`, `sep_f ~= 0`

For `aspect_ratio = 4.0`, tick `21`:

- rear10: `coh_f ~= +0.1850`, `tgt_f ~= +0.7768`
- front10: `coh_f ~= -0.2681`, `tgt_f ~= +1.1917`

Interpretation:

- rear units are being asked to catch up
- front units are being asked to restore backward
- but the objective-facing target drive remains larger than the restore term
- this lets front units continue to outrun the reference envelope

## 5. Expected-position reference is not acting as a strong forward-depth anchor

The runtime expected-position surface is built as:

- `current centroid`
- plus `initial slot offsets`
- resolved along the current target/reference axis

So this surface is a moving reference frame, not a fixed world-frame shape anchor.

That by itself is not necessarily wrong, but it means:

- it does not automatically impose strong depth preservation
- it must rely on runtime restore weighting if shape preservation is desired

Also important:

- the axial restore gate currently inspected in trace stays effectively inactive during ordinary early ticks
- in the sampled trace, `cohesion_axial_raw` remains `0.0`
- this means the special axial gating path is not the mechanism currently maintaining standard-rectangle depth

## 6. Error against expected positions confirms forward-axis drift

Comparing `x_post/y_post` against `expected_pos_x/y` in local forward/lateral coordinates:

For `aspect_ratio = 1.0`, tick `101`:

- rear10 mean forward error `~= -0.6924`
- mid10 mean forward error `~= +0.7787`
- front10 mean forward error `~= +3.0035`

For `aspect_ratio = 4.0`, tick `101`:

- rear10 mean forward error `~= -0.4714`
- mid10 mean forward error `~= +0.8609`
- front10 mean forward error `~= +2.7946`

Lateral error exists, but it is smaller than the forward error signal in the later sampled ticks.

Interpretation:

- front ranks are materially ahead of their expected forward slots
- rear ranks are lagging behind expected forward slots
- the rectangle is not merely "spreading sideways"
- it is being stretched along the forward axis relative to the moving expected-position reference

## Bounded Conclusion

The standard-rectangle early stretching is best read as a **runtime mechanism issue**.

The current best bounded reading is:

1. standard rectangle generation itself is clean
2. the distortion is real in headless runtime, not only in the viewer
3. drift begins in the movement step before legality projection
4. target-facing forward drive is stronger than early restore pressure
5. projection mainly resolves local spacing and does not appear to be the primary cause
6. the current centroid-anchored expected-position reference does not by itself enforce strong depth preservation during ordinary transit ticks

## What This Note Does Not Claim

This note does **not** yet claim a final single-line fix.

It does **not** yet decide:

- whether the next correction should live in target-drive weighting
- cohesion restore weighting
- axial restore activation policy
- spacing / projection cooperation rules

It only narrows the primary mechanism suspicion to:

- **movement-vs-restore balance in ordinary transit ticks**

with projection treated as a secondary amplifier / local resolver rather than the lead cause.

## Recommended Read

For later governance / engineering review, this note should be read as:

- one final bounded root-cause probe
- standard rectangles only
- enough to justify that the issue belongs to runtime mechanism tuning / policy, not viewer polish and not malformed initial layout generation
