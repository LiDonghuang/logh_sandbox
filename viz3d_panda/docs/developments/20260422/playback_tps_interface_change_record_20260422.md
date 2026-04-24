# LOGH Sandbox

## Playback TPS Interface Change Record 20260422

Date: 2026-04-22  
Scope: VIZ-local playback control surface and camera-take schema change in `viz3d_panda/`  
Status: implemented locally; compile-checked; viewer/export smoke not run in this note

---

## 1. One-sentence conclusion

The viewer playback-rate surface now uses `tps` rather than `fps`, with fixed
levels `0.5 / 1 / 2 / 5 / 10`, and camera-take payloads now record
`playback_tps` under `format_version = 2`.

---

## 2. Why this record exists

This is more than a wording cleanup.

It changes:

- the viewer CLI surface
- the HUD wording
- the camera-take replay/export carrier
- the meaning boundary between replay tick rate and true renderer frame rate

That makes it a VIZ-local interface change worth recording independently.

---

## 3. Exact active surfaces changed

Primary owner path:

- `viz3d_panda/app.py`

Companion renderer path:

- `viz3d_panda/unit_renderer.py`

Updated viewer-side references:

- `viz3d_panda/docs/3D_VIZ_Debug_Block_Reference_v1.0.md`
- `viz3d_panda/docs/3D_VIZ_Cluster_Micro_Sway_Reference_v1.0.md`

---

## 4. Exact interface changes

### CLI

Changed:

- `--playback-fps`

To:

- `--playback-tps`

Supported fixed levels now:

- `0.5`
- `1`
- `2`
- `5`
- `10`

### HUD wording

Changed stable HUD line label:

- `fps=...`

To:

- `tps=...`

### Camera-take payload

Changed replay-request field:

- `playback_fps`

To:

- `playback_tps`

Changed viewer-snapshot field:

- `playback_fps`

To:

- `playback_tps`

Changed take schema version:

- `format_version = 1`

To:

- `format_version = 2`

---

## 5. Compatibility decision in this slice

This slice does **not** silently migrate old camera-take payloads.

Current behavior:

- old `format_version = 1` takes fail fast with an explicit message
- the failure names the reason:
  - pre-TPS `playback_fps` schema

This was chosen to avoid silent fallback or hidden schema duality during the
rename.

---

## 6. Fire-link behavior change in this slice

This slice also removes the current fire-link pulse-speed multiplier that was
derived from `playback_level_index`.

Reason:

- after the fixed levels changed, `2 tps` moved from the old lowest gear
  position to the new middle gear position
- keeping index-based fire-link scaling would make equal numeric tick rates
  look different only because the gear slot moved

Current post-change rule:

- fire-link pulse motion follows replay playback time and
  `FIRE_LINK_BASE_SPEED_PER_SECOND`
- it no longer gets extra speed from gear index alone

---

## 7. What did not change

Still unchanged in this slice:

- no runtime/test-run semantics change
- no camera-tracking gear-profile redesign
- no new renderer-frame-rate parameter
- no broad slow-clock semantics rework

Important remaining reality:

- `camera_controller.py` still uses `playback_level_index` for tracked-camera
  smoothing profile
- so not every gear-dependent viewer behavior now follows numeric `tps`

That remaining split is intentional for this bounded slice.

---

## 8. Validation performed

Performed in this turn:

- static owner/path audit
- compile check for:
  - `viz3d_panda/app.py`
  - `viz3d_panda/unit_renderer.py`
  - `viz3d_panda/camera_controller.py`
  - `viz3d_panda/export_video.py`
- CLI help check for:
  - `python -m viz3d_panda.app --help`
- fixed-level resolution smoke for:
  - `0.5 / 1 / 2 / 5 / 10`

Not performed in this turn:

- live viewer visual smoke
- offline export smoke

---

## 9. Short governance-facing read

VIZ now reserves the term `fps` for future true render-frame-rate controls and
uses `tps` for replay playback tick rate.

This is an implemented VIZ-local interface correction, not a runtime semantics
change.
