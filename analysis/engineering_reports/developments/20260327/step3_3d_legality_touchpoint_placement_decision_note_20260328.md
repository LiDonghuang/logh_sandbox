# Step 3 3D Legality Touchpoint Placement Decision Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line local pre-implementation touchpoint-placement decision
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: fixes the minimum relative placement of legality between mapping-produced reference outcome and first downstream feasible-outcome consumption without opening implementation, hook design, or viewer ownership
Mapping Impact: preserves mapping ownership by keeping legality intake fully downstream of mapping-produced reference outcome and by refusing any split placement that pushes legality work back into mapping
Governance Impact: advances legality from touchpoint inventory to a bounded placement decision while staying smaller than implementation or hook design
Backward Compatible: yes

Summary
- This turn decides the minimum relative touchpoint placement for legality only.
- Legality should be placed as one bounded middle layer between mapping-produced reference outcome and the first downstream consumer of feasible outcome.
- The correct bounded structure is one upstream intake seam, one legality-owned resolution stage, and one downstream handoff seam.
- Observer/report echo should branch only from the post-handoff side as a secondary non-owning echo and not as part of the core placement.
- Exact hook location, storage site, runtime type, call path, and execution order remain undecided.

## 1. Decision Scope

This carrier decides only:

- the minimum relative placement of legality touchpoints

It does not decide:

- exact runtime hook location
- exact file/module location
- exact storage site
- exact runtime type
- exact execution order
- exact algorithm shape

The correct reading is:

- placement decision only
- implementation still closed

## 2. Core Placement Decision

The minimum legality placement should now be read as:

- one upstream intake seam after mapping output
- one bounded legality-owned resolution stage
- one downstream handoff seam before the first downstream consumer

This means legality should not be split across:

- mapping-owned production
- downstream consumer-owned post-handoff use
- observer/report echo surfaces

The cleanest bounded decision is therefore:

- legality occupies one middle placement envelope only

## 3. Upstream Placement

The upstream legality touchpoint should be placed:

- immediately downstream of mapping-produced reference outcome
- at the first contract/interface seam where mapping output becomes available for legality intake

This upstream placement should still be read weakly as intake only.

It does not mean:

- mapping redesign
- `expected_position_map` ownership redesign
- exact runtime hook freeze

The bounded placement answer is:

- mapping ends
- legality intake begins

## 4. Internal Resolution Placement

The legality-owned resolution work should be placed as one bounded internal stage.

That internal stage is where the already-stabilized legality ownership stays:

- `feasibility_ownership`
- `projection_scope`
- `collision_boundary_scope`

This stage should not be fragmented across multiple downstream consumers or observer/report surfaces.

The bounded decision is:

- legality-owned resolution stays inside one dedicated middle stage

This still does not decide:

- projection procedure
- collision procedure
- boundary procedure
- execution ordering details

## 5. Downstream Placement

The downstream legality touchpoint should be placed:

- at one feasible-outcome handoff seam
- immediately before the first downstream consumer of legality-resolved feasible outcome

The downstream placement answer is:

- legality-owned resolution ends here
- downstream consumer ownership begins here

This seam should remain weakly read as:

- handoff boundary only
- not downstream consumer implementation design
- not downstream orchestration design

## 6. Observer / Report Echo Placement

Observer/report echo should be placed outside the core legality placement envelope.

The safest bounded reading is:

- observer/report echo may branch from post-handoff outcome if structurally unavoidable
- observer/report echo is not part of the core legality intake-resolution-handoff chain

This means observer/report echo is:

- secondary
- non-core
- non-owning
- post-handoff

It should not be used to justify:

- viewer semantic ownership
- legality ownership continuation
- telemetry contract freeze

## 7. What The Placement Decision Fixes

This placement decision now fixes only the following relative structure:

- legality is fully downstream of mapping output
- legality is fully upstream of first downstream feasible-outcome consumption
- legality-owned resolution stays in one middle stage
- observer/report echo stays outside the core chain on the post-handoff side

That is enough to stop continued ambiguity about where legality belongs in the overall flow.

## 8. What Still Remains Open

Even after this placement decision, future implementation work still must decide:

- exact hook locations
- exact runtime/storage types
- exact call paths
- exact execution order
- exact projection algorithm shape
- exact collision / boundary handling procedures
- exact downstream consumer integration shape

Those remain later decisions and are not settled here.

## 9. Bottom Line

The minimum touchpoint placement decision is:

- place legality as one bounded middle envelope
- intake after mapping output
- resolve legality-owned feasibility inside that envelope
- hand off before first downstream consumer
- keep observer/report echo outside the core chain on the post-handoff side

That is sufficient for this carrier.
