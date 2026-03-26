# dev_v2.0 Settings Mapping Directory (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap / settings ownership record
Affected Parameters: none beyond the already-authorized viewer `--steps` override surface
New Variables Introduced: none
Cross-Dimension Coupling: viewer inherits layered 2D simulation settings and consumes the resulting replay data; no parallel 3D simulation stack is introduced
Mapping Impact: clarifies ownership only; canonical mapping is unchanged
Governance Impact: records the Step 1 inheritance-first / duplication-last boundary for `viz3d_panda/`
Backward Compatible: yes

Summary
- `viz3d_panda/` inherits existing layered `test_run` simulation settings by default.
- The only simulation-facing override retained on the viewer surface is explicit `--steps`.
- Viewer-local settings stay limited to display and usability concerns.
- No `scenario`, `movement`, `contact`, `runtime`, or `observer` mirror surface is created under `viz3d_panda/`.
- `max_time_steps` does not get a parallel 3D default contract.
- This document is a boundary record, not a new settings spec.

## Part 1 - Inherited 2D Simulation Settings

| Setting | Source file / layer | Current interpreter | Viewer inheritance path | Override allowed this turn |
| --- | --- | --- | --- | --- |
| `run_control.max_time_steps` | `test_run/test_run_v1_0.runtime.settings.json`, merged by `test_run/settings_accessor.py` | `test_run/test_run_scenario.py` and `test_run/test_run_execution.py` | `viz3d_panda/replay_source.py` loads layered settings and passes the resolved value through unchanged unless the human explicitly passes `--steps` | `Yes`, but only through explicit `--steps` |
| `fleet.*`, `unit.*`, `battlefield.*` | `test_run/test_run_v1_0.runtime.settings.json`, merged layered settings | `test_run/test_run_scenario.py` prepares the active scenario and initial state | Viewer does not mirror these fields; it reuses the prepared active scenario via `test_run_entry.run_active_surface(...)` | `No` |
| `runtime.*` | `test_run/test_run_v1_0.runtime.settings.json` plus layered overlays | `test_run/test_run_execution.py` and the maintained runtime path reached through `test_run` | Viewer inherits by passing layered settings into the maintained active-surface execution path | `No` |
| `visualization.vector_display_mode` | `test_run/test_run_v1_0.settings.json` layered visualization section | `test_run/test_run_v1_0_viz.py` for 2D display semantics | `viz3d_panda/replay_source.py` reads the same layered setting and resolves 3D heading with the same display-mode contract | `No` |
| `visualization.show_attack_target_lines` | `test_run/test_run_v1_0.settings.json` layered visualization section | 2D visualization / target-line display logic | Viewer reads the same flag to decide whether replay capture must include target links for display-direction reconstruction | `No` |

Notes:
- Inheritance happens through `test_run/settings_accessor.py`, not through a duplicated `viz3d_panda` settings file.
- The viewer is a consumer of resolved simulation output. It does not become the owner of simulation meaning.

## Part 2 - Viewer-Local Settings

| Setting | Scope | Changes simulation meaning | Why it can stay viewer-local |
| --- | --- | --- | --- |
| `--playback-fps` | Playback speed inside the Panda3D viewer | `No` | It changes only how fast captured frames are replayed on screen |
| `--window-width`, `--window-height` | Panda3D window size | `No` | Pure display ergonomics |
| `--frame-stride` | Replay capture density for the viewer bundle | `No` | Simulation still runs on the same maintained tick path; this only changes how often frames are sampled for viewing |
| camera controls in `viz3d_panda/camera_controller.py` | Orbit / pan / zoom behavior | `No` | View framing only |
| glyph shape, token alpha, HP bucket scales in `viz3d_panda/unit_renderer.py` | Unit rendering style | `No` | Pure readability / display treatment |
| playback stepping / looping in `viz3d_panda/app.py` | Viewer interaction | `No` | Changes replay navigation only after simulation output already exists |

Notes:
- Viewer-local means display or usability only.
- Viewer-local does not authorize a shadow simulation policy layer.

## Part 3 - Explicit Non-Surface Items

The following are explicitly not introduced as independent `viz3d_panda` settings surfaces in this turn:

- `scenario` settings mirror
- `movement` settings mirror
- `contact` settings mirror
- `observer` settings mirror
- `runtime` settings mirror
- `battlefield` settings mirror
- parallel `max_time_steps` default semantics
- new 3D-native replay format settings

Current rule:

- simulation ownership stays with the existing layered `test_run` contract
- viewer ownership stays with display and usability only
- explicit `--steps` is the single bounded exception, and it reuses the same tick meaning as the maintained 2D path
