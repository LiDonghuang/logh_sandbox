# Phase A Thread Reading List (2026-03-19)

Status: working navigation document  
Purpose: structured reading list for a fresh thread, and later reference for A2 document cleanup  
Scope: current project background, active Phase A context, and practical code-entry order  
Authority: navigation only, not canonical semantics authority

## How To Use This List

Read in tiers.

- Tier 0: mandatory thread bootstrapping
- Tier 1: current phase and cleanup context
- Tier 2: active code surface
- Tier 3: optional detail / evidence
- Tier 4: historical material to defer

The point is not to read everything. The point is to get oriented quickly without getting buried in old experiment residue.

## Tier 0 - Mandatory Bootstrapping

These are the first files a new thread should read.

### 1. `AGENTS.md`

Why:

- defines execution contract
- defines frozen layers
- defines TS migration rule
- defines no-silent-fallback rule
- defines commit/push discipline

Why it matters now:

- current work is still inside `Phase A`
- several recent cleanup decisions were constrained directly by `AGENTS`

Cleanup tag:

- `active / mandatory`

### 2. `archive/ts_handoff_archive/TS_HANDOFF_20260319_210459/TS_HANDOFF_20260319_210459.md`

Why:

- most compact current-state handoff
- captures completed / in-progress / pending
- records recent human dissatisfaction as a real risk signal
- lists carried constraints and recommended next steps

Why it matters now:

- this is the best single-file continuity bridge into a fresh thread

Cleanup tag:

- `active / handoff`

### 3. `repo_context.md`

Why:

- high-level repo orientation
- current phase focus
- key entry files and config files

Cleanup tag:

- `active / governance index`

### 4. `system_map.md`

Why:

- current layer map
- clarifies how schema, engine, harness, launcher, viz, and settings fit together

Cleanup tag:

- `active / governance index`

## Tier 1 - Current Phase A Context

These explain what we are doing now, and what not to do.

### 5. `docs/Global_Road_Map_Engagement_to_Personality_20260318.md`

Why:

- top-level phase ordering
- defines the current sequence:
  - Engagement Substrate Modernization
  - Neutral Baseline Rebuild
  - Personality Restart
- shows that current work is still in `Phase A`

Cleanup tag:

- `active / roadmap`

### 6. `docs/phase_a_governance_update_20260319.md`

Why:

- most recent compact governance-facing status
- records the key correction:
  - subtraction first
  - quieter stdout
  - smaller routine regression gate
- explicitly records human dissatisfaction about fake simplification

Cleanup tag:

- `active / phase summary`

### 7. `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_harness_cleanup_record_20260319.md`

Why:

- summarizes what A5 has already changed
- useful before touching `test_run_main.py`, `test_run_experiments.py`, or `settings_accessor.py`

Cleanup tag:

- `active / cleanup record`

### 8. `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_anchor_regression_policy_20260319.md`

Why:

- current validation policy
- default routine regression is now `3 runs`
- `9 runs` only for major changes

Cleanup tag:

- `active / validation policy`

## Tier 2 - Settings And Harness Surface

This is the most important code-adjacent reading tier for Phase A.

### 9. `test_run/test_run_v1_0.settings.reference.md`

Why:

- explains layered settings structure
- explains which settings file carries what responsibility

Cleanup tag:

- `active / interface reference`

### 10. `test_run/test_run_v1_0.settings.json`

Why:

- thin entry settings file
- shows layer pointer structure

Cleanup tag:

- `active / entry config`

### 11. `test_run/test_run_v1_0.runtime.settings.json`

Why:

- current runtime-facing values

Cleanup tag:

- `active / runtime config`

### 12. `test_run/test_run_v1_0.testonly.settings.json`

Why:

- current test-only controls and mode surface
- important because Phase A cleanup still lives largely in `test_run`

Cleanup tag:

- `active / test-only config`

### 13. `test_run/test_run_v1_0.viz.settings.json`

Why:

- current viz-side values
- relevant before `A4`

Cleanup tag:

- `active / viz config`

### 14. `test_run/test_run_v1_0.settings.comments.json`

Why:

- active comments aligned to current settings surface
- should stay in sync with live modes and live keys

Cleanup tag:

- `active / comments source`

### 15. `test_run/settings_accessor.py`

Why:

- all layered settings loading/access now routes through here
- touching settings without reading this first is risky

Cleanup tag:

- `active / harness plumbing`

