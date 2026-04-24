## PR9 Phase II - Retreat Mechanism Concept Proposal

Date: 2026-04-21  
Scope: concept proposal only; no implementation in this note  
Status: document-first proposal for next-round discussion

### 1. Battle read first

In this model, retreat should not mean "a unit wiggles less" or "a unit brakes a
bit."

If retreat is ever activated, the battle should read like this:

- the fleet is no longer trying to hold the current contact line in the same
  way
- unit motion now serves a disengagement decision
- local motion is no longer just a small correction inside the existing front

Acceptable read:

- a damaged or over-pressured side pulls back in a readable, disciplined way
- the fleet front stays interpretable
- disengagement looks deliberate, not chaotic

Unacceptable read:

- every unit independently fleeing on its own
- retreat being smuggled in as just "very strong brake"
- local restore-line logic being mislabeled as retreat

### 2. One-sentence conclusion

The first honest retreat split should stay separate from the immediate
precontact/standoff slice, and should be discussed as a fleet-authorized family
with two conceptually distinct forms: `back_off_keep_front` and
`turn_away_retirement`.

### 3. What retreat means in this model

Plain-language definition:

- retreat means the side has decided not merely to correct local over-commit,
  but to concede or reduce the current contact
- retreat therefore changes the higher-level battle intent, not just local
  maneuver temperature

Engineering read:

- retreat is not just a stronger local correction
- retreat is a higher-level authorization to disengage

### 4. How retreat differs from nearby concepts

#### 4.1 Local brake

What it is:

- a temporary speed reduction while still pursuing the same contact intent

What it is not:

- not disengagement
- not conceding the line

#### 4.2 Restore-line tendency

What it is:

- a local correction that pulls units back toward readable fleet shape or front

What it is not:

- not a decision to exit the fight
- not permission to abandon the line

#### 4.3 Back-out-lite

What it is:

- a bounded violation response that creates a little more space and reduces
  overlap pressure
- still below full retreat

What it is not:

- not doctrine-scale disengagement
- not a full owner for retreat semantics

#### 4.4 Retreat

What it is:

- a higher-level decision to reduce or break contact intentionally

What it adds beyond the three items above:

- sustained disengagement intent
- clearer directionality away from current threat/contact
- changed priority relationship between keeping fire opportunity and restoring
  safety / spacing

### 5. Fleet-side owner versus unit-side realization

Preferred owner split:

- fleet-side owner:
  - authorizes whether retreat is active
  - decides broad retreat form
  - preserves overall front/readability goals
- unit-side realization:
  - realizes heading, speed, and local spacing under that retreat authorization

Why this split matters:

- in the current model, one Unit represents many ships
- therefore "retreat" should not begin as many independent unit-side tactical
  choices
- retreat should begin as a higher-level fleet decision and only then be
  realized locally

### 6. First honest retreat split

#### `back_off_keep_front`

Plain-language read:

- reduce pressure
- open space
- keep the fleet still reading frontally coherent
- do not rotate away completely

Likely behavior:

- brake
- back out / separate
- preserve front orientation as much as practical

Best use:

- first retreat-like family to discuss
- closest to current restore / hold concepts

#### `turn_away_retirement`

Plain-language read:

- disengage more decisively
- give up current direct front-facing contact
- reorient away from the enemy more clearly

Likely behavior:

- stronger departure from current front-facing posture
- more obvious withdrawal

Best use:

- more severe / later-stage retreat family
- should not be mixed into the first restorative slice

### 7. Interaction with fleet front, unit facing, and actual velocity

Retreat must keep these three layers separate:

- fleet front:
  - higher-level battle read
- unit facing:
  - local realized orientation
- actual velocity:
  - realized movement, which may lag or differ from facing

Engineering read:

- `back_off_keep_front` should preserve fleet front more strongly while letting
  local facing/velocity realize the withdrawal
- `turn_away_retirement` would allow larger departure between current front and
  local facing/velocity, but that should come only with stronger fleet-side
  authorization

### 8. Minimum conditions that would justify retreat

This is still concept-only, but the minimum conditions should likely include a
fleet-side read, not only unit-local geometry.

Candidate authorization class:

- contact is mature enough that retreat is meaningful
- restore / hold response is no longer enough
- fleet relation is persistently violated or collapsing
- battle pressure / disadvantage is sustained, not momentary

Important constraint:

- retreat should not trigger merely because one unit sees a bad local angle
- retreat should require a broader fleet-context judgment

### 9. Why retreat remains separate from the immediate next slice

The immediate next slice is about:

- preventing early crossing
- restoring bounded standoff when violation starts

That remains a restorative constraint problem.

Retreat is different:

- it changes battle intent
- it needs clearer owner split
- it risks opening doctrine-scale behavior if mixed too early with the current
  restorative envelope work

Therefore the immediate next maneuver-envelope slice should stay separate from:

- full retreat implementation

### 10. Current recommendation

For the next round of discussion:

- keep retreat as a separate document-first track
- discuss it first as a fleet-authorized family
- keep the first conceptual split:
  - `back_off_keep_front`
  - `turn_away_retirement`

And keep it separate from the immediate bounded slice on:

- precontact no-crossing
- standoff-violation response
