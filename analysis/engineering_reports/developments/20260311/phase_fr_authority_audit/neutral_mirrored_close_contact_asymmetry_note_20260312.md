# Neutral Mirrored Close-Contact Asymmetry Note

Date: 2026-03-12
Status: Engineering diagnostic note
Scope: Explain why `FrontCurv` differs strongly under the current neutral mirrored close-contact test setting, and identify other low-level blockers that should be treated as pre-personality issues.

## 1. Test principle

This note uses the current `test_run/test_run_v1_0.settings.json` as a low-personality-influence diagnostic case:

- Fleet A archetype: `grillparzer`
- Fleet B archetype: `knappstein`
- Current archetype values: both sides are all `5`
- Initial size: `100 vs 100`
- Initial aspect ratio: `2.0 vs 2.0`
- Initial deployment: mirrored diagonal close-contact setup
  - A origin `[80, 80]`, facing `45 deg`
  - B origin `[120, 120]`, facing `225 deg`

This is not a pure movement baseline, because the active setting still uses:

- `runtime.selectors.movement_model = baseline -> v3a`
- `runtime.movement.v3a.experiment = exp_precontact_centroid_probe`
- `runtime.movement.v3a.centroid_probe_scale = 0.5`

However, it is still a valid low-personality diagnostic window because:

- the two personalities are numerically identical
- ODW-centered posture bias is neutral at `ODW = 5`
- the opening geometry is intentionally mirrored and close-contact

So any strong A/B divergence here should be treated as a low-level symmetry problem first, not a personality-semantics problem.

## 2. What was confirmed

### 2.1 Personality is not the cause in this case

Current `archetypes/archetypes_v1_5.json` has:

- `grillparzer = all 5`
- `knappstein = all 5`

So the current run is not testing asymmetric FR / MB / ODW / PD values.

### 2.2 Initial geometry is truly mirrored

After the recent `origin_xy` / aspect-ratio centering fix, the current initial unit positions are an exact 180-degree mirror pair.

Observed checks:

- fleet centroids sum to `(200.0, 200.0)`
- reflected B-side unit positions match A-side unit positions exactly
- `max_180_symmetry_error = 0.0`

This rules out current initial deployment as the source of the A/B `FrontCurv` split.

### 2.3 A/B divergence still appears immediately

With the current setting, raw runtime readout still diverges very early:

- first contact: `tick 19`
- first alive lead: `tick 28`
- final outcome in one representative rerun: `A wins 7:0`

More importantly, raw `FrontCurv` diverges almost immediately:

- `tick 0`: A `-0.0662`, B `-0.0668`
- `tick 1`: A `0.1593`, B `-0.0739`

So this is not just a late-battle BRF artifact.

## 3. Root cause A: observer sign asymmetry

The first major issue is in the observer-side geometry metric definition in `test_run/test_run_v1_0.py`.

Relevant lines:

- `test_run/test_run_v1_0.py:1980`
- `test_run/test_run_v1_0.py:2020`
- `test_run/test_run_v1_0.py:2049`
- `test_run/test_run_v1_0.py:2057`
- `test_run/test_run_v1_0.py:2079`
- `test_run/test_run_v1_0.py:2092`

### 3.1 Global axis is reused for both fleets

The observer initializes one global axis from A-centroid to B-centroid:

- `axis_dir = normalize(B_centroid - A_centroid)`

This axis is then reused for both sides.

That is already unsafe for front-geometry readout, because:

- for A, positive projection along `axis_dir` points toward the enemy
- for B, positive projection along `axis_dir` points away from the enemy

### 3.2 `FrontCurv` selects the wrong "front" for B

Current observer logic:

- project each unit onto the single global axis
- sort by `advance_now`
- take `projected_units[-front_group_size:]` as the `front_group`

This works for A, but for B it selects the rear-most band relative to B's own enemy-facing direction.

In other words:

- A-side `front_group` is actually the front
- B-side `front_group` is actually the rear

So B-side `front_curvature_index` is not measuring the same geometric object as A-side.

### 3.3 `center_wing_parallel_share` is also sign-biased

Current observer logic computes:

- `parallel_velocity = velocity dot axis_dir`
- then clips negative values to `0`

See:

- `test_run/test_run_v1_0.py:2079`

