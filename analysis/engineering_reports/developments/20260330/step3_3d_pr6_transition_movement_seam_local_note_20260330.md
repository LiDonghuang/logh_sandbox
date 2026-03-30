# Step 3 3D PR #6 Transition Movement Seam Local Note

Status: local working note only  
Scope: `test_run/` bounded carrier seam, not pushed  
Layer read: harness / candidate-only, no frozen-runtime modification

## Purpose

This note records the first bounded movement-realization seams added on top of the current PR #6 transition carrier:

1. `shape vs advance`
2. `heading relaxation`

These seams were introduced because Human correctly identified that the current transition problem is no longer only a reference/morphology issue.
The carrier also needs a minimal motion-realization layer:

- when to keep advancing
- when to spend motion budget on reshaping
- how turning / heading change should be realized more plausibly
- how arrival/hold should avoid point-anchor shell collapse

## Local code scope

Touched local files:

- `test_run/settings_accessor.py`
- `test_run/test_run_scenario.py`
- `test_run/test_run_execution.py`
- `test_run/test_run_v1_0.testonly.settings.json`
- `test_run/test_run_v1_0.settings.comments.json`
- `test_run/test_run_v1_0.settings.reference.md`

Frozen runtime was not modified:

- `runtime/engine_skeleton.py`

## New test-only settings surface

Under `runtime.movement.v4a.test_only`:

- `shape_vs_advance_strength`
- `heading_relaxation`

Current local defaults:

- `shape_vs_advance_strength = 0.65`
- `heading_relaxation = 0.18`

Current intended semantics:

- `shape_vs_advance_strength`
  - reduces pure objective-chasing authority when morphology error is still large
  - leaves more motion budget for ongoing shape transition

- `heading_relaxation`
  - introduces a bounded fleet-level realized heading
  - avoids instantly snapping the transition carrier to raw target direction

## Carrier-side implementation read

The local harness seam now does three extra things for `v4a`:

1. tracks a `movement_heading_current_xy` state per fleet bundle
2. scales fleet target-direction authority by current morphology error
3. redistributes per-unit speed in the transition carrier using:
   - current shape need
   - current heading alignment

Additionally, fixture arrival/hold was tightened:

- objective arrival is no longer treated as complete solely because the centroid enters `stop_radius`
- fixture completion now waits for morphology-level hold readiness

## Minimal validation commands

Syntax:

```powershell
python -m py_compile test_run\settings_accessor.py test_run\test_run_scenario.py test_run\test_run_execution.py
```

Light neutral-transition sweep used locally:

- `1 -> 1`
- `4 -> 4`
- `1 -> 4`
- `4 -> 1`

All runs used:

- `movement_model = v4a`
- `reference_surface_mode = soft_morphology_v1`
- `expected_reference_spacing = 2.0`
- `min_unit_spacing = 1.0`

## Current local read

What improved:

- the carrier now has a real bounded movement-realization seam instead of only reference-surface tuning
- `4 -> 1` responds meaningfully to `shape_vs_advance_strength`
- fixture completion no longer triggers merely on radius entry when morphology hold is not ready

What did not resolve:

- `1 -> 4` still stalls around a lateral/forward ratio near `~2`, not near the `~4.75` reference target
- `1 -> 1` and `4 -> 4` remain nearly rigid
- the new movement seams do not by themselves solve the deeper transition-transport problem

## Quick local read from the first seam pass

Using:

- `shape_vs_advance_strength = 0.65`
- `heading_relaxation = 0.18`

the local neutral-transition read is:

- `1 -> 1`
  - still effectively rigid / exact

- `4 -> 4`
  - still effectively rigid / exact

- `1 -> 4`
  - changes in the correct broad direction at first
  - but then stalls around a ratio near `~2`
  - does not honestly complete the transition

- `4 -> 1`
  - changes more credibly than before
  - but still finishes with large internal disorder / high RMS

This asymmetry is important:

- movement-realization seams help
- but they help an already partly-compressive transition (`4 -> 1`) more than an expansive one (`1 -> 4`)
- so the remaining bottleneck is not only movement realization
- it is also transition transport/topology continuity

## Current engineering conclusion

The new seams are still worth keeping and documenting.
They are likely long-term useful components of the formation-transition problem.

But the local read is now clearer:

- `shape vs advance` and `heading relaxation` are necessary
- they are not sufficient by themselves
- the remaining bottleneck is still the transition carrier's transport/topology layer, especially for `1 -> 4`

So the next honest step remains:

- keep these two movement seams
- continue reworking the transition carrier as a coupled problem of:
  - target morphology
  - transport/topology continuity
  - movement realization

## Later local refinement read

After the first movement-seam pass, two additional bounded local refinements were also explored:

1. `morphology_center_current`
   - a slowly relaxing morphology-center state, separate from raw live centroid
   - intended to stop the expected surface from being re-centered too eagerly by the moving body

2. continuous transport phase
   - per-unit material phase no longer remains fixed at the initial morphology
   - instead it relaxes toward target reference phase continuously

Local result after those refinements:

- `4 -> 1` improved substantially and now approaches a believable ratio near `1`
- `1 -> 4` still does not honestly complete
- when pure advance is suppressed harder, `1 -> 4` degrades rather than improving

Current sharper local read:

- the harness-only transition carrier can now express:
  - useful movement budgeting
  - useful heading relaxation
  - useful center ownership
  - useful continuous transport phase

- but for expansive transition like `1 -> 4`, the frozen movement core still appears to lack enough realization authority
  - fleet-level target direction remains shared
  - movement realization is still too close to instantaneous vector composition
  - there is no true per-unit turning / slowing / route-yield seam inside the frozen path

So the practical boundary exposed by the latest local work is:

- harness-only seams can improve the carrier
- harness-only seams may not be sufficient to finish the expansive transition case honestly

## Later local terminal-semantics correction

After the transition-movement seam, terminal / arrival behavior was isolated as a separate first-priority local fix.

Two bounded harness-only corrections were applied:

1. terminal-stage capture
   - entering stop radius is now allowed to latch a morphology-level terminal stage
   - this decouples mission-arrival capture from the stricter "final hold shape-error threshold"

2. post-move terminal capture
   - terminal latch is also allowed from the post-move observed centroid
   - this is specifically intended to catch cases that briefly enter the objective radius and then get pulled away again on the next tick

Local read after that terminal correction:

- `1 -> 4`
  - no longer runs to the `999` hard cap
  - objective capture now completes in the expected terminal window
  - shape remains imperfect, but the prior "never arrived" failure mode is removed

- `4 -> 1`
  - also no longer runs to the `999` hard cap
  - objective capture now completes in the terminal window
  - centroid hold is materially better than before, but motion/readability issues remain and the internal formation is still not judged settled/correct

Current sharper local read after the terminal fix:

- terminal semantics were a real independent bug
- fixing terminal semantics improves both human readability and experiment honesty
- but terminal correctness still does not solve the broader formation-transition problem
- after this fix, the remaining problem surface is again mainly:
  - transition transport/topology continuity
  - plus minimal movement realization quality inside the frozen core boundary