### 16. `test_run/test_run_v1_0.py`

Why:

- engine-facing harness core
- still the key bridge between runtime skeleton and `test_run`
- contains core helper surface that later cleanup may still narrow

Cleanup tag:

- `active / harness core`

### 17. `test_run/test_run_experiments.py`

Why:

- build initial state
- execute simulation
- collect telemetry
- this is now the main execution surface outside launcher/orchestration

Cleanup tag:

- `active / experiment execution`

### 18. `test_run/test_run_main.py`

Why:

- launcher/orchestration entry
- current main cleanup pain point
- the place where "claimed simplification vs real subtraction" must be judged most strictly

Cleanup tag:

- `active / primary A5 target`

### 19. `test_run/test_run_v1_0_viz.py`

Why:

- rendering / plots / animation export
- should be read before starting `A4`

Cleanup tag:

- `active / A4 target`

## Tier 3 - Runtime / Engine Foundation

Read this tier when the thread needs to understand what `test_run` is sitting on top of.

### 20. `runtime/runtime_v0_1.py`

Why:

- runtime schema and state types

Cleanup tag:

- `active / foundation`

### 21. `runtime/engine_skeleton.py`

Why:

- frozen engine skeleton
- required to understand actual tick pipeline boundaries

Important:

- read-only under `AGENTS`

Cleanup tag:

- `active / frozen foundation`

### 22. `docs/governance/Baseline_Replacement_Protocol_v1.0.md`

Why:

- required reference when judging experiment vs baseline-replacement boundaries

Important:

- read for boundary discipline
- do not duplicate its workflow into ad hoc thread doctrine

Cleanup tag:

- `active / governance protocol`

## Tier 4 - Optional Evidence / Point-in-Time Artifacts

These are useful, but they are not startup reading.

### 23. `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.md`
### 24. `analysis/engineering_reports/developments/20260318/structural_cleanup/a5_iteration0_baseline_anchor_20260318.json`

Why:

- baseline anchor evidence for A5 changes
- useful when validating structural cleanup

When to read:

- only if you are about to validate nontrivial A5 changes

Cleanup tag:

- `active / validation evidence`

### 25. `test_run/battle_report_builder.py`
### 26. `test_run/brf_narrative_messages.py`

Why:

- relevant only if a thread is touching battle report generation or narrative/export behavior

When to read:

- defer unless the thread is explicitly on battle report cleanup

Cleanup tag:

- `active / deferred subsystem`

## Tier 5 - Historical Material To Defer

These may contain concept history, but should not be startup reading.

### 27. `analysis/engineering_reports/developments/...`

Why defer:

- large historical volume
- much of it reflects retired or superseded intermediate states
- current guidance is to use concept-level lessons only, not to treat old DOE scripts or historical points as reproducible active workflow

Use only when:

- a thread explicitly needs concept history
- or `A2` document cleanup is organizing archives and statuses

Cleanup tag:

- `archive / defer by default`

### 28. Historical DOE scripts under `analysis/...`

Why defer:

- they are not an active reproducibility target
- they should not constrain current cleanup or active harness decisions

Cleanup tag:

- `archive / non-startup`

## Recommended Startup Reading Order For A Fresh Thread

If the new thread is continuing current `Phase A` work, use this order:

1. `AGENTS.md`
2. `archive/ts_handoff_archive/TS_HANDOFF_20260319_210459/TS_HANDOFF_20260319_210459.md`
3. `repo_context.md`
4. `system_map.md`
5. `docs/Global_Road_Map_Engagement_to_Personality_20260318.md`
6. `docs/phase_a_governance_update_20260319.md`
7. `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_harness_cleanup_record_20260319.md`
8. `analysis/engineering_reports/developments/20260318/structural_cleanup/test_run_anchor_regression_policy_20260319.md`
9. `test_run/test_run_v1_0.settings.reference.md`
10. `test_run/settings_accessor.py`
11. `test_run/test_run_v1_0.py`
12. `test_run/test_run_experiments.py`
13. `test_run/test_run_main.py`
14. `test_run/test_run_v1_0_viz.py` only if touching `A4`

## Recommended Cleanup Use Later (A2)

This document can later be used as a cleanup scaffold:

- keep Tier 0 / Tier 1 items visible and current
- keep Tier 2 items aligned with live interfaces
- move stale or superseded point-in-time artifacts downward into historical/archive groups
- keep startup reading short; do not let archive material drift back into mandatory reading
