# PR9 Phase II Unit Structure Contract Note 20260419

## Scope

- Type: structural contract note
- Phase context: PR #9 Phase II opening wave
- Status: note only, no mechanism implementation in this document
- Purpose: make the fleet layer, unit solving layer, locomotion layer, and combat execution stage explicit before later bounded implementation work

## Input Governance Anchor

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md)

## Why This Note Exists

The governance direction already locks the Phase II read at a high level.

This note does not restate that governance in full.
Instead, it records the minimum structural contract needed so later work can:

- keep current active owners truthful
- make the new unit-layer seam explicit
- avoid owner relapse during later targeting and locomotion follow-up work

## Current Active Path Read

This section describes current code truth, not desired future end-state.

### 1. Tick order still ends in combat-owned target choice

Current visible step order in `runtime/engine_skeleton.py` is:

- `evaluate_cohesion()`
- `evaluate_target()`
- `evaluate_utility()`
- movement integration
- contact impedance / fixture clamp
- `resolve_combat()`

Therefore target choice has not yet been re-rooted into a distinct unit solving stage.

### 2. Fleet-level active carriers already exist in runtime state

Current fleet-level carriers in `runtime/runtime_v0_1.py` `BattleState` are:

- `last_target_direction`
- `coarse_body_heading_current`
- `movement_command_direction`

These are the current active fleet/coarse-body carrier family.
This note does not rename them.

### 3. Heading owner relock is already active

Current active read in `runtime/engine_skeleton.py::_prepare_v4a_bridge_state(...)`:

- `BattleState.coarse_body_heading_current` is the maintained runtime heading owner
- `bundle["movement_heading_current_xy"]` is a mirror / bridge / diagnostic surface

This boundary should remain intact during Phase II.

### 4. `resolve_combat()` still carries the target-owner burden

Current active read in `runtime/engine_skeleton.py::resolve_combat(...)`:

- local enemy enumeration happens there
- forward fire-cone filtering happens there
- nearest valid enemy choice happens there
- `engaged` / `engaged_target_id` writeback happens there
- damage and HP resolution happen there

Therefore the current active path still mixes:

- target choice
- contact / fire permission
- damage execution
- engagement-state writeback

This is the main Phase II owner tension.

### 5. Locomotion seam exists, but remains downstream of current combat state

Current active read in `runtime/engine_skeleton.py`:

- `_prepare_v4a_bridge_state(...)` maintains fleet heading and movement-command carriers
- `_apply_v4a_transition_speed_realization(...)` and `_apply_v4a_hold_speed_realization(...)` provide bounded speed realization work
- `_apply_v4a_transition_speed_realization(...)` still reads `engaged_target_id` for attack-direction speed shaping

So the locomotion seam already exists, but it is not yet fed by an explicit Phase II unit solving contract.

## Phase II Structural Contract

This section describes the intended contract boundary for later notes and bounded implementation slices.
It is not a claim that the active runtime already behaves this way.

### A. Fleet layer

Fleet layer owns:

- objective direction / where the fleet should go at coarse scale
- fleet front / coarse-body heading memory
- formation reference arrangement
- coarse legality / spacing boundary inputs

Fleet layer does not own:

- per-unit target choice
- per-unit combat adaptation choice
- final per-unit desired heading
- final per-unit desired speed

### B. Unit solving layer

Unit solving layer owns:

- local perception read usage
- target choice
- local combat adaptation read
- desired heading generation
- desired speed generation

Unit solving layer receives upstream context from:

- fleet-level reference direction and coarse-body context
- formation/reference arrangement context
- runtime-provided local spatial visibility service

Unit solving layer outputs downstream intent to:

- low-level locomotion
- combat execution stage

This note intentionally does not freeze the exact target-carrier field name.
That belongs in the next targeting note.

### C. Low-level locomotion layer

Low-level locomotion owns:

- bounded realization of desired heading
- bounded realization of desired speed
- physical-limit style realization behavior

Low-level locomotion does not own:

- target doctrine
- fleet front doctrine
- combat adaptation doctrine

This note also preserves the existing conceptual separation between:

- fleet front axis
- unit facing
- actual movement / velocity direction

### D. Combat execution stage

Combat execution owns:

- same-tick target validity re-check
- in-range / in-cone confirmation
- fire permission
- damage / HP resolution
- engagement-status writeback

Combat execution does not remain the long-term primary owner of target selection.

### E. Shared spatial service

Shared spatial service is a runtime infrastructure seam.

It may provide:

- bounded local visible enemy enumeration
- local neighborhood read support for unit solving

It must not itself own:

- target scoring doctrine
- combat adaptation doctrine
- movement doctrine

The exact interface and minimal same-tick target carrier remain for the targeting note.

## Contract Consequences For Later Work

The next notes should follow from this contract in order:

1. simplified unit targeting note
2. locomotion follow-up note
3. only then a bounded implementation-slice proposal

The first bounded implementation candidate should still be read as:

- minimal target-owner reroot away from `resolve_combat()`

## Non-Goals In This Note

This note does not authorize:

- retreat-policy activation
- a new heavy unit state machine
- broad Formation-side patch growth
- harness-side doctrine growth in `test_run`
- broad viewer-driven changes

## Bottom Line

Current code truth remains:

- fleet-level coarse-body carriers already exist
- heading owner relock is active
- `resolve_combat()` is still the current target owner in practice
- locomotion seam exists but is not yet fed by an explicit unit solving contract

The correct next move remains document-first:

- keep this structure note as the contract baseline
- follow with the targeting note before any bounded implementation slice
