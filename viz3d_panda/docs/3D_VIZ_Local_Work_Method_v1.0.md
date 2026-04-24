# LOGH Sandbox

## 3D VIZ Local Work Method v1.0

Status: active local working method  
Scope: `viz3d_panda/` design, implementation, reporting, and governance handoff posture  
Authority: VIZ-local method only, not canonical governance authority

---

## Purpose

This note creates a VIZ-local working method that mirrors the Engineering main
thread style without duplicating governance-core standards.

The goal is to make future 3D / GPU / batch-drawing work easier to:

- scope locally
- document honestly
- hand off to Governance when needed
- keep replay/view ownership separate from runtime ownership

---

## Directory Identity

`viz3d_panda/` should be treated as:

- replay/view consumer layer
- Panda3D host and renderer layer
- offline export consumer of the same viewer path

It should not be treated as:

- runtime semantics owner
- test harness doctrine owner
- governance-core report standard owner

This matches the current Engineering structural read:

- runtime owns maintained simulation truth
- `test_run` owns execution / experiment plumbing
- `viz3d_panda` consumes replay output and stays viewer-local

Reference:

- `analysis/engineering_reports/_standards/Engineering_Structural_Optimization_Progress_and_Lessons_20260412.md`

---

## What To Create Locally

For VIZ-local work, the preferred local artifacts are:

1. local `AGENTS.md`
2. maintained viewer reference notes in `viz3d_panda/docs/`
3. dated development notes in `viz3d_panda/docs/developments/<YYYYMMDD>/`
4. TS handoff package in the root archive path only when thread migration is needed

This is the minimal local stack.

Do not create a second VIZ-local replacement for:

- DOE standards
- BRF standards
- baseline-replacement protocol
- governance-core doctrine

Reference them instead.

---

## Working Sequence

For structural VIZ work, use the same basic Engineering rhythm:

1. inspect
2. static owner audit
3. proposal or boundary note
4. bounded implementation
5. implementation report
6. governance handoff only if the scope truly crosses into governance territory

This is especially important for:

- renderer ownership clarification
- GPU / batch-drawing design
- export-path compatibility work
- viewer-side contract changes

---

## Recommended Report Split

### A. Owner / Boundary Note

Use when the next step is still architectural or scope-setting.

Preferred topics:

- active owner
- hot path
- current carrier
- local vs cross-layer boundary
- smallest honest next slice

Typical use:

- before a future GPU / batch-drawing pass
- before changing app / renderer / export boundaries

### B. Bounded Implementation Proposal

Use before non-trivial code changes.

Preferred purpose:

- describe the smallest authorized slice
- identify exact target files
- say what stays unchanged
- say what validation will be used

This mirrors the recent Engineering proposal style:

- one-sentence conclusion first
- exact owner/path to change
- fixed assumptions
- keep vs replace
- validation posture

### C. Bounded Implementation Report

Use after implementation.

Preferred purpose:

- describe what changed
- record active owner/path
- record exact target files
- record validation
- record residual risks

This mirrors the recent Engineering report style:

- plain-language read first
- static owner/path audit
- exact role or boundary change
- validation result
- short conclusion

### D. Major Change Record

Use when a VIZ change materially affects:

- active mechanism availability
- default viewer/export interface meaning
- public VIZ control surface
- maintained owner map

Use a new dated record instead of rewriting old notes.

### E. TS Handoff

Use only when thread sustainability risk becomes real.

Placement stays at the root archive path required by the root `AGENTS.md`:

- `docs/archive/ts_handoff_archive/TS_HANDOFF_<YYYYMMDD_HHMMSS>/`

---

## Recommended VIZ Note Skeleton

For most VIZ proposal/report notes, the following skeleton is sufficient:

1. title
2. `Date`
3. `Scope`
4. `Status`
5. one-sentence conclusion or visual-read-first summary
6. static owner/path audit
7. exact target file(s)
8. current carrier / control path / export path
9. proposed or implemented change
10. validation posture and result
11. open risks / unknowns
12. short governance-facing summary when relevant

This is a local working shape, not a repository-wide mandatory reporting
standard.

---

## Placement and Naming Pattern

### Maintained Viewer Reference Notes

Place under:

- `viz3d_panda/docs/`

Use when the note describes an active maintained viewer-side rule or contract.

Example pattern:

- `3D_VIZ_<Topic>_Reference_v1.0.md`
- `3D_VIZ_<Topic>_Contract_v1.0.md`

### Dated Development Notes

Place under:

- `viz3d_panda/docs/developments/<YYYYMMDD>/`

Preferred filename patterns:

- `<topic>_owner_boundary_note_<YYYYMMDD>.md`
- `<topic>_bounded_implementation_proposal_<YYYYMMDD>.md`
- `<topic>_bounded_implementation_report_<YYYYMMDD>.md`
- `<topic>_major_change_record_<YYYYMMDD>.md`

Use plain descriptive topic names instead of generic `notes.md` or `report.md`.

---

## When To Escalate Beyond VIZ-Local Notes

VIZ-local notes are enough when the work stays viewer-local.

Escalate to Engineering / Governance-facing reporting when the change affects:

- replay export contract meaning
- observer-facing report semantics
- baseline replacement or default-path promotion
- cross-layer owner transfer
- public experiment protocol

When escalation is needed, keep the VIZ-local note and add the higher-level
document rather than rewriting the local note into governance doctrine.

Required references when applicable:

- `analysis/engineering_reports/_standards/DOE_Report_Standard_v1.0.md`
- `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md`
- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`

---

## GPU / Batch-Drawing Line Guidance

For future GPU / batch-drawing work, the default local framing should be:

- `app.py`
  - host / playback / export carrier
- `scene_builder.py`
  - static scene shell
- `unit_renderer.py`
  - dynamic battlefield visual owner

So the default smallest honest design move is:

- keep host ownership in `app.py`
- keep static world assembly in `scene_builder.py`
- place renderer-backend evolution under the renderer family

Do not silently:

- move runtime ownership into VIZ
- split live and export into unrelated render paths
- describe speculative backend scaffolding as finished optimization

---

## Validation Posture For VIZ Work

Minimum honest validation for most VIZ slices:

- static owner/path audit
- compile touched Python files
- viewer-local smoke appropriate to scope
- export-path smoke when export-visible behavior changed

If the slice is design-only, say so explicitly instead of implying that runtime
or visual validation was completed.

---

## Collaboration Rule With Governance Threads

When VIZ work will later be reviewed by a Governance thread, the preferred order
is:

1. local owner/boundary note or proposal in `viz3d_panda/docs/developments/`
2. bounded implementation if authorized
3. local implementation report
4. governance-facing summary only if the result changes a cross-layer contract
   or default behavior decision

This keeps the local technical truth close to the code while still giving
Governance a clean handoff surface.
