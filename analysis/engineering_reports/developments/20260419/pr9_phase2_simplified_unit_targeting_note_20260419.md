# PR9 Phase II Simplified Unit Targeting Note 20260419

## Scope

- Type: targeting ownership and contract note
- Phase context: PR #9 Phase II opening wave
- Status: note only, no mechanism implementation in this document
- Purpose: define the simplified unit-level target owner and same-tick target carrier read before any bounded implementation slice

## Input Anchors

- [docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md](E:/logh_sandbox/docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_solving_feasibility_and_plan_20260419.md)
- [analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md](E:/logh_sandbox/analysis/engineering_reports/developments/20260419/pr9_phase2_unit_structure_contract_note_20260419.md)

## Why This Note Exists

The Phase II structure note already separates:

- fleet layer
- unit solving layer
- locomotion layer
- combat execution stage

This note narrows only one seam:

- target ownership

It records what current code truth is, and what the Phase II simplified target contract should become.

## Current Active Path Read

This section describes current code truth, not the desired future contract.

### 1. Fleet-level `evaluate_target()` is still coarse and fleet-owned

Current active read in `runtime/engine_skeleton.py::evaluate_target(...)`:

- it computes one fleet-level direction from own centroid toward the nearest enemy to that centroid
- it writes fleet-level carriers:
  - `last_target_direction`
  - `movement_command_direction`

This stage is still coarse-body / fleet-direction work.
It is not a unit-level target owner.

### 2. `resolve_combat()` is still the actual per-unit target selector

Current active read in `runtime/engine_skeleton.py::resolve_combat(...)`:

- it builds a combat local-neighborhood spatial hash
- it enumerates nearby visible enemies during combat resolution
- it applies forward fire-cone filtering
- it chooses the nearest valid enemy
- it writes `engaged` and `engaged_target_id`
- it applies damage / HP resolution

Therefore current code truth is that per-unit target choice still materially happens inside `resolve_combat()`.

### 3. Current active target-related unit carrier is engagement-state oriented

Current active unit carrier in `runtime/runtime_v0_1.py` is:

- `UnitState.engaged_target_id`

Its current role is contact / engagement-state writeback.
It is not yet an explicit same-tick unit-solving target-selection carrier.

### 4. Shared spatial enumeration is present, but not yet separated as its own explicit seam

Current active read:

- local-neighborhood enumeration already exists inside `resolve_combat()`
- the search mechanism is currently coupled to combat-stage ownership

So the infrastructure capability exists, but the owner boundary is not yet explicit.

## Phase II Simplified Targeting Contract

This section records the intended contract for later bounded implementation work.
It is not a claim that the active runtime already behaves this way.

### A. Target owner moves to the unit solving layer

Target ownership should move from combat execution to the unit solving layer.

Correct intended read:

- fleet layer remains upstream and coarse
- unit solving layer performs per-unit target choice
- combat execution consumes that same-tick result

### B. Minimal same-tick target carrier

The near-term target carrier should be:

- minimal
- same-tick
- non-heavy-memory

Preferred contract read:

- unit solving produces `selected_target_id`
- `selected_target_id` is the minimal same-tick carrier passed to combat execution
- this carrier is not a long-lived lock-on doctrine
- this carrier is not a persistent target-memory subsystem

This note freezes the seam concept, not the final code-placement detail.
Exact schema placement should stay local to the later bounded implementation slice.

### C. Simplified target-choice doctrine

The simplified unit-level target doctrine should remain:

- read locally visible enemy objects from shared spatial service
- keep only enemies inside the unit forward fire cone
- choose the nearest valid enemy

This note does not reopen:

- expected-damage ranking as the default target doctrine
- global target optimization
- full-search-as-default language
- heavy target memory or target history systems

### D. Shared spatial service contract

Shared spatial service may provide:

- bounded local visible enemy enumeration
- same-tick local neighborhood access for unit solving

Shared spatial service must not own:

- target scoring doctrine
- target ranking doctrine
- combat adaptation doctrine
- combat execution doctrine

Its role is infrastructure-only.

### E. Combat-stage responsibility after reroot

After target ownership is rerooted, `resolve_combat()` should be read as:

- validity re-check of `selected_target_id`
- in-range confirmation
- in-cone confirmation
- fire permission check
- damage / HP resolution
- engagement-status writeback

`resolve_combat()` should not silently re-select a different target as fallback and thereby remain the real owner.

## Boundary Warnings

This targeting note explicitly rejects two opposite mistakes:

1. adding a heavy persistent target-memory doctrine too early
2. leaving target choice in `resolve_combat()` while merely renaming the result

Either mistake would violate the intended Phase II owner reroot.

## Deferred Details

This note intentionally defers:

- exact storage location of `selected_target_id`
- any optional companion carrier beyond the minimal target id
- combat adaptation logic beyond target choice
- retreat-policy interaction
- parameter-default refreezing

Those belong to later bounded implementation and later notes only if needed.

## Recommended First Implementation Read

When implementation is later opened, the smallest correct targeting slice should be:

- introduce same-tick unit target selection before combat execution
- pass minimal `selected_target_id` into combat execution
- reduce `resolve_combat()` to re-check / fire / damage / engagement work

## Bottom Line

Current code truth remains:

- fleet-level direction is still coarse and fleet-owned
- `resolve_combat()` is still the active per-unit target selector
- `engaged_target_id` is currently engagement-state oriented, not yet the explicit unit-solving carrier

The intended Phase II simplified targeting contract is:

- unit solving owns target choice
- shared spatial service provides bounded local visibility only
- `selected_target_id` is the minimal same-tick carrier
- combat execution must not silently re-own target selection
