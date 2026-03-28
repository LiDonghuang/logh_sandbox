# Step 3 3D Mapping Opening Scope Confirmation Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 next-carrier structural-draft-only mapping opening scope confirmation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: confirms the structural role of mapping between formation reference and legality without opening legality, movement, runtime integration, or viewer ownership
Mapping Impact: scope confirmation only; no minimum field freeze and no implementation opening
Governance Impact: opens the mapping layer only as a bounded pre-implementation carrier
Backward Compatible: yes

Summary
- This turn confirms mapping as the downstream assignment-structure layer between formation reference and legality.
- This opening is a scope-confirmation carrier, not a minimum field freeze.
- The minimum mapping question set is limited to assignment ownership, remapping/reflow ownership as a scope question, and the candidate output-surface question.
- `expected_position_map` or equivalent may be discussed only as a scope-definition output-surface anchor, not as an implementation commitment.
- Legality, movement, runtime integration, viewer ownership, and implementation design remain explicitly closed.

## 1. Mapping Ownership

The mapping layer is confirmed as owning:

- assignment from stable unit identity to reference slots
- the layer boundary between formation reference and legality

The intended layer order remains:

- objective
- formation reference
- mapping
- legality

This means:

- objective remains upstream and already answers where to go
- formation reference remains upstream and answers reference geometry only
- mapping answers assignment structure only
- legality remains downstream and closed in this turn

## 2. Minimum Mapping Question Set

Because the repo currently provides mapping-role clarification without an equally stabilized minimum field table, this opening should confirm only the minimum structural question set:

- whether stable identity-to-slot assignment belongs to mapping
- whether reflow/remapping belongs to mapping in principle
- what output surface mapping is expected to produce
- what remains explicitly outside mapping

Under the current bounded reading, the mapping layer may answer:

- how stable unit identity maps to reference slots
- whether reflow/remapping is allowed in principle
- how `expected_position_map` or equivalent reference-assignment output is produced

This turn does not freeze those questions into a stable minimum field list.

It only confirms that these are the correct structural questions for the mapping layer.

## 3. Weak Reading Of Reflow / Remapping

If reflow or remapping is discussed in this opening, it must be read only as scope-definition language:

- does this class of question belong to mapping at all
- not how it is implemented
- not when it triggers
- not what runtime mechanism performs it

At this turn, reflow/remapping must not become:

- implementation logic
- runtime trigger design
- execution algorithm
- policy freeze

The weak reading is:

- reflow/remapping is only a question of mapping-layer ownership in principle
- not a decision that a runtime remapping mechanism is now designed or authorized

## 4. Candidate Output-Surface Reading

The candidate output-surface reading for this opening is:

- `expected_position_map` or equivalent reference-assignment output

This should be read only at scope-definition level.

It means:

- mapping is expected to produce a reference-assignment result surface
- that surface is conceptually downstream of formation reference
- that surface remains upstream of legality

It does not mean:

- the exact runtime type is frozen
- the exact code path is chosen
- the exact hook location is chosen
- implementation is authorized

The repo already contains `expected_position_map` as an existing term anchor, but this note does not elevate that term into a finalized implementation contract.

## 5. Explicit Exclusions

This mapping-opening scope confirmation does not open:

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

- mapping answers assignment structure only
- mapping sits downstream of formation reference and upstream of legality
- legality remains closed
- implementation remains closed

That is sufficient for this turn.

No legality opening, runtime integration design, or viewer-semantic expansion is confirmed here.
