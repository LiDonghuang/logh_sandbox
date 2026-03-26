# dev_v2.0 Panda3D Bootstrap Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap container
Affected Parameters: none
New Variables Introduced: `.venv_dev_v2_0`, `viz3d_panda/` scaffold
Cross-Dimension Coupling: existing 2D `position_frames` consumed as viewer input only
Mapping Impact: none
Governance Impact: bounded to viewer/bootstrap only; no runtime semantic change
Backward Compatible: yes

Summary
- Panda3D is accepted here only as the first candidate for the `dev_v2.0` viewer bootstrap container.
- The isolated environment is `.venv_dev_v2_0`.
- The first scaffold is additive under `viz3d_panda/` and does not alter `runtime/` or canonical/governance layers.
- The first data contract is in-memory `test_run` output, especially returned `position_frames`.
- No repo-level persisted replay standard is introduced in this turn.

## Why Panda3D In This Turn

Panda3D fits the bounded bootstrap goal because it can be installed directly into the isolated branch-local venv and can open a Python-driven 3D scene without pulling in a larger game-stack commitment. That makes it suitable for answering the immediate question:

can an additive 3D viewer container consume current replay-like output and make it readable?

This note does **not** treat Panda3D as a final locked engine decision.

## Implemented Bootstrap Surface

The current first scaffold is:

- `viz3d_panda/__init__.py`
- `viz3d_panda/app.py`
- `viz3d_panda/replay_source.py`
- `viz3d_panda/scene_builder.py`
- `viz3d_panda/unit_renderer.py`
- `viz3d_panda/camera_controller.py`

Responsibility split is intentionally small:

- `app.py`: Panda3D entry, playback loop, overlay text, input wiring
- `replay_source.py`: existing `test_run` execution call and `position_frames` normalization
- `scene_builder.py`: simple scene/grid/light setup
- `unit_renderer.py`: unit placeholder drawing and per-frame updates
- `camera_controller.py`: bounded orbit/pan/zoom control

## Environment And Install

Isolated venv:

- `.venv_dev_v2_0`

Install command used in this turn:

```powershell
py -3 -m venv .venv_dev_v2_0
.\.venv_dev_v2_0\Scripts\python.exe -m pip install --upgrade pip panda3d
```

Minimal run command:

```powershell
.\.venv_dev_v2_0\Scripts\python.exe -m viz3d_panda.app
```

One-click launcher from repo root:

```powershell
.\launch_dev_v2_0_viewer.bat
```

Optional shorter replay command:

```powershell
.\.venv_dev_v2_0\Scripts\python.exe -m viz3d_panda.app --steps 180 --playback-fps 10
```

VS Code launch entry added in this turn:

- `dev_v2.0 Viewer (Panda3D)`

## Current Boundary

This scaffold currently **is**:

- a viewer/replay bootstrap container
- an additive branch-local prototype
- a consumer of current `test_run` output

This scaffold currently is **not**:

- a 3D runtime combat engine
- a 3D movement substrate
- a 3D formation mechanics implementation
- a persistent replay standard
- a generalized engine replacement branch

## Natural Next Step

If Governance keeps this line open, the most natural next step is not new 3D semantics. The natural next step is to stabilize the viewer container itself:

- confirm a small set of repeatable replay source presets
- decide whether a tiny debug export helper is needed
- improve scene readability and camera framing without changing runtime meaning
