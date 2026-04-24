# PR9 Phase II - Strict Subtraction Ledger Audit Note

Date: 2026-04-22  
Scope: governance ledger after accepted no-drift cleanup  
Status: audit only, no runtime implementation in this note

## 1. Battle / Structure Read

The latest cleanup improved truthfulness, but it did not make the active
structural area small.

The current battle-facing risk is not that one more parameter is wrong. The
risk is that Human, Engineering, and Governance may again lose track of which
surface owns which behavior:

- target identity must stay separate from combat execution
- Unit-local desire / maneuver response must stay separate from locomotion
  capability
- behavior-line back-off must stay separate from literal keep-front backward
  motion
- maintained default must stay separate from test-only experimental behavior

This ledger therefore asks a stricter subtraction question:

- what can be deleted now
- what must remain but be marked honestly
- what cannot be touched because behavior would drift
- what should wait for a named future condition

## 2. Ledger Buckets

Each item below is classified into exactly one bucket:

- `delete now`
- `keep but explicitly mark as testonly / experimental / transitional`
- `do not touch now because behavior would drift`
- `defer until a named future condition is met`

## 3. Strict Ledger

| Item | Class | What it does now | Real layer | Bucket | Why / future condition |
| --- | --- | --- | --- | --- | --- |
| `_select_targets_same_tick(...)` | compatibility wrapper / alias | Former pure wrapper around `_compute_unit_intent_target_by_unit(...)` | none after cleanup | `delete now` | Already deleted in the accepted cleanup. Do not recreate an alias unless a real owner boundary appears. |
| VIZ display of `relation_violation_severity` | debug / focus indicator surface | VIZ still names the old violation indicator even though runtime/test_run now exports `late_reopen_persistence` | viewer debug surface | `delete now` | This is stale reader-facing surface, not active behavior. Replace/remove in the next VIZ sync so Human is not reading a dead indicator. |
| VIZ debug reference docs for `relation_violation_severity` | historical naming / debug docs | Documents the old local maneuver indicator as current | viewer docs | `delete now` | Runtime no longer exports it as visible debug. Update docs to the current minimal indicator set. |
| `_compute_unit_intent_target_by_unit(...)` | helper / active owner | Computes the single same-tick target source for Unit intent and combat re-check | runtime Unit-solving seam | `do not touch now because behavior would drift` | It is the active target-selection owner. Retirement requires a future shared spatial-service owner or equivalent authorized replacement. |
| `unit_intent_target_by_unit` | carrier map / mirror | Carries same-tick selected target IDs from target selection into bridge/desire/combat reads | runtime tick-local carrier | `do not touch now because behavior would drift` | Active wiring depends on this carrier. Future condition: an authorized unit-layer schema or shared service replaces the carrier. |
| `selected_target_by_unit` argument to `resolve_combat(...)` | carrier map | Makes combat execution consume target identity rather than choose it | runtime combat boundary | `do not touch now because behavior would drift` | It protects target selection != combat execution. Remove only if a new equivalent contract is approved. |
| `unit_desire_by_unit` | carrier map / mirror | Carries `desired_heading_xy` and `desired_speed_scale` into locomotion realization | runtime tick-local carrier | `do not touch now because behavior would drift` | This is the accepted locomotion input seam. Future condition: authorized unit-layer schema or physical module split. |
| `_compute_unit_desire_by_unit(...)` | helper / active mechanism block | Computes placeholder desire plus experimental Unit-local maneuver / back-off behavior when enabled | runtime Unit desire generation | `do not touch now because behavior would drift` | It is large, but splitting or pruning it now would change active experimental behavior or hide unsettled logic. Future condition: family accepted, retired, or separated by governance. |
| Inline `LOCAL_DESIRE_*` constants | transitional settings / internal constants | Hold current experimental behavior-line thresholds and strengths | runtime experimental branch | `keep but explicitly mark as testonly / experimental / transitional` | They are active only behind the test-only switch. If the family is promoted, expose a minimal settled set; if retired, delete with the family. |
| `runtime.physical.local_desire.experimental_signal_read_realignment_enabled` | transitional settings surface | Explicit switch for current experimental Unit-local maneuver / back-off family | test-only settings surface bridged into runtime | `keep but explicitly mark as testonly / experimental / transitional` | Name is stale, but it is the current explicit freeze/enable switch. Future condition: stable family rename or deletion after governance decision. |
| `local_desire_turn_need_onset` | transitional settings surface | Tunes the experimental local desire turn-need onset | test-only experimental settings | `keep but explicitly mark as testonly / experimental / transitional` | Still part of the frozen/experimental family. Delete only if the family is retired; migrate only if the family is promoted. |
| `local_desire_heading_bias_cap` | transitional settings surface | Caps experimental heading-side local bias | test-only experimental settings | `keep but explicitly mark as testonly / experimental / transitional` | Same condition as the local desire family. It must not be read as maintained doctrine. |
| `local_desire_speed_brake_strength` | transitional settings surface | Tunes experimental speed-side brake-only restraint | test-only experimental settings | `keep but explicitly mark as testonly / experimental / transitional` | Same condition as the local desire family. |
| `runtime.movement.v4a.engagement.engaged_speed_scale` | transitional settings surface | Applies per-Unit engaged movement-speed shaping | transitional Unit-side surface under historical v4a naming | `keep but explicitly mark as testonly / experimental / transitional` | Active wiring still uses it. Future condition: governance authorizes Unit-side settings-surface migration. |
| `runtime.movement.v4a.engagement.attack_speed_lateral_scale` | transitional settings surface | Applies attack-direction-aware speed allowance for lateral attack bearing | transitional Unit-side surface under historical v4a naming | `keep but explicitly mark as testonly / experimental / transitional` | Active wiring still uses it. Rename/migrate only with settings-surface migration. |
| `runtime.movement.v4a.engagement.attack_speed_backward_scale` | historical naming | Applies speed allowance when attack bearing is backward relative to current facing | transitional Unit-side speed shaping | `keep but explicitly mark as testonly / experimental / transitional` | It is not literal keep-front backward motion. Future condition: locomotion capability gate or settings-surface migration. |
| `_apply_v4a_transition_speed_realization(...)` | helper / active mechanism block | Realizes transitional per-Unit speed shaping during v4a transition movement | runtime locomotion / bridge realization | `do not touch now because behavior would drift` | It affects movement behavior directly. Future condition: authorized Unit-side owner migration or locomotion split. |
| `_apply_v4a_hold_speed_realization(...)` | helper / active mechanism block | Applies hold-state speed realization | runtime locomotion / bridge realization | `do not touch now because behavior would drift` | It affects hold behavior. Review only with the v4a hold/Unit-side migration line. |
| `_smoothstep01(...)` | helper | Shared bounded smoothing for gates and persistence curves | runtime utility | `do not touch now because behavior would drift` | It is used by active behavior gates. Delete/replace only if the mechanism family using it is retired or a no-drift proof is explicitly required. |
| `_MovementDiagSupport.build_pending(...)` local desire payload | debug / focus indicator surface | Packages minimal local desire fleet debug into runtime debug | runtime diagnostic surface | `keep but explicitly mark as testonly / experimental / transitional` | Current fields are experimental review aids, not behavior owners. Future condition: debug schema accepted or experimental family retired. |
| `test_run_execution._build_focus_indicator_payload(...)` local desire reads | debug / focus indicator surface | Copies local desire fleet debug into focus indicators for VIZ | harness / viewer handoff | `keep but explicitly mark as testonly / experimental / transitional` | It is a handoff surface, not runtime owner. Future condition: VIZ/debug contract stabilization. |
| `local_desire_diag_by_fleet` | carrier map / debug mirror | Mirrors fleet-level local desire indicators for debug export | runtime diagnostic mirror | `keep but explicitly mark as testonly / experimental / transitional` | Needed for Human review while behavior-line family remains experimental. Delete if the family is retired or debug contract no longer uses it. |
| `relation_violation_severity_fleet` internal variable | historical naming | Still derives compressed-line / give-ground severity inside the active formula family | runtime experimental branch | `defer until a named future condition is met` | The name is less current than the battle read, but it is internal active formula state. Future condition: formula family accepted/retired; then rename to a clearer restore/compression term or delete with the family. |
| `battle_relation_gap_raw` use in local maneuver | reused scalar family | Owns early guard / early no-crossing permission | fleet/reference signal reused by Unit realization | `do not touch now because behavior would drift` | Governance locked this role. Future changes require a new signal-role proposal. |
| `battle_relation_gap_current` use in local maneuver | reused scalar family | Supplies later compressed-line truth and late persistence band | fleet/reference signal reused by Unit realization | `do not touch now because behavior would drift` | Active back-off behavior depends on it. Future changes require a new behavior-line slice. |
| `battle_brake_drive_current` use in local maneuver | reused scalar family | Supplies later severity / urgency context | fleet/reference signal reused by Unit realization | `do not touch now because behavior would drift` | Active speed restraint depends on it. Future changes require behavior validation. |
| `battle_hold_weight_current` use in local maneuver | reused scalar family | Caps/coheres local maneuver inside fleet hold context | fleet/reference signal reused by Unit realization | `do not touch now because behavior would drift` | Active coherence behavior depends on it. Future changes require coupling review. |
| `near_contact_gate` and target-range localizers | auxiliary localizers | Localize maneuver response to selected-target range / contact conditions | Unit-local geometry auxiliary | `do not touch now because behavior would drift` | They are not strategic owners. Future condition: new localizer role proposal if Human sees over/under-localization. |
| `movement_direction_by_fleet.get(... last_target_direction ...)` | fallback-like read | Supplies a command direction when a per-fleet movement direction is absent | runtime movement default / no-command handling | `do not touch now because behavior would drift` | This is behavior-bearing no-command handling, not a silent target fallback. Review only with locomotion owner work. |
| `state.coarse_body_heading_current.get(... fallback ...)` in desire/bridge | fallback-like read | Initializes or preserves fleet-front heading when state lacks the current key | runtime movement state continuity | `do not touch now because behavior would drift` | Removing it could alter early tick or neutral behavior. Future condition: explicit required-heading invariant is established. |
| `_normalize_direction_with_fallback(...)` | helper / fallback-like utility | Normalizes a direction and falls back to a provided axis when degenerate | runtime/vector utility | `do not touch now because behavior would drift` | It is active in reference/heading construction. Future condition: degenerate-direction handling policy is replaced. |
| `_read_v4a_bridge_float(... fallback ...)` | fallback-like debug read | Lets focus indicators show `NaN`/fallback when bridge debug is absent | harness diagnostic surface | `defer until a named future condition is met` | It is debug-only but still masks missing diagnostic rows. Future condition: VIZ/debug contract decides whether absent diagnostics should fail or display `NaN`. |
| `local_desire_tick.get(... {})` / `local_desire_row.get(... NaN)` in focus export | fallback-like debug read | Displays `NaN` when experimental local desire debug is absent | harness / viewer handoff | `keep but explicitly mark as testonly / experimental / transitional` | Absence is expected when switch is false. Keep as diagnostic absence, not runtime fallback. |
| symmetric movement debug merge for `v4a_bridge` / `local_desire` | carrier mirror / debug compatibility | Merges per-fleet debug rows from symmetric movement variants | runtime diagnostic mirror | `defer until a named future condition is met` | Touching could alter debug truth in symmetric runs. Future condition: debug ownership is narrowed or symmetric movement debug contract is rewritten. |
| `settings_accessor` low-level default-capable getters | fallback-like API | Expose generic settings reads with caller-provided defaults | harness utility layer | `defer until a named future condition is met` | Scenario builders now use `_require_present` for required active values. Future condition: separate settings API simplification line. |
| `_require_present(...)` in scenario builder | fail-fast helper | Converts required active settings into explicit errors | harness / settings validation | `do not touch now because behavior would drift` | It enforces no-silent-fallback discipline. Remove only if a stronger validation layer replaces it. |
| display fallbacks such as avatar/color fallback | fallback-like read | Preserve presentation when optional display metadata is missing | harness presentation / non-runtime | `defer until a named future condition is met` | Not part of active mechanism truth. Future condition: separate presentation-surface cleanup. |
| historical `v3` cohesion naming in cohesion helpers | historical naming | Names older cohesion helper family still used by current skeleton code | runtime cohesion internals | `defer until a named future condition is met` | Outside the active maneuver/back-off cleanup area. Future condition: dedicated cohesion owner/naming audit. |

