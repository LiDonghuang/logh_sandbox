## PR9 Phase II - Local Desire Standoff Rebalance Human-Observation Addendum

Date: 2026-04-21  
Scope: addendum analysis only for the experimental `local_desire` branch under `36v36`  
Status: document-only; no runtime changes in this note

### 1. One-sentence conclusion

Human observation is correct: with `local_desire` experimental branch enabled,
the current controller may look slightly tidier than the older live
realignment in some windows, but it still does **not** preserve fleet-level
hold, still allows first-contact overrun, still sustains dog-fight behavior too
long, and still amplifies battle asymmetry beyond the temporary working anchor.

### 2. Observation posture and exact switch

This addendum assumes the experimental branch was enabled through the existing
runtime-facing switch:

- [test_run/test_run_v1_0.runtime.settings.json](E:/logh_sandbox/test_run/test_run_v1_0.runtime.settings.json:65)
  - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled = true`

That is the correct switch for observing the current experimental
`local_desire` family.

Runtime wiring for that switch:

- [test_run/settings_accessor.py](E:/logh_sandbox/test_run/settings_accessor.py:19)
- [test_run/test_run_execution.py](E:/logh_sandbox/test_run/test_run_execution.py:656)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1676)

This note is limited to:

- experimental `battle_36v36`
- same active owner/path:
  - [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1662)
    `EngineTickSkeleton._compute_unit_desire_by_unit(...)`

This note does **not** reopen:

- target-selection ownership
- `resolve_combat(...)` ownership
- mode / retreat / persistent memory
- locomotion rewrite
- module split
- combat-coupling redesign

### 3. Human observations and engineering judgment

#### 3.1 Observation 1

Human observation:

- at first contact, front-rank overlap / overrun still exists
- current mechanism still breaks the fleet-level hold read

Engineering judgment:

- confirmed

What the numbers show in `battle_36v36`:

- temporary working anchor:
  - ticks with `front_gap < 0`: `9`
  - first negative `front_gap`: tick `74`
  - negative `front_gap` window ends by tick `82`
- current experimental branch:
  - ticks with `front_gap < 0`: `34`
  - first negative `front_gap`: tick `70`
  - negative `front_gap` persists as late as ticks:
    - `349`
    - `350`
    - `376`
    - `402`

Important first-contact samples:

- tick `70`
  - anchor:
    - `front_gap_A = 4.579634`
  - current:
    - `front_gap_A = -0.522338`
    - `in_contact_count = 72`
- tick `74`
  - anchor:
    - `front_gap_A = -1.958681`
  - current:
    - `front_gap_A = -2.885867`

Read:

- overlap is not only still present
- it starts earlier and lasts longer than the temporary working anchor
- therefore the current experimental branch does still violate the fleet-level
  hold read in the first-contact regime

#### 3.2 Observation 2

Human observation:

- dog-fight behavior still remains significant
- it may look a bit tidier, but not decisively better

Engineering judgment:

- confirmed

The part that may look "a bit tidier" is real:

- in window `61-90`, average contact is lower than the anchor
  - anchor mean contact: `36.10`
  - current mean contact: `32.40`
- in the same window, average front gap is wider
  - anchor mean front gap: `3.81`
  - current mean front gap: `5.86`

So the human sense that the battle can look slightly more organized in some
early windows is consistent with the data.

But the overall battle class does **not** change:

- ticks `>= 180` with `in_contact_count > 10`
  - anchor: `5`
  - current: `106`
- ticks `>= 180` with `front_gap < 2`
  - anchor: `0`
  - current: `53`

Late sticky-contact samples:

- tick `205`
  - anchor:
    - `in_contact_count = 1`
    - `front_gap_A = 13.508874`
  - current:
    - `in_contact_count = 22`
    - `front_gap_A = 6.400445`
- tick `240`
  - anchor:
    - `in_contact_count = 1`
    - `front_gap_A = 11.688423`
  - current:
    - `in_contact_count = 5`
    - `front_gap_A = -0.445882`
- tick `260`
  - anchor:
    - `in_contact_count = 5`
  - current:
    - `in_contact_count = 23`

Read:

- the current branch can look more orderly in some early phases
- but the controller still allows too much long-tail close combat
- that means the visual class remains "persistent dog-fight / sticky contact,"
  not "fleet fronts with small local shaping"

#### 3.3 Observation 3

Human observation:

- late asymmetry still expands to about `20 : 24`

Engineering judgment:

- confirmed in magnitude

Current re-check result:

- final alive:
  - `A = 24`
  - `B = 20`
  - absolute gap = `4`

Temporary working anchor:

- final alive:
  - `A = 28`
  - `B = 27`
  - absolute gap = `1`

Asymmetry threshold crossings:

- current experimental branch:
  - first alive-gap `>= 1`: tick `131`
  - first alive-gap `>= 2`: tick `288`
  - first alive-gap `>= 3`: tick `292`
  - first alive-gap `>= 4`: tick `293`
- temporary working anchor:
  - first alive-gap `>= 1`: tick `116`
  - first alive-gap `>= 2`: tick `133`
  - first alive-gap `>= 3`: tick `141`
  - alive-gap `>= 4`: never occurs

Read:

- the current branch does not merely drift a little
- it materially widens the late battle asymmetry envelope relative to the
  temporary working anchor

### 4. Mechanism explanation in plain language

Plain-language read first:

- the new controller does give Units a more real local steering response
- but it still does not give them a strong enough "do not keep pushing through
  the front" restraint
- so Units are allowed to peel, overlap, and keep circling too long
- once that happens, the battle stops reading like two fronts keeping distance
  and starts reading like many sticky local fights

### 5. Why fleet-level hold is still being broken

#### 5.1 `battle_relation_gap_current` only acts as permission, not as hard restraint

Current active heading-side path:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1845)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1867)

What it does:

- `battle_relation_gap_current` opens or closes a `standoff_envelope`
- that envelope then scales heading-side bias permission

What it does **not** do:

- it does not actively push Units back toward line
- it does not hard-stop forward overrun
- it does not override locomotion with a "hold the strip" command

Consequence:

- fleet-level hold remains the higher-level owner
- but `local_desire` is still strong enough to erode that hold at the unit edge
  before any hard corrective force appears

#### 5.2 Speed restraint still keys off turn-need, not off standoff violation itself

Current speed-side path:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1829)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1873)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1912)

Current logic shape:

- brake-only
- but brake strength still depends on:
  - `speed_turn_need`
  - which comes from `unit facing -> selected target bearing`

This means:

- if a Unit has already turned into its selected target,
  `speed_turn_need` collapses
- once that happens, the brake weakens
- and it weakens even if the fleet relation is already too tight

This is the most important structural mismatch in the current controller.

Shortest version:

- heading freedom is allowed by fleet-relation context
- but speed restraint is still released by unit-local facing success
- so the controller becomes too permissive exactly when it should stay strict

#### 5.3 `near_contact_gate` is no longer the only problem, but it still helps localize the failure into the worst zone

Current contact gate constants:

- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1711)
- [runtime/engine_skeleton.py](E:/logh_sandbox/runtime/engine_skeleton.py:1712)

With maintained `attack_range = 20.0`, this means:

- gate starts around distance `7.0`
- gate is fully on around distance `4.0`

So the experimental branch is still most active exactly where:

- overrun matters most
- overlap starts
- return-to-line becomes hardest

That is not the sole root cause now, but it still concentrates controller
action in the most dangerous regime.

#### 5.4 There is still no active "back out / restore line" mechanism

Current branch still has:

- no explicit reverse / back-out term
- no standoff-violation-led speed clamp independent of turn alignment
- no direct front-gap restoration term

Therefore:

- once overlap happens
- the system has only weak tools to unwind it
- and the observed result is late sticky contact plus rotational-collapse-like
  persistence

### 6. Why asymmetry still grows

This is not best read as "random chaos" or "personality doctrine" in the
current maintained experiment.

The more useful engineering read is:

1. selected-target and contact geometry are same-tick and order-sensitive
2. one side gains slightly better local geometry first
3. heading-side bias gives that side real steering opportunity
4. once Units turn into target, speed-side restraint relaxes too early
5. that side keeps more local fire links alive
6. the small lead compounds into a wider alive-gap later

Why this matters:

- the asymmetry is not only a cosmetic left/right issue
- it is evidence that the controller still has positive feedback without
  adequate fleet-level damping

### 7. Engineering interpretation of the current slice

What the slice **did** achieve:

- it proved that heading-side standoff-aware gating is a real seam
- it reduced some average early contact pressure
- it can make parts of the battle look slightly tidier than the older live
  realignment family

What it did **not** achieve:

- it did not restore fleet-level hold in the first-contact regime
- it did not stop deep overlap early enough
- it did not suppress late sticky contact strongly enough
- it did not keep asymmetry inside the temporary-anchor envelope

So the correct current classification is:

- useful experimental seam result
- not a maintained-ready battle controller

### 8. Governance-facing judgment

Shortest judgment for governance:

- Human observations are valid.
- The current experimental branch remains structurally too permissive.
- The main remaining problem is not "more tuning on the same formulas."
- The deeper issue is that local heading freedom is now partially
  standoff-aware, but local speed restraint is still not standoff-violation-led
  strongly enough to preserve fleet-level hold once contact starts.

Explicitly out of scope for this addendum:

- mode system
- retreat activation
- second target owner
- persistent target memory
- broad locomotion rewrite
- module split
- combat-coupling redesign