For B, movement toward the enemy is usually opposite the global A->B axis, so its forward motion becomes negative and is clipped away.

This makes B-side `center_wing_parallel_share` artificially collapse toward `0`, even when B is advancing coherently toward A.

### 3.4 Derived posture labels inherit this asymmetry

The following downstream observer quantities therefore become unreliable for mirrored A/B comparison:

- `front_curvature_index`
- `center_wing_parallel_share`
- `posture_persistence_time`
- any BRF-level wedge / posture inference derived from them

### 3.5 External recomputation confirms this

When the same tick is recomputed using a fleet-local enemy-facing axis instead of the single global axis:

- A corrected `FrontCurv` stays the same
- B corrected `FrontCurv` flips from the current negative/near-zero artifact to a value that nearly matches A

Representative tick-1 comparison:

- current observer:
  - A `FrontCurv = 0.1950`
  - B `FrontCurv = -0.0659`
- corrected fleet-local axis:
  - A `FrontCurv = 0.1950`
  - B `FrontCurv = 0.1952`

Representative tick-1 `center_wing_parallel_share` comparison:

- current observer:
  - A `-0.0109`
  - B `0.0000`
- corrected fleet-local axis:
  - A `-0.0109`
  - B `-0.0059`

So a large part of the current A/B `FrontCurv` difference is an observer-definition asymmetry.

## 4. Root cause B: runtime sequential-update asymmetry

The second major issue is in the actual movement runtime, not only in the observer layer.

Relevant lines in `runtime/engine_skeleton.py`:

- `runtime/engine_skeleton.py:567`
- `runtime/engine_skeleton.py:597`
- `runtime/engine_skeleton.py:598`
- `runtime/engine_skeleton.py:602`
- `runtime/engine_skeleton.py:615`
- `runtime/engine_skeleton.py:912`

### 4.1 Movement uses `updated_units`, not a pure cross-fleet snapshot

Inside `integrate_movement()`:

- one `snapshot_positions` dictionary is built first
- but fleet movement is then updated in fleet iteration order
- and during that update, both `alive_units` and `enemy_alive_units` are drawn from `updated_units`

This means:

- the first fleet in iteration order is evaluated against old positions
- the second fleet is evaluated after the first fleet has already changed state

So the movement tick is not fully synchronous across fleets.

### 4.2 Mirror symmetry breaks on tick 1

Using the current neutral mirrored state and stepping the engine directly:

- `tick 0 mirror error = 0.0`
- `tick 1 mirror error = 14.2062`

That is too large to be dismissed as plotting noise. The symmetry break happens immediately at the runtime level.

### 4.3 Fleet iteration order shows up in outcome trajectory

An additional control was run by changing only the insertion order of `state.fleets`:

- normal order: `{'A', 'B'}`
- reordered only: `{'B', 'A'}`

No geometry, no personality, and no setting values were changed.

Observed result:

- normal order representative run:
  - first alive lead: `A @ tick 28`
- reordered-only representative run:
  - first alive lead: `B @ tick 28`

This does not mean the full final winner always flips cleanly on every rerun, but it is still strong evidence that fleet iteration order is leaking into runtime behavior.

### 4.4 This is independent of personality asymmetry

This result occurs while:

- personalities are identical
- deployment is geometrically mirrored
- side sizes and aspect ratios are equal

So this is a true low-level runtime asymmetry.

## 5. Additional engineering observations

### 5.1 The current setting is not a pure baseline movement test

The current setting still enables:

- `exp_precontact_centroid_probe`

So this note should not be misread as "baseline v3a is already fully cleared."

However, this does not weaken the main conclusion:

- even in a low-personality, mirrored close-contact test, strong asymmetry survives
- therefore current personality-mechanism experiments should not be trusted as the first interpretation layer

### 5.2 Plot rendering further distorts the visual impression

In `test_run/test_run_v1_0_viz.py`, the displayed `FrontCurv` line is additionally:

- early-baseline centered
- NaN-filled
- smoothed

See:

- `test_run/test_run_v1_0_viz.py:2147`
- `test_run/test_run_v1_0_viz.py:2151`

This is not the root cause, but it can make an already biased raw observer series look even more different on the chart.

## 6. Engineering judgment

Current judgment:

