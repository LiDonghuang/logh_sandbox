# Step 3 3D Legality Interface Surface Stabilization Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line direct-push pre-implementation interface-surface stabilization
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: stabilizes the smallest legality interface surface between mapping-produced reference outcome and downstream feasible-outcome consumption without opening implementation, hook design, or viewer ownership
Mapping Impact: preserves mapping ownership by treating the legality upstream side only as an input interface surface fed by mapping output
Governance Impact: advances legality from touchpoint inventory into a smaller stabilized interface reading while remaining contract/interface only
Backward Compatible: yes

Summary
- This turn stabilizes the minimum legality interface surface only at contract/interface level.
- The smallest clean reading separates one core upstream interface, one legality-internal resolution stage, and one core downstream interface.
- Observer/report echo is retained only as a non-core optional echo surface when structurally unavoidable.
- All names remain implementation-neutral and are not runtime-facing identifiers, storage keys, hook names, or algorithm entries.
- Implementation, runtime hook design, runtime touchpoint freeze, mapping redesign, and viewer semantic ownership remain explicitly closed.

## 1. Stabilized Minimum Interface Surface

The smallest clean legality interface surface can be stabilized as:

- one core upstream interface surface
- one legality-internal resolution stage
- one core downstream interface surface
- one non-core optional observer/report echo surface only if structurally unavoidable

If a field-equivalent anchor set is needed for future discussion, it should remain no larger than:

- `upstream_reference_input_surface`
- `legality_resolution_surface`
- `downstream_feasible_outcome_surface`
- `observer_report_echo_surface` only as optional non-core echo

These anchors are only contract/interface labels.

They are not:

- runtime-facing identifiers
- storage keys
- hook names
- call-path commitments
- execution-order commitments
- algorithm entries

## 2. Core Upstream Interface Surface

The core upstream legality interface surface should be read only as:

- mapping-produced reference outcome intake
- reference-assignment result surface intake
- contract/interface input to legality only

This upstream side stays intentionally weak.

It means only that legality receives an already-produced mapping output surface such as:

- `expected_position_map`
- or an equivalent reference-assignment output surface

This stabilization does not freeze:

- exact field names
- exact runtime type
- exact storage site
- exact hook location
- exact call path

Mapping still owns how that upstream reference outcome is produced.

## 3. Legality-Internal Resolution Stage

The legality-internal resolution stage should be stabilized as one bounded internal interface stage only.

Its minimum reading is:

- downstream feasibility ownership sits here
- projection-scope ownership sits here
- collision / boundary-scope ownership sits here

Its bounded role is:

- receive upstream reference intent
- resolve legality-owned feasibility questions
- prepare a downstream feasible outcome surface

This stage is still contract/interface only.

It does not freeze:

- projection algorithm design
- collision algorithm design
- boundary algorithm design
- fallback procedure design
- execution order
- runtime integration path

## 4. Core Downstream Interface Surface

The core downstream legality interface surface should be read only as:

- legality-resolved feasible outcome handoff
- feasibility-shaped downstream result surface
- contract/interface output from legality only

This is the first downstream surface where the system may cleanly distinguish:

- upstream reference intent
- downstream feasible realization

The bounded reading is only that legality exposes a feasible outcome surface for downstream consumption.

This stabilization does not freeze:

- exact downstream name
- exact runtime type
- exact consumer boundary
- exact handoff location
- exact execution ordering

## 5. Observer / Report Echo As Non-Core Optional Surface

Observer/report echo should be treated as non-core and optional.

The bounded reading is:

- legality may need a small echo surface for diagnostics or reporting only if structurally unavoidable

It should not be read as part of the core legality interface minimum.

It should also not be read as:

- viewer semantic ownership
- viewer protocol ownership
- required rendering semantics
- a frozen telemetry contract

This keeps the core legality interface surface smaller and avoids widening the carrier into observer or viewer design.

## 6. Boundary Reading

This stabilization includes only:

- one core upstream legality input surface
- one legality-internal resolution stage
- one core downstream legality output surface
- one optional non-core observer/report echo surface

This stabilization does not absorb mapping ownership.

Mapping still owns:

- stable identity-to-slot assignment structure
- remapping / reflow ownership questions
- production of the mapping output surface consumed by legality

The following still remain outside this carrier:

- implementation
- runtime hook design
- runtime touchpoint freeze
- projection algorithm design
- collision / boundary algorithm design
- execution-order redesign
- mapping redesign
- viewer semantic ownership

## 7. Interface Bottom Line

The correct bounded result for this turn is:

- stabilize one upstream legality input surface
- stabilize one legality-owned internal resolution stage
- stabilize one downstream feasible-outcome surface
- demote observer/report echo to optional non-core status

That is sufficient for this carrier.

No hook location, storage site, runtime type, call path, execution order, or algorithm is frozen here.
