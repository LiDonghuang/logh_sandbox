# Objective-Area realistic Debug Note (2026-03-27)

Status: debug-only investigation
Carrier: `neutral_transit_v1`
Actual objective window: `tick 420 .. 430` around `objective_reached_tick=425`

## Scope

This note records only viewer-local debug readout for the remaining objective-area realistic residual. No runtime or viewer fix is applied here.

## Window facts

- `objective_reached_tick = 425`
- requested window = `t* +/- 5`
- actual window used = `tick 420 .. 430`
- window rows exported = `1100`
- candidate rows exported = `1100`
- realistic threshold = `0.200000`

## Effective vs realistic within the window

- effective large-turn count (`>90 deg`) = `112`
- realistic large-turn count (`>90 deg`) = `10`
- effective hard-flip count (`>150 deg`) = `37`
- realistic hard-flip count (`>150 deg`) = `1`

Interpretation:
- effective does still flip inside the objective window, so path/posture residual is not zero.
- realistic flips much less often than effective in the same window, so the current realistic estimator is damping most of the raw frame-to-frame heading disorder rather than amplifying it.
- within this exact window the chosen source is almost entirely `prev_window_next_window`, so the tail behavior here is not being driven by rapid fallback churn across shorter candidate sources.

## Candidate-source readout

- `prev_next`: 1
- `prev_window_next_window`: 1099

## Per-unit hotspots

- `A:A72`: realistic_large=1, realistic_hard=1, effective_large=2, effective_hard=1
- `A:A33`: realistic_large=1, realistic_hard=0, effective_large=3, effective_hard=1
- `A:A92`: realistic_large=1, realistic_hard=0, effective_large=1, effective_hard=1
- `A:A71`: realistic_large=1, realistic_hard=0, effective_large=3, effective_hard=2
- `A:A91`: realistic_large=1, realistic_hard=0, effective_large=2, effective_hard=2
- `A:A73`: realistic_large=1, realistic_hard=0, effective_large=2, effective_hard=2
