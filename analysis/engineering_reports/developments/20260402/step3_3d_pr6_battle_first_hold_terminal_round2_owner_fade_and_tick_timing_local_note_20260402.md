# PR #6 Round 2 Local Note
## Battle-First Hold/Terminal: Owner Fade + Tick Timing

Status: local implementation note (candidate rejected and reverted locally)  
Scope: test-only / harness-only candidate, no frozen runtime change

## Why this round exists

Round 1 showed that:

- `contact => td = 0` is not a valid battle-first ownership transfer
- it removes Layer A ownership before a real Layer B owner exists
- the result is centroid rebound / separation and alive-body incoherence

So Round 2 changes the candidate from:

- binary cut

to:

- bounded owner fade

## What changed locally

1. Battle/neutral far-field owner now decays continuously rather than dropping to zero in one step.
2. Battle fade no longer triggers on the first contact tick.
   - it waits for a small sustained-contact persistence window first
3. Neutral still uses the same broad read:
   - objective reached starts owner fade
   - no separate neutral doctrine is introduced
4. A new public harness/runtime-observer setting was added:
   - `runtime.observer.tick_timing_enabled`
   - default: `true`
   - records per-tick wall-clock elapsed time into telemetry as `tick_elapsed_ms`

## Current read

- The timing-toggle addition remains valid.
- The owner-fade candidate did not survive centroid/alive-body validation.
- Human observation and centroid trajectory both showed the same failure:
  - fleets were still bounced apart
  - then drifted back / separated instead of transferring ownership honestly
- Therefore the owner-fade mechanism in this round was rejected and removed from local code.

## Recording scope

- runtime/observer interpretation boundary: affected
- test-only / harness-only: yes
- frozen runtime core: unchanged
