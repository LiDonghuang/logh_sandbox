## PR9 Phase II - `back_off_keep_front` Late Reopen-Space Persistence Bounded Implementation Proposal

Date: 2026-04-22  
Scope: document-first bounded proposal for Human + Governance  
Status: no implementation in this note

**Line classification:** Behavior line  
**Owner classification:** fleet-authorized / unit-realized  
**Honest claim boundary:** this note may propose a bounded give-ground / reopen-space persistence adjustment under current locomotion semantics; it may not claim literal keep-front backward motion, turn-away retirement, full retreat doctrine, or a new locomotion capability

### 1. Battle read first

The current experimental `back_off_keep_front` line is better than the prior
local-desire family in one important way:

- the first contact no longer reads like immediate deep overrun
- the front stays more readable in the opening collision
- `100v100` clearly benefits from the new line discipline

The remaining failure is narrower:

- at `36v36`, after the opening has already been controlled, too many Units
  stay in a sticky firing contact band
- the battle reads less like chaotic first-contact crossing, but still does not
  create a clear enough later space-reopening window
- the front is readable, but the small battle can remain welded into a broad
  firing line

The next slice should therefore not make Units freer and should not reopen the
whole local-maneuver problem.

The visible target is:

- keep the better early line discipline
- keep the better `100v100` readability
- reduce `36v36` sticky contact in the later windows
- create a clearer late "make room, then re-form" read
- still acknowledge rotating / fragmented recovery as an honest residual of
  current locomotion semantics

### 2. One-sentence conclusion

The proposed next slice is a narrow late-phase persistence adjustment: keep
`battle_relation_gap_raw` as the early guard, but let the later `back_off_keep_front`
response persist mildly while the fleet is only barely reopened and Units are
still locally in firing contact, so `36v36` can reduce sticky late contact
without losing the early crossing gains.

### 3. Exact owner/path to change if later authorized

Only this owner/path would change:

- `runtime/engine_skeleton.py`
  - `EngineTickSkeleton._compute_unit_desire_by_unit(...)`
  - existing experimental branch behind:
    - `runtime.physical.local_desire.experimental_signal_read_realignment_enabled`

Unchanged:

- same-tick target source stays:
  - `selected_target_by_unit`
- current Unit desire carrier stays:
  - `desired_heading_xy`
  - `desired_speed_scale`
- `resolve_combat(...)` ownership stays unchanged
- no second target owner
- no guide-target semantics
- no mode
- no retreat implementation
- no locomotion rewrite
- no module split
- no owner-language cleanup expansion

### 4. What is already improved and should stay fixed

The current line should not be thrown away.

The useful parts to preserve are:

1. `battle_relation_gap_raw` as early guard

- it now prevents early local opportunity from breaking fleet hold too soon
- this is the part most directly tied to improved opening front readability

2. heading-side local opportunity suppression

- Units are less likely to keep peeling toward off-axis firing opportunity when
  the fleet-level context says the line is compressed

3. speed-side brake-only restraint

- speed response is now a real partner rather than a tiny decorative factor
- it still does not become sprint / lunge / turn-away retirement

4. no literal backward-motion claim

- the current branch remains honest:
  - it can reduce over-commit
  - it can help reopen some space
  - it cannot literally translate backward while preserving forward-facing
    posture

### 5. The real remaining mechanism question

The remaining problem is mainly:

1. **later authorization is too narrow / too short-lived**
2. **later give-ground severity loses persistence too early at small scale**

Secondary read:

- the coherence cap is not too strong; if anything, it is too weak when it is
  the only remaining limiter after the relation-gap violation has cleared
- localizer use is not the primary failure, but the late response should be
  localized to Units still in the firing-contact neighborhood

Plain-language explanation:

- in `36v36`, the fleet-level gap can look "open enough" while a small number
  of front-rank Units are still stuck in local firing contact
- once `battle_relation_gap_current` becomes positive enough, the current
  later restorative response largely turns off
- the Units then retain too much local firing-contact persistence, even though
  the battle still does not read like a clean reopen-space window

This is not an early-guard problem.

The early guard did its job.

This is a late persistence problem:

- after the line is no longer deeply violated
- but before the local contact band has actually unwelded

### 6. Why this should not be treated as vague tuning

This proposal is not simply "increase a parameter."

The underpowered job is specific:

- the current later response treats "negative / violated relation gap" as the
  main restore trigger
- but `36v36` can still have visible sticky contact after that global violation
  read has faded

So the next slice should add a bounded late persistence read, not just heat all
local-desire knobs.

The proposed role remains:

- early guard:
  - do not cross too early
- late persistence:
  - do not instantly stop making room just because the global gap has barely
    returned positive

### 7. Proposed narrow mechanism change

If later authorized, add one derived late-phase context inside the existing
experimental branch:

- a bounded `late_reopen_persistence` read

Plain-language meaning:

- "the line is no longer in the worst compression, but it is still not reopened
  enough to release front-rank Units fully back into sticky firing contact"

Suggested source role:

- primary fleet-side source:
  - `battle_relation_gap_current`
- early-release protection:
  - `battle_relation_gap_raw` / existing early-embargo permission
- localizer:
  - same-tick selected-target distance via existing `maneuver_context_gate` /
    `near_contact_gate`

Important boundary:

- this is not a new target owner
- this is not persistent memory
- this is not retreat authorization
- this is not a new locomotion capability

### 8. Variable-role discipline

#### 8.1 Early guard remains unchanged

Use:

- `battle_relation_gap_raw`

Job:

- early no-crossing / early release guard

What must not change:

- it should not become the late restore owner
- it should not become retreat authorization
- it should not be reused as a generic severity signal

#### 8.2 Later compressed-line truth gets a persistence band

