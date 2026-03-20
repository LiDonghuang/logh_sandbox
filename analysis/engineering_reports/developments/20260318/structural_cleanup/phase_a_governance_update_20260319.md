# Phase A Governance Update (2026-03-19)

Status: Working update for governance-side review  
Scope: Phase A progress, current issues, human dissatisfaction, immediate correction direction

## Completed / Established

- A1 hostile penetration line has been frozen into working/stopped/failed identities.
- A3 settings layering has been completed:
  - runtime values
  - test-only values
  - viz values
  - comments/reference separation
- A5 harness separation has materially progressed:
  - `test_run/test_run_main.py`
  - `test_run/test_run_experiments.py`
  - `test_run/settings_accessor.py`
  - `test_run/test_run_v1_0.py` now carries a more engine-facing helper/core role

## Current Problem

Phase A harness cleanup has improved boundary clarity, but has underperformed on actual subtraction.

The main concrete failure:

- repeated engineering claims of "simplification" did not consistently reduce launcher size or perceived weight
- `test_run/test_run_main.py` remained large and heavily parameter-passing
- helper growth often outpaced visible reduction

## Human Dissatisfaction (Explicit)

Human architect dissatisfaction is now itself a material governance signal.

The complaint is not that cleanup was attempted, but that:

- code was often made more explicit without becoming meaningfully lighter
- default stdout became too noisy and too detailed
- parameter passthrough remained excessive
- "safe refactor" repeatedly drifted into additive wrapper growth

The human explicitly reports reduced trust in repeated claims of simplification when script size and weight did not visibly go down.

## Immediate Correction Direction

The current correction direction should be:

- subtraction first, not helper proliferation
- fail-fast on invalid launcher-consumed settings
- much quieter default stdout
- smaller routine regression gate:
  - default 3-run anchor
  - full 9-run only for major changes

## Current Working Assessment

Boundary clarity has improved.
Human-facing maintainability has not improved enough.

Phase A should continue, but with a stricter standard:

- real line-count pressure
- real stdout reduction
- real interface narrowing
- no more counting additive indirection as "simplification"
