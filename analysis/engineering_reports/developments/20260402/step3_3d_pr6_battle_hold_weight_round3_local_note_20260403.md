# PR #6 Round 3 Local Note
## Battle-First Reversible Hold Weight Candidate

Status: local implementation note  
Scope: test-only / harness-only candidate, no frozen runtime change

## Why this round exists

Round 1 and Round 2 showed two different mistakes:

- `contact => td = 0` was wrong
- sticky owner fade was also wrong

Both treated battle hold as an irreversible transfer event.

Human corrected the read:

- hold is not a one-time contact switch
- hold should strengthen near the desired engagement state
- if fleets are pulled apart again, hold should weaken and pre-contact-like approach should resume

## What changed locally

1. A new bounded v4a test-only parameter was added:
   - `battle_hold_weight_strength`
   - range: `[0.0, 1.0]`
   - default local read: `1.0`
2. The battle standoff line now computes a reversible hold weight near `d*`.
3. Far-field approach is no longer removed.
   - it is only suppressed by the current hold weight
4. No new Layer-B owner was introduced.
5. No frozen runtime combat/targeting code was changed.

## Current read

- This is a bounded candidate only.
- It is still not a full battle engagement geometry solution.
- The point is only to correct the previous semantic mistake:
  battle hold is a reversible distance-state blend, not an irreversible contact event.

## Early local probe read

On a bounded `4 -> 1` battle probe:

- first contact still occurred normally
- centroid speed no longer collapsed toward near-zero immediately after contact
- centroid separation remained near an active engagement scale instead of blowing back out toward origin-scale drift

This is only a first gate pass, not final acceptance.

## Recording scope

- public test_run configuration interface: affected
- test-only / harness-only: yes
- frozen runtime core: unchanged
