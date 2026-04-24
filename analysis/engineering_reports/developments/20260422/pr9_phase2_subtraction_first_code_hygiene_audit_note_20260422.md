## PR9 Phase II - Subtraction-First Code Hygiene Audit Note

Date: 2026-04-22  
Scope: practical code-hygiene audit before further structural work  
Status: audit only, no runtime implementation in this note

### 1. Battle-read reason for the audit

The recent Phase II work has been useful because it made previously implicit
Unit-level behavior visible:

- target identity is no longer owned by combat execution
- Unit-local desire exists as an explicit tick-local carrier
- `back_off_keep_front` now has a behavior-line experimental branch
- late reopen-space persistence has a concrete experimental read

But this also creates a real risk.

If every slice leaves behind one more helper, one more diagnostic mirror, one
more transitional setting name, or one more fallback-style read, then Human,
Engineering, and Governance will eventually stop seeing the actual battle
owner/path clearly.

The battle risk is practical:

- a sticky-contact behavior may appear to be caused by one mechanism while the
  live code is actually reading a stale carrier or fallback
- a Unit-side maneuver surface may still be labeled as v4a / formation-facing
  and mislead future tuning
- a debug indicator may survive after its mechanism role has changed, causing
  Human review to track the wrong variable

So the immediate goal should be subtraction-first hygiene:

- remove pure passthroughs where they do not protect a boundary
- replace stale debug surfaces instead of adding more indicators
- fail fast on active owner/path wiring mistakes instead of treating missing
  data as "no target"
- keep experimental single-site logic inline until Governance settles the
  mechanism family

### 2. Keep / retire / relabel / defer table

| Item | Current role | Decision | Reason | Recommended action |
| --- | --- | --- | --- | --- |
| `_compute_unit_intent_target_by_unit(...)` | Runtime-local same-tick target selector used by Unit intent and combat re-check | Keep | It owns the current minimal same-tick target source and protects the target-selection / combat-execution split | Keep as the active selector until a real shared spatial-service owner is authorized |
| `_select_targets_same_tick(...)` | Pure passthrough to `_compute_unit_intent_target_by_unit(...)` | Retire | It does not clarify a boundary and adds an alias-like call path | Replace call sites with `_compute_unit_intent_target_by_unit(...)` in a small cleanup |
| `_compute_unit_desire_by_unit(...)` | Single-site experimental Unit desire / maneuver response logic | Keep inline | It is long, but still under active Governance review; splitting now would create helper growth without a stable subproblem | Do not extract helpers yet; subtract stale branches first |
| `_smoothstep01(...)` | Shared bounded smoothing math | Keep | It is used in multiple places and gives one stable clamped smoothing semantics | Keep |
| `unit_intent_target_by_unit` in `_debug_state` | Tick-local carrier from target selection into bridge/desire | Keep | It is an explicit active carrier, not compatibility residue | Keep until a future owner/schema split replaces it |
| `unit_desire_by_unit` in `_debug_state` | Tick-local carrier into locomotion realization | Keep | It is the active Unit desire carrier | Keep |
| `local_desire_diag_by_fleet` | Debug mirror for local desire fleet indicators | Defer, then replace | It is useful for review, but now only mirrors older variables while the live branch added late persistence | In a debug cleanup, replace with a minimal current set rather than adding a large catalog |
| `runtime.physical.local_desire.experimental_signal_read_realignment_enabled` | Test-only explicit enablement for experimental Unit-local maneuver family | Relabel, not rename yet | Name is stale, but key has real active dependency across settings and runtime | Keep key for now; keep comments saying this is test-only back-off / Unit-local maneuver behavior, not maintained doctrine |
| `runtime.movement.v4a.engagement.*` | Transitional Unit-side engaged maneuver-speed shaping under historical v4a surface | Relabel | Active code still reads these keys, but owner language should not imply fleet doctrine | Keep runtime wiring; continue owner-language cleanup only |
| `attack_speed_backward_scale` | Backward-relative attack direction speed allowance | Relabel | It is not literal backward-motion capability | Keep, but keep documentation explicit |
| `battle_relation_gap_raw` | Early no-crossing guard | Keep | Governance locked its role | No cleanup unless role is violated |
| `battle_relation_gap_current` | Later compressed-line truth / late persistence band | Keep | Active behavior-line owner for later context | No surface move yet |
| `battle_brake_drive_current` | Later severity / urgency | Keep | Active role is narrow and documented | No surface move yet |
| `battle_hold_weight_current` | Coherence cap / fleet hold context | Keep | Active fleet/reference-side signal reused by Unit realization | Keep coupling note visible |
| `near_contact_gate` and local target range gates | Auxiliary localizers | Keep | They localize Unit-side response but do not own authorization | Keep; do not promote to strategic authority |

