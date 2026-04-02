# LOGH Sandbox

## 3D VIZ Debug Block Reference v1.0

Status: maintained viewer reference  
Scope: `viz3d_panda/app.py` left-bottom debug block  
Authority: viewer-side reference only, not runtime doctrine

---

## Purpose

This note records the meaning of the 3D viewer debug block.

The block is intentionally allowed to change over time.
The last one or two lines may be repurposed as "current focus indicators"
for the mechanism currently under investigation.

When indicators are added, removed, shown, or hidden, this document should be
updated together with the viewer change.

---

## Layout Rule

The left-bottom debug block and the right-bottom control block share one common
bottom inset parameter in `viz3d_panda/app.py`:

- `HUD_BOTTOM_INSET`

This keeps:

- the debug block's last line above the bottom edge
- the right-side control block aligned to the same bottom margin

The current layout rule is:

- first build the full text content
- then count lines
- then place each block so its **bottom edge** respects `HUD_BOTTOM_INSET`

The two blocks therefore share a bottom edge margin rather than a top edge margin.

---

## Always-Shown Lines

### Line 1

- content: fleet alive counts + playback state
- example: `A=100 B=100  state=playing`
- shown in HUD: yes

### Line 2

- content: frame / fps / gear
- example: `frame=120/600  fps=6.0  gear=3/5`
- shown in HUD: yes

### Line 3

- content: fleet centroids
- example: `A=(12.4, 48.1)  B=(87.7, 49.3)`
- shown in HUD: yes

### Line 4

- content: fleet centroid speed per frame
- definition: absolute centroid displacement from frame `t-1` to frame `t`
- example: `speed/frame: A=0.73  B=0.68`
- shown in HUD: yes

### Line 5

- content: viewer mode tail
- current fields:
  - direction mode
  - fire-link mode
  - smoothing state
  - fixture readout when present
- shown in HUD: yes

---

## Focus Indicators

These lines are intentionally temporary/replaceable.
They are the preferred place to expose the current mechanism-level indicators
that Human and Engineering are actively using.

### `focus <fleet_id>`

- shown in HUD: yes
- source: `runtime_debug.focus_indicators[<fleet_id>]`

Current fields:

- `td`
  - source field: `td_norm`
  - meaning: norm of the current fleet target-direction vector
  - current read: remaining advance/target authority after current budgeting

- `adv`
  - source field: `advance_share`
  - meaning: current transition advance share
  - current read: how much forward advance authority remains after shape-vs-advance budgeting

- `shape_err`
  - source field: `shape_err`
  - meaning: current mismatch between actual formation half-extents and target half-extents

- `fcur`
  - source field: `forward_current`
  - meaning: current carrier-owned forward half-extent
  - current read: what the formation-transition carrier thinks the forward size should be now

- `afwd`
  - source field: `actual_forward`
  - meaning: actual live-unit forward half-extent measured on the current morphology axis

- `lcur`
  - source field: `lateral_current`
  - meaning: current carrier-owned lateral half-extent

- `alat`
  - source field: `actual_lateral`
  - meaning: actual live-unit lateral half-extent measured on the current morphology axis

The viewer currently prints these as:

- `fcur/afwd`
- `lcur/alat`

This makes the current target-vs-actual half-extents readable as pairs.

Because both forward and lateral values are half-extents, the aspect-ratio read is unchanged:

- target aspect ratio ≈ `lcur / fcur`
- actual aspect ratio ≈ `alat / afwd`

### `focus <fleet_id>+`

- shown in HUD: yes when any current focus transport indicators are finite
- source: `runtime_debug.focus_indicators[<fleet_id>]`

Current fields:

- `ctr_fwd`
  - source field: `center_forward_offset`
  - meaning: forward-axis difference between morphology center and live centroid
  - current read: whether the whole formation reference body is being dragged ahead/behind the live body

- `phase_fwd`
  - source field: `phase_forward_mean`
  - meaning: mean forward delta caused by phase/extent target alone, without center offset
  - current read: whether phase ownership itself is pulling the fleet forward/backward on average

- `fwd_align`
  - source field: `forward_align`
  - meaning: fraction of units whose forward transport sign is topologically aligned
  - current read:
    - front-side units should tend to move backward when compressing
    - rear-side units should tend to move forward when compressing
    - higher value means the transport intent is more topologically consistent

- `fwd-`
  - source field: `forward_neg_frac`
  - meaning: fraction of units with negative forward transport delta

- `fwd+`
  - source field: `forward_pos_frac`
  - meaning: fraction of units with positive forward transport delta

`forward_delta_mean` is still available in the harness bundle as a local diagnostic,
but it is **not** currently shown in the HUD.
For the current investigation, the positive/negative split is easier to read than
one signed mean, because the mean can hide a symmetric split.

---

## Display Status Table

| Field / line | Shown in HUD | Notes |
| --- | --- | --- |
| alive counts + playback state | yes | stable line |
| frame / fps / gear | yes | stable line |
| fleet centroids | yes | stable line |
| centroid speed per frame | yes | stable line |
| direction / fire-links / smoothing / fixture tail | yes | stable line |
| `td_norm` | yes | current focus line |
| `advance_share` | yes | current focus line |
| `shape_err` | yes | current focus line |
| `forward_current` | yes | current focus line |
| `actual_forward` | yes | current focus line |
| `lateral_current` | yes | current focus line |
| `actual_lateral` | yes | current focus line |
| `center_forward_offset` | yes | current focus line |
| `phase_forward_mean` | yes | current focus line |
| `forward_align` | yes | current focus line |
| `forward_neg_frac` | yes | current focus line |
| `forward_pos_frac` | yes | current focus line |
| `forward_delta_mean` | no | kept in harness payload only |
| additional future temporary indicators | maybe | must be added here when introduced |

---

## Maintenance Rule

When the current focus indicators change:

1. update `viz3d_panda/app.py`
2. update this document
3. mark whether each indicator is currently shown in HUD

This avoids repeated re-explanation in thread and keeps Human-readable viewer
semantics synchronized with the active investigation line.
