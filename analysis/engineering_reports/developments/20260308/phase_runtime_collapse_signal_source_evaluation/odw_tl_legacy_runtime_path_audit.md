# ODW TL Legacy Runtime Path Audit

Status: Active engineering audit  
Scope: Legacy parameter-path clarification only  
Implementation: No mechanism change authorized by this note

## Purpose

This note records the current runtime status of the legacy `offense_defense_weight` (ODW) and `targeting_logic` (TL) paths.

The purpose is clarification, not repair.

Both paths were treated for a long time as either experimental or inactive.
This audit confirms the current code reality so future mechanism work can start from an explicit baseline.

## ODW Current State

### Personality Layer

ODW exists in:

- `archetypes/archetypes_v1_5.json`
- `runtime/runtime_v0_1.py` as `PersonalityParameters.offense_defense_weight`
- `test_run/test_run_v1_0.py` personality loading and report export

### Runtime Consumption

Combat currently reads:

- `runtime/engine_skeleton.py:2388`
- `runtime/engine_skeleton.py:2389`

using:

```text
attacker.offense_defense_weight
target.offense_defense_weight
```

### Active Runtime Gap

`build_initial_state(...)` creates `UnitState(...)` without injecting archetype ODW.

Confirmed locations:

- `test_run/test_run_v1_0.py:1441`
- `test_run/test_run_v1_0.py:1455`

`UnitState.offense_defense_weight` therefore remains at the dataclass default:

- `runtime/runtime_v0_1.py:59`
- default = `0.5`

### Runtime Spot Check

Engineering spot check confirmed:

- fleet personality ODW changes correctly when archetype ODW is modified
- unit-level ODW remains `0.5` for all units

Therefore:

```text
ODW exists in personality data
but does not currently propagate into the active unit-level combat path
```

## TL Current State

### Personality Layer

TL exists in:

- `archetypes/archetypes_v1_5.json`
- `runtime/runtime_v0_1.py` as `PersonalityParameters.targeting_logic`
- `test_run/test_run_v1_0.py` personality loading and report export

### Runtime Consumption

Engineering search of the active runtime path found:

- no `targeting_logic` usage in `runtime/engine_skeleton.py`
- no `targeting_logic` usage in active target-selection logic

Therefore:

```text
TL is currently carried by archetype/personality/report layers
but is not consumed by the active runtime target-selection path
```

## Interpretation

The current system state is:

- `ODW`: partially wired historical path
  - present in personality data
  - present in combat formula
  - not injected into unit runtime state
- `TL`: dormant legacy path
  - present in personality data
  - not consumed by active runtime logic

These should be treated as:

- legacy reference traces
- future mechanism inputs for redesigned ODW / TL work

They should not be interpreted as currently active battlefield behavior controls.

## Engineering Recommendation

Do not repair these legacy paths as part of cleanup.

Future ODW and TL mechanism work should:

1. declare new intended runtime mapping explicitly
2. treat current ODW/TL behavior as legacy baseline
3. avoid assuming historical code paths were already active
