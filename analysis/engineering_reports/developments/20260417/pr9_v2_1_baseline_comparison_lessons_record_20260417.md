# pr9_v2_1_baseline_comparison_lessons_record_20260417

## Scope

- formation-only debugging discipline
- regression-isolation method
- causal lessons after `dev_v2.1 / a0d0b46` baseline comparison

## Why this record exists

This record is not a new mechanism proposal.

Its purpose is to preserve the concrete lessons from the recent
`a0d0b46 -> current freeze branch` owner/path comparison so later PR#9 slices do
not repeat the same causal mistakes.

## Highest-trust method lesson

The highest-trust regression anchor for this window was:

- `dev_v2.1 / a0d0b46`

The reliable comparison method was:

1. capture `initial_state`
2. capture `runtime_cfg`
3. capture `execution_cfg`
4. capture `observer_cfg`
5. replay current runtime against the exact same prepared payload
6. compare tick-by-tick frame facts, not chronology intuition

This matters because runtime itself is deterministic.

So:

- `effective_random_seed` drift is not an explanation for runtime behavior
- chronology notes are not proof of causality
- same-initial-state replay is the right causal filter

## Main debugging lesson

The recent failure mode was:

- several changes were initially treated as mostly structural cleanup
- but some of them were actually active behavior changes
- the behavior drift became obvious only after Human launcher observation and
  same-initial-state replay

Therefore:

- anything that changes an active reader/writer path for an already-live carrier
  must be treated as behavior-affecting until proven otherwise
- moving state between bundle, runtime state, and local bridge payload is **not**
  behavior-neutral by default

## Specific lessons by mechanism family

### 1. Reference-speed carrier changes clearly affect behavior

The following are behavior-owning, not cosmetic:

- `transition_reference_max_speed_by_unit`
- `formation_hold_reference_max_speed_by_unit`

Lesson:

- these are not mere caches
- they carry phase-entry / phase-local speed reference semantics
- replacing them with a different state shape can change battle and neutral
  motion immediately

Concrete recent lesson:

- rewriting them as a long-lived unit-state reference-speed family changed
  pre-contact and hold behavior
- restoring the bundle-map semantics removed the observed pre-contact drift

### 2. Direction-carrier split changes clearly affect behavior

The following are behavior-owning:

- `last_target_direction`
- `movement_heading_current_xy`
- the direction fed into `_resolve_v4a_reference_surface(...)`
- the direction fed into `integrate_movement()`

Lesson:

- if restore/reference reads one direction while realized movement reads another,
  runtime enters a split-brain state
- this immediately changes pre-contact behavior and can create jitter / excess
  rigidity

Concrete recent lesson:

- routing reference-surface reads to a different direction carrier than movement
  was not neutral
- restoring the old aligned read removed the first-tick divergence against
  `a0d0b46`

### 3. Engagement-result carriers can leak into geometry ownership

The following are behavior-owning when battle geometry reads them:

- `engaged_attack_vectors`
- `engagement_geometry_active_current`
- `front_reorientation_weight_current`
- `last_engagement_intensity`

Lesson:

- combat-assignment outputs must not be assumed to be harmless if movement /
  battle geometry also consumes them
- changing unit-level fire-control can indirectly change fleet-level steering if
  these reads are coupled

Concrete recent lesson:

- forward fire cone was intended to affect firing / target assignment only
- but battle reorientation also consumed engagement-result signals
- that coupling made post-contact motion more rigid until it was separated

### 4. BattleState carrier moves are not neutral by default

The following recent move was structurally reasonable in principle:

- moving fleet-level runtime carriers into `BattleState`

But lesson:

- if symmetric merge, fixture reads, bridge reads, and movement reads are not all
  updated with exact semantic parity, the move changes behavior
- state relocation must be audited as an owner-path change, not logged as
  refactor-only by default

## Concrete rule for upcoming PR#9 work

The following categories must be assumed behavior-affecting unless proven
otherwise:

1. any change to active readers/writers of:
   - `last_target_direction`
   - `movement_heading_current_xy`
   - `transition_reference_max_speed_by_unit`
   - `formation_hold_reference_max_speed_by_unit`
   - `last_engagement_intensity`
2. any change to which direction feeds:
   - reference surface
   - expected-position restore
   - realized movement
3. any change that lets unit-level combat engagement outputs affect:
   - fleet geometry activation
   - fleet front reorientation
4. any new low-level locomotion constraint:
   - acceleration
   - deceleration
   - turn-rate
   - speed-turn coupling

These are all real behavior seams, not merely internal organization choices.

## Practical debugging lesson

The correct sequence for this PR#9 line is:

1. Human launcher observation
2. same-initial-state replay against trusted anchor
3. isolate one mechanism group
4. only then make the next bounded slice

The wrong sequence is:

1. assume structure-only
2. stack multiple owner changes
3. interpret later drift from chronology alone

## Short conclusion

The strongest lesson from this window is:

- the current Formation / bridge / movement family contains several carriers that
  look infrastructural but are actually live behavior owners

So for the next PR#9 slices:

- treat carrier-path changes as behavior changes
- prove neutrality with same-initial-state replay instead of assuming it
- isolate one mechanism group at a time