1. The current A/B `FrontCurv` mismatch is not primarily a personality issue.
2. A major part of the visible mismatch comes from observer sign asymmetry.
3. There is also a real runtime asymmetry in movement synchronization.
4. Under the current principle of "neutral mirrored close-contact" diagnostics, these issues must be treated as blockers before further personality-mechanism expansion.

## 7. Implemented test-run mitigations and residual issue

Two test-run-layer mitigations were implemented without touching frozen runtime:

1. Observer-side symmetry correction
   - fleet-local enemy-facing axis is now used for:
     - `front_curvature_index`
     - `center_wing_parallel_share`
     - `posture_persistence_time`

2. Harness-side symmetric movement merge
   - in `TestModeEngineTickSkeleton.step()`
   - movement is now merged from per-fleet "lead-first" passes on the same snapshot
   - this is a test-only attempt to suppress cross-fleet sequential update leakage without editing frozen runtime

### 7.1 What improved

After observer correction:

- tick-1 `FrontCurv` became nearly aligned again:
  - A `0.1572`
  - B `0.1573`

So the original large early A/B `FrontCurv` mismatch was indeed heavily observer-induced.

After symmetric movement merge:

- tick-1 order-sensitive position delta dropped from about `5.56e-4` to about `2.02e-5`

This is roughly a `27x` reduction in first-step order leakage.

### 7.2 What did not fully go away

Even after those two mitigations, full run outcome can still remain fleet-order-sensitive in the close-contact neutral case.

So:

- observer asymmetry was a major problem and is now substantially corrected
- movement sequential leakage was real and has been reduced
- but a residual low-level asymmetry still appears to remain

### 7.3 Additional `center_wing_parallel_share` refinement

The original observer-side `center_wing_parallel_share` was still too fragile after the first sign fix because it relied on:

- instantaneous velocity projection
- a positive-only interpretation inherited from the old sign-biased formulation
- a center/wing split that was not shared consistently across instantaneous and interval readouts

This was refined again in the test-run observer layer:

- `center_wing_parallel_share` now prefers a fleet-local, signed interval readout
- the denominator is `abs(center_total) + abs(wing_total)`
- the same current center/wing partition is used for both the interval and instantaneous fallback paths

This did not require frozen runtime edits.

### 7.4 What the refined `C_W_SPhere` now shows

With the current mirrored neutral close-contact setting, the refined `center_wing_parallel_share` behaves very differently before and after contact.

Representative segmented A/B mean absolute difference:

- `ticks 1-10`: `0.0045`
- `ticks 11-20`: `0.0010`
- `ticks 21-40`: `0.0445`
- `ticks 41-80`: `0.0515`
- `ticks 81-120`: `0.1302`

This matters because:

- before contact, the observer asymmetry is now nearly gone
- the visually obvious remaining asymmetry is mostly a post-contact phenomenon

So the remaining `C_W_SPhere` mismatch should no longer be interpreted primarily as an observer-definition problem.

It is now much more consistent with:

- residual runtime order leakage
- contact-phase interaction asymmetry
- or another post-contact low-level mechanism

rather than continued front-axis sign error.

## 8. New suspect: target-direction tie structure

An additional in-memory experiment was run without committing a code change:

- keep symmetric movement merge enabled
- replace fleet-level `evaluate_target()` direction from:
  - nearest enemy
- to:
  - enemy centroid direction

Observed result:

- with the centroid-target variant, normal fleet order and swapped fleet order converged to the same winner label in the neutral close-contact case

This does not prove that centroid-targeting is the correct permanent design.
But it is strong evidence that:

- current `evaluate_target()` tie structure
- or its nearest-enemy dependence in highly symmetric openings

is likely the next residual asymmetry source after observer correction and movement synchronization mitigation.

However, a second follow-up check also matters:

- switching fleet-level target direction from `nearest enemy` to `enemy centroid`
- did not improve the refined `center_wing_parallel_share`
- and in that readout it actually made A/B mismatch worse

So centroid-target direction should not currently be treated as a general fix.
At most, it remains a clue that target/tie structure is involved in winner-order sensitivity.
It is not yet a validated correction for `C_W_SPhere` symmetry.

Two additional harness-side probes were also tried and did not produce a clean correction:

1. reordering `fleet.unit_ids` before combat using local geometric ranking
2. symmetric two-pass combat merge

