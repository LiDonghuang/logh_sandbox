# Test Run Anchor Regression Policy (2026-03-19)

Scope: harness-only / protocol

## Default Rule

Routine harness cleanup should use a 3-run anchor regression, not the full 9-run matrix.

Default 3-run set:

- fixture: `neutral_close_100v100`
- modes:
  - `off`
  - `hybrid_v2`
  - `intent_unified_spacing_v1`

## Escalation Rule

Use the full 9-run matrix only for major changes, including:

- broad multi-file runtime/harness restructuring
- public `test_run` configuration interface change
- observer interpretation boundary change
- movement/combat execution path change

## Rationale

- keeps routine A5 cleanup cheaper
- preserves the 9-run matrix as a higher-cost guardrail for major turns
- avoids treating every launcher/harness edit as a full protocol event
