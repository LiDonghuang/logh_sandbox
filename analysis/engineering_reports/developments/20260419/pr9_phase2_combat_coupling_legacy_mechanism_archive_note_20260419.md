# PR9 Phase II Combat Coupling Legacy Mechanism Archive Note 20260419

## Scope

This note archives the current engineering read of the maintained
`combat coupling` mechanism in the active runtime path.

Scope classification:

- runtime behavior review only
- document / archive only
- no code change

The immediate reason for archiving is that this mechanism appears to be much
older than the current PR9 Phase II owner/path work, but it now sits inside a
combat path that has already been rerooted around:

- same-tick target selection
- upstream unit intent
- same-tick unit desire
- local desire adaptation
- locomotion realization

So even though the mechanism itself is small, it is now coupled to several much
newer seams and should not be treated as an isolated legacy knob anymore.

## Current Active Owner

The active owner is:

- `runtime/engine_skeleton.py`
- `EngineTickSkeleton.resolve_combat(...)`

The scalar itself is defined in the maintained runtime path at:

- `geom_gamma = 0.3`
  - `runtime/engine_skeleton.py:3545`

The fleet-level participation inputs are built at:

- `alive_by_fleet`
  - `runtime/engine_skeleton.py:3602`
- `attackers_by_fleet`
  - `runtime/engine_skeleton.py:3618`
- `participation_by_fleet = attackers_by_fleet / alive_by_fleet`
  - `runtime/engine_skeleton.py:3629`

The actual coupling application is:

- `coupling = 1.0 + (geom_gamma * (p_attacker - p_target))`
  - `runtime/engine_skeleton.py:3694`
- `event_damage = self.damage_per_tick * coupling * q * range_quality`
  - `runtime/engine_skeleton.py:3698`

## Plain-Language Read

Current read in plain human terms:

- each unit still has a fixed base `damage_per_tick`
- but the actual damage of a hit is scaled by a small fleet-level advantage term
- that term asks:
  - among currently alive units in the attacker's fleet, what fraction currently
    has a same-tick selected target?
  - among currently alive units in the target's fleet, what fraction currently
    has a same-tick selected target?
- if the attacker's participation fraction is higher, hits from that fleet gain
  a small bonus
- if the target fleet's participation fraction is higher, hits from the attacker
  take a small penalty

With `geom_gamma = 0.3`, the raw coupling range is bounded to:

- minimum `0.7`
- maximum `1.3`

because both participation fractions are in `[0.0, 1.0]`.

## Important Semantic Detail

This mechanism does **not** currently count "units that actually deal damage on
this tick."

It counts units that have a non-`None` same-tick selected target in
`selected_target_by_unit`, before the later re-checks inside `resolve_combat(...)`.

That means `attackers_by_fleet` is upstream of:

- final range re-check
- final forward fire-cone re-check
- contact hysteresis enter/exit decision
- actual damage event emission

So the current participation fraction is more precisely:

- `selected-target participation fraction`

not:

- `actual firing participation fraction`

This distinction matters and is likely one reason the mechanism now feels
legacy/misaligned.

## Current Coupling to Newer Mechanisms

### 1. Same-tick target selection reroot

`resolve_combat(...)` no longer owns target choice internally. It consumes:

- `selected_target_by_unit`
- from `_select_targets_same_tick(...)`
- from `_compute_unit_intent_target_by_unit(...)`

Relevant active path:

- `runtime/engine_skeleton.py:3537`
- `runtime/engine_skeleton.py:3428`
- `runtime/engine_skeleton.py:3618`

So any future change to target-selection semantics now changes coupling input
semantics immediately.

### 2. Forward fire-cone filtering

The selected-target path already applies `fire_cone_half_angle_deg` in the
selector, and `resolve_combat(...)` applies the cone again as a final re-check.

Relevant active path:

- selector-side cone gate:
  - `runtime/engine_skeleton.py:3432`
- resolve-side cone re-check:
  - `runtime/engine_skeleton.py:3560`

This means coupling is already implicitly downstream of the newer cone-owned
combat path, even before damage quality is computed.

### 3. Fire optimal range semantics

`fire_optimal_range_ratio` affects:

- range-quality decay in `resolve_combat(...)`
  - `runtime/engine_skeleton.py:3555`
- and also v4a battle-gap/front-strip semantics upstream
  - `runtime/engine_skeleton.py:2303`

So the current damage event is shaped by both:

- a fleet-level participation scalar (`coupling`)
- and a fire-range control seam that already couples into locomotion/battle-gap
  geometry

This is a newer cross-stage coupling than the original legacy damage scalar
likely assumed.