These did not produce a stable improvement in the mirrored close-contact case.
So the remaining asymmetry should not currently be treated as something that can be removed by a simple observer-side or shallow harness-side patch.

## 8.1 Post-contact audit result

An additional post-contact audit was run under the same neutral mirrored close-contact setting.

### 8.1.1 `evaluate_target()` tie hypothesis was not confirmed

Two candidate suspicions were checked:

1. fleet-level nearest-enemy ties in `evaluate_target()`
2. per-attacker best-target ties in `resolve_combat()`

Observed result:

- fleet-level nearest-enemy ties exist only as a harmless opening geometry artifact
- per-attacker best-target ties were effectively absent in the audited 120-tick window

Representative readout:

- first contact: `tick 20`
- first fleet-level target tie: `tick 0`
- first combat best-target tie: `none`
- mean combat best-target ties after tick 20:
  - A `0.0`
  - B `0.0`

So the remaining post-contact asymmetry should not currently be explained as a simple target-tie bug.

### 8.1.2 Contact-phase asymmetry still grows after contact

Even without meaningful combat best-target ties:

- contact participation counts diverge after contact
- alive trajectories diverge gradually
- `center_wing_parallel_share` A/B mismatch grows most strongly in the post-contact window

Representative segmented `C_W_SPhere` A/B mean absolute difference:

- `ticks 1-10`: `0.0045`
- `ticks 11-20`: `0.0010`
- `ticks 21-40`: `0.0445`
- `ticks 41-80`: `0.0515`
- `ticks 81-120`: `0.1302`

This supports the judgment that:

- the main observer symmetry issue is already largely corrected
- the remaining problem is a true post-contact low-level asymmetry

### 8.1.3 Additional probes that failed

The following extra probes were tested and did not produce a clean improvement:

1. continuous weighted `center-vs-wing` observer share
2. combat-time geometric reordering of `fleet.unit_ids`
3. symmetric two-pass combat merge

These probes either:

- worsened `FrontCurv`
- worsened `C_W_SPhere`
- or changed outcome without producing a cleaner symmetry result

Therefore no additional correction from these probes was promoted into code.

## 9. Priority recommendation

Before continuing personality-mechanism work, priority should be:

1. Fix observer geometry sign symmetry for mirrored opposing fleets
   - especially `FrontCurv`
   - `center_wing_parallel_share`
   - downstream posture/wedge inference

2. Audit and correct movement synchronization asymmetry
   - ensure cross-fleet movement integrates from the same tick snapshot
   - avoid second-fleet reads against already-updated first-fleet state

3. Audit target-direction symmetry in close-contact mirrored openings
   - especially nearest-enemy tie behavior
   - and whether a more symmetric fleet-level direction surrogate is needed for diagnostics or test mode

4. Only after these are stabilized, resume further personality-mechanism interpretation

## 10. Bottom line

Under the current "all parameters = 5, mirrored geometry, close-contact opening" principle, any strong A/B asymmetry should be interpreted as a low-level blocker first.

That is exactly what this diagnostic window exposed:

- the current observer does not define A/B front geometry symmetrically
- the current runtime movement step does not preserve mirrored fleet symmetry
- after those are partially corrected, residual asymmetry likely remains in target-direction tie structure

Both issues are serious enough that they should be addressed before treating `FrontCurv` differences as evidence about personality authority.

## 11. Diagnostic snapshot preservation and new contact-entry symptom

This setting should now be treated as a reusable low-level validation fixture, not as a transient ad hoc setup.

Saved snapshot files:

- `test_run/test_run_v1_0_neutral_mirrored_close_contact.settings.json`
- `test_run/test_run_v1_0_neutral_mirrored_close_contact.personality_snapshot.json`

This matters because:

- the setting itself is now a recurring validation window for low-level mechanism work
- the archetype file is not canonical and may drift later
- the saved personality snapshot preserves the exact "all 5 vs all 5" state that made this window diagnostically useful

Additional human observation to carry forward:

- around `t = 23..24`, immediately after first contact, the two formations appear to undergo a slight sudden offset from the previously clean mirrored approach

Current engineering interpretation of that observation:

