## PR9 Phase II - 36v36 Observation Read and Back-Off Governance Addendum

Date: 2026-04-22  
Scope: document-only governance addendum; no new implementation in this note  
Status: intended for Human + Governance review

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this note may claim bounded give-ground / restore-space battle behavior and observation-level support or rebuttal; it may not claim literal keep-front backward motion, full retreat doctrine, or a new locomotion capability already exists

### 1. Battle read first

The current experimental maneuver-envelope branch does **not** read like a
failed or invisible mechanism.

It does read like a bounded mechanism that is currently:

- strong enough to make unit-level sortie / return-to-line behavior visible
- not strong enough to produce a consistently clear maintained battle read
- still prone to a late sticky-contact relapse window at `36v36`

Plain-language judgment:

- Human's current visual read is mostly supported
- but the "effect seems somewhat weak" conclusion needs one important nuance:
  - the current branch is not simply weak everywhere
  - it is more bounded early, cleaner in some middle windows, and then still
    has a late relapse pocket that makes the whole battle feel less decisive

### 2. Support / refute of the Human visual read

#### 2.1 "This battle now reads closer to baseline"

Judgment:

- supported

Why:

- first-contact timing stays close to the temporary working anchor
- broad fleet rhythm is still readable as fleet-vs-fleet rather than free-form
  chaos
- the branch no longer reads like the earlier over-hot dog-fight family

Engineering evidence from the already completed `36v36` paired read:

- first negative `front_gap` moved from about `tick 73` to `tick 74`
- deepest early `front_gap` overlap improved from about `-3.93` to `-2.30`

Human-readable interpretation:

- the opening no longer breaks line quite as early or quite as deeply

#### 2.2 "Unit-level active sortie and return-to-line are visible"

Judgment:

- supported

Why:

- there are windows where forward peel-out is visibly stronger than the
  temporary working anchor
- there are later windows where return-to-line is also stronger than the
  temporary working anchor

Engineering evidence:

- during the opening contact window, fleet-A forward projection span was larger
  than baseline around the first contact-compression neighborhood:
  - around `tick 73`: about `10.85 -> 14.85`
  - around `tick 74`: about `9.61 -> 14.67`
- later, return-to-line became stronger:
  - around `tick 140`, fleet-A span was smaller than baseline:
    - about `23.06 -> 16.87`
  - around `tick 190`, contact count was lower:
    - about `2 -> 0`

Human-readable interpretation:

- Units do peel out a bit
- they also do come back into a more disciplined read later

#### 2.3 "The effect seems somewhat weak"

Judgment:

- partially supported, with an important correction

What is supported:

- the active effect does not yet read as strong, crisp, or decisive enough to
  become a maintained battle signature
- the visual impression can absolutely feel "a little weak" because the
  controller often protects the line first and only shows local freedom in a
  bounded envelope

What needs correction:

- the current branch is not simply weak in the sense of "nothing is happening"
- the local maneuver seam is real
- what makes it *feel* weaker is the combination of:
  - bounded early release
  - stronger mid-battle cleanup
  - a remaining late sticky-contact relapse that blunts the overall read

Engineering evidence:

- in the `91-150` window, mean contact was lower than baseline:
  - about `17.45 -> 15.38`
- in the `151-220` window, mean contact was again lower:
  - about `9.27 -> 8.41`
- but there was still a late relapse pocket:
  - around `tick 230`, contact rose from about `2` at baseline to about `14`
    on the current branch

Human-readable interpretation:

- the branch looks cleaner in several windows
- but because it still re-sticks later, the eye does not receive a clean
  "this new behavior is clearly better and stronger" conclusion

### 3. Parameter-tuning read

Current engineering judgment:

- parameter tuning should **not** be treated as the main next-step answer to
  the Human's "slightly weak" observation

Why:

- the exposed heading-side knobs did not materially move the `36v36 / 300 tick`
  read in prior bounded experiments
- the knob that does still move behavior most clearly is the brake side
- brake tuning mainly trades:
  - more or less overlap suppression
  - more or less sticky contact
- brake tuning does **not** honestly solve the deeper question:
  - what kind of local back-out / restore-line behavior should exist when the
    line is too compressed

