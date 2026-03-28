# Step 3 3D Mapping Minimum Contract Structural Draft Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 mapping line second-carrier structural-draft-only minimum-contract opening
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: narrows the minimum contract surface for mapping between formation reference and legality without opening legality, movement, runtime integration, or viewer ownership
Mapping Impact: minimum contract draft only; remains pre-implementation and keeps legality closed
Governance Impact: advances mapping beyond pure scope confirmation while remaining smaller than implementation design
Backward Compatible: yes

Summary
- This turn advances mapping from pure scope confirmation to a minimum contract structural draft.
- A full stabilized field table is still premature; the smallest clean contract surface is a very small contract-question set.
- That minimum contract surface must still express assignment ownership, weak remapping/reflow allowance language, and an implementation-neutral output anchor.
- `expected_position_map` or equivalent may be proposed as the contract-level output anchor only under a weak, non-committal reading.
- Legality, movement, runtime integration, viewer ownership, and implementation remain explicitly closed.

## 1. Minimum Mapping Contract Surface

The minimum mapping contract surface should express only the following:

- that mapping owns assignment from stable unit identity to reference slots
- whether remapping/reflow is allowed in principle
- what contract-level reference-assignment output surface mapping exposes
- what remains explicitly outside mapping

This is the smallest contract surface that still makes the mapping layer legible as a layer distinct from both formation reference and legality.

It stays narrower than implementation because it does not choose runtime touchpoints, algorithms, or hook locations.

## 2. Candidate Minimum Fields Or Equivalent Contract-Question Set

The cleanest bounded result for this turn is not yet a frozen field table.

Instead, the minimum contract is best stated as a very small contract-question set:

- assignment basis question
  - how stable unit identity is related to reference slots

- remapping allowance question
  - whether remapping/reflow is allowed in principle

- output-surface question
  - what reference-assignment output surface the mapping layer exposes

This is smaller and safer than prematurely freezing a wider field list.

If a later field table is introduced, it should remain no larger than what is needed to answer those three contract questions.

Debug or inspection-only emission controls do not belong in the minimum mapping contract surface.

## 3. Weak Reading Of Remapping / Reflow

If remapping/reflow is retained in the contract at all, it must remain weak:

- ownership / allowance language only
- no trigger logic
- no runtime policy freeze
- no execution algorithm

At this turn, remapping/reflow should be read only as:

- whether that class of question belongs to mapping in principle

It must not be read as:

- when reassignment occurs
- what event causes reassignment
- how reassignment is executed
- what runtime subsystem owns the execution path

## 4. Weak Reading Of `expected_position_map` Or Equivalent Output Anchor

`expected_position_map` or equivalent may be proposed as the contract-level output anchor only under a weak reading:

- implementation-neutral output-surface language only
- no code-path commitment
- no hook-location commitment
- no runtime-type freeze

The bounded intended reading is:

- mapping should expose a reference-assignment result surface
- that surface should remain downstream of formation reference
- that surface should remain upstream of legality

The repo already contains `expected_position_map` as a useful existing term anchor, but this note does not elevate that name into a finalized runtime contract.

## 5. Explicit Exclusions

This minimum-contract opening does not open:

- legality / projection semantics
- collision / boundary semantics
- movement semantics
- viewer ownership semantics
- implementation-path commitment

More specifically, this note does not authorize:

- feasibility
- projection
- collision handling
- boundary clipping
- legality override
- fallback placement logic
- steering behavior
- temporal response
- turning dynamics
- inertia semantics
- doctrine / posture movement reading
- rendering ownership
- `viz3d_panda/` semantic authority
- camera/display attributes
- glyph/display/layout visualization semantics
- runtime touchpoint inventory
- runtime integration sketch
- code path proposal
- hook design
- execution algorithm
- performance strategy
- target preference semantics
- doctrine / posture semantics
- tactic language
- combat meaning

## 6. Boundary Bottom Line

The correct bounded reading remains:

- mapping contract answers assignment-structure contract only
- mapping remains downstream of formation reference and upstream of legality
- legality remains closed
- implementation remains closed

That is sufficient for this turn.

No legality opening, runtime integration design, or viewer-semantic expansion is confirmed here.
