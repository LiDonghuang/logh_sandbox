# step3_3d_pr6 cleanup rounds governance report - 2026-04-05

Engine Version:
`dev_v2.1` local cleanup line after PR `#6` opening package

Modified Layer:
- runtime combat targeting
- runtime movement ownership surface
- `test_run` harness execution / settings / report surface
- settings truth surface

Affected Parameters:
- `runtime.physical.fire_control.fire_quality_alpha`
- `runtime.physical.fire_control.alpha_safe_max`
- `runtime.physical.fire_control.fire_optimal_range_ratio`
- `runtime.movement.v4a.restore_strength`
- `runtime.movement.v3a.experiment`
- `runtime.movement.v3a.centroid_probe_scale`
- retired public harness/settings surfaces:
  - `runtime.movement.v3a.continuous_fr_shaping.*`
  - `runtime.movement.v3a.pre_tl_target_substrate`

New Variables Introduced:
- runtime-local movement surface key `v4a_restore_strength`

Cross-Dimension Coupling:
- none newly introduced
- cleanup stayed inside runtime + maintained `test_run` spine and did not widen viewer/mapping ownership

Mapping Impact:
- none

Governance Impact:
- PR `#7` remains the accepted docs / ownership-only cleanup opening and should not be used as the mechanism carrier for this package
- active `v4a` ownership truth is now materially narrower and more honest
- next major gate is no longer `restore_strength` decoupling; it is planning for `test_mode` retirement and broader `v3a` support-path retirement

Backward Compatible:
- current active launcher path remains valid
- default active path still reads `movement=v4a`, `cohesion=v3_test`
- forced `v3a` fallback still runs after this package
- removed legacy knobs are **not** backward-compatible as public settings surfaces

## Summary

- current targeting local package has been packaged honestly rather than reopened as a new design phase
- `v4a.restore_strength` is now native to the active `v4a` line rather than carried through old `v3_test` / centroid-probe reuse
- old-family public surfaces have been narrowed in several small subtraction-first rounds
- current launcher/settings truth now aligns better with the active path
- the next meaningful governance question is whether `test_mode` and the remaining supported `v3a` line should now enter formal retirement planning

## 1. What this package actually contains

This package is the first real mechanism cleanup package after the `PR #7`
cleanup opening was accepted and bounded.

It contains three grouped lines:

1. targeting local package disposition and packaging  
2. `restore_strength` ownership re-rooting / decoupling  
3. subtraction-first old-family retirement rounds in `test_run`

Repo-relative records for this package include:

- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_targeting_package_disposition_and_restore_strength_truth_map_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_restore_strength_decoupling_planning_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_restore_strength_decoupling_implementation_record_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_round1_restore_bridge_surface_removal_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_round2_v3a_summary_surface_narrowing_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_round3_v3a_debug_context_narrowing_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_round4_continuous_fr_shaping_retirement_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_old_family_retirement_round5_pre_tl_target_substrate_retirement_20260405.md`
- `analysis/engineering_reports/developments/20260404/step3_3d_pr6_active_ownership_map_post_decoupling_20260405.md`

## 2. Current truthful active-path read

For the current layered settings and maintained launcher path:

- `movement_model_effective = v4a`
- `runtime_decision_source_effective = v3_test`
- `v4a.restore_strength` now writes a native runtime movement seam
- active `v4a` no longer depends on the old `v3a.experiment` / `centroid_probe_scale` carrier

This means the package should be read as:

- active `v4a` mainline retained
- old bridge dependency removed
- old-family support surfaces narrowed but not fully retired

## 3. What was retired already

The cleanup rounds did **not** remove all of `v3a`.

They removed or narrowed specific stale / legacy public surfaces:

- stale active restore-bridge truth surfaces
- `v3a`-only summary / BRF export on default active `v4a`
- `v3a`-only debug context on default active `v4a`
- `continuous_fr_shaping` harness/settings surface
- `pre_tl_target_substrate` public test-only knob

Two important honesty points:

1. the non-bundle old fallback target read still exists in reduced form  
   - it is now one fixed nearest-5-centroid behavior rather than a public configurable substrate family

2. broader `v3a` support still exists  
   - especially through `movement_model = v3a`, `experiment`, `centroid_probe_scale`, and `odw_posture_bias`

So this package is best classified as:

- `Partial Cleanup`

not:

- full `v3a` retirement

## 4. Human direction captured in this round

Engineering is also carrying explicit Human direction that materially affects
next-step governance interpretation:

- only mechanisms actually used through the current launcher with current layered settings should be preserved as active surface
- when old mechanisms are deleted, `runtime.settings.json` / `testonly.settings.json` / `settings.comments.json` must be kept synchronized
- code-structure simplicity is now the dominant engineering priority because uncontrolled growth has already created real maintenance cost
- `test_run/test_run_v1_0_viz.py` is an older 2D visual mechanism and should later be retired gradually where it is no longer on the active `v4a` hot path
- `runtime/engine_skeleton.py` still carries many older-mechanism residues that should later be retired gradually where they are no longer on the active `v4a` hot path
- Human now judges `test_mode != 2` as no longer worth preserving, and judges `test_mode` itself as an old mechanism that should be deleted rather than retained indefinitely

That last point is important because it changes the next cleanup frontier.

## 5. Governance-facing next gate

Engineering does **not** recommend reading this package as authorization to
delete all of `v3a` immediately.

Current verified blockers:

- `test_run/test_run_scenario.py` still resolves `baseline -> v3a`
- `test_run/test_run_anchor_regression.py` still forces `movement_model = v3a`
- `runtime/engine_skeleton.py` and `test_run/test_run_execution.py` still keep real `v3a` execution support
- `test_mode` still gates baseline-vs-explicit selection

So the next governance-facing gate should be read as:

- `test_mode` retirement planning
- `v3a` support-path retirement planning
- likely baseline-replacement / maintained-fallback decision rather than another small old-family knob cleanup

## 6. Requested governance interpretation

Engineering requests Governance to read the project state as follows:

1. PR `#7` successfully served as the accepted cleanup opening, but mechanism cleanup now requires its own carrier
2. targeting local package, `restore_strength` decoupling, and the first two old-family public-knob retirements are now real and separately recorded
3. active `v4a` ownership is cleaner, but the repo still supports `v3a`
4. the next serious governance question is not more tiny knob cleanup, but whether the project should formally stop preserving `test_mode != 2` and begin bounded `test_mode` / `v3a` retirement planning

