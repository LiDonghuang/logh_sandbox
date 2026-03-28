# Step 3 3D Legality Runtime Integration Envelope Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line direct-push pre-implementation runtime-integration-envelope consolidation
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: consolidates the legality-side contract, interface, touchpoint, and post-handoff ownership readings into one pre-implementation integration envelope without opening implementation, hook design, or viewer ownership
Mapping Impact: preserves mapping ownership by keeping legality intake downstream of the mapping-produced reference outcome and by keeping mapping redesign explicitly outside the legality envelope
Governance Impact: closes the current legality document sequence into one coherent pre-implementation envelope for future implementation-facing work while remaining strictly contract/boundary level
Backward Compatible: yes

Summary
- This turn consolidates the legality line into one pre-implementation runtime-integration envelope only.
- Legality receives a mapping-produced reference outcome through a weak upstream intake surface and owns downstream feasibility resolution after mapping.
- Legality may transform upstream reference intent into a feasibility-resolved downstream outcome, but only under weak projection / collision / boundary scope ownership.
- Legality emits only a weak feasible-outcome surface and remains implementation-neutral about names, types, storage, hook locations, and call paths.
- Legality ownership ends at feasible-outcome handoff; downstream consumption, reporting use, and viewer-side use are outside legality ownership.
- Observer/report echo remains optional, non-core, and non-owning.
- Implementation, exact touchpoint freeze, algorithm design, mapping redesign, and viewer semantic ownership remain explicitly closed.

## 1. Envelope Purpose And Scope

This note consolidates the already-completed legality-side work into one coherent pre-implementation envelope.

It integrates, in one place:

- legality minimum contract
- legality contract stabilization
- legality touchpoint inventory
- legality interface surface stabilization
- legality post-handoff ownership

The correct bounded reading is:

- legality is downstream of mapping
- legality is the downstream feasibility layer
- legality is not yet an implementation design

This note does not reopen:

- implementation
- runtime hook design freeze
- exact touchpoint freeze
- projection / collision / boundary algorithm design
- execution-order redesign
- mapping redesign
- viewer semantic ownership

## 2. What Legality Receives

Legality receives only a weak upstream intake surface.

That upstream intake should be read as:

- mapping-produced reference outcome
- reference-assignment result surface
- contract/interface intake only

The most relevant existing anchor remains:

- `expected_position_map` or equivalent mapping-produced reference-assignment surface

This means legality begins only after mapping has already produced its upstream reference outcome.

This intake remains weak and implementation-neutral.

It does not freeze:

- exact field name
- exact runtime type
- exact storage site
- exact hook location
- exact call path

## 3. What Legality Owns

Legality owns only downstream feasibility resolution after mapping.

The smallest stable contract-level surface remains:

- `feasibility_ownership`
- `projection_scope`
- `collision_boundary_scope`
- `feasible_outcome_surface`

These are field-equivalent semantic anchors only.

They should be read as:

- contract-level placeholders
- implementation-neutral ownership and surface language
- replaceable by later equivalent wording if semantics stay unchanged

They should not be read as:

- runtime-facing identifiers
- storage keys
- hook names
- code-path names

## 4. What Legality May Transform

Legality may transform only:

- upstream reference intent
- into a downstream feasible outcome

That transformation remains bounded to weak ownership language only.

The allowed bounded reading is:

- legality may resolve downstream feasibility questions
- legality may own projection only as a downstream feasibility class
- legality may own collision / overlap and boundary handling only as downstream feasibility classes

The not-allowed reading remains:

- projection algorithm design
- collision-resolution algorithm design
- boundary-clamp algorithm design
- fallback-placement procedure design
- runtime trigger design
- execution-order design

## 5. What Legality Emits

Legality emits only a weak downstream feasible-outcome surface.

That output should be read only as:

- legality-resolved feasible outcome
- feasibility-resolved downstream result surface
- downstream handoff surface after legality-owned resolution

This output remains intentionally weak.

It does not freeze:

- exact downstream name
- exact runtime type
- exact storage site
- exact handoff location
- exact downstream consumer identity

## 6. Runtime-Adjacent Touchpoint Envelope

The minimum runtime-adjacent touchpoint envelope for legality remains:

- one upstream contract-intake class
- one legality-owned resolution class
- one downstream feasible-outcome handoff class
- one observer/report echo class only where structurally unavoidable

The smallest stabilized interface reading inside that envelope is:

- one core upstream interface surface
- one legality-internal resolution stage
- one core downstream interface surface
- one optional non-core observer/report echo surface

This is sufficient for pre-implementation reading.

It is not yet:

- exact runtime hook design
- exact touchpoint placement
- exact call-order integration

## 7. Where Legality Ownership Ends

Legality ownership ends at feasible-outcome handoff.

The first downstream consumer boundary begins only after:

- legality-owned feasibility resolution is complete
- legality-resolved feasible outcome is exposed for downstream use

After that handoff, legality no longer owns:

- downstream consumer behavior
- downstream consumption sequencing
- downstream storage/readout conventions
- downstream interpretation or presentation ownership
- downstream observer/report usage ownership
- downstream viewer-side usage ownership

This keeps legality from expanding into general downstream orchestration.

## 8. Observer / Report Echo Status

Observer/report echo remains:

- secondary
- non-core
- non-owning
- optional unless structurally unavoidable

Observer/report echo may reflect legality-shaped downstream outcome for diagnosis or reporting, but it does not become:

- legality ownership continuation
- core downstream consumer definition
- viewer semantic ownership
- a frozen telemetry contract

The safest bounded reading is that observer/report echo sits outside the core legality-owned envelope.

## 9. What Remains Outside Legality

The following remain outside legality:

- mapping ownership of stable identity-to-slot assignment and mapping-produced reference outcome production
- downstream consumer ownership after feasible-outcome handoff
- observer/report pipeline ownership
- viewer semantic ownership
- doctrine / posture / combat meaning

Legality therefore should not absorb:

- mapping redesign
- downstream consumer redesign
- reporting redesign
- rendering ownership

## 10. What Future Implementation Would Still Need To Decide

This envelope is intentionally pre-implementation.

A future implementation would still need to decide, later and explicitly:

- exact runtime hook locations
- exact touchpoint placement
- exact runtime/storage types
- exact call paths
- exact execution order
- exact projection algorithm shape
- exact collision / overlap resolution procedure
- exact boundary handling procedure
- exact downstream consumer integration shape

Those decisions are not settled here.

## 11. Envelope Bottom Line

The full bounded pre-implementation legality envelope can now be read as:

- legality receives a weak mapping-produced reference intake
- legality owns downstream feasibility resolution through a very small stabilized contract surface
- legality may transform upstream reference intent only into a weak feasible-outcome surface
- legality emits a weak downstream feasible-outcome handoff
- legality ownership ends at that handoff
- observer/report echo stays optional, secondary, and non-owning
- implementation-facing choices remain for a later turn

That is sufficient for this carrier.
