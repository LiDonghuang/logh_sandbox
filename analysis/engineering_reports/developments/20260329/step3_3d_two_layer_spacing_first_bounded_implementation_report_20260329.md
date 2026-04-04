# Step 3 3D Two-Layer Spacing First Bounded Implementation Report (2026-03-29)

Engine Version: `dev_v2.0`  
Modified Layer: maintained battle-path candidate bridge in `test_run/` only  
Affected Parameters: no public surfaces; test-only `v4a` reference settings only (`expected_reference_spacing`, `reference_layout_mode`)  
New Variables Introduced: per-fleet expected-slot bundles inside the maintained harness only  
Cross-Dimension Coupling: introduces one bounded battle-path bridge from expected-slot restore into the maintained battle path while keeping expected/reference spacing and physical minimum spacing conceptually split inside the candidate line  
Mapping Impact: none  
Governance Impact: first bounded implementation candidate now exists for the two-layer spacing line plus maintained battle-path restoration bridge; remains candidate-only and non-default  
Backward Compatible: yes for maintained repo defaults; `v3a` remains retained and no default switch is made

Summary
- This turn implements the first bounded two-layer spacing candidate without modifying the frozen runtime core.
- The candidate keeps physical minimum spacing on the runtime low-level side while moving expected/reference spacing and reference layout mode onto narrow test-only `v4a` settings.
- The maintained battle path now sees a bounded expected-slot restoration bridge for `v4a`, instead of only carrying the `v4a` label while leaving the restore line fixture-only.
- Validation shows the bridge materially changes battle-path geometry and strongly suppresses the early rectangle stretch seen on the coupled baseline.
- Human battle observation now sharpens the read: pre-contact marching stability is consistent with current scope, but later contact exposes an old hostile-penetration / interleaving problem much more clearly.
- The correct review read is therefore: effective candidate, not yet accepted architecture, and not a silent baseline replacement.

## Files Changed

- `test_run/test_run_execution.py`
- `test_run/test_run_scenario.py`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_first_bounded_battle_comparison_20260329.csv`
- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_first_bounded_implementation_report_20260329.md`
- `repo_context.md`
- `system_map.md`

## Implementation Seam Chosen

The candidate stays entirely inside the maintained harness layer:

1. `test_run/test_run_scenario.py`
   - takes expected/reference spacing and reference layout mode from narrow test-only `v4a` settings
   - leaves physical minimum spacing on the existing runtime low-level `min_unit_spacing` surface
2. `test_run/test_run_execution.py`
   - builds per-fleet expected-slot reference bundles from the initial maintained battle state
   - injects those bundles into a temporary fixture-shaped config only during `integrate_movement(...)`
   - restores the prior fixture config immediately after the movement call

This seam is intentionally narrow:

- no `runtime/engine_skeleton.py` modification
- no public settings expansion
- no `v3a` removal
- no default switch

## Validation Path Used

Validation used one bounded maintained battle-path comparison:

- repo committed battle settings as the base
- fixed seeds:
  - `run_control.random_seed = 20260329`
  - `runtime.metatype.random_seed = 20260329`
  - `battlefield.background_map_seed = 20260329`
- effective movement model forced to `v4a`
- bounded run window:
  - `max_time_steps = 120`
- same branch code, two modes:
- baseline: coupled expected/reference `2.0` and physical `2.0`, candidate inactive
- candidate: expected/reference `2.0` with physical `1.0`, battle restore bridge active

Human-readable artifact:

- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_first_bounded_battle_comparison_20260329.csv`

The CSV records sampled ticks:

- `1`
- `20`
- `50`
- `100`
- `120`

for:

- `width_depth_ratio`
- `front_extent_ratio`
- `expected_position_rms_error`
- rear / middle / front `forward_slot_error`
- `projection_pairs_count`
- `corrected_unit_ratio`

## Key Observed Comparison

### Baseline: coupled `2.0 / 2.0`

At `tick = 120`:

- `width_depth_ratio = 0.6497`
- `front_extent_ratio = 5.6900`
- `expected_position_rms_error = 10.7621`
- `rear_forward_slot_error = -6.3786`
- `mid_forward_slot_error = -2.5302`
- `front_forward_slot_error = 8.9820`
- `projection_pairs_count = 123`
- `corrected_unit_ratio = 0.63`

### Candidate: split `2.0 / 1.0` + battle restore bridge

At `tick = 120`:

- `width_depth_ratio = 4.6847`
- `front_extent_ratio = 1.0146`
- `expected_position_rms_error = 0.0365`
- `rear_forward_slot_error = -0.0032`
- `mid_forward_slot_error = 0.0018`
- `front_forward_slot_error = 0.0016`
- `projection_pairs_count = 0`
- `corrected_unit_ratio = 0.0`

## What Improved

- the maintained battle path now actually expresses the expected-slot restoration line rather than only carrying the `v4a` selector label
- the spacing split remains materially important outside the earlier fixture-only frame
- early rectangle stretching is dramatically reduced on the bounded battle path
- pre-contact marching formation now stays stable in the maintained battle path, which matches current design scope rather than reading as over-constraint by itself
- front-extent blowout and rank-split forward-slot error both collapse from large drift to near-zero levels
- projection/correction breadth is also strongly reduced on the same candidate path

## What Worsened

- the candidate now makes the old hostile penetration problem much easier to see during contact
- in human 3D observation around the later contact window, opposing fleets can interleave in a sawtooth pattern and even pass through each other
- this means the candidate proves the bridge and the spacing split matter, but it also reveals that the overloaded `min_unit_spacing` had been masking part of the contact-side penetration problem

## What Remains Unclear

- whether the maintained battle path needs any weaker restore pressure at all before personality-side formation variation is opened
- whether the low-level floor split is the correct long-term structural answer by itself, or only the necessary first half of the answer
- what the smallest bounded hostile anti-penetration follow-up should be once Governance reviews this candidate
- where the eventual ownership boundary should sit if this line advances beyond candidate level
- whether future bounded hardening should focus first on contact-side hostile separation rather than further formation-side restore tuning

## Merge-Worthy Assessment

Current engineering read:

- useful PR review candidate
- not yet merge-worthy as a new maintained baseline

Reason:

- the candidate successfully proves that battle can see the restoration line
- it also proves that the spacing split matters outside fixture-only context
- but the resulting battle behavior still exposes unresolved hostile penetration at contact, so it should not be accepted as a maintained baseline by momentum

The correct review reading is:

- first bounded implementation candidate only
- not final two-layer spacing architecture
- not final battle restoration architecture
- not a default switch
- not a baseline replacement
