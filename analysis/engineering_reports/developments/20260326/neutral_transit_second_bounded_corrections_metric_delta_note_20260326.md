# Neutral Transit Second Bounded Corrections Metric Delta Note (2026-03-26)

Engine Version: `dev_v2.0`
Modified Layer: before/after metric note only
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: none
Mapping Impact: none
Governance Impact: supplies a compact delta readout for the second bounded correction turn
Backward Compatible: yes

## Before / After

Comparison anchor here is the first bounded correction state (`A1 + B1`) versus the revised second bounded correction state (`A1 + B1 + E2`, with late side frozen at A1).

| Metric | First bounded correction | Second bounded correction |
| --- | ---: | ---: |
| `objective_reached_tick` | 425 | 647 |
| `centroid_to_objective_distance final` | 0.271 | 0.066 |
| `centroid_to_objective_distance min` | 0.248 | 0.048 |
| `formation_rms_radius_ratio peak` | 1.0209 | 1.0525 |
| `front_extent_ratio peak` | 1.9109 | 4.7762 |
| `front_extent_ratio final` | 1.9109 | 4.1007 |

## Near-Target Axial Progress

First bounded correction:

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

Second bounded correction:

- `(647, 1.809, +1.000)`
- `(648, 1.317, +1.000)`
- `(649, 0.758, +1.000)`
- `(650, 0.126, +1.000)`
- `(651, 0.069, +1.000)`
- `(652, 0.061, +1.000)`
- `(653, 0.048, +1.000)`
- `(654, 0.050, -1.000)`
- `(655, 0.058, -1.000)`
- `(656, 0.063, -1.000)`
- `(657, 0.066, -1.000)`

## Short Reading

- Late side is unchanged as mechanism and should be read as frozen at A1.
- Early formation geometry worsens materially.
- Net human-visible outcome is still not acceptable.
