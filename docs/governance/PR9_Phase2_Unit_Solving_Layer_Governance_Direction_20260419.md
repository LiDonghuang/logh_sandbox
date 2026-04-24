# PR9 Phase II Unit Solving Layer Governance Direction 20260419

Source export:

- PR #9 governance comment
- April 19, 2026 UTC
- `Governance directive - PR #9 Phase II direction lock (unit solving layer carrier)`
- Source URL: `https://github.com/LiDonghuang/logh_sandbox/pull/9#issuecomment-4275383388`

Export intent:

- repo-side stable governance reference
- no broader implementation claim is made by this export itself

## Action Mode

- `[BRANCH + PR]`
- Workflow / protocol docs update: no
- APP local-file sync required: yes

## Scope And Authority

- This is the formal governance direction for PR #9 after the boundary-lock endpoint.
- This is a long-horizon governance direction, not an authorization for immediate broad mechanism implementation.
- This is not a cleanup instruction.
- This is not a viewer doctrine instruction.
- This is not an authorization to reopen Formation-side patch growth.
- Human remains the final sequencing authority.

## I. Phase Determination

- PR #9 Phase I is judged complete at the boundary-lock level.
- The completed endpoint is the already-clarified narrow endpoint:
  1. heading-owner boundary relock
  2. explicit Formation coarse-body boundary lock
  3. locomotion responsibility separation note
- Therefore the next natural carrier is no longer "continue patching Formation."
- PR #9 Phase II should now be read as:
  - unit solving layer first bounded carrier
  - with simplified targeting as part of the unit layer
  - with locomotion realization as the lower realization layer

## II. Long-Term Direction Lock

- Formation remains coarse-body only.
- Fleet heading / fleet front remains upstream, fleet-level, runtime-owned.
- Unit becomes the minimal fighting-body solving layer.
- Low-level locomotion becomes more real.
- Unit-level targeting remains aggressively simplified.
- No-O(n^2)-by-default remains a hard constraint.
- All of the above should be read as preparation for later true 3D fleet/body/combat architecture rather than further 2D patch accumulation.

## III. Core Structural Read For Phase II

### A. Fleet layer and unit layer must now be read as distinct primary layers

- Fleet layer owns:
  - objective direction ownership
  - coarse-body / battle-geometry ownership
  - fleet front / fleet heading ownership
  - formation reference ownership
- Unit layer owns:
  - local target read
  - local combat adaptation / maneuver-for-fire read
  - desired heading generation
  - desired speed generation
  - unit-facing realization intent
- Low-level locomotion owns:
  - bounded realization of heading/speed intent under physical limits

### B. Fleet layer internal separation must remain explicit

- Keep distinct:
  1. objective / "where to go"
  2. coarse-body / battle geometry
  3. formation reference / "how to arrange reference body"
  4. final legality / projection / spacing enforcement
- Do not collapse objective, formation reference, and final legality into one owner again.

### C. Unit layer internal separation should now become explicit

- Keep distinct:
  1. local perception read
  2. target choice
  3. combat adaptation / engagement mode read
  4. desire generation
  5. locomotion realization
- Do not read unit solving as a large behavior tree.
- Mode should be read only as solving-assist semantics, not as a heavy doctrine/state-machine system.

## IV. Combat Adaptation Seam

- Governance explicitly locks that the Phase II design must include a combat adaptation seam.
- Correct read:
  - target choice is not the same as battle behavior choice
  - formation is not a hard owner that must remain fully intact throughout combat
  - units may locally loosen / deviate / partially de-form during combat to obtain firing solutions
  - local combat adaptation must not cause owner flow-back into Formation
- Therefore:
  - local de-formation / local battle adaptation is acceptable
  - owner flow-back from unit combat behavior into Formation doctrine is not acceptable
- Do not attempt to encode combat-time de-formation by pushing more meaning into FR or other personality parameters at this stage.

## V. Shared Spatial Service

- Local visible-object enumeration should be treated as shared runtime infrastructure.
- It should be runtime-owned shared spatial service.
- It should provide bounded local visible enemy enumeration for unit solving.
- It is infrastructure, not targeting doctrine.
- It should not itself own:
  - target scoring policy
  - target merit ranking doctrine
  - combat adaptation doctrine
- Do not allow targeting, movement, and combat stages to each silently grow their own parallel neighborhood/full-search owners.

## VI. Targeting Ownership

- Target ownership should move to the unit layer.
- `resolve_combat()` should not remain the long-term owner of primary target selection.
- The correct target carrier for the near-term design is:
  - minimal
  - same-tick
  - non-heavy-memory
- Preferred read:
  - unit layer selects target
  - same-tick minimal `selected_target_id` carrier is allowed
  - no heavy long-lived lock-on / memory system is required here
- Therefore the design should avoid two opposite mistakes:
  1. no heavy persistent target doctrine
  2. no fallback where `resolve_combat()` silently re-owns target selection

## VII. Simplified Unit-Level Targeting Doctrine

- The simplified target-choice doctrine remains:
  - read local visible enemy objects from shared spatial service
  - keep only those inside the unit's forward fire cone
  - choose the nearest valid one
