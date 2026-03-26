# dev_v2.0 Container Boundary Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap boundary record
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: `viz3d_panda/` consumes existing 2D `test_run` output but does not own simulation meaning
Mapping Impact: ownership clarification only
Governance Impact: pins `viz3d_panda/` to the Step 2 container identity and dependency boundary
Backward Compatible: yes

Summary
- `viz3d_panda/` is an additive 3D replay/viewer bootstrap container.
- Simulation ownership remains in the maintained 2D `test_run` / runtime path.
- Viewer ownership is limited to replay consumption, scene setup, rendering, camera, and viewer-local usability.
- `app.py` owns launch/playback wiring, not simulation policy.
- `replay_source.py` owns replay consumption, not battle semantics.
- `scene_builder.py`, `unit_renderer.py`, and `camera_controller.py` remain viewer-local modules only.
- Legal growth stays display-side and additive.
- Growth into 3D mechanism, parallel settings ownership, or replay-protocol ownership is out of bounds.

## Formal Identity

`viz3d_panda/` should be read as:

- additive 3D replay / viewer bootstrap container

It should not be read as:

- 3D combat runtime
- 3D movement substrate
- 3D formation engine
- 3D simulation owner
- canonical baseline container

## Module Boundary

- `viz3d_panda/app.py`
  - Owns CLI parsing, Panda window setup, playback loop, overlay text, and top-level wiring.
  - Does not own replay generation semantics, stop contract semantics, or battle rules.

- `viz3d_panda/replay_source.py`
  - Owns consumption of existing maintained-path output and normalization into a viewer replay bundle.
  - May interpret viewer display direction from already-owned 2D output.
  - Does not own simulation state evolution, parameter meaning, or canonical replay protocol design.

- `viz3d_panda/scene_builder.py`
  - Owns scene root, lights, grid, and simple axes.
  - Does not own asset-pipeline policy, semantic terrain, or battlefield rules.

- `viz3d_panda/unit_renderer.py`
  - Owns viewer glyph geometry, color application, HP-size bucket rendering, and per-frame node sync.
  - Does not own movement logic, target logic, or formation semantics.

- `viz3d_panda/camera_controller.py`
  - Owns orbit / pan / zoom camera interaction only.
  - Does not own tactical camera doctrine, semantic framing rules, or simulation timing.

## Allowed Dependency Directions

Allowed:

- `app.py` -> viewer-local modules (`replay_source.py`, `scene_builder.py`, `unit_renderer.py`, `camera_controller.py`)
- `replay_source.py` -> maintained 2D harness access (`test_run_entry.py`, `test_run_scenario.py`, `settings_accessor.py`)
- `unit_renderer.py` -> viewer replay types only
- `scene_builder.py` and `camera_controller.py` -> Panda3D only

Not allowed:

- `scene_builder.py` -> `test_run/` or runtime modules
- `unit_renderer.py` -> `test_run/` or runtime modules
- `camera_controller.py` -> `test_run/` or runtime modules
- `app.py` -> direct simulation ownership logic beyond the bounded replay load call
- `viz3d_panda/` -> new canonical replay/schema owner role

## Legal Growth

Growth is still legal when it stays inside:

- viewer-local playback controls
- scene readability improvements
- display-only smoothing
- bounded camera usability
- additive bootstrap documentation

Growth becomes out-of-bounds when it starts adding:

- 3D movement logic
- 3D combat logic
- 3D formation semantics
- parallel simulation settings
- replay protocol ownership
- doctrine or parameter reinterpretation
