# Step 3 3D PR #6 Banded-Surface Follow-Up Governance Review Request (2026-03-30)

Status: governance review request  
Authority: discussion / review only, not implementation authorization  
Scope: PR #6 formation-substrate follow-up read after human observation and local re-check  
Non-scope: runtime-core rewrite, hostile-contact repair as primary line, legality redesign, turning-cost implementation

## Purpose

This note asks Governance to review the next engineering read on PR `#6` after:

- Human direct observation of `neutral_transit_v1` and `battle`
- local re-check under matched `v4a + soft_morphology_v1 + expected_reference_spacing=2.0 + min_unit_spacing=1.0`

The specific question is no longer:

- whether the new soft carrier is semantically real

That threshold has already been crossed.

The current question is:

- why the new carrier now reads as an explicit left / center / right banded system
- why `neutral_transit_v1` shows stronger early lateral disturbance than battle
- what the next bounded correction should be without rolling back the band idea itself

## Current Human + Engineering Read

Human observed:

1. `neutral_transit_v1`
- initial formation is visibly partitioned into left / center / right groups
- early transit already shows small but persistent wing-side disturbance
- after arrival, the formation collapses into three compact lateral clusters with continuing local "Brownian" motion

2. `battle`
- initial formation is also visibly partitioned into left / center / right groups
- pre-contact march is visually steadier than neutral transit
- early hostile interleaving remains, but appears somewhat less extreme than before

Human also clarified:

- the neutral early-phase instability is already visible before the terminal arrival phase
- this difference should not be hand-waved as only an end-of-run effect

Engineering re-check now agrees with that correction.

## What Was Re-Checked

Local re-check used the current PR `#6` carrier line with:

- `movement_model = v4a`
- `reference_surface_mode = soft_morphology_v1`
- `expected_reference_spacing = 2.0`
- `min_unit_spacing = 1.0`
- `restore_strength = 0.25`
- `soft_morphology_relaxation = 0.2`

Matched comparisons were re-run for:

- `neutral_transit_v1`, `aspect_ratio = 1.0`
- `battle`, `aspect_ratio = 1.0`
- `neutral_transit_v1`, `aspect_ratio = 4.0`
- `battle`, `aspect_ratio = 4.0`

The purpose was not to produce a new artifact batch yet, but to answer whether the neutral early-phase difference still exists under matched aspect ratio.

## Re-Check Findings

### 1. The lateral three-block read is real

The current first carrier should be read as:

- `front/mid/rear + left/center/right`
- effectively a `3 x 3` banded surface

This is not only a viewer illusion.

The current implementation explicitly:

- derives stable broad band identity from initial terciles
- groups units by `(forward_band, lateral_band)`
- computes a target center per group
- clamps each group to its own target envelope
- rescales within each group

So the current carrier behaves less like:

- one continuous morphology field

and more like:

- several bounded subformation regions

### 2. Neutral early-phase lateral disturbance is real

Matched-aspect re-check confirms that `neutral_transit_v1` shows stronger early lateral micro-disturbance than battle.

For `aspect_ratio = 1.0`, average early lateral per-tick motion over approximately `tick 1..50` was:

- neutral:
  - left `~0.0092`
  - center `~0.0086`
  - right `~0.0026`
- battle:
  - left `~0.0047`
  - center `~0.0045`
  - right `~0.0026`

So the neutral left/center bands are indeed visibly more active early, not only late.

For `aspect_ratio = 4.0`, the same pattern is less uniform but still not cleanly identical between modes.

### 3. Neutral terminal collapse is also real

In the same re-check, `neutral_transit_v1` still shows the strong post-arrival failure mode:

- `objective_reached_tick = 423`
- after arrival, lateral motion jumps from the early `~0.003 - 0.009` scale
  to roughly `~0.48 - 0.60`
- the three lateral groups contract into compact clusters and continue local wandering

This confirms the human observation that the post-arrival three-cluster read is a real carrier behavior, not just a subjective visual impression.

## Current Explanation

Engineering's current explanation is now narrower and more specific than the earlier "too rigid / too strong restore" read.

### A. The carrier currently has band ownership that is too explicit and too active

The current problem is not best read as:

- simple restore-strength excess

and not only as:

- rigid exact-slot ownership

