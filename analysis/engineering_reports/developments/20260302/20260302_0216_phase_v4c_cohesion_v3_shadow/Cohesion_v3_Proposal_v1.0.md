## Cohesion v3 Proposal v1.0

LOGH Fleet Sandbox — Cohesion Mechanism (Snapshot Observable)

Status: Proposal (Shadow-Only)
Authority: Governance Core
Scope: Structural Observable Definition (No Decision Logic Switch)

### 1. Purpose

Cohesion is a **fleet-level objective snapshot** measuring “organizational integrity” and “exploitable structure” in geometry.

It must be:

* memoryless (no time recursion)
* personality-independent (not driven by FR/MB/PD)
* shape-agnostic (not tied to circle/rectangle benchmarks)
* interpretable and auditable

Cohesion is a temperature gauge, not a commander judgment.

### 2. Design Constraint: Diversity of Formations

A valid fleet formation may be rectangular (e.g., aspect_ratio=2.0), wedge-shaped, or other structured layouts.

Therefore Cohesion=1 cannot mean “close to a circle”.

However, Cohesion must penalize extreme disorganization, e.g.:

* “100-unit long snake”
* scattered or highly stretched formations with weak mutual support

### 3. Structural Decomposition

Cohesion v3 decomposes integrity into two orthogonal terms:

1. **Connectivity Integrity** — is the fleet still one coherent body?
2. **Organization Scale** — is the fleet’s spread within an acceptable organizational range?

This avoids encoding a preferred shape while still detecting grossly poor organization.

### 4. Definitions

Let a fleet-side at tick t have N alive units with positions (x_i).

#### 4.1 Connectivity Term

Define adjacency using the existing engine’s connectivity rule (no change).

Let:

* (LCC) be the size of the largest connected component
* (C_{conn} = LCC / N)

Properties:

* intact body → (C_{conn}=1)
* cut/pocket formation → (C_{conn}<1)

#### 4.2 Scale Term (Shape-Agnostic)

Define the fleet centroid:

[
\mu = \frac{1}{N}\sum_i x_i
]

Define RMS radius:

[
R = \sqrt{\frac{1}{N}\sum_i |x_i - \mu|^2}
]

Define reference scale using only unit count and spacing:

[
R_{ref} = s \cdot \sqrt{N}
]

where (s = \text{min_unit_spacing}).

Define dimensionless spread:

[
\rho = \frac{R}{R_{ref}}
]

This avoids dependence on arena size and avoids assuming a specific shape.

#### 4.3 Window Penalty

Define an acceptable organization window ([\rho_{low}, \rho_{high}]).

Chosen fixed constants for this shadow proposal:

* (\rho_{low} = 0.35)
* (\rho_{high} = 1.15)
* (k = 6.0)

Define:

[
C_{scale}(\rho)=
\begin{cases}
\exp(-k(\rho_{low}-\rho)^2), & \rho < \rho_{low} \\ 
1, & \rho_{low}\le \rho \le \rho_{high} \\ 
\exp(-k(\rho-\rho_{high})^2), & \rho > \rho_{high}
\end{cases}
]

Interpretation:

* within window → no penalty (formation diversity permitted)
* extreme crowding or extreme stretching → penalty increases smoothly

#### 4.4 Final Cohesion v3

[
C_{v3} = \text{clip}(C_{conn}\cdot C_{scale}, 0, 1)
]

Cohesion remains bounded in [0,1].
Cohesion > 1 is not permitted because 1 represents maximal organizational integrity.

### 5. Expected Qualitative Behavior

* Reasonable intact formations at t=0 → (C_{v3}\approx 1)
* Long snake formation → (C_{conn}=1) but (\rho) high → (C_{scale}<1) → (C_{v3}<1)
* Formation cut / pocket emergence → (C_{conn}<1) → (C_{v3}) drops immediately
* Late endgame with very small N → v3 must remain numerically stable and interpretable

### 6. Determinism & Symmetry

Cohesion v3 uses only:

* positions at the current tick
* deterministic component extraction (centroid, RMS radius, LCC)

No randomness. No ordering dependence.

### 7. Phase Discipline

This proposal is **shadow-only**.

It must not be connected to:

* collapse logic
* PD trigger logic
* movement logic

until Governance explicitly issues a switch directive.

### 8. Deliverables

Engineering shall provide:

* early tick CSVs (ticks 0..20) across the standard diagnostic grid
* full timeline CSVs for designated reference cases
* a concise summary table for baseline calibration

Generated files:

* analysis/engineering_reports/20260302_0216_phase_v4c_cohesion_v3_shadow/cohesion_v3_shadow_early_ticks_3x3x3.csv
* analysis/engineering_reports/20260302_0216_phase_v4c_cohesion_v3_shadow/cohesion_v3_shadow_FR8_MB8_PD5_ticks0_200.csv
* analysis/engineering_reports/20260302_0216_phase_v4c_cohesion_v3_shadow/cohesion_v3_shadow_reference_alpha_AB_ticks0_200.csv
* analysis/engineering_reports/20260302_0216_phase_v4c_cohesion_v3_shadow/cohesion_v3_shadow_tick01_summary.csv

### 9. Acceptance Intent (for Governance Review)

Cohesion v3 is structurally preferred if it:

* avoids unjustified low baseline at t=0 for reasonable formations
* penalizes grossly disorganized “snake-like” organization without encoding a preferred shape
* preserves interpretability and deterministic auditability

End of Cohesion v3 Proposal v1.0