Shortest conclusion:

- the Human perception problem is not mainly "the heading numbers are too cold"
- it is now closer to a mechanism-content question than a pure knob-temperature
  question

### 4. Back-off recommendation in plain language

If Governance wants to open the next line of work, Engineering recommends
treating **back-off** as a distinct question from both:

- local brake / local restore-line
- full retreat

Plain-language read:

- local brake means "push in less"
- restore-line means "come back toward readable fleet shape"
- back-off means "make space on purpose once the line is already too compressed"
- retreat means "the fleet has changed battle intent and is disengaging"

Engineering recommendation:

- open **back-off** first as the next bounded discussion track
- keep **retreat** separate unless Governance explicitly wants to open a larger
  doctrine gate

### 5. Main warning: literal `back_off_keep_front` is not free

This is the most important implementation-boundary warning for Governance.

Current locomotion semantics still do this:

- `realized_heading_hat` is produced inside
  - `runtime/engine_skeleton.py`
  - `integrate_movement(...)`
- `orientation_vector` is then written from that realized heading
- `velocity` is also written along that same realized heading
- movement speed is non-negative

Plain-language implication:

- the current runtime does **not** have a native expression for:
  - "move backward while still facing forward"

So if Governance says:

- "back off, but keep the front"

there are two different possible meanings:

1. readable-fleet meaning
   - the fleet still reads frontally coherent while units locally open space
2. literal kinematic meaning
   - units physically travel backward while their facing remains forward

Engineering recommendation:

- do **not** let those two meanings stay blurred
- Governance should decide explicitly which meaning is intended

Why this matters:

- meaning `1` can likely stay within the existing maneuver-envelope /
  restore-line family
- meaning `2` is no longer just a small maneuver tweak
  - it touches locomotion / facing / velocity semantics

### 6. Recommended smallest honest next step

Engineering recommends the next bounded discussion be framed as:

- `standoff-violation back-off response`

not as:

- full retreat
- generic "smarter local_desire"
- immediate locomotion rewrite

Preferred plain-language target:

- once the line is already too compressed, units should help reopen space
  deliberately
- but they should still do so under fleet-side discipline
- this should reduce:
  - lingering front-rank overlap
  - sticky dog-fight persistence
  - rotational collapse

without yet claiming:

- formal retreat doctrine
- literal reverse-with-front-preserved kinematics

### 7. Suggested owner/boundary posture for back-off

Engineering recommendation:

- fleet side should still authorize the envelope
- unit side should still realize the motion

Keep unchanged unless Governance explicitly widens scope:

- no second target owner
- no `resolve_combat(...)` owner change
- no mode system
- no persistent target memory
- no broad locomotion rewrite

Recommended active signal family for a bounded back-off discussion:

- early guard / early "do not cross yet":
  - `battle_relation_gap_raw`
- later restorative context:
  - `battle_relation_gap_current`
  - `battle_brake_drive_current`
  - `battle_hold_weight_current`

Recommended caution:

- do not let one scalar family member silently become:
  - early guard
  - release owner
  - restore owner
  - retreat owner
  all at once

### 8. Questions Engineering recommends Governance answer explicitly

Before authorizing a back-off slice, Engineering recommends Governance answer
these questions in plain language:

1. Does "back-off" mean:
   - "restore space while still reading like a fleet front"
   or
   - "literal backward movement while preserving forward-facing posture"

2. Is back-off still a bounded restorative response inside the current battle
   intent?
   or
   Is it already the first form of retreat?

3. Should back-off remain:
   - fleet-authorized
   - unit-realized
   with current target ownership unchanged?

4. Is the next slice allowed to touch locomotion semantics if literal
   backward-with-front-preserved motion is desired?

### 9. One-sentence conclusion

Human's latest `36v36` visual read is mostly supported:

- the branch is closer to baseline
- unit-level sortie / return is real
- but the effect still feels weaker than desired because it is bounded early
  and still has a late sticky-contact relapse window

Engineering recommendation for the next line:

- discuss **bounded back-off** first
- keep it separate from full retreat
- and force an explicit Governance decision on whether
  `back_off_keep_front` means a readable fleet behavior or a literal new
  locomotion/facing kinematic capability