- Parameter values may remain configurable.
- This directive does not re-freeze any specific default value.
- Do not reopen:
  - full search as default language
  - targeting-owned hash doctrine as doctrine owner
  - expected-damage merit ranking as default owner language
  - global target optimization as normal runtime behavior

## VIII. Combat-Stage Responsibility After Target-Owner Reroot

- Long-term intended read for `resolve_combat()`:
  - validity re-check of same-tick selected target
  - fire permission check
  - in-range / in-cone confirmation
  - damage / HP resolution
  - engaged-status update
- Do not keep `resolve_combat()` as the hidden main targeting-doctrine owner after Phase II direction lock.

## IX. Locomotion Direction Lock

- Low-level locomotion must continue toward real realization rather than Formation-side compensation.
- Upper layers should output:
  - desired heading
  - desired speed
- Low-level locomotion should realize them under bounded constraints such as:
  - max acceleration
  - max deceleration
  - max turn rate
  - speed-turn coupling
- Governance explicitly clarifies:
  - locomotion should not be read as "turn-rate limiting only"
  - speed coordination / pace realization is a first-class part of the seam
- Do not continue relying on Formation-side heading/speed patches to compensate for unreal locomotion.
- Guiding phrase remains valid:
  - Formation becomes dumber
  - locomotion becomes truer

## X. Facing / Movement / Fleet Front Separation

- The following three layers must remain conceptually distinct:
  1. fleet front axis
  2. unit facing
  3. actual velocity / movement direction
- They may remain lightly coupled in realization.
- They must not collapse into one owner again.
- In particular:
  - fleet front must not be redefined directly by realized unit velocity or unit-orientation average
  - unit facing is the correct owner for fire-cone semantics
  - velocity is not the owner of fleet front or fire doctrine

## XI. Execution / Test Run Boundary

- `test_run` / execution should not remain a mechanism owner for unit doctrine or locomotion doctrine.
- It should remain limited to:
  - scenario / fixture
  - observer packaging
  - replay / debug readout
  - harness validation
- Do not let unit solving doctrine re-spread into test harness surfaces.

## XII. 3D Reservation

- Governance explicitly records that the true long-term target is later 3D fleet/body/combat architecture.
- Therefore Phase II design must preserve future upgrade room for:
  - fleet frame / formation frame
  - principal extents / anisotropy-style body measures
  - 3D-compatible reference ownership
- Do not hard-freeze 2D width-depth semantics into future unit/combat ownership.
- Do not let current 2D patch semantics become future architectural owners.
- Current work should be read as preparing clean fleet/unit/locomotion seams for later 3D growth.

## XIII. Retreat Policy Status

- Retreat policy remains important and will later matter for deeper formation/combat realism.
- However it is not activated as an immediate implementation target in this Phase II opening wave.
- Correct current read:
  - reserve seam
  - do not activate full mechanism now
- If revisited later, the correct direction remains:
  - distinguish `back_off_keep_front`
  - distinguish `turn_away_retirement`
  - fleet/coarse-body decides family first
  - unit/locomotion realizes family second
- Do not let retreat-policy activation interrupt the current Phase II owner/path clarification wave.

## XIV. Computational Hard Constraint

- No-O(n^2)-by-default remains non-negotiable.
- Explicitly rejected as default language:
  - all-pairs interaction as normal operation
  - full search as normal targeting owner
  - global combinatorial reassignment
  - every-tick optimal remap
  - repeated global geometry solve
- Preferred computational language remains:
  - fleet-level low-dimensional state
  - per-unit local response
  - shared spatial service
  - O(n) / O(nk) bounded local neighborhood organization
- Read this as both a performance and realism constraint for future larger fleet counts and multi-fleet battles.

## XV. Immediate Required Deliverable

- Engineering is not being authorized here to push broad implementation slices immediately.
- Engineering is instructed first to export this governance direction into a repo-side markdown document.
- Preferred document path:
  - `docs/governance/PR9_Phase2_Unit_Solving_Layer_Governance_Direction_20260419.md`
- Document intent:
  - long-horizon governance direction
  - repo-side stable reference for later APP local-file sync
- The exported markdown should preserve the semantics of this directive rather than reinterpret it.
- After export, Engineering should report back in PR #9 with:
  - the exact repo-relative path
  - a short confirmation that no broader implementation claim is being made by the export itself

## XVI. Recommended Next Document Sequence After Export

- After the governance-direction markdown export is complete, the preferred next document order is:
  1. `unit structure / contract note`
  2. `simplified unit targeting note`
  3. `locomotion follow-up note`
  4. only then possible bounded implementation-slice proposal
- Continue to require:
  - one essential owner/path change at a time
  - design/review note before implementation
  - Human confirmation before push/report of broader mechanism work

## Shortest Conclusion

- PR #9 Phase I is closed at the boundary-lock endpoint.
- PR #9 Phase II is now locked as the first bounded carrier for the unit solving layer.
- Formation remains coarse-body only.
- Combat adaptation seam is now explicitly required.
- Target owner should move to the unit layer via same-tick minimal carrier.
- Shared spatial service is the required infrastructure seam.
- Locomotion must become truer in both heading and speed realization.
- 3D future-upgrade room must be preserved from now on.
- Export this directive to repo-side markdown first; do not over-read this document as immediate authorization for broad implementation.
