# Neutral Transit Bounded Corrections Metric Delta Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: before/after metric note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: supplies a compact before/after readout for the bounded A1 + B1 correction turn
Backward Compatible: yes

## Before / After

| Metric | Baseline | Corrected |
| --- | ---: | ---: |
| `objective_reached_tick` | 426 | 425 |
| `centroid_to_objective_distance final` | 0.763 | 0.271 |
| `centroid_to_objective_distance min` | 0.185 | 0.248 |
| `formation_rms_radius_ratio peak` | 1.0188 | 1.0209 |
| `front_extent_ratio peak` | 2.3934 | 1.9109 |
| `front_extent_ratio final` | 1.9929 | 1.9109 |

## Near-Target Axial Progress

Baseline:

- `(426, 1.257, +1.000)`
- `(427, 0.257, +1.000)`
- `(428, 0.743, -1.000)`
- `(429, 0.232, -0.975)`
- `(430, 0.751, -0.983)`
- `(431, 0.210, -0.961)`
- `(432, 0.749, -0.960)`
- `(433, 0.202, -0.951)`
- `(434, 0.756, -0.958)`
- `(435, 0.185, -0.940)`
- `(436, 0.763, -0.948)`

Corrected:

- `(425, 1.752, +1.000)`
- `(426, 0.752, +1.000)`
- `(427, 0.248, -1.000)`
- `(428, 0.728, -0.975)`
- `(429, 0.257, -0.985)`
- `(430, 0.708, -0.965)`
- `(431, 0.265, -0.973)`
- `(432, 0.693, -0.958)`
- `(433, 0.264, -0.956)`
- `(434, 0.688, -0.952)`
- `(435, 0.271, -0.957)`

## Short Reading

- Late objective-near outer swing is reduced, and the run ends closer to the target.
- Early front-axis growth is reduced more clearly than RMS growth.
- The correction is real but partial.
