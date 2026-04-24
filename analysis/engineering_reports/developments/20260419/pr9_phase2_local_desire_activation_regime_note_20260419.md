# PR9 Phase II Local Desire Activation Regime Note 20260419

Status: note only
Date: 2026-04-19
Scope: post-fourth-slice document-first continuation read
Authority: engineering-side design/review note for Human + governance review before any fifth runtime slice

## Purpose

This note records the next smallest unresolved seam after the accepted fourth
bounded slice.

Current accepted read is now:

- same-tick target identity exists
- same-tick desire carrier exists
- same-tick local desire content is no longer placeholder-only
- the fourth slice remains bounded and non-doctrinal

The next seam is no longer whether local desire adaptation exists at all.
It is the activation regime of that adaptation.

This note does not implement anything.
This note does not authorize a fifth slice.

## Input Anchors

- [analysis/engineering_reports/developments/20260419/pr9_phase2_local_desire_adaptation_fourth_bounded_implementation_report_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_local_desire_adaptation_fourth_bounded_implementation_report_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_fourth_slice_bounded_implementation_proposal_local_desire_adaptation_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_fourth_slice_bounded_implementation_proposal_local_desire_adaptation_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_combat_adaptation_seam_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_combat_adaptation_seam_note_20260419.md)
- [analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json](E:/logh_sandbox/analysis/reference_notes/eng_dev_v2_1_formation_only_a4b5ce2b7dba_dirty_baseline_capture_manifest_20260419.json)

## Assumptions

1. The accepted fourth slice is the current active starting point.
2. The current local desire regime in maintained battle baselines remains very conservative.
3. The next honest question is regime calibration, not owner reroot, schema work, or doctrine expansion.

## Verified Current Active Regime

Current active truth in [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py):

- local regime constants live inside `_compute_unit_desire_by_unit(...)` at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1672)
- current bounded activation terms are:
  - `LOCAL_DESIRE_HEADING_BIAS_MAX = 0.03`
  - `LOCAL_DESIRE_NEAR_CONTACT_GATE_START_RATIO = 0.35`
  - `LOCAL_DESIRE_NEAR_CONTACT_GATE_FULL_RATIO = 0.20`
  - `LOCAL_DESIRE_TURN_NEED_BRAKE_START = 0.65`
  - `LOCAL_DESIRE_SPEED_BRAKE_STRENGTH = 0.03`
  - `LOCAL_DESIRE_SPEED_BRAKE_FLOOR = 0.97`
- near-contact gating is computed from selected-target distance at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1727)
- turn-need weighting is computed from target bearing vs current unit facing at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1774)
- heading bias is bounded by `local_heading_bias_weight` at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1787)
- brake-only speed adaptation is applied at
  [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1805)

Accepted fourth-slice evidence already shows:

- controlled local geometry can produce non-placeholder desire output
- maintained battle / neutral primary baselines still match on behavior-bearing surfaces

Shortest plain-language read:

- the seam exists
- the regime is still intentionally cold

## Is The Current Near-Contact Gate Proof-Of-Seam Or Maintained-Behavior Bearing?

Current engineering read:

- the present near-contact gate should be read primarily as a proof-of-seam gate
- not yet as a meaningfully behavior-bearing maintained battle regime

Reason:

- in controlled local geometry, the helper does produce real desire adaptation
- in maintained battle baselines, the fourth slice preserved the accepted behavioral window almost exactly

So the current fourth-slice regime proves:

- the seam is technically live
- the output shape is viable

But it does **not** yet prove:

- that the maintained battle regime should now rely on this activation range and weighting as its long-term operating point

## Main Unresolved Seam

The current main unresolved seam is:

- whether local desire adaptation should remain a near-dormant proof-of-seam regime
- or become a modestly behavior-bearing maintained battle regime

That question breaks down into four smaller activation-regime questions:

1. activation range / proximity regime
2. turn-need weighting regime
3. heading-bias cap regime
4. brake-strength / speed-floor regime

