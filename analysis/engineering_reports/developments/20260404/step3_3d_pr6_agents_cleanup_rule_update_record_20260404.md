# AGENTS Cleanup Rule Update Record - 2026-04-04

Status: protocol / policy only  
Scope: root `AGENTS.md` and `test_run/AGENTS.md` tightening after the `dev_v2.1` recovery and cleanup-opening lessons  
Authority: local engineering interaction contract update; not mechanism doctrine

## Intent

This record captures a rule-surface tightening pass after repeated failure / recovery lessons made several gaps clear:

- ownership truth was not explicit enough
- chronology was too easily mistaken for causality
- `test_run` hot-path regressions were not isolated strictly enough
- public / comment surfaces were allowed to drift away from active mechanism reality

The goal is not to broaden doctrine.

The goal is to reduce future misdiagnosis and reduce additive harness drift.

This record was also revised once in the same day because the first pass made the AGENTS surfaces larger by pure addition.

The accepted read after revision is:

- compress first
- merge before adding
- keep only the failure lessons that materially change future behavior

## Root AGENTS changes

The root `AGENTS.md` was tightened by folding new lessons back into existing rule clusters instead of keeping them as new trailing sections.

Main compression outcomes:

1. ownership truth and public-surface honesty were folded into the existing no-silent-refactor cluster  
2. regression isolation was folded into the existing subtraction-first cleanup cluster  
3. frozen-layer exception wording was kept, but not as a new standalone rule family  
4. the extra additive tail rules were removed

## `test_run` AGENTS changes

`test_run/AGENTS.md` was also rewritten as a smaller surface.

Main compression outcomes:

1. directory identity and duplicate-owner warnings were merged  
2. simplification, passthrough-wrapper, and direct-narrowing rules were merged  
3. regression isolation and cleanup scope-creep rules were merged  
4. ownership truth and active-surface honesty were merged  
5. direct-narrowing preference and helper-justification guidance were kept inside merged `T-02` instead of surviving as standalone rule heads  
6. total local rule count became smaller

## Read of the change

This update should be read as:

- failure-informed rule tightening
- subtraction-first cleanup support
- human-trust protection
- rule-surface compression rather than additive growth

It should not be read as:

- mechanism redesign
- governance replacement
- runtime doctrine change

## Bottom Line

The AGENTS surfaces were tightened so that future cleanup and stabilization work is more likely to:

- tell the truth about ownership
- isolate regressions one group at a time
- avoid harness-side duplicate ownership
- remove stale or dormant public surfaces earlier
