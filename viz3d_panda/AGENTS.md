# viz3d_panda - Viewer / Replay / Export Discipline

This directory is the Panda3D viewer / replay / export consumer layer.

It is not the simulation runtime owner.
It is not governance authority.

The purpose of these local rules is to keep future 3D / GPU / batch-drawing
work viewer-local, owner-truthful, and easy to hand off to Engineering and
Governance threads without duplicating their standards.

---

## V-01 - Directory Identity and Ownership Boundary

`viz3d_panda/` is responsible for:

- viewer bootstrap and playback host
- replay consumption and reconstruction on the viewer side
- camera control
- scene assembly
- viewer-local rendering and overlays
- offline export through the same viewer path

`viz3d_panda/` is **not** responsible for:

- runtime battle semantics
- canonical observer doctrine
- harness / DOE policy
- governance-core standards

Do not use VIZ work to silently rewrite:

- `runtime/*` mechanism meaning
- `test_run/*` experiment doctrine
- canonical report semantics
- governance policy

If a viewer feature depends on upstream replay/export truth, keep the bridge
explicit and honest.

---

## V-02 - Active Owner Map Must Be Named Before Structural Change

Before changing active VIZ mechanism behavior, identify the current owner and
carrier first.

Current default owner read:

- `viz3d_panda/app.py`
  - viewer host
  - playback/export state carrier
  - UI / camera-take / export orchestration
- `viz3d_panda/scene_builder.py`
  - static scene shell
  - skybox / lights / grid / axes assembly
- `viz3d_panda/unit_renderer.py`
  - dynamic battlefield visual owner
  - token / cluster / fire-link / halo rendering
- `viz3d_panda/replay_source.py`
  - viewer replay reconstruction carrier
- `viz3d_panda/export_video.py`
  - offline export launcher entry

Do not silently move ownership between these surfaces.

If current code reality differs from an older note or comment, correct the
mismatch explicitly.

---

## V-03 - GPU / Batch Work Must Stay Viewer-Local First

Future 3D optimization work may be large, but it still starts as viewer-local
work unless the Human explicitly expands scope.

For GPU / batch-drawing lines:

- audit the current hot family first
- keep replay/runtime ownership outside VIZ unless explicitly approved
- keep live viewer and offline export compatibility explicit
- treat renderer backend changes as VIZ implementation work, not runtime
  semantics work

Preferred family framing for future acceleration work:

- token / cluster presentation
- fire links
- later dynamic VFX families such as explosion FX if and when they become
  active

Do not silently convert `app.py` into the renderer backend owner.
Do not silently turn `scene_builder.py` into a dynamic render hot path.

---

## V-04 - Static Audit Before Broad Rendering Work

For structural cleanup, ownership clarification, or GPU / batch work, use this
sequence first:

1. inspect
2. static owner/path audit
3. bounded design note or proposal
4. small implementation slice
5. review / report

Before writing code for renderer-adjacent work, surface:

- exact target file(s)
- active owner
- current state carrier or replay path
- whether the cost is:
  - node churn
  - per-frame transform churn
  - line rebuild churn
  - transparent overdraw
  - true backend draw cost

Dynamic profiling or visual smoke should validate a narrowed hypothesis, not
replace owner-truth audit.

---

## V-05 - Reporting and Note Placement

Local VIZ design and implementation notes belong under:

- `viz3d_panda/docs/developments/<YYYYMMDD>/`

Maintained viewer-side reference notes belong under:

- `viz3d_panda/docs/`

Use independent dated documents for material VIZ changes.
Do not back-edit older notes to make them look like later mechanism reality.

If work becomes:

- DOE reporting
- BRF export policy
- baseline replacement
- governance-core protocol work

then use the authoritative standards and governance docs instead of inventing a
VIZ-local replacement.

Required references when applicable:

- `analysis/engineering_reports/_standards/DOE_Report_Standard_v1.0.md`
- `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md`
- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`

TS handoff packages still belong in the root archive path required by the root
`AGENTS.md`, not in `viz3d_panda/docs/developments/`.

---

## V-06 - Preferred VIZ Report Shapes

For non-trivial VIZ work, prefer the same engineering-thread pattern:

- owner / boundary note
- bounded implementation proposal
- bounded implementation report
- major change record when mechanism availability or interface meaning changes

Keep the local note honest about status:

- proposal only
- implemented locally
- validation complete
- still experimental
- viewer reference only

Do not describe a VIZ note as governance approval by itself.

---

## V-07 - Validation and Failure Discipline

For VIZ behavior changes, the minimum honest validation posture is usually:

- static owner/path audit
- compile check for touched `viz3d_panda/*.py`
- minimal viewer-local smoke appropriate to scope
- export-path validation when export-visible behavior changed

If a required viewer/export input is invalid, prefer explicit failure over
silent fallback unless bounded normalization is already part of the maintained
runtime or viewer semantics.

Do not hide:

- invalid replay payload
- invalid export payload
- missing visual assets
- renderer mode mismatch

behind tolerant continue behavior.

---

## V-08 - No Silent Modernization

Do not present a backend rewrite, helper extraction wave, or file fan-out as a
"small cleanup" unless visible human-facing simplification actually occurred.

For renderer work, optimize for:

- honest owner boundaries
- smaller public control surface
- stable live/export parity
- local subtraction when possible
- explicit notes when a new backend seam is introduced

If a change is mainly architecture or future-facing scaffolding, describe it
that way instead of calling it simplification.