The more precise read is:

- current band ownership is too explicit / too active

That is why the branch currently behaves as:

- banded subformations by behavior

not yet as:

- one continuous soft morphology

### B. Neutral still borrows a mode-specific target direction too directly

The current soft carrier still resolves its working frame from the active target direction path rather than from a truly independent morphology-axis state.

That means:

- `neutral_transit_v1` uses the fixture point-anchor target direction path
- battle uses the battle target-substrate path

Both are fleet-level, but they are not yet the same owned morphology-axis semantics.

So the current carrier has not yet fully separated:

- movement target direction

from:

- morphology reference axis

This is now the most plausible explanation for why neutral shows stronger early lateral disturbance than battle under matched aspect ratio.

### C. Post-arrival collapse is a missing hold/latch semantics problem

Once neutral reaches the destination:

- external forward-driving meaning collapses
- but the banded morphology actuation continues

So the system no longer reads as:

- one fleet holding a stable formation at objective

and instead reads as:

- several lateral band clusters still trying to locally re-organize

This should be read as missing:

- formation hold / latch semantics

not merely as noise.

## Engineering Recommendation

Engineering does **not** recommend rolling back the band idea itself.

Human's structural point is accepted:

- if bands are opened at all, they should be treated symmetrically and cleanly
- not by silently weakening lateral ownership only

This is also a better long-path read for future 3D formation expression.

### Recommended next bounded correction set

#### 1. Introduce an independent fleet-level morphology axis state

The branch should stop directly using the current mode-specific target direction as the immediate morphology reference frame.

Instead, introduce:

- `morphology_axis_current`

with:

- bounded continuous relaxation toward desired direction

Purpose:

- make morphology ownership actually fleet-owned
- reduce mode-specific jitter transfer into the reference surface

#### 2. Introduce formation hold / latch semantics

Add a fleet-level hold state, conceptually usable later in both:

- neutral-transit arrival
- battle "await / hold position" situations

When hold is activated:

- latch current morphology axis
- latch current morphology extents
- latch current band-anchor state
- stop re-solving the reference surface from the external objective each tick

This is required not only for current neutral-transit behavior but also for future battle formation meaning.

#### 3. Keep band equality, but soften band actuation

Do **not** remove bands.

Do **not** treat lateral bands as less legitimate than forward bands.

Instead:

- keep `front/mid/rear + left/center/right`
- keep them as stable topology ownership
- stop making every `(forward_band, lateral_band)` act like a strong per-tick subformation center

The next carrier should move toward:

- shared morphology lattice / anchor frame
- band identity as topology membership
- within-band soft residual placement

and away from:

- per-band recenter + per-band clamp + per-band rescale as the dominant behavior

## Why This Is Preferred Over Other Immediate Paths

### Not preferred now

- more restore-strength tuning
- immediate hostile-contact repair as the new main line
- direct rollback of bands
- full 3D ownership claim

### Preferred now

- clarify morphology ownership first
- separate morphology axis from raw movement target direction
- add hold/latch semantics
- soften band actuation without discarding topology

This keeps PR `#6` on the formation-substrate line while staying consistent with the recent movement and computation discussions:

- clear source-of-truth
- bounded state
- deterministic carrier
- no every-tick global remap
- no frozen runtime-core rewrite

## Review Questions For Governance

Please review whether Engineering's current read is acceptable:

1. The new problem should now be read as:
- not mainly restore-strength
- not mainly rigid slot ownership
- but current band ownership being too explicit / too active

2. The neutral early-phase difference should now be read as:
- evidence that morphology axis ownership is not yet truly independent
- rather than as an unimportant fixture-only visual quirk

3. The neutral terminal three-cluster collapse should now be read as:
- missing formation hold / latch semantics
- not only as residual jitter

4. The next bounded carrier should therefore prioritize:
- morphology-axis state
- hold/latch state
- softening band actuation while keeping band equality

## Bottom Line

PR `#6` should still remain on the formation-substrate main line.

The next bounded correction should **not** be:

- further scalar restore tuning
- hostile-contact repair as the main line
- rollback of band structure

The next bounded correction should be:

- independent morphology-axis ownership
- formation hold / latch semantics
- equal but softer band actuation

Engineering requests Governance review on that read before the next implementation step.
