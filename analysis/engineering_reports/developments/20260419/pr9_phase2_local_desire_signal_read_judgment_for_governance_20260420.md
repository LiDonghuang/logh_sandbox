## PR9 Phase II - Local Desire Signal Read Judgment for Governance

Date: 2026-04-20  
Scope: document-only review of `local_desire` signal read on the maintained path  
Status: engineering judgment note, no implementation in this round

### 0. Active owner/path under review

Current `local_desire` owner/path is:

- `runtime/engine_skeleton.py`
  - `_compute_unit_desire_by_unit(...)`

Current same-tick target source remains:

- `_compute_unit_intent_target_by_unit(...)`
- `_select_targets_same_tick(...)`

Current heading-side local bias is driven by:

- `front_bearing_need`
  - derived from `fleet front -> selected target bearing`
- `heading_turn_need`
  - derived from `unit facing -> selected target bearing`
- `local_heading_bias_weight = heading_bias_cap * near_contact_gate * front_bearing_need * heading_turn_need`

Current speed-side brake is driven by:

- `speed_turn_need = heading_turn_need^2`
- `desired_speed_scale = 1 - speed_brake_strength * near_contact_gate * speed_turn_need`

### 1. One-sentence conclusion

The current main problem is **signal-domain collapse**, not merely cold tuning:
the maintained `selected_target_by_unit` path is already constrained by the
upstream fire cone around current unit facing, so the downstream
`unit facing -> selected target bearing` signal is too narrow to serve as the
primary activation read for heading-side `local_desire`.

### 2. Evidence from the maintained battle baselines

Engineering measured target-line geometry directly from the current Phase II
primary battle baselines.

For `battle_36v36`:

- samples: `4088`
- `unit facing -> selected target bearing`
  - mean angle: `17.0902 deg`
  - p95: `29.1936 deg`
  - max: `29.9988 deg`
- `fleet front -> selected target bearing`
  - mean angle: `57.8964 deg`
  - p95: `144.5346 deg`
  - max: `179.7473 deg`
- `near_contact_gate > 0` ratio: `0.093933`
- current `heading_turn_need > 0` ratio: `0.0`

For `battle_100v100`:

- samples: `11092`
- `unit facing -> selected target bearing`
  - mean angle: `19.1211 deg`
  - p95: `29.3863 deg`
  - max: `29.9994 deg`
- `fleet front -> selected target bearing`
  - mean angle: `75.7770 deg`
  - p95: `166.5886 deg`
  - max: `179.9925 deg`
- `near_contact_gate > 0` ratio: `0.038406`
- current `heading_turn_need > 0` ratio: `0.0`

Engineering read of these numbers:

- the current `unit facing -> selected target bearing` domain is effectively
  capped at the `30 deg` fire cone
- under current `turn_need_raw = (1 - cos(theta)) / 2` and
  `turn_need_onset = 0.45`, that domain never reaches nonzero
  `heading_turn_need`
- meanwhile, `fleet front -> selected target bearing` remains broad and
  informative on the same maintained path
- `near_contact_gate` is also conservative, but it is secondary: even before
  proximity becomes limiting, the current heading-side turn signal has already
  collapsed to zero

### 3. Core answer to question 1

Main cause ranking:

1. **selected-target-driven signal domain collapse**
2. conservative / late `near_contact_gate`
3. `turn_need_onset` calibration against the collapsed domain
4. `heading_bias_cap` and speed brake magnitude

Engineering does **not** read the current problem as “just turn the knobs
hotter.”

Reason:

- if the primary signal itself is bounded by the upstream fire cone, raising cap
  or onset alone is only compensating for the wrong read
- the present onset looks too cold mainly because it is being applied on a
  domain that has already been compressed to about `0..30 deg`

### 4. Minimal acceptable signal read

Engineering recommends a split read while keeping one same-tick target source.

Heading-side local bias should primarily read:

- `fleet front -> selected target bearing`

Reason:

- heading bias is about how much per-unit desire should deviate from fleet base
  motion / front-axis intent
- this signal remains broad and meaningful even after upstream target selection
  has already been cone-filtered around current unit facing
- it directly answers the local geometry question: “relative to the current
  fleet front, how lateral is the chosen firing opportunity?”

Speed-side brake-only adaptation should primarily read:

- `unit facing -> selected target bearing`

Reason:

- brake-only adaptation is about actual turn burden of the current unit, not
  about fleet-front geometry
- if the unit is already nose-aligned enough for the selected target, speed
  should not brake simply because the fleet front is skewed
- speed-side should therefore stay later, weaker, and more conservative

Minimal combined read:

- heading-side:
  - primary angular signal = `fleet front -> selected target bearing`
- speed-side:
  - primary angular signal = `unit facing -> selected target bearing`
- shared target identity:
  - still `selected_target_by_unit`
- shared proximity read may remain, but it should not be mistaken for the main
  fix

### 5. Single target source: yes or no

Engineering answer: **yes**

`selected_target_by_unit` should remain the only target source for the next
`local_desire` correction.

Reason:

- target identity is not the missing piece
- the current failure is in the geometry read derived from that target identity
- a second target-like carrier would introduce new owner competition without
  solving the core collapse
- the current same-tick target source is already sufficient to support:
  - heading-side fleet-front-relative bias
  - speed-side facing-relative brake

Engineering does **not** currently see a need for:

- guide target
- parallel target
- secondary maneuver target

### 6. Heading-side and speed-side: shared or split

Engineering answer: **split**

They should not continue to share the same primary activation signal.

Minimal split:

- heading-side
  - earlier
  - softer
  - continuous
  - primarily reads `fleet front -> selected target bearing`
- speed-side
  - later
  - weaker
  - brake-only
  - primarily reads `unit facing -> selected target bearing`

This keeps the currently accepted separation intact:

- fleet front axis != unit facing != actual velocity
- target selection != combat execution
- local desire adaptation != Formation / FR owner flow-back

### 7. Keep vs replace

Retain:

- `local_desire` carrier itself
- owner/path in `_compute_unit_desire_by_unit(...)`
- output shape:
  - `desired_heading_xy`
  - `desired_speed_scale`
- same-tick single target source:
  - `selected_target_by_unit`
- speed-side brake-only posture

Replace:

- the current heading-side primary activation read
  - do not let `unit facing -> selected target bearing` remain the main heading
    activation signal
- the current shared turn-need dominance
  - heading-side and speed-side should no longer be driven mainly by the same
    angular read
- the current interpretation that “cold tuning” is the main issue
  - the first correction should be signal-read realignment, not just knob
    heating

Likely keep for now, then review later:

- `near_contact_gate`
- cap / strength regime tuning

Reason:

- they are not the best first answer to the present collapse
- they become meaningful to retune only after the signal read is no longer
  self-compressed

### 8. Minimal proposal theme if a later implementation proposal is requested

`pr9_phase2_local_desire_signal_read_realignment_bounded_implementation_proposal_YYYYMMDD.md`

Theme only:

- realign heading-side and speed-side local-desire signal reads while keeping
  the existing carrier, owner/path, and single target source