- it is consistent with the current judgment that the remaining asymmetry is primarily a contact-entry / post-contact low-level issue
- it should be treated as an explicit diagnostic symptom in future low-level validation work
- later mechanism changes that claim to improve symmetry should be checked against this exact contact-entry window, not only against end-state outcome or late-battle trajectory

## 12. Contact-entry slice audit around `t ≈ 23..24`

An additional bounded audit was run by splitting each tick into:

1. `evaluate_target()`
2. movement integration
3. `resolve_combat()`

and then inspecting `tick 20..30` under the saved neutral mirrored close-contact fixture.

### 12.1 Earliest strong asymmetry does not first appear as a centroid offset

Fleet lateral centroids remain effectively symmetric through the contact-entry window.

Representative per-side lateral-centroid means:

- `tick 21 move`: A `~ 2.86e-14`, B `~ 3.47e-14`
- `tick 23 move`: A `~ 3.33e-14`, B `~ -1.14e-14`
- `tick 24 move`: A `~ -8.61e-15`, B `~ -1.03e-14`

So the first clearly meaningful residual asymmetry is not a gross center-of-mass side-slip.

### 12.2 The earliest strong divergence appears in fleet-level target surrogate

The earliest large non-mirrored shift appears in `evaluate_target()`, before obvious post-combat casualty asymmetry.

Representative fleet-level target directions:

- `tick 21`
  - A `(0.7678, 0.6406)`
  - B `(-0.7671, -0.6416)`
  - still nearly mirrored

- `tick 22`
  - A `(0.7584, 0.6518)`
  - B `(-0.6210, -0.7838)`
  - no longer close to mirrored

- `tick 23`
  - A `(0.7765, 0.6301)`
  - B `(-0.6180, -0.7862)`

The associated nearest-enemy surrogate also diverges asymmetrically:

- `tick 21`
  - A nearest enemy: `B97`
  - B nearest enemy: `A97`

- `tick 22`
  - A nearest enemy remains `B97`
  - B nearest enemy flips to `A96`

- `tick 23`
  - A still points at `B97`
  - B still points at `A96`

So the first strong contact-entry asymmetry currently looks more like:

- fleet-level nearest-enemy surrogate divergence
- then target-direction divergence

rather than a first-order centroid displacement problem.

### 12.3 Orientation field diverges before large casualty asymmetry

The fleet-average lateral orientation component begins to diverge strongly during contact entry.

Representative movement-phase orientation lateral averages:

- `tick 21`
  - A `-0.1707`
  - B `-0.1846`

- `tick 22`
  - A `-0.1905`
  - B `-0.0061`

- `tick 23`
  - A `-0.2711`
  - B `+0.0092`

- `tick 24`
  - A `-0.5068`
  - B `-0.3922`

This suggests that the human-observed "slight offset" near `t ≈ 23..24` is more plausibly tied to:

- early orientation-field skew
- contact-entry target surrogate divergence
- and only then visible geometry drift

rather than to a large immediate positional jump.

### 12.4 Casualty/engagement asymmetry follows slightly later

Engaged counts remain symmetric at first:

- `tick 21 combat`: A `10`, B `10`
- `tick 22 combat`: A `18`, B `18`

The first clear engaged-count split appears at:

- `tick 23 combat`: A `35`, B `32`

By `tick 24`:

- A `46`
- B `44`

And only later does combat writeback begin to create an additional mirror-error gap between movement-phase and combat-phase state:

- `tick 28`
  - movement mirror error: `6.2230`
  - combat mirror error: `6.3616`

So the current slice ordering is best summarized as:

1. fleet-level target surrogate divergence
2. orientation-field divergence
3. engaged-count / participation divergence
4. later post-combat state divergence

### 12.5 Current engineering judgment for the contact-entry slice

The new audit narrows the contact-entry symptom further:

- the human-observed `t ≈ 23..24` offset is real as a diagnostic symptom
- but it is not best explained as a first-order centroid drift
- the earliest meaningful residual asymmetry currently appears to start in:
  - fleet-level nearest-enemy target surrogate
  - target-direction carry-through
  - orientation-field skew during contact entry

This does not yet prove a single bug.
But it materially reduces the search space for the next low-level audit stage.

### 12.6 Additional surrogate comparison: `nearest enemy` vs `enemy centroid`

One additional in-memory comparison was run at the same low-level slice:

