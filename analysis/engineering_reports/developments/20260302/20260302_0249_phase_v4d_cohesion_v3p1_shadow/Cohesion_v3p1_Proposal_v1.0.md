## Cohesion_v3p1 Proposal v1.0

LOGH Fleet Sandbox - Cohesion Mechanism (Snapshot Observable, Shadow Only)

Status: Proposal (Shadow-Only)
Authority: Governance Core
Scope: Structural Observable Refinement (No Decision Logic Switch)

### 1. Purpose

Cohesion_v3.1 refines connectivity calibration while preserving:

- snapshot-only behavior (no recursion)
- personality independence (no FR/MB/PD injection)
- shape agnosticism
- deterministic auditability

### 2. Connectivity Revision (v3.1)

Replace absolute-threshold adjacency with relative adjacency:

1) nearest-neighbor distances:

[
d_i = \min_{j\ne i} |x_i - x_j|
]

2) robust spacing reference:

[
d_{ref} = \text{median}(d_i)
]

3) relative adjacency criterion:

[
|x_i - x_j| \le \beta \cdot d_{ref}
]

with fixed diagnostic constant:

[
\beta = 1.6
]

4) connectivity term:

[
C_{conn}^{(rel)} = \frac{LCC}{N}
]

Degenerate handling:

[
N < 2 \Rightarrow C_{conn}^{(rel)} = 1
]

### 3. Scale Term (unchanged from v3)

[
R = \sqrt{\frac{1}{N}\sum_i |x_i-\mu|^2},\quad R_{ref} = s\sqrt{N},\quad \rho = \frac{R}{R_{ref}}
]

[
C_{scale}(\rho)=
\begin{cases}
\exp(-k(\rho_{low}-\rho)^2), & \rho < \rho_{low} \\
1, & \rho_{low}\le \rho \le \rho_{high} \\
\exp(-k(\rho-\rho_{high})^2), & \rho > \rho_{high}
\end{cases}
]

Constants:

- rho_low = 0.35
- rho_high = 1.15
- k = 6.0

### 4. Final Observer

[
C_{v3.1} = \text{clip}(C_{conn}^{(rel)}\cdot C_{scale}, 0, 1)
]

Comparison observer retained:

[
C_{v3} = \text{clip}(C_{conn}^{(abs)}\cdot C_{scale}, 0, 1)
]

### 5. Shadow Discipline

This observer is not connected to:

- collapse logic
- PD trigger input
- movement/combat/targeting logic

### 6. Produced Artifacts

- analysis/engineering_reports/20260302_0249_phase_v4d_cohesion_v3p1_shadow/cohesion_v3p1_shadow_tick01_summary.csv
- analysis/engineering_reports/20260302_0249_phase_v4d_cohesion_v3p1_shadow/cohesion_v3p1_shadow_early_ticks_3x3x3.csv
- analysis/engineering_reports/20260302_0249_phase_v4d_cohesion_v3p1_shadow/cohesion_v3p1_shadow_FR8_MB8_PD5_ticks0_200.csv
- analysis/engineering_reports/20260302_0249_phase_v4d_cohesion_v3p1_shadow/cohesion_v3p1_shadow_reference_alpha_AB_ticks0_200.csv

Determinism sanity (FR8_MB8_PD5): PASS
Digest1: 3b1976cb6e9a08dcd2753bda58699b6def2081b67f6a1d244e946642ad747883
Digest2: 3b1976cb6e9a08dcd2753bda58699b6def2081b67f6a1d244e946642ad747883

End of Cohesion_v3p1 Proposal v1.0
