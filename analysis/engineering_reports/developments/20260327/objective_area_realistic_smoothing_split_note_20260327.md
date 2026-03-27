# Objective-Area realistic Smoothing Split Note (2026-03-27)

Status: debug-only comparison
Window: `tick 420 .. 430`
Smoothing comparison: `smooth=off` exact-frame realistic vs `smooth=on` midpoint presentation at `alpha=0.5`

## Raw realistic (smooth off)

- large-turn count (`>90 deg`) = `10`
- hard-flip count (`>150 deg`) = `1`

## Smoothed midpoint presentation (smooth on)

- midpoint pairs examined = `1000`
- midpoint large-turn count (`max(current->half, half->next) > 90 deg`) = `0`
- interpolation hard-switch count (`dot <= -0.98`) = `0`
- mean current->half delta = `5.536 deg`
- mean half->next delta = `5.536 deg`

## Read

- `smooth=off` already contains the residual set of unstable realistic headings near the objective, but the count is limited relative to `effective`.
- `smooth=on` does not appear to invent the residual from nothing, and in this window it does not add any new `>90 deg` midpoint turns.
- with zero interpolation hard-switches in this window, the current low-speed smoothing is mostly redistributing existing motion rather than creating the observed disorder.