- keep the current mirrored close-contact fixture
- keep the same harness-side symmetric movement merge
- change only the fleet-level target surrogate inside `evaluate_target()` from:
  - `nearest enemy`
- to:
  - `enemy centroid`

This was not promoted into code.
It was used only as a diagnostic comparison.

Observed effect in the contact-entry window:

- with `nearest enemy`, fleet-level `target_direction` can lose mirror symmetry very early
- with `enemy centroid`, `target_direction` stays almost exactly mirrored through the same early window
- the fleet-average lateral orientation skew is also smaller and cleaner in that window

Representative comparison:

- `nearest enemy`
  - `tick 21`
    - A target dir `(0.7107, 0.7035)`
    - B target dir `(-0.6766, -0.7364)`
  - movement-phase lateral orientation:
    - A `-0.0034`
    - B `+0.0449`

- `enemy centroid`
  - `tick 21`
    - A target dir `(0.7068, 0.7074)`
    - B target dir `(-0.7068, -0.7074)`
  - movement-phase lateral orientation:
    - A `-0.0166`
    - B `-0.0120`

- `enemy centroid`
  - `tick 22`
    - A target dir `(0.7067, 0.7075)`
    - B target dir `(-0.7067, -0.7075)`
  - movement-phase lateral orientation:
    - A `-0.0071`
    - B `+0.0071`

Engineering interpretation:

- this does not validate `enemy centroid` as the permanent design
- it does strengthen the suspicion that the current `nearest-enemy` fleet-level surrogate is a major trigger for early contact-entry asymmetry
- in other words, `nearest-enemy` currently looks less like a neutral diagnostic direction surrogate and more like an asymmetry amplifier in mirrored close-contact openings

So the current priority should remain:

- audit the fleet-level direction surrogate itself
- then audit how that surrogate is carried into movement/orientation during contact entry

before returning to broader mechanism interpretation.

### 12.7 `nearest-enemy` looks numerically fragile in mirrored openings

An additional bounded diagnostic checked the local candidate set behind the fleet-level surrogate itself.

Under the mirrored same-force opening, the top few enemy candidates around the fleet centroid are often separated by only a very thin distance margin.

Representative nearest-candidate margins:

- `tick 21`
  - A margin between rank-1 and rank-2 enemy: `~ 0.0070`
  - B margin between rank-1 and rank-2 enemy: `~ 0.0248`

- `tick 22`
  - A margin: `~ 0.0562`
  - B margin: `~ 0.0203`

- `tick 23`
  - A margin: `~ 0.0668`
  - B margin: `~ 0.1081`

- `tick 24`
  - A margin: `~ 0.1206`
  - B margin: `~ 0.0687`

These are very small discriminators for a fleet-level direction surrogate.

Engineering interpretation:

- `nearest-enemy` is acting like a single-point selector on top of a nearly tied local enemy set
- in a mirrored close-contact opening, that makes it structurally sensitive to small geometric perturbations
- so even when there is no explicit target-tie bug in combat targeting, the fleet-level surrogate itself can still become an asymmetry amplifier

### 12.8 Smooth local surrogates remain more neutral than raw `nearest-enemy`

Another in-memory comparison inserted two smoother local surrogates:

- `nearest-3 centroid`
- `nearest-5 centroid`

These were compared against:

- raw `nearest-enemy`
- global `enemy centroid`

Representative `tick 21` comparison:

- A
  - `nearest-enemy`: `(0.7107, 0.7035)`
  - `nearest-3 centroid`: `(0.6971, 0.7170)`
  - `nearest-5 centroid`: `(0.7042, 0.7100)`
  - `enemy centroid`: `(0.7075, 0.7067)`

- B
  - `nearest-enemy`: `(-0.6766, -0.7364)`
  - `nearest-3 centroid`: `(-0.7065, -0.7077)`
  - `nearest-5 centroid`: `(-0.7043, -0.7099)`
  - `enemy centroid`: `(-0.7075, -0.7067)`

This pattern persisted through the same early window:

- `nearest-enemy` can swing away from the mirrored centroid direction
- `nearest-3` / `nearest-5` remain much closer to mirrored local neutrality

Engineering interpretation:

- the current problem is not just that `enemy centroid` is smoother
- it is more specifically that a single-point nearest-unit selector is too sharp for the current mirrored contact-entry diagnostic role
- local smooth surrogates appear to preserve more of the local-contact character while avoiding some of the asymmetry amplification of raw `nearest-enemy`