## 1. Activation Range / Proximity Regime

Current read:

- activation begins only deep inside near-contact
- this keeps maintained battle behavior almost unchanged

The next honest activation question is:

- should the gate remain this deep
- or should it open slightly earlier while still remaining smooth and conservative

Smallest honest next regime decision:

- choose whether the gate is only a seam-proof window
- or a slightly earlier pre-contact / edge-of-contact window

This is a regime question, not a doctrine question.

## 2. Turn-Need Weighting Regime

Current read:

- turn need only matters after a fairly high threshold
- this makes the slice activate only for strongly misaligned units

The next honest question is:

- should unit-facing misalignment remain almost binary and late
- or should it become a smoother, earlier weighting curve

This is the smallest honest next regime seam because it controls:

- how much local reorientation pressure exists before contact geometry is fully mature

without changing owner boundaries.

## 3. Heading-Bias Cap Regime

Current read:

- heading bias cap is explicitly small
- target bearing does not replace fleet base heading

The next honest question is:

- whether `0.03`-scale maximum bias is intentionally just a proof-of-seam cap
- or whether maintained battle behavior eventually wants a slightly larger but still bounded cap

Key boundary:

- cap tuning remains a bounded local-adaptation question
- it must not become a covert route to full target-owned heading replacement

## 4. Brake-Strength / Speed-Floor Regime

Current read:

- brake is shallow
- floor remains high
- speed adaptation is difficult to notice in maintained baseline scenarios

The next honest question is:

- whether brake-only local speed adaptation should remain almost invisible
- or become modestly behavior-bearing under strong turn need near contact

This remains a regime seam only if:

- it stays brake-only
- it stays bounded
- it does not grow into boost / lunge / sprint families

## How To Keep The Regime Continuous And Bounded

Any future activation tuning should preserve:

- smooth / monotonic gating
- no visible chatter
- no flip-flop threshold behavior

Preferred engineering read:

- keep activation as continuous ramps, not discrete stage jumps
- keep turn-need weighting monotonic in misalignment
- keep bias caps explicit and small
- keep speed floor explicit and high enough to avoid hard stop-like artifacts
- avoid paired thresholds that can toggle on adjacent ticks with tiny geometric noise

The most honest way to remain small is:

- change curves and caps
- not change state structure

## Separation That Must Stay Intact

Any next regime work must preserve the already accepted separation:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- local desire adaptation != Formation / FR owner flow-back

Meaning:

- fleet front remains reference geometry, not local combat owner
- unit facing remains realized low-level heading, not the same as desired heading input
- actual velocity remains the final low-level motion result
- local desire adaptation remains a pre-realization bias layer only

## Why The Next Seam Is Still Smaller Than Larger Mechanism Waves

The activation-regime seam still remains smaller than:

- mode system introduction
- retreat activation
- broad locomotion redesign
- doctrine-scale combat-adaptation family

because it would only decide:

- when the existing bounded seam should activate
- how strongly it should activate
- how smoothly it should ramp

It would not decide:

- a new tactical vocabulary
- a new planner
- a new locomotion owner
- a new combat owner
- a new memory system

Shortest plain-language read:

- next seam is regime shaping of an already-bounded seam
- not expansion into a new subsystem family

## Explicitly Out Of Scope

Still not authorized:

- mode implementation
- retreat activation
- persistent target memory
- broad locomotion redesign
- Formation / FR combat-adaptation owner flow-back
- harness-owned doctrine growth
- automatic opening of slice five before governance review

Also out of scope for this note:

- exact formula edits
- runtime parameter introduction
- new signal catalog growth
- cross-file implementation planning

## Bottom Line

The current main unresolved seam is:

- whether local desire adaptation should remain primarily proof-of-seam, or become modestly behavior-bearing in maintained battle scenarios through a revised activation regime

The right next question is not a new mechanism family.
It is only the regime of:

- proximity activation
- turn-need weighting
- heading-bias cap
- brake-strength / speed-floor

within the already accepted bounded local desire seam.