### 3. Helper audit

#### `_smoothstep01(...)`

Why it exists:

- shared clamped smoothing for continuous gates

Boundary value:

- real utility, because it removes repeated clamp / polynomial code

Recommendation:

- keep

#### `_compute_unit_intent_target_by_unit(...)`

Why it exists:

- computes the same-tick target source used before locomotion and before combat
  re-check

Boundary value:

- real owner boundary:
  - target selection != combat execution

Recommendation:

- keep

#### `_select_targets_same_tick(...)`

Why it exists:

- currently only forwards to `_compute_unit_intent_target_by_unit(...)`

Boundary value:

- weak
- it creates a second name for the same owner without adding behavior or
  validation

Recommendation:

- retire in a small cleanup
- call `_compute_unit_intent_target_by_unit(...)` directly from `step(...)`

#### `_compute_unit_desire_by_unit(...)`

Why it exists:

- owns the current tick-local Unit desire carrier content
- includes the experimental Unit-local maneuver / `back_off_keep_front`
  behavior line

Boundary value:

- real owner boundary:
  - Unit desire generation != locomotion realization

Should it be split now:

- no
- the block is busy, but still experimental and single-site
- helper extraction now would spread an unsettled mechanism across more names

Recommendation:

- keep inline
- subtract stale conditions / stale diagnostics before considering any helper
  extraction

#### `_apply_v4a_transition_speed_realization(...)`

Why it exists:

- applies transitional engaged maneuver-speed shaping inside the v4a bridge /
  transition-speed path

Boundary value:

- currently real, but owner language is transitional

Recommendation:

- keep wiring unchanged
- avoid creating another wrapper around it
- continue relabeling as transitional Unit-side maneuver-speed shaping

### 4. Fallback audit

| Fallback-like behavior | Explicit or silent | Necessary? | Temporary or maintained | Recommended action |
| --- | --- | --- | --- | --- |
| `unit_intent_target_by_unit = self._debug_state.get(..., {})` in bridge/desire paths | Silent-ish defensive read | Not ideal on active path | Temporary | Replace with fail-fast or direct required read after confirming `step(...)` ordering remains stable |
| `unit_intent_target_by_unit.get(unit_id)` when computing selected target for Unit desire / bridge speed | Silent missing-key read | Unnecessary if selector owns all alive Units | Temporary | Treat missing key as wiring error; preserve `None` only as explicit "no selected target" |
| `selected_target_by_unit.get(attacker_id)` in `resolve_combat(...)` | Silent missing-key read | Unnecessary if combat receives complete selector output | Temporary | Fail fast on missing attacker key; allow value `None` as explicit no-target |
| `state.coarse_body_heading_current.get(..., movement_direction)` and related heading fallback | Explicit defensive initialization | Probably necessary during early ticks / neutral paths | Maintained for now | Keep, but do not use as precedent for mechanism fallback |
| `movement_direction_by_fleet.get(..., state.last_target_direction...)` in Unit desire | Explicit no-target / no-command behavior | Necessary for no-target or neutral-like conditions | Maintained for now | Keep |
| `local_desire_diag_by_fleet` type reset to `{}` | Silent debug repair | Not behavior-critical, but can hide debug wiring errors | Temporary | Defer; in debug cleanup, either fail-fast for malformed debug state or remove the mirror |
| `settings_accessor` public accessors returning caller-provided defaults | Explicit accessor API | Necessary as low-level API only | Maintained | Keep, because active scenario builders use `MISSING` + `_require_present` for runtime semantics |
| `_require_present(...)` in `test_run_scenario.py` | Explicit fail-fast | Necessary | Maintained | Keep |
| archetype/color/avatar display fallbacks | Explicit presentation/prep fallback | Outside active runtime mechanism | Maintained/defer | Not part of this behavior-line cleanup |

