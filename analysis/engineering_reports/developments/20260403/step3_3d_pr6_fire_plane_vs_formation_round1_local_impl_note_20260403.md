# LOGH Sandbox

## PR #6 Fire Plane vs Formation Round 1 Local Implementation Note

Status: local implementation note only  
Scope: `test_run`-side bounded battle-geometry probe  
Authority: local engineering note before Human review  
Non-scope: push approval, merge approval, runtime-core rewrite

---

## Scope

This round implements the smallest candidate discussed in the design note:

- `effective_fire_axis`
- `front_reorientation_weight`
- `engagement_geometry_active`

The change remains inside:

- `test_run/test_run_execution.py`

plus viewer-side temporary debug display support.

No targeting change is included.
No local range-entry correction is included.
No `runtime/engine_skeleton.py` change is included.

---

## Current Read

The implemented probe does the following:

1. aggregate a fleet-level `effective_fire_axis` from currently engaged
   outgoing attack directions
2. derive `engagement_geometry_active` from engaged-unit fraction
3. derive `front_reorientation_weight` from:
   - engagement activation
   - fire-axis coherence
4. use that bounded weight to bias morphology-axis ownership toward the
   effective fire axis with low-jump relaxation

This is intentionally a fleet-level front-ownership probe only.

It is **not**:

- a local enemy targeting change
- a nearest-enemy correction
- a local swarm release

---

## Viewer Support

The 3D HUD focus line is repurposed toward current battle geometry:

- `eng_act`
- `front_rw`
- `fire_da`

while the older transport-continuity diagnostics remain in payload only.

---

## Reminder

This round still requires Human review against the hard gates:

- fleet-centroid trajectory
- alive-unit body observation

If those fail, the candidate should be treated as rejected even if the new
indicators appear internally tidy.

