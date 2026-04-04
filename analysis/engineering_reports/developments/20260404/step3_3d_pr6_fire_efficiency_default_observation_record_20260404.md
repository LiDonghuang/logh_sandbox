# PR6 Fire Efficiency Default Observation Record

Status: local engineering record  
Date: 2026-04-04  
Scope: observer / telemetry / viewer readout only  
Boundary: no frozen-runtime semantic change

## What Changed

`FireEfficiency` is now promoted from a 2D/report-side derived metric to a default battle-facing observation surface in the active `test_run` line.

This change includes:

- default `observer_telemetry["fire_efficiency"]` per fleet, per tick
- current per-tick `fire_eff` in `runtime_debug.focus_indicators`
- always-shown 3D HUD readout:
  - `FireEff: A: e=... | B: e=...`
- engineering validation standard updated so fire-efficiency is an explicit mandatory battle-facing gate together with:
  - fleet-centroid trajectory
  - alive-unit body observation

## Formula

The promoted formula intentionally reuses the already-established 2D/report-side read:

- actual damage this tick = enemy fleet-size drop from previous tick to current tick
- theoretical damage potential this tick = own alive count on previous tick multiplied by `damage_per_tick`
- `fire_efficiency = actual_damage / theoretical_damage_potential`
- bounded to `[0, 1]`

## Why This Record Exists

This is a material observer-surface change.

It affects:

- what the default battle read is expected to include
- what counts as mandatory routine validation in active battle-facing work
- what the viewer exposes by default as first-class runtime evidence

Therefore it is recorded as an independent dated item rather than only being implied by code changes or back-edited into older notes.

## Scope Clarification

This record does **not** claim:

- a new combat doctrine
- a new targeting doctrine
- a new runtime damage model

It only promotes an existing derived readout into the default mandatory observation surface.