## 4. Smallest Safe Deletions Identified

The next safe deletion candidates are not runtime mechanism formulas. They are
reader-facing stale surfaces:

1. VIZ display row for `relation_violation_severity`
2. VIZ debug docs that still describe `relation_violation_severity` as current
3. Any leftover references that imply the current debug indicator set is
   `early_embargo_permission + relation_violation_severity`

Expected effect:

- no battle behavior change
- clearer Human debug read
- fewer stale indicators

Required caution:

- replace with the already-current minimal runtime/test_run debug set rather
  than adding a larger indicator catalog

## 5. Items Not Ready For Deletion

The biggest code bodies are not automatically deletion candidates:

- `_compute_unit_desire_by_unit(...)`
- `_apply_v4a_transition_speed_realization(...)`
- symmetric movement diagnostic merge
- v4a engagement speed-shaping surfaces

Reason:

- they are behavior-bearing or active diagnostic handoff surfaces
- deleting or splitting them now would either drift behavior or reopen owner
  boundaries before Governance has chosen the next line

## 6. Ledger Conclusion

Subtraction work is not finished.

The current best next subtraction move is a reader-facing cleanup, not a
runtime formula cleanup:

- remove/replace stale VIZ `relation_violation_severity` surfaces
- keep runtime behavior untouched
- keep experimental family explicitly test-only / transitional

Runtime-side subtraction should wait until one of these conditions is met:

- the Unit-local maneuver / back-off family is retired
- the family is promoted and given a stable maintained surface
- Governance authorizes a Unit-side settings migration
- Governance authorizes a locomotion capability gate or module split