This still does **not** authorize a code change by itself.
But it sharpens the next audit question:

- whether fleet-level direction for mirrored diagnostics should stay as a single nearest-unit selector
- or whether a smoother local surrogate is the more neutral low-level diagnostic reference

### 12.9 Surrogate family comparison under the active close-contact fixture

A wider in-memory comparison was then run on the active fixture itself:

- same-force
- same all-5 personalities
- mirrored close-contact opening
- same harness-side symmetric movement merge

Compared surrogate families:

- `nearest-1` (current raw `nearest-enemy`)
- `nearest-3 centroid`
- `nearest-5 centroid`
- `enemy centroid`

Tracked summary readouts:

- average target-direction mirror error over `ticks 1..24`
- average orientation lateral-gap over `ticks 21..24`
- average movement-phase mirror error over `ticks 21..24`
- first contact tick
- first engaged-count split tick

Representative summary:

- `nearest-1`
  - avg target-direction symmetry error: `0.0315`
  - avg orientation lateral-gap (`ticks 21..24`): `0.1741`
  - avg movement mirror error (`ticks 21..24`): `4.8920`
  - first contact: `tick 21`
  - first engaged split: `tick 22`

- `nearest-3 centroid`
  - avg target-direction symmetry error: `0.0393`
  - avg orientation lateral-gap: `0.1382`
  - avg movement mirror error: `5.2076`
  - first contact: `tick 21`
  - first engaged split: `tick 22`

- `nearest-5 centroid`
  - avg target-direction symmetry error: `0.0090`
  - avg orientation lateral-gap: `0.0384`
  - avg movement mirror error: `5.0525`
  - first contact: `tick 21`
  - first engaged split: `tick 24`

- `enemy centroid`
  - avg target-direction symmetry error: `0.0000`
  - avg orientation lateral-gap: `0.0195`
  - avg movement mirror error: `5.0029`
  - first contact: `tick 20`
  - first engaged split: `tick 21`

Engineering interpretation:

- `nearest-1` is clearly not the cleanest mirrored diagnostic surrogate
- `nearest-3` is not a consistent improvement and should not currently be preferred
- `nearest-5` is the strongest local smooth surrogate among the tested local families
- `enemy centroid` is the cleanest on pure target-direction symmetry, but it also changes contact timing and may be too global to serve as the best local-contact diagnostic surrogate

So the current bounded judgment is:

- raw `nearest-enemy` looks too sharp for mirrored contact-entry diagnostics
- a smoother local surrogate appears more promising than the current single-point selector
- among the tested local candidates, `nearest-5 centroid` is currently the most plausible next diagnostic comparator

This is still a tracing result, not an implementation instruction.

### 12.10 Long-range mirrored approach reveals `FrontCurv` observer sensitivity

After the pre-TL substrate selector was made setting-selectable in `test_run`, the active fixture was temporarily switched from mirrored close-contact opening to the longer-range mirrored diagonal opening:

- all-5 personalities
- same-force mirrored geometry
- `A @ [10,10], 45°`
- `B @ [190,190], 225°`
- current default pre-TL substrate: `nearest5_centroid`

A bounded re-run then showed:

- `first_contact_tick = 115`
- `alive @ tick 50 = 100 / 100`
- `alive @ tick 120 = 100 / 100`

So the visible `FrontCurv` mismatch in the first `50` ticks is not a contact-phase amplification artifact.
It is a **pure pre-contact observer/readout issue**.

Representative current-default readout:

- `frontcurve_diff_t1_20 = 0.2219`
- `frontcurve_diff_t21_40 = 0.0691`
- `frontcurve_diff_t41_50 = 0.0582`

But the corresponding `C_W_SPhere` gaps remain very small:

- `cws_diff_t1_20 = 0.0056`
- `cws_diff_t21_40 = 0.0035`
- `cws_diff_t41_50 = 0.0015`

Engineering interpretation:

- wide movement/posture symmetry is still mostly intact in this long-range mirrored case
- the stronger mismatch is concentrated in the `FrontCurv` observer itself
- this means current pre-contact `FrontCurv` is still too sensitive to early ranking / band-selection changes, even after the earlier local-axis symmetry corrections

