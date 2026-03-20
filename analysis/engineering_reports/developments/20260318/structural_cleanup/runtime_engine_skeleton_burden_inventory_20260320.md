# Runtime Engine Skeleton Burden Inventory (2026-03-20)

Status: preparatory review / read-only burden inventory  
Scope: `runtime/engine_skeleton.py` only  
Classification: frozen-layer review material / no implementation changes

## 1. Identity

This document is a read-only preparatory review.

It does **not**:

- modify `runtime/engine_skeleton.py`
- authorize cleanup-by-stealth
- change runtime semantics
- change pipeline order
- reinterpret canonical runtime behavior

Its purpose is only to identify burden concentration and likely future cut points for a separately authorized runtime round.

## 2. Current File Shape

Current file:

- `runtime/engine_skeleton.py`
- line count: `2496`

Primary class:

- `EngineTickSkeleton`: lines `7-2691`

Major method blocks:

- `__init__`: `8-69` (`62` lines)
- `step`: `71-78` (`8` lines)
- `_compute_cohesion_v2_geometry`: `106-276` (`171` lines)
- `_compute_cohesion_v3_shadow_geometry`: `278-403` (`126` lines)
- `evaluate_cohesion`: `405-452` (`48` lines)
- `evaluate_target`: `454-493` (`40` lines)
- `evaluate_utility`: `495-496` (`2` lines)
- `integrate_movement`: `498-2228` (`1731` lines)
- `resolve_combat`: `2230-2691` (`462` lines)

## 3. Main Burden Concentrations

### A. Debug / Diagnostic State Density In `__init__`

`__init__` contains a large amount of debug and diagnostic state initialization:

- contact diagnostics
- FSR diagnostics
- diag4 / RPG diagnostics
- outlier tracking
- cohesion shadow/debug caches
- boundary-force tracking

This makes the constructor heavier than a minimal runtime execution host would ideally be.

### B. Cohesion Runtime + Shadow / Debug Overlay Coupling

`evaluate_cohesion(...)` is only `48` lines, but it coordinates:

- runtime cohesion decision source switching
- v1/v2 debug retention
- v3 shadow cohesion computation
- debug payload persistence

This is not yet a request to split it.

It is a note that even a short method here still mixes runtime decision and debug-shadow concerns.

### C. `integrate_movement(...)` Is The Dominant Burden Center

`integrate_movement(...)` is `1731` lines and is the single largest concentration of file weight.

Observed burden types inside this one method:

- movement integration proper
- fleet major-axis geometry and formation metrics
- pursuit / collapse-adjacent decision shaping
- boundary soft/hard handling
- FSR block
- diag4 / RPG / outlier tracking
- contact-window history bookkeeping
- pending diagnostic payload assembly

This method is therefore not only “long”.

It is currently the main mixed hot path in the runtime frozen layer.

### D. `resolve_combat(...)` Still Mixes Semantics And Diagnostics

`resolve_combat(...)` is `462` lines and combines:

- contact hysteresis behavior
- fire-quality modulation
- combat resolution
- combat statistics capture
- diagnostic payload continuation

This is a second strong burden center, though smaller than `integrate_movement(...)`.

## 4. Observed Burden Themes

The repeated burden pattern across the file is:

- execution semantics
- debug/diagnostic shadow bookkeeping
- observer-adjacent metric accumulation

The file is not only large because of raw mechanism logic.

It is also large because debug/diagnostic and shadow-accounting concerns remain interleaved with hot-path execution methods.

## 5. Candidate Cut Map (Read-Only)

These are preparatory candidates only.

They are not approved implementation actions.

### Candidate A. Constructor Diagnostic State Consolidation

Potential future cut:

- consolidate debug/diagnostic state initialization so `__init__` stops manually enumerating so many tracking containers

Risk level:

- medium

Reason:

- packaging change only in appearance
- but still touches frozen runtime state layout, so it would require authorization

### Candidate B. Cohesion Shadow / Debug Side-Channel Isolation

Potential future cut:

- isolate the v1/v2/v3 shadow/debug retention path from the minimal runtime cohesion substitution path

Risk level:

- high

Reason:

- crosses the runtime/observer/debug interpretation boundary
- could accidentally shift what runtime treats as active versus shadow

### Candidate C. `integrate_movement(...)` Diagnostic Shedding

Potential future cut:

- separate movement-core execution from optional diagnostic payload assembly and long-lived outlier bookkeeping

Risk level:

- high

Reason:

- this is the heaviest method in the file
- but it is also the hottest semantic path, so even packaging-only work needs strong guardrails

### Candidate D. `resolve_combat(...)` Diagnostic Shedding

Potential future cut:

- isolate combat resolution from combat diagnostics/contact-window payload assembly

Risk level:

- high

Reason:

- likely worthwhile
- but directly adjacent to combat semantics and contact interpretation

## 6. Packaging Candidates vs Gate-Triggering Candidates

### Packaging-Oriented Candidates

These look like packaging candidates in spirit, though still not authorized:

- constructor diagnostic-state consolidation
- local diagnostic payload assembly extraction
- grouping repeated diagnostic bookkeeping helpers

### Gate-Triggering Candidates

These would clearly require a separate runtime authorization gate:

- any change to `step(...)` ordering
- any change to how cohesion substitution is applied
- any change to movement/boundary/FSR interaction semantics
- any change to combat/contact hysteresis meaning
- any change that shifts runtime vs observer responsibility

## 7. Recommended Next Runtime-Side Question

If governance opens a later runtime round, the strongest first question is likely:

- can runtime hot-path diagnostics be separated from core execution flow without changing mechanism semantics?

That question is narrower and safer than:

- “simplify engine_skeleton broadly”

## 8. Final Note

Current governance-safe conclusion:

- `runtime/engine_skeleton.py` is a legitimate future cleanup target
- but the correct next step remains separate authorization, not direct implementation

No runtime code was modified in this review.