### 4. Same-tick local desire adaptation / locomotion realization

PR9 Phase II now computes:

- same-tick target intent
- same-tick unit desire
- bounded local desire adaptation

Relevant active path:

- `_compute_unit_desire_by_unit(...)`
  - `runtime/engine_skeleton.py:1666`
- `integrate_movement(...)` consuming `unit_desire_by_unit`
  - `runtime/engine_skeleton.py:3139`

That means unit orientation, local alignment timing, and therefore selected
target availability and cone pass-rate are all now influenced by much newer
upstream desire/locomotion seams.

So `coupling` is no longer sitting on top of a simple old "move and fire"
stack. It now indirectly reads outcomes of the newer intent/desire pipeline.

### 5. Engagement writeback remains post-resolution

`engaged_target_id` remains post-resolution writeback:

- `runtime/runtime_v0_1.py:64`
- `runtime/engine_skeleton.py:3727`

This is good from an owner/path standpoint, but it also means the old coupling
scalar now lives in a path where:

- target identity is same-tick pre-resolution
- engagement state is post-resolution

So the combat owner has already been partially modernized around it.

## Why This Mechanism Now Looks Legacy

The current engineering read is that this mechanism likely came from an older
combat model where a small fleet-level scalar on per-hit damage was an acceptable
proxy for "line advantage" or "massed participation."

That read is now weaker for five reasons:

1. It operates at fleet aggregate level, but current combat shaping has become
   much more explicit at unit/same-tick level.

2. Its participation denominator is `alive_by_fleet`, while its numerator is not
   actual damaging attackers, but selected-target holders before final re-check.

3. It is hardcoded (`geom_gamma = 0.3`) rather than clearly documented as an
   accepted maintained doctrine seam.

4. It sits next to newer, more explicit seams:
   - fire cone
   - range quality
   - same-tick target owner
   - local desire adaptation
   - locomotion realization

5. Because it multiplies final event damage directly, it can materially affect
   battle outcomes while still being conceptually under-specified.

## Why This May Need More Than Minor Tuning

This does not currently look like a good candidate for "just tweak one number."

The more honest redesign questions are larger:

1. Should fleet-level participation modify per-hit damage at all?

2. If yes, should the input be:
   - selected-target participation
   - actual in-contact firing participation
   - some local geometry participation read
   - some front-line depth / frontage occupancy read

3. If no, should `coupling` be removed entirely and replaced by already explicit
   local mechanisms:
   - fire cone
   - range quality
   - local desire / orientation alignment
   - contact geometry

4. If retained, should it move out of "legacy scalar" form and become an
   explicitly named maintained seam with settings exposure and doctrine note?

Because the mechanism now touches battle outcome directly and is coupled to
several newer Phase II seams, this likely qualifies as a mechanism-content gate,
not a minor cleanup.

## Conservative Redesign Options

Document-first options worth considering later:

### Option A - Clarify and retain

Keep the mechanism, but re-specify it honestly as:

- fleet-level fire participation advantage scalar

If this path is chosen, the next minimum honest cleanup would be:

- count only units that pass final combat eligibility, not just same-tick
  selected target
- document and possibly expose `geom_gamma`

### Option B - Replace with tighter participation read

Retain a fleet-level scalar, but compute it from something closer to actual
combat realization, for example:

- actual in-contact attackers this tick
- or actual valid firing attackers after cone/range/contact re-check

This would make the mechanism less misleading while keeping the same general
family.

### Option C - Retire from damage path

Remove coupling from `event_damage` entirely and let explicit newer seams carry
combat differentiation:

- target selection
- fire cone
- range quality
- local desire / orientation
- contact geometry

If a fleet-level metric is still useful, keep it as telemetry rather than a
damage multiplier.

## Current Recommendation

Current engineering recommendation:

- archive the current mechanism as a legacy combat scalar
- do not silently tweak `geom_gamma`
- do not treat it as a harmless small constant
- revisit it only as a document-first combat-content review item

If this stage opens a larger combat-content pass, `coupling` should be reviewed
together with:

- target-selection participation semantics
- fire-cone doctrine
- range-quality semantics
- local desire / orientation alignment effects
- engagement/contact writeback boundaries

## Out of Scope

This note does **not**:

- propose an implementation slice
- authorize removal
- authorize parameter exposure
- change baseline expectations
- change governance state

It is an archive/report note only.

## Conclusion

The current `coupling` mechanism is small in code but no longer small in
architectural consequence.

It is a legacy fleet-level damage scalar now embedded in a much newer same-tick
targeting / desire / locomotion / combat stack.

That makes it a plausible candidate for substantial redesign rather than local
tuning.
