# LOGH Sandbox

## GPU / Batch Owner Boundary Note 20260422

Date: 2026-04-22  
Scope: static owner/boundary audit for future viewer-local GPU / batch-drawing work in `viz3d_panda/`  
Status: owner note only; no implementation in this document

---

## 1. One-sentence conclusion

The smallest honest next-stage design for future GPU / batch-drawing work is to
keep `viz3d_panda/app.py` as the playback/export host, keep
`viz3d_panda/scene_builder.py` as the static scene shell, and treat
`viz3d_panda/unit_renderer.py` as the primary owner for any renderer-backend
evolution.

---

## 2. Purpose

This note exists to freeze the owner/boundary read before a larger VIZ
optimization line begins.

The goal of this note is **not** to optimize the current viewer.

The goal is:

- identify the active owner of dynamic battlefield visuals
- separate static scene assembly from per-frame render work
- keep replay/view ownership separate from runtime ownership
- name the smallest honest next slice for a future GPU / batch path

---

## 3. Static owner/path audit

### 3.1 `viz3d_panda/app.py`

Current active role:

- viewer host
- playback state owner
- camera-take / export carrier
- app-facing renderer control surface

Current active entry and control paths:

- `FleetViewerApp.__init__(...)` at line `441`
- `_render_frame(...)` at line `900`
- `_tick(...)` at line `1468`
- `export_camera_take_video(...)` at line `1569`

Current boundary read:

- this file owns orchestration
- this file does **not** own low-level renderer backend detail
- live viewer and offline export both reuse this host path

Implication:

- future backend work must preserve host-level parity between live playback and
  export
- `app.py` should not become the dynamic draw backend owner

### 3.2 `viz3d_panda/scene_builder.py`

Current active role:

- static scene-shell assembly

Current active entry and build paths:

- `_attach_skybox(...)` at line `136`
- `build_scene(...)` at line `167`

Current boundary read:

- skybox / lights / grid / axes are built here
- no active token / cluster / fire-link hot path is owned here
- this file is currently construction-time, not per-frame dynamic rendering

Implication:

- `scene_builder.py` may host static attachment roots
- it should not absorb battlefield draw-update ownership

### 3.3 `viz3d_panda/unit_renderer.py`

Current active role:

- dynamic battlefield visual owner
- per-frame unit transform owner
- fire-link draw owner
- fleet halo / objective marker owner

Current active hot paths:

- `UnitRenderer.__init__(...)` at line `405`
- `update_view(...)` at line `638`
- `sync_frame(...)` at line `881`
- `apply_interpolated_transforms(...)` at line `954`
- `_sync_fire_links(...)` at line `988`

Current boundary read:

- this file already centralizes the visual families most likely to need shared
  acceleration strategy
- it currently mixes:
  - frame-to-frame visual-state derivation
  - Panda3D node mutation
  - line geometry rebuild

Implication:

- the future backend seam belongs here first
- the first honest separation is inside the renderer family, not above it

---

## 4. Active visual family read

The currently active visual-performance family in scope is:

- token / cluster presentation
- fire links
- fleet halos
- objective marker

Important reality:

- `explosion FX` is not an active owner path in the audited files today
- it should not be invented as a separate app-level subsystem by default
- if later activated, it should be considered part of the same battlefield
  visual family rather than a new host-layer owner

---

## 5. Static hot-path observations

This note is static-only and does not claim profiler proof.

Still, current code-path truth suggests the likely rendering burden is a mixed
family rather than one isolated decorative effect.

Observed current pressure points:

- `sync_frame(...)`
  - owns unit-node create/show/remove and root transform writes
- `update_view(...)`
  - walks all unit nodes for camera-distance-driven token/cluster visibility and
    alpha decisions
- `_sync_fire_links(...)`
  - removes and rebuilds the full fire-link geometry node for active updates
- `sync_fleet_halos(...)`
  - updates halo placement and color-scale state per frame

This supports a design read of:

- not another small CPU micro-tune first
- instead, first define a renderer-owned backend boundary for the whole dynamic
  battlefield family

---

## 6. Owner boundary that should remain fixed

### Keep in `app.py`

- playback timing
- camera-take state
- export-path orchestration
- viewer input / hotkeys
- app-facing renderer mode toggles

### Keep in `scene_builder.py`

- skybox
- static scene shell
- static attachment environment

### Keep in `unit_renderer.py`

- unit visual family ownership
- visual-state derivation from replay frame + camera + playback timing
- actual battlefield draw/update backend ownership

### Do not move into VIZ from outside

- runtime battle semantics
- test harness experiment doctrine
- governance/report doctrine

---

## 7. Smallest honest future backend seam

If a future bounded implementation is authorized, the smallest honest seam is:

1. keep the current app host and export path
2. keep the current replay carrier
3. split renderer-private logic into:
   - visual-state compilation
   - draw backend application
4. keep that split inside the renderer family first

Practical meaning:

- `app.py` should continue to submit high-level replay/camera/timing state
- `unit_renderer.py` should decide how that state becomes draw commands or node
  updates
- any later GPU / batch backend should be renderer-owned rather than app-owned

---

## 8. Recommended first bounded implementation slice if later authorized

Recommended first slice:

- start with `token / cluster` and `fire links`

Reason:

- these are the clearest high-frequency dynamic visual paths in the current
  code
- they already live under one owner
- they affect both live playback and export-visible output

Recommended secondary hold-outs for the first slice:

- leave `fleet halos` and `objective marker` on the current path initially
- only fold them into a later acceleration pass if the first renderer seam
  proves stable

---

## 9. Exact target file read for that later slice

Primary target file:

- `viz3d_panda/unit_renderer.py`

Possible narrow companion file:

- `viz3d_panda/app.py`
  - only if a small public renderer control surface must be added

Possible static companion file:

- `viz3d_panda/scene_builder.py`
  - only if a renderer-owned static mount point is needed

Not recommended as the first move:

- broad file fan-out
- new app-level backend coordinator
- split live viewer and export into separate renderer implementations

---

## 10. Validation posture for later work

If later implementation is authorized, minimum honest validation should be:

- static owner/path audit
- compile check for touched `viz3d_panda/*.py`
- live viewer smoke
- export-path smoke
- explicit confirmation that the same camera-take/export path still works

This note itself performed:

- static owner/path audit only

---

## 11. Open risks / unknowns

- this note does not claim profiler-backed cost ranking
- transparent overdraw vs node churn vs line rebuild cost still needs measured
  confirmation later
- a future backend seam must preserve camera-take/export parity
- future dynamic VFX such as explosion work should not be attached to the wrong
  owner by convenience

---

## 12. Short governance-facing read

Engineering-VIZ should treat future GPU / batch-drawing work as a viewer-local
renderer-family line first.

Current recommended owner framing:

- host and export carrier remain in `app.py`
- static scene shell remains in `scene_builder.py`
- dynamic battlefield render evolution remains under `unit_renderer.py`

That is the smallest honest boundary before implementation begins.