This was checked across the three retained pre-TL substrates:

- `nearest5_centroid`
  - `fc 1..20 = 0.2219`
  - `fc 21..50 = 0.0655`
  - `cws 1..20 = 0.0056`
  - `cws 21..50 = 0.0028`

- `weighted_local`
  - `fc 1..20 = 0.1262`
  - `fc 21..50 = 0.1360`
  - `cws 1..20 = 0.0071`
  - `cws 21..50 = 0.0057`

- `local_cluster`
  - `fc 1..20 = 0.2214`
  - `fc 21..50 = 0.2770`
  - `cws 1..20 = 0.0054`
  - `cws 21..50 = 0.0025`

Engineering interpretation:

- the new long-range mismatch is not well explained as "the default substrate is wrong"
- all three retained substrates still show much larger `FrontCurv` mismatch than `C_W_SPhere` mismatch in the pre-contact window
- therefore the dominant new suspicion is:
  - **`FrontCurv` front-band construction is itself too sensitive in long-range mirrored approach**

The current implementation defines `FrontCurv` using:

- the top `30%` of units by projected advance
- then splitting that front group by width rank into center vs wing bands

This likely remains fragile when:

- a clean physical front has not yet formed
- projected advance ranks are still very shallow and easily permuted
- small unit-order changes move units across the observer-defined "front 30%" boundary

So the next low-level tracing question is no longer only about fleet-level target surrogate.
It is also:

- whether `FrontCurv` should continue to use the current fixed front-band construction during long-range pre-contact mirrored approach

This is still an observer-audit conclusion, not yet an implementation instruction.

### 12.11 Boundary on/off audit shows boundary is not the main current driver

A bounded boundary audit was then run under the current mirrored diagnostic assumptions:

- same-force
- all-5 personalities
- mirrored geometry
- default pre-TL substrate fixed to `nearest5_centroid`
- `6` representative fixtures
- `boundary_enabled = false` vs `true`

Fixtures:

- `long_10_100`
- `mid_30_100`
- `mid_50_50`
- `mid_50_100`
- `mid_50_150`
- `close_90_100`

Aggregate readout:

- `boundary = false`
  - `mean fc1_20 = 0.1678`
  - `mean fc21_50 = 0.1865`
  - `mean fc51_120 = 0.3341`
  - `mean cws1_20 = 0.0069`
  - `mean cws21_50 = 0.0262`
  - `mean remaining gap = 1.7778%`

- `boundary = true`
  - `mean fc1_20 = 0.1654`
  - `mean fc21_50 = 0.1831`
  - `mean fc51_120 = 0.3247`
  - `mean cws1_20 = 0.0065`
  - `mean cws21_50 = 0.0261`
  - `mean remaining gap = 1.7778%`

The decisive point is that only one fixture changed materially:

- `long_10_100`

In the other five fixtures:

- `mid_30_100`
- `mid_50_50`
- `mid_50_100`
- `mid_50_150`
- `close_90_100`

the `boundary` switch produced effectively identical results across:

- contact timing
- `FrontCurv`
- `C_W_SPhere`
- final remaining-force gap

The one meaningful exception was the far-corner long-range fixture:

- `long_10_100`
  - `fc1_20`: `0.2360 -> 0.2219`
  - `fc21_50`: `0.0859 -> 0.0655`
  - `fc51_120`: `0.2106 -> 0.1542`
  - `cws1_20`: `0.0080 -> 0.0056`
  - `first_contact_tick`: `114 -> 115`

Engineering interpretation:

- `boundary` is **not** the main driver of the current mirrored asymmetry line
- it does **not** explain the close-contact and mid-range residual asymmetry being audited here
- it only becomes materially active in the far-corner long-range fixture, where the fleet is interacting with map-edge geometry during the long diagonal approach

So the current low-level reading should be tightened to:

- `boundary` is a secondary geometric intervention variable
- relevant mainly for far-corner long-range observer audits
- not a primary suspect for the current close-contact / mid-range mirrored asymmetry problem

Practical implication:

- the current mirrored close-contact fixture can keep its present `boundary` setting without distorting the main conclusion
- but future long-range mirrored observer audits should prefer `boundary_enabled = false` by default, to avoid mixing boundary-side shaping into the observer diagnosis
