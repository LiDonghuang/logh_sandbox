# Major Change Record

Date: 2026-04-11
Status: Active independent record
Purpose: Record maintained mainline retirements and interface narrowing without rewriting historical `analysis`.

## Item 1 - `intent_unified_spacing_v1` retired from the maintained hostile-contact surface

Date: 2026-04-11
Scope: `test_run` harness / test-only hostile-contact execution surface
Status: Implemented

Summary:
- The maintained test-only hostile-contact selector no longer exposes `intent_unified_spacing_v1`.
- The active selector surface is now `off | hybrid_v2`.
- The maintained hot path no longer applies the retired pre-movement intent-penetration bias / post-movement restore sequence.

Effect boundary:
- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `repo_context.md`
- `system_map.md`

Interface effect:
- `runtime.physical.contact.hostile_contact_impedance.active_mode`
  - retired value: `intent_unified_spacing_v1`
  - maintained values: `off | hybrid_v2`
- The retired nested settings block `intent_unified_spacing_v1.*` was removed from the maintained active settings surface.

## Item 2 - `movement_model=baseline` retired from the maintained public selector

Date: 2026-04-11
Scope: `test_run` harness / maintained movement selection interface
Status: Implemented

Summary:
- The maintained public movement selector no longer accepts `baseline` as an alias.
- The maintained public selector is now `v4a` only.
- Scenario/execution carrier naming was narrowed from `movement_model_effective` / `model_effective` to direct `movement_model` / `model`.

Effect boundary:
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_entry.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `repo_context.md`
- `system_map.md`

Interface effect:
- `runtime.selectors.movement_model`
  - retired value: `baseline`
  - maintained value: `v4a`
- Prepared-summary readout now uses `movement_model` rather than `movement_model_effective`.

## Item 3 - `PersonalityParameters` decoupled from runtime state and retained as scenario-level high-level metadata

Date: 2026-04-11
Scope: maintained runtime schema + `test_run` scenario build surface
Status: Implemented

Summary:
- `FleetState` no longer carries `PersonalityParameters`.
- The maintained `test_run` scenario path still resolves archetype-derived `PersonalityParameters`, but keeps them on the prepared high-level interface rather than runtime state.
- Yang metatype sampling remains available as scenario-level prepared metadata only; maintained runtime/tick mechanisms do not consume it.

Effect boundary:
- `runtime/runtime_v0_1.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_entry.py`
- `test_run/test_run_v1_0.runtime.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`
- `archetypes/metatype_settings.json`
- `repo_context.md`
- `system_map.md`

Interface effect:
- Removed maintained runtime schema surface:
  - `FleetState.parameters`
- Restored maintained high-level scenario interface:
  - `runtime.metatype.random_seed`
  - prepared payload keys:
    - `fleet_a_parameters`
    - `fleet_b_parameters`
    - `fleet_parameters`
  - prepared summary key:
    - `effective_metatype_random_seed`

Behavior intent:
- Keep active runtime state limited to maintained battle/movement needs.
- Preserve Yang/personality sampling only as cold high-level metadata so a future personality return can rebuild mechanism semantics without inheriting the old runtime-state carrier.

## Item 4 - `integrate_movement()` owner returned to runtime

Date: 2026-04-11
Scope: maintained runtime/harness movement boundary
Status: Implemented

Summary:
- The maintained v4a movement hot-path is again owned by `runtime/engine_skeleton.py::integrate_movement()`.
- `TestModeEngineTickSkeleton` no longer overrides `integrate_movement()`.
- `test_run` still prepares battle/fixture bundles, but those bundles now act as carriers into runtime-owned movement pre-shaping rather than a second movement owner.

Effect boundary:
- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`

Interface effect:
- Removed maintained harness override:
  - `TestModeEngineTickSkeleton.integrate_movement()`
- Active carrier inputs remain:
  - `TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET`
  - `TEST_RUN_FIXTURE_REFERENCE_BUNDLE`
  - `TEST_RUN_FIXTURE_CFG`

Behavior intent:
- Keep `test_run` honest as bundle-preparation / harness support rather than a second movement hot-path owner.
- Preserve current maintained v4a semantics while narrowing the runtime/harness owner split.

## Item 5 - canonical tick-stage ownership narrowed back to runtime

Date: 2026-04-11
Scope: maintained runtime/harness tick-stage boundary
Status: Implemented

Summary:
- The maintained hot-path stage owners for `step()` and `evaluate_target()` now live in `runtime/engine_skeleton.py`.
- `TestModeEngineTickSkeleton` no longer overrides the canonical stages `step()` or `evaluate_target()`.
- The maintained `test_run` candidate engine now acts as a support/helper surface for v4a bundle/reference preparation rather than a second canonical tick-stage owner.

Effect boundary:
- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`

Interface effect:
- Removed maintained harness stage overrides:
  - `TestModeEngineTickSkeleton.step()`
  - `TestModeEngineTickSkeleton.evaluate_target()`
- Active support surface retained in `test_run`:
  - `_resolve_v4a_reference_surface(...)`
  - bundle carriers such as `TEST_RUN_BATTLE_RESTORE_BUNDLES_BY_FLEET`
  - fixture carrier `TEST_RUN_FIXTURE_CFG`

Behavior intent:
- Collapse the long-standing "runtime canonical stage + harness active stage" split that accumulated during experimental development.
- Keep maintained battle/fixture support explicit without leaving `test_run` as a parallel tick owner.

## Item 6 - maintained active candidate engine returned to `EngineTickSkeleton`

Date: 2026-04-11
Scope: maintained `test_run` execution owner boundary
Status: Implemented

Summary:
- `run_simulation()` now directly instantiates `EngineTickSkeleton`.
- `TestModeEngineTickSkeleton` remains only as a cold compatibility shell for older analysis references.
- `_resolve_v4a_reference_surface(...)` now lives in runtime with the rest of the maintained v4a bridge support.

Effect boundary:
- `runtime/engine_skeleton.py`
- `test_run/test_run_execution.py`

Interface effect:
- Active maintained instantiation:
  - `EngineTickSkeleton(...)`
- `TestModeEngineTickSkeleton` is no longer part of the maintained execution hot path.

Behavior intent:
- Finish the active-path owner return that began with `integrate_movement()`, then continued through `step()` and `evaluate_target()`.
- Leave older analysis imports non-blocking without keeping `test_run` as a second maintained engine implementation.
