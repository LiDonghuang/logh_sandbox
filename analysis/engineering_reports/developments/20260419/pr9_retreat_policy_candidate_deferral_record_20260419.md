# PR9 Retreat Policy Candidate Deferral Record 20260419

## Scope

- Type: runtime design deferral record
- Status: no implementation in this record
- Topic: short-range retreat / `back_off_keep_front` candidate

## Current Decision

The currently discussed retreat-policy candidate should be recorded, but not implemented yet.

Reason:

- the candidate already implies too much new policy surface for the current moment
- even as internal-only design, the proposed entry/exit controls and realization bounds would introduce a new mechanism family before the next governance read
- the preferred near-term direction is to continue reading new governance instruction first and complete higher-level structural work in an orderly way

## Candidate That Was Deferred

The deferred candidate was:

- a narrow fleet-level `back_off_keep_front` retreat family
- intended only for short-range over-close contact
- meant to keep coarse-body front stable while allowing bounded sternway/back-off
- explicitly not the same as later `turn_away_retirement`

## Why It Was Not Carried Forward Yet

Even in a bounded form, this candidate would still require:

- a new retreat-family decision surface
- a low-level realization branch distinct from ordinary turn-and-go motion
- policy judgment on when retreat should stay front-stable versus escalate into turn-away

That is too much mechanism introduction to proceed ahead of the next governance pass.

## Current Working Read

Until governance gives the next instruction, treat the retreat-policy work as:

- directionally plausible
- worth preserving as a candidate
- not authorized as the current execution target

## Operational Consequence

Next work should prefer:

- reading the next governance instruction
- continuing orderly global-structure / ownership work
- postponing retreat-family implementation until explicitly re-opened