Most important cleanup target:

- missing active target-carrier keys should fail fast
- missing target value may still be `None`
- missing key should not silently mean "no target"

### 5. Compatibility residue audit

#### `local_desire.experimental_signal_read_realignment_enabled`

Active dependency:

- settings accessor
- scenario builder
- runtime movement surface
- Human/VIZ test-only enablement

Issue:

- the key name still says `signal_read_realignment`, but the family now
  includes:
  - Unit-local maneuver envelope
  - behavior-line `back_off_keep_front`
  - late reopen-space persistence

Recommendation:

- do not add a second switch now
- do not rename the key during this behavior line unless Governance explicitly
  opens a settings-surface migration
- keep relabeling comments/documentation as test-only experimental Unit-local
  maneuver / back-off behavior family

Retirement / rename condition:

- after Governance decides whether this family is retained, retired, or promoted
  into a maintained mechanism with a stable name

#### `runtime.movement.v4a.engagement.*`

Active dependency:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `runtime/engine_skeleton.py`
  - `_apply_v4a_transition_speed_realization(...)`

Issue:

- key path still says v4a engagement
- practical job is transitional Unit-side engaged maneuver-speed shaping

Recommendation:

- relabel only for now
- no wiring move in this hygiene gate

Retirement / migration condition:

- after Governance authorizes a settings-surface migration or Unit-side surface
  owner move

#### `attack_speed_backward_scale`

Active dependency:

- runtime transition-speed shaping

Issue:

- can be misread as literal backward-motion capability

Recommendation:

- keep explicit documentation:
  - backward-relative attack direction speed allowance
  - not literal keep-front backward translation

Retirement / rename condition:

- future locomotion capability gate or settings-surface migration

#### `local_desire_diag_by_fleet`

Active dependency:

- `_MovementDiagSupport.build_pending(...)`
- `test_run_execution._build_focus_indicator_payload(...)`
- VIZ debug focus block

Issue:

- currently mirrors only older local-desire indicators:
  - `early_embargo_permission`
  - `relation_violation_severity`
- late reopen-space persistence is active in runtime but not cleanly represented
  by the current debug mirror

Recommendation:

- do not add a large indicator catalog
- in a separate debug cleanup, replace stale indicators with a minimal active
  set that maps to current battle read

Retirement / replacement condition:

- after Human confirms which debug values are still used for review

#### `_select_targets_same_tick(...)`

Active dependency:

- `step(...)`

Issue:

- compatibility-style alias around the actual selector

Recommendation:

- retire

Retirement condition:

- immediate small cleanup is safe if Governance allows a subtraction-only edit

### 6. Smallest subtraction moves

The following are the smallest safe cleanup moves that do not reopen the larger
mechanism debate.

1. Retire `_select_targets_same_tick(...)`

- replace `self._select_targets_same_tick(moved_state)` with
  `self._compute_unit_intent_target_by_unit(moved_state)`
- delete the wrapper
- no behavior change intended

2. Make same-tick target carrier reads fail-fast on missing keys

- keep `None` as explicit "no selected target"
- treat missing unit key as wiring error
- apply to:
  - Unit desire read
  - bridge speed-shaping read
  - combat re-check read

3. Replace, do not expand, local-desire debug indicators

- do not add many new fields
- decide a minimal active set for current review
- likely candidates are:
  - early guard permission
  - late reopen persistence
  - maybe relation violation severity only if still actively reviewed

4. Continue relabel-only treatment for v4a engagement surfaces

- do not move wiring yet
- keep docs clear that these are transitional Unit-side speed-shaping surfaces

5. Keep experimental `local_desire` logic inline

- do not extract more helpers while the family is still experimental
- subtract stale branches first

### 7. Shortest conclusion

The next hygiene move should be subtraction-only.

Best first cleanup:

- remove the pure target-selection wrapper
- make missing same-tick carrier keys fail fast
- replace stale debug indicators instead of adding a catalog

Do not:

- add helpers for the long experimental block
- add compatibility switches
- add fallback paths
- move v4a engagement wiring yet
- rename settings keys before Governance opens a surface migration.