Use:

- `battle_relation_gap_current`

Current job:

- later compressed-line truth / later authorization context

Proposed narrow extension:

- add a small positive "not reopened enough yet" persistence band
- this band should be weaker than true violation response
- it should only extend the back-off response after early line discipline has
  already been protected

Why this remains a later-phase problem:

- the extension should not activate as early crossing permission
- it should only keep a mild reopen-space response alive while the line is just
  barely re-opened and local contact still exists

#### 8.3 Brake drive remains later severity / urgency

Use:

- `battle_brake_drive_current`

Job:

- severity / urgency when the relation is truly too compressed

What should not change:

- it should not be forced to explain positive-gap sticky contact by itself
- it should not become a full retreat drive

Proposed use:

- retain it as the stronger severity path
- combine it with the milder late persistence band by `max(...)` or another
  bounded monotonic read, not by raw multiplication that amplifies both stages
  invisibly

#### 8.4 Hold weight remains coherence cap

Use:

- `battle_hold_weight_current`

Job:

- coherence cap / front-readability context

What should not change:

- it should not become the main reopen-space owner
- it should not become a hidden retreat owner

Proposed use:

- keep it as a cap on local freelancing
- if reused in the late-persistence path, use it only as a bounded coherence
  limiter, not as a raw drive term

#### 8.5 Local geometry remains auxiliary localizer

Use:

- `near_contact_gate`
- `maneuver_context_gate`
- same-tick target range from the existing selected target

Job:

- identify which Units are still in local contact / maneuver pressure

What should not change:

- these should not become fleet-side authorization
- they should not create a second target owner
- they should not decide retreat

### 9. Minimal implementation shape if later authorized

The minimal implementation should stay entirely within the existing
experimental branch and current carrier.

Recommended shape:

1. keep the current early-guard math unchanged

- do not change `battle_relation_gap_raw`
- do not change the early no-crossing role

2. derive a mild late persistence context from `battle_relation_gap_current`

- true negative relation violation remains the stronger response
- a small positive relation-gap band becomes a weak persistence response
- this positive band should mean:
  - "not badly compressed anymore"
  - but also:
  - "not reopened enough to fully release sticky contact"

3. apply that persistence mostly to speed-side restraint first

- desired speed remains brake-only
- no boost / lunge / sprint
- no turn-away retirement
- the response should make front-rank Units stop re-feeding the sticky contact
  band

4. apply only a restrained heading-side effect

- keep heading-side local opportunity suppression while persistence is active
- do not introduce a large new heading drive
- do not re-create the earlier dog-fight / peel-out problem

5. require local contact neighborhood

- use existing selected-target range gates only as localizers
- this avoids slowing rear or irrelevant Units when only a few front Units are
  still welded

### 10. What should not be changed in this slice

This proposal explicitly excludes:

- target-selection ownership
- combat execution ownership
- second target / guide-target semantics
- mode system
- retreat implementation
- persistent target memory
- literal keep-front backward-motion capability
- broad locomotion rewrite
- module split
- owner-language cleanup expansion
- changing the temporary working anchor / baseline policy

### 11. Coupling risk and why it is bounded

This proposal reuses the same battle-gap family, so the coupling risk must stay
visible.

Risk:

- `battle_relation_gap_current` already participates in fleet movement / hold
  logic
- using it again inside Unit-local desire can duplicate the same standoff read
  across stages

Why the reuse may still be acceptable:

- the proposed use is not a new raw drive
- it is a bounded persistence envelope for the already experimental
  behavior-line branch
- it does not change the fleet-side owner of standoff truth
- it does not create a second target or a new combat owner

Residual risk:

- if the persistence band is too wide, it can over-brake the battle and make
  small fights feel sluggish
- if it is too strong, it can damage the `100v100` improvement by over-holding
  fronts that already behave well
- if it is not localized to actual contact, it can suppress normal fleet motion
  instead of only reducing sticky front-rank contact

### 12. Validation posture if later authorized

Validation should focus on preserving the already-won behavior before judging
the new improvement.

Required comparison anchor:

- current temporary working-anchor baselines
- explicit experimental enablement on the current branch

Priority order:

1. preserve current early-crossing improvement

- `36v36` opening should not return to deep first-contact overrun
- `61-90` should remain clearly better than the temporary working anchor

2. preserve `100v100` gains

- `100v100` should not lose its later reduced-contact improvement
- especially around `190-220`

3. improve `36v36` late reopen-space

- primary windows:
  - `190-220`
  - `230-280`
- expected change:
  - lower mean contact than the current experimental branch
  - clearer visible space-reopening window
  - no obvious reintroduction of early crossing

4. inspect human-readable residuals

- rotating pullback may remain
- fragmented return may remain
- collapse-like recovery after deep overlap may remain
- but sticky firing-line persistence should be reduced

### 13. Recommended evidence to report after implementation

If this proposal is later authorized and implemented, Engineering should report:

1. static owner/path audit
2. compile check
3. narrow smoke behind explicit experimental enablement
4. paired comparison against the temporary working anchor
5. targeted `36v36` window table for:
   - `61-90`
   - `190-220`
   - `230-280`
6. targeted `100v100` check for regression in:
   - `190-220`
7. one short human-readable replay read:
   - opening contact
   - late contact
   - reopen-space window
   - residual rotating / fragmented recovery

### 14. Shortest conclusion

The next slice should not reopen the whole maneuver problem.

It should keep the early guard fixed and add only a bounded late reopen-space
persistence read, because the remaining `36v36` failure is:

- not early crossing
- not lack of target identity
- not lack of a carrier
- not literal retreat

It is:

- late sticky contact persisting after the global gap has barely returned to an
  acceptable-looking value.
