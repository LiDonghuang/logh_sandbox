# Step 3 3D Legality Touchpoint Inventory Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line local-only pre-implementation touchpoint inventory
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: inventories the minimum runtime-adjacent touchpoint surface for legality between mapping output and downstream feasible-outcome consumption without opening implementation, hook design, or viewer ownership
Mapping Impact: preserves mapping ownership by treating the upstream legality input only as a mapping-produced reference outcome surface
Governance Impact: inventories legality touchpoint classes before any implementation-facing hook or algorithm turn
Backward Compatible: yes

Summary
- This turn inventories the smallest runtime-adjacent touchpoint surface for legality only as structure.
- Upstream input remains a mapping-produced reference outcome surface at contract/interface language only.
- Downstream output remains a legality-resolved feasible outcome surface at contract/interface language only.
- The note inventories touchpoint classes only and does not freeze hook locations, execution order, or algorithms.
- Implementation, mapping redesign, and viewer semantic ownership remain explicitly closed.

## 1. Upstream Input Surface To Legality

The upstream input surface to legality should be read only as:

- mapping-produced reference outcome
- reference-assignment result surface
- contract/interface language only

The most relevant repo-side existing term anchor remains:

- `expected_position_map` or equivalent reference-assignment output surface

Under the current bounded reading, legality does not own how that upstream mapping surface is produced.

Legality only begins after that upstream reference-assignment surface already exists.

This means the legality inventory may acknowledge upstream inputs such as:

- mapping-produced reference slot positions
- equivalent reference-assignment bundles
- equivalent reference-orientation/spacing context carried with that mapping result

This note does not freeze an exact upstream runtime type, storage site, or hook location.

## 2. Downstream Output Surface From Legality

The downstream output surface from legality should be read only as:

- legality-resolved feasible outcome
- feasibility-resolved positions or equivalent feasible-result surface
- contract/interface language only

This downstream surface is the first place where the system may conceptually distinguish:

- upstream reference intent
- downstream feasible realization

The bounded reading is:

- legality consumes mapping-produced reference outcome
- legality exposes a feasibility-resolved downstream outcome surface

This note does not freeze:

- the exact downstream identifier
- the exact runtime type
- the exact storage site
- the exact call path

## 3. Candidate Touchpoint Classes

The existing repo surfaces suggest four touchpoint classes only.

### A. Upstream Contract Intake Class

Conceptual role:

- where a mapping-produced reference outcome becomes available for legality consumption

Existing repo-adjacent surface examples:

- `analysis/engineering_reports/developments/20260327/step3_3d_mapping_opening_scope_confirmation_note_20260328.md`
- `analysis/engineering_reports/developments/20260327/step3_3d_mapping_minimum_contract_structural_draft_note_20260328.md`
- `runtime/engine_skeleton.py` fixture-local expected-position build / consume terminology

Bounded reading:

- this class inventories the presence of an upstream contract/interface surface only
- it does not pick a final runtime hook or storage location

### B. Legality Resolution Class

Conceptual role:

- where downstream feasibility-owned work would conceptually sit after mapping output and before downstream feasible-outcome consumption

Existing repo-adjacent surface examples:

- `analysis/engineering_reports/developments/20260326/step3_3d_formation_mapping_legality_split_note.md`
- `runtime/engine_skeleton.py` post-movement projection and boundary-resolution surfaces

Bounded reading:

- this class identifies the existence of a legality-owned resolution stage in structure
- it does not authorize projection, collision, or boundary algorithm design

### C. Downstream Feasible-Outcome Handoff Class

Conceptual role:

- where the legality-resolved feasible outcome would conceptually be handed to downstream consumers

Existing repo-adjacent surface examples:

- post-projection / post-boundary unit position state in `runtime/engine_skeleton.py`
- feasibility-shaped output reading in `analysis/engineering_reports/developments/20260327/step3_3d_legality_opening_scope_confirmation_note_20260328.md`
- stabilized `feasible_outcome_surface` anchor in `analysis/engineering_reports/developments/20260327/step3_3d_legality_contract_stabilization_note_20260328.md`

Bounded reading:

- this class inventories the existence of a downstream handoff surface only
- it does not freeze the downstream consumer boundary or execution order

### D. Observer / Report Echo Class

Conceptual role:

- where legality-shaped downstream feasibility outcomes or metrics may need to be echoed for diagnostics or reporting if structurally unavoidable

Existing repo-adjacent surface examples:

- `test_run/test_run_execution.py` observer telemetry assembly
- `runtime/engine_skeleton.py` debug payloads for projection / boundary surfaces
- `test_run/battle_report_builder.py` report consumption of runtime/boundary telemetry

Bounded reading:

- this class exists only because downstream feasibility work is difficult to interpret without some echo surface
- it does not reopen viewer semantic ownership
- it does not imply a required viewer-facing legality protocol

## 4. Boundary Statement

This legality inventory includes:

- the upstream input surface category to legality
- the downstream output surface category from legality
- the conceptual classes where legality-owned feasibility work would sit
- structurally unavoidable observer/report echo classes only

This legality inventory does not absorb mapping ownership.

Mapping still owns:

- stable identity-to-slot assignment
- remapping / reflow ownership questions
- production of mapping-produced reference outcome surface

The following still remain outside legality inventory:

- implementation design
- hook placement
- runtime touchpoint freeze
- viewer semantic ownership
- doctrine / posture / combat meaning

## 5. Explicit Exclusions

This touchpoint inventory does not open:

- implementation
- runtime hook design freeze
- projection algorithm design
- collision / boundary algorithm design
- execution-order redesign
- mapping redesign
- viewer semantic ownership

More specifically, this note does not authorize:

- exact function-level hook choice
- exact call-path choice
- exact storage-site choice
- projection solver design
- collision-resolution procedure design
- boundary-clamp procedure design
- remapping / reflow redesign
- `expected_position_map` ownership redesign
- rendering ownership
- `viz3d_panda/` semantic authority

## 6. Inventory Bottom Line

The minimum legality touchpoint inventory can be kept to:

- one upstream contract/interface input class
- one legality-owned resolution class
- one downstream feasible-outcome handoff class
- one observer/report echo class only where structurally unavoidable

That is sufficient for this turn.

This is a structural inventory only, not hook design and not implementation.
