# dev_v2.0 Anti-Fat Guardrail Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: additive 3D viewer bootstrap governance guardrail record
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: guardrails keep viewer consumption separate from 2D/runtime ownership
Mapping Impact: none
Governance Impact: defines the anti-fat checks for continued `viz3d_panda/` work
Backward Compatible: yes

Summary
- The main Step 2 risk is `viz3d_panda/` gradually absorbing simulation-like ownership.
- The most likely fattening points are replay shaping, settings duplication, semantic state mapping, and tactical camera logic.
- Viewer-local convenience is allowed; parallel simulation ownership is not.
- Display smoothing is allowed; semantic smoothing is not.
- Any move toward 3D mechanism, protocol ownership, or generalized engine scope must return to Governance first.

## Core Rules

- Inheritance first, duplication last
- Viewer consumes, runtime owns
- Display smoothing is allowed; semantic smoothing is not
- Viewer-local convenience is allowed; parallel simulation ownership is not
- Additive bootstrap first; generalized engine later only by explicit authorization

## Likely Fat-Risk Points

- `replay_source.py` starts accumulating simulation-policy branching or replay-schema ownership
- `app.py` starts carrying parameter semantics, stop semantics, or scenario-selection policy
- `unit_renderer.py` starts mapping semantic state into multiple doctrine-like visual channels
- `camera_controller.py` starts encoding tactical intent rather than camera convenience
- new viewer-local config files begin mirroring 2D simulation settings

## Current Prohibited List

- 3D movement logic
- 3D combat logic
- 3D formation semantics
- parallel simulation settings stack
- generalized replay protocol redesign
- observer / doctrine / parameter meaning reinterpretation
- generalized engine-container growth under `viz3d_panda/`

## Observation Signals

Treat the viewer bootstrap as starting to become fat when any of these appear:

- a new `viz3d_panda` module needs direct runtime ownership knowledge to function
- a viewer feature requires changing battle semantics rather than consuming existing output
- a new settings surface is added under `viz3d_panda/` for simulation-like values
- replay loading begins exporting or defining long-lived protocol contracts
- display smoothing begins changing semantic timing or semantic geometry rather than only visual presentation

## Governance Gate Before Any Step 3 Candidate

Governance review is required before opening any of the following:

- 3D movement substrate work
- 3D combat / targeting semantics
- 3D formation mechanics
- canonical replay format work
- new 3D-native runtime state ownership
- generalized asset-pipeline or engine-container expansion
